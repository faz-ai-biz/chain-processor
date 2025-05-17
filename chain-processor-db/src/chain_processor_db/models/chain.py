"""
Chain models for the Chain Processing System.

This module defines the database models for chains and strategies.
"""

import uuid
from typing import Dict, List, Optional

from sqlalchemy import String, Text, ForeignKey, Boolean, Integer
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel, BaseVersionedModel


class ChainStrategy(BaseVersionedModel):
    """Chain strategy model for the Chain Processing System."""

    __tablename__ = "chain_strategies"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    metadata: Mapped[Dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Relationships
    created_by_user = relationship("User", back_populates="chain_strategies")
    strategy_nodes = relationship(
        "StrategyNode", 
        back_populates="strategy", 
        order_by="StrategyNode.position"
    )
    chain_executions = relationship("ChainExecution", back_populates="strategy")

    def __repr__(self) -> str:
        """Return string representation of the ChainStrategy model."""
        return f"<ChainStrategy {self.name} v{self.version}>"


class StrategyNode(BaseModel):
    """Link model between strategies and nodes."""

    __tablename__ = "strategy_nodes"

    strategy_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("chain_strategies.id"), nullable=False
    )
    node_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("nodes.id"), nullable=False
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    config: Mapped[Dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Relationships
    strategy = relationship("ChainStrategy", back_populates="strategy_nodes")
    node = relationship("Node", back_populates="strategy_nodes")

    def __repr__(self) -> str:
        """Return string representation of the StrategyNode model."""
        return f"<StrategyNode {self.strategy_id}:{self.node_id} pos:{self.position}>" 