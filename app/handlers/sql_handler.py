import os
import sqlite3
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

DB_PATH = "data/processed/movies.db"

SCHEMA = """
테이블: movies  (movieId, title, genres)
테이블: ratings (userId, movieId, rating, timestamp)
"""

SQL_PROMPT = ChatPromptTemplate.from_template("""
다음 DB 스키마를 참고해서 질문에 맞는 SQLite 쿼리를 작성해.
SELECT 문만 작성하고, 코드 블록 없이 쿼리만 출력해.

스키마:
{schema}

질문: {question}
""")

ANSWER_PROMPT = ChatPromptTemplate.from_template("""
사용자 질문과 DB 조회 결과를 바탕으로 자연스럽게 답변해줘.

질문: {question}
조회 결과: {result}
""")

def _run_query(sql: str) -> str:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.execute(sql)
        rows = cursor.fetchmany(20)
        cols = [d[0] for d in cursor.description]
        conn.close()
        if not rows:
            return "결과 없음"
        header = " | ".join(cols)
        body = "\n".join(" | ".join(str(v) for v in row) for row in rows)
        return f"{header}\n{body}"
    except Exception as e:
        return f"쿼리 오류: {e}"

async def sql_handler(message: str, image_base64: str | None = None) -> str:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0,
    )

    # 1단계: 질문 → SQL 생성
    sql_chain = SQL_PROMPT | llm | StrOutputParser()
    sql = await sql_chain.ainvoke({"schema": SCHEMA, "question": message})
    sql = sql.strip()

    # 2단계: SQL 실행
    result = _run_query(sql)

    # 3단계: 결과 → 자연어 답변
    answer_chain = ANSWER_PROMPT | llm | StrOutputParser()
    return await answer_chain.ainvoke({"question": message, "result": result})
