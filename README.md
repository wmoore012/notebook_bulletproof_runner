# icat-notebook-runner

[![CI](https://img.shields.io/github/actions/workflow/status/wmoore012/notebook_bulletproof_runner/ci.yml?branch=main)](https://github.com/wmoore012/notebook_bulletproof_runner/actions)
[![PyPI](https://img.shields.io/pypi/v/icat-notebook-runner)](https://pypi.org/project/icat-notebook-runner/)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**Process-isolated, timeout-protected execution for untrusted code. Safely run user-generated functions, notebook cells, or arbitrary callables without risking your main application.**

---

## 🎯 Vision

Running untrusted code is inherently risky. This module provides **bulletproof isolation** that lets you execute user functions, notebook cells, or third-party code safely with automatic timeouts, memory limits, and process isolation.

**Perfect for:**
- Jupyter notebook servers with user code execution
- Code evaluation platforms (online IDEs, coding challenges)
- Plugin systems requiring safe execution
- Data science workflows with user-defined functions
- Educational platforms with student code execution

---

## 🚀 Quick Start

```bash
pip install icat-notebook-runner
```

```python
from icat_notebook_runner import run_safe, ExecutionResult

# Safely execute a user function
def user_function():
    return 2 + 2

result: ExecutionResult = run_safe(
    user_function, 
    timeout=5  # 5 second timeout
)

print(f"Success: {result.success}")  # True
print(f"Result: {result.value}")  # 4
print(f"Time: {result.duration_ms}ms")  # ~1
```

---

## 🛡️ Security Features

### Process Isolation
```python
# Each execution runs in a separate process
def malicious_function():
    import os
    os.system("rm -rf /")  # This won't affect your main process!
    return "evil"

result = run_safe(malicious_function, timeout=1)
print(result.success)  # False - process killed safely
```

### Automatic Timeout Protection
```python
def slow_function():
    import time
    time.sleep(10)  # This will timeout
    return "done"

result = run_safe(slow_function, timeout=2)
print(result.success)  # False
print(result.error)  # "Timeout after 2s"
```

### Memory and Resource Control
```python
def memory_hog():
    return [0] * 1000000000  # Large memory allocation

result = run_safe(memory_hog, timeout=5)
# Process will be killed if memory usage exceeds limits
```

---

## 📊 Usage Examples

### Basic Safe Execution
```python
from icat_notebook_runner import run_safe

# Simple function execution
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

result = run_safe(
    lambda: calculate_fibonacci(10),
    timeout=10
)

if result.success:
    print(f"Fibonacci(10) = {result.value}")
else:
    print(f"Error: {result.error}")
```

### Notebook Cell Execution
```python
# Simulate Jupyter notebook cell execution
def execute_notebook_cell(cell_code: str):
    # Create a function from the cell code
    exec_globals = {}
    exec(cell_code, exec_globals)
    
    # Execute in isolated process
    result = run_safe(
        lambda: exec_globals.get('result', None),
        timeout=30
    )
    
    return result

# Example usage
cell_code = """
import pandas as pd
import numpy as np

data = pd.DataFrame({
    'x': np.random.randn(1000),
    'y': np.random.randn(1000)
})

result = data.corr()
"""

result = execute_notebook_cell(cell_code)
```

### Educational Platform Integration
```python
def grade_student_code(student_code: str, test_cases: list):
    results = []
    
    for test_case in test_cases:
        # Execute student code with test input
        def run_test():
            exec(student_code)
            return locals().get('function_name')(test_case['input'])
        
        result = run_safe(run_test, timeout=5)
        
        if result.success and result.value == test_case['expected']:
            results.append(True)
        else:
            results.append(False)
    
    return results

# Example
student_code = """
def add_numbers(a, b):
    return a + b
"""

test_cases = [
    {'input': (1, 2), 'expected': 3},
    {'input': (-1, 1), 'expected': 0}
]

grades = grade_student_code(student_code, test_cases)
print(f"Score: {sum(grades)}/{len(grades)}")
```

### Plugin System Safety
```python
class SafePluginRunner:
    def __init__(self):
        self.plugins = {}
    
    def register_plugin(self, name: str, plugin_function):
        self.plugins[name] = plugin_function
    
    def execute_plugin(self, name: str, *args, **kwargs):
        if name not in self.plugins:
            raise ValueError(f"Plugin '{name}' not found")
        
        def run_plugin():
            return self.plugins[name](*args, **kwargs)
        
        result = run_safe(run_plugin, timeout=30)
        
        if not result.success:
            raise RuntimeError(f"Plugin execution failed: {result.error}")
        
        return result.value

# Usage
runner = SafePluginRunner()

def user_plugin(data):
    return sum(data) * 2

runner.register_plugin("sum_doubled", user_plugin)
result = runner.execute_plugin("sum_doubled", [1, 2, 3, 4])
print(result)  # 20
```

---

## 🔧 Features

- **Process Isolation**: Each execution runs in separate process
- **Automatic Timeouts**: Configurable execution time limits
- **Memory Protection**: Built-in memory usage monitoring
- **Error Handling**: Graceful failure with detailed error messages
- **Performance Metrics**: Execution time tracking
- **Type Safe**: Full mypy support with strict typing
- **Cross-Platform**: Works on Linux, macOS, and Windows

---

## 🛠️ Installation

```bash
# From PyPI
pip install icat-notebook-runner

# From source
git clone https://github.com/wmoore012/notebook_bulletproof_runner.git
cd notebook_bulletproof_runner
pip install -e .
```

**Requirements:**
- Python 3.8+
- No external dependencies (uses standard library only)

---

## 🤝 Contributing

We welcome contributions! This module follows the **OSS bricks** philosophy:

- **Security First**: All changes must maintain or improve isolation
- **TDD Approach**: Write tests, then implementation
- **Zero Breaking Changes**: Maintain backward compatibility
- **Clear Documentation**: All APIs must be well-documented

**Quick Start for Contributors:**
```bash
git clone https://github.com/wmoore012/notebook_bulletproof_runner.git
cd notebook_bulletproof_runner
poetry install
poetry run pytest  # Run tests
poetry run ruff check  # Lint
poetry run mypy  # Type check
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 📈 Roadmap

- [ ] **Resource limits** (CPU usage, file I/O restrictions)
- [ ] **Network isolation** (prevent network access)
- [ ] **Sandboxed filesystem** (temporary, isolated file access)
- [ ] **Docker container support** (additional isolation layer)
- [ ] **Jupyter kernel integration** (direct notebook support)

---

## 📄 License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built as part of the iCatalog ecosystem - a collection of production-tested, open-source data tools designed for reliability and maintainability.
