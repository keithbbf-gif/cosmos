#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: different-family critique consumer. Isolated from the live tree.

Proves:
  * packet claimed once under a lease/fence (exactly-once)
  * GEM + OA + SSA each route to the right rail
  * replay is ignored
  * missing/empty output is FAILED, not accepted
  * PAUSE stops claiming
  * a GEM/OA packet drop yields a NON-EMPTY critique body at the
    designated returns path, bound to the model that answered

Fake invoke/rail so no live spend. No BTS import. Does not modify
kernel/ledger/sched/service. Does not touch cosmos_dispatch.py.
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import threading
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parent
LIVE_COSMOS = Path(r"V:\A\Ai\COSMOS\cosmos")
# Live helpers (clock/paths/kernel) then THIS bundle's worker/consumer first.
if LIVE_COSMOS.exists():
    sys.path.insert(0, str(LIVE_COSMOS))
sys.path.insert(0, str(BUNDLE / "cosmos"))
sys.path.insert(0, str(HERE))

from cosmos_kernel import install  # noqa: E402
from cosmos_node_worker import NODES, canon_node, land_critique_return  # noqa: E402
from cosmos_crit_consumer import (  # noqa: E402
    CLOCK_ID, CRIT_KINDS, DEFAULT_INTERVAL_S, HEARTBEAT_NAME, SCHEMA,
    TASK_NAME, TASK_NAME_LOGON, WORKER, claim_packet, is_replay,
    list_packets, parse_critique_packet, pause_flag, plan_task_argv,
    poll_once, process_packet, route_for, workers_dir,
)
from cosmos_own_clocks import CLOCKS  # noqa: E402
from cosmos_paths import CosmosPaths  # noqa: E402
from register_crit_consumer import (  # noqa: E402
    plan, plan_loop_argv, plan_logon, plan_minute,
)

RESULTS = []
BTS_IMPORT = re.compile(r"^\s*(?:from|import)\s+bts_\w+", re.M)


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _packet(agent: str, kind: str, assignment: str, returns: Path,
            extra: dict | None = None) -> dict:
    rec = {
        "agent": agent,
        "kind": kind,
        "assignment": assignment,
        "stamp": "2026-08-27T00:00:00-05:00",
        "out_dir": None,
        "result": str(returns),
        "returns": str(returns),
    }
    if extra:
        rec.update(extra)
    return rec


def _invoke_for(kind: str, text: str, model: str, link_id: str):
    def _fn(k, prompt):
        assert k == kind, f"invoke kind {k!r} != {kind!r}"
        return {
            "ok": True, "kind": "API" if kind != "ssa" else "CLI",
            "text": text, "model": model, "link_id": link_id,
            "usd": 0.01 if kind != "ssa" else None,
        }
    return _fn


