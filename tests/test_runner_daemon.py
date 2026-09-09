#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: COSMOS runner daemon heartbeat + poll, isolated from the BTS queue.

Covers stage-5 HIGH/MED: file-drop adapter, logon-task name, bare -c refuse,
stranded heartbeat, status_view side-effect-free, sched_ledger after submit.
"""
from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_kernel import install
from cosmos_run import (HEARTBEAT_NAME, LOGON_TASK_NAME, TASK_NAME, bind,
                        heartbeat_age_s, plan_loop_argv, plan_task_argv,
                        pythonw_exe, status_view)
from cosmos_runner import Runner
from cosmos_sched import Scheduler

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_rundaemon_"))
    root = install(td / "live", tree_id="spike-runner-daemon")

    # ---- bind uses the resolver's queue role, never a foreign queue ----
    b = bind(str(root))
    check("bind: heartbeat path is logs/cosmos_runner_heartbeat.json",
          lambda: b["heartbeat"] == root / "logs" / HEARTBEAT_NAME)
    check("bind: queue is the install's queue role",
          lambda: b["queue"] == root / "queue")
    check("bind: queue is under THIS root",
          lambda: str(b["queue"]).startswith(str(root.resolve()) if False else str(root)))
    check("bind: adapter is attached",
          lambda: getattr(b["runner"], "adapter", None) is not None)

    # ---- poll_once writes last_run_epoch even when idle ----
    t0 = int(time.time())
    results = b["runner"].poll_once(b["heartbeat"])
    rec = json.loads(b["heartbeat"].read_text(encoding="utf-8"))
    check("poll_once: empty queue returns no jobs", lambda: results == [])
    check("poll_once: heartbeat file exists", lambda: b["heartbeat"].exists())
    check("poll_once: last_run_epoch is an int near now",
          lambda: isinstance(rec["last_run_epoch"], int)
          and abs(rec["last_run_epoch"] - t0) < 10)
    check("poll_once: last_run carries a UTC offset",
          lambda: rec["last_run"].endswith(("+00:00",))
          or ("+" in rec["last_run"][-6:] or rec["last_run"][-6:].count(":") == 1
              and rec["last_run"][-6] in "+-"))
    check("poll_once: queue_root in heartbeat is THIS install's queue",
          lambda: rec["queue_root"] == str(root / "queue"))
    check("heartbeat_age_s: fresh after poll",
          lambda: heartbeat_age_s(rec) is not None and heartbeat_age_s(rec) < 5)
    check("poll_once: idle empty names pending_files=0 not just tick=idle",
          lambda: rec.get("tick") == "idle" and rec.get("pending_files") == 0
          and rec.get("manifests_queued") == 0)

    # ---- drain_loop stops when asked; heartbeat advances ----
    n = {"i": 0}

    def stop():
        n["i"] += 1
        return n["i"] > 2

    b["runner"].drain_loop(b["heartbeat"], interval_s=0.05, stop=stop)
    rec2 = json.loads(b["heartbeat"].read_text(encoding="utf-8"))
    check("drain_loop: polls field increments",
          lambda: rec2.get("polls", 0) >= 2)
    check("drain_loop: last_run_epoch still fresh",
          lambda: abs(rec2["last_run_epoch"] - int(time.time())) < 10)

    # ---- a real job through poll_once lands CLEAN and is recorded (argv: form) ----
    jid = b["sched"].submit(
        'argv:["py","-3.14","-c","print(\'cosmos-own-queue\')"]', "normal")
    got = b["runner"].poll_once(b["heartbeat"])
    rec3 = json.loads(b["heartbeat"].read_text(encoding="utf-8"))
    check("poll_once: submitted job claimed and CLEAN",
          lambda: len(got) == 1 and got[0]["job_id"] == jid
          and got[0]["outcome"] == "CLEAN")
    check("poll_once: heartbeat names the job",
          lambda: rec3.get("jobs_this_tick") == 1
          and jid in (rec3.get("job_ids") or []))
    check("poll_once: sched_ledger exists under the bound queue after submit",
          lambda: (b["queue"] / "sched_ledger.jsonl").is_file()
          and "JOB_SUBMITTED" in (b["queue"] / "sched_ledger.jsonl").read_text(
              encoding="utf-8"))

    # ---- H4: bare submit is BAD_COMMAND, not python -c ----
    j_bare = b["sched"].submit("import os; os.system('echo pwned')", "normal")
    r_bare = b["runner"].run_one()
    check("H4: bare submit() is BAD_COMMAND not -c",
          lambda: r_bare["job_id"] == j_bare and r_bare["outcome"] == "BROKE"
          and r_bare.get("bad_command"))
    check("bind: runner.paths is the install (pool can run crucible:round)",
          lambda: getattr(b["runner"], "paths", None) is not None)

    j_cru_bad = b["sched"].submit("crucible:round not-json", "high")
    r_cru_bad = b["runner"].run_one()
    check("crucible:round bad JSON is BROKE, not python -c",
          lambda: r_cru_bad["job_id"] == j_cru_bad
          and r_cru_bad["outcome"] == "BROKE")

    j_cru_path = b["sched"].submit(
        'crucible:round {"sources":["C:/Windows/win.ini"],"critics":["ALPHA"]}',
        "high")
    r_cru_path = b["runner"].run_one()
    check("crucible:round absolute source is refuse, not a spend round",
          lambda: r_cru_path["job_id"] == j_cru_path
          and r_cru_path["outcome"] == "BROKE")

    # ---- H4: argv: -c plus an outside path token is still confined ----
    outside = td / "c_with_path.py"
    outside.write_text("print('pwn-path')\n", encoding="utf-8")
    j_cpath = b["sched"].submit(
        "argv:" + json.dumps(["py", "-3.14", "-c", "print(1)", str(outside)]),
        "normal")
    r_cpath = b["runner"].run_one()
    check("H4: argv: with -c still confines other path tokens",
          lambda: r_cpath["job_id"] == j_cpath and r_cpath.get("traversal_refused"))

    # ---- M3: pre-claim queue path is traversal, not a job ----
    pre = b["queue"] / "preclaim_not_a_job.py"
    pre.write_text("print('pre-claim')\n", encoding="utf-8")
    ad = b["runner"].adapter
    b["runner"].adapter = None
    try:
        j_pre = b["sched"].submit(f"py:{pre}", "normal")
        r_pre = b["runner"].run_one()
    finally:
        b["runner"].adapter = ad
    check("M3: py: of a pre-claim queue path is traversal_refused",
          lambda: r_pre["job_id"] == j_pre and r_pre.get("traversal_refused"))

    # ---- M2: stranded heartbeat names the unmatched file-drop ----
    held = b["queue"] / "stranded_hold__t30.py"
    held.write_text("print('hold')\n", encoding="utf-8")
    pending = b["runner"].adapter.scan()
    b["runner"].write_heartbeat(b["heartbeat"], extra={
        "tick": "stranded",
        "pending_files": len(pending),
        "pending_file_names": [p.name for p in pending],
    })
    rec_s = json.loads(b["heartbeat"].read_text(encoding="utf-8"))
    check("M2: heartbeat tick=stranded with pending_files when drops sit",
          lambda: rec_s.get("tick") == "stranded" and rec_s.get("pending_files", 0) >= 1
          and "stranded_hold__t30.py" in (rec_s.get("pending_file_names") or []))

    # ---- H1/H2: file-drop without submit() is claimed-by-rename and CLEAN ----
    drop = b["queue"] / "drop_ok__t30.py"
    drop.write_text("print('file-drop-ok')\n", encoding="utf-8")
    time.sleep(0.05)
    got_drop = b["runner"].poll_once(b["heartbeat"])
    rec_d = json.loads(b["heartbeat"].read_text(encoding="utf-8"))
    check("H1: file-drop without submit() is drained CLEAN",
          lambda: len(got_drop) == 1 and got_drop[0]["outcome"] == "CLEAN")
    check("H2: claimed file left the queue root (rename into running/done)",
          lambda: not drop.exists())
    check("H1: heartbeat tick=drained names the adapted job",
          lambda: rec_d.get("tick") == "drained"
          and got_drop[0]["job_id"] in (rec_d.get("job_ids") or []))
    check("H2: adapter copy sits under tools/adapter_jobs",
          lambda: (root / "cosmos" / "adapter_jobs").exists()
          and any(p.suffix == ".py" for p in (root / "cosmos" / "adapter_jobs").iterdir()))
    done_hit = list((b["queue"] / "done").glob("drop_ok__t30*.py")) if (
        b["queue"] / "done").exists() else []
    check("L7/H2: CLEAN file-drop projected into queue/done",
          lambda: len(done_hit) == 1)

    # leftover file-drops (stranded_hold, preclaim) — drain so later checks stay quiet
    for _ in range(6):
        if not b["runner"].adapter.scan():
            break
        b["runner"].poll_once(b["heartbeat"])

    # ---- launcher plans: logon name is NOT the minute self-heal ----
    loop_argv = plan_loop_argv(str(root))
    task_argv = plan_task_argv(str(root))
    tn = task_argv[task_argv.index("/tn") + 1] if "/tn" in task_argv else ""
    check("plan_loop_argv: pythonw + --loop + this root",
          lambda: loop_argv[0] == pythonw_exe()
          and "--loop" in loop_argv
          and str(root.resolve()) in loop_argv)
    check("plan_task_argv: /tn is COSMOS Runner Logon, not the minute task",
          lambda: tn == LOGON_TASK_NAME and tn != TASK_NAME
          and "onlogon" in task_argv)
    check("plan_task_argv: /tr points at cosmos_run.py --loop, not BTS queue",
          lambda: "cosmos_run.py" in task_argv[task_argv.index("/tr") + 1]
          and "--loop" in task_argv[task_argv.index("/tr") + 1]
          and r"V:\Ai\_queue" not in task_argv[task_argv.index("/tr") + 1])

    # ---- M5: --status does not mkdir manifests / compose Scheduler ----
    root_st = install(td / "live_status", tree_id="spike-runner-status")
    before = (root_st / "queue" / "manifests").exists()
    view = status_view(str(root_st))
    check("M5: status_view does not create queue/manifests",
          lambda: not before and not (root_st / "queue" / "manifests").exists()
          and view["queue"] == str(root_st / "queue")
          and view["path"].endswith(HEARTBEAT_NAME))

    # ---- Runner.write_heartbeat is also usable off bind() ----
    s = Scheduler(td / "q2", b"k", "F5")
    r = Runner(s, td / "w2", "F5")
    hb = td / "hb.json"
    r.write_heartbeat(hb)
    h = json.loads(hb.read_text(encoding="utf-8"))
    check("Runner.write_heartbeat: last_run_epoch present without a bind",
          lambda: isinstance(h.get("last_run_epoch"), int) and h["worker"] == "F5")

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for l, ok, e in RESULTS:
        print(("  OK  " if ok else "  FAIL") + f" {l}" + (f"  {e}" if e else ""))
    print(f"{len(RESULTS) - len(bad)}/{len(RESULTS)} passed")
    return 1 if bad else 0


def test_runner_daemon():
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
