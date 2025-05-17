"""
Node models for the Chain Processing System.

This module defines the database models for processing nodes.
"""

import uuid
from typing import Dict, List, Optional

from sqlalchemy import String, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel, BaseVersionedModel


class Node(BaseVersionedModel):
    """Node model for the Chain Processing System."""

    __tablename__ = "nodes"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    code: Mapped[str] = mapped_column(Text, nullable=False)
    created_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    is_builtin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    metadata_json: Mapped[Dict] = mapped_column(
        "metadata", JSONB, default=dict, nullable=False
    )
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), default=list, nullable=False)

    # Relationships
    created_by_user = relationship("User", back_populates="nodes")
    strategy_nodes = relationship("StrategyNode", back_populates="node")
    node_executions = relationship("NodeExecution", back_populates="node")

    def __repr__(self) -> str:
        """Return string representation of the Node model."""
        return f"<Node {self.name} v{self.version}>" 