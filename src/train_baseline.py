import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


def main() -> None:
    frame = pd.read_csv("data/processed/train_fd001_with_rul.csv")
    feature_columns = [
        "cycle",
        "op_setting_1",
        "op_setting_2",
        "op_setting_3",
        *[f"sensor_{index}" for index in range(1, 22)],
    ]

    # 按发动机划分，避免同一台发动机同时出现在训练集和验证集。
    unit_numbers = sorted(frame["unit_number"].unique())
    train_units = set(unit_numbers[:80])
    validation_units = set(unit_numbers[80:])

    train = frame[frame["unit_number"].isin(train_units)]
    validation = frame[frame["unit_number"].isin(validation_units)]

    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(train[feature_columns], train["rul"])

    predictions = model.predict(validation[feature_columns])
    mae = mean_absolute_error(validation["rul"], predictions)
    rmse = mean_squared_error(validation["rul"], predictions) ** 0.5

    print("训练发动机数量:", len(train_units))
    print("验证发动机数量:", len(validation_units))
    print(f"MAE: {mae:.2f} cycles")
    print(f"RMSE: {rmse:.2f} cycles")


if __name__ == "__main__":
    main()
