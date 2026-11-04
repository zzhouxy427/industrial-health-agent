from pathlib import Path

import pandas as pd


COLUMNS = [
    "unit_number",
    "cycle",
    "op_setting_1",
    "op_setting_2",
    "op_setting_3",
    *[f"sensor_{index}" for index in range(1, 22)],
]


def load_training_data() -> pd.DataFrame:
    return pd.read_csv(
        "data/raw/train_FD001.txt",
        sep=r"\s+",
        header=None,
        names=COLUMNS,
    )


def add_rul(frame: pd.DataFrame) -> pd.DataFrame:
    last_cycle = frame.groupby("unit_number")["cycle"].transform("max")
    result = frame.copy()
    result["rul"] = last_cycle - result["cycle"]
    return result


def main() -> None:
    frame = add_rul(load_training_data())
    output_path = Path("data/processed/train_fd001_with_rul.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False)

    print("已生成:", output_path)
    print("数据形状:", frame.shape)
    print("\n第一台发动机的前五行:")
    print(frame[frame["unit_number"] == 1][["unit_number", "cycle", "rul"]].head())
    print("\n第一台发动机的最后五行:")
    print(frame[frame["unit_number"] == 1][["unit_number", "cycle", "rul"]].tail())


if __name__ == "__main__":
    main()
