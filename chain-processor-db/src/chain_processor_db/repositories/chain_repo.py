"""
Chain repository for the Chain Processing System.

This module defines the repository for chain-related operations.
"""

from typing import List, Optional, Tuple
import uuid

from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session, joinedload

from ..models.chain import ChainStrategy, StrategyNode
from ..models.node import Node
from .base import BaseRepository


class ChainRepository(BaseRepository[ChainStrategy]):
    """Repository for ChainStrategy entities."""

    def get_by_name(self, name: str) -> Optional[ChainStrategy]:
        """
        Get a chain strategy by name.

        Args:
            name: The chain strategy name

        Returns:
            The chain strategy if found, None otherwise
        """
        stmt = select(ChainStrategy).where(ChainStrategy.name == name)
        return self.db.scalar(stmt)

    def get_by_tag(self, tag: str, limit: int = 100, offset: int = 0) -> List[ChainStrategy]:
        """
        Get chain strategies by tag.

        Args:
            tag: The tag to filter by
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            List of chain strategies with the specified tag
        """
        stmt = select(ChainStrategy).where(
            ChainStrategy.tags.contains([tag])
        ).limit(limit).offset(offset)
        return list(self.db.scalars(stmt).all())

    def get_with_nodes(self, strategy_id: uuid.UUID) -> Optional[ChainStrategy]:
        """
        Get a chain strategy with its nodes preloaded.

        Args:
            strategy_id: The chain strategy ID

        Returns:
            The chain strategy with nodes if found, None otherwise
        """
        stmt = (
            select(ChainStrategy)
            .options(joinedload(ChainStrategy.strategy_nodes).joinedload(StrategyNode.node))
            .where(ChainStrategy.id == strategy_id)
        )
        return self.db.scalar(stmt)

    def get_active_strategies(self, limit: int = 100, offset: int = 0) -> List[ChainStrategy]:
        """
        Get active chain strategies.

        Args:
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            List of active chain strategies
        """
        stmt = select(ChainStrategy).where(
            ChainStrategy.is_active == True
        ).limit(limit).offset(offset)
        return list(self.db.scalars(stmt).all())

    def get_latest_version(self, name: str) -> Optional[ChainStrategy]:
        """
        Get the latest version of a chain strategy by name.

        Args:
            name: The chain strategy name

        Returns:
            The latest version of the chain strategy if found, None otherwise
        """
        stmt = (
            select(ChainStrategy)
            .where(ChainStrategy.name == name)
            .order_by(ChainStrategy.version.desc())
            .limit(1)
        )
        return self.db.scalar(stmt)

    def count_by_creator(self, creator_id: uuid.UUID) -> int:
        """
        Count the number of chain strategies created by a user.

        Args:
            creator_id: The ID of the creator

        Returns:
            The number of chain strategies created by the user
        """
        stmt = select(func.count()).select_from(
            ChainStrategy
        ).where(ChainStrategy.created_by_id == creator_id)
        return self.db.scalar(stmt) or 0

    def add_node_to_strategy(
        self, strategy_id: uuid.UUID, node_id: uuid.UUID, position: int, config: dict = None
    ) -> StrategyNode:
        """
        Add a node to a chain strategy.

        Args:
            strategy_id: The chain strategy ID
            node_id: The node ID
            position: The position of the node in the chain
            config: Optional node configuration

        Returns:
            The created strategy node link
        """
        strategy_node = StrategyNode(
            strategy_id=strategy_id,
            node_id=node_id,
            position=position,
            config=config or {},
        )
        self.db.add(strategy_node)
        self.db.commit()
        self.db.refresh(strategy_node)
        return strategy_node

    def remove_node_from_strategy(self, strategy_id: uuid.UUID, node_id: uuid.UUID) -> bool:
        """
        Remove a node from a chain strategy.

        Args:
            strategy_id: The chain strategy ID
            node_id: The node ID

        Returns:
            True if the node was removed, False otherwise
        """
        stmt = (
            select(StrategyNode)
            .where(
                and_(
                    StrategyNode.strategy_id == strategy_id,
                    StrategyNode.node_id == node_id,
                )
            )
        )
        strategy_node = self.db.scalar(stmt)
        if strategy_node:
            self.db.delete(strategy_node)
            self.db.commit()
            return True
        return False 