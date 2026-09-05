#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_cosmos_test_guard - F-60 heartbeat write fence for tests/.

Bite: this file imported nothing named cosmos_test_guard before that
module existed; the first run is FAIL 0/N by ImportError. CONTROL: an
unguarded write_heartbeat to a path outside the OS temp dir actually
writes (the CLOCK_POSTMORTEM scar). The same path under
sandbox_heartbeats is PROD_WRITE_REFUSED and the file is not created.

    py -3.14 tests/test_cosmos_test_guard.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
GUARD = HERE / "cosmos_test_guard.py"

sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "cosmos"))

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def main() -> int:
    if not GUARD.is_file():
        check("tests/cosmos_test_guard.py exists (F-60)", lambda: False)
        check("sandbox_heartbeats is importable", lambda: False)
        print("ABSENT: tests/cosmos_test_guard.py — this is the F-60 bite")
        for label, ok, err in RESULTS:
            print(f"  {'OK  ' if ok else 'FAIL'}  {label}{('  ' + err) if err else ''}")
        print("live_value: " + json.dumps({"state": "ABSENT"}))
        print("result: FAIL  0/2")
        return 1

    from cosmos_test_guard import ProductionWriteRefused, sandbox_heartbeats
    import cosmos_clock

    outside = REPO / "_delme" / "f60_unguarded_hb"
    outside.mkdir(parents=True, exist_ok=True)
    scar = outside / "not_temp_heartbeat.json"
    if scar.exists():
        scar.unlink()

    # CONTROL: the unguarded helper WILL write outside temp. That is the scar.
    cosmos_clock.write_heartbeat(scar, "f60-scar")
    check("CONTROL: unguarded write_heartbeat lands outside the OS temp dir",
          lambda: scar.is_file())
    scar_existed = scar.is_file()
    if scar.exists():
        scar.unlink()

    refused = {"kind": None}

    def _guarded_outside():
        with sandbox_heartbeats():
            cosmos_clock.write_heartbeat(scar, "f60-guarded")
        return False

    try:
        _guarded_outside()
    except ProductionWriteRefused as e:
        refused["kind"] = e.kind
    check("guarded write_heartbeat to a non-temp path is PROD_WRITE_REFUSED",
          lambda: refused["kind"] == "PROD_WRITE_REFUSED")
    check("the refused write did not create the file",
          lambda: scar.is_file() is False)

    # Scratch root (OS temp) still writes.
    import tempfile
    td = Path(tempfile.mkdtemp(prefix="cosmos_f60_ok_"))
    ok_path = td / "hb.json"
    with sandbox_heartbeats():
        cosmos_clock.write_heartbeat(ok_path, "f60-ok")
    check("guarded write_heartbeat under OS temp dir still lands",
          lambda: ok_path.is_file())

    src_dhx = (HERE / "test_collector_dhx.py").read_text(encoding="utf-8")
    src_nbw = (HERE / "test_node_bucket_worker.py").read_text(encoding="utf-8")
    check("test_collector_dhx.py wraps main in sandbox_heartbeats",
          lambda: "sandbox_heartbeats" in src_dhx
          and "cosmos_test_guard" in src_dhx)
    check("test_node_bucket_worker.py wraps main in sandbox_heartbeats",
          lambda: "sandbox_heartbeats" in src_nbw
          and "cosmos_test_guard" in src_nbw)
    src_bak = (HERE / "test_backup_clock.py").read_text(encoding="utf-8")
    check("test_backup_clock.py wraps main in sandbox_heartbeats",
          lambda: "sandbox_heartbeats" in src_bak
          and "cosmos_test_guard" in src_bak)

    src_guard = GUARD.read_text(encoding="utf-8")
    check("sandbox_heartbeats wraps cosmos_clock.run_schtasks (F-60 CLOCKS writers)",
          lambda: "run_schtasks" in src_guard
          and "guarded_run_schtasks" in src_guard)

    sch_refused = {"kind": None, "called_real": False}
    real_sch = cosmos_clock.run_schtasks

    def _bomb(*a, **kw):
        sch_refused["called_real"] = True
        raise AssertionError("real schtasks writer must not run in this pin")

    # Bomb first so an unwrapped call cannot register a production task.
    cosmos_clock.run_schtasks = _bomb
    try:
        with sandbox_heartbeats():
            cosmos_clock.run_schtasks(
                ["schtasks", "/create", "/tn", "COSMOS Collector"])
    except ProductionWriteRefused as e:
        sch_refused["kind"] = e.kind
    except AssertionError:
        pass
    finally:
        cosmos_clock.run_schtasks = real_sch
    check("guarded schtasks /create of a COSMOS task is PROD_WRITE_REFUSED",
          lambda: sch_refused["kind"] == "PROD_WRITE_REFUSED")
    check("guarded schtasks /create did not invoke the real writer",
          lambda: sch_refused["called_real"] is False)

    src_fence = (HERE / "test_live_write_fence.py").read_text(encoding="utf-8")
    check("test_live_write_fence.py fences test_backup_clock.py",
          lambda: "tests/test_backup_clock.py" in src_fence)
    check("test_live_write_fence.py sets COSMOS_SCHTASKS_SANDBOX on the child",
          lambda: 'COSMOS_SCHTASKS_SANDBOX' in src_fence)
    check("test_live_write_fence.py pins health suite unfenced_spawns empty (F-60)",
          lambda: "no native unfenced spawns (F-60)" in src_fence)

    env_set = {"on": False, "after": None}
    prev_sb = os.environ.get("COSMOS_SCHTASKS_SANDBOX")
    if "COSMOS_SCHTASKS_SANDBOX" in os.environ:
        del os.environ["COSMOS_SCHTASKS_SANDBOX"]
    try:
        with sandbox_heartbeats():
            env_set["on"] = os.environ.get("COSMOS_SCHTASKS_SANDBOX") == "1"
        env_set["after"] = os.environ.get("COSMOS_SCHTASKS_SANDBOX")
    finally:
        if prev_sb is None:
            os.environ.pop("COSMOS_SCHTASKS_SANDBOX", None)
        else:
            os.environ["COSMOS_SCHTASKS_SANDBOX"] = prev_sb
    check("sandbox_heartbeats sets COSMOS_SCHTASKS_SANDBOX=1 (child inherit)",
          lambda: env_set["on"] is True)
    check("sandbox_heartbeats restores COSMOS_SCHTASKS_SANDBOX on exit",
          lambda: env_set["after"] is None)

    # Env-inherited /query must not invoke subprocess (health --once leftover).
    query_calls = []
    real_run = cosmos_clock.subprocess.run

    def _spy_run(*a, **kw):
        query_calls.append(a[0] if a else None)
        raise AssertionError("sandbox /query must not spawn schtasks.exe")

    cosmos_clock.subprocess.run = _spy_run
    os.environ["COSMOS_SCHTASKS_SANDBOX"] = "1"
    qrec = None
    try:
        qrec = cosmos_clock.run_schtasks(
            ["schtasks", "/query", "/tn", "COSMOS Health Watchdog"])
    finally:
        cosmos_clock.subprocess.run = real_run
        os.environ.pop("COSMOS_SCHTASKS_SANDBOX", None)
        if prev_sb is not None:
            os.environ["COSMOS_SCHTASKS_SANDBOX"] = prev_sb
    check("sandbox /query does not invoke subprocess (F-60 health leftover)",
          lambda: query_calls == [])
    check("sandbox /query is typed SCHTASKS_SANDBOX and sandbox=true",
          lambda: qrec is not None
          and qrec.get("kind") == "SCHTASKS_SANDBOX"
          and qrec.get("sandbox") is True
          and qrec.get("ok") is False)

    src_clock = (REPO / "cosmos" / "cosmos_clock.py").read_text(encoding="utf-8")
    check("cosmos_clock names COSMOS_SCHTASKS_SANDBOX (F-60 inherit)",
          lambda: "COSMOS_SCHTASKS_SANDBOX" in src_clock
          and "schtasks_sandbox_on" in src_clock)

    bad = [x for x in RESULTS if not x[1]]
    for label, ok, err in RESULTS:
        print(f"  {'OK  ' if ok else 'FAIL'}  {label}{('  ' + err) if err else ''}")
    print("live_value: " + json.dumps({
        "checks": len(RESULTS),
        "passed": len(RESULTS) - len(bad),
        "scar_unguarded_wrote": scar_existed,
        "refused_kind": refused["kind"],
        "scratch_ok": ok_path.is_file(),
    }, sort_keys=True))
    print(f"result: {'ok' if not bad else 'FAIL'}  "
          f"{len(RESULTS) - len(bad)}/{len(RESULTS)}")
    return 1 if bad else 0


def test_cosmos_test_guard():
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
