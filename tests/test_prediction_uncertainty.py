import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from src.prediction_uncertainty import (
    apply_conformal_adjustment,
    estimate_conformal_adjustment,
    evaluate_interval_coverage,
    predict_with_uncertainty,
)


def test_prediction_uncertainty_has_ordered_interval() -> None:
    features = pd.DataFrame({"x": [0, 1, 2, 3, 4], "y": [1, 1, 2, 2, 3]})
    target = pd.Series([0, 1, 2, 3, 4])
    model = RandomForestRegressor(n_estimators=10, random_state=42).fit(features, target)

    mean, lower, upper, spread = predict_with_uncertainty(model, features)

    assert len(mean) == len(features)
    assert (lower <= upper).all()
    assert (spread >= 0).all()


def test_interval_coverage_reports_expected_counts() -> None:
    metrics = evaluate_interval_coverage(
        actual=[2, 5, 11],
        lower=[1, 6, 8],
        upper=[3, 9, 10],
    )

    assert metrics["sample_count"] == 3
    assert metrics["coverage"] == 1 / 3
    assert metrics["below_lower_count"] == 1
    assert metrics["above_upper_count"] == 1
    assert metrics["mean_width"] == 7 / 3


def test_conformal_adjustment_expands_interval_for_calibration_errors() -> None:
    adjustment = estimate_conformal_adjustment(
        actual=[0, 5, 12], lower=[1, 4, 8], upper=[3, 6, 10], coverage=0.8
    )
    lower, upper = apply_conformal_adjustment([1, 4], [3, 6], adjustment)

    assert adjustment == 2.0
    assert lower.tolist() == [0.0, 2.0]
    assert upper.tolist() == [5.0, 8.0]
