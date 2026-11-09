import json

from src.release_audit import build_release_audit, format_release_audit


def write_inputs(tmp_path, queue_recall: float = 0.94, artifact_hash: str = "") -> tuple:
    evaluation_path = tmp_path / "evaluation.json"
    queue_path = tmp_path / "queue.json"
    model_path = tmp_path / "model.joblib"
    manifest_path = tmp_path / "manifest.json"
    model_path.write_bytes(b"trusted-local-model")
    if not artifact_hash:
        from src.model_artifact import sha256_file

        artifact_hash = sha256_file(model_path)
    evaluation_path.write_text(
        json.dumps({"mae": 19.5, "rmse": 26.1}), encoding="utf-8"
    )
    queue_path.write_text(
        json.dumps(
            {
                "threshold": 20,
                "point_critical": {"precision": 0.9, "recall": 0.6},
                "actionable_queue": {"precision": 0.7, "recall": queue_recall},
            }
        ),
        encoding="utf-8",
    )
    manifest_path.write_text(
        json.dumps({"model_file": "model.joblib", "model_sha256": artifact_hash}),
        encoding="utf-8",
    )
    return evaluation_path, queue_path, manifest_path


def test_release_audit_passes_all_local_safeguards(tmp_path) -> None:
    audit = build_release_audit(*write_inputs(tmp_path))

    assert audit["passed"] is True
    assert all(audit["checks"].values())
    assert "结论：**通过**" in format_release_audit(audit)


def test_release_audit_collects_multiple_failures(tmp_path) -> None:
    paths = write_inputs(tmp_path, queue_recall=0.80, artifact_hash="invalid")
    audit = build_release_audit(*paths)

    assert audit["passed"] is False
    assert audit["checks"]["risk_queue_gate"] is False
    assert audit["checks"]["model_snapshot_integrity"] is False
    assert len(audit["failures"]) == 2
