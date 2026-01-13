# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Perday CatalogLAB™

"""
Helper functions for testing process-isolated-runner.

These functions must be at module level to be picklable by multiprocessing.
"""

import os
import time


# Basic execution helpers
def simple_func():
    """Simple function that returns None."""
    pass


def return_string():
    """Function that returns a string."""
    return "test_result"


def return_dict():
    """Function that returns a dictionary."""
    return {"key": "value", "number": 42}


def return_none():
    """Function that explicitly returns None."""
    return None


# Error handling helpers
def raise_error():
    """Function that raises a ValueError."""
    raise ValueError("Test error message")


def divide_by_zero():
    """Function that raises ZeroDivisionError."""
    return 1 / 0


def type_error():
    """Function that raises TypeError."""
    return "string" + 123


def runtime_error():
    """Function that raises RuntimeError."""
    raise RuntimeError("Runtime error occurred")


# Timeout helpers
def slow_function():
    """Function that sleeps for 10 seconds."""
    time.sleep(10)
    return "completed"


def fast_function():
    """Function that completes quickly."""
    return "fast"


def medium_function():
    """Function that sleeps for 1 second."""
    time.sleep(1)
    return "medium"


# Memory helpers
def allocate_memory():
    """Function that allocates some memory."""
    data = [0] * (1024 * 1024)  # Allocate ~8MB
    return len(data)


def small_allocation():
    """Function that allocates small amount of memory."""
    data = [0] * 1000
    return len(data)


# Process isolation helpers
def get_pid():
    """Function that returns the process ID."""
    return os.getpid()


GLOBAL_STATE = {"value": 0}


def modify_global():
    """Function that modifies global state."""
    GLOBAL_STATE["value"] = 42
    return GLOBAL_STATE["value"]


def crash():
    """Function that raises an exception."""
    raise Exception("Intentional crash")


# Edge case helpers
def empty():
    """Empty function."""
    pass


def nested_outer():
    """Outer function for nested calls."""

    def inner():
        return 42

    return inner()


def factorial(n=5):
    """Recursive factorial function."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)


def instant():
    """Function that returns immediately."""
    return "instant"


# Performance helpers
def timed_function():
    """Function that sleeps for 0.1 seconds."""
    time.sleep(0.1)
    return "timed"


def quick_function():
    """Function that completes very quickly."""
    return sum(range(100))


# Concurrent execution helpers
def counter_func(n):
    """Function that returns its input."""
    return n


def func1():
    """First test function."""
    return "result1"


def func2():
    """Second test function."""
    return "result2"
