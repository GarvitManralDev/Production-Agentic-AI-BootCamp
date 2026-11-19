"""
Section 9 - Managing secrets and environment configuration

    GET /config     non-sensitive settings + a MASKED api key
    GET /health     shows which environment is running

Setup:
    cp 09_secrets_config/.env.example 09_secrets_config/.env   # then edit values

Run:   python 09_secrets_config/app.py
Try:   ENVIRONMENT=production LLM_MODEL=llama-3.3-70b python 09_secrets_config/app.py
"""

from pathlib import Path

from fastapi import Depends, FastAPI

from config import Settings, get_settings

app = FastAPI(title="Environment Config Demo")


def mask(secret: str) -> str:
    return secret[:3] + "*" * max(len(secret) - 6, 4) + secret[-3:] if len(secret) > 6 else "****"


@app.get("/config")
async def show_config(settings: Settings = Depends(get_settings)):
    return {
        "app": settings.app_name,
        "environment": settings.environment,
        "debug": settings.debug,
        "model": settings.llm_model,
        "llm_timeout_seconds": settings.llm_timeout_seconds,
        # NEVER return the real secret - show just enough to know which key is loaded
        "llm_api_key": mask(settings.llm_api_key.get_secret_value()),
    }


@app.get("/health")
async def health(settings: Settings = Depends(get_settings)):
    return {"status": "ok", "environment": settings.environment}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        f"{Path(__file__).stem}:app",
        app_dir=str(Path(__file__).parent),
        host="127.0.0.1",
        port=8080,
        reload=True,
    )
