"""
Input validation utilities for the Chain Processing System.

This module provides utilities for validating input data.
"""

import re
from typing import Optional, Dict, Any, List, Callable, Union, Pattern
from uuid import UUID

from ..exceptions.errors import InvalidInputError


def validate_uuid(uuid_str: str, field_name: str = "ID") -> UUID:
    """
    Validate that a string is a valid UUID.
    
    Args:
        uuid_str: The string to validate
        field_name: The name of the field being validated
        
    Returns:
        The validated UUID
        
    Raises:
        InvalidInputError: If the string is not a valid UUID
    """
    try:
        return UUID(uuid_str)
    except (ValueError, AttributeError, TypeError):
        raise InvalidInputError(f"{field_name} must be a valid UUID")


def validate_text(text: str, min_length: Optional[int] = None, 
                 max_length: Optional[int] = None, 
                 pattern: Optional[Union[str, Pattern]] = None,
                 field_name: str = "Text") -> str:
    """
    Validate text input.
    
    Args:
        text: The text to validate
        min_length: Optional minimum length
        max_length: Optional maximum length
        pattern: Optional regex pattern
        field_name: The name of the field being validated
        
    Returns:
        The validated text
        
    Raises:
        InvalidInputError: If the text fails validation
    """
    if not isinstance(text, str):
        raise InvalidInputError(f"{field_name} must be a string")
        
    if min_length is not None and len(text) < min_length:
        raise InvalidInputError(f"{field_name} must be at least {min_length} characters")
        
    if max_length is not None and len(text) > max_length:
        raise InvalidInputError(f"{field_name} must be at most {max_length} characters")
        
    if pattern is not None:
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        if not pattern.match(text):
            raise InvalidInputError(f"{field_name} must match the required pattern")
            
    return text


def validate_numeric(value: Union[int, float], min_value: Optional[Union[int, float]] = None,
                    max_value: Optional[Union[int, float]] = None,
                    field_name: str = "Value") -> Union[int, float]:
    """
    Validate numeric input.
    
    Args:
        value: The value to validate
        min_value: Optional minimum value
        max_value: Optional maximum value
        field_name: The name of the field being validated
        
    Returns:
        The validated value
        
    Raises:
        InvalidInputError: If the value fails validation
    """
    if not isinstance(value, (int, float)):
        raise InvalidInputError(f"{field_name} must be a number")
        
    if min_value is not None and value < min_value:
        raise InvalidInputError(f"{field_name} must be at least {min_value}")
        
    if max_value is not None and value > max_value:
        raise InvalidInputError(f"{field_name} must be at most {max_value}")
        
    return value


def validate_email(email: str, field_name: str = "Email") -> str:
    """
    Validate an email address.
    
    Args:
        email: The email to validate
        field_name: The name of the field being validated
        
    Returns:
        The validated email
        
    Raises:
        InvalidInputError: If the email is invalid
    """
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return validate_text(email, pattern=email_pattern, field_name=field_name)


def validate_url(url: str, field_name: str = "URL") -> str:
    """
    Validate a URL.
    
    Args:
        url: The URL to validate
        field_name: The name of the field being validated
        
    Returns:
        The validated URL
        
    Raises:
        InvalidInputError: If the URL is invalid
    """
    url_pattern = r'^(https?|ftp)://[^\s/$.?#].[^\s]*$'
    return validate_text(url, pattern=url_pattern, field_name=field_name) 