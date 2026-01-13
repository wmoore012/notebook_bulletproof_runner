# SPDX - License - Identifier: MIT
# Copyright (c) 2025 Perday CatalogLAB™

from __future__ import annotations

import multiprocessing as mp
import time
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class ExecutionResult:
    success: bool
    value: Any | None = None
    error: str | None = None
    duration_ms: int = 0
    memory_used_mb: float = 0


def _target(
    fn: Callable[[], Any],
    q: mp.Queue[tuple[str, Any | None, str | None, int]],
    memory_limit_mb: int,
) -> None:
    try:
        # Set memory limit if supported (Unix systems)
        try:
            import resource

            # Convert MB to bytes
            memory_limit_bytes = memory_limit_mb * 1024 * 1024
            # Only set limit if it's reasonable (> 10MB) and less than current limit
            if memory_limit_bytes > 10 * 1024 * 1024:  # 10MB minimum
                current_limit = resource.getrlimit(resource.RLIMIT_AS)[0]
                if (
                    current_limit == resource.RLIM_INFINITY
                    or memory_limit_bytes < current_limit
                ):
                    resource.setrlimit(
                        resource.RLIMIT_AS, (memory_limit_bytes, memory_limit_bytes)
                    )
        except (ImportError, OSError, ValueError):
            # Memory limits not supported on this system (e.g., Windows) or invalid limit
            pass

        start = time.perf_counter()
        res = fn()
        duration_ms = int((time.perf_counter() - start) * 1000)
        q.put(("success", res, None, duration_ms))
    except MemoryError:
        q.put(("error", None, f"Memory limit exceeded ({memory_limit_mb}MB)", 0))
    except Exception as e:  # noqa: BLE001
        q.put(("error", None, str(e), 0))


def run_safe(
    fn: Callable[[], Any], timeout: int = 30, memory_limit_mb: int = 512
) -> ExecutionResult:
    """
    Run a callable in a separate process with timeout and memory limits.

    Args:
        fn: The function to execute safely
        timeout: Maximum execution time in seconds (default: 30)
        memory_limit_mb: Maximum memory usage in MB (default: 512)

    Returns:
        ExecutionResult with success status, value / error, and performance metrics
    """
    q: mp.Queue[tuple[str, Any | None, str | None, int]] = _CTX.Queue()
    p = _CTX.Process(target=_target, args=(fn, q, memory_limit_mb))

    try:
        import psutil as psutil_module

        parent_proc = psutil_module.Process()
        initial_memory = parent_proc.memory_info().rss / 1024 / 1024  # MB
        psutil_available = True
    except ImportError:  # pragma: no cover - psutil always available in CI
        psutil_available = False
        psutil_module = None
        initial_memory = 0.0

    p.start()
    start = time.time()

    peak_memory = initial_memory
    startup_grace = min(1.0, float(timeout))
    deadline = start + timeout + startup_grace
    check_interval = 0.05  # 50ms granularity keeps responsiveness high
    child_process = None

    while p.is_alive():
        if psutil_available and psutil_module is not None:
            try:
                if child_process is None:
                    child_process = psutil_module.Process(p.pid)
                mem_info = child_process.memory_info().rss / 1024 / 1024  # MB
                peak_memory = max(peak_memory, mem_info)
            except Exception:
                psutil_available = False

        remaining = deadline - time.time()
        if remaining <= 0:
            break
        time.sleep(min(check_interval, remaining))

    duration_ms = int((time.time() - start) * 1000)
    memory_used_mb = max(0.0, peak_memory - initial_memory)

    child_duration_ms: int | None = None

    if p.is_alive():
        p.terminate()
        p.join()
        status, result, err = ("error", None, f"Timeout after {timeout}s")
    else:
        p.join()
        try:
            status, result, err, child_duration_ms = q.get_nowait()
        except Exception:
            status, result, err = ("error", None, "no result returned")

    return ExecutionResult(
        success=(status == "success"),
        value=result if status == "success" else None,
        error=err if status != "success" else None,
        duration_ms=child_duration_ms if child_duration_ms is not None else duration_ms,
        memory_used_mb=memory_used_mb,
    )


if "fork" in mp.get_all_start_methods():
    _CTX = mp.get_context("fork")
else:  # pragma: no cover - Windows / fallback path
    _CTX = mp.get_context()
