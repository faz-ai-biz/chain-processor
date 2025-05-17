"""
Node models for the Chain Processing System.

This module defines the models for processing nodes.
"""

from typing import List, Optional, Dict, Any, Literal
from uuid import UUID

from pydantic import Field, field_validator

from .base import VersionedModel


class NodeReference(VersionedModel):
    """Reference to a node with position information."""

    node_id: UUID
    position: int = Field(ge=0)
    config: Dict[str, Any] = Field(default_factory=dict)


class NodeParameter(VersionedModel):
    """Parameter definition for a node."""

    name: str
    description: Optional[str] = None
    type: Literal["string", "integer", "float", "boolean", "array", "object"] = "string"
    required: bool = False
    default: Optional[Any] = None


class Node(VersionedModel):
    """Processing node model."""

    name: str
    description: Optional[str] = None
    code: str
    parameters: List[NodeParameter] = Field(default_factory=list)
    created_by: Optional[UUID] = None
    tags: List[str] = Field(default_factory=list)

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Validate that the code is not empty."""
        if not v or not v.strip():
            raise ValueError("Node code cannot be empty")
        return v


class NodeCreate(VersionedModel):
    """Model for creating a new node."""

    name: str
    description: Optional[str] = None
    code: str
    parameters: List[NodeParameter] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class NodeUpdate(VersionedModel):
    """Model for updating a node."""

    name: Optional[str] = None
    description: Optional[str] = None
    code: Optional[str] = None
    parameters: Optional[List[NodeParameter]] = None
    tags: Optional[List[str]] = None 