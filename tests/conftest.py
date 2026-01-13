"""
Pytest configuration that ensures the package imports resolve when running the
test suite without installing the distribution first.
"""

from __future__ import annotations

import sys
from pathlib import Path


def _add_src_to_path() -> None:
    project_root = Path(__file__).resolve().parents[1]
    src_dir = project_root / "src"
    src_str = str(src_dir)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)


_add_src_to_path()
