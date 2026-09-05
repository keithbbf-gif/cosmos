#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B8 — a worker that ships unsupervised must be DETECTED, not merely unlikely.

`cvm_supervision` derives the required supervision rows from the workers' own
`TASK_NAME` / `HEARTBEAT_NAME` declarations and measures them against the two
hand-maintained registries plus the real `schtasks` and the real heartbeat
files. These tests prove the detector actually fires, on a synthetic repo
built for the purpose — a detector validated only against the real tree could
be passing because the tree happens to be clean.

rc=0 is NOT the gate. `SUPERVISION_TEST.json`'s `live_value.real_tree` quotes
the audit of the ACTUAL repo: measured heartbeat ages in seconds for the two
workers CLOCK_POSTMORTEM named, read off `live/logs/`.

    py -3.14 builds\\cvm-dt\\test_cvm_supervision.py --root <RUNTIME>
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "cosmos"))

import cvm_supervision as sup  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []
LIVE: dict = {}


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, "%s: %s" % (type(e).__name__, e)))


def _fake_repo() -> Path:
    """A repo with one wired worker, one silently unwired, one staged copy."""
    td = Path(tempfile.mkdtemp(prefix="cvm-sup-"))
    (td / "cosmos").mkdir()
    (td / "builds" / "thing").mkdir(parents=True)
    (td / "builds" / "thing" / "_delme" / "old").mkdir(parents=True)
    (td / "cosmos" / "wired_worker.py").write_text(
        'TASK_NAME = "COSMOS Wired"\n'
        'TASK_NAME_LOGON = "COSMOS Wired Logon"\n'
        'HEARTBEAT_NAME = "wired_heartbeat.json"\n', encoding="utf-8")
    (td / "builds" / "thing" / "lonely_worker.py").write_text(
        '"""Ships a --register that only emits. Nobody watches it."""\n'
        'TASK_NAME = "COSMOS Lonely"\n'
        'HEARTBEAT_NAME = "lonely_heartbeat.json"\n', encoding="utf-8")
    # Staged copy of the same worker: must NOT be audited twice.
    (td / "builds" / "thing" / "_delme" / "old" / "lonely_worker.py").write_text(
        'TASK_NAME = "COSMOS Lonely"\n'
        'HEARTBEAT_NAME = "lonely_heartbeat.json"\n', encoding="utf-8")
    # A local (non module-level) assignment must not be mistaken for one.
    (td / "cosmos" / "not_a_worker.py").write_text(
        "def f():\n    TASK_NAME = 'COSMOS Nope'\n    return TASK_NAME\n",
        encoding="utf-8")
    return td


def test_scan_finds_only_real_declarations():
    td = _fake_repo()
    found = sup.scan(td)
    names = sorted(w["module"] for w in found)
    LIVE["fake_scan"] = {"repo": str(td), "modules": names,
                         "paths": sorted(w["path"] for w in found)}
    check("scan_finds_both_workers",
          lambda: names == ["lonely_worker", "wired_worker"])
    check("scan_skips_delme_staged_copy",
          lambda: not any("_delme" in w["path"] for w in found))
    check("scan_ignores_function_local_assignment",
          lambda: "not_a_worker" not in names)
    check("scan_reads_the_logon_name",
          lambda: [w for w in found if w["module"] == "wired_worker"
                   ][0]["task_logon"] == "COSMOS Wired Logon")


def test_unwired_worker_is_detected(monkey: dict):
    """The postmortem's exact shape: shipped, declared, in neither registry."""
    td = _fake_repo()
    real = sup.registries
    sup.registries = lambda: {
        "clocks": [{"id": 1, "task": "COSMOS Wired",
                    "logon": "COSMOS Wired Logon",
                    "heartbeat": "wired_heartbeat.json",
                    "script": "wired_worker.py"}],
        "watchlist": ["wired_heartbeat.json"], "errors": [], "max_clock_id": 1}
    try:
        rec = sup.audit(None, use_schtasks=False, repo=td)
    finally:
        sup.registries = real
    by = {r["module"]: r for r in rec["workers"]}
    LIVE["fake_audit"] = {"ok": rec["ok"], "declared": rec["declared"],
                          "unsupervised": rec["unsupervised"]}
    monkey["rec"] = rec
    check("wired_worker_is_supervised",
          lambda: by["wired_worker"]["supervised"] is True
          and by["wired_worker"]["missing"] == [])
    check("lonely_worker_is_flagged",
          lambda: by["lonely_worker"]["supervised"] is False)
    check("flag_names_both_missing_registries",
          lambda: by["lonely_worker"]["missing"] == [
              "cosmos_own_clocks.CLOCKS",
              "cosmos_health_clock.PEER_HEARTBEATS"])
    check("audit_not_ok_when_one_is_unwired", lambda: rec["ok"] is False)
    check("no_runtime_root_is_a_named_state",
          lambda: by["lonely_worker"]["heartbeat_state"] == "no_runtime_root"
          and by["lonely_worker"]["heartbeat_age_s"] is None)


def test_clean_repo_is_ok():
    """The detector must be capable of saying yes, or it says nothing."""
    td = _fake_repo()
    real = sup.registries
    sup.registries = lambda: {
        "clocks": [{"id": 1, "task": "COSMOS Wired",
                    "logon": "COSMOS Wired Logon",
                    "heartbeat": "wired_heartbeat.json", "script": "w.py"},
                   {"id": 2, "task": "COSMOS Lonely", "logon": None,
                    "heartbeat": "lonely_heartbeat.json", "script": "l.py"}],
        "watchlist": ["wired_heartbeat.json", "lonely_heartbeat.json"],
        "errors": [], "max_clock_id": 2}
    try:
        rec = sup.audit(None, use_schtasks=False, repo=td)
    finally:
        sup.registries = real
    check("fully_wired_repo_is_ok",
          lambda: rec["ok"] is True and rec["unsupervised"] == []
          and rec["declared"] == 2 and rec["supervised"] == 2)


