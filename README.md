# Notebook Bulletproof Runner

[![CI](https://github.com/wmoore012/notebook_bulletproof_runner/actions/workflows/ci.yml/badge.svg)](https://github.com/wmoore012/notebook_bulletproof_runner/actions/workflows/ci.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/wmoore012/notebook_bulletproof_runner/blob/main/LICENSE)

> **Built for [Perday CatalogLAB](https://perdaycatalog.com)** - a live demo of a data story platform for music producers and songwriters.

Reliable Jupyter notebook execution for production pipelines.

**Repo:** https://github.com/wmoore012/notebook_bulletproof_runner
**What it does:** Runs notebooks headlessly with timeout protection, error capture, and artifact collection so your ETL notebooks don't fail silently at 3am.

## Why I Built It

Data pipelines often live in Jupyter notebooks. You can schedule them with cron or Airflow, but what happens when a notebook:
- Hangs forever on a bad API call?
- Throws an exception in cell 47 of 50?
- Runs out of memory and crashes the kernel?

You wake up to missing data and no logs.

I built `notebook_bulletproof_runner` to make notebook execution reliable for CatalogLAB's daily ETL. It captures errors, enforces timeouts, and saves outputs even when things go wrong.

## Key Features

- **Timeout enforcement** at notebook and cell level
- **Error capture** with full tracebacks and cell context
- **Output collection** for downstream processing
- **Parameterized execution** via papermill integration
- **Retry logic** with exponential backoff

## Installation

```bash
pip install notebook-bulletproof-runner
```

Or clone locally:

```bash
git clone https://github.com/wmoore012/notebook_bulletproof_runner.git
cd notebook_bulletproof_runner
pip install -e .
```

## Quick Start

```python
from notebook_bulletproof_runner import run_notebook

result = run_notebook(
    "daily_etl.ipynb",
    timeout_minutes=30,
    parameters={"date": "2026-01-23"},
    output_dir="./runs/"
)

if result.success:
    print(f"Completed in {result.duration_seconds}s")
else:
    print(f"Failed at cell {result.failed_cell}: {result.error}")
```

## CLI Usage

```bash
nbrun daily_etl.ipynb --timeout 30 --param date=2026-01-23
```

## Performance

| Metric | Value |
|--------|-------|
| Startup overhead | < 2 seconds |
| Memory efficiency | Streams cell outputs |
| Timeout precision | Within 1 second |

See [BENCHMARKS.md](BENCHMARKS.md) for detailed results.

## Documentation

- [API Documentation](docs/)
- [Examples](examples/)
- [Contributing Guide](CONTRIBUTING.md)
- [Security Policy](SECURITY.md)

## Professional Context

Built by **Wilton Moore** for Perday Labs. This module demonstrates:

- Production-grade notebook orchestration
- Defensive programming for unreliable environments
- Observability patterns for data pipelines

## Contact

Questions about notebook automation or collabs?
- LinkedIn: https://www.linkedin.com/in/wiltonmoore/
- GitHub: https://github.com/wmoore012

## License

MIT License. See [LICENSE](LICENSE) for details.
