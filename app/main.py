from fastapi import FastAPI
from app.schemas import ChatRequest, ChatResponse
from app.mapping.query_mapper import route_and_handle

app = FastAPI(title="Multimodal Query Pipeline")


@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    return ChatResponse(answer=f"받은 메시지: {request.message}", route="none")