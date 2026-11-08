"""Create a review-priority queue from the latest RUL predictions."""

from pathlib import Path

import pandas as pd

from config import RISK_THRESHOLD
from risk_queue import build_risk_queue


def main() -> None:
    predictions = pd.read_csv("artifacts/fd001_predictions.csv")
    queue = build_risk_queue(predictions, RISK_THRESHOLD)
    output_path = Path("artifacts/risk_queue.csv")
    queue.to_csv(output_path, index=False)

    print("风险队列汇总:")
    print(queue["priority"].value_counts().reindex(["critical", "review", "monitor"], fill_value=0))
    print("\n优先复核队列（前 10 条）:")
    print(
        queue.loc[
            queue["priority"] != "monitor",
            ["unit_number", "predicted_rul", "prediction_p10", "prediction_p90", "priority", "review_reason"],
        ]
        .head(10)
        .to_string(index=False)
    )
    print("\n已保存:", output_path)


if __name__ == "__main__":
    main()
