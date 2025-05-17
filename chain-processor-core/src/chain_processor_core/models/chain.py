"""
Chain and Strategy models for the Chain Processing System.

This module defines the models for chains and strategies.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import Field, computed_field

from .base import VersionedModel
from .node import Node, NodeReference


class StrategyNodeLink(VersionedModel):
    """Link between a strategy and a node."""

    strategy_id: UUID
    node_id: UUID
    position: int = Field(ge=0)
    config: Dict[str, Any] = Field(default_factory=dict)


class ChainStrategy(VersionedModel):
    """Chain execution strategy."""

    name: str
    description: Optional[str] = None
    strategy_nodes: List[StrategyNodeLink] = Field(default_factory=list)
    is_active: bool = True
    created_by: Optional[UUID] = None
    tags: List[str] = Field(default_factory=list)

    @computed_field
    def node_count(self) -> int:
        """Get the number of nodes in the strategy."""
        return len(self.strategy_nodes)


class ChainStrategyCreate(VersionedModel):
    """Model for creating a new chain strategy."""

    name: str
    description: Optional[str] = None
    nodes: List[NodeReference]
    tags: List[str] = Field(default_factory=list)


class Chain(VersionedModel):
    """Chain model that combines a strategy with concrete nodes."""

    strategy: ChainStrategy
    nodes: List[Node] = Field(default_factory=list)
    
    @computed_field
    def node_count(self) -> int:
        """Get the number of nodes in the chain."""
        return len(self.nodes) 