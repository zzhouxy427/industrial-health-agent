"""Distribution-shift checks for model input monitoring."""

import numpy as np
import pandas as pd


def population_stability_index(
    reference: pd.Series, current: pd.Series, bins: int = 10
) -> float:
    """Calculate PSI between a reference feature distribution and a new batch."""
    reference_values = reference.dropna().to_numpy(dtype=float)
    current_values = current.dropna().to_numpy(dtype=float)
    if len(reference_values) == 0 or len(current_values) == 0:
        raise ValueError("PSI requires non-empty reference and current values")

    if np.ptp(reference_values) == 0:
        return 0.0 if np.all(current_values == reference_values[0]) else float("inf")

    edges = np.unique(np.quantile(reference_values, np.linspace(0, 1, bins + 1)))
    edges[0] = -np.inf
    edges[-1] = np.inf
    reference_share = np.histogram(reference_values, bins=edges)[0] / len(reference_values)
    current_share = np.histogram(current_values, bins=edges)[0] / len(current_values)

    epsilon = 1e-6
    reference_share = np.clip(reference_share, epsilon, None)
    current_share = np.clip(current_share, epsilon, None)
    return float(np.sum((current_share - reference_share) * np.log(current_share / reference_share)))


def assess_feature_drift(
    reference: pd.DataFrame, current: pd.DataFrame, feature_columns: list[str]
) -> pd.DataFrame:
    """Return PSI and an interpretable status for each monitored feature."""
    records = []
    for feature in feature_columns:
        psi = population_stability_index(reference[feature], current[feature])
        if psi >= 0.25:
            status = "significant"
        elif psi >= 0.10:
            status = "moderate"
        else:
            status = "stable"
        records.append({"feature": feature, "psi": psi, "status": status})
    return pd.DataFrame(records).sort_values("psi", ascending=False).reset_index(drop=True)
