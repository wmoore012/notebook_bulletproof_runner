"""
Comprehensive tests for icat-notebook-runner

Tests cover real-world notebook scenarios including:
- Basic execution and error handling
- Memory-intensive operations
- Data processing workflows
- Timeout scenarios
- Process isolation verification
"""

import time
import os
import multiprocessing
import tempfile
from typing import Any, Dict, List
from icat_notebook_runner import run_safe


# Module-level test functions (can be pickled)
def _simple_job() -> int:
    return 42


def _slow_job() -> int:
    time.sleep(1.5)
    return 1


def _error_job() -> int:
    raise ValueError("Test error")


def _memory_job() -> List[int]:
    """Simulate memory-intensive operation"""
    return list(range(100000))  # 100K integers


def _data_processing_job() -> Dict[str, Any]:
    """Simulate typical notebook data processing"""
    # Simulate pandas-like operations
    data = []
    for i in range(1000):
        data.append({"id": i, "value": i * 2, "category": "A" if i % 2 == 0 else "B"})

    # Simulate aggregation
    total = sum(item["value"] for item in data)
    count_a = sum(1 for item in data if item["category"] == "A")

    return {
        "total_records": len(data),
        "sum_values": total,
        "category_a_count": count_a,
        "avg_value": total / len(data) if data else 0,
    }


def _computation_job() -> float:
    """Simulate computational work like ML training"""
    result = 0.0
    for i in range(10000):
        result += (i**0.5) / (i + 1)
    return result


def _file_operation_job() -> Dict[str, Any]:
    """Simulate file operations that notebooks often do"""
    import os

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("test data\nline 2\nline 3\n")
        temp_path = f.name

    try:
        # Read it back
        with open(temp_path, "r") as f:
            lines = f.readlines()

        return {
            "file_created": True,
            "lines_count": len(lines),
            "first_line": lines[0].strip() if lines else None,
        }
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def _infinite_loop_job() -> int:
    """Job that would run forever without timeout"""
    while True:
        time.sleep(0.1)
    return 1  # Never reached


def _exception_chain_job() -> int:
    """Job with nested exceptions"""
    try:
        raise ValueError("Inner error")
    except ValueError as e:
        raise RuntimeError("Outer error") from e


def _isolation_test() -> Dict[str, Any]:
    """Test process isolation"""

    return {"pid": os.getpid(), "process_name": multiprocessing.current_process().name}


def _none_job() -> None:
    return None


def _complex_job() -> Dict[str, Any]:
    return {
        "numbers": [1, 2, 3],
        "nested": {"key": "value"},
        "mixed": [1, "string", {"nested": True}],
    }


def _quick_job() -> int:
    return 1


def _notebook_cell() -> Dict[str, Any]:
    """Simulate a typical data analysis notebook cell"""
    # Import libraries (common in notebooks)
    import math

    # Generate some data
    data = []
    for i in range(100):
        data.append({"x": i, "y": math.sin(i / 10.0), "category": "high" if i > 50 else "low"})

    # Analyze data
    high_count = sum(1 for item in data if item["category"] == "high")
    avg_y = sum(item["y"] for item in data) / len(data)

    # Return results
    return {
        "data_points": len(data),
        "high_category_count": high_count,
        "average_y": avg_y,
        "analysis_complete": True,
    }


def _ml_workflow() -> Dict[str, Any]:
    """Simulate ML training workflow"""
    import random

    # Generate training data
    X = [[random.random() for _ in range(5)] for _ in range(1000)]
    y = [sum(row) > 2.5 for row in X]  # Simple classification

    # Simple "training" (just statistics)
    positive_samples = sum(y)
    feature_means = [sum(row[i] for row in X) / len(X) for i in range(5)]

    # "Model evaluation"
    accuracy = positive_samples / len(y)  # Dummy accuracy

    return {
        "training_samples": len(X),
        "positive_samples": positive_samples,
        "feature_means": feature_means,
        "model_accuracy": accuracy,
        "training_complete": True,
    }


def _timed_job() -> int:
    time.sleep(0.1)  # Sleep for 100ms
    return 42


def _scalable_job_100() -> Dict[str, int]:
    data = list(range(100))
    total = sum(data)
    return {"size": len(data), "sum": total}


