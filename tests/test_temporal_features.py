import pandas as pd
import pytest

from src.train_engineered import build_features


def test_rolling_features_do_not_cross_engine_boundaries() -> None:
    frame = pd.DataFrame(
        {
            "unit_number": [1, 1, 2],
            "cycle": [1, 2, 1],
            **{f"sensor_{index}": [10.0, 20.0, 100.0] for index in range(1, 22)},
        }
    )

    result, columns = build_features(frame, window_size=2)

    assert result.loc[1, "sensor_1_mean_2"] == 15.0
    assert result.loc[2, "sensor_1_mean_2"] == 100.0
    assert result.loc[2, "sensor_1_std_2"] == 0.0
    assert "sensor_21_std_2" in columns
    assert "op_setting_3" in columns


def test_feature_window_must_be_positive() -> None:
    frame = pd.DataFrame({"unit_number": [1], "cycle": [1]})

    with pytest.raises(ValueError, match="window_size"):
        build_features(frame, window_size=0)
