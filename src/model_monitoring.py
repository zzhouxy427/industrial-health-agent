"""Reusable batch-level model-input monitoring utilities."""

import pandas as pd

try:
    from .data_drift import assess_feature_drift
    from .data_quality import FEATURE_COLUMNS, load_raw
except ImportError:  # Supports direct execution from src scripts.
    from data_drift import assess_feature_drift
    from data_quality import FEATURE_COLUMNS, load_raw


def summarize_drift(drift: pd.DataFrame) -> dict:
    """Create a compact, JSON-safe applicability summary from PSI results."""
    significant = drift.loc[drift["status"] == "significant"]
    moderate = drift.loc[drift["status"] == "moderate"]
    return {
        "significant_feature_count": int(len(significant)),
        "moderate_feature_count": int(len(moderate)),
        "warning": not significant.empty,
        "top_shifted_features": [
            {"feature": row.feature, "psi": round(float(row.psi), 3)}
            for row in drift.head(3).itertuples(index=False)
        ],
    }


def assess_current_batch_drift() -> dict:
    """Compare the current FD001 input batch against the training reference."""
    train = load_raw("data/raw/train_FD001.txt")
    current = load_raw("data/raw/test_FD001.txt")
    drift = assess_feature_drift(train, current, FEATURE_COLUMNS)
    return summarize_drift(drift)
