#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: the Core :8770 supervisor inside cosmos_health_clock.

Isolated from the live root and from the live port. `_probe_port` and
`spawn_detached` are BOTH injected, so this suite never opens a socket on 8770
and never starts a second Core -- the one thing the diagnosis
(builds/probe/CORE_8770_DIAGNOSIS.md) was careful not to do either.

Proves the two halves of the contract:
  1. supervise OFF is inert -- no row, no state file, no lock file, NO SPAWN.
  2. supervise ON is fail-closed -- every non-spawn path returns a typed kind
     (DISABLED, ALREADY_UP, PAUSED_HOLD, BACKOFF, CHILD_ALIVE, SUPERVISOR_BUSY,
     SPAWN_FAILED) and only the one legal path returns SPAWNED.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, r"V:\A\Ai\COSMOS\tests")
sys.path.insert(0, r"V:\A\Ai\COSMOS\cosmos")


import cosmos_health_clock as hc                                   # noqa: E402
from cosmos_kernel import install                                  # noqa: E402
from cosmos_clock import acquire_lock                              # noqa: E402
from cosmos_paths import CosmosPaths                               # noqa: E402

RESULTS = []
CALLS = []
PORT_UP = [False]


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def fake_probe(host, port, timeout_s=0.25):
    return {"ok": PORT_UP[0], "host": host, "port": port, "rtt_s": 0.0,
            "error": None if PORT_UP[0] else "injected: not listening"}


def fake_spawn(argv, cwd, log_path):
    CALLS.append({"argv": list(argv), "cwd": str(cwd), "log": str(log_path)})
    return {"ok": True, "pid": 0, "method": "injected"}


def failing_spawn(argv, cwd, log_path):
    CALLS.append({"argv": list(argv), "cwd": str(cwd), "log": str(log_path)})
    return {"ok": False, "error": "injected spawn failure"}


def raising_spawn(argv, cwd, log_path):
    CALLS.append({"argv": list(argv), "cwd": str(cwd), "log": str(log_path)})
    raise OSError("injected: exec not found")


def state_of(root: Path) -> dict:
    p = root / "logs" / hc.SERVE_STATE_NAME
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def put_state(root: Path, **kw) -> None:
    st = state_of(root)
    st.update(kw)
    (root / "logs" / hc.SERVE_STATE_NAME).write_text(
        json.dumps(st), encoding="utf-8")


