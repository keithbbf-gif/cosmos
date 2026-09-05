#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_dispatch_stamps - stamps, DHx, collector index (R5/R6/R7).

Split out of `cosmos_dispatch.py` (PHASE 4, `docs/CORE_RESTRUCTURE.md`) along a
seam that already existed:

    # ---------------------------------------------------------------------------
    # stamps, DHx, collector index (R5 ACCEPT, R6 lock ` · `, R7 sidecar+lock)
    # ---------------------------------------------------------------------------

This is the dispatch harness's *pure* stamp/DHx/index layer. A marker or
JSONL row in, a locked append / sidecar out -- no runtime root identity,
no kind inference, no queue drop. `cosmos_dispatch` re-exports every name
below, so every existing importer of these names off cosmos_dispatch keeps
working unchanged (including `cosmos_node_worker.append_dhx_marker`,
`cosmos_dispatcher_daemon.compose_agent_prompt`,
`cosmos_crit_consumer.append_dhx_marker`).

What lives here, and why it is one piece:
  * `_iso_now` / `_marker_line` / `_marker_tail` -- the protocol stamp
  * `_with_file_lock` / `_LockCM` -- the locked RMW used by DHx and index
  * `append_dhx_marker` -- DHx Assignment-log append (idempotent on tail)
  * `_iter_index_rows` / `_already_in_index` / `_latest_for_job`
    / `append_index_row` / `append_assignment_row` / `append_session_assignment`
    -- collector index + per-session assignment JSONL
  * `repo_docs_dir` / `load_boundaries_text` / `compose_agent_prompt`
    -- AGENT_BOUNDARIES addendum that rides the DHx assignment
  * `write_inbox_sidecar` -- R7 collector inbox sidecar

What deliberately did NOT move: `dispatch()` / `job_status` / `run_gate`.
Those own the queue drop and the stage-6 live-tree gate. Resolver identity
(`default_dhx` / `index_path_for`) stays -- it is a different banner.
Kind inference stays. `_oneline` stays on dispatch (summaries in
`dispatch()`); this module carries its own copy for `_marker_line`.

`MARKER_SEP` / `DHX_ASSIGN_HEADER` / `INDEX_LOCK_NAME` / `ONELINE_CAP`
are duplicated here with the same values dispatch already published.
Dispatch re-exports the FUNCTIONS as the same objects (not copies).
Importing the constants the other way would cycle (dispatch imports this
module).

Does not modify kernel / ledger / sched / service. No hard-coded drive
literals.
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime
from pathlib import Path

from cosmos_dispatch_workspace import DispatchError  # noqa: E402

# Values MUST match cosmos_dispatch.py. Dispatch re-exports the FUNCTIONS
# (same objects). These names are the stamp layer's closed-over vocabulary,
# not a second identity table.
MARKER_SEP = " · "
INDEX_LOCK_NAME = "index.jsonl.lock"
DHX_ASSIGN_HEADER = "## Assignment log"
ONELINE_CAP = 140


# ---------------------------------------------------------------------------
# stamps, DHx, collector index (R5 ACCEPT, R6 lock ` · `, R7 sidecar+lock)
# ---------------------------------------------------------------------------

def _oneline(text: str, n: int = ONELINE_CAP) -> str:
    s = " ".join(str(text).split())
    if len(s) <= n:
        return s
    return s[: n - 1] + "…"


def _iso_now() -> str:
    """The stamp. Never hand-typed. Caller must use this, not a literal."""
    return datetime.now().astimezone().isoformat()


def _marker_line(stamp: str, agent: str, task: str, lane: str,
                 filename: str) -> str:
    return (f"{stamp}{MARKER_SEP}{agent}{MARKER_SEP}"
            f"{_oneline(task)}{MARKER_SEP}{lane}/{filename}")


def _marker_tail(marker: str) -> str:
    if MARKER_SEP in marker:
        return marker.rsplit(MARKER_SEP, 1)[-1].strip()
    return marker.rsplit(" - ", 1)[-1].strip()


