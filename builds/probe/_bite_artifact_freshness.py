#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: claim-backing artifacts had no source fingerprint.

Required before belief. Against the CURRENT (pre-stamp) artifacts this
must be all_bite:true:

  * dated longpath JSON has no describes (UNFINGERPRINTED)
  * hmac live JSON names cosmos_backup.py but does not hash it
  * cosmos_backup.py is NEWER than the longpath measurement
  * a planted wrong-hash fixture is STALE
  * a planted matching fixture is MATCH

    py -3.14 builds/probe/_bite_artifact_freshness.py
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

import artifact_freshness as af                                         # noqa: E402

OUT = HERE / "_bite_artifact_freshness.json"


def _mtime(p: Path) -> float:
    return p.stat().st_mtime


def main() -> int:
    dated = REPO / "builds/probe/_longpath_behaviour_20260831T0700Z.json"
    hmac = REPO / "builds/backup/_hmac_copyhash_live.json"
    src = REPO / "builds/backup/cosmos_backup.py"
    rec: dict = {
        "schema": "cosmos-bite/1",
        "what": "claim artifacts unfingerprinted; source newer than measurement",
    }

    dated_doc = json.loads(dated.read_text(encoding="utf-8")) if dated.is_file() else {}
    rec["dated_longpath_present"] = dated.is_file()
    rec["dated_longpath_has_describes"] = bool(dated_doc.get("describes"))
    rec["dated_longpath_kind"] = af.compare(
        dated_doc.get("describes"),
        af.fingerprint(REPO, ["builds/backup/cosmos_backup.py"]),
    )["kind"]

    hmac_doc = json.loads(hmac.read_text(encoding="utf-8")) if hmac.is_file() else {}
    rec["hmac_names_file"] = "cosmos_backup.py" in str(hmac_doc.get("check_seal_file") or "")
    rec["hmac_has_describes"] = bool(hmac_doc.get("describes"))
    rec["hmac_kind"] = af.compare(
        hmac_doc.get("describes"),
        af.fingerprint(REPO, ["builds/backup/cosmos_backup.py"]),
    )["kind"]

    rec["backup_src_newer_than_dated_longpath"] = (
        dated.is_file() and src.is_file() and _mtime(src) > _mtime(dated)
    )
    rec["backup_src_mtime_utc"] = datetime.fromtimestamp(
        _mtime(src), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if src.is_file() else None
    rec["dated_longpath_mtime_utc"] = datetime.fromtimestamp(
        _mtime(dated), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if dated.is_file() else None
    rec["backup_src_bytes"] = src.stat().st_size if src.is_file() else None

    td = Path(tempfile.mkdtemp(prefix="cosmos_fresh_bite_"))
    try:
        (td / "builds/backup").mkdir(parents=True)
        (td / "builds/probe").mkdir(parents=True)
        body = b"THIS-IS-NOT-THE-LIVE-BACKUP-MODULE\n"
        planted_src = td / "builds/backup/cosmos_backup.py"
        planted_src.write_bytes(body)
        live_fp = af.fingerprint(td, ["builds/backup/cosmos_backup.py"])
        wrong = {"builds/backup/cosmos_backup.py": {
            "exists": True, "bytes": 1, "sha256": "0" * 64}}
        rec["planted_wrong_kind"] = af.compare(wrong, live_fp)["kind"]
        rec["planted_match_kind"] = af.compare(live_fp, live_fp)["kind"]
        rec["planted_absent_kind"] = af.compare(None, live_fp)["kind"]
    finally:
        # never-delete is for the live tree; OS temp is the throwaway.
        import shutil
        shutil.rmtree(td, ignore_errors=True)

    rec["all_bite"] = (
        rec["dated_longpath_present"] is True
        and rec["dated_longpath_has_describes"] is False
        and rec["dated_longpath_kind"] == "UNFINGERPRINTED"
        and rec["hmac_names_file"] is True
        and rec["hmac_has_describes"] is False
        and rec["hmac_kind"] == "UNFINGERPRINTED"
        and rec["backup_src_newer_than_dated_longpath"] is True
        and rec["planted_wrong_kind"] == "STALE"
        and rec["planted_match_kind"] == "MATCH"
        and rec["planted_absent_kind"] == "UNFINGERPRINTED"
    )
    OUT.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8", newline="\n")
    print(json.dumps(rec, indent=2, sort_keys=True))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
