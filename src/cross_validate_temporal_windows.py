"""Select temporal feature windows using engine-level grouped cross-validation."""

from pathlib import Path

import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import GroupKFold

try:
    from .model_factory import build_rul_model
    from .train_engineered import build_features
except ImportError:  # Supports `python src/cross_validate_temporal_windows.py`.
    from model_factory import build_rul_model
    from train_engineered import build_features


def prepare_features(
    frame: pd.DataFrame, window_size: int | None
) -> tuple[pd.DataFrame, list[str], str]:
    if window_size is None:
        sensor_columns = [f"sensor_{index}" for index in range(1, 22)]
        columns = ["cycle", "op_setting_1", "op_setting_2", "op_setting_3", *sensor_columns]
        return frame.copy(), columns, "raw"

    prepared, columns = build_features(frame, window_size=window_size)
    return prepared, columns, f"rolling_{window_size}"


def evaluate_configuration(
    frame: pd.DataFrame, window_size: int | None, n_splits: int = 5
) -> list[dict[str, float | int | str]]:
    """Return fold-level engine-grouped validation metrics for one configuration."""
    prepared, feature_columns, label = prepare_features(frame, window_size)
    features = prepared[feature_columns]
    target = prepared["rul"]
    groups = prepared["unit_number"]
    splitter = GroupKFold(n_splits=n_splits)
    rows: list[dict[str, float | int | str]] = []

    for fold, (train_index, validation_index) in enumerate(
        splitter.split(features, target, groups), start=1
    ):
        model = build_rul_model()
        model.fit(features.iloc[train_index], target.iloc[train_index])
        prediction = model.predict(features.iloc[validation_index])
        rows.append(
            {
                "feature_set": label,
                "window_size": 0 if window_size is None else window_size,
                "fold": fold,
                "mae": mean_absolute_error(target.iloc[validation_index], prediction),
                "rmse": mean_squared_error(target.iloc[validation_index], prediction) ** 0.5,
            }
        )
    return rows


def main() -> None:
    frame = pd.read_csv("data/processed/train_fd001_with_rul.csv")
    all_rows = [
        row
        for window in (None, 3, 5, 10)
        for row in evaluate_configuration(frame, window)
    ]
    folds = pd.DataFrame(all_rows)
    summary = (
        folds.groupby(["feature_set", "window_size"], as_index=False)
        .agg(mae_mean=("mae", "mean"), mae_std=("mae", "std"), rmse_mean=("rmse", "mean"), rmse_std=("rmse", "std"))
        .sort_values("mae_mean")
    )

    print("时间窗口特征 5 折发动机级交叉验证（按 MAE 排序）")
    print(
        summary.to_string(
            index=False,
            formatters={
                "mae_mean": "{:.2f}".format,
                "mae_std": "{:.2f}".format,
                "rmse_mean": "{:.2f}".format,
                "rmse_std": "{:.2f}".format,
            },
        )
    )
    best = summary.iloc[0]
    print(
        f"\n推荐特征集：{best['feature_set']} "
        f"(MAE {best['mae_mean']:.2f} ± {best['mae_std']:.2f}, "
        f"RMSE {best['rmse_mean']:.2f} ± {best['rmse_std']:.2f})"
    )

    output_dir = Path("artifacts")
    output_dir.mkdir(exist_ok=True)
    folds.to_csv(output_dir / "temporal_window_cv_folds.csv", index=False)
    summary.to_csv(output_dir / "temporal_window_cv_summary.csv", index=False)
    print("已保存：artifacts/temporal_window_cv_folds.csv")
    print("已保存：artifacts/temporal_window_cv_summary.csv")


if __name__ == "__main__":
    main()
