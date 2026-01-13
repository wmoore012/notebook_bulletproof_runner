# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Perday CatalogLAB™

"""
Tests for exception hierarchy.
"""

import pytest
from process_isolated_runner import (
    ConfigurationError,
    IcatNotebookRunnerError,
    MemoryLimitError,
    OperationError,
    ProcessExecutionError,
    ResourceError,
    TimeoutError,
    ValidationError,
)


class TestExceptionHierarchy:
    """Test exception class hierarchy."""

    def test_base_exception(self):
        """Test base exception can be raised."""
        with pytest.raises(IcatNotebookRunnerError):
            raise IcatNotebookRunnerError("Base error")

    def test_validation_error(self):
        """Test ValidationError is subclass of base."""
        with pytest.raises(IcatNotebookRunnerError):
            raise ValidationError("test_field", "invalid_value", "valid value")

    def test_configuration_error(self):
        """Test ConfigurationError is subclass of base."""
        with pytest.raises(IcatNotebookRunnerError):
            raise ConfigurationError("test_key", "Config error")

    def test_resource_error(self):
        """Test ResourceError is subclass of base."""
        with pytest.raises(IcatNotebookRunnerError):
            raise ResourceError("memory", "Resource error")

    def test_operation_error(self):
        """Test OperationError is subclass of base."""
        with pytest.raises(IcatNotebookRunnerError):
            raise OperationError("test_operation", "Operation failed")

    def test_process_execution_error(self):
        """Test ProcessExecutionError is subclass of base."""
        with pytest.raises(IcatNotebookRunnerError):
            raise ProcessExecutionError(exit_code=1)

    def test_timeout_error(self):
        """Test TimeoutError is subclass of base."""
        with pytest.raises(IcatNotebookRunnerError):
            raise TimeoutError(timeout_seconds=5.0)

    def test_memory_limit_error(self):
        """Test MemoryLimitError is subclass of base."""
        with pytest.raises(IcatNotebookRunnerError):
            raise MemoryLimitError(limit_mb=100)


class TestExceptionMessages:
    """Test exception messages."""

    def test_exception_with_message(self):
        """Test exception stores message."""
        error = IcatNotebookRunnerError("Test message")
        assert "Test message" in str(error)

    def test_exception_with_details(self):
        """Test exception with details."""
        error = IcatNotebookRunnerError("Test message", details={"key": "value"})
        assert "Test message" in str(error)
        assert "key=value" in str(error)

    def test_exception_with_suggestion(self):
        """Test exception with suggestion."""
        error = IcatNotebookRunnerError("Test message", suggestion="Try this fix")
        assert "Test message" in str(error)
        assert "Try this fix" in str(error)

    def test_validation_error_message(self):
        """Test ValidationError message format."""
        error = ValidationError("test_field", "bad_value", "good value", "Fix it")
        msg = str(error)
        assert "Invalid test_field" in msg
        assert "bad_value" in msg
        assert "good value" in msg
        assert "Fix it" in msg


class TestExceptionCatching:
    """Test exception catching patterns."""

    def test_catch_specific_exception(self):
        """Test catching specific exception type."""
        with pytest.raises(ValidationError) as exc_info:
            raise ValidationError("field", "value", "expected")

        assert "Invalid field" in str(exc_info.value)

    def test_catch_base_exception(self):
        """Test catching base exception catches all subtypes."""
        with pytest.raises(IcatNotebookRunnerError):
            raise ValidationError("field", "value", "expected")

    def test_multiple_exception_types(self):
        """Test different exception types can be raised."""
        exceptions = [
            ValidationError("field", "value", "expected"),
            ConfigurationError("key", "issue"),
            ResourceError("resource", "issue"),
            OperationError("operation", "reason"),
            ProcessExecutionError(exit_code=1),
            TimeoutError(timeout_seconds=5.0),
            MemoryLimitError(limit_mb=100),
        ]

        for exc in exceptions:
            with pytest.raises(IcatNotebookRunnerError):
                raise exc


class TestExceptionInheritance:
    """Test exception inheritance relationships."""

    def test_validation_error_inheritance(self):
        """Test ValidationError inherits from base."""
        assert issubclass(ValidationError, IcatNotebookRunnerError)

    def test_configuration_error_inheritance(self):
        """Test ConfigurationError inherits from base."""
        assert issubclass(ConfigurationError, IcatNotebookRunnerError)

    def test_resource_error_inheritance(self):
        """Test ResourceError inherits from base."""
        assert issubclass(ResourceError, IcatNotebookRunnerError)

    def test_operation_error_inheritance(self):
        """Test OperationError inherits from base."""
        assert issubclass(OperationError, IcatNotebookRunnerError)

    def test_process_execution_error_inheritance(self):
        """Test ProcessExecutionError inherits from base."""
        assert issubclass(ProcessExecutionError, IcatNotebookRunnerError)

    def test_timeout_error_inheritance(self):
        """Test TimeoutError inherits from base."""
        assert issubclass(TimeoutError, IcatNotebookRunnerError)

    def test_memory_limit_error_inheritance(self):
        """Test MemoryLimitError inherits from base."""
        assert issubclass(MemoryLimitError, IcatNotebookRunnerError)

    def test_all_inherit_from_exception(self):
        """Test all custom exceptions inherit from Exception."""
        exceptions = [
            IcatNotebookRunnerError,
            ValidationError,
            ConfigurationError,
            ResourceError,
            OperationError,
            ProcessExecutionError,
            TimeoutError,
            MemoryLimitError,
        ]

        for exc_class in exceptions:
            assert issubclass(exc_class, Exception)
