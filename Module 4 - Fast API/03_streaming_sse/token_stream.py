"""
Section 3.1 - Streaming LLM tokens with Server-Sent Events (SSE)

    GET /stream?prompt=...   -> text/event-stream, one token per event

SSE wire format (each event ends with a blank line):

    event: token
    data: {"text": "Machine "}

    event: done
    data: {"tokens": 8}

Run:   python 03_streaming_sse/token_stream.py
Try:   curl -N "http://127.0.0.1:8080/stream?prompt=What is ML"
"""

import asyncio
import json
from collections.abc import AsyncIterator
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI(title="SSE Token Streaming")

# Seconds between tokens so the streaming is visible
TOKEN_DELAY = 0.3

SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",  # stop nginx from buffering the stream
}


def sse(event: str, data: dict) -> str:
    """Format one Server-Sent Event."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def fake_llm_tokens(prompt: str) -> AsyncIterator[str]:
    # A real app would iterate over a streaming LLM client here,
    # e.g. `async for chunk in client.chat.completions.create(..., stream=True)`
    answer = "Machine learning allows computers to learn patterns from data."
    for word in answer.split(" "):
        await asyncio.sleep(TOKEN_DELAY)
        yield word + " "


async def token_events(prompt: str) -> AsyncIterator[str]:
    count = 0
    async for token in fake_llm_tokens(prompt):
        count += 1
        yield sse("token", {"text": token})
    yield sse("done", {"tokens": count})


@app.get("/stream")
async def stream(prompt: str = "What is machine learning?"):
    return StreamingResponse(
        token_events(prompt),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        f"{Path(__file__).stem}:app",
        app_dir=str(Path(__file__).parent),
        host="127.0.0.1",
        port=8080,
        reload=True,
    )
