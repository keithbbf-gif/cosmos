#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_health_clock - FAST (~2s) Core liveness / heartbeat satellite.

Does NOT instantiate Kernel or HealthBoard (those ledger HEALTH_BOARD on every
run — a 2s loop would flood the authority). This clock probes what a 2s OS
dynamic can ask without writing the ledger: sentinel, ledger file, install
key, queue role, :8770 listener, peer-clock heartbeat ages.

    py -3.14 cosmos\\cosmos_health_clock.py --root V:\\A\\Ai\\COSMOS\\live --loop
    py -3.14 cosmos\\cosmos_health_clock.py --root ... --once
    py -3.14 cosmos\\cosmos_health_clock.py --root ... --standup
    py -3.14 cosmos\\cosmos_health_clock.py --root ... --status
    py -3.14 cosmos\\cosmos_health_clock.py --root ... --loop --supervise

--supervise (DEFAULT ON since 2026-08-31; `--no-supervise` to opt out) turns the
observer into Core's missing supervisor: it STARTS `cosmos.py serve` on :8770
when the probe says down. Every other COSMOS subsystem has a clock that restarts
it; Core had only this observer, which had measured the port red 89,082 times
and acted zero times because the registered SCHTASKS action never passed the
opt-in flag. Default-ON is the fix that needs no re-registration: the existing
`COSMOS Health` task action supervises as soon as it reloads this file.

Why Core was down on the REAL root (measured 2026-08-31): the only task that
started Core, `COSMOS_Serve_Watchdog`, runs the out-of-tree
`V:\\Ai\\BTS_MESH\\cosmos_watchdog.py`, hard-coded to ROOT=...\\trylive PORT=8791.
It kept the TRIAL Core (tree_id KMesh-COSMOS-try) alive and returned rc=0 every
2 minutes, so the real root (KMesh-COSMOS-live, :8770) was never served and the
green task hid it. rc=0 is not done. See docs/CORE_SERVE_SUPERVISOR.md.

Task: COSMOS Health. Detached daemon + 1-min self-heal + onlogon relaunch.
The observe path does NOT honor PAUSE (not a retask clock); the --supervise
spawn does. No bts_* import. Does not modify kernel/ledger/sched/service.
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_clock import (  # noqa: E402
    acquire_lock, create_task, heartbeat_age_s, pid_alive, pythonw_exe,
    query_task, read_heartbeat, spawn_detached, tr_cmdline, wait_fresh,
    write_heartbeat, atomic_json,
)
from cosmos_paths import CosmosPaths, CosmosPathError  # noqa: E402

WORKER = "cosmos-health-clock"
TASK_NAME = "COSMOS Health"
TASK_NAME_LOGON = "COSMOS Health Logon"
HEARTBEAT_NAME = "health_clock_heartbeat.json"
LOCK_NAME = "health_clock.lock"
BOARD_NAME = "board.json"
SCHEMA = "cosmos-health-clock/1"
DEFAULT_INTERVAL_S = 2.0
FRESH_S = 8.0
SERVE_PORT = 8770
SERVE_LOCK_NAME = "core_serve.lock"
SERVE_STATE_NAME = "core_serve.json"
# A 2s loop must never storm a failing exec: 15 -> 30 -> 60 -> 120 -> 300s,
# persisted so a clock restart does not reset the ladder.
SERVE_BACKOFF_S = (15, 30, 60, 120, 300)

PEER_HEARTBEATS = (
    "watchdog2_heartbeat.json",
    "collector_heartbeat.json",
    "cosmos_runner_heartbeat.json",
    "motif_driver_heartbeat.json",
    "mesh_discovery_heartbeat.json",
    "cosmos_index_heartbeat.json",
    "cdeck_feed_heartbeat.json",
    "rails_prober_heartbeat.json",
    "spend_meter_heartbeat.json",
    "drive_meter_heartbeat.json",
    "backup_clock_heartbeat.json",
    "ledger_verify_heartbeat.json",
    "cvm_clock_heartbeat.json",
    "cvm_dt_clock_heartbeat.json",
    "cvm_dt_voice_heartbeat.json",
)


def repo_tree() -> Path:
    return Path(__file__).resolve().parent.parent


def _probe_port(host: str, port: int, timeout_s: float = 0.25) -> dict:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout_s)
    t0 = time.time()
    try:
        s.connect((host, port))
        ok = True
        err = None
    except OSError as e:
        ok = False
        err = f"{type(e).__name__}: {e}"
    finally:
        try:
            s.close()
        except OSError:
            pass
    return {"ok": ok, "host": host, "port": port,
            "rtt_s": round(time.time() - t0, 4), "error": err}


