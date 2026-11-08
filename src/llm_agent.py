import argparse
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

from settings import load_local_env
from validate_llm_output import validate_text


def main() -> None:
    load_local_env()
    parser = argparse.ArgumentParser(description="Generate a safety-checked LLM diagnostic")
    parser.add_argument("--unit", type=int, default=18)
    args = parser.parse_args()

    api_key = os.environ.get("LLM_API_KEY")
    base_url = os.environ.get("LLM_BASE_URL")
    model = os.environ.get("LLM_MODEL")

    if not api_key or not base_url or not model:
        raise SystemExit(
            "请先设置 LLM_API_KEY、LLM_BASE_URL 和 LLM_MODEL，且不要把密钥写入代码。"
        )

    subprocess.run(
        [sys.executable, "src/export_agent_context.py", "--unit", str(args.unit)],
        check=True,
        capture_output=True,
        text=True,
    )
    context = Path(f"artifacts/agent_context_unit_{args.unit}.json").read_text(
        encoding="utf-8"
    )
    template = Path("docs/diagnostic_prompt.md").read_text(encoding="utf-8")
    prompt = f"{template}\n\n## JSON Context\n```json\n{context}\n```\n"
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "temperature": 0.1,
    }
    request = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        result = json.loads(response.read().decode("utf-8"))

    answer = result["choices"][0]["message"]["content"]
    missing, forbidden = validate_text(answer)
    if missing or forbidden:
        raise SystemExit(
            f"LLM 输出未通过安全校验。缺少: {missing}; 禁止内容: {forbidden}"
        )
    output_path = Path(f"artifacts/llm_diagnostic_unit_{args.unit}.md")
    output_path.write_text(answer, encoding="utf-8")
    print(f"大模型诊断已保存: {output_path}")
    print(answer)


if __name__ == "__main__":
    main()
