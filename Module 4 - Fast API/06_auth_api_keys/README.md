# 6. Authentication, Authorization and API Keys

Every request to the API must answer two questions:

```text
1. Who are you?                 → Authentication → fails with 401 Unauthorized
2. What are you allowed to do?  → Authorization  → fails with 403 Forbidden
```

An **API key** is a secret the client sends with each request, like a hotel key card:

```text
Client ── X-API-Key: abc123xyz ──▶ Server checks the key ──▶ allow / reject
```

## Files

| File | What it shows |
| --- | --- |
| `authentication.py` | API key from an env var, `APIKeyHeader`, timing-safe comparison, 401 |
| `authorization.py` | Users with roles and a reusable `require_role(...)` dependency, 403 |

## Run & try: authentication

```bash
python 06_auth_api_keys/authentication.py
```

```bash
curl -X POST "http://127.0.0.1:8080/secure-chat?message=hi"                          # 401
curl -X POST "http://127.0.0.1:8080/secure-chat?message=hi" -H "X-API-Key: wrong"    # 401
curl -X POST "http://127.0.0.1:8080/secure-chat?message=hi" -H "X-API-Key: dev-secret-key"   # 200
```

To use your own key: `DEMO_API_KEY=my-key python 06_auth_api_keys/authentication.py`

In `/docs`, click **Authorize** 🔒 and paste the key once. Every request will then include it.

## Run & try: authorization

```bash
python 06_auth_api_keys/authorization.py
```

| Key | `/basic-chat` | `/premium-chat` | `/admin/stats` |
| --- | --- | --- | --- |
| *(none)* | 401 | 401 | 401 |
| `free-123` | ✅ | 403 | 403 |
| `premium-456` | ✅ | ✅ | 403 |
| `admin-789` | ✅ | ✅ | ✅ |

```bash
curl -X POST "http://127.0.0.1:8080/premium-chat?message=hi" -H "X-API-Key: free-123"     # 403
curl -X POST "http://127.0.0.1:8080/premium-chat?message=hi" -H "X-API-Key: premium-456"  # 200
curl http://127.0.0.1:8080/admin/stats -H "X-API-Key: admin-789"                           # 200
curl http://127.0.0.1:8080/me -H "X-API-Key: premium-456"
```

## Complete flow

```text
Request ─▶ AUTHENTICATION (valid key?) ──NO──▶ 401
                    │ YES
                    ▼
           AUTHORIZATION (allowed role?) ──NO──▶ 403
                    │ YES
                    ▼
               AI endpoint ─▶ response
```

## Production tips

- Load keys from env vars or a secret manager, never from source code.
- Store **hashes** of API keys in the database, the same way you store passwords.
- Compare secrets with `secrets.compare_digest` to prevent timing attacks.
- Always use HTTPS. Otherwise anyone on the network can read the header.
- For end users (not machine clients), prefer OAuth2/JWT with `fastapi.security.OAuth2PasswordBearer`.
