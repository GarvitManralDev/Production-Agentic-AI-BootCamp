# 9. Managing Secrets and Environment Configuration

Keep API keys, passwords, database URLs and environment-specific settings **out of source code**.

```python
OPENAI_API_KEY = "sk-super-secret-key"   # ❌  git add . && git push → key leaked
```

```text
              SAME CODE
                 │
       ┌─────────┼─────────┐
       ↓         ↓         ↓
      DEV       TEST      PROD
   Dev keys   Test keys  Prod keys
```

## Files

| File | Purpose | Commit it? |
| --- | --- | --- |
| `config.py` | Typed `Settings` class (pydantic-settings) | ✅ |
| `app.py` | Reads settings through `Depends(get_settings)` | ✅ |
| `.env.example` | Template that lists every variable, with fake values | ✅ |
| `.env` | Your **real** values | ❌ git-ignored |

## Run & try

```bash
cp 09_secrets_config/.env.example 09_secrets_config/.env   # edit LLM_API_KEY
python 09_secrets_config/app.py
curl http://127.0.0.1:8080/config
```

Real environment variables **override** `.env`:

```bash
ENVIRONMENT=production LLM_MODEL=llama-3.3-70b python 09_secrets_config/app.py
curl http://127.0.0.1:8080/config    # environment: production, model: llama-3.3-70b
```

The app **fails fast** when config is missing or invalid:

```bash
ENVIRONMENT=staging python 09_secrets_config/app.py
# ValidationError: environment must be 'development' | 'test' | 'production'
```

## Key ideas in `config.py`

- **Typed settings.** `debug: bool` turns `"true"` into `True`, and `Literal[...]` restricts the allowed values.
- **Required secrets.** `llm_api_key` has no default, so the app won't start without it.
- **`SecretStr`.** `print(settings)` shows `llm_api_key=SecretStr('**********')`. Call `.get_secret_value()` only where you actually need the key.
- **`@lru_cache get_settings()`.** The `.env` file is read once.
- **Absolute `env_file` path.** The config works no matter which folder you start the app from.

## Production tips

- Locally, use `.env`. On servers, use real environment variables or a secret manager (AWS Secrets Manager, GCP Secret Manager, Vault, Doppler).
- If a secret is ever committed, **rotate it**. Deleting the commit isn't enough, because it may already have been cloned or cached.
- Never log or return secrets. Mask them as `/config` does.

> Configuration changes between environments. Source code shouldn't have to.
