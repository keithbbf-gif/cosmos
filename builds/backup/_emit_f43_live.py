#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Live (scratch) values for F-43 SOURCE_MUTATED + do_retire.

Never points at live/backups. Never reads a credential. Output:
`builds/backup/_f43_mutate_retire_live.json`.

    py -3.14 builds/backup/_emit_f43_live.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

import cosmos_backup as cb

HERE = Path(__file__).resolve().parent
OUT = HERE / "_f43_mutate_retire_live.json"
KEY = b"test-hmac-key-not-a-real-secret"


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="cosmos_f43_live_"))
    rec = {"schema": "cosmos-backup-live/1", "scratch": str(tmp)}
    try:
        src = tmp / "src"
        dest = tmp / "dest"
        (src / "nested").mkdir(parents=True)
        (src / "a.txt").write_text("alpha\n", encoding="utf-8", newline="\n")
        (src / "nested" / "b.bin").write_bytes(b"bravo")

        orig = cb.LocalDirTarget.store

        def after_store(self, rel, src_path):
            orig(self, rel, src_path)
            if rel == "a.txt":
                Path(src_path).write_bytes(b"MUTATED-AFTER-COPY\n")

        cb.LocalDirTarget.store = after_store
        try:
            cb.do_backup(src, dest, key=KEY)
            rec["mutated_kind"] = "BACKUP_OK"
            rec["mutated_crash"] = None
        except cb.BackupRefusal as e:
            rec["mutated_kind"] = e.kind
            rec["mutated_crash"] = None
        except Exception as e:  # noqa: BLE001
            rec["mutated_kind"] = None
            rec["mutated_crash"] = type(e).__name__
        finally:
            cb.LocalDirTarget.store = orig

        rec["manifest_sealed"] = bool(list(dest.glob("*/MANIFEST.json")))
        rec["incident_kinds"] = []
        for p in dest.glob("*/INCIDENT-*.json"):
            rec["incident_kinds"].append(
                json.loads(p.read_text(encoding="utf-8"))["kind"])
        rec["incomplete_left"] = any(
            p.is_dir() and (p / cb.DATA_DIR).is_dir()
            and not (p / cb.MANIFEST_NAME).is_file()
            for p in dest.iterdir() if p.is_dir()
        )

        # restore a.txt so subsequent backups can seal
        (src / "a.txt").write_text("alpha\n", encoding="utf-8", newline="\n")
        sets = []
        for i in range(3):
            (src / "a.txt").write_text(f"gen-{i}\n", encoding="utf-8",
                                       newline="\n")
            sets.append(cb.do_backup(src, dest, key=KEY))
        rec["sets_before_retire"] = len(cb.list_backup_sets(dest))
        receipt = cb.do_retire(dest, 2, key=KEY)
        rec["retire_kind"] = receipt["kind"]
        rec["never_deleted"] = receipt["never_deleted"]
        rec["retired_count"] = len(receipt["retired"])
        rec["kept_count"] = len(receipt["kept"])
        rec["sets_after_retire"] = len(cb.list_backup_sets(dest))
        staged = Path(receipt["retired"][0]["to"])
        rec["staged_has_manifest"] = (staged / cb.MANIFEST_NAME).is_file()
        rec["staged_verifies"] = False
        cb.do_verify(staged, KEY)
        rec["staged_verifies"] = True
        rec["oldest_gone_from_dest"] = not sets[0].exists()
        rec["keep_zero_kind"] = None
        try:
            cb.do_retire(dest, 0, key=KEY)
        except cb.BackupRefusal as e:
            rec["keep_zero_kind"] = e.kind

        rec["ok"] = (
            rec["mutated_kind"] == "SOURCE_MUTATED"
            and rec["mutated_crash"] is None
            and rec["manifest_sealed"] is False
            and rec["incident_kinds"] == ["SOURCE_MUTATED"]
            and rec["incomplete_left"] is True
            and rec["retire_kind"] == "RETIRE_OK"
            and rec["never_deleted"] is True
            and rec["retired_count"] == 1
            and rec["kept_count"] == 2
            and rec["sets_after_retire"] == 2
            and rec["staged_has_manifest"] is True
            and rec["staged_verifies"] is True
            and rec["oldest_gone_from_dest"] is True
            and rec["keep_zero_kind"] == "KEEP_TOO_SMALL"
        )
    finally:
        shutil.rmtree(tmp, True)

    sys.path.insert(0, str(HERE.parent / "probe"))
    import artifact_freshness as af                                    # noqa: WPS433
    af.write_stamped(OUT, rec, HERE.parents[1],
                     ["builds/backup/cosmos_backup.py"])
    print(json.dumps(rec, indent=2, default=str))
    return 0 if rec.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
