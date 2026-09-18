#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_own_clocks - register the dozen COSMOS-own Windows clocks.

One standup for the matrix in docs/ORCHESTRATION.md. Does not modify
kernel/ledger/sched/service. No bts_* import. Task names are 'COSMOS <x>'.

    py -3.14 cosmos\\cosmos_own_clocks.py --root V:\\A\\Ai\\COSMOS\\live --standup
    py -3.14 cosmos\\cosmos_own_clocks.py --root ... --status
    py -3.14 cosmos\\cosmos_own_clocks.py --root ... --matrix
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_clock import (  # noqa: E402
    create_task, heartbeat_age_s, plan_create, query_task, read_heartbeat,
    tr_cmdline,
)
from cosmos_paths import CosmosPaths, CosmosPathError  # noqa: E402

ROOT_DEFAULT = r"V:\A\Ai\COSMOS\live"

# clock | cadence | script | task name | vehicle | heartbeat
CLOCKS = (
    {
        "id": 1, "clock": "COSMOS Activity Clock (Watchdog2)",
        "cadence": "15s", "script": "cosmos_watchdog2.py",
        "task": "COSMOS Watchdog2", "logon": "COSMOS Watchdog2 Logon",
        "vehicle": "detached daemon + 1-min self-heal + onlogon",
        "heartbeat": "watchdog2_heartbeat.json",
        "standup": "watchdog2",
    },
    {
        "id": 2, "clock": "COSMOS Collector",
        "cadence": "30s", "script": "cosmos_collector.py",
        "task": "COSMOS Collector", "logon": "COSMOS Collector Logon",
        "vehicle": "detached daemon + 1-min self-heal + onlogon",
        "heartbeat": "collector_heartbeat.json",
        "standup": "collector",
    },
    {
        "id": 3, "clock": "COSMOS Runner",
        "cadence": "15s loop / 1-min self-heal", "script": "cosmos_run.py",
        "task": "COSMOS Runner", "logon": "COSMOS Runner Logon",
        "vehicle": "detached daemon + 1-min self-heal + onlogon",
        "heartbeat": "cosmos_runner_heartbeat.json",
        "standup": "runner",
    },
    {
        "id": 4, "clock": "COSMOS Motif Driver",
        "cadence": "15m", "script": "cosmos_motif_driver.py",
        "task": "COSMOS Motif Driver", "logon": None,
        "vehicle": "schtasks /sc minute /mo 15 --once",
        "heartbeat": "motif_driver_heartbeat.json",
        "standup": "motif",
    },
    {
        "id": 5, "clock": "COSMOS Discovery",
        "cadence": "hourly", "script": "cosmos_discover.py",
        "task": "COSMOS Mesh Discovery", "logon": None,
        "vehicle": "schtasks /sc HOURLY --once",
        "heartbeat": "mesh_discovery_heartbeat.json",
        "standup": "discover",
    },
    {
        "id": 6, "clock": "COSMOS Health",
        "cadence": "~2s", "script": "cosmos_health_clock.py",
        "task": "COSMOS Health", "logon": "COSMOS Health Logon",
        "vehicle": "detached daemon + 1-min self-heal + onlogon",
        "heartbeat": "health_clock_heartbeat.json",
        "standup": "health",
    },
    {
        "id": 7, "clock": "COSMOS Rails Prober",
        "cadence": "1m", "script": "cosmos_rails_prober.py",
        "task": "COSMOS Rails Prober", "logon": None,
        "vehicle": "schtasks /sc minute /mo 1 --once",
        "heartbeat": "rails_prober_heartbeat.json",
        "standup": "rails",
    },
    {
        "id": 8, "clock": "COSMOS Spend Meter",
        "cadence": "1m", "script": "cosmos_spend_meter.py",
        "task": "COSMOS Spend Meter", "logon": None,
        "vehicle": "schtasks /sc minute /mo 1 --once",
        "heartbeat": "spend_meter_heartbeat.json",
        "standup": "spend",
    },
    {
        "id": 9, "clock": "COSMOS Drive Meter",
        "cadence": "1m", "script": "cosmos_drive_meter.py",
        "task": "COSMOS Drive Meter", "logon": None,
        "vehicle": "schtasks /sc minute /mo 1 --once",
        "heartbeat": "drive_meter_heartbeat.json",
        "standup": "drive",
    },
    {
        "id": 10, "clock": "COSMOS cDeck Feed",
        "cadence": "0.75s", "script": "cosmos_cdeck_feed.py",
        "task": "COSMOS cDeck Feed", "logon": "COSMOS cDeck Feed Logon",
        "vehicle": "detached daemon + 1-min self-heal + onlogon",
        "heartbeat": "cdeck_feed_heartbeat.json",
        "standup": "cdeck",
    },
    {
        "id": 11, "clock": "COSMOS Backup",
        "cadence": "07/11/19/23 daily", "script": "cosmos_backup_clock.py",
        "task": "COSMOS Backup 07", "logon": None,
        "extra_tasks": ["COSMOS Backup 11", "COSMOS Backup 19",
                        "COSMOS Backup 23"],
        "vehicle": "schtasks DAILY at 07/11/19/23 --once --force",
        "heartbeat": "backup_clock_heartbeat.json",
        "standup": "backup",
    },
    {
        "id": 12, "clock": "COSMOS Ledger Verify",
        "cadence": "5m", "script": "cosmos_ledger_verify.py",
        "task": "COSMOS Ledger Verify", "logon": None,
        "vehicle": "schtasks /sc minute /mo 5 --once",
        "heartbeat": "ledger_verify_heartbeat.json",
        "standup": "ledger",
    },
    {
        "id": 13, "clock": "COSMOS Index",
        "cadence": "1m", "script": "cosmos_index.py",
        "task": "COSMOS Index", "logon": None,
        "vehicle": "schtasks /sc minute /mo 1 --once",
        "heartbeat": "cosmos_index_heartbeat.json",
        "standup": "index",
    },
    {
        "id": 14, "clock": "COSMOS Dispatcher",
        "cadence": "5s daemon + 1-min self-heal",
        "script": "cosmos_dispatcher_daemon.py",
        "task": "COSMOS Dispatcher", "logon": "COSMOS Dispatcher Logon",
        "vehicle": "detached daemon + 1-min self-heal + onlogon",
        "heartbeat": "dispatcher_heartbeat.json",
        "standup": "dispatcher",
    },
    {
        "id": 15, "clock": "COSMOS Runner Pool",
        "cadence": "15s loop / 1-min self-heal",
        "script": "cosmos_pool.py",
        "task": "COSMOS Runner Pool", "logon": "COSMOS Runner Pool Logon",
        "vehicle": "detached daemon + 1-min self-heal + onlogon",
        "heartbeat": "cosmos_pool_heartbeat.json",
        "standup": "pool",
    },
    {
        "id": 16, "clock": "COSMOS CVM Clock",
        "cadence": "2s daemon (audio/ux) + 15s pull ticket",
        "script": "cosmos_cvm_clock.py",
        "task": "COSMOS CVM Clock", "logon": "COSMOS CVM Clock Logon",
        "vehicle": "detached daemon + 1-min self-heal + onlogon",
        "heartbeat": "cvm_clock_heartbeat.json",
        "standup": "cvm",
    },
    {
        "id": 17, "clock": "COSMOS Work-Order Runner",
        "cadence": "15s loop / 1-min self-heal",
        "script": "cosmos_work_order_run.py",
        "task": "COSMOS Work-Order Runner",
        "logon": "COSMOS Work-Order Runner Logon",
        "vehicle": "detached daemon + 1-min self-heal + onlogon",
        "heartbeat": "work_order_runner_heartbeat.json",
        "standup": "work_order",
    },
    {
        "id": 18, "clock": "COSMOS Resession",
        "cadence": "1m", "script": "cosmos_resession.py",
        "task": "COSMOS Resession", "logon": None,
        "vehicle": "schtasks /sc minute /mo 1 --once",
        "heartbeat": "resession_heartbeat.json",
        "standup": "resession",
    },
    {
        "id": 19, "clock": "COSMOS Askmine",
        "cadence": "hourly", "script": "cosmos_askmine.py",
        "task": "COSMOS Askmine", "logon": None,
        "vehicle": "schtasks /sc HOURLY --once",
        "heartbeat": "askmine_heartbeat.json",
        "standup": "askmine",
    },
    {
        "id": 20, "clock": "COSMOS CritConsumer",
        "cadence": "10s loop / 1-min self-heal",
        "script": "cosmos_crit_consumer.py",
        "task": "COSMOS CritConsumer",
        "logon": "COSMOS CritConsumer Logon",
        "vehicle": "detached daemon + 1-min self-heal + onlogon",
        "heartbeat": "crit_consumer_heartbeat.json",
        "standup": "crit_consumer",
    },
    {
        "id": 21, "clock": "COSMOS Grok Bucket Worker",
        "cadence": "5-15s loop / 1-min self-heal",
        "script": "cosmos_grok_bucket_worker.py",
        "task": "COSMOS Grok Bucket Worker",
        "logon": "COSMOS Grok Bucket Worker Logon",
        "vehicle": "detached daemon + 1-min self-heal + onlogon",
        "heartbeat": "cosmos_grok_bucket_worker_heartbeat.json",
        "standup": "grok_bucket",
    },
    {
        "id": 22, "clock": "COSMOS GEM Bucket Worker",
        "cadence": "5-15s loop / 1-min self-heal",
        "script": "cosmos_gem_bucket_worker.py",
        "task": "COSMOS GEM Bucket Worker",
        "logon": "COSMOS GEM Bucket Worker Logon",
        "vehicle": "detached daemon + 1-min self-heal + onlogon",
        "heartbeat": "cosmos_gem_bucket_worker_heartbeat.json",
        "standup": "gem_bucket",
    },
    {
        "id": 23, "clock": "COSMOS NEW-AI Scout",
        "cadence": "hourly", "script": "cosmos_newai_scout.py",
        "task": "COSMOS NEW-AI Scout", "logon": None,
        "vehicle": "schtasks /sc HOURLY --once",
        "heartbeat": "newai_scout_heartbeat.json",
        "standup": "newai_scout",
    },
    {
        "id": 24, "clock": "COSMOS Prepaid Orchestrator",
        "cadence": "1m", "script": "cosmos_prepaid_orch.py",
        "task": "COSMOS Prepaid Orchestrator", "logon": None,
        "vehicle": "schtasks /sc minute /mo 1 --once",
        "heartbeat": "prepaid_orch_heartbeat.json",
        "standup": "prepaid_orch",
    },
    {
        "id": 25, "clock": "COSMOS CVM DT Clock",
        "cadence": "2s drain idle / 1-min self-heal + onlogon",
        "script": "builds/cvm-dt/cvm_dt_clock.py",
        "task": "COSMOS CVM DT Clock",
        "logon": "COSMOS CVM DT Clock Logon",
        "vehicle": "detached daemon + 1-min self-heal + onlogon",
        "heartbeat": "cvm_dt_clock_heartbeat.json",
        "standup": "cvm_dt",
    },
    {
        "id": 26, "clock": "COSMOS SGH Drop Ingest",
        "cadence": "15s loop / 1-min self-heal",
        "script": "cosmos_sgh_drop_ingest.py",
        "task": "COSMOS SGH Drop Ingest",
        "logon": "COSMOS SGH Drop Ingest Logon",
        "vehicle": "detached daemon + 1-min self-heal + onlogon",
        "heartbeat": "sgh_drop_ingest_heartbeat.json",
        "standup": "sgh_drop_ingest",
    },
    {
        "id": 28, "clock": "COSMOS Learn Style",
        "cadence": "15m", "script": "cosmos_learn_clock.py",
        "task": "COSMOS Learn Style", "logon": None,
        "vehicle": "schtasks /sc minute /mo 15 --once",
        "heartbeat": "learn_clock_heartbeat.json",
        "standup": "learn",
    },
)


