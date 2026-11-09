"""Append-only local audit trail for diagnostic-agent runs."""

from datetime import datetime, timezone
import json
from pathlib import Path


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
