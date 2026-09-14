#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Header-action feature pins (static ui/ contract; no live Core required).

Run:  py -3.14 builds/cdeck/test_deck_features.py
"""
from __future__ import annotations

import sys
from pathlib import Path

UI = Path(__file__).resolve().parent / "ui"
RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((label, bool(ok), str(detail)[:400]))


def _read(name: str) -> str:
    p = UI / name
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def main() -> int:
    index = _read("index.html")
    header = _read("header.js")

    check("index loads header.js before pane scripts", "header.js" in index)
    check("header exports apiGet/apiPost globals", "window.apiGet" in header and "window.apiPost" in header)
    check("no raw fetch() in model_rater.js", "fetch(" not in _read("model_rater.js"))
    check("RELOAD control kept", "btnReload" in index and "bindReload" in header)
    check("Core paths use /api/v1 prefix for header POSTs",
          header.count('"/api/v1/') >= 6)

    failed = [r for r in RESULTS if not r[1]]
    for label, ok, err in RESULTS:
        print(f"  {'OK  ' if ok else 'FAIL'}  {label}{('  ' + err) if err and not ok else ''}")
    print(f"result: {'ok' if not failed else 'FAIL'}  {len(RESULTS) - len(failed)}/{len(RESULTS)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
