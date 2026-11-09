import json

from src.release_status import load_release_status


def test_release_status_reports_missing_evaluation(tmp_path) -> None:
    status = load_release_status(tmp_path / "missing.json")

    assert status["evaluated"] is False
    assert status["passed"] is False
    assert status["failures"] == ["尚未生成官方评估结果"]


def test_release_status_reports_gate_result(tmp_path) -> None:
    path = tmp_path / "evaluation.json"
    path.write_text(json.dumps({"mae": 19.5, "rmse": 26.1}), encoding="utf-8")

    status = load_release_status(
        path, {"max_official_test_mae": 22.0, "max_official_test_rmse": 30.0}
    )

    assert status["evaluated"] is True
    assert status["passed"] is True
    assert status["metrics"]["mae"] == 19.5
