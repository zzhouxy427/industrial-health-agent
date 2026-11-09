from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from conformal_calibration import estimate_interval_calibration, save_interval_calibration
from feature_config import build_selected_features
from model_artifact import save_model_bundle
from model_factory import build_rul_model
from prediction_uncertainty import apply_conformal_adjustment, predict_with_uncertainty


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
    train, feature_columns = build_selected_features(train)
    test, _ = build_selected_features(test)

    model = build_rul_model()
    model.fit(train[feature_columns], train["rul"])

    calibration = estimate_interval_calibration(train)

    last_rows = test.loc[test.groupby("unit_number")["cycle"].idxmax()]
    predictions, lower, upper, prediction_std = predict_with_uncertainty(
        model, last_rows[feature_columns]
    )
    lower, upper = apply_conformal_adjustment(
        lower, upper, calibration["adjustment"]
    )
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
            "prediction_p10": lower,
            "prediction_p90": upper,
            "prediction_std": prediction_std,
        }
    )
    result["absolute_error"] = (
        result["actual_rul"] - result["predicted_rul"]
    ).abs()

    output_dir = Path("artifacts")
    output_dir.mkdir(exist_ok=True)
    result.to_csv(output_dir / "fd001_predictions.csv", index=False)
    save_interval_calibration(calibration, output_dir / "interval_calibration.json")
    manifest = save_model_bundle(model, feature_columns, calibration, output_dir)

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
    print("区间校准偏移:", f"{calibration['adjustment']:.2f} cycles")
    print("最大绝对误差:", f"{result['absolute_error'].max():.2f} cycles")
    print("已保存模型快照:", output_dir / manifest["model_file"])
    print("模型 SHA-256:", manifest["model_sha256"])


if __name__ == "__main__":
    main()
