# SPDX-License-Identifier: MIT
# Copyright (c) 2024 MusicScope

"""
Custom exceptions for icat-notebook-runner module.

This module provides comprehensive error handling with specific exception types
for different failure scenarios, enabling precise error handling and debugging.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class IcatNotebookRunnerError(Exception):
    """Base exception for all icat-notebook-runner errors."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
    ) -> None:
        """
        Initialize the exception with detailed error information.

        Args:
            message: Human-readable error message
            details: Additional error context and debugging information
            suggestion: Suggested solution or next steps
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.suggestion = suggestion

    def __str__(self) -> str:
        """Return formatted error message with details and suggestions."""
        result = self.message

        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            result += f" (Details: {details_str})"

        if self.suggestion:
            result += f" Suggestion: {self.suggestion}"

        return result


class ValidationError(IcatNotebookRunnerError):
    """Raised when input validation fails."""

    def __init__(
        self, field: str, value: Any, expected: str, suggestion: Optional[str] = None
    ) -> None:
        """
        Initialize validation error with field-specific information.

        Args:
            field: Name of the field that failed validation
            value: The invalid value that was provided
            expected: Description of what was expected
            suggestion: How to fix the validation error
        """
        message = f"Invalid {field}: got {type(value).__name__} '{value}', expected {expected}"
        details = {"field": field, "value": value, "expected": expected}
        super().__init__(message, details, suggestion)
        self.field = field
        self.value = value
        self.expected = expected


class ConfigurationError(IcatNotebookRunnerError):
    """Raised when configuration is invalid or missing."""

    def __init__(self, config_key: str, issue: str, suggestion: Optional[str] = None) -> None:
        """
        Initialize configuration error.

        Args:
            config_key: The configuration key that has an issue
            issue: Description of the configuration problem
            suggestion: How to fix the configuration
        """
        message = f"Configuration error for '{config_key}': {issue}"
        details = {"config_key": config_key, "issue": issue}
        super().__init__(message, details, suggestion)
        self.config_key = config_key
        self.issue = issue


class ResourceError(IcatNotebookRunnerError):
    """Raised when system resources are unavailable or exhausted."""

    def __init__(
        self,
        resource: str,
        issue: str,
        current_usage: Optional[str] = None,
        suggestion: Optional[str] = None,
    ) -> None:
        """
        Initialize resource error.

        Args:
            resource: The resource that is unavailable (memory, disk, network, etc.)
            issue: Description of the resource problem
            current_usage: Current resource usage information
            suggestion: How to resolve the resource issue
        """
        message = f"Resource error ({resource}): {issue}"
        details = {"resource": resource, "issue": issue}
        if current_usage:
            details["current_usage"] = current_usage
        super().__init__(message, details, suggestion)
        self.resource = resource
        self.issue = issue
        self.current_usage = current_usage


class OperationError(IcatNotebookRunnerError):
    """Raised when an operation fails due to business logic or external factors."""

    def __init__(
        self,
        operation: str,
        reason: str,
        retry_possible: bool = False,
        suggestion: Optional[str] = None,
    ) -> None:
        """
        Initialize operation error.

        Args:
            operation: The operation that failed
            reason: Why the operation failed
            retry_possible: Whether retrying the operation might succeed
            suggestion: How to resolve the operation failure
        """
        message = f"Operation '{operation}' failed: {reason}"
        details = {"operation": operation, "reason": reason, "retry_possible": retry_possible}
        super().__init__(message, details, suggestion)
        self.operation = operation
        self.reason = reason
        self.retry_possible = retry_possible


class ProcessExecutionError(OperationError):
    """Raised when process execution fails."""

    def __init__(
        self,
        exit_code: Optional[int] = None,
        stdout: Optional[str] = None,
        stderr: Optional[str] = None,
        suggestion: Optional[str] = None,
    ) -> None:
        reason = (
            f"Process exited with code {exit_code}" if exit_code else "Process execution failed"
        )
        super().__init__("process_execution", reason, suggestion=suggestion)
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr


class TimeoutError(ResourceError):
    """Raised when operation times out."""

    def __init__(
        self, timeout_seconds: float, operation: str = "execution", suggestion: Optional[str] = None
    ) -> None:
        issue = f"Operation timed out after {timeout_seconds}s"
        super().__init__("time", issue, suggestion=suggestion or "Try increasing the timeout value")
        self.timeout_seconds = timeout_seconds
        self.operation = operation


class MemoryLimitError(ResourceError):
    """Raised when memory limit is exceeded."""

    def __init__(
        self, limit_mb: int, used_mb: Optional[float] = None, suggestion: Optional[str] = None
    ) -> None:
        issue = f"Memory limit of {limit_mb}MB exceeded"
        current_usage = f"{used_mb:.1f}MB" if used_mb else None
        super().__init__(
            "memory", issue, current_usage, suggestion or "Try increasing memory_limit_mb parameter"
        )
        self.limit_mb = limit_mb
        self.used_mb = used_mb
