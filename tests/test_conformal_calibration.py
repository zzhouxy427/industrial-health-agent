import pandas as pd

from src.conformal_calibration import select_simulated_observations


def test_select_simulated_observations_keeps_causal_per_engine_rows() -> None:
    frame = pd.DataFrame(
        {
            "unit_number": [1, 1, 1, 1, 2, 2, 2, 2],
            "cycle": [1, 2, 3, 4, 1, 2, 3, 4],
        }
    )

    selected = select_simulated_observations(frame, fractions=(0.5, 1.0))

    assert selected[["unit_number", "cycle"]].to_dict("records") == [
        {"unit_number": 1, "cycle": 2},
        {"unit_number": 1, "cycle": 4},
        {"unit_number": 2, "cycle": 2},
        {"unit_number": 2, "cycle": 4},
    ]
