#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hermetic clone-detect. Never opens live opencode.db."""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "builds" / "session-tools"))
from clone import refuse_duplicate, shared_tail  # noqa: E402

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, str(e)))


def test_same_800():
    block = "X" * 800
    return shared_tail("aa" + block, "bb" + block, 800) is True


def test_799_not():
    a = "Y" * 799
    return shared_tail(a + "A", a + "B", 800) is False


def test_empty():
    return shared_tail("", "abc", 800) is False and shared_tail("a", "", 800) is False


def test_short():
    return shared_tail("short", "short", 800) is False


def test_n_zero():
    return shared_tail("abc", "abc", 0) is False


def test_refuse_duplicate():
    block = "Z" * 800
    try:
        refuse_duplicate("left:" + block, "right:" + block)
    except Exception as e:  # noqa: BLE001
        return getattr(e, "kind", None) == "CLONE"
    return False


if __name__ == "__main__":
    check("800 identical tail", test_same_800)
    check("799 not clone", test_799_not)
    check("empty", test_empty)
    check("short < n", test_short)
    check("n=0", test_n_zero)
    check("duplicate mouth refuses with CLONE", test_refuse_duplicate)
    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for l, ok, e in RESULTS:
        print(("PASS" if ok else "FAIL"), l, e)
    print(f"{sum(1 for _, ok, _ in RESULTS if ok)}/{len(RESULTS)}")
    raise SystemExit(1 if bad else 0)