def test_heartbeat_states_are_typed():
    td = Path(tempfile.mkdtemp(prefix="cvm-sup-hb-"))
    now = time.time()
    (td / "fresh.json").write_text(json.dumps({"last_run_epoch": now - 5}),
                                   encoding="utf-8")
    (td / "cold.json").write_text(
        json.dumps({"last_run_epoch": now - (sup.COLD_S + 60)}),
        encoding="utf-8")
    (td / "empty.json").write_text(json.dumps({"note": "no epoch"}),
                                   encoding="utf-8")
    (td / "junk.json").write_text("{not json", encoding="utf-8")
    got = {n: sup._heartbeat(td, n + ".json", now)
           for n in ("fresh", "cold", "empty", "junk", "missing")}
    got["undeclared"] = sup._heartbeat(td, "", now)
    LIVE["heartbeat_states"] = {k: v["state"] for k, v in got.items()}
    check("fresh_is_fresh", lambda: got["fresh"]["state"] == "fresh"
          and 4 <= got["fresh"]["age_s"] <= 8)
    check("cold_is_cold", lambda: got["cold"]["state"] == "cold"
          and got["cold"]["age_s"] > sup.COLD_S)
    check("no_epoch_is_named", lambda: got["empty"]["state"] == "no_last_run_epoch")
    check("junk_is_unreadable", lambda: got["junk"]["state"] == "unreadable"
          and bool(got["junk"].get("detail")))
    check("missing_file_is_absent", lambda: got["missing"]["state"] == "absent")
    check("undeclared_is_not_absent",
          lambda: got["undeclared"]["state"] == "not_declared")


def test_real_tree_measurement(root):
    """The actual repo. Numbers, not adjectives."""
    rec = sup.audit(root, use_schtasks=False)
    by = {r["module"]: r for r in rec["workers"]}
    LIVE["real_tree"] = {
        "declared": rec["declared"], "supervised": rec["supervised"],
        "unsupervised_count": rec["unsupervised_count"],
        "cold_count": rec["cold_count"],
        "clocks_rows": rec["registries"]["clocks_rows"],
        "max_clock_id": rec["registries"]["max_clock_id"],
        "watchlist_len": rec["registries"]["watchlist_len"],
        "runtime": rec["runtime"],
        "postmortem_workers": {
            m: {"missing": by[m]["missing"],
                "heartbeat_age_s": by[m]["heartbeat_age_s"],
                "heartbeat_state": by[m]["heartbeat_state"]}
            for m in ("cvm_dt_clock", "cvm_dt_voice") if m in by},
        "unsupervised": [r["module"] for r in rec["unsupervised"]],
    }
    check("real_tree_declares_workers", lambda: rec["declared"] >= 20)
    check("registries_read_without_error",
          lambda: rec["registries"]["errors"] == [])
    check("postmortem_workers_still_unwired",
          lambda: all(
              "cosmos_own_clocks.CLOCKS" in by[m]["missing"]
              and "cosmos_health_clock.PEER_HEARTBEATS" in by[m]["missing"]
              for m in ("cvm_dt_clock", "cvm_dt_voice")))
    check("postmortem_workers_measured_cold",
          lambda: all(by[m]["heartbeat_state"] == "cold"
                      for m in ("cvm_dt_clock", "cvm_dt_voice")))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(
        Path(__file__).resolve().parents[2] / "live"))
    a = ap.parse_args(argv)

    monkey: dict = {}
    test_scan_finds_only_real_declarations()
    test_unwired_worker_is_detected(monkey)
    test_clean_repo_is_ok()
    test_heartbeat_states_are_typed()
    test_real_tree_measurement(a.root)

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for label, ok, err in RESULTS:
        print("%s %s%s" % ("PASS" if ok else "FAIL", label,
                           (" - " + err) if err else ""))
    ok_all = passed == len(RESULTS)
    pm = LIVE.get("real_tree", {}).get("postmortem_workers", {})
    rec = {
        "ok": ok_all, "wire": "cvm-dt-b8-supervision/1",
        "suite": "test_cvm_supervision.py",
        "passed": passed, "total": len(RESULTS),
        "gated_at_epoch": time.time(), "python": sys.version.split()[0],
        "live_value": LIVE,
        "emitted": "b8-sup:%s/%s supervised; cvm_dt_clock cold %ss; "
                   "cvm_dt_voice cold %ss" % (
                       LIVE.get("real_tree", {}).get("supervised"),
                       LIVE.get("real_tree", {}).get("declared"),
                       pm.get("cvm_dt_clock", {}).get("heartbeat_age_s"),
                       pm.get("cvm_dt_voice", {}).get("heartbeat_age_s")),
        "results": [{"name": n, "verdict": "PASS" if o else "FAIL",
                     "detail": e} for n, o, e in RESULTS],
    }
    out = Path(__file__).resolve().parent / "SUPERVISION_TEST.json"
    out.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    print(json.dumps({"ok": ok_all, "passed": passed, "total": len(RESULTS),
                      "emitted": rec["emitted"], "proof_path": str(out)},
                     indent=1))
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
