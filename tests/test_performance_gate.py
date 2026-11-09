from src.performance_gate import check_performance_gates


def test_performance_gate_accepts_metrics_within_limits() -> None:
    assert check_performance_gates({"mae": 19.53, "rmse": 26.10}) == []


def test_performance_gate_reports_each_regressed_metric() -> None:
    failures = check_performance_gates({"mae": 22.01, "rmse": 30.01})

    assert len(failures) == 2
    assert "MAE" in failures[0]
    assert "RMSE" in failures[1]


def test_performance_gate_reports_missing_metric() -> None:
    assert check_performance_gates({"mae": 19.53}) == ["缺少指标: rmse"]
