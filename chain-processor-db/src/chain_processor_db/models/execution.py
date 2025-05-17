"""
Execution models for the Chain Processing System.

This module defines the database models for tracking executions of chains and nodes.
"""

from datetime import datetime
import uuid
from typing import Dict, Optional, List, Literal

from sqlalchemy import String, Text, ForeignKey, Integer, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel, BaseVersionedModel


class ExecutionStatus(str, Enum):
    """Execution status enum."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ChainExecution(BaseVersionedModel):
    """Chain execution record model."""

    __tablename__ = "chain_executions"

    strategy_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("chain_strategies.id"), nullable=False
    )
    input_text: Mapped[str] = mapped_column(Text, nullable=False)
    output_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    metadata: Mapped[Dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Relationships
    strategy = relationship("ChainStrategy", back_populates="chain_executions")
    created_by_user = relationship("User", back_populates="chain_executions")
    node_executions = relationship(
        "NodeExecution", 
        back_populates="chain_execution", 
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Return string representation of the ChainExecution model."""
        return f"<ChainExecution {self.id} status:{self.status}>"


class NodeExecution(BaseModel):
    """Node execution record model."""

    __tablename__ = "node_executions"

    execution_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("chain_executions.id"), nullable=False
    )
    node_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("nodes.id"), nullable=False
    )
    input_text: Mapped[str] = mapped_column(Text, nullable=False)
    output_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    metadata: Mapped[Dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Relationships
    chain_execution = relationship("ChainExecution", back_populates="node_executions")
    node = relationship("Node", back_populates="node_executions")

    def __repr__(self) -> str:
        """Return string representation of the NodeExecution model."""
        return f"<NodeExecution {self.id} node:{self.node_id} status:{self.status}>" 