#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_recents_panel — GET /api/v1/recents for cDeck Open Sessions.

Schema cdeck-recents/1. Legal stream rows omitted. GET never mutates or mkdir.
?open=1&id=<sid> returns OPENED transcript when the id is in recents.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

SCHEMA = "cdeck-recents/1"
RECENTS_NAME = "recents.json"


def recents_path(paths) -> Path:
    return paths.state("recents", RECENTS_NAME)


def emit_from_catalog(catalog_path: Path, out_path: Path) -> None:
    """Build recents.json from a COW_SESSION_CATALOG-style JSON file."""
    cat = json.loads(catalog_path.read_text(encoding="utf-8"))
    if not isinstance(cat, list):
        raise ValueError("catalog must be a JSON array")
    rows = []
    omitted = 0
    for item in cat:
        if not isinstance(item, dict):
            continue
        stream = str(item.get("stream") or "").strip().lower()
        if stream == "legal":
            omitted += 1
            continue
        sid = str(item.get("session_id") or item.get("id") or "").strip()
        if not sid:
            continue
        rows.append({
            "id": f"cow-{sid}",
            "session_id": sid,
            "date": item.get("date"),
            "stream": item.get("stream"),
            "title": item.get("title"),
            "turns": item.get("turns"),
            "filename": item.get("filename"),
        })
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps({
            "schema": SCHEMA,
            "rows": rows,
            "n_omitted_legal": omitted,
            "updated_at": time.time(),
        }, indent=2)
        + "\n",
        encoding="utf-8",
    )


def _load_rows(paths) -> tuple[dict | None, list]:
    p = recents_path(paths)
    if not p.is_file():
        return None, []
    try:
        rec = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        return None, []
    if not isinstance(rec, dict):
        return None, []
    rows = rec.get("rows")
    return rec, rows if isinstance(rows, list) else []


def _find_row(rows: list, sid: str) -> dict | None:
    want = sid.strip()
    for r in rows:
        if not isinstance(r, dict):
            continue
        rid = str(r.get("id") or "")
        if rid == want or rid == f"cow-{want}" or str(r.get("session_id") or "") == want:
            return r
    return None


def _transcript_text(paths, row: dict) -> str:
    fn = row.get("filename")
    if not fn:
        return ""
    for base in (
        paths.root.parent / "ordered_transcripts",
        paths.state("recents", "transcripts"),
    ):
        p = Path(base) / str(fn)
        if p.is_file():
            return p.read_text(encoding="utf-8", errors="replace")
    return ""


def handle_get(
    root,
    *,
    expected_tree_id: str | None = None,
    query: dict | None = None,
) -> tuple[int, dict]:
    from cosmos_paths import CosmosPaths

    paths = CosmosPaths(str(root), expected_tree_id=expected_tree_id)
    tid = paths.sentinel.tree_id
    q = query or {}
    open_q = (q.get("open") or [""])[0]
    sid_q = (q.get("id") or [""])[0]

    file_rec, rows = _load_rows(paths)
    if file_rec is None:
        body = {
            "schema": SCHEMA,
            "ok": True,
            "available": False,
            "kind": "NO_SOURCE",
            "detail": "recents.json not present — explicit empty",
            "rows": [],
            "n": 0,
            "n_shown": 0,
            "n_omitted_legal": None,
            "tree_id": tid,
            "measured_at": time.time(),
        }
        if str(open_q) == "1" and sid_q:
            body["ok"] = False
            body["kind"] = "NOT_IN_RECENTS"
            body["id"] = sid_q
            body["http"] = 404
            return 404, body
        return 200, body

    omitted = file_rec.get("n_omitted_legal")
    if str(open_q) == "1" and sid_q:
        row = _find_row(rows, sid_q)
        if row is None:
            return 404, {
                "schema": SCHEMA,
                "ok": False,
                "kind": "NOT_IN_RECENTS",
                "id": sid_q,
                "http": 404,
                "tree_id": tid,
                "measured_at": time.time(),
            }
        text = _transcript_text(paths, row)
        return 200, {
            "schema": SCHEMA,
            "ok": True,
            "kind": "OPENED",
            "id": row.get("id"),
            "title": row.get("title"),
            "text": text,
            "text_len": len(text),
            "stream": row.get("stream"),
            "tree_id": tid,
            "measured_at": time.time(),
        }

    return 200, {
        "schema": SCHEMA,
        "ok": True,
        "available": True,
        "kind": "OK",
        "rows": rows,
        "n": len(rows),
        "n_shown": len(rows),
        "n_omitted_legal": omitted,
        "tree_id": tid,
        "measured_at": time.time(),
    }