def main() -> int:
    hc._probe_port = fake_probe
    hc.spawn_detached = fake_spawn

    td = Path(tempfile.mkdtemp(prefix="cosmos_coresup_"))
    root = install(td / "live", tree_id="spike-core-supervisor")
    root_p = install(td / "paused", tree_id="spike-core-supervisor-paused")
    paths = CosmosPaths(str(root))
    paths_p = CosmosPaths(str(root_p))
    state_file = root / "logs" / hc.SERVE_STATE_NAME
    lock_file = root / "logs" / hc.SERVE_LOCK_NAME

    # ---- 1. OFF is inert. The live fleet runs this path right now. -----------
    del CALLS[:]
    r = hc.poll_once(str(root), supervise=False)
    check("supervise OFF: no serve_supervisor row",
          lambda: "serve_supervisor" not in r["rows"])
    check("supervise OFF: NO SPAWN", lambda: CALLS == [])
    check("supervise OFF: no core_serve.json written",
          lambda: not state_file.exists())
    check("supervise OFF: no core_serve.lock written",
          lambda: not lock_file.exists())
    check("supervise OFF: heartbeat carries no supervisor key",
          lambda: "serve_supervisor" not in json.loads(
              (root / "logs" / hc.HEARTBEAT_NAME).read_text(encoding="utf-8")))
    board = json.loads(
        (root / "state" / "health" / "board.json").read_text(encoding="utf-8"))
    check("supervise OFF: board unchanged (no supervisor row)",
          lambda: "serve_supervisor" not in board["rows"])
    check("supervise OFF: serve_8770 still measured and RED",
          lambda: r["rows"]["serve_8770"]["ok"] is False
          and "serve_8770" in board["reds"])

    # ---- 2. Typed refusals, one per non-spawn path --------------------------
    del CALLS[:]
    d = hc._supervise_serve(paths, False, False, False, None)
    check("direct call without supervise -> DISABLED",
          lambda: d["kind"] == "DISABLED" and CALLS == []
          and not state_file.exists())

    u = hc._supervise_serve(paths, True, True, False, None)
    check("port already listening -> ALREADY_UP",
          lambda: u["kind"] == "ALREADY_UP" and CALLS == []
          and not state_file.exists())

    pause = paths_p.role("state") / "control" / "PAUSE.flag"
    pause.parent.mkdir(parents=True, exist_ok=True)
    pause.write_text(json.dumps({"mode": "hold"}), encoding="utf-8")
    p1 = hc._supervise_serve(paths_p, False, True, True, "hold")
    check("PAUSE mode=hold -> PAUSED_HOLD, no spawn",
          lambda: p1["kind"] == "PAUSED_HOLD" and CALLS == [])
    p2 = hc._supervise_serve(paths_p, False, True, True, None)
    check("bare PAUSE flag (no mode) defaults to hold -> PAUSED_HOLD",
          lambda: p2["kind"] == "PAUSED_HOLD" and CALLS == [])
    p3 = hc.poll_once(str(root_p), supervise=True)
    check("poll_once honors PAUSE and still writes its board",
          lambda: p3["rows"]["serve_supervisor"]["kind"] == "PAUSED_HOLD"
          and CALLS == []
          and not (root_p / "logs" / hc.SERVE_STATE_NAME).exists())
    check("a resume-gate PAUSE does NOT block the standup (default is motion)",
          lambda: hc._supervise_serve(paths_p, True, True, True,
                                      "resume-gate")["kind"] == "ALREADY_UP")

    # ---- 3. The one legal spawn path ---------------------------------------
    del CALLS[:]
    s = hc._supervise_serve(paths, False, True, False, None)
    check("port down + enabled -> SPAWNED", lambda: s["kind"] == "SPAWNED")
    check("SPAWNED spawned exactly once", lambda: len(CALLS) == 1)
    argv = CALLS[0]["argv"] if CALLS else []
    check("argv execs THIS tree's cosmos.py serve",
          lambda: Path(argv[1]).name == "cosmos.py"
          and Path(argv[1]).is_file() and argv[2] == "serve")
    check("argv carries the resolved root, not a literal",
          lambda: argv[argv.index("--root") + 1] == str(paths.root)
          and str(root) in argv[argv.index("--root") + 1])
    check("argv carries --port 8770 from the probed constant",
          lambda: argv[argv.index("--port") + 1] == str(hc.SERVE_PORT))
    check("spawn state persisted with a backoff deadline",
          lambda: state_of(root)["fails"] == 0
          and state_of(root)["next_attempt_epoch"] > time.time())
    fd0 = acquire_lock(lock_file)
    check("lock released after the spawn (fd closed)", lambda: fd0 is not None)
    if fd0 is not None:
        os.close(fd0)

    # ---- 4. No respawn storm ------------------------------------------------
    del CALLS[:]
    b = hc._supervise_serve(paths, False, True, False, None)
    check("second tick inside the window -> BACKOFF, no second Core",
          lambda: b["kind"] == "BACKOFF" and CALLS == [])

    put_state(root, next_attempt_epoch=0, pid=os.getpid())
    c = hc._supervise_serve(paths, False, True, False, None)
    check("live child + silent port -> CHILD_ALIVE, never a second writer",
          lambda: c["kind"] == "CHILD_ALIVE" and c["pid"] == os.getpid()
          and CALLS == [])

    put_state(root, next_attempt_epoch=0, pid=0)
    fd = acquire_lock(lock_file)
    busy = hc._supervise_serve(paths, False, True, False, None)
    os.close(fd)
    check("another supervisor holds the lock -> SUPERVISOR_BUSY",
          lambda: busy["kind"] == "SUPERVISOR_BUSY" and CALLS == [])

    # ---- 5. Failure is typed, counted, and backed off -----------------------
    hc.spawn_detached = failing_spawn
    del CALLS[:]
    put_state(root, next_attempt_epoch=0, pid=0, fails=0)
    f1 = hc._supervise_serve(paths, False, True, False, None)
    put_state(root, next_attempt_epoch=0)
    f2 = hc._supervise_serve(paths, False, True, False, None)
    put_state(root, next_attempt_epoch=0)
    f3 = hc._supervise_serve(paths, False, True, False, None)
    check("spawn refusal is typed SPAWN_FAILED",
          lambda: [x["kind"] for x in (f1, f2, f3)] == ["SPAWN_FAILED"] * 3)
    check("failure count climbs", lambda: [x["fails"] for x in (f1, f2, f3)]
          == [1, 2, 3])
    check("backoff ladder climbs 15 -> 30 -> 60",
          lambda: [x["backoff_s"] for x in (f1, f2, f3)] == [15, 30, 60])
    check("backoff ladder is non-decreasing and finite",
          lambda: list(hc.SERVE_BACKOFF_S) == sorted(hc.SERVE_BACKOFF_S)
          and all(isinstance(v, int) and v > 0 for v in hc.SERVE_BACKOFF_S))
    check("SPAWN_FAILED carries the spawner's own error text",
          lambda: "injected spawn failure" in f1["detail"])

    put_state(root, next_attempt_epoch=0)
    rf = hc.poll_once(str(root), supervise=True)
    board2 = json.loads(
        (root / "state" / "health" / "board.json").read_text(encoding="utf-8"))
    check("SPAWN_FAILED is a visible RED on the board, not a swallowed log",
          lambda: rf["rows"]["serve_supervisor"]["ok"] is False
          and "serve_supervisor" in board2["reds"])

    hc.spawn_detached = raising_spawn
    del CALLS[:]
    put_state(root, next_attempt_epoch=0)
    rz = hc._supervise_serve(paths, False, True, False, None)
    check("a raising spawner is caught and typed, not a traceback",
          lambda: rz["kind"] == "SPAWN_FAILED"
          and "exec not found" in rz["detail"])

    # ---- 6. Corrupt state fails closed, never crashes the 2s loop -----------
    hc.spawn_detached = fake_spawn
    del CALLS[:]
    (root / "logs" / hc.SERVE_STATE_NAME).write_text("{not json", encoding="utf-8")
    z = hc._supervise_serve(paths, False, True, False, None)
    check("unreadable core_serve.json is treated as no state, not a crash",
          lambda: z["kind"] == "SPAWNED" and len(CALLS) == 1)

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for l, ok, e in RESULTS:
        print(("  OK  " if ok else "  FAIL") + f" {l}" + (f"  {e}" if e else ""))
    print(f"{len(RESULTS) - len(bad)}/{len(RESULTS)} passed")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
