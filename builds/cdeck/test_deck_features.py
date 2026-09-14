#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Portfolio Studio stage-transition feature pins (PS-05).

Run: cd builds/cdeck && py -3.14 test_deck_features.py
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "cosmos"))

from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_profiles import (  # noqa: E402
    TRANSITION_EVENT,
    UNMEASURED,
    ProfileError,
    apply_stage_transition,
    load_engine,
    motif_transition_edges,
    save_engine,
    transition_contract,
)

RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, fn) -> None:
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _gates(paths):
    return {
        "health": {"verdict": "GREEN", "reds": 0, "negative_control_red": True},
        "tree": {"tree_id": paths.sentinel.tree_id},
        "spend": {"kind": "OK"},
        "product": {"id": "website", "kind": "OK"},
    }


def main() -> int:
    c = transition_contract()
    check("transition schema frozen",
          lambda: c["schema"].startswith("cosmos-profiles-transition/")
          and c["event"] == TRANSITION_EVENT
          and len(c["allowed_edges"]) == 9
          and set(c["gates"]) == {"health", "tree", "spend", "product"})
    check("every legal adjacent edge requires Keith",
          lambda: all(e.get("requires_keith") is True
                      for e in motif_transition_edges()))

    td = Path(tempfile.mkdtemp(prefix="cdeck_ps05_feat_"))
    root = install(td / "live", tree_id="cdeck-ps05-feat")
    k = Kernel(root)
    save_engine(k.paths, {
        "profile": "website",
        "define": {"text": "WHAT: deck features. WHY: PS-05."},
        "dest": {"kind": "staged"},
    })
    eng = load_engine(k.paths, "website")
    jobs_before = dict(k.sched._state())
    out = apply_stage_transition(k.paths, {
        "profile": "website",
        "action": "transition",
        "transition": {
            "from_stage": "define",
            "to_stage": "research",
            "expect_version": eng["version"],
        },
        "keith_decision": {"approved": True, "decided_by": "keith"},
        "gates": _gates(k.paths),
    }, kernel=k)
    check("Keith-approved adjacent transition ledger-bound; no job start",
          lambda: out["transition"]["ledger_event"] == TRANSITION_EVENT
          and isinstance(out["transition"]["ledger_seq"], int)
          and out["transition"]["job_started"] is False
          and dict(k.sched._state()) == jobs_before
          and out["engine"]["current_stage"] == "research")

    eng2 = load_engine(k.paths, "website")

    def refused(kind, body):
        try:
            apply_stage_transition(k.paths, body, kernel=k)
            return False
        except ProfileError as e:
            return e.kind == kind and dict(k.sched._state()) == jobs_before

    check("SKIPPED non-adjacent refuses without queueing",
          lambda: refused("SKIPPED", {
              "profile": "website",
              "transition": {"from_stage": "define", "to_stage": "critics",
                             "expect_version": eng2["version"]},
              "keith_decision": {"approved": True, "decided_by": "keith"},
              "gates": _gates(k.paths),
          }))
    check("STALE fencing refuses without queueing",
          lambda: refused("STALE", {
              "profile": "website",
              "transition": {"from_stage": "research", "to_stage": "arch",
                             "expect_version": eng2["version"] + 50},
              "keith_decision": {"approved": True, "decided_by": "keith"},
              "gates": _gates(k.paths),
          }))
    check("RED health refuses without queueing",
          lambda: refused("RED", {
              "profile": "website",
              "transition": {"from_stage": "research", "to_stage": "arch",
                             "expect_version": eng2["version"]},
              "keith_decision": {"approved": True, "decided_by": "keith"},
              "gates": {**_gates(k.paths), "health": {
                  "verdict": "RED x1", "reds": 1, "negative_control_red": True}},
          }))
    check("UNMEASURED product refuses without queueing",
          lambda: refused("UNMEASURED", {
              "profile": "website",
              "transition": {"from_stage": "research", "to_stage": "arch",
                             "expect_version": eng2["version"]},
              "keith_decision": {"approved": True, "decided_by": "keith"},
              "gates": {**_gates(k.paths), "product": {
                  "id": "website", "kind": UNMEASURED}},
          }))
    check("UNGATED missing Keith refuses without queueing",
          lambda: refused("UNGATED", {
              "profile": "website",
              "transition": {"from_stage": "research", "to_stage": "arch",
                             "expect_version": eng2["version"]},
              "gates": _gates(k.paths),
          }))

    failed = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("DECK_FEATURES %s - %d checks"
          % ("PASS" if not failed else "FAIL", len(RESULTS)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
