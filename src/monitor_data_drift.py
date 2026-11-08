"""Create a batch-level data-distribution monitoring report for FD001."""

from pathlib import Path

from data_drift import assess_feature_drift
from data_quality import FEATURE_COLUMNS, load_raw
from model_monitoring import summarize_drift


def main() -> None:
    train = load_raw("data/raw/train_FD001.txt")
    current = load_raw("data/raw/test_FD001.txt")
    drift = assess_feature_drift(train, current, FEATURE_COLUMNS)

    output_dir = Path("artifacts")
    output_dir.mkdir(exist_ok=True)
    drift.to_csv(output_dir / "data_drift.csv", index=False)

    summary = summarize_drift(drift)
    report = "\n".join(
        [
            "# 输入数据分布监控报告",
            "",
            "- 方法：按训练集分位数分箱计算 PSI（Population Stability Index）。",
            f"- 显著偏移特征（PSI ≥ 0.25）：{summary['significant_feature_count']} 个",
            f"- 中等偏移特征（0.10 ≤ PSI < 0.25）：{summary['moderate_feature_count']} 个",
            "",
            "## PSI 最高的 10 个特征",
            "",
            "| 特征 | PSI | 状态 |",
            "| --- | ---: | --- |",
            *[
                f"| {row.feature} | {row.psi:.3f} | {row.status} |"
                for row in drift.head(10).itertuples(index=False)
            ],
            "",
            "## 解读边界",
            "",
            "PSI 反映当前批次输入分布相对训练集的变化，不等同于模型预测误差，"
            "也不单独代表模型失效。若显著偏移特征较多，应人工复核工况变化、"
            "传感器校准和模型适用范围，再决定是否重训或调整模型。",
        ]
    ) + "\n"
    report_path = output_dir / "data_drift_report.md"
    report_path.write_text(report, encoding="utf-8")

    print(drift.head(10).to_string(index=False))
    print("\n已保存:", output_dir / "data_drift.csv")
    print("已保存:", report_path)


if __name__ == "__main__":
    main()
