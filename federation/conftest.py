"""Path setup for proposal tests.

`tmp_path` is not used. On this machine the pytest temp root under
the user profile is not writable, so tests ask for the `scratch` fixture.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

_PROPOSALS = _ROOT / "proposals"
if _PROPOSALS.is_dir():
    for _child in sorted(_PROPOSALS.iterdir()):
        if _child.is_dir() and str(_child) not in sys.path:
            sys.path.insert(0, str(_child))


@pytest.fixture
def scratch() -> Iterator[Path]:
    """A real empty directory the test may write. Removed afterwards."""
    directory = Path(tempfile.mkdtemp(prefix="fed-"))
    try:
        yield directory
    finally:
        shutil.rmtree(directory, ignore_errors=True)
