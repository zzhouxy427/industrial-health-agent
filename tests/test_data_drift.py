import pandas as pd

from src.data_drift import assess_feature_drift, population_stability_index


def test_psi_is_low_for_matching_distribution() -> None:
    values = pd.Series(range(100))

    assert population_stability_index(values, values) < 0.01


def test_psi_detects_shifted_distribution() -> None:
    reference = pd.DataFrame({"sensor_1": range(100)})
    current = pd.DataFrame({"sensor_1": range(100, 200)})

    result = assess_feature_drift(reference, current, ["sensor_1"])

    assert result.loc[0, "status"] == "significant"
    assert result.loc[0, "psi"] >= 0.25
