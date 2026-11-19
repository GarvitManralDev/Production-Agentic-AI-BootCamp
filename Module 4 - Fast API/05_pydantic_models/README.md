# 5. Building Typed APIs with Pydantic Models

Make sure users send **correct, predictable input** before anything reaches the AI system, and return responses with a **guaranteed shape**.

```text
User → JSON → Pydantic → Valid?
                          ├── NO  → 422 with a clear error message
                          └── YES → AI logic → response_model → JSON
```

## What `typed_chat.py` demonstrates

| Feature | Example |
| --- | --- |
| Length limits | `message: str = Field(min_length=1, max_length=2000)` |
| Number ranges | `temperature: float = Field(ge=0, le=2)` |
| Allowed values only | `model: Literal["llama-3.1-8b", "llama-3.3-70b", "demo-model"]` |
| Nested models | `history: list[Message]` |
| Custom validator | `@field_validator("message")` rejects blank strings |
| Reject typos | `ConfigDict(extra="forbid")` |
| Typed output | `response_model=ChatResponse` filters and validates the response |
| Docs examples | `json_schema_extra` pre-fills the body in `/docs` |

## Run & try

```bash
python 05_pydantic_models/typed_chat.py
```

Open <http://127.0.0.1:8080/docs>. The request example is already filled in.

```bash
# ✅ Valid
curl -X POST http://127.0.0.1:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is RAG?", "temperature": 0.7}'

# ❌ 422 - temperature out of range, empty message
curl -X POST http://127.0.0.1:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "", "temperature": 999}'

# ❌ 422 - unknown model
curl -X POST http://127.0.0.1:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "hi", "model": "gpt-99"}'

# ❌ 422 - typo in field name (extra="forbid")
curl -X POST http://127.0.0.1:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "hi", "temprature": 0.5}'
```

## Takeaway

> Never trust data that comes from outside the application. Validate it first, and type your responses too.
