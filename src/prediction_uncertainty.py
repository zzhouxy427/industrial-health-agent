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
