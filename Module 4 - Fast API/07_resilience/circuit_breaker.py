"""
Section 7.4 - Circuit breaker  (protect from FAILED SERVICES)

    CLOSED ──(3 failures in a row)──▶ OPEN ──(wait 10s)──▶ HALF_OPEN
       ▲                               │                     │
       └────────(test call succeeds)───┼─────────────────────┘
                                       └◀──(test call fails)─┘

    GET  /generate?fail=true    force the fake LLM to fail (easy to trip the breaker)
    GET  /generate              70% random failure rate
    GET  /circuit-status
    POST /reset-circuit

While OPEN, requests are rejected instantly with 503 - the broken LLM isn't called at all.

Run:   python 07_resilience/circuit_breaker.py
"""

import random
import time
from enum import Enum
from pathlib import Path

from fastapi import FastAPI, HTTPException

app = FastAPI(title="Circuit Breaker Demo")


class State(str, Enum):
    CLOSED = "CLOSED"        # healthy - requests flow normally
    OPEN = "OPEN"            # broken - reject immediately
    HALF_OPEN = "HALF_OPEN"  # cooling down is over - let ONE test request through


class CircuitOpenError(Exception):
    pass


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_time: float = 10):
        self.failure_threshold = failure_threshold
        self.recovery_time = recovery_time
        self.reset()

    def reset(self) -> None:
        self.state = State.CLOSED
        self.failure_count = 0
        self.opened_at: float | None = None

    def seconds_until_retry(self) -> float:
        if self.opened_at is None:
            return 0
        return max(0.0, self.recovery_time - (time.monotonic() - self.opened_at))

    async def call(self, func, *args, **kwargs):
        # STEP 1: is the circuit open?
        if self.state == State.OPEN:
            if self.seconds_until_retry() > 0:
                raise CircuitOpenError(
                    f"Circuit is OPEN. Try again in {self.seconds_until_retry():.1f}s."
                )
            print("Recovery time over -> HALF_OPEN, sending a test request")
            self.state = State.HALF_OPEN

        # STEP 2: call the real service
        try:
            result = await func(*args, **kwargs)
        except Exception:
            self._on_failure()
            raise

        # STEP 3: success closes the circuit
        if self.state == State.HALF_OPEN:
            print("Test request succeeded -> CLOSED")
        self.reset()
        return result

    def _on_failure(self) -> None:
        self.failure_count += 1
        print(f"LLM call failed ({self.failure_count}/{self.failure_threshold})")

        # A failed test request re-opens immediately
        if self.state == State.HALF_OPEN or self.failure_count >= self.failure_threshold:
            self.state = State.OPEN
            self.opened_at = time.monotonic()
            print("Circuit is now OPEN")


breaker = CircuitBreaker(failure_threshold=3, recovery_time=10)


# --------------------------------------------------
# Fake LLM
# --------------------------------------------------

async def fake_llm(fail: bool | None = None) -> str:
    should_fail = fail if fail is not None else random.random() < 0.7
    if should_fail:
        raise RuntimeError("Temporary LLM service error")
    return "AI generated the answer."


# --------------------------------------------------
# Routes
# --------------------------------------------------

@app.get("/")
async def home():
    return {
        "message": "Circuit Breaker Demo API is running",
        "try": ["/generate?fail=true (x3)", "/circuit-status", "/generate?fail=false"],
    }


@app.get("/generate")
async def generate(fail: bool | None = None):
    try:
        answer = await breaker.call(fake_llm, fail)
    except CircuitOpenError as error:
        # Fail fast - we didn't even call the LLM
        raise HTTPException(status_code=503, detail=str(error))
    except RuntimeError as error:
        raise HTTPException(status_code=502, detail=str(error))

    return {"status": "success", "answer": answer}


@app.get("/circuit-status")
async def circuit_status():
    return {
        "circuit": breaker.state,
        "failure_count": breaker.failure_count,
        "recovery_in_seconds": round(breaker.seconds_until_retry(), 2),
    }


@app.post("/reset-circuit")
async def reset_circuit():
    breaker.reset()
    return {"message": "Circuit breaker reset", "circuit": breaker.state}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        f"{Path(__file__).stem}:app",
        app_dir=str(Path(__file__).parent),
        host="127.0.0.1",
        port=8080,
        reload=True,
    )
