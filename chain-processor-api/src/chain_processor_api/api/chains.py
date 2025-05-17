from __future__ import annotations

from typing import List, Dict
from datetime import datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from chain_processor_db.session import get_db
from chain_processor_db.models.chain import ChainStrategy, StrategyNode
from chain_processor_db.models.execution import ChainExecution, NodeExecution, ExecutionStatus
from chain_processor_db.repositories.chain_repo import ChainRepository
from chain_processor_db.repositories.node_repo import NodeRepository
from chain_processor_db.repositories.execution_repo import ExecutionRepository

from chain_processor_core.executor.chain_executor import ChainExecutor
from chain_processor_core.exceptions.errors import ChainProcessorError

from ..schemas import (
    ChainCreate, 
    ChainRead, 
    ChainExecuteRequest, 
    ChainExecuteResponse,
    NodeExecutionResult,
    AddNodeToChainRequest
)

router = APIRouter(prefix="/chains", tags=["chains"])


@router.post("/", response_model=ChainRead)
def create_chain(chain_in: ChainCreate, db: Session = Depends(get_db)) -> ChainRead:
    repo = ChainRepository(db)
    chain = ChainStrategy(
        name=chain_in.name,
        description=chain_in.description,
        is_active=True,
        tags=chain_in.tags,
    )
    repo.create(chain)
    return ChainRead(
        id=chain.id,
        name=chain.name,
        description=chain.description,
        tags=chain.tags,
        version=chain.version,
    )


@router.get("/", response_model=List[ChainRead])
def list_chains(db: Session = Depends(get_db)) -> List[ChainRead]:
    repo = ChainRepository(db)
    chains = repo.get_all()
    return [
        ChainRead(
            id=c.id,
            name=c.name,
            description=c.description,
            tags=c.tags,
            version=c.version,
        )
        for c in chains
    ]


@router.post("/{chain_id}/nodes", status_code=status.HTTP_201_CREATED)
def add_node_to_chain(
    chain_id: uuid.UUID,
    node_request: AddNodeToChainRequest,
    db: Session = Depends(get_db)
) -> dict:
    """
    Add a node to a chain strategy.
    
    Args:
        chain_id: The ID of the chain to add the node to
        node_request: The node to add
        db: Database session
        
    Returns:
        A message indicating success
    """
    chain_repo = ChainRepository(db)
    node_repo = NodeRepository(db)
    
    # Check if chain exists
    chain = chain_repo.get_by_id(chain_id)
    if not chain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chain with ID {chain_id} not found",
        )
    
    # Check if node exists
    node = node_repo.get_by_id(node_request.node_id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node with ID {node_request.node_id} not found",
        )
    
    # Add node to chain
    try:
        chain_repo.add_node_to_strategy(
            strategy_id=chain_id,
            node_id=node_request.node_id,
            position=node_request.position,
            config=node_request.config,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add node to chain: {str(e)}",
        )
    
    return {
        "message": f"Node {node_request.node_id} added to chain {chain_id} at position {node_request.position}"
    }


