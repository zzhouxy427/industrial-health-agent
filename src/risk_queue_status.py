"""Load offline risk-queue evidence for the dashboard without exposing labels at runtime."""

import json
from pathlib import Path


def load_risk_queue_status(
    evaluation_path: Path = Path("artifacts/risk_queue_evaluation.json"),
) -> dict:
    """Return a safe dashboard status when offline queue evidence is absent or present."""
    status = {
        "evaluated": False,
        "threshold": None,
        "point_critical": None,
        "actionable_queue": None,
        "message": "尚未生成风险队列离线评估结果。",
    }
    if not evaluation_path.exists():
        return status

    result = json.loads(evaluation_path.read_text(encoding="utf-8"))
    required = {"threshold", "point_critical", "actionable_queue"}
    if not required.issubset(result):
        status["message"] = "风险队列离线评估结果不完整。"
        return status

    status.update(
        {
            "evaluated": True,
            "threshold": result["threshold"],
            "point_critical": result["point_critical"],
            "actionable_queue": result["actionable_queue"],
            "message": "结果仅来自带真实标签的 FD001 离线实验，不用于在线决策。",
        }
    )
    return status
