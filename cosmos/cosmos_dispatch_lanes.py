#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_dispatch_lanes - BTS compatibility lane accounting (R13).

Split out of `cosmos_dispatch.py` (PHASE 4, `docs/CORE_RESTRUCTURE.md`) along a
seam that already existed:

    # ---------------------------------------------------------------------------
    # BTS compatibility lane accounting (R13 ACCEPT for the bridge)
    # ---------------------------------------------------------------------------

This is the dispatch harness's *pure* lane-accounting layer. A queue path
in, load counts / least-loaded lane / job filename / locate / returns dir
out -- no runtime root identity, no DHx stamp, no collector index, no
queue drop. `cosmos_dispatch` re-exports every name below, so every
existing importer of these names off cosmos_dispatch keeps working
unchanged (including `cosmos_watchdog2.measure_lanes`).

What lives here, and why it is one piece:
  * `_lane_dir` / `lane_load` / `measure_lanes` / `pick_least_loaded`
    -- BTS `--lanes` accounting
  * `job_filename` / `_write_exclusive` / `locate_job` / `returns_dir`
    -- drop identity across lanes/buckets

What deliberately did NOT move: `dispatch()` / `job_status` / `run_gate`.
Those own the queue drop, the collector index, and the stage-6 live-tree
gate. Kind inference stays (it is not this banner). DHx/stamps/index is
the other remaining named helper banner.

`LANE_ORDER` / `NATIVE_STREAM` / `RUNNABLE_SUFFIXES` / `SKIP_COUNT_NAMES`
are duplicated here with the same values dispatch already published.
Dispatch re-exports the FUNCTIONS as the same objects (not copies).
Importing the constants the other way would cycle (dispatch imports this
module).

Does not modify kernel / ledger / sched / service. No hard-coded drive
literals.
"""
from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path

# Values MUST match cosmos_dispatch.py. Dispatch re-exports the FUNCTIONS
# (same objects). These names are the lane layer's closed-over vocabulary,
# not a second identity table.
NATIVE_STREAM = "cm"
LANE_ORDER = ("root", "lg", "pb")
RUNNABLE_SUFFIXES = {".py", ".bat", ".cmd", ".ps1"}
SKIP_COUNT_NAMES = {
    "running", "done", "failed", "logs", "staged", "elevated",
    "_lanes", "_delme", "_hold", "_superseded", "__pycache__",
    "research", "findings", "returns", ".git", ".tmp",
    "manifests", "jobs", "dispatch_jobs",
}


# ---------------------------------------------------------------------------
# BTS compatibility lane accounting (R13 ACCEPT for the bridge)
# ---------------------------------------------------------------------------

def _slug(text: str, n: int = 40) -> str:
    words = re.findall(r"[A-Za-z0-9]+", str(text).lower())
    s = "_".join(words) if words else "task"
    return s[:n].strip("_") or "task"


def _lane_dir(queue: Path, lane: str) -> Path:
    if lane in ("root", "cm", ""):
        return Path(queue)
    return Path(queue) / "_lanes" / lane


def _is_runnable(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in RUNNABLE_SUFFIXES


def _is_helper(path: Path) -> bool:
    return path.name.startswith("_")


def lane_load(lane_dir: Path) -> dict:
    """Count running + queued the way bts_runner --lanes does.

    queued = runnable non-helper files sitting in the lane root (not subdirs).
    running = anything in running/.
    """
    queued = 0
    if lane_dir.exists():
        for p in lane_dir.iterdir():
            if p.name in SKIP_COUNT_NAMES or p.name.startswith("."):
                continue
            if _is_runnable(p) and not _is_helper(p):
                queued += 1
    running_dir = lane_dir / "running"
    running = 0
    if running_dir.exists():
        running = sum(1 for p in running_dir.iterdir()
                      if p.is_file() and not p.name.startswith("."))
    return {"queued": queued, "running": running,
            "load": queued + running, "dir": str(lane_dir)}


def measure_lanes(queue: Path) -> dict:
    out = {}
    for name in LANE_ORDER:
        d = _lane_dir(queue, name)
        rec = lane_load(d)
        rec["lane"] = name
        out[name] = rec
    return out


def pick_least_loaded(queue: Path) -> str:
    """Lowest running+queued. Tie -> first in LANE_ORDER (root, lg, pb)."""
    loads = measure_lanes(queue)
    best = None
    best_n = None
    for name in LANE_ORDER:
        n = int(loads[name]["load"])
        if best_n is None or n < best_n:
            best, best_n = name, n
    return best


def job_filename(agent: str, kind: str, task: str, target_dir: str,
                 timeout_s: int) -> str:
    """Deterministic name: same inputs -> same file. Never `_`-prefixed."""
    agent_s = _slug(agent, 16)
    kind_s = _slug(kind, 12)
    task_s = _slug(task, 36)
    digest = hashlib.sha256(
        f"{agent}\0{kind}\0{task}\0{target_dir}".encode("utf-8")
    ).hexdigest()[:8]
    name = f"{agent_s}_{kind_s}_{task_s}_{digest}__t{int(timeout_s)}.py"
    if name.startswith("_"):
        name = "j" + name
    return name


def _write_exclusive(path: Path, text: str) -> bool:
    """True if created. False if the name already existed (idempotent)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY
    try:
        fd = os.open(str(path), flags, 0o644)
    except FileExistsError:
        return False
    try:
        os.write(fd, text.encode("utf-8"))
    except Exception:
        try:
            os.close(fd)
        except OSError:
            pass
        raise
    else:
        os.close(fd)
    return True


def _find_existing(queue: Path, filename: str) -> Path | None:
    loc = locate_job(queue, filename)
    return loc["path"]


def locate_job(queue: Path, filename: str) -> dict:
    """Find a job file across BTS lanes/buckets. state is queued|running|done|failed|missing."""
    name = Path(filename).name
    searches = (
        ("queued", ""),
        ("running", "running"),
        ("done", "done"),
        ("done", str(Path("done") / "findings")),
        ("failed", "failed"),
    )
    for lane in LANE_ORDER:
        base = _lane_dir(queue, lane)
        for state, rel in searches:
            p = base / name if not rel else base / rel / name
            if p.exists():
                return {"path": p, "lane": lane, "state": state,
                        "bucket": rel or ".", "filename": name}
    # native record copies (queue/jobs, tools/dispatch_jobs) are not BTS buckets
    for rel in ("jobs", Path("jobs") / "running"):
        p = Path(queue) / rel / name if not isinstance(rel, Path) else Path(queue) / rel / name
        # the loop above already covers simple names; extra native dirs:
    native_job = Path(queue) / "jobs" / name
    if native_job.exists():
        return {"path": native_job, "lane": NATIVE_STREAM, "state": "queued",
                "bucket": "jobs", "filename": name}
    return {"path": None, "lane": None, "state": "missing",
            "bucket": None, "filename": name}


def _lane_of_path(job_path: Path, queue: Path) -> str:
    """Identity via Path.parts, not a substring of the Windows path text (L2)."""
    parts = [p.lower() for p in Path(job_path).parts]
    for i, p in enumerate(parts):
        if p == "_lanes" and i + 1 < len(parts):
            return parts[i + 1]
    if "jobs" in parts or "dispatch_jobs" in parts:
        return NATIVE_STREAM
    return "root"


def returns_dir(lane_dir: Path) -> Path:
    """BTS compatibility copy: the lane IS the stream; results land in returns/."""
    return Path(lane_dir) / "returns"