def _supervise_serve(paths, up: bool, supervise: bool, pause_present: bool,
                     pause_mode) -> dict:
    """Start Core on :8770 when it is down. THE fix for BACKLOG 'serve not up on
    real root': this clock probed the port ~83k times and started it zero times.
    Opt-in, single-supervisor, backed off, PAUSE-aware; every non-spawn path
    returns a typed `kind` and touches nothing.

    kinds: DISABLED · ALREADY_UP · PAUSED_HOLD · BACKOFF · CHILD_ALIVE ·
           SUPERVISOR_BUSY · SPAWNED · SPAWN_FAILED
    """
    if not supervise:
        return {"kind": "DISABLED", "detail": "--no-supervise set"}
    if up:
        return {"kind": "ALREADY_UP", "detail": "port %d listening" % SERVE_PORT}
    if pause_present and (pause_mode or "hold") == "hold":
        # A HOLD pause waits for a human. A resume-gate pause self-clears and
        # the default is MOTION, so it does not block the standup.
        return {"kind": "PAUSED_HOLD", "detail": "PAUSE mode=hold - no spawn"}
    st_path = paths.logs(SERVE_STATE_NAME)
    try:
        st = json.loads(st_path.read_text(encoding="utf-8"))
        if not isinstance(st, dict):
            st = {}
    except (OSError, ValueError):
        st = {}
    now = time.time()
    try:
        next_at = float(st.get("next_attempt_epoch") or 0)
    except (TypeError, ValueError):
        next_at = 0.0
    if now < next_at:
        return {"kind": "BACKOFF", "fails": st.get("fails", 0),
                "detail": "next attempt in %.0fs" % (next_at - now)}
    pid = st.get("pid")
    pid = int(pid) if isinstance(pid, int) else 0
    if pid_alive(pid):
        # A child exists but the port has not answered yet - or it is wedged.
        # Either way a second Core would be a second writer: refuse, never race.
        return {"kind": "CHILD_ALIVE", "pid": pid,
                "detail": "pid=%d up, port not answering" % pid}
    fd = acquire_lock(paths.logs(SERVE_LOCK_NAME))
    if fd is None:
        return {"kind": "SUPERVISOR_BUSY",
                "detail": "another supervisor holds the Core spawn lock"}
    try:
        core = Path(__file__).resolve().with_name("cosmos.py")
        argv = [pythonw_exe(), str(core), "serve",
                "--root", str(paths.root), "--port", str(SERVE_PORT)]
        try:
            rec = spawn_detached(argv, str(repo_tree()),
                                 paths.logs("core_serve.out"))
        except OSError as e:
            rec = {"ok": False, "error": "%s: %s" % (type(e).__name__, e)}
        ok = bool(rec.get("ok"))
        fails = 0 if ok else int(st.get("fails") or 0) + 1
        back = SERVE_BACKOFF_S[min(max(fails - 1, 0), len(SERVE_BACKOFF_S) - 1)]
        atomic_json(st_path, {"pid": rec.get("pid"), "ok": ok, "argv": argv,
                              "fails": fails, "attempted_epoch": now,
                              "next_attempt_epoch": now + back})
        return {"kind": "SPAWNED" if ok else "SPAWN_FAILED",
                "detail": str(rec.get("error") or rec.get("note") or
                              rec.get("method") or "")[:200],
                "pid": rec.get("pid"), "fails": fails, "backoff_s": back}
    finally:
        os.close(fd)


