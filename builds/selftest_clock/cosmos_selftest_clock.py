#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_selftest_clock.py -- the gate that gates the gates.

COSMOS canon says "every gate executes" and "rc=0 is NOT done -- bind every claim
to a real emitted artifact". On 2026-08-30 an audit found 34 of 58 suites failing,
27 of them unable to even import the modules they test. Nothing was running them,
so a CRITICAL defect in the motif route (the in-flight set counted COMPLETED work,
wedging all 10 deliverables) shipped underneath a red suite and stayed there.

This daemon closes that hole. It runs the suite on a clock and publishes the result
as a heartbeat artifact, exactly like every other COSMOS daemon, so a red suite is
visible in the same place the fleet's health already lives.

Canon:
  - No hard-coded paths: the tree is passed with --root; every path resolves under it.
  - Fail-closed: a suite that will not import is a FAIL, never a skip.
  - Never-delete: results are written, nothing is pruned.
  - PYTHONUTF8=1 is forced for children -- a cp1252 console must never turn a
    passing suite red (scar 2026-08-30: test_cvm_push died on an arrow character).
  - Flake-aware: a failing suite is retried once. Passing on retry is recorded as
    FLAKY, not as PASS -- a non-deterministic gate is a broken gate, and hiding it
    behind a retry is the fabricated-compliance failure this system exists to refuse.
  - Windowless on Windows (CREATE_NO_WINDOW); PAUSE-aware; heartbeated.

Emits <runtime_root>/logs/selftest_clock_heartbeat.json on EVERY tick, pass or idle:
  {passed, failed, flaky, total, failing: [...], flaky_names: [...], elapsed_s}

Run:
  py -3.14 builds\\selftest_clock\\cosmos_selftest_clock.py --root V:\\A\\Ai\\COSMOS --once
  py -3.14 builds\\selftest_clock\\cosmos_selftest_clock.py --root V:\\A\\Ai\\COSMOS --interval 900
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

NO_WINDOW = 0x08000000 if os.name == "nt" else 0
HEARTBEAT_NAME = "selftest_clock_heartbeat.json"
SCHEMA = "cosmos-selftest-clock/1"
DEFAULT_TIMEOUT_S = 120


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def child_env() -> dict:
    """UTF-8 forced. A console codec must never decide whether a gate is green."""
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def run_suite(path: Path, cwd: Path, timeout: int) -> tuple[bool, str]:
    """Run one suite. Returns (ok, tail). A crash is a failure, never a skip."""
    try:
        p = subprocess.run(
            [sys.executable, str(path)], capture_output=True, text=True,
            encoding="utf-8", errors="replace", cwd=str(cwd), timeout=timeout,
            env=child_env(), creationflags=NO_WINDOW, stdin=subprocess.DEVNULL,
        )
        out = ((p.stdout or "") + (p.stderr or "")).strip()
        return p.returncode == 0, out[-400:]
    except subprocess.TimeoutExpired:
        return False, f"TIMEOUT after {timeout}s"
    except Exception as e:                                            # noqa: BLE001
        return False, f"{type(e).__name__}: {e}"


def tick(repo: Path, runtime_root: Path, timeout: int) -> dict:
    t0 = time.time()
    tests_dir = repo / "tests"
    if not tests_dir.is_dir():
        return {"ok": False, "schema": SCHEMA, "ts": _now(),
                "error": f"NO_TESTS_DIR: {tests_dir}"}

    # builds/<x>/test_*.py counts too. A deliverable that ships its own suite
    # beside itself is still a gate, and globbing only tests/ left those
    # ungated -- the health watchdog's 17 checks were passing where nothing
    # was looking. Gate the gates means ALL of them. (2026-08-30)
    suites = sorted(tests_dir.glob("test_*.py"))
    builds_dir = repo / "builds"
    if builds_dir.is_dir():
        seen = {p.resolve() for p in suites}
        for p in sorted(builds_dir.glob("*/test_*.py")):
            if "__pycache__" in p.parts or p.resolve() in seen:
                continue
            suites.append(p)
    passed, failing, flaky = 0, [], []

    for s in suites:
        ok, tail = run_suite(s, repo, timeout)
        if ok:
            passed += 1
            continue
        # One retry: distinguishes a real failure from a flake. A suite that
        # only passes on retry is FLAKY -- recorded, never counted as passing.
        ok2, tail2 = run_suite(s, repo, timeout)
        if ok2:
            flaky.append(s.name)
        else:
            failing.append({"suite": s.name, "tail": tail2 or tail})

    return {
        "ok": not failing,
        "schema": SCHEMA,
        "ts": _now(),
        "total": len(suites),
        "passed": passed,
        "flaky": len(flaky),
        "failed": len(failing),
        "flaky_names": flaky,
        "failing": failing,
        "elapsed_s": round(time.time() - t0, 1),
        "repo": str(repo),
    }


TASK_NAME = "COSMOS Selftest Clock"


def _pythonw() -> str:
    """pythonw beside this interpreter: the clock must not flash a console every
    15 minutes. Falls back to the console python when pythonw is absent."""
    cand = Path(sys.executable).with_name("pythonw.exe")
    return str(cand) if cand.exists() else sys.executable


