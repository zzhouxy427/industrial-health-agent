import pandas as pd

from model_factory import build_rul_model
from train_engineered import build_features


def main() -> None:
    frame = pd.read_csv("data/processed/train_fd001_with_rul.csv")
    frame, feature_columns = build_features(frame)

    unit_numbers = sorted(frame["unit_number"].unique())
    train_units = set(unit_numbers[:80])
    validation_units = set(unit_numbers[80:])
    train = frame[frame["unit_number"].isin(train_units)]
    validation = frame[frame["unit_number"].isin(validation_units)]

    model = build_rul_model()
    model.fit(train[feature_columns], train["rul"])

    # 模拟多个真实观测时刻，覆盖健康、退化和临界状态。
    validation = validation.copy()
    validation["max_cycle"] = validation.groupby("unit_number")["cycle"].transform("max")
    observation_ratios = [0.50, 0.70, 0.85, 0.95]
    observed_parts = []
    for ratio in observation_ratios:
        candidate = validation.copy()
        candidate["observation_cycle"] = (
            candidate["max_cycle"] * ratio
        ).astype(int)
        observed_parts.append(
            candidate.loc[candidate["cycle"] == candidate["observation_cycle"]]
        )
    observed_rows = pd.concat(observed_parts, ignore_index=True)
    observed_rows["actual_rul"] = (
        observed_rows["max_cycle"] - observed_rows["cycle"]
    )
    observed_rows["predicted_rul"] = model.predict(observed_rows[feature_columns])

    rows = []
    for threshold in range(10, 81, 10):
        actual_critical = observed_rows["actual_rul"] <= threshold
        predicted_critical = observed_rows["predicted_rul"] <= threshold
        false_negative = (actual_critical & ~predicted_critical).sum()
        false_positive = (~actual_critical & predicted_critical).sum()
        cost = 5 * false_negative + false_positive
        rows.append(
            {
                "threshold": threshold,
                "false_negative": false_negative,
                "false_positive": false_positive,
                "risk_cost": cost,
            }
        )

    summary = pd.DataFrame(rows).sort_values("risk_cost")
    print("验证集阈值校准结果（漏报成本按误报的 5 倍计算）:")
    print(summary.to_string(index=False))
    print("\n推荐阈值:", int(summary.iloc[0]["threshold"]))


if __name__ == "__main__":
    main()
