#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_recents_panel — GET /api/v1/recents handler for cDeck.

Serves the Recents pane: list cowork sessions (legal omitted) and open
one session by id to return its transcript + title.

    handle_get(root, expected_tree_id=None, query=None) -> (http_code, body)
    emit_from_catalog(catalog_path, dest_path)           -- write recents.json
    recents_path(paths)                                  -- path to recents.json

Schema: cdeck-recents/1
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "cosmos"))

from cosmos_paths import CosmosPaths  # noqa: E402

SCHEMA = "cdeck-recents/1"
LEGAL_STREAMS = frozenset({"legal", "Legal"})
COW_PREFIX = "cow-"


def recents_path(paths: CosmosPaths) -> Path:
    return paths.role("state", "recents", "recents.json")


def _load_recents(paths: CosmosPaths) -> dict | None:
    p = recents_path(paths)
    if not p.is_file():
        return None
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(obj, dict):
        return None
    return obj


def emit_from_catalog(catalog_path: Path, dest: Path) -> dict:
    """Convert a COW_SESSION_CATALOG.json to recents.json."""
    try:
        rows = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return {"ok": False, "error": str(e)}
    if not isinstance(rows, list):
        return {"ok": False, "error": "catalog not a list"}
    trans_dir = catalog_path.parent / "ordered_transcripts"
    sessions = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        stream = row.get("stream") or ""
        if stream in LEGAL_STREAMS:
            continue
        sid = row.get("session_id") or ""
        fname = row.get("filename") or ""
        text_path = trans_dir / fname if fname else None
        sessions.append({
            "id": COW_PREFIX + sid,
            "session_id": sid,
            "date": row.get("date"),
            "stream": stream,
            "title": row.get("title"),
            "turns": row.get("turns"),
            "filename": fname,
            "text_path": str(text_path) if text_path else None,
        })
    dest.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "schema": SCHEMA,
        "sessions": sessions,
        "n_omitted_legal": sum(
            1 for row in rows
            if isinstance(row, dict) and row.get("stream") in LEGAL_STREAMS
        ),
    }
    dest.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    return {"ok": True, "n": len(sessions)}


def _session_by_id(sessions: list, sid: str) -> dict | None:
    for s in sessions:
        if s.get("id") == sid:
            return s
    return None


def _open_session(session: dict, tree_id: str | None) -> tuple[int, dict]:
    text_path = session.get("text_path")
    text = ""
    if text_path:
        p = Path(text_path)
        if p.is_file():
            try:
                text = p.read_text(encoding="utf-8")
            except OSError:
                text = ""
    return 200, {
        "schema": SCHEMA,
        "ok": True,
        "kind": "OPENED",
        "id": session.get("id"),
        "session_id": session.get("session_id"),
        "title": session.get("title"),
        "stream": session.get("stream"),
        "date": session.get("date"),
        "tree_id": tree_id,
        "text": text,
        "text_len": len(text),
    }


def handle_get(root: str, expected_tree_id: str | None = None,
               query: dict | None = None) -> tuple[int, dict]:
    """Handle GET /api/v1/recents.

    query is a dict from urllib.parse.parse_qs, e.g.:
        {"open": ["1"], "id": ["cow-abc"]}
    """
    try:
        paths = CosmosPaths(root, expected_tree_id=expected_tree_id)
        tree_id = paths.sentinel.tree_id
    except Exception as e:  # noqa: BLE001
        return 503, {"ok": False, "error": "PATHS_ERROR", "detail": str(e)[:200]}

    rec = _load_recents(paths)
    if rec is None:
        return 200, {
            "schema": SCHEMA,
            "ok": True,
            "kind": "NO_SOURCE",
            "available": False,
            "tree_id": tree_id,
            "detail": "no recents.json",
        }

    sessions = rec.get("sessions") or []

    # Handle open request
    if query:
        open_vals = query.get("open") or []
        id_vals = query.get("id") or []
        if "1" in open_vals and id_vals:
            sid = id_vals[0]
            session = _session_by_id(sessions, sid)
            if session is None:
                return 404, {
                    "schema": SCHEMA,
                    "ok": False,
                    "kind": "NOT_IN_RECENTS",
                    "id": sid,
                    "tree_id": tree_id,
                }
            return _open_session(session, tree_id)

    # List request
    rows = []
    for s in sessions:
        rows.append({
            "id": s.get("id"),
            "session_id": s.get("session_id"),
            "date": s.get("date"),
            "stream": s.get("stream"),
            "title": s.get("title"),
            "turns": s.get("turns"),
            "filename": s.get("filename"),
        })

    return 200, {
        "schema": SCHEMA,
        "ok": True,
        "kind": "LIST",
        "available": True,
        "tree_id": tree_id,
        "n": len(rows),
        "n_shown": len(rows),
        "n_omitted_legal": rec.get("n_omitted_legal", 0),
        "rows": rows,
    }
