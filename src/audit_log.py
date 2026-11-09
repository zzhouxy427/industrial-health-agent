"""Append-only local audit trail for diagnostic-agent runs."""

from datetime import datetime, timezone
import json
from pathlib import Path


def _as_mapping(value: object) -> dict:
    """Return a mapping only when an audit field really contains one."""
    return value if isinstance(value, dict) else {}


def format_events_for_display(events: list[dict]) -> list[dict]:
    """Flatten audit events while remaining compatible with older event shapes.

    Older JSONL rows predate model monitoring and metadata. When loaded into a
    DataFrame, pandas represents missing values as ``NaN`` floats rather than
    ``None``. Normalize those fields before the dashboard renders the table.
    """
    formatted_events = []
    for event in events:
        row = dict(event)
        interval = _as_mapping(row.pop("prediction_interval_80", None))
        lower = interval.get("lower")
        upper = interval.get("upper")
        if isinstance(lower, (int, float)) and isinstance(upper, (int, float)):
            row["interval_80"] = f"{lower:.1f}–{upper:.1f}"
        else:
            row["interval_80"] = None

        data_quality = _as_mapping(row.pop("data_quality", None))
        row["data_quality_passed"] = data_quality.get("passed")

        monitoring = _as_mapping(row.pop("model_monitoring", None))
        row["model_drift_warning"] = monitoring.get("warning")

        metadata = _as_mapping(row.pop("model_metadata", None))
        row["model_version"] = metadata.get("model_version", "legacy")
        formatted_events.append(row)
    return formatted_events


def append_diagnosis_event(context: dict, path: Path = Path("artifacts/diagnosis_audit.jsonl")) -> None:
    """Persist the decision-relevant context as one JSON Lines audit event."""
    event = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "unit_number": context["unit_number"],
        "current_cycle": context["current_cycle"],
        "predicted_rul": context["predicted_rul"],
        "prediction_interval_80": context["prediction_interval_80"],
        "risk_level": context["risk_level"],
        "trend_warning": context["trend_warning"],
        "data_quality": context["data_quality"],
        "model_monitoring": context.get("model_monitoring"),
        "model_metadata": context.get("model_metadata"),
    }
    path.parent.mkdir(exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, ensure_ascii=False) + "\n")


def load_recent_events(
    path: Path = Path("artifacts/diagnosis_audit.jsonl"), limit: int = 10
) -> list[dict]:
    """Load the newest audit events first, without modifying the log."""
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in reversed(lines[-limit:])]