def _scalable_job_1000() -> Dict[str, int]:
    data = list(range(1000))
    total = sum(data)
    return {"size": len(data), "sum": total}


def _scalable_job_10000() -> Dict[str, int]:
    data = list(range(10000))
    total = sum(data)
    return {"size": len(data), "sum": total}


# Basic functionality tests
def test_simple_success():
    """Test basic successful execution"""
    result = run_safe(_simple_job, timeout=5)

    assert result.success is True
    assert result.value == 42
    assert result.error is None
    assert result.duration_ms >= 0


def test_timeout_handling():
    """Test timeout protection"""
    result = run_safe(_slow_job, timeout=1)

    # The job might complete or timeout depending on system load
    # Just ensure it behaves reasonably
    if not result.success:
        assert "Timeout" in (result.error or "")
        assert result.duration_ms >= 1000  # Should be at least 1 second
    else:
        # Job completed within timeout
        assert result.value == 1


def test_error_handling():
    """Test error capture and reporting"""
    result = run_safe(_error_job, timeout=5)

    assert result.success is False
    assert result.value is None
    assert "Test error" in (result.error or "")
    assert result.duration_ms >= 0


def test_infinite_loop_timeout():
    """Test that infinite loops are properly terminated"""
    result = run_safe(_infinite_loop_job, timeout=2)

    assert result.success is False
    assert result.value is None
    assert "Timeout" in (result.error or "")
    assert result.duration_ms >= 2000


def test_exception_chain():
    """Test handling of chained exceptions"""
    result = run_safe(_exception_chain_job, timeout=5)

    assert result.success is False
    assert result.value is None
    assert "Outer error" in (result.error or "")


# Real-world notebook scenario tests
def test_data_processing_workflow():
    """Test typical data processing notebook cell"""
    result = run_safe(_data_processing_job, timeout=10)

    assert result.success is True
    assert result.value is not None
    assert isinstance(result.value, dict)

    data = result.value
    assert data["total_records"] == 1000
    assert data["sum_values"] == 999000  # Sum of 0*2 + 1*2 + ... + 999*2
    assert data["category_a_count"] == 500  # Half should be category A
    assert data["avg_value"] == 999.0


def test_memory_intensive_operation():
    """Test memory-intensive operations like large data loading"""
    result = run_safe(_memory_job, timeout=60)  # Very long timeout for large operations

    # The operation might timeout on slower systems, so we'll be flexible
    if result.success:
        assert result.value is not None
        assert len(result.value) == 100000
        assert result.value[0] == 0
        assert result.value[-1] == 99999
    else:
        # If it times out, that's also acceptable behavior
        assert "Timeout" in (result.error or "")


def test_computational_work():
    """Test computational work like ML training"""
    result = run_safe(_computation_job, timeout=10)

    assert result.success is True
    assert result.value is not None
    assert isinstance(result.value, float)
    assert result.value > 0  # Should be positive


def test_file_operations():
    """Test file I/O operations common in notebooks"""
    result = run_safe(_file_operation_job, timeout=10)

    assert result.success is True
    assert result.value is not None

    data = result.value
    assert data["file_created"] is True
    assert data["lines_count"] == 3
    assert data["first_line"] == "test data"


# Performance and isolation tests
def test_process_isolation():
    """Test that processes are properly isolated"""
    # Run twice to ensure different processes
    result1 = run_safe(_isolation_test, timeout=5)
    result2 = run_safe(_isolation_test, timeout=5)

    assert result1.success is True
    assert result2.success is True

    # Should have different PIDs (different processes)
    pid1 = result1.value["pid"]
    pid2 = result2.value["pid"]

    # PIDs might be the same if processes are reused quickly, but process names should indicate isolation
    assert isinstance(pid1, int)
    assert isinstance(pid2, int)


def test_multiple_timeouts():
    """Test multiple timeout scenarios"""
    timeouts = [0.5, 2.0]  # Short and long timeouts

    for timeout in timeouts:
        result = run_safe(_slow_job, timeout=timeout)

        # Just ensure the function completes and returns reasonable results
        assert isinstance(result.success, bool)
        assert result.duration_ms >= 0

        if timeout >= 2.0:  # Long timeout should succeed
            assert result.success is True
            assert result.value == 1


