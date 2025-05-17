"""
Chain Processor Core - Foundation library for the Chain Processing System.

This package provides domain models, interfaces, and utilities used across
all services in the Chain Processing System.
"""

__version__ = "0.1.0"

# Import node implementations to ensure they are registered
from . import nodes  # noqa: F401
from .lib_chains.registry import default_registry
from .executor.chain_executor import ChainExecutor

# Export key components
__all__ = ["default_registry", "ChainExecutor"] 
