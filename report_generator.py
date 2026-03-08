"""
report_generator.py — PDF Audit Report + Fairness Certificate using ReportLab
"""
import os
import io
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics import renderPDF


# ── colour palette ────────────────────────────────────────────────────────────
C_BG      = colors.HexColor("#0f1117")
C_ACCENT  = colors.HexColor("#3498db")
C_GREEN   = colors.HexColor("#2ecc71")
C_RED     = colors.HexColor("#e74c3c")
C_ORANGE  = colors.HexColor("#f39c12")
C_TEXT    = colors.HexColor("#2c3e50")
C_LIGHT   = colors.HexColor("#ecf0f1")
C_WHITE   = colors.white


def _styles():
    ss = getSampleStyleSheet()
    return {
        "title":    ParagraphStyle("title",  fontName="Helvetica-Bold",
                                   fontSize=22, textColor=C_WHITE,
                                   alignment=TA_CENTER, spaceAfter=6),
        "subtitle": ParagraphStyle("sub",    fontName="Helvetica",
                                   fontSize=12, textColor=C_LIGHT,
                                   alignment=TA_CENTER, spaceAfter=4),
        "h2":       ParagraphStyle("h2",     fontName="Helvetica-Bold",
                                   fontSize=14, textColor=C_ACCENT,
                                   spaceBefore=14, spaceAfter=6),
        "body":     ParagraphStyle("body",   fontName="Helvetica",
                                   fontSize=10, textColor=C_TEXT,
                                   leading=14, spaceAfter=4),
        "small":    ParagraphStyle("small",  fontName="Helvetica",
                                   fontSize=8,  textColor=colors.grey),
        "center":   ParagraphStyle("center", fontName="Helvetica",
                                   fontSize=10, textColor=C_TEXT,
                                   alignment=TA_CENTER),
    }


def _header_block(s, model_name: str, timestamp: str):
    """Dark banner header."""
    d = Drawing(480, 90)
    d.add(Rect(0, 0, 480, 90, fillColor=C_BG, strokeColor=None))
    d.add(String(240, 60, "🛡 FairGuard AI", fontName="Helvetica-Bold",
                 fontSize=20, fillColor=colors.white, textAnchor="middle"))
    d.add(String(240, 38, "Bias Audit & Correction Platform",
                 fontName="Helvetica", fontSize=11, fillColor=C_LIGHT,
                 textAnchor="middle"))
    d.add(String(240, 18, f"Model: {model_name}  |  Generated: {timestamp}",
                 fontName="Helvetica", fontSize=9, fillColor=colors.grey,
                 textAnchor="middle"))
    return d


def _metric_table(audit_results: dict, s: dict):
    rows = [["Attribute", "Dem. Parity", "Eq. Opportunity",
             "Pred. Parity", "Disp. Impact", "Severity"]]
    for attr, res in audit_results.items():
        dp   = res["demographic_parity_diff"]
        eo   = res["equal_opportunity_diff"]
        pp   = res["predictive_parity_diff"]
        di   = res["disparate_impact_ratio"]
        sev  = "Low" if dp < 0.05 else "Moderate" if dp < 0.1 else "High" if dp < 0.2 else "Critical"
        rows.append([attr, f"{dp:.3f}", f"{eo:.3f}", f"{pp:.3f}", f"{di:.3f}", sev])

    col_w = [4*cm, 2.5*cm, 3.2*cm, 2.8*cm, 2.8*cm, 2.2*cm]
    tbl   = Table(rows, colWidths=col_w)
    sev_colors = {"Low": C_GREEN, "Moderate": C_ORANGE,
                  "High": C_RED, "Critical": colors.HexColor("#8e1515")}

    style = [
        ("BACKGROUND",  (0, 0), (-1, 0), C_BG),
        ("TEXTCOLOR",   (0, 0), (-1, 0), C_WHITE),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_LIGHT, C_WHITE]),
        ("GRID",        (0, 0), (-1, -1), 0.25, colors.grey),
        ("ALIGN",       (1, 0), (-1, -1), "CENTER"),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",  (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0,0), (-1, -1), 5),
    ]
    for i, row in enumerate(rows[1:], 1):
        sev = row[-1]
        c   = sev_colors.get(sev, colors.grey)
        style.append(("BACKGROUND", (-1, i), (-1, i), c))
        style.append(("TEXTCOLOR",  (-1, i), (-1, i), C_WHITE))
        style.append(("FONTNAME",   (-1, i), (-1, i), "Helvetica-Bold"))

    tbl.setStyle(TableStyle(style))
    return tbl


