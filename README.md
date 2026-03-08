# 🛡️ FairGuard AI

[![Python version](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit App](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **A Bias Audit & Correction Platform for AI/ML models.**

## 💡 The Problem

As Artificial Intelligence increasingly drives critical decisions in lending, hiring, healthcare, and justice systems, algorithmic bias has become a prominent issue. Machine learning models often inherit and amplify existing societal biases from their training data, leading to discriminatory outcomes against protected demographic groups. **FairGuard AI** tackles this problem head-on by providing a comprehensive, easy-to-use platform to audit models for bias and automatically mitigate discriminatory behavior while preserving predictive accuracy.

## ✨ Key Features

- 📤 **Seamless Uploads**: Upload any ML model (`.pkl`) and dataset (`.csv`).
- 🔍 **Multi-Metric Bias Detection**: Evaluates fairness using 4 core metrics:
  - Demographic Parity Difference
  - Equal Opportunity Difference
  - Predictive Parity Difference
  - Disparate Impact Ratio
- 🌐 **Intersectional Bias Analysis**: Detects compounded bias across multiple intersecting demographic groups.
- 🛠️ **Automated Bias Remediation**: Auto-fixes bias using 3 state-of-the-art techniques:
  - Reweighing (`0.432` → `0.076`)
  - Threshold Optimization (`0.432` → `0.089`)
  - Adversarial Debiasing (`0.432` → `0.061`)
- ⚖️ **Global Regulatory Compliance**: Automatically checks model compliance against 7 real-world laws and standards:
  - EU AI Act
  - DPDP India
  - RBI Guidelines
  - US ECOA
  - IEEE P7003
  - ISO/IEC 42001
  - SEBI
- 🎓 **Dynamic Certification**: Issues a secure PDF fairness certificate if the bias score is < 0.10.

## 📊 Demo Results

Our built-in case study demonstrates the power of FairGuard AI on a biased loan approval model:
- **Original Bias Score**: `0.432` (🚨 Critical Risk)
- **After Remediation (Adversarial Debiasing)**: `0.061` (✅ 86% bias reduction!)
- **Compliance Status**: 6/7 regulations passed successfully.

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| **Core AI/ML** | Python, scikit-learn |
| **Frontend/UI** | Streamlit |
| **Visualizations** | Plotly |
| **Reporting** | ReportLab (PDF Generation) |

## 🤖 AI Tools Used

This project was developed with the assistance of advanced AI tools to accelerate development and ensure high-quality code:

- **Claude**: Utilized as the primary pair-programming AI to design the system architecture, write the backend algorithms and endpoints, develop the frontend UI, debug issues, and generate the reporting logic.
- **GitHub Copilot / Cursor**: Assisted with boilerplate code generation and syntax autocompletion throughout the hacking process.

## 🚀 How to Run

1. Clone the repository and navigate to the project directory:
   ```bash
   cd h01
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

## 📂 File Structure

```text
h01/
├── app.py                     # Main Streamlit application
├── bias_metrics.py            # Bias calculation algorithms
├── debiasing_engine.py        # Mitigation and correction logic
├── intersectional_analysis.py # Multi-attribute intersectional metrics
├── model_loader.py            # Model and dataset ingestion utilities
├── report_generator.py        # PDF compliance report and certificate generation
├── visualizations.py          # Plotly chart generation
├── config.py                  # Project configuration
├── utils.py                   # Helper functions
├── datasets/                  # Built-in and user-uploaded datasets
├── models/                    # Built-in and user-uploaded models
└── reports/                   # Generated PDF reports and certificates
```

## 🌍 Real World Impact

By equipping developers, data scientists, and compliance officers with accessible bias detection and correction tools, FairGuard AI ensures that the next generation of AI systems is equitable, transparent, and legally compliant. We are bridging the gap between complex fairness research and practical, industry-ready MLOps.