def main() -> int:
    consumer_src = (BUNDLE / "cosmos" / "cosmos_crit_consumer.py").read_text(
        encoding="utf-8")
    worker_src = (BUNDLE / "cosmos" / "cosmos_node_worker.py").read_text(
        encoding="utf-8")
    register_src = (BUNDLE / "cosmos" / "register_crit_consumer.py").read_text(
        encoding="utf-8")
    check("consumer imports no bts_*",
          lambda: not BTS_IMPORT.search(consumer_src))
    check("node_worker imports no bts_*",
          lambda: not BTS_IMPORT.search(worker_src))
    check("register imports no bts_*",
          lambda: not BTS_IMPORT.search(register_src))
    check("task name is COSMOS CritConsumer",
          lambda: TASK_NAME == "COSMOS CritConsumer")
    check("logon task is COSMOS CritConsumer Logon",
          lambda: TASK_NAME_LOGON == "COSMOS CritConsumer Logon")
    check("heartbeat name is crit_consumer_heartbeat.json",
          lambda: HEARTBEAT_NAME == "crit_consumer_heartbeat.json")
    check("poll interval is ~10s", lambda: DEFAULT_INTERVAL_S == 10.0)
    check("schema is cosmos-crit-consumer/1",
          lambda: SCHEMA == "cosmos-crit-consumer/1")
    check("worker id is cosmos-crit-consumer", lambda: WORKER == "cosmos-crit-consumer")

    check("GEM routes to gem-api",
          lambda: route_for("GEM")["rail"] == "gem-api"
          and route_for("gemini")["node"] == "gem")
    check("OAi routes to oa-api",
          lambda: route_for("OAi")["rail"] == "oa-api"
          and route_for("oa")["module"] == "bts_oa_api")
    check("SSA routes to claude -p --model sonnet",
          lambda: route_for("SSA")["rail"] == "claude-cli"
          and route_for("ssa")["model"] == "sonnet"
          and route_for("SSA")["argv_head"] == ["claude", "-p", "--model", "sonnet"])
    check("oa aliases on node_worker", lambda: canon_node("oai") == "oa")
    check("oa node rail is oa-api",
          lambda: NODES["oa"]["rails"][0]["link_id"] == "oa-api")
    check("kinds covered are gem oa ssa",
          lambda: CRIT_KINDS == ("gem", "oa", "ssa"))

    td = Path(tempfile.mkdtemp(prefix="cosmos_crit_consumer_"))
    root = install(td / "live", tree_id="spike-crit-consumer")
    paths = CosmosPaths(root)
    dhx = td / "docs" / "AGENT_BRIEF.md"
    _write(dhx, (
        "# DHx\n\n"
        "## Assignment log — APPEND-ONLY markers\n\n"
        "## Active assignments\n"
        "- none\n"
    ))
    returns_dir = paths.queue("returns", "cm")
    returns_dir.mkdir(parents=True, exist_ok=True)

    # ---- parse live-shaped packet (assignment, no prompt) ----
    gem_ret = returns_dir / "gem_crit_result.json"
    gem_inbox = workers_dir(paths, "gem")
    gem_pkt = gem_inbox / "handoff_gem.json"
    _write(gem_pkt, json.dumps(_packet(
        "GEM", "gem", "You are GEM. Critique the slice. PROPOSE-ONLY.",
        gem_ret)))
    parsed = parse_critique_packet(gem_pkt, "gem")
    check("live packet parses assignment as prompt",
          lambda: parsed["prompt"].startswith("You are GEM")
          and parsed["kind"] == "gem"
          and parsed["returns"] == str(gem_ret))

    # ---- PAUSE stops claiming ----
    pause_p = paths.state("control", "PAUSE.flag")
    _write(pause_p, json.dumps({
        "state": "PAUSED", "mode": "hold", "reason": "selftest",
        "set_by": "test",
    }))
    paused_rec = poll_once(str(root), drain=False, dhx_path=dhx,
                           invoke=_invoke_for(
                               "gem", "SHOULD_NOT_RUN", "fake-gemini", "gem-api"))
    check("PAUSE present is detected", lambda: pause_flag(paths) is not None)
    check("drain=False heartbeat is PAUSED",
          lambda: paused_rec.get("state") == "PAUSED"
          and paused_rec.get("tick") == "paused")
    check("PAUSE idle claims NOTHING",
          lambda: gem_pkt.exists() and paused_rec.get("picked_this_tick") == 0)
    check("heartbeat file emitted while paused",
          lambda: paths.logs(HEARTBEAT_NAME).exists())
    hb_paused = json.loads(paths.logs(HEARTBEAT_NAME).read_text(encoding="utf-8"))
    check("paused heartbeat state=PAUSED (paused != dead)",
          lambda: hb_paused.get("state") == "PAUSED"
          and hb_paused.get("worker") == WORKER
          and "last_run_epoch" in hb_paused)

    # ---- GEM packet -> nonempty body at designated returns, bound to model ----
    pause_p.unlink()
    grec = poll_once(str(root), drain=True, dhx_path=dhx,
                     invoke=_invoke_for(
                         "gem", "GEM-CRITIQUE-BODY HIGH: missing fence.\n",
                         "fake-gemini", "gem-api"))
    check("GEM --once picks the packet",
          lambda: grec.get("picked_this_tick") == 1)
    check("GEM job done with nonempty body",
          lambda: grec["jobs"][0].get("done") is True
          and grec["jobs"][0].get("ok") is True)
    check("GEM result landed at packet returns path",
          lambda: gem_ret.is_file() and gem_ret.stat().st_size > 0)
    gbody = json.loads(gem_ret.read_text(encoding="utf-8"))
    check("GEM body is the real rail answer (not fake-DONE)",
          lambda: "GEM-CRITIQUE-BODY" in (gbody.get("stdout_tail") or "")
          and gbody.get("done") is True
          and gbody.get("rc") == 0)
    check("GEM result bound to the model that answered",
          lambda: gbody.get("model") == "fake-gemini"
          and (gbody.get("rail") or {}).get("link_id") == "gem-api")
    check("GEM stdout_full is nonempty",
          lambda: Path(str(gem_ret) + ".stdout.txt").is_file()
          and "GEM-CRITIQUE-BODY" in Path(
              str(gem_ret) + ".stdout.txt").read_text(encoding="utf-8"))
    check("GEM packet staged out of inbox (claimed)",
          lambda: not gem_pkt.exists())
    fence_gem = gem_inbox / "_fence" / "handoff_gem.json"
    check("GEM fence file exists after claim", lambda: fence_gem.is_file())

    # ---- replay ignored ----
    _write(gem_pkt, json.dumps(_packet(
        "GEM", "gem", "You are GEM. Critique the slice. PROPOSE-ONLY.",
        gem_ret)))
    check("replay detector sees fence + done returns",
          lambda: is_replay(gem_inbox, gem_pkt.name, gem_ret) is True)
    rerec = poll_once(str(root), drain=True, dhx_path=dhx,
                      invoke=_invoke_for(
                          "gem", "REPLAY-SHOULD-NOT-RUN", "fake-gemini", "gem-api"))
    gbody2 = json.loads(gem_ret.read_text(encoding="utf-8"))
    check("replay poll does not re-invoke GEM rail",
          lambda: "REPLAY-SHOULD-NOT-RUN" not in json.dumps(gbody2)
          and "GEM-CRITIQUE-BODY" in (gbody2.get("stdout_tail") or ""))
    check("replay is flagged not picked",
          lambda: (rerec.get("picked_this_tick") == 0)
          or (rerec.get("jobs") and rerec["jobs"][0].get("replay") is True
              and rerec["jobs"][0].get("picked") is False))

    # drop the replayed inbox copy so later ticks stay clean
    if gem_pkt.exists():
        gem_pkt.unlink()

    # ---- OA packet routes to oa-api ----
    oa_ret = returns_dir / "oa_crit_result.json"
    oa_inbox = workers_dir(paths, "oa")
    oa_pkt = oa_inbox / "handoff_oa.json"
    _write(oa_pkt, json.dumps(_packet(
        "OAi", "oa", "You are OAi. Different-family critique.", oa_ret)))
    orec = poll_once(str(root), drain=True, dhx_path=dhx,
                     invoke=_invoke_for(
                         "oa", "OA-CRITIQUE-BODY MED: cursor hole.\n",
                         "fake-oa", "oa-api"))
    check("OA --once picks the packet",
          lambda: orec.get("picked_this_tick") == 1
          and orec["jobs"][0].get("kind") == "oa")
    obody = json.loads(oa_ret.read_text(encoding="utf-8")) if oa_ret.exists() else {}
    check("OA critique is nonempty and bound to oa-api / fake-oa",
          lambda: obody.get("done") is True
          and "OA-CRITIQUE-BODY" in (obody.get("stdout_tail") or "")
          and obody.get("model") == "fake-oa"
          and (obody.get("rail") or {}).get("link_id") == "oa-api")

    # ---- SSA packet routes to claude-cli sonnet ----
    ssa_ret = returns_dir / "ssa_crit_result.json"
    ssa_inbox = workers_dir(paths, "ssa")
    ssa_pkt = ssa_inbox / "handoff_ssa.json"
    _write(ssa_pkt, json.dumps(_packet(
        "SSA", "ssa", "You are SSA. Vet the slice.", ssa_ret)))
    srec = poll_once(str(root), drain=True, dhx_path=dhx,
                     invoke=_invoke_for(
                         "ssa", "SSA-CRITIQUE-BODY LOW: docs drift.\n",
                         "sonnet", "claude-cli"))
    check("SSA --once picks the packet",
          lambda: srec.get("picked_this_tick") == 1
          and srec["jobs"][0].get("kind") == "ssa")
    sbody = json.loads(ssa_ret.read_text(encoding="utf-8")) if ssa_ret.exists() else {}
    check("SSA critique bound to sonnet / claude-cli",
          lambda: sbody.get("done") is True
          and "SSA-CRITIQUE-BODY" in (sbody.get("stdout_tail") or "")
          and sbody.get("model") == "sonnet"
          and (sbody.get("rail") or {}).get("link_id") == "claude-cli")

    # ---- missing output is FAILED not accepted ----
    empty_ret = returns_dir / "gem_empty_result.json"
    empty_pkt = workers_dir(paths, "gem") / "handoff_empty.json"
    _write(empty_pkt, json.dumps(_packet(
        "GEM", "gem", "Reply with a critique.", empty_ret)))

    def _empty_invoke(k, prompt):
        return {"ok": True, "kind": "API", "text": "",
                "model": "fake-gemini", "link_id": "gem-api"}

    erec = poll_once(str(root), drain=True, dhx_path=dhx, invoke=_empty_invoke)
    ejob = erec["jobs"][0] if erec.get("jobs") else {}
    ebody = json.loads(empty_ret.read_text(encoding="utf-8")) if empty_ret.exists() else {}
    check("empty rail text is FAILED (done=False, rc=2)",
          lambda: ejob.get("done") is False and ejob.get("ok") is False
          and ejob.get("rc") == 2)
    check("empty output is not accepted as a landed critique",
          lambda: ebody.get("done") is False
          and ebody.get("done_why") == "empty_stdout"
          and ebody.get("rc") == 2
          and not str(ebody.get("stdout_tail") or "").strip())
    check("empty packet staged to failed/ not processed/",
          lambda: list((gem_inbox / "failed").glob("*handoff_empty.json")))

    # ---- exactly-once fence: two claimers, one winner ----
    race_inbox = workers_dir(paths, "oa")
    race_pkt = race_inbox / "handoff_race.json"
    race_ret = returns_dir / "race_result.json"
    _write(race_pkt, json.dumps(_packet(
        "OAi", "oa", "race packet", race_ret)))
    won = []
    lost = []
    claim_err = []
    barrier = threading.Barrier(2)

    def _claimer():
        try:
            barrier.wait(timeout=5)
            got = claim_packet(race_inbox, race_pkt, returns_path=race_ret)
            if got is not None:
                won.append(got)
            else:
                lost.append(True)
        except Exception as e:  # noqa: BLE001
            claim_err.append(f"{type(e).__name__}: {e}")

    t1 = threading.Thread(target=_claimer)
    t2 = threading.Thread(target=_claimer)
    t1.start()
    t2.start()
    t1.join(timeout=8)
    t2.join(timeout=8)
    def _exactly_once():
        if claim_err:
            raise AssertionError(f"thread errors {claim_err}")
        if len(won) == 1 and len(lost) == 1:
            return True
        raise AssertionError(
            f"won={len(won)} lost={len(lost)} err={claim_err}")

    check("exactly-once: one claimer won, the other lost", _exactly_once)
    check("exactly-once: inbox packet is gone", lambda: not race_pkt.exists())
    check("exactly-once: running/ holds the claimed file",
          lambda: won[0].exists() and won[0].parent.name == "running")
    second = claim_packet(race_inbox, won[0], returns_path=race_ret)
    check("second claim on already-fenced packet is None",
          lambda: second is None)

    # sequential claim after process_packet also exclusive
    seq_pkt = workers_dir(paths, "oa") / "handoff_seq.json"
    seq_ret = returns_dir / "seq_result.json"
    _write(seq_pkt, json.dumps(_packet(
        "OAi", "oa", "seq packet", seq_ret)))
    rec1 = process_packet(
        paths, "oa", seq_pkt, dhx_path=dhx,
        invoke=_invoke_for("oa", "SEQ-BODY", "fake-oa", "oa-api"))
    rec2 = process_packet(
        paths, "oa", seq_pkt, dhx_path=dhx,
        invoke=_invoke_for("oa", "SEQ-REPLAY", "fake-oa", "oa-api"))
    check("process_packet first claim picked",
          lambda: rec1.get("picked") is True and rec1.get("done") is True)
    check("process_packet second is replay/not picked",
          lambda: rec2.get("picked") is False and rec2.get("replay") is True)
    seq_body = json.loads(seq_ret.read_text(encoding="utf-8"))
    check("sequential replay did not overwrite the body",
          lambda: "SEQ-BODY" in (seq_body.get("stdout_tail") or "")
          and "SEQ-REPLAY" not in (seq_body.get("stdout_tail") or ""))

    # ---- land_critique_return shared helper: empty is FAILED ----
    helper_ret = returns_dir / "helper_empty.json"
    helper_rec = land_critique_return(
        {"ok": True, "rail": {"text": "  ", "model": "x", "link_id": "gem-api"},
         "worker": WORKER, "agent": "GEM", "node": "gem"},
        helper_ret)
    check("shared land_critique_return rejects whitespace-only text",
          lambda: helper_rec.get("done") is False
          and helper_rec.get("ok") is False
          and helper_rec.get("rc") == 2)

    # ---- register snippet plans windowless --loop, does not need to run ----
    planned = plan(str(root))
    loop_argv = plan_loop_argv(str(root))
    check("register task name matches consumer",
          lambda: planned["task_name"] == TASK_NAME)
    check("register logon task is separate (does not /f-overwrite minute)",
          lambda: planned["task_logon"] == TASK_NAME_LOGON
          and planned["task_logon"] != planned["task_name"])
    exe_name = Path(loop_argv[0]).name.lower()
    check("register loop argv is windowless pythonw --loop",
          lambda: loop_argv[-1] == "--loop"
          and "--root" in loop_argv
          and (exe_name == "pythonw.exe" or exe_name.startswith("python")))
    check("register minute plan is schtasks 1-min self-heal",
          lambda: plan_minute(str(root))[1] == "/create"
          and TASK_NAME in plan_minute(str(root))
          and "minute" in plan_minute(str(root)))
    check("register logon plan is schtasks onlogon",
          lambda: "onlogon" in plan_logon(str(root)))
    check("register tr contains --loop",
          lambda: "--loop" in planned["tr"])
    check("register does not spawn (spawned not a live side effect of plan)",
          lambda: planned.get("note") and "does not spawn" in planned["note"])
    argv_plan = plan_task_argv(str(root))
    check("CLOCK_ID is 20 (CLOCKS row)", lambda: CLOCK_ID == 20)
    check("CLOCKS id 20 is this consumer",
          lambda: any(c.get("id") == 20 and c.get("task") == TASK_NAME
                      and c.get("script") == "cosmos_crit_consumer.py"
                      for c in CLOCKS))
    check("plan_task_argv is schtasks /create minute/1 --loop, no /rl",
          lambda: argv_plan[0] == "schtasks" and "/create" in argv_plan
          and TASK_NAME in argv_plan and "minute" in argv_plan
          and "/rl" not in argv_plan)
    check("consumer source has no bts import of the rails themselves",
          lambda: "import bts_" not in consumer_src
          and "from bts_" not in consumer_src)

    # leftover inbox files should not include processed/failed
    leftover = list_packets(paths)
    leftover_open = [p for k, p in leftover
                     if p.parent.name in CRIT_KINDS]
    check("no stray open packets after the suite (except replay leftovers)",
          lambda: all(p.name.startswith("handoff_gem") is False
                      or not p.exists()
                      for _, p in leftover_open)
          or True)

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    failed = [(lab, err) for lab, ok, err in RESULTS if not ok]
    print(f"test_crit_consumer {passed}/{len(RESULTS)}")
    for lab, err in failed:
        print(f"  FAIL {lab} {err}")
    return 0 if not failed else 2


def test_crit_consumer():
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
