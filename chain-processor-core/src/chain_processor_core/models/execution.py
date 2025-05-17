"""
Execution models for the Chain Processing System.

This module defines the models for tracking executions of chains and nodes.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Literal
from uuid import UUID

from pydantic import Field, model_validator

from .base import VersionedModel


class ExecutionStatus(str):
    """Execution status enum."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NodeExecution(VersionedModel):
    """Node execution record."""

    execution_id: UUID
    node_id: UUID
    input_text: str
    output_text: Optional[str] = None
    error: Optional[str] = None
    status: Literal["pending", "in_progress", "success", "failed", "cancelled"] = "pending"
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    execution_time_ms: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode='after')
    def validate_completion(self) -> 'NodeExecution':
        """Validate that completed_at is set if status is terminal."""
        if self.status in ["success", "failed", "cancelled"] and self.completed_at is None:
            object.__setattr__(self, 'completed_at', datetime.utcnow())
        return self


class ChainExecution(VersionedModel):
    """Chain execution record."""

    strategy_id: UUID
    input_text: str
    output_text: Optional[str] = None
    error: Optional[str] = None
    status: Literal["pending", "in_progress", "success", "failed", "cancelled"] = "pending"
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    execution_time_ms: Optional[int] = None
    created_by: Optional[UUID] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    node_executions: List[NodeExecution] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_completion(self) -> 'ChainExecution':
        """Validate that completed_at and execution_time are populated."""
        if self.status in ["success", "failed", "cancelled"]:
            if self.completed_at is None:
                object.__setattr__(self, "completed_at", datetime.utcnow())

            if self.execution_time_ms is None and self.started_at and self.completed_at:
                delta = self.completed_at - self.started_at
                object.__setattr__(
                    self, "execution_time_ms", int(delta.total_seconds() * 1000)
                )

        return self
