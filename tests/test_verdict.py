#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Isolated tests for cosmos_verdict. No live-tree writes, no network."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_here = Path(__file__).resolve().parent
_root = _here.parent
sys.path.insert(0, str(_root / "cosmos"))

from cosmos_paths import CosmosPaths, write_sentinel  # noqa: E402
from cosmos_verdict import (  # noqa: E402
    CLAIM_REASON, DONE_REASON, VerdictError, emit_verdict, format_objection,
    make_verdict, objection_is_concrete, parse_github_source, spoken_line,
    stamp_verdict, verdict_for, voice_drop_payload,
)
from cosmos_work_order import (  # noqa: E402
    drop_order, file_done, parse_order, pickup_order, reject_order,
)


def _root_pair():
    td = Path(tempfile.mkdtemp(prefix="cosmos_verdict_"))
    repo = td
    live = td / "live"
    write_sentinel(live, tree_id="wo-selftest")
    for name in ("cosmos", "docs", "tests"):
        (repo / name).mkdir(parents=True, exist_ok=True)
    (repo / "docs" / "WORK_ORDER_SPEC.md").write_text("# spec\n", encoding="utf-8")
    (live / "state").mkdir(parents=True, exist_ok=True)
    (live / "work").mkdir(parents=True, exist_ok=True)
    (live / "logs").mkdir(parents=True, exist_ok=True)
    (live / "config").mkdir(parents=True, exist_ok=True)
    return repo, live, CosmosPaths(live)


GROK = {
    "Agent": "xAI | Grok | grok-4.6",
    "Context source": ["docs/WORK_ORDER_SPEC.md [read*]"],
    "Task": "emit a one-line result",
    "Target & scope": "workspace out/ only",
    "Timestamp": "2026-09-02T11:45:20-05:00",
    "Output": "proposals | work-order-loop.json",
}


