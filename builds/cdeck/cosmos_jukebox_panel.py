#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_jukebox_panel — GET /api/v1/jukebox (scheduler truth fold).

Legal job states (scheduler words only): QUEUED, RUNNING, BROKE, CLEAN, FINDINGS.
Terminal outcomes from ``cosmos_sched.OUTCOMES`` map 1:1; compatibility aliases
``state`` (= ``st``), ``DONE``→CLEAN, ``FAILED``→BROKE, ``COMPLETED``→CLEAN.

Response shape (documented, stable for Gitur / Review / Runs / Studio):

    {
      "schema": "cdeck-jukebox/1",
      "ok": true,
      "tree_id": "<sentinel>",
      "measured_at": <epoch>,
      "records": <ledger lines folded>,
      "hmac_verified": <bool>,
      "chain_linked": <bool>,
      "counts": { "QUEUED": n, "RUNNING": n, "FINDINGS": n, "BROKE": n, "CLEAN": n,
                  "stale_flagged": n },
      "queue": {
        "available": <bool>,
        "kind": <null | TOO_LARGE | MALFORMED | LEDGER_REFUSED | UNREADABLE>,
        "total": n,
        "shown": n,
        "counts": { ... same five words + stale_flagged ... },
        "jobs": [ { "job_id", "st", "state", "command", "priority", "lane",
                    "age_s", "stale_flag", "manifest_present", "stage"? }, ... ]
      }
    }

