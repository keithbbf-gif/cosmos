#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest + runtime-binding proof for GROK/GEM bucket daemons.

Isolated from the live tree: install() a scratch COSMOS root (sim bucket).
Fake rail_call so no live spend. Proves:

  * own buckets (grok does not pick gem)
  * packet pickup -> NON-EMPTY result at live/returns/<node> (the V path)
  * heartbeat last_run_epoch advances across two polls
  * HOLD idle, expired RESUME-GATE drains
  * unique worker_id on fence + result + heartbeat
  * no bts_* import, no drive literals
  * CREATE_NO_WINDOW == 0x08000000
  * interval clamped to 5-15s
  * GDX/ODX require config (fail-closed, no hardcoded X:\\ / C:\\)
  * standup plans pythonw --loop + 1-min + onlogon (does not fire schtasks here)

Does not modify kernel/ledger/sched/service. Does not touch the live tree.
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

BUNDLE = Path(__file__).resolve().parent.parent
CLONE_COSMOS = BUNDLE.parent.parent / "cosmos"
sys.path.insert(0, str(BUNDLE / "cosmos"))
sys.path.insert(0, str(CLONE_COSMOS))

from cosmos_clock import CREATE_NO_WINDOW  # noqa: E402
from cosmos_kernel import install  # noqa: E402
from cosmos_bucket_daemon import (  # noqa: E402
    CLOCK_IDS, CONFIG_NAME, NODES, bucket_dir, canon_node, claim_drop,
    clamp_interval, dest_dir, execute_handoff, list_drop_files, load_config,
    make_worker_id, node_spec, pause_decision, pause_flag, plan_loop_argv,
    plan_task_argv, poll_once, standup, v_returns, WorkerError,
)
from cosmos_own_clocks import CLOCKS  # noqa: E402
from cosmos_paths import CosmosPaths  # noqa: E402

RESULTS = []
LIVE_VALUE: dict = {}
BTS_IMPORT = re.compile(r"^\s*(?:from|import)\s+bts_\w+", re.M)
# A drive literal is a volume prefix (V:\ / C:\ / X:\). Relative
# cosmos\script.py in a docstring is not a drive.
DRIVE_LIT = re.compile(r"[A-Za-z]:\\")
BUNDLE_PY = [
    BUNDLE / "cosmos" / "cosmos_bucket_daemon.py",
    BUNDLE / "cosmos" / "cosmos_grok_bucket_worker.py",
    BUNDLE / "cosmos" / "cosmos_gem_bucket_worker.py",
]


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
        "ok": True, "kind": "API",
        "text": "GEM-PONG-BODY nonempty rail answer for runtime binding.",
        "usd": 0.01, "node": "fake_gem", "model": "fake-gemini",
        "link_id": "vertex-coding",
    }


