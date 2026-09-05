#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""New round-2 backup pins MUST FAIL against the staged predecessor.

Staged at builds/backup/_delme/predispose_unpinned_round2_20260831T133712Z/

    py -3.14 builds/backup/_fail_unpinned_round2_against_old.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "_fail_unpinned_round2_against_old.json"
OLD = HERE / "_delme" / "predispose_unpinned_round2_20260831T133712Z"


def _exec(path: Path, name: str, src: str | None = None):
    mod = types.ModuleType(name)
    mod.__file__ = str(HERE / path.name)
    sys.modules[name] = mod
    text = src if src is not None else path.read_text(encoding="utf-8")
    exec(compile(text, str(path), "exec"), mod.__dict__)
    return mod


def main() -> int:
    failed = []
    ran = []
    old_src = (OLD / "cosmos_backup.py").read_text(encoding="utf-8")
    old = _exec(OLD / "cosmos_backup.py", "cosmos_backup_old_r2", old_src)

    tmp = Path(tempfile.mkdtemp(prefix="cosmos_failold_r2_"))
    try:
        src = tmp / "src"
        src.mkdir()
        (src / "a.txt").write_text("alpha\n", encoding="utf-8", newline="\n")
        dest_file = tmp / "dest_is_file"
        dest_file.write_text("not-a-dir", encoding="utf-8")

        ran.append("DEST_NOT_DIR_dest_is_file")
        try:
            old.do_backup(src, dest_file)
            failed.append("DEST_NOT_DIR_dest_is_file:did_not_raise")
        except old.BackupRefusal as e:
            if e.kind == "DEST_NOT_DIR":
                pass  # unexpected PASS against old
            else:
                failed.append("DEST_NOT_DIR_dest_is_file")
        except Exception:
            failed.append("DEST_NOT_DIR_dest_is_file")

        stripped = old_src.replace('"COPY_IO_ERROR"', '"STRIPPED_COPY_IO_ERROR"')
        old_c = _exec(OLD / "cosmos_backup.py", "cosmos_backup_old_r2c", stripped)
        dst_dir = tmp / "dst_as_dir"
        dst_dir.mkdir()
        (dst_dir / "keep.txt").write_text("PRECIOUS", encoding="utf-8")
        ran.append("COPY_IO_ERROR_onto_dir")
        try:
            old_c._copy(src / "a.txt", dst_dir)
            failed.append("COPY_IO_ERROR_onto_dir:did_not_raise")
        except old_c.BackupRefusal as e:
            if e.kind == "COPY_IO_ERROR":
                pass
            else:
                failed.append("COPY_IO_ERROR_onto_dir")
        except Exception:
            failed.append("COPY_IO_ERROR_onto_dir")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    rec = {
        "schema": "cosmos-bite/1",
        "what": "round2 backup pins FAIL against staged predecessor",
        "old": str(OLD),
        "tests_run": len(ran),
        "failed": len(failed),
        "failed_names": failed,
        "ran_names": ran,
        "all_new_pins_failed": len(failed) == len(ran) and len(ran) > 0,
    }
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
