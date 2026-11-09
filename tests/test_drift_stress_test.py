import pandas as pd

from src.drift_stress_test import add_standard_deviation_shift, evaluate_drift_scenarios


def test_controlled_shift_does_not_mutate_input_and_triggers_warning() -> None:
    reference = pd.DataFrame({"sensor_1": range(100)})
    current = reference.copy()

    shifted = add_standard_deviation_shift(current, reference, "sensor_1", 3.0)
    result = evaluate_drift_scenarios(
        reference,
        current,
        ["sensor_1"],
        [("controlled", "sensor_1", 3.0)],
    )

    assert current["sensor_1"].equals(reference["sensor_1"])
    assert not shifted["sensor_1"].equals(current["sensor_1"])
    assert bool(result.loc[0, "warning"]) is True
    assert result.loc[0, "injected_feature_psi"] >= 0.25
    assert result.loc[0, "top_shifted_feature"] == "sensor_1"
