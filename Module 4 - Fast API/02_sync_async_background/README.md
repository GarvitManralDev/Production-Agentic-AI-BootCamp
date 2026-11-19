# 2. Synchronous, Asynchronous and Background Workflows

LLM calls are slow. The goal is to run different kinds of work **without making users wait for no reason and without blocking the server**.

```text
Synchronous   → Do it and wait.
Asynchronous  → While waiting, let other work happen.
Background    → Send the response first, do the secondary work afterwards.
```

## Files

| File | Endpoints | Lesson |
| --- | --- | --- |
| `sync_demo.py` | `/sync`, `/blocking-async`, `/ping` | `def` runs in a thread pool. `time.sleep` inside `async def` freezes the whole server. |
| `async_demo.py` | `/sequential`, `/concurrent` | `asyncio.gather()` runs 3 "LLM calls" in about 1× the time instead of 3× |
| `background_demo.py` | `POST /chat`, `POST /reports`, `GET /reports/{id}` | `BackgroundTasks`, plus the job-id + polling pattern |

## Run & try

```bash
python 02_sync_async_background/sync_demo.py
```

```bash
# Terminal A                                   # Terminal B (run right after A)
curl http://127.0.0.1:8080/blocking-async      curl http://127.0.0.1:8080/ping   # hangs ~5s ❌
curl http://127.0.0.1:8080/sync                curl http://127.0.0.1:8080/ping   # instant ✅
```

```bash
python 02_sync_async_background/async_demo.py

curl http://127.0.0.1:8080/sequential   # total_time ≈ 6s
curl http://127.0.0.1:8080/concurrent   # total_time ≈ 2s
```

```bash
python 02_sync_async_background/background_demo.py

curl -X POST "http://127.0.0.1:8080/chat?message=Hello"
cat 02_sync_async_background/chat_logs.txt

curl -X POST "http://127.0.0.1:8080/reports?topic=Python"
# -> {"job_id": "a1b2c3d4", "status": "pending", ...}
curl http://127.0.0.1:8080/reports/a1b2c3d4     # running ... then completed (after 10s)
```

## Mental models

```text
SYNC                         ASYNC                              BACKGROUND
Request                      User A → call LLM → waiting...     Generate answer
  ↓                                   server handles User B         ↓
time.sleep(5)  (WAIT)                 server handles User C     Return response
  ↓                          LLM responds → continue User A         ↓
Return response                                                 Save log afterwards
```

## Rules of thumb

- Use **`async def` + `await`** for I/O with async clients (`httpx.AsyncClient`, async LLM SDKs, async DB drivers).
- Use plain **`def`** when you have to call blocking libraries. FastAPI moves it to a thread for you.
- **Never** call blocking code (`time.sleep`, `requests.get`) inside `async def`.
- `BackgroundTasks` runs in the same process. It suits logs, analytics and emails. Long or critical jobs belong in a real queue (Celery, RQ, Arq) with persistent job storage.

> Async does not make the LLM faster. It lets the server use its waiting time well.
