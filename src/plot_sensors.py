from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


COLUMNS = [
    "unit_number",
    "cycle",
    "op_setting_1",
    "op_setting_2",
    "op_setting_3",
    *[f"sensor_{index}" for index in range(1, 22)],
]


def main() -> None:
    frame = pd.read_csv(
        "data/raw/train_FD001.txt",
        sep=r"\s+",
        header=None,
        names=COLUMNS,
    )

    selected = frame[frame["unit_number"] == 1]

    output_path = Path("docs/engine_1_sensors.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    for axis, sensor_number in zip(axes, [2, 4, 11]):
        axis.plot(selected["cycle"], selected[f"sensor_{sensor_number}"])
        axis.set_ylabel(f"sensor_{sensor_number}")
        axis.grid(True, alpha=0.3)

    axes[-1].set_xlabel("cycle")
    fig.suptitle("Engine 1 sensor trajectories")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    print(f"图像已保存到: {output_path}")


if __name__ == "__main__":
    main()
