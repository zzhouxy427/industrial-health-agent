"""Local Streamlit dashboard for the industrial health agent."""

from pathlib import Path
import subprocess
import sys

import pandas as pd
import streamlit as st

from config import RISK_THRESHOLD
from data_quality import assess_unit_quality
from audit_log import load_recent_events
from model_monitoring import assess_current_batch_drift
from risk_queue import build_risk_queue


RAW_COLUMNS = [
    "unit_number",
    "cycle",
    "op_setting_1",
    "op_setting_2",
    "op_setting_3",
    *[f"sensor_{index}" for index in range(1, 22)],
]
def load_predictions() -> pd.DataFrame:
    return pd.read_csv("artifacts/fd001_predictions.csv")


def load_test_data() -> pd.DataFrame:
    return pd.read_csv(
        "data/raw/test_FD001.txt",
        sep=r"\s+",
        header=None,
        names=RAW_COLUMNS,
    )


def main() -> None:
    st.set_page_config(page_title="Industrial Health Agent", page_icon="⚙️")
    st.title("⚙️ Industrial Health Agent")
    st.caption("基于 C-MAPSS FD001 的剩余寿命预测与维护诊断原型")

    try:
        predictions = load_predictions()
        test_data = load_test_data()
        monitoring = assess_current_batch_drift()
    except FileNotFoundError:
        st.error("缺少数据或预测文件。请先运行 `python src\\save_predictions.py`。")
        return

    st.subheader("优先人工复核队列")
    if monitoring["warning"]:
        st.warning(
            "模型适用性提示：当前批次与训练集存在显著输入分布偏移（"
            f"{monitoring['significant_feature_count']} 个特征）。"
            "预测结果需要结合人工复核，不代表模型已失效。"
        )
    else:
        st.success("模型适用性提示：未检测到显著的批次级输入分布偏移。")
    risk_queue = build_risk_queue(predictions, RISK_THRESHOLD)
    review_queue = risk_queue.loc[risk_queue["priority"] != "monitor"]
    if review_queue.empty:
        st.success("当前没有预测或预测区间触及风险阈值的发动机。")
    else:
        st.dataframe(
            review_queue[
                [
                    "unit_number",
                    "predicted_rul",
                    "prediction_p10",
                    "prediction_p90",
                    "priority",
                    "review_reason",
                ]
            ],
            hide_index=True,
            use_container_width=True,
        )

    unit = st.sidebar.selectbox(
        "选择发动机", sorted(predictions["unit_number"].unique())
    )
    row = predictions.loc[predictions["unit_number"] == unit].iloc[0]
    predicted_rul = float(row["predicted_rul"])
    risk_level = "高风险" if predicted_rul <= RISK_THRESHOLD else "低风险"
    recommended_action = (
        "建议人工复核" if risk_level == "高风险" else "建议继续监控"
    )

    metric_1, metric_2, metric_3 = st.columns(3)
    metric_1.metric("预测剩余寿命", f"{predicted_rul:.1f} cycles")
    metric_2.metric("风险阈值", f"{RISK_THRESHOLD} cycles")
    metric_3.metric("风险等级", risk_level)
    st.info(f"当前建议：{recommended_action}。传感器趋势仍需结合诊断报告人工判断。")
    st.caption(
        "80% 预测区间："
        f"{float(row['prediction_p10']):.1f} 至 {float(row['prediction_p90']):.1f} cycles"
    )

    quality = assess_unit_quality(unit)
    if quality["passed"]:
        st.success(
            "数据质量通过："
            f"范围提示比例 {quality['outside_ratio']:.2%}（阈值 2.00%）"
        )
    else:
        st.warning("数据质量需要人工复核；请先检查输入数据，再参考预测结果。")

    st.subheader("传感器趋势")
    trajectory = test_data.loc[test_data["unit_number"] == unit].set_index("cycle")
    sensor_4_column, sensor_11_column = st.columns(2)
    with sensor_4_column:
        st.caption("sensor_4")
        st.line_chart(trajectory[["sensor_4"]])
    with sensor_11_column:
        st.caption("sensor_11")
        st.line_chart(trajectory[["sensor_11"]])

    with st.expander("查看基准真值（仅用于实验评估）"):
        st.write(f"实际 RUL：{float(row['actual_rul']):.1f} cycles")
        st.caption("真实部署场景中不可获得该数值，因此不能用于运行时决策。")

    st.subheader("诊断报告")
    report_path = Path(f"artifacts/diagnostic_report_unit_{unit}.md")
    if st.button("生成或刷新诊断报告", type="primary"):
        completed = subprocess.run(
            [sys.executable, "src/agent_cli.py", "--unit", str(unit)],
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            st.error(completed.stderr or completed.stdout)
        else:
            st.success("诊断报告已生成")

    if report_path.exists():
        st.markdown(report_path.read_text(encoding="utf-8"))
    else:
        st.info("点击上方按钮生成该发动机的诊断报告。")

    st.subheader("LLM 辅助诊断（可选）")
    st.caption("调用已配置的模型服务；输出会先通过安全校验，再展示。")
    llm_path = Path(f"artifacts/llm_diagnostic_unit_{unit}.md")
    if st.button("生成 LLM 辅助诊断"):
        with st.spinner("正在调用 LLM 并进行安全校验..."):
            completed = subprocess.run(
                [sys.executable, "src/llm_agent.py", "--unit", str(unit)],
                text=True,
                capture_output=True,
                check=False,
            )
        if completed.returncode != 0:
            st.error(completed.stderr or completed.stdout)
        else:
            st.success("LLM 辅助诊断已通过安全校验")

    if llm_path.exists():
        st.markdown(llm_path.read_text(encoding="utf-8"))

    st.subheader("近期诊断审计记录")
    audit_events = load_recent_events()
    if audit_events:
        audit_frame = pd.DataFrame(audit_events)
        interval = audit_frame.pop("prediction_interval_80")
        audit_frame["interval_80"] = interval.map(
            lambda value: f"{value['lower']:.1f}–{value['upper']:.1f}"
        )
        audit_frame["data_quality_passed"] = audit_frame.pop("data_quality").map(
            lambda value: value["passed"]
        )
        if "model_monitoring" in audit_frame:
            audit_frame["model_drift_warning"] = audit_frame.pop(
                "model_monitoring"
            ).map(lambda value: value.get("warning") if value else None)
        st.dataframe(audit_frame, hide_index=True, use_container_width=True)
    else:
        st.info("暂无审计记录。点击“生成或刷新诊断报告”后将自动生成记录。")

    st.divider()
    st.caption("仅用于研究与学习；不构成真实设备维护或安全指令。")


if __name__ == "__main__":
    main()
