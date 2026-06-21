from app.router.intent_router import classify_intent
from app.handlers.rag_handler import rag_handler
from app.handlers.sql_handler import sql_handler
from app.handlers.pandas_handler import pandas_handler


async def _placeholder(message: str, image_base64: str | None = None) -> str:
    return f"[{message}] 처리 예정"


HANDLER_MAP = {
    "sql": sql_handler,
    "pandas": pandas_handler,
    "rag": rag_handler,
    "vlm": _placeholder,
}


async def route_and_handle(
    message: str, image_base64: str | None = None
) -> tuple[str, str]:
    route = await classify_intent(message, has_image=image_base64 is not None)
    handler = HANDLER_MAP[route]
    answer = await handler(message, image_base64)
    return answer, route
