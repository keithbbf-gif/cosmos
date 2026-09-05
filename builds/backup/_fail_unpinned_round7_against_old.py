#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""New round-7 pins MUST FAIL against the staged predecessor.

Staged at builds/backup/_delme/predispose_unpinned_round7_20260831T174500Z/

Predecessor (measured `_bite_unpinned_round7.json`):
  * source_drift({})                         — KeyError
  * source_drift({"files": "a.txt"})         — AttributeError
  * _check files-str / entry-str             — AttributeError / TypeError
  * is_excluded(..., "git")                  — silent bool
  * is_excluded(..., 1)                      — TypeError
  * canonical_request headers=[]/None/"x"    — AttributeError
  * local_row([]) / parse_excludes([])       — AttributeError
  * pem_label_kind(None)                     — TypeError
  * pem_label_kind("PRIVATE KEY")            — "ambiguous" (characters)

    py -3.14 builds/backup/_fail_unpinned_round7_against_old.py
"""
from __future__ import annotations

import json
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "_fail_unpinned_round7_against_old.json"
OLD = HERE / "_delme" / "predispose_unpinned_round7_20260831T174500Z"


def _exec(path: Path, name: str) -> types.ModuleType:
    mod = types.ModuleType(name)
    mod.__file__ = str(path)
    sys.modules[name] = mod
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"),
         mod.__dict__)
    return mod


def main() -> int:
    failed = []
    ran = []
    sys.path.insert(0, str(HERE))
    if not (OLD / "cosmos_backup.py").is_file():
        raise SystemExit(f"missing predecessor {OLD}")

    old_cb = _exec(OLD / "cosmos_backup.py", "cosmos_backup")
    old_r2_src = (OLD / "cosmos_backup_r2.py").read_text(encoding="utf-8")
    old_r2 = types.ModuleType("cosmos_backup_r2")
    old_r2.__file__ = str(OLD / "cosmos_backup_r2.py")
    sys.modules["cosmos_backup_r2"] = old_r2
    exec(compile(old_r2_src, str(OLD / "cosmos_backup_r2.py"), "exec"),
         old_r2.__dict__)
    old_lc = _exec(OLD / "cosmos_local_clock.py", "cosmos_local_clock")

    def _want_kind(label, fn, kind):
        ran.append(label)
        try:
            got = fn()
            failed.append(f"{label}:returned:{type(got).__name__}:{got!r}"[:140])
        except old_cb.BackupRefusal as e:
            if e.kind != kind:
                failed.append(f"{label}:{e.kind}")
        except Exception as e:                                        # noqa: BLE001
            failed.append(f"{label}:{type(e).__name__}")

    def _want_eq(label, fn, expected):
        ran.append(label)
        try:
            got = fn()
            if got != expected:
                failed.append(f"{label}:got:{got!r}")
        except Exception as e:                                        # noqa: BLE001
            failed.append(f"{label}:{type(e).__name__}")

    src = HERE  # unused; drift crashes before reading
    _want_kind("drift_missing_files_is_NOT_A_BACKUP_SET",
               lambda: old_cb.source_drift(src, {}), "NOT_A_BACKUP_SET")
    _want_kind("drift_files_str_is_NOT_A_BACKUP_SET",
               lambda: old_cb.source_drift(src, {"files": "a.txt"}),
               "NOT_A_BACKUP_SET")
    _want_kind("check_files_str_is_NOT_A_BACKUP_SET",
               lambda: old_cb._check({"files": "a.txt"}, lambda rel: src / rel),
               "NOT_A_BACKUP_SET")
    _want_kind("check_entry_str_is_NOT_A_BACKUP_SET",
               lambda: old_cb._check({"files": {"a.txt": "not-an-entry"}},
                                     lambda rel: src / rel),
               "NOT_A_BACKUP_SET")
    _want_kind("exclude_str_is_BAD_EXCLUDES",
               lambda: old_cb.is_excluded("live/git/x", "git"), "BAD_EXCLUDES")
    _want_kind("exclude_int_is_BAD_EXCLUDES",
               lambda: old_cb.is_excluded("a.txt", 1), "BAD_EXCLUDES")
    _want_kind("headers_list_is_BAD_HEADERS",
               lambda: old_r2.canonical_request("GET", "/b/k", [], "0" * 64),
               "BAD_HEADERS")
    _want_kind("headers_none_is_BAD_HEADERS",
               lambda: old_r2.canonical_request("GET", "/b/k", None, "0" * 64),
               "BAD_HEADERS")
    _want_kind("local_row_list_is_BAD_CONFIG",
               lambda: old_lc.local_row([]), "BAD_CONFIG")
    _want_kind("parse_excludes_list_is_BAD_CONFIG",
               lambda: old_lc.parse_excludes([]), "BAD_CONFIG")
    _want_eq("pem_label_none_is_ambiguous",
             lambda: old_cb.pem_label_kind(None), "ambiguous")
    _want_eq("pem_label_str_is_one_label",
             lambda: old_cb.pem_label_kind("PRIVATE KEY"), "private")

    rec = {
        "schema": "cosmos-fail-old/1",
        "what": "round7 unpinned backup pins against predecessor",
        "predecessor": str(OLD),
        "ran": ran,
        "failed": failed,
        "n_ran": len(ran),
        "n_failed": len(failed),
        "all_new_pins_failed": bool(failed) and len(failed) == len(ran),
    }
    OUT.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    print(json.dumps(rec, indent=2, default=str))
    print(f"{len(failed)}/{len(ran)} FAIL  all_new_pins_failed={rec['all_new_pins_failed']}")
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
