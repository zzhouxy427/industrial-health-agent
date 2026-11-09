"""Evaluate whether input monitoring reacts to controlled, reversible shifts."""

from pathlib import Path

import pandas as pd

try:
    from .data_drift import assess_feature_drift
    from .data_quality import FEATURE_COLUMNS, load_raw
    from .model_monitoring import summarize_drift
except ImportError:  # Supports direct script execution.
    from data_drift import assess_feature_drift
    from data_quality import FEATURE_COLUMNS, load_raw
    from model_monitoring import summarize_drift


def add_standard_deviation_shift(
    frame: pd.DataFrame, reference: pd.DataFrame, feature: str, standard_deviations: float
) -> pd.DataFrame:
    """Return a copy with one feature shifted by a reference-data standard deviation scale."""
    if feature not in frame or feature not in reference:
        raise ValueError(f"feature not present in both frames: {feature}")
    shifted = frame.copy()
    scale = float(reference[feature].std(ddof=0))
    if scale == 0:
        raise ValueError(f"reference feature has zero variation: {feature}")
    shifted[feature] = shifted[feature] + standard_deviations * scale
    return shifted


def evaluate_drift_scenarios(
    reference: pd.DataFrame,
    current: pd.DataFrame,
    feature_columns: list[str],
    scenarios: list[tuple[str, str | None, float]],
) -> pd.DataFrame:
    """Run baseline and controlled-shift scenarios, returning compact monitoring evidence."""
    records = []
    for name, feature, shift_std in scenarios:
        scenario = current
        if feature is not None:
            scenario = add_standard_deviation_shift(current, reference, feature, shift_std)
        drift = assess_feature_drift(reference, scenario, feature_columns)
        summary = summarize_drift(drift)
        injected_psi = None
        if feature is not None:
            injected_psi = float(drift.loc[drift["feature"] == feature, "psi"].iloc[0])
        records.append(
            {
                "scenario": name,
                "injected_feature": feature or "none",
                "shift_standard_deviations": shift_std,
                "injected_feature_psi": injected_psi,
                "significant_feature_count": summary["significant_feature_count"],
                "moderate_feature_count": summary["moderate_feature_count"],
                "warning": summary["warning"],
                "top_shifted_feature": summary["top_shifted_features"][0]["feature"],
                "top_shifted_psi": summary["top_shifted_features"][0]["psi"],
            }
        )
    return pd.DataFrame(records)


def main() -> None:
    train = load_raw("data/raw/train_FD001.txt")
    current = load_raw("data/raw/test_FD001.txt")
    scenarios = [
        ("observed_fd001_test", None, 0.0),
        ("sensor_4_calibration_offset", "sensor_4", 3.0),
        ("sensor_11_calibration_offset", "sensor_11", 3.0),
        ("op_setting_1_operating_shift", "op_setting_1", 3.0),
    ]
    results = evaluate_drift_scenarios(train, current, FEATURE_COLUMNS, scenarios)

    output_dir = Path("artifacts")
    output_dir.mkdir(exist_ok=True)
    results.to_csv(output_dir / "drift_stress_test.csv", index=False)
    report_lines = [
        "# 输入漂移压力测试",
        "",
        "在不修改原始 FD001 文件的前提下，复制当前测试批次并对单个输入特征施加训练集标准差 3 倍的加性偏置。该测试验证 PSI 监控是否能把受控输入偏移标记为需要人工复核；不评估真实故障机理，也不代表生产环境中的传感器误差范围。",
        "",
        "| 场景 | 注入特征 | 偏移（训练集标准差） | 注入特征 PSI | 显著偏移特征数 | 监控告警 |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in results.itertuples(index=False):
        injected_psi = "-" if pd.isna(row.injected_feature_psi) else f"{row.injected_feature_psi:.3f}"
        report_lines.append(
            f"| {row.scenario} | {row.injected_feature} | {row.shift_standard_deviations:.1f} | {injected_psi} | {row.significant_feature_count} | {'是' if row.warning else '否'} |"
        )
    report_lines.extend(
        [
            "",
            "## 解读边界",
            "",
            "受控偏移场景的告警只能证明当前 PSI 实现对该类统计分布变化敏感。它不能单独证明模型准确率下降，更不能自动触发停机、维修或模型下线。发生告警后，应由人工检查工况、传感器校准、数据采集和模型适用范围。",
        ]
    )
    (output_dir / "drift_stress_test.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(results.to_string(index=False))
    print("已保存:", output_dir / "drift_stress_test.csv")
    print("已保存:", output_dir / "drift_stress_test.md")


if __name__ == "__main__":
    main()