def _with_file_lock(lock_path: Path, timeout_s: float = 15.0):
    """Blocking exclusive lock. Yields the fd. Always closed."""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_RDWR | os.O_CREAT
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY
    fd = os.open(str(lock_path), flags, 0o644)
    deadline = time.time() + float(timeout_s)
    locked = False
    try:
        while True:
            try:
                if os.name == "nt":
                    import msvcrt
                    os.lseek(fd, 0, os.SEEK_SET)
                    try:
                        os.write(fd, b"\x00")
                    except OSError:
                        pass
                    os.lseek(fd, 0, os.SEEK_SET)
                    msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                locked = True
                break
            except OSError:
                if time.time() >= deadline:
                    os.close(fd)
                    raise DispatchError(
                        "IO", f"timeout acquiring lock {lock_path}")
                time.sleep(0.05)
        yield fd
    finally:
        if locked:
            try:
                if os.name == "nt":
                    import msvcrt
                    os.lseek(fd, 0, os.SEEK_SET)
                    msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            except OSError:
                pass
        try:
            os.close(fd)
        except OSError:
            pass


class _LockCM:
    def __init__(self, lock_path: Path, timeout_s: float = 15.0):
        self.lock_path = lock_path
        self.timeout_s = timeout_s
        self._gen = None

    def __enter__(self):
        self._gen = _with_file_lock(self.lock_path, self.timeout_s)
        return next(self._gen)

    def __exit__(self, *exc):
        try:
            next(self._gen, None)
        except StopIteration:
            pass
        return False


def append_dhx_marker(dhx: Path, marker: str) -> dict:
    """Append `- <marker>` to the Assignment log section. Idempotent on the
    `stream/file` tail so a retry does not double-stamp. Locked RMW (M2)."""
    dhx.parent.mkdir(parents=True, exist_ok=True)
    lock_path = dhx.with_name(dhx.name + ".lock")
    with _LockCM(lock_path):
        body = dhx.read_text(encoding="utf-8") if dhx.exists() else (
            "# DHx — the DHot box (AGENT BRIEF).\n\n"
            f"{DHX_ASSIGN_HEADER} — APPEND-ONLY markers\n\n"
        )
        line = f"- {marker}\n"
        tail = _marker_tail(marker)
        for existing in body.splitlines():
            if existing.startswith("- ") and existing.rstrip().endswith(tail):
                return {"wrote": False, "line": existing, "path": str(dhx)}
        idx = body.find(DHX_ASSIGN_HEADER)
        if idx < 0:
            if not body.endswith("\n"):
                body += "\n"
            new = body + "\n" + line
        else:
            nl = body.find("\n", idx)
            rest = nl + 1 if nl >= 0 else len(body)
            next_h = body.find("\n## ", rest)
            if next_h < 0:
                prefix, suffix = body, ""
            else:
                prefix, suffix = body[:next_h], body[next_h:]
            if not prefix.endswith("\n"):
                prefix += "\n"
            new = prefix + line + suffix
        dhx.write_text(new, encoding="utf-8")
    return {"wrote": True, "line": line.rstrip("\n"), "path": str(dhx)}


def _iter_index_rows(index_path: Path):
    if not index_path.exists():
        return
    try:
        fh = open(index_path, "r", encoding="utf-8", errors="replace")
    except OSError:
        return
    with fh:
        for ln in fh:
            ln = ln.strip()
            if not ln:
                continue
            try:
                row = json.loads(ln)
            except ValueError:
                continue
            if isinstance(row, dict):
                yield row


def _already_in_index(index_path: Path, artifact: str, source: str = "dispatch_assignment") -> dict | None:
    found = None
    for row in _iter_index_rows(index_path) or []:
        if row.get("source") == source and row.get("artifact") == artifact:
            found = row
    return found


def _latest_for_job(index_path: Path, *, artifact: str | None = None,
                    job_file: str | None = None) -> dict | None:
    found = None
    for row in _iter_index_rows(index_path) or []:
        if artifact and row.get("artifact") == artifact:
            found = row
            continue
        if job_file and Path(str(row.get("job_file") or row.get("artifact") or "")).name == job_file:
            found = row
            continue
        if job_file and str(row.get("artifact") or "").endswith(job_file):
            found = row
    return found


