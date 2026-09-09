#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_pool - concurrent runner pool (pull supervisor + N drain workers).

Pull, not push: each worker claim_next()s under the ledger head-fence
(expect_head_seq). Exactly-once is THAT fence — we do not invent a second
claim protocol. Unique worker-id per slot so Scheduler.done() (completer ==
claimant) cannot cross workers.

Topology:
  * Supervisor is the durable daemon (cosmos_pool.lock). It creates N general
    drain processes + 1 reserved fast slot, replaces a crashed child, honors
    PAUSE by keeping workers alive (workers self-gate claiming).
  * Workers are CREATE_NO_WINDOW children; each holds cosmos_runner.slotN.lock
    so a relaunched supervisor cannot double a slot.
  * Slot 0 is the coordinator: the only adapter (single file-drop ingestor)
    and the only JOB_STALE reporter.
  * Fast slot claims ONLY --fast-lane (default: "default") so a short admin
    job is claimable within one poll while general slots drain pb/lg grok.

CLOCKS collapse: pool is the only claim_next on live/queue. cosmos_run.py
is the double-claim surface — do not run it beside --supervise. This hour
does not /delete COSMOS Runner Logon (reboot would respawn it). Pool off
is no longer "behaves as today."

    py -3.14 cosmos\\cosmos_pool.py --root V:\\A\\Ai\\COSMOS\\live --supervise
    py -3.14 cosmos\\cosmos_pool.py --root ... --standup
    py -3.14 cosmos\\cosmos_pool.py --root ... --status
    # --worker --slot N  is internal; users never call it.

N starts at 3 general + 1 fast. Fast lane is the existing ``default`` lane
(adapter tags _lanes/pb and _lanes/lg already; default is the short/admin
path). A new dedicated short lane would starve until every submitter changes.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_clock import (  # noqa: E402
    create_task, pid_alive, spawn_detached, tr_cmdline, write_heartbeat,
)
from cosmos_job_adapter import LegacyJobAdapter                  # noqa: E402
from cosmos_node_worker import is_paused, pause_flag            # noqa: E402
from cosmos_paths import CosmosPaths, CosmosPathError          # noqa: E402
from cosmos_run import (                                        # noqa: E402
    CREATE_NEW_PROCESS_GROUP, CREATE_NO_WINDOW, DETACHED_PROCESS,
    acquire_lock, heartbeat_age_s, pythonw_exe, query_task,
    read_heartbeat, wait_fresh,
)
from cosmos_runner import Runner                                 # noqa: E402
from cosmos_sched import Scheduler                               # noqa: E402

WORKER = "cosmos-pool"
TASK_NAME = "COSMOS Runner Pool"
LOGON_TASK_NAME = "COSMOS Runner Pool Logon"
HEARTBEAT_NAME = "cosmos_pool_heartbeat.json"
LOCK_NAME = "cosmos_pool.lock"
DEFAULT_INTERVAL_S = 15.0
DEFAULT_N = 3
DEFAULT_FAST_LANE = "default"
STALE_AFTER_S = 7200.0
FRESH_S = 60.0


# ---------------------------------------------------------------------------
# slot plan — unique worker-id per slot is the done() invariant
# ---------------------------------------------------------------------------

def worker_id_for(slot) -> str:
    """cosmos-runner-slot0 / -slot1 / -slot2 / cosmos-runner-fast."""
    s = str(slot)
    if s == "fast":
        return "cosmos-runner-fast"
    return f"cosmos-runner-slot{s}"


def slot_lock_name(slot) -> str:
    return f"cosmos_runner.slot{slot}.lock"


def slot_heartbeat_name(slot) -> str:
    return f"cosmos_runner.slot{slot}_heartbeat.json"


def slot_log_name(slot) -> str:
    return f"cosmos_runner.slot{slot}.out"


