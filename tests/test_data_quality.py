import pandas as pd

from src.data_quality import assess_data_quality


FEATURES = ["sensor_1"]
REFERENCE = pd.DataFrame(
    {
        "unit_number": [1] * 100,
        "cycle": list(range(1, 101)),
        "sensor_1": [float(value) for value in range(100)],
    }
)


def test_clean_history_passes_quality_check() -> None:
    history = REFERENCE.iloc[2:98].copy()

    result = assess_data_quality(history, REFERENCE, FEATURES)

    assert result["passed"] is True
    assert result["missing_values"] == 0
    assert result["range_warning"] is False


def test_missing_value_fails_quality_check() -> None:
    history = REFERENCE.iloc[2:98].copy()
    history.loc[1, "sensor_1"] = None

    result = assess_data_quality(history, REFERENCE, FEATURES)

    assert result["passed"] is False
    assert result["missing_values"] == 1
