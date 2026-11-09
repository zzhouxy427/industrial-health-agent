"""Prediction intervals derived from the individual trees in a random forest."""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor


def predict_with_uncertainty(
    model: RandomForestRegressor, features: pd.DataFrame
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return mean prediction, 10th/90th percentiles, and tree spread."""
    tree_predictions = np.vstack(
        [tree.predict(features.to_numpy()) for tree in model.estimators_]
    )
    return (
        tree_predictions.mean(axis=0),
        np.percentile(tree_predictions, 10, axis=0),
        np.percentile(tree_predictions, 90, axis=0),
        tree_predictions.std(axis=0),
    )


def evaluate_interval_coverage(
    actual: np.ndarray, lower: np.ndarray, upper: np.ndarray
) -> dict[str, float | int]:
    """Measure empirical coverage and width of a prediction interval."""
    actual_values = np.asarray(actual, dtype=float)
    lower_values = np.asarray(lower, dtype=float)
    upper_values = np.asarray(upper, dtype=float)
    if not (len(actual_values) == len(lower_values) == len(upper_values)):
        raise ValueError("actual, lower, and upper must have equal length")
    if np.any(lower_values > upper_values):
        raise ValueError("lower interval bounds must not exceed upper bounds")

    covered = (actual_values >= lower_values) & (actual_values <= upper_values)
    below_lower = actual_values < lower_values
    above_upper = actual_values > upper_values
    return {
        "sample_count": int(len(actual_values)),
        "coverage": float(covered.mean()) if len(actual_values) else 0.0,
        "mean_width": float((upper_values - lower_values).mean())
        if len(actual_values)
        else 0.0,
        "below_lower_count": int(below_lower.sum()),
        "above_upper_count": int(above_upper.sum()),
    }


def estimate_conformal_adjustment(
    actual: np.ndarray, lower: np.ndarray, upper: np.ndarray, coverage: float = 0.80
) -> float:
    """Estimate a split-conformal expansion for an existing prediction interval.

    The calibration values must be independent of the model-fitting data. The
    returned non-negative offset expands both interval bounds and is selected
    with the finite-sample conformal quantile rule.
    """
    if not 0 < coverage < 1:
        raise ValueError("coverage must be between 0 and 1")
    actual_values = np.asarray(actual, dtype=float)
    lower_values = np.asarray(lower, dtype=float)
    upper_values = np.asarray(upper, dtype=float)
    if not (len(actual_values) == len(lower_values) == len(upper_values)):
        raise ValueError("actual, lower, and upper must have equal length")
    if len(actual_values) == 0:
        raise ValueError("calibration data must not be empty")
    if np.any(lower_values > upper_values):
        raise ValueError("lower interval bounds must not exceed upper bounds")

    scores = np.maximum.reduce(
        [lower_values - actual_values, actual_values - upper_values, np.zeros(len(actual_values))]
    )
    quantile = min(np.ceil((len(scores) + 1) * coverage) / len(scores), 1.0)
    return float(np.quantile(scores, quantile, method="higher"))


def apply_conformal_adjustment(
    lower: np.ndarray, upper: np.ndarray, adjustment: float
) -> tuple[np.ndarray, np.ndarray]:
    """Expand bounds by a calibrated offset and enforce non-negative RUL."""
    if adjustment < 0:
        raise ValueError("adjustment must not be negative")
    lower_values = np.asarray(lower, dtype=float)
    upper_values = np.asarray(upper, dtype=float)
    if np.any(lower_values > upper_values):
        raise ValueError("lower interval bounds must not exceed upper bounds")
    return np.maximum(lower_values - adjustment, 0.0), upper_values + adjustment
