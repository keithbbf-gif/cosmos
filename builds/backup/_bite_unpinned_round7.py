#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: round-7 unpinned backup refusals against CURRENT code.

Round 6b typed seal()/scan_secrets garbage. What still sits next to a
typed path and crashes untyped, or silently iterates a string as
patterns / files:

  * source_drift / _check with files missing / str / list / None
  * _check when a files value is a string, not {sha256,...}
  * is_excluded(rel, "git")          — string iterates as characters
  * is_excluded(rel, 1)              — TypeError
  * canonical_request headers=[] / None
  * local_row(config=[])             — AttributeError
  * parse_excludes(row=[])
  * FrozenTree.capture missing source
  * do_verify of a sealed MANIFEST whose files is a string

Expected before a pin: all_bite == true.

    py -3.14 builds/backup/_bite_unpinned_round7.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = HERE / "_bite_unpinned_round7.json"

import cosmos_backup as cb                                            # noqa: E402
import cosmos_backup_freeze as fz                                     # noqa: E402
import cosmos_backup_r2 as r2                                         # noqa: E402
import cosmos_local_clock as lc                                       # noqa: E402


def _catch(fn):
    try:
        got = fn()
        preview = type(got).__name__
        if got is not None and not isinstance(got, (bool, int)):
            try:
                preview = f"{type(got).__name__}:{str(got)[:80]}"
            except Exception:                                         # noqa: BLE001
                preview = type(got).__name__
        return {"kind": None, "crash": None, "returned": type(got).__name__,
                "value_preview": preview}
    except cb.BackupRefusal as e:
        return {"kind": e.kind, "crash": None, "returned": None,
                "value_preview": None}
    except Exception as e:                                            # noqa: BLE001
        return {"kind": None, "crash": type(e).__name__, "returned": None,
                "value_preview": str(e)[:80]}


def main() -> int:
    rec = {"schema": "cosmos-bite/1",
           "what": "round7 unpinned backup refusals — current vs claimed"}
    tmp = Path(tempfile.mkdtemp(prefix="cosmos_bite7_"))
    try:
        src = tmp / "src"
        src.mkdir()
        (src / "a.txt").write_text("alpha\n", encoding="utf-8", newline="\n")
        dest = tmp / "dest"
        dest.mkdir()

        rec["drift_missing_files"] = _catch(
            lambda: cb.source_drift(src, {}))
        rec["drift_files_str"] = _catch(
            lambda: cb.source_drift(src, {"files": "a.txt"}))
        rec["drift_files_list"] = _catch(
            lambda: cb.source_drift(src, {"files": [{"rel": "a.txt"}]}))
        rec["drift_files_none"] = _catch(
            lambda: cb.source_drift(src, {"files": None}))
        rec["check_files_str"] = _catch(
            lambda: cb._check({"files": "a.txt"}, lambda rel: src / rel))
        rec["check_entry_str"] = _catch(
            lambda: cb._check({"files": {"a.txt": "not-an-entry"}},
                              lambda rel: src / rel))

        rec["exclude_str"] = _catch(lambda: cb.is_excluded("live/git/x", "git"))
        rec["exclude_str_returned"] = rec["exclude_str"].get("returned")
        rec["exclude_int"] = _catch(lambda: cb.is_excluded("a.txt", 1))
        rec["exclude_none"] = _catch(lambda: cb.is_excluded("a.txt", None))

        rec["canon_headers_list"] = _catch(
            lambda: r2.canonical_request("GET", "/b/k", [], "0" * 64))
        rec["canon_headers_none"] = _catch(
            lambda: r2.canonical_request("GET", "/b/k", None, "0" * 64))
        rec["canon_headers_str"] = _catch(
            lambda: r2.canonical_request("GET", "/b/k", "host:x", "0" * 64))

        rec["local_row_list"] = _catch(lambda: lc.local_row([]))
        rec["local_row_none"] = _catch(lambda: lc.local_row(None))
        rec["parse_excludes_list"] = _catch(lambda: lc.parse_excludes([]))
        rec["parse_excludes_str"] = _catch(lambda: lc.parse_excludes("*.lock"))

        missing = tmp / "no_such_src"
        freeze_dest = tmp / "frozen_missing"
        rec["freeze_missing_src"] = _catch(
            lambda: fz.FrozenTree.capture(missing, freeze_dest))

        rec["pem_label_none"] = _catch(lambda: cb.pem_label_kind(None))
        rec["pem_label_str"] = _catch(lambda: cb.pem_label_kind("PRIVATE"))

        # Sealed MANIFEST whose files is a string — check_seal would pass
        # (the body hashes), then _check would crash untyped.
        set_dir = tmp / "set_str_files"
        (set_dir / cb.DATA_DIR).mkdir(parents=True)
        body = {"format": cb.FORMAT, "files": "a.txt", "total_bytes": 0}
        sealed = cb.seal(body)
        (set_dir / cb.MANIFEST_NAME).write_text(
            json.dumps(sealed, indent=2, sort_keys=True), encoding="utf-8")
        rec["verify_files_str"] = _catch(lambda: cb.do_verify(set_dir))

        rec["list_sets_file"] = _catch(
            lambda: cb.list_backup_sets(src / "a.txt"))
        rec["safe_rel_empty"] = _catch(lambda: r2.safe_rel(""))
        rec["safe_rel_dotdot"] = _catch(lambda: r2.safe_rel(".."))
        rec["r2_prefix_dotdot"] = _catch(
            lambda: r2.R2Target(
                r2.R2Credentials("acct", "AKIAFAKE0001",
                                 "SECRET-VALUE-THAT-MUST-NEVER-BE-RENDERED",
                                 "bucket"),
                "..", r2.MemoryTransport()))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    bites = []
    for name, row in rec.items():
        if not isinstance(row, dict):
            continue
        if row.get("crash"):
            bites.append(name)
        elif (row.get("kind") is None and row.get("returned")
              and name.startswith("exclude_str")):
            # string-as-patterns is a silent pass (green-log)
            bites.append(name + ":silent")
    rec["bites"] = bites
    rec["all_bite"] = bool(bites)
    rec["could_not_pin"] = []

    OUT.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    print(json.dumps(rec, indent=2, default=str))
    print("all_bite", rec["all_bite"], "bites", rec["bites"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
