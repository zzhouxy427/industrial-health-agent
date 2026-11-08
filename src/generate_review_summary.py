"""Generate a human-review summary from the latest risk queue."""

from pathlib import Path

import pandas as pd

try:
    from .config import RISK_THRESHOLD
    from .risk_queue import build_risk_queue
except ImportError:  # Supports direct execution: python src\generate_review_summary.py
    from config import RISK_THRESHOLD
    from risk_queue import build_risk_queue


DISPLAY_COLUMNS = [
    "unit_number",
    "predicted_rul",
    "prediction_p10",
    "prediction_p90",
    "priority",
    "review_reason",
]


def format_review_summary(queue: pd.DataFrame, threshold: int) -> str:
    """Return a Markdown review handoff for critical and review-priority units."""
    counts = queue["priority"].value_counts()
    review_queue = queue.loc[queue["priority"] != "monitor", DISPLAY_COLUMNS]

    lines = [
        "# 批量风险复核摘要",
        "",
        f"- 风险阈值：{threshold} cycles",
        f"- critical（点预测低于阈值）：{counts.get('critical', 0)} 台",
        f"- review（预测区间下界触及阈值）：{counts.get('review', 0)} 台",
        f"- monitor（常规监测）：{counts.get('monitor', 0)} 台",
        "",
        "## 优先人工复核清单",
        "",
    ]

    if review_queue.empty:
        lines.append("当前没有发动机进入优先复核队列。")
    else:
        lines.extend(
            [
                "| 发动机 | 预测 RUL | 80% 经验区间 | 优先级 | 复核原因 |",
                "| --- | ---: | --- | --- | --- |",
            ]
        )
        for row in review_queue.itertuples(index=False):
            lines.append(
                "| {unit} | {prediction:.1f} | {lower:.1f}–{upper:.1f} | "
                "{priority} | {reason} |".format(
                    unit=row.unit_number,
                    prediction=row.predicted_rul,
                    lower=row.prediction_p10,
                    upper=row.prediction_p90,
                    priority=row.priority,
                    reason=row.review_reason,
                )
            )

    lines.extend(
        [
            "",
            "## 处置边界",
            "",
            "本清单用于安排人工复核顺序。应结合设备工况、传感器趋势和数据质量进行判断，"
            "不得据此自动执行停机、维修或其他安全关键操作。",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    predictions = pd.read_csv("artifacts/fd001_predictions.csv")
    queue = build_risk_queue(predictions, RISK_THRESHOLD)
    output_path = Path("artifacts/maintenance_review_summary.md")
    summary = format_review_summary(queue, RISK_THRESHOLD)
    output_path.write_text(summary, encoding="utf-8")
    print(summary)
    print("已保存:", output_path)


if __name__ == "__main__":
    main()