def plan_slots(n: int, fast_lane: str = DEFAULT_FAST_LANE) -> list[dict]:
    """slot0 (adapt + general) + slots 1..n-1 (general) + slot 'fast'."""
    n = int(n)
    if n < 1:
        raise ValueError("n must be >= 1 (need a coordinator slot0)")
    lane = str(fast_lane or DEFAULT_FAST_LANE)
    slots: list[dict] = []
    for i in range(n):
        slots.append({
            "slot": i,
            "adapt": i == 0,
            "lanes": None,
            "exclude": None,
            "report_stale": i == 0,
            "kind": "coordinator" if i == 0 else "general",
        })
    slots.append({
        "slot": "fast",
        "adapt": False,
        "lanes": {lane},
        "exclude": None,
        "report_stale": False,
        "kind": "fast",
    })
    return slots


def slot_spec(slot, n: int, fast_lane: str) -> dict:
    key = str(slot)
    for spec in plan_slots(n, fast_lane):
        if str(spec["slot"]) == key:
            return spec
    raise ValueError(f"unknown pool slot {slot!r} for n={n}")


# ---------------------------------------------------------------------------
# bind / run one worker
# ---------------------------------------------------------------------------

def bind_worker(root: str, slot, lanes, exclude, adapt: bool) -> dict:
    """Scheduler + Runner for one slot. Unique worker-id. Adapter on slot0 only.

    Signatures used exactly as cosmos_run.bind: CosmosPaths(root),
    paths.config("install_key.bin"), paths.role("queue"|"work"|"tools"),
    paths.logs(filename).
    """
    paths = CosmosPaths(root)
    keyfile = paths.config("install_key.bin")
    if not keyfile.exists():
        raise CosmosPathError(
            "NOT_FOUND",
            f"no install key at {keyfile} - run cosmos.py install; the pool "
            f"does not invent authentication material")
    key = keyfile.read_bytes()
    q = paths.role("queue")
    q.mkdir(parents=True, exist_ok=True)
    work = paths.role("work")
    work.mkdir(parents=True, exist_ok=True)
    logs = paths.logs()
    logs.mkdir(parents=True, exist_ok=True)
    wid = worker_id_for(slot)
    sched = Scheduler(q, key, wid)
    runner = Runner(sched, work, wid)
    runner.tools_root = paths.role("tools")
    runner.paths = paths
    runner.claim_lanes = lanes
    runner.claim_exclude = exclude
    if adapt:
        runner.adapter = LegacyJobAdapter(
            queue=q, tools_root=paths.role("tools"), work_root=work,
            sched=sched)
    runner.instance_id = uuid.uuid4().hex[:12]
    hb = logs / slot_heartbeat_name(slot)
    lock = logs / slot_lock_name(slot)
    return {"paths": paths, "sched": sched, "runner": runner,
            "heartbeat": hb, "lock": lock, "queue": q, "work": work,
            "worker_id": wid, "slot": slot}


