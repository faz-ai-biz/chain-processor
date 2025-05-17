from __future__ import annotations

from typing import List, Optional, Dict, Any, Generic, TypeVar
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

T = TypeVar('T')


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    roles: List[str] = []


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    full_name: Optional[str] = None
    roles: List[str] = []
    is_active: bool
    version: int


class ChainCreate(BaseModel):
    name: str
    description: Optional[str] = None
    tags: List[str] = []


class ChainRead(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    tags: List[str] = []
    version: int


class NodeReference(BaseModel):
    id: str
    position: int
    config: Dict[str, Any] = {}


class NodeRead(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    tags: List[str] = []
    version: int


class AddNodeToChainRequest(BaseModel):
    node_id: UUID
    position: int = Field(ge=0)
    config: Dict[str, Any] = Field(default_factory=dict)


class ChainExecuteRequest(BaseModel):
    input_text: str
    
    @field_validator('input_text')
    @classmethod
    def validate_input_text(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Input text cannot be empty")
        if len(v) > 10000:  # Limit to 10,000 characters
            raise ValueError("Input text too long (max 10,000 characters)")
        return v


class NodeExecutionResult(BaseModel):
    node_id: str
    input_text: str
    output_text: Optional[str] = None
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None
    success: bool


class ChainExecuteResponse(BaseModel):
    id: UUID
    chain_id: UUID
    input_text: str
    output_text: Optional[str] = None
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    node_results: List[NodeExecutionResult] = []


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic pagination response."""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    
    @property
    def has_next(self) -> bool:
        return self.page < self.pages
    
    @property
    def has_prev(self) -> bool:
        return self.page > 1
