#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: STAGE_OCCUPIED, restore/rehearse re-hash, SOURCE_NOT_DIR, NOT_A_BACKUP_SET.

These kinds sit in `BackupRefusal.kind` and in the do_restore / build_manifest
docstrings. No test named them. A suite that only restores onto an empty
stage, with a clean retrieve, stays green if those branches are deleted.

Reconstructed pre-fix behaviours (the unpinned claim WAS this):

  1. STAGE_OCCUPIED check deleted. Restore `os.replace`s over the occupied
     stage slot. The previously staged file is gone. Dest is restored.
  2. Post-restore `_check` deleted. A retrieve() that flips a byte still
     returns a sealed RESTORE_OK.
  3. Post-rehearse `_check` deleted. The same flip still seals
     REHEARSAL.json as REHEARSAL_PASS.
  4. SOURCE_NOT_DIR check deleted. A file (not a dir) as source is
     SOURCE_UNREADABLE — os.walk onerror on a non-directory, not the
     typed "source root is not a directory".
  5. NOT_A_BACKUP_SET check deleted. LocalDirTarget on an empty folder
     then get_artifact raises FileNotFoundError, untyped.

Expected (and required before belief): all_bite == true.

    py -3.14 builds/backup/_bite_stage_restore.py
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "_bite_stage_restore.json"
MOD_PATH = HERE / "cosmos_backup.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def old_do_restore_clobber_stage(mod, set_dir, dest_root, key, stage_dir):
    """Current produce(), minus the STAGE_OCCUPIED guard."""
    manifest = mod.do_verify(set_dir, key)
    target = mod.LocalDirTarget(set_dir)
    dest_root = Path(dest_root)
    stage = Path(stage_dir)
    displaced = []

    def produce(rel, dst):
        if mod._xexists(dst):
            keep = mod._child(stage, rel)
            # STAGE_OCCUPIED ABSENT — clobbers keep
            mod._xmkdirs(keep.parent)
            try:
                os.replace(mod._x(dst), mod._x(keep))
            except OSError:
                shutil.move(mod._x(dst), mod._x(keep))
            displaced.append(rel)
        target.retrieve(rel, dst)

    bad = mod._check(manifest, lambda rel: mod._child(dest_root, rel), produce=produce)
    if bad:
        raise mod.BackupRefusal("RESTORE_HASH_MISMATCH", "would have refused")
    return mod.seal(
        {"format": mod.FORMAT, "kind": "RESTORE_OK", "displaced": sorted(displaced)},
        key,
    )


def old_do_restore_no_rehash(mod, set_dir, dest_root, key, stage_dir):
    """Current produce(), then seal RESTORE_OK without looking at `bad`."""
    manifest = mod.do_verify(set_dir, key)
    target = mod.LocalDirTarget(set_dir)
    dest_root = Path(dest_root)
    stage = Path(stage_dir) if stage_dir else None
    displaced = []

    def produce(rel, dst):
        if mod._xexists(dst):
            if stage is None:
                raise mod.BackupRefusal("RESTORE_DEST_OCCUPIED", "occupied")
            keep = mod._child(stage, rel)
            if mod._xexists(keep):
                raise mod.BackupRefusal("STAGE_OCCUPIED", f"stage slot already used: {keep}")
            mod._xmkdirs(keep.parent)
            try:
                os.replace(mod._x(dst), mod._x(keep))
            except OSError:
                shutil.move(mod._x(dst), mod._x(keep))
            displaced.append(rel)
        target.retrieve(rel, dst)

    mod._check(manifest, lambda rel: mod._child(dest_root, rel), produce=produce)
    # re-hash ABSENT — a flipped retrieve is indistinguishable from a clean one
    return mod.seal(
        {"format": mod.FORMAT, "kind": "RESTORE_OK",
         "files_restored": len(manifest["files"]), "displaced": sorted(displaced)},
        key,
    )


