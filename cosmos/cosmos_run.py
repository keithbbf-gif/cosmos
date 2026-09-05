#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_run - COSMOS's OWN runner daemon.

Persistent drain of THIS install's queue role (CosmosPaths.role("queue")),
isolated from the shared BTS queue. Jobs execute through cosmos_runner.Runner.
A heartbeat is written on EVERY poll so liveness is a file, not a log line.

    py -3.14 cosmos\\cosmos_run.py --root V:\\A\\Ai\\COSMOS\\live --loop
    py -3.14 cosmos\\cosmos_run.py --root ... --once
    py -3.14 cosmos\\cosmos_run.py --root ... --standup

--standup registers a Windows scheduled task (survives logoff) and/or spawns a
DETACHED_PROCESS pythonw child (survives this job's process-tree kill). A plain
child of this process is NOT used: it dies with the job.
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

from cosmos_job_adapter import LegacyJobAdapter                  # noqa: E402
from cosmos_paths import CosmosPaths, CosmosPathError          # noqa: E402
from cosmos_runner import Runner                                 # noqa: E402
from cosmos_sched import Scheduler                               # noqa: E402

WORKER = "cosmos-runner"
TASK_NAME = "COSMOS Runner"
LOGON_TASK_NAME = "COSMOS Runner Logon"
HEARTBEAT_NAME = "cosmos_runner_heartbeat.json"
LOCK_NAME = "cosmos_runner.lock"
DEFAULT_INTERVAL_S = 15.0

# Windows process-creation flags. DETACHED + new group + no window is the
# incumbent survival set (bts cosmos_watchdog). BREAKAWAY escapes a Job Object
# when the parent job allows it (this agent job will kill its tree on exit).
DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200
CREATE_NO_WINDOW = 0x08000000
CREATE_BREAKAWAY_FROM_JOB = 0x01000000


def pythonw_exe() -> str:
    exe = Path(sys.executable)
    cand = exe.with_name("pythonw.exe")
    return str(cand) if cand.exists() else str(exe)


def plan_loop_argv(root: str, python: str | None = None) -> list[str]:
    return [python or pythonw_exe(), str(Path(__file__).resolve()),
            "--root", str(Path(root).resolve()), "--loop"]


def plan_task_argv(root: str) -> list[str]:
    """schtasks /create plan for the onlogon relaunch ONLY.

    The live 1-min self-heal is ``COSMOS Runner``. This plan uses the separate
    name ``COSMOS Runner Logon`` so --standup cannot /f-overwrite the minute
    clock (ORCHESTRATION.md; own-clocks logon_specs).
    """
    tr = subprocess.list2cmdline([
        pythonw_exe(), str(Path(__file__).resolve()),
        "--root", str(Path(root).resolve()), "--loop",
    ])
    return ["schtasks", "/create", "/tn", LOGON_TASK_NAME, "/tr", tr,
            "/sc", "onlogon", "/f"]


def query_task(name: str) -> dict:
    try:
        p = subprocess.run(
            ["schtasks", "/query", "/tn", name],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=30)
    except OSError as e:
        return {"ok": False, "out": str(e), "name": name}
    out = ((p.stdout or "") + (p.stderr or "")).strip()
    return {"ok": p.returncode == 0, "rc": p.returncode, "out": out, "name": name}


def bind(root: str) -> dict:
    """Resolve the install, compose Scheduler+Runner on the queue/work roles.

    Queue identity is the resolver, not a drive literal: this daemon cannot
    drain V:\\Ai\\_queue because that path is not a role under this root.
    """
    paths = CosmosPaths(root)
    keyfile = paths.config("install_key.bin")
    if not keyfile.exists():
        raise CosmosPathError(
            "NOT_FOUND",
            f"no install key at {keyfile} - run cosmos.py install; the runner "
            f"does not invent authentication material")
    key = keyfile.read_bytes()
    q = paths.role("queue")
    q.mkdir(parents=True, exist_ok=True)
    work = paths.role("work")
    work.mkdir(parents=True, exist_ok=True)
    logs = paths.logs()
    logs.mkdir(parents=True, exist_ok=True)
    sched = Scheduler(q, key, WORKER)
    runner = Runner(sched, work, WORKER)
    runner.tools_root = paths.role("tools")
    runner.adapter = LegacyJobAdapter(
        queue=q, tools_root=paths.role("tools"), work_root=work, sched=sched)
    runner.instance_id = uuid.uuid4().hex[:12]
    hb = logs / HEARTBEAT_NAME
    lock = logs / LOCK_NAME
    return {"paths": paths, "sched": sched, "runner": runner,
            "heartbeat": hb, "lock": lock, "queue": q, "work": work}


def read_heartbeat(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return None


def heartbeat_age_s(rec: dict | None, now: float | None = None) -> float | None:
    if not rec or "last_run_epoch" not in rec:
        return None
    return (now if now is not None else time.time()) - float(rec["last_run_epoch"])


def status_view(root: str) -> dict:
    """Liveness read. Does not mkdir roles or instantiate Scheduler."""
    paths = CosmosPaths(root)
    hb = paths.logs(HEARTBEAT_NAME)
    rec = read_heartbeat(hb)
    age = heartbeat_age_s(rec)
    return {
        "path": str(hb),
        "age_s": age,
        "heartbeat": rec,
        "queue": str(paths.role("queue")),
        "fresh": age is not None and age < 60,
    }


def _pid_alive(pid: int) -> bool:
    if not isinstance(pid, int) or pid <= 0:
        return False
    if os.name == "nt":
        import ctypes
        SYNCHRONIZE = 0x00100000
        h = ctypes.windll.kernel32.OpenProcess(SYNCHRONIZE, 0, pid)
        if h:
            ctypes.windll.kernel32.CloseHandle(h)
            return True
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def acquire_lock(lock_path: Path):
    """Exclusive OS lock held for the process lifetime. None if already held."""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_RDWR | os.O_CREAT
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY
    fd = os.open(str(lock_path), flags)
    try:
        if os.name == "nt":
            import msvcrt
            os.write(fd, b"\x00")
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        os.close(fd)
        return None
    os.lseek(fd, 0, os.SEEK_SET)
    os.ftruncate(fd, 0)
    os.write(fd, str(os.getpid()).encode("ascii"))
    os.fsync(fd)
    return fd


def spawn_wmi(root: str) -> dict:
    """Create the daemon via WMI Win32_Process.Create.

    The creator is the WMI service, not this process, so the child is OUTSIDE
    a per-tool Job Object. CREATE_BREAKAWAY_FROM_JOB is ignored when the job
    does not allow breakaway — measured: pythonw pid 4284 died with the standup
    tool-call even with DETACHED_PROCESS|BREAKAWAY set.
    """
    argv = plan_loop_argv(root)
    cmdline = subprocess.list2cmdline(argv)
    cwd = str(Path(__file__).resolve().parent)
    ps = (
        "$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create "
        "-Arguments @{ CommandLine = %s; CurrentDirectory = %s }; "
        "$r | ConvertTo-Json -Compress"
    ) % (json.dumps(cmdline), json.dumps(cwd))
    p = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=30)
    out = (p.stdout or "").strip()
    rec = {"method": "wmi", "argv": argv, "cmdline": cmdline,
           "ps_rc": p.returncode, "ps_out": out[:800],
           "ps_err": (p.stderr or "").strip()[:400]}
    try:
        data = json.loads(out)
    except ValueError:
        rec["ok"] = False
        rec["note"] = "WMI Create did not return JSON"
        return rec
    if isinstance(data, list):
        data = data[0] if data else {}
    rv = data.get("ReturnValue", data.get("returnValue"))
    pid = data.get("ProcessId", data.get("processId"))
    rec["ReturnValue"] = rv
    rec["pid"] = pid
    rec["ok"] = rv == 0 and bool(pid)
    return rec


def spawn_popen_detached(root: str, log_path: Path) -> dict:
    """Fallback: pythonw + DETACHED_PROCESS. May still die with the parent job."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    argv = plan_loop_argv(root)
    flags_breakaway = (DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
                       | CREATE_NO_WINDOW | CREATE_BREAKAWAY_FROM_JOB)
    flags_plain = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW
    log_fh = open(log_path, "ab")
    err = None
    try:
        try:
            p = subprocess.Popen(
                argv, stdin=subprocess.DEVNULL, stdout=log_fh,
                stderr=subprocess.STDOUT,
                cwd=str(Path(__file__).resolve().parent), close_fds=True,
                creationflags=flags_breakaway)
            flags_used = flags_breakaway
            breakaway = True
        except OSError as e:
            err = str(e)
            breakaway = False
            p = subprocess.Popen(
                argv, stdin=subprocess.DEVNULL, stdout=log_fh,
                stderr=subprocess.STDOUT,
                cwd=str(Path(__file__).resolve().parent), close_fds=True,
                creationflags=flags_plain)
            flags_used = flags_plain
    finally:
        log_fh.close()
    rec = {"method": "popen", "pid": p.pid, "argv": argv, "log": str(log_path),
           "creationflags": flags_used, "breakaway": breakaway, "ok": True}
    if err:
        rec["breakaway_error"] = err
    return rec


def spawn_detached(root: str, log_path: Path) -> dict:
    """Start the loop outside this job's process tree. WMI first, Popen fallback."""
    wmi = spawn_wmi(root)
    if wmi.get("ok"):
        return wmi
    pop = spawn_popen_detached(root, log_path)
    pop["wmi_failed"] = wmi
    return pop


def install_task(root: str) -> dict:
    """Register ``COSMOS Runner Logon`` only. Never /f the minute self-heal."""
    existing = query_task(LOGON_TASK_NAME)
    if existing.get("ok"):
        return {"ok": True, "already": True, "skipped": True,
                "name": LOGON_TASK_NAME, "note": "logon task already registered; "
                "minute self-heal COSMOS Runner left untouched",
                "argv": plan_task_argv(root), "rc": 0}
    argv = plan_task_argv(root)
    try:
        p = subprocess.run(argv, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=60)
    except OSError as e:
        return {"argv": argv, "rc": -1, "ok": False, "out": str(e),
                "note": "schtasks could not run at all",
                "keith_cmd": subprocess.list2cmdline(argv),
                "needs_elevation": False}
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
        "note": ("registered: COSMOS Runner Logon starts on every logon; "
                 "minute self-heal COSMOS Runner left untouched"
                 if p.returncode == 0 else
                 "FAILED - schtasks returned nonzero (minute task not touched)"),
    }
    if p.returncode == 0:
        r = subprocess.run(["schtasks", "/run", "/tn", LOGON_TASK_NAME],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=30,
                           creationflags=(CREATE_NO_WINDOW if os.name == "nt" else 0))
        rec["run_rc"] = r.returncode
        rec["run_out"] = ((r.stdout or "") + (r.stderr or "")).strip()
        rec["run_ok"] = r.returncode == 0
    return rec


