#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compatibility shim. Body lives in tools/_fail_f39_critique_against_old.py — re-export / runpy, not a copy."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
_BODY = _REPO / "tools" / Path(__file__).name
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

if __name__ == "__main__":
    raise SystemExit(runpy.run_path(str(_BODY), run_name="__main__"))

# In-tree imports (e.g. cosmos/test_rails_wired.py → _bite_check_f24_f25).
_ns = runpy.run_path(str(_BODY), run_name=__name__)
globals().update({k: v for k, v in _ns.items() if k not in {"__name__", "__file__", "__cached__"}})
