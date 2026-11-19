# 7. Rate Limiting, Retries, Timeouts and Circuit Breakers

These four patterns keep the AI API **resilient when users or external services misbehave**.

```text
Rate limit      → protect from USERS            (429)
Retry           → survive TEMPORARY failures    (503 if every attempt fails)
Timeout         → protect from WAITING          (504)
Circuit breaker → protect from FAILED SERVICES  (503, fail fast)
```

## Files

| File | Endpoint(s) |
| --- | --- |
| `rate_limiting.py` | `GET /limited` (5 requests / 60s per `X-User-Id`) |
| `retry.py` | `GET /generate?failure_rate=0.7` |
| `timeout.py` | `GET /timeout-example?llm_seconds=10&timeout=5` |
| `circuit_breaker.py` | `GET /generate?fail=true`, `GET /circuit-status`, `POST /reset-circuit` |

---

## 7.1 Rate limiting

**Problem:** one user sends 10,000 requests, all of them hit the LLM API, and you get a huge bill.

```bash
python 07_resilience/rate_limiting.py

for i in $(seq 1 7); do
  curl -s -o /dev/null -w "request $i -> %{http_code}\n" \
    -H "X-User-Id: garvit" http://127.0.0.1:8080/limited
done
# requests 1-5 -> 200, requests 6-7 -> 429

curl -i -H "X-User-Id: garvit" http://127.0.0.1:8080/limited   # see Retry-After header
curl -i -H "X-User-Id: someone-else" http://127.0.0.1:8080/limited   # separate quota ✅
```

> **Production note:** an in-memory dict only works for a single process. Use Redis, `slowapi`, or an API gateway so every server shares the same counters.

## 7.2 Retry

**Problem:** LLM providers sometimes fail briefly (503s, 429s, network blips).

```bash
python 07_resilience/retry.py

curl "http://127.0.0.1:8080/generate"                   # watch the server terminal
curl "http://127.0.0.1:8080/generate?failure_rate=0"    # succeeds first try
curl "http://127.0.0.1:8080/generate?failure_rate=1"    # 503 after 3 attempts
```

```text
Attempt 1 ❌ → wait 0.5s → Attempt 2 ❌ → wait 1s → Attempt 3 ✅
```

> Retry only transient errors, and use exponential backoff plus jitter. Never retry a 400 or 401. In real projects, use the [`tenacity`](https://tenacity.readthedocs.io/) library.

## 7.3 Timeout

**Problem:** what if the LLM never responds?

```bash
python 07_resilience/timeout.py

curl "http://127.0.0.1:8080/timeout-example?llm_seconds=2&timeout=5"    # 200
curl "http://127.0.0.1:8080/timeout-example?llm_seconds=10&timeout=5"   # 504 after 5s
```

> Never let an external call wait forever. Set timeouts on every HTTP client and LLM SDK call.

## 7.4 Circuit breaker

**Problem:** the LLM provider is completely down, yet every request still waits for it and fails.

```bash
python 07_resilience/circuit_breaker.py

curl "http://127.0.0.1:8080/generate?fail=true"   # 502 (failure 1)
curl "http://127.0.0.1:8080/generate?fail=true"   # 502 (failure 2)
curl "http://127.0.0.1:8080/generate?fail=true"   # 502 (failure 3 → OPEN)
curl "http://127.0.0.1:8080/generate?fail=false"  # 503 instantly, LLM not called
curl  http://127.0.0.1:8080/circuit-status        # {"circuit": "OPEN", "recovery_in_seconds": 7.4}
# ...wait 10 seconds...
curl "http://127.0.0.1:8080/generate?fail=false"  # HALF_OPEN test succeeds → CLOSED ✅
```

```text
CLOSED ──3 failures──▶ OPEN ──10s──▶ HALF_OPEN ──success──▶ CLOSED
                         ▲                │
                         └────failure─────┘
```

> In production, use a tested library such as `pybreaker` or `aiobreaker`, or circuit breaking built into your service mesh or gateway.

## How they fit together

```text
Request → rate limit → circuit breaker → retry( timeout( LLM call ) )
```
