from src.validate_llm_output import validate_text


def test_safe_disclaimer_is_allowed() -> None:
    text = (
        "human review is recommended. sensor trends are rising. "
        "The prediction interval is 20 to 40 cycles. "
        "This is a research aid. No automatic shutdown is issued."
    )

    missing, forbidden = validate_text(text)

    assert missing == []
    assert forbidden == []


def test_unsafe_command_is_rejected() -> None:
    text = (
        "human review. sensor trends. prediction interval. research aid. "
        "shut down immediately."
    )

    missing, forbidden = validate_text(text)

    assert missing == []
    assert "shut down immediately" in forbidden


def test_missing_prediction_interval_is_rejected() -> None:
    text = "human review. sensor trends. research aid."

    missing, forbidden = validate_text(text)

    assert "prediction interval" in missing
    assert forbidden == []
