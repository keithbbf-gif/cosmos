#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FOLLOW_KEYS on events COSMOS already writes.

cDeck FOLLOW harvests job_id / link_id / rail / node / session_id (and
sid / rid). CONVO_TURN declared job_ids and wrote [] every time; it
carried sid but not session_id. BOOT_VERIFIED carried worker but not
node. guarded_call wrote rid+rail on the spend events and then dropped
them from the return. TOOL_DECLARED / MAKER_ADDED carried name/id but
none of FOLLOW_KEYS, so the bootstrap page and a maker-add pulse had
nothing to draw.

This suite binds the emit-the-id fix to values only the new writers
produce, and BITE-proves the old writers do not.

BITE FIRST against
  _delme/predispose_follow_events_20260831T105507Z/ (convo/spend/kernel)
  _delme/predispose_follow_tool_maker_20260831T061706Z/ (tools/makers)
  _delme/predispose_follow_health_20260831T132220Z/ (health)
  _delme/predispose_follow_backup_command_20260831T134754Z/ (backup/command/clock/cli)

Run:  py -3.14 tests/test_follow_ids.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(REPO / "cosmos"))

from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_ledger import Ledger  # noqa: E402
from cosmos_convo import ConvoStore  # noqa: E402
from cosmos_spend import SpendGate  # noqa: E402
from cosmos_tools import ToolContracts  # noqa: E402
from cosmos_makers import MakerMap  # noqa: E402
from cosmos_health import HealthBoard  # noqa: E402
from cosmos_command import Commander  # noqa: E402
from cosmos_backup import Backup  # noqa: E402

EVIDENCE = REPO / "cosmos" / "_follow_ids_prove.json"
PRE = (
    REPO / "_delme" / "predispose_follow_events_20260831T105507Z" / "cosmos"
)
PRE_TM = (
    REPO / "_delme" / "predispose_follow_tool_maker_20260831T061706Z" / "cosmos"
)
PRE_H = (
    REPO / "_delme" / "predispose_follow_health_20260831T132220Z" / "cosmos"
)
PRE_BC = (
    REPO / "_delme" / "predispose_follow_backup_command_20260831T134754Z"
    / "cosmos"
)


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load " + str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _convo_turn_payloads(store) -> list:
    return [r["payload"] for r in store._ledger.verify()
            if r["event"] == "CONVO_TURN"]


