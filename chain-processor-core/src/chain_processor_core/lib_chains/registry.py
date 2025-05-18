"""
Node registry for the Chain Processing System.

This module provides a registry for chain nodes, allowing them to be
looked up by name and metadata.
"""

from typing import Dict, List, Type, Optional, Callable, Any, Set
import inspect
import uuid
import logging

from .base import ChainNode, TextChainNode, FunctionNode
from ..exceptions.errors import NodeLoadError, NodeNotFoundError

logger = logging.getLogger(__name__)


class NodeRegistry:
    """Registry for chain nodes."""

    _instance = None
    
    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super(NodeRegistry, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
        
    def _initialize(self):
        """Initialize the registry data structures."""
        self._nodes: Dict[str, Type[ChainNode]] = {}
        self._node_instances: Dict[str, ChainNode] = {}
        self._tags: Dict[str, Set[str]] = {}
        self._node_uuids: Dict[str, uuid.UUID] = {}  # Store UUIDs for nodes
        
    def clear(self):
        """
        Clear all registered nodes and tags.
        This method is primarily intended for testing purposes.
        """
        self._initialize()

    def register(self, node_class: Type[ChainNode], name: Optional[str] = None, tags: Optional[List[str]] = None) -> str:
        """
        Register a node class.
        
        Args:
            node_class: The node class to register
            name: Optional name for the node (defaults to class name)
            tags: Optional tags for categorizing the node
            
        Returns:
            The node identifier
            
        Raises:
            ValueError: If the node is already registered
        """
        name = name or node_class.__name__
        node_key = f"class:{name}"
        
        if node_key in self._nodes:
            raise ValueError(f"Node with name '{name}' is already registered")
            
        self._nodes[node_key] = node_class
        
        # Generate a deterministic UUID for this node type
        namespace = uuid.UUID('9e5d3eaa-f5c8-4d03-956d-17f455189c27')  # Fixed namespace for nodes
        node_uuid = uuid.uuid5(namespace, node_key)
        self._node_uuids[node_key] = node_uuid
        
        # Add tags
        if tags:
            for tag in tags:
                if tag not in self._tags:
                    self._tags[tag] = set()
                self._tags[tag].add(node_key)
                
        return name

    def register_function(self, func: Callable[[str], str], name: Optional[str] = None, 
                         tags: Optional[List[str]] = None) -> str:
        """
        Register a function as a node.
        
        Args:
            func: The function to register
            name: Optional name for the node (defaults to function name)
            tags: Optional tags for categorizing the node
            
        Returns:
            The node identifier
            
        Raises:
            ValueError: If the node is already registered
        """
        name = name or func.__name__
        node_key = f"func:{name}"
        
        if node_key in self._nodes or node_key in self._node_instances:
            raise ValueError(f"Node with name '{name}' is already registered")
            
        # Create function node instance
        node = FunctionNode(func, name)
        
        # Store in both dictionaries
        self._nodes[node_key] = FunctionNode  # Register the class
        self._node_instances[node_key] = node  # Store the instance
        
        # Generate a deterministic UUID for this node
        namespace = uuid.UUID('9e5d3eaa-f5c8-4d03-956d-17f455189c27')  # Fixed namespace for nodes
        node_uuid = uuid.uuid5(namespace, node_key)
        self._node_uuids[node_key] = node_uuid
        
        # Add tags
        if tags:
            for tag in tags:
                if tag not in self._tags:
                    self._tags[tag] = set()
                self._tags[tag].add(node_key)
                
        return name

    def get_node_class(self, name: str) -> Type[ChainNode]:
        """
        Get a node class by name.
        
        Args:
            name: The name of the node
            
        Returns:
            The node class
            
        Raises:
            NodeNotFoundError: If the node is not found
        """
        # Try with explicit namespace
        if name.startswith("class:") or name.startswith("func:"):
            if name in self._nodes:
                return self._nodes[name]
        
        # Try class namespace first
        class_key = f"class:{name}"
        if class_key in self._nodes:
            return self._nodes[class_key]
            
        # Try function namespace second
        func_key = f"func:{name}"
        if func_key in self._nodes:
            return self._nodes[func_key]
            
        # For backward compatibility, try without namespace
        if name in self._nodes:
            return self._nodes[name]
            
        raise NodeNotFoundError(f"Node '{name}' not found")

    def get_node_instance(self, name: str, *args: Any, **kwargs: Any) -> ChainNode:
        """
        Get a node instance by name.
        
        If the node is a function node that's already instantiated, return it.
        Otherwise, instantiate a new instance of the node class.
        
        Args:
            name: The name of the node
            *args: Arguments to pass to the node constructor
            **kwargs: Keyword arguments to pass to the node constructor
            
        Returns:
            The node instance
            
        Raises:
            NodeNotFoundError: If the node is not found
            NodeLoadError: If the node cannot be instantiated
        """
        # Check if we have a pre-instantiated node with namespaces
        func_key = f"func:{name}"
        if func_key in self._node_instances:
            return self._node_instances[func_key]
            
        # For backward compatibility, check without namespace
        if name in self._node_instances:
            return self._node_instances[name]
            
        # Otherwise, get the class and instantiate
        try:
            node_class = self.get_node_class(name)
            return node_class(*args, **kwargs)
        except NodeNotFoundError:
            raise
        except Exception as e:
            raise NodeLoadError(f"Failed to instantiate node '{name}': {e}")

    def get_node_uuid(self, node_name: str) -> uuid.UUID:
        """
        Get the UUID for a node by name.
        
        Args:
            name: The name of the node
            
        Returns:
            UUID for the node
        """
        # Try existing lookups first
        for key in [f"class:{node_name}", f"func:{node_name}", node_name]:
            if key in self._node_uuids:
                return self._node_uuids[key]
        
        # Generate a deterministic UUID
        namespace = uuid.UUID('9e5d3eaa-f5c8-4d03-956d-17f455189c27')
        generated_uuid = uuid.uuid5(namespace, node_name)
        
        # Check if this UUID already exists with a different name
        reverse_lookup = {str(id): name for name, id in self._node_uuids.items()}
        if str(generated_uuid) in reverse_lookup:
            conflicting_name = reverse_lookup[str(generated_uuid)]
            logger.warning(
                f"UUID collision: {node_name} and {conflicting_name} "
                f"would both generate {generated_uuid}"
            )
            # Create a unique namespaced UUID by adding a suffix
            suffix = 0
            while str(generated_uuid) in reverse_lookup:
                suffix += 1
                generated_uuid = uuid.uuid5(namespace, f"{node_name}_{suffix}")
        
        # Store this mapping for future lookups
        self._node_uuids[node_name] = generated_uuid
        return generated_uuid

    def list_nodes(self, tag: Optional[str] = None) -> List[str]:
        """
        List all registered nodes, optionally filtered by tag.
        
        Args:
            tag: Optional tag to filter by
            
        Returns:
            A list of node names
        """
        if tag:
            if tag not in self._tags:
                return []
            # Strip namespace prefixes when returning node names
            return [key.split(':', 1)[1] if ':' in key else key for key in self._tags[tag]]
        
        # Strip namespace prefixes when returning node names
        return [key.split(':', 1)[1] if ':' in key else key for key in self._nodes.keys()]

    def list_tags(self) -> List[str]:
        """
        List all tags.
        
        Returns:
            A list of tag names
        """
        return list(self._tags.keys())


# Create the default registry instance
default_registry = NodeRegistry()


def register_node(name: Optional[str] = None, tags: Optional[List[str]] = None):
    """
    Decorator to register a node class.
    
    Args:
        name: Optional name for the node (defaults to class name)
        tags: Optional tags for categorizing the node
        
    Returns:
        A decorator function
        
    Example:
        @register_node(tags=["text", "manipulation"])
        class UppercaseNode(TextChainNode):
            def process(self, input_text: str) -> str:
                super().process(input_text)
                return input_text.upper()
    """
    def decorator(cls: Type[ChainNode]) -> Type[ChainNode]:
        default_registry.register(cls, name, tags)
        return cls
    return decorator


def register_function_node(name: Optional[str] = None, tags: Optional[List[str]] = None):
    """
    Decorator to register a function as a node.
    
    Args:
        name: Optional name for the node (defaults to function name)
        tags: Optional tags for categorizing the node
        
    Returns:
        A decorator function
        
    Example:
        @register_function_node(tags=["text", "manipulation"])
        def uppercase(text: str) -> str:
            return text.upper()
    """
    def decorator(func: Callable[[str], str]) -> Callable[[str], str]:
        default_registry.register_function(func, name, tags)
        return func
    return decorator 