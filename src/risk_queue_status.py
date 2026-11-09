"""Load offline risk-queue evidence for the dashboard without exposing labels at runtime."""

import json
from pathlib import Path

try:
    from .model_metadata import RISK_QUEUE_GATES
    from .risk_queue_gate import check_risk_queue_gates
except ImportError:  # Supports direct script execution.
    from model_metadata import RISK_QUEUE_GATES
    from risk_queue_gate import check_risk_queue_gates


def load_risk_queue_status(
    evaluation_path: Path = Path("artifacts/risk_queue_evaluation.json"),
) -> dict:
    """Return a safe dashboard status when offline queue evidence is absent or present."""
    status = {
        "evaluated": False,
        "threshold": None,
        "point_critical": None,
        "actionable_queue": None,
        "gates": RISK_QUEUE_GATES.copy(),
        "passed": False,
        "failures": ["尚未生成风险队列离线评估结果。"],
        "message": "尚未生成风险队列离线评估结果。",
    }
    if not evaluation_path.exists():
        return status

    result = json.loads(evaluation_path.read_text(encoding="utf-8"))
    required = {"threshold", "point_critical", "actionable_queue"}
    if not required.issubset(result):
        status["message"] = "风险队列离线评估结果不完整。"
        return status

    failures = check_risk_queue_gates(result)
    status.update(
        {
            "evaluated": True,
            "threshold": result["threshold"],
            "point_critical": result["point_critical"],
            "actionable_queue": result["actionable_queue"],
            "passed": not failures,
            "failures": failures,
            "message": "结果仅来自带真实标签的 FD001 离线实验，不用于在线决策。",
        }
    )
    return status
