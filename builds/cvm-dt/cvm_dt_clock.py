#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cvm-dt native OWN-CLOCK — windowless driver of cvm_dt_client --loop.

The Windows Task Scheduler clock carries the overhead (canon: NEVER a
Claude loop). This satellite:

  * ticks CvmDtClient.cycle_once (GET /cvm/pull drain-fold + desktop stamp)
  * 2 s idle heartbeat; Core GET coalesces when idle. Speech is a local
    VAD/STT interrupt (not a GET burst); backlog>0 still drains GET
  * heartbeats live/logs/cvm_dt_clock_heartbeat.json on EVERY tick
    (pass, idle, paused, refused) — last_run_epoch schema matches
    cosmos_runner_heartbeat.json so staleness is measurable
  * honors the same HOLD / RESUME-GATE PAUSE.flag the runners read
    (idle the cycle, keep the heartbeat — paused != dead)
  * skip_alive by unique clock_id so a second --once/--loop no-ops
  * --register EMITS the schtasks /Create line and does NOT run it
    (Keith runs COSMOS himself; no bats)

    py -3.14 builds\\cvm-dt\\cvm_dt_clock.py --root <RUNTIME> --once
    py -3.14 builds\\cvm-dt\\cvm_dt_clock.py --root <RUNTIME> --loop
    py -3.14 builds\\cvm-dt\\cvm_dt_clock.py --root <RUNTIME> --register
    py -3.14 builds\\cvm-dt\\cvm_dt_clock.py --root <RUNTIME> --status
    py -3.14 builds\\cvm-dt\\test_cvm_dt_clock.py

rc=0 is not the gate. Runtime-binding value (named, not claimed):
a POST /api/v1/cvm/push phone turn appears in the desktop-owned
GET /api/v1/cvm/pull view with the advanced cursor under this clock
(CLOCK_ID == PULL_CLOCK_ID 18, --once lock). Heartbeat last_run_epoch
advances too. live/logs/cvm_dt_clock_heartbeat.json is written EVERY tick.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
# Same hop as cvm_dt.py: file is builds/cvm-dt/*.py → repo/cosmos.
_COSMOS_LIB = Path(__file__).resolve().parents[2] / "cosmos"
if _COSMOS_LIB.is_dir() and str(_COSMOS_LIB) not in sys.path:
    sys.path.insert(0, str(_COSMOS_LIB))

from cosmos_clock import (  # noqa: E402
    acquire_lock, heartbeat_age_s, pid_alive, plan_create, pythonw_exe,
    query_task, read_heartbeat, tr_cmdline, write_heartbeat,
)
from cosmos_cvm_push import PULL_CLOCK_ID, cadence_wait, voice_state  # noqa: E402
from cosmos_paths import CosmosPaths  # noqa: E402

from cvm_dt import (  # noqa: E402
    CLIENT_ID, CoreClient, CvmDtError, RefusalKind,
    load_paths, load_token, pull_url,
)
from cvm_dt_client import CvmDtClient  # noqa: E402
from cvm_pull import DRAIN_IDLE_S  # noqa: E402

WORKER = "cvm-dt-clock"
SCHEMA = "cvm-dt-clock/1"
# CLOCKS registry: 15=pool, 16=CVM satellite (audio/ux; defers pull.json),
# 17=work_order. pull.json.clock_id is PULL_CLOCK_ID — one truth.
CLOCK_ID = PULL_CLOCK_ID
TASK_NAME = "COSMOS CVM DT Clock"
TASK_NAME_LOGON = "COSMOS CVM DT Clock Logon"
HEARTBEAT_NAME = "cvm_dt_clock_heartbeat.json"
LOCK_NAME = "cvm_dt_clock.lock"
DEFAULT_BASE = "http://127.0.0.1:8770"
DEFAULT_INTERVAL_S = DRAIN_IDLE_S  # 2s drain idle; schtasks floor is 1 min
FRESH_S = 60.0


