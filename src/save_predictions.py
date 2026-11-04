from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from train_engineered import build_features


COLUMNS = [
    "unit_number",
    "cycle",
    "op_setting_1",
    "op_setting_2",
    "op_setting_3",
    *[f"sensor_{index}" for index in range(1, 22)],
]


def main() -> None:
    train = pd.read_csv("data/processed/train_fd001_with_rul.csv")
    test = pd.read_csv(
        "data/raw/test_FD001.txt",
        sep=r"\s+",
        header=None,
        names=COLUMNS,
    )
    train, feature_columns = build_features(train)
    test, _ = build_features(test)

    model = RandomForestRegressor(
        n_estimators=150,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(train[feature_columns], train["rul"])

    last_rows = test.loc[test.groupby("unit_number")["cycle"].idxmax()]
    predictions = model.predict(last_rows[feature_columns])
    truth = pd.read_csv(
        "data/raw/RUL_FD001.txt",
        sep=r"\s+",
        header=None,
        names=["actual_rul"],
    )["actual_rul"]

    result = pd.DataFrame(
        {
            "unit_number": last_rows["unit_number"].to_numpy(),
            "actual_rul": truth.to_numpy(),
            "predicted_rul": predictions,
        }
    )
    result["absolute_error"] = (
        result["actual_rul"] - result["predicted_rul"]
    ).abs()

    output_dir = Path("artifacts")
    output_dir.mkdir(exist_ok=True)
    result.to_csv(output_dir / "fd001_predictions.csv", index=False)

    result.plot(
        x="unit_number",
        y=["actual_rul", "predicted_rul"],
        kind="line",
        marker="o",
        figsize=(12, 6),
        title="FD001 actual vs predicted RUL",
    )
    plt.ylabel("RUL (cycles)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / "fd001_predictions.png", dpi=150)
    print("已保存:", output_dir / "fd001_predictions.csv")
    print("已保存:", output_dir / "fd001_predictions.png")
    print("最大绝对误差:", f"{result['absolute_error'].max():.2f} cycles")


if __name__ == "__main__":
    main()
