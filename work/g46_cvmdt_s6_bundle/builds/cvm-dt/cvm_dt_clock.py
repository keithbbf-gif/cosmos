#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cvm-dt native OWN-CLOCK — windowless driver of cvm_dt_client --loop.

The Windows Task Scheduler clock carries the overhead (canon: NEVER a
Claude loop). This satellite:

  * ticks CvmDtClient.cycle_once (HTTP stack lives on the client)
  * heartbeats logs/cvm_dt_clock_heartbeat.json on EVERY tick
    (pass, idle, paused, refused) — last_run_epoch schema matches
    cosmos_runner_heartbeat.json so staleness is measurable
  * honors the same HOLD / RESUME-GATE PAUSE.flag the runners read
    (idle the cycle, keep the heartbeat — paused != dead)
  * skip_alive by unique clock_id so a second --loop no-ops
  * --once is a commanded drain (even while paused); it does not
    take the loop lock (same contract as cosmos_node_worker)
  * --register EMITS the schtasks /Create line and does NOT run it
    (Keith runs COSMOS himself; no bats)

Dead Core is UNREACHABLE and still heartbeats. Never fake-alive.

    py -3.14 builds\\cvm-dt\\cvm_dt_clock.py --root <RUNTIME> --once
    py -3.14 builds\\cvm-dt\\cvm_dt_clock.py --root <RUNTIME> --loop
    py -3.14 builds\\cvm-dt\\cvm_dt_clock.py --root <RUNTIME> --register
    py -3.14 builds\\cvm-dt\\cvm_dt_clock.py --root <RUNTIME> --status
    py -3.14 builds\\cvm-dt\\test_cvm_dt_clock.py

rc=0 is not the gate. Runtime-binding value (named, not claimed):
heartbeat last_run_epoch advances across two native ticks AND
state/cvm/pull.json cursor advances under this clock with NO human
turn and NO Claude process running. Software proof this slice: the
heartbeat file is emitted with a fresh epoch and CLOCK_ID is one value.
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
_COSMOS_LIB = _HERE.parents[2] / "cosmos"
if _COSMOS_LIB.is_dir() and str(_COSMOS_LIB) not in sys.path:
    sys.path.insert(0, str(_COSMOS_LIB))

from cosmos_clock import (  # noqa: E402
    acquire_lock, heartbeat_age_s, pid_alive, plan_create, pythonw_exe,
    read_heartbeat, tr_cmdline, write_heartbeat,
)
from cosmos_paths import CosmosPaths  # noqa: E402

from cvm_dt import (  # noqa: E402
    CLIENT_ID, CoreClient, CvmDtError, RefusalKind,
    load_paths, load_token, pull_url,
)
from cvm_dt_client import CvmDtClient  # noqa: E402
from cvm_pull import PULL_INTERVAL_S  # noqa: E402

WORKER = "cvm-dt-clock"
SCHEMA = "cvm-dt-clock/1"
# Own id. CLOCKS: 15=pool, 16=cvm satellite (pull.json issuer), 17=work_order.
CLOCK_ID = 18
TASK_NAME = "COSMOS CVM DT Clock"
TASK_NAME_LOGON = "COSMOS CVM DT Clock Logon"
HEARTBEAT_NAME = "cvm_dt_clock_heartbeat.json"
LOCK_NAME = "cvm_dt_clock.lock"
DEFAULT_BASE = "http://127.0.0.1:8770"
DEFAULT_INTERVAL_S = PULL_INTERVAL_S  # 15s inner; schtasks floor is 1 min
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
    """Second --loop of THIS clock-id no-ops when the holder pid is alive."""
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


