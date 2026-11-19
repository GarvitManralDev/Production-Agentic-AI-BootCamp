"""
Typed application settings loaded from environment variables / .env

Priority (highest wins):
    1. Real environment variables   (export LLM_MODEL=...)
    2. .env file next to this config.py
    3. Defaults below
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Absolute path -> works no matter which folder you run from
        env_file=Path(__file__).parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Production AI API"
    environment: Literal["development", "test", "production"] = "development"
    debug: bool = False

    # No default -> the app refuses to start if it's missing
    # SecretStr  -> prints as '**********' in logs, tracebacks and repr()
    llm_api_key: SecretStr

    llm_model: str = "demo-model"
    llm_timeout_seconds: float = 30


@lru_cache
def get_settings() -> Settings:
    # Read env/.env once, then reuse the same object
    return Settings()
