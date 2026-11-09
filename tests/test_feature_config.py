import pandas as pd
import pytest

from src.feature_config import SELECTED_FEATURE_SET, build_selected_features


def make_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "cycle": [1],
            "op_setting_1": [0.0],
            "op_setting_2": [0.0],
            "op_setting_3": [100.0],
            **{f"sensor_{index}": [float(index)] for index in range(1, 22)},
        }
    )


def test_selected_features_are_raw_and_present() -> None:
    prepared, columns = build_selected_features(make_frame())

    assert SELECTED_FEATURE_SET == "raw"
    assert prepared.equals(make_frame())
    assert len(columns) == 25


def test_selected_features_reject_missing_columns() -> None:
    with pytest.raises(ValueError, match="sensor_21"):
        build_selected_features(make_frame().drop(columns="sensor_21"))