def append_index_row(index_path: Path, row: dict, lock_path: Path | None = None) -> dict:
    """Append one JSONL row under the collector index lock (H3)."""
    index_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(row, sort_keys=True, separators=(",", ":"),
                         default=str) + "\n"
    lp = lock_path if lock_path is not None else index_path.with_name(INDEX_LOCK_NAME)
    with _LockCM(lp):
        with open(index_path, "a", encoding="utf-8", newline="") as fh:
            fh.write(payload)
            fh.flush()
            os.fsync(fh.fileno())
    return {"wrote": True, "row": row, "path": str(index_path)}


def append_assignment_row(index_path: Path, row: dict, lock_path: Path | None = None) -> dict:
    existing = _already_in_index(index_path, row["artifact"], "dispatch_assignment")
    if existing is not None:
        return {"wrote": False, "row": existing, "path": str(index_path)}
    return append_index_row(index_path, row, lock_path=lock_path)


def append_session_assignment(path: Path, row: dict) -> dict:
    """Append one JSONL row to the per-session agent-assignment file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(row, sort_keys=True, separators=(",", ":"),
                         default=str) + "\n"
    lock_path = path.with_name(path.name + ".lock")
    with _LockCM(lock_path):
        with open(path, "a", encoding="utf-8", newline="") as fh:
            fh.write(payload)
            fh.flush()
            os.fsync(fh.fileno())
    return {"wrote": True, "path": str(path), "row": row}


def repo_docs_dir() -> Path:
    """Repo-tree docs/ beside this module (not the runtime-root docs role)."""
    return Path(__file__).resolve().parent.parent / "docs"


def load_boundaries_text(path: Path | None = None) -> str:
    """Full text of docs/AGENT_BOUNDARIES.md. Empty string if missing
    (the daemon then refuses rather than sending a task without it)."""
    p = Path(path) if path is not None else (repo_docs_dir() / "AGENT_BOUNDARIES.md")
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8")


def compose_agent_prompt(assignment: str, *, context_blob: str = "",
                         context_hint: str = "", boundaries: str = "",
                         provenance: dict | None = None) -> str:
    """Feed {context + assignment + mandatory AGENT_BOUNDARIES addendum}."""
    parts = [str(assignment or "").strip()]
    hint = str(context_hint or "").strip()
    if hint:
        parts.append("## CONTEXT HINT\n" + hint)
    blob = str(context_blob or "").strip()
    if blob or provenance:
        prov = provenance or {}
        header = (
            "## SESSION CONTEXT (native transcript tail)\n"
            f"session_id={prov.get('session_id')} "
            f"bytes={prov.get('byte_start')}-{prov.get('byte_end')} "
            f"path={prov.get('path')}"
        )
        parts.append(header + ("\n" + blob if blob else "\n(no text turns in tail)"))
    bounds = str(boundaries or "").strip()
    if bounds:
        parts.append(
            "============================================================\n"
            "MANDATORY ADDENDUM — docs/AGENT_BOUNDARIES.md\n"
            "Only the Orchestrator (COW) touches the live tree. Agents PROPOSE\n"
            "tree changes in their results (target path + full content or diff)\n"
            "for COW to execute, or not. Agents never write the live tree or\n"
            "the C:\\ Claude tree, and never delete (propose staging to _delme\\).\n"
            "============================================================\n\n"
            + bounds
        )
    return "\n\n".join(parts).strip() + "\n"


def write_inbox_sidecar(inbox: Path, row: dict) -> dict:
    inbox.parent.mkdir(parents=True, exist_ok=True)
    tmp = inbox.with_suffix(inbox.suffix + ".tmp")
    tmp.write_text(json.dumps(row, indent=1, default=str), encoding="utf-8")
    tmp.replace(inbox)
    return {"wrote": True, "path": str(inbox)}