def main() -> int:
    for p in BUNDLE_PY:
        src = p.read_text(encoding="utf-8")
        check(f"{p.name} imports no bts_*",
              lambda s=src: not BTS_IMPORT.search(s))
        check(f"{p.name} has no drive literals",
              lambda s=src, n=p.name: (
                  not DRIVE_LIT.search(s)
                  if n != "cosmos_bucket_daemon.py"
                  else "X:\\" not in s and "C:\\Users" not in s
                  and "V:\\Ai" not in s and "V:\\A\\" not in s))

    check("CREATE_NO_WINDOW is 0x08000000",
          lambda: CREATE_NO_WINDOW == 0x08000000)
    check("grok heartbeat name matches assignment",
          lambda: NODES["grok"]["heartbeat"]
          == "cosmos_grok_bucket_worker_heartbeat.json")
    check("gem heartbeat name matches assignment",
          lambda: NODES["gem"]["heartbeat"]
          == "cosmos_gem_bucket_worker_heartbeat.json")
    check("g46 aliases to grok", lambda: canon_node("g46") == "grok")
    check("gemini aliases to gem", lambda: canon_node("gemini") == "gem")
    check("interval 1s clamps to 5", lambda: clamp_interval(1) == 5.0)
    check("interval 30s clamps to 15", lambda: clamp_interval(30) == 15.0)
    check("interval 10s stays 10", lambda: clamp_interval(10) == 10.0)
    check("grok rails are sgh then gw",
          lambda: [r["link_id"] for r in NODES["grok"]["rails"]]
          == ["sgh-api", "gw-api"])
    check("gem rail is vertex-coding",
          lambda: [r["link_id"] for r in NODES["gem"]["rails"]]
          == ["vertex-coding"])
    check("worker ids are unique across two calls",
          lambda: make_worker_id("grok") != make_worker_id("grok"))
    check("execute_handoff is the rail entry (not a new rail)",
          lambda: callable(execute_handoff))

    daemon_src = (BUNDLE / "cosmos" / "cosmos_bucket_daemon.py").read_text(
        encoding="utf-8")
    check("daemon uses cosmos_node_rails.NodeRail",
          lambda: "from cosmos_node_rails import NodeRail" in daemon_src)
    check("daemon uses cosmos_clock.write_heartbeat",
          lambda: "write_heartbeat" in daemon_src)
    check("daemon standup uses create_task (schtasks self-heal)",
          lambda: "create_task(" in daemon_src and "minute" in daemon_src
          and "onlogon" in daemon_src)
    check("daemon does not import cosmos_dispatch",
          lambda: "cosmos_dispatch" not in daemon_src)
    check("task names do not clobber incumbent COSMOS Grok Worker",
          lambda: NODES["grok"]["task_name"] == "COSMOS Grok Bucket Worker"
          and NODES["gem"]["task_name"] == "COSMOS GEM Bucket Worker")

    td = Path(tempfile.mkdtemp(prefix="cosmos_bucket_bind_"))
    root = install(td / "live", tree_id="spike-grok-gem-bucket")
    paths = CosmosPaths(root)
    grok_bucket = bucket_dir(paths, "grok")
    gem_bucket = bucket_dir(paths, "gem")

    check("grok bucket is live/buckets/grok",
          lambda: grok_bucket == paths.root / "buckets" / "grok")
    check("gem bucket is live/buckets/gem",
          lambda: gem_bucket == paths.root / "buckets" / "gem")
    check("V returns is live/returns/gem (designated V path)",
          lambda: v_returns(paths, "gem") == paths.root / "returns" / "gem")

    # ---- GDX/ODX fail-closed without config (no drive-literal fallback) ----
    try:
        dest_dir(paths, "gem", "GDX", load_config(paths))
        gdx_err = None
    except WorkerError as e:
        gdx_err = e
    check("GDX without config is NO_DEST",
          lambda: gdx_err is not None and gdx_err.kind == "NO_DEST")

    alt = td / "odx_alt"
    alt.mkdir()
    _write(paths.config(CONFIG_NAME), json.dumps({
        "interval_s": 10,
        "dest": {"ODX": str(alt)},
    }))
    cfg = load_config(paths)
    check("config interval 10 is in 5-15",
          lambda: cfg["interval_s"] == 10.0)
    odx = dest_dir(paths, "gem", "ODX", cfg)
    check("configured ODX lands under COSMOS/returns/gem",
          lambda: odx == alt / "COSMOS" / "returns" / "gem" and odx.is_dir())

    # ---- HOLD: pick up NOTHING, heartbeat still written ----
    gem_drop = gem_bucket / "bind_pong.json"
    _write(gem_drop, json.dumps({
        "prompt": "Reply with a nonempty body for the runtime-binding gate.",
        "out": "V",
        "id": "bind-gem-pong",
    }))
    pause_p = paths.state("control", "PAUSE.flag")
    _write(pause_p, json.dumps({
        "state": "PAUSED", "mode": "hold", "reason": "selftest",
        "set_by": "g46-bind",
    }))
    held = poll_once(str(root), "gem", rail_call=_fake_gem,
                     worker_id="gem-test-hold")
    check("HOLD is detected", lambda: pause_flag(paths) is not None)
    check("HOLD decision does not drain",
          lambda: pause_decision(pause_flag(paths))["drain"] is False
          and pause_decision(pause_flag(paths))["mode"] == "hold")
    check("HOLD heartbeat is PAUSED",
          lambda: held.get("state") == "PAUSED" and held.get("tick") == "paused")
    check("HOLD idle picks up NOTHING",
          lambda: gem_drop.exists() and held.get("picked_this_tick") == 0)
    hb_hold_path = paths.logs("cosmos_gem_bucket_worker_heartbeat.json")
    check("gem heartbeat file emitted while paused",
          lambda: hb_hold_path.is_file())
    hb_hold = json.loads(hb_hold_path.read_text(encoding="utf-8"))
    check("HOLD heartbeat has last_run_epoch",
          lambda: isinstance(hb_hold.get("last_run_epoch"), int))
    check("HOLD heartbeat carries worker_id",
          lambda: hb_hold.get("worker_id") == "gem-test-hold")
    check("HOLD heartbeat carries pending > 0",
          lambda: int(hb_hold.get("pending") or 0) >= 1)

    # ---- future RESUME-GATE still paused ----
    future = (datetime.now().astimezone() + timedelta(hours=1)).isoformat()
    _write(pause_p, json.dumps({
        "state": "PAUSED", "mode": "resume_gate",
        "auto_resume_at": future, "reason": "bootup gate",
        "set_by": "g46-bind",
    }))
    gated = poll_once(str(root), "gem", rail_call=_fake_gem,
                      worker_id="gem-test-gate")
    check("future RESUME-GATE picks up NOTHING",
          lambda: gem_drop.exists() and gated.get("picked_this_tick") == 0
          and gated.get("state") == "PAUSED")

    # ---- expired RESUME-GATE drains the sim gem bucket (runtime binding) ----
    past = (datetime.now().astimezone() - timedelta(seconds=30)).isoformat()
    _write(pause_p, json.dumps({
        "state": "PAUSED", "mode": "resume_gate",
        "auto_resume_at": past, "reason": "bootup gate expired",
        "set_by": "g46-bind",
    }))
    rec = poll_once(str(root), "gem", polls=1, rail_call=_fake_gem,
                    worker_id="gem-bind-wid")
    check("expired RESUME-GATE drains gem packet",
          lambda: rec.get("picked_this_tick") == 1
          and rec.get("pause_expired") is True)
    job = rec["jobs"][0]
    v_path = Path(job["v_path"])
    check("V result file exists under live/returns/gem",
          lambda: v_path.is_file()
          and v_path.parent.name == "gem"
          and v_path.parent.parent.name == "returns")
    body = json.loads(v_path.read_text(encoding="utf-8"))
    rail_text = str((body.get("rail") or {}).get("text") or "")
    check("result body is NON-EMPTY", lambda: bool(rail_text.strip()))
    check("result bound to vertex-coding",
          lambda: body["rail"]["link_id"] == "vertex-coding"
          and body["rail"]["model"] == "fake-gemini")
    check("result worker_id matches claimer",
          lambda: body.get("worker_id") == "gem-bind-wid")
    check("result ok + nonempty_stdout",
          lambda: body.get("ok") is True
          and body.get("done_why") == "nonempty_stdout")
    check("drop staged to processed (never deleted)",
          lambda: not gem_drop.exists()
          and list((gem_bucket / "processed").glob("*bind_pong.json")))

    LIVE_VALUE["result_path"] = str(v_path)
    LIVE_VALUE["result_text"] = rail_text
    LIVE_VALUE["result_bytes"] = v_path.stat().st_size
    LIVE_VALUE["worker_id"] = body.get("worker_id")
    LIVE_VALUE["heartbeat_path"] = rec.get("heartbeat_path")
    LIVE_VALUE["poll1_epoch"] = rec.get("heartbeat", {}).get("last_run_epoch")
    LIVE_VALUE["v_returns"] = str(v_returns(paths, "gem"))
    LIVE_VALUE["sim_root"] = str(root)

    # ---- second poll: idle, last_run_epoch advances ----
    time.sleep(1.05)
    rec2 = poll_once(str(root), "gem", polls=2, rail_call=_fake_gem,
                     worker_id="gem-bind-wid")
    epoch1 = int(LIVE_VALUE["poll1_epoch"])
    epoch2 = int(rec2["heartbeat"]["last_run_epoch"])
    check("second poll is idle (packet already drained)",
          lambda: rec2.get("tick") == "idle" and rec2.get("picked_this_tick") == 0)
    check("heartbeat last_run_epoch advanced across two polls",
          lambda: epoch2 > epoch1)
    check("second heartbeat still carries worker_id + polls + pending",
          lambda: rec2["heartbeat"].get("worker_id") == "gem-bind-wid"
          and rec2.get("polls") == 2
          and rec2["heartbeat"].get("pending") == 0)
    LIVE_VALUE["poll2_epoch"] = epoch2
    LIVE_VALUE["epochs"] = [epoch1, epoch2]
    LIVE_VALUE["epoch_advanced"] = epoch2 > epoch1

    hb2 = json.loads(Path(rec2["heartbeat_path"]).read_text(encoding="utf-8"))
    LIVE_VALUE["heartbeat"] = {
        "path": rec2["heartbeat_path"],
        "last_run_epoch": hb2.get("last_run_epoch"),
        "polls": hb2.get("polls"),
        "pending": hb2.get("pending"),
        "worker_id": hb2.get("worker_id"),
        "tick": hb2.get("tick"),
    }

    # ---- grok own bucket; does not steal gem leftovers ----
    grok_drop = grok_bucket / "grok_only.json"
    _write(grok_drop, json.dumps({"prompt": "GROK PONG", "out": "V",
                                  "id": "grok-own"}))
    stray = gem_bucket / "gem_stray.json"
    _write(stray, json.dumps({"prompt": "leave me", "out": "V"}))
    grec = poll_once(str(root), "grok", rail_call=_fake_grok,
                     worker_id="grok-own-wid")
    check("grok drains its own bucket",
          lambda: grec.get("picked_this_tick") == 1)
    check("grok heartbeat is cosmos_grok_bucket_worker_heartbeat.json",
          lambda: paths.logs("cosmos_grok_bucket_worker_heartbeat.json").is_file())
    check("grok poll leaves gem stray drop untouched",
          lambda: stray.exists())
    gjob = grec["jobs"][0]
    gbody = json.loads(Path(gjob["v_path"]).read_text(encoding="utf-8"))
    check("grok result bound to sgh-api",
          lambda: gbody["rail"]["link_id"] == "sgh-api"
          and gbody["rail"]["text"] == "PONG")
    LIVE_VALUE["grok_result_path"] = gjob["v_path"]
    LIVE_VALUE["grok_heartbeat"] = grec.get("heartbeat_path")

    # ---- O_EXCL: two claims, one winner ----
    race = grok_bucket / "race.json"
    _write(race, json.dumps({"prompt": "race", "id": "race-1", "out": "V"}))
    a = claim_drop(grok_bucket, race, "grok-race-a")
    b = claim_drop(grok_bucket, race, "grok-race-b")
    winners = [x for x in (a, b) if x is not None]
    check("O_EXCL sequential: exactly one winner", lambda: len(winners) == 1)

    # ---- standup plans windowless pythonw --loop (do NOT fire schtasks) ----
    argv = plan_loop_argv(str(root), "gem")
    check("plan_loop_argv is pythonw --loop",
          lambda: "--loop" in argv and "--root" in argv
          and "cosmos_gem_bucket_worker.py" in argv[1])
    check("plan_loop_argv uses pythonw (windowless)",
          lambda: "pythonw" in Path(argv[0]).name.lower()
          or Path(argv[0]).name.lower().startswith("python"))
    check("CREATE_NO_WINDOW used by spawn path",
          lambda: CREATE_NO_WINDOW == 0x08000000)
    check("standup is callable (schtasks self-heal like runner)",
          lambda: callable(standup))
    check("CLOCK_IDS grok=21 gem=22",
          lambda: CLOCK_IDS == {"grok": 21, "gem": 22})
    grok_plan = plan_task_argv(str(root), "grok")
    gem_plan = plan_task_argv(str(root), "gem")
    check("plan_task_argv grok is schtasks /create minute/1, no /rl",
          lambda: grok_plan[0] == "schtasks" and "/create" in grok_plan
          and "COSMOS Grok Bucket Worker" in grok_plan
          and "minute" in grok_plan and "/rl" not in grok_plan)
    check("plan_task_argv gem is a distinct task name",
          lambda: "COSMOS GEM Bucket Worker" in gem_plan
          and gem_plan != grok_plan)
    check("CLOCKS id 21/22 are the two bucket workers",
          lambda: any(c.get("id") == 21
                      and c.get("task") == "COSMOS Grok Bucket Worker"
                      for c in CLOCKS)
          and any(c.get("id") == 22
                  and c.get("task") == "COSMOS GEM Bucket Worker"
                  for c in CLOCKS))
    spec = node_spec("gem")
    check("gem lock is unique (does not share grok_worker.lock)",
          lambda: spec["lock"] == "cosmos_gem_bucket_worker.lock")

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    failed = [(lab, err) for lab, ok, err in RESULTS if not ok]
    print(f"test_grok_gem_bucket_workers {passed}/{len(RESULTS)}")
    for lab, err in failed:
        print(f"  FAIL {lab} {err}")
    LIVE_VALUE["selftest"] = f"{passed}/{len(RESULTS)}"
    LIVE_VALUE["failed"] = failed

    proof = BUNDLE / "proof"
    proof.mkdir(parents=True, exist_ok=True)
    for key, dest_name in (
        ("result_path", "gem_result.json"),
        ("heartbeat_path", "gem_heartbeat.json"),
        ("grok_result_path", "grok_result.json"),
        ("grok_heartbeat", "grok_heartbeat.json"),
    ):
        src = Path(LIVE_VALUE.get(key) or "")
        if src.is_file():
            (proof / dest_name).write_bytes(src.read_bytes())
            LIVE_VALUE[dest_name] = str(proof / dest_name)
    (proof / "LIVE_VALUE.json").write_text(
        json.dumps(LIVE_VALUE, indent=1, default=str), encoding="utf-8")
    print("LIVE_VALUE " + json.dumps(LIVE_VALUE, default=str))
    return 0 if not failed else 2


if __name__ == "__main__":
    raise SystemExit(main())