def wait_fresh(hb_path: Path, timeout_s: float = 20.0,
               max_age_s: float = 60.0, min_epoch: float = 0,
               expect_pid: int | None = None) -> dict:
    deadline = time.time() + timeout_s
    last = None
    while time.time() < deadline:
        last = read_heartbeat(hb_path)
        age = heartbeat_age_s(last)
        if (last is not None and age is not None and age < max_age_s
                and float(last.get("last_run_epoch") or 0) >= min_epoch
                and (expect_pid is None or last.get("pid") == expect_pid)
                and _pid_alive(int(last.get("pid") or 0))):
            return {"ok": True, "heartbeat": last, "age_s": round(age, 3),
                    "path": str(hb_path)}
        time.sleep(0.4)
    return {"ok": False, "heartbeat": last, "age_s": heartbeat_age_s(last),
            "path": str(hb_path)}


def loop(root: str, interval_s: float) -> int:
    bound = bind(root)
    log_path = bound["paths"].logs("cosmos_runner.out")
    err_path = bound["paths"].logs("cosmos_runner.err")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_fh = open(log_path, "a", encoding="utf-8", buffering=1)
    sys.stdout = log_fh
    sys.stderr = log_fh
    fd = acquire_lock(bound["lock"])
    if fd is None:
        rec = read_heartbeat(bound["heartbeat"])
        age = heartbeat_age_s(rec)
        pid = (rec or {}).get("pid")
        alive = _pid_alive(int(pid or 0))
        # Long jobs pause the heartbeat; a live holder still owns the drain.
        if alive:
            print(json.dumps({"already_running": True, "pid": pid,
                              "age_s": None if age is None else round(age, 3),
                              "heartbeat": str(bound["heartbeat"])}, indent=1),
                  flush=True)
            return 0
        print("runner lock held and heartbeat not fresh - refusing second loop",
              flush=True)
        return 2
    runner = bound["runner"]
    print(json.dumps({"loop": True, "pid": os.getpid(),
                      "queue": str(bound["queue"]),
                      "heartbeat": str(bound["heartbeat"]),
                      "interval_s": interval_s,
                      "instance_id": runner.instance_id}, indent=1), flush=True)
    try:
        try:
            runner.drain_loop(bound["heartbeat"], interval_s=interval_s)
        except BaseException:
            import traceback
            tb = traceback.format_exc()
            print(tb, flush=True)
            err_path.write_text(tb, encoding="utf-8")
            raise
    finally:
        os.close(fd)
    return 0


