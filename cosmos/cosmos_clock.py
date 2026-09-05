#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_clock - shared Windows-clock primitives for COSMOS-own satellites.

NOT core (kernel/ledger/sched/service). New clocks reuse this so heartbeat,
lock, schtasks, and detached spawn stay one pattern. No bts_* import.

    schtasks floor is 1 minute. Anything faster is a detached --loop daemon
    plus a 1-min self-heal task and an onlogon relaunch.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone as dt_timezone
from pathlib import Path

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200
CREATE_NO_WINDOW = 0x08000000
CREATE_BREAKAWAY_FROM_JOB = 0x01000000

PY_LAUNCHER = ("py", "-3.14")

# F-60: a Python wrap in the parent interpreter cannot cover a native
# `schtasks.exe` spawned from a descendant `--once` (health suite leftover).
# Child processes inherit this env; when set, run_schtasks / harden_task
# never invoke the native binary. Production daemons leave it unset.
SCHTASKS_SANDBOX_ENV = "COSMOS_SCHTASKS_SANDBOX"
_SCHTASKS_WRITE_VERBS = ("/create", "/delete", "/change", "/run", "/end")


def schtasks_sandbox_on() -> bool:
    v = str(os.environ.get(SCHTASKS_SANDBOX_ENV, "") or "").strip().lower()
    return v not in ("", "0", "false", "no", "off")


def _schtasks_writes(argv) -> bool:
    if not argv:
        return False
    joined = " ".join(str(x).lower() for x in argv)
    if "schtasks" not in joined:
        return False
    return any(v in joined for v in _SCHTASKS_WRITE_VERBS)


def pythonw_exe() -> str:
    exe = Path(sys.executable)
    cand = exe.with_name("pythonw.exe")
    return str(cand) if cand.exists() else str(exe)


def iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def write_heartbeat(path: Path, worker: str, extra: dict | None = None,
                    polls: int = 0, interval_s: float | None = None) -> dict:
    now = datetime.now().astimezone()
    rec = {
        "last_run": now.isoformat(timespec="seconds"),
        "last_run_epoch": int(now.timestamp()),
        "last_run_utc": now.astimezone(dt_timezone.utc).isoformat(
            timespec="seconds"),
        "worker": worker,
        "pid": os.getpid(),
        "polls": polls,
        "_readme": (
            "Written on EVERY tick, pass or idle. COMPARE USING last_run_epoch."
        ),
    }
    if interval_s is not None:
        rec["interval_s"] = float(interval_s)
    if extra:
        rec.update(extra)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    tmp.replace(path)
    return rec


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


def pid_alive(pid: int) -> bool:
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


def hush_vbs() -> Path:
    return Path(__file__).resolve().parent / "hush.vbs"


def tr_cmdline(script: Path, root: str, *extra: str) -> str:
    # pythonw is GUI-subsystem, but Task Scheduler (Interactive) still
    # attaches a conhost to capture stdout — that is the burst of flashes
    # at the minute tick (scar 2026-08-26, again 2026-09-01). hush.py
    # FreeConsole() before runpy so the fire is invisible.
    hush_py = Path(__file__).resolve().parent / "hush.py"
    argv = [pythonw_exe(), str(hush_py), str(Path(script).resolve()),
            "--root", str(Path(root).resolve())]
    argv.extend(extra)
    return subprocess.list2cmdline(argv)


def plan_create(task_name: str, tr: str, sc: str, mo: int | None = None,
                st: str | None = None) -> list[str]:
    argv = ["schtasks", "/create", "/tn", task_name, "/tr", tr,
            "/sc", sc, "/f"]
    if mo is not None:
        argv.extend(["/mo", str(mo)])
    if st is not None:
        argv.extend(["/st", st])
    return argv


def run_schtasks(argv: list[str], timeout_s: float = 60) -> dict:
    if schtasks_sandbox_on():
        writes = _schtasks_writes(argv)
        return {
            "argv": argv,
            "rc": 2 if writes else 1,
            "ok": False,
            "out": "PROD_WRITE_REFUSED" if writes else "SCHTASKS_SANDBOX",
            "keith_cmd": None,
            "needs_elevation": False,
            "sandbox": True,
            "kind": "PROD_WRITE_REFUSED" if writes else "SCHTASKS_SANDBOX",
            "note": "COSMOS_SCHTASKS_SANDBOX: native schtasks.exe not invoked",
        }
    try:
        p = subprocess.run(argv, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout_s,
                           creationflags=(CREATE_NO_WINDOW if os.name == "nt" else 0))
    except OSError as e:
        return {"argv": argv, "rc": -1, "ok": False, "out": str(e),
                "keith_cmd": subprocess.list2cmdline(argv),
                "needs_elevation": False,
                "note": "schtasks could not run at all"}
    out = ((p.stdout or "") + (p.stderr or "")).strip()
    low = out.lower()
    denied = p.returncode != 0 and ("access is denied" in low
                                    or "access denied" in low
                                    or "elevat" in low
                                    or "denied" in low)
    return {
        "argv": argv, "rc": p.returncode, "ok": p.returncode == 0, "out": out,
        "needs_elevation": denied,
        "keith_cmd": subprocess.list2cmdline(argv) if p.returncode != 0 else None,
    }


