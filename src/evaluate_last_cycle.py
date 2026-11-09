import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

from feature_config import build_selected_features


def main() -> None:
    frame = pd.read_csv("data/processed/train_fd001_with_rul.csv")
    frame, feature_columns = build_selected_features(frame)

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

    last_rows = validation.loc[
        validation.groupby("unit_number")["cycle"].idxmax()
    ]
    predictions = model.predict(last_rows[feature_columns])
    mae = mean_absolute_error(last_rows["rul"], predictions)
    rmse = mean_squared_error(last_rows["rul"], predictions) ** 0.5

    print("只评估每台验证发动机最后一个周期:")
    print("验证发动机数量:", len(last_rows))
    print(f"MAE: {mae:.2f} cycles")
    print(f"RMSE: {rmse:.2f} cycles")


if __name__ == "__main__":
    main()
