#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Open Sessions — first product COSMOS ships (Keith 2026-09-05).

COSMOS is the OS. This is a product on that OS: list and open AI sessions
(Cowork pack via cowork_to_openwork → cDeck recents, plus Grok TUI history
when present). Legal rows stay omitted. No fake ids.

    py -3.14 builds/open_sessions/Open_sessions.py list --root V:\\A\\Ai\\COSMOS\\live
    py -3.14 builds/open_sessions/Open_sessions.py open cow-TOPIC --root V:\\A\\Ai\\COSMOS\\live

Session-tools suite (crash / all AIs / diff / anonymize) iterates on this.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "builds" / "cdeck"))
sys.path.insert(0, str(REPO / "cosmos"))

from cosmos_recents_panel import handle_get  # noqa: E402

PRODUCT = "Open Sessions"
SCHEMA = "open-sessions/1"


def list_sessions(root: str, tree_id: str | None) -> dict:
    code, body = handle_get(root, expected_tree_id=tree_id)
    rows = body.get("rows") or [] if body.get("available") else []
    return {
        "schema": SCHEMA,
        "product": PRODUCT,
        "http": code,
        "available": bool(body.get("available")),
        "kind": body.get("kind"),
        "tree_id": body.get("tree_id"),
        "n": len(rows),
        "n_omitted_legal": body.get("n_omitted_legal"),
        "rows": rows,
        "detail": body.get("detail"),
    }


def open_session(root: str, sid: str, tree_id: str | None) -> dict:
    code, body = handle_get(
        root, expected_tree_id=tree_id,
        query={"open": ["1"], "id": [sid]},
    )
    body = dict(body)
    body["schema"] = SCHEMA
    body["product"] = PRODUCT
    body["http"] = code
    return body


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="Open_sessions.py",
        description="Open Sessions — list/open AI sessions on COSMOS (first product).",
    )
    p.add_argument("--root", help="COSMOS runtime root (live/)")
    p.add_argument("--tree-id", default=None)
    p.add_argument("--json", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="list recents (legal omitted)")
    op = sub.add_parser("open", help="open one session (transcript + OpenWork focus)")
    op.add_argument("id")
    a = p.parse_args(argv)
    if not a.root:
        p.error("--root is required (no guessed live path)")
    if a.cmd == "list":
        rec = list_sessions(a.root, a.tree_id)
        if a.json:
            print(json.dumps({k: rec[k] for k in rec if k != "rows"}, indent=2))
            print(json.dumps(rec["rows"][:20]))
        else:
            print(f"{PRODUCT}  n={rec['n']}  legal_omitted={rec.get('n_omitted_legal')}  "
                  f"tree={rec.get('tree_id')}  available={rec['available']}")
            if not rec["available"]:
                print(rec.get("kind"), rec.get("detail") or "")
            for r in rec["rows"][:20]:
                print(f"  {r.get('id')}  {r.get('date')}  {r.get('stream')}  {r.get('title')}")
            if rec["n"] > 20:
                print(f"  … {rec['n'] - 20} more")
        return 0 if rec.get("available") or rec.get("kind") == "NO_SOURCE" else 1
    rec = open_session(a.root, a.id, a.tree_id)
    if a.json:
        dump = {k: rec[k] for k in rec if k != "text"}
        dump["text_len"] = len(rec.get("text") or "")
        print(json.dumps(dump, indent=2))
    else:
        print(f"{PRODUCT}  {rec.get('kind')}  {rec.get('id')}  {rec.get('opencode_id')}")
        print(rec.get("title") or "")
        t = rec.get("text") or rec.get("detail") or ""
        print(t[:2000])
        print(rec.get("openwork") or "")
    # NO_SOURCE sets ok for an empty list. That is not an opened id.
    opened = rec.get("kind") in ("OPENED", "NO_TRANSCRIPT", "TRANSCRIPT_UNREADABLE")
    return 0 if rec.get("ok") and opened else 2


if __name__ == "__main__":
    raise SystemExit(main())
