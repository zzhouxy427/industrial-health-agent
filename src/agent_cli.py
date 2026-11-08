import argparse
import json
import subprocess
import sys
from pathlib import Path

from audit_log import append_diagnosis_event


def main() -> None:
    parser = argparse.ArgumentParser(description="Industrial health agent")
    parser.add_argument("--unit", type=int, required=True)
    args = parser.parse_args()

    print(f"Agent: 收到发动机 {args.unit} 的诊断请求")
    print("Agent: 调用预测、趋势分析和知识库工具...\n")

    subprocess.run(
        [
            sys.executable,
            "src/generate_diagnostic_report.py",
            "--unit",
            str(args.unit),
        ],
        check=True,
    )

    subprocess.run(
        [sys.executable, "src/export_agent_context.py", "--unit", str(args.unit)],
        check=True,
    )
    context_path = Path(f"artifacts/agent_context_unit_{args.unit}.json")
    context = json.loads(context_path.read_text(encoding="utf-8"))
    append_diagnosis_event(context)

    print("\nAgent: 诊断任务完成，已生成报告和审计记录。")


if __name__ == "__main__":
    main()
