"""
visualizations.py — All Plotly charts for the dashboard
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

PALETTE = px.colors.qualitative.Set2
RED     = "#e74c3c"
GREEN   = "#2ecc71"
ORANGE  = "#f39c12"
BLUE    = "#3498db"
BG      = "#0f1117"
CARD_BG = "#1e2130"

_layout = dict(
    paper_bgcolor=BG,
    plot_bgcolor=CARD_BG,
    font=dict(color="#e0e0e0", family="Inter, sans-serif"),
    margin=dict(l=40, r=30, t=50, b=40),
)


# ── 1. Approval rate by group ─────────────────────────────────────────────────
def approval_rate_chart(group_stats: dict, attr: str) -> go.Figure:
    groups = list(group_stats.keys())
    rates  = [v["ppr"] * 100 for v in group_stats.values()]
    colors = [GREEN if r >= 50 else RED for r in rates]

    fig = go.Figure(go.Bar(
        x=groups, y=rates,
        marker_color=colors,
        text=[f"{r:.1f}%" for r in rates],
        textposition="outside",
    ))
    fig.update_layout(
        title=f"Approval Rate by {attr}",
        yaxis_title="Approval Rate (%)",
        yaxis=dict(range=[0, 110]),
        **_layout,
    )
    return fig


# ── 2. Bias score radar chart ─────────────────────────────────────────────────
def bias_radar_chart(audit_results: dict) -> go.Figure:
    attrs   = list(audit_results.keys())
    dp_vals = [audit_results[a]["demographic_parity_diff"] for a in attrs]
    eo_vals = [audit_results[a]["equal_opportunity_diff"]  for a in attrs]
    pp_vals = [audit_results[a]["predictive_parity_diff"]  for a in attrs]

    fig = go.Figure()
    for label, vals, color in [
        ("Demographic Parity", dp_vals, RED),
        ("Equal Opportunity",  eo_vals, ORANGE),
        ("Predictive Parity",  pp_vals, BLUE),
    ]:
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=attrs + [attrs[0]],
            name=label,
            line=dict(color=color),
            fill="toself",
            fillcolor=color,
            opacity=0.3,
        ))
    fig.update_layout(
        title="Bias Score Radar",
        polar=dict(
            bgcolor=CARD_BG,
            radialaxis=dict(visible=True, range=[0, 0.5], color="#aaa"),
            angularaxis=dict(color="#aaa"),
        ),
        showlegend=True,
        **_layout,
    )
    return fig


# ── 3. Before vs After comparison bar ────────────────────────────────────────
def before_after_chart(comparison_rows: list) -> go.Figure:
    methods   = [r["method"] for r in comparison_rows]
    acc_vals  = [r["accuracy"] * 100 for r in comparison_rows]
    bias_vals = [r["dp_diff"] * 100  for r in comparison_rows]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Accuracy (%)", x=methods, y=acc_vals,
        marker_color=BLUE,
        text=[f"{v:.1f}%" for v in acc_vals], textposition="outside",
    ))
    fig.add_trace(go.Bar(
        name="Bias Score ×100", x=methods, y=bias_vals,
        marker_color=RED,
        text=[f"{v:.1f}" for v in bias_vals], textposition="outside",
    ))
    fig.update_layout(
        title="Before vs After Debiasing",
        barmode="group",
        yaxis_title="Value",
        yaxis=dict(range=[0, 110]),
        **_layout,
    )
    return fig


# ── 4. Feature importance bar ─────────────────────────────────────────────────
def feature_importance_chart(model, feature_cols: list) -> go.Figure:
    if not hasattr(model, "feature_importances_"):
        return go.Figure()

    importances = model.feature_importances_
    idx = np.argsort(importances)[::-1]
    names  = [feature_cols[i] for i in idx]
    values = [importances[i]  for i in idx]

    fig = go.Figure(go.Bar(
        x=values, y=names,
        orientation="h",
        marker_color=PALETTE[:len(names)],
        text=[f"{v*100:.1f}%" for v in values],
        textposition="outside",
    ))
    fig.update_layout(
        title="Feature Importance (SHAP Proxy)",
        xaxis_title="Importance",
        yaxis=dict(autorange="reversed"),
        **_layout,
    )
    return fig


# ── 5. Intersectional heatmap ─────────────────────────────────────────────────
def intersectional_heatmap(df: pd.DataFrame, attr1: str, attr2: str,
                            data: pd.DataFrame, y_pred) -> go.Figure:
    pivot = pd.DataFrame({attr1: data[attr1], attr2: data[attr2], "pred": y_pred})
    pt    = pivot.groupby([attr1, attr2])["pred"].mean().unstack(fill_value=0)

    fig = go.Figure(go.Heatmap(
        z=pt.values,
        x=list(pt.columns),
        y=list(pt.index),
        colorscale="RdYlGn",
        zmin=0, zmax=1,
        text=[[f"{v:.2f}" for v in row] for row in pt.values],
        texttemplate="%{text}",
        colorbar=dict(title="Approval Rate"),
    ))
    fig.update_layout(
        title=f"Approval Rate: {attr1} × {attr2}",
        xaxis_title=attr2,
        yaxis_title=attr1,
        **_layout,
    )
    return fig


# ── 6. Group disparity horizontal bar ────────────────────────────────────────
def disparity_bar(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return go.Figure()
    colors = [GREEN if v >= 0 else RED for v in df["Disparity"]]
    fig = go.Figure(go.Bar(
        x=df["Disparity"], y=df["Group"],
        orientation="h",
        marker_color=colors,
        text=[f"{v:+.3f}" for v in df["Disparity"]],
        textposition="outside",
    ))
    fig.add_vline(x=0, line_color="white", line_dash="dash")
    fig.update_layout(
        title="Approval Rate Disparity per Intersection Group",
        xaxis_title="Δ from Overall Mean",
        **_layout,
    )
    return fig


# ── 7. Bias gauge ─────────────────────────────────────────────────────────────
def bias_gauge(score: float, title: str = "Bias Score") -> go.Figure:
    color = GREEN if score < 0.05 else ORANGE if score < 0.1 else RED
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(score, 3),
        title={"text": title, "font": {"color": "#e0e0e0"}},
        gauge={
            "axis": {"range": [0, 0.5], "tickcolor": "#aaa"},
            "bar": {"color": color},
            "bgcolor": CARD_BG,
            "steps": [
                {"range": [0, 0.05],  "color": "#1a3a2a"},
                {"range": [0.05, 0.1],"color": "#3a2a0a"},
                {"range": [0.1, 0.5], "color": "#3a0a0a"},
            ],
            "threshold": {
                "line": {"color": "white", "width": 2},
                "thickness": 0.75,
                "value": 0.1,
            },
        },
        number={"font": {"color": color}},
    ))
    fig.update_layout(paper_bgcolor=BG, font=dict(color="#e0e0e0"),
                      margin=dict(l=20, r=20, t=60, b=20), height=220)
    return fig
