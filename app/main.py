from fastapi import FastAPI
from app.schemas import ChatRequest, ChatResponse
from app.mapping.query_mapper import route_and_handle

app = FastAPI(title="Multimodal Query Pipeline")


@app.get("/")
async def root():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    answer, route = await route_and_handle(request.message, request.image_base64)
    return ChatResponse(answer=answer, route=route)
