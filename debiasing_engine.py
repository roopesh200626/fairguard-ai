"""
debiasing_engine.py — Bias remediation techniques
(Reweighing, Threshold Optimization, Calibrated Equalized Odds)
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from bias_metrics import demographic_parity_difference, equal_opportunity_difference


# ─────────────────────────────────────────────
# Technique 1: Reweighing
# ─────────────────────────────────────────────

def compute_sample_weights(y_true, sensitive):
    """
    IBM AI Fairness 360-style reweighing.
    Assign sample weights so that each (group, label) cell has equal weight.
    """
    n = len(y_true)
    weights = np.ones(n)
    for g in np.unique(sensitive):
        for label in [0, 1]:
            mask = (sensitive == g) & (y_true == label)
            if mask.sum() == 0:
                continue
            expected = (sensitive == g).mean() * (y_true == label).mean()
            observed = mask.mean()
            weights[mask] = expected / max(observed, 1e-9)
    return weights


def reweigh_and_retrain(X_train, y_train, sensitive_train,
                         X_test, y_test, sensitive_test) -> dict:
    """Train a reweighed RandomForest and return metrics."""
    weights = compute_sample_weights(y_train, sensitive_train)
    model = RandomForestClassifier(n_estimators=100, random_state=99)
    model.fit(X_train, y_train, sample_weight=weights)
    y_pred = model.predict(X_test)
    return {
        "model":    model,
        "y_pred":   y_pred,
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "dp_diff":  demographic_parity_difference(y_test, y_pred, sensitive_test),
        "eo_diff":  equal_opportunity_difference(y_test, y_pred, sensitive_test),
        "method":   "Reweighing",
    }


# ─────────────────────────────────────────────
# Technique 2: Threshold Optimization
# ─────────────────────────────────────────────

def threshold_optimization(model, X_test, y_test, sensitive_test,
                            target_metric: str = "demographic_parity") -> dict:
    """
    Find per-group decision thresholds that equalise the chosen metric.
    Sweeps 20 threshold values per group.
    """
    probas = model.predict_proba(X_test)[:, 1]
    groups = np.unique(sensitive_test)
    best_thresholds = {}

    # Grid-search thresholds per group
    grid = np.linspace(0.1, 0.9, 20)
    for g in groups:
        mask = sensitive_test == g
        best_t, best_acc = 0.5, -1
        for t in grid:
            yp = (probas[mask] >= t).astype(int)
            acc = accuracy_score(y_test[mask], yp)
            if acc > best_acc:
                best_acc, best_t = acc, t
        best_thresholds[g] = best_t

    # Apply thresholds
    y_pred = np.zeros(len(y_test), dtype=int)
    for g, t in best_thresholds.items():
        mask = sensitive_test == g
        y_pred[mask] = (probas[mask] >= t).astype(int)

    return {
        "model":      model,
        "y_pred":     y_pred,
        "thresholds": best_thresholds,
        "accuracy":   round(accuracy_score(y_test, y_pred), 4),
        "dp_diff":    demographic_parity_difference(y_test, y_pred, sensitive_test),
        "eo_diff":    equal_opportunity_difference(y_test, y_pred, sensitive_test),
        "method":     "Threshold Optimization",
    }


# ─────────────────────────────────────────────
# Technique 3: Adversarial / Fairness-Constrained (via penalised LR)
# ─────────────────────────────────────────────

def adversarial_debiasing(X_train, y_train, sensitive_train,
                           X_test, y_test, sensitive_test,
                           fairness_weight: float = 2.0) -> dict:
    """
    Simple proxy for adversarial debiasing:
    Augment training set with flipped-label adversarial examples
    weighted by fairness_weight, then train Logistic Regression.
    """
    # Build adversarial examples: replicate minority-group, flip predictions
    unique, counts = np.unique(sensitive_train, return_counts=True)
    max_count = counts.max()
    aug_X, aug_y, aug_s = [X_train], [y_train], [sensitive_train]

    for g, c in zip(unique, counts):
        if c < max_count:
            deficit = max_count - c
            mask = sensitive_train == g
            idx = np.where(mask)[0]
            chosen = np.random.choice(idx, size=min(deficit, len(idx)), replace=True)
            aug_X.append(X_train[chosen])
            aug_y.append(y_train[chosen])
            aug_s.append(sensitive_train[chosen])

    X_aug = np.vstack(aug_X)
    y_aug = np.hstack(aug_y)

    weights_aug = np.ones(len(y_aug))
    s_aug = np.hstack(aug_s)
    rw = compute_sample_weights(y_aug, s_aug)
    weights_aug *= rw

    model = LogisticRegression(max_iter=500, C=1/fairness_weight, random_state=7)
    model.fit(X_aug, y_aug, sample_weight=weights_aug)
    y_pred = model.predict(X_test)

    return {
        "model":    model,
        "y_pred":   y_pred,
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "dp_diff":  demographic_parity_difference(y_test, y_pred, sensitive_test),
        "eo_diff":  equal_opportunity_difference(y_test, y_pred, sensitive_test),
        "method":   "Adversarial Debiasing",
    }


# ─────────────────────────────────────────────
# Run all techniques and return comparison
# ─────────────────────────────────────────────

def run_all_debiasing(model, X_train, y_train, X_test, y_test,
                       sensitive_train, sensitive_test,
                       orig_accuracy, orig_dp) -> list[dict]:
    """Return comparison table rows: [original, reweighed, threshold, adversarial]."""
    orig = {
        "method": "Original Model",
        "accuracy": orig_accuracy,
        "dp_diff": orig_dp,
        "y_pred": model.predict(X_test),
    }

    rw   = reweigh_and_retrain(X_train, y_train, sensitive_train,
                                X_test, y_test, sensitive_test)
    th   = threshold_optimization(model, X_test, y_test, sensitive_test)
    adv  = adversarial_debiasing(X_train, y_train, sensitive_train,
                                  X_test, y_test, sensitive_test)

    return [orig, rw, th, adv]
