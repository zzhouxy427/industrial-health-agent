import json

from src.audit_log import append_diagnosis_event, format_events_for_display, load_recent_events


def test_append_diagnosis_event_writes_json_line(tmp_path) -> None:
    path = tmp_path / "audit.jsonl"
    context = {
        "unit_number": 18,
        "current_cycle": 133,
        "predicted_rul": 56.7,
        "prediction_interval_80": {"lower": 31.0, "upper": 86.0},
        "risk_level": "low",
        "trend_warning": True,
        "data_quality": {"passed": True},
        "model_metadata": {"model_version": "rf-fd001-raw-v2"},
    }

    append_diagnosis_event(context, path)

    event = json.loads(path.read_text(encoding="utf-8"))
    assert event["unit_number"] == 18
    assert event["data_quality"]["passed"] is True
    assert event["model_metadata"]["model_version"] == "rf-fd001-raw-v2"
    assert "timestamp_utc" in event

    events = load_recent_events(path)
    assert len(events) == 1
    assert events[0]["unit_number"] == 18


def test_format_events_for_display_handles_legacy_optional_fields() -> None:
    events = [
        {
            "unit_number": 18,
            "prediction_interval_80": {"lower": 31.0, "upper": 86.0},
            "data_quality": {"passed": True},
            "model_monitoring": float("nan"),
            "model_metadata": float("nan"),
        }
    ]

    formatted = format_events_for_display(events)

    assert formatted == [
        {
            "unit_number": 18,
            "interval_80": "31.0–86.0",
            "data_quality_passed": True,
            "model_drift_warning": None,
            "model_version": "legacy",
        }
    ]
