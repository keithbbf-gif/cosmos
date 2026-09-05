#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: COSMOS results-collector projection + heartbeat + dedup.

Isolated from the live BTS queue and the live COSMOS root. Does not register
schtasks or spawn a daemon. Proves: bind uses the resolver; poll_once writes
heartbeat + index + COLLECTOR.md; dedup by artifact+mtime; second poll is a
no-op for unchanged files; a rewritten file (new mtime) is a new row; ledger
result events are collected and BOOT_VERIFIED is not; schtasks plan points at
cosmos_collector.py --loop.

The DHx grammar/join unit checks moved to tests/test_collector_dhx.py with
cosmos_collector_dhx (PHASE 4 split, docs/CORE_RESTRUCTURE.md). What is proved
here is the end-to-end behaviour plus the re-export contract.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_kernel import install
from cosmos_collector import (
    HEARTBEAT_NAME, TASK_NAME, TASK_NAME_LOGON, Collector, bind, heartbeat_age_s,
    plan_loop_argv, plan_task_argv, plan_logon_argv, pythonw_exe, dedup_key,
    parse_dhx_markers, display_agent, WELL_KNOWN_BOOTSTRAP,
    iter_queue_files, ledger_event_kept,
)

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_collector_"))
    root = install(td / "live", tree_id="spike-collector")
    queue = td / "queue"
    research = td / "research"
    summary = td / "docs" / "COLLECTOR.md"

    # ---- fake BTS queue (root + lg + pb) ----
    _write(queue / "g46_fanout12_result.json", json.dumps({
        "agents": 2, "ok": 2, "rc": 0, "app": "COSMOS",
        "out_tail": "fanout complete 2/2",
        "by_app": {"COSMOS": ["research1:ok"]},
    }))
    _write(queue / "cursor_prove_result.json", json.dumps({
        "me": {"apiKeyName": "Cursor COSMOS 2"},
        "run": {"status": "FINISHED", "result": "wrote CURSOR_PROVE.md"},
    }))
    _write(queue / "done" / "g46_review__t600.py", '"""review the lock."""\nprint(1)\n')
    _write(queue / "failed" / "cosmos_populate__t600.py", "raise SystemExit(1)\n")
    _write(queue / "logs" / "g46_review__t600__2026-08-25T21-00-00.log",
           "start\nCLEAN rc=0\n")
    _write(queue / "_lanes" / "lg" / "grok_docs_result.json", json.dumps({
        "rc": 0, "ok": True, "out_tail": "gitlab docs collected",
    }))
    _write(queue / "_lanes" / "lg" / "done" / "grok_docs__t1200.py", "print('lg')\n")
    _write(queue / "_lanes" / "pb" / "claude_docs_result.json", json.dumps({
        "rc": 1, "ok": False, "err": "timeout",
    }))
    _write(queue / "_lanes" / "pb" / "failed" / "stage2_fanout__t1800.py", "nope\n")
    # a queued (not done) script must NOT be indexed
    _write(queue / "waiting_job__t300.py", "print('still queued')\n")

    # ---- research ----
    _write(research / "COSMOS" / "RESEARCH_1.md",
           "# COSMOS Core OS — RESEARCH_1\n\n**Researcher:** G46\n")
    _write(research / "G46_HANDS.md",
           "# G46 hands\n\nHow Grok Build actually works.\n")

    # ---- authority ledger (unsigned JSONL; collector does not verify HMAC) ----
    led = root / "ledger" / "authority.jsonl"
    led.parent.mkdir(parents=True, exist_ok=True)
    events = [
        {"seq": 1, "event": "BOOT_VERIFIED", "t": 1000.0, "writer": "cli",
         "payload": {"root": str(root)}, "payload_len": 1},
        {"seq": 2, "event": "RAIL_RESULT", "t": 2000.0, "writer": "cm-dispatch",
         "payload": {"link_id": "sgh-api", "ok": True, "reply": "I am Grok"},
         "payload_len": 40},
        {"seq": 3, "event": "TOOL_DECLARED", "t": 3000.0, "writer": "cli",
         "payload": {"id": "noise"}, "payload_len": 2},
        {"seq": 4, "event": "PROBE_RESULT", "t": 4000.0, "writer": "prober",
         "payload": {"link_id": "gem-api", "ok": True}, "payload_len": 20},
    ]
    led.write_text("\n".join(json.dumps(e) for e in events) + "\n", encoding="utf-8")

    # DHx fixture: one marker whose result exists, one that is MISSING,
    # plus a cm/ lane marker (H1 residual: parser used to only match root|lg|pb)
    dhx = td / "docs" / "AGENT_BRIEF.md"
    _write(dhx, """# DHx
## Assignment log — APPEND-ONLY markers
- 2026-08-25T21:00:00-05:00 · G46 · fanout test · root/g46_fanout12__t600.py
- 2026-08-25T21:01:00-05:00 · G46 · ghost never returned · root/ghost_unmatched__t1800.py
- 2026-08-27T01:50:46.467635-05:00 · G46 · motif_collector_s6 gate · cm/g46_grok_motif_collector_s6_you_are_g46_grok_bd071d24__t1800.py
- 2026-08-25T23:55:24.411180-05:00 · GROK · pickup PONG · buckets/grok/proof_pong_grok.json
## Active assignments
- ignore
""")
    # native COSMOS queue role + returns/ + runner_ledger (M1/M2/M3)
    _write(root / "queue" / "native_probe_result.json", json.dumps({
        "rc": 0, "ok": True, "agent": "G46", "summary": "native queue hit",
    }))
    _write(queue / "returns" / "g46_fanout12_result.json", json.dumps({
        "rc": 0, "ok": True, "agent": "G46", "out_tail": "returns copy",
    }))
    _write(queue / "returns" / "cm" / "g46_grok_motif_collector_s6_you_are_g46_grok_bd071d24_result.json",
           json.dumps({
               "rc": 0, "ok": True, "agent": "G46",
               "summary": "collector stage-6 gate",
           }))
    _write(queue / "_lanes" / "cm" / "done" / "g46_grok_motif_collector_s6_you_are_g46_grok_bd071d24__t1800.py",
           "print('cm lane job')\n")
    _write(root / "returns" / "G46" / "drop_probe_result.json", json.dumps({
        "rc": 0, "ok": True, "agent": "G46", "summary": "live/returns drop",
    }))
    _write(root / "returns" / "GROK" / "proof_pong_grok_result.json", json.dumps({
        "rc": 0, "ok": True, "agent": "GROK", "summary": "PONG",
    }))
    _write(queue / "runner_ledger.jsonl",
           json.dumps({"t": 2000.0, "event": "end", "job": "g46_fanout12__t600.py",
                       "rc": 0, "elapsed": 1.2, "verdict": "OK"}) + "\n")
    # spend event must NOT be collected (M10)
    events.append(
        {"seq": 5, "event": "SPEND_RESERVED", "t": 5000.0, "writer": "cli",
         "payload": {"rail": "oa-api"}, "payload_len": 3},
    )
    led.write_text("\n".join(json.dumps(e) for e in events) + "\n", encoding="utf-8")

    coll = Collector(str(root), queue=queue, research=research,
                     summary_md=summary, interval_s=30.0, dhx=dhx)

    check("bind/ctor: heartbeat path is logs/collector_heartbeat.json",
          lambda: coll.heartbeat == root / "logs" / HEARTBEAT_NAME)
    check("bind/ctor: index is state/collector/index.jsonl",
          lambda: coll.index_path == root / "state" / "collector" / "index.jsonl")
    check("bind/ctor: queue is the TEST queue, not V:\\Ai\\_queue",
          lambda: coll.queue == queue)
    check("H4: native queue identity is resolver role",
          lambda: coll.native_queue == root / "queue")

    t0 = int(time.time())
    r1 = coll.poll_once()
    rec = json.loads(coll.heartbeat.read_text(encoding="utf-8"))
    rows = [json.loads(ln) for ln in coll.index_path.read_text(encoding="utf-8").splitlines()
            if ln.strip()]

    check("poll_once: heartbeat file exists", lambda: coll.heartbeat.exists())
    check("poll_once: last_run_epoch is an int near now",
          lambda: isinstance(rec["last_run_epoch"], int)
          and abs(rec["last_run_epoch"] - t0) < 30)
    check("poll_once: last_run carries an offset",
          lambda: rec["last_run"][-6] in "+-" or rec["last_run"].endswith("Z"))
    check("heartbeat_age_s: fresh after poll",
          lambda: heartbeat_age_s(rec) is not None and heartbeat_age_s(rec) < 10)
    check("poll_once: polls field is 1", lambda: rec.get("polls") == 1)
    check("poll_once: worker is cosmos-collector",
          lambda: rec.get("worker") == "cosmos-collector")
    check("poll_once: new_this_tick > 0", lambda: r1["new_this_tick"] > 0)
    check("poll_once: index_rows == new_this_tick on first poll",
          lambda: r1["index_rows"] == r1["new_this_tick"])
    check("index: at least the two root result JSONs",
          lambda: sum(1 for x in rows if x.get("source") == "queue_result") >= 3)
    check("index: g46_fanout12 collected with app COSMOS",
          lambda: any(x.get("task") == "g46_fanout12" and x.get("app") == "COSMOS"
                      for x in rows))
    check("index: cursor_prove inferred as Cursor",
          lambda: any(x.get("task") == "cursor_prove"
                      and x.get("maker") == "Cursor" for x in rows))
    check("index: lg lane result collected",
          lambda: any(x.get("lane") == "lg" and x.get("source") == "queue_result"
                      for x in rows))
    check("index: pb failed result status failed",
          lambda: any(x.get("lane") == "pb" and x.get("status") == "failed"
                      for x in rows))
    check("index: done/ script collected",
          lambda: any(x.get("source") == "queue_done" for x in rows))
    check("index: failed/ script collected",
          lambda: any(x.get("source") == "queue_failed" for x in rows))
    check("index: logs/ collected",
          lambda: any(x.get("source") == "queue_log" for x in rows))
    check("index: waiting (not done) job NOT collected",
          lambda: not any("waiting_job" in str(x.get("artifact")) for x in rows))
    check("index: RESEARCH_1.md collected under COSMOS",
          lambda: any(x.get("source") == "research"
                      and "RESEARCH_1" in str(x.get("artifact"))
                      and x.get("app") == "COSMOS" for x in rows))
    check("index: G46_HANDS.md maker is G46",
          lambda: any(x.get("task") == "G46_HANDS" and x.get("maker") == "G46"
                      for x in rows))
    check("index: RAIL_RESULT ledger event collected",
          lambda: any(x.get("source") == "ledger"
                      and str(x.get("task")).startswith("RAIL_RESULT")
                      for x in rows))
    check("index: PROBE_RESULT ledger event collected",
          lambda: any(x.get("source") == "ledger"
                      and str(x.get("task")).startswith("PROBE_RESULT")
                      for x in rows))
    check("index: BOOT_VERIFIED NOT collected (infrastructure noise)",
          lambda: not any("BOOT_VERIFIED" in str(x.get("task")) for x in rows))
    check("index: TOOL_DECLARED NOT collected",
          lambda: not any("TOOL_DECLARED" in str(x.get("task")) for x in rows))
    check("M10: SPEND_RESERVED NOT collected",
          lambda: not any("SPEND_RESERVED" in str(x.get("task")) for x in rows))
    check("H1: DHx marker for g46_fanout12 is matched to a result",
          lambda: any(x.get("source") == "dhx_marker"
                      and "g46_fanout12" in str(x.get("artifact"))
                      and x.get("status") == "matched"
                      and x.get("result_artifact")
                      and x.get("result_artifact") != "MISSING"
                      for x in rows))
    check("H1: unmatched DHx marker is explicit MISSING",
          lambda: any(x.get("source") == "dhx_marker"
                      and "ghost_unmatched" in str(x.get("artifact"))
                      and x.get("status") == "MISSING"
                      and x.get("result_artifact") == "MISSING"
                      for x in rows))
    check("H1: cm/ lane jobfile is parsed (not swallowed into assignment)",
          lambda: any(x.get("source") == "dhx_marker"
                      and "bd071d24" in str(x.get("jobfile") or x.get("artifact"))
                      and x.get("lane") == "cm"
                      for x in rows))
    check("H1: cm/ motif_collector_s6 marker is matched to a result",
          lambda: any(x.get("source") == "dhx_marker"
                      and "bd071d24" in str(x.get("artifact"))
                      and x.get("status") == "matched"
                      and x.get("result_artifact")
                      and x.get("result_artifact") != "MISSING"
                      for x in rows))
    check("H2: lane cm is never stored as maker or agent",
          lambda: all(str(x.get("maker")).lower() != "cm"
                      and str(x.get("agent")).lower() != "cm"
                      for x in rows))
    check("M2: live/returns drop zone collected",
          lambda: any(x.get("source") == "drop_returns"
                      and "drop_probe" in str(x.get("artifact")).replace("\\", "/")
                      for x in rows))
    check("H2: lane pb is never stored as maker or agent",
          lambda: all(str(x.get("maker")).lower() != "pb"
                      and str(x.get("agent")).lower() != "pb"
                      for x in rows))
    check("H2: lane lg is never stored as maker or agent",
          lambda: all(str(x.get("maker")).lower() != "lg"
                      and str(x.get("agent")).lower() != "lg"
                      for x in rows))
    check("M1: runner_ledger.jsonl collected",
          lambda: any(x.get("source") == "runner_ledger" for x in rows))
    check("M2: returns/ collected as queue_returns",
          lambda: any(x.get("source") == "queue_returns"
                      and "returns" in str(x.get("artifact")).replace("\\", "/")
                      for x in rows))
    check("M3: native live/queue role scanned",
          lambda: any(x.get("task") == "native_probe" for x in rows))
    check("H3: index_rows equals file line count",
          lambda: r1.get("index_rows") == r1.get("index_file_lines") == len(rows))

    md = summary.read_text(encoding="utf-8")
    check("COLLECTOR.md exists at the configured summary path",
          lambda: summary.exists() and len(md) > 100)
    check("COLLECTOR.md grouped heading for Grok/G46/COSMOS/Cursor",
          lambda: ("# COSMOS Results Collector" in md
                   and "## COSMOS" in md
                   and ("## G46" in md or "## Grok" in md)
                   and "## Cursor" in md))
    check("H2: COLLECTOR.md has ## G46 (agent), not ## pb / ## lg",
          lambda: ("## G46" in md and "## pb" not in md and "## lg" not in md))
    check("H1: COLLECTOR.md has DHx DIFF section with MISSING",
          lambda: ("DHx" in md and "MISSING" in md and "ghost_unmatched" in md))
    check("H2: COLLECTOR.md groups motif_collector under G46 not cm",
          lambda: ("bd071d24" in md and "## G46" in md
                   and "\n## cm\n" not in md and not md.startswith("## cm\n")))
    check("stage6 gate file quotes a live-tree triple",
          lambda: (coll.paths.state("collector") / "STAGE6_GATE.json").exists()
          and json.loads((coll.paths.state("collector") / "STAGE6_GATE.json")
                         .read_text(encoding="utf-8")).get("bound") is True)
    check("M4: unmatched assignments are listed (not capped away)",
          lambda: "ghost never returned" in md or "ghost_unmatched" in md)
    check("live summary also written under state/collector/",
          lambda: coll.live_summary.exists())
    check("H1: dhx.json snapshot exists with matched+missing",
          lambda: (coll.dhx_snap.exists()
                   and (lambda d: d.get("matched") >= 1 and d.get("missing") >= 1)(
                       json.loads(coll.dhx_snap.read_text(encoding="utf-8")))))

    n_first = r1["index_rows"]
    r2 = coll.poll_once()
    rec2 = json.loads(coll.heartbeat.read_text(encoding="utf-8"))
    check("second poll: new_this_tick == 0 (dedup by artifact+mtime)",
          lambda: r2["new_this_tick"] == 0)
    check("second poll: index_rows unchanged",
          lambda: r2["index_rows"] == n_first)
    check("second poll: polls incremented",
          lambda: rec2.get("polls") == 2)
    check("drain_loop: two more ticks increment polls",
          (lambda: (lambda n: (coll.drain_loop(interval_s=0.01,
                                               stop=(lambda: (n.__setitem__(0, n[0]+1) or n[0] > 2))),
                               json.loads(coll.heartbeat.read_text(encoding="utf-8")).get("polls") >= 4)
                    )([0])[1]))

    # rewrite a result (new mtime) -> new row; old row kept (append-only)
    time.sleep(1.05)
    _write(queue / "g46_fanout12_result.json", json.dumps({
        "agents": 2, "ok": 2, "rc": 0, "app": "COSMOS",
        "out_tail": "fanout rewritten",
    }))
    r3 = coll.poll_once()
    rows3 = [json.loads(ln) for ln in coll.index_path.read_text(encoding="utf-8").splitlines()
             if ln.strip()]
    fanouts = [x for x in rows3 if x.get("task") == "g46_fanout12"
               and x.get("source") == "queue_result"]
    check("rewrite: new_this_tick >= 1 (rewritten result is a new row)",
          lambda: r3["new_this_tick"] >= 1)
    check("rewrite: both mtimes kept (never lose a result)",
          lambda: len(fanouts) == 2)
    check("rewrite: newest summary is the rewritten tail",
          lambda: any("rewritten" in str(x.get("summary")) for x in fanouts))
    keys = {dedup_key(x["artifact"], x["mtime"]) for x in rows3}
    check("dedup_key unique across index", lambda: len(keys) == len(rows3))

    # ---- launcher plans ----
    loop_argv = plan_loop_argv(str(root))
    task_argv = plan_task_argv(str(root))
    check("plan_loop_argv: pythonw + --loop + this root",
          lambda: loop_argv[0] == pythonw_exe()
          and "--loop" in loop_argv
          and str(root.resolve()) in loop_argv)
    check("plan_task_argv: schtasks /create /tn COSMOS Collector /sc minute /mo 1",
          lambda: task_argv[0] == "schtasks" and task_argv[1] == "/create"
          and TASK_NAME in task_argv and "minute" in task_argv
          and "1" in task_argv)
    check("plan_task_argv: /tr points at cosmos_collector.py --loop",
          lambda: "cosmos_collector.py" in task_argv[task_argv.index("/tr") + 1]
          and "--loop" in task_argv[task_argv.index("/tr") + 1])
    check("plan_task_argv: does not bake V:\\Ai\\_queue (queue is a default, not identity)",
          lambda: r"V:\Ai\_queue" not in task_argv[task_argv.index("/tr") + 1])
    logon_argv = plan_logon_argv(str(root))
    check("plan_logon_argv: ONLOGON relaunch (M7)",
          lambda: TASK_NAME_LOGON in logon_argv and "onlogon" in logon_argv)

    b = bind(str(root), queue=queue, research=research, summary_md=summary, dhx=dhx)
    check("bind() returns a Collector", lambda: isinstance(b, Collector))

    # H1: MISSING marker later matches when the result appears
    _write(queue / "ghost_unmatched_result.json", json.dumps({
        "rc": 0, "ok": True, "agent": "G46", "summary": "ghost returned",
    }))
    r4 = coll.poll_once()
    rows4 = [json.loads(ln) for ln in coll.index_path.read_text(encoding="utf-8").splitlines()
             if ln.strip()]
    ghosts = [x for x in rows4 if x.get("source") == "dhx_marker"
              and "ghost_unmatched" in str(x.get("artifact"))]
    check("H1: later result flips ghost marker to matched",
          lambda: any(x.get("status") == "matched" for x in ghosts)
          and r4["new_this_tick"] >= 1)

    # H3: sibling append during the next poll appears in the summary
    sib = {
        "schema": "cosmos-collector/1", "source": "dispatch_assignment",
        "lane": "root", "agent": "G46", "maker": "Grok", "app": "Grok",
        "task": "sibling_dispatch", "status": "assigned", "rc": None,
        "artifact": str(queue / "sibling_dispatch__t1800.py"),
        "mtime": time.time(), "mtime_iso": "2026-08-25T23:00:00-05:00",
        "summary": "sibling writer", "bytes": 1,
    }
    with open(coll.index_path, "a", encoding="utf-8", newline="") as fh:
        fh.write(json.dumps(sib, sort_keys=True) + "\n")
    r5 = coll.poll_once()
    md5 = summary.read_text(encoding="utf-8")
    check("H3: sibling dispatch row appears in next summary",
          lambda: "sibling_dispatch" in md5
          and r5.get("index_rows") == r5.get("index_file_lines"))

    # M9: growing log is not a new result
    logp = queue / "logs" / "g46_review__t600__2026-08-25T21-00-00.log"
    before_logs = sum(1 for x in rows4 if x.get("source") == "queue_log"
                      and str(x.get("artifact")) == str(logp))
    time.sleep(1.05)
    _write(logp, "start\nCLEAN rc=0\nmore lines appended\n")
    r6 = coll.poll_once()
    rows6 = [json.loads(ln) for ln in coll.index_path.read_text(encoding="utf-8").splitlines()
             if ln.strip()]
    after_logs = sum(1 for x in rows6 if x.get("source") == "queue_log"
                     and str(x.get("artifact")) == str(logp))
    check("M9: growing queue_log does not add a second row",
          lambda: after_logs == before_logs == 1)

    # H4: missing configured bootstrap is a typed error, not a quiet 0
    missing_q = td / "no_such_queue"
    coll_miss = Collector(str(root), queue=missing_q, research=research,
                          summary_md=td / "docs" / "COLLECTOR_miss.md",
                          interval_s=30.0, dhx=dhx)
    rm = coll_miss.poll_once()
    check("H4: missing bootstrap -> tick=error with typed reason",
          lambda: rm.get("tick") == "error"
          and any("BOOTSTRAP_QUEUE_MISSING" in str(e) for e in (rm.get("errors") or [])))

    ident = Collector(str(root), research=research, summary_md=summary, dhx=dhx)
    check("H4: default identity is resolver queue, not the BTS drive literal",
          lambda: ident.queue == ident.native_queue == root / "queue"
          and ident.bootstrap_configured is False)

    # The DHx grammar/join unit checks moved to tests/test_collector_dhx.py with
    # the module (PHASE 4 split). What stays here is the re-export contract: the
    # names this suite has always imported off cosmos_collector still resolve,
    # and still resolve to the module that now owns them.
    markers = parse_dhx_markers(dhx.read_text(encoding="utf-8"))
    check("re-export: parse_dhx_markers off cosmos_collector still parses the log",
          lambda: len(markers) == 4 and markers[0]["agent"] == "G46"
          and markers[1]["jobfile"].startswith("ghost_unmatched"))
    check("re-export: the DHx names are cosmos_collector_dhx's, not a copy",
          lambda: parse_dhx_markers.__module__ == "cosmos_collector_dhx")
    check("re-export: the scan names are cosmos_collector_scan's, not a copy",
          lambda: iter_queue_files.__module__ == "cosmos_collector_scan"
          and ledger_event_kept.__module__ == "cosmos_collector_scan")
    pb_row = {"agent": "pb", "maker": "pb", "task": "add_kdash",
              "artifact": str(queue / "_lanes" / "pb" / "done" / "add_kdash.py")}
    check("display_agent: lane name pb is not an agent",
          lambda: display_agent(pb_row) == "unknown")

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for l, ok, e in RESULTS:
        print(("  OK  " if ok else "  FAIL") + f" {l}" + (f"  {e}" if e else ""))
    print(f"{len(RESULTS) - len(bad)}/{len(RESULTS)} passed")
    return 1 if bad else 0


def test_collector():
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
