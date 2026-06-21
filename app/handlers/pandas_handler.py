import os
import pandas as pd
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

CSV_PATH = "data/processed/boxoffice.csv"

PROMPT = ChatPromptTemplate.from_template("""
아래 영화 데이터 분석 결과를 바탕으로 질문에 자연스럽게 답해줘.

[컬럼 설명]
- title: 영화 제목
- genres: 장르
- year: 개봉 연도
- avg_rating: 평균 평점 (5점 만점)
- rating_count: 평점 참여 수
- box_office_million: 추정 박스오피스 (백만 달러)

[분석 데이터]
{data}

질문: {question}
""")

def _compute(df: pd.DataFrame, question: str) -> str:
    q = question.lower()

    if "top" in q or "순위" in q or "흥행" in q or "많이" in q:
        result = df.nlargest(10, "box_office_million")[
            ["title", "year", "avg_rating", "box_office_million"]
        ]
    elif "평점" in q or "rating" in q or "높은" in q:
        result = df.nlargest(10, "avg_rating")[
            ["title", "year", "avg_rating", "rating_count"]
        ]
    elif "장르" in q or "genre" in q:
        result = (
            df.assign(genre=df["genres"].str.split("|"))
            .explode("genre")
            .groupby("genre")["box_office_million"]
            .mean()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )
    elif "연도" in q or "년" in q or "year" in q:
        result = (
            df.dropna(subset=["year"])
            .groupby("year")
            .agg(count=("title", "count"), avg_rating=("avg_rating", "mean"))
            .sort_values("year", ascending=False)
            .head(15)
        )
    else:
        result = df.nlargest(10, "rating_count")[
            ["title", "year", "avg_rating", "box_office_million"]
        ]

    return result.to_string(index=False)

async def pandas_handler(message: str, image_base64: str | None = None) -> str:
    df = pd.read_csv(CSV_PATH)
    data = _compute(df, message)

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.3,
    )
    chain = PROMPT | llm | StrOutputParser()
    return await chain.ainvoke({"data": data, "question": message})
