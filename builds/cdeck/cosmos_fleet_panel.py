#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_fleet_panel — GET /api/v1/fleet handler for cDeck."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "cosmos"))

from cosmos_paths import CosmosPaths  # noqa: E402

SCHEMA = "cdeck-fleet/1"


def _load_feed(paths: CosmosPaths) -> dict | None:
    p = paths.role("state", "cdeck", "feed.json")
    if not p.is_file():
        return None
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return obj if isinstance(obj, dict) else None


def handle_get(root: str, expected_tree_id: str | None = None) -> tuple[int, dict]:
    try:
        paths = CosmosPaths(root, expected_tree_id=expected_tree_id)
        tree_id = paths.sentinel.tree_id
    except Exception as e:  # noqa: BLE001
        return 503, {"ok": False, "error": "PATHS_ERROR", "detail": str(e)[:200]}

    feed = _load_feed(paths)
    if feed is None:
        return 200, {
            "schema": SCHEMA,
            "ok": True,
            "tree_id": tree_id,
            "fleet": {"available": False, "detail": "no feed.json"},
        }

    clocks_raw = feed.get("clocks") or {}
    clocks = []
    for name, info in clocks_raw.items():
        if not isinstance(info, dict):
            continue
        clocks.append({
            "name": name,
            "worker": info.get("worker"),
            "pid": info.get("pid"),
            "alive": info.get("alive"),
            "state": info.get("state"),
            "age_s": info.get("age_s"),
            "last_run_epoch": info.get("last_run_epoch"),
        })

    pause = feed.get("pause") or {}
    queue = feed.get("queue") or {}

    return 200, {
        "schema": SCHEMA,
        "ok": True,
        "tree_id": tree_id,
        "measured_epoch": feed.get("measured_epoch"),
        "pause": {"state": pause.get("state", "UNKNOWN"), "present": bool(pause.get("present"))},
        "queue": {"manifests": queue.get("manifests", 0)},
        "fleet": {
            "available": True,
            "clocks": clocks,
            "snapshots": feed.get("snapshots") or {},
        },
    }
