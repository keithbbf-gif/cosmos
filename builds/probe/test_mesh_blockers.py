#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_mesh_blockers.py -- pins the blocker taxonomy. Offline and deterministic.

The tool it gates reports WHY a node rail does not prove live. The one way that
report can lie is by mis-classifying: calling an unasked-but-healthy rail "broken",
calling a stale proof fresh, or -- worst -- calling something live that carries no
proof. Those are the cases pinned here, on synthetic ledger/probe records, so the
suite needs no network, no key and no incumbent tree.

    py -3.14 builds\\probe\\test_mesh_blockers.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "cosmos"))

from mesh_blockers import (  # noqa: E402
    NODE_PROOF_TTL_S, UNBLOCK, UNWIRED_ROWS, WIRED_NODES,
    _kind_of, classify, render_md, rows,
)

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _state(lid, *, ok=None, rail_type="API", src="core", dst="models"):
    return {lid: {"claim": {"link_id": lid, "rail_type": rail_type, "src": src,
                            "dst": dst, "policy_rank": 0},
                  "last_probe": None, "ok": ok, "model": None, "rc": None,
                  "body_bytes": None}}


def _live(lid, age):
    return {lid: {"link_id": lid, "rail_type": "API", "verified": True,
                  "model": "m", "rc": 0, "body_bytes": 4, "age_s": age}}


WIRED_ROW = {"link_id": "sgh-api", "probe_with": "bts_sgh", "route": "core->models",
             "rail_type": "API"}
# A SYNTHETIC link_id, deliberately absent from WIRED_NODES. It used to be
# "cursor-api" -- a real rail -- so wiring that rail (F-24, 2026-08-31) turned
# four checks red with nothing broken: the fixture was asserting the current
# CONTENTS of a production table, not the classifier's behaviour. These checks
# are about the classifier, so the row it classifies is now ours alone.
UNWIRED_ROW = {"link_id": "_fixture-never-wired",
               "probe_with": "cosmos_cursor_rail"}
OK_PROBE = {"ok": True, "detail": "live", "evidence": {}}


