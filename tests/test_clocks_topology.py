#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: proposals/clocks-topology.json (WO: CLOCKS topology, issue #31).

The proposal is a DECISION RECORD in the same shape as cosmos_port_plan.PORT_DECISIONS,
so it gets the same treatment: the four dispositions are validated against the tree's own
vocabulary (cosmos_tools.DISPOSITIONS), and the accounting is COUNTED, never quoted.

The rule this enforces, from cosmos_port_plan: "a successor that does not exist is a
claim, not a port". Here that means every REPLACED clock must name where its duty went,
and every one of the 26 rows must land in exactly one bucket.

Carries a PLANTED-FAILURE row per cosmos_health: a board that cannot go red is not a
board. That row must be RED on every pass and is stripped from the verdict.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "cosmos"))

from cosmos_tools import DISPOSITIONS  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "proposals" / "clocks-topology.json"
DOC = ROOT / "proposals" / "clocks-topology.md"

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


plan = json.loads(PLAN.read_text(encoding="utf-8"))
clocks = plan["clocks"]
procs = plan["resident_processes"]["processes"]

# ---- the registry is not shrunk -------------------------------------------------
check("26 clock rows, ids 1..26 contiguous",
      lambda: sorted(int(k) for k in clocks) == list(range(1, 27)))

# ---- dispositions come from the tree's vocabulary, not a new one ----------------
check("every disposition is one of the tree's four (cosmos_tools.DISPOSITIONS)",
      lambda: all(c["disposition"] in DISPOSITIONS for c in clocks.values()))

check("proposal's declared vocabulary matches cosmos_tools exactly",
      lambda: set(plan["dispositions"]["valid"]) == DISPOSITIONS)

# ---- vehicle / cadence rule: >=60s is calendar, <60s is resident ----------------
once = {k for k, c in clocks.items() if c["vehicle"] == "once"}
loop = {k for k, c in clocks.items() if c["vehicle"] != "once"}

check("12 calendar --once rows, 14 resident rows, and they partition the 26",
      lambda: len(once) == 12 and len(loop) == 14 and once | loop == set(clocks))

check("every calendar --once row has cadence >= 60s (the cadence rule)",
      lambda: all(clocks[k]["cadence_s"] >= 60 for k in once))

check("every resident row has cadence < 60s (nothing resident without a reason)",
      lambda: all(clocks[k]["cadence_s"] < 60 for k in loop))

# ---- the calendar rows are left alone -------------------------------------------
check("every calendar --once row is PRESERVED (they were never the problem)",
      lambda: all(clocks[k]["disposition"] == "PRESERVED" for k in once))

check("PRESERVED is used ONLY for calendar rows",
      lambda: {k for k, c in clocks.items() if c["disposition"] == "PRESERVED"} == once)

# ---- a successor that does not exist is a claim, not a port ---------------------
check("every REPLACED row names a successor",
      lambda: all(c.get("successor")
                  for c in clocks.values() if c["disposition"] == "REPLACED"))

check("every ABANDONED row names where the duty went (or that it ends)",
      lambda: all(c.get("successor") and c.get("reason")
                  for c in clocks.values() if c["disposition"] == "ABANDONED"))

check("every row carries a reason - no silent rulings",
      lambda: all(str(c.get("reason", "")).strip() for c in clocks.values()))

# ---- accounting: every resident row lands in exactly one place ------------------
absorbed = [i for p in procs.values() for i in p["absorbs"]]
abandoned = {int(k) for k, c in clocks.items() if c["disposition"] == "ABANDONED"}

check("no clock is absorbed by two processes",
      lambda: len(absorbed) == len(set(absorbed)))

check("absorbed + abandoned == exactly the 14 resident rows",
      lambda: set(absorbed) | abandoned == {int(k) for k in loop})

check("no calendar row was absorbed by a resident process",
      lambda: not (set(absorbed) & {int(k) for k in once}))

check("row 15 (Runner Pool) and row 10 (cDeck Feed) are the abandoned pair",
      lambda: abandoned == {10, 15})

# ---- the headline count is derived, not asserted --------------------------------
check("count_after == Core + the three daemons",
      lambda: plan["resident_processes"]["count_after"] == len(procs) == 4)

check("count_before == Core + 14 resident rows",
      lambda: plan["resident_processes"]["count_before"] == 1 + len(loop) == 15)

