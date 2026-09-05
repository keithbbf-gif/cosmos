#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inventory documented/raised kinds vs kinds named in tests. Read-only."""
from __future__ import annotations

import re
from pathlib import Path

RAISE_RE = re.compile(
    r"""raise\s+\w+\(\s*["']([A-Z][A-Z0-9_]+)["']"""
)
KIND_ASSIGN_RE = re.compile(
    r"""kind\s*=\s*["']([A-Z][A-Z0-9_]+)["']"""
)
KIND_UPDATE_RE = re.compile(
    r"""kind=["']([A-Z][A-Z0-9_]+)["']"""
)
QUOTED_RE = re.compile(r"""["']([A-Z][A-Z0-9_]{2,})["']""")
DOC_KIND_RE = re.compile(
    r"""kind\s*(?:in|∈)\s*\{([^}]+)\}""", re.IGNORECASE
)


def kinds_in(text: str) -> tuple[set[str], set[str], set[str]]:
    raised = set(RAISE_RE.findall(text))
    assigned = set(KIND_ASSIGN_RE.findall(text)) | set(KIND_UPDATE_RE.findall(text))
    documented = set()
    for block in DOC_KIND_RE.findall(text):
        documented |= set(re.findall(r"[A-Z][A-Z0-9_]+", block))
    return documented, raised, assigned


def named_in_tests(tests) -> set[str]:
    named: set[str] = set()
    for t in tests:
        named |= set(QUOTED_RE.findall(t.read_text(encoding="utf-8", errors="replace")))
    return named


def scan(mods, tests, label: str) -> None:
    named = named_in_tests(tests)
    print(f"=== {label} ===")
    for p in sorted(mods, key=lambda x: x.name):
        text = p.read_text(encoding="utf-8", errors="replace")
        documented, raised, assigned = kinds_in(text)
        live = raised | assigned
        untested_raised = sorted(k for k in raised if k not in named)
        untested_assigned = sorted(k for k in assigned if k not in named)
        untested_doc = sorted(k for k in documented if k not in named)
        if not (live or documented):
            continue
        print(f"{p.name}")
        print(f"  documented: {sorted(documented)}")
        print(f"  raised:     {sorted(raised)}")
        print(f"  assigned:   {sorted(assigned)}")
        if untested_raised:
            print(f"  UNTESTED RAISES: {untested_raised}")
        if untested_assigned:
            print(f"  UNTESTED ASSIGN: {untested_assigned}")
        if untested_doc:
            print(f"  UNTESTED DOC:    {untested_doc}")
        print()


def main() -> int:
    backup = Path(__file__).resolve().parent.parent / "backup"
    probe = Path(__file__).resolve().parent
    mods_b = list(backup.glob("cosmos_*.py"))
    tests_b = list(backup.glob("test_*.py"))
    mods_p = [
        p for p in probe.glob("*.py")
        if not p.name.startswith("test_")
        and not p.name.startswith("_")
        and p.name != Path(__file__).name
    ]
    tests_p = list(probe.glob("test_*.py"))
    scan(mods_b, tests_b, "BACKUP")
    scan(mods_p, tests_p, "PROBE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
