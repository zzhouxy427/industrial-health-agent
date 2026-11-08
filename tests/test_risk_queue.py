import pandas as pd

from src.risk_queue import build_risk_queue


def test_risk_queue_prioritizes_point_and_interval_risk() -> None:
    predictions = pd.DataFrame(
        {
            "unit_number": [1, 2, 3],
            "predicted_rul": [10.0, 35.0, 60.0],
            "prediction_p10": [5.0, 15.0, 40.0],
            "prediction_p90": [20.0, 50.0, 80.0],
        }
    )

    queue = build_risk_queue(predictions, threshold=20)

    assert queue["unit_number"].tolist() == [1, 2, 3]
    assert queue["priority"].tolist() == ["critical", "review", "monitor"]