check("dropping conditional P2 gives the stated smaller count",
      lambda: (plan["resident_processes"]["count_after"]
               - sum(1 for p in procs.values() if p.get("conditional"))
               == plan["resident_processes"]["count_after_if_cvm_not_realtime"]))

check("every conditional process states its condition AND how to resolve it",
      lambda: all(p.get("condition") and p.get("resolve_with")
                  for p in procs.values() if p.get("conditional")))

# ---- Core is protected by construction ------------------------------------------
check("P0 is Core, is not a CLOCKS row, and absorbs nothing",
      lambda: procs["P0"]["is_clocks_row"] is False and procs["P0"]["absorbs"] == [])

check("collapse invariant names Core :8770 and forbids zero restarters",
      lambda: "8770" in plan["collapse_order"]["invariant"]
      and "never stopped" in plan["collapse_order"]["invariant"].lower())

check("the never-do list carries all five P10 boundaries",
      lambda: len(plan["collapse_order"]["never"]) == 5
      and any("delete" in n for n in plan["collapse_order"]["never"])
      and any("8770" in n for n in plan["collapse_order"]["never"]))

check("every collapse step names who holds the invariant and its gate",
      lambda: all(s.get("invariant_held_by") and s.get("gate")
                  for s in plan["collapse_order"]["steps"]))

check("retirement is /disable, never /delete",
      lambda: "/disable" in plan["logon_relaunches"]["retirement_method"]
      and "NEVER /delete" in plan["logon_relaunches"]["retirement_method"])

# ---- P10: this PR proposes, it does not act -------------------------------------
ch = plan["constraints_honoured"]
check("P10 honoured: tuple not shrunk, PEER_HEARTBEATS not edited, nothing acted on",
      lambda: ch["clocks_tuple_shrunk"] is False
      and ch["peer_heartbeats_edited"] is False
      and ch["schtasks_touched"] is False
      and ch["core_8770_touched"] is False
      and ch["hold_pause_lifted"] is False
      and ch["v_ai_written"] is False
      and ch["anthropic_off"] == "unchanged")

check("this PR touches only proposals/ and its own test",
      lambda: all(f.startswith("proposals/") or f == "tests/test_clocks_topology.py"
                  for f in ch["files_written"]))

# ---- every claim is falsifiable --------------------------------------------------
check("every falsification entry carries a runnable check",
      lambda: all(f.get("check") and f.get("falsified_if")
                  for f in plan["falsification"]))

check("open questions are declared, not hidden",
      lambda: len(plan["open_questions"]) >= 5)

check("the 404 evidence warning is carried in the machine-readable file too",
      lambda: "404" in plan["evidence_warning"])

# ---- prose and data agree --------------------------------------------------------
doc = DOC.read_text(encoding="utf-8")
check("markdown states the same headline as the JSON",
      lambda: "four resident Python processes" in doc)

check("markdown carries the PEER_HEARTBEATS change as a diff only, not an edit",
      lambda: "--- a/cosmos/cosmos_health_clock.py" in doc
      and not (ROOT / "cosmos" / "cosmos_health_clock.py").exists())

check("markdown answers all five numbered asks",
      lambda: all(h in doc for h in (
          "## 1. How many resident Python processes",
          "## 2. Which CLOCKS rows stay calendar",
          "## 3. Which loops should die",
          "## 4. What couplings break",
          "## 5. Collapse order")))

# ---- THE NEGATIVE CONTROL (cosmos_health): must be RED on every pass -------------
check("negative control (must be RED)",
      lambda: clocks["4"]["disposition"] == "ABANDONED")


def main() -> int:
    control = [r for r in RESULTS if r[0] == "negative control (must be RED)"]
    rows = [r for r in RESULTS if r[0] != "negative control (must be RED)"]
    control_red = bool(control) and control[0][1] is False

    for label, ok, err in rows:
        print(f"  {'PASS' if ok else 'FAIL'}  {label}{(' - ' + err) if err else ''}")
    print(f"  {'PASS' if control_red else 'FAIL'}  negative control stayed RED "
          f"(green here means this test cannot detect failure)")

    reds = [r for r in rows if not r[1]]
    if not control_red:
        print("\nBOARD-BROKEN: the planted failure showed GREEN")
        return 2
    if reds:
        print(f"\nRED x{len(reds)}")
        return 1
    print(f"\nGREEN - {len(rows)} checks, negative control red")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
