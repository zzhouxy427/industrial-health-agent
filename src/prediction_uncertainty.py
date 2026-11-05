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