def query_task(name: str) -> dict:
    argv = ["schtasks", "/query", "/tn", name, "/fo", "LIST", "/v"]
    rec = run_schtasks(argv, timeout_s=30)
    rec["name"] = name
    return rec


def run_task(name: str) -> dict:
    return run_schtasks(["schtasks", "/run", "/tn", name], timeout_s=30)


def create_task(task_name: str, tr: str, sc: str, mo: int | None = None,
                st: str | None = None, run_now: bool = False) -> dict:
    rec = run_schtasks(plan_create(task_name, tr, sc, mo=mo, st=st))
    if rec.get("ok"):
        rec["harden"] = harden_task(task_name)
        if run_now:
            rec["run"] = run_task(task_name)
            rec["run_ok"] = bool(rec["run"].get("ok"))
    return rec


def harden_task(task_name: str) -> dict:
    """Disable the 72h ExecutionTimeLimit and battery-stop (daemon survival)."""
    if schtasks_sandbox_on():
        return {
            "ok": False,
            "out": "PROD_WRITE_REFUSED",
            "keith_cmd": None,
            "sandbox": True,
            "kind": "PROD_WRITE_REFUSED",
            "note": "COSMOS_SCHTASKS_SANDBOX: Set-ScheduledTask not invoked",
        }
    # Names with spaces must be quoted for -TaskName.
    ps = (
        "$t = Get-ScheduledTask -TaskName %s -ErrorAction Stop; "
        "$t.Settings.ExecutionTimeLimit = 'PT0S'; "
        "$t.Settings.StopIfGoingOnBatteries = $false; "
        "$t.Settings.DisallowStartIfOnBatteries = $false; "
        "$t.Settings.Hidden = $true; "
        "$t.Settings.MultipleInstances = 'IgnoreNew'; "
        "Set-ScheduledTask -InputObject $t | Out-Null; "
        "$s = (Get-ScheduledTask -TaskName %s).Settings; "
        "$s.ExecutionTimeLimit; $s.Hidden"
    ) % (json.dumps(task_name), json.dumps(task_name))
    try:
        p = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=30, creationflags=(CREATE_NO_WINDOW if os.name == "nt" else 0))
    except OSError as e:
        return {"ok": False, "out": str(e), "keith_cmd": None}
    out = ((p.stdout or "") + (p.stderr or "")).strip()
    ok = (p.returncode == 0
          and "PT0S" in out.upper().replace(" ", "")
          and "true" in out.lower())
    low = out.lower()
    denied = p.returncode != 0 and ("access is denied" in low or "denied" in low)
    keith = None
    if not ok:
        keith = (
            "powershell -NoProfile -Command "
            + json.dumps(
                "$t=Get-ScheduledTask -TaskName %s; "
                "$t.Settings.ExecutionTimeLimit='PT0S'; "
                "$t.Settings.StopIfGoingOnBatteries=$false; "
                "$t.Settings.DisallowStartIfOnBatteries=$false; "
                "$t.Settings.Hidden=$true; "
                "$t.Settings.MultipleInstances='IgnoreNew'; "
                "Set-ScheduledTask -InputObject $t" % json.dumps(task_name)
            )
        )
    return {"ok": ok, "rc": p.returncode, "out": out[:500],
            "needs_elevation": denied, "keith_cmd": keith}


def spawn_wmi(argv: list[str], cwd: str) -> dict:
    cmdline = subprocess.list2cmdline(argv)
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


def spawn_popen_detached(argv: list[str], cwd: str, log_path: Path) -> dict:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    flags_breakaway = (DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
                       | CREATE_NO_WINDOW | CREATE_BREAKAWAY_FROM_JOB)
    flags_plain = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW
    log_fh = open(log_path, "ab")
    err = None
    try:
        try:
            p = subprocess.Popen(
                argv, stdin=subprocess.DEVNULL, stdout=log_fh,
                stderr=subprocess.STDOUT, cwd=cwd, close_fds=True,
                creationflags=flags_breakaway)
            flags_used = flags_breakaway
            breakaway = True
        except OSError as e:
            err = str(e)
            breakaway = False
            p = subprocess.Popen(
                argv, stdin=subprocess.DEVNULL, stdout=log_fh,
                stderr=subprocess.STDOUT, cwd=cwd, close_fds=True,
                creationflags=flags_plain)
            flags_used = flags_plain
    finally:
        log_fh.close()
    rec = {"method": "popen", "pid": p.pid, "argv": argv, "log": str(log_path),
           "creationflags": flags_used, "breakaway": breakaway, "ok": True}
    if err:
        rec["breakaway_error"] = err
    return rec


def spawn_detached(argv: list[str], cwd: str, log_path: Path) -> dict:
    wmi = spawn_wmi(argv, cwd)
    if wmi.get("ok"):
        return wmi
    pop = spawn_popen_detached(argv, cwd, log_path)
    pop["wmi_failed"] = wmi
    return pop


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
                and pid_alive(int(last.get("pid") or 0))):
            return {"ok": True, "heartbeat": last, "age_s": round(age, 3),
                    "path": str(hb_path)}
        time.sleep(0.4)
    return {"ok": False, "heartbeat": last, "age_s": heartbeat_age_s(last),
            "path": str(hb_path)}


def atomic_json(path: Path, obj) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1, default=str), encoding="utf-8")
    tmp.replace(path)
