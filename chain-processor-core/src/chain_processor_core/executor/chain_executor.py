"""
Chain executor implementation.

This module provides the executor for running chain strategies.
"""

import time
import uuid
import re
import logging
from typing import Dict, List, Optional, Any, Tuple, cast

from ..lib_chains.registry import default_registry
from ..lib_chains.base import ChainNode, TextChainNode
from ..exceptions.errors import ChainProcessorError, NodeNotFoundError

logger = logging.getLogger(__name__)


class NodeExecutionResult:
    """Result of a node execution."""
    
    def __init__(
        self,
        node_id: uuid.UUID,
        node_name: str,
        input_text: str,
        output_text: Optional[str] = None,
        error: Optional[str] = None,
        execution_time_ms: Optional[int] = None
    ):
        self.node_id = node_id
        self.node_name = node_name
        self.input_text = input_text
        self.output_text = output_text
        self._error = error
        self.execution_time_ms = execution_time_ms
        self.success = error is None
    
    @property
    def error(self) -> Optional[str]:
        return self._error
    
    @error.setter
    def error(self, value: Optional[str]):
        self._error = value
        self.success = value is None
    
    # For backward compatibility
    @property
    def input_data(self) -> str:
        return self.input_text
        
    @property
    def output_data(self) -> Optional[str]:
        return self.output_text


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
    
    def _sanitize_error_message(self, message: str) -> str:
        """
        Sanitize error messages to remove sensitive information.
        
        Args:
            message: The error message to sanitize
            
        Returns:
            Sanitized message
        """
        # Redact passwords, tokens, keys, credentials
        patterns = [
            # Password patterns
            r'(?:password|passwd|pwd|pass)\s*[=:]\s*[^\s,;]+',
            # API keys and tokens
            r'(?:api[-_]?key|token|secret|access[-_]?key)\s*[=:]\s*[^\s,;]+',
            # Connection strings
            r'(?:connection[-_]?string|conn[-_]?str)\s*[=:]\s*[^\s,;]+',
            # Authentication headers
            r'(?:authorization|auth)\s*[=:]\s*[^\s,;]+',
            # JWT tokens
            r'(?:bearer|jwt)\s+[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+',
            # Basic auth
            r'basic\s+[A-Za-z0-9+/=]+',
            # URLs with credentials
            r'(?:https?|ftp|sftp)://[^:]+:[^@]+@',
        ]
        
        sanitized = message
        for pattern in patterns:
            sanitized = re.sub(pattern, '[REDACTED]', sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    def get_node_uuid(self, node_name: str) -> uuid.UUID:
        """
        Get the UUID for a node name. If the node is built-in and doesn't
        have a UUID, generate a deterministic one based on the name.
        
        Args:
            node_name: Name of the node
            
        Returns:
            UUID for the node
        """
        # Use the registry to get the UUID if possible
        try:
            uuid_from_registry = default_registry.get_node_uuid(node_name)
            logger.debug(f"Using UUID from registry for {node_name}: {uuid_from_registry}")
            return uuid_from_registry
        except NodeNotFoundError as e:
            # This is an expected case - fall through to deterministic generation
            logger.debug(f"Node {node_name} not found in registry, generating UUID")
        except Exception as e:
            # Log unexpected errors but still continue
            logger.warning(f"Unexpected error getting UUID from registry for {node_name}: {str(e)}")
            
        # Generate a deterministic UUID from the name
        # This ensures consistency across executions
        namespace = uuid.UUID('9e5d3eaa-f5c8-4d03-956d-17f455189c27')  # Fixed namespace for nodes
        return uuid.uuid5(namespace, node_name)
    
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
        logger.info(f"Starting chain execution for chain {chain_id}")
        chain_start_time = time.time()
        node_results: List[NodeExecutionResult] = []
        current_data = input_data
        
        try:
            # Execute each node in the chain
            for node_name, config in node_configs:
                # Generate UUID for this node
                node_uuid = self.get_node_uuid(node_name)
                logger.debug(f"Generated UUID for node {node_name}: {node_uuid}")
                
                # Create a node execution result object
                node_result = NodeExecutionResult(
                    node_id=node_uuid,
                    node_name=node_name,
                    input_text=current_data
                )
                
                try:
                    # Get the node
                    node_start_time = time.time()
                    logger.debug(f"Getting node instance for {node_name}")
                    
                    # Get the node instance from the registry
                    try:
                        node = default_registry.get_node_instance(node_name, **config)
                        logger.debug(f"Got node instance: {type(node).__name__}")
                    except NodeNotFoundError:
                        logger.error(f"Node '{node_name}' not found in registry")
                        raise NodeNotFoundError(f"Node '{node_name}' not found in registry")
                    
                    # Process the data
                    logger.debug(f"Processing data with node {node_name}")
                    result = node.process(current_data)
                    if not isinstance(result, str):
                        error_msg = f"Node '{node_name}' returned {type(result)}, expected str"
                        logger.error(error_msg)
                        raise TypeError(error_msg)
                    if not result:  # Check if result is empty
                        error_msg = f"Node '{node_name}' returned empty string"
                        logger.warning(error_msg)
                        # Just log a warning but continue
                    current_data = result
                    logger.debug(f"Node {node_name} processed data successfully")
                    
                    # Update node result
                    node_execution_time = int((time.time() - node_start_time) * 1000)
                    node_result.output_text = current_data
                    node_result.execution_time_ms = node_execution_time
                    
                except Exception as e:
                    # If node execution fails, record the error
                    error_msg = self._sanitize_error_message(str(e))
                    logger.error(f"Node execution failed: {error_msg}")
                    node_result.error = error_msg
                    raise ChainProcessorError(f"Node '{node_name}' execution failed: {error_msg}")
                finally:
                    # Add the node result to the list
                    node_results.append(node_result)
            
            # Calculate total execution time
            chain_execution_time = int((time.time() - chain_start_time) * 1000)
            logger.info(f"Chain execution completed successfully in {chain_execution_time}ms")
            
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
            error_msg = self._sanitize_error_message(str(e))
            logger.error(f"Chain execution failed: {error_msg}")
            
            return ChainExecutionResult(
                chain_id=chain_id,
                input_data=input_data,
                error=error_msg,
                execution_time_ms=chain_execution_time,
                node_results=node_results
            ) 