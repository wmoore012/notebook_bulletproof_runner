from __future__ import annotations

import multiprocessing as mp
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional


@dataclass
class ExecutionResult:
    success: bool
    value: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: int = 0
    memory_used_mb: float = 0


def _target(
    fn: Callable[[], Any],
    q: mp.Queue[tuple[str, Optional[Any], Optional[str]]],
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
                if current_limit == resource.RLIM_INFINITY or memory_limit_bytes < current_limit:
                    resource.setrlimit(resource.RLIMIT_AS, (memory_limit_bytes, memory_limit_bytes))
        except (ImportError, OSError, ValueError):
            # Memory limits not supported on this system (e.g., Windows) or invalid limit
            pass

        res = fn()
        q.put(("success", res, None))
    except MemoryError:
        q.put(("error", None, f"Memory limit exceeded ({memory_limit_mb}MB)"))
    except Exception as e:  # noqa: BLE001
        q.put(("error", None, str(e)))


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
        ExecutionResult with success status, value/error, and performance metrics
    """
    start = time.time()
    q: mp.Queue[tuple[str, Optional[Any], Optional[str]]] = mp.Queue()
    p = mp.Process(target=_target, args=(fn, q, memory_limit_mb))

    # Track memory usage
    try:
        import psutil

        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    except ImportError:
        initial_memory = 0.0

    p.start()

    # Monitor memory usage during execution (simplified)
    peak_memory = initial_memory
    try:
        import psutil

        # Check memory a few times during execution instead of continuous monitoring
        for _ in range(min(10, int(timeout * 10))):  # Check up to 10 times or every 0.1s
            if not p.is_alive():
                break
            try:
                proc_info = psutil.Process(p.pid)
                current_memory = proc_info.memory_info().rss / 1024 / 1024  # MB
                peak_memory = max(peak_memory, current_memory)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break
            time.sleep(0.1)  # Check every 100ms
    except ImportError:
        pass

    p.join(timeout=timeout)
    duration_ms = int((time.time() - start) * 1000)
    memory_used_mb = max(0.0, peak_memory - initial_memory)

    if p.is_alive():
        p.terminate()
        p.join()
        return ExecutionResult(
            success=False,
            error=f"Timeout after {timeout}s",
            duration_ms=duration_ms,
            memory_used_mb=memory_used_mb,
        )

    try:
        status, result, err = q.get_nowait()
    except Exception:
        status, result, err = ("error", None, "no result returned")

    return ExecutionResult(
        success=(status == "success"),
        value=result if status == "success" else None,
        error=err if status != "success" else None,
        duration_ms=duration_ms,
        memory_used_mb=memory_used_mb,
    )
