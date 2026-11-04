import json
import os
import urllib.request
from pathlib import Path


def main() -> None:
    api_key = os.environ.get("LLM_API_KEY")
    base_url = os.environ.get("LLM_BASE_URL")
    model = os.environ.get("LLM_MODEL")

    if not api_key or not base_url or not model:
        raise SystemExit(
            "请先设置 LLM_API_KEY、LLM_BASE_URL 和 LLM_MODEL，且不要把密钥写入代码。"
        )

    prompt = Path("artifacts/prompt_unit_18.md").read_text(encoding="utf-8")
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
    output_path = Path("artifacts/llm_diagnostic_unit_18.md")
    output_path.write_text(answer, encoding="utf-8")
    print(f"大模型诊断已保存: {output_path}")
    print(answer)


if __name__ == "__main__":
    main()
