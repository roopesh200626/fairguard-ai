# 📊 Datasets Directory

This directory stores the datasets used by FairGuard AI for bias auditing and remediation.

## 📁 Built-in Demo Dataset

The demo dataset simulates a **Loan Approval** scenario where applicants are evaluated for creditworthiness.

### Dataset Columns
- **Features**: `Income`, `Credit_Score`, `Loan_Amount`, `Years_Employed`
- **Protected Attributes**: `Gender`, `Age`, `Race`, `Education`
- **Target Label**: `Loan_Status` (1 = Approved, 0 = Rejected)

### ⚠️ Built-in Bias & Why It Exists
The demo dataset contains historically injected bias against certain demographic groups (e.g., females and younger applicants). This bias exists because historical lending practices often reflect societal inequalities, and models trained on such data will learn and reproduce these disparities. Evaluating this dataset showcases FairGuard AI's ability to detect and mitigate severe algorithmic discrimination.

## 🚀 How to Use Your Own Dataset

1. Place your `.csv` file in this directory (or upload it directly via the UI).
2. Ensure your dataset contains:
   - Your feature columns
   - At least one protected demographic attribute (e.g., Gender, Race)
   - The true target labels (ground truth)
3. Load the dataset in the application to evaluate your model's predictions against the protected attributes.
