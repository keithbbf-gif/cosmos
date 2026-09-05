#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cvm-dt-voice DAEMON VEHICLE — the parts that make it schedulable at all.

CLOCK_POSTMORTEM.md: voice sat 3.5 days stale not because it crashed but
because it had no vehicle — no task name, no lock, no `--loop`, no
`--register`. The vehicle now exists; these rows are what keeps it existing.
The voice behaviour suite (test_cvm_dt_voice.py) covers ear/mouth; this one
covers only single-instance, emit-don't-run, and the argv round-trip.

The negative that matters: a SECOND instance under a held OS lock must
REFUSE — measured with a real second process, not a simulated one, because
"two Claude/daemon copies on one tree" is a defect that only reproduces
across process boundaries.

    py -3.14 builds\\cvm-dt\\test_cvm_dt_voice_vehicle.py

rc=0 is not the gate. Runtime-binding value, named: the child process's real
pid holding the lock while the parent's `_locked` returns rc=2, and the exact
argv `register()` emits parsing clean through `voice_parser()` — a worker
whose own emitted command line it would reject is the postmortem's bug again.
"""
from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
import tempfile
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
for _p in (_HERE, _HERE.parents[1] / "cosmos"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from cosmos_clock import write_heartbeat  # noqa: E402
from cosmos_paths import CosmosPaths, write_sentinel  # noqa: E402

import cvm_dt_voice as vox  # noqa: E402

TREE_ID = "KMesh-COSMOS-live"

# Child: take the OS lock on argv[1], say READY, hold it until told to stop.
_HOLDER = """
import sys, time
sys.path.insert(0, sys.argv[2])
from cosmos_clock import acquire_lock
from pathlib import Path
fd = acquire_lock(Path(sys.argv[1]))
print("READY" if fd is not None else "NOLOCK", flush=True)
time.sleep(float(sys.argv[3]))
"""


def _scratch() -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="cvm-dt-voice-vehicle-"))
    write_sentinel(tmp, TREE_ID)
    for sub in ("config", "state", "logs"):
        (tmp / sub).mkdir()
    (tmp / "config" / "api_token.txt").write_text("test-token",
                                                  encoding="utf-8")
    return tmp


def _hold_lock(paths: CosmosPaths, seconds: float = 20.0):
    """Spawn a real second process holding the worker's lock."""
    proc = subprocess.Popen(
        [sys.executable, "-c", _HOLDER, str(paths.logs(vox.LOCK_NAME)),
         str(_HERE.parents[1] / "cosmos"), str(seconds)],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    line = proc.stdout.readline().strip()
    if line != "READY":
        proc.kill()
        raise AssertionError("lock holder did not start: %r" % line)
    return proc


def test_second_instance_refuses_under_held_lock():
    """NEGATIVE: lock held by a live foreign process, no heartbeat -> rc=2."""
    tmp = _scratch()
    paths = CosmosPaths(tmp)
    proc = _hold_lock(paths)
    try:
        assert proc.poll() is None, "holder died before the test ran"
        fd, rc = vox._locked(paths)
        assert fd is None, "second instance got the lock while it was held"
        assert rc == 2, "expected REFUSE rc=2, got %r" % rc
        holder_pid = proc.pid
    finally:
        proc.kill()
        proc.wait(timeout=10)
    return {"holder_pid": holder_pid, "second_instance_fd": None, "rc": 2}


def test_second_instance_noops_when_holder_is_skip_alive():
    """Held lock + a live matching heartbeat -> quiet no-op (rc=0), never a
    second daemon and never a refusal storm from the 1-min self-heal task."""
    tmp = _scratch()
    paths = CosmosPaths(tmp)
    proc = _hold_lock(paths)
    try:
        write_heartbeat(paths.logs(vox.HEARTBEAT_NAME), vox.WORKER,
                        extra={"pid": proc.pid}, polls=7)
        # write_heartbeat stamps os.getpid(); the holder is the real owner.
        hb = paths.logs(vox.HEARTBEAT_NAME)
        rec = json.loads(hb.read_text(encoding="utf-8"))
        rec["pid"] = proc.pid
        hb.write_text(json.dumps(rec), encoding="utf-8")

        assert vox.skip_alive(paths) is not None, "skip_alive did not see it"
        fd, rc = vox._locked(paths)
        assert fd is None, "second instance got the lock while it was held"
        assert rc == 0, "expected skip_alive no-op rc=0, got %r" % rc
        holder_pid = proc.pid
    finally:
        proc.kill()
        proc.wait(timeout=10)
    return {"holder_pid": holder_pid, "rc": 0, "polls_seen": rec["polls"]}


def test_lock_is_free_once_the_holder_exits():
    """The lock FILE is not the lock: Windows drops it when the pid dies."""
    tmp = _scratch()
    paths = CosmosPaths(tmp)
    proc = _hold_lock(paths)
    proc.kill()
    proc.wait(timeout=10)
    assert paths.logs(vox.LOCK_NAME).exists(), "lock file vanished"
    fd, rc = vox._locked(paths)
    assert fd is not None, "stale lock FILE wrongly blocked a fresh start"
    os.close(fd)
    return {"stale_lock_file_present": True, "acquired_after_exit": True}


def test_register_emits_and_does_not_run():
    """--register EMITS the schtasks line. It must never execute one."""
    tmp = _scratch()
    rec = vox.register(str(tmp))
    assert rec["ran"] is False, rec
    assert rec["task_name"] == "COSMOS CVM DT Voice", rec
    assert rec["task_logon"] == "COSMOS CVM DT Voice Logon", rec
    assert len(rec["keith_cmds"]) == 2, rec
    joined = " ".join(rec["keith_cmds"])
    assert "schtasks" in joined and "/create" in joined.lower(), joined
    assert "--loop" in joined, joined
    assert "pythonw" in Path(rec["pythonw"]).name.lower(), rec["pythonw"]
    assert "/sc minute" in joined.lower() or "minute" in joined, joined
    assert "onlogon" in joined.lower(), joined
    return {"ran": rec["ran"], "cmds": rec["keith_cmds"]}


def test_emitted_argv_parses_back():
    """The command line register() emits must be one voice_main accepts —
    the postmortem's bug in miniature: an emitted `--loop` the parser would
    have rejected as unrecognized."""
    tmp = _scratch()
    rec = vox.register(str(tmp))
    argv = shlex.split(rec["tr"], posix=False)
    # tr is "<pythonw> <script> --root <root> --loop"; drop exe + script.
    flags = [a.strip('"') for a in argv[2:]]
    ns = vox.voice_parser().parse_args(flags)
    assert ns.loop is True, ns
    assert Path(ns.root).resolve() == tmp.resolve(), (ns.root, str(tmp))
    assert ns.selftest is False and ns.register is False, ns
    return {"flags": flags, "parsed_loop": ns.loop}


def test_status_names_unregistered_not_merely_stale():
    """A never-scheduled worker must READ as never-scheduled."""
    tmp = _scratch()
    rec = vox.status(str(tmp))
    assert rec["task_name"] == "COSMOS CVM DT Voice", rec
    assert rec["age_s"] is None, rec           # no heartbeat in a fresh root
    assert rec["fresh"] is False, rec
    assert isinstance(rec["registered"], bool), rec
    rc = vox.voice_main(["--root", str(tmp), "--status"])
    assert rc == 2, "unregistered/stale --status must fail closed, got %r" % rc
    return {"rc": rc, "registered": rec["registered"], "fresh": rec["fresh"]}


def test_heartbeat_carries_the_staleness_readme():
    """Every tick's heartbeat carries the _readme other COSMOS daemons carry,
    so a reader compares last_run_epoch and not the file's mtime."""
    tmp = _scratch()
    paths = CosmosPaths(tmp)
    t0 = time.time()
    write_heartbeat(paths.logs(vox.HEARTBEAT_NAME), vox.WORKER,
                    extra={"tick": "idle"}, polls=1, interval_s=2.0)
    body = json.loads(paths.logs(vox.HEARTBEAT_NAME).read_text(
        encoding="utf-8"))
    assert "_readme" in body, body
    assert "last_run_epoch" in body["_readme"], body["_readme"]
    assert body["worker"] == vox.WORKER, body
    assert body["last_run_epoch"] >= int(t0), body
    return {"_readme": body["_readme"],
            "last_run_epoch": body["last_run_epoch"]}


def main() -> int:
    ok = fail = 0
    live: dict = {}

    def check(label, fn):
        nonlocal ok, fail
        try:
            live[label] = fn()
            print("PASS  %s" % label)
            ok += 1
        except Exception as e:                                    # noqa: BLE001
            print("FAIL  %s: %s: %s" % (label, type(e).__name__, e))
            fail += 1

    check("NEGATIVE second instance REFUSES under a real held OS lock (rc=2)",
          test_second_instance_refuses_under_held_lock)
    check("held lock + live matching heartbeat is a quiet no-op (rc=0)",
          test_second_instance_noops_when_holder_is_skip_alive)
    check("stale lock FILE does not block a fresh start",
          test_lock_is_free_once_the_holder_exits)
    check("--register EMITS schtasks and does not run it",
          test_register_emits_and_does_not_run)
    check("the emitted command line parses back through voice_parser",
          test_emitted_argv_parses_back)
    check("--status fails closed on unregistered, not merely stale",
          test_status_names_unregistered_not_merely_stale)
    check("heartbeat carries the _readme staleness note",
          test_heartbeat_carries_the_staleness_readme)

    print("live_value: %s" % json.dumps(live, sort_keys=True, default=str))
    print("result: %s  %d/%d" % ("ok" if not fail else "FAIL", ok, ok + fail))
    return 0 if not fail else 1


if __name__ == "__main__":
    raise SystemExit(main())
