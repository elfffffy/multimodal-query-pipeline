from app.router.intent_router import classify_intent
from app.handlers.rag_handler import rag_handler
from app.handlers.sql_handler import sql_handler
from app.handlers.pandas_handler import pandas_handler
from app.handlers.vlm_handler import vlm_handler


HANDLER_MAP = {
    "sql": sql_handler,
    "pandas": pandas_handler,
    "rag": rag_handler,
    "vlm": vlm_handler,
}


async def route_and_handle(
    message: str, image_base64: str | None = None
) -> tuple[str, str]:
    route = await classify_intent(message, has_image=image_base64 is not None)
    handler = HANDLER_MAP[route]
    answer = await handler(message, image_base64)
    return answer, route
