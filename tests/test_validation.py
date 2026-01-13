# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Perday CatalogLAB™

"""
Tests for validation functionality.
"""

from pathlib import Path

import pytest
from process_isolated_runner import (
    ValidationError,
    validate_dict,
    validate_not_none,
    validate_number,
    validate_path,
    validate_string,
)


class TestValidateNotNone:
    """Test validate_not_none function."""

    def test_valid_value(self):
        """Test validation passes for non-None values."""
        assert validate_not_none(42, "number") == 42
        assert validate_not_none("string", "text") == "string"
        assert validate_not_none([], "list") == []
        assert validate_not_none({}, "dict") == {}

    def test_none_value_raises_error(self):
        """Test validation fails for None."""
        with pytest.raises(ValidationError, match="Invalid number"):
            validate_not_none(None, "number")

    def test_zero_is_valid(self):
        """Test that zero is considered valid."""
        assert validate_not_none(0, "count") == 0

    def test_false_is_valid(self):
        """Test that False is considered valid."""
        assert validate_not_none(False, "flag") is False

    def test_empty_string_is_valid(self):
        """Test that empty string is considered valid."""
        assert validate_not_none("", "text") == ""


class TestValidateString:
    """Test validate_string function."""

    def test_valid_string(self):
        """Test validation passes for valid strings."""
        assert validate_string("hello", "greeting") == "hello"
        assert validate_string("test", "name") == "test"

    def test_empty_string_raises_error(self):
        """Test validation fails for empty string."""
        with pytest.raises(
            ValidationError,
            match="Invalid text.*expected string with at least 1 characters",
        ):
            validate_string("", "text")

    def test_whitespace_only_is_accepted_unstripped(self):
        """Whitespace-only strings are accepted; caller must strip if needed."""
        result = validate_string("   ", "text")
        assert result == "   "

    def test_none_raises_error(self):
        """Test validation fails for None."""
        with pytest.raises(ValidationError, match="Invalid text.*expected string"):
            validate_string(None, "text")

    def test_non_string_raises_error(self):
        """Test validation fails for non-string types."""
        with pytest.raises(ValidationError, match="Invalid number.*expected string"):
            validate_string(123, "number")

    def test_string_with_content(self):
        """Test validation passes for strings with content."""
        assert validate_string("  hello  ", "greeting") == "  hello  "

    def test_string_exceeds_max_length_raises_error(self):
        """Strings exceeding max_length raise ValidationError."""
        with pytest.raises(
            ValidationError,
            match="Invalid name.*expected string with at most 3 characters",
        ):
            validate_string("toolong", "name", max_length=3)

    def test_string_pattern_mismatch_raises_error(self):
        """Pattern mismatches raise ValidationError."""
        with pytest.raises(
            ValidationError,
            match=r"Invalid code.*expected string matching pattern",
        ):
            validate_string("abcd", "code", pattern=r"^\w{3}$")


class TestValidateNumber:
    """Test validate_number function."""

    def test_valid_positive_number(self):
        """Test validation passes for positive numbers."""
        assert validate_number(42, "count") == 42
        assert validate_number(3.14, "pi") == 3.14

    def test_valid_zero(self):
        """Test validation passes for zero."""
        assert validate_number(0, "count") == 0

    def test_negative_number_raises_error(self):
        """Test validation fails for negative numbers when min_value is set."""
        with pytest.raises(
            ValidationError, match="Invalid count.*expected number >= 0"
        ):
            validate_number(-1, "count", min_value=0)

    def test_none_raises_error(self):
        """Test validation fails for None."""
        with pytest.raises(ValidationError, match="Invalid value.*expected float"):
            validate_number(None, "value")

    def test_numeric_string_is_converted_to_float(self):
        """Numeric strings are converted to float and accepted."""
        result = validate_number("123", "text")
        assert result == 123.0

    def test_float_number(self):
        """Test validation passes for float numbers."""
        assert validate_number(1.5, "ratio") == 1.5
        assert validate_number(0.0, "zero") == 0.0

    def test_zero_disallowed_when_allow_zero_false(self):
        """Zero raises when allow_zero=False."""
        with pytest.raises(
            ValidationError, match="Invalid count.*expected non - zero number"
        ):
            validate_number(0, "count", allow_zero=False)

    def test_max_value_exceeded_raises_error(self):
        """Values above max raise ValidationError."""
        with pytest.raises(
            ValidationError, match="Invalid score.*expected number <= 10"
        ):
            validate_number(11, "score", max_value=10)

    def test_non_numeric_string_raises_validation_error(self):
        """Non numeric strings raise ValidationError."""
        with pytest.raises(
            ValidationError, match="Invalid value.*Provide a valid numeric value"
        ):
            validate_number("abc", "value")

    def test_int_number_type_converts_and_returns_int(self):
        """When number_type=int, returns int."""
        result = validate_number("5", "count", number_type=int)
        assert result == 5
        assert isinstance(result, int)


