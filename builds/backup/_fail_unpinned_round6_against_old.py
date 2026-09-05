#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""New round-6 freeze pins MUST FAIL against the staged predecessor.

Staged at builds/backup/_delme/predispose_unpinned_round6_20260831T161207Z/

Predecessor:
  * acquire(handle with read_root+release, no info) returns the handle
  * do_backup(freeze=that handle) AttributeError on handle.info
  * BAD_FREEZE / FREEZE_DEST_OCCUPIED already fire but are unnamed in tests
    (those two kinds are pinned in the suite; they do not discriminate
    the predecessor, so they are not in this fail-old set)

    py -3.14 builds/backup/_fail_unpinned_round6_against_old.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "_fail_unpinned_round6_against_old.json"
OLD = HERE / "_delme" / "predispose_unpinned_round6_20260831T161207Z"


def _exec(path: Path, name: str) -> types.ModuleType:
    mod = types.ModuleType(name)
    mod.__file__ = str(path)
    sys.modules[name] = mod
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"),
         mod.__dict__)
    return mod


class _NoInfo:
    def __init__(self, root):
        self._root = root

    def read_root(self):
        return self._root

    def release(self):
        return None


def main() -> int:
    failed = []
    ran = []
    sys.path.insert(0, str(HERE))
    if not (OLD / "cosmos_backup_freeze.py").is_file():
        raise SystemExit(f"missing predecessor {OLD}")

    old_fz = _exec(OLD / "cosmos_backup_freeze.py", "cosmos_backup_freeze")
    import cosmos_backup as cb                                        # noqa: E402

    tmp = Path(tempfile.mkdtemp(prefix="cosmos_failold_r6_"))
    try:
        src = tmp / "src"
        src.mkdir()
        (src / "a.txt").write_text("x\n", encoding="utf-8", newline="\n")
        dest = tmp / "dest"
        dest.mkdir()

        ran.append("noinfo_acquire_is_BAD_FREEZE")
        try:
            got = old_fz.acquire(src, _NoInfo(src))
            failed.append(
                f"noinfo_acquire_is_BAD_FREEZE:returned:{type(got).__name__}")
        except cb.BackupRefusal as e:
            if e.kind != "BAD_FREEZE":
                failed.append(f"noinfo_acquire_is_BAD_FREEZE:{e.kind}")
            # predecessor raising BAD_FREEZE would mean the pin already lived
        except Exception as e:                                        # noqa: BLE001
            failed.append(f"noinfo_acquire_is_BAD_FREEZE:{type(e).__name__}")

        ran.append("noinfo_dobackup_is_BAD_FREEZE")
        try:
            cb.do_backup(src, dest / "set", freeze=_NoInfo(src))
            failed.append("noinfo_dobackup_is_BAD_FREEZE:did_not_raise")
        except cb.BackupRefusal as e:
            if e.kind != "BAD_FREEZE":
                failed.append(f"noinfo_dobackup_is_BAD_FREEZE:{e.kind}")
        except Exception as e:                                        # noqa: BLE001
            failed.append(f"noinfo_dobackup_is_BAD_FREEZE:{type(e).__name__}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    rec = {
        "schema": "cosmos-bite/1",
        "what": "new round6 freeze pins FAIL against predecessor (no info() gate)",
        "predecessor": str(OLD),
        "tests_run": len(ran),
        "failed_names": failed,
        "ran_names": ran,
        "all_new_pins_failed": (
            len(ran) > 0 and len(failed) == len(ran)
        ),
    }
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
