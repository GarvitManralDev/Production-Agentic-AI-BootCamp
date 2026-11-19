"""
Section 7.3 - Timeouts  (protect from WAITING forever)

    GET /timeout-example?llm_seconds=2&timeout=5    -> 200 (LLM finished in time)
    GET /timeout-example?llm_seconds=10&timeout=5   -> 504 after 5s

asyncio.wait_for() cancels the slow call once the time limit is reached.

Run:   python 07_resilience/timeout.py
"""

import asyncio
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query

app = FastAPI(title="Timeout Demo")


async def slow_llm(seconds: float) -> str:
    await asyncio.sleep(seconds)
    return f"AI response (took {seconds}s)"


@app.get("/timeout-example")
async def timeout_example(
    llm_seconds: float = Query(default=10, ge=0, le=60, description="How long the fake LLM takes"),
    timeout: float = Query(default=5, gt=0, le=60, description="Max seconds we are willing to wait"),
):
    start = time.perf_counter()
    try:
        result = await asyncio.wait_for(slow_llm(llm_seconds), timeout=timeout)
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail=f"LLM request timed out after {timeout}s",
        )

    return {"answer": result, "elapsed": round(time.perf_counter() - start, 2)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        f"{Path(__file__).stem}:app",
        app_dir=str(Path(__file__).parent),
        host="127.0.0.1",
        port=8080,
        reload=True,
    )