def main() -> int:
    # -- the taxonomy reader: the rail's own kind, never an invented one --------
    check("a NO_KEY refusal is read as NO_KEY even when wrapped in UNREACHABLE:",
          lambda: _kind_of("UNREACHABLE: NO_KEY: [NO_KEY] key missing at x",
                           "BROKE") == "NO_KEY")
    check("a generic wrapper is used only when no specific cause is present",
          lambda: _kind_of("UNREACHABLE: probe raised; BROKE later", "X")
          == "UNREACHABLE")
    check("the specific cause outranks the wrapper wherever it appears",
          lambda: _kind_of("BROKE trailing AUTH_REQUIRED", "X") == "AUTH_REQUIRED")
    check("an unrecognised refusal falls back to the caller's default, not to OK",
          lambda: _kind_of("something nobody typed", "BROKE") == "BROKE")

    # -- the classifier: proof status is the ledger's answer, not the probe's ---
    healthy_unasked = classify(UNWIRED_ROW, OK_PROBE, {}, _state("_fixture-never-wired"))
    check("a healthy rail nobody asks is NOT_WIRED, not broken",
          lambda: healthy_unasked["kind"] == "NOT_WIRED"
          and healthy_unasked["probe_kind"] == "OK")
    check("NOT_WIRED is never reported as proven live",
          lambda: healthy_unasked["in_registry"] is False)
    check("the NOT_WIRED blocker names the table that has to change",
          lambda: "WIRED_NODES" in healthy_unasked["blocker"])
    check("a claim with zero measurements is reported as such",
          lambda: healthy_unasked["ledger_last"]["probe_results_recorded"] is False)
    check("rail_type and route come from the ledger claim, not from this tool",
          lambda: classify(UNWIRED_ROW, OK_PROBE, {},
                           _state("_fixture-never-wired", rail_type="CLI", dst="code")
                           )["route"] == "core->code")
    check("a link with no claim at all is 'unclaimed', never guessed",
          lambda: classify(UNWIRED_ROW, OK_PROBE, {}, {})["route"] == "unclaimed")

    fresh = classify(WIRED_ROW, OK_PROBE, _live("sgh-api", 10.0), _state("sgh-api", ok=True))
    old = classify(WIRED_ROW, OK_PROBE, _live("sgh-api", NODE_PROOF_TTL_S + 1),
                   _state("sgh-api", ok=True))
    check("a fresh proof is NONE", lambda: fresh["kind"] == "NONE")
    check("a proof older than the TTL is STALE_PROOF, not NONE",
          lambda: old["kind"] == "STALE_PROOF")
    check("the stale blocker states the age and the TTL",
          lambda: str(int(NODE_PROOF_TTL_S)) in old["blocker"])

    refusing = classify(WIRED_ROW, {"ok": False, "detail": "UNREACHABLE: NO_KEY: x"},
                        _live("sgh-api", 10.0), _state("sgh-api", ok=True))
    check("a registered node whose probe refuses keeps BOTH facts",
          lambda: refusing["kind"] == "NONE" and refusing["probe_kind"] == "NO_KEY")

    unmeasured = classify(UNWIRED_ROW,
                          {"ok": False, "kind": "UNMEASURED", "detail": "not run"},
                          {}, {})
    check("an unmeasured rail is never counted live",
          lambda: unmeasured["in_registry"] is False
          and unmeasured["probe_kind"] == "UNMEASURED")

    wired_no_proof = classify(WIRED_ROW, OK_PROBE, {}, _state("sgh-api"))
    check("wired + probe-green + no recorded proof is NO_PROOF",
          lambda: wired_no_proof["kind"] == "NO_PROOF")

    # -- the rows table is derived from the prober, never a second copy --------
    r = rows()
    check("every row carries a probe target",
          lambda: all(x.get("probe_with") for x in r))
    check("claude-cli (module=None in WIRED_NODES) routes to the claude rail",
          lambda: [x for x in r if x["link_id"] == "claude-cli"][0]["probe_with"]
          == "cosmos_claude_rail")
    # The UNION, not the sum: a rail that has been wired leaves UNWIRED_ROWS on
    # the way out of rows(), so summing the two tables double-counts exactly the
    # rails whose duplication this check exists to catch.
    expect = len({w["link_id"] for w in WIRED_NODES}
                 | {u["link_id"] for u in UNWIRED_ROWS})
    check("every wired and unasked rail is present exactly once",
          lambda: len(r) == expect
          and len({x["link_id"] for x in r}) == expect)
    check("every kind the classifier can emit has an unblock line",
          lambda: all(k in UNBLOCK for k in
                      ("NONE", "STALE_PROOF", "NOT_WIRED", "NO_PROOF", "NO_KEY",
                       "UNREACHABLE", "BROKE", "UNMEASURED", "AUTH_REQUIRED")))

    # -- F-25 leftover: live_nodes() drops stale; classify must still NAME them --
    # After the registry freshness filter landed, Registry.live_nodes() omits
    # expired proofs. The pre-fix classifier only saw STALE_PROOF when the row
    # was still IN `live`, so the live path re-labelled claude-cli as NO_PROOF
    # and the document kept claiming "file_runtime applies no freshness filter".
    try:
        stale_only = classify(
            WIRED_ROW, OK_PROBE, {}, _state("sgh-api", ok=True),
            stale=_live("sgh-api", NODE_PROOF_TTL_S + 99))
    except TypeError:
        # Pre-fix signature has no `stale=` — that is the defect.
        stale_only = classify(WIRED_ROW, OK_PROBE, {}, _state("sgh-api", ok=True))
    check("a row live_nodes() dropped is STALE_PROOF when named in stale_nodes(), not NO_PROOF",
          lambda: stale_only["kind"] == "STALE_PROOF")
    check("the stale row is not reported as proven live",
          lambda: stale_only.get("in_registry") is False)
    check("the stale blocker no longer claims file_runtime has no freshness filter",
          lambda: "no freshness filter" not in str(stale_only.get("blocker") or "").lower())
    check("the stale blocker names the projection's stale list",
          lambda: "stale" in str(stale_only.get("blocker") or "").lower())
    check("UNBLOCK[STALE_PROOF] no longer tells the reader the filter is missing",
          lambda: "no freshness filter" not in UNBLOCK["STALE_PROOF"].lower())

    # -- the rendered document cannot outrun the measurement -------------------
    rec = {"schema": "cosmos-mesh-blockers/1", "measured_at": "T", "root": "R",
           "deep": True, "ledger_error": None, "projection": "P",
           "projection_count": 1, "proof_ttl_s": NODE_PROOF_TTL_S,
           "live_count": 1, "total": 2, "elapsed_s": 0.1,
           "nodes": [fresh, healthy_unasked]}
    md = render_md(rec)
    check("the document reports the measured live count",
          lambda: "**1 of 2 node rails carry a passing proof**" in md)
    check("the document says the gate is proof_ok and is not weakened",
          lambda: "proof_ok" in md and "Nothing here weakens it" in md)
    check("the unasked rail's structural blocker reaches the document",
          lambda: "no prove() call path" in md)
    check("the document is renderable to a str with no None leaking in",
          lambda: isinstance(md, str) and "None" not in md.splitlines()[3])

    stale_md = render_md({**rec, "live_count": 0, "stale_count": 1,
                          "nodes": [stale_only, healthy_unasked]})
    check("the document does not claim file_runtime applies no freshness filter",
          lambda: "no freshness filter" not in stale_md.lower())
    check("the document says a stale row is listed under stale, not counted live",
          lambda: "`stale`" in stale_md.lower() or "stale list" in stale_md.lower())

    for label, ok, err in RESULTS:
        print(f"  {'OK  ' if ok else 'FAIL'}  {label}{('  ' + err) if err else ''}")
    bad = [x for x in RESULTS if not x[1]]
    print("live_value: " + json.dumps(
        {"kinds_pinned": sorted({x["kind"] for x in (fresh, old, healthy_unasked,
                                                     unmeasured, wired_no_proof)}),
         "rows": len(r), "md_bytes": len(md.encode("utf-8"))}, sort_keys=True))
    print(f"result: {'ok' if not bad else 'FAIL'}  "
          f"{len(RESULTS) - len(bad)}/{len(RESULTS)}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
