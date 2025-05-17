"""
Pytest configuration for Chain Processor DB tests.

This module provides fixtures for testing database operations.
"""

import os
import uuid
from typing import Generator

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from chain_processor_db.base import metadata
from chain_processor_db.models import *  # Import all models


@pytest.fixture(scope="session")
def db_url() -> str:
    """Get the database URL for testing."""
    test_db_url = os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/chain_processor_test"
    )
    return test_db_url


@pytest.fixture(scope="session")
def engine(db_url: str):
    """Create a database engine for testing."""
    engine = create_engine(db_url)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def setup_db(engine):
    """Set up the database for testing."""
    # Create all tables
    metadata.create_all(engine)
    yield
    # Drop all tables
    metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session(setup_db, engine) -> Generator[Session, None, None]:
    """Create a database session for testing."""
    connection = engine.connect()
    transaction = connection.begin()
    session_factory = sessionmaker(bind=connection)
    session = session_factory()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def sample_user(db_session: Session):
    """Create a sample user for testing."""
    from chain_processor_db.models.user import User
    
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        full_name="Test User",
        is_active=True,
        is_superuser=False,
        roles=["user"],
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_node(db_session: Session, sample_user):
    """Create a sample node for testing."""
    from chain_processor_db.models.node import Node
    
    node = Node(
        name="Test Node",
        description="A test node",
        code="def node(input_text): return input_text.upper()",
        created_by_id=sample_user.id,
        is_builtin=False,
        is_active=True,
        tags=["test", "uppercase"],
    )
    db_session.add(node)
    db_session.commit()
    db_session.refresh(node)
    return node


@pytest.fixture
def sample_strategy(db_session: Session, sample_user):
    """Create a sample chain strategy for testing."""
    from chain_processor_db.models.chain import ChainStrategy
    
    strategy = ChainStrategy(
        name="Test Strategy",
        description="A test strategy",
        created_by_id=sample_user.id,
        is_active=True,
        tags=["test"],
    )
    db_session.add(strategy)
    db_session.commit()
    db_session.refresh(strategy)
    return strategy


@pytest.fixture
def sample_strategy_node(db_session: Session, sample_strategy, sample_node):
    """Create a sample strategy node link for testing."""
    from chain_processor_db.models.chain import StrategyNode
    
    strategy_node = StrategyNode(
        strategy_id=sample_strategy.id,
        node_id=sample_node.id,
        position=0,
        config={},
    )
    db_session.add(strategy_node)
    db_session.commit()
    db_session.refresh(strategy_node)
    return strategy_node


@pytest.fixture
def sample_chain_execution(db_session: Session, sample_strategy, sample_user):
    """Create a sample chain execution for testing."""
    from chain_processor_db.models.execution import ChainExecution
    
    execution = ChainExecution(
        strategy_id=sample_strategy.id,
        input_text="test input",
        status="pending",
        created_by_id=sample_user.id,
    )
    db_session.add(execution)
    db_session.commit()
    db_session.refresh(execution)
    return execution


@pytest.fixture
def sample_node_execution(db_session: Session, sample_chain_execution, sample_node):
    """Create a sample node execution for testing."""
    from chain_processor_db.models.execution import NodeExecution
    
    node_execution = NodeExecution(
        execution_id=sample_chain_execution.id,
        node_id=sample_node.id,
        input_text="test input",
        status="pending",
    )
    db_session.add(node_execution)
    db_session.commit()
    db_session.refresh(node_execution)
    return node_execution 