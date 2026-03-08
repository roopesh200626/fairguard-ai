# 🧠 Models Directory

This directory manages the Machine Learning models evaluated by FairGuard AI.

## 🤖 Demo Model Description

The included demo model is a pre-trained **Random Forest Classifier** trained on the biased loan approval dataset. It achieves high overall accuracy but exhibits critical discrimination against minority subgroups, demonstrating a high Demographic Parity Difference (0.432).

## ✅ Supported Model Types

FairGuard AI supports a wide range of ML models. As long as the model exposes standard `scikit-learn` API methods, it can be audited:
- `sklearn` classifiers (Random Forest, Logistic Regression, SVM, etc.)
- XGBoost / LightGBM
- Any custom model wrapper exposing a `.predict()` and `.predict_proba()` method.

## 🚀 How to Use Your Own Model

1. Train your model using your preferred framework.
2. Export your trained model as a serialized `.pkl` file using `pickle` or `joblib`.
3. Place your model in this directory (or upload it via the UI).
4. Run FairGuard AI and select your model to instantly generate a comprehensive fairness audit.
