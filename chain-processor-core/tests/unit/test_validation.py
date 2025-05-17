"""
Unit tests for validation utilities.
"""

import re
import uuid
import pytest

from chain_processor_core.utils.validation import (
    validate_uuid,
    validate_text,
    validate_numeric,
    validate_email,
    validate_url,
)
from chain_processor_core.exceptions.errors import InvalidInputError


class TestValidation:
    """Test case for validation utilities."""

    def test_validate_uuid(self):
        """Test UUID validation."""
        # Valid UUID
        valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
        result = validate_uuid(valid_uuid)
        assert result == uuid.UUID(valid_uuid)

        # Invalid UUID
        with pytest.raises(InvalidInputError):
            validate_uuid("not-a-uuid")

    def test_validate_text(self):
        """Test text validation."""
        # Basic validation
        assert validate_text("hello") == "hello"

        # Min length validation
        assert validate_text("hello", min_length=5) == "hello"
        with pytest.raises(InvalidInputError):
            validate_text("hi", min_length=3)

        # Max length validation
        assert validate_text("hello", max_length=5) == "hello"
        with pytest.raises(InvalidInputError):
            validate_text("hello world", max_length=5)

        # Pattern validation
        assert validate_text("abc123", pattern=r"^[a-z0-9]+$") == "abc123"
        with pytest.raises(InvalidInputError):
            validate_text("ABC", pattern=r"^[a-z]+$")

        # Compiled pattern
        pattern = re.compile(r"^[a-z]+$")
        assert validate_text("abc", pattern=pattern) == "abc"
        with pytest.raises(InvalidInputError):
            validate_text("123", pattern=pattern)

    def test_validate_numeric(self):
        """Test numeric validation."""
        # Basic validation
        assert validate_numeric(5) == 5
        assert validate_numeric(5.5) == 5.5

        # Type validation
        with pytest.raises(InvalidInputError):
            validate_numeric("5")

        # Min value validation
        assert validate_numeric(5, min_value=5) == 5
        with pytest.raises(InvalidInputError):
            validate_numeric(5, min_value=6)

        # Max value validation
        assert validate_numeric(5, max_value=5) == 5
        with pytest.raises(InvalidInputError):
            validate_numeric(5, max_value=4)

    def test_validate_email(self):
        """Test email validation."""
        # Valid email
        assert validate_email("user@example.com") == "user@example.com"

        # Invalid emails
        with pytest.raises(InvalidInputError):
            validate_email("not-an-email")
        with pytest.raises(InvalidInputError):
            validate_email("user@")
        with pytest.raises(InvalidInputError):
            validate_email("@example.com")

    def test_validate_url(self):
        """Test URL validation."""
        # Valid URLs
        assert validate_url("https://example.com") == "https://example.com"
        assert validate_url("http://example.com/path") == "http://example.com/path"
        assert validate_url("ftp://example.com") == "ftp://example.com"

        # Invalid URLs
        with pytest.raises(InvalidInputError):
            validate_url("not-a-url")
        with pytest.raises(InvalidInputError):
            validate_url("example.com")  # Missing protocol
        with pytest.raises(InvalidInputError):
            validate_url("http://")  # Missing domain 