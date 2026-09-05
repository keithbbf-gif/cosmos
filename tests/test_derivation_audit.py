#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pin CORE_RESTRUCTURE work order 2.3 derivation audit.

F-36 leftover: Phase 2 work order 2.3 had no artifact. This suite is the
pin that the audit runs, classifies every declared site, and does NOT
flip tracker authority.

Bite: before cosmos_derivation_audit.py existed this file ImportError'd.
Does not flip write_tracker_json authority.

Run:  py -3.14 tests/test_derivation_audit.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "cosmos"))

from cosmos_derivation_audit import SCHEMA, SITES, audit  # noqa: E402

RESULTS = []
LIVE_VALUE = {}
EVIDENCE = REPO / "cosmos" / "_f36_derivation_audit.json"


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, "%s: %s" % (type(e).__name__, e)))


def main() -> int:
    rec = audit(REPO / "cosmos")
    EVIDENCE.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")

    check("audit schema is cosmos-derivation-audit/1",
          lambda: rec["schema"] == SCHEMA)
    check("every classified site is ok (no FILE/SYMBOL drift)",
          lambda: rec["ok"] is True and rec["unreviewed_count"] == 0)
    check("work order 2.3 OPEN leftover is parse_tracker_markdown only (waits on 2.1a)",
          lambda: rec["open"] == ["parse_tracker_markdown"]
          and rec["open_count"] == 1)
    check("filename/prose skip-stage sites are now advisory",
          lambda: "critique_filename_stage" in rec["advisory"]
          and "inflight_filenames_mtime" in rec["advisory"]
          and "wd2_dhx_haystack" in rec["advisory"]
          and "wd2_uses_inflight_filenames" in rec["advisory"])
    check("COLLECTOR.md is advisory, not skip authority",
          lambda: "collector_md_soft_names" in rec["advisory"])
    check("inflight leases are a primitive",
          lambda: "inflight_leases" in rec["primitive"])
    check("tracker JSON projection is still authority=markdown",
          lambda: '"authority": "markdown"' in
          (REPO / "cosmos" / "cosmos_motif_driver.py").read_text(encoding="utf-8"))
    check("declared site count matches SITES",
          lambda: rec["site_count"] == len(SITES) == 11)
    check("emitted artifact is the audit record",
          lambda: json.loads(EVIDENCE.read_text(encoding="utf-8"))["open_count"]
          == rec["open_count"])

    LIVE_VALUE.update({
        "checks": len(RESULTS),
        "ok": rec["ok"],
        "open_count": rec["open_count"],
        "unreviewed_count": rec["unreviewed_count"],
        "open": rec["open"],
        "advisory": rec["advisory"],
        "primitive": rec["primitive"],
        "artifact": str(EVIDENCE),
    })
    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % (
            "OK  " if ok else "FAIL", label,
            ("  [" + err + "]") if err else ""))
    print("live_value: " + json.dumps(LIVE_VALUE, sort_keys=True))
    print("result: %s  %d/%d" % (
        "ok" if not bad else "FAIL",
        len(RESULTS) - len(bad), len(RESULTS)))
    return 1 if bad else 0


def test_derivation_audit():
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
