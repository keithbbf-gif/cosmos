#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_collector_scan - queue / research / ledger file iterators.

Split out of `cosmos_collector.py` (PHASE 4, `docs/CORE_RESTRUCTURE.md`) along a
seam that already existed:

    # ---------------------------------------------------------------------------
    # scanning
    # ---------------------------------------------------------------------------

This is the collector's *pure* walk layer. Paths and event names in, (path,
source) pairs or parsed dicts out -- no runtime root, no resolver, no daemon
state, no writes. `cosmos_collector` re-exports every name below, so every
existing importer of these names off cosmos_collector keeps working unchanged.

What lives here, and why it is one piece:
  * SKIP_DIR_NAMES / LEDGER_KEEP / LEDGER_DROP / LEDGER_KEEP_SUBSTR
    -- the vocabulary the walkers filter on
  * `_walk_files` / `_is_result_name` -- long-path walk + result-name gate
  * `iter_queue_files` / `iter_research_files` -- queue and research ingress
  * `iter_ledger_events` / `iter_runner_ledger` / `iter_jsonl_objs`
    -- JSONL readers (torn lines skipped; the ledger itself stays fail-closed
    for Core)
  * `ledger_event_kept` -- the keep/drop predicate `_collect_ledger` calls

What deliberately did NOT move: `Collector._collect_*`. Those methods hold
`self.catalog`, append through `self._row`/`self._consider`, and own the
heartbeat. Pulling them out would mean passing the collector into a free
function -- coupling wearing a module's clothes, not a seam. The seam is
exactly here, at the boundary where the walk stops needing the daemon.

The one filesystem touch is read-only (`os.walk` / JSONL open) and takes
roots as arguments -- no path is assembled from a literal (canon: no
hard-coded paths). `extended()` is the long-path helper from cosmos_paths.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from cosmos_paths import extended  # noqa: E402

SKIP_DIR_NAMES = {
    "_lanes", "_delme", "__pycache__", ".git", "running", "staged",
    "_hold", ".tmp",
}

# Ledger events that are agent/worker outcomes. Infrastructure noise
# (BOOT_VERIFIED, TOOL_DECLARED, LINK_REGISTERED, BUDGET_SET, spend/session)
# stays out of the agent aggregate; the ledger itself remains the authority.
LEDGER_KEEP = {
    "RAIL_RESULT", "RAIL_DISPATCH", "PROBE_RESULT", "NODE_REVIEW",
    "JOB_DONE", "JOB_FAILED", "JOB_STALE", "JOB_CLAIMED", "JOB_SUBMITTED",
}

LEDGER_KEEP_SUBSTR = ("RESULT", "DONE", "FAILED", "REVIEW")
LEDGER_DROP = {
    "BOOT_VERIFIED", "TOOL_DECLARED", "LINK_REGISTERED", "BUDGET_SET",
    "SESSION_OPENED", "SESSION_CLOSED", "SEED_WRITTEN",
    "TOOL_DISPOSITION", "MAKER_ADDED",
    "SPEND_RESERVED", "SPEND_SETTLED", "SPEND_DENIED",
}


# ---------------------------------------------------------------------------
# scanning
# ---------------------------------------------------------------------------

def _walk_files(base: Path, skip_dirs: set[str]):
    """Yield Path for each file under base, skipping named dirs. Tolerates errors."""
    if not base.exists() or not base.is_dir():
        return
    start = extended(base)
    for dirpath, dirnames, filenames in os.walk(start, onerror=lambda _e: None):
        dirnames[:] = [d for d in dirnames
                       if d not in skip_dirs and not d.startswith(".")]
        for fn in filenames:
            if fn.startswith(".") or fn.endswith(".pyc"):
                continue
            p = Path(dirpath) / fn
            # strip \\?\ prefix for stable artifact paths
            s = str(p)
            if s.startswith("\\\\?\\"):
                s = s[4:]
            yield Path(s)


def _is_result_name(name: str) -> bool:
    n = name.lower()
    return n.endswith("_result.json") or n.endswith(".result.json")


def iter_queue_files(queue_root: Path, lane: str):
    """Yield (path, source) for one queue tree.

    Root scan skips `_lanes` so lg/pb are not double-counted when those
    trees are scanned as their own sources.
    """
    skip = set(SKIP_DIR_NAMES)
    if lane == "root":
        skip.add("_lanes")
    skip.add("returns")  # own source (M2) — do not double-count as queue_result
    # result JSONs anywhere under this tree except returns/
    seen: set[str] = set()
    for p in _walk_files(queue_root, skip):
        if _is_result_name(p.name):
            key = str(p).lower()
            if key not in seen:
                seen.add(key)
                yield p, "queue_result"
    for bucket, source in (("done", "queue_done"),
                           ("failed", "queue_failed"),
                           ("logs", "queue_log"),
                           ("returns", "queue_returns")):
        folder = queue_root / bucket
        if not folder.exists():
            continue
        # done/failed/logs keep their own nested dirs (findings/, resolved_*)
        for p in _walk_files(folder, {"__pycache__", ".git"}):
            key = str(p).lower()
            if key in seen:
                continue
            seen.add(key)
            yield p, source


def iter_research_files(research_dir: Path):
    if not research_dir.exists():
        return
    for p in _walk_files(research_dir, {"__pycache__", ".git"}):
        if p.suffix.lower() == ".md":
            yield p, "research"


def iter_ledger_events(ledger_path: Path):
    """Yield parsed JSON objects from the authority JSONL. Torn lines skipped
    (this projection does not refuse the whole poll for a bad source line;
    the ledger itself remains fail-closed for Core)."""
    if not ledger_path.exists():
        return
    try:
        fh = open(ledger_path, "r", encoding="utf-8", errors="replace")
    except OSError:
        return
    with fh:
        for i, ln in enumerate(fh, 1):
            ln = ln.strip()
            if not ln:
                continue
            try:
                rec = json.loads(ln)
            except ValueError:
                continue
            if not isinstance(rec, dict):
                continue
            rec["_line"] = i
            yield rec


def ledger_event_kept(event: str) -> bool:
    if not event:
        return False
    up = event.upper()
    if up in LEDGER_DROP:
        return False
    if event in LEDGER_KEEP or up in LEDGER_KEEP:
        return True
    return any(s in up for s in LEDGER_KEEP_SUBSTR)


def iter_runner_ledger(path: Path):
    """Yield parsed runner_ledger.jsonl events (start/end times)."""
    if not path.exists():
        return
    try:
        fh = open(path, "r", encoding="utf-8", errors="replace")
    except OSError:
        return
    with fh:
        for i, ln in enumerate(fh, 1):
            ln = ln.strip()
            if not ln:
                continue
            try:
                rec = json.loads(ln)
            except ValueError:
                continue
            if not isinstance(rec, dict):
                continue
            rec["_line"] = i
            rec["_ledger"] = str(path)
            yield rec


def iter_jsonl_objs(path: Path):
    """Yield parsed dicts from any JSONL. Torn lines skipped."""
    if not path.exists():
        return
    try:
        fh = open(path, "r", encoding="utf-8", errors="replace")
    except OSError:
        return
    with fh:
        for i, ln in enumerate(fh, 1):
            ln = ln.strip()
            if not ln:
                continue
            try:
                rec = json.loads(ln)
            except ValueError:
                continue
            if isinstance(rec, dict):
                rec["_line"] = i
                yield rec
