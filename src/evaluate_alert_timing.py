"""Backtest how early the uncertainty-aware queue raises an RUL review alert."""

from pathlib import Path

import pandas as pd

try:
    from .conformal_calibration import (
        INTERVAL_COVERAGE,
        select_simulated_observations,
    )
    from .feature_config import build_selected_features
    from .model_factory import build_rul_model
    from .prediction_uncertainty import (
        apply_conformal_adjustment,
        estimate_conformal_adjustment,
        predict_with_uncertainty,
    )
except ImportError:  # Supports direct script execution.
    from conformal_calibration import INTERVAL_COVERAGE, select_simulated_observations
    from feature_config import build_selected_features
    from model_factory import build_rul_model
    from prediction_uncertainty import (
        apply_conformal_adjustment,
        estimate_conformal_adjustment,
        predict_with_uncertainty,
    )


RISK_THRESHOLD = 20


def summarize_alert_timing(rows: pd.DataFrame, threshold: int = RISK_THRESHOLD) -> dict:
    """Summarize first-alert timing for a collection of held-out engines."""
    if rows.empty:
        return {
            "engine_count": 0,
            "alerted_count": 0,
            "missed_count": 0,
            "early_alert_count": 0,
            "median_lead_cycles": 0.0,
        }

    alerted = rows[rows["alert_type"] != "none"].copy()
    lead = (alerted["actual_rul_at_alert"] - threshold).clip(lower=0)
    return {
        "engine_count": int(len(rows)),
        "alerted_count": int(len(alerted)),
        "missed_count": int((rows["alert_type"] == "none").sum()),
        "early_alert_count": int((alerted["actual_rul_at_alert"] > threshold).sum()),
        "median_lead_cycles": float(lead.median()) if not lead.empty else 0.0,
    }


def build_backtest_rows(frame: pd.DataFrame, threshold: int = RISK_THRESHOLD) -> tuple[pd.DataFrame, float]:
    """Fit/calibrate on earlier train engines, then backtest alerts on held-out engines."""
    prepared, feature_columns = build_selected_features(frame)
    units = sorted(prepared["unit_number"].unique())
    fit_units = set(units[:64])
    calibration_units = set(units[64:80])
    evaluation_units = set(units[80:])

    fit = prepared[prepared["unit_number"].isin(fit_units)]
    calibration_history = prepared[prepared["unit_number"].isin(calibration_units)]
    evaluation_history = prepared[prepared["unit_number"].isin(evaluation_units)].copy()

    model = build_rul_model()
    model.fit(fit[feature_columns], fit["rul"])

    calibration_rows = select_simulated_observations(calibration_history)
    _, cal_lower, cal_upper, _ = predict_with_uncertainty(model, calibration_rows[feature_columns])
    adjustment = estimate_conformal_adjustment(
        calibration_rows["rul"].to_numpy(), cal_lower, cal_upper, coverage=INTERVAL_COVERAGE
    )

    predicted, lower, upper, _ = predict_with_uncertainty(model, evaluation_history[feature_columns])
    lower, upper = apply_conformal_adjustment(lower, upper, adjustment)
    evaluation_history["predicted_rul"] = predicted
    evaluation_history["prediction_p10"] = lower
    evaluation_history["prediction_p90"] = upper

    rows = []
    for unit_number, history in evaluation_history.groupby("unit_number", sort=True):
        history = history.sort_values("cycle")
        alerted = history[history["prediction_p10"] <= threshold]
        if alerted.empty:
            rows.append(
                {
                    "unit_number": int(unit_number),
                    "alert_type": "none",
                    "alert_cycle": None,
                    "actual_rul_at_alert": None,
                    "predicted_rul_at_alert": None,
                    "prediction_p10_at_alert": None,
                }
            )
            continue

        first = alerted.iloc[0]
        alert_type = "critical" if first["predicted_rul"] <= threshold else "review"
        rows.append(
            {
                "unit_number": int(unit_number),
                "alert_type": alert_type,
                "alert_cycle": int(first["cycle"]),
                "actual_rul_at_alert": float(first["rul"]),
                "predicted_rul_at_alert": float(first["predicted_rul"]),
                "prediction_p10_at_alert": float(first["prediction_p10"]),
            }
        )
    return pd.DataFrame(rows), float(adjustment)


def save_backtest_report(rows: pd.DataFrame, adjustment: float) -> None:
    Path("artifacts").mkdir(exist_ok=True)
    rows.to_csv("artifacts/alert_timing_backtest.csv", index=False)
    summary = summarize_alert_timing(rows)
    report = f"""# 风险告警提前量回测

- 回测发动机数：{summary['engine_count']}
- 触发人工复核的发动机数：{summary['alerted_count']}
- 未触发复核的发动机数：{summary['missed_count']}
- 在真实 RUL 进入 {RISK_THRESHOLD} cycles 临界区前已触发的发动机数：{summary['early_alert_count']}
- 提前告警的中位提前量：{summary['median_lead_cycles']:.1f} cycles
- 区间校准偏移：{adjustment:.2f} cycles

## 解读

回测使用发动机级划分：前 64 台拟合模型，随后 16 台用于区间校准，最后 20 台用于告警时序评估。每台设备仅使用当前及历史周期的信息寻找首次告警，不使用未来周期或官方测试标签。该结果只反映 FD001 模拟数据上的研究性回测，不能直接用于真实设备告警时限承诺。
"""
    Path("artifacts/alert_timing_backtest.md").write_text(report, encoding="utf-8")


def main() -> None:
    frame = pd.read_csv("data/processed/train_fd001_with_rul.csv")
    rows, adjustment = build_backtest_rows(frame)
    save_backtest_report(rows, adjustment)
    print("风险告警提前量回测：")
    print(rows.to_string(index=False))
    print("\n", summarize_alert_timing(rows))
    print("已保存: artifacts/alert_timing_backtest.csv")


if __name__ == "__main__":
    main()
