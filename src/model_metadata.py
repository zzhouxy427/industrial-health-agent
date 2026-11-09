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

# Guardrails are deliberately looser than the recorded baseline to tolerate
# harmless library/platform variation while rejecting material regressions.
PERFORMANCE_GATES = {
    "max_official_test_mae": 22.0,
    "max_official_test_rmse": 30.0,
}

# This protects the human-review triage objective, separately from RUL error.
# It is evaluated only against labels in the offline FD001 experiment.
RISK_QUEUE_GATES = {
    "min_actionable_queue_recall": 0.90,
}


def get_model_metadata() -> dict:
    """Return serializable model provenance for reports and audit logs."""
    return {
        "model_version": MODEL_VERSION,
        "feature_set": SELECTED_FEATURE_SET,
        "hyperparameters": RUL_MODEL_PARAMETERS.copy(),
        "evaluation_summary": EVALUATION_SUMMARY.copy(),
        "performance_gates": PERFORMANCE_GATES.copy(),
        "risk_queue_gates": RISK_QUEUE_GATES.copy(),
    }