def run_worker(root: str, slot, n: int = DEFAULT_N,
               fast_lane: str = DEFAULT_FAST_LANE,
               interval_s: float = DEFAULT_INTERVAL_S) -> int:
    """Internal child body. Acquire per-slot lock or refuse already_running."""
    spec = slot_spec(slot, n, fast_lane)
    bound = bind_worker(root, spec["slot"], spec["lanes"], spec["exclude"],
                        spec["adapt"])
    paths = bound["paths"]
    log_path = paths.logs(slot_log_name(spec["slot"]))
    err_path = paths.logs(f"cosmos_runner.slot{spec['slot']}.err")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_fh = open(log_path, "a", encoding="utf-8", buffering=1)
    sys.stdout = log_fh
    sys.stderr = log_fh
    fd = acquire_lock(bound["lock"])
    if fd is None:
        rec = read_heartbeat(bound["heartbeat"])
        age = heartbeat_age_s(rec)
        pid = (rec or {}).get("pid")
        print(json.dumps({"already_running": True, "slot": spec["slot"],
                          "worker_id": bound["worker_id"], "pid": pid,
                          "age_s": None if age is None else round(age, 3),
                          "heartbeat": str(bound["heartbeat"])}, indent=1),
              flush=True)
        return 0
    runner = bound["runner"]
    stale = STALE_AFTER_S if spec["report_stale"] else float("inf")
    print(json.dumps({"worker": True, "slot": spec["slot"],
                      "worker_id": bound["worker_id"],
                      "pid": os.getpid(),
                      "kind": spec["kind"],
                      "adapt": spec["adapt"],
                      "lanes": (sorted(spec["lanes"])
                                if spec["lanes"] is not None else None),
                      "report_stale": spec["report_stale"],
                      "queue": str(bound["queue"]),
                      "heartbeat": str(bound["heartbeat"]),
                      "interval_s": interval_s,
                      "instance_id": runner.instance_id}, indent=1),
          flush=True)

    def _pause_gate() -> bool:
        return is_paused(pause_flag(paths))

    try:
        try:
            runner.drain_loop(bound["heartbeat"], interval_s=interval_s,
                              stale_after_s=stale, pause_gate=_pause_gate)
        except BaseException:
            import traceback
            tb = traceback.format_exc()
            print(tb, flush=True)
            try:
                err_path.write_text(tb, encoding="utf-8")
            except OSError:
                pass
            raise
    finally:
        os.close(fd)
    return 0


# ---------------------------------------------------------------------------
# supervisor
# ---------------------------------------------------------------------------

def _slot_holder_alive(paths: CosmosPaths, slot) -> int | None:
    """Live pid holding this slot, or None. Heartbeat first, lock-file pid next."""
    hb = paths.logs(slot_heartbeat_name(slot))
    rec = read_heartbeat(hb)
    pid = int((rec or {}).get("pid") or 0)
    if pid and pid_alive(pid):
        return pid
    lock = paths.logs(slot_lock_name(slot))
    try:
        raw = lock.read_text(encoding="ascii").strip()
        lp = int(raw or 0)
    except (OSError, ValueError):
        lp = 0
    if lp and pid_alive(lp):
        return lp
    return None


def spawn_worker(root: str, spec: dict, n: int, fast_lane: str,
                 interval_s: float) -> dict:
    """Popen pythonw, DETACHED | NEW_GROUP | NO_WINDOW. Child of supervisor."""
    argv = [
        pythonw_exe(), str(Path(__file__).resolve()),
        "--root", str(Path(root).resolve()),
        "--worker", "--slot", str(spec["slot"]),
        "--n", str(n), "--fast-lane", str(fast_lane),
        "--interval", str(interval_s),
    ]
    flags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW
    try:
        p = subprocess.Popen(
            argv, stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            cwd=str(Path(__file__).resolve().parent), close_fds=True,
            creationflags=flags)
    except OSError as e:
        return {"ok": False, "error": str(e), "argv": argv,
                "slot": spec["slot"], "worker_id": worker_id_for(spec["slot"])}
    return {"ok": True, "pid": p.pid, "argv": argv, "slot": spec["slot"],
            "worker_id": worker_id_for(spec["slot"]),
            "creationflags": flags}


