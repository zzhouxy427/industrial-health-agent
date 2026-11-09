"""Compare causal rolling-window feature configurations on an engine-level holdout."""

import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

try:
    from .model_factory import build_rul_model
    from .train_engineered import build_features
except ImportError:  # Supports `python src/compare_temporal_windows.py`.
    from model_factory import build_rul_model
    from train_engineered import build_features


def evaluate_window(frame: pd.DataFrame, window_size: int | None) -> dict[str, float | str]:
    """Evaluate raw features or a causal rolling-window feature configuration."""
    if window_size is None:
        sensor_columns = [f"sensor_{index}" for index in range(1, 22)]
        prepared = frame.copy()
        feature_columns = ["cycle", "op_setting_1", "op_setting_2", "op_setting_3", *sensor_columns]
        label = "raw"
    else:
        prepared, feature_columns = build_features(frame, window_size=window_size)
        label = f"rolling_{window_size}"

    units = sorted(prepared["unit_number"].unique())
    train = prepared[prepared["unit_number"].isin(units[:80])]
    validation = prepared[prepared["unit_number"].isin(units[80:])]

    model = build_rul_model()
    model.fit(train[feature_columns], train["rul"])
    prediction = model.predict(validation[feature_columns])
    return {
        "feature_set": label,
        "window_size": 0 if window_size is None else window_size,
        "mae": mean_absolute_error(validation["rul"], prediction),
        "rmse": mean_squared_error(validation["rul"], prediction) ** 0.5,
    }


def main() -> None:
    frame = pd.read_csv("data/processed/train_fd001_with_rul.csv")
    results = pd.DataFrame(
        [evaluate_window(frame, window) for window in (None, 3, 5, 10)]
    ).sort_values("mae")

    print("时间窗口特征对比（按发动机划分：前 80 台训练，后 20 台验证）")
    print(results.to_string(index=False, formatters={"mae": "{:.2f}".format, "rmse": "{:.2f}".format}))
    best = results.iloc[0]
    print(f"\n当前最佳：{best['feature_set']}，MAE {best['mae']:.2f}，RMSE {best['rmse']:.2f}")

    output = "artifacts/temporal_window_comparison.csv"
    results.to_csv(output, index=False)
    print(f"已保存：{output}")


if __name__ == "__main__":
    main()
