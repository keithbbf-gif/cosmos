#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_cdeck_feed - FAST (0.75s) display feed for cDeck.

Cadence rubric: dynamic display = detached Python daemon at 0.5s–few-s.
This clock does NOT call the ledger, Kernel, or SpendGate every tick — it
aggregates already-written heartbeats and meter projections so cDeck can
paint an age-bearing snapshot without hammering authority.

Writes live/state/cdeck/feed.json + heartbeat.

    py -3.14 cosmos\\cosmos_cdeck_feed.py --root V:\\A\\Ai\\COSMOS\\live --loop
    py -3.14 cosmos\\cosmos_cdeck_feed.py --root ... --once
    py -3.14 cosmos\\cosmos_cdeck_feed.py --root ... --standup

Task: COSMOS cDeck Feed. Detached daemon + 1-min self-heal + onlogon.
Does NOT honor PAUSE (display stays live while retask is paused).
No bts_* import. Does not modify core.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_clock import (  # noqa: E402
    acquire_lock, atomic_json, create_task, heartbeat_age_s, pid_alive,
    pythonw_exe, read_heartbeat, spawn_detached, tr_cmdline, wait_fresh,
    write_heartbeat,
)
from cosmos_paths import CosmosPaths, CosmosPathError  # noqa: E402

WORKER = "cosmos-cdeck-feed"
TASK_NAME = "COSMOS cDeck Feed"
TASK_NAME_LOGON = "COSMOS cDeck Feed Logon"
HEARTBEAT_NAME = "cdeck_feed_heartbeat.json"
LOCK_NAME = "cdeck_feed.lock"
SCHEMA = "cosmos-cdeck-feed/1"
DEFAULT_INTERVAL_S = 0.75
FRESH_S = 4.0

SNAPSHOT_FILES = (
    ("health", "state", ("health", "board.json")),
    ("spend", "state", ("spend", "meter.json")),
    ("drive", "state", ("drive", "meter.json")),
    ("rails", "state", ("rails", "probe.json")),
    ("discovery", "state", ("discovery", "hands.json")),
    ("ledger_verify", "state", ("ledger", "verify.json")),
)


def _load_json(path: Path) -> tuple[dict | None, float | None]:
    if not path.exists():
        return None, None
    try:
        st = path.stat()
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None, None
    if not isinstance(obj, dict):
        return None, None
    return obj, float(st.st_mtime)


def _age(mtime: float | None, now: float) -> float | None:
    if mtime is None:
        return None
    return round(now - mtime, 3)


def _pause(paths: CosmosPaths) -> dict:
    p = paths.role("state") / "control" / "PAUSE.flag"
    if not p.is_file():
        return {"present": False, "state": "RUNNING"}
    rec = {"present": True, "state": "PAUSED", "path": str(p)}
    try:
        raw = p.read_text(encoding="utf-8").strip()
        if raw.startswith("{"):
            obj = json.loads(raw)
            if isinstance(obj, dict):
                rec.update({k: obj.get(k) for k in
                            ("mode", "reason", "set_by", "set_at",
                             "auto_resume_at")})
                rec["state"] = obj.get("state") or "PAUSED"
    except (OSError, ValueError):
        rec["reason"] = "(unreadable flag)"
    return rec


def _queue_counts(paths: CosmosPaths) -> dict:
    q = paths.role("queue")
    manifests = 0
    man = q / "manifests"
    if man.is_dir():
        try:
            manifests = sum(1 for p in man.iterdir()
                            if p.is_file() and p.suffix.lower() == ".json")
        except OSError:
            manifests = -1
    py_jobs = 0
    for lane_dir in (q, q / "_lanes" / "lg", q / "_lanes" / "pb"):
        if not lane_dir.is_dir():
            continue
        try:
            for p in lane_dir.iterdir():
                if p.is_file() and p.suffix.lower() == ".py" and not p.name.startswith("_"):
                    py_jobs += 1
        except OSError:
            continue
    return {"path": str(q), "manifests": manifests, "lane_py_jobs": py_jobs}


