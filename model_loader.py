"""
model_loader.py — Load pre-trained ML models and datasets
"""
import pickle
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
import io


def load_model_from_bytes(file_bytes: bytes):
    """Load a pickled model from bytes."""
    return pickle.loads(file_bytes)


def load_dataset_from_bytes(file_bytes: bytes) -> pd.DataFrame:
    """Load CSV dataset from bytes."""
    return pd.read_csv(io.BytesIO(file_bytes))


def load_demo_model_and_data():
    """
    Generate and return a demo biased loan approval model + dataset.
    Returns: (model, data, feature_cols, target_col)
    """
    np.random.seed(42)
    n = 1000

    gender      = np.random.choice(["Male","Female"], n, p=[0.55, 0.45])
    age         = np.random.randint(22, 65, n)
    income      = np.where(gender == "Male",
                           np.random.randint(30000, 120000, n),
                           np.random.randint(20000, 90000, n))
    education   = np.random.choice(["High School","Bachelor","Master","PhD"], n,
                                   p=[0.3, 0.4, 0.2, 0.1])
    location    = np.random.choice(["Urban","Rural","Suburban"], n,
                                   p=[0.5, 0.25, 0.25])

    prob = (
        (income > 50000).astype(float) * 0.40 +
        (education == "Master").astype(float) * 0.20 +
        (education == "PhD").astype(float) * 0.25 +
        (gender == "Male").astype(float) * 0.15 +   # intentional bias
        (location == "Urban").astype(float) * 0.10 +
        (age < 40).astype(float) * 0.10
    )
    prob = np.clip(prob, 0, 1)
    loan_status = (np.random.random(n) < prob).astype(int)

    data = pd.DataFrame({
        "Gender": gender, "Age": age, "Income": income,
        "Education": education, "Location": location,
        "Loan_Status": loan_status
    })

    # Encode for training
    le_map = {}
    data_enc = data.copy()
    for col in ["Gender", "Education", "Location"]:
        le = LabelEncoder()
        data_enc[col] = le.fit_transform(data_enc[col])
        le_map[col] = le

    feature_cols = ["Gender", "Age", "Income", "Education", "Location"]
    target_col   = "Loan_Status"
    X = data_enc[feature_cols].values
    y = data_enc[target_col].values

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    model.le_map        = le_map
    model.feature_cols  = feature_cols
    model.target_col    = target_col

    return model, data, feature_cols, target_col


def prepare_features(data: pd.DataFrame, feature_cols: list, le_map: dict = None):
    """Encode categorical columns and return numpy array."""
    df = data[feature_cols].copy()
    if le_map:
        for col, le in le_map.items():
            if col in df.columns:
                df[col] = df[col].apply(
                    lambda x: le.transform([x])[0]
                    if x in le.classes_ else -1
                )
    return df.values
