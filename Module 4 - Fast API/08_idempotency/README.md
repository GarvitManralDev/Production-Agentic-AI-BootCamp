# 8. Making LLM Requests Idempotent

Prevent the **same logical request from running more than once by accident**.

```text
Generate report → LLM runs ✅ → network drops the response ❌ → client retries → LLM runs AGAIN ❌ ($$)
Agent: send email ✅ → retry → send email AGAIN ❌
```

**Fix:** the client creates a unique `Idempotency-Key` (a UUID) for each logical operation and sends the **same key on every retry**. The server remembers the key and replays the stored result.

```text
Request + Idempotency-Key
        ↓
Seen this key? ── YES ─▶ same body?   ── YES ─▶ return stored result (no LLM call)
        │                     └── NO  ─▶ 422 (key reused for a different request)
        │                still running? ─▶ 409
        NO
        ↓
Claim key → call LLM → store result → return
```

## Run & try

```bash
python 08_idempotency/idempotent.py
```

```bash
KEY=$(uuidgen)

# 1st call - runs the LLM (~2s)
curl -i -X POST http://127.0.0.1:8080/generate \
  -H "Idempotency-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"message": "Write a report"}'

# Retry with the same key - instant, header "Idempotent-Replayed: true", same generated_at
curl -i -X POST http://127.0.0.1:8080/generate \
  -H "Idempotency-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"message": "Write a report"}'

curl http://127.0.0.1:8080/stats      # llm_calls: 1 ✅

# Same key, different body -> 422
curl -i -X POST http://127.0.0.1:8080/generate \
  -H "Idempotency-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"message": "Something else"}'

# No key -> 422 (header is required)
curl -i -X POST http://127.0.0.1:8080/generate \
  -H "Content-Type: application/json" -d '{"message": "hi"}'
```

To see the **409**, send the same new key from two terminals at the same moment. The second request arrives while the first is still running.

## Production tips

- Store keys in **Redis or a database with a TTL**, shared by every server. An in-memory dict disappears on restart.
- Claim the key atomically (Redis `SET key value NX EX 86400`) **before** the expensive work starts.
- Save a fingerprint of the request body so a reused key can't return the wrong result.
- If the operation fails, release the key so the client can retry.

> Same idempotency key means the same logical operation. Don't run expensive or side-effecting work twice by accident.
