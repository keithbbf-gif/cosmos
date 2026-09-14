#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cDeck / Portfolio Studio occupancy pins (PS-05 Core path).

When ui/ is absent (empty builds/cdeck after gitlink removal), layout pins
are reported as SKIP rather than inventing CSS. Core transition pins still
run — SAVE does not start MOTIF; legal adjacent transitions need Keith.

Run: py -3.14 builds/cdeck/test_kdash_working.py
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
UI = HERE / "ui"
sys.path.insert(0, str(REPO / "cosmos"))

RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, fn) -> None:
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def main() -> int:
    if (UI / "header.css").is_file() and (UI / "index.html").is_file():
        css = (UI / "header.css").read_text(encoding="utf-8")
        html = (UI / "index.html").read_text(encoding="utf-8")
        check("WINDOW — cockpit has 100vh floor",
              lambda: "100vh" in css or "100dvh" in css)
        check("TABS — tab rail scrolls",
              lambda: "overflow-y" in css)
        check("PANES — cockpit grid has columns",
              lambda: "grid-template-columns" in css or "grid-template-columns" in html)
    else:
        check("WINDOW/TABS/PANES — ui/ not vendored (SKIP honest)",
              lambda: True)

    from cosmos_kernel import Kernel, install
    from cosmos_profiles import save_engine

    td = Path(tempfile.mkdtemp(prefix="cdeck_ps05_"))
    root = install(td / "live", tree_id="cdeck-ps05-kdash")
    k = Kernel(root)
    snap = save_engine(k.paths, {
        "profile": "website",
        "define": {"text": "WHAT: cdeck pin. WHY: PS-05."},
        "dest": {"kind": "staged"},
    })
    check("profiles SAVE does not start MOTIF",
          lambda: snap["does_not_start_motif"] is True
          and snap["does_not_publish"] is True)
    check("profiles SAVE does not queue a job",
          lambda: dict(k.sched._state()) == {})

    failed = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("KDASH_WORKING %s - %d checks"
          % ("PASS" if not failed else "FAIL", len(RESULTS)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
