import pandas as pd


def main() -> None:
    result = pd.read_csv("artifacts/fd001_predictions.csv")
    rows = []

    for threshold in range(10, 81, 10):
        actual_critical = result["actual_rul"] <= threshold
        predicted_critical = result["predicted_rul"] <= threshold
        false_negative = (actual_critical & ~predicted_critical).sum()
        false_positive = (~actual_critical & predicted_critical).sum()
        rows.append(
            {
                "threshold": threshold,
                "false_negative": false_negative,
                "false_positive": false_positive,
            }
        )

    summary = pd.DataFrame(rows)
    print(summary.to_string(index=False))
    print("\n注意：阈值越高通常越保守，可能减少漏报，但会增加误报。")


if __name__ == "__main__":
    main()
