"""
Section 7.2 - Retries with exponential backoff  (handle TEMPORARY failures)

    GET /generate?failure_rate=0.7

    Attempt 1 ❌ -> wait ~0.5s
    Attempt 2 ❌ -> wait ~1s
    Attempt 3 ✅    (or 503 after MAX_ATTEMPTS)

Only TRANSIENT errors (timeouts, 429, 5xx) are retried.
PERMANENT errors (bad request, invalid API key) fail immediately - retrying won't help.

Run:   python 07_resilience/retry.py
Watch the terminal to see each attempt.
"""

import asyncio
import random
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query

app = FastAPI(title="LLM Retry Demo")

MAX_ATTEMPTS = 3
BASE_DELAY = 0.5   # seconds; doubles every attempt


class TransientLLMError(Exception):
    """Temporary problem - worth retrying (timeout, rate limited, 5xx)."""


class PermanentLLMError(Exception):
    """Will never succeed - don't retry (invalid key, bad request)."""


# --------------------------------------------------
# Fake LLM
# --------------------------------------------------

async def fake_llm(failure_rate: float) -> str:
    roll = random.random()
    print(f"  random roll: {roll:.2f} (fails if < {failure_rate})")
    if roll < failure_rate:
        raise TransientLLMError("Temporary LLM error (503 from provider)")
    return "AI generated the answer."


# --------------------------------------------------
# Retry helper
# --------------------------------------------------

async def call_with_retry(failure_rate: float) -> tuple[str, int]:
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            print(f"Calling LLM, attempt {attempt}/{MAX_ATTEMPTS}")
            return await fake_llm(failure_rate), attempt

        except PermanentLLMError:
            raise  # no point retrying

        except TransientLLMError as error:
            print(f"  attempt {attempt} failed: {error}")
            if attempt == MAX_ATTEMPTS:
                raise

            # Exponential backoff + jitter: 0.5s, 1s, 2s ... (+ random 0-100ms)
            # Jitter stops thousands of clients from retrying at the exact same moment.
            delay = BASE_DELAY * 2 ** (attempt - 1) + random.uniform(0, 0.1 * BASE_DELAY)
            print(f"  waiting {delay:.2f}s before retrying...")
            await asyncio.sleep(delay)

    raise AssertionError("unreachable")


# --------------------------------------------------
# Route
# --------------------------------------------------

@app.get("/generate")
async def generate(failure_rate: float = Query(default=0.7, ge=0, le=1)):
    try:
        answer, attempts = await call_with_retry(failure_rate)
    except TransientLLMError:
        raise HTTPException(
            status_code=503,
            detail=f"LLM service temporarily unavailable after {MAX_ATTEMPTS} attempts.",
        )
    except PermanentLLMError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return {"status": "success", "answer": answer, "attempts": attempts}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        f"{Path(__file__).stem}:app",
        app_dir=str(Path(__file__).parent),
        host="127.0.0.1",
        port=8080,
        reload=True,
    )
