from src.risk_queue_gate import check_risk_queue_gates


def test_risk_queue_gate_accepts_high_recall() -> None:
    metrics = {"actionable_queue": {"recall": 0.9375}}

    assert check_risk_queue_gates(metrics) == []


def test_risk_queue_gate_rejects_low_recall() -> None:
    failures = check_risk_queue_gates({"actionable_queue": {"recall": 0.89}})

    assert failures == ["人工复核队列召回率=89.0% 低于门限 90.0%"]


def test_risk_queue_gate_reports_missing_recall() -> None:
    assert check_risk_queue_gates({}) == ["缺少指标: actionable_queue.recall"]
