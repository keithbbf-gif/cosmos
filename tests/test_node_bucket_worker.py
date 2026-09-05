#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: GROK/GEM bucket daemons. Isolated from the live tree.

Proves: own buckets, O_EXCL exactly-once (one worker-id wins), HOLD idle,
expired RESUME-GATE drains, V: result file, unique worker-id on fence+result,
monotonic last_run_epoch, grok does not pick gem, register helper EMITS
/Create and does not call schtasks. Fake rail_call so no live spend.
No BTS import. Does not modify kernel/ledger/sched/service.
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_kernel import install  # noqa: E402
from cosmos_node_bucket_worker import (  # noqa: E402
    NODES, bucket_dir, canon_node, claim_drop, dest_dir, list_drop_files,
    parse_task, pause_decision, pause_flag, poll_once, v_returns,
)
from cosmos_paths import CosmosPaths  # noqa: E402
from register_node_workers import keith_cmd, plan  # noqa: E402

RESULTS = []
BTS_IMPORT = re.compile(r"^\s*(?:from|import)\s+bts_\w+", re.M)
COSMOS_DIR = Path(__file__).resolve().parent.parent / "cosmos"
LIVE_VALUE: dict = {}


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _fake_grok(prompt: str) -> dict:
    return {
        "ok": True, "kind": "API", "text": "PONG",
        "usd": 0.004, "node": "fake_sgh", "model": "fake-grok",
        "link_id": "sgh-api",
    }


def _fake_gem(prompt: str) -> dict:
    return {
        "ok": True, "kind": "API", "text": "PONG",
        "usd": 0.01, "node": "fake_gem", "model": "fake-gemini",
        "link_id": "gem-api",
    }


def stage5_critique() -> dict:
    """What a different-family critic would flag. Bound to the build."""
    return {
        "family_note": (
            "Builder is G46/Grok. This is a self-critique, not a second-family "
            "vote. COW still owes GEM/OA stage-5 on the disposed tree."
        ),
        "starvation": {
            "one_task_per_tick": (
                "Intentional: a long rail must not starve last_run_epoch. "
                "A deep grok bucket drains 1 drop / 15s. HOLD starves by "
                "design. Crash after O_EXCL fence + before rename: fence is "
                "released if the drop is still in the inbox and the pid is "
                "dead; a live pid keeps the fence (anti double-claim wins)."
            ),
            "open": (
                "Incumbent cosmos_node_worker.py still rename-claims without "
                "this fence. During transition both daemons can see the same "
                "drop; the OS lock (grok_worker.lock) serializes --loop, but "
                "two --once processes without the lock can still race the "
                "old rename path. Stop the old TR when Keith runs keith_cmd."
            ),
        },
        "double_claim": {
            "same_helper": (
                "Two threads / two worker-ids: O_EXCL fence first, one winner. "
                "Grok never lists live/buckets/gem (own bucket)."
            ),
            "across_daemons": (
                "Grok vs GEM cannot double-claim: separate buckets, separate "
                "locks, separate heartbeats. Two GROK processes share "
                "grok_worker.lock in --loop. The remaining hole is the "
                "incumbent rename-claimer (cosmos_node_worker) which this "
                "file does not edit (NEW-files-only / one-writer)."
            ),
        },
        "heartbeat_staleness": {
            "shape": (
                "cosmos_clock.write_heartbeat always stamps last_run_epoch. "
                "poll_once writes at tick start, again as tick=busy before "
                "the rail, and at end (idle/drained/paused). FRESH_S=90s."
            ),
            "open": (
                "last_run_epoch is int seconds — two polls in the same second "
                "are not a monotonic bump. A rail longer than FRESH_S still "
                "looks alive because busy is written first; a hung rail "
                "after busy with a dead pid is indistinguishable from a "
                "long call until FRESH_S elapses. No secret material is "
                "copied into the heartbeat (worker_id/pid/paths only)."
            ),
        },
        "secret_handling": {
            "done": (
                "No API keys in heartbeat, fence, or result. install_key.bin "
                "is read as bytes for the ledger client and never logged. "
                "No bts_* import. dest GDX/ODX paths come from "
                "live/config/node_bucket_worker.json (gitignored runtime), "
                "not from this module as identity."
            ),
            "open": (
                "rail.text is the model answer and may contain user content; "
                "it is written to live/returns (and GDX/ODX if configured). "
                "That is the designated folder, not a secret store — still "
                "not a place for keys. Keith's credentialing remains "
                "open-window handoff; this worker never opens one."
            ),
        },
        "bloat": {
            "subtracted": (
                "No cosmos_dispatch import, no DHx marker, no collector "
                "index write, no execute_handoff, no OA node, no standup "
                "that calls create_task. Register helper has zero "
                "create_task/run_schtasks calls."
            ),
            "known_dup": (
                "pause_flag is still local (node_worker and crit_consumer "
                "each have a copy). Moving it to cosmos_clock would touch "
                "a shared file outside NEW-files scope. Next iteration."
            ),
        },
    }