def old_do_rehearse_no_rehash(mod, set_dir, scratch_dir, key):
    """do_rehearse without the post-retrieve `_check` refusal."""
    manifest = mod.do_verify(set_dir, key)
    scratch = Path(scratch_dir)
    if mod._xisdir(scratch) and os.listdir(mod._x(scratch)):
        raise mod.BackupRefusal("SCRATCH_NOT_EMPTY", "not empty")
    mod._xmkdirs(scratch)
    target = mod.LocalDirTarget(set_dir)
    mod._check(manifest, lambda rel: mod._child(scratch, rel),
               produce=lambda rel, p: target.retrieve(rel, p))
    # re-hash ABSENT
    proof = mod.seal(
        {"format": mod.FORMAT, "kind": "REHEARSAL_PASS",
         "files_restored": len(manifest["files"])},
        key,
    )
    target.put_artifact(mod.REHEARSAL_NAME, proof)
    return proof


def old_build_manifest_no_isdir(mod, source_root, excludes=None):
    """build_manifest without SOURCE_NOT_DIR. A file walks empty → SOURCE_EMPTY."""
    if excludes is None:
        excludes = mod.DEFAULT_EXCLUDES
    source_root = Path(source_root).resolve()
    files = {}
    total = 0
    for rel in mod.iter_files(source_root, frozenset(excludes)):
        p = source_root / rel
        st = mod._xstat(p)
        digest = mod.sha256_file(p)
        files[rel] = {"sha256": digest, "size": st.st_size, "mtime": st.st_mtime}
        total += st.st_size
    if not files:
        raise mod.BackupRefusal("SOURCE_EMPTY",
                                f"nothing to back up under {source_root}")
    return {"format": mod.FORMAT, "files": files, "file_count": len(files),
            "total_bytes": total}