def standup(root: str, interval_s: float) -> dict:
    """Make the daemon live past this job. Prefer schtasks; fall back to
    WMI-created pythonw (outside the tool-call Job Object). Proof is a
    FRESH heartbeat from a still-alive pid, not an exit code."""
    bound = bind(root)
    hb = bound["heartbeat"]
    t0 = time.time()
    rec = read_heartbeat(hb)
    live_pid = int((rec or {}).get("pid") or 0)
    if live_pid and _pid_alive(live_pid):
        age = heartbeat_age_s(rec)
        return {"started": "already",
                "proof": {"ok": True, "heartbeat": rec, "age_s": age,
                          "path": str(hb), "note": "pid alive (heartbeat may "
                          "be stale mid-job)"},
                "queue": str(bound["queue"])}
    proof = wait_fresh(hb, timeout_s=1.5)
    if proof["ok"]:
        return {"started": "already", "proof": proof,
                "queue": str(bound["queue"])}

    task = install_task(root)
    launched_via = None
    detach = None
    if task.get("ok") and task.get("run_ok"):
        launched_via = "schtasks"
        proof = wait_fresh(hb, timeout_s=12.0, min_epoch=t0)
    if not proof.get("ok"):
        detach = spawn_detached(root, bound["paths"].logs("cosmos_runner.out"))
        launched_via = detach.get("method") or "detached_process"
        expect = detach.get("pid") if isinstance(detach.get("pid"), int) else None
        proof = wait_fresh(hb, timeout_s=15.0, min_epoch=t0, expect_pid=expect)

    return {
        "started": launched_via,
        "task": task,
        "detach": detach,
        "proof": proof,
        "queue": str(bound["queue"]),
        "heartbeat_path": str(hb),
        "keith_cmd": task.get("keith_cmd") if task.get("needs_elevation") else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_run")
    ap.add_argument("--root", required=True,
                    help="COSMOS runtime root (sentinel-verified)")
    ap.add_argument("--loop", action="store_true",
                    help="persistent drain loop (what the daemon runs)")
    ap.add_argument("--once", action="store_true",
                    help="one poll then exit (heartbeat still written)")
    ap.add_argument("--standup", action="store_true",
                    help="register schtasks and/or spawn a surviving daemon")
    ap.add_argument("--status", action="store_true",
                    help="print heartbeat age; exit 0 if fresh")
    ap.add_argument("--interval", type=float, default=DEFAULT_INTERVAL_S)
    a = ap.parse_args()

    if a.status:
        view = status_view(a.root)
        print(json.dumps(view, indent=1, default=str))
        return 0 if view.get("fresh") else 2

    if a.standup:
        r = standup(a.root, a.interval)
        print(json.dumps(r, indent=1, default=str))
        return 0 if (r.get("proof") or {}).get("ok") else 2

    if a.once:
        bound = bind(a.root)
        results = bound["runner"].poll_once(bound["heartbeat"])
        print(json.dumps({"jobs": results,
                          "heartbeat": str(bound["heartbeat"]),
                          "queue": str(bound["queue"])}, indent=1, default=str))
        return 0

    # --loop, or a bare --root: the daemon body (what schtasks / pythonw invoke)
    return loop(a.root, a.interval)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CosmosPathError as e:
        print(e, file=sys.stderr)
        raise SystemExit(2)
