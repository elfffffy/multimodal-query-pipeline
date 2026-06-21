from pathlib import Path
from app.rag.indexer import get_vectorstore, KOREAN_TITLES

PLOTS_DIR = Path("data/processed/movie_plots")


def _find_by_korean_title(query: str) -> list[str]:
    for english_title, korean_title in KOREAN_TITLES.items():
        if korean_title in query:
            filename = english_title.replace(" ", "_").replace(":", "") + ".txt"
            filepath = PLOTS_DIR / filename
            if filepath.exists():
                return [filepath.read_text(encoding="utf-8")]
    return []


def retrieve(query: str, k: int = 3) -> list[str]:
    # 키워드 매칭 먼저
    keyword_results = _find_by_korean_title(query)
    if keyword_results:
        return keyword_results

    # 없으면 FAISS 유사도 검색
    vectorstore = get_vectorstore()
    docs = vectorstore.similarity_search(query, k=k)
    return [doc.page_content for doc in docs]
