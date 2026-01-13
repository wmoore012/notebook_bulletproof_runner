# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Perday CatalogLAB™

"""
Tests for the run_safe function and ExecutionResult.
"""

import os
import time

import pytest
from process_isolated_runner import ExecutionResult, run_safe

from .test_helpers import (
    GLOBAL_STATE,
    allocate_memory,
    counter_func,
    crash,
    divide_by_zero,
    empty,
    factorial,
    fast_function,
    func1,
    func2,
    get_pid,
    instant,
    medium_function,
    modify_global,
    nested_outer,
    quick_function,
    raise_error,
    return_dict,
    return_none,
    return_string,
    runtime_error,
    simple_func,
    slow_function,
    small_allocation,
    timed_function,
    type_error,
)


class TestBasicExecution:
    """Test basic execution functionality."""

    def test_successful_execution(self):
        """Test successful function execution."""
        result = run_safe(simple_func, timeout=5)

        assert result.success is True
        assert result.value is None
        assert result.error is None
        assert result.duration_ms >= 0
        assert result.memory_used_mb >= 0

    def test_execution_with_return_value(self):
        """Test execution returns correct value."""
        result = run_safe(return_string, timeout=5)

        assert result.success is True
        assert result.value == "test_result"
        assert result.error is None

    def test_execution_with_complex_return(self):
        """Test execution with complex return types."""
        result = run_safe(return_dict, timeout=5)

        assert result.success is True
        assert isinstance(result.value, dict)
        assert result.value["key"] == "value"
        assert result.value["number"] == 42

    def test_execution_with_none_return(self):
        """Test execution with None return value."""
        result = run_safe(return_none, timeout=5)

        assert result.success is True
        assert result.value is None


class TestErrorHandling:
    """Test error handling in isolated execution."""

    def test_exception_handling(self):
        """Test that exceptions are captured properly."""
        result = run_safe(raise_error, timeout=5)

        assert result.success is False
        assert result.value is None
        assert result.error is not None

    def test_zero_division_error(self):
        """Test handling of ZeroDivisionError."""
        result = run_safe(divide_by_zero, timeout=5)

        assert result.success is False
        assert result.value is None
        assert result.error is not None

    def test_type_error_handling(self):
        """Test handling of TypeError."""
        result = run_safe(type_error, timeout=5)

        assert result.success is False
        assert result.value is None
        assert result.error is not None

    def test_runtime_error_handling(self):
        """Test handling of RuntimeError."""
        result = run_safe(runtime_error, timeout=5)

        assert result.success is False
        assert result.value is None
        assert result.error is not None


class TestTimeoutProtection:
    """Test timeout protection functionality."""

    def test_timeout_enforcement(self):
        """Test that timeout is enforced."""
        start_time = time.time()
        result = run_safe(slow_function, timeout=1)
        elapsed = time.time() - start_time

        assert result.success is False
        assert elapsed < 3  # Should timeout well before function completes

    def test_fast_execution_no_timeout(self):
        """Test that fast functions don't timeout."""
        result = run_safe(fast_function, timeout=5)

        assert result.success is True
        assert result.value == "fast"

    def test_custom_timeout_value(self):
        """Test custom timeout values."""
        result = run_safe(medium_function, timeout=2)

        assert result.success is True
        assert result.value == "medium"


class TestMemoryManagement:
    """Test memory management and tracking."""

    def test_memory_tracking(self):
        """Test that memory usage is tracked."""
        result = run_safe(allocate_memory, timeout=5, memory_limit_mb=512)

        assert result.success is True
        assert result.memory_used_mb >= 0

    def test_small_memory_allocation(self):
        """Test small memory allocations."""
        result = run_safe(small_allocation, timeout=5, memory_limit_mb=100)

        assert result.success is True
        assert result.value == 1000


class TestProcessIsolation:
    """Test process isolation functionality."""

    def test_isolated_execution(self):
        """Test that function runs in separate process."""
        current_pid = os.getpid()
        result = run_safe(get_pid, timeout=5)

        assert result.success is True
        assert result.value != current_pid  # Should be different process

    def test_global_state_isolation(self):
        """Test that global state changes don't affect parent."""
        original_value = GLOBAL_STATE["value"]
        result = run_safe(modify_global, timeout=5)

        assert result.success is True
        assert result.value == 42
        assert GLOBAL_STATE["value"] == original_value  # Parent state unchanged

    def test_exception_isolation(self):
        """Test that exceptions in child don't crash parent."""
        result = run_safe(crash, timeout=5)

        assert result.success is False
        # Parent process continues normally


class TestExecutionResult:
    """Test ExecutionResult dataclass."""

    def test_execution_result_creation(self):
        """Test creating ExecutionResult."""
        result = ExecutionResult(
            success=True, value=42, error=None, duration_ms=100.5, memory_used_mb=50.2
        )

        assert result.success is True
        assert result.value == 42
        assert result.error is None
        assert result.duration_ms == 100.5
        assert result.memory_used_mb == 50.2

    def test_execution_result_failure(self):
        """Test ExecutionResult for failures."""
        result = ExecutionResult(
            success=False,
            value=None,
            error="Test error",
            duration_ms=50.0,
            memory_used_mb=10.0,
        )

        assert result.success is False
        assert result.value is None
        assert result.error == "Test error"


class TestEdgeCases:
    """Test edge cases and unusual inputs."""

    def test_empty_function(self):
        """Test empty function execution."""
        result = run_safe(empty, timeout=5)

        assert result.success is True
        assert result.value is None

    def test_nested_function_calls(self):
        """Test nested function calls."""
        result = run_safe(nested_outer, timeout=5)

        assert result.success is True
        assert result.value == 42

    def test_recursive_function(self):
        """Test recursive function execution."""
        result = run_safe(factorial, timeout=5)

        assert result.success is True
        assert result.value == 120  # 5! = 120

    def test_very_short_timeout(self):
        """Test very short timeout still works."""
        result = run_safe(instant, timeout=1)

        assert result.success is True
        assert result.value == "instant"


class TestPerformanceMetrics:
    """Test performance metric tracking."""

    def test_duration_tracking(self):
        """Test that duration is tracked accurately."""
        result = run_safe(timed_function, timeout=5)

        assert result.success is True
        assert result.duration_ms >= 100  # Should take at least 100ms

    def test_duration_accuracy(self):
        """Test duration tracking accuracy."""
        result = run_safe(quick_function, timeout=5)

        assert result.success is True
        assert result.duration_ms >= 0
        assert result.duration_ms < 1000  # Should complete quickly


class TestConcurrentExecution:
    """Test concurrent execution scenarios."""

    def test_multiple_sequential_executions(self):
        """Test multiple sequential executions."""
        results = []
        for _ in range(3):
            result = run_safe(simple_func, timeout=5)
            results.append(result)

        # All executions should succeed
        assert all(r.success for r in results)
        assert len(results) == 3

    def test_independent_executions(self):
        """Test that executions are independent."""
        result1 = run_safe(func1, timeout=5)
        result2 = run_safe(func2, timeout=5)

        assert result1.success is True
        assert result2.success is True
        assert result1.value == "result1"
        assert result2.value == "result2"
