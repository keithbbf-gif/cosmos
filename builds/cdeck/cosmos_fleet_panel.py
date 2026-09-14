#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_fleet_panel — GET /api/v1/fleet for cDeck (feed.json heartbeats only).

Never invents clock rows. Missing or unreadable feed → available:false.
"""
from __future__ import annotations

import json
import time

FEED_MAX_AGE_S = 120


def _read_feed(paths):
    p = paths.role("state", "cdeck", "feed.json")
    if not p.is_file():
        return None, "NO_SOURCE"
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        return None, "BROKE"
    if not isinstance(obj, dict):
        return None, "BROKE"
    measured = float(obj.get("measured_epoch") or obj.get("measured_at") or 0)
    age = time.time() - measured if measured else None
    if age is not None and age > FEED_MAX_AGE_S:
        return obj, "STALE"
    return obj, "OK"


def _clocks_from_feed(feed: dict | None) -> list[dict]:
    raw = (feed or {}).get("clocks")
    if not isinstance(raw, dict):
        return []
    rows: list[dict] = []
    for hb_name, row in raw.items():
        if not isinstance(row, dict):
            continue
        rows.append({
            "heartbeat": hb_name,
            "worker": row.get("worker"),
            "age_s": row.get("age_s"),
            "pid": row.get("pid"),
            "alive": row.get("alive"),
            "state": row.get("state"),
            "verdict": row.get("verdict"),
            "last_run_epoch": row.get("last_run_epoch"),
        })
    rows.sort(key=lambda r: str(r.get("heartbeat") or ""))
    return rows


def handle_get(root, *, expected_tree_id=None):
    from cosmos_paths import CosmosPaths

    paths = CosmosPaths(root)
    if expected_tree_id and paths.sentinel.tree_id != expected_tree_id:
        return 409, {"ok": False, "error": "TREE_ID_MISMATCH",
                     "tree_id": paths.sentinel.tree_id}
    feed, kind = _read_feed(paths)
    clocks = _clocks_from_feed(feed)
    available = feed is not None and kind in ("OK", "STALE")
    return 200, {
        "ok": True,
        "tree_id": paths.sentinel.tree_id,
        "fleet": {
            "available": available,
            "kind": kind,
            "stale": kind == "STALE",
            "clock_count": len(clocks),
            "clocks": clocks,
        },
        "note": "Rows are feed.json heartbeats only; never invented schtasks rows.",
    }
