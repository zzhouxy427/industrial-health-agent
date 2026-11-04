import pandas as pd
from sklearn.ensemble import RandomForestRegressor


def main() -> None:
    frame = pd.read_csv("data/processed/train_fd001_with_rul.csv")
    feature_columns = [
        "cycle",
        "op_setting_1",
        "op_setting_2",
        "op_setting_3",
        *[f"sensor_{index}" for index in range(1, 22)],
    ]

    train_units = set(sorted(frame["unit_number"].unique())[:80])
    train = frame[frame["unit_number"].isin(train_units)]

    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(train[feature_columns], train["rul"])

    importance = pd.Series(model.feature_importances_, index=feature_columns)
    print("特征重要性排名:")
    print(importance.sort_values(ascending=False).head(10))


if __name__ == "__main__":
    main()
