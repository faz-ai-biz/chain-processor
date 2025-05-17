from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


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
