"""Mona Store support API.   uvicorn app.main:app --port 8000"""
from fastapi import FastAPI
from pydantic import BaseModel, Field
from . import llm
from .pipeline import handle

app = FastAPI(title="Mona Store support", version="1.0")

class ChatIn(BaseModel):
    customer_id: int = Field(..., examples=[7])
    message: str = Field(..., min_length=1, max_length=2000, examples=["الأوردر 1042 فين؟"])

class ChatOut(BaseModel):
    trace_id: str
    intent: str
    reply: str
    action: str
    amount: int | None = None
    escalate: bool
    flags: list[str]
    tokens: dict
    ms: int

@app.get("/health")
def health(): return {"ok": True, "llm": llm.LLM, "model": llm.MODEL}

@app.post("/chat", response_model=ChatOut)
def chat(body: ChatIn): return handle(body.message, body.customer_id)
