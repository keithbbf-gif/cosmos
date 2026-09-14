#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Timeline projection of the ROLLED milestone feed.

Source of record is `ROLLED.md` (milestone lines: ``t | seat | kind | title | ref``).
Paths come from ``COSMOS_ROLLED_FEED`` (``pathsep``-separated ``.md`` files) or, when
unset, ``state/ROLLED.md`` under the runtime root via the declared ``state`` role.
Each projected row is ``rolled-event/1`` shaped: ``t · seat · kind · title · ref``.
This module only reads; it does not emit JSONL or write anywhere.

Three empty states, kept apart on purpose:

  * ``NO_SOURCE``  — no feed file on disk. ``n`` is **null**: nothing was measured.
  * ``EMPTY``      — a feed exists and holds no milestone lines. ``n`` is a measured ``0``.
  * ``UNPARSEABLE``— one bad milestone line refuses the whole projection, naming the line.
                   A corrupt segment refuses rather than being repaired past.
"""
from __future__ import annotations

import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from sessions_refusals import SessionsAppRefusal

REPO = Path(__file__).resolve().parent.parent.parent
if str(REPO / "cosmos") not in sys.path:
    sys.path.insert(0, str(REPO / "cosmos"))

TIMELINE_SCHEMA = "sessions-app-timeline/1"
EVENT_SCHEMA = "rolled-event/1"
FIELDS = ("t", "seat", "kind", "title", "ref")
FEED_MD = ("ROLLED.md",)
DEFAULT_LIMIT = 200
_ENV_FEED = "COSMOS_ROLLED_FEED"
_TZ_SHORT = re.compile(r"^(.+[Tt]\d{2}:\d{2})([+-]\d{2})$")


def feed_path(root: str | Path) -> Path:
    from cosmos_paths import CosmosPaths, CosmosPathError  # noqa: PLC0415
    try:
        return CosmosPaths(root).role("state", *FEED_MD)
    except CosmosPathError as e:
        raise SessionsAppRefusal(getattr(e, "kind", "BAD_ROOT"), str(e)) from e


def feed_paths(root: str | Path) -> list[Path]:
    raw = os.environ.get(_ENV_FEED, "").strip()
    if raw:
        return [Path(p.strip()) for p in raw.split(os.pathsep) if p.strip()]
    return [feed_path(root)]


def _parse_t(raw: str) -> float | None:
    s = raw.strip()
    if not s or s.upper() == "UNMEASURED":
        return None
    m = _TZ_SHORT.match(s)
    if m:
        s = m.group(1) + m.group(2) + ":00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError as e:
        raise SessionsAppRefusal("UNPARSEABLE", f"timestamp {raw!r}: {e}") from e
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp()


def _resolve_ref(ref_path: str | None) -> str | None:
    if not ref_path:
        return None
    target = (REPO / ref_path).resolve()
    try:
        target.relative_to(REPO.resolve())
    except ValueError:
        return "UNRESOLVED"
    if target.is_file() or target.is_dir():
        return ref_path
    return "UNRESOLVED"


def _sort_key(row: dict):
    t = row.get("t")
    seq = int(row.get("_seq") or 0)
    if t is None:
        return (1, 0.0, seq)
    return (0, float(t), seq)


def _parse_milestone(line: str, n: int, path: Path, seq: int) -> dict | None:
    stripped = line.strip()
    if not stripped.startswith("- ") or " | " not in stripped:
        return None
    parts = [p.strip() for p in stripped[2:].split(" | ")]
    if len(parts) < 4:
        raise SessionsAppRefusal(
            "UNPARSEABLE",
            f"{path} line {n}: milestone needs t | seat | kind | title [| ref=path]")
    t_s, seat, kind, title = parts[0], parts[1], parts[2], parts[3]
    ref_raw = parts[4] if len(parts) > 4 else None
    ref_path = None
    if ref_raw:
        ref_path = ref_raw[4:].strip() if ref_raw.startswith("ref=") else ref_raw
    try:
        t = _parse_t(t_s)
    except SessionsAppRefusal as e:
        raise SessionsAppRefusal(e.kind, f"{path} line {n}: {e}") from e
    row = {f: None for f in FIELDS}
    row.update({"t": t, "seat": seat, "kind": kind, "title": title,
                "ref": _resolve_ref(ref_path), "_seq": seq})
    return row


def _parse(path: Path, seq_start: int) -> tuple[list[dict], int]:
    rows: list[dict] = []
    seq = seq_start
    text = path.read_text(encoding="utf-8", errors="replace")
    for n, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        rec = _parse_milestone(line, n, path, seq)
        if rec is None:
            continue
        rows.append(rec)
        seq += 1
    return rows, seq


def _load(paths: list[Path]) -> list[dict]:
    rows: list[dict] = []
    seq = 0
    for path in paths:
        if not path.is_file():
            continue
        part, seq = _parse(path, seq)
        rows.extend(part)
    rows.sort(key=_sort_key)
    for r in rows:
        r.pop("_seq", None)
    return rows


def project(root: str | Path, limit: int = DEFAULT_LIMIT) -> dict:
    paths = feed_paths(root)
    source = os.pathsep.join(str(p) for p in paths)
    base = {
        "schema": TIMELINE_SCHEMA,
        "event_schema": EVENT_SCHEMA,
        "fields": list(FIELDS),
        "source": source,
        "measured_at": time.time(),
    }
    existing = [p for p in paths if p.is_file()]
    if not existing:
        return base | {
            "available": False, "kind": "NO_SOURCE",
            "n": None, "n_shown": None, "rows": [],
            "detail": "no ROLLED feed on disk - nothing measured, not zero milestones",
        }
    rows = _load(paths)
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
