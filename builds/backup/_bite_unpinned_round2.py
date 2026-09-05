#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: round-2 unpinned backup refusals against CURRENT (pre-change) code.

  * do_backup dest-is-a-file is an untyped FileNotFoundError (DEST_NOT_DIR
    is in the kind set and in list_backup_sets / do_retire, unpinned on
    the write path).
  * _copy onto an existing directory already raises COPY_IO_ERROR (the
    OSError wrapper), but no test named dest-is-dir.

    py -3.14 builds/backup/_bite_unpinned_round2.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = HERE / "_bite_unpinned_round2.json"

import cosmos_backup as cb                                            # noqa: E402


def main() -> int:
    rec: dict = {
        "schema": "cosmos-bite/1",
        "what": "round2 unpinned backup refusals — dest-is-file / copy-onto-dir",
        "all_bite": False,
    }
    tmp = Path(tempfile.mkdtemp(prefix="cosmos_bite2_"))
    try:
        src = tmp / "src"
        src.mkdir()
        (src / "a.txt").write_text("alpha\n", encoding="utf-8", newline="\n")

        dest_file = tmp / "dest_is_file"
        dest_file.write_text("not-a-dir", encoding="utf-8")
        try:
            cb.do_backup(src, dest_file)
            rec["dest_file_old_kind"] = None
            rec["dest_file_old_crash"] = None
        except cb.BackupRefusal as e:
            rec["dest_file_old_kind"] = e.kind
            rec["dest_file_old_crash"] = None
        except Exception as e:                                        # noqa: BLE001
            rec["dest_file_old_kind"] = None
            rec["dest_file_old_crash"] = type(e).__name__
            rec["dest_file_old_detail"] = str(e)[:200]

        dst_dir = tmp / "dst_as_dir"
        dst_dir.mkdir()
        (dst_dir / "keep.txt").write_text("PRECIOUS", encoding="utf-8")
        try:
            cb._copy(src / "a.txt", dst_dir)
            rec["copy_onto_dir_old_kind"] = None
            rec["copy_onto_dir_old_crash"] = None
        except cb.BackupRefusal as e:
            rec["copy_onto_dir_old_kind"] = e.kind
            rec["copy_onto_dir_old_crash"] = None
        except Exception as e:                                        # noqa: BLE001
            rec["copy_onto_dir_old_kind"] = None
            rec["copy_onto_dir_old_crash"] = type(e).__name__
            rec["copy_onto_dir_detail"] = str(e)[:200]
        rec["copy_onto_dir_precious_survived"] = (
            (dst_dir / "keep.txt").read_text(encoding="utf-8") == "PRECIOUS"
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    rec["all_bite"] = (
        rec.get("dest_file_old_crash") == "FileNotFoundError"
        and rec.get("dest_file_old_kind") is None
        and rec.get("copy_onto_dir_old_kind") == "COPY_IO_ERROR"
        and rec.get("copy_onto_dir_precious_survived") is True
    )
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
