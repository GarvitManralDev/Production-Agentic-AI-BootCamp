"""
Section 6.1 - Authentication with an API key  ("Who are you?")

The client sends:   X-API-Key: <key>
Missing / wrong key -> 401 Unauthorized

    GET  /public        no key needed
    POST /secure-chat   requires a valid X-API-Key

Run:   python 06_auth_api_keys/authentication.py
Key:   DEMO_API_KEY env var (defaults to "dev-secret-key" for local learning)
"""

import os
import secrets
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import APIKeyHeader

app = FastAPI(title="API Key Authentication")

# Read the key from the environment - never hard-code real keys (see section 9)
API_KEY = os.getenv("DEMO_API_KEY", "dev-secret-key")

# auto_error=False -> we raise our own 401 instead of FastAPI's default 403
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str | None = Depends(api_key_header)) -> str:
    # compare_digest takes the same time whether the first or last char differs,
    # so attackers can't guess the key one character at a time (timing attack)
    if api_key is None or not secrets.compare_digest(api_key, API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "APIKey"},
        )
    return api_key


@app.get("/public")
async def public():
    return {"message": "Anyone can see this"}


@app.post("/secure-chat")
async def secure_chat(message: str, _: str = Depends(verify_api_key)):
    # FastAPI runs verify_api_key() BEFORE this function body
    return {"answer": f"Secure AI response for: {message}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        f"{Path(__file__).stem}:app",
        app_dir=str(Path(__file__).parent),
        host="127.0.0.1",
        port=8080,
        reload=True,
    )
