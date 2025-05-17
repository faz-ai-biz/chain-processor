"""
Exception hierarchy for the Chain Processing System.

This module defines the common exception classes used across all services
in the Chain Processing System.
"""

from typing import Optional


class ChainProcessorError(Exception):
    """Base exception for all Chain Processor errors."""

    def __init__(self, message: str, code: Optional[str] = None):
        """
        Initialize a new ChainProcessorError.

        Args:
            message: Error message
            code: Optional error code
        """
        self.message = message
        self.code = code
        super().__init__(message)


class StrategyError(ChainProcessorError):
    """Base exception for strategy-related errors."""
    pass


class StrategyNotFoundError(StrategyError):
    """Raised when a strategy is not found."""
    pass


class StrategyValidationError(StrategyError):
    """Raised when a strategy fails validation."""
    pass


class NodeError(ChainProcessorError):
    """Base exception for node-related errors."""
    pass


class NodeNotFoundError(NodeError):
    """Raised when a node is not found."""
    pass


class NodeValidationError(NodeError):
    """Raised when a node fails validation."""
    pass


class NodeLoadError(NodeError):
    """Raised when a node cannot be loaded for execution."""
    pass


class ExecutionError(ChainProcessorError):
    """Base exception for execution-related errors."""
    pass


class ExecutionNotFoundError(ExecutionError):
    """Raised when an execution record is not found."""
    pass


class InvalidInputError(ExecutionError):
    """Raised when input validation fails during execution."""
    pass


class AuthenticationError(ChainProcessorError):
    """Raised when authentication fails."""
    pass


class AuthorizationError(ChainProcessorError):
    """Raised when authorization checks fail."""
    pass 