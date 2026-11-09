"""Split-conformal calibration for RUL prediction intervals using train engines only."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

try:
    from .feature_config import build_selected_features
    from .model_factory import build_rul_model
    from .prediction_uncertainty import estimate_conformal_adjustment, predict_with_uncertainty
except ImportError:  # Supports direct script execution.
    from feature_config import build_selected_features
    from model_factory import build_rul_model
    from prediction_uncertainty import estimate_conformal_adjustment, predict_with_uncertainty


CALIBRATION_FRACTIONS = (0.50, 0.70, 0.85, 0.95)
INTERVAL_COVERAGE = 0.80


def select_simulated_observations(
    frame: pd.DataFrame, fractions: tuple[float, ...] = CALIBRATION_FRACTIONS
) -> pd.DataFrame:
    """Choose several causal observation points from each full engine trajectory."""
    rows = []
    for _, history in frame.groupby("unit_number", sort=True):
        history = history.sort_values("cycle")
        for fraction in fractions:
            position = min(max(int(np.ceil(len(history) * fraction)) - 1, 0), len(history) - 1)
            rows.append(history.iloc[position])
    return pd.DataFrame(rows).reset_index(drop=True)


def estimate_interval_calibration(frame: pd.DataFrame) -> dict:
    """Calibrate with held-out train engines, never with official test labels."""
    prepared, feature_columns = build_selected_features(frame)
    units = sorted(prepared["unit_number"].unique())
    split_index = int(len(units) * 0.8)
    fit_units, calibration_units = set(units[:split_index]), set(units[split_index:])
    fit = prepared[prepared["unit_number"].isin(fit_units)]
    calibration_history = prepared[prepared["unit_number"].isin(calibration_units)]
    calibration_rows = select_simulated_observations(calibration_history)

    model = build_rul_model()
    model.fit(fit[feature_columns], fit["rul"])
    _, lower, upper, _ = predict_with_uncertainty(model, calibration_rows[feature_columns])
    adjustment = estimate_conformal_adjustment(
        calibration_rows["rul"].to_numpy(), lower, upper, coverage=INTERVAL_COVERAGE
    )
    return {
        "method": "split_conformal_interval_expansion",
        "coverage": INTERVAL_COVERAGE,
        "adjustment": round(adjustment, 6),
        "fit_engine_count": len(fit_units),
        "calibration_engine_count": len(calibration_units),
        "calibration_observation_count": len(calibration_rows),
        "observation_fractions": list(CALIBRATION_FRACTIONS),
    }


def save_interval_calibration(result: dict, path: Path = Path("artifacts/interval_calibration.json")) -> None:
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
