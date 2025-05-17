from datetime import datetime, timedelta
from uuid import uuid4

from chain_processor_core.models.execution import ChainExecution


class TestChainExecutionValidation:
    """Tests for ChainExecution model validation."""

    def test_validate_completion_sets_time(self):
        start = datetime.utcnow() - timedelta(seconds=1)
        exec_model = ChainExecution(
            strategy_id=uuid4(),
            input_text="hello",
            status="success",
            started_at=start,
        )
        assert exec_model.completed_at is not None
        assert exec_model.execution_time_ms is not None
        expected_ms = int((exec_model.completed_at - start).total_seconds() * 1000)
        assert exec_model.execution_time_ms == expected_ms

    def test_validate_completion_uses_provided_completed_at(self):
        start = datetime.utcnow() - timedelta(seconds=5)
        completed = start + timedelta(seconds=2)
        exec_model = ChainExecution(
            strategy_id=uuid4(),
            input_text="hello",
            status="success",
            started_at=start,
            completed_at=completed,
        )
        assert exec_model.completed_at == completed
        assert exec_model.execution_time_ms == 2000

    def test_execution_time_not_overwritten(self):
        start = datetime.utcnow() - timedelta(seconds=10)
        completed = start + timedelta(seconds=4)
        exec_model = ChainExecution(
            strategy_id=uuid4(),
            input_text="hello",
            status="success",
            started_at=start,
            completed_at=completed,
            execution_time_ms=1234,
        )
        assert exec_model.completed_at == completed
        assert exec_model.execution_time_ms == 1234

