"""
Base models for the Chain Processing System.

This module defines base models and common fields used across the system.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict, field_validator


class BaseModelWithId(BaseModel):
    """Base model with ID field."""

    model_config = ConfigDict(populate_by_name=True)

    id: UUID = Field(default_factory=uuid4)


class TimestampedModel(BaseModelWithId):
    """Base model with timestamp fields."""

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("updated_at", mode="before")
    @classmethod
    def update_timestamp(cls, v: Optional[datetime], info: Dict[str, Any]) -> datetime:
        """Update the timestamp if not provided."""
        if v is None:
            return datetime.utcnow()
        return v


class VersionedModel(TimestampedModel):
    """Base model with versioning support."""

    version: int = Field(default=1, ge=1)
    
    @field_validator("version", mode="before")
    @classmethod
    def ensure_positive_version(cls, v: int) -> int:
        """Ensure the version is positive."""
        if v < 1:
            raise ValueError("Version must be a positive integer")
        return v 