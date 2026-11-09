"""Central definition of the feature set selected by grouped cross-validation."""

import pandas as pd


SELECTED_FEATURE_SET = "raw"
SELECTED_FEATURE_COLUMNS = [
    "cycle",
    "op_setting_1",
    "op_setting_2",
    "op_setting_3",
    *[f"sensor_{index}" for index in range(1, 22)],
]


def build_selected_features(frame: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Return the production feature frame chosen by grouped CV.

    The raw configuration was selected over rolling windows because it had the
    lowest mean MAE in the window-comparison experiment. Keeping this function
    as the single production entry point prevents evaluation/reporting drift.
    """
    missing = sorted(set(SELECTED_FEATURE_COLUMNS) - set(frame.columns))
    if missing:
        raise ValueError(f"missing required feature columns: {', '.join(missing)}")
    return frame.copy(), list(SELECTED_FEATURE_COLUMNS)