def check_current() -> list:
    out = []

    def rec(name, ok, detail=""):
        out.append({"name": name, "ok": bool(ok), "detail": str(detail)[:400]})

    td = Path(tempfile.mkdtemp(prefix="cosmos_follow_"))
    KEY = b"k"
    led = Ledger(td / "c.jsonl", KEY, "follow")
    store = ConvoStore(led)
    sid = store.create_session("follow")
    store.append_turn(sid, "user", "hello")
    store.append_turn(sid, "assistant", "world", job_ids=["job-7"],
                      follow={"link_id": "sgh-api", "rail": "sgh-api",
                              "rid": "r-abc", "node": "grok"})
    turns = _convo_turn_payloads(store)
    user, asst = turns[0], turns[1]
    rec("user_turn_session_id_is_sid",
        user.get("session_id") == sid and user.get("sid") == sid,
        "session_id=%s sid=%s" % (user.get("session_id"), user.get("sid")))
    rec("assistant_job_id_singular",
        asst.get("job_id") == "job-7" and asst.get("job_ids") == ["job-7"],
        "job_id=%s job_ids=%s" % (asst.get("job_id"), asst.get("job_ids")))
    rec("assistant_follow_scalars",
        asst.get("link_id") == "sgh-api" and asst.get("rail") == "sgh-api"
        and asst.get("rid") == "r-abc" and asst.get("node") == "grok"
        and asst.get("session_id") == sid,
        "keys=%s" % sorted(asst.keys()))
    rec("follow_does_not_invent",
        user.get("job_id") is None and user.get("link_id") is None
        and user.get("job_ids") == [],
        "user extras=%s" % {k: user.get(k) for k in
                            ("job_id", "link_id", "rail", "node", "rid")})

    g = SpendGate(Ledger(td / "s.jsonl", KEY, "follow"))
    g.set_budget("gem", 1.00)
    r = g.guarded_call("gem", 0.10, lambda: {"usd": 0.01, "text": "ok"})
    rec("guarded_call_stamps_rid_rail",
        isinstance(r.get("rid"), str) and r["rid"].startswith("r-")
        and r.get("rail") == "gem" and r.get("usd") == 0.01,
        "rid=%s rail=%s usd=%s" % (r.get("rid"), r.get("rail"), r.get("usd")))

    root = td / "live"
    install(root, tree_id="follow-boot")
    k = Kernel(root, worker="core-follow")
    boot = next(r for r in k.ledger.verify() if r["event"] == "BOOT_VERIFIED")
    rec("boot_verified_node_equals_worker",
        boot["payload"].get("node") == "core-follow"
        and boot["payload"].get("worker") == "core-follow",
        "payload=%s" % boot["payload"])

    tled = Ledger(td / "t.jsonl", KEY, "follow")
    tc = ToolContracts(tled)
    tc.declare("sgh.ask", ["ask"], "one prompt in, one priced answer out")
    decl = next(r for r in tled.verify() if r["event"] == "TOOL_DECLARED")
    rec("tool_declared_node_equals_name",
        decl["payload"].get("node") == "sgh.ask"
        and decl["payload"].get("name") == "sgh.ask",
        "payload=%s" % decl["payload"])
    tc.disposition("sgh.ask", "PRESERVED", "contract held")
    disp = next(r for r in tled.verify() if r["event"] == "TOOL_DISPOSITION")
    rec("tool_disposition_node_equals_name",
        disp["payload"].get("node") == "sgh.ask",
        "payload=%s" % disp["payload"])

    mled = Ledger(td / "m.jsonl", KEY, "follow")
    mm = MakerMap(mled, seed=False)
    added = mm.add({
        "id": "cursor-cloud-agent",
        "kind": "AGENT",
        "location": "Cursor Cloud Agent",
        "function": "spawn a cloud coding agent against a repo branch",
        "access": "cursor.com background agents",
        "potential_sources": ["cursor.com/agents"],
        "tags": ["cloud", "coding"],
    })
    maker = next(r for r in mled.verify() if r["event"] == "MAKER_ADDED")
    rec("maker_added_node_equals_id",
        maker["payload"].get("node") == "cursor-cloud-agent"
        and maker["payload"].get("id") == "cursor-cloud-agent"
        and added.get("node") == "cursor-cloud-agent",
        "payload=%s" % maker["payload"])
    rec("maker_projection_strips_follow_key",
        "node" not in MakerMap(mled, seed=False).state()["cursor-cloud-agent"],
        "state=%s" % MakerMap(mled, seed=False).state()["cursor-cloud-agent"])

    # Live tail is 90/100 HEALTH_BOARD with zero FOLLOW_KEYS. Stamp the
    # resolver identity already on the kernel (sentinel.system == "COSMOS"),
    # never a guessed rail. That is the id the deck's COSMOS box already draws.
    hb = HealthBoard(k)
    board = hb.run()
    health = next(r for r in k.ledger.verify() if r["event"] == "HEALTH_BOARD")
    rec("health_board_node_equals_system",
        health["payload"].get("node") == k.paths.sentinel.system
        and k.paths.sentinel.system == "COSMOS"
        and board.get("verdict") == "GREEN",
        "payload=%s system=%s" % (health["payload"], k.paths.sentinel.system))

    # COMMAND_HANDLED is PULSE_HOME → CVM. Pulse already lights that box; FOLLOW
    # harvests none of FOLLOW_KEYS on the 56 live rows. Stamp the box the deck
    # already draws (addNode("CVM")), never a guessed rail.
    Commander(k).handle("status")
    ch = [r for r in k.ledger.verify() if r["event"] == "COMMAND_HANDLED"][-1]
    rec("command_handled_node_is_cvm",
        ch["payload"].get("node") == "CVM" and ch["payload"].get("ok") is True,
        "payload=%s" % ch["payload"])
    try:
        Commander(k).handle("delete everything")
    except Exception:
        pass
    cr = [r for r in k.ledger.verify() if r["event"] == "COMMAND_REFUSED"][-1]
    rec("command_refused_node_is_cvm",
        cr["payload"].get("node") == "CVM",
        "payload=%s" % cr["payload"])

    # BACKUP_VERIFIED is in the live tail and is NOT in PULSE_HOME, so it
    # currently pulses nothing. Stamp resolver identity (same as HEALTH_BOARD).
    src_b = td / "bak_src"
    src_b.mkdir()
    (src_b / "a.txt").write_text("alpha", encoding="utf-8")
    tgt_b = td / "bak_tgt"
    tgt_b.mkdir()
    bled = Ledger(td / "b.jsonl", KEY, "follow")
    try:
        bk = Backup(bled, node="COSMOS")
        br = bk.run(src_b, tgt_b)
        bv = next(r for r in bled.verify() if r["event"] == "BACKUP_VERIFIED")
        rec("backup_verified_node",
            bv["payload"].get("node") == "COSMOS" and br.get("files") == 1,
            "payload=%s" % bv["payload"])
        rr = bk.rehearse_restore(br["dest"], td / "bak_scratch")
        rp = next(r for r in bled.verify()
                  if r["event"] == "RESTORE_REHEARSAL_PASSED")
        rec("restore_rehearsal_passed_node",
            rp["payload"].get("node") == "COSMOS" and rr.get("files") == 1,
            "payload=%s" % rp["payload"])
    except TypeError as e:
        rec("backup_verified_node", False, "TypeError: %s" % e)
        rec("restore_rehearsal_passed_node", False, "TypeError: %s" % e)

    clock_src = (REPO / "cosmos" / "cosmos_backup_clock.py").read_text(
        encoding="utf-8")
    rec("clock_constructs_backup_with_sentinel_system",
        "node=paths.sentinel.system" in "".join(clock_src.split()),
        "clock_has_node_kwarg=%s" % ("node=paths.sentinel.system"
                                     in "".join(clock_src.split())))
    cli_src = (REPO / "cosmos" / "cosmos.py").read_text(encoding="utf-8")
    rec("cli_constructs_backup_with_sentinel_system",
        "node=k.paths.sentinel.system" in "".join(cli_src.split()),
        "cli_has_node_kwarg=%s" % ("node=k.paths.sentinel.system"
                                  in "".join(cli_src.split())))
    return out


