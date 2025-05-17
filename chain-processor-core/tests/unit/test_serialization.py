"""
Unit tests for serialization utilities.
"""

import json
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from uuid import UUID
import pytest

from pydantic import BaseModel

from chain_processor_core.utils.serialization import (
    CustomJSONEncoder,
    json_dumps,
    json_loads,
    serialize_model,
    deserialize_model,
    deserialize_models,
)
from chain_processor_core.models.base import BaseModelWithId, TimestampedModel, VersionedModel


class SampleEnum(Enum):
    """Sample enum for testing."""
    VALUE1 = "value1"
    VALUE2 = "value2"


class SampleModel(BaseModel):
    """Sample model for testing."""
    name: str
    value: int


class TestCustomJSONEncoder:
    """Test case for CustomJSONEncoder."""

    def test_datetime_serialization(self):
        """Test serialization of datetime objects."""
        dt = datetime(2023, 1, 1, 12, 0, 0)
        encoder = CustomJSONEncoder()
        result = encoder.default(dt)
        assert result == "2023-01-01T12:00:00"

    def test_date_serialization(self):
        """Test serialization of date objects."""
        d = date(2023, 1, 1)
        encoder = CustomJSONEncoder()
        result = encoder.default(d)
        assert result == "2023-01-01"

    def test_uuid_serialization(self):
        """Test serialization of UUID objects."""
        uuid_obj = UUID("123e4567-e89b-12d3-a456-426614174000")
        encoder = CustomJSONEncoder()
        result = encoder.default(uuid_obj)
        assert result == "123e4567-e89b-12d3-a456-426614174000"

    def test_decimal_serialization(self):
        """Test serialization of Decimal objects."""
        decimal_obj = Decimal("10.5")
        encoder = CustomJSONEncoder()
        result = encoder.default(decimal_obj)
        assert result == 10.5
        assert isinstance(result, float)

    def test_enum_serialization(self):
        """Test serialization of Enum objects."""
        enum_obj = SampleEnum.VALUE1
        encoder = CustomJSONEncoder()
        result = encoder.default(enum_obj)
        assert result == "value1"

    def test_pydantic_model_serialization(self):
        """Test serialization of Pydantic models."""
        model = SampleModel(name="test", value=42)
        encoder = CustomJSONEncoder()
        result = encoder.default(model)
        assert result == {"name": "test", "value": 42}


class TestJsonFunctions:
    """Test case for JSON serialization functions."""

    def test_json_dumps(self):
        """Test json_dumps function."""
        # Test with simple data
        data = {"name": "test", "value": 42}
        result = json_dumps(data)
        assert result == '{"name": "test", "value": 42}'

        # Test with complex data
        complex_data = {
            "datetime": datetime(2023, 1, 1, 12, 0, 0),
            "uuid": UUID("123e4567-e89b-12d3-a456-426614174000"),
            "decimal": Decimal("10.5"),
            "enum": SampleEnum.VALUE1,
            "model": SampleModel(name="test", value=42)
        }
        result = json_dumps(complex_data)
        expected = json.dumps({
            "datetime": "2023-01-01T12:00:00",
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "decimal": 10.5,
            "enum": "value1",
            "model": {"name": "test", "value": 42}
        })
        assert json.loads(result) == json.loads(expected)

    def test_json_loads(self):
        """Test json_loads function."""
        # Test with simple data
        json_str = '{"name": "test", "value": 42}'
        result = json_loads(json_str)
        assert result == {"name": "test", "value": 42}

        # Test with custom kwargs
        json_str = '{"name": "test", "value": 42}'
        result = json_loads(json_str, object_hook=lambda d: {k.upper(): v for k, v in d.items()})
        assert result == {"NAME": "test", "VALUE": 42}


class TestModelSerialization:
    """Test case for model serialization functions."""

    def test_serialize_model(self):
        """Test serialize_model function."""
        # Test with simple model
        model = SampleModel(name="test", value=42)
        result = serialize_model(model)
        assert result == {"name": "test", "value": 42}

        # Test with None values
        class ModelWithNone(BaseModel):
            name: str
            value: int = None

        model = ModelWithNone(name="test")
        # With exclude_none=True (default)
        result = serialize_model(model)
        assert result == {"name": "test"}
        # With exclude_none=False
        result = serialize_model(model, exclude_none=False)
        assert result == {"name": "test", "value": None}

    def test_deserialize_model(self):
        """Test deserialize_model function."""
        # Test with simple model
        data = {"name": "test", "value": 42}
        result = deserialize_model(SampleModel, data)
        assert isinstance(result, SampleModel)
        assert result.name == "test"
        assert result.value == 42

    def test_deserialize_models(self):
        """Test deserialize_models function."""
        # Test with list of models
        data_list = [
            {"name": "test1", "value": 42},
            {"name": "test2", "value": 43}
        ]
        result = deserialize_models(SampleModel, data_list)
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(item, SampleModel) for item in result)
        assert result[0].name == "test1"
        assert result[0].value == 42
        assert result[1].name == "test2"
        assert result[1].value == 43


class TestIntegration:
    """Integration tests for serialization utilities."""

    def test_base_model_serialization(self):
        """Test serialization of base models."""
        # Test BaseModelWithId
        model = BaseModelWithId()
        serialized = serialize_model(model)
        assert "id" in serialized
        deserialized = deserialize_model(BaseModelWithId, serialized)
        assert isinstance(deserialized, BaseModelWithId)
        assert deserialized.id == model.id

        # Test TimestampedModel
        model = TimestampedModel()
        serialized = serialize_model(model)
        assert "id" in serialized
        assert "created_at" in serialized
        assert "updated_at" in serialized
        deserialized = deserialize_model(TimestampedModel, serialized)
        assert isinstance(deserialized, TimestampedModel)
        assert deserialized.id == model.id
        assert deserialized.created_at == model.created_at
        assert deserialized.updated_at == model.updated_at

        # Test VersionedModel
        model = VersionedModel()
        serialized = serialize_model(model)
        assert "id" in serialized
        assert "created_at" in serialized
        assert "updated_at" in serialized
        assert "version" in serialized
        deserialized = deserialize_model(VersionedModel, serialized)
        assert isinstance(deserialized, VersionedModel)
        assert deserialized.id == model.id
        assert deserialized.created_at == model.created_at
        assert deserialized.updated_at == model.updated_at
        assert deserialized.version == model.version

    def test_roundtrip_serialization(self):
        """Test full roundtrip serialization."""
        # Create a model
        model = VersionedModel()
        
        # Serialize to JSON string
        json_str = json_dumps(model)
        
        # Deserialize from JSON string
        data = json_loads(json_str)
        
        # Deserialize to model
        deserialized = deserialize_model(VersionedModel, data)
        
        # Verify
        assert isinstance(deserialized, VersionedModel)
        assert deserialized.id == model.id
        assert deserialized.created_at == model.created_at
        assert deserialized.updated_at == model.updated_at
        assert deserialized.version == model.version 