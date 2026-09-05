#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite F-43 freeze against the incumbent BEFORE the freeze seam.

The named leftover: COVERAGE.md gap 3 is detect-and-refuse SOURCE_MUTATED,
not a frozen tree. do_backup has no freeze parameter; a mutation after
store is SOURCE_MUTATED; there is no module that can hand a point-in-time
read root to the copy.

    py -3.14 builds/backup/_bite_f43_freeze.py
"""
from __future__ import annotations

import importlib.util
import inspect
import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLD = (HERE / "_delme" / "predispose_cosmos_backup_f43_freeze_20260831T151003Z"
       / "cosmos_backup.py")
OUT = HERE / "_bite_f43_freeze.json"
KEY = b"test-hmac-key-not-a-real-secret"


def _load(path: Path):
    spec = importlib.util.spec_from_file_location("cosmos_backup_bite_freeze", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    src_path = OLD if OLD.is_file() else HERE / "cosmos_backup.py"
    cb = _load(src_path)
    rec = {
        "schema": "cosmos-bite/1",
        "what": "F-43 freeze — incumbent has no freeze seam",
        "predecessor": str(src_path),
        "has_freeze_param": "freeze" in inspect.signature(cb.do_backup).parameters,
        "has_freeze_module": (HERE / "cosmos_backup_freeze.py").is_file(),
        "freeze_kw_crash": None,
        "freeze_kw_kind": None,
        "mutated_kind": None,
        "mutated_crash": None,
        "mutated_manifest_sealed": None,
    }
    tmp = Path(tempfile.mkdtemp(prefix="cosmos_bite_f43_freeze_"))
    try:
        src = tmp / "src"
        dest = tmp / "dest"
        src.mkdir()
        (src / "a.txt").write_text("alpha\n", encoding="utf-8", newline="\n")
        try:
            cb.do_backup(src, dest, key=KEY, freeze=True)
            rec["freeze_kw_kind"] = "BACKUP_OK"
        except TypeError as e:
            rec["freeze_kw_crash"] = type(e).__name__
        except Exception as e:  # noqa: BLE001
            rec["freeze_kw_crash"] = type(e).__name__
            rec["freeze_kw_kind"] = getattr(e, "kind", None)

        orig = cb.LocalDirTarget.store

        def after_store(self, rel, src_path):
            orig(self, rel, src_path)
            if rel == "a.txt":
                Path(src_path).write_bytes(b"MUTATED-AFTER-COPY\n")

        cb.LocalDirTarget.store = after_store
        dest2 = tmp / "dest2"
        try:
            cb.do_backup(src, dest2, key=KEY)
            rec["mutated_kind"] = "BACKUP_OK"
        except cb.BackupRefusal as e:
            rec["mutated_kind"] = e.kind
        except Exception as e:  # noqa: BLE001
            rec["mutated_crash"] = type(e).__name__
        finally:
            cb.LocalDirTarget.store = orig
        rec["mutated_manifest_sealed"] = bool(list(dest2.glob("*/MANIFEST.json")))
    finally:
        shutil.rmtree(tmp, True)

    rec["all_bite"] = (
        rec["has_freeze_param"] is False
        and rec["freeze_kw_crash"] == "TypeError"
        and rec["mutated_kind"] == "SOURCE_MUTATED"
        and rec["mutated_manifest_sealed"] is False
        and rec["mutated_crash"] is None
    )
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
