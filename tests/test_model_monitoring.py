import pandas as pd

from src.model_monitoring import summarize_drift


def test_drift_summary_marks_significant_shift_as_warning() -> None:
    drift = pd.DataFrame(
        {
            "feature": ["sensor_4", "sensor_11", "sensor_2"],
            "psi": [0.31, 0.15, 0.02],
            "status": ["significant", "moderate", "stable"],
        }
    )

    summary = summarize_drift(drift)

    assert summary["warning"] is True
    assert summary["significant_feature_count"] == 1
    assert summary["moderate_feature_count"] == 1
    assert summary["top_shifted_features"][0] == {"feature": "sensor_4", "psi": 0.31}
