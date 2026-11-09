"""Reject material RUL-regression before publishing a new project result."""

import json
from pathlib import Path

try:
    from .model_metadata import PERFORMANCE_GATES
except ImportError:  # Supports direct script execution.
    from model_metadata import PERFORMANCE_GATES


def check_performance_gates(metrics: dict, gates: dict = PERFORMANCE_GATES) -> list[str]:
    """Return human-readable gate failures, or an empty list when all pass."""
    required = {"mae": "max_official_test_mae", "rmse": "max_official_test_rmse"}
    failures = []
    for metric_name, gate_name in required.items():
        if metric_name not in metrics:
            failures.append(f"缺少指标: {metric_name}")
            continue
        if float(metrics[metric_name]) > float(gates[gate_name]):
            failures.append(
                f"{metric_name.upper()}={float(metrics[metric_name]):.2f} 超过门限 "
                f"{float(gates[gate_name]):.2f}"
            )
    return failures


def main() -> None:
    path = Path("artifacts/official_evaluation.json")
    if not path.exists():
        raise FileNotFoundError("缺少官方评估结果，请先运行 evaluate_official_test.py")
    metrics = json.loads(path.read_text(encoding="utf-8"))
    failures = check_performance_gates(metrics)
    if failures:
        raise SystemExit("模型性能门禁失败:\n- " + "\n- ".join(failures))
    print("模型性能门禁通过")
    print(
        f"MAE={metrics['mae']:.2f} ≤ {PERFORMANCE_GATES['max_official_test_mae']:.2f}; "
        f"RMSE={metrics['rmse']:.2f} ≤ {PERFORMANCE_GATES['max_official_test_rmse']:.2f}"
    )


if __name__ == "__main__":
    main()
