"""
Section 2.1 - Synchronous work (and the #1 async mistake)

    GET /sync           `def` + time.sleep()        -> FastAPI runs it in a thread pool.
                                                       Slow for THIS user, others are fine.
    GET /blocking-async `async def` + time.sleep()  -> BLOCKS THE EVENT LOOP.
                                                       Every other request freezes too.
    GET /ping           Instant endpoint, used to feel the difference.

Experiment: open /blocking-async in one tab, then hit /ping in another.
/ping hangs until the sleep finishes. Repeat with /sync - /ping answers instantly.

Run:   python 02_sync_async_background/sync_demo.py
"""

import time
from pathlib import Path

from fastapi import FastAPI

app = FastAPI(title="Synchronous Demo")

# Seconds to simulate a slow LLM call
DELAY = 5


@app.get("/sync")
def synchronous_example():
    # Plain `def` -> FastAPI runs this in a worker thread,
    # so time.sleep() only blocks this one request.
    print("Sync task started")
    time.sleep(DELAY)
    print("Sync task completed")
    return {"message": "Synchronous task completed", "waited_seconds": DELAY}


@app.get("/blocking-async")
async def blocking_async_example():
    # WRONG: `async def` runs ON the event loop.
    # time.sleep() is not awaitable, so the whole server stops for DELAY seconds.
    # Use `await asyncio.sleep()` / async clients instead (see async_demo.py).
    print("Blocking the event loop...")
    time.sleep(DELAY)
    return {"message": "Event loop was blocked", "waited_seconds": DELAY}


@app.get("/ping")
async def ping():
    return {"pong": time.strftime("%H:%M:%S")}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        f"{Path(__file__).stem}:app",
        app_dir=str(Path(__file__).parent),
        host="127.0.0.1",
        port=8080,
        reload=True,
    )
