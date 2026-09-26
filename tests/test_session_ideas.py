#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hermetic: session-ideas gather is Core state, not V:\\Ai\\ROLD."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_kernel import install  # noqa: E402
from cosmos_session_ideas import (  # noqa: E402
    SCHEMA, extract_turns, fold, grok_ccr_parents,
)


def check(label, fn, results):
    try:
        ok = bool(fn())
        results.append((label, ok, ""))
    except Exception as e:
        results.append((label, False, "%s: %s" % (type(e).__name__, e)))


def main() -> int:
    results = []
    td = Path(tempfile.mkdtemp(prefix="cosmos_session_ideas_"))
    live = install(td / "live", tree_id="spike-ideas")
    sessions = td / "sessions" / "V%3A%5CA%5CAi%5CCOSMOS"
    parent = sessions / "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    child = sessions / "01a0dead-beef-0000-0000-ffffffffffff"
    parent.mkdir(parents=True)
    child.mkdir(parents=True)
    (parent / "chat_history.jsonl").write_text(
        json.dumps({"content": "<user_query>Far-right infinite snap grid</user_query>"})
        + "\n",
        encoding="utf-8",
    )
    (child / "chat_history.jsonl").write_text(
        json.dumps({"content": "<user_query>subagent noise</user_query>"}) + "\n",
        encoding="utf-8",
    )
    from cosmos_paths import CosmosPaths
    paths = CosmosPaths(str(live))
    rec = fold(paths, sessions_root=td / "sessions")
    md = Path(rec["md"]).read_text(encoding="utf-8")
    check("schema", lambda: rec.get("schema") == SCHEMA, results)
    check("one parent session", lambda: rec.get("n_sessions") == 1, results)
    check("skips 01a0 subagent", lambda: rec.get("n_turns") == 1, results)
    check("Keith quote in OS file", lambda: "Far-right infinite snap grid" in md, results)
    check("not V:\\Ai\\ROLD", lambda: "ROLD" not in rec["md"] or "Ai\\COSMOS" in rec["md"].replace("/", "\\"), results)
    ok = all(r[1] for r in results)
    for lab, good, err in results:
        print(("PASS" if good else "FAIL"), lab, err)
    print("n", len(results), "ok", sum(1 for r in results if r[1]))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
