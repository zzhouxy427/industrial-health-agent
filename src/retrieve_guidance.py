from pathlib import Path


def retrieve_guidance(keywords: list[str]) -> list[str]:
    knowledge = Path("docs/maintenance_knowledge.md").read_text(encoding="utf-8")
    sections = knowledge.split("\n## ")
    matches = []
    for section in sections:
        if any(keyword in section for keyword in keywords):
            matches.append(section.strip())
    return matches


def main() -> None:
    keywords = ["传感器", "上升", "趋势"]
    matches = retrieve_guidance(keywords)
    print("检索关键词:", ", ".join(keywords))
    print("\n匹配的维护建议:\n")
    for match in matches:
        print(match)
        print("\n---\n")


if __name__ == "__main__":
    main()
