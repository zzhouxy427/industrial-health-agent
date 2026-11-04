"""Compare several RUL regression models on an engine-level holdout split."""

import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def main() -> None:
    frame = pd.read_csv("data/processed/train_fd001_with_rul.csv")
    feature_columns = [
        "cycle",
        "op_setting_1",
        "op_setting_2",
        "op_setting_3",
        *[f"sensor_{index}" for index in range(1, 22)],
    ]

    unit_numbers = sorted(frame["unit_number"].unique())
    train = frame[frame["unit_number"].isin(unit_numbers[:80])]
    validation = frame[frame["unit_number"].isin(unit_numbers[80:])]

    models = {
        "ridge": make_pipeline(StandardScaler(), Ridge(alpha=10.0)),
        "random_forest": RandomForestRegressor(
            n_estimators=150, random_state=42, n_jobs=-1
        ),
        "hist_gradient_boosting": HistGradientBoostingRegressor(
            max_iter=200, learning_rate=0.08, random_state=42
        ),
    }

    print("模型对比（按发动机划分，前 80 台训练，后 20 台验证）:")
    print("model                 MAE     RMSE")
    print("-" * 39)
    for name, model in models.items():
        model.fit(train[feature_columns], train["rul"])
        predictions = model.predict(validation[feature_columns])
        mae = mean_absolute_error(validation["rul"], predictions)
        rmse = mean_squared_error(validation["rul"], predictions) ** 0.5
        print(f"{name:<22} {mae:>6.2f}  {rmse:>8.2f}")


if __name__ == "__main__":
    main()
