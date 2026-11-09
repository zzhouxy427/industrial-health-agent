import pandas as pd

from src.evaluate_risk_queue import evaluate_risk_queue, format_risk_queue_report


def test_risk_queue_evaluation_quantifies_point_and_uncertainty_triage() -> None:
    predictions = pd.DataFrame(
        {
            "actual_rul": [10.0, 30.0, 10.0, 40.0],
            "predicted_rul": [10.0, 10.0, 30.0, 40.0],
            "prediction_p10": [5.0, 5.0, 10.0, 40.0],
            "prediction_p90": [15.0, 15.0, 35.0, 45.0],
        }
    )

    result = evaluate_risk_queue(predictions, threshold=20)

    assert result["actual_critical_count"] == 2
    assert result["point_critical"] == {
        "true_positive": 1,
        "false_positive": 1,
        "false_negative": 1,
        "true_negative": 1,
        "precision": 0.5,
        "recall": 0.5,
    }
    assert result["actionable_queue"]["recall"] == 1.0
    assert result["actionable_queue"]["precision"] == 0.6667
    assert "人工复核队列" in format_risk_queue_report(result)
