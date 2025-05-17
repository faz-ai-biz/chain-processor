"""
Execution models for the Chain Processing System.

This module defines the models for tracking executions of chains and nodes.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Literal
from uuid import UUID

from pydantic import Field, field_validator, model_validator

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
        """Validate that completed_at is set if status is terminal."""
        if self.status in ["success", "failed", "cancelled"] and self.completed_at is None:
            object.__setattr__(self, 'completed_at', datetime.utcnow())
        return self

    @field_validator("execution_time_ms", mode="before")
    @classmethod
    def calculate_execution_time(cls, v: Optional[int], info: Dict[str, Any]) -> Optional[int]:
        """Calculate execution time from started_at and completed_at if not provided."""
        if v is not None:
            return v
            
        data = info.data
        started = data.get("started_at")
        completed = data.get("completed_at")
        
        if started and completed:
            delta = completed - started
            return int(delta.total_seconds() * 1000)
            
        return None 