def _task_ok(name: str | None) -> dict:
    if not name:
        return {"name": None, "registered": False}
    q = query_task(name)
    return {
        "name": name,
        "registered": bool(q.get("ok")),
        "rc": q.get("rc"),
        "out": (q.get("out") or "")[:1600],
    }


def matrix(root: str) -> list[dict]:
    paths = CosmosPaths(root)
    logs = paths.logs()
    rows = []
    for spec in CLOCKS:
        hb = read_heartbeat(logs / spec["heartbeat"])
        age = heartbeat_age_s(hb)
        task = _task_ok(spec["task"])
        logon = _task_ok(spec.get("logon"))
        extras = [_task_ok(n) for n in spec.get("extra_tasks") or []]
        registered = task["registered"] and all(e["registered"] for e in extras)
        rows.append({
            "id": spec["id"],
            "clock": spec["clock"],
            "cadence": spec["cadence"],
            "script": spec["script"],
            "task_name": spec["task"],
            "logon_task": spec.get("logon"),
            "extra_tasks": spec.get("extra_tasks") or [],
            "vehicle": spec["vehicle"],
            "heartbeat": spec["heartbeat"],
            "registered": registered,
            "logon_registered": (True if not spec.get("logon")
                                 else logon["registered"]),
            "heartbeat_age_s": age,
            "heartbeat_state": (hb or {}).get("state"),
            "heartbeat_pid": (hb or {}).get("pid"),
            "last_run_epoch": (hb or {}).get("last_run_epoch"),
            "task_query": task,
            "logon_query": logon if spec.get("logon") else None,
            "extra_query": extras or None,
        })
    return rows


