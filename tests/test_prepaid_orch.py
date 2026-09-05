#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: F-53 prepaid parallel orchestrator (winner=grok, never claude).

Isolated from the live COSMOS root. Does not register schtasks. Does not
spawn grok (injected which + spawn). Proves:

  * CLOCKS id 24 is this satellite
  * winner is grok; claude is CLAUDE_SPEND
  * HOLD wins
  * missing grok is NO_RAIL
  * COW-fresh tick is PARALLEL: mailbox ping + one MOTIF drop (empty bucket)
  * PARALLEL flood guard: a second tick with an open order drops 0
  * COW-quiet tick is ORCHESTRATE, drop 1, spawn only if injected
  * --dry-run writes nothing
  * --plan-task registers nothing

Does not modify kernel/ledger/sched/service.
"""
from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "cosmos"))

from cosmos_kernel import install  # noqa: E402
from cosmos_own_clocks import CLOCKS  # noqa: E402
from cosmos_prepaid_orch import (  # noqa: E402
    CLOCK_ID, HEARTBEAT_NAME, PROJECTION_NAME, SCHEMA, TASK_NAME, WINNER,
    PrepaidOrchError, cow_fresh, open_prepaid_orders, plan_task_argv,
    poll_once, refuse_rail, spawn_argv,
)
import cosmos_prepaid_orch as orch  # noqa: E402

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _kind(fn):
    try:
        fn()
    except PrepaidOrchError as e:
        return e.kind
    return None


def _which_grok(name):
    return r"C:\fake\grok.exe" if name == "grok" else None


def _write_cow(root: Path, age_s: float) -> None:
    control = root / "state" / "control"
    control.mkdir(parents=True, exist_ok=True)
    (control / "COW_HEARTBEAT.json").write_text(json.dumps({
        "last_run_epoch": time.time() - age_s,
        "worker": "cow",
        "pid": 1,
    }), encoding="utf-8")


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_prepaid_orch_"))
    root = install(td / "live", tree_id="spike-prepaid-orch")

    check("CLOCK_ID is 24", lambda: CLOCK_ID == 24)
    check("CLOCKS id 24 is COSMOS Prepaid Orchestrator",
          lambda: any(c.get("id") == 24 and c.get("task") == TASK_NAME
                      and c.get("script") == "cosmos_prepaid_orch.py"
                      and c.get("heartbeat") == HEARTBEAT_NAME
                      for c in CLOCKS))
    check("winner is grok", lambda: WINNER == "grok")
    now = time.time()
    check("cow_fresh honors cosmos-cow-heartbeat stamped_at",
          lambda: cow_fresh({"stamped_at":
                             time.strftime("%Y-%m-%dT%H:%M:%S%z",
                                           time.localtime(now))}, now) is True)
    check("cow_fresh stamped_at older than HEARTBEAT_STALE_S is quiet",
          lambda: cow_fresh({"stamped_at":
                             time.strftime("%Y-%m-%dT%H:%M:%S%z",
                                           time.localtime(now - 999))},
                            now) is False)
    check("spawn_argv is grok --single --always-approve",
          lambda: spawn_argv("p", str(REPO), "sid-1")[:2] == ["grok", "--single"]
          and "--always-approve" in spawn_argv("p", str(REPO), "sid-1")
          and "claude" not in spawn_argv("p", str(REPO), "sid-1"))
    check("refuse_rail(claude) is CLAUDE_SPEND",
          lambda: _kind(lambda: refuse_rail("claude")) == "CLAUDE_SPEND")
    check("refuse_rail(grok) returns grok",
          lambda: refuse_rail("grok") == "grok")

    missing = poll_once(str(root), which=lambda _n: None, dry_run=True)
    check("missing grok is NO_RAIL",
          lambda: missing.get("state") == "NO_RAIL"
          and missing.get("kind") == "NO_RAIL"
          and missing.get("ok") is False
          and missing.get("writes") == 0)

    pause = root / "state" / "control" / "PAUSE.flag"
    pause.parent.mkdir(parents=True, exist_ok=True)
    pause.write_text(json.dumps({
        "state": "PAUSED", "mode": "hold", "set_by": "keith",
        "reason": "stop",
    }), encoding="utf-8")
    held = poll_once(str(root), which=_which_grok, dry_run=True)
    check("operator HOLD wins",
          lambda: held.get("state") == "HOLD" and held.get("kind") == "HOLD"
          and held.get("dropped") == 0)
    pause.unlink()

    _write_cow(root, age_s=5)
    calls = []
    par = poll_once(str(root), which=_which_grok, spawn=calls.append)
    hb = root / "logs" / HEARTBEAT_NAME
    proj = root / "state" / "prepaid_orch" / PROJECTION_NAME
    mail_cow = list((root / "state" / "mail" / "cow" / "inbox").glob("*.json"))
    check("COW-fresh tick is PARALLEL",
          lambda: par.get("ok") is True and par.get("state") == "PARALLEL"
          and par.get("schema") == SCHEMA)
    par_orders = list((root / "state" / "work_orders" / "bucket").glob("*.json"))
    par_order = (json.loads(par_orders[0].read_text(encoding="utf-8"))
                 if par_orders else {})
    check("PARALLEL empty-bucket drops one MOTIF work-order",
          lambda: par.get("dropped") == 1 and len(par_orders) == 1
          and par_order.get("state") == "DROPPED"
          and "prepaid-orch" in str(par_order.get("Agent") or "")
          and "MOTIF" in str(par_order.get("Task") or ""))
    check("PARALLEL spawn-injected fires once with grok argv",
          lambda: par.get("spawned") == 1 and len(calls) == 1
          and calls[0][0] == "grok" and "--always-approve" in calls[0])
    check("PARALLEL mailbox ping to cow",
          lambda: par.get("mail_sent") == 1 and len(mail_cow) == 1)
    check("PARALLEL writes heartbeat + projection",
          lambda: hb.is_file() and proj.is_file())
    check("open_prepaid_orders sees the PARALLEL drop",
          lambda: len(open_prepaid_orders(root)) == 1)

    calls_flood = []
    par2 = poll_once(str(root), which=_which_grok, spawn=calls_flood.append)
    par_orders2 = list((root / "state" / "work_orders" / "bucket").glob("*.json"))
    check("PARALLEL flood guard: second tick drops nothing",
          lambda: par2.get("state") == "PARALLEL" and par2.get("dropped") == 0
          and par2.get("spawned") == 0 and calls_flood == []
          and len(par_orders2) == 1 and par2.get("open_prepaid") == 1)

    quiet = Path(tempfile.mkdtemp(prefix="cosmos_prepaid_quiet_"))
    qroot = install(quiet / "live", tree_id="spike-prepaid-quiet")
    spawned = []
    orch_rec = poll_once(str(qroot), which=_which_grok, spawn=spawned.append)
    orders = list((qroot / "state" / "work_orders" / "bucket").glob("*.json"))
    check("COW-quiet tick is ORCHESTRATE",
          lambda: orch_rec.get("state") == "ORCHESTRATE"
          and orch_rec.get("ok") is True)
    check("ORCHESTRATE drops exactly one grok work-order",
          lambda: orch_rec.get("dropped") == 1 and len(orders) == 1)
    order = json.loads(orders[0].read_text(encoding="utf-8")) if orders else {}
    check("dropped order Agent family is xAI/grok, state DROPPED",
          lambda: "xAI" in str(order.get("Agent") or "")
          and order.get("state") == "DROPPED")
    check("injected spawn is called once with grok argv",
          lambda: len(spawned) == 1 and spawned[0][0] == "grok"
          and "--always-approve" in spawned[0])

    dry_root = install(Path(tempfile.mkdtemp(prefix="cosmos_prepaid_dry_"))
                       / "live", tree_id="spike-prepaid-dry")
    dry = poll_once(str(dry_root), which=_which_grok, dry_run=True)
    check("dry_run writes nothing",
          lambda: dry.get("dry_run") is True and dry.get("writes") == 0
          and not (dry_root / "logs" / HEARTBEAT_NAME).exists()
          and not (dry_root / "state" / "prepaid_orch" / PROJECTION_NAME).exists()
          and not list((dry_root / "state" / "work_orders" / "bucket").glob("*.json")))
    check("dry_run still plans grok argv",
          lambda: (dry.get("spawn_argv") or [None])[0] == "grok")

    argv = plan_task_argv(str(root))
    check("plan_task_argv is schtasks /create minute/1, no /rl",
          lambda: argv[0] == "schtasks" and "/create" in argv
          and TASK_NAME in argv and "minute" in argv and "/rl" not in argv)

    calls2 = []
    real = orch.subprocess.run
    orch.subprocess.run = lambda *a, **k: calls2.append((a, k)) or type(
        "P", (), {"returncode": 0, "stdout": "", "stderr": ""})()
    try:
        rc = orch.main(["--root", str(root), "--plan-task"])
    finally:
        orch.subprocess.run = real
    check("--plan-task registers nothing (subprocess.run never called)",
          lambda: rc == 0 and calls2 == [])

    rc_claude = orch.main(["--root", str(root), "--once", "--dry-run",
                           "--rail", "claude"])
    check("--rail claude exits 2 CLAUDE_SPEND",
          lambda: rc_claude == 2)

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for l, ok, e in RESULTS:
        print(("  OK  " if ok else "  FAIL") + f" {l}" + (f"  {e}" if e else ""))
    print(f"{len(RESULTS) - len(bad)}/{len(RESULTS)} passed")
    live_value = {
        "checks": len(RESULTS),
        "clock_id": CLOCK_ID,
        "winner": WINNER,
        "parallel_state": par.get("state"),
        "orchestrate_state": orch_rec.get("state"),
        "dropped": orch_rec.get("dropped"),
        "heartbeat": HEARTBEAT_NAME,
    }
    print("LIVE_VALUE", json.dumps(live_value))
    (REPO / "cosmos" / "_f53_prepaid_orch.json").write_text(
        json.dumps({"ok": not bad, "live_value": live_value}, indent=1) + "\n",
        encoding="utf-8")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
