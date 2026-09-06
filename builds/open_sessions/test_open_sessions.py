#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hermetic pins for Open Sessions (first COSMOS product)."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "builds" / "cdeck"))
sys.path.insert(0, str(REPO / "cosmos"))

from cosmos_kernel import install  # noqa: E402
from cosmos_paths import CosmosPaths  # noqa: E402
from cosmos_recents_panel import emit_from_catalog, recents_path  # noqa: E402
import Open_sessions as osess  # noqa: E402

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, str(e)))


def _root_with_cat():
    td = Path(tempfile.mkdtemp(prefix="open_sessions_"))
    root = install(td / "live", tree_id="spike-open-sessions")
    cat = td / "COW_SESSION_CATALOG.json"
    trans = td / "ordered_transcripts"
    trans.mkdir()
    cat.write_text(json.dumps([
        {"seq": 1, "filename": "001.md", "date": "2026-09-01", "stream": "plumbing",
         "session_id": "abc", "turns": 2, "title": "clocks"},
        {"seq": 2, "filename": "002.md", "date": "2026-09-02", "stream": "legal",
         "session_id": "law", "turns": 4, "title": "RFP"},
    ]), encoding="utf-8")
    (trans / "001.md").write_text("opened clocks\n", encoding="utf-8")
    paths = CosmosPaths(str(root), expected_tree_id="spike-open-sessions")
    emit_from_catalog(cat, recents_path(paths))
    return str(root)


def t_list_omits_legal():
    root = _root_with_cat()
    rec = osess.list_sessions(root, "spike-open-sessions")
    ids = [r["id"] for r in rec["rows"]]
    return rec["available"] and rec["n"] == 1 and "cow-abc" in ids and "cow-law" not in ids


def t_open_loads_text():
    root = _root_with_cat()
    rec = osess.open_session(root, "cow-abc", "spike-open-sessions")
    return rec.get("ok") and rec.get("kind") == "OPENED" and "opened clocks" in rec.get("text", "")


def t_open_legal_refuses():
    root = _root_with_cat()
    rec = osess.open_session(root, "cow-law", "spike-open-sessions")
    return rec.get("kind") == "NOT_IN_RECENTS" and rec.get("http") == 404


def t_cli_list_no_guessed_root():
    try:
        osess.main(["list"])
    except SystemExit as e:
        return e.code != 0
    return False


def main() -> int:
    for label, fn in (
        ("list omits legal", t_list_omits_legal),
        ("open loads transcript", t_open_loads_text),
        ("open legal refuses", t_open_legal_refuses),
        ("CLI refuses guessed root", t_cli_list_no_guessed_root),
    ):
        check(label, fn)
    n = sum(1 for _, ok, _ in RESULTS if ok)
    for label, ok, err in RESULTS:
        print(("PASS" if ok else "FAIL") + "  " + label + (f"  :: {err}" if err else ""))
    print(f"{n}/{len(RESULTS)} passed")
    return 0 if n == len(RESULTS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
