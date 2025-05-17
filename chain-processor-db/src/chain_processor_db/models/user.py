"""
User models for the Chain Processing System.

This module defines the database models for users and related entities.
"""

from datetime import datetime
import uuid
from typing import Dict, List, Optional

from sqlalchemy import String, Boolean, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel, BaseVersionedModel


class User(BaseVersionedModel):
    """User model for the Chain Processing System."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    roles: Mapped[List[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    preferences: Mapped[Dict] = mapped_column(JSONB, default=dict, nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Relationships
    chain_executions = relationship("ChainExecution", back_populates="created_by_user")
    chain_strategies = relationship("ChainStrategy", back_populates="created_by_user")
    nodes = relationship("Node", back_populates="created_by_user")

    def __repr__(self) -> str:
        """Return string representation of the User model."""
        return f"<User {self.email}>" 