def _call_standup(name: str, root: str) -> dict:
    """Import each satellite standup. Isolated so one failure doesn't abort."""
    try:
        if name == "watchdog2":
            from cosmos_watchdog2 import standup, DEFAULT_INTERVAL_S as _wd
            return standup(root, _wd)
        if name == "collector":
            from cosmos_collector import standup, DEFAULT_INTERVAL_S as _col
            return standup(root, _col)
        if name == "runner":
            from cosmos_run import standup, DEFAULT_INTERVAL_S as _run
            return standup(root, _run)
        if name == "motif":
            from cosmos_motif_driver import standup
            return standup()
        if name == "discover":
            from cosmos_discover import standup
            return standup(root)
        if name == "health":
            from cosmos_health_clock import standup
            return standup(root)
        if name == "rails":
            from cosmos_rails_prober import standup
            return standup(root)
        if name == "spend":
            from cosmos_spend_meter import standup
            return standup(root)
        if name == "drive":
            from cosmos_drive_meter import standup
            return standup(root)
        if name == "cdeck":
            from cosmos_cdeck_feed import standup
            return standup(root)
        if name == "backup":
            from cosmos_backup_clock import standup
            return standup(root)
        if name == "ledger":
            from cosmos_ledger_verify import standup
            return standup(root)
        if name == "index":
            from cosmos_index import standup
            return standup(root)
        if name == "dispatcher":
            from cosmos_dispatcher_daemon import standup, DEFAULT_INTERVAL_S as _disp
            return standup(root, _disp)
        if name == "pool":
            from cosmos_pool import standup, DEFAULT_INTERVAL_S as _pool
            return standup(root, _pool)
        if name == "cvm":
            from cosmos_cvm_clock import standup
            return standup(root)
        if name == "work_order":
            from cosmos_work_order_run import standup, DEFAULT_INTERVAL_S as _wo
            return standup(root, _wo)
        if name == "resession":
            from cosmos_resession import standup
            return standup(root)
        if name == "askmine":
            from cosmos_askmine import standup
            return standup(root)
        if name == "crit_consumer":
            from cosmos_crit_consumer import standup
            return standup(root)
        if name == "grok_bucket":
            from cosmos_bucket_daemon import standup
            return standup(root, "grok")
        if name == "gem_bucket":
            from cosmos_bucket_daemon import standup
            return standup(root, "gem")
        if name == "newai_scout":
            from cosmos_newai_scout import standup
            return standup(root)
        if name == "prepaid_orch":
            from cosmos_prepaid_orch import standup
            return standup(root)
        if name == "sgh_drop_ingest":
            from cosmos_sgh_drop_ingest import standup, DEFAULT_INTERVAL_S as _sgh
            return standup(root, _sgh)
        if name == "learn":
            from cosmos_learn_clock import standup
            return standup(root)
        if name == "cvm_dt":
            # Emit-only. cvm_dt_clock.register never runs schtasks
            # (Keith elevated host action). Do not import the worker:
            # cvm_dt_clock pulls the desktop client stack.
            repo = Path(__file__).resolve().parent.parent
            script = repo / "builds" / "cvm-dt" / "cvm_dt_clock.py"
            tr = tr_cmdline(script, root, "--loop")
            minute = plan_create("COSMOS CVM DT Clock", tr, "minute", mo=1)
            logon = plan_create("COSMOS CVM DT Clock Logon", tr, "onlogon")
            cmds = [subprocess.list2cmdline(a) for a in (minute, logon)]
            return {
                "ok": True,
                "started": "emitted",
                "ran": False,
                "keith_cmds": cmds,
                "keith_cmd": " & ".join(cmds),
            }
        return {"ok": False, "error": f"unknown standup {name}"}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


