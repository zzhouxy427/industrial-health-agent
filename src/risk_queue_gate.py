"""Reject a release when the offline human-review queue misses too many critical cases."""

import json
from pathlib import Path

try:
    from .model_metadata import RISK_QUEUE_GATES
except ImportError:  # Supports direct script execution.
    from model_metadata import RISK_QUEUE_GATES


def check_risk_queue_gates(
    metrics: dict, gates: dict = RISK_QUEUE_GATES
) -> list[str]:
    """Return gate failures for the uncertainty-aware human-review queue."""
    try:
        recall = float(metrics["actionable_queue"]["recall"])
    except (KeyError, TypeError, ValueError):
        return ["缺少指标: actionable_queue.recall"]

    minimum = float(gates["min_actionable_queue_recall"])
    if recall < minimum:
        return [
            f"人工复核队列召回率={recall:.1%} 低于门限 {minimum:.1%}"
        ]
    return []


def main() -> None:
    path = Path("artifacts/risk_queue_evaluation.json")
    if not path.exists():
        raise FileNotFoundError(
            "缺少风险队列离线评估结果，请先运行 evaluate_risk_queue.py"
        )

    metrics = json.loads(path.read_text(encoding="utf-8"))
    failures = check_risk_queue_gates(metrics)
    if failures:
        raise SystemExit("风险队列门禁失败:\n- " + "\n- ".join(failures))

    recall = metrics["actionable_queue"]["recall"]
    print("风险队列门禁通过")
    print(
        f"人工复核队列召回率={recall:.1%} ≥ "
        f"{RISK_QUEUE_GATES['min_actionable_queue_recall']:.1%}"
    )


if __name__ == "__main__":
    main()
