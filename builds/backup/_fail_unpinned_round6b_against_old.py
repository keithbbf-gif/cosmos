#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""New round-6b pins MUST FAIL against the staged predecessor.

Staged at builds/backup/_delme/predispose_unpinned_round6b_20260831T161500Z/

Predecessor (measured `_bite_unpinned_round6.json`):
  * seal([]) / seal(None) / seal("x")  — AttributeError
  * scan_secrets({})                   — KeyError
  * scan_secrets([])                   — TypeError
  * scan_secrets({"files": "install_key.bin"}) — silent []
  * scan_secrets({"files": None})      — TypeError

    py -3.14 builds/backup/_fail_unpinned_round6b_against_old.py
"""
from __future__ import annotations

import json
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "_fail_unpinned_round6b_against_old.json"
OLD = HERE / "_delme" / "predispose_unpinned_round6b_20260831T161500Z"


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

    # Live BackupRefusal so isinstance checks in the old module still work
    # when it raises... old seal doesn't raise, it crashes.
    old_cb = _exec(OLD / "cosmos_backup.py", "cosmos_backup")
    # r2 imports cosmos_backup at load; point it at the staged sibling.
    old_r2_src = (OLD / "cosmos_backup_r2.py").read_text(encoding="utf-8")
    old_r2 = types.ModuleType("cosmos_backup_r2")
    old_r2.__file__ = str(OLD / "cosmos_backup_r2.py")
    sys.modules["cosmos_backup_r2"] = old_r2
    # The staged r2 `import cosmos_backup as cb` will hit sys.modules we just
    # loaded as cosmos_backup (the OLD one). That is the predecessor.
    exec(compile(old_r2_src, str(OLD / "cosmos_backup_r2.py"), "exec"),
         old_r2.__dict__)

    def _want_kind(label, fn, kind):
        ran.append(label)
        try:
            got = fn()
            failed.append(f"{label}:returned:{type(got).__name__}:{got!r}"[:120])
        except old_cb.BackupRefusal as e:
            if e.kind != kind:
                failed.append(f"{label}:{e.kind}")
            # predecessor raising the new kind would mean the pin already lived
        except Exception as e:                                        # noqa: BLE001
            failed.append(f"{label}:{type(e).__name__}")

    _want_kind("seal_array_is_NO_SEAL", lambda: old_cb.seal([]), "NO_SEAL")
    _want_kind("seal_none_is_NO_SEAL", lambda: old_cb.seal(None), "NO_SEAL")
    _want_kind("seal_str_is_NO_SEAL", lambda: old_cb.seal("x"), "NO_SEAL")
    _want_kind("scan_empty_obj_is_NOT_A_BACKUP_SET",
               lambda: old_cb.scan_secrets({}), "NOT_A_BACKUP_SET")
    _want_kind("scan_array_is_NOT_A_BACKUP_SET",
               lambda: old_cb.scan_secrets([]), "NOT_A_BACKUP_SET")
    _want_kind("scan_files_str_is_NOT_A_BACKUP_SET",
               lambda: old_r2.scan_secrets({"files": "install_key.bin"}),
               "NOT_A_BACKUP_SET")
    _want_kind("scan_files_none_is_NOT_A_BACKUP_SET",
               lambda: old_r2.scan_secrets({"files": None}),
               "NOT_A_BACKUP_SET")
    _want_kind("scan_files_int_is_NOT_A_BACKUP_SET",
               lambda: old_r2.scan_secrets({"files": 1}),
               "NOT_A_BACKUP_SET")

    rec = {
        "schema": "cosmos-bite/1",
        "what": "new round6b seal/scan pins FAIL against predecessor",
        "predecessor": str(OLD),
        "tests_run": len(ran),
        "failed_names": failed,
        "ran_names": ran,
        "all_new_pins_failed": (len(ran) > 0 and len(failed) == len(ran)),
    }
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
