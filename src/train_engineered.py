import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


def build_features(frame: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    result = frame.copy()
    sensor_columns = [f"sensor_{index}" for index in range(1, 22)]
    feature_columns = ["cycle", *sensor_columns]

    grouped = result.groupby("unit_number", group_keys=False)
    for column in sensor_columns:
        result[f"{column}_mean_5"] = grouped[column].transform(
            lambda values: values.rolling(5, min_periods=1).mean()
        )
        result[f"{column}_std_5"] = grouped[column].transform(
            lambda values: values.rolling(5, min_periods=1).std().fillna(0)
        )
        feature_columns.extend([f"{column}_mean_5", f"{column}_std_5"])

    return result, feature_columns


def main() -> None:
    frame = pd.read_csv("data/processed/train_fd001_with_rul.csv")
    frame, feature_columns = build_features(frame)

    unit_numbers = sorted(frame["unit_number"].unique())
    train_units = set(unit_numbers[:80])
    validation_units = set(unit_numbers[80:])
    train = frame[frame["unit_number"].isin(train_units)]
    validation = frame[frame["unit_number"].isin(validation_units)]

    model = RandomForestRegressor(
        n_estimators=150,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(train[feature_columns], train["rul"])
    predictions = model.predict(validation[feature_columns])

    mae = mean_absolute_error(validation["rul"], predictions)
    rmse = mean_squared_error(validation["rul"], predictions) ** 0.5
    print("加入 5 周期滑动平均和标准差后的结果:")
    print(f"MAE: {mae:.2f} cycles")
    print(f"RMSE: {rmse:.2f} cycles")


if __name__ == "__main__":
    main()