def standup_all(root: str) -> dict:
    results = []
    keith = []
    for spec in CLOCKS:
        rec = _call_standup(spec["standup"], root)
        rec_out = {
            "id": spec["id"],
            "clock": spec["clock"],
            "task": spec["task"],
            "started": rec.get("started"),
            "ok": rec.get("ok", rec.get("started") not in (None, "failed")),
            "keith_cmd": rec.get("keith_cmd"),
            "proof_ok": (rec.get("proof") or {}).get("ok"),
            "error": rec.get("error"),
        }
        results.append(rec_out)
        cmds = rec.get("keith_cmds") or (
            [rec["keith_cmd"]] if rec.get("keith_cmd") else [])
        for c in cmds:
            if c and c not in keith:
                keith.append(c)
        # Also harvest logon from nested recs
        for key in ("task_logon", "task"):
            nested = rec.get(key) or {}
            if nested.get("keith_cmd") and nested["keith_cmd"] not in keith:
                if nested.get("needs_elevation") or not nested.get("ok"):
                    keith.append(nested["keith_cmd"])
    # Separate * Logon names so a 1-min self-heal is not overwritten.
    here = Path(__file__).resolve().parent
    logon_specs = (
        ("COSMOS Watchdog2 Logon", "cosmos_watchdog2.py", ("--loop",)),
        ("COSMOS Collector Logon", "cosmos_collector.py", ("--loop",)),
        ("COSMOS Runner Logon", "cosmos_run.py", ("--loop",)),
        ("COSMOS Health Logon", "cosmos_health_clock.py", ("--loop",)),
        ("COSMOS cDeck Feed Logon", "cosmos_cdeck_feed.py", ("--loop",)),
        ("COSMOS Dispatcher Logon", "cosmos_dispatcher_daemon.py", ("--loop",)),
        ("COSMOS Runner Pool Logon", "cosmos_pool.py", ("--supervise",)),
        ("COSMOS CVM Clock Logon", "cosmos_cvm_clock.py", ("--loop",)),
        ("COSMOS Work-Order Runner Logon", "cosmos_work_order_run.py", ("--loop",)),
        ("COSMOS CritConsumer Logon", "cosmos_crit_consumer.py", ("--loop",)),
        ("COSMOS Grok Bucket Worker Logon", "cosmos_grok_bucket_worker.py",
         ("--loop",)),
        ("COSMOS GEM Bucket Worker Logon", "cosmos_gem_bucket_worker.py",
         ("--loop",)),
        ("COSMOS SGH Drop Ingest Logon", "cosmos_sgh_drop_ingest.py",
         ("--loop",)),
    )
    for name, script, extra in logon_specs:
        if query_task(name).get("ok"):
            continue
        tr = tr_cmdline(here / script, root, *extra)
        rec = create_task(name, tr, "onlogon")
        results.append({
            "id": None, "clock": name, "task": name,
            "started": "schtasks" if rec.get("ok") else "failed",
            "ok": bool(rec.get("ok")),
            "keith_cmd": rec.get("keith_cmd"),
            "proof_ok": rec.get("ok"),
            "error": None if rec.get("ok") else rec.get("out"),
        })
        if rec.get("keith_cmd") and rec["keith_cmd"] not in keith:
            if rec.get("needs_elevation") or not rec.get("ok"):
                keith.append(rec["keith_cmd"])
    rows = matrix(root)
    return {
        "ok": all(r.get("registered") for r in rows),
        "root": root,
        "standups": results,
        "matrix": [{k: r[k] for k in (
            "id", "clock", "cadence", "script", "task_name",
            "registered", "logon_registered", "heartbeat",
            "heartbeat_age_s", "heartbeat_state")} for r in rows],
        "keith_cmds": keith,
        "keith_one_liner": " & ".join(keith) if keith else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_own_clocks")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--standup", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--matrix", action="store_true")
    a = ap.parse_args()
    if a.standup:
        r = standup_all(a.root)
        print(json.dumps(r, indent=1, default=str))
        return 0 if r.get("ok") else 2
    rows = matrix(a.root)
    print(json.dumps({"root": a.root, "matrix": [
        {k: r[k] for k in (
            "id", "clock", "cadence", "script", "task_name", "logon_task",
            "extra_tasks", "vehicle", "heartbeat", "registered",
            "logon_registered", "heartbeat_age_s", "heartbeat_state",
            "last_run_epoch")}
        for r in rows
    ]}, indent=1, default=str))
    if a.status:
        return 0 if all(r["registered"] for r in rows) else 2
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CosmosPathError as e:
        print(e, file=sys.stderr)
        raise SystemExit(2)
