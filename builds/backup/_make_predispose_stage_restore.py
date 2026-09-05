#!/usr/bin/env python3
"""Write the stripped predecessor of cosmos_backup.py used as fail-against-old.

Never deletes the live module. Output lives under
builds/backup/_delme/predispose_stage_restore_*/cosmos_backup.py.
"""
from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "cosmos_backup.py"
DST = (HERE / "_delme" / "predispose_stage_restore_20260831T123422Z"
       / "cosmos_backup.py")


def main() -> int:
    text = SRC.read_text(encoding="utf-8")
    swaps = [
        (
            "            keep = _child(stage, rel)\n"
            "            if _xexists(keep):\n"
            '                raise BackupRefusal("STAGE_OCCUPIED", f"stage slot already used: {keep}")\n'
            "            _xmkdirs(keep.parent)\n",
            "            keep = _child(stage, rel)\n"
            "            # STAGE_OCCUPIED ABSENT — clobbers keep\n"
            "            _xmkdirs(keep.parent)\n",
            "STAGE_OCCUPIED",
        ),
        (
            "    if bad:\n"
            '        emit_incident(Path(set_dir), "RESTORE_HASH_MISMATCH",\n'
            '                      {"mismatches": bad, "displaced": displaced}, key)\n'
            '        raise BackupRefusal("RESTORE_HASH_MISMATCH",\n'
            '                            f"{len(bad)} restored file(s) fail re-hash under {dest_root}")\n'
            '    return seal({"format": FORMAT, "kind": "RESTORE_OK", "at_utc": _utcnow(),\n',
            "    # restore re-hash ABSENT — a flipped retrieve still seals RESTORE_OK\n"
            '    return seal({"format": FORMAT, "kind": "RESTORE_OK", "at_utc": _utcnow(),\n',
            "RESTORE_HASH_MISMATCH",
        ),
        (
            "    if bad:\n"
            '        emit_incident(Path(set_dir), "REHEARSAL_HASH_MISMATCH", {"mismatches": bad}, key)\n'
            '        raise BackupRefusal("REHEARSAL_HASH_MISMATCH",\n'
            '                            f"rehearsal restore failed re-hash for {len(bad)} file(s)")\n'
            "    target.put_artifact(REHEARSAL_NAME, seal(\n",
            "    # rehearse re-hash ABSENT — a flipped retrieve still seals REHEARSAL_PASS\n"
            "    target.put_artifact(REHEARSAL_NAME, seal(\n",
            "REHEARSAL_HASH_MISMATCH",
        ),
        (
            "    if not _xisdir(source_root):\n"
            '        raise BackupRefusal("SOURCE_NOT_DIR", f"source root is not a directory: {source_root}")\n'
            "    files = {}\n",
            "    # SOURCE_NOT_DIR ABSENT — a file walks as SOURCE_UNREADABLE / SOURCE_EMPTY\n"
            "    files = {}\n",
            "SOURCE_NOT_DIR",
        ),
        (
            "        elif not _xisdir(self.set_dir / DATA_DIR):\n"
            '            raise BackupRefusal("NOT_A_BACKUP_SET", f"no data/ under {self.set_dir}")\n',
            "        # NOT_A_BACKUP_SET ABSENT — get_artifact FileNotFoundError, untyped\n",
            "NOT_A_BACKUP_SET",
        ),
    ]
    for old, new, label in swaps:
        if old not in text:
            raise SystemExit(f"block not found: {label}")
        text = text.replace(old, new, 1)
    DST.parent.mkdir(parents=True, exist_ok=True)
    DST.write_text(text, encoding="utf-8")
    print(f"wrote {DST} bytes={DST.stat().st_size}")
    print("STAGE_OCCUPIED raise present:", 'raise BackupRefusal("STAGE_OCCUPIED"' in text)
    print("RESTORE_HASH raise present:", 'raise BackupRefusal("RESTORE_HASH_MISMATCH"' in text)
    print("do_rehearse REHEARSAL raise present:",
          'emit_incident(Path(set_dir), "REHEARSAL_HASH_MISMATCH"' in text)
    print("SOURCE_NOT_DIR raise present:", 'raise BackupRefusal("SOURCE_NOT_DIR"' in text)
    print("NOT_A_BACKUP_SET raise present:", 'raise BackupRefusal("NOT_A_BACKUP_SET"' in text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
