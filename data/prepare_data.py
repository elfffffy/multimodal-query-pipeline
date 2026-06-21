import io
import zipfile
import sqlite3
import requests
import numpy as np
import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PLOTS_DIR = PROCESSED_DIR / "movie_plots"


def setup_dirs():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def download_movielens():
    print("MovieLens 다운로드 중...")
    url = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
    response = requests.get(url)
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        z.extractall(RAW_DIR)
    print("완료: data/raw/ml-latest-small/")


def create_sqlite():
    print("SQLite DB 생성 중...")
    movies = pd.read_csv(RAW_DIR / "ml-latest-small/movies.csv")
    ratings = pd.read_csv(RAW_DIR / "ml-latest-small/ratings.csv")

    conn = sqlite3.connect(PROCESSED_DIR / "movies.db")
    movies.to_sql("movies", conn, if_exists="replace", index=False)
    ratings.to_sql("ratings", conn, if_exists="replace", index=False)
    conn.close()
    print("완료: data/processed/movies.db")


def create_boxoffice_csv():
    print("박스오피스 CSV 생성 중...")
    movies = pd.read_csv(RAW_DIR / "ml-latest-small/movies.csv")
    ratings = pd.read_csv(RAW_DIR / "ml-latest-small/ratings.csv")

    stats = (
        ratings.groupby("movieId")
        .agg(
            avg_rating=("rating", "mean"),
            rating_count=("rating", "count"),
        )
        .reset_index()
    )

    df = movies.merge(stats, on="movieId")
    df["year"] = df["title"].str.extract(r"\((\d{4})\)").astype("Int64")
    df = df.nlargest(500, "rating_count")

    # 평점 수 기반으로 가상 박스오피스 수치 생성
    np.random.seed(42)
    df["box_office_million"] = (
        (
            df["rating_count"] / df["rating_count"].max() * 500
            + np.random.normal(0, 30, len(df))
        )
        .round(1)
        .clip(1, 500)
    )

    df[
        [
            "movieId",
            "title",
            "genres",
            "year",
            "avg_rating",
            "rating_count",
            "box_office_million",
        ]
    ].to_csv(PROCESSED_DIR / "boxoffice.csv", index=False)
    print("완료: data/processed/boxoffice.csv")


def fetch_movie_plots():
    print("영화 줄거리 수집 중 (Wikipedia API)...")
    headers = {"User-Agent": "multimodal-query-pipeline/1.0 (learning project)"}
    titles = [
        "Inception",
        "The Dark Knight",
        "Interstellar",
        "Pulp Fiction",
        "The Shawshank Redemption",
        "Forrest Gump",
        "The Matrix",
        "Schindler's List",
        "Goodfellas",
        "Fight Club",
        "The Silence of the Lambs",
        "Se7en",
        "The Godfather",
        "Saving Private Ryan",
        "Gladiator",
        "The Lord of the Rings: The Fellowship of the Ring",
        "Avengers: Endgame",
        "Parasite",
        "Oppenheimer",
        "Dune",
    ]

    for title in titles:
        try:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ', '_')}"
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                extract = data.get("extract", "")
                if extract:
                    filepath = (
                        PLOTS_DIR / f"{title.replace(' ', '_').replace(':', '')}.txt"
                    )
                    filepath.write_text(
                        f"Title: {title}\n\n{extract}", encoding="utf-8"
                    )
                    print(f"  ✓ {title}")
        except Exception as e:
            print(f"  ✗ {title}: {e}")

    print("완료: data/processed/movie_plots/")


if __name__ == "__main__":
    setup_dirs()
    download_movielens()
    create_sqlite()
    create_boxoffice_csv()
    fetch_movie_plots()
    print("\n모든 데이터 준비 완료!")