@router.post("/{chain_id}/execute", response_model=ChainExecuteResponse)
def execute_chain(
    chain_id: uuid.UUID, 
    request: ChainExecuteRequest, 
    db: Session = Depends(get_db)
) -> ChainExecuteResponse:
    # Get the chain strategy
    chain_repo = ChainRepository(db)
    execution_repo = ExecutionRepository(db)
    node_repo = NodeRepository(db)
    
    # Use database locking to prevent race conditions
    chain = db.query(ChainStrategy).with_for_update().filter(
        ChainStrategy.id == chain_id
    ).first()
    
    if not chain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chain with ID {chain_id} not found",
        )
    
    if not chain.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Chain with ID {chain_id} is not active",
        )
    
    # Begin transaction
    with db.begin_nested():
        # Create a chain execution record
        chain_execution = ChainExecution(
            strategy_id=chain_id,
            input_text=request.input_text,
            status=ExecutionStatus.IN_PROGRESS,
        )
        execution_repo.create(chain_execution)
    
    try:
        # Get the node configurations
        strategy_nodes = db.query(StrategyNode).filter(
            StrategyNode.strategy_id == chain_id
        ).order_by(StrategyNode.position).all()
        
        if not strategy_nodes:
            with db.begin_nested():
                chain_execution.status = ExecutionStatus.FAILED
                chain_execution.error = f"Chain with ID {chain_id} has no nodes"
                chain_execution.completed_at = datetime.utcnow()
                db.commit()
                
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Chain with ID {chain_id} has no nodes",
            )
        
        # Prepare node configurations for executor and create a mapping of node names to IDs
        node_configs = []
        node_name_to_id_map: Dict[str, uuid.UUID] = {}
        ordered_nodes = []  # Store nodes in order
        
        for sn in strategy_nodes:
            node = node_repo.get_by_id(sn.node_id)
            if not node:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Node with ID {sn.node_id} not found",
                )
            # Use the node name as the identifier for the registry
            node_configs.append((node.name, sn.config))
            # Store mapping of node name to database UUID
            node_name_to_id_map[node.name] = node.id
            # Store the node in order
            ordered_nodes.append(node)
        
        # Execute the chain
        executor = ChainExecutor()
        result = executor.execute_chain(
            chain_id=str(chain_id),
            input_data=request.input_text,
            node_configs=node_configs
        )
        
        # Update the chain execution record
        with db.begin_nested():
            chain_execution.status = ExecutionStatus.SUCCESS if result.success else ExecutionStatus.FAILED
            chain_execution.output_text = result.output_data
            chain_execution.error = result.error
            chain_execution.execution_time_ms = result.execution_time_ms
            chain_execution.completed_at = datetime.utcnow()
            db.flush()
            
            # Create node execution records
            # Don't rely on the node_id from the results, use the ordered nodes instead
            node_executions = []
            
            # Assuming the order of nodes in the strategy matches the order of results
            if len(result.node_results) == len(ordered_nodes):
                for i, node_result in enumerate(result.node_results):
                    # NodeExecutionResult now includes both node_id (UUID) and node_name (str)
                    # We can use the node_id directly as it's already a UUID
                    node_exec = NodeExecution(
                        execution_id=chain_execution.id,
                        node_id=node_result.node_id,  # Use UUID directly
                        input_text=node_result.input_text,
                        output_text=node_result.output_data,
                        error=node_result.error,
                        status=ExecutionStatus.SUCCESS if node_result.success else ExecutionStatus.FAILED,
                        execution_time_ms=node_result.execution_time_ms,
                        completed_at=datetime.utcnow() if node_result.output_data or node_result.error else None
                    )
                    node_executions.append(node_exec)
            else:
                # If lengths don't match, log the issue and fail explicitly
                error_msg = f"Node result count mismatch: {len(result.node_results)} vs {len(ordered_nodes)}"
                print(f"Error: {error_msg}")
                
                # Update chain execution
                chain_execution.status = ExecutionStatus.FAILED
                chain_execution.error = error_msg
                chain_execution.completed_at = datetime.utcnow()
                db.commit()
                
                # Return error response
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Internal processing error: {error_msg}"
                )
            
            # Add all node executions in a single operation
            if node_executions:
                db.add_all(node_executions)
                db.commit()
        
        # Create the response
        node_results = [
            NodeExecutionResult(
                node_id=nr.node_id,
                node_name=nr.node_name,
                input_text=nr.input_text,
                output_text=nr.output_data,
                error=nr.error,
                execution_time_ms=nr.execution_time_ms,
                success=nr.success
            )
            for nr in result.node_results
        ]
        
        return ChainExecuteResponse(
            id=chain_execution.id,
            chain_id=chain_id,
            input_text=request.input_text,
            output_text=result.output_data,
            error=result.error,
            execution_time_ms=result.execution_time_ms,
            status=chain_execution.status,
            started_at=chain_execution.started_at,
            completed_at=chain_execution.completed_at,
            node_results=node_results
        )
        
    except ChainProcessorError as e:
        # Update the chain execution record with the error
        chain_execution.status = ExecutionStatus.FAILED
        chain_execution.error = str(e)
        chain_execution.completed_at = datetime.utcnow()
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        # Update the chain execution record with the error
        chain_execution.status = ExecutionStatus.FAILED
        chain_execution.error = f"Unexpected error: {str(e)}"
        chain_execution.completed_at = datetime.utcnow()
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )
