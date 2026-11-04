import pandas as pd

from src.prepare_data import add_rul
from src.retrieve_guidance import retrieve_guidance


def test_add_rul_reaches_zero_at_last_cycle() -> None:
    frame = pd.DataFrame(
        {
            "unit_number": [1, 1, 2],
            "cycle": [1, 3, 2],
        }
    )

    result = add_rul(frame)

    assert result.loc[1, "rul"] == 0
    assert result.loc[2, "rul"] == 0


def test_knowledge_retrieval_finds_sensor_guidance() -> None:
    matches = retrieve_guidance(["传感器", "上升"])

    assert matches
    assert any("人工复核" in match for match in matches)
