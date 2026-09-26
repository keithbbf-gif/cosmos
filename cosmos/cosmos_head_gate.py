#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One head. origin/main..HEAD must be 0 or refuse synced.

warn_if_two_heads only warns. This gate refuses the claim. It does not
join-commit and it does not edit the kernel. Unmeasured is not synced.

    py -3.14 cosmos\\cosmos_head_gate.py --selftest
"""
from __future__ import annotations

import subprocess
from pathlib import Path

SCHEMA = "cosmos-head-gate/1"
AHEAD_REF = "origin/main..HEAD"


def _repo(repo) -> Path:
    root = Path(repo)
    if not (root / ".git").exists() and (root.parent / ".git").exists():
        root = root.parent
    return root


def measure_ahead(repo, *, run=None) -> int:
    """Count of commits on HEAD that origin/main does not have.

    -1 means the count was not measured. 0 is a real zero, not a guess.
    """
    root = _repo(repo)
    cmd = ["git", "rev-list", "--count", AHEAD_REF]
    try:
        if run is None:
            text = subprocess.check_output(
                cmd, cwd=str(root), stderr=subprocess.DEVNULL, text=True)
        else:
            text = run(cmd, root)
        return int(str(text).strip() or "0")
    except (OSError, subprocess.CalledProcessError, ValueError, TypeError):
        return -1


def head_gate(repo, *, run=None) -> dict:
    """Claim synced only when the count is 0. Else WARN ×3 and refuse."""
    from cosmos_warn import WarnRefuse

    n = measure_ahead(repo, run=run)
    if n < 0:
        raise WarnRefuse(
            "HEAD_UNMEASURED",
            "git rev-list --count %s failed — refuse synced" % AHEAD_REF)
    if n != 0:
        raise WarnRefuse(
            "NOT_SYNCED",
            "origin/main..HEAD has %d commits — refuse synced" % n)
    return {"schema": SCHEMA, "synced": True, "ahead": 0, "ref": AHEAD_REF}


def _selftest() -> int:
    import io

    from cosmos_warn import WarnRefuse

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, "%s: %s" % (type(e).__name__, e)))

    def run_zero(_cmd, _root):
        return "0\n"

    def run_ahead(_cmd, _root):
        return "37\n"

    def run_boom(_cmd, _root):
        raise OSError("git missing")

    zero = head_gate(".", run=run_zero)
    check("zero ahead is synced",
          lambda: zero["synced"] is True and zero["ahead"] == 0)

    kind = None
    detail = ""
    buf = io.StringIO()
    try:
        import cosmos_warn
        old = cosmos_warn.sys.stderr
        cosmos_warn.sys.stderr = buf
        try:
            head_gate(".", run=run_ahead)
        finally:
            cosmos_warn.sys.stderr = old
    except WarnRefuse as e:
        kind = e.kind
        detail = e.detail
    text = buf.getvalue()
    check("ahead refuses synced after WARN ×3",
          lambda: kind == "NOT_SYNCED" and "37" in detail
          and text.count("WARN BEFORE ERROR") == 3)

    miss = None
    try:
        head_gate(".", run=run_boom)
    except WarnRefuse as e:
        miss = e.kind
    check("unmeasured refuses synced", lambda: miss == "HEAD_UNMEASURED")
    check("measure_ahead failure is -1 not 0",
          lambda: measure_ahead(".", run=run_boom) == -1)

    bad = [(label, err) for label, ok, err in results if not ok]
    for label, ok, err in results:
        print(("  OK  " if ok else "  FAIL") + " " + label + (("  " + err) if err else ""))
    print("%d/%d passed" % (len(results) - len(bad), len(results)))
    return 1 if bad else 0


def main() -> int:
    import sys
    if "--selftest" in sys.argv:
        return _selftest()
    print("usage: py -3.14 cosmos\\cosmos_head_gate.py --selftest")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
