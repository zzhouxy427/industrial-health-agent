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


def verify_model_bundle(
    manifest_path: Path = Path("artifacts/rul_model_manifest.json"),
) -> dict:
    """Verify a locally-produced model bundle without deserializing its binary."""
    status = {
        "available": False,
        "verified": False,
        "model_version": None,
        "message": "尚未生成本地模型快照。",
    }
    if not manifest_path.exists():
        return status

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        model_file = manifest["model_file"]
        expected_hash = manifest["model_sha256"]
    except (json.JSONDecodeError, KeyError, TypeError):
        status["message"] = "模型快照清单格式不完整。"
        return status

    candidate = Path(model_file)
    if candidate.name != model_file or candidate.is_absolute():
        status["message"] = "模型快照清单包含不安全的文件路径。"
        return status

    model_path = manifest_path.parent / candidate
    if not model_path.exists():
        status["available"] = True
        status["message"] = "模型快照二进制文件缺失。"
        return status

    status["available"] = True
    status["model_version"] = manifest.get("model_version")
    if sha256_file(model_path) != expected_hash:
        status["message"] = "模型快照完整性校验失败：SHA-256 不匹配。"
        return status

    status.update(
        {
            "verified": True,
            "message": "模型快照 SHA-256 完整性校验通过。",
        }
    )
    return status
