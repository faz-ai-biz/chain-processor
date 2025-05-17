"""
Base model implementations for the Chain Processing System.

This module defines the base model class for all database models.
"""

import uuid
from sqlalchemy import Column, Integer, DateTime, func, String, UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TimestampMixin, VersionedMixin


class BaseModel(Base, TimestampMixin):
    """Base model with ID and timestamps."""

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Return the table name for the model."""
        return cls.__name__.lower()


class BaseVersionedModel(BaseModel, VersionedMixin):
    """Base model with versioning support."""

    __abstract__ = True 