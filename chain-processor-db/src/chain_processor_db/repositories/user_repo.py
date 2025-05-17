"""
User repository for the Chain Processing System.

This module defines the repository for user-related operations.
"""

from typing import List, Optional
import uuid

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ..models.user import User
from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User entities."""

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.

        Args:
            email: The user's email address

        Returns:
            The user if found, None otherwise
        """
        stmt = select(User).where(User.email == email)
        return self.db.scalar(stmt)

    def get_by_role(self, role: str, limit: int = 100, offset: int = 0) -> List[User]:
        """
        Get users by role.

        Args:
            role: The role to filter by
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            List of users with the specified role
        """
        stmt = select(User).where(
            User.roles.contains([role])
        ).limit(limit).offset(offset)
        return list(self.db.scalars(stmt).all())

    def count_active_users(self) -> int:
        """
        Count the number of active users.

        Returns:
            The number of active users
        """
        stmt = select(func.count()).select_from(User).where(User.is_active == True)
        return self.db.scalar(stmt) or 0 