def supervise(root: str, n: int = DEFAULT_N,
              fast_lane: str = DEFAULT_FAST_LANE,
              interval: float = DEFAULT_INTERVAL_S, stop=None) -> int:
    """Durable supervisor. Acquire cosmos_pool.lock; keep N+fast workers alive.

    Workers self-honor PAUSE; supervisor does not kill in-flight and does not
    pause respawn, so resume has no respawn latency.
    """
    paths = CosmosPaths(root)
    logs = paths.logs()
    logs.mkdir(parents=True, exist_ok=True)
    hb = logs / HEARTBEAT_NAME
    lock = logs / LOCK_NAME
    log_path = paths.logs("cosmos_pool.out")
    err_path = paths.logs("cosmos_pool.err")
    log_fh = open(log_path, "a", encoding="utf-8", buffering=1)
    sys.stdout = log_fh
    sys.stderr = log_fh
    fd = acquire_lock(lock)
    if fd is None:
        rec = read_heartbeat(hb)
        age = heartbeat_age_s(rec)
        pid = (rec or {}).get("pid")
        alive = pid_alive(int(pid or 0))
        if alive:
            print(json.dumps({"already_running": True, "pid": pid,
                              "age_s": None if age is None else round(age, 3),
                              "heartbeat": str(hb)}, indent=1), flush=True)
            return 0
        print("pool lock held and heartbeat pid not alive - refusing second "
              "supervise", flush=True)
        return 2
    planned = plan_slots(n, fast_lane)
    print(json.dumps({"supervise": True, "pid": os.getpid(),
                      "n": n, "fast_lane": fast_lane,
                      "slots": [worker_id_for(s["slot"]) for s in planned],
                      "heartbeat": str(hb),
                      "interval_s": interval}, indent=1), flush=True)
    polls = 0
    try:
        while stop is None or not stop():
            polls += 1
            slot_rows = []
            for spec in planned:
                live = _slot_holder_alive(paths, spec["slot"])
                spawned = None
                if live is None:
                    spawned = spawn_worker(root, spec, n, fast_lane, interval)
                    live = spawned.get("pid") if spawned.get("ok") else None
                slot_rows.append({
                    "slot": spec["slot"],
                    "worker_id": worker_id_for(spec["slot"]),
                    "kind": spec["kind"],
                    "pid": live,
                    "alive": bool(live and pid_alive(int(live))),
                    "spawned_this_tick": bool(spawned and spawned.get("ok")),
                    "spawn_error": (spawned or {}).get("error"),
                })
            extra = {
                "tick": "supervise",
                "state": "RUNNING",
                "n": n,
                "fast_lane": fast_lane,
                "slots": slot_rows,
                "queue": str(paths.role("queue")),
            }
            write_heartbeat(hb, WORKER, extra=extra, polls=polls,
                            interval_s=interval)
            time.sleep(max(0.05, float(interval)))
    except BaseException:
        import traceback
        tb = traceback.format_exc()
        print(tb, flush=True)
        try:
            err_path.write_text(tb, encoding="utf-8")
        except OSError:
            pass
        raise
    finally:
        os.close(fd)
    return 0


# ---------------------------------------------------------------------------
# status / standup (durable daemon, like COSMOS Runner)
# ---------------------------------------------------------------------------

def status_view(root: str, n: int = DEFAULT_N,
                fast_lane: str = DEFAULT_FAST_LANE) -> dict:
    """Liveness read. Does not mkdir roles or instantiate Scheduler."""
    paths = CosmosPaths(root)
    hb = paths.logs(HEARTBEAT_NAME)
    rec = read_heartbeat(hb)
    age = heartbeat_age_s(rec)
    n_use = int((rec or {}).get("n") or n)
    lane = str((rec or {}).get("fast_lane") or fast_lane)
    workers = []
    for spec in plan_slots(n_use, lane):
        shb = paths.logs(slot_heartbeat_name(spec["slot"]))
        srec = read_heartbeat(shb)
        sage = heartbeat_age_s(srec)
        workers.append({
            "slot": spec["slot"],
            "worker_id": worker_id_for(spec["slot"]),
            "kind": spec["kind"],
            "path": str(shb),
            "age_s": sage,
            "pid": (srec or {}).get("pid"),
            "alive": pid_alive(int((srec or {}).get("pid") or 0)),
            "state": (srec or {}).get("state"),
            "tick": (srec or {}).get("tick"),
            "fresh": sage is not None and sage < FRESH_S,
        })
    return {
        "path": str(hb),
        "age_s": age,
        "heartbeat": rec,
        "queue": str(paths.role("queue")),
        "fresh": age is not None and age < FRESH_S,
        "task": query_task(TASK_NAME),
        "workers": workers,
    }


