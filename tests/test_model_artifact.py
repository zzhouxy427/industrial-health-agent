import json

import numpy as np
from sklearn.ensemble import RandomForestRegressor

from src.model_artifact import save_model_bundle, sha256_file, verify_model_bundle


def test_model_bundle_records_model_integrity_and_provenance(tmp_path) -> None:
    model = RandomForestRegressor(n_estimators=3, random_state=42).fit(
        np.array([[0.0], [1.0], [2.0]]), np.array([3.0, 2.0, 1.0])
    )

    manifest = save_model_bundle(
        model,
        ["cycle"],
        {"method": "test", "adjustment": 1.0},
        output_dir=tmp_path,
    )

    model_path = tmp_path / "rul_model.joblib"
    stored_manifest = json.loads((tmp_path / "rul_model_manifest.json").read_text())
    assert model_path.exists()
    assert manifest["model_sha256"] == sha256_file(model_path)
    assert stored_manifest["feature_columns"] == ["cycle"]
    assert stored_manifest["interval_calibration"]["adjustment"] == 1.0

    status = verify_model_bundle(tmp_path / "rul_model_manifest.json")
    assert status["verified"] is True


def test_model_bundle_reports_tampered_binary(tmp_path) -> None:
    model = RandomForestRegressor(n_estimators=3, random_state=42).fit(
        np.array([[0.0], [1.0], [2.0]]), np.array([3.0, 2.0, 1.0])
    )
    save_model_bundle(model, ["cycle"], {}, output_dir=tmp_path)
    (tmp_path / "rul_model.joblib").write_bytes(b"tampered")

    status = verify_model_bundle(tmp_path / "rul_model_manifest.json")

    assert status["available"] is True
    assert status["verified"] is False
    assert "SHA-256" in status["message"]
