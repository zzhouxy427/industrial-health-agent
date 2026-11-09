import pandas as pd

from src.evaluate_alert_timing import summarize_alert_timing


def test_alert_timing_summary_counts_early_and_missed_alerts() -> None:
    rows = pd.DataFrame(
        {
            "unit_number": [1, 2, 3],
            "alert_type": ["review", "critical", "none"],
            "actual_rul_at_alert": [35.0, 10.0, None],
        }
    )

    summary = summarize_alert_timing(rows, threshold=20)

    assert summary == {
        "engine_count": 3,
        "alerted_count": 2,
        "missed_count": 1,
        "early_alert_count": 1,
        "median_lead_cycles": 7.5,
    }