def plan_task_argv(repo: Path, interval_min: int = 15) -> list[str]:
    """schtasks /create plan. Current-user, NO /rl highest -- running the suite
    needs no elevation, and asking for it would be capability this does not need."""
    tr = subprocess.list2cmdline([
        _pythonw(), str(Path(__file__).resolve()),
        "--root", str(repo), "--once",
    ])
    return ["schtasks", "/create", "/tn", TASK_NAME, "/tr", tr,
            "/sc", "minute", "/mo", str(interval_min), "/f"]


def install_task(repo: Path, interval_min: int = 15) -> dict:
    """Register the clock. A nonzero rc is REPORTED, never swallowed."""
    argv = plan_task_argv(repo, interval_min)
    try:
        p = subprocess.run(argv, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=60,
                           creationflags=NO_WINDOW)
    except OSError as e:
        return {"ok": False, "rc": -1, "argv": argv, "out": str(e)}
    out = ((p.stdout or "") + (p.stderr or "")).strip()
    return {"ok": p.returncode == 0, "rc": p.returncode, "argv": argv, "out": out}


def paused(runtime_root: Path) -> bool:
    """Unreadable control flag = fail-closed: treat as paused, do not run."""
    flag = runtime_root / "state" / "control" / "PAUSE.flag"
    try:
        return str(json.loads(flag.read_text(encoding="utf-8") or "{}")
                   .get("state", "PAUSED")).upper() != "RUNNING"
    except FileNotFoundError:
        return False
    except Exception:                                                 # noqa: BLE001
        return True


def write_heartbeat(runtime_root: Path, rec: dict) -> Path:
    hb = runtime_root / "logs" / HEARTBEAT_NAME
    hb.parent.mkdir(parents=True, exist_ok=True)
    body = dict(rec)
    body.update({
        "worker": "cosmos-selftest-clock",
        "pid": os.getpid(),
        "last_run": datetime.now().astimezone().isoformat(),
        "last_run_epoch": int(time.time()),
        "_readme": ("Written on EVERY tick, pass or idle. COMPARE USING "
                    "last_run_epoch. Older than ~2x the interval means this "
                    "clock failed. failed>0 means the tree is NOT gated green; "
                    "flaky>0 means a gate is non-deterministic, which is also "
                    "a broken gate."),
    })
    tmp = hb.with_suffix(".tmp")
    tmp.write_text(json.dumps(body, indent=1), encoding="utf-8")
    os.replace(tmp, hb)                                    # atomic
    return hb


def main() -> int:
    ap = argparse.ArgumentParser(description="COSMOS selftest clock")
    ap.add_argument("--root", required=True,
                    help="repo tree (contains tests/); runtime defaults to <root>/live")
    ap.add_argument("--runtime-root", default=None)
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_S)
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--interval", type=float, default=0.0)
    ap.add_argument("--plan-task", action="store_true",
                    help="print the schtasks argv without registering anything")
    ap.add_argument("--install-task", action="store_true",
                    help="register the 15-minute clock for the current user")
    ap.add_argument("--every-min", type=int, default=15)
    a = ap.parse_args()

    repo = Path(a.root).resolve()
    runtime_root = Path(a.runtime_root).resolve() if a.runtime_root else repo / "live"

    # Identity, not existence (the mesh() scar): refuse a root that is not COSMOS.
    sentinel = runtime_root / ".cosmos-root.json"
    try:
        if str(json.loads(sentinel.read_text(encoding="utf-8")).get("system")) != "COSMOS":
            print(f"[selftest_clock] REFUSED [IDENTITY_MISMATCH] {sentinel}", file=sys.stderr)
            return 2
    except FileNotFoundError:
        print(f"[selftest_clock] REFUSED [NO_ROOT] no sentinel at {sentinel}", file=sys.stderr)
        return 2

    if a.plan_task:
        print(json.dumps({"task": TASK_NAME,
                          "argv": plan_task_argv(repo, a.every_min)}, indent=1))
        return 0
    if a.install_task:
        rec = install_task(repo, a.every_min)
        print(json.dumps(rec, indent=1))
        return 0 if rec["ok"] else 1

    def one() -> dict:
        if paused(runtime_root):
            rec = {"ok": True, "schema": SCHEMA, "ts": _now(), "tick": "paused"}
        else:
            rec = tick(repo, runtime_root, a.timeout)
        write_heartbeat(runtime_root, rec)
        return rec

    if a.once or not a.interval:
        rec = one()
        print(json.dumps(rec, indent=1))
        # rc reflects the GATE, not the daemon: non-zero when the tree is not green.
        return 0 if rec.get("ok") else 1

    while True:
        try:
            rec = one()
            print(f"[selftest_clock] {rec.get('passed')}/{rec.get('total')} pass, "
                  f"{rec.get('failed')} fail, {rec.get('flaky')} flaky", flush=True)
        except KeyboardInterrupt:
            return 0
        except Exception as e:                                        # noqa: BLE001
            print(f"[selftest_clock] tick error (daemon continues): {e}", flush=True)
        time.sleep(a.interval)


if __name__ == "__main__":
    raise SystemExit(main())
