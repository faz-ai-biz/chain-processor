"""
Chain executor implementation.

This module provides the executor for running chain strategies.
"""

import time
import uuid
from typing import Dict, List, Optional, Any, Tuple, cast

from ..lib_chains.registry import default_registry
from ..lib_chains.base import ChainNode, TextChainNode
from ..exceptions.errors import ChainProcessorError, NodeNotFoundError


class NodeExecutionResult:
    """Result of a node execution."""
    
    def __init__(
        self,
        node_id: str,
        input_data: str,
        output_data: Optional[str] = None,
        error: Optional[str] = None,
        execution_time_ms: Optional[int] = None
    ):
        self.node_id = node_id
        self.input_data = input_data
        self.output_data = output_data
        self.error = error
        self.execution_time_ms = execution_time_ms
        self.success = error is None


class ChainExecutionResult:
    """Result of a chain execution."""
    
    def __init__(
        self,
        chain_id: str,
        input_data: str,
        output_data: Optional[str] = None,
        error: Optional[str] = None,
        execution_time_ms: Optional[int] = None,
        node_results: Optional[List[NodeExecutionResult]] = None
    ):
        self.chain_id = chain_id
        self.input_data = input_data
        self.output_data = output_data
        self.error = error
        self.execution_time_ms = execution_time_ms
        self.node_results = node_results or []
        self.success = error is None


class ChainExecutor:
    """Executor for chain strategies."""
    
    def execute_chain(
        self, 
        chain_id: str,
        input_data: str,
        node_configs: List[Tuple[str, Dict[str, Any]]]
    ) -> ChainExecutionResult:
        """
        Execute a chain with the given input data.
        
        Args:
            chain_id: Chain identifier
            input_data: Input data to process
            node_configs: List of (node_id, config) tuples
            
        Returns:
            ChainExecutionResult containing execution results
            
        Raises:
            ChainProcessorError: If execution fails
        """
        chain_start_time = time.time()
        node_results: List[NodeExecutionResult] = []
        current_data = input_data
        
        try:
            # Execute each node in the chain
            for node_id, config in node_configs:
                # Create a node execution result object
                node_result = NodeExecutionResult(node_id=node_id, input_data=current_data)
                
                try:
                    # Get the node
                    node_start_time = time.time()
                    
                    # Get the node instance from the registry
                    try:
                        node = default_registry.get_node_instance(node_id, **config)
                    except NodeNotFoundError:
                        raise NodeNotFoundError(f"Node '{node_id}' not found in registry")
                    
                    # Process the data
                    if isinstance(node, TextChainNode):
                        # For text nodes, pass the string directly
                        current_data = cast(str, node.process(current_data))
                    else:
                        # For other node types, might need different handling
                        current_data = cast(str, node.process(current_data))
                    
                    # Update node result
                    node_execution_time = int((time.time() - node_start_time) * 1000)
                    node_result.output_data = current_data
                    node_result.execution_time_ms = node_execution_time
                    
                except Exception as e:
                    # If node execution fails, record the error
                    node_result.error = str(e)
                    raise ChainProcessorError(f"Node '{node_id}' execution failed: {e}")
                finally:
                    # Add the node result to the list
                    node_results.append(node_result)
            
            # Calculate total execution time
            chain_execution_time = int((time.time() - chain_start_time) * 1000)
            
            # Return successful result
            return ChainExecutionResult(
                chain_id=chain_id,
                input_data=input_data,
                output_data=current_data,
                execution_time_ms=chain_execution_time,
                node_results=node_results
            )
            
        except Exception as e:
            # If chain execution fails, return error result
            chain_execution_time = int((time.time() - chain_start_time) * 1000)
            
            return ChainExecutionResult(
                chain_id=chain_id,
                input_data=input_data,
                error=str(e),
                execution_time_ms=chain_execution_time,
                node_results=node_results
            ) 