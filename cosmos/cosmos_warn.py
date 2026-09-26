#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WARN BEFORE ERROR ×3. Humans are distracted. Then fail-closed.

Keith: see the danger → say something → repeat 3× → refuse.
"""
from __future__ import annotations

import sys
from typing import TextIO

WARN_LINE = "WARN BEFORE ERROR"


def warn3(kind: str, detail: str = "", *, stream: TextIO | None = None) -> str:
    """Print the warning three times, return the line. Always before refuse."""
    msg = "%s: %s" % (WARN_LINE, kind)
    if detail:
        msg = "%s — %s" % (msg, detail)
    out = stream or sys.stderr
    for _ in range(3):
        print(msg, file=out)
    return msg


def warn_if_two_heads(repo) -> int:
    """WARN ×3 if origin/main..HEAD is not empty. Does not refuse serve.

    Claiming synced is cosmos_head_gate.head_gate. Non-zero or unmeasured
    refuses. This fold stays warn-only so a boot can still come up.
    """
    import subprocess
    from pathlib import Path
    root = Path(repo)
    if not (root / ".git").exists() and (root.parent / ".git").exists():
        root = root.parent
    try:
        n = int(subprocess.check_output(
            ["git", "rev-list", "--count", "origin/main..HEAD"],
            cwd=str(root), stderr=subprocess.DEVNULL, text=True).strip() or "0")
    except (OSError, subprocess.CalledProcessError, ValueError):
        return -1
    if n > 0:
        warn3("TWO_HEADS", "origin/main..HEAD has %d commits — do not join-commit; Gitur only" % n)
    return n


class WarnRefuse(Exception):
    def __init__(self, kind: str, detail: str = "") -> None:
        self.kind = kind
        self.detail = detail
        self.warned = warn3(kind, detail)
        super().__init__(self.warned)


def _selftest() -> None:
    import io
    buf = io.StringIO()
    line = warn3("GROK_EXE_SCAR", "grok --single", stream=buf)
    text = buf.getvalue()
    n = text.count(WARN_LINE)
    assert n == 3, n
    assert "GROK_EXE_SCAR" in line
    try:
        raise WarnRefuse("NO_CONTEXT", "concat · ")
    except WarnRefuse as e:
        assert e.kind == "NO_CONTEXT"
        assert WARN_LINE in str(e)
    n = warn_if_two_heads(".")
    assert isinstance(n, int)
    print("warn3 selftest 3/3 (printed ×3 + two-heads fold)")


if __name__ == "__main__":
    _selftest()
