"""
utils.py — Shared utility functions for FairGuard AI
"""
import os
import pickle
import hashlib
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.preprocessing import LabelEncoder


# ── File helpers ───────────────────────────────────────────────────────────────

def save_model(model, path: str) -> str:
    """Pickle a model to disk. Returns the saved path."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(model, f)
    return path


def load_model(path: str):
    """Load a pickled model from disk."""
    with open(path, "rb") as f:
        return pickle.load(f)


def ensure_dirs(*dirs):
    """Create directories if they don't exist."""
    for d in dirs:
        os.makedirs(d, exist_ok=True)


# ── Data helpers ───────────────────────────────────────────────────────────────

def encode_categoricals(df: pd.DataFrame, cols: list) -> tuple[pd.DataFrame, dict]:
    """
    Label-encode specified columns.
    Returns (encoded_df, le_map) where le_map is {col: LabelEncoder}.
    """
    df_enc = df.copy()
    le_map = {}
    for col in cols:
        if col in df_enc.columns and df_enc[col].dtype == object:
            le = LabelEncoder()
            df_enc[col] = le.fit_transform(df_enc[col].astype(str))
            le_map[col] = le
    return df_enc, le_map


def decode_column(series: pd.Series, le: LabelEncoder) -> pd.Series:
    """Inverse-transform a label-encoded column."""
    return series.apply(lambda x: le.inverse_transform([int(x)])[0]
                        if 0 <= int(x) < len(le.classes_) else "Unknown")


def safe_encode_value(value, le: LabelEncoder):
    """Encode a single value, returning -1 if unseen."""
    try:
        return le.transform([value])[0]
    except ValueError:
        return -1


def detect_categorical_cols(df: pd.DataFrame, max_unique: int = 20) -> list:
    """Return column names that look categorical (object dtype or low cardinality int)."""
    cats = []
    for col in df.columns:
        if df[col].dtype == object:
            cats.append(col)
        elif df[col].nunique() <= max_unique and df[col].dtype in ["int32", "int64"]:
            cats.append(col)
    return cats


def validate_dataset(df: pd.DataFrame, target_col: str,
                     feature_cols: list) -> list[str]:
    """Return list of validation error strings (empty = OK)."""
    errors = []
    if df.empty:
        errors.append("Dataset is empty.")
    if target_col not in df.columns:
        errors.append(f"Target column '{target_col}' not found.")
    missing_feats = [c for c in feature_cols if c not in df.columns]
    if missing_feats:
        errors.append(f"Feature columns missing: {missing_feats}")
    null_pct = df.isnull().mean()
    high_null = null_pct[null_pct > 0.3].index.tolist()
    if high_null:
        errors.append(f"High null rate (>30%) in columns: {high_null}")
    if target_col in df.columns:
        n_classes = df[target_col].nunique()
        if n_classes < 2:
            errors.append("Target column has fewer than 2 unique values.")
        if n_classes > 10:
            errors.append(f"Target has {n_classes} unique values — expected binary classification.")
    return errors


# ── Metric helpers ─────────────────────────────────────────────────────────────

def format_score(score: float, decimals: int = 3) -> str:
    return f"{score:.{decimals}f}"


def bias_percentage_reduction(original: float, mitigated: float) -> float:
    """How much % was the bias reduced?"""
    if original == 0:
        return 0.0
    return max(0.0, (original - mitigated) / original * 100)


def generate_audit_id(model_name: str) -> str:
    """Generate a short unique audit ID."""
    ts  = datetime.now().isoformat()
    raw = f"{model_name}_{ts}"
    h   = hashlib.md5(raw.encode()).hexdigest()[:8].upper()
    return f"FG-{h}"


def timestamp_str(fmt: str = "%Y-%m-%d %H:%M UTC") -> str:
    return datetime.utcnow().strftime(fmt)


# ── Report helpers ─────────────────────────────────────────────────────────────

def save_report_to_disk(pdf_bytes: bytes, model_name: str,
                         kind: str = "report") -> str:
    """Save PDF bytes to reports/ folder. Returns filename."""
    ensure_dirs("reports")
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = model_name.replace(" ", "_").replace("/", "-")
    filename  = f"reports/fairguard_{kind}_{safe_name}_{ts}.pdf"
    with open(filename, "wb") as f:
        f.write(pdf_bytes)
    return filename


def build_summary_dict(model_name: str, audit_results: dict,
                        protected_attrs: list, accuracy: float) -> dict:
    """Build a flat summary dict for display / export."""
    max_dp = max(r["demographic_parity_diff"] for r in audit_results.values())
    min_di = min(r["disparate_impact_ratio"]   for r in audit_results.values())
    return {
        "model_name":        model_name,
        "audit_id":          generate_audit_id(model_name),
        "timestamp":         timestamp_str(),
        "protected_attrs":   ", ".join(protected_attrs),
        "overall_accuracy":  round(accuracy, 4),
        "max_dp_diff":       round(max_dp, 4),
        "min_di_ratio":      round(min_di, 4),
        "cert_eligible":     max_dp < 0.10,
        "attrs_audited":     len(protected_attrs),
    }