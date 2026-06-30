from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration, loaded from environment / .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Core ---
    PROJECT_NAME: str = "EvalForge"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # --- Database ---
    # Defaults to local SQLite so the app runs with zero setup.
    # Set DATABASE_URL to a Postgres URL in production.
    DATABASE_URL: str = "sqlite:///./evalforge.db"

    # --- Auth ---
    SECRET_KEY: str = "change-me-in-production-please"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # --- CORS ---
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # --- Background jobs ---
    # When REDIS_URL is unset, Celery runs eagerly (synchronously) in-process,
    # so the app works without a running broker.
    REDIS_URL: str = ""

    # --- LLM provider API keys (optional; mock provider used if absent) ---
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    @property
    def celery_eager(self) -> bool:
        return not bool(self.REDIS_URL)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
