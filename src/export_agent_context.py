import argparse
import json
from pathlib import Path

import pandas as pd

from retrieve_guidance import retrieve_guidance


COLUMNS = [
    "unit_number",
    "cycle",
    "op_setting_1",
    "op_setting_2",
    "op_setting_3",
    *[f"sensor_{index}" for index in range(1, 22)],
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", type=int, required=True)
    args = parser.parse_args()

    predictions = pd.read_csv("artifacts/fd001_predictions.csv")
    prediction = predictions.loc[predictions["unit_number"] == args.unit].iloc[0]
    test = pd.read_csv(
        "data/raw/test_FD001.txt",
        sep=r"\s+",
        header=None,
        names=COLUMNS,
    )
    history = test[test["unit_number"] == args.unit].sort_values("cycle")

    trends = []
    changes = []
    for sensor_number in [4, 11]:
        column = f"sensor_{sensor_number}"
        recent = history[column].tail(10).mean()
        previous = history[column].tail(20).head(10).mean()
        change = recent - previous
        changes.append(change)
        trends.append(
            {
                "sensor": column,
                "recent_mean": round(float(recent), 3),
                "change": round(float(change), 3),
            }
        )

    predicted_rul = float(prediction["predicted_rul"])
    threshold = 20
    if predicted_rul <= threshold:
        risk_level = "high"
    elif predicted_rul <= 2 * threshold:
        risk_level = "medium"
    else:
        risk_level = "low"

    context = {
        "unit_number": args.unit,
        "current_cycle": int(history["cycle"].max()),
        "predicted_rul": round(predicted_rul, 3),
        "risk_threshold": threshold,
        "risk_level": risk_level,
        "trend_warning": all(change > 0 for change in changes),
        "sensor_trends": trends,
        "maintenance_guidance": retrieve_guidance(["传感器", "上升", "趋势"]),
    }

    output_path = Path(f"artifacts/agent_context_unit_{args.unit}.json")
    output_path.write_text(
        json.dumps(context, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Agent 上下文已生成: {output_path}")
    print(json.dumps(context, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
