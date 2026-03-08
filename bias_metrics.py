"""
bias_metrics.py — Bias detection engine (Fairlearn-style metrics, pure numpy/sklearn)
"""
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix


# ─────────────────────────────────────────────
# Core fairness metrics
# ─────────────────────────────────────────────

def _group_rates(y_true, y_pred, sensitive):
    """Return per-group positive prediction rates and true-positive rates."""
    groups = {}
    for g in np.unique(sensitive):
        mask = sensitive == g
        yt, yp = y_true[mask], y_pred[mask]
        n = len(yt)
        if n == 0:
            continue
        ppr   = yp.mean()                            # positive prediction rate
        tpr   = yt[yp == 1].sum() / max(yt.sum(), 1) # recall / TPR
        ppv   = yt[yp == 1].sum() / max(yp.sum(), 1) # precision / PPV
        acc   = accuracy_score(yt, yp)
        groups[g] = {"n": n, "ppr": ppr, "tpr": tpr, "ppv": ppv, "acc": acc}
    return groups


def demographic_parity_difference(y_true, y_pred, sensitive):
    """Max – Min positive prediction rate across groups."""
    gr = _group_rates(y_true, y_pred, sensitive)
    pprs = [v["ppr"] for v in gr.values()]
    return round(max(pprs) - min(pprs), 4) if len(pprs) >= 2 else 0.0


def equal_opportunity_difference(y_true, y_pred, sensitive):
    """Max – Min TPR across groups."""
    gr = _group_rates(y_true, y_pred, sensitive)
    tprs = [v["tpr"] for v in gr.values()]
    return round(max(tprs) - min(tprs), 4) if len(tprs) >= 2 else 0.0


def predictive_parity_difference(y_true, y_pred, sensitive):
    """Max – Min PPV (precision) across groups."""
    gr = _group_rates(y_true, y_pred, sensitive)
    ppvs = [v["ppv"] for v in gr.values()]
    return round(max(ppvs) - min(ppvs), 4) if len(ppvs) >= 2 else 0.0


def disparate_impact_ratio(y_true, y_pred, sensitive):
    """Min PPR / Max PPR  (1.0 = perfect fairness, <0.8 = adverse impact)."""
    gr = _group_rates(y_true, y_pred, sensitive)
    pprs = [v["ppr"] for v in gr.values()]
    if not pprs or max(pprs) == 0:
        return 1.0
    return round(min(pprs) / max(pprs), 4)


# ─────────────────────────────────────────────
# Full audit per protected attribute
# ─────────────────────────────────────────────

def audit_attribute(y_true, y_pred, sensitive_series: pd.Series) -> dict:
    """Return full bias report for one sensitive attribute."""
    sensitive = sensitive_series.values
    gr = _group_rates(y_true, y_pred, sensitive)
    return {
        "group_stats":                  gr,
        "demographic_parity_diff":      demographic_parity_difference(y_true, y_pred, sensitive),
        "equal_opportunity_diff":       equal_opportunity_difference(y_true, y_pred, sensitive),
        "predictive_parity_diff":       predictive_parity_difference(y_true, y_pred, sensitive),
        "disparate_impact_ratio":       disparate_impact_ratio(y_true, y_pred, sensitive),
        "overall_accuracy":             round(accuracy_score(y_true, y_pred), 4),
    }


def run_full_audit(data: pd.DataFrame, y_true, y_pred,
                   protected_attrs: list) -> dict:
    """Run audit for all selected protected attributes."""
    results = {}
    for attr in protected_attrs:
        if attr in data.columns:
            results[attr] = audit_attribute(y_true, y_pred, data[attr])
    return results


# ─────────────────────────────────────────────
# Severity classification
# ─────────────────────────────────────────────

def classify_bias_severity(score: float) -> tuple[str, str]:
    """(label, color) for a bias score 0–1."""
    if score < 0.05:
        return "✅ Low", "#2ecc71"
    elif score < 0.10:
        return "⚠️ Moderate", "#f39c12"
    elif score < 0.20:
        return "🔴 High", "#e74c3c"
    else:
        return "🚨 Critical", "#8e1515"