def pause_flag(paths: CosmosPaths) -> dict | None:
    """Same contract as cosmos_node_worker.pause_flag (the flag runners read)."""
    p = paths.state("control", "PAUSE.flag")
    if not p.exists() or not p.is_file():
        return None
    rec: dict = {"path": str(p), "state": "PAUSED"}
    try:
        raw = p.read_text(encoding="utf-8").strip()
    except OSError as e:
        rec["read_error"] = str(e)
        return rec
    if raw.startswith("{"):
        try:
            obj = json.loads(raw)
        except ValueError:
            obj = None
        if isinstance(obj, dict):
            rec.update(obj)
            rec.setdefault("state", "PAUSED")
            rec["path"] = str(p)
            return rec
    rec["reason"] = raw[:240] or "(empty flag file)"
    return rec


def is_paused(paused: dict | None) -> bool:
    """Same contract as cosmos_node_worker.is_paused. HOLD never self-clears.

    RESUME-GATE stays paused here until WD2 unlinks the flag at
    auto_resume_at — this clock does not steal the clearer.
    """
    if paused is None:
        return False
    return str(paused.get("state") or "PAUSED").upper() != "RUNNING"


def skip_alive(paths: CosmosPaths, clock_id: int = CLOCK_ID) -> dict | None:
    """Second launch of THIS clock-id no-ops when the holder pid is alive."""
    rec = read_heartbeat(paths.logs(HEARTBEAT_NAME))
    if not rec or rec.get("clock_id") != clock_id:
        return None
    try:
        pid = int(rec.get("pid") or 0)
    except (TypeError, ValueError):
        return None
    if not pid_alive(pid):
        return None
    return rec


def _pause_extra(paused: dict | None) -> dict:
    if paused is None:
        return {"pause_present": False, "pause_mode": None,
                "auto_resume_at": None}
    return {
        "pause_present": True,
        "pause_mode": paused.get("mode") or "hold",
        "auto_resume_at": paused.get("auto_resume_at"),
    }


def _refuse(extra: dict, kind: RefusalKind | str, detail: object) -> dict:
    extra["ok"] = False
    extra["tick"] = "refused"
    extra["state"] = "REFUSED"
    extra["kind"] = str(kind)
    extra["detail"] = str(detail)[:300]
    return extra


def _stamp(paths: CosmosPaths, extra: dict, polls: int,
           interval_s: float) -> dict:
    hb_path = paths.logs(HEARTBEAT_NAME)
    hb = write_heartbeat(hb_path, WORKER, extra=extra,
                         polls=polls, interval_s=interval_s)
    extra["heartbeat"] = hb
    extra["heartbeat_path"] = str(hb_path)
    extra["last_run_epoch"] = hb["last_run_epoch"]
    return extra


def _locked(paths: CosmosPaths):
    """acquire_lock. On conflict: skip_alive no-op (None, 0) or refuse (None, 2)."""
    fd = acquire_lock(paths.logs(LOCK_NAME))
    if fd is not None:
        return fd, None
    rec = skip_alive(paths)
    if rec is None:
        print("cvm-dt-clock lock held and holder not skip_alive - refusing",
              flush=True)
        return None, 2
    age = heartbeat_age_s(rec)
    print(json.dumps({
        "already_running": True, "clock_id": rec.get("clock_id"),
        "pid": rec.get("pid"),
        "age_s": None if age is None else round(age, 3),
    }, indent=1, default=str), flush=True)
    return None, 0


