"""
Section 7.1 - Rate limiting  (protect from USERS)

Sliding window: each user may make LIMIT requests per WINDOW seconds.
The 6th request inside a minute gets 429 Too Many Requests + Retry-After.

    GET /limited      identify the caller by X-User-Id header (falls back to client IP)
    GET /unlimited    no limit, for comparison

Every response carries:
    X-RateLimit-Limit, X-RateLimit-Remaining   (and Retry-After on 429)

Run:   python 07_resilience/rate_limiting.py
"""

import math
import time
from collections import defaultdict, deque
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response

app = FastAPI(title="Rate Limiting Demo")

LIMIT = 5      # max requests...
WINDOW = 60    # ...per this many seconds

# user_id -> timestamps of recent requests.
# Production: Redis (shared by every server) or an API gateway.
request_history: dict[str, deque[float]] = defaultdict(deque)


def rate_limit(
    request: Request,
    response: Response,
    x_user_id: str | None = Header(default=None),
) -> str:
    user_id = x_user_id or (request.client.host if request.client else "anonymous")
    now = time.monotonic()
    history = request_history[user_id]

    # Drop timestamps that fell out of the window
    while history and now - history[0] >= WINDOW:
        history.popleft()

    if len(history) >= LIMIT:
        retry_after = math.ceil(WINDOW - (now - history[0]))
        raise HTTPException(
            status_code=429,
            detail=f"Too many requests. Try again in {retry_after}s.",
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": str(LIMIT),
                "X-RateLimit-Remaining": "0",
            },
        )

    history.append(now)
    response.headers["X-RateLimit-Limit"] = str(LIMIT)
    response.headers["X-RateLimit-Remaining"] = str(LIMIT - len(history))
    return user_id


@app.get("/limited")
async def limited_endpoint(user_id: str = Depends(rate_limit)):
    return {"message": "Your request was accepted", "user": user_id}


@app.get("/unlimited")
async def unlimited_endpoint():
    return {"message": "No limit here"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        f"{Path(__file__).stem}:app",
        app_dir=str(Path(__file__).parent),
        host="127.0.0.1",
        port=8080,
        reload=True,
    )
