import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

ROUTE_PROMPT = ChatPromptTemplate.from_template("""
너는 사용자 질문을 분류하는 분류기야.
반드시 아래 4개 중 하나의 단어만 출력해. 다른 말은 절대 하지 마.

sql    - 영화 목록, 감독, 장르, 출연진 등 DB에서 조회하는 질문
pandas - 통계, 순위, 평균, 흥행 분석 등 수치 계산이 필요한 질문
rag    - 줄거리, 내용, 배경, 설명 등 문서에서 찾아야 하는 질문
vlm    - 이미지가 첨부된 질문

질문: {message}
""")


def get_router():
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0,
    )
    
    return ROUTE_PROMPT | llm | StrOutputParser()


async def classify_intent(message: str, has_image: bool = False) -> str:
    if has_image:
        return "vlm"

    chain = get_router()
    result = await chain.ainvoke({"message": message})
    route = result.strip().lower()

    if route not in ("sql", "pandas", "rag", "vlm"):
        route = "rag"

    return route
