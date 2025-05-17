"""
Pytest configuration for the Chain Processor Core tests.
"""

import pytest
from uuid import uuid4
from datetime import datetime, timedelta

from chain_processor_core.models.base import BaseModelWithId, TimestampedModel, VersionedModel
from chain_processor_core.models.chain import ChainStrategy, StrategyNodeLink
from chain_processor_core.models.node import Node, NodeParameter
from chain_processor_core.models.execution import ChainExecution, NodeExecution
from chain_processor_core.models.user import User


@pytest.fixture
def sample_node():
    """Fixture providing a sample node."""
    return Node(
        id=uuid4(),
        name="Test Node",
        description="A test node",
        code="def node(input_text: str) -> str:\n    return input_text.upper()",
        parameters=[
            NodeParameter(
                name="param1",
                description="A test parameter",
                type="string",
                required=True
            )
        ],
        created_by=uuid4(),
        tags=["test", "example"]
    )


@pytest.fixture
def sample_strategy(sample_node):
    """Fixture providing a sample chain strategy."""
    return ChainStrategy(
        id=uuid4(),
        name="Test Strategy",
        description="A test strategy",
        strategy_nodes=[
            StrategyNodeLink(
                strategy_id=uuid4(),
                node_id=sample_node.id,
                position=0,
                config={"param1": "value1"}
            )
        ],
        created_by=uuid4(),
        tags=["test", "example"]
    )


@pytest.fixture
def sample_chain_execution(sample_strategy):
    """Fixture providing a sample chain execution."""
    return ChainExecution(
        id=uuid4(),
        strategy_id=sample_strategy.id,
        input_text="Hello, world!",
        status="pending",
        started_at=datetime.utcnow(),
        created_by=uuid4(),
        metadata={"source": "test"}
    )


@pytest.fixture
def sample_node_execution(sample_chain_execution, sample_node):
    """Fixture providing a sample node execution."""
    return NodeExecution(
        id=uuid4(),
        execution_id=sample_chain_execution.id,
        node_id=sample_node.id,
        input_text="Hello, world!",
        status="pending",
        started_at=datetime.utcnow()
    )


@pytest.fixture
def sample_user():
    """Fixture providing a sample user."""
    return User(
        id=uuid4(),
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        roles=["admin", "editor"],
        last_login=datetime.utcnow() - timedelta(hours=1)
    ) 