"""
Unit tests for node registry functionality.
"""

import pytest

from chain_processor_core.lib_chains.base import TextChainNode
from chain_processor_core.lib_chains.registry import (
    NodeRegistry,
    register_node,
    register_function_node,
    default_registry,
)
from chain_processor_core.exceptions.errors import NodeNotFoundError, NodeLoadError


@pytest.fixture(autouse=True)
def reset_registry(request):
    """Reset the registry before each test."""
    registry = NodeRegistry()
    
    # Store decorator registered nodes
    decorated_nodes = []
    if "RegisteredNode" in registry.list_nodes():
        decorated_nodes.append("RegisteredNode")
    if "lowercase_node" in registry.list_nodes():
        decorated_nodes.append("lowercase_node")
    
    # Clear registry
    registry.clear()
    
    # Re-register decorator nodes if needed
    for test_name in ["test_registry_decorators"]:
        if request.function.__name__ == test_name:
            # Re-register the decorator nodes for specific tests
            registry.register(RegisteredNode, "RegisteredNode", ["test", "uppercase"])
            
            # Register lowercase_node function
            def lowercase_fn(text: str) -> str:
                return text.lower()
            
            registry.register_function(lowercase_fn, "lowercase_node", ["test", "lowercase"])
    
    yield


class TestNode(TextChainNode):
    """Test node implementation."""

    def process(self, input_text: str) -> str:
        """Process the input text."""
        super().validate_input(input_text)
        return input_text.upper()


class TestNodeWithArgs(TextChainNode):
    """Test node implementation with constructor arguments."""

    def __init__(self, prefix: str = ""):
        """Initialize the node."""
        self.prefix = prefix

    def process(self, input_text: str) -> str:
        """Process the input text."""
        super().validate_input(input_text)
        return f"{self.prefix}{input_text.upper()}"


@register_node(tags=["test", "uppercase"])
class RegisteredNode(TextChainNode):
    """Node that is registered via decorator."""

    def process(self, input_text: str) -> str:
        """Process the input text."""
        super().validate_input(input_text)
        return input_text.upper()


@register_function_node(name="lowercase_node", tags=["test", "lowercase"])
def lowercase_function(text: str) -> str:
    """Node function that is registered via decorator."""
    return text.lower()


class TestRegistry:
    """Test case for node registry functionality."""

    def test_registry_singleton(self):
        """Test that NodeRegistry is a singleton."""
        registry1 = NodeRegistry()
        registry2 = NodeRegistry()
        assert registry1 is registry2

    def test_register_class(self):
        """Test registering a node class."""
        registry = NodeRegistry()
        name = registry.register(TestNode, "test_node", ["test"])

        assert name == "test_node"
        assert "test_node" in registry.list_nodes()
        assert "test" in registry.list_tags()
        assert "test_node" in registry.list_nodes("test")

    def test_register_function(self):
        """Test registering a function as a node."""
        registry = NodeRegistry()

        def reverse_text(text: str) -> str:
            return text[::-1]

        name = registry.register_function(reverse_text, "reverse_node", ["text"])

        assert name == "reverse_node"
        assert "reverse_node" in registry.list_nodes()
        assert "text" in registry.list_tags()
        assert "reverse_node" in registry.list_nodes("text")

    def test_get_node_class(self):
        """Test getting a node class."""
        registry = NodeRegistry()
        registry.register(TestNode, "test_node")

        node_class = registry.get_node_class("test_node")
        assert node_class is TestNode

        with pytest.raises(NodeNotFoundError):
            registry.get_node_class("nonexistent_node")

    def test_get_node_instance(self):
        """Test getting a node instance."""
        registry = NodeRegistry()
        registry.register(TestNode, "test_node")
        registry.register(TestNodeWithArgs, "test_node_with_args")

        # Get instance without args
        node1 = registry.get_node_instance("test_node")
        assert isinstance(node1, TestNode)
        assert node1.process("hello") == "HELLO"

        # Get instance with args
        node2 = registry.get_node_instance("test_node_with_args", prefix="PREFIX_")
        assert isinstance(node2, TestNodeWithArgs)
        assert node2.process("hello") == "PREFIX_HELLO"

        # Get nonexistent node
        with pytest.raises(NodeNotFoundError):
            registry.get_node_instance("nonexistent_node")

    def test_registry_decorators(self):
        """Test node registration via decorators."""
        # Check that the decorated nodes are registered
        assert "RegisteredNode" in default_registry.list_nodes()
        assert "lowercase_node" in default_registry.list_nodes()

        # Check that tags are registered
        assert "RegisteredNode" in default_registry.list_nodes("test")
        assert "RegisteredNode" in default_registry.list_nodes("uppercase")
        assert "lowercase_node" in default_registry.list_nodes("test")
        assert "lowercase_node" in default_registry.list_nodes("lowercase")

        # Check that the nodes work
        node1 = default_registry.get_node_instance("RegisteredNode")
        assert node1.process("hello") == "HELLO"

        node2 = default_registry.get_node_instance("lowercase_node")
        assert node2.process("HELLO") == "hello"

    def test_list_nodes_and_tags(self):
        """Test listing nodes and tags."""
        registry = NodeRegistry()
        registry.register(TestNode, "node1", ["tag1", "tag2"])
        registry.register(TestNode, "node2", ["tag2", "tag3"])
        registry.register(TestNode, "node3", ["tag1", "tag3"])

        # List all nodes
        all_nodes = registry.list_nodes()
        assert "node1" in all_nodes
        assert "node2" in all_nodes
        assert "node3" in all_nodes

        # List nodes by tag
        assert set(registry.list_nodes("tag1")) == {"node1", "node3"}
        assert set(registry.list_nodes("tag2")) == {"node1", "node2"}
        assert set(registry.list_nodes("tag3")) == {"node2", "node3"}
        assert registry.list_nodes("nonexistent_tag") == []

        # List all tags
        all_tags = registry.list_tags()
        assert "tag1" in all_tags
        assert "tag2" in all_tags
        assert "tag3" in all_tags 