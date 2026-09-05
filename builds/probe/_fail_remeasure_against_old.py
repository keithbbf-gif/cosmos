#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fail-against-old: the freshness detector shipped without a remesure loop.

Required before belief. Points at the never-delete incumbents staged
BEFORE remeasure_claims.py existed. Those copies must still:

  * have a STALE longpath artefact (the detector can fail)
  * have a test_artifact_freshness.py that does not call refresh_if_stale
  * contain no remeasure_claims.py

    py -3.14 builds/probe/_fail_remeasure_against_old.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

import artifact_freshness as af                                         # noqa: E402

STAGED = HERE / "_delme" / "predispose_stale_claims_20260831T152926Z"
OUT = HERE / "_fail_remeasure_against_old.json"


def main() -> int:
    old_test = ""
    old_test_path = STAGED / "test_artifact_freshness.py"
    if old_test_path.is_file():
        old_test = old_test_path.read_text(encoding="utf-8")
    longpath = STAGED / "_longpath_behaviour.json"
    live = af.fingerprint(REPO, (
        "cosmos/cosmos_backup.py",
        "cosmos/cosmos_backup_clock.py",
        "builds/backup/cosmos_backup.py",
    ))
    rec = json.loads(longpath.read_text(encoding="utf-8")) if longpath.is_file() else {}
    compared = af.compare(rec.get("describes"), live)
    doc = {
        "schema": "cosmos-fail-against-old/1",
        "what": "claim remesure loop was absent; staged longpath is STALE",
        "staged": str(STAGED),
        "old_freshness_has_refresh_if_stale": "refresh_if_stale" in old_test,
        "old_freshness_imports_remeasure_claims": "remeasure_claims" in old_test,
        "staged_remeasure_claims_present": (STAGED / "remeasure_claims.py").is_file(),
        "staged_longpath_present": longpath.is_file(),
        "staged_longpath_kind": compared.get("kind"),
        "staged_longpath_drift": compared.get("drift") or [],
        "staged_longpath_recorded_backup_bytes": (
            (rec.get("describes") or {}).get("cosmos/cosmos_backup.py") or {}
        ).get("bytes"),
        "live_backup_bytes": (live.get("cosmos/cosmos_backup.py") or {}).get("bytes"),
    }
    doc["all_new_pins_failed"] = (
        doc["old_freshness_has_refresh_if_stale"] is False
        and doc["old_freshness_imports_remeasure_claims"] is False
        and doc["staged_remeasure_claims_present"] is False
        and doc["staged_longpath_present"] is True
        and doc["staged_longpath_kind"] == "STALE"
        and "cosmos/cosmos_backup.py" in doc["staged_longpath_drift"]
    )
    OUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8", newline="\n")
    print(json.dumps(doc, indent=2, sort_keys=True))
    return 0 if doc["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