def poll_once(root: str, *, polls: int = 0,
              interval_s: float = DEFAULT_INTERVAL_S,
              base: str = DEFAULT_BASE, client_id: str = CLIENT_ID,
              handoff_request_id: Optional[str] = None,
              client: Optional[CvmDtClient] = None,
              drain: Optional[bool] = None) -> dict:
    """One tick. Heartbeat ALWAYS (pass / idle / paused / refused)."""
    paths = load_paths(root)
    paused = pause_flag(paths)
    paused_now = is_paused(paused)
    if drain is None:
        drain = not paused_now

    extra: dict = {
        "schema": SCHEMA,
        "tick": "poll",
        "state": "RUNNING",
        "tree_id": paths.sentinel.tree_id,
        "clock_id": CLOCK_ID,
        "quoted_from": pull_url(client_id),
        "voice_state": voice_state(),
        **_pause_extra(paused),
    }
    if paused and paused.get("read_error"):
        return _stamp(paths, _refuse(
            extra, RefusalKind.CONTROL_BLOCKED, paused.get("read_error")),
                      polls, interval_s)
    if paused_now and not drain:
        extra["ok"] = True
        extra["tick"] = "paused"
        extra["state"] = "PAUSED"
        return _stamp(paths, extra, polls, interval_s)
    if paused_now:
        extra["tick"] = "once_while_paused"

    try:
        if client is None:
            client = CvmDtClient(
                CoreClient(base, load_token(paths)), paths, client_id,
                handoff_request_id=handoff_request_id)
        t0 = time.perf_counter()
        rec = client.cycle_once()
        tick_ms = rec.get("tick_ms")
        if tick_ms is None:
            tick_ms = round((time.perf_counter() - t0) * 1000.0, 3)
        extra["tick"] = "coalesced" if rec.get("skipped_http") else "pulled"
        extra["ok"] = True
        extra["cursor"] = rec.get("cursor")
        extra["cursor_prev"] = rec.get("cursor_prev")
        extra["cursor_advanced"] = rec.get("cursor_advanced")
        extra["audio_owner"] = rec.get("audio_owner")
        extra["pull_ms"] = rec.get("pull_ms")
        extra["backlog"] = rec.get("backlog")
        extra["drain_lag_ms"] = rec.get("drain_lag_ms")
        extra["tick_ms"] = tick_ms
        extra["skipped_http"] = bool(rec.get("skipped_http"))
        extra["cadence_mode"] = rec.get("cadence_mode")
        extra["speech_live"] = rec.get("speech_live")
        extra["pcm_sha256"] = rec.get("pcm_sha256")
        extra["first_word_ms"] = rec.get("first_word_ms")
        extra["stt_kind"] = rec.get("stt_kind")
        extra["voice_state"] = rec.get("voice_state") or voice_state()
        extra["live_value"] = rec.get("live_value")
        extra["cycle"] = {
            k: rec.get(k) for k in (
                "folded", "handoff_granted", "handoff_replayed",
                "grant_count", "quoted_audio_owner", "quoted_cursor",
                "pull_ms", "backlog", "drain_lag_ms",
                "tick_ms", "skipped_http", "cadence_mode", "speech_live",
                "first_word_ms", "stt_kind", "voice_state",
            )
        }
    except CvmDtError as e:
        _refuse(extra, e.kind, e)
    except Exception as e:                                            # noqa: BLE001
        _refuse(extra, RefusalKind.BAD_CORE,
                "%s: %s" % (type(e).__name__, e))
    return _stamp(paths, extra, polls, interval_s)


def loop(root: str, interval_s: float = DEFAULT_INTERVAL_S, *,
         base: str = DEFAULT_BASE, client_id: str = CLIENT_ID,
         handoff_request_id: Optional[str] = None) -> int:
    """Detached pythonw --loop body. Windowless; lock + skip_alive."""
    paths = load_paths(root)
    out_path = paths.logs("cvm_dt_clock.out")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    log_fh = open(out_path, "a", encoding="utf-8", buffering=1)
    sys.stdout = log_fh
    sys.stderr = log_fh
    fd, rc = _locked(paths)
    if fd is None:
        return rc
    client = CvmDtClient(
        CoreClient(base, load_token(paths)), paths, client_id,
        handoff_request_id=handoff_request_id)
    polls = 0
    print(json.dumps({"loop": True, "pid": os.getpid(),
                      "interval_s": interval_s, "clock_id": CLOCK_ID,
                      "windowless": Path(pythonw_exe()).name.lower().startswith(
                          "pythonw")}, indent=1), flush=True)
    try:
        while True:
            polls += 1
            rec = poll_once(root, polls=polls, interval_s=interval_s,
                            base=base, client_id=client_id,
                            handoff_request_id=handoff_request_id,
                            client=client)
            cadence_wait(rec, interval_s, paths=paths,
                         tree_id=paths.sentinel.tree_id)
    finally:
        os.close(fd)
    return 0


