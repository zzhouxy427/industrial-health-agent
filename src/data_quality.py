"""Reusable data-quality checks for an engine sensor trajectory."""

import pandas as pd


COLUMNS = [
    "unit_number",
    "cycle",
    "op_setting_1",
    "op_setting_2",
    "op_setting_3",
    *[f"sensor_{index}" for index in range(1, 22)],
]
FEATURE_COLUMNS = COLUMNS[2:]


def load_raw(path: str) -> pd.DataFrame:
    return pd.read_csv(path, sep=r"\s+", header=None, names=COLUMNS)


def assess_data_quality(
    history: pd.DataFrame, reference: pd.DataFrame, feature_columns: list[str]
) -> dict[str, int | float | bool]:
    """Compare one engine history against basic structural and range checks."""
    missing_values = int(history[feature_columns].isna().sum().sum())
    duplicate_cycles = int(history.duplicated(["unit_number", "cycle"]).sum())
    ordered = history.sort_values("cycle")
    cycle_gaps = int((ordered["cycle"].diff().dropna() != 1).sum())

    lower = reference[feature_columns].quantile(0.01)
    upper = reference[feature_columns].quantile(0.99)
    outside_range = history[feature_columns].lt(lower).sum().sum() + history[
        feature_columns
    ].gt(upper).sum().sum()
    checked_values = len(history) * len(feature_columns)
    outside_ratio = float(outside_range / checked_values) if checked_values else 0.0
    range_warning = outside_ratio > 0.02

    return {
        "missing_values": missing_values,
        "duplicate_cycles": duplicate_cycles,
        "cycle_gaps": cycle_gaps,
        "outside_reference_range": int(outside_range),
        "checked_values": checked_values,
        "outside_ratio": outside_ratio,
        "range_warning": range_warning,
        "passed": (
            missing_values == 0
            and duplicate_cycles == 0
            and cycle_gaps == 0
            and not range_warning
        ),
    }


def assess_unit_quality(unit: int) -> dict[str, int | float | bool]:
    """Assess a test engine against the FD001 training-data reference range."""
    train = load_raw("data/raw/train_FD001.txt")
    test = load_raw("data/raw/test_FD001.txt")
    history = test.loc[test["unit_number"] == unit]
    if history.empty:
        raise ValueError(f"未找到发动机 {unit}")
    return assess_data_quality(history, train, FEATURE_COLUMNS)
