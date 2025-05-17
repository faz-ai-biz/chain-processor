"""
Execution repository for the Chain Processing System.

This module defines the repository for execution-related operations.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Tuple
import uuid

from sqlalchemy import select, func, desc, and_, between
from sqlalchemy.orm import Session, joinedload

from ..models.execution import ChainExecution, NodeExecution
from .base import BaseRepository


class ExecutionRepository(BaseRepository[ChainExecution]):
    """Repository for ChainExecution entities."""

    def get_with_nodes(self, execution_id: uuid.UUID) -> Optional[ChainExecution]:
        """
        Get a chain execution with its node executions preloaded.

        Args:
            execution_id: The chain execution ID

        Returns:
            The chain execution with node executions if found, None otherwise
        """
        stmt = (
            select(ChainExecution)
            .options(joinedload(ChainExecution.node_executions))
            .where(ChainExecution.id == execution_id)
        )
        return self.db.scalar(stmt)

    def get_by_status(
        self, status: str, limit: int = 100, offset: int = 0
    ) -> List[ChainExecution]:
        """
        Get chain executions by status.

        Args:
            status: The execution status
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            List of chain executions with the specified status
        """
        stmt = (
            select(ChainExecution)
            .where(ChainExecution.status == status)
            .order_by(desc(ChainExecution.created_at))
            .limit(limit)
            .offset(offset)
        )
        return list(self.db.scalars(stmt).all())

    def get_by_strategy(
        self, strategy_id: uuid.UUID, limit: int = 100, offset: int = 0
    ) -> List[ChainExecution]:
        """
        Get chain executions by strategy.

        Args:
            strategy_id: The strategy ID
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            List of chain executions for the specified strategy
        """
        stmt = (
            select(ChainExecution)
            .where(ChainExecution.strategy_id == strategy_id)
            .order_by(desc(ChainExecution.created_at))
            .limit(limit)
            .offset(offset)
        )
        return list(self.db.scalars(stmt).all())

    def get_by_creator(
        self, creator_id: uuid.UUID, limit: int = 100, offset: int = 0
    ) -> List[ChainExecution]:
        """
        Get chain executions by creator.

        Args:
            creator_id: The creator ID
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            List of chain executions created by the specified user
        """
        stmt = (
            select(ChainExecution)
            .where(ChainExecution.created_by_id == creator_id)
            .order_by(desc(ChainExecution.created_at))
            .limit(limit)
            .offset(offset)
        )
        return list(self.db.scalars(stmt).all())

    def get_recent_executions(
        self, days: int = 7, limit: int = 100, offset: int = 0
    ) -> List[ChainExecution]:
        """
        Get recent chain executions.

        Args:
            days: Number of days to look back
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            List of recent chain executions
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        stmt = (
            select(ChainExecution)
            .where(ChainExecution.created_at >= start_date)
            .order_by(desc(ChainExecution.created_at))
            .limit(limit)
            .offset(offset)
        )
        return list(self.db.scalars(stmt).all())

    def get_execution_stats(self, strategy_id: Optional[uuid.UUID] = None) -> dict:
        """
        Get execution statistics.

        Args:
            strategy_id: Optional strategy ID to filter by

        Returns:
            Dictionary with execution statistics
        """
        where_clause = ChainExecution.strategy_id == strategy_id if strategy_id else True
        
        # Total count
        total_stmt = select(func.count()).select_from(ChainExecution).where(where_clause)
        total_count = self.db.scalar(total_stmt) or 0
        
        # Status counts
        status_counts = {}
        for status in ["pending", "in_progress", "success", "failed", "cancelled"]:
            status_stmt = (
                select(func.count())
                .select_from(ChainExecution)
                .where(and_(where_clause, ChainExecution.status == status))
            )
            status_counts[status] = self.db.scalar(status_stmt) or 0
        
        # Average execution time for successful executions
        avg_time_stmt = (
            select(func.avg(ChainExecution.execution_time_ms))
            .select_from(ChainExecution)
            .where(
                and_(
                    where_clause,
                    ChainExecution.status == "success",
                    ChainExecution.execution_time_ms.is_not(None),
                )
            )
        )
        avg_execution_time = self.db.scalar(avg_time_stmt)
        
        return {
            "total_count": total_count,
            "status_counts": status_counts,
            "avg_execution_time_ms": avg_execution_time,
        }

    def create_node_execution(
        self, 
        execution_id: uuid.UUID, 
        node_id: uuid.UUID, 
        input_text: str, 
        status: str = "pending"
    ) -> NodeExecution:
        """
        Create a new node execution.

        Args:
            execution_id: The chain execution ID
            node_id: The node ID
            input_text: The input text
            status: The initial status

        Returns:
            The created node execution
        """
        node_execution = NodeExecution(
            execution_id=execution_id,
            node_id=node_id,
            input_text=input_text,
            status=status,
        )
        self.db.add(node_execution)
        self.db.commit()
        self.db.refresh(node_execution)
        return node_execution

    def update_node_execution(
        self, 
        node_execution_id: uuid.UUID, 
        output_text: Optional[str] = None, 
        status: Optional[str] = None,
        error: Optional[str] = None,
        execution_time_ms: Optional[int] = None,
    ) -> Optional[NodeExecution]:
        """
        Update a node execution.

        Args:
            node_execution_id: The node execution ID
            output_text: Optional output text
            status: Optional status
            error: Optional error message
            execution_time_ms: Optional execution time in milliseconds

        Returns:
            The updated node execution if found, None otherwise
        """
        data = {}
        if output_text is not None:
            data["output_text"] = output_text
        if status is not None:
            data["status"] = status
        if error is not None:
            data["error"] = error
        if execution_time_ms is not None:
            data["execution_time_ms"] = execution_time_ms
        
        if status in ["success", "failed", "cancelled"]:
            data["completed_at"] = datetime.utcnow()
            
        if not data:
            # No updates to make
            node_execution = self.db.get(NodeExecution, node_execution_id)
            return node_execution
            
        result = self.db.execute(
            update(NodeExecution)
            .where(NodeExecution.id == node_execution_id)
            .values(**data)
            .returning(NodeExecution)
        )
        self.db.commit()
        return result.scalar_one_or_none()