def _stamp(paths: CosmosPaths, extra: dict, polls: int,
           interval_s: float) -> dict:
    """One cosmos_runner-shaped heartbeat. Always. extra is the mode payload."""
    hb_path = paths.logs(HEARTBEAT_NAME)
    hb_path.parent.mkdir(parents=True, exist_ok=True)
    extra.setdefault("schema", SCHEMA)
    extra.setdefault("clock_id", CLOCK_ID)
    hb = write_heartbeat(hb_path, WORKER, extra=extra,
                         polls=polls, interval_s=interval_s)
    extra["heartbeat"] = hb
    extra["heartbeat_path"] = str(hb_path)
    extra["last_run_epoch"] = hb["last_run_epoch"]
    return extra


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
        **_pause_extra(paused),
    }
    if paused and paused.get("read_error"):
        extra["ok"] = False
        extra["tick"] = "error"
        extra["state"] = "REFUSED"
        extra["kind"] = str(RefusalKind.CONTROL_BLOCKED)
        extra["detail"] = str(paused.get("read_error"))[:300]
        return _stamp(paths, extra, polls, interval_s)
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
        rec = client.cycle_once()
        extra["tick"] = "pulled"
        extra["ok"] = True
        extra["cursor"] = rec.get("cursor")
        extra["cursor_prev"] = rec.get("cursor_prev")
        extra["cursor_advanced"] = rec.get("cursor_advanced")
        extra["audio_owner"] = rec.get("audio_owner")
        extra["live_value"] = rec.get("live_value")
        extra["cycle"] = {
            k: rec.get(k) for k in (
                "folded", "handoff_granted", "handoff_replayed",
                "grant_count", "quoted_audio_owner", "quoted_cursor",
            )
        }
        ck = (rec.get("live_value") or {}).get("core_kind") or rec.get("core_kind")
        if ck:
            extra["core_kind"] = ck
            extra["core_ready"] = str(ck).upper() not in (
                "UNREACHABLE", "CLOCK_STALE", "AUTH_REQUIRED")
    except CvmDtError as e:
        extra["ok"] = False
        extra["tick"] = "error"
        extra["state"] = "REFUSED"
        extra["kind"] = str(e.kind)
        extra["detail"] = str(e)[:300]
        if str(e.kind) == "UNREACHABLE":
            extra["core_kind"] = "UNREACHABLE"
            extra["core_ready"] = False
    except Exception as e:                                            # noqa: BLE001
        import traceback
        tb = traceback.format_exc()
        try:
            paths.logs("cvm_dt_clock.err").write_text(tb, encoding="utf-8")
        except OSError:
            pass
        extra["ok"] = False
        extra["tick"] = "error"
        extra["state"] = "REFUSED"
        extra["kind"] = str(RefusalKind.BAD_CORE)
        extra["detail"] = ("%s: %s" % (type(e).__name__, e))[:300]
        extra["error"] = tb[-500:]
    return _stamp(paths, extra, polls, interval_s)


def loop(root: str, interval_s: float = DEFAULT_INTERVAL_S, *,
         base: str = DEFAULT_BASE, client_id: str = CLIENT_ID,
         handoff_request_id: Optional[str] = None) -> int:
    """Detached pythonw --loop body. Windowless; lock + skip_alive."""
    paths = load_paths(root)
    out_path = paths.logs("cvm_dt_clock.out")
    lock_path = paths.logs(LOCK_NAME)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    log_fh = open(out_path, "a", encoding="utf-8", buffering=1)
    sys.stdout = log_fh
    sys.stderr = log_fh
    fd = acquire_lock(lock_path)
    if fd is None:
        rec = skip_alive(paths)
        if rec is not None:
            age = heartbeat_age_s(rec)
            print(json.dumps({
                "already_running": True,
                "clock_id": rec.get("clock_id"),
                "pid": rec.get("pid"),
                "age_s": None if age is None else round(age, 3),
            }), flush=True)
            return 0
        print("cvm-dt-clock lock held and holder not skip_alive - refusing",
              flush=True)
        return 2
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
            poll_once(root, polls=polls, interval_s=interval_s,
                      base=base, client_id=client_id,
                      handoff_request_id=handoff_request_id,
                      client=client)
            time.sleep(float(interval_s))
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
    paths = load_paths(root)
    rec = read_heartbeat(paths.logs(HEARTBEAT_NAME))
    age = heartbeat_age_s(rec)
    return {
        "path": str(paths.logs(HEARTBEAT_NAME)),
        "age_s": age,
        "clock_id": None if rec is None else rec.get("clock_id"),
        "fresh": age is not None and age < FRESH_S,
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
        return 0 if rec.get("fresh") else 2
    hid = ns.handoff_request_id or None
    if ns.once:
        rec = poll_once(ns.root, interval_s=ns.interval, base=ns.base,
                        client_id=ns.client_id, handoff_request_id=hid,
                        drain=True)
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