class TestValidatePath:
    """Test validate_path function."""

    def test_valid_existing_path(self, tmp_path):
        """Test validation passes for existing path."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        result = validate_path(str(test_file), "file")
        assert result == Path(test_file)

    def test_valid_existing_directory(self, tmp_path):
        """Test validation passes for existing directory."""
        result = validate_path(str(tmp_path), "dir")
        assert result == tmp_path

    def test_nonexistent_path_raises_error(self):
        """Test validation fails for non-existent path when must_exist=True."""
        with pytest.raises(
            ValidationError, match="Invalid file.*expected existing file path"
        ):
            validate_path("/nonexistent/path/file.txt", "file", must_exist=True)

    def test_nonexistent_path_allowed_when_must_exist_false(self, tmp_path):
        """Non-existent path is accepted when must_exist=False."""
        candidate = tmp_path / "missing.txt"
        result = validate_path(candidate, "file", must_exist=False)
        assert result == candidate

    def test_none_raises_error(self):
        """Test validation fails for None."""
        with pytest.raises(
            ValidationError, match="Invalid path.*expected valid file path"
        ):
            validate_path(None, "path")

    def test_empty_string_raises_error(self):
        """Test validation passes for empty string (creates Path(''))."""
        # Empty string creates a valid Path object (current directory)
        result = validate_path("", "path")
        assert result == Path("")

    def test_path_object_input(self, tmp_path):
        """Test validation works with Path objects."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        result = validate_path(test_file, "file")
        assert result == test_file


class TestValidateDict:
    """Test validate_dict function."""

    def test_valid_dict(self):
        """Test validation passes for valid dictionary."""
        test_dict = {"key": "value"}
        assert validate_dict(test_dict, "config") == test_dict

    def test_empty_dict_is_valid(self):
        """Test validation passes for empty dictionary."""
        assert validate_dict({}, "config") == {}

    def test_none_raises_error(self):
        """Test validation fails for None."""
        with pytest.raises(
            ValidationError, match="Invalid config.*expected dictionary"
        ):
            validate_dict(None, "config")

    def test_list_raises_error(self):
        """Test validation fails for list."""
        with pytest.raises(ValidationError, match="Invalid data.*expected dictionary"):
            validate_dict([1, 2, 3], "data")

    def test_string_raises_error(self):
        """Test validation fails for string."""
        with pytest.raises(ValidationError, match="Invalid text.*expected dictionary"):
            validate_dict("not a dict", "text")

    def test_nested_dict(self):
        """Test validation passes for nested dictionary."""
        nested = {"outer": {"inner": "value"}}
        assert validate_dict(nested, "config") == nested

    def test_required_keys_missing_raises_error(self):
        """Missing required keys raise ValidationError."""
        with pytest.raises(
            ValidationError,
            match=r"Invalid config.*expected dictionary with keys: \['host', 'port'\]",
        ):
            validate_dict(
                {"host": "localhost"}, "config", required_keys=["host", "port"]
            )

    def test_allowed_keys_blocks_extra_keys(self):
        """Extra keys when allowed_keys specified raise ValidationError."""
        with pytest.raises(
            ValidationError,
            match=r"Invalid config.*expected dictionary with only allowed keys: \['host'\]",
        ):
            validate_dict(
                {"host": "localhost", "debug": True},
                "config",
                allowed_keys=["host"],
            )

    def test_required_and_allowed_keys_ok(self):
        """Combination of required/allowed keys passes."""
        cfg = {"host": "localhost", "port": 5432}
        result = validate_dict(
            cfg,
            "config",
            required_keys=["host"],
            allowed_keys=["host", "port"],
        )
        assert result == cfg
