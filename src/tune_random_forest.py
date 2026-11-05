"""Select Random Forest hyperparameters using grouped cross-validation only."""

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import GroupKFold, ParameterGrid


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

    # A small, explainable search space keeps the experiment practical on a laptop.
    candidates = list(
        ParameterGrid(
            {
                "n_estimators": [200],
                "max_depth": [None, 20],
                "min_samples_leaf": [1, 2, 4],
                "max_features": [1.0],
            }
        )
    )
    splitter = GroupKFold(n_splits=3)
    results = []

    for number, parameters in enumerate(candidates, start=1):
        fold_maes = []
        fold_rmses = []
        for train_index, validation_index in splitter.split(features, target, groups):
            model = RandomForestRegressor(
                **parameters, random_state=42, n_jobs=-1
            )
            model.fit(features.iloc[train_index], target.iloc[train_index])
            predictions = model.predict(features.iloc[validation_index])
            fold_maes.append(
                mean_absolute_error(target.iloc[validation_index], predictions)
            )
            fold_rmses.append(
                mean_squared_error(target.iloc[validation_index], predictions) ** 0.5
            )

        result = {
            **parameters,
            "mae": sum(fold_maes) / len(fold_maes),
            "rmse": sum(fold_rmses) / len(fold_rmses),
        }
        results.append(result)
        print(
            f"候选 {number}/{len(candidates)}: {parameters}, "
            f"MAE {result['mae']:.2f}, RMSE {result['rmse']:.2f}"
        )

    ranking = pd.DataFrame(results).sort_values(["mae", "rmse"])
    print("\n调优结果（按 MAE 从低到高）:")
    print(ranking.to_string(index=False, float_format="{:.2f}".format))
    best = ranking.iloc[0]
    print("\n推荐参数:")
    print(
        "n_estimators={n_estimators}, max_depth={max_depth}, "
        "min_samples_leaf={min_samples_leaf}, max_features={max_features}".format(
            **best.to_dict()
        )
    )


if __name__ == "__main__":
    main()