def register(root: str) -> dict:
    """Emit schtasks /Create lines. Do NOT run them (no bats; Keith does)."""
    paths = load_paths(root)
    script = Path(__file__).resolve()
    tr = tr_cmdline(script, str(paths.root), "--loop")
    minute = plan_create(TASK_NAME, tr, "minute", mo=1)
    logon = plan_create(TASK_NAME_LOGON, tr, "onlogon")
    cmds = [subprocess.list2cmdline(a) for a in (minute, logon)]
    return {
        "ok": True,
        "ran": False,
        "clock_id": CLOCK_ID,
        "task_name": TASK_NAME,
        "task_logon": TASK_NAME_LOGON,
        "tr": tr,
        "pythonw": pythonw_exe(),
        "keith_cmds": cmds,
        "keith_cmd": " & ".join(cmds),
        "heartbeat": str(paths.logs(HEARTBEAT_NAME)),
        "note": ("EMITTED, not executed. Keith runs COSMOS himself. "
                 "No bats. pythonw --loop + 1-min self-heal + onlogon."),
    }


def status(root: str) -> dict:
    """Freshness AND registration.

    Freshness alone cannot tell "the daemon died" from "no daemon was ever
    scheduled" — and it was the second. This clock sat 3.5 days at
    age_s=315715 with no task registered and nothing to notice, because
    --status only ever asked the heartbeat (CLOCK_POSTMORTEM.md). Quote the
    schtasks answer too: an unregistered clock is a stale clock that will
    STAY stale.
    """
    paths = load_paths(root)
    rec = read_heartbeat(paths.logs(HEARTBEAT_NAME))
    age = heartbeat_age_s(rec)
    registered = bool(query_task(TASK_NAME).get("ok"))
    return {
        "path": str(paths.logs(HEARTBEAT_NAME)),
        "age_s": age,
        "clock_id": None if rec is None else rec.get("clock_id"),
        "fresh": age is not None and age < FRESH_S,
        "task_name": TASK_NAME,
        "registered": registered,
        "logon_registered": bool(query_task(TASK_NAME_LOGON).get("ok")),
        "skip_alive": skip_alive(paths) is not None,
        "heartbeat": rec,
    }


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="cvm-dt-clock")
    ap.add_argument("--root", required=True,
                    help="COSMOS runtime root (handed in; sentinel verified)")
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--client-id", default=CLIENT_ID)
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--register", action="store_true",
                    help="emit schtasks /Create; do not run it")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--interval", type=float, default=DEFAULT_INTERVAL_S)
    ap.add_argument("--handoff-request-id", default="")
    ns = ap.parse_args(argv)
    if not (ns.once or ns.loop or ns.register or ns.status):
        ap.error("one of --once / --loop / --register / --status is required")
    if ns.register:
        rec = register(ns.root)
        print(json.dumps(rec, indent=1, default=str))
        return 0
    if ns.status:
        rec = status(ns.root)
        print(json.dumps(rec, indent=1, default=str))
        # Fail closed: unregistered is a REFUSAL, not a quiet stale reading.
        return 0 if (rec.get("fresh") and rec.get("registered")) else 2
    hid = ns.handoff_request_id or None
    if ns.once:
        fd, rc = _locked(load_paths(ns.root))
        if fd is None:
            return rc
        try:
            rec = poll_once(ns.root, interval_s=ns.interval, base=ns.base,
                            client_id=ns.client_id, handoff_request_id=hid,
                            drain=True)
        finally:
            os.close(fd)
        print(json.dumps({k: rec[k] for k in rec if k != "heartbeat"},
                         indent=1, default=str))
        return 0 if rec.get("ok") else 2
    return loop(ns.root, ns.interval, base=ns.base, client_id=ns.client_id,
                handoff_request_id=hid)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CvmDtError as e:
        print(json.dumps({"ok": False, "kind": str(e.kind), "detail": str(e)},
                         indent=1), file=sys.stderr)
        raise SystemExit(2)
