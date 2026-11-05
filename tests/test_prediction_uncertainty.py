import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from src.prediction_uncertainty import predict_with_uncertainty


def test_prediction_uncertainty_has_ordered_interval() -> None:
    features = pd.DataFrame({"x": [0, 1, 2, 3, 4], "y": [1, 1, 2, 2, 3]})
    target = pd.Series([0, 1, 2, 3, 4])
    model = RandomForestRegressor(n_estimators=10, random_state=42).fit(features, target)

    mean, lower, upper, spread = predict_with_uncertainty(model, features)

    assert len(mean) == len(features)
    assert (lower <= upper).all()
    assert (spread >= 0).all()
