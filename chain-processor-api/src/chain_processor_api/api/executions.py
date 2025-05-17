"""API endpoints for managing chain executions."""

from __future__ import annotations

from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from chain_processor_db.session import get_db
from chain_processor_db.repositories.execution_repo import ExecutionRepository

from ..schemas import ChainExecuteResponse, NodeExecutionResult


router = APIRouter(prefix="/executions", tags=["executions"])


@router.get("/", response_model=List[ChainExecuteResponse])
def list_executions(
    strategy_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
) -> List[ChainExecuteResponse]:
    """
    List chain executions, optionally filtered by strategy ID or status.
    
    Args:
        strategy_id: Optional strategy ID to filter by
        status: Optional status to filter by
        limit: Maximum number of results to return
        offset: Number of results to skip
        db: Database session
        
    Returns:
        List of chain executions
    """
    repo = ExecutionRepository(db)
    
    if strategy_id:
        executions = repo.get_by_strategy(strategy_id, limit=limit, offset=offset)
    elif status:
        executions = repo.get_by_status(status, limit=limit, offset=offset)
    else:
        executions = repo.get_all(limit=limit, offset=offset)
    
    return [
        ChainExecuteResponse(
            id=e.id,
            chain_id=e.strategy_id,
            input_text=e.input_text,
            output_text=e.output_text,
            error=e.error,
            execution_time_ms=e.execution_time_ms,
            status=e.status,
            started_at=e.started_at,
            completed_at=e.completed_at,
            node_results=[]  # We don't load node results in the list view
        )
        for e in executions
    ]


@router.get("/{execution_id}", response_model=ChainExecuteResponse)
def get_execution(
    execution_id: uuid.UUID,
    db: Session = Depends(get_db)
) -> ChainExecuteResponse:
    """
    Get a chain execution by ID.
    
    Args:
        execution_id: The execution ID
        db: Database session
        
    Returns:
        The chain execution
    """
    repo = ExecutionRepository(db)
    execution = repo.get_with_nodes(execution_id)
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution with ID {execution_id} not found",
        )
    
    # Convert node executions to NodeExecutionResult objects
    node_results = []
    for ne in execution.node_executions:
        node_results.append(
            NodeExecutionResult(
                node_id=str(ne.node_id),
                input_text=ne.input_text,
                output_text=ne.output_text,
                error=ne.error,
                execution_time_ms=ne.execution_time_ms,
                success=ne.status == "success"
            )
        )
    
    return ChainExecuteResponse(
        id=execution.id,
        chain_id=execution.strategy_id,
        input_text=execution.input_text,
        output_text=execution.output_text,
        error=execution.error,
        execution_time_ms=execution.execution_time_ms,
        status=execution.status,
        started_at=execution.started_at,
        completed_at=execution.completed_at,
        node_results=node_results
    ) 