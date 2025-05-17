"""
Basic text processing nodes.

This module provides simple text transformation nodes.
"""

from ..lib_chains.base import TextChainNode
from ..lib_chains.registry import register_node, register_function_node


@register_node(tags=["text", "transformation"])
class UppercaseNode(TextChainNode):
    """Node that converts text to uppercase."""
    
    def process(self, input_text: str) -> str:
        """
        Convert input text to uppercase.
        
        Args:
            input_text: The input text to process
            
        Returns:
            The uppercase version of the input text
        """
        self.validate_input(input_text)
        return input_text.upper()


@register_node(tags=["text", "transformation"])
class LowercaseNode(TextChainNode):
    """Node that converts text to lowercase."""
    
    def process(self, input_text: str) -> str:
        """
        Convert input text to lowercase.
        
        Args:
            input_text: The input text to process
            
        Returns:
            The lowercase version of the input text
        """
        self.validate_input(input_text)
        return input_text.lower()


@register_node(tags=["text", "transformation"])
class ReverseTextNode(TextChainNode):
    """Node that reverses the input text."""
    
    def process(self, input_text: str) -> str:
        """
        Reverse the input text.
        
        Args:
            input_text: The input text to process
            
        Returns:
            The reversed input text
        """
        self.validate_input(input_text)
        return input_text[::-1]


@register_function_node(tags=["text", "transformation"])
def remove_whitespace(input_text: str) -> str:
    """
    Remove all whitespace from the input text.
    
    Args:
        input_text: The input text to process
        
    Returns:
        The input text with all whitespace removed
    """
    return "".join(input_text.split())


@register_function_node(tags=["text", "analysis"])
def count_words(input_text: str) -> str:
    """
    Count the number of words in the input text.
    
    Args:
        input_text: The input text to process
        
    Returns:
        A string representation of the word count
    """
    words = input_text.split()
    return f"Word count: {len(words)}"


@register_function_node(tags=["text", "analysis"])
def count_characters(input_text: str) -> str:
    """
    Count the number of characters in the input text.
    
    Args:
        input_text: The input text to process
        
    Returns:
        A string representation of the character count
    """
    return f"Character count: {len(input_text)}" 