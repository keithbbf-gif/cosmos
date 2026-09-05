#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fence isolation — suites heartbeat into a SCRATCH root, never production.

Closes the residual finding of CLOCK_POSTMORTEM.md: if a suite writes the
production heartbeat path, a dead worker reads FRESH for FRESH_S and the
staleness signal becomes producible by something other than the daemon.

Fast rows (default) prove the guard itself bites and does not over-refuse.
The sweep row is the whole-fence measurement and is opt-in because it re-runs
every sibling suite (~60 s, spins a real Service):

    py -3.14 builds\\cvm-dt\\test_cvm_fence_isolation.py
    py -3.14 builds\\cvm-dt\\test_cvm_fence_isolation.py --sweep <PROD_LOGS_DIR>
    py -3.14 builds\\cvm-dt\\test_cvm_fence_isolation.py --sweep <PROD_LOGS_DIR> \\
             --fence builds\\cvm-phone

rc=0 is not the gate. The runtime-binding value for the sweep is named, not
claimed: the (size, mtime_ns, sha256) of every `cvm_dt*` / `cvm_phone*` file in
the production logs dir, read before and after each suite, identical across
all of them — a value only an actually-isolated run can emit.
"""
from __future__ import annotations

import hashlib
import json
import runpy
import sys
import tempfile
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
for _p in (_HERE, _HERE.parents[1] / "cosmos"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import cosmos_clock  # noqa: E402
from cosmos_paths import CosmosPaths, write_sentinel  # noqa: E402

import cvm_dt_clock as clk  # noqa: E402
from cvm_test_guard import ProductionWriteRefused, sandbox_heartbeats  # noqa: E402

TREE_ID = "KMesh-COSMOS-live"
# Names these two fences' workers own in a production logs dir.
OWNED = ("cvm_dt", "cvm_phone")


def _scratch() -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="cvm-fence-iso-"))
    write_sentinel(tmp, TREE_ID)
    for sub in ("config", "state", "logs"):
        (tmp / sub).mkdir()
    (tmp / "config" / "api_token.txt").write_text("test-token",
                                                  encoding="utf-8")
    return tmp


def _nontemp_target(name: str) -> Path:
    """A writable path that is deliberately NOT under the OS temp dir."""
    d = _HERE / "_disposal" / "guard_probe"
    d.mkdir(parents=True, exist_ok=True)
    p = d / name
    if p.exists():
        p.unlink()
    return p


def test_guard_refuses_nonscratch_heartbeat():
    """A heartbeat aimed off the scratch root REFUSES, and writes nothing."""
    target = _nontemp_target("would_be_production_heartbeat.json")
    with sandbox_heartbeats():
        try:
            cosmos_clock.write_heartbeat(target, "cvm-dt-clock")
            raise AssertionError("guard did not refuse a non-scratch write")
        except ProductionWriteRefused as e:
            detail = str(e)
    assert "PROD_WRITE_REFUSED" in detail, detail
    assert target.name in detail, detail
    assert not target.exists(), "refused write still created %s" % target
    return {"kind": "PROD_WRITE_REFUSED", "target_exists": target.exists()}


def test_guard_refuses_nonscratch_lock():
    """Same fail-closed rule for the OS lock file."""
    target = _nontemp_target("would_be_production.lock")
    with sandbox_heartbeats():
        try:
            cosmos_clock.acquire_lock(target)
            raise AssertionError("guard did not refuse a non-scratch lock")
        except ProductionWriteRefused as e:
            detail = str(e)
    assert "PROD_WRITE_REFUSED" in detail, detail
    assert not target.exists(), "refused lock still created %s" % target
    return {"kind": "PROD_WRITE_REFUSED", "target_exists": target.exists()}


def test_guard_allows_scratch_tick():
    """Not over-refusing: a real tick on a scratch root still heartbeats."""
    tmp = _scratch()
    with sandbox_heartbeats() as info:
        rec = clk.poll_once(str(tmp), polls=1, base="http://127.0.0.1:1")
    hb = CosmosPaths(tmp).logs(clk.HEARTBEAT_NAME)
    assert hb.exists(), "scratch heartbeat was not written"
    body = json.loads(hb.read_text(encoding="utf-8"))
    assert body["worker"] == clk.WORKER, body
    assert body["last_run_epoch"] > 0, body
    assert rec["kind"] == "UNREACHABLE", rec  # dead Core is still typed
    assert info["heartbeat_modules"] >= 1, info
    return {"heartbeat": str(hb), "last_run_epoch": body["last_run_epoch"],
            "rebound_modules": info}


def test_guard_restores_on_exit():
    """The monkeypatch is scoped; nothing leaks past the context."""
    before = cosmos_clock.write_heartbeat, cosmos_clock.acquire_lock
    with sandbox_heartbeats():
        assert cosmos_clock.write_heartbeat is not before[0]
    assert cosmos_clock.write_heartbeat is before[0], "write_heartbeat leaked"
    assert cosmos_clock.acquire_lock is before[1], "acquire_lock leaked"
    return {"restored": True}


# ---------------------------------------------------------------- the sweep

def _prod_snap(logs: Path) -> dict:
    """(size, mtime_ns, sha) of the files THESE fences own. Fleet files are
    hashed only by stat: a live daemon can hold its own .log open."""
    out = {}
    for p in sorted(logs.iterdir()):
        if not p.is_file():
            continue
        st = p.stat()
        h = ""
        if p.name.startswith(OWNED):
            try:
                h = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
            except OSError as e:
                h = "ERR:%s" % type(e).__name__
        out[p.name] = [st.st_size, st.st_mtime_ns, h]
    return out


def sweep(fence: Path, logs: Path) -> dict:
    """Run every sibling suite under the guard; blame per suite, not per run."""
    rows = []
    suites = [s for s in sorted(fence.glob("test_*.py"))
              if s.resolve() != Path(__file__).resolve()]
    for s in suites:
        before = _prod_snap(logs)
        saved, sys.argv = list(sys.argv), [s.name]
        t0, rc, err = time.perf_counter(), 0, None
        try:
            with sandbox_heartbeats():
                runpy.run_path(str(s), run_name="__main__")
        except SystemExit as e:
            rc = int(e.code or 0)
        except BaseException as e:                                # noqa: BLE001
            rc, err = 99, "%s: %s" % (type(e).__name__, e)
        finally:
            sys.argv = saved
        after = _prod_snap(logs)
        touched = set(after) ^ set(before)
        touched |= {k for k in after if k in before and after[k] != before[k]}
        rows.append({"suite": s.name, "rc": rc, "error": err,
                     "secs": round(time.perf_counter() - t0, 2),
                     "leaked": sorted(k for k in touched
                                      if k.startswith(OWNED))})
        print("  %-32s rc=%d leaked=%s" % (s.name, rc, rows[-1]["leaked"]),
              file=sys.stderr, flush=True)
    return {"logs": str(logs), "suites": rows,
            "any_leak": sorted({n for r in rows for n in r["leaked"]}),
            "any_rc": sorted({r["rc"] for r in rows})}


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
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

    check("NEGATIVE heartbeat outside the scratch root is REFUSED",
          test_guard_refuses_nonscratch_heartbeat)
    check("NEGATIVE lock outside the scratch root is REFUSED",
          test_guard_refuses_nonscratch_lock)
    check("guard does not over-refuse: scratch tick still heartbeats",
          test_guard_allows_scratch_tick)
    check("guard restores the real helpers on exit", test_guard_restores_on_exit)

    if "--sweep" in argv:
        i = argv.index("--sweep")
        if i + 1 >= len(argv):
            print("--sweep needs the PRODUCTION logs dir", file=sys.stderr)
            return 2
        fence = _HERE
        if "--fence" in argv:                 # sweep a sibling fence too
            fence = Path(argv[argv.index("--fence") + 1]).resolve()
        rec = sweep(fence, Path(argv[i + 1]))
        live["sweep"] = rec
        if rec["any_leak"] or any(r for r in rec["any_rc"] if r):
            print("FAIL  whole-fence sweep leaked/failed: %s"
                  % json.dumps({"leak": rec["any_leak"], "rc": rec["any_rc"]}))
            fail += 1
        else:
            print("PASS  whole-fence sweep: %d suites, 0 production writes"
                  % len(rec["suites"]))
            ok += 1

    print("live_value: %s" % json.dumps(live, sort_keys=True, default=str))
    print("result: %s  %d/%d" % ("ok" if not fail else "FAIL",
                                 ok, ok + fail))
    return 0 if not fail else 1


if __name__ == "__main__":
    raise SystemExit(main())
