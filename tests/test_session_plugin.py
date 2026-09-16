#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Drive the session-plugin node suite from the Python harness.

The plugin is TypeScript because OpenWork plugins are TypeScript. Node runs it
by stripping types (no tsconfig, no bundler, no node_modules), so this wrapper
is a shell-out, not a second implementation.

A missing or too-old node is UNMEASURED and exits 2 - a refusal, never a green
pass for a suite that did not run.

    py -3.14 tests/test_session_plugin.py
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SUITE = REPO / "builds" / "session-plugin" / "test" / "test_session_plugin.ts"
MIN_NODE = (22, 6)  # --experimental-strip-types landed in 22.6


def _node_version(exe: str) -> tuple[int, ...] | None:
    try:
        out = subprocess.run([exe, "--version"], capture_output=True, text=True,
                             timeout=30, check=True).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
    try:
        return tuple(int(p) for p in out.lstrip("v").split(".")[:3])
    except ValueError:
        return None


def main() -> int:
    if not SUITE.is_file():
        print("FAIL suite missing", SUITE)
        return 1
    exe = shutil.which("node")
    if exe is None:
        print("UNMEASURED NODE_ABSENT node is not on PATH - the plugin suite did not run")
        return 2
    ver = _node_version(exe)
    if ver is None or ver < MIN_NODE:
        print(f"UNMEASURED NODE_TOO_OLD {ver} < {MIN_NODE} - no --experimental-strip-types")
        return 2
    proc = subprocess.run(
        [exe, "--experimental-strip-types", str(SUITE)],
        capture_output=True, text=True, cwd=str(REPO), timeout=300)
    sys.stdout.write(proc.stdout)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
