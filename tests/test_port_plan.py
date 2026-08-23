#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: cosmos_port_plan (the COSMOS PORT PLAN). Every incumbent tool gets a
recorded disposition with a successor-or-reason; a REPLACED tool names a cosmos_ module
that ACTUALLY EXISTS on disk (a successor that does not exist is a claim); the summary
counts are consistent with the plan and with the applied ledger state; there is no
silent UNDECIDED beyond ones that carry an explicit reason; and applying twice is
idempotent - the drift guard fires and the projected rulings do not change."""
from __future__ import annotations
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_ledger import Ledger
from cosmos_tools import ToolContracts, DISPOSITIONS
from cosmos_port_plan import (PORT_DECISIONS, VALID_DISPOSITIONS, UNDECIDED,
                              apply, summary)

RESULTS = []
HERE = Path(__file__).resolve().parent
_CMOD = re.compile(r"cosmos_[a-z]+")


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def existing_cosmos_modules() -> set[str]:
    """Ground truth: every cosmos_*.py that exists, in this spike dir and the sibling
    SPIKE_F5_* spike dirs (cosmos_paths/lock/mail live in their own spike folders)."""
    mods = {p.stem for p in HERE.glob("cosmos_*.py")}
    for sib in HERE.parent.glob("SPIKE_F5_*"):
        if sib.is_dir():
            mods |= {p.stem for p in sib.glob("cosmos_*.py")}
    return mods


def cosmos_tokens(successor) -> list[str]:
    return _CMOD.findall(successor or "")


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_pp_"))
    tc = ToolContracts(Ledger(td / "port.jsonl", b"k", "F5"))
    result = apply(tc)
    existing = existing_cosmos_modules()

    # ---- sanity: the ground-truth set really found the successors we depend on ----
    check("cosmos module discovery found the spike successors (paths/lock/mail)",
          lambda: {"cosmos_paths", "cosmos_lock", "cosmos_mail"} <= existing)

    # ================= EVERY DECISION IS WELL-FORMED =================
    check("plan is non-empty",
          lambda: len(PORT_DECISIONS) > 0)
    check("every decision has a VALID disposition (four + UNDECIDED sentinel)",
          lambda: all(d["disposition"] in VALID_DISPOSITIONS
                      for d in PORT_DECISIONS.values()))
    check("every decision has a successor OR a reason (never neither)",
          lambda: all(bool(d.get("successor")) or bool((d.get("reason") or "").strip())
                      for d in PORT_DECISIONS.values()))
    check("every decision carries a reason (the recorded why)",
          lambda: all((d.get("reason") or "").strip() for d in PORT_DECISIONS.values()))

    # ================= REPLACED NAMES A REAL COSMOS MODULE =================
    replaced = {n: d for n, d in PORT_DECISIONS.items()
                if d["disposition"] == "REPLACED"}
    check("every REPLACED entry names a successor",
          lambda: all(d.get("successor") for d in replaced.values()))
    check("every REPLACED successor contains at least one cosmos_ module token",
          lambda: all(cosmos_tokens(d["successor"]) for d in replaced.values()))
    check("every cosmos_ module named by a REPLACED successor EXISTS on disk",
          lambda: all(all(tok in existing for tok in cosmos_tokens(d["successor"]))
                      for d in replaced.values()))

    # belt-and-braces: ANY cosmos_ token anywhere in a successor must be real
    check("no successor (any disposition) names a non-existent cosmos_ module",
          lambda: all(all(tok in existing for tok in cosmos_tokens(d.get("successor")))
                      for d in PORT_DECISIONS.values()))

    # ================= NO SILENT UNDECIDED =================
    undecided = [n for n, d in PORT_DECISIONS.items()
                 if d["disposition"] == UNDECIDED]
    check("no UNDECIDED is silent - each names its debt in the reason",
          lambda: all((PORT_DECISIONS[n].get("reason") or "").strip()
                      for n in undecided))
    check("summary().undecided matches the plan's UNDECIDED set",
          lambda: set(summary()["undecided"]) == set(undecided))

    # ================= SUMMARY COUNTS ARE CONSISTENT =================
    s = summary()
    check("summary total == len(PORT_DECISIONS)",
          lambda: s["total"] == len(PORT_DECISIONS))
    check("by_disposition sums to total (no tool uncounted, none double-counted)",
          lambda: sum(s["by_disposition"].values()) == s["total"])
    check("apply() returned the same summary shape as summary()",
          lambda: result["total"] == s["total"]
          and result["by_disposition"] == s["by_disposition"])
    check("required incumbents are all present in the plan",
          lambda: {"bts_paths", "tree_lock", "bts_phone", "bts_runner", "bts_health",
                   "bts_kdash_feed", "bts_serve", "task_registry", "rail_check",
                   "bts_elevated_ops", "bts_drive_health", "backup_to_onedrive",
                   "backup_watchdog", "tools_sync", "corrections", "scars",
                   "verify_pointers", "verify_conf", "mesh_fanout", "bts_sgh",
                   "bts_gem", "bts_gw", "bts_oa_api", "bts_cursor", "bts_bus",
                   "bts_node", "bts_dymon", "bts_watchdog", "bts_poller",
                   "bts_identity", "bts_spend", "bts_cop", "bts_policy"}
          <= set(PORT_DECISIONS))

    # ================= APPLIED STATE MATCHES THE PLAN =================
    st = tc.state()
    check("every planned tool was declared into the registry",
          lambda: all(n in st for n in PORT_DECISIONS))
    check("every FOUR-disposition tool recorded that exact decision in the ledger",
          lambda: all(st[n]["disposition"]
                      and st[n]["disposition"]["decision"] == d["disposition"]
                      for n, d in PORT_DECISIONS.items()
                      if d["disposition"] in DISPOSITIONS))
    check("every UNDECIDED tool is declared but carries NO disposition event (the gap)",
          lambda: all(st[n]["disposition"] is None for n in undecided))

    # ================= RE-APPLY IS IDEMPOTENT =================
    before = summary()
    state_before = {n: (v["disposition"] or {}).get("decision")
                    for n, v in tc.state().items()}
    result2 = apply(tc)            # must not raise on the duplicate declares
    state_after = {n: (v["disposition"] or {}).get("decision")
                   for n, v in tc.state().items()}
    check("re-apply does not raise and returns identical counts",
          lambda: result2["by_disposition"] == before["by_disposition"]
          and result2["total"] == before["total"])
    check("re-apply leaves the projected rulings unchanged (no drift on replay)",
          lambda: state_after == state_before)
    check("re-apply adds no new tools to the registry",
          lambda: set(tc.state()) == set(st))

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("PORT PLAN: %d tools mapped | %s" % (s["total"], s["by_disposition"]))
    print("SELFTEST %s - %d checks (architecture wins where a contract conflicts; "
          "every decision recorded, never drifted)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_port_plan():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
