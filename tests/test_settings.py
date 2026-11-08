import os

from src.settings import load_local_env


def test_load_local_env_reads_missing_values_only(tmp_path, monkeypatch) -> None:
    path = tmp_path / ".env"
    path.write_text("TEST_AGENT_KEY=from_file\nEXISTING=value_from_file\n", encoding="utf-8")
    monkeypatch.delenv("TEST_AGENT_KEY", raising=False)
    monkeypatch.setenv("EXISTING", "keep_existing")

    load_local_env(path)

    assert os.environ["TEST_AGENT_KEY"] == "from_file"
    assert os.environ["EXISTING"] == "keep_existing"
