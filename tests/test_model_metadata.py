from src.model_metadata import MODEL_VERSION, get_model_metadata


def test_model_metadata_matches_selected_production_configuration() -> None:
    metadata = get_model_metadata()

    assert metadata["model_version"] == MODEL_VERSION
    assert metadata["feature_set"] == "raw"
    assert metadata["hyperparameters"]["n_estimators"] == 200
    assert metadata["evaluation_summary"]["official_test_mae"] == 19.53
    assert metadata["evaluation_summary"]["interval_80_coverage"] == 0.86
    assert metadata["evaluation_summary"]["interval_calibration_adjustment"] == 6.33
    assert metadata["performance_gates"]["max_official_test_mae"] == 22.0
