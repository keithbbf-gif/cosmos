#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_jukebox_panel — GET /api/v1/jukebox fold.

Scheduler truth only. Five legal state words:

    QUEUED · RUNNING · BROKE · CLEAN · FINDINGS

`stale` is a flag on a RUNNING row (JOB_STALE / report-never-retry), never a
sixth outcome and never a retry. GET does not mkdir, append, claim, cancel,
hold, or retry. No DONE/FAILED vocabulary.

Documented jobs/counts shape (one object, aliases kept for current consumers):

    {
      schema: "cdeck-jukebox/1",
      ok: true,
      tree_id, measured_at,
      jobs: [ {job_id, st, command, priority, age_s, stale_flag, ...} ],
      counts: {QUEUED, RUNNING, BROKE, CLEAN, FINDINGS, stale_flagged},
      queue: {available, jobs, counts, kind},   # Gitur / Review / Runs
      jobs_n, shown, total,                     # census aliases
      in_flight_n, broke_n, clean_n, findings_n, done_n, stale_flagged
    }

`done_n` is CLEAN only — FINDINGS is not a clean terminal. WORK IN FLIGHT is
QUEUED + RUNNING + FINDINGS; BROKE is not in-flight.

Product/stage come from manifest tags (`product`/`profile`, `stage`). Untagged
historic work is UNATTRIBUTED / UNMEASURED. Command text is never classified.

Mirrors cosmos_sched.Scheduler._state: JOB_SUBMITTED→QUEUED, JOB_CLAIMED only
from QUEUED, JOB_DONE/JOB_STALE only when the job_id is already in state.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "cosmos"))

from cosmos_ledger import Ledger, LedgerError, _canon  # noqa: E402
from cosmos_paths import CosmosPathError, CosmosPaths  # noqa: E402

SCHEMA = "cdeck-jukebox/1"
LEGAL_STATES = ("QUEUED", "RUNNING", "BROKE", "CLEAN", "FINDINGS")
TERMINAL = frozenset({"BROKE", "CLEAN", "FINDINGS"})
IN_FLIGHT = frozenset({"QUEUED", "RUNNING", "FINDINGS"})
PRIORITIES = {"critical": 3, "high": 2, "normal": 1, "low": 0}
MAX_LEDGER_BYTES = 8 * 1024 * 1024
PATH_KINDS = frozenset({
    "NOT_FOUND", "UNREADABLE", "UNPARSEABLE",
    "IDENTITY_MISMATCH", "NOT_A_DIRECTORY",
})


