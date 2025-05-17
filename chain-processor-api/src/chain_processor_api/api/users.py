from __future__ import annotations

import hashlib
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from chain_processor_db.session import get_db
from chain_processor_db.models.user import User
from chain_processor_db.repositories.user_repo import UserRepository

from ..schemas import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    repo = UserRepository(db)
    if repo.get_by_email(user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    password_hash = hashlib.sha256(user_in.password.encode()).hexdigest()
    user = User(
        email=user_in.email,
        password_hash=password_hash,
        full_name=user_in.full_name or "",
        is_active=True,
        is_superuser=False,
        roles=user_in.roles,
    )
    repo.create(user)
    return UserRead(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        roles=user.roles,
        is_active=user.is_active,
        version=user.version,
    )


@router.get("/", response_model=List[UserRead])
def list_users(db: Session = Depends(get_db)) -> List[UserRead]:
    repo = UserRepository(db)
    users = repo.get_all()
    return [
        UserRead(
            id=u.id,
            email=u.email,
            full_name=u.full_name,
            roles=u.roles,
            is_active=u.is_active,
            version=u.version,
        )
        for u in users
    ]
