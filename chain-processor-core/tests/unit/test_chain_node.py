"""
Unit tests for chain node functionality.
"""

import pytest

from chain_processor_core.lib_chains.base import TextChainNode, create_node, FunctionNode
from chain_processor_core.exceptions.errors import InvalidInputError


class UppercaseNode(TextChainNode):
    """Example node that converts text to uppercase."""

    def process(self, input_text: str) -> str:
        """Process the input text."""
        super().validate_input(input_text)
        return input_text.upper()


class LowercaseNode(TextChainNode):
    """Example node that converts text to lowercase."""

    def process(self, input_text: str) -> str:
        """Process the input text."""
        super().validate_input(input_text)
        return input_text.lower()


class TestChainNode:
    """Test case for chain node functionality."""

    def test_text_chain_node(self):
        """Test TextChainNode implementation."""
        # Create nodes
        uppercase_node = UppercaseNode()
        lowercase_node = LowercaseNode()

        # Test processing
        assert uppercase_node.process("hello") == "HELLO"
        assert lowercase_node.process("HELLO") == "hello"

        # Test chaining
        result = lowercase_node.process(uppercase_node.process("Hello World"))
        assert result == "hello world"

    def test_input_validation(self):
        """Test input validation."""
        node = UppercaseNode()

        # Valid input
        assert node.process("hello") == "HELLO"

        # Invalid input
        with pytest.raises(InvalidInputError):
            node.process("")
        with pytest.raises(InvalidInputError):
            node.process(None)  # type: ignore
        with pytest.raises(InvalidInputError):
            node.process(123)  # type: ignore

    def test_function_node(self):
        """Test FunctionNode implementation."""
        # Create a function node
        def reverse_text(text: str) -> str:
            return text[::-1]

        node = FunctionNode(reverse_text)

        # Test processing
        assert node.process("hello") == "olleh"

        # Test input validation
        with pytest.raises(InvalidInputError):
            node.process("")

    def test_create_node_decorator(self):
        """Test create_node decorator."""
        # Create a node using the decorator
        @create_node
        def capitalize_text(text: str) -> str:
            return text.capitalize()

        # Test processing
        assert capitalize_text.process("hello world") == "Hello world"

        # Test input validation
        with pytest.raises(InvalidInputError):
            capitalize_text.process("") 