def install_task(root: str, n: int, fast_lane: str,
                 interval_s: float) -> dict:
    """Register ``COSMOS Runner Pool Logon`` only. Never /f the minute self-heal."""
    existing = query_task(LOGON_TASK_NAME)
    if existing.get("ok"):
        return {"ok": True, "already": True, "skipped": True,
                "name": LOGON_TASK_NAME,
                "note": "logon task already registered; minute self-heal "
                        "COSMOS Runner Pool left untouched"}
    tr = tr_cmdline(Path(__file__).resolve(), root, "--supervise",
                    "--n", str(n), "--fast-lane", str(fast_lane),
                    "--interval", str(interval_s))
    argv = ["schtasks", "/create", "/tn", LOGON_TASK_NAME, "/tr", tr,
            "/sc", "onlogon", "/f"]
    try:
        p = subprocess.run(argv, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=60)
    except OSError as e:
        return {"argv": argv, "rc": -1, "ok": False, "out": str(e),
                "note": "schtasks could not run at all",
                "keith_cmd": subprocess.list2cmdline(argv),
                "needs_elevation": False, "name": LOGON_TASK_NAME}
    out = ((p.stdout or "") + (p.stderr or "")).strip()
    low = out.lower()
    denied = p.returncode != 0 and ("access is denied" in low
                                    or "access denied" in low
                                    or "elevat" in low
                                    or "denied" in low)
    rec = {
        "argv": argv, "rc": p.returncode, "ok": p.returncode == 0, "out": out,
        "needs_elevation": denied, "name": LOGON_TASK_NAME,
        "keith_cmd": subprocess.list2cmdline(argv) if p.returncode != 0 else None,
        "note": ("registered: COSMOS Runner Pool Logon starts on every logon; "
                 "minute self-heal COSMOS Runner Pool left untouched"
                 if p.returncode == 0 else
                 "FAILED - schtasks returned nonzero (minute task not touched)"),
    }
    if p.returncode == 0:
        r = subprocess.run(["schtasks", "/run", "/tn", LOGON_TASK_NAME],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=30,
                           creationflags=(CREATE_NO_WINDOW if os.name == "nt"
                                          else 0))
        rec["run_rc"] = r.returncode
        rec["run_out"] = ((r.stdout or "") + (r.stderr or "")).strip()
        rec["run_ok"] = r.returncode == 0
    return rec


