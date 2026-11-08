"""Evaluate empirical coverage of the exported RUL prediction intervals."""

from pathlib import Path

import pandas as pd

from prediction_uncertainty import evaluate_interval_coverage


def main() -> None:
    predictions = pd.read_csv("artifacts/fd001_predictions.csv")
    metrics = evaluate_interval_coverage(
        predictions["actual_rul"].to_numpy(),
        predictions["prediction_p10"].to_numpy(),
        predictions["prediction_p90"].to_numpy(),
    )
    report = f"""# 预测区间经验覆盖率评估

- 样本数：{metrics['sample_count']}
- 区间：随机森林树预测的 P10–P90（名义覆盖率约 80%）
- 实际覆盖率：{metrics['coverage']:.1%}
- 平均区间宽度：{metrics['mean_width']:.2f} cycles
- 真实 RUL 低于区间下界：{metrics['below_lower_count']} 台
- 真实 RUL 高于区间上界：{metrics['above_upper_count']} 台

## 解读

该结果衡量经验区间在 FD001 官方测试集上的实际覆盖程度。若实际覆盖率显著低于 80%，
说明区间偏窄或未校准；若远高于 80%，说明区间可能过宽。无论结果如何，当前区间均不应被解释为经过严格统计校准的置信区间。
"""
    output_path = Path("artifacts/prediction_interval_report.md")
    output_path.write_text(report, encoding="utf-8")
    print(report)
    print("已保存:", output_path)


if __name__ == "__main__":
    main()
