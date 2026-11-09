"""Persist a versioned local model bundle for reproducible offline diagnosis."""

import hashlib
import json
from pathlib import Path

import joblib

try:
    from .model_metadata import MODEL_VERSION
except ImportError:  # Supports direct script execution.
    from model_metadata import MODEL_VERSION


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of a local binary artifact."""
    digest = hashlib.sha256()
    with path.open("rb") as artifact:
        for block in iter(lambda: artifact.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def save_model_bundle(
    model,
    feature_columns: list[str],
    calibration: dict,
    output_dir: Path = Path("artifacts"),
) -> dict:
    """Save model binary plus JSON manifest; only locally-produced artifacts are trusted."""
    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / "rul_model.joblib"
    manifest_path = output_dir / "rul_model_manifest.json"
    joblib.dump(model, model_path)
    manifest = {
        "model_version": MODEL_VERSION,
        "model_file": model_path.name,
        "model_sha256": sha256_file(model_path),
        "feature_columns": list(feature_columns),
        "feature_count": len(feature_columns),
        "interval_calibration": calibration,
        "security_note": (
            "joblib files must only be loaded from a trusted local source; "
            "they are not accepted as user uploads."
        ),
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return manifest
