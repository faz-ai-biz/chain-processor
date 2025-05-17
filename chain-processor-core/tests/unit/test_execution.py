"""Unit tests for ChainExecution model."""

from datetime import datetime, timedelta
from uuid import uuid4

from chain_processor_core.models.execution import ChainExecution


def test_chain_execution_completion_and_timing():
    """ChainExecution should populate completion fields on validation."""
    start = datetime.utcnow() - timedelta(milliseconds=10)
    execution = ChainExecution(
        strategy_id=uuid4(),
        input_text="test",
        status="success",
        started_at=start,
    )

    # Re-validate to trigger execution_time_ms calculation
    execution = ChainExecution.model_validate(execution.model_dump())

    assert execution.completed_at is not None
    assert execution.execution_time_ms is not None
    assert execution.execution_time_ms >= 0
