# 10. Capstone: Production-Ready Streaming LLM API

A small but complete FastAPI project that combines **sections 1–9** into one app, with a web UI for normal and streaming responses.

> The LLM is simulated, so you don't need a paid API key.
>
> Based on [entbappy/Build-a-Production-Ready-Streaming-LLM-API](https://github.com/entbappy/Build-a-Production-Ready-Streaming-LLM-API) from the course (Apache-2.0, see [`LICENSE`](./LICENSE)).

## Concepts → where they were taught

| Concept | Used in this project | Section |
| --- | --- | --- |
| Async AI workloads | `async def` routes, `asyncio.sleep` fake LLM | [2](../02_sync_async_background/) |
| Background logging | `BackgroundTasks` writes `chat_logs.txt` after responding | [2](../02_sync_async_background/) |
| SSE streaming | `POST /v1/chat/stream` | [3](../03_streaming_sse/) |
| Pydantic validation | `src/models.py` (`ChatRequest`, `ChatResponse`) | [5](../05_pydantic_models/) |
| API-key authentication | `src/security.py` (`X-API-Key` header) | [6](../06_auth_api_keys/) |
| Rate limiting | `src/rate_limiter.py` (per API key) | [7](../07_resilience/) |
| Retry + timeout | `src/services/llm_service.py` + `asyncio.wait_for(..., 8)` | [7](../07_resilience/) |
| Idempotency | `Idempotency-Key` header on `POST /v1/chat` | [8](../08_idempotency/) |
| Environment config | `src/config.py` + `.env` | [9](../09_secrets_config/) |
| Templates + static files | Jinja2 `templates/`, `static/` | new |

## Project structure

```text
10_capstone_streaming_llm_api/
├── app.py                     # FastAPI app: routes, idempotency, background logging
├── src/
│   ├── config.py              # Settings loaded from .env
│   ├── models.py              # Pydantic request / response models
│   ├── security.py            # API-key authentication
│   ├── rate_limiter.py        # In-memory sliding-window rate limiter
│   └── services/
│       └── llm_service.py     # Fake LLM + retry + word streaming
├── templates/index.html       # Web UI (Jinja2)
├── static/                    # app.js (fetch + SSE reader), style.css
├── .env.example
├── requirements.txt
└── LICENSE
```

## Run

From the `Module 4 - Fast API` folder:

```bash
pip install -r requirements.txt   # module requirements (includes jinja2)

cp 10_capstone_streaming_llm_api/.env.example 10_capstone_streaming_llm_api/.env

python 10_capstone_streaming_llm_api/app.py
```

- Web UI: <http://127.0.0.1:8080>
- Swagger: <http://127.0.0.1:8080/docs>

The default API key is `course-secret`, and the web UI pre-fills it.

## Try it

### In the browser

1. Open <http://127.0.0.1:8080>.
2. Type a question, for example *Explain RAG in simple words*.
3. Click **Normal Response** (waits about 2s and returns the whole answer) or **Stream Response** (the answer appears word by word).

### With curl

```bash
# Health check (no key needed)
curl http://127.0.0.1:8080/health

# Normal response
curl -X POST http://127.0.0.1:8080/v1/chat \
  -H "Content-Type: application/json" -H "X-API-Key: course-secret" \
  -d '{"message": "Explain RAG"}'

# Streaming response (SSE)
curl -N -X POST http://127.0.0.1:8080/v1/chat/stream \
  -H "Content-Type: application/json" -H "X-API-Key: course-secret" \
  -d '{"message": "Explain RAG"}'

# Idempotency: the 2nd call returns instantly with "cached": true
curl -X POST http://127.0.0.1:8080/v1/chat \
  -H "Content-Type: application/json" -H "X-API-Key: course-secret" \
  -H "Idempotency-Key: demo-123" -d '{"message": "Explain RAG"}'

# Wrong key -> 401
curl -i -X POST http://127.0.0.1:8080/v1/chat \
  -H "Content-Type: application/json" -H "X-API-Key: wrong" \
  -d '{"message": "hi"}'

# Invalid body -> 422
curl -i -X POST http://127.0.0.1:8080/v1/chat \
  -H "Content-Type: application/json" -H "X-API-Key: course-secret" \
  -d '{"message": "", "temperature": 5}'
```

Send more than `RATE_LIMIT` (10) requests within a minute and you'll get **429 Too Many Requests**.

## Request flow

```text
Browser / curl
   ↓
FastAPI
   ↓
API key authentication   → 401
   ↓
Rate limiting            → 429
   ↓
Pydantic validation      → 422
   ↓
Idempotency check        → cached response
   ↓
Retry + timeout          → 503 / 504
   ↓
Fake LLM
   ↓
Normal JSON response  OR  SSE stream
   ↓
Background logging (after the response is sent)
```

## Production notes

- Rate limiting and idempotency are deliberately **kept in memory** so the code is easy to read. A real deployment with several servers would use Redis or a database.
- To use a real model, replace the functions in `src/services/llm_service.py` with a real provider (Groq, OpenAI, Anthropic, ...). The rest of the project can stay almost the same.
