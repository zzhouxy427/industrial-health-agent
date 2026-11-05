"""Run data-quality checks before diagnosing a selected engine."""

import argparse

from data_quality import assess_unit_quality


def main() -> None:
    parser = argparse.ArgumentParser(description="Check engine sensor data quality")
    parser.add_argument("--unit", type=int, required=True)
    args = parser.parse_args()

    result = assess_unit_quality(args.unit)
    print(f"发动机 {args.unit} 数据质量检查")
    print("缺失值数量:", result["missing_values"])
    print("重复周期数量:", result["duplicate_cycles"])
    print("周期不连续数量:", result["cycle_gaps"])
    print("超出训练集 1%–99% 范围的读数:", result["outside_reference_range"])
    print(f"范围提示比例: {result['outside_ratio']:.2%}")
    print("范围提示阈值: 2.00%")
    print("质量状态:", "通过" if result["passed"] else "需要人工复核")


if __name__ == "__main__":
    main()
