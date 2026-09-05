#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_derivation_audit - CORE_RESTRUCTURE Phase 2 work order 2.3.

Work order 2.3: audit every remaining derivation. State inferred from
filenames, mtimes, or prose is either moved to a primitive (ledger,
registry, inflight leases, tracker JSON) or documented as advisory-only,
the way `soft_names` now is.

This module IS the artifact. It does not flip tracker authority (that is
a human action after 96 consecutive agreeing ticks). It fails closed if
a classified site drifts (symbol gone) or if `write_tracker_json` ever
silently writes authority=json.

    py -3.14 cosmos/cosmos_derivation_audit.py
    py -3.14 tests/test_derivation_audit.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_DEFAULT = HERE / "_f36_derivation_audit.json"
SCHEMA = "cosmos-derivation-audit/1"

# Each site is a derivation of skip / stage / dispatch / authority from
# something other than the four primitives, OR a documented advisory.
# verdict: primitive (reads an owned primitive) | advisory | open.
SITES = (
    {
        "id": "inflight_leases",
        "file": "cosmos_inflight.py",
        "symbol": "class Inflight",
        "kind": "primitive",
        "verdict": "primitive",
        "note": "Owned expiring leases. Work order 2.x inflight primitive.",
    },
    {
        "id": "tracker_json_projection",
        "file": "cosmos_motif_driver.py",
        "symbol": "def write_tracker_json",
        "kind": "prose",
        "verdict": "advisory",
        "must_contain": '"authority": "markdown"',
        "note": "JSON is a projection. authority is hard-coded markdown; "
                "flip is advice (flip_ready), never an action.",
    },
    {
        "id": "agreement_streak",
        "file": "cosmos_motif_driver.py",
        "symbol": "def record_agreement",
        "kind": "prose",
        "verdict": "advisory",
        "must_contain": "flip_ready",
        "note": "Streak is evidence for a human. Nothing here flips authority.",
    },
    {
        "id": "collector_md_soft_names",
        "file": "cosmos_motif_driver.py",
        "symbol": "soft_names",
        "kind": "prose",
        "verdict": "advisory",
        "must_contain": "cannot decide a skip",
        "note": "COLLECTOR.md is counted, never used to skip (scar 2026-08-30).",
    },
    {
        "id": "parse_tracker_markdown",
        "file": "cosmos_motif_driver.py",
        "symbol": "def parse_tracker",
        "kind": "prose",
        "verdict": "open",
        "note": "Work order 2.2 unfinished: still parses MOTIF_TRACKER.md. "
                "JSON-authority parse waits on the human flip.",
    },
    {
        "id": "critique_filename_stage",
        "file": "cosmos_motif_driver.py",
        "symbol": "def critique_exists",
        "kind": "filename",
        "verdict": "advisory",
        "must_contain": "cannot lift",
        "note": "critique_exists is counted; effective_stage does not lift "
                "current_stage from a critique filename.",
    },
    {
        "id": "inflight_filenames_mtime",
        "file": "cosmos_motif_driver.py",
        "symbol": "def inflight_filenames",
        "kind": "filename+mtime",
        "verdict": "advisory",
        "must_contain": "cannot decide a skip",
        "note": "Queue filenames still scraped as an advisory count; skip is "
                "leases + ledger.",
    },
    {
        "id": "ledger_inflight_derived",
        "file": "cosmos_motif_driver.py",
        "symbol": "def ledger_inflight",
        "kind": "primitive",
        "verdict": "primitive",
        "note": "Reads runner/lane ledgers (a primitive). Unioned into skip "
                "as belt-and-braces, not as a filename scrape.",
    },
    {
        "id": "wd2_dhx_haystack",
        "file": "cosmos_watchdog2_scan.py",
        "symbol": "def dhx_haystack",
        "kind": "prose",
        "verdict": "advisory",
        "must_contain": "cannot decide a skip",
        "note": "dhx_haystack still folds the log; name_hit no longer returns "
                "dhx: — assignment-log prose cannot decide a skip.",
    },
    {
        "id": "wd2_uses_inflight_filenames",
        "file": "cosmos_watchdog2.py",
        "symbol": "inflight_filenames",
        "kind": "filename+mtime",
        "verdict": "advisory",
        "must_contain": "cannot decide a skip",
        "note": "scan_once still calls inflight_filenames as an advisory "
                "count; skip is leases + ledger.",
    },
    {
        "id": "index_parse_tracker",
        "file": "cosmos_index.py",
        "symbol": "def parse_tracker",
        "kind": "prose",
        "verdict": "advisory",
        "note": "Index display parse of MOTIF_TRACKER.md. Rebuildable "
                "projection; not a skip/dispatch authority.",
    },
)


def audit(cosmos_dir: Path | None = None) -> dict:
    cosmos_dir = Path(cosmos_dir or HERE)
    hits = []
    unreviewed = []
    for site in SITES:
        path = cosmos_dir / site["file"]
        rec = dict(site)
        rec["path"] = str(path)
        if not path.is_file():
            rec["ok"] = False
            rec["detail"] = "FILE_ABSENT"
            unreviewed.append(rec["id"])
            hits.append(rec)
            continue
        text = path.read_text(encoding="utf-8")
        if site["symbol"] not in text:
            rec["ok"] = False
            rec["detail"] = "SYMBOL_ABSENT"
            unreviewed.append(rec["id"])
            hits.append(rec)
            continue
        extra = site.get("must_contain")
        if extra and extra not in text:
            rec["ok"] = False
            rec["detail"] = "MUST_CONTAIN_ABSENT"
            unreviewed.append(rec["id"])
            hits.append(rec)
            continue
        rec["ok"] = True
        rec["detail"] = "classified"
        hits.append(rec)

    open_ids = [h["id"] for h in hits if h.get("verdict") == "open" and h.get("ok")]
    advisory_ids = [h["id"] for h in hits if h.get("verdict") == "advisory" and h.get("ok")]
    primitive_ids = [h["id"] for h in hits if h.get("verdict") == "primitive" and h.get("ok")]
    ok = not unreviewed
    return {
        "schema": SCHEMA,
        "ok": ok,
        "work_order": "2.3",
        "authority_flip": "not this artifact — human lands json after 96 agreeing ticks",
        "sites": hits,
        "site_count": len(hits),
        "open": open_ids,
        "advisory": advisory_ids,
        "primitive": primitive_ids,
        "unreviewed": unreviewed,
        "open_count": len(open_ids),
        "unreviewed_count": len(unreviewed),
    }


def main() -> int:
    rec = audit()
    OUT_DEFAULT.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": rec["ok"],
        "open_count": rec["open_count"],
        "unreviewed_count": rec["unreviewed_count"],
        "open": rec["open"],
        "artifact": str(OUT_DEFAULT),
    }, indent=2))
    return 0 if rec["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
