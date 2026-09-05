#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build patched copies of the two out-of-fence suites in builds/health/ so the
PROPOSED edits can be PROVEN to work without touching tests/.

tests/ belongs to another holder; per AGENT_BOUNDARIES this agent proposes and
does not write there. This script materialises the proposal as runnable code.

    py -3.14 builds\\health\\make_patched_tests.py
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
T = REPO / "tests"
B = REPO / "builds" / "health"

OLD_SELF = 'sys.path.insert(0, str(Path(__file__).resolve().parent))'
OLD_COS = 'sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))'
NEW_PATHS = 'sys.path.insert(0, r"%s")\nsys.path.insert(0, r"%s")' % (
    T, REPO / "cosmos")


def repath(src: str) -> str:
    """Copies live in builds/health/, so the suites' relative sys.path inserts
    would resolve to builds/cosmos. Pin them to the repo instead."""
    src = src.replace(OLD_SELF, NEW_PATHS, 1)
    src = src.replace(OLD_COS, "", 1)
    return src


def patch(name: str, edits: list[tuple[str, str]]) -> None:
    src = (T / name).read_text(encoding="utf-8")
    out = src
    for old, new in edits:
        if old not in out:
            raise SystemExit("ANCHOR MISSING in %s: %r" % (name, old[:70]))
        out = out.replace(old, new, 1)
    out = repath(out)
    dst = B / ("patched_" + name)
    dst.write_text(out, encoding="utf-8")
    print("wrote %s  (%d edits)" % (dst.name, len(edits)))


# ---- PROPOSAL 1: tests/test_core_supervisor.py -----------------------------
# ONE line. Section 1 means "OFF is inert"; it relied on OFF being the DEFAULT.
# Saying supervise=False explicitly restores the section's meaning AND removes
# the core_serve.json pollution that cascaded into 7 later assertions.
patch("test_core_supervisor.py", [
    ("r = hc.poll_once(str(root))",
     "r = hc.poll_once(str(root), supervise=False)"),
])

# ---- PROPOSAL 2: tests/test_health_clock_optin.py --------------------------
# This suite's premise ("opt-in") is what the fix inverts. The inertness checks
# stay valuable -- they just have to ASK for OFF now instead of assuming it.
patch("test_health_clock_optin.py", [
    ('rc, out = run_cli("--root", str(off), "--once")',
     'rc, out = run_cli("--root", str(off), "--once", "--no-supervise")'),
    ('rc2, out2 = run_cli("--root", str(off), "--once")',
     'rc2, out2 = run_cli("--root", str(off), "--once", "--no-supervise")'),
    ('and "Default OFF" in help_out',
     'and "--no-supervise" in help_out and "DEFAULT ON" in help_out'),
    ('check(f"{name}(supervise=) defaults to False",\n'
     '              lambda s=sig: s.parameters["supervise"].default is False)',
     'check(f"{name}(supervise=) defaults to True",\n'
     '              lambda s=sig: s.parameters["supervise"].default is True)'),
])
print("\nNow run:")
print("  py -3.14 builds/health/patched_test_core_supervisor.py")
print("  py -3.14 builds/health/patched_test_health_clock_optin.py")