class JukeboxPanelError(RuntimeError):
    """kind in {TOO_LARGE, MALFORMED, LEDGER_REFUSED} plus path kinds."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__("[%s] %s" % (kind, detail))


def _fold_sched(state: dict, rec: dict) -> dict:
    """Same transitions as Scheduler._state. Unknown-job DONE/STALE vanish."""
    p, e = rec.get("payload") or {}, rec.get("event")
    if not isinstance(p, dict):
        return state
    jid = p.get("job_id")
    if not jid:
        return state
    if e == "JOB_SUBMITTED":
        state[jid] = {"m": p, "st": "QUEUED", "by": None, "finished": None}
    elif e == "JOB_CLAIMED" and state.get(jid, {}).get("st") == "QUEUED":
        state[jid].update(st="RUNNING", by=p.get("worker"), claimed=rec.get("t"))
    elif e == "JOB_DONE" and jid in state:
        outcome = p.get("outcome")
        if outcome in TERMINAL and state[jid]["st"] == "RUNNING":
            state[jid].update(st=outcome, by=p.get("worker"),
                              finished=rec.get("t"), detail=p.get("detail"))
    elif e == "JOB_STALE" and jid in state:
        state[jid]["stale_reported"] = True
    return state


def _read_manifest(queue: Path, jid: str) -> tuple[bool, dict]:
    mp = queue / "manifests" / ("%s.json" % jid)
    if not mp.is_file():
        return False, {}
    try:
        obj = json.loads(mp.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError):
        return True, {}
    return True, obj if isinstance(obj, dict) else {}


def _tag(disk: dict, m: dict, *keys: str):
    for src in (disk, m):
        for k in keys:
            v = src.get(k)
            if v is None:
                continue
            s = str(v).strip()
            if s:
                return s
    return None


def _age_s(v: dict, now: float):
    st = v.get("st")
    if st == "RUNNING" and v.get("claimed") is not None:
        src = v.get("claimed")
    elif st in TERMINAL and v.get("finished") is not None:
        src = v.get("finished")
    else:
        src = (v.get("m") or {}).get("submitted")
    if src is None or src == "":
        return None
    try:
        return round(max(0.0, now - float(src)), 1)
    except (TypeError, ValueError):
        return None


def _row(jid: str, v: dict, queue: Path, now: float) -> dict:
    m = v.get("m") if isinstance(v.get("m"), dict) else {}
    present, disk = _read_manifest(queue, jid)
    st = v.get("st")
    if st not in LEGAL_STATES:
        st = None
    command = _tag(disk, m, "command", "task")
    priority = _tag(disk, m, "priority") or m.get("priority")
    product = _tag(disk, m, "product", "profile")
    stage = _tag(disk, m, "stage", "portfolio_stage")
    stale = bool(v.get("stale_reported"))
    age = _age_s(v, now)
    submitted = disk.get("submitted", m.get("submitted"))
    return {
        "job_id": jid,
        "st": st,
        "state": st,
        "outcome": st if st in TERMINAL else None,
        "command": command,
        "priority": priority,
        "lane": _tag(disk, m, "lane") or m.get("lane") or "default",
        "age_s": age,
        "stale_flag": stale,
        "stale": stale,
        "submitted": submitted,
        "claimed": v.get("claimed"),
        "finished": v.get("finished"),
        "by": v.get("by"),
        "manifest_present": present,
        "product": product if product is not None else "UNATTRIBUTED",
        "stage": stage if stage is not None else "UNMEASURED",
        "terminal": st in TERMINAL,
        "detail": v.get("detail") or disk.get("detail") or m.get("detail"),
    }


def _sort_key(row: dict):
    pri = PRIORITIES.get(str(row.get("priority") or ""), -1)
    try:
        submitted = float(row.get("submitted") or 0)
    except (TypeError, ValueError):
        submitted = 0.0
    return (-pri, -submitted, str(row.get("job_id") or ""))


def _counts(rows: list[dict]) -> dict:
    out = {w: 0 for w in LEGAL_STATES}
    stale_flagged = 0
    for r in rows:
        st = r.get("st")
        if st in out:
            out[st] += 1
        if r.get("stale_flag"):
            stale_flagged += 1
    out["stale_flagged"] = stale_flagged
    return out


def _unsigned_fold(path: Path) -> tuple[dict, bool]:
    """Replay without HMAC when the install key is absent. Chain still checked."""
    raw = path.read_text(encoding="utf-8")
    state: dict = {}
    prev_sha = ""
    chain_linked = True
    for i, ln in enumerate(raw.splitlines(), 1):
        if not ln.strip():
            continue
        try:
            rec = json.loads(ln)
        except ValueError as e:
            raise JukeboxPanelError(
                "MALFORMED", "line %d: does not parse (%s)" % (i, e)) from e
        if not isinstance(rec, dict) or "payload" not in rec:
            raise JukeboxPanelError(
                "MALFORMED", "line %d: parseable but not a ledger record" % i)
        body = _canon(rec["payload"])
        if (rec.get("payload_len") != len(body)
                or rec.get("payload_sha") != hashlib.sha256(body).hexdigest()):
            raise JukeboxPanelError(
                "MALFORMED", "line %d: payload_sha" % i)
        if rec.get("prev_sha") != prev_sha:
            chain_linked = False
        prev_sha = hashlib.sha256(ln.encode("utf-8")).hexdigest()
        state = _fold_sched(state, rec)
    return state, chain_linked


def _bind_state(queue: Path, key: bytes | None) -> tuple[dict, dict]:
    """Project sched_ledger.jsonl. GET never creates the file or manifests/."""
    meta = {
        "hmac_verified": None,
        "chain_linked": True,
        "records": 0,
        "kind": "OK",
    }
    led_p = queue / "sched_ledger.jsonl"
    if not led_p.is_file():
        return {}, meta
    try:
        n = led_p.stat().st_size
    except OSError as e:
        raise JukeboxPanelError("LEDGER_REFUSED", str(e)[:200]) from e
    if n > MAX_LEDGER_BYTES:
        raise JukeboxPanelError(
            "TOO_LARGE",
            "sched_ledger.jsonl is %d bytes (max %d)" % (n, MAX_LEDGER_BYTES))
    if key:
        try:
            led = Ledger(led_p, key, "jukebox-get")
            recs = list(led.verify())
        except LedgerError as e:
            raise JukeboxPanelError(
                "LEDGER_REFUSED", "%s: %s" % (e.kind, e)) from e
        state: dict = {}
        for rec in recs:
            state = _fold_sched(state, rec)
        meta["hmac_verified"] = True
        meta["records"] = len(recs)
        return state, meta
    try:
        state, chain_linked = _unsigned_fold(led_p)
    except JukeboxPanelError:
        raise
    except OSError as e:
        raise JukeboxPanelError("LEDGER_REFUSED", str(e)[:200]) from e
    meta["hmac_verified"] = False
    meta["chain_linked"] = chain_linked
    meta["records"] = sum(1 for _ in state)
    return state, meta


def _pack(tree_id: str, rows: list[dict], meta: dict, now: float) -> dict:
    counts = _counts(rows)
    jobs_n = len(rows)
    in_flight_n = sum(counts[w] for w in IN_FLIGHT)
    body = {
        "schema": SCHEMA,
        "ok": True,
        "tree_id": tree_id,
        "measured_at": now,
        "jobs": rows,
        "counts": counts,
        "jobs_n": jobs_n,
        "shown": jobs_n,
        "total": jobs_n,
        "in_flight_n": in_flight_n,
        "broke_n": counts["BROKE"],
        "clean_n": counts["CLEAN"],
        "findings_n": counts["FINDINGS"],
        "done_n": counts["CLEAN"],
        "stale_flagged": counts["stale_flagged"],
        "hmac_verified": meta.get("hmac_verified"),
        "chain_linked": meta.get("chain_linked"),
        "records": meta.get("records"),
        "queue": {
            "available": True,
            "kind": meta.get("kind") or "OK",
            "jobs": rows,
            "counts": counts,
        },
        "note": (
            "Scheduler projection. Legal words: QUEUED RUNNING BROKE CLEAN "
            "FINDINGS. stale is a flag (report-never-retry). GET does not "
            "mutate. Untagged product=UNATTRIBUTED stage=UNMEASURED."
        ),
    }
    return body


def _refuse(kind: str, detail: str, tree_id: str | None = None) -> tuple[int, dict]:
    if kind in PATH_KINDS:
        code = 409
    elif kind == "PATHS_ERROR":
        code = 503
    else:
        code = 200
    body = {
        "schema": SCHEMA,
        "ok": False,
        "error": kind,
        "kind": kind,
        "detail": str(detail)[:300],
        "queue": {"available": False, "kind": kind, "jobs": None},
    }
    if tree_id is not None:
        body["tree_id"] = tree_id
    return code, body


def handle_get(root: str, expected_tree_id: str | None = None,
               kernel=None) -> tuple[int, dict]:
    """Rich queue fold. `kernel` is optional — Core passes it so /jukebox
    and /jobs share one Scheduler projection. Disk fold is the fallback.
    GET never mutates."""
    now = time.time()
    try:
        if kernel is not None and getattr(kernel, "paths", None) is not None:
            paths = kernel.paths
            if (expected_tree_id is not None
                    and paths.sentinel.tree_id != expected_tree_id):
                raise CosmosPathError(
                    "IDENTITY_MISMATCH",
                    "sentinel tree_id=%r != expected %r" % (
                        paths.sentinel.tree_id, expected_tree_id))
        else:
            paths = CosmosPaths(root, expected_tree_id=expected_tree_id)
        tree_id = paths.sentinel.tree_id
        queue = paths.role("queue")
    except CosmosPathError as e:
        return _refuse(e.kind if e.kind in PATH_KINDS else "PATHS_ERROR", str(e))
    except Exception as e:  # noqa: BLE001
        return 503, {
            "ok": False,
            "error": "PATHS_ERROR",
            "detail": "%s: %s" % (type(e).__name__, e),
            "queue": {"available": False, "kind": "PATHS_ERROR", "jobs": None},
        }

    try:
        if kernel is not None and getattr(kernel, "sched", None) is not None:
            raw = kernel.sched._state()
            state = raw if isinstance(raw, dict) else {}
            meta = {
                "hmac_verified": True,
                "chain_linked": True,
                "records": None,
                "kind": "OK",
            }
        else:
            key = None
            keyfile = paths.config("install_key.bin")
            if keyfile.is_file():
                try:
                    key = keyfile.read_bytes()
                except OSError:
                    key = None
            state, meta = _bind_state(queue, key)
        rows = [_row(jid, v, queue, now)
                for jid, v in state.items()
                if isinstance(v, dict)]
        rows.sort(key=_sort_key)
        return 200, _pack(tree_id, rows, meta, now)
    except JukeboxPanelError as e:
        code, body = _refuse(e.kind, str(e), tree_id)
        return code, body
    except LedgerError as e:
        return _refuse("LEDGER_REFUSED", "%s: %s" % (e.kind, e), tree_id)
