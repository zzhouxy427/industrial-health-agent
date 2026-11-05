"""Central definition of the selected RUL prediction model."""

from sklearn.ensemble import RandomForestRegressor


def build_rul_model() -> RandomForestRegressor:
    """Return the model selected by grouped cross-validation tuning."""
    return RandomForestRegressor(
        n_estimators=200,
        max_depth=20,
        min_samples_leaf=4,
        max_features=1.0,
        random_state=42,
        n_jobs=-1,
    )
