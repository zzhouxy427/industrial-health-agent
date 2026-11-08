"""Prioritize engines that need human maintenance review."""

import pandas as pd


def build_risk_queue(predictions: pd.DataFrame, threshold: int) -> pd.DataFrame:
    """Rank engines by point prediction and uncertainty-aware review priority."""
    queue = predictions.copy()
    queue["priority"] = "monitor"
    queue.loc[queue["prediction_p10"] <= threshold, "priority"] = "review"
    queue.loc[queue["predicted_rul"] <= threshold, "priority"] = "critical"

    queue["review_reason"] = "RUL 区间未触及风险阈值"
    queue.loc[queue["prediction_p10"] <= threshold, "review_reason"] = (
        "预测区间下界触及风险阈值，建议人工复核"
    )
    queue.loc[queue["predicted_rul"] <= threshold, "review_reason"] = (
        "点预测已低于风险阈值，优先人工复核"
    )

    rank = {"critical": 0, "review": 1, "monitor": 2}
    queue["priority_rank"] = queue["priority"].map(rank)
    return queue.sort_values(["priority_rank", "predicted_rul"]).drop(
        columns="priority_rank"
    )
