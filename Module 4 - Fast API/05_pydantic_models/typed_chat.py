"""
Section 5 - Building typed APIs with Pydantic models

Validate EVERYTHING coming in before it reaches the LLM,
and guarantee the SHAPE of everything going out.

    POST /chat      ChatRequest -> ChatResponse
    GET  /models    list of allowed models

Run:   python 05_pydantic_models/typed_chat.py
Docs:  http://127.0.0.1:8080/docs   (request examples are pre-filled)
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field, field_validator

app = FastAPI(title="Typed Chat API")

ModelName = Literal["llama-3.1-8b", "llama-3.3-70b", "demo-model"]


# =========================
# REQUEST MODELS
# =========================

class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    # Reject unknown fields - catches client typos like "temprature"
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "message": "What is RAG?",
                    "model": "demo-model",
                    "temperature": 0.7,
                    "max_tokens": 256,
                    "history": [
                        {"role": "user", "content": "Hi"},
                        {"role": "assistant", "content": "Hello! How can I help?"},
                    ],
                }
            ]
        },
    )

    message: str = Field(min_length=1, max_length=2000)
    model: ModelName = "demo-model"
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=256, ge=1, le=4096)
    history: list[Message] = Field(default_factory=list, max_length=50)

    @field_validator("message")
    @classmethod
    def message_not_blank(cls, value: str) -> str:
        # min_length=1 allows "   " - strip and check again
        value = value.strip()
        if not value:
            raise ValueError("message cannot be blank")
        return value


# =========================
# RESPONSE MODELS
# =========================

class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatResponse(BaseModel):
    answer: str
    model: ModelName
    usage: Usage
    created_at: datetime


# =========================
# ROUTES
# =========================

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # By the time we get here, `request` is fully validated and typed
    answer = f"You asked: {request.message}"

    prompt_tokens = len(request.message.split()) + sum(
        len(m.content.split()) for m in request.history
    )
    completion_tokens = len(answer.split())

    return ChatResponse(
        answer=answer,
        model=request.model,
        usage=Usage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        ),
        created_at=datetime.now(timezone.utc),
    )


@app.get("/models", response_model=list[str])
async def list_models():
    return list(ModelName.__args__)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        f"{Path(__file__).stem}:app",
        app_dir=str(Path(__file__).parent),
        host="127.0.0.1",
        port=8080,
        reload=True,
    )
