import os
import base64
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv()


async def vlm_handler(message: str, image_base64: str | None = None) -> str:
    if not image_base64:
        return "이미지가 첨부되지 않았어요."

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.3,
    )

    content = [
        {"type": "text", "text": message},
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
        },
    ]

    response = await llm.ainvoke([HumanMessage(content=content)])
    return response.content
