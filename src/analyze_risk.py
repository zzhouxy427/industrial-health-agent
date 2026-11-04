import pandas as pd


def main() -> None:
    result = pd.read_csv("artifacts/fd001_predictions.csv")
    horizon = 30
    result["actual_critical"] = result["actual_rul"] <= horizon
    result["predicted_critical"] = result["predicted_rul"] <= horizon

    true_positive = (
        result["actual_critical"] & result["predicted_critical"]
    ).sum()
    false_negative = (
        result["actual_critical"] & ~result["predicted_critical"]
    ).sum()
    false_positive = (
        ~result["actual_critical"] & result["predicted_critical"]
    ).sum()
    true_negative = (
        ~result["actual_critical"] & ~result["predicted_critical"]
    ).sum()

    print(f"临界寿命阈值: {horizon} cycles")
    print(f"正确识别临界状态: {true_positive}")
    print(f"漏报临界状态: {false_negative}")
    print(f"误报临界状态: {false_positive}")
    print(f"正确识别非临界状态: {true_negative}")

    if false_negative:
        print("\n漏报的发动机:")
        print(
            result.loc[
                result["actual_critical"] & ~result["predicted_critical"],
                ["unit_number", "actual_rul", "predicted_rul"],
            ].to_string(index=False)
        )


if __name__ == "__main__":
    main()
