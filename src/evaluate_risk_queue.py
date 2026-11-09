"""Offline evaluation of risk-queue triage against FD001 labels only."""

import json
from pathlib import Path

import pandas as pd

try:
    from .config import RISK_THRESHOLD
    from .risk_queue import build_risk_queue
except ImportError:  # Supports direct script execution.
    from config import RISK_THRESHOLD
    from risk_queue import build_risk_queue


def binary_metrics(actual_positive: pd.Series, predicted_positive: pd.Series) -> dict[str, int | float]:
    """Return transparent confusion counts plus precision and recall."""
    actual = actual_positive.astype(bool)
    predicted = predicted_positive.astype(bool)
    true_positive = int((actual & predicted).sum())
    false_positive = int((~actual & predicted).sum())
    false_negative = int((actual & ~predicted).sum())
    true_negative = int((~actual & ~predicted).sum())
    return {
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "true_negative": true_negative,
        "precision": round(true_positive / (true_positive + false_positive), 4)
        if true_positive + false_positive
        else 0.0,
        "recall": round(true_positive / (true_positive + false_negative), 4)
        if true_positive + false_negative
        else 0.0,
    }


def evaluate_risk_queue(predictions: pd.DataFrame, threshold: int = RISK_THRESHOLD) -> dict:
    """Evaluate point alerts and uncertainty-aware review queue using offline labels.

    `actual_rul` is used exclusively for post-hoc FD001 experiment reporting;
    it is never an input to runtime queue construction.
    """
    required = {"actual_rul", "predicted_rul", "prediction_p10", "prediction_p90"}
    missing = required - set(predictions.columns)
    if missing:
        raise ValueError(f"缺少离线队列评估字段: {', '.join(sorted(missing))}")

    queue = build_risk_queue(predictions, threshold)
    actual_critical = queue["actual_rul"] <= threshold
    point_alert = queue["priority"] == "critical"
    actionable_alert = queue["priority"].isin(["critical", "review"])
    return {
        "threshold": threshold,
        "engine_count": int(len(queue)),
        "actual_critical_count": int(actual_critical.sum()),
        "point_critical": binary_metrics(actual_critical, point_alert),
        "actionable_queue": binary_metrics(actual_critical, actionable_alert),
        "queue_counts": {
            priority: int((queue["priority"] == priority).sum())
            for priority in ["critical", "review", "monitor"]
        },
    }


def format_risk_queue_report(result: dict) -> str:
    """Format a compact Chinese experiment report from queue-evaluation metrics."""
    point = result["point_critical"]
    actionable = result["actionable_queue"]
    counts = result["queue_counts"]
    return f"""# 风险队列离线评估

- 评估发动机数：{result['engine_count']}
- 真实 RUL ≤ {result['threshold']} cycles 的发动机数：{result['actual_critical_count']}
- 队列组成：critical {counts['critical']} 台、review {counts['review']} 台、monitor {counts['monitor']} 台

| 策略 | 精确率 | 召回率 | TP | FP | FN | TN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 仅 `critical` 点预测 | {point['precision']:.1%} | {point['recall']:.1%} | {point['true_positive']} | {point['false_positive']} | {point['false_negative']} | {point['true_negative']} |
| `critical` + `review` 人工复核队列 | {actionable['precision']:.1%} | {actionable['recall']:.1%} | {actionable['true_positive']} | {actionable['false_positive']} | {actionable['false_negative']} | {actionable['true_negative']} |

## 解读边界

本报告只在 FD001 官方测试集的离线实验中使用 `actual_rul` 计算指标；真实在线诊断无法获得未来真实 RUL，队列构建只使用模型预测及其区间。人工复核队列的目标是降低漏报风险，因此可能比仅使用点预测产生更多待复核项。该结果不构成真实设备的告警性能或安全保证。
"""


def main() -> None:
    predictions = pd.read_csv("artifacts/fd001_predictions.csv")
    result = evaluate_risk_queue(predictions)
    output_dir = Path("artifacts")
    output_dir.mkdir(exist_ok=True)
    (output_dir / "risk_queue_evaluation.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    report = format_risk_queue_report(result)
    (output_dir / "risk_queue_evaluation.md").write_text(report, encoding="utf-8")
    print(report)
    print("已保存:", output_dir / "risk_queue_evaluation.json")
    print("已保存:", output_dir / "risk_queue_evaluation.md")


if __name__ == "__main__":
    main()
