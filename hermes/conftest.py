"""Put the proposal tree and each feature folder on sys.path."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

_PROPOSALS = _ROOT / "proposals"
if _PROPOSALS.is_dir():
    for _child in sorted(_PROPOSALS.iterdir()):
        if _child.is_dir() and str(_child) not in sys.path:
            sys.path.insert(0, str(_child))
