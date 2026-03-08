from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import pickle
import io
from fastapi.responses import Response
from pydantic import BaseModel
import pandas as pd
import numpy as np

# Import existing modules
from model_loader import load_demo_model_and_data, prepare_features
from bias_metrics import run_full_audit
from intersectional_analysis import intersectional_audit
from debiasing_engine import run_all_debiasing
from report_generator import generate_full_report, generate_certificate

app = FastAPI(title="FairGuard AI API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global State Management (replicating Streamlit session state)
state = {
    "model": None,
    "data": None,
    "feature_cols": [],
    "target_col": "Loan_Status",
    "le_map": {},
    "y_pred": None,
    "audit_results": None,
    "protected_attrs": [],
    "comparison_rows": [],
    "model_name": "Demo Loan Model",
    "best_result": None
}

class AuditRequest(BaseModel):
    protected_attrs: list[str]

class IntersectionalRequest(BaseModel):
    attrs: list[str]
    min_size: int = 20

class DebiasRequest(BaseModel):
    sensitive_attr: str
    test_size: float = 0.2

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/demo")
def load_demo():
    try:
        model, data, feature_cols, target_col = load_demo_model_and_data()
        state["model"] = model
        state["data"] = data
        state["feature_cols"] = feature_cols
        state["target_col"] = target_col
        state["le_map"] = model.le_map
        state["model_name"] = "Demo Loan Approval Model"
        
        X = prepare_features(data, feature_cols, model.le_map)
        state["y_pred"] = model.predict(X)
        
        # Return a preview of the data (first 10 rows)
        preview = data.head(10).to_dict(orient="records")
        return {
            "status": "success",
            "message": "Demo loaded",
            "model_name": state["model_name"],
            "rows": len(data),
            "columns": len(data.columns),
            "preview": preview
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_files(
    model: UploadFile = File(...),
    dataset: UploadFile = File(...),
    model_name: str = Form("My AI Model")
):
    try:
        # Load model
        model_bytes = await model.read()
        loaded_model = pickle.loads(model_bytes)
        
        # Load dataset
        dataset_bytes = await dataset.read()
        df = pd.read_csv(io.BytesIO(dataset_bytes))
        
        # Update global state
        state["model"] = loaded_model
        state["data"] = df
        state["model_name"] = model_name
        
        if hasattr(loaded_model, "feature_cols"):
            state["feature_cols"] = loaded_model.feature_cols
        state["le_map"] = getattr(loaded_model, "le_map", {})
        
        # We need to infer the target column, or use current state default
        target_col = state["target_col"]
        if target_col not in df.columns:
             # Just default to last column if 'Loan_Status' is not in df
             target_col = df.columns[-1]
             state["target_col"] = target_col
             
        X = prepare_features(df, state["feature_cols"], state["le_map"])
        state["y_pred"] = loaded_model.predict(X)

        preview = df.head(10).to_dict(orient="records")
        return {
            "status": "success",
            "message": "Files loaded",
            "model_name": state["model_name"],
            "rows": len(df),
            "columns": len(df.columns),
            "preview": preview
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/audit")
def run_audit(req: AuditRequest):
    if state["model"] is None or state["data"] is None:
        raise HTTPException(status_code=400, detail="Model and data not loaded")
    
    if len(req.protected_attrs) < 2:
        raise HTTPException(status_code=400, detail="Select at least 2 protected attributes")

    state["protected_attrs"] = req.protected_attrs
    data = state["data"]
    target_col = state["target_col"]
    y_true = data[target_col].values
    y_pred = state["y_pred"]

    try:
        audit = run_full_audit(data, y_true, y_pred, req.protected_attrs)
        state["audit_results"] = audit
        def convert_numpy(obj):
            if isinstance(obj, dict):
                return {str(k): convert_numpy(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(v) for v in obj]
            elif isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32)):
                if np.isnan(obj) or np.isinf(obj): return None
                return float(obj)
            elif isinstance(obj, (np.bool_, bool)):
                return bool(obj)
            elif isinstance(obj, np.ndarray):
                return convert_numpy(obj.tolist())
            return obj

        audit_json = convert_numpy(audit)
        return {"status": "success", "audit_results": audit_json}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/intersectional")
def run_intersectional(req: IntersectionalRequest):
    if state["model"] is None or state["y_pred"] is None:
        raise HTTPException(status_code=400, detail="Run audit first")
    
    if len(req.attrs) < 2:
        raise HTTPException(status_code=400, detail="Select at least 2 attributes")

    data = state["data"]
    y_true = data[state["target_col"]].values
    y_pred = state["y_pred"]

    try:
        # Determine appropriate min_size based on dataset size
        # Very small datasets need smaller thresholds
        total_rows = len(state["data"])
        default_min = max(5, int(total_rows * 0.01)) # 1% or 5, whichever is larger
        min_size_used = req.min_size if req.min_size is not None and req.min_size > 0 else default_min
        
        # Override if default 20 is too high for this dataset
        if min_size_used == 20 and default_min < 20:
            min_size_used = default_min

        df_int = intersectional_audit(data, y_true, y_pred, req.attrs, min_size_used)
        
        # Build our custom numpy converting engine
        def convert_numpy(obj):
            if isinstance(obj, dict):
                return {str(k): convert_numpy(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(v) for v in obj]
            elif isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32)):
                if np.isnan(obj) or np.isinf(obj): return None
                return float(obj)
            elif isinstance(obj, (np.bool_, bool)):
                return bool(obj)
            elif isinstance(obj, np.ndarray):
                return convert_numpy(obj.tolist())
            return obj

        records = convert_numpy(df_int.to_dict(orient="records"))
        return {"status": "success", "results": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/debias")
def run_debias(req: DebiasRequest):
    if state["model"] is None or not state["protected_attrs"]:
        raise HTTPException(status_code=400, detail="Run audit first")
    
    from sklearn.model_selection import train_test_split
    from bias_metrics import demographic_parity_difference

    data = state["data"]
    model = state["model"]
    feature_cols = state["feature_cols"]
    target_col = state["target_col"]

    try:
        X = prepare_features(data, feature_cols, state["le_map"])
        y = data[target_col].values
        sens = data[req.sensitive_attr].values

        X_tr, X_te, y_tr, y_te, s_tr, s_te = train_test_split(
            X, y, sens, test_size=req.test_size, random_state=42)

        orig_pred = model.predict(X_te)
        orig_acc = (orig_pred == y_te).mean()
        orig_dp = demographic_parity_difference(y_te, orig_pred, s_te)

        rows = run_all_debiasing(model, X_tr, y_tr, X_te, y_te, s_tr, s_te, orig_acc, orig_dp)
        state["comparison_rows"] = rows

        best = min(rows[1:], key=lambda r: r["dp_diff"])
        state["best_result"] = best

        def convert_numpy(obj):
            if isinstance(obj, dict):
                return {str(k): convert_numpy(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(v) for v in obj]
            elif isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32)):
                if np.isnan(obj) or np.isinf(obj): return None
                return float(obj)
            elif isinstance(obj, (np.bool_, bool)):
                return bool(obj)
            elif isinstance(obj, np.ndarray):
                return convert_numpy(obj.tolist())
            return obj
            
        for r in rows:
            r.pop("model", None)
            r.pop("y_pred", None)
            r.pop("thresholds", None)
            
        return {"status": "success", "results": convert_numpy(rows), "best": convert_numpy(best)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/compliance")
def get_compliance():
    if not state["audit_results"]:
        raise HTTPException(status_code=400, detail="Run audit first")
    
    audit = state["audit_results"]
    best = state["best_result"]
    
    orig_max_dp = float(max(r["demographic_parity_diff"] for r in audit.values()))
    orig_di_min = float(min(r["disparate_impact_ratio"] for r in audit.values()))
    
    if best:
        eff_dp = float(best["dp_diff"])
        eff_acc = float(best["accuracy"])
        eff_di = float(max(0.0, 1.0 - eff_dp))
        status = "debiased"
    else:
        eff_dp = orig_max_dp
        eff_di = orig_di_min
        eff_acc = float(list(audit.values())[0]["overall_accuracy"])
        status = "original"
        
    REGULATIONS = [
        {"name": "EU AI Act (Art.10 & Art.13)", "pass": bool(eff_dp < 0.10), "thresh": "DP Diff < 0.10", "desc": "High-Risk AI must ensure non-discrimination."},
        {"name": "DPDP Act 2023 (India)", "pass": bool(eff_dp < 0.15), "thresh": "DP Diff < 0.15", "desc": "Data protection laws prohibit discriminatory profiling."},
        {"name": "RBI Fair Lending Guidelines", "pass": bool(eff_di > 0.80), "thresh": "DI Ratio > 0.80", "desc": "Lending decisions must not exhibit adverse impact on groups."},
        {"name": "US ECOA / Regulation B", "pass": bool(eff_di > 0.80), "thresh": "DI Ratio > 0.80", "desc": "Equal credit opportunity; adverse impact rule at 80%."},
        {"name": "IEEE P7003 Std (Bias in AI)", "pass": bool(eff_dp < 0.10), "thresh": "DP Diff < 0.10", "desc": "Industry standard for algorithmic bias considerations."},
        {"name": "ISO/IEC 42001 (AI Management)", "pass": bool(eff_dp < 0.20), "thresh": "DP Diff < 0.20", "desc": "AI management systems must address fairness risk."},
        {"name": "SEBI Algo Trading Guidelines", "pass": bool(eff_dp < 0.15), "thresh": "DP Diff < 0.15", "desc": "Algorithmic systems in finance must be auditable."},
    ]

    return {
        "status": status,
        "effective_dp": eff_dp,
        "effective_di": eff_di,
        "effective_acc": eff_acc,
        "original_max_dp": orig_max_dp,
        "regulations": REGULATIONS
    }

@app.get("/report/pdf")
def get_pdf_report():
    if not state["audit_results"]:
        raise HTTPException(status_code=400, detail="Run audit first")
        
    try:
        pdf_bytes = generate_full_report(
            model_name = state["model_name"],
            audit_results = state["audit_results"],
            comparison_rows = state["comparison_rows"],
            protected_attrs = state["protected_attrs"],
            overall_accuracy = state["best_result"]["accuracy"] if state["best_result"] else list(state["audit_results"].values())[0]["overall_accuracy"]
        )
        return Response(content=pdf_bytes, media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/report/certificate")
def get_certificate():
    if not state["audit_results"]:
        raise HTTPException(status_code=400, detail="Run audit first")
        
    audit = state["audit_results"]
    best = state["best_result"]
    max_dp = max(r["demographic_parity_diff"] for r in audit.values())
    acc = list(audit.values())[0]["overall_accuracy"]
    
    effective_bias = best["dp_diff"] if best else max_dp
    effective_acc = best["accuracy"] if best else acc
    
    if effective_bias >= 0.10:
        raise HTTPException(status_code=400, detail="Bias score must be < 0.10 to generate certificate")
        
    try:
        cert_pdf = generate_certificate(
            model_name = state["model_name"],
            bias_score = effective_bias,
            accuracy = effective_acc,
            protected_attrs = state["protected_attrs"],
        )
        return Response(content=cert_pdf, media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
