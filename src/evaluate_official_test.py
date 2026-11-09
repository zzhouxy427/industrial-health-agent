import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

from feature_config import build_selected_features
from model_factory import build_rul_model


COLUMNS = [
    "unit_number",
    "cycle",
    "op_setting_1",
    "op_setting_2",
    "op_setting_3",
    *[f"sensor_{index}" for index in range(1, 22)],
]


def load_raw(path: str) -> pd.DataFrame:
    return pd.read_csv(path, sep=r"\s+", header=None, names=COLUMNS)


def main() -> None:
    train = pd.read_csv("data/processed/train_fd001_with_rul.csv")
    test = load_raw("data/raw/test_FD001.txt")
    train, feature_columns = build_selected_features(train)
    test, _ = build_selected_features(test)

    model = build_rul_model()
    model.fit(train[feature_columns], train["rul"])

    last_rows = test.loc[test.groupby("unit_number")["cycle"].idxmax()]
    predictions = model.predict(last_rows[feature_columns])
    truth = pd.read_csv(
        "data/raw/RUL_FD001.txt",
        sep=r"\s+",
        header=None,
        names=["rul"],
    )["rul"]

    mae = mean_absolute_error(truth, predictions)
    rmse = mean_squared_error(truth, predictions) ** 0.5
    print("官方测试集发动机数量:", len(last_rows))
    print(f"MAE: {mae:.2f} cycles")
    print(f"RMSE: {rmse:.2f} cycles")


if __name__ == "__main__":
    main()
