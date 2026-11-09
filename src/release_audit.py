"""Build one local release verdict from model, triage, and artifact safeguards."""

import json
from pathlib import Path

try:
    from .release_status import load_release_status
    from .risk_queue_status import load_risk_queue_status
    from .model_artifact import verify_model_bundle
except ImportError:  # Supports direct script execution.
    from release_status import load_release_status
    from risk_queue_status import load_risk_queue_status
    from model_artifact import verify_model_bundle


def build_release_audit(
    evaluation_path: Path = Path("artifacts/official_evaluation.json"),
    queue_path: Path = Path("artifacts/risk_queue_evaluation.json"),
    manifest_path: Path = Path("artifacts/rul_model_manifest.json"),
) -> dict:
    """Return an explicit local release verdict without claiming production readiness."""
    performance = load_release_status(evaluation_path)
    queue = load_risk_queue_status(queue_path)
    artifact = verify_model_bundle(manifest_path)
    checks = {
        "performance_gate": performance["passed"],
        "risk_queue_gate": queue["passed"],
        "model_snapshot_integrity": artifact["verified"],
    }
    failures = []
    if not checks["performance_gate"]:
        failures.extend(performance["failures"])
    if not checks["risk_queue_gate"]:
        failures.extend(queue["failures"])
    if not checks["model_snapshot_integrity"]:
        failures.append(artifact["message"])
    return {
        "passed": not failures,
        "checks": checks,
        "failures": failures,
        "model_version": performance["model_version"],
        "scope_note": (
            "这是本地 FD001 研究原型的发布检查，不是生产部署、安全认证或维护授权。"
        ),
    }


def format_release_audit(audit: dict) -> str:
    """Format the audit as a compact human-readable Markdown artifact."""
    verdict = "通过" if audit["passed"] else "未通过"
    check_rows = "\n".join(
        f"| {name} | {'通过' if passed else '未通过'} |"
        for name, passed in audit["checks"].items()
    )
    failure_text = "\n".join(f"- {failure}" for failure in audit["failures"]) or "- 无"
    return f"""# 本地发布审计

- 结论：**{verdict}**
- 模型版本：`{audit['model_version']}`
- 范围：{audit['scope_note']}

| 检查项 | 状态 |
| --- | --- |
{check_rows}

## 未通过项

{failure_text}
"""


def main() -> None:
    audit = build_release_audit()
    output_dir = Path("artifacts")
    output_dir.mkdir(exist_ok=True)
    (output_dir / "release_audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / "release_audit.md").write_text(
        format_release_audit(audit), encoding="utf-8"
    )
    print(format_release_audit(audit))
    print("已保存:", output_dir / "release_audit.json")
    print("已保存:", output_dir / "release_audit.md")
    if not audit["passed"]:
        raise SystemExit("本地发布审计未通过")


if __name__ == "__main__":
    main()
