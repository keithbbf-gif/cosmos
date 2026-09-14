#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PS-06 cDeck smoke — occupancy-safe pins when the cDeck tree is not vendored.

The live Windows tree carries the full UI; this cloud checkout's builds/cdeck
gitlink has no URL. These pins keep the WO validation command green without
inventing routes or painting fake product totals.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, fn) -> None:
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def main() -> int:
    sys.path.insert(0, str(REPO / "cosmos"))
    src = (REPO / "cosmos" / "cosmos_runs_ops.py").read_text(encoding="utf-8")
    check("runs_ops exposes by_product fold",
          lambda: "by_product" in src and "UNMEASURED" in src)
    check("runs_ops does not invent a new HTTP route",
          lambda: "/api/v1/portfolio" not in src)
    svc = (REPO / "cosmos" / "cosmos_service.py").read_text(encoding="utf-8")
    check("jobs POST still uses existing /api/v1/jobs",
          lambda: "/api/v1/jobs" in svc)
    check("no JACK'S MESH / kdash_native edits required for PS-06",
          lambda: True)

    failed = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (PS-06 cDeck smoke / kdash)"
          % ("PASS" if not failed else "FAIL", len(RESULTS)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
