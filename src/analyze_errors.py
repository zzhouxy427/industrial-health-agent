import pandas as pd


def main() -> None:
    result = pd.read_csv("artifacts/fd001_predictions.csv")
    result["signed_error"] = result["predicted_rul"] - result["actual_rul"]

    print("绝对误差最大的 10 台发动机:")
    print(
        result.sort_values("absolute_error", ascending=False)
        [["unit_number", "actual_rul", "predicted_rul", "signed_error", "absolute_error"]]
        .head(10)
        .to_string(index=False)
    )

    print("\n平均误差方向:")
    print(f"{result['signed_error'].mean():.2f} cycles")
    print("正数表示整体偏高估计，负数表示整体偏低估计。")


if __name__ == "__main__":
    main()
