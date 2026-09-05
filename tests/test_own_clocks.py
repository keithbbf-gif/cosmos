#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: COSMOS-own clocks (no BTS, no core edits).

Isolated from the live root. Does not register schtasks. Proves: new modules
have COSMOS task names, write heartbeats, default to the resolver queue role,
and import no bts_*.
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_kernel import install
from cosmos_watchdog2 import Watchdog2, TASK_NAME as WD2_TASK
from cosmos_collector import Collector, TASK_NAME as COL_TASK
from cosmos_health_clock import poll_once as health_once, TASK_NAME as HEALTH_TASK
from cosmos_drive_meter import poll_once as drive_once, TASK_NAME as DRIVE_TASK
from cosmos_cdeck_feed import poll_once as feed_once, TASK_NAME as FEED_TASK
from cosmos_ledger_verify import poll_once as verify_once, TASK_NAME as LV_TASK
from cosmos_spend_meter import poll_once as spend_once, TASK_NAME as SPEND_TASK
from cosmos_rails_prober import poll_once as rails_once, TASK_NAME as RAILS_TASK
from cosmos_backup_clock import poll_once as backup_once, TASK_NAMES as BAK_TASKS
from cosmos_own_clocks import CLOCKS
from cosmos_clock import plan_create

RESULTS = []
BTS_IMPORT = re.compile(r"^\s*(?:from|import)\s+bts_\w+", re.M)
COSMOS_DIR = Path(__file__).resolve().parent.parent / "cosmos"
NEW_MODULES = (
    "cosmos_clock.py",
    "cosmos_health_clock.py",
    "cosmos_rails_prober.py",
    "cosmos_spend_meter.py",
    "cosmos_drive_meter.py",
    "cosmos_cdeck_feed.py",
    "cosmos_backup_clock.py",
    "cosmos_ledger_verify.py",
    "cosmos_own_clocks.py",
    "cosmos_context_pull.py",
    "cosmos_dispatcher_daemon.py",
    "cosmos_resession.py",
    "cosmos_askmine.py",
    "cosmos_newai_scout.py",
    "cosmos_prepaid_orch.py",
    "cosmos_sgh_drop_ingest.py",
)


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_ownclocks_"))
    root = install(td / "live", tree_id="spike-own-clocks")

    for spec in CLOCKS:
        check(f"task name starts COSMOS: {spec['task']}",
              lambda s=spec: s["task"].startswith("COSMOS "))
    check("at least a dozen clocks in the matrix",
          lambda: len(CLOCKS) >= 12)
    check("Activity Clock is #1 Watchdog2",
          lambda: CLOCKS[0]["task"] == "COSMOS Watchdog2"
          and CLOCKS[0]["cadence"] == "15s")
    check("clock 18 is COSMOS Resession",
          lambda: any(c.get("id") == 18 and c.get("task") == "COSMOS Resession"
                      and c.get("script") == "cosmos_resession.py"
                      for c in CLOCKS))
    check("clock 19 is COSMOS Askmine",
          lambda: any(c.get("id") == 19 and c.get("task") == "COSMOS Askmine"
                      and c.get("script") == "cosmos_askmine.py"
                      and c.get("heartbeat") == "askmine_heartbeat.json"
                      for c in CLOCKS))
    check("clock 20 is COSMOS CritConsumer",
          lambda: any(c.get("id") == 20 and c.get("task") == "COSMOS CritConsumer"
                      and c.get("script") == "cosmos_crit_consumer.py"
                      and c.get("heartbeat") == "crit_consumer_heartbeat.json"
                      for c in CLOCKS))
    check("clock 21 is COSMOS Grok Bucket Worker",
          lambda: any(c.get("id") == 21
                      and c.get("task") == "COSMOS Grok Bucket Worker"
                      and c.get("script") == "cosmos_grok_bucket_worker.py"
                      for c in CLOCKS))
    check("clock 22 is COSMOS GEM Bucket Worker",
          lambda: any(c.get("id") == 22
                      and c.get("task") == "COSMOS GEM Bucket Worker"
                      and c.get("script") == "cosmos_gem_bucket_worker.py"
                      for c in CLOCKS))
    check("clock 23 is COSMOS NEW-AI Scout",
          lambda: any(c.get("id") == 23 and c.get("task") == "COSMOS NEW-AI Scout"
                      and c.get("script") == "cosmos_newai_scout.py"
                      and c.get("heartbeat") == "newai_scout_heartbeat.json"
                      for c in CLOCKS))
    check("clock 24 is COSMOS Prepaid Orchestrator",
          lambda: any(c.get("id") == 24
                      and c.get("task") == "COSMOS Prepaid Orchestrator"
                      and c.get("script") == "cosmos_prepaid_orch.py"
                      and c.get("heartbeat") == "prepaid_orch_heartbeat.json"
                      for c in CLOCKS))
    check("clock 26 is COSMOS SGH Drop Ingest",
          lambda: any(c.get("id") == 26
                      and c.get("task") == "COSMOS SGH Drop Ingest"
                      and c.get("script") == "cosmos_sgh_drop_ingest.py"
                      and c.get("heartbeat") == "sgh_drop_ingest_heartbeat.json"
                      and c.get("logon") == "COSMOS SGH Drop Ingest Logon"
                      for c in CLOCKS))

    wd = Watchdog2(str(root))
    check("watchdog2 default queue is THIS install's queue role",
          lambda: wd.queue == root / "queue")
    check("watchdog2 task name COSMOS Watchdog2",
          lambda: WD2_TASK == "COSMOS Watchdog2")

    coll = Collector(str(root))
    check("collector default queue is THIS install's queue role",
          lambda: coll.queue == root / "queue")
    check("collector task name COSMOS Collector",
          lambda: COL_TASK == "COSMOS Collector")

    h = health_once(str(root))
    check("health clock writes heartbeat",
          lambda: (root / "logs" / "health_clock_heartbeat.json").exists())
    check("health clock verdict is a string",
          lambda: isinstance(h.get("verdict"), str))
    check("health clock does not require :8770 to write",
          lambda: h.get("ok") is True)
    board = json.loads((root / "state" / "health" / "board.json").read_text(
        encoding="utf-8"))
    check("health board carries tree_id",
          lambda: board.get("tree_id") == "spike-own-clocks")

    d = drive_once(str(root))
    check("drive meter ok", lambda: d.get("ok") is True)
    check("drive meter heartbeat",
          lambda: (root / "logs" / "drive_meter_heartbeat.json").exists())
    meter = json.loads((root / "state" / "drive" / "meter.json").read_text(
        encoding="utf-8"))
    check("drive meter lists at least one volume",
          lambda: isinstance(meter.get("drives"), list) and meter["drives"])

    s = spend_once(str(root))
    check("spend meter ok on empty ledger", lambda: s.get("ok") is True)
    check("spend meter heartbeat",
          lambda: (root / "logs" / "spend_meter_heartbeat.json").exists())

    v = verify_once(str(root))
    check("ledger verify ok on empty/fresh chain", lambda: v.get("ok") is True)
    check("ledger verify state VERIFIED",
          lambda: v.get("state") == "VERIFIED")

    r = rails_once(str(root))
    check("rails prober ok", lambda: r.get("ok") is True)
    check("rails prober probed > 0", lambda: int(r.get("probed_count") or 0) > 0)

    f = feed_once(str(root))
    check("cdeck feed writes feed.json",
          lambda: (root / "state" / "cdeck" / "feed.json").exists())
    feed = json.loads((root / "state" / "cdeck" / "feed.json").read_text(
        encoding="utf-8"))
    check("cdeck feed has pause + clocks + snapshots",
          lambda: "pause" in feed and "clocks" in feed and "snapshots" in feed)
    check("cdeck feed pause is not present on a fresh root",
          lambda: feed["pause"].get("present") is False)

    b = backup_once(str(root), force=True)
    check("backup clock force-run ok", lambda: b.get("ok") is True)
    check("backup clock files > 0", lambda: int(b.get("files") or 0) > 0)

    argv = plan_create("COSMOS Health", "py -3.14 x.py --loop", "minute", mo=1)
    check("plan_create: no /rl highest", lambda: "/rl" not in argv)
    check("plan_create: task name COSMOS Health",
          lambda: "COSMOS Health" in argv)

    check("backup task names COSMOS Backup HH",
          lambda: all(n.startswith("COSMOS Backup ") for n, _ in BAK_TASKS)
          and HEALTH_TASK == "COSMOS Health"
          and DRIVE_TASK == "COSMOS Drive Meter"
          and FEED_TASK == "COSMOS cDeck Feed"
          and LV_TASK == "COSMOS Ledger Verify"
          and SPEND_TASK == "COSMOS Spend Meter"
          and RAILS_TASK == "COSMOS Rails Prober")

    for name in NEW_MODULES:
        text = (COSMOS_DIR / name).read_text(encoding="utf-8")
        check(f"no bts_ import in {name}",
              lambda t=text: BTS_IMPORT.search(t) is None)
        check(f"{name} does not mention kernel/ledger/sched/service writes as self",
              lambda t=text: "Does NOT modify COSMOS core" in t
              or "Does not modify" in t
              or name in ("cosmos_clock.py", "cosmos_own_clocks.py"))

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for l, ok, e in RESULTS:
        print(("  OK  " if ok else "  FAIL") + f" {l}" + (f"  {e}" if e else ""))
    print(f"{len(RESULTS) - len(bad)}/{len(RESULTS)} passed")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
