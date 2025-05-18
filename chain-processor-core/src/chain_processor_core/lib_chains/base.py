"""
Base classes for chain nodes.

This module defines the base classes for implementing chain nodes.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Callable, TypeVar, Generic

from ..exceptions.errors import InvalidInputError, NodeValidationError


T = TypeVar('T')
U = TypeVar('U')


class ChainNode(ABC, Generic[T, U]):
    """
    Abstract base class for chain nodes.
    
    This class defines the interface that all chain nodes must implement.
    """

    @classmethod
    def validate_input(cls, input_data: T) -> None:
        """
        Validate the input data.
        
        Args:
            input_data: The input data to validate
            
        Raises:
            InvalidInputError: If the input data is invalid
        """
        if input_data is None:
            raise InvalidInputError("Input data cannot be None")

    @abstractmethod
    def process(self, input_data: T) -> U:
        """
        Process the input data and return the transformed output.
        
        Args:
            input_data: The input data to process
            
        Returns:
            The transformed output data
            
        Raises:
            InvalidInputError: If the input data is invalid
            NodeValidationError: If node validation fails
        """
        pass


class TextChainNode(ChainNode[str, str]):
    """
    Base class for chain nodes that process text.
    
    This class implements the ChainNode interface for text-based nodes.
    """

    @classmethod
    def validate_input(cls, input_text: str) -> None:
        """
        Validate the input text.
        
        Args:
            input_text: The input text to validate
            
        Raises:
            InvalidInputError: If the input text is invalid
        """
        super().validate_input(input_text)
        if not isinstance(input_text, str):
            raise InvalidInputError("Input must be a string")
        if not input_text:
            raise InvalidInputError("Input cannot be empty")

    @abstractmethod
    def process(self, input_text: str) -> str:
        """
        Process the input text and return the transformed output.
        
        Args:
            input_text: The input text to process
            
        Returns:
            The transformed output text
            
        Raises:
            InvalidInputError: If the input text is invalid
            NodeValidationError: If node validation fails
        """
        self.validate_input(input_text)
        return input_text


class FunctionNode(TextChainNode):
    """
    Node that wraps a function.
    
    This class allows simple functions to be used as chain nodes.
    """

    def __init__(self, func: Callable[[str], str], name: Optional[str] = None):
        """
        Initialize a new FunctionNode.
        
        Args:
            func: The function to wrap
            name: Optional name for the node
        """
        self.func = func
        self.name = name or func.__name__

    def process(self, input_text: str) -> str:
        """
        Process the input text using the wrapped function.
        
        Args:
            input_text: The input text to process
            
        Returns:
            The transformed output text
            
        Raises:
            NodeValidationError: If validation fails or the function raises an exception
        """
        self.validate_input(input_text)
        try:
            result = self.func(input_text)
            if not isinstance(result, str):
                raise NodeValidationError(
                    f"Function node '{self.name}' returned {type(result)}, expected str"
                )
            return result
        except Exception as e:
            if isinstance(e, NodeValidationError):
                raise e
            raise NodeValidationError(f"Error in function node '{self.name}': {str(e)}") from e


def create_node(func: Callable[[str], str]) -> FunctionNode:
    """
    Create a FunctionNode from a function.
    
    This is a decorator that can be used to convert a function into a chain node.
    
    Args:
        func: The function to convert
        
    Returns:
        A FunctionNode wrapping the function
        
    Example:
        @create_node
        def uppercase_node(text: str) -> str:
            return text.upper()
    """
    return FunctionNode(func) 