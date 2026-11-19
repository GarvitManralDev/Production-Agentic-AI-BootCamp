# Module 4 - Building Production AI APIs with FastAPI

Building an LLM app is about making the AI work. **Production AI engineering** is about keeping it working once real users, real traffic, real failures, real costs and real infrastructure show up.

Each section is a small, self-contained FastAPI app. You can run it on localhost and try it with curl, `/docs`, or the browser.

## Sections

| # | Section | Files | Key idea |
| --- | --- | --- | --- |
| 1 | [Intro to FastAPI + CRUD](./01_intro_crud/) | `crud.py` | Routes, path params, POST/GET/PUT/PATCH/DELETE |
| 2 | [Sync, Async & Background](./02_sync_async_background/) | `sync_demo.py`, `async_demo.py`, `background_demo.py` | Don't block the event loop; respond first, work later |
| 3 | [Streaming with SSE](./03_streaming_sse/) | `token_stream.py`, `agent_stream.py` | Stream tokens, tool events and agent progress |
| 4 | [WebSockets](./04_websockets/) | `chat.py` | Two-way, real-time agent chat |
| 5 | [Typed APIs with Pydantic](./05_pydantic_models/) | `typed_chat.py` | Validate input, guarantee output shape |
| 6 | [Auth & API Keys](./06_auth_api_keys/) | `authentication.py`, `authorization.py` | 401 vs 403, role-based access |
| 7 | [Rate Limits, Retries, Timeouts, Circuit Breakers](./07_resilience/) | `rate_limiting.py`, `retry.py`, `timeout.py`, `circuit_breaker.py` | Survive bad users and failing providers |
| 8 | [Idempotent LLM Requests](./08_idempotency/) | `idempotent.py` | Same key → LLM runs once |
| 9 | [Secrets & Environment Config](./09_secrets_config/) | `config.py`, `app.py` | pydantic-settings, `.env`, `SecretStr` |

Every section folder has its own README with the concept, a diagram, and copy-paste curl commands.

## Setup

```bash
cd "Module 4 - Fast API"

conda create -n fastapi-demo python=3.11 -y
conda activate fastapi-demo
pip install -r requirements.txt
```

Section 9 also needs a `.env`:

```bash
cp 09_secrets_config/.env.example 09_secrets_config/.env
```

## Run any demo on localhost

All commands run from the `Module 4 - Fast API` folder:

```bash
python 01_intro_crud/crud.py
python 03_streaming_sse/agent_stream.py
python 07_resilience/circuit_breaker.py
# ...etc
```

Every app serves on **<http://127.0.0.1:8080>** with auto-reload, so stop one (`Ctrl+C`) before starting the next.

- <http://127.0.0.1:8080/docs> is the interactive Swagger UI for every app.
- <http://127.0.0.1:8080/> is the browser UI for `agent_stream.py` (SSE) and `chat.py` (WebSocket).

You can also run them with uvicorn directly, for example `uvicorn crud:app --reload --app-dir 01_intro_crud --port 8080`.

## Folder layout

```text
Module 4 - Fast API/
├── 01_intro_crud/ … 09_secrets_config/   # one folder per section: code + README
├── notes/                                # original lecture notes (docs.md, excalidraw)
└── requirements.txt
```
