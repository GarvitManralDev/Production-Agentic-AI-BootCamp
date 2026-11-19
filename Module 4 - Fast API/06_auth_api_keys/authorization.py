"""
Section 6.2 - Authorization with roles  ("What are you allowed to do?")

    API key        role
    -------------  -------
    free-123       free
    premium-456    premium
    admin-789      admin

    POST /basic-chat     free, premium, admin
    POST /premium-chat   premium, admin          (free -> 403)
    GET  /admin/stats    admin only              (others -> 403)
    GET  /me             any valid key

401 = we don't know who you are.   403 = we know you, but you can't do this.

Run:   python 06_auth_api_keys/authorization.py
"""

from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

app = FastAPI(title="Role-Based Authorization")

Role = Literal["free", "premium", "admin"]


class User(BaseModel):
    name: str
    role: Role


# Pretend this is our database.
# Production: store a HASH of each key (like passwords), never the raw key.
USERS: dict[str, User] = {
    "free-123": User(name="Fiona", role="free"),
    "premium-456": User(name="Priya", role="premium"),
    "admin-789": User(name="Arjun", role="admin"),
}

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


# ----------------------------
# AUTHENTICATION - who are you?
# ----------------------------

def get_current_user(api_key: str | None = Depends(api_key_header)) -> User:
    user = USERS.get(api_key) if api_key else None
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return user


# ----------------------------
# AUTHORIZATION - can you do this?
# ----------------------------

def require_role(*allowed: Role):
    """Dependency factory: `Depends(require_role("premium", "admin"))`."""

    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role: {' or '.join(allowed)}",
            )
        return user

    return checker


# ----------------------------
# ROUTES
# ----------------------------

@app.get("/me", response_model=User)
async def me(user: User = Depends(get_current_user)):
    return user


@app.post("/basic-chat")
async def basic_chat(message: str, user: User = Depends(get_current_user)):
    return {"answer": f"Basic AI answered {user.name}: {message}"}


@app.post("/premium-chat")
async def premium_chat(message: str, user: User = Depends(require_role("premium", "admin"))):
    return {"answer": f"Premium AI (bigger model) answered {user.name}: {message}"}


@app.get("/admin/stats")
async def admin_stats(_: User = Depends(require_role("admin"))):
    return {
        "total_users": len(USERS),
        "by_role": {r: sum(u.role == r for u in USERS.values()) for r in ("free", "premium", "admin")},
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        f"{Path(__file__).stem}:app",
        app_dir=str(Path(__file__).parent),
        host="127.0.0.1",
        port=8080,
        reload=True,
    )
