"""
Section 2.2 - Asynchronous work

Imagine each function below calls an external LLM API that takes DELAY seconds.

    GET /sequential  -> await one after another   ~ 3 x DELAY seconds
    GET /concurrent  -> asyncio.gather()          ~ 1 x DELAY seconds

Async does not make the LLM faster - it lets the server use waiting time efficiently.

Run:   python 02_sync_async_background/async_demo.py
"""

import asyncio
import time
from pathlib import Path

from fastapi import FastAPI

app = FastAPI(title="Asynchronous Demo")

# Seconds each fake provider takes
DELAY = 2.0


async def call_llm(provider: str) -> str:
    print(f"{provider} started...")
    await asyncio.sleep(DELAY)  # non-blocking wait: other requests keep running
    print(f"{provider} completed!")
    return f"Response from {provider}"


PROVIDERS = ["OpenAI", "Gemini", "Groq"]


@app.get("/sequential")
async def sequential_example():
    start = time.perf_counter()

    results = []
    for provider in PROVIDERS:
        results.append(await call_llm(provider))

    return {
        "results": results,
        "total_time": f"{time.perf_counter() - start:.2f} seconds",
    }


@app.get("/concurrent")
async def concurrent_example():
    start = time.perf_counter()

    # All three calls start together; we wait for the slowest one
    results = await asyncio.gather(*(call_llm(p) for p in PROVIDERS))

    return {
        "results": results,
        "total_time": f"{time.perf_counter() - start:.2f} seconds",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        f"{Path(__file__).stem}:app",
        app_dir=str(Path(__file__).parent),
        host="127.0.0.1",
        port=8080,
        reload=True,
    )
