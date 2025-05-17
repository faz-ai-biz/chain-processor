"""
Database session management for the Chain Processing System.

This module provides utilities for creating database sessions
and configuring the database connection.
"""

import os
from typing import AsyncGenerator, Generator, Optional

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .base import db_metadata as metadata
from chain_processor_api.core.config import settings


def get_connection_url() -> str:
    """Get the database connection URL from environment variables."""
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise ValueError(
            "DATABASE_URL environment variable is not set. "
            "Please set it to a valid PostgreSQL connection string."
        )
    return db_url


def create_database_engine(
    connection_url: Optional[str] = None, pool_size: Optional[int] = None, max_overflow: Optional[int] = None
) -> Engine:
    """
    Create a SQLAlchemy database engine.

    Args:
        connection_url: The database connection URL. If not provided, it will be read from the environment.
        pool_size: The number of connections to keep in the pool. If not provided, it will be read from the environment.
        max_overflow: The maximum number of connections to create above the pool_size. If not provided, it will be read from the environment.

    Returns:
        SQLAlchemy Engine
    """
    conn_url = connection_url or get_connection_url()
    
    # Get pool size and max overflow from environment variables if not provided
    if pool_size is None:
        pool_size_str = os.environ.get("DATABASE_POOL_SIZE", "10")
        pool_size = int(pool_size_str)
    
    if max_overflow is None:
        max_overflow_str = os.environ.get("DATABASE_MAX_OVERFLOW", "20")
        max_overflow = int(max_overflow_str)
    
    # Create engine with connection pooling
    engine = create_engine(
        conn_url,
        poolclass=QueuePool,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_recycle=300,  # Recycle connections after 5 minutes
        pool_pre_ping=True,  # Check connection validity before using
    )
    
    return engine


# Create a global engine for the application
_engine: Optional[Engine] = None


def get_engine() -> Engine:
    """Get the database engine, creating it if it doesn't exist."""
    global _engine
    if _engine is None:
        _engine = create_database_engine()
    return _engine


def create_session_factory(engine: Optional[Engine] = None) -> sessionmaker:
    """
    Create a SQLAlchemy sessionmaker.

    Args:
        engine: The database engine. If not provided, the global engine will be used.

    Returns:
        SQLAlchemy sessionmaker
    """
    engine = engine or get_engine()
    return sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=engine,
    )


# Create a global session factory
_session_factory: Optional[sessionmaker] = None


def get_session_factory() -> sessionmaker:
    """Get the session factory, creating it if it doesn't exist."""
    global _session_factory
    if _session_factory is None:
        _session_factory = create_session_factory()
    return _session_factory


def get_db() -> Generator[Session, None, None]:
    """
    Get a database session from the session factory.
    This function is meant to be used as a FastAPI dependency.

    Yields:
        A SQLAlchemy Session
    """
    session_factory = get_session_factory()
    db = session_factory()
    try:
        yield db
    finally:
        db.close() 