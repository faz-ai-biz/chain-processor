"""
User and authentication models for the Chain Processing System.

This module defines the models for users and authentication.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Literal
from uuid import UUID

from pydantic import Field, field_validator, EmailStr

from .base import VersionedModel


class Role(str):
    """User role enum."""
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class User(VersionedModel):
    """User model."""

    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    roles: List[Literal["admin", "editor", "viewer"]] = Field(default_factory=lambda: ["viewer"])
    last_login: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format."""
        if not v or not v.strip():
            raise ValueError("Username cannot be empty")
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        if not v.isalnum() and not all(c.isalnum() or c in "-_" for c in v):
            raise ValueError("Username can only contain alphanumeric characters, hyphens, and underscores")
        return v


class UserCreate(VersionedModel):
    """Model for creating a new user."""

    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    roles: List[Literal["admin", "editor", "viewer"]] = Field(default_factory=lambda: ["viewer"])

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(VersionedModel):
    """Model for updating a user."""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    roles: Optional[List[Literal["admin", "editor", "viewer"]]] = None


class Token(VersionedModel):
    """Authentication token."""

    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    refresh_token: Optional[str] = None 