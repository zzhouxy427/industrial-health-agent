import json

from src.risk_queue_status import load_risk_queue_status


def test_risk_queue_status_reports_missing_evaluation(tmp_path) -> None:
    status = load_risk_queue_status(tmp_path / "missing.json")

    assert status["evaluated"] is False
    assert status["point_critical"] is None
    assert status["passed"] is False


def test_risk_queue_status_loads_offline_metrics(tmp_path) -> None:
    path = tmp_path / "queue.json"
    path.write_text(
        json.dumps(
            {
                "threshold": 20,
                "point_critical": {"precision": 0.9, "recall": 0.6},
                "actionable_queue": {"precision": 0.7, "recall": 0.94},
            }
        ),
        encoding="utf-8",
    )

    status = load_risk_queue_status(path)

    assert status["evaluated"] is True
    assert status["threshold"] == 20
    assert status["actionable_queue"]["recall"] == 0.94
    assert status["passed"] is True


def test_risk_queue_status_surfaces_gate_failure(tmp_path) -> None:
    path = tmp_path / "queue.json"
    path.write_text(
        json.dumps(
            {
                "threshold": 20,
                "point_critical": {"precision": 0.9, "recall": 0.6},
                "actionable_queue": {"precision": 0.7, "recall": 0.80},
            }
        ),
        encoding="utf-8",
    )

    status = load_risk_queue_status(path)

    assert status["passed"] is False
    assert "低于门限" in status["failures"][0]
