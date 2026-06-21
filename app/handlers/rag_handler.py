import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.rag.retriever import retrieve

load_dotenv()

PROMPT = ChatPromptTemplate.from_template("""
아래 문서를 참고해서 사용자 질문에 답해줘. 문서에 없는 내용은 모른다고 해.

[참고 문서]
{context}

[질문]
{question}
""")


async def rag_handler(message: str, image_base64: str | None = None) -> str:
    docs = retrieve(message)

    if not docs:
        return "관련된 정보를 찾지 못했어요."

    context = "\n\n---\n\n".join(docs)

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.3,
    )
    chain = PROMPT | llm | StrOutputParser()
    return await chain.ainvoke({"context": context, "question": message})
