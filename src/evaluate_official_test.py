import json
from pathlib import Path

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


def evaluate_official_model(
    train: pd.DataFrame, test: pd.DataFrame, truth: pd.Series
) -> dict[str, float | int]:
    """Fit the production model and return official FD001 holdout metrics."""
    train, feature_columns = build_selected_features(train.copy())
    test, _ = build_selected_features(test.copy())

    model = build_rul_model()
    model.fit(train[feature_columns], train["rul"])

    last_rows = test.loc[test.groupby("unit_number")["cycle"].idxmax()]
    predictions = model.predict(last_rows[feature_columns])
    mae = mean_absolute_error(truth, predictions)
    rmse = mean_squared_error(truth, predictions) ** 0.5
    return {
        "engine_count": int(len(last_rows)),
        "mae": round(float(mae), 6),
        "rmse": round(float(rmse), 6),
    }


def main() -> None:
    train = pd.read_csv("data/processed/train_fd001_with_rul.csv")
    test = load_raw("data/raw/test_FD001.txt")
    truth = pd.read_csv(
        "data/raw/RUL_FD001.txt",
        sep=r"\s+",
        header=None,
        names=["rul"],
    )["rul"]
    metrics = evaluate_official_model(train, test, truth)
    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/official_evaluation.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("官方测试集发动机数量:", metrics["engine_count"])
    print(f"MAE: {metrics['mae']:.2f} cycles")
    print(f"RMSE: {metrics['rmse']:.2f} cycles")
    print("已保存: artifacts/official_evaluation.json")


if __name__ == "__main__":
    main()
