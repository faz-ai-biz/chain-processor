"""
Base SQLAlchemy classes and metadata for the Chain Processing System.

This module defines the base SQLAlchemy model class and metadata
used across all database models in the Chain Processing System.
"""

from datetime import datetime
import uuid
from typing import Any, ClassVar, Dict, Optional

from sqlalchemy import MetaData, UUID, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)

# Conventions for constraint naming
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# Create metadata with naming conventions
chain_db_metadata = MetaData(naming_convention=convention)

# Export metadata for backwards compatibility with Alembic environment
metadata = chain_db_metadata


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    metadata = chain_db_metadata # Explicitly associate metadata
    type_annotation_map: ClassVar[Dict[Any, Any]] = {
        uuid.UUID: UUID(as_uuid=True),
    }


class TimestampMixin:
    """Mixin to add created_at and updated_at columns to models."""

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=func.now(),
        nullable=False,
    )


class VersionedMixin:
    """Mixin to add version control to models."""

    version: Mapped[int] = mapped_column(default=1, nullable=False) 