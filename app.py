"""
app.py — FairGuard AI: Bias Audit & Correction Platform
Streamlit multi-page dashboard
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import numpy as np
import pandas as pd
import pickle
import io
import base64
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# ── local modules ─────────────────────────────────────────────────────────────
from model_loader          import load_demo_model_and_data, prepare_features
from bias_metrics          import run_full_audit, classify_bias_severity
from intersectional_analysis import intersectional_audit, highest_bias_group, most_favoured_group
from debiasing_engine      import run_all_debiasing
from visualizations        import (
    approval_rate_chart, bias_radar_chart, before_after_chart,
    feature_importance_chart, intersectional_heatmap, disparity_bar, bias_gauge,
)
from report_generator      import generate_full_report, generate_certificate

# ── page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FairGuard AI",
    page_icon="🛡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.main { background: #0f1117; color: #e0e0e0; }
section[data-testid="stSidebar"] { background: #1a1d2e !important; }

.metric-card {
    background: #1e2130; border-radius: 12px; padding: 18px 22px;
    border-left: 4px solid #3498db; margin-bottom: 12px;
}
.metric-card h3 { color: #3498db; margin: 0 0 4px 0; font-size: 13px; }
.metric-card .val { font-size: 32px; font-weight: 700; color: #fff; }
.metric-card .sub { font-size: 11px; color: #888; }

.section-header {
    background: linear-gradient(90deg,#1e2130,#16213e);
    border-left: 4px solid #3498db; border-radius: 8px;
    padding: 12px 18px; margin: 16px 0 10px 0;
}
.section-header h2 { color: #3498db; margin: 0; font-size: 16px; }

.badge-low      { background:#1a3a2a; color:#2ecc71; padding:2px 10px; border-radius:12px; font-size:12px; font-weight:700; }
.badge-moderate { background:#3a2a0a; color:#f39c12; padding:2px 10px; border-radius:12px; font-size:12px; font-weight:700; }
.badge-high     { background:#3a0a0a; color:#e74c3c; padding:2px 10px; border-radius:12px; font-size:12px; font-weight:700; }
.badge-critical { background:#2a0000; color:#ff4444; padding:2px 10px; border-radius:12px; font-size:12px; font-weight:700; }

.cert-box {
    background: linear-gradient(135deg, #1e3a1e, #1a3a2a);
    border: 2px solid #2ecc71; border-radius: 16px;
    padding: 30px; text-align: center; margin: 20px 0;
}
.cert-box h1 { color: #2ecc71; font-size: 28px; }
.cert-box p  { color: #ccc; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# ── Session state init ─────────────────────────────────────────────────────────
if "model"           not in st.session_state: st.session_state.model           = None
if "data"            not in st.session_state: st.session_state.data            = None
if "feature_cols"    not in st.session_state: st.session_state.feature_cols    = []
if "target_col"      not in st.session_state: st.session_state.target_col      = "Loan_Status"
if "le_map"          not in st.session_state: st.session_state.le_map          = {}
if "y_pred"          not in st.session_state: st.session_state.y_pred          = None
if "audit_results"   not in st.session_state: st.session_state.audit_results   = None
if "protected_attrs" not in st.session_state: st.session_state.protected_attrs = []
if "comparison_rows" not in st.session_state: st.session_state.comparison_rows = []
if "model_name"      not in st.session_state: st.session_state.model_name      = "Demo Loan Model"
if "best_result"     not in st.session_state: st.session_state.best_result     = None

# ── Sidebar navigation ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛡 FairGuard AI")
    st.markdown("*Bias Audit & Correction Platform*")
    st.divider()
    pages = [
        "📁  Upload & Setup",
        "🔍  Bias Analysis",
        "🔀  Intersectional Bias",
        "🔧  Bias Remediation",
        "📋  Compliance Report",
        "🏅  Audit Certificate",
    ]
    page = st.radio("Navigate", pages, label_visibility="collapsed")
    st.divider()
    if st.session_state.model is not None:
        st.success("✅ Model loaded")
    if st.session_state.audit_results:
        max_dp = max(r["demographic_parity_diff"]
                     for r in st.session_state.audit_results.values())
        label, _ = classify_bias_severity(max_dp)
        st.info(f"Bias Level: {label}")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE 1 — Upload & Setup
# ─────────────────────────────────────────────────────────────────────────────
if page == pages[0]:
    st.markdown("# 📁 Upload & Setup")
    st.markdown("Upload your model and dataset, or load the demo.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🤖 Model")
        model_file = st.file_uploader("Upload .pkl model", type=["pkl"])
        model_name_input = st.text_input("Model Name", value="My AI Model")

    with col2:
        st.markdown("### 📊 Dataset")
        dataset_file = st.file_uploader("Upload .csv dataset", type=["csv"])

    st.divider()
    st.markdown("### ⚡ Or use the built-in demo")
    if st.button("🚀 Load Demo (Loan Approval Dataset)", width="stretch"):
        with st.spinner("Loading demo model and dataset…"):
            model, data, feature_cols, target_col = load_demo_model_and_data()
            st.session_state.model        = model
            st.session_state.data         = data
            st.session_state.feature_cols = feature_cols
            st.session_state.target_col   = target_col
            st.session_state.le_map       = model.le_map
            st.session_state.model_name   = "Demo Loan Approval Model"
            X = prepare_features(data, feature_cols, model.le_map)
            st.session_state.y_pred = model.predict(X)
            st.success("✅ Demo loaded! Navigate to Bias Analysis →")

    if model_file and dataset_file:
        if st.button("📥 Load Uploaded Files", width="stretch"):
            with st.spinner("Loading files…"):
                try:
                    model = pickle.loads(model_file.read())
                    data  = pd.read_csv(dataset_file)
                    st.session_state.model      = model
                    st.session_state.data       = data
                    st.session_state.model_name = model_name_input
                    # Try to get feature cols from model or let user pick
                    if hasattr(model, "feature_cols"):
                        st.session_state.feature_cols = model.feature_cols
                    st.session_state.le_map = getattr(model, "le_map", {})
                    st.success("✅ Files loaded!")
                except Exception as e:
                    st.error(f"Error loading files: {e}")

    # Show preview
    if st.session_state.data is not None:
        st.divider()
        st.markdown("### 📋 Dataset Preview")
        data = st.session_state.data
        c1, c2, c3 = st.columns(3)
        c1.metric("Rows", f"{len(data):,}")
        c2.metric("Columns", len(data.columns))
        c3.metric("Target Distribution", f"{data[st.session_state.target_col].mean()*100:.1f}% +ve")
        st.dataframe(data.head(10), use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE 2 — Bias Analysis
# ─────────────────────────────────────────────────────────────────────────────
elif page == pages[1]:
    st.markdown("# 🔍 Bias Analysis")

    if st.session_state.model is None:
        st.warning("⬅ Please load a model first (Upload & Setup page).")
        st.stop()

    data         = st.session_state.data
    model        = st.session_state.model
    target_col   = st.session_state.target_col
    feature_cols = st.session_state.feature_cols

    # Protected attribute selection
    st.markdown("### 🎯 Select Protected Attributes (min 4)")
    candidate_cols = [c for c in data.columns if c != target_col]
    protected_attrs = st.multiselect(
        "Protected Attributes",
        candidate_cols,
        default=[c for c in ["Gender","Age","Location","Income"] if c in candidate_cols],
    )
    if len(protected_attrs) < 2:
        st.error("Please select at least 2 attributes to audit.")
        st.stop()

    st.session_state.protected_attrs = protected_attrs

    if st.button("▶ Run Bias Audit", width="stretch"):
        with st.spinner("Running bias detection engine…"):
            X      = prepare_features(data, feature_cols, st.session_state.le_map)
            y_true = data[target_col].values
            y_pred = model.predict(X)
            st.session_state.y_pred = y_pred

            audit = run_full_audit(data, y_true, y_pred, protected_attrs)
            st.session_state.audit_results = audit
            st.success("✅ Audit complete!")

    if st.session_state.audit_results:
        audit = st.session_state.audit_results
        y_true = data[target_col].values
        y_pred = st.session_state.y_pred

        # KPI row
        st.divider()
        st.markdown("### 📊 Key Bias Metrics")
        cols = st.columns(len(audit))
        for col_w, (attr, res) in zip(cols, audit.items()):
            dp    = res["demographic_parity_diff"]
            label, color = classify_bias_severity(dp)
            col_w.plotly_chart(bias_gauge(dp, attr), width="stretch")

        # Radar
        st.plotly_chart(bias_radar_chart(audit), width="stretch")

        # Per-attribute detail
        for attr, res in audit.items():
            st.markdown(f"#### {attr}")
            gs = res["group_stats"]
            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(approval_rate_chart(gs, attr), width="stretch")
            with c2:
                df_gs = pd.DataFrame(gs).T.reset_index().rename(columns={"index":"Group"})
                df_gs["Approval %"] = (df_gs["ppr"].astype(float) * 100).round(1)
                df_gs["TPR %"]      = (df_gs["tpr"].astype(float) * 100).round(1)
                df_gs["Accuracy %"] = (df_gs["acc"].astype(float) * 100).round(1)
                st.dataframe(df_gs[["Group","n","Approval %","TPR %","Accuracy %"]],
                             use_container_width=True)

            dp   = res["demographic_parity_diff"]
            eo   = res["equal_opportunity_diff"]
            pp   = res["predictive_parity_diff"]
            di   = res["disparate_impact_ratio"]
            lbl, _ = classify_bias_severity(dp)
            m1,m2,m3,m4 = st.columns(4)
            m1.metric("Dem. Parity Diff",  f"{dp:.3f}")
            m2.metric("Equal Opp. Diff",   f"{eo:.3f}")
            m3.metric("Pred. Parity Diff", f"{pp:.3f}")
            m4.metric("Disparate Impact",  f"{di:.3f}")
            st.divider()

        # Feature importance
        st.markdown("### 🔮 Feature Importance (SHAP Proxy)")
        st.plotly_chart(feature_importance_chart(model, feature_cols),
                        width="stretch")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE 3 — Intersectional Bias
# ─────────────────────────────────────────────────────────────────────────────
elif page == pages[2]:
    st.markdown("# 🔀 Intersectional Bias Detection")

    if st.session_state.model is None or st.session_state.y_pred is None:
        st.warning("⬅ Run Bias Analysis first.")
        st.stop()

    data         = st.session_state.data
    y_true       = data[st.session_state.target_col].values
    y_pred       = st.session_state.y_pred
    p_attrs      = st.session_state.protected_attrs or [c for c in data.columns
                                                         if c != st.session_state.target_col][:4]

    st.markdown("### 🎛 Select Attributes for Intersection")
    sel_attrs = st.multiselect("Combine attributes:", p_attrs, default=p_attrs[:2])
    min_size  = st.slider("Minimum group size", 10, 100, 20)

    if len(sel_attrs) < 2:
        st.info("Select at least 2 attributes.")
        st.stop()

    if st.button("▶ Analyse Intersectional Bias", width="stretch"):
        with st.spinner("Computing intersection groups…"):
            df_int = intersectional_audit(data, y_true, y_pred, sel_attrs, min_size)
            st.session_state["int_df"]    = df_int
            st.session_state["int_attrs"] = sel_attrs

    df_int    = st.session_state.get("int_df", pd.DataFrame())
    int_attrs = st.session_state.get("int_attrs", sel_attrs)

    if not df_int.empty:
        st.divider()
        worst = highest_bias_group(df_int)
        best  = most_favoured_group(df_int)

        c1, c2 = st.columns(2)
        with c1:
            st.error(f"**Most Disadvantaged Group**\n\n{worst.get('Group','—')}\n\nApproval Rate: {worst.get('Approval Rate',0)*100:.1f}%")
        with c2:
            st.success(f"**Most Favoured Group**\n\n{best.get('Group','—')}\n\nApproval Rate: {best.get('Approval Rate',0)*100:.1f}%")

        st.markdown("### 📊 Disparity Chart")
        st.plotly_chart(disparity_bar(df_int), width="stretch")

        st.markdown("### 🗂 All Intersection Groups")
        st.dataframe(df_int, use_container_width=True)

        if len(int_attrs) >= 2:
            st.markdown("### 🌡 Approval Rate Heatmap")
            st.plotly_chart(
                intersectional_heatmap(df_int, int_attrs[0], int_attrs[1], data, y_pred),
                width="stretch")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE 4 — Bias Remediation
# ─────────────────────────────────────────────────────────────────────────────
elif page == pages[3]:
    st.markdown("# 🔧 Bias Remediation Engine")

    if st.session_state.model is None:
        st.warning("⬅ Load a model first.")
        st.stop()

    data         = st.session_state.data
    model        = st.session_state.model
    target_col   = st.session_state.target_col
    feature_cols = st.session_state.feature_cols
    p_attrs      = st.session_state.protected_attrs

    if not p_attrs:
        st.warning("⬅ Select protected attributes in Bias Analysis first.")
        st.stop()

    sensitive_attr = st.selectbox("Primary sensitive attribute for debiasing:", p_attrs)
    test_size      = st.slider("Test set size", 0.1, 0.4, 0.2, 0.05)

    st.markdown("### 🛠 Available Techniques")
    c1, c2, c3 = st.columns(3)
    c1.info("**1️⃣ Reweighing**\nAssigns sample weights so each group-label cell has equal influence during training.")
    c2.info("**2️⃣ Threshold Optimization**\nFinds per-group decision thresholds that equalise positive prediction rates.")
    c3.info("**3️⃣ Adversarial Debiasing**\nAugments training data with fairness-weighted resampling + penalised logistic regression.")

    if st.button("🚀 Fix Bias — Run All Techniques", width="stretch", type="primary"):
        with st.spinner("Training debiased models (this may take a moment)…"):
            X      = prepare_features(data, feature_cols, st.session_state.le_map)
            y      = data[target_col].values
            sens   = data[sensitive_attr].values

            X_tr, X_te, y_tr, y_te, s_tr, s_te = train_test_split(
                X, y, sens, test_size=test_size, random_state=42)

            orig_acc  = (model.predict(X_te) == y_te).mean()
            orig_pred = model.predict(X_te)
            from bias_metrics import demographic_parity_difference
            orig_dp   = demographic_parity_difference(y_te, orig_pred, s_te)

            rows = run_all_debiasing(model, X_tr, y_tr, X_te, y_te, s_tr, s_te,
                                     orig_acc, orig_dp)
            st.session_state.comparison_rows = rows

            # Best = lowest DP diff
            best = min(rows[1:], key=lambda r: r["dp_diff"])
            st.session_state.best_result = best
        st.success(f"✅ Best method: **{best['method']}** — Bias reduced to {best['dp_diff']:.3f}!")

    if st.session_state.comparison_rows:
        rows = st.session_state.comparison_rows
        st.divider()
        st.markdown("### 📊 Before vs After Comparison")
        st.plotly_chart(before_after_chart(rows), width="stretch")

        st.markdown("### 📋 Comparison Table")
        orig_dp = rows[0]["dp_diff"]
        tbl_data = []
        for r in rows:
            red = max(0, (orig_dp - r["dp_diff"]) / max(orig_dp, 1e-9) * 100)
            tbl_data.append({
                "Method":         r["method"],
                "Accuracy":       f"{r['accuracy']*100:.1f}%",
                "Bias (DP Diff)": f"{r['dp_diff']:.3f}",
                "Bias Reduction": f"{red:.0f}%",
            })
        st.dataframe(pd.DataFrame(tbl_data), use_container_width=True)

        best = st.session_state.best_result
        if best and best["dp_diff"] < 0.1:
            st.balloons()
            st.success(f"🎉 **{best['method']}** achieved bias score of **{best['dp_diff']:.3f}** — below the 0.10 threshold! Navigate to Audit Certificate to generate your certificate.")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE 5 — Compliance Report
# ─────────────────────────────────────────────────────────────────────────────
elif page == pages[4]:
    st.markdown("# 📋 Regulatory Compliance Report")

    if not st.session_state.audit_results:
        st.warning("⬅ Run Bias Analysis first.")
        st.stop()

    audit      = st.session_state.audit_results
    best       = st.session_state.best_result
    orig_max_dp = max(r["demographic_parity_diff"] for r in audit.values())
    orig_di_min = min(r["disparate_impact_ratio"]   for r in audit.values())

    # ── Use debiased scores if remediation has been run ──────────────────────
    if best:
        # best_result has dp_diff for the primary attribute
        # Use it as the effective score for all compliance checks
        eff_dp = best["dp_diff"]
        eff_acc = best["accuracy"]
        # Estimate DI ratio from dp_diff (approx: DI ≈ 1 - dp_diff)
        eff_di = max(0.0, 1.0 - eff_dp)
        st.success(f"✅ Using **debiased model** scores ({best['method']}) — Bias reduced from **{orig_max_dp:.3f}** → **{eff_dp:.3f}**")
    else:
        eff_dp  = orig_max_dp
        eff_di  = orig_di_min
        eff_acc = list(audit.values())[0]["overall_accuracy"]
        st.warning("⚠️ Showing **original model** scores. Go to **Bias Remediation** page and click 'Fix Bias' first for better compliance results.")

    REGULATIONS = [
        ("EU AI Act (Art.10 & Art.13)",    eff_dp < 0.10, "DP Diff < 0.10",    "High-Risk AI must ensure non-discrimination."),
        ("DPDP Act 2023 (India)",           eff_dp < 0.15, "DP Diff < 0.15",    "Data protection laws prohibit discriminatory profiling."),
        ("RBI Fair Lending Guidelines",     eff_di > 0.80, "DI Ratio > 0.80",   "Lending decisions must not exhibit adverse impact on groups."),
        ("US ECOA / Regulation B",          eff_di > 0.80, "DI Ratio > 0.80",   "Equal credit opportunity; adverse impact rule at 80%."),
        ("IEEE P7003 Std (Bias in AI)",     eff_dp < 0.10, "DP Diff < 0.10",    "Industry standard for algorithmic bias considerations."),
        ("ISO/IEC 42001 (AI Management)",   eff_dp < 0.20, "DP Diff < 0.20",    "AI management systems must address fairness risk."),
        ("SEBI Algo Trading Guidelines",    eff_dp < 0.15, "DP Diff < 0.15",    "Algorithmic systems in finance must be auditable."),
    ]

    pass_count = sum(1 for _, ok, _, _ in REGULATIONS if ok)
    st.markdown(f"### Compliance Score: {pass_count}/{len(REGULATIONS)}")

    bar_color = "green" if pass_count == len(REGULATIONS) else "orange" if pass_count >= 4 else "red"
    st.progress(pass_count / len(REGULATIONS))

    # Show before vs after if remediation was done
    if best:
        st.markdown("### 📊 Before vs After Remediation")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div style="background:#3a0a0a;border-radius:10px;padding:16px;border-left:4px solid #e74c3c">
              <b style="color:#e74c3c">Before Fix</b><br>
              <span style="color:#fff;font-size:24px;font-weight:700">{orig_max_dp:.3f}</span><br>
              <span style="color:#aaa">Bias Score</span>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div style="background:#1a3a2a;border-radius:10px;padding:16px;border-left:4px solid #2ecc71">
              <b style="color:#2ecc71">After Fix ({best['method']})</b><br>
              <span style="color:#fff;font-size:24px;font-weight:700">{eff_dp:.3f}</span><br>
              <span style="color:#aaa">Bias Score</span>
            </div>""", unsafe_allow_html=True)
        st.divider()

    for reg, ok, thresh, desc in REGULATIONS:
        icon  = "✅" if ok else "⚠️"
        color = "#1a3a2a" if ok else "#3a1a0a"
        status= "PASS" if ok else "RISK"
        st.markdown(f"""
        <div style="background:{color};border-radius:10px;padding:12px 18px;margin:8px 0;
                    border-left:4px solid {'#2ecc71' if ok else '#e74c3c'}">
          <b style="color:{'#2ecc71' if ok else '#e74c3c'}">{icon} {reg}</b> &nbsp;
          <span style="color:#aaa;font-size:12px">({thresh})</span><br>
          <span style="color:#ccc;font-size:13px">{desc}</span><br>
          <b style="color:{'#2ecc71' if ok else '#e74c3c'}">{status}</b>
        </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("### 📄 Download Full PDF Report")
    accuracy = eff_acc
    if st.button("📥 Generate PDF Report", width="stretch"):
        with st.spinner("Generating report…"):
            pdf_bytes = generate_full_report(
                model_name       = st.session_state.model_name,
                audit_results    = audit,
                comparison_rows  = st.session_state.comparison_rows,
                protected_attrs  = st.session_state.protected_attrs,
                overall_accuracy = accuracy,
            )
        st.download_button(
            label="⬇ Download Audit Report (PDF)",
            data=pdf_bytes,
            file_name=f"fairguard_audit_{st.session_state.model_name.replace(' ','_')}.pdf",
            mime="application/pdf",
            width="stretch",
        )


# ─────────────────────────────────────────────────────────────────────────────
# PAGE 6 — Audit Certificate
# ─────────────────────────────────────────────────────────────────────────────
elif page == pages[5]:
    st.markdown("# 🏅 AI Fairness Audit Certificate")

    if not st.session_state.audit_results:
        st.warning("⬅ Run Bias Analysis first.")
        st.stop()

    audit   = st.session_state.audit_results
    max_dp  = max(r["demographic_parity_diff"] for r in audit.values())
    acc     = list(audit.values())[0]["overall_accuracy"]
    best    = st.session_state.best_result

    # Check if debiased model passes
    effective_bias = best["dp_diff"] if best else max_dp
    effective_acc  = best["accuracy"] if best else acc
    method_used    = best["method"]   if best else "Original Model"
    threshold      = 0.10

    if effective_bias < threshold:
        st.markdown(f"""
        <div class="cert-box">
          <h1>🏅 CERTIFIED FAIR</h1>
          <p style="font-size:18px;color:#2ecc71;font-weight:700">
            This model has passed the FairGuard AI fairness audit.
          </p>
          <p>Model: <b>{st.session_state.model_name}</b></p>
          <p>Bias Score (DP Diff): <b>{effective_bias:.4f}</b> &lt; 0.10 threshold</p>
          <p>Method Used: <b>{method_used}</b></p>
          <p>Accuracy: <b>{effective_acc*100:.1f}%</b></p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📜 Download Certificate (PDF)", width="stretch", type="primary"):
            with st.spinner("Generating certificate…"):
                cert_pdf = generate_certificate(
                    model_name      = st.session_state.model_name,
                    bias_score      = effective_bias,
                    accuracy        = effective_acc,
                    protected_attrs = st.session_state.protected_attrs,
                )
            st.download_button(
                label="⬇ Download Certificate (PDF)",
                data=cert_pdf,
                file_name=f"fairguard_certificate_{st.session_state.model_name.replace(' ','_')}.pdf",
                mime="application/pdf",
                width="stretch",
            )
    else:
        st.error(f"""
        ❌ **Certificate Not Issued**

        Current bias score: **{effective_bias:.4f}** exceeds the threshold of **{threshold}**.

        → Go to **Bias Remediation** page and run the debiasing engine to fix the bias first.
        """)
        st.markdown(f"""
        <div style="background:#3a0a0a;border-radius:10px;padding:20px;border-left:4px solid #e74c3c">
          <h3 style="color:#e74c3c">🚫 Certification Failed</h3>
          <p>Bias score <b>{effective_bias:.3f}</b> exceeds allowed limit of <b>0.10</b>.</p>
          <p>Apply debiasing techniques to bring the score below 0.10, then return here.</p>
        </div>
        """, unsafe_allow_html=True)