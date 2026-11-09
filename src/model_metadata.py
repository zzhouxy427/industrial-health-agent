"""Immutable metadata attached to each diagnostic decision for traceability."""

try:
    from .feature_config import SELECTED_FEATURE_SET
    from .model_factory import RUL_MODEL_PARAMETERS
except ImportError:  # Supports direct execution from src scripts.
    from feature_config import SELECTED_FEATURE_SET
    from model_factory import RUL_MODEL_PARAMETERS


MODEL_VERSION = "rf-fd001-raw-conformal-v3"
EVALUATION_SUMMARY = {
    "official_test_mae": 19.53,
    "official_test_rmse": 26.10,
    "grouped_cv_mae_mean": 26.37,
    "grouped_cv_mae_std": 1.64,
    "grouped_cv_rmse_mean": 37.57,
    "grouped_cv_rmse_std": 2.77,
    "interval_80_coverage": 0.86,
    "interval_calibration_method": "split_conformal_interval_expansion",
    "interval_calibration_adjustment": 6.33,
}


def get_model_metadata() -> dict:
    """Return serializable model provenance for reports and audit logs."""
    return {
        "model_version": MODEL_VERSION,
        "feature_set": SELECTED_FEATURE_SET,
        "hyperparameters": RUL_MODEL_PARAMETERS.copy(),
        "evaluation_summary": EVALUATION_SUMMARY.copy(),
    }
