#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Timeline projection of the ROLLED milestone feed.

Source of record is an append-only `rolled-event/1` JSONL under the runtime
root, resolved through the declared `state` role — never a hand-assembled path.
Each record is `t · seat · kind · title · ref`. This module only reads: the feed
has a writer elsewhere, and a projection is rebuildable, never authority.

Three empty states, kept apart on purpose:

  * `NO_SOURCE`  — no feed on disk. `n` is **null**: nothing was measured.
  * `EMPTY`      — a feed exists and holds no records. `n` is a measured `0`.
  * `UNPARSEABLE`— one bad line refuses the whole projection, naming the line.
                   A corrupt segment refuses rather than being repaired past.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from sessions_refusals import SessionsAppRefusal

REPO = Path(__file__).resolve().parent.parent.parent
if str(REPO / "cosmos") not in sys.path:
    sys.path.insert(0, str(REPO / "cosmos"))

TIMELINE_SCHEMA = "sessions-app-timeline/1"
EVENT_SCHEMA = "rolled-event/1"
FIELDS = ("t", "seat", "kind", "title", "ref")
FEED_PARTS = ("rolled", "feed.jsonl")
DEFAULT_LIMIT = 200


def feed_path(root: str | Path) -> Path:
    from cosmos_paths import CosmosPaths, CosmosPathError  # noqa: PLC0415
    try:
        return CosmosPaths(root).role("state", *FEED_PARTS)
    except CosmosPathError as e:
        raise SessionsAppRefusal(getattr(e, "kind", "BAD_ROOT"), str(e)) from e


def _sort_key(row: dict):
    t = row.get("t")
    try:
        return (0, -float(t))
    except (TypeError, ValueError):
        # a milestone with no measured t sorts last, it does not become t=0
        return (1, 0.0)


def _parse(path: Path) -> list[dict]:
    rows: list[dict] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    for n, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError as e:
            raise SessionsAppRefusal(
                "UNPARSEABLE", f"{path} line {n}: {e}") from e
        if not isinstance(rec, dict):
            raise SessionsAppRefusal(
                "UNPARSEABLE", f"{path} line {n}: record is not an object")
        if str(rec.get("schema") or "") != EVENT_SCHEMA:
            raise SessionsAppRefusal(
                "UNPARSEABLE",
                f"{path} line {n}: schema {rec.get('schema')!r} is not {EVENT_SCHEMA}")
        rows.append({f: rec.get(f) for f in FIELDS})
    rows.sort(key=_sort_key)
    return rows


def project(root: str | Path, limit: int = DEFAULT_LIMIT) -> dict:
    path = feed_path(root)
    base = {
        "schema": TIMELINE_SCHEMA,
        "event_schema": EVENT_SCHEMA,
        "fields": list(FIELDS),
        "source": str(path),
        "measured_at": time.time(),
    }
    if not path.is_file():
        return base | {
            "available": False, "kind": "NO_SOURCE",
            "n": None, "n_shown": None, "rows": [],
            "detail": "no ROLLED feed on disk - nothing measured, not zero milestones",
        }
    rows = _parse(path)
    if not rows:
        return base | {
            "available": True, "kind": "EMPTY",
            "n": 0, "n_shown": 0, "rows": [],
            "detail": "feed exists and holds no milestone yet",
        }
    shown = rows[:max(1, int(limit))]
    return base | {
        "available": True, "kind": "OK",
        "n": len(rows), "n_shown": len(shown), "rows": shown, "detail": None,
    }