``counts`` is duplicated at the top level for older consumers. Empty queue:
``available`` true, every legal count **0** (never UNMEASURED as 0). Oversize
ledger (``MAX_LEDGER_BYTES``): ``kind=TOO_LARGE``, no counts. Malformed line in
the middle: ``kind=MALFORMED``, no counts. ``prev_sha`` break: ``chain_linked``
false, detail names ``prev_sha``, queue still folded. Report-never-retry: stale
is ``stale_flag`` on RUNNING, not a rerun. GET never mutates. No cancel/hold.
"""
from __future__ import annotations

import hashlib
import hmac as hmac_mod
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "cosmos"))

from cosmos_ledger import LedgerError  # noqa: E402
from cosmos_paths import CosmosPaths  # noqa: E402
from cosmos_sched import OUTCOMES  # noqa: E402

SCHEMA = "cdeck-jukebox/1"
MAX_LEDGER_BYTES = 8 * 1024 * 1024
LEGAL = frozenset({"QUEUED", "RUNNING", "BROKE", "CLEAN", "FINDINGS"})
_ALIASES = {
    "DONE": "CLEAN",
    "COMPLETED": "CLEAN",
    "FAILED": "BROKE",
    "ERROR": "BROKE",
}
_SHOWN_LIMIT = 50


def _canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sign(key: bytes, seq: int, prev_sha: str, payload_sha: str) -> str:
    msg = f"{seq}|{prev_sha}|{payload_sha}".encode("utf-8")
    return hmac_mod.new(key, msg, hashlib.sha256).hexdigest()


def _empty_counts() -> dict[str, int]:
    return {w: 0 for w in ("QUEUED", "RUNNING", "FINDINGS", "BROKE", "CLEAN")} | {
        "stale_flagged": 0,
    }


def _normalize_st(raw: str | None) -> str:
    st = str(raw or "QUEUED").upper()
    st = _ALIASES.get(st, st)
    return st if st in LEGAL else "BROKE"


def _bind(paths: CosmosPaths) -> tuple[Path, bytes]:
    keyfile = paths.config("install_key.bin")
    if not keyfile.is_file():
        raise FileNotFoundError("install_key.bin missing")
    ledger = paths.role("queue") / "sched_ledger.jsonl"
    return ledger, keyfile.read_bytes()


def _fold_ledger(path: Path, key: bytes) -> dict:
    """Fold sched_ledger.jsonl. Does not silently vanish on a hole."""
    if not path.is_file():
        return {
            "kind": None,
            "records": [],
            "records_n": 0,
            "chain_linked": True,
            "hmac_verified": True,
            "detail": None,
        }
    try:
        size = path.stat().st_size
    except OSError as e:
        return {
            "kind": "UNREADABLE",
            "records": [],
            "records_n": 0,
            "chain_linked": False,
            "hmac_verified": False,
            "detail": str(e)[:200],
        }
    if size > MAX_LEDGER_BYTES:
        return {
            "kind": "TOO_LARGE",
            "records": [],
            "records_n": 0,
            "chain_linked": False,
            "hmac_verified": False,
            "detail": f"{size} bytes > MAX_LEDGER_BYTES={MAX_LEDGER_BYTES}",
        }
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as e:
        return {
            "kind": "UNREADABLE",
            "records": [],
            "records_n": 0,
            "chain_linked": False,
            "hmac_verified": False,
            "detail": str(e)[:200],
        }

    records: list[dict] = []
    prev_sha = ""
    chain_linked = True
    hmac_verified = True
    detail = None

    for i, ln in enumerate(lines, 1):
        if not ln.strip():
            continue
        try:
            rec = json.loads(ln)
        except ValueError as e:
            return {
                "kind": "MALFORMED",
                "records": [],
                "records_n": 0,
                "chain_linked": False,
                "hmac_verified": False,
                "detail": f"line {i}: {e}"[:200],
            }
        if not isinstance(rec, dict) or "payload" not in rec:
            return {
                "kind": "MALFORMED",
                "records": [],
                "records_n": 0,
                "chain_linked": False,
                "hmac_verified": False,
                "detail": f"line {i}: not a ledger record"[:200],
            }
        body = _canon(rec["payload"])
        if (
            rec.get("payload_len") != len(body)
            or rec.get("payload_sha") != hashlib.sha256(body).hexdigest()
        ):
            return {
                "kind": "MALFORMED",
                "records": [],
                "records_n": 0,
                "chain_linked": False,
                "hmac_verified": False,
                "detail": f"line {i}: payload hash mismatch"[:200],
            }
        if rec.get("prev_sha") != prev_sha:
            chain_linked = False
            if detail is None:
                detail = f"prev_sha mismatch at line {i}"
        good = _sign(key, int(rec.get("seq") or 0), rec.get("prev_sha") or "", rec["payload_sha"])
        got = rec.get("hmac") or ""
        ok = hmac_mod.compare_digest(good, got) or (
            len(got) == 32 and hmac_mod.compare_digest(good[:32], got)
        )
        if not ok:
            hmac_verified = False
        records.append(rec)
        prev_sha = hashlib.sha256(ln.encode("utf-8")).hexdigest()

    return {
        "kind": None,
        "records": records,
        "records_n": len(records),
        "chain_linked": chain_linked,
        "hmac_verified": hmac_verified,
        "detail": detail,
    }


def _project(records: list[dict]) -> dict:
    def fold(state, rec):
        p, e = rec["payload"], rec["event"]
        jid = p.get("job_id")
        if not jid:
            return state
        if e == "JOB_SUBMITTED":
            state[jid] = {"m": p, "st": "QUEUED", "by": None, "claimed": None,
                          "stale_reported": False}
        elif e == "JOB_CLAIMED" and state.get(jid, {}).get("st") == "QUEUED":
            state[jid].update(st="RUNNING", by=p.get("worker"), claimed=rec.get("t"))
        elif e == "JOB_DONE" and jid in state:
            outcome = _normalize_st(p.get("outcome"))
            if outcome not in OUTCOMES:
                outcome = "BROKE"
            state[jid].update(st=outcome, by=p.get("worker"))
        elif e == "JOB_STALE" and jid in state:
            state[jid]["stale_reported"] = True
        return state

    state: dict = {}
    for rec in records:
        state = fold(state, rec)
    return state


def _manifest(paths: CosmosPaths, job_id: str) -> tuple[dict | None, bool]:
    mp = paths.role("queue") / "manifests" / f"{job_id}.json"
    if not mp.is_file():
        return None, False
    try:
        obj = json.loads(mp.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None, True
    return (obj if isinstance(obj, dict) else {}), True


def _rows(paths: CosmosPaths, state: dict, now: float) -> list[dict]:
    """Manifest on disk wins command/priority; gone file does not vanish the job."""
    rows = []
    for jid, v in state.items():
        m = dict(v.get("m") or {})
        m.setdefault("job_id", jid)
        file_m, present = _manifest(paths, jid)
        cmd = m.get("command")
        priority = m.get("priority")
        lane = m.get("lane")
        stage = None
        if file_m:
            cmd = file_m.get("command") or file_m.get("task") or cmd
            priority = file_m.get("priority", priority)
            lane = file_m.get("lane", lane)
            stage = file_m.get("stage") or file_m.get("motif_stage")
        st = _normalize_st(v.get("st"))
        submitted = m.get("submitted")
        claimed = v.get("claimed")
        age_base = claimed if st == "RUNNING" and claimed else submitted
        age_s = None if age_base is None else round(max(0.0, now - float(age_base)), 1)
        timeout_s = m.get("timeout_s")
        stale_flag = bool(v.get("stale_reported"))
        if (
            not stale_flag
            and st == "RUNNING"
            and timeout_s is not None
            and age_base is not None
            and now - float(age_base) > float(timeout_s)
        ):
            stale_flag = True
        row = {
            "job_id": jid,
            "st": st,
            "state": st,
            "command": cmd,
            "priority": priority,
            "lane": lane or "default",
            "age_s": age_s,
            "stale_flag": stale_flag,
            "manifest_present": present,
            "submitted": submitted,
        }
        if stage:
            row["stage"] = stage
        rows.append(row)
    rows.sort(key=lambda r: (
        {"RUNNING": 0, "QUEUED": 1, "FINDINGS": 2, "BROKE": 3, "CLEAN": 4}.get(r["st"], 9),
        -(r.get("priority") or 0) if isinstance(r.get("priority"), (int, float)) else 0,
        r.get("job_id") or "",
    ))
    return rows


def _counts(jobs: list[dict]) -> dict[str, int]:
    c = _empty_counts()
    for j in jobs:
        st = j.get("st")
        if st in LEGAL:
            c[st] += 1
        if j.get("stale_flag"):
            c["stale_flagged"] += 1
    return c


def handle_get(root: str, expected_tree_id: str | None = None) -> tuple[int, dict]:
    try:
        paths = CosmosPaths(root, expected_tree_id=expected_tree_id)
        tree_id = paths.sentinel.tree_id
    except Exception as e:  # noqa: BLE001
        return 503, {"ok": False, "error": "PATHS_ERROR", "detail": str(e)[:200]}

    now = time.time()
    try:
        ledger_path, key = _bind(paths)
    except FileNotFoundError as e:
        return 503, {"ok": False, "error": "PATHS_ERROR", "detail": str(e)[:200]}
    except OSError as e:
        return 503, {"ok": False, "error": "PATHS_ERROR", "detail": str(e)[:200]}

    try:
        folded = _fold_ledger(ledger_path, key)
    except LedgerError as e:
        folded = {
            "kind": "LEDGER_REFUSED",
            "records": [],
            "records_n": 0,
            "chain_linked": False,
            "hmac_verified": False,
            "detail": f"{e.kind}: {e}"[:200],
        }

    kind = folded.get("kind")
    if kind in ("TOO_LARGE", "MALFORMED", "UNREADABLE", "LEDGER_REFUSED"):
        return 200, {
            "schema": SCHEMA,
            "ok": True,
            "tree_id": tree_id,
            "measured_at": now,
            "records": folded.get("records_n", 0),
            "hmac_verified": folded.get("hmac_verified"),
            "chain_linked": folded.get("chain_linked"),
            "detail": folded.get("detail"),
            "queue": {
                "available": False,
                "kind": kind,
                "total": 0,
                "shown": 0,
                "jobs": [],
            },
        }

    state = _project(folded.get("records") or [])
    jobs = _rows(paths, state, now)
    counts = _counts(jobs)
    shown = jobs[:_SHOWN_LIMIT]

    body = {
        "schema": SCHEMA,
        "ok": True,
        "tree_id": tree_id,
        "measured_at": now,
        "records": folded.get("records_n", 0),
        "hmac_verified": bool(folded.get("hmac_verified")),
        "chain_linked": bool(folded.get("chain_linked")),
        "counts": dict(counts),
        "queue": {
            "available": True,
            "kind": None,
            "total": len(jobs),
            "shown": len(shown),
            "counts": dict(counts),
            "jobs": shown,
        },
        # compatibility aliases (legacy flat consumers)
        "jobs_n": len(jobs),
        "in_flight_n": counts["QUEUED"] + counts["RUNNING"],
        "broke_n": counts["BROKE"],
        "done_n": counts["CLEAN"] + counts["FINDINGS"],
        "jobs": shown,
    }
    if folded.get("detail"):
        body["detail"] = folded["detail"]
    return 200, body
