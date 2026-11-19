"""
Section 8 - Making LLM requests idempotent

Same Idempotency-Key  =  same logical operation  =  LLM runs ONCE.

    POST /generate   header: Idempotency-Key: <uuid>    body: {"message": "..."}

    first call                 -> runs the LLM, stores the result         (200)
    retry, same key + body     -> returns the stored result, no LLM call  (200, Idempotent-Replayed: true)
    same key, DIFFERENT body   -> 422  (client bug: keys must be unique per operation)
    same key while still running -> 409  (first request hasn't finished yet)

    GET /stats       how many times the "expensive" LLM actually ran

Run:   python 08_idempotency/idempotent.py
"""

import asyncio
import hashlib
import json
import time
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException, Response
from pydantic import BaseModel, Field

app = FastAPI(title="Idempotent LLM Requests")

# Seconds the fake LLM takes
LLM_DELAY = 2
# How long we remember a key
KEY_TTL_SECONDS = 24 * 60 * 60


class GenerateRequest(BaseModel):
    message: str = Field(min_length=1)


class GenerateResponse(BaseModel):
    answer: str
    generated_at: float


# key -> {"fingerprint", "status": "processing"|"done", "response", "stored_at"}
# Production: Redis / database with a TTL, shared by all servers.
idempotency_store: dict[str, dict] = {}
llm_calls = 0


def fingerprint(body: GenerateRequest) -> str:
    return hashlib.sha256(json.dumps(body.model_dump(), sort_keys=True).encode()).hexdigest()


async def expensive_llm(message: str) -> GenerateResponse:
    global llm_calls
    llm_calls += 1
    print(f"Calling LLM (call #{llm_calls}) ...")
    await asyncio.sleep(LLM_DELAY)
    return GenerateResponse(answer=f"AI generated result for: {message}", generated_at=time.time())


@app.post("/generate", response_model=GenerateResponse)
async def generate(
    body: GenerateRequest,
    response: Response,
    idempotency_key: Annotated[str, Header(min_length=8, max_length=128)],
):
    now = time.time()
    body_hash = fingerprint(body)
    entry = idempotency_store.get(idempotency_key)

    # Forget expired keys
    if entry and now - entry["stored_at"] > KEY_TTL_SECONDS:
        entry = None

    # STEP 1: have we seen this key before?
    if entry:
        if entry["fingerprint"] != body_hash:
            raise HTTPException(
                status_code=422,
                detail="Idempotency-Key was already used with a different request body",
            )
        if entry["status"] == "processing":
            raise HTTPException(
                status_code=409,
                detail="A request with this Idempotency-Key is still being processed",
            )
        print("Duplicate request detected - replaying stored response")
        response.headers["Idempotent-Replayed"] = "true"
        return entry["response"]

    # STEP 2: claim the key BEFORE the slow work, so a parallel retry gets 409
    idempotency_store[idempotency_key] = {
        "fingerprint": body_hash,
        "status": "processing",
        "response": None,
        "stored_at": now,
    }

    try:
        result = await expensive_llm(body.message)
    except Exception:
        # Failed -> release the key so the client can retry
        del idempotency_store[idempotency_key]
        raise

    # STEP 3: store the result for future retries
    idempotency_store[idempotency_key].update(status="done", response=result)
    return result


@app.get("/stats")
async def stats():
    return {"llm_calls": llm_calls, "stored_keys": len(idempotency_store)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        f"{Path(__file__).stem}:app",
        app_dir=str(Path(__file__).parent),
        host="127.0.0.1",
        port=8080,
        reload=True,
    )