def poll_once(root: str, polls: int = 0,
              interval_s: float = DEFAULT_INTERVAL_S,
              supervise: bool = True) -> dict:
    paths = CosmosPaths(root)
    logs = paths.logs()
    logs.mkdir(parents=True, exist_ok=True)
    state = paths.state("health")
    state.mkdir(parents=True, exist_ok=True)
    hb_path = logs / HEARTBEAT_NAME
    board_path = state / BOARD_NAME

    rows: dict[str, dict] = {}

    sent = paths.root / ".cosmos-root.json"
    rows["sentinel"] = {
        "ok": sent.is_file(),
        "detail": f"tree_id={paths.sentinel.tree_id}" if sent.is_file()
        else "missing .cosmos-root.json",
    }

    led = paths.ledger("authority.jsonl")
    try:
        st = led.stat() if led.exists() else None
    except OSError as e:
        st = None
        rows["ledger_file"] = {"ok": False, "detail": str(e)}
    if "ledger_file" not in rows:
        if st is None:
            rows["ledger_file"] = {"ok": True,
                                   "detail": "absent (empty history is legal)"}
        else:
            rows["ledger_file"] = {
                "ok": True,
                "detail": f"bytes={st.st_size} mtime_epoch={int(st.st_mtime)}",
                "bytes": int(st.st_size),
            }

    key = paths.config("install_key.bin")
    try:
        key_ok = key.is_file() and key.stat().st_size > 0
    except OSError:
        key_ok = False
    rows["install_key"] = {
        "ok": key_ok,
        "detail": "present" if key_ok else "missing install_key.bin",
    }

    q = paths.role("queue")
    rows["queue"] = {
        "ok": q.is_dir(),
        "detail": str(q),
    }

    pause = paths.role("state") / "control" / "PAUSE.flag"
    pause_present = pause.is_file()
    pause_mode = None
    if pause_present:
        try:
            raw = pause.read_text(encoding="utf-8").strip()
            if raw.startswith("{"):
                obj = json.loads(raw)
                pause_mode = obj.get("mode") if isinstance(obj, dict) else None
        except (OSError, ValueError):
            pause_mode = None
    rows["pause_flag"] = {
        "ok": True,  # presence is a state, not a fault
        "present": pause_present,
        "mode": pause_mode,
        "detail": ("PAUSED mode=%s" % (pause_mode or "hold")
                   if pause_present else "RUNNING (no flag)"),
    }

    sock = _probe_port("127.0.0.1", SERVE_PORT)
    rows["serve_8770"] = {
        "ok": sock["ok"],
        "detail": ("listening rtt_s=%s" % sock["rtt_s"] if sock["ok"]
                   else sock.get("error") or "not listening"),
        "rtt_s": sock["rtt_s"],
    }

    # Observer -> supervisor, opt-in only. With --supervise off nothing is read,
    # written or reported: the running fleet cannot change under anyone.
    sup = None
    if supervise:
        sup = _supervise_serve(paths, sock["ok"], supervise, pause_present,
                               pause_mode)
        rows["serve_supervisor"] = {
            "ok": sup["kind"] != "SPAWN_FAILED",
            "kind": sup["kind"],
            "detail": ("%s %s" % (sup["kind"], sup.get("detail") or "")).strip(),
        }

    peers = {}
    now = time.time()
    for name in PEER_HEARTBEATS:
        rec = read_heartbeat(logs / name)
        age = heartbeat_age_s(rec, now=now)
        peers[name] = {
            "present": rec is not None,
            "age_s": None if age is None else round(age, 3),
            "pid": (rec or {}).get("pid"),
            "state": (rec or {}).get("state"),
            "alive": pid_alive(int((rec or {}).get("pid") or 0)),
        }
    rows["peer_heartbeats"] = {
        "ok": True,
        "detail": "%d files" % sum(1 for v in peers.values() if v["present"]),
        "peers": peers,
    }

    reds = {n: r for n, r in rows.items()
            if n not in ("pause_flag", "peer_heartbeats", "serve_8770")
            and not r.get("ok")}
    # serve down is a RED but Core may be off by design; still report it.
    if not rows["serve_8770"]["ok"]:
        reds["serve_8770"] = rows["serve_8770"]

    verdict = "GREEN" if not reds else "RED x%d" % len(reds)
    extra = {
        "schema": SCHEMA,
        "tick": "once",
        "state": "RUNNING",
        "verdict": verdict,
        "reds": len(reds),
        "rows": {k: {kk: vv for kk, vv in v.items() if kk != "peers"}
                 for k, v in rows.items()},
        "pause_present": pause_present,
        "pause_mode": pause_mode,
        "serve_8770": sock["ok"],
        "tree_id": paths.sentinel.tree_id,
        "board": str(board_path),
    }
    if sup is not None:
        # --once strips "rows" when it prints; the typed kind must still surface.
        extra["serve_supervisor"] = sup
    hb = write_heartbeat(hb_path, WORKER, extra=extra, polls=polls,
                         interval_s=interval_s)
    board = {
        "schema": SCHEMA,
        "measured_at": hb["last_run"],
        "measured_epoch": hb["last_run_epoch"],
        "verdict": verdict,
        "reds": sorted(reds),
        "rows": rows,
        "tree_id": paths.sentinel.tree_id,
        "worker": WORKER,
        "pid": os.getpid(),
    }
    atomic_json(board_path, board)
    extra["heartbeat"] = hb
    extra["ok"] = True
    extra["heartbeat_path"] = str(hb_path)
    return extra


