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


def main() -> None:
    data_path = Path("data/raw/train_FD001.txt")
    frame = pd.read_csv(data_path, sep=r"\s+", header=None, names=COLUMNS)

    print("数据形状:", frame.shape)
    print("发动机数量:", frame["unit_number"].nunique())
    print("最大运行周期:", frame["cycle"].max())
    print("\n字段名称:")
    print(list(frame.columns))
    print("\n前五行:")
    print(frame.head())
    print("\n每台发动机的最后运行周期（前 10 台）:")
    print(frame.groupby("unit_number")["cycle"].max().head(10))


if __name__ == "__main__":
    main()
