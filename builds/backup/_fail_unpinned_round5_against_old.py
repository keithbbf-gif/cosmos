#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""New round-5 backup pins MUST FAIL against the staged predecessor.

Staged at builds/backup/_delme/predispose_unpinned_round5_20260831T143821Z/

Predecessor:
  * check_seal([]) AttributeError
  * check_seal seal-as-string AttributeError
  * LocalDirTarget.get_artifact garbage JSON JSONDecodeError
  * LocalDirTarget.get_artifact [] returns a list
  * R2Target.get_artifact garbage JSON JSONDecodeError

    py -3.14 builds/backup/_fail_unpinned_round5_against_old.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "_fail_unpinned_round5_against_old.json"
OLD = HERE / "_delme" / "predispose_unpinned_round5_20260831T143821Z"


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
    old_cb = _exec(OLD / "cosmos_backup.py", "cb_old_r5")
    # r2 imports cosmos_backup by name; point it at the staged module.
    sys.modules["cosmos_backup"] = old_cb
    old_r2 = _exec(OLD / "cosmos_backup_r2.py", "r2_old_r5")

    tmp = Path(tempfile.mkdtemp(prefix="cosmos_failold_r5_"))
    try:
        ran.append("check_seal_array_is_NO_SEAL")
        try:
            old_cb.check_seal([])
            failed.append("check_seal_array_is_NO_SEAL:did_not_raise")
        except old_cb.BackupRefusal as e:
            if e.kind != "NO_SEAL":
                failed.append(f"check_seal_array_is_NO_SEAL:{e.kind}")
            # predecessor raising NO_SEAL would mean the pin already lived
        except Exception as e:                                        # noqa: BLE001
            failed.append(f"check_seal_array_is_NO_SEAL:{type(e).__name__}")

        sealed = old_cb.seal({"n": 1})
        bad = dict(sealed)
        bad["seal"] = "not-an-object"
        ran.append("check_seal_str_is_NO_SEAL")
        try:
            old_cb.check_seal(bad)
            failed.append("check_seal_str_is_NO_SEAL:did_not_raise")
        except old_cb.BackupRefusal as e:
            if e.kind != "NO_SEAL":
                failed.append(f"check_seal_str_is_NO_SEAL:{e.kind}")
        except Exception as e:                                        # noqa: BLE001
            failed.append(f"check_seal_str_is_NO_SEAL:{type(e).__name__}")

        set_dir = tmp / "set"
        (set_dir / old_cb.DATA_DIR).mkdir(parents=True)
        (set_dir / old_cb.MANIFEST_NAME).write_text("{not json", encoding="utf-8")
        target = old_cb.LocalDirTarget(set_dir)
        ran.append("local_garbage_is_NOT_A_BACKUP_SET")
        try:
            target.get_artifact(old_cb.MANIFEST_NAME)
            failed.append("local_garbage_is_NOT_A_BACKUP_SET:did_not_raise")
        except old_cb.BackupRefusal as e:
            if e.kind != "NOT_A_BACKUP_SET":
                failed.append(f"local_garbage_is_NOT_A_BACKUP_SET:{e.kind}")
        except Exception as e:                                        # noqa: BLE001
            failed.append(f"local_garbage_is_NOT_A_BACKUP_SET:{type(e).__name__}")

        (set_dir / old_cb.MANIFEST_NAME).write_text("[]", encoding="utf-8")
        ran.append("local_array_is_NOT_A_BACKUP_SET")
        try:
            got = target.get_artifact(old_cb.MANIFEST_NAME)
            failed.append(f"local_array_is_NOT_A_BACKUP_SET:returned_{type(got).__name__}")
        except old_cb.BackupRefusal as e:
            if e.kind != "NOT_A_BACKUP_SET":
                failed.append(f"local_array_is_NOT_A_BACKUP_SET:{e.kind}")
        except Exception as e:                                        # noqa: BLE001
            failed.append(f"local_array_is_NOT_A_BACKUP_SET:{type(e).__name__}")

        tp = old_r2.MemoryTransport()
        creds = old_r2.R2Credentials(
            "acct1234", "AKIAFAKE0001",
            "SECRET-VALUE-THAT-MUST-NEVER-BE-RENDERED", "cosmos-bucket")
        rt = old_r2.R2Target(creds, "cosmos", tp)
        rt.put_artifact(old_cb.MANIFEST_NAME, {"n": 1})
        for k in list(tp.objects):
            tp.objects[k] = b"{not json"
        ran.append("r2_garbage_is_NOT_A_BACKUP_SET")
        try:
            rt.get_artifact(old_cb.MANIFEST_NAME)
            failed.append("r2_garbage_is_NOT_A_BACKUP_SET:did_not_raise")
        except old_r2.BackupRefusal as e:
            if e.kind != "NOT_A_BACKUP_SET":
                failed.append(f"r2_garbage_is_NOT_A_BACKUP_SET:{e.kind}")
        except Exception as e:                                        # noqa: BLE001
            failed.append(f"r2_garbage_is_NOT_A_BACKUP_SET:{type(e).__name__}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        sys.modules.pop("cosmos_backup", None)

    rec = {
        "schema": "cosmos-fail-old/1",
        "what": "round5 backup pins against predecessor",
        "ran": ran,
        "failed": failed,
        "n_ran": len(ran),
        "n_failed": len(failed),
        "all_new_pins_failed": len(failed) == len(ran) and len(ran) > 0,
    }
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1))
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
