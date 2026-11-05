from pathlib import Path
import argparse

import pandas as pd

from config import RISK_THRESHOLD
from retrieve_guidance import retrieve_guidance


COLUMNS = [
    "unit_number",
    "cycle",
    "op_setting_1",
    "op_setting_2",
    "op_setting_3",
    *[f"sensor_{index}" for index in range(1, 22)],
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an engine diagnostic report")
    parser.add_argument("--unit", type=int, default=15, help="engine unit number")
    args = parser.parse_args()
    unit_number = args.unit
    threshold = RISK_THRESHOLD

    predictions = pd.read_csv("artifacts/fd001_predictions.csv")
    prediction = predictions.loc[predictions["unit_number"] == unit_number].iloc[0]

    test = pd.read_csv(
        "data/raw/test_FD001.txt",
        sep=r"\s+",
        header=None,
        names=COLUMNS,
    )
    history = test[test["unit_number"] == unit_number].sort_values("cycle")

    sensor_findings = []
    trend_changes = []
    for sensor_number in [4, 11]:
        column = f"sensor_{sensor_number}"
        previous = history[column].tail(10).mean()
        earlier = history[column].tail(20).head(10).mean()
        change = previous - earlier
        trend_changes.append(change)
        sensor_findings.append(
            f"{column}: 近期均值 {previous:.3f}，相对前一阶段变化 {change:+.3f}"
        )

    predicted_rul = prediction["predicted_rul"]
    if predicted_rul <= threshold:
        risk = "高风险：建议人工检查"
    elif predicted_rul <= 2 * threshold:
        risk = "中风险：建议安排维护计划"
    else:
        risk = "低风险：继续监控"

    trend_warning = "无明显趋势复核提示"
    if all(change > 0 for change in trend_changes):
        trend_warning = "关键传感器均呈上升趋势：建议人工复核，不能只依据模型的低风险判断"

    guidance = retrieve_guidance(["传感器", "上升", "趋势"])
    guidance_text = "\n\n".join(guidance)

    report = f"""# 发动机 {unit_number} 诊断报告

## 结论

- 当前观测周期：{int(history['cycle'].max())}
- 预测剩余寿命：{predicted_rul:.1f} cycles
- 风险等级：{risk}
- 风险阈值：{threshold} cycles
- 趋势复核：{trend_warning}

## 传感器趋势

{chr(10).join(f'- {finding}' for finding in sensor_findings)}

## 知识库维护建议

{guidance_text}

## 说明

该报告由预测模型和规则生成器自动整理，仅用于研究和学习。
高风险结果需要人工复核，不能直接作为真实设备维护指令。
"""

    output_path = Path(f"artifacts/diagnostic_report_unit_{unit_number}.md")
    output_path.write_text(report, encoding="utf-8")
    print(f"报告已生成: {output_path}")
    print(report)


if __name__ == "__main__":
    main()