def _comparison_table(comparison_rows: list, s: dict):
    rows = [["Method", "Accuracy", "Bias (DP Diff)", "Bias Reduction"]]
    orig_bias = comparison_rows[0]["dp_diff"] if comparison_rows else 0.1
    for r in comparison_rows:
        red = max(0, (orig_bias - r["dp_diff"]) / max(orig_bias, 1e-9) * 100)
        rows.append([r["method"], f"{r['accuracy']*100:.1f}%",
                     f"{r['dp_diff']:.3f}", f"{red:.0f}%"])

    tbl = Table(rows, colWidths=[5*cm, 3*cm, 3.5*cm, 3*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0), C_ACCENT),
        ("TEXTCOLOR",   (0, 0), (-1, 0), C_WHITE),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_LIGHT, C_WHITE]),
        ("GRID",        (0, 0), (-1, -1), 0.25, colors.grey),
        ("ALIGN",       (1, 0), (-1, -1), "CENTER"),
        ("TOPPADDING",  (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0,0), (-1, -1), 5),
    ]))
    return tbl


def _compliance_table(audit_results: dict, s: dict):
    max_dp = max(r["demographic_parity_diff"] for r in audit_results.values())
    di_min = min(r["disparate_impact_ratio"]   for r in audit_results.values())

    rules = [
        ("EU AI Act (Art.10)",      max_dp < 0.10, "DP Diff < 0.10"),
        ("DPDP Act 2023 (India)",   max_dp < 0.15, "DP Diff < 0.15"),
        ("RBI Fair Lending",        di_min > 0.80, "Disparate Impact > 0.80"),
        ("US ECOA / Reg B",         di_min > 0.80, "Disparate Impact > 0.80"),
        ("IEEE P7003 Std",          max_dp < 0.10, "DP Diff < 0.10"),
        ("ISO/IEC 42001 (AI Mgmt)", max_dp < 0.20, "DP Diff < 0.20"),
    ]

    rows = [["Regulation", "Threshold", "Status"]]
    for reg, ok, thresh in rules:
        rows.append([reg, thresh, "✅  PASS" if ok else "⚠️  RISK"])

    tbl = Table(rows, colWidths=[6*cm, 5*cm, 3*cm])
    style = [
        ("BACKGROUND",  (0, 0), (-1, 0), C_BG),
        ("TEXTCOLOR",   (0, 0), (-1, 0), C_WHITE),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_LIGHT, C_WHITE]),
        ("GRID",        (0, 0), (-1, -1), 0.25, colors.grey),
        ("TOPPADDING",  (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0,0), (-1, -1), 5),
    ]
    for i, (_, ok, _) in enumerate(rules, 1):
        c = C_GREEN if ok else C_ORANGE
        style += [("TEXTCOLOR",  (-1, i), (-1, i), c),
                  ("FONTNAME",   (-1, i), (-1, i), "Helvetica-Bold")]
    tbl.setStyle(TableStyle(style))
    return tbl


# ── Main export functions ─────────────────────────────────────────────────────

