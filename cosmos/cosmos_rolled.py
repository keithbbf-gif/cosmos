#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_rolled — read the ROLLED.md milestone feed.

Schema: rolled-event/1 lines, pipe-separated: t | seat | kind | title | ref
File location: live/state/ROLLED.md  (absent → returns empty events list).

GET /api/v1/rolled is read-only; it never mkdir or write.
"""
from __future__ import annotations

import time
from pathlib import Path

SCHEMA = "cosmos-rolled/1"
EVENT_SCHEMA = "rolled-event/1"
_ROLLED_MD = "ROLLED.md"
_STATE_ROLE = "state"


def _parse_event_line(line: str) -> dict | None:
    """Parse one `rolled-event/1 t | seat | kind | title | ref` line.
    Returns None if the line does not match the schema."""
    stripped = line.strip()
    if not stripped.startswith(EVENT_SCHEMA):
        return None
    body = stripped[len(EVENT_SCHEMA):].strip()
    parts = [p.strip() for p in body.split("|")]
    if len(parts) < 4:
        return None
    t = parts[0] if len(parts) > 0 else ""
    seat = parts[1] if len(parts) > 1 else ""
    kind = parts[2] if len(parts) > 2 else ""
    title = parts[3] if len(parts) > 3 else ""
    ref = parts[4] if len(parts) > 4 else ""
    return {"t": t, "seat": seat, "kind": kind, "title": title, "ref": ref}


def snapshot(paths) -> dict:
    """Return the ROLLED.md feed as a structured dict.

    Always returns a valid dict.  Events list is empty when the file is absent.
    GET never writes or mkdir.
    """
    result: dict = {
        "schema": SCHEMA,
        "measured_at": time.time(),
        "available": False,
        "kind": "NO_SOURCE",
        "events": [],
        "n": 0,
        "source": None,
    }
    try:
        rolled_path: Path = paths.state(_ROLLED_MD)
    except Exception:  # noqa: BLE001
        result["kind"] = "PATH_ERROR"
        return result

    if not rolled_path.exists():
        return result

    result["available"] = True
    result["source"] = _ROLLED_MD
    try:
        text = rolled_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        result["available"] = False
        result["kind"] = "READ_ERROR"
        result["detail"] = str(exc)[:300]
        return result

    events = []
    for line in text.splitlines():
        ev = _parse_event_line(line)
        if ev is not None:
            events.append(ev)

    result["kind"] = "OK"
    result["events"] = events
    result["n"] = len(events)
    return result