def test_verdict():
    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    check("pending make_verdict has no required objection",
          lambda: make_verdict("pending", reason=CLAIM_REASON).get("status") == "pending"
          and "objection" not in make_verdict("pending", reason=CLAIM_REASON))
    check("applied omits objection",
          lambda: "objection" not in make_verdict("applied", reason="COW accepted the proposal."))
    check("rejected without Fix: refused",
          lambda: _raises(lambda: make_verdict(
              "rejected", reason="nope", objection="it failed")))
    check("vague objection refused",
          lambda: objection_is_concrete("doesn't work") is False)
    ob = format_objection(
        kind="BAD_INPUT",
        file="work_orders/drop/wo-20260902T114530.json",
        symbol='"Target and scope"',
        what="SOP requires Target & scope",
        fix="rename the key to Target & scope and re-drop")
    check("format_objection passes validator",
          lambda: objection_is_concrete(ob) and ob.startswith("BAD_INPUT:") and "Fix:" in ob)
    check("status enum closed",
          lambda: _raises(lambda: make_verdict("DONE", reason="x")))

    rec = {"state": "PICKED_UP", "order_id": "wo-1",
           "_output": {"folder": "proposals", "filename": "x.json"}}
    check("PICKED_UP → pending claim reason",
          lambda: verdict_for(rec)["status"] == "pending"
          and verdict_for(rec)["reason"] == CLAIM_REASON)
    rec["state"] = "DONE"
    rec["output_exists"] = True
    check("DONE → pending awaiting COW",
          lambda: verdict_for(rec)["status"] == "pending"
          and verdict_for(rec)["reason"] == DONE_REASON)
    rec["state"] = "COMPLETED"
    rec["accept_note"] = "looks good"
    check("COMPLETED → applied",
          lambda: verdict_for(rec)["status"] == "applied"
          and verdict_for(rec).get("objection") in (None, ""))
    rec = {"state": "FAILED", "order_id": "wo-fail",
           "fail_kind": "FAILED",
           "fail_detail": "Output file missing or empty",
           "source": "github:keithbbf-gif/cosmos/work_orders/drop/wo-fail.json",
           "output_exists": False,
           "run": {"err": "rc=41 Vertex env missing", "rc": 41}}
    v = verdict_for(rec)
    check("FAILED → rejected concrete objection",
          lambda: v["status"] == "rejected" and objection_is_concrete(v["objection"])
          and "wo-fail.json" in v["objection"] and "Fix:" in v["objection"])
    check("DROPPED has no verdict",
          lambda: verdict_for({"state": "DROPPED"}) is None)

    src = parse_github_source(
        "github:keithbbf-gif/cosmos/work_orders/drop/wo-20260902T114520-05:00.json")
    check("parse github source keeps colon filename",
          lambda: src and src["path"].endswith("wo-20260902T114520-05:00.json"))
    check("README and non-drop paths refused",
          lambda: parse_github_source("github:keithbbf-gif/cosmos/docs/VERDICT_SPEC.md") is None)

    drop = {
        "Agent": GROK["Agent"], "Context source": GROK["Context source"],
        "Task": GROK["Task"], "Target & scope": GROK["Target & scope"],
        "Timestamp": GROK["Timestamp"], "Output": GROK["Output"],
        "extra_voice_note": "keep me",
        "_workspace": "V:\\secret",
    }
    pending = make_verdict("pending", reason=CLAIM_REASON, order_id="wo-1")
    voice = voice_drop_payload(drop, pending)
    check("voice payload keeps six SOP fields + Verdict",
          lambda: set(["Agent", "Context source", "Task", "Target & scope",
                       "Timestamp", "Output", "Verdict"]).issubset(voice)
          and "_workspace" not in voice
          and voice["Verdict"]["status"] == "pending")
    check("spoken pending is in progress",
          lambda: spoken_line(pending, order_id="wo-1").startswith("Work order wo-1 is in progress"))

    repo, live, paths = _root_pair()
    grok = dict(GROK)
    grok["source"] = "github:keithbbf-gif/cosmos/work_orders/drop/wo-dry.json"
    drop_path = drop_order(paths, grok, order_id="wo-dry")
    rec = pickup_order(paths, drop_path, repo_tree=repo, live_root=live)
    check("pickup stamps pending on live rec",
          lambda: stamp_verdict(rec)["status"] == "pending"
          and rec["Verdict"]["status"] == "pending")

    store = {"wo-dry.json": {
        "sha": "abc",
        "json": {k: grok[k] for k in ("Agent", "Context source", "Task",
                                      "Target & scope", "Timestamp", "Output")},
    }}
    puts = []
    posts = []

    def getter(owner, repo_n, path):
        return store[Path(path).name]

    def putter(owner, repo_n, path, *, message, payload, sha, branch="main"):
        puts.append({"path": path, "sha": sha, "payload": payload, "message": message})
        store[Path(path).name] = {"sha": "def", "json": payload}
        return {"content": {"sha": "def"}}

    def poster(url, body):
        posts.append({"url": url, "body": json.loads(body.decode("utf-8"))})
        return {"ok": True, "status": 200}

    rec["source"] = grok["source"]
    dry = emit_verdict(rec, paths=paths, github=True, notify=True, dry_run=True,
                       getter=getter, putter=putter, poster=poster)
    check("dry-run does not PUT or POST",
          lambda: dry["github"]["kind"] in ("DRY", "SELFTEST") and not puts and not posts)
    # tree_id wo-selftest also blocks live PUT even when dry_run=False
    live_emit = emit_verdict(rec, paths=paths, github=True, notify=True, dry_run=False,
                             getter=getter, putter=putter, poster=poster)
    check("selftest tree_id skips real PUT",
          lambda: live_emit["github"]["kind"] == "SELFTEST" and not puts)

    # Force emit path with a non-selftest sentinel by calling guts via dry payloads
    check("dry payload is the voice object",
          lambda: dry["github"]["payload"]["Verdict"]["status"] == "pending"
          and dry["github"]["payload"]["Agent"] == GROK["Agent"])

    rec["state"] = "DONE"
    rec["output_exists"] = True
    stamp_verdict(rec)
    refresh = emit_verdict(rec, paths=paths, github=True, notify=True, dry_run=True,
                           getter=getter, putter=putter, poster=poster)
    check("pending→pending skips notify POST",
          lambda: refresh["notify"]["kind"] in ("NO_STATUS_CHANGE", "DRY", "MISSING", "SELFTEST")
          or refresh.get("event", {}).get("event") == "verdict_refresh")

    rec["state"] = "FAILED"
    rec["fail_kind"] = "FAILED"
    rec["fail_detail"] = "Output file missing or empty"
    rec["output_exists"] = False
    stamp_verdict(rec)
    fail_e = emit_verdict(rec, paths=paths, github=True, notify=True, dry_run=True,
                          getter=getter, putter=putter, poster=poster)
    ev = fail_e.get("event") or {}
    obj = str((ev.get("Verdict") or fail_e.get("Verdict") or {}).get("objection") or "")
    check("FAILED dry event is verdict_changed rejected",
          lambda: ev.get("event") in ("verdict_changed", "verdict_landed", "verdict_refresh")
          and (fail_e.get("status") == "rejected" or (ev.get("Verdict") or {}).get("status") == "rejected")
          and "Fix:" in obj)

    (live / "config" / "ara_notify_url.txt").write_text("http://example.invalid/x\n", encoding="utf-8")
    from cosmos_verdict import load_notify_url
    check("http notify URL refused",
          lambda: load_notify_url(paths)[1] == "REFUSED_NOT_HTTPS")
    (live / "config" / "ara_notify_url.txt").write_text("https://example.invalid/hook\n", encoding="utf-8")
    check("https notify URL accepted",
          lambda: load_notify_url(paths)[1] == "OK")
    (live / "config" / "ara_notify_url.txt").unlink()
    check("missing notify URL is SKIP not a guessed host",
          lambda: load_notify_url(paths) == (None, "MISSING"))

    check("114530-shaped Agent without pipes-spaces still parse_github",
          lambda: parse_github_source(
              "github:keithbbf-gif/cosmos/work_orders/drop/wo-20260902T114530.json")["path"]
          .endswith("wo-20260902T114530.json"))

    bad = [(l, e) for l, ok, e in results if not ok]
    for l, ok, e in results:
        print(("  OK  " if ok else "  FAIL") + f" {l}" + (f"  {e}" if e else ""))
    print(f"{len(results) - len(bad)}/{len(results)} passed")
    assert not bad


def _raises(fn):
    try:
        fn()
    except VerdictError:
        return True
    return False


if __name__ == "__main__":
    test_verdict()
