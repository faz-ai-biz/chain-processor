"""
Serialization utilities for the Chain Processing System.

This module provides utilities for serializing and deserializing data.
"""

import json
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Union, TypeVar, Type, cast
from uuid import UUID

from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for types not natively supported by JSON."""

    def default(self, obj: Any) -> Any:
        """
        Convert objects to JSON-serializable types.
        
        Args:
            obj: The object to convert
            
        Returns:
            A JSON-serializable representation of the object
        """
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        return super().default(obj)


def json_dumps(obj: Any, **kwargs: Any) -> str:
    """
    Serialize an object to a JSON string.
    
    Args:
        obj: The object to serialize
        **kwargs: Additional arguments to pass to json.dumps
        
    Returns:
        The JSON string
    """
    return json.dumps(obj, cls=CustomJSONEncoder, **kwargs)


def json_loads(data: str, **kwargs: Any) -> Any:
    """
    Deserialize a JSON string to an object.
    
    Args:
        data: The JSON string to deserialize
        **kwargs: Additional arguments to pass to json.loads
        
    Returns:
        The deserialized object
    """
    return json.loads(data, **kwargs)


def serialize_model(model: BaseModel, exclude_none: bool = True) -> Dict[str, Any]:
    """
    Serialize a Pydantic model to a dictionary.
    
    Args:
        model: The model to serialize
        exclude_none: Whether to exclude None values
        
    Returns:
        The serialized model as a dictionary
    """
    return model.model_dump(exclude_none=exclude_none)


def deserialize_model(model_class: Type[T], data: Dict[str, Any]) -> T:
    """
    Deserialize a dictionary to a Pydantic model.
    
    Args:
        model_class: The model class to deserialize to
        data: The dictionary to deserialize
        
    Returns:
        The deserialized model
    """
    return model_class.model_validate(data)


def deserialize_models(model_class: Type[T], data_list: List[Dict[str, Any]]) -> List[T]:
    """
    Deserialize a list of dictionaries to a list of Pydantic models.
    
    Args:
        model_class: The model class to deserialize to
        data_list: The list of dictionaries to deserialize
        
    Returns:
        The list of deserialized models
    """
    return [deserialize_model(model_class, item) for item in data_list] 