def poll_once(root: str, polls: int = 0,
              interval_s: float = DEFAULT_INTERVAL_S) -> dict:
    paths = CosmosPaths(root)
    logs = paths.logs()
    logs.mkdir(parents=True, exist_ok=True)
    dest_dir = paths.state("cdeck")
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "feed.json"
    now = time.time()

    clocks = {}
    for p in logs.glob("*heartbeat*.json"):
        rec = read_heartbeat(p)
        age = heartbeat_age_s(rec, now=now)
        clocks[p.name] = {
            "age_s": None if age is None else round(age, 3),
            "pid": (rec or {}).get("pid"),
            "state": (rec or {}).get("state"),
            "worker": (rec or {}).get("worker"),
            "alive": pid_alive(int((rec or {}).get("pid") or 0)),
            "verdict": (rec or {}).get("verdict"),
            "last_run_epoch": (rec or {}).get("last_run_epoch"),
        }

    snaps = {}
    for key, role, parts in SNAPSHOT_FILES:
        path = paths.role(role, *parts)
        obj, mt = _load_json(path)
        snaps[key] = {
            "path": str(path),
            "present": obj is not None,
            "age_s": _age(mt, now),
            "ok": None if obj is None else obj.get("ok", obj.get("verdict")),
        }
        if obj is not None:
            for field in ("verdict", "live_count", "rail_count", "warn",
                          "kind", "records", "head_seq"):
                if field in obj:
                    snaps[key][field] = obj[field]
            if key == "spend" and isinstance(obj.get("audit"), dict):
                rails = obj["audit"].get("rails") or {}
                snaps[key]["rail_count"] = len(rails)
            if key == "health" and "verdict" in obj:
                snaps[key]["verdict"] = obj.get("verdict")
                snaps[key]["reds"] = obj.get("reds")

    pause = _pause(paths)
    queue = _queue_counts(paths)
    extra = {
        "schema": SCHEMA,
        "tick": "once",
        "state": "RUNNING",
        "feed": str(dest),
        "clocks": len(clocks),
        "pause_present": bool(pause.get("present")),
        "queue_manifests": queue["manifests"],
    }
    hb = write_heartbeat(logs / HEARTBEAT_NAME, WORKER, extra=extra,
                         polls=polls, interval_s=interval_s)
    feed = {
        "schema": SCHEMA,
        "measured_at": hb["last_run"],
        "measured_epoch": hb["last_run_epoch"],
        "age_rule": "every panel carries measured age_s; UNMEASURED stays UNMEASURED",
        "worker": WORKER,
        "pid": os.getpid(),
        "tree_id": paths.sentinel.tree_id,
        "pause": pause,
        "queue": queue,
        "clocks": clocks,
        "snapshots": snaps,
    }
    atomic_json(dest, feed)
    extra["ok"] = True
    extra["heartbeat"] = hb
    extra["heartbeat_path"] = str(logs / HEARTBEAT_NAME)
    extra["feed_path"] = str(dest)
    return extra


def loop(root: str, interval_s: float) -> int:
    paths = CosmosPaths(root)
    out_path = paths.logs("cdeck_feed.out")
    err_path = paths.logs("cdeck_feed.err")
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
        print("cdeck-feed lock held and heartbeat not fresh - refusing",
              flush=True)
        return 2
    polls = 0
    print(json.dumps({"loop": True, "pid": os.getpid(),
                      "interval_s": interval_s}, indent=1), flush=True)
    try:
        while True:
            polls += 1
            try:
                poll_once(root, polls=polls, interval_s=interval_s)
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


def standup(root: str, interval_s: float = DEFAULT_INTERVAL_S) -> dict:
    paths = CosmosPaths(root)
    hb = paths.logs(HEARTBEAT_NAME)
    t0 = time.time()
    proof = wait_fresh(hb, timeout_s=1.0, max_age_s=FRESH_S)
    if proof["ok"]:
        return {"started": "already", "proof": proof, "keith_cmd": None,
                "task_name": TASK_NAME}
    script = Path(__file__).resolve()
    tr = tr_cmdline(script, root, "--loop")
    minute = create_task(TASK_NAME, tr, "minute", mo=1, run_now=True)
    logon = create_task(TASK_NAME_LOGON, tr, "onlogon")
    launched_via = None
    detach = None
    if minute.get("ok") and minute.get("run_ok"):
        launched_via = "schtasks"
        proof = wait_fresh(hb, timeout_s=12.0, min_epoch=t0, max_age_s=FRESH_S)
    if not proof.get("ok"):
        argv = [pythonw_exe(), str(script), "--root", str(Path(root).resolve()),
                "--loop"]
        detach = spawn_detached(argv, str(script.parent),
                                paths.logs("cdeck_feed.out"))
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
        "started": launched_via, "task_minute": minute, "task_logon": logon,
        "detach": detach, "proof": proof, "heartbeat_path": str(hb),
        "keith_cmd": " & ".join(keith) if keith else None,
        "keith_cmds": keith, "task_name": TASK_NAME,
    }


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_cdeck_feed")
    ap.add_argument("--root", required=True)
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--standup", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--interval", type=float, default=DEFAULT_INTERVAL_S)
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
        r = standup(a.root, a.interval)
        print(json.dumps(r, indent=1, default=str))
        return 0 if (r.get("proof") or {}).get("ok") else 2
    if a.once:
        r = poll_once(a.root, interval_s=a.interval)
        print(json.dumps({"ok": True, "feed": r.get("feed_path"),
                          "clocks": r.get("clocks"),
                          "pause_present": r.get("pause_present")},
                         indent=1, default=str))
        return 0
    return loop(a.root, a.interval)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CosmosPathError as e:
        print(e, file=sys.stderr)
        raise SystemExit(2)
