import pandas as pd

from config import RISK_THRESHOLD


def main() -> None:
    result = pd.read_csv("artifacts/fd001_predictions.csv")
    threshold = RISK_THRESHOLD
    actual_critical = result["actual_rul"] <= threshold
    predicted_critical = result["predicted_rul"] <= threshold

    true_positive = (actual_critical & predicted_critical).sum()
    false_negative = (actual_critical & ~predicted_critical).sum()
    false_positive = (~actual_critical & predicted_critical).sum()
    true_negative = (~actual_critical & ~predicted_critical).sum()

    print("最终官方测试集风险评估")
    print("固定阈值:", threshold, "cycles")
    print("正确识别临界状态:", true_positive)
    print("漏报临界状态:", false_negative)
    print("误报临界状态:", false_positive)
    print("正确识别非临界状态:", true_negative)
    print("\n注意：该结果用于研究和学习，不代表真实航空维护安全结论。")


if __name__ == "__main__":
    main()
