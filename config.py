"""
config.py — Global configuration and constants for FairGuard AI
"""

# ── Bias thresholds ────────────────────────────────────────────────────────────
BIAS_THRESHOLDS = {
    "low":      0.05,   # below this = Low bias
    "moderate": 0.10,   # below this = Moderate
    "high":     0.20,   # below this = High
    # above 0.20 = Critical
}

CERTIFICATE_THRESHOLD = 0.10   # DP Diff must be below this to issue certificate
DISPARATE_IMPACT_MIN  = 0.80   # DI ratio must be above this (80% rule)

# ── Regulatory rules ───────────────────────────────────────────────────────────
REGULATIONS = [
    {
        "name":        "EU AI Act (Art.10 & Art.13)",
        "metric":      "dp_diff",
        "threshold":   0.10,
        "operator":    "<",
        "description": "High-risk AI systems must ensure non-discrimination and fairness.",
        "region":      "EU",
    },
    {
        "name":        "DPDP Act 2023 (India)",
        "metric":      "dp_diff",
        "threshold":   0.15,
        "operator":    "<",
        "description": "Data protection law prohibits discriminatory profiling of individuals.",
        "region":      "India",
    },
    {
        "name":        "RBI Fair Lending Guidelines",
        "metric":      "di_ratio",
        "threshold":   0.80,
        "operator":    ">",
        "description": "Lending decisions must not exhibit adverse impact on protected groups.",
        "region":      "India",
    },
    {
        "name":        "US ECOA / Regulation B",
        "metric":      "di_ratio",
        "threshold":   0.80,
        "operator":    ">",
        "description": "Equal credit opportunity; 80% adverse impact rule applies.",
        "region":      "USA",
    },
    {
        "name":        "IEEE P7003 (Algorithmic Bias)",
        "metric":      "dp_diff",
        "threshold":   0.10,
        "operator":    "<",
        "description": "Industry standard for identifying and addressing algorithmic bias.",
        "region":      "Global",
    },
    {
        "name":        "ISO/IEC 42001 (AI Management)",
        "metric":      "dp_diff",
        "threshold":   0.20,
        "operator":    "<",
        "description": "AI management systems must identify and mitigate fairness risks.",
        "region":      "Global",
    },
    {
        "name":        "SEBI Algo Trading Guidelines",
        "metric":      "dp_diff",
        "threshold":   0.15,
        "operator":    "<",
        "description": "Algorithmic systems in finance must be auditable and non-discriminatory.",
        "region":      "India",
    },
]

# ── Default protected attributes ───────────────────────────────────────────────
DEFAULT_PROTECTED_ATTRS = ["Gender", "Age", "Location", "Income", "Education"]

# ── Demo dataset settings ──────────────────────────────────────────────────────
DEMO_DATASET = {
    "n_samples":   1000,
    "random_seed": 42,
    "target_col":  "Loan_Status",
    "feature_cols": ["Gender", "Age", "Income", "Education", "Location"],
    "protected_attrs": ["Gender", "Age", "Income", "Location"],
}

# ── Model settings ─────────────────────────────────────────────────────────────
MODEL_SETTINGS = {
    "n_estimators": 100,
    "random_state": 42,
    "test_size":    0.20,
}

# ── Report settings ────────────────────────────────────────────────────────────
REPORT_SETTINGS = {
    "output_dir":    "reports/",
    "company_name":  "FairGuard AI",
    "platform_name": "Bias Audit & Correction Platform",
}

# ── UI Colours ─────────────────────────────────────────────────────────────────
COLORS = {
    "low":      "#2ecc71",
    "moderate": "#f39c12",
    "high":     "#e74c3c",
    "critical": "#8e1515",
    "accent":   "#3498db",
    "bg":       "#0f1117",
    "card_bg":  "#1e2130",
}