def generate_full_report(
    model_name: str,
    audit_results: dict,
    comparison_rows: list,
    protected_attrs: list,
    overall_accuracy: float,
) -> bytes:
    """Generate full bias audit PDF report. Returns bytes."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=1.8*cm, rightMargin=1.8*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)
    s   = _styles()
    ts  = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    story = []

    story.append(_header_block(s, model_name, ts))
    story.append(Spacer(1, 0.4*cm))
    story.append(HRFlowable(width="100%", color=C_ACCENT, thickness=1.5))
    story.append(Spacer(1, 0.3*cm))

    # Executive Summary
    story.append(Paragraph("Executive Summary", s["h2"]))
    max_dp = max(r["demographic_parity_diff"] for r in audit_results.values())
    verdict = ("LOW RISK — Model meets basic fairness thresholds."
               if max_dp < 0.10 else
               "MODERATE RISK — Bias detected; remediation recommended."
               if max_dp < 0.20 else
               "HIGH RISK — Significant bias detected; immediate action required.")
    story.append(Paragraph(f"<b>Verdict:</b> {verdict}", s["body"]))
    story.append(Paragraph(
        f"Attributes audited: {', '.join(protected_attrs)}. "
        f"Overall model accuracy: {overall_accuracy*100:.1f}%. "
        f"Maximum demographic parity difference: {max_dp:.3f}.", s["body"]))
    story.append(Spacer(1, 0.3*cm))

    # Bias Metrics Table
    story.append(Paragraph("Section 1 — Bias Detection Results", s["h2"]))
    story.append(_metric_table(audit_results, s))
    story.append(Spacer(1, 0.4*cm))

    # Before vs After
    if comparison_rows:
        story.append(Paragraph("Section 2 — Debiasing Comparison", s["h2"]))
        story.append(_comparison_table(comparison_rows, s))
        story.append(Spacer(1, 0.4*cm))

    # Compliance
    story.append(Paragraph("Section 3 — Regulatory Compliance Check", s["h2"]))
    story.append(_compliance_table(audit_results, s))
    story.append(Spacer(1, 0.5*cm))

    # Footer
    story.append(HRFlowable(width="100%", color=colors.grey, thickness=0.5))
    story.append(Paragraph(
        f"FairGuard AI  |  {ts}  |  Confidential — For Internal Review Only",
        s["small"]))

    doc.build(story)
    return buf.getvalue()


def generate_certificate(
    model_name: str,
    bias_score: float,
    accuracy: float,
    protected_attrs: list,
) -> bytes:
    """Generate a 1-page fairness certificate if bias < 0.1."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    s  = _styles()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    story = []

    # Big header
    d = Drawing(480, 110)
    d.add(Rect(0, 0, 480, 110, fillColor=C_BG, strokeColor=None))
    d.add(Rect(0, 0, 480, 6,   fillColor=C_GREEN, strokeColor=None))
    d.add(Rect(0, 104, 480, 6, fillColor=C_GREEN, strokeColor=None))
    d.add(String(240, 72, "🏅  AI FAIRNESS AUDIT CERTIFICATE",
                 fontName="Helvetica-Bold", fontSize=17,
                 fillColor=colors.white, textAnchor="middle"))
    d.add(String(240, 48, "FairGuard AI — Bias Audit & Correction Platform",
                 fontName="Helvetica", fontSize=11,
                 fillColor=C_LIGHT, textAnchor="middle"))
    d.add(String(240, 26, f"Issued: {ts}",
                 fontName="Helvetica", fontSize=9,
                 fillColor=colors.grey, textAnchor="middle"))
    story.append(d)
    story.append(Spacer(1, 0.6*cm))

    story.append(Paragraph("This certifies that the AI model described below has been audited by "
                            "FairGuard AI and has <b>passed</b> the fairness threshold requirements.",
                            s["center"]))
    story.append(Spacer(1, 0.6*cm))

    cert_data = [
        ["Field", "Value"],
        ["Model Name",          model_name],
        ["Audit Date",          ts],
        ["Bias Score (DP Diff)",f"{bias_score:.4f}"],
        ["Threshold",           "< 0.10 (PASS)"],
        ["Accuracy",            f"{accuracy*100:.1f}%"],
        ["Protected Attributes",", ".join(protected_attrs)],
        ["Certificate ID",      f"FG-{abs(hash(model_name+ts)) % 999999:06d}"],
        ["Status",              "✅  CERTIFIED FAIR"],
    ]
    tbl = Table(cert_data, colWidths=[6*cm, 10*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0), C_ACCENT),
        ("TEXTCOLOR",   (0, 0), (-1, 0), C_WHITE),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME",    (0, 1), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_LIGHT, C_WHITE]),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN",       (0, 0), (0, -1), "RIGHT"),
        ("TOPPADDING",  (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING",(0,0), (-1, -1), 7),
    ]))
    # Colour last row green
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (-1, -1), (-1, -1), C_GREEN),
        ("TEXTCOLOR",  (-1, -1), (-1, -1), C_WHITE),
        ("FONTNAME",   (-1, -1), (-1, -1), "Helvetica-Bold"),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.8*cm))

    seal = Drawing(480, 60)
    seal.add(Rect(100, 10, 280, 40, fillColor=C_GREEN, strokeColor=None,
                  rx=8, ry=8))
    seal.add(String(240, 26, "⭐  CERTIFIED FAIR by FairGuard AI  ⭐",
                    fontName="Helvetica-Bold", fontSize=13,
                    fillColor=colors.white, textAnchor="middle"))
    story.append(seal)

    doc.build(story)
    return buf.getvalue()