def standup(root: str, interval_s: float = DEFAULT_INTERVAL_S,
            n: int = DEFAULT_N,
            fast_lane: str = DEFAULT_FAST_LANE) -> dict:
    """Register schtask + logon, spawn detached if needed.

    Proof = a FRESH cosmos_pool_heartbeat.json from a live pid, not an exit code.
    """
    paths = CosmosPaths(root)
    hb = paths.logs(HEARTBEAT_NAME)
    t0 = time.time()
    rec = read_heartbeat(hb)
    live_pid = int((rec or {}).get("pid") or 0)
    if live_pid and pid_alive(live_pid):
        age = heartbeat_age_s(rec)
        return {"started": "already",
                "proof": {"ok": True, "heartbeat": rec, "age_s": age,
                          "path": str(hb),
                          "note": "pid alive (heartbeat may be stale mid-tick)"},
                "n": n, "fast_lane": fast_lane, "keith_cmd": None,
                "task_name": TASK_NAME}
    proof = wait_fresh(hb, timeout_s=1.5, max_age_s=FRESH_S)
    if proof["ok"]:
        return {"started": "already", "proof": proof, "n": n,
                "fast_lane": fast_lane, "keith_cmd": None,
                "task_name": TASK_NAME}

    script = Path(__file__).resolve()
    tr = tr_cmdline(script, root, "--supervise",
                    "--n", str(n), "--fast-lane", str(fast_lane),
                    "--interval", str(interval_s))
    # Minute self-heal is a NEW clock — must be created (unlike re-standup of
    # COSMOS Runner, whose minute task already exists and must not be /f'd
    # with onlogon). Separate names: TASK_NAME vs LOGON_TASK_NAME.
    minute = create_task(TASK_NAME, tr, "minute", mo=1, run_now=True)
    logon = install_task(root, n, fast_lane, interval_s)
    launched_via = None
    detach = None
    if minute.get("ok") and minute.get("run_ok"):
        launched_via = "schtasks"
        proof = wait_fresh(hb, timeout_s=12.0, min_epoch=t0, max_age_s=FRESH_S)
    if not proof.get("ok"):
        argv = [pythonw_exe(), str(script),
                "--root", str(Path(root).resolve()),
                "--supervise", "--n", str(n),
                "--fast-lane", str(fast_lane),
                "--interval", str(interval_s)]
        detach = spawn_detached(argv, str(script.parent),
                                paths.logs("cosmos_pool.out"))
        launched_via = detach.get("method") or "detached"
        expect = detach.get("pid") if isinstance(detach.get("pid"), int) else None
        proof = wait_fresh(hb, timeout_s=15.0, min_epoch=t0, max_age_s=FRESH_S,
                           expect_pid=expect)

    keith = []
    for rec_t in (minute, logon):
        if rec_t.get("keith_cmd") and (rec_t.get("needs_elevation")
                                       or not rec_t.get("ok")):
            keith.append(rec_t["keith_cmd"])
        h = rec_t.get("harden") or {}
        if h.get("keith_cmd") and not h.get("ok"):
            keith.append(h["keith_cmd"])
    return {
        "started": launched_via,
        "task_minute": minute,
        "task_logon": logon,
        "detach": detach,
        "proof": proof,
        "n": n,
        "fast_lane": fast_lane,
        "heartbeat_path": str(hb),
        "keith_cmd": " & ".join(keith) if keith else None,
        "keith_cmds": keith,
        "task_name": TASK_NAME,
    }


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_pool")
    ap.add_argument("--root", required=True,
                    help="COSMOS runtime root (sentinel-verified)")
    ap.add_argument("--supervise", action="store_true",
                    help="durable supervisor daemon (default)")
    ap.add_argument("--worker", action="store_true",
                    help="internal child; users never call")
    ap.add_argument("--slot", default=None,
                    help="internal: slot id (0..n-1 or 'fast')")
    ap.add_argument("--standup", action="store_true",
                    help="register schtasks + spawn a surviving supervisor")
    ap.add_argument("--status", action="store_true",
                    help="print supervisor + per-slot heartbeat age")
    ap.add_argument("--interval", type=float, default=DEFAULT_INTERVAL_S)
    ap.add_argument("--n", type=int, default=DEFAULT_N,
                    help="general worker count (plus one reserved fast slot)")
    ap.add_argument("--fast-lane", default=DEFAULT_FAST_LANE, dest="fast_lane",
                    help="lane reserved for the fast slot (default: default)")
    a = ap.parse_args()

    if a.n < 1:
        print("n must be >= 1", file=sys.stderr)
        return 2

    if a.status:
        view = status_view(a.root, n=a.n, fast_lane=a.fast_lane)
        print(json.dumps(view, indent=1, default=str))
        return 0 if view.get("fresh") else 2

    if a.standup:
        r = standup(a.root, a.interval, n=a.n, fast_lane=a.fast_lane)
        print(json.dumps(r, indent=1, default=str))
        return 0 if (r.get("proof") or {}).get("ok") else 2

    if a.worker:
        if a.slot is None or str(a.slot).strip() == "":
            print("--worker requires --slot", file=sys.stderr)
            return 2
        return run_worker(a.root, a.slot, n=a.n, fast_lane=a.fast_lane,
                          interval_s=a.interval)

    # --supervise, or a bare --root: the daemon body (what schtasks invoke)
    return supervise(a.root, n=a.n, fast_lane=a.fast_lane,
                     interval=a.interval)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CosmosPathError as e:
        print(e, file=sys.stderr)
        raise SystemExit(2)
