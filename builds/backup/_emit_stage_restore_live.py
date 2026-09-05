#!/usr/bin/env python3
"""Emit live kinds for the newly pinned restore claims. Scratch only."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

import cosmos_backup as cb

HERE = Path(__file__).resolve().parent
OUT = HERE / "_stage_restore_live.json"
KEY = b"live-stage-key-not-a-secret"


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="cosmos_stage_restore_live_"))
    rec = {"schema": "cosmos-live/1", "kinds": {}}
    try:
        src = tmp / "src"
        dest = tmp / "dest"
        src.mkdir()
        dest.mkdir()
        (src / "a.txt").write_text("alpha\n", encoding="utf-8", newline="\n")
        set_dir = cb.do_backup(src, dest, key=KEY)

        live = tmp / "live"
        live.mkdir()
        (live / "a.txt").write_text("LIVE\n", encoding="utf-8", newline="\n")
        stage = tmp / "stage"
        stage.mkdir()
        (stage / "a.txt").write_text("PRECIOUS\n", encoding="utf-8", newline="\n")
        try:
            cb.do_restore(set_dir, live, KEY, stage)
            rec["kinds"]["STAGE_OCCUPIED"] = "PASSED"
        except cb.BackupRefusal as e:
            rec["kinds"]["STAGE_OCCUPIED"] = e.kind
            rec["stage_untouched"] = (stage / "a.txt").read_text(encoding="utf-8") == "PRECIOUS\n"
            rec["dest_untouched"] = (live / "a.txt").read_text(encoding="utf-8") == "LIVE\n"

        orig = cb.LocalDirTarget.retrieve

        def flip(self, rel, dst):
            orig(self, rel, dst)
            p = Path(dst)
            blob = bytearray(p.read_bytes())
            if blob:
                blob[0] ^= 0xFF
                p.write_bytes(bytes(blob))

        cb.LocalDirTarget.retrieve = flip
        try:
            live2 = tmp / "live2"
            live2.mkdir()
            (live2 / "a.txt").write_text("LIVE2\n", encoding="utf-8", newline="\n")
            try:
                cb.do_restore(set_dir, live2, KEY, tmp / "stage2")
                rec["kinds"]["RESTORE_HASH_MISMATCH"] = "PASSED"
            except cb.BackupRefusal as e:
                rec["kinds"]["RESTORE_HASH_MISMATCH"] = e.kind
            try:
                cb.do_rehearse(set_dir, tmp / "scratch2", KEY)
                rec["kinds"]["REHEARSAL_HASH_MISMATCH"] = "PASSED"
            except cb.BackupRefusal as e:
                rec["kinds"]["REHEARSAL_HASH_MISMATCH"] = e.kind
        finally:
            cb.LocalDirTarget.retrieve = orig

        notdir = tmp / "not_a_dir.txt"
        notdir.write_text("file\n", encoding="utf-8", newline="\n")
        try:
            cb.build_manifest(notdir)
            rec["kinds"]["SOURCE_NOT_DIR"] = "PASSED"
        except cb.BackupRefusal as e:
            rec["kinds"]["SOURCE_NOT_DIR"] = e.kind

        empty = tmp / "emptyset"
        empty.mkdir()
        try:
            cb.LocalDirTarget(empty)
            rec["kinds"]["NOT_A_BACKUP_SET"] = "PASSED"
        except cb.BackupRefusal as e:
            rec["kinds"]["NOT_A_BACKUP_SET"] = e.kind
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    rec["ok"] = rec["kinds"] == {
        "STAGE_OCCUPIED": "STAGE_OCCUPIED",
        "RESTORE_HASH_MISMATCH": "RESTORE_HASH_MISMATCH",
        "REHEARSAL_HASH_MISMATCH": "REHEARSAL_HASH_MISMATCH",
        "SOURCE_NOT_DIR": "SOURCE_NOT_DIR",
        "NOT_A_BACKUP_SET": "NOT_A_BACKUP_SET",
    }
    sys.path.insert(0, str(HERE.parent / "probe"))
    import artifact_freshness as af                                    # noqa: WPS433
    af.write_stamped(OUT, rec, HERE.parents[1],
                     ["builds/backup/cosmos_backup.py"])
    print(json.dumps(rec, indent=2))
    return 0 if rec["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
