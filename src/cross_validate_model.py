"""Evaluate the selected RUL model with engine-level cross-validation."""

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import GroupKFold


def main() -> None:
    frame = pd.read_csv("data/processed/train_fd001_with_rul.csv")
    feature_columns = [
        "cycle",
        "op_setting_1",
        "op_setting_2",
        "op_setting_3",
        *[f"sensor_{index}" for index in range(1, 22)],
    ]

    features = frame[feature_columns]
    target = frame["rul"]
    groups = frame["unit_number"]
    splitter = GroupKFold(n_splits=5)
    results = []

    for fold, (train_index, validation_index) in enumerate(
        splitter.split(features, target, groups), start=1
    ):
        model = RandomForestRegressor(
            n_estimators=100, random_state=42, n_jobs=-1
        )
        model.fit(features.iloc[train_index], target.iloc[train_index])
        predictions = model.predict(features.iloc[validation_index])
        mae = mean_absolute_error(target.iloc[validation_index], predictions)
        rmse = mean_squared_error(target.iloc[validation_index], predictions) ** 0.5
        results.append({"fold": fold, "mae": mae, "rmse": rmse})
        print(f"第 {fold} 折: MAE {mae:.2f}, RMSE {rmse:.2f}")

    result_frame = pd.DataFrame(results)
    print("\n5 折发动机级交叉验证汇总:")
    print(f"MAE:  {result_frame['mae'].mean():.2f} ± {result_frame['mae'].std():.2f}")
    print(f"RMSE: {result_frame['rmse'].mean():.2f} ± {result_frame['rmse'].std():.2f}")


if __name__ == "__main__":
    main()
