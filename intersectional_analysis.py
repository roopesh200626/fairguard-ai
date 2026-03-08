"""
intersectional_analysis.py — Detect bias across combinations of protected attributes
"""
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from bias_metrics import _group_rates, classify_bias_severity


def build_intersection_groups(data: pd.DataFrame, attrs: list) -> pd.Series:
    """Combine selected attributes into a single intersection label."""
    combined = data[attrs[0]].astype(str)
    for attr in attrs[1:]:
        combined = combined + " + " + data[attr].astype(str)
    return combined


def intersectional_audit(data: pd.DataFrame, y_true, y_pred,
                          attrs: list, min_group_size: int = 20) -> pd.DataFrame:
    """
    Compute approval rate and bias metrics for every intersection group.
    Returns a sorted DataFrame.
    """
    if len(attrs) < 2:
        return pd.DataFrame()

    groups = build_intersection_groups(data, attrs)
    rows = []

    for grp_name in groups.unique():
        mask = (groups == grp_name).values
        if mask.sum() < min_group_size:
            continue
        yt = y_true[mask]
        yp = y_pred[mask]
        n  = len(yt)
        approval_rate = yp.mean()
        actual_rate   = yt.mean()
        tpr = (yt[yp == 1].sum() / max(yt.sum(), 1))
        acc = accuracy_score(yt, yp)
        rows.append({
            "Group":          grp_name,
            "Count":          n,
            "Approval Rate":  round(approval_rate, 3),
            "Actual Rate":    round(actual_rate, 3),
            "TPR":            round(tpr, 3),
            "Accuracy":       round(acc, 3),
        })

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows).sort_values("Approval Rate", ascending=True)
    overall_rate = y_pred.mean()
    df["Disparity"] = (df["Approval Rate"] - overall_rate).round(3)
    label_col, color_col = [], []
    for _, row in df.iterrows():
        score = abs(row["Disparity"])
        label, color = classify_bias_severity(score)
        label_col.append(label)
        color_col.append(color)
    df["Severity"] = label_col
    return df.reset_index(drop=True)


def highest_bias_group(df: pd.DataFrame) -> dict:
    """Return the group with the most negative disparity."""
    if df.empty:
        return {}
    worst = df.loc[df["Disparity"].idxmin()]
    return worst.to_dict()


def most_favoured_group(df: pd.DataFrame) -> dict:
    """Return the most advantaged group."""
    if df.empty:
        return {}
    best = df.loc[df["Disparity"].idxmax()]
    return best.to_dict()
