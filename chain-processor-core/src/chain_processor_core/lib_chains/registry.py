"""
Node registry for the Chain Processing System.

This module provides a registry for chain nodes, allowing them to be
looked up by name and metadata.
"""

from typing import Dict, List, Type, Optional, Callable, Any, Set
import inspect
import uuid

from .base import ChainNode, TextChainNode, FunctionNode
from ..exceptions.errors import NodeLoadError, NodeNotFoundError


class NodeRegistry:
    """Registry for chain nodes."""

    _instance = None
    
    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super(NodeRegistry, cls).__new__(cls)
            cls._instance._nodes: Dict[str, Type[ChainNode]] = {}
            cls._instance._node_instances: Dict[str, ChainNode] = {}
            cls._instance._tags: Dict[str, Set[str]] = {}
        return cls._instance

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
        if name in self._nodes:
            raise ValueError(f"Node with name '{name}' is already registered")
            
        self._nodes[name] = node_class
        
        # Add tags
        if tags:
            for tag in tags:
                if tag not in self._tags:
                    self._tags[tag] = set()
                self._tags[tag].add(name)
                
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
        if name in self._nodes:
            raise ValueError(f"Node with name '{name}' is already registered")
            
        node = FunctionNode(func, name)
        self._node_instances[name] = node
        
        # Add tags
        if tags:
            for tag in tags:
                if tag not in self._tags:
                    self._tags[tag] = set()
                self._tags[tag].add(name)
                
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
        if name not in self._nodes:
            raise NodeNotFoundError(f"Node '{name}' not found")
        return self._nodes[name]

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
        # Check if we have a pre-instantiated node
        if name in self._node_instances:
            return self._node_instances[name]
            
        # Otherwise, instantiate from the class
        if name not in self._nodes:
            raise NodeNotFoundError(f"Node '{name}' not found")
            
        try:
            node_class = self._nodes[name]
            return node_class(*args, **kwargs)
        except Exception as e:
            raise NodeLoadError(f"Failed to instantiate node '{name}': {e}")

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
            return list(self._tags[tag])
        return list(self._nodes.keys())

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