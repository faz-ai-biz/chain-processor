"""API endpoints for managing nodes."""

from __future__ import annotations

from typing import List, Optional
import uuid
import math

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from chain_processor_db.session import get_db
from chain_processor_db.models.node import Node
from chain_processor_db.repositories.node_repo import NodeRepository
from chain_processor_core.lib_chains.registry import default_registry

from ..schemas import NodeRead, PaginatedResponse


router = APIRouter(prefix="/nodes", tags=["nodes"])


@router.get("/", response_model=PaginatedResponse[NodeRead])
def list_nodes(
    tag: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
) -> PaginatedResponse[NodeRead]:
    """
    List all nodes, optionally filtered by tag.
    
    Args:
        tag: Optional tag to filter by
        limit: Maximum number of results to return
        offset: Number of results to skip
        db: Database session
        
    Returns:
        Paginated list of nodes
    """
    repo = NodeRepository(db)
    
    # Get total count
    total = repo.count(tag=tag)
    
    # Calculate pagination values
    page = (offset // limit) + 1
    total_pages = math.ceil(total / limit) if total > 0 else 1
    
    # Get paginated results
    if tag:
        nodes = repo.get_by_tag(tag, limit=limit, offset=offset)
    else:
        nodes = repo.get_all(limit=limit, offset=offset)
    
    # Convert to response model
    items = [
        NodeRead(
            id=n.id,
            name=n.name,
            description=n.description,
            tags=n.tags,
            version=n.version,
        )
        for n in nodes
    ]
    
    # Create pagination response
    return PaginatedResponse[NodeRead](
        items=items,
        total=total,
        page=page,
        size=limit,
        pages=total_pages
    )


@router.get("/available", response_model=List[str])
def list_available_nodes(
    tag: Optional[str] = None,
) -> List[str]:
    """
    List all available node types from the registry, optionally filtered by tag.
    
    Args:
        tag: Optional tag to filter by
        
    Returns:
        List of node type names
    """
    registry = default_registry
    return registry.list_nodes(tag=tag)


@router.get("/tags", response_model=List[str])
def list_node_tags() -> List[str]:
    """
    List all available node tags from the registry.
    
    Returns:
        List of tag names
    """
    registry = default_registry
    return registry.list_tags()


@router.get("/{node_id}", response_model=NodeRead)
def get_node(
    node_id: uuid.UUID,
    db: Session = Depends(get_db)
) -> NodeRead:
    """
    Get a node by ID.
    
    Args:
        node_id: The node ID
        db: Database session
        
    Returns:
        The node
    """
    repo = NodeRepository(db)
    node = repo.get_by_id(node_id)
    
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node with ID {node_id} not found",
        )
    
    return NodeRead(
        id=node.id,
        name=node.name,
        description=node.description,
        tags=node.tags,
        version=node.version,
    ) 