def check_prechange() -> list:
    """Old convo/spend/kernel do not emit the followable keys."""
    out = []

    def rec(name, ok, detail=""):
        out.append({"name": name, "ok": bool(ok), "detail": str(detail)[:400]})

    old_convo = _load("old_cosmos_convo", PRE / "cosmos_convo.py")
    old_spend = _load("old_cosmos_spend", PRE / "cosmos_spend.py")

    td = Path(tempfile.mkdtemp(prefix="cosmos_follow_old_"))
    KEY = b"k"
    led = Ledger(td / "c.jsonl", KEY, "follow-old")
    store = old_convo.ConvoStore(led)
    sid = store.create_session("follow")
    store.append_turn(sid, "assistant", "world", job_ids=["job-7"])
    p = _convo_turn_payloads(store)[0]
    rec("old_convo_has_no_session_id",
        p.get("session_id") is None,
        "session_id=%s keys=%s" % (p.get("session_id"), sorted(p.keys())))
    rec("old_convo_has_no_singular_job_id",
        p.get("job_id") is None and p.get("job_ids") == ["job-7"],
        "job_id=%s job_ids=%s" % (p.get("job_id"), p.get("job_ids")))

    g = old_spend.SpendGate(Ledger(td / "s.jsonl", KEY, "follow-old"))
    g.set_budget("gem", 1.00)
    r = g.guarded_call("gem", 0.10, lambda: {"usd": 0.01})
    rec("old_guarded_call_drops_rid_rail",
        r.get("rid") is None and r.get("rail") is None and r.get("usd") == 0.01,
        "rid=%s rail=%s keys=%s" % (r.get("rid"), r.get("rail"),
                                    sorted(r.keys())))

    src = (PRE / "cosmos_kernel.py").read_text(encoding="utf-8")
    rec("old_boot_verified_source_has_no_node_key",
        '"node": worker' not in src and "'node': worker" not in src,
        "node-stamp absent from staged kernel source")

    old_tools = _load("old_cosmos_tools", PRE_TM / "cosmos_tools.py")
    old_makers = _load("old_cosmos_makers", PRE_TM / "cosmos_makers.py")
    td_tm = Path(tempfile.mkdtemp(prefix="cosmos_follow_old_tm_"))
    tled = Ledger(td_tm / "t.jsonl", KEY, "follow-old")
    old_tools.ToolContracts(tled).declare("sgh.ask", ["ask"], "priced")
    dp = next(r for r in tled.verify() if r["event"] == "TOOL_DECLARED")["payload"]
    rec("old_tool_declared_has_no_node",
        dp.get("node") is None and dp.get("name") == "sgh.ask",
        "payload=%s" % dp)

    mled = Ledger(td_tm / "m.jsonl", KEY, "follow-old")
    old_makers.MakerMap(mled, seed=False).add({
        "id": "cursor-cloud-agent",
        "kind": "AGENT",
        "location": "Cursor Cloud Agent",
        "function": "spawn a cloud coding agent against a repo branch",
        "access": "cursor.com background agents",
        "potential_sources": ["cursor.com/agents"],
        "tags": ["cloud", "coding"],
    })
    mp = next(r for r in mled.verify() if r["event"] == "MAKER_ADDED")["payload"]
    rec("old_maker_added_has_no_node",
        mp.get("node") is None and mp.get("id") == "cursor-cloud-agent",
        "payload=%s" % mp)

    old_health = _load("old_cosmos_health", PRE_H / "cosmos_health.py")
    td_h = Path(tempfile.mkdtemp(prefix="cosmos_follow_old_h_"))
    root_h = install(td_h / "live", tree_id="follow-old-health")
    k_h = Kernel(root_h, worker="core-follow-old")
    old_health.HealthBoard(k_h).run()
    hp = next(r for r in k_h.ledger.verify()
              if r["event"] == "HEALTH_BOARD")["payload"]
    rec("old_health_board_has_no_node",
        hp.get("node") is None and "verdict" in hp,
        "payload=%s" % hp)

    old_bak = _load("old_cosmos_backup", PRE_BC / "cosmos_backup.py")
    old_cmd = _load("old_cosmos_command", PRE_BC / "cosmos_command.py")
    td_bc = Path(tempfile.mkdtemp(prefix="cosmos_follow_old_bc_"))
    src_o = td_bc / "src"
    src_o.mkdir()
    (src_o / "a.txt").write_text("alpha", encoding="utf-8")
    tgt_o = td_bc / "tgt"
    tgt_o.mkdir()
    bled_o = Ledger(td_bc / "b.jsonl", KEY, "follow-old-bak")
    old_bak.Backup(bled_o).run(src_o, tgt_o)
    bpo = next(r for r in bled_o.verify()
               if r["event"] == "BACKUP_VERIFIED")["payload"]
    rec("old_backup_verified_has_no_node",
        bpo.get("node") is None and bpo.get("files") == 1,
        "payload=%s" % bpo)

    root_o = install(td_bc / "live", tree_id="follow-old-cmd")
    k_o = Kernel(root_o, worker="voice-old")
    old_cmd.Commander(k_o).handle("status")
    cpo = next(r for r in k_o.ledger.verify()
               if r["event"] == "COMMAND_HANDLED")["payload"]
    rec("old_command_handled_has_no_node",
        cpo.get("node") is None and cpo.get("ok") is True,
        "payload=%s" % cpo)

    clock_old = "".join((PRE_BC / "cosmos_backup_clock.py").read_text(
        encoding="utf-8").split())
    rec("old_clock_source_has_no_node_kwarg",
        "node=paths.sentinel.system" not in clock_old,
        "has_kwarg=%s" % ("node=paths.sentinel.system" in clock_old))
    cli_old = "".join((PRE_BC / "cosmos.py").read_text(
        encoding="utf-8").split())
    rec("old_cli_source_has_no_node_kwarg",
        "node=k.paths.sentinel.system" not in cli_old,
        "has_kwarg=%s" % ("node=k.paths.sentinel.system" in cli_old))
    return out


