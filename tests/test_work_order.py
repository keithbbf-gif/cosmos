#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: typed work-order schema + runner. Isolated from the live tree.

Proves: Family|Clade|Version routing, WRITE-PRIVATE cwd, DONE != COMPLETED,
CHECKED stamps (GitHub/Cursor/GitLab) on DONE, COW accept_order is the only
COMPLETED transition, PAUSE idle. Does not invoke grok/claude/codex/gemini
and does not write the live tree. Anthropic stays OFF.
"""
from __future__ import annotations

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_root = _here.parent
sys.path.insert(0, str(_root))
sys.path.insert(0, str(_root / "cosmos"))
# Off-tree bundle: live cosmos package (paths/clock) sits at repo/cosmos.
_repo_cosmos = _root.parent.parent / "cosmos"
if _repo_cosmos.is_dir():
    sys.path.append(str(_repo_cosmos))

from cosmos_work_order_run import _selftest  # noqa: E402


def test_work_order():
    assert _selftest() == 0


if __name__ == "__main__":
    sys.exit(_selftest())
