from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def retrieve_guidance(keywords: list[str]) -> list[str]:
    knowledge = Path("docs/maintenance_knowledge.md").read_text(encoding="utf-8")
    sections = knowledge.split("\n## ")
    sections = [section.strip() for section in sections if section.strip()]
    query = " ".join(keywords)
    vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(2, 4))
    matrix = vectorizer.fit_transform(sections + [query])
    scores = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
    ranked = scores.argsort()[::-1]
    return [sections[index] for index in ranked if scores[index] > 0]


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
