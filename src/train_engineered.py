import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

try:
    from .model_factory import build_rul_model
except ImportError:  # Supports `python src/train_engineered.py`.
    from model_factory import build_rul_model


def build_features(
    frame: pd.DataFrame, window_size: int = 5
) -> tuple[pd.DataFrame, list[str]]:
    """Build causal per-engine rolling features without crossing engine boundaries."""
    if window_size < 1:
        raise ValueError("window_size must be at least 1")

    result = frame.copy()
    sensor_columns = [f"sensor_{index}" for index in range(1, 22)]
    feature_columns = [
        "cycle",
        "op_setting_1",
        "op_setting_2",
        "op_setting_3",
        *sensor_columns,
    ]

    grouped = result.groupby("unit_number", group_keys=False)
    for column in sensor_columns:
        mean_column = f"{column}_mean_{window_size}"
        std_column = f"{column}_std_{window_size}"
        result[mean_column] = grouped[column].transform(
            lambda values: values.rolling(window_size, min_periods=1).mean()
        )
        result[std_column] = grouped[column].transform(
            lambda values: values.rolling(window_size, min_periods=1).std().fillna(0)
        )
        feature_columns.extend([mean_column, std_column])

    return result, feature_columns


def main() -> None:
    frame = pd.read_csv("data/processed/train_fd001_with_rul.csv")
    frame, feature_columns = build_features(frame)

    unit_numbers = sorted(frame["unit_number"].unique())
    train_units = set(unit_numbers[:80])
    validation_units = set(unit_numbers[80:])
    train = frame[frame["unit_number"].isin(train_units)]
    validation = frame[frame["unit_number"].isin(validation_units)]

    model = build_rul_model()
    model.fit(train[feature_columns], train["rul"])
    predictions = model.predict(validation[feature_columns])

    mae = mean_absolute_error(validation["rul"], predictions)
    rmse = mean_squared_error(validation["rul"], predictions) ** 0.5
    print("加入 5 周期滑动平均和标准差后的结果:")
    print(f"MAE: {mae:.2f} cycles")
    print(f"RMSE: {rmse:.2f} cycles")


if __name__ == "__main__":
    main()
