import argparse
import subprocess
import sys


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

    print("\nAgent: 诊断任务完成，请查看 artifacts 目录中的 Markdown 报告。")


if __name__ == "__main__":
    main()