def main() -> int:
    if not MOD_PATH.is_file():
        raise SystemExit(f"missing {MOD_PATH}")
    mod = _load(MOD_PATH, "cosmos_backup_stage_bite")
    KEY = b"bite-stage-key-not-a-secret"

    rec = {
        "schema": "cosmos-bite/1",
        "what": "STAGE_OCCUPIED + restore/rehearse re-hash + SOURCE_NOT_DIR + NOT_A_BACKUP_SET asserted in prose, unpinned",
        "module": str(MOD_PATH),
        "stage_occupied_old_kind": None,
        "stage_occupied_old_clobbered": None,
        "stage_occupied_old_dest_restored": None,
        "restore_hash_old_kind": None,
        "restore_hash_old_restore_ok": None,
        "rehearse_hash_old_kind": None,
        "rehearse_hash_old_pass_sealed": None,
        "source_not_dir_old_kind": None,
        "not_a_backup_set_old_crash": None,
        "not_a_backup_set_old_kind": None,
        "all_bite": False,
    }

    tmp = Path(tempfile.mkdtemp(prefix="cosmos_bite_stage_restore_"))
    try:
        src = tmp / "src"
        dest = tmp / "dest"
        src.mkdir()
        dest.mkdir()
        (src / "a.txt").write_text("alpha\n", encoding="utf-8", newline="\n")
        set_dir = mod.do_backup(src, dest, key=KEY)

        # --- 1. STAGE_OCCUPIED deleted ---
        live = tmp / "live1"
        live.mkdir()
        (live / "a.txt").write_text("LIVE\n", encoding="utf-8", newline="\n")
        stage = tmp / "stage1"
        stage.mkdir()
        (stage / "a.txt").write_text("PRECIOUS\n", encoding="utf-8", newline="\n")
        precious = mod.hashlib.sha256(b"PRECIOUS\n").hexdigest()
        try:
            receipt = old_do_restore_clobber_stage(mod, set_dir, live, KEY, stage)
            rec["stage_occupied_old_kind"] = receipt.get("kind")
        except mod.BackupRefusal as e:
            rec["stage_occupied_old_kind"] = e.kind
        except Exception as e:  # noqa: BLE001
            rec["stage_occupied_old_kind"] = type(e).__name__
        rec["stage_occupied_old_clobbered"] = (
            mod.sha256_file(stage / "a.txt") != precious
        )
        rec["stage_occupied_old_dest_restored"] = (
            (live / "a.txt").read_text(encoding="utf-8") == "alpha\n"
        )

        # --- 2. restore re-hash deleted ---
        live2 = tmp / "live2"
        live2.mkdir()
        (live2 / "a.txt").write_text("LIVE2\n", encoding="utf-8", newline="\n")
        stage2 = tmp / "stage2"
        orig_retrieve = mod.LocalDirTarget.retrieve

        def flip_retrieve(self, rel, dst):
            orig_retrieve(self, rel, dst)
            blob = bytearray(Path(dst).read_bytes())
            if blob:
                blob[0] ^= 0xFF
                Path(dst).write_bytes(bytes(blob))

        mod.LocalDirTarget.retrieve = flip_retrieve
        try:
            try:
                receipt = old_do_restore_no_rehash(mod, set_dir, live2, KEY, stage2)
                rec["restore_hash_old_kind"] = receipt.get("kind")
                rec["restore_hash_old_restore_ok"] = receipt.get("kind") == "RESTORE_OK"
            except mod.BackupRefusal as e:
                rec["restore_hash_old_kind"] = e.kind
                rec["restore_hash_old_restore_ok"] = False
            except Exception as e:  # noqa: BLE001
                rec["restore_hash_old_kind"] = type(e).__name__
                rec["restore_hash_old_restore_ok"] = False

            # --- 3. rehearse re-hash deleted ---
            scratch = tmp / "scratch3"
            try:
                proof = old_do_rehearse_no_rehash(mod, set_dir, scratch, KEY)
                rec["rehearse_hash_old_kind"] = proof.get("kind")
                rec["rehearse_hash_old_pass_sealed"] = (
                    proof.get("kind") == "REHEARSAL_PASS"
                    and (set_dir / mod.REHEARSAL_NAME).is_file()
                )
            except mod.BackupRefusal as e:
                rec["rehearse_hash_old_kind"] = e.kind
                rec["rehearse_hash_old_pass_sealed"] = False
            except Exception as e:  # noqa: BLE001
                rec["rehearse_hash_old_kind"] = type(e).__name__
                rec["rehearse_hash_old_pass_sealed"] = False
        finally:
            mod.LocalDirTarget.retrieve = orig_retrieve

        # --- 4. SOURCE_NOT_DIR deleted ---
        notdir = tmp / "not_a_dir.txt"
        notdir.write_text("I am a file\n", encoding="utf-8", newline="\n")
        try:
            old_build_manifest_no_isdir(mod, notdir)
            rec["source_not_dir_old_kind"] = "PASSED"
        except mod.BackupRefusal as e:
            rec["source_not_dir_old_kind"] = e.kind
        except Exception as e:  # noqa: BLE001
            rec["source_not_dir_old_kind"] = type(e).__name__

        # --- 5. NOT_A_BACKUP_SET deleted ---
        empty_set = tmp / "emptyset"
        empty_set.mkdir()
        try:
            # skip the DATA_DIR check the constructor would have made
            bogus = mod.LocalDirTarget.__new__(mod.LocalDirTarget)
            bogus.set_dir = empty_set
            bogus.get_artifact(mod.MANIFEST_NAME)
            rec["not_a_backup_set_old_crash"] = None
            rec["not_a_backup_set_old_kind"] = "PASSED"
        except mod.BackupRefusal as e:
            rec["not_a_backup_set_old_crash"] = None
            rec["not_a_backup_set_old_kind"] = e.kind
        except Exception as e:  # noqa: BLE001
            rec["not_a_backup_set_old_crash"] = type(e).__name__
            rec["not_a_backup_set_old_kind"] = None
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    rec["all_bite"] = bool(
        rec["stage_occupied_old_kind"] == "RESTORE_OK"
        and rec["stage_occupied_old_clobbered"] is True
        and rec["stage_occupied_old_dest_restored"] is True
        and rec["restore_hash_old_restore_ok"] is True
        and rec["restore_hash_old_kind"] == "RESTORE_OK"
        and rec["rehearse_hash_old_pass_sealed"] is True
        and rec["rehearse_hash_old_kind"] == "REHEARSAL_PASS"
        and rec["source_not_dir_old_kind"] == "SOURCE_UNREADABLE"
        and rec["not_a_backup_set_old_crash"] == "FileNotFoundError"
        and rec["not_a_backup_set_old_kind"] is None
    )
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    sys.exit(main())