def run() -> int:
    for name in ("cosmos_node_bucket_worker.py", "register_node_workers.py"):
        src = (COSMOS_DIR / name).read_text(encoding="utf-8")
        check(f"{name} imports no bts_*", lambda s=src: not BTS_IMPORT.search(s))

    reg_src = (COSMOS_DIR / "register_node_workers.py").read_text(encoding="utf-8")
    check("register helper does not call create_task",
          lambda: "create_task(" not in reg_src)
    check("register helper does not call run_schtasks",
          lambda: "run_schtasks(" not in reg_src)

    check("grok task name",
          lambda: NODES["grok"]["task_name"] == "COSMOS Grok Worker")
    check("gem task name",
          lambda: NODES["gem"]["task_name"] == "COSMOS GEM Worker")
    check("g46 aliases to grok", lambda: canon_node("g46") == "grok")
    check("gemini aliases to gem", lambda: canon_node("gemini") == "gem")
    # The heartbeat NAME only. Every path below resolves under the tempdir root
    # installed in main(); tests/test_live_write_fence.py proves by syscall that
    # this suite never writes the live runtime root -- a test that can freshen a
    # production heartbeat makes heartbeat age forgeable.
    check("heartbeat name is <runtime>/logs/<node>_heartbeat.json",
          lambda: NODES["grok"]["heartbeat"] == "grok_heartbeat.json"
          and NODES["gem"]["heartbeat"] == "gem_heartbeat.json")

    td = Path(tempfile.mkdtemp(prefix="cosmos_node_bucket_"))
    root = install(td / "live", tree_id="spike-node-bucket")
    paths = CosmosPaths(root)
    grok_bucket = bucket_dir(paths, "grok")
    gem_bucket = bucket_dir(paths, "gem")

    check("grok bucket is live/buckets/grok",
          lambda: grok_bucket == paths.root / "buckets" / "grok")
    check("gem bucket is live/buckets/gem",
          lambda: gem_bucket == paths.root / "buckets" / "gem")
    check("V returns is live/returns/grok",
          lambda: v_returns(paths, "grok") == paths.root / "returns" / "grok")

    drop = grok_bucket / "pong.json"
    _write(drop, json.dumps({
        "prompt": "Reply with the single word PONG.",
        "out": "V",
        "id": "proof-pong",
    }))
    parsed = parse_task(drop)
    check("json drop parses prompt + out V",
          lambda: parsed["prompt"].startswith("Reply") and parsed["out"] == "V")

    # ---- HOLD: pick up NOTHING, heartbeat still written ----
    pause_p = paths.state("control", "PAUSE.flag")
    _write(pause_p, json.dumps({
        "state": "PAUSED", "mode": "hold", "reason": "selftest",
        "set_by": "test",
    }))
    held = poll_once(str(root), "grok", rail_call=_fake_grok,
                     worker_id="grok-test-hold")
    check("HOLD is detected", lambda: pause_flag(paths) is not None)
    check("HOLD decision does not drain",
          lambda: pause_decision(pause_flag(paths))["drain"] is False
          and pause_decision(pause_flag(paths))["mode"] == "hold")
    check("HOLD heartbeat is PAUSED",
          lambda: held.get("state") == "PAUSED" and held.get("tick") == "paused")
    check("HOLD idle picks up NOTHING",
          lambda: drop.exists() and held.get("picked_this_tick") == 0)
    check("grok heartbeat file emitted while paused",
          lambda: paths.logs("grok_heartbeat.json").exists())
    hb_hold = json.loads(paths.logs("grok_heartbeat.json").read_text(
        encoding="utf-8"))
    check("HOLD heartbeat has last_run_epoch",
          lambda: isinstance(hb_hold.get("last_run_epoch"), int))
    check("HOLD heartbeat carries worker_id",
          lambda: hb_hold.get("worker_id") == "grok-test-hold")

    # ---- RESUME-GATE in the future: still paused ----
    future = (datetime.now().astimezone() + timedelta(hours=1)).isoformat()
    _write(pause_p, json.dumps({
        "state": "PAUSED", "mode": "resume_gate",
        "auto_resume_at": future, "reason": "bootup gate",
        "set_by": "test",
    }))
    gated = poll_once(str(root), "grok", rail_call=_fake_grok,
                      worker_id="grok-test-gate")
    check("future RESUME-GATE picks up NOTHING",
          lambda: drop.exists() and gated.get("picked_this_tick") == 0
          and gated.get("state") == "PAUSED")

    # ---- expired RESUME-GATE: drains (WD2 owns deleting the flag) ----
    past = (datetime.now().astimezone() - timedelta(seconds=30)).isoformat()
    _write(pause_p, json.dumps({
        "state": "PAUSED", "mode": "resume_gate",
        "auto_resume_at": past, "reason": "bootup gate expired",
        "set_by": "test",
    }))
    rec = poll_once(str(root), "grok", rail_call=_fake_grok,
                    worker_id="grok-test-wid")
    check("expired RESUME-GATE drains",
          lambda: rec.get("picked_this_tick") == 1
          and rec.get("pause_expired") is True)
    check("exactly one worker-id claimed the task",
          lambda: rec.get("claimed_by") == ["grok-test-wid"]
          and rec["jobs"][0]["worker_id"] == "grok-test-wid")
    job = rec["jobs"][0]
    v_path = Path(job["v_path"])
    check("V result file exists", lambda: v_path.is_file())
    body = json.loads(v_path.read_text(encoding="utf-8"))
    check("result bound to rail model",
          lambda: body["rail"]["model"] == "fake-grok")
    check("result bound to spend usd",
          lambda: body["rail"]["usd"] == 0.004)
    check("result bound to link_id sgh-api",
          lambda: body["rail"]["link_id"] == "sgh-api")
    check("result text is the real rail answer",
          lambda: body["rail"]["text"] == "PONG")
    check("result worker_id matches claimer",
          lambda: body.get("worker_id") == "grok-test-wid")
    check("O_EXCL fence file exists for the drop",
          lambda: Path(job["fence_path"]).is_file()
          if job.get("fence_path") else False)
    fence = json.loads(Path(job["fence_path"]).read_text(encoding="utf-8"))
    check("fence worker_id is the unique claimer",
          lambda: fence.get("worker_id") == "grok-test-wid")
    check("drop staged to processed (never deleted)",
          lambda: not drop.exists()
          and list((grok_bucket / "processed").glob("*pong.json")))

    LIVE_VALUE["claimed_by"] = "grok-test-wid"
    LIVE_VALUE["claimers"] = rec.get("claimed_by")
    LIVE_VALUE["result_path"] = str(v_path)
    LIVE_VALUE["result_worker_id"] = body.get("worker_id")
    LIVE_VALUE["fence_path"] = job.get("fence_path")
    LIVE_VALUE["heartbeat_path"] = rec.get("heartbeat_path")
    LIVE_VALUE["last_run_epoch"] = rec.get("heartbeat", {}).get("last_run_epoch")

    # ---- O_EXCL: two threads, one winner ----
    race = grok_bucket / "race.json"
    _write(race, json.dumps({"prompt": "race", "id": "race-1", "out": "V"}))
    got: list = [None, None]

    def _claim(i, wid):
        got[i] = claim_drop(grok_bucket, race, wid)

    t1 = threading.Thread(target=_claim, args=(0, "grok-race-a"))
    t2 = threading.Thread(target=_claim, args=(1, "grok-race-b"))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    winners = [g for g in got if g is not None]
    check("O_EXCL two threads: exactly one winner",
          lambda: len(winners) == 1)
    check("O_EXCL winner carries one worker_id",
          lambda: winners[0]["worker_id"] in ("grok-race-a", "grok-race-b"))
    LIVE_VALUE["oexcl_winners"] = len(winners)
    LIVE_VALUE["oexcl_worker_id"] = winners[0]["worker_id"] if winners else None

    # leftover running/race.json — stage it out so it is not a drop
    running_race = grok_bucket / "running" / "race.json"
    if running_race.exists():
        running_race.replace(grok_bucket / "processed" / "race.json")

    # ---- gem own bucket ----
    gem_drop = gem_bucket / "gem_pong.json"
    _write(gem_drop, json.dumps({"prompt": "Reply PONG.", "out": "V",
                                 "id": "gem-proof"}))
    grec = poll_once(str(root), "gem", rail_call=_fake_gem,
                     worker_id="gem-test-wid")
    check("gem --once drains its own bucket",
          lambda: grec.get("picked_this_tick") == 1)
    gjob = grec["jobs"][0]
    gpath = Path(gjob["v_path"])
    check("gem result landed under live/returns/gem",
          lambda: gpath.is_file()
          and gpath.parent.name == "gem"
          and gpath.parent.parent.name == "returns")
    gbody = json.loads(gpath.read_text(encoding="utf-8"))
    check("gem result bound to gem-api",
          lambda: gbody["rail"]["link_id"] == "gem-api"
          and gbody["rail"]["model"] == "fake-gemini")
    check("gem result worker_id is gem-test-wid",
          lambda: gbody.get("worker_id") == "gem-test-wid")
    check("gem heartbeat file emitted",
          lambda: paths.logs("gem_heartbeat.json").exists())
    check("grok worker does not pick gem drops",
          lambda: list_drop_files(gem_bucket) == [])

    stray = gem_bucket / "stray.json"
    _write(stray, json.dumps({"prompt": "leave me", "out": "V"}))
    poll_once(str(root), "grok", rail_call=_fake_grok,
              worker_id="grok-no-gem")
    check("grok poll leaves gem stray drop untouched",
          lambda: stray.exists())

    check("dest V resolves under the runtime root",
          lambda: dest_dir(paths, "grok", "V") == paths.root / "returns" / "grok")

    # ---- monotonic heartbeat epoch (idle ticks) ----
    e1 = poll_once(str(root), "grok", rail_call=_fake_grok,
                   worker_id="grok-mono")
    epoch1 = int(e1["heartbeat"]["last_run_epoch"])
    time.sleep(1.05)
    e2 = poll_once(str(root), "grok", rail_call=_fake_grok,
                   worker_id="grok-mono")
    epoch2 = int(e2["heartbeat"]["last_run_epoch"])
    check("idle poll still writes last_run_epoch",
          lambda: e2.get("tick") == "idle" and e2.get("picked_this_tick") == 0)
    check("heartbeat last_run_epoch is monotonic across polls",
          lambda: epoch2 > epoch1)
    LIVE_VALUE["heartbeat_epochs"] = [epoch1, epoch2]
    LIVE_VALUE["monotonic"] = epoch2 > epoch1

    # ---- register helper emits /Create, does not run it ----
    planned = plan(str(root))
    check("register plan ran_schtasks is False",
          lambda: planned.get("ran_schtasks") is False
          and planned.get("emit_only") is True)
    check("register plan has grok and gem nodes",
          lambda: [n["node"] for n in planned["nodes"]] == ["grok", "gem"])
    grok_tr = planned["nodes"][0]["tr"]
    gem_tr = planned["nodes"][1]["tr"]
    check("grok TR is --node grok --loop",
          lambda: "--node" in grok_tr and "grok" in grok_tr and "--loop" in grok_tr)
    check("gem TR is --node gem --loop",
          lambda: "--node" in gem_tr and "gem" in gem_tr and "--loop" in gem_tr)
    check("minute plan is schtasks /create /sc minute",
          lambda: planned["nodes"][0]["minute"][:3] == ["schtasks", "/create", "/tn"]
          and "minute" in planned["nodes"][0]["minute"])
    check("logon plan is schtasks /create /sc onlogon",
          lambda: "onlogon" in planned["nodes"][0]["logon"])
    kcmd = keith_cmd(str(root))
    check("keith_cmd is one elevated line covering both daemons",
          lambda: kcmd.count("schtasks") == 4
          and "COSMOS Grok Worker" in kcmd
          and "COSMOS GEM Worker" in kcmd
          and " & " in kcmd)
    LIVE_VALUE["keith_cmd_preview"] = kcmd[:180]

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    failed = [(lab, err) for lab, ok, err in RESULTS if not ok]
    print(f"test_node_bucket_worker {passed}/{len(RESULTS)}")
    for lab, err in failed:
        print(f"  FAIL {lab} {err}")
    LIVE_VALUE["selftest"] = f"{passed}/{len(RESULTS)}"
    LIVE_VALUE["stage5"] = stage5_critique()
    print("LIVE_VALUE " + json.dumps(LIVE_VALUE, default=str))
    return 0 if not failed else 2


def main() -> int:
    from cosmos_test_guard import sandbox_heartbeats
    with sandbox_heartbeats():
        return run()


if __name__ == "__main__":
    raise SystemExit(main())
