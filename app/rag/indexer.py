import os
import pickle
import hashlib
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader

PLOTS_DIR = Path("data/processed/movie_plots")
INDEX_DIR = Path("faiss_index")
HASH_FILE = INDEX_DIR / "docs_hash.pkl"

KOREAN_TITLES = {
    "Inception": "인셉션",
    "The Dark Knight": "다크 나이트",
    "Interstellar": "인터스텔라",
    "Pulp Fiction": "펄프 픽션",
    "The Shawshank Redemption": "쇼생크 탈출",
    "Forrest Gump": "포레스트 검프",
    "The Matrix": "매트릭스",
    "Schindler's List": "쉰들러 리스트",
    "Goodfellas": "좋은 친구들",
    "Fight Club": "파이트 클럽",
    "The Silence of the Lambs": "양들의 침묵",
    "Se7en": "세븐",
    "The Godfather": "대부",
    "Saving Private Ryan": "라이언 일병 구하기",
    "Gladiator": "글래디에이터",
    "The Lord of the Rings: The Fellowship of the Ring": "반지의 제왕",
    "Avengers: Endgame": "어벤져스 엔드게임",
    "Parasite": "기생충",
    "Oppenheimer": "오펜하이머",
    "Dune": "듄",
}


# 문서 변경 감지용
def _get_docs_hash() -> str:
    files = sorted(PLOTS_DIR.glob("*.txt"))
    content = "".join(f"{f.name}{f.stat().st_mtime}" for f in files)
    return hashlib.md5(content.encode()).hexdigest()


# 인덱스 재생성 필요 여부 판단
def _is_index_stale() -> bool:
    if not (INDEX_DIR / "index.faiss").exists():
        return True
    if not HASH_FILE.exists():
        return True
    with open(HASH_FILE, "rb") as f:
        saved_hash = pickle.load(f)
    return saved_hash != _get_docs_hash()


# 실제 인덱스 생섣
def build_index() -> FAISS:
    INDEX_DIR.mkdir(exist_ok=True)

    docs = []
    for path in PLOTS_DIR.glob("*.txt"):
        loader = TextLoader(str(path), encoding="utf-8")
        loaded = loader.load()

        english_title = path.stem.replace("_", " ")
        korean_title = KOREAN_TITLES.get(english_title, "")
        if korean_title:
            for doc in loaded:
                doc.page_content = f"한국어 제목: {korean_title}\n\n" + doc.page_content
        docs.extend(loaded)

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    # 청킹 후에도 모든 청크에 한국어 제목 유지
    for chunk in chunks:
        source = chunk.metadata.get("source", "")
        english_title = Path(source).stem.replace("_", " ")
        korean_title = KOREAN_TITLES.get(english_title, "")
        if korean_title and not chunk.page_content.startswith("한국어 제목"):
            chunk.page_content = f"한국어 제목: {korean_title}\n\n" + chunk.page_content

    embeddings = HuggingFaceEmbeddings(
        model_name="paraphrase-multilingual-MiniLM-L12-v2"
    )
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(str(INDEX_DIR))

    with open(HASH_FILE, "wb") as f:
        pickle.dump(_get_docs_hash(), f)

    print(f"인덱스 생성 완료: {len(chunks)}개 청크")
    return vectorstore


def load_index() -> FAISS:
    embeddings = HuggingFaceEmbeddings(
        model_name="paraphrase-multilingual-MiniLM-L12-v2"
    )
    return FAISS.load_local(
        str(INDEX_DIR), embeddings, allow_dangerous_deserialization=True
    )


def get_vectorstore() -> FAISS:
    if _is_index_stale():
        print("인덱스가 없거나 오래됨 → 재생성")
        return build_index()
    return load_index()
