"""Application configuration using Pydantic and python-dotenv."""

import os
from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables from .env file if it exists
load_dotenv()


class Settings(BaseModel):
    """Application settings loaded from environment variables."""

    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/chain_processor",
        description="Database connection URL"
    )
    CORS_ORIGINS: List[str] = Field(
        default=["*"],
        description="List of allowed CORS origins"
    )


# Initialize settings from environment variables
settings = Settings(
    DATABASE_URL=os.getenv("DATABASE_URL", Settings().DATABASE_URL),
    CORS_ORIGINS=os.getenv("CORS_ORIGINS", ",").split(",") if os.getenv("CORS_ORIGINS") else Settings().CORS_ORIGINS,
)
