"""Application configuration using Pydantic settings."""

from pydantic import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    DATABASE_URL: str = (
        "postgresql://postgres:postgres@localhost:5432/chain_processor"
    )
    CORS_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