def loop(root: str, interval_s: float, supervise: bool = True) -> int:
    paths = CosmosPaths(root)
    out_path = paths.logs("health_clock.out")
    err_path = paths.logs("health_clock.err")
    lock_path = paths.logs(LOCK_NAME)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    log_fh = open(out_path, "a", encoding="utf-8", buffering=1)
    sys.stdout = log_fh
    sys.stderr = log_fh
    fd = acquire_lock(lock_path)
    if fd is None:
        rec = read_heartbeat(paths.logs(HEARTBEAT_NAME))
        age = heartbeat_age_s(rec)
        pid = (rec or {}).get("pid")
        if age is not None and age < FRESH_S and pid_alive(int(pid or 0)):
            print(json.dumps({"already_running": True, "pid": pid,
                              "age_s": round(age, 3)}), flush=True)
            return 0
        print("health-clock lock held and heartbeat not fresh - refusing",
              flush=True)
        return 2
    polls = 0
    print(json.dumps({"loop": True, "pid": os.getpid(),
                      "interval_s": interval_s}, indent=1), flush=True)
    try:
        while True:
            polls += 1
            try:
                poll_once(root, polls=polls, interval_s=interval_s,
                          supervise=supervise)
            except Exception:
                import traceback
                tb = traceback.format_exc()
                try:
                    err_path.write_text(tb, encoding="utf-8")
                except OSError:
                    pass
                try:
                    write_heartbeat(paths.logs(HEARTBEAT_NAME), WORKER,
                                    extra={"tick": "error", "error": tb[-500:]},
                                    polls=polls, interval_s=interval_s)
                except OSError:
                    pass
            time.sleep(interval_s)
    finally:
        os.close(fd)
    return 0


def standup(root: str, interval_s: float = DEFAULT_INTERVAL_S,
            supervise: bool = True) -> dict:
    paths = CosmosPaths(root)
    hb = paths.logs(HEARTBEAT_NAME)
    t0 = time.time()
    proof = wait_fresh(hb, timeout_s=1.2, max_age_s=FRESH_S)
    if proof["ok"]:
        return {"started": "already", "proof": proof, "keith_cmd": None,
                "task_name": TASK_NAME}

    script = Path(__file__).resolve()
    # Register the intent EXPLICITLY, never by relying on the default: a task
    # action that omits the flag is exactly how the supervisor stayed dormant.
    flags = ["--loop", "--supervise" if supervise else "--no-supervise"]
    tr = tr_cmdline(script, root, *flags)
    minute = create_task(TASK_NAME, tr, "minute", mo=1, run_now=True)
    logon = create_task(TASK_NAME_LOGON, tr, "onlogon")
    launched_via = None
    detach = None
    if minute.get("ok") and minute.get("run_ok"):
        launched_via = "schtasks"
        proof = wait_fresh(hb, timeout_s=12.0, min_epoch=t0, max_age_s=FRESH_S)
    if not proof.get("ok"):
        argv = [pythonw_exe(), str(script), "--root",
                str(Path(root).resolve())] + flags
        detach = spawn_detached(argv, str(script.parent),
                                paths.logs("health_clock.out"))
        launched_via = detach.get("method") or "detached"
        expect = detach.get("pid") if isinstance(detach.get("pid"), int) else None
        proof = wait_fresh(hb, timeout_s=15.0, min_epoch=t0, max_age_s=FRESH_S,
                           expect_pid=expect)

    keith = []
    for rec in (minute, logon):
        if rec.get("keith_cmd") and (rec.get("needs_elevation") or not rec.get("ok")):
            keith.append(rec["keith_cmd"])
        h = rec.get("harden") or {}
        if h.get("keith_cmd") and not h.get("ok"):
            keith.append(h["keith_cmd"])
    return {
        "started": launched_via,
        "task_minute": minute,
        "task_logon": logon,
        "detach": detach,
        "proof": proof,
        "heartbeat_path": str(hb),
        "keith_cmd": " & ".join(keith) if keith else None,
        "keith_cmds": keith,
        "task_name": TASK_NAME,
    }


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_health_clock")
    ap.add_argument("--root", required=True)
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--standup", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--interval", type=float, default=DEFAULT_INTERVAL_S)
    ap.add_argument("--supervise", action=argparse.BooleanOptionalAction,
                    default=True,
                    help="START Core on :8770 when it is down (single-supervisor, "
                         "backed off, PAUSE-aware). DEFAULT ON; --no-supervise "
                         "to observe only.")
    a = ap.parse_args()
    if a.status:
        paths = CosmosPaths(a.root)
        rec = read_heartbeat(paths.logs(HEARTBEAT_NAME))
        age = heartbeat_age_s(rec)
        print(json.dumps({"path": str(paths.logs(HEARTBEAT_NAME)),
                          "age_s": age, "heartbeat": rec}, indent=1,
                         default=str))
        return 0 if age is not None and age < FRESH_S else 2
    if a.standup:
        r = standup(a.root, a.interval, supervise=a.supervise)
        print(json.dumps(r, indent=1, default=str))
        return 0 if (r.get("proof") or {}).get("ok") else 2
    if a.once:
        r = poll_once(a.root, interval_s=a.interval, supervise=a.supervise)
        print(json.dumps({k: r[k] for k in r if k != "rows"},
                         indent=1, default=str))
        return 0
    return loop(a.root, a.interval, supervise=a.supervise)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CosmosPathError as e:
        print(e, file=sys.stderr)
        raise SystemExit(2)
