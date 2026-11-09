"""Load a dashboard-friendly view of the local model performance gate."""

import json
from pathlib import Path

try:
    from .model_metadata import MODEL_VERSION, PERFORMANCE_GATES
    from .performance_gate import check_performance_gates
except ImportError:  # Supports direct script execution.
    from model_metadata import MODEL_VERSION, PERFORMANCE_GATES
    from performance_gate import check_performance_gates


def load_release_status(
    evaluation_path: Path = Path("artifacts/official_evaluation.json"),
    gates: dict = PERFORMANCE_GATES,
) -> dict:
    """Return a safe status for UI display without raising on absent local artifacts."""
    status = {
        "model_version": MODEL_VERSION,
        "evaluated": False,
        "passed": False,
        "metrics": None,
        "gates": gates.copy(),
        "failures": ["尚未生成官方评估结果"],
    }
    if not evaluation_path.exists():
        return status

    metrics = json.loads(evaluation_path.read_text(encoding="utf-8"))
    failures = check_performance_gates(metrics, gates)
    status.update(
        {
            "evaluated": True,
            "passed": not failures,
            "metrics": metrics,
            "failures": failures,
        }
    )
    return status