def main() -> int:
    if not (PRE / "cosmos_convo.py").is_file():
        print("REFUSING: pre-change convo not staged at %s" % PRE)
        return 1
    if not (PRE_TM / "cosmos_tools.py").is_file():
        print("REFUSING: pre-change tools not staged at %s" % PRE_TM)
        return 1
    if not (PRE_H / "cosmos_health.py").is_file():
        print("REFUSING: pre-change health not staged at %s" % PRE_H)
        return 1
    if not (PRE_BC / "cosmos_backup.py").is_file():
        print("REFUSING: pre-change backup not staged at %s" % PRE_BC)
        return 1
    if not (PRE_BC / "cosmos_command.py").is_file():
        print("REFUSING: pre-change command not staged at %s" % PRE_BC)
        return 1
    pre = check_prechange()
    cur = check_current()
    pre_pass = sum(1 for c in pre if c["ok"])
    cur_pass = sum(1 for c in cur if c["ok"])
    bite = pre_pass == len(pre)  # these checks ARE the "old lacks the key" facts
    all_cur = cur_pass == len(cur)
    evidence = {
        "ok": bool(bite and all_cur),
        "probe": "tests/test_follow_ids.py — emit FOLLOW_KEYS on existing events",
        "prechange_path": str(PRE),
        "prechange": {"checks": pre, "tests_run": len(pre),
                      "tests_passed": pre_pass},
        "current": {"checks": cur, "tests_run": len(cur),
                    "tests_passed": cur_pass},
        "emitted": {
            "boot": next((c["detail"] for c in cur
                          if c["name"] == "boot_verified_node_equals_worker"), ""),
            "tool_declared": next((c["detail"] for c in cur
                                   if c["name"] == "tool_declared_node_equals_name"), ""),
            "maker_added": next((c["detail"] for c in cur
                                 if c["name"] == "maker_added_node_equals_id"), ""),
            "health_board": next((c["detail"] for c in cur
                                  if c["name"] == "health_board_node_equals_system"), ""),
            "command_handled": next((c["detail"] for c in cur
                                     if c["name"] == "command_handled_node_is_cvm"), ""),
            "backup_verified": next((c["detail"] for c in cur
                                     if c["name"] == "backup_verified_node"), ""),
        },
    }
    EVIDENCE.write_text(json.dumps(evidence, indent=1), encoding="utf-8")
    print("== PRECHANGE (old writers MUST lack the keys) ==")
    for c in pre:
        print("  %s  %s  %s" % (
            "OK  " if c["ok"] else "FAIL", c["name"], c.get("detail") or ""))
    print("== CURRENT ==")
    for c in cur:
        print("  %s  %s  %s" % (
            "OK  " if c["ok"] else "FAIL", c["name"], c.get("detail") or ""))
    print("EVIDENCE %s" % EVIDENCE)
    print("SELFTEST %s - current %d/%d; prechange-lacks-keys %d/%d"
          % ("PASS" if evidence["ok"] else "FAIL",
             cur_pass, len(cur), pre_pass, len(pre)))
    return 0 if evidence["ok"] else 1


def test_follow_ids():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
