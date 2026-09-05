#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bounce Core :8770 onto this tree, then start Pulse --loop if dead.

Does not /delete schtasks. Does not touch other pythonw clocks.
Kill is only the verified cosmos.py serve listener.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_clock import pid_alive, pythonw_exe, spawn_detached  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
ROOT = r"V:\A\Ai\COSMOS\live"
PYW = pythonw_exe()
STATUS = "http://127.0.0.1:8770/api/v1/status"


def listener_pid(port: int = 8770) -> int | None:
    out = subprocess.check_output(
        "netstat -ano -p tcp", shell=True, text=True, errors="replace")
    for line in out.splitlines():
        if f":{port}" in line and "LISTENING" in line:
            try:
                return int(line.strip().split()[-1])
            except ValueError:
                continue
    return None


def cmdline(pid: int) -> str:
    r = subprocess.run(
        ["wmic", "process", "where", f"ProcessId={pid}",
         "get", "CommandLine", "/format:list"],
        capture_output=True, text=True, errors="replace")
    for line in r.stdout.splitlines():
        if line.startswith("CommandLine="):
            return line.split("=", 1)[1].strip()
    return ""


def get(path: str, timeout: float = 5.0):
    try:
        with urllib.request.urlopen("http://127.0.0.1:8770" + path, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))
    except Exception as e:  # noqa: BLE001
        return 0, {"error": "%s: %s" % (type(e).__name__, e)}


def wait_status(timeout_s: float = 40.0) -> dict:
    deadline = time.time() + timeout_s
    last = None
    while time.time() < deadline:
        code, body = get("/api/v1/status", timeout=3.0)
        last = {"code": code, "body": body}
        if code == 200 and body.get("ready") is True:
            return last
        time.sleep(0.8)
    return last or {"code": 0, "body": {"error": "timeout"}}


def main() -> int:
    rec: dict = {"ok": False}
    pid = listener_pid()
    rec["old_pid"] = pid
    rec["old_cmd"] = cmdline(pid) if pid else ""
    if pid and "cosmos.py" in rec["old_cmd"] and "serve" in rec["old_cmd"]:
        k = subprocess.run(["taskkill", "/PID", str(pid), "/F"],
                           capture_output=True, text=True, errors="replace")
        rec["kill_rc"] = k.returncode
        rec["kill_out"] = (k.stdout + k.stderr).strip()[:300]
        time.sleep(1.0)
    else:
        rec["kill_rc"] = None
        rec["kill_out"] = "no verified serve listener"

    rec["status_after"] = wait_status()
    rec["new_pid"] = listener_pid()
    rec["new_cmd"] = cmdline(rec["new_pid"]) if rec["new_pid"] else ""

    # Pulse: start --loop if no living cosmos_pulse.py
    pulse_alive = False
    r = subprocess.run(
        ["wmic", "process", "where", "Name='pythonw.exe'",
         "get", "ProcessId,CommandLine", "/format:list"],
        capture_output=True, text=True, errors="replace")
    blocks = r.stdout.split("\n\n")
    for b in blocks:
        if "cosmos_pulse.py" in b:
            pulse_alive = True
            rec["pulse_existing"] = b.strip()[:400]
            break
    if not pulse_alive:
        argv = [PYW, str(REPO / "cosmos" / "cosmos_pulse.py"),
                "--root", ROOT, "--loop"]
        rec["pulse_spawn"] = spawn_detached(
            argv, str(REPO), Path(ROOT) / "logs" / "pulse_loop.out")
    rec["routes"] = {}
    for path in ("/api/v1/status", "/api/v1/surfaces",
                 "/api/v1/fleet", "/api/v1/nodemap", "/api/v1/jukebox"):
        rec["routes"][path] = get(path)
    rec["ok"] = (
        rec["status_after"].get("code") == 200
        and rec["routes"]["/api/v1/fleet"][0] == 200
        and rec["routes"]["/api/v1/nodemap"][0] == 200
        and rec["routes"]["/api/v1/jukebox"][0] == 200
        and rec["routes"]["/api/v1/surfaces"][0] == 200
    )
    print(json.dumps(rec, indent=1, default=str))
    return 0 if rec["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
