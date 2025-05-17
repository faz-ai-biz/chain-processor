"""
Node repository for the Chain Processing System.

This module defines the repository for node-related operations.
"""

from typing import List, Optional
import uuid

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ..models.node import Node
from .base import BaseRepository


class NodeRepository(BaseRepository[Node]):
    """Repository for Node entities."""

    def get_by_name(self, name: str) -> Optional[Node]:
        """
        Get a node by name.

        Args:
            name: The node name

        Returns:
            The node if found, None otherwise
        """
        stmt = select(Node).where(Node.name == name)
        return self.db.scalar(stmt)

    def get_by_tag(self, tag: str, limit: int = 100, offset: int = 0) -> List[Node]:
        """
        Get nodes by tag.

        Args:
            tag: The tag to filter by
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            List of nodes with the specified tag
        """
        stmt = select(Node).where(
            Node.tags.contains([tag])
        ).limit(limit).offset(offset)
        return list(self.db.scalars(stmt).all())

    def get_active_nodes(self, limit: int = 100, offset: int = 0) -> List[Node]:
        """
        Get active nodes.

        Args:
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            List of active nodes
        """
        stmt = select(Node).where(Node.is_active == True).limit(limit).offset(offset)
        return list(self.db.scalars(stmt).all())

    def get_latest_version(self, name: str) -> Optional[Node]:
        """
        Get the latest version of a node by name.

        Args:
            name: The node name

        Returns:
            The latest version of the node if found, None otherwise
        """
        stmt = (
            select(Node)
            .where(Node.name == name)
            .order_by(Node.version.desc())
            .limit(1)
        )
        return self.db.scalar(stmt)

    def count_by_creator(self, creator_id: uuid.UUID) -> int:
        """
        Count the number of nodes created by a user.

        Args:
            creator_id: The ID of the creator

        Returns:
            The number of nodes created by the user
        """
        stmt = select(func.count()).select_from(Node).where(Node.created_by_id == creator_id)
        return self.db.scalar(stmt) or 0 