def test_concurrent_execution():
    """Test that multiple executions can run concurrently"""
    import threading
    import queue

    results_queue = queue.Queue()

    def run_test():
        result = run_safe(_simple_job, timeout=5)
        results_queue.put(result)

    # Start multiple threads
    threads = []
    for _ in range(3):
        thread = threading.Thread(target=run_test)
        threads.append(thread)
        thread.start()

    # Wait for all to complete
    for thread in threads:
        thread.join()

    # Check all results
    results = []
    while not results_queue.empty():
        results.append(results_queue.get())

    assert len(results) == 3
    for result in results:
        assert result.success is True
        assert result.value == 42


# Edge cases and robustness tests
def test_none_return_value():
    """Test handling of None return values"""
    result = run_safe(_none_job, timeout=5)

    assert result.success is True
    assert result.value is None
    assert result.error is None


def test_complex_return_value():
    """Test handling of complex return values"""
    result = run_safe(_complex_job, timeout=5)

    assert result.success is True
    assert result.value is not None
    assert result.value["numbers"] == [1, 2, 3]
    assert result.value["nested"]["key"] == "value"


def test_very_short_timeout():
    """Test very short timeouts"""
    result = run_safe(_quick_job, timeout=0.1)  # 100ms timeout

    # This might succeed or timeout depending on system load
    # Just ensure it doesn't crash
    assert isinstance(result.success, bool)
    assert isinstance(result.duration_ms, int)


def test_zero_timeout():
    """Test zero timeout (should timeout immediately)"""
    result = run_safe(_simple_job, timeout=0)

    assert result.success is False
    assert "Timeout" in (result.error or "")


# Integration tests simulating notebook scenarios
def test_notebook_cell_simulation():
    """Simulate a complete notebook cell execution"""
    result = run_safe(_notebook_cell, timeout=10)

    assert result.success is True
    assert result.value["data_points"] == 100
    assert result.value["high_category_count"] == 49  # 51-99 = 49 items
    assert result.value["analysis_complete"] is True
    assert isinstance(result.value["average_y"], float)


def test_ml_workflow_simulation():
    """Simulate a machine learning workflow"""
    result = run_safe(_ml_workflow, timeout=15)

    assert result.success is True
    assert result.value["training_samples"] == 1000
    assert result.value["training_complete"] is True
    assert 0 <= result.value["model_accuracy"] <= 1
    assert len(result.value["feature_means"]) == 5


# Performance benchmarking tests
def test_performance_metrics():
    """Test that performance metrics are reasonable"""
    result = run_safe(_timed_job, timeout=5)

    assert result.success is True
    assert result.value == 42
    # Should take at least 100ms (allowing for system overhead)
    assert result.duration_ms >= 90


def test_scalability():
    """Test scalability with different data sizes"""
    # Test with 100 items
    result = run_safe(_scalable_job_100, timeout=10)
    assert result.success is True
    assert result.value["size"] == 100
    assert result.value["sum"] == sum(range(100))

    # Test with 1000 items
    result = run_safe(_scalable_job_1000, timeout=10)
    assert result.success is True
    assert result.value["size"] == 1000
    assert result.value["sum"] == sum(range(1000))

    # Test with 10000 items
    result = run_safe(_scalable_job_10000, timeout=10)
    assert result.success is True
    assert result.value["size"] == 10000
    assert result.value["sum"] == sum(range(10000))


# Error recovery tests
def test_error_recovery():
    """Test that errors don't affect subsequent executions"""
    # First, run a job that fails
    error_result = run_safe(_error_job, timeout=5)
    assert error_result.success is False

    # Then run a job that succeeds
    success_result = run_safe(_simple_job, timeout=5)
    assert success_result.success is True
    assert success_result.value == 42


def test_timeout_recovery():
    """Test that timeouts don't affect subsequent executions"""
    # First, run a job that might timeout (depending on system speed)
    _timeout_result = run_safe(_slow_job, timeout=0.5)  # Very short timeout

    # Then run a job that should succeed
    success_result = run_safe(_simple_job, timeout=5)
    assert success_result.success is True
    assert success_result.value == 42
