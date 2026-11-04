from src.validate_llm_output import validate_text


def test_safe_disclaimer_is_allowed() -> None:
    text = (
        "human review is recommended. sensor trends are rising. "
        "This is a research aid. No automatic shutdown is issued."
    )

    missing, forbidden = validate_text(text)

    assert missing == []
    assert forbidden == []


def test_unsafe_command_is_rejected() -> None:
    text = "human review. sensor trends. research aid. shut down immediately."

    missing, forbidden = validate_text(text)

    assert missing == []
    assert "shut down immediately" in forbidden
