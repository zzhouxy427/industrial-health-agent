import pandas as pd

from src.generate_review_summary import format_review_summary
from src.risk_queue import build_risk_queue


def test_review_summary_lists_only_units_needing_review() -> None:
    predictions = pd.DataFrame(
        {
            "unit_number": [1, 2, 3],
            "predicted_rul": [10.0, 35.0, 60.0],
            "prediction_p10": [5.0, 15.0, 40.0],
            "prediction_p90": [20.0, 50.0, 80.0],
        }
    )
    queue = build_risk_queue(predictions, threshold=20)

    summary = format_review_summary(queue, threshold=20)

    assert "critical（点预测低于阈值）：1 台" in summary
    assert "review（预测区间下界触及阈值）：1 台" in summary
    assert "| 1 |" in summary
    assert "| 2 |" in summary
    assert "| 3 |" not in summary
    assert "不得据此自动执行停机" in summary
