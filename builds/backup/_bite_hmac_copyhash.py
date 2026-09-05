#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: HMAC seal + verify-on-write were asserted in prose, unpinned.

Runs against the STAGED incumbent (`_delme/predispose_cosmos_backup_hmac_*`)
AND against two reconstructed pre-fix behaviours that the incumbent itself
implements as silent success:

  1. check_seal with the HMAC branch stripped (sha256 only). A forged
     hmac_sha256 still verifies. The suite has never asked.
  2. do_backup without the post-copy _check. A store() that flips a byte
     still seals MANIFEST.json. COPY_HASH_MISMATCH is in the kind set
     and in the changelog as a live event; no test pins it.
  3. The incumbent check_seal given hmac_sha256=None. Prose says REFUSE;
     the machine raises TypeError (compare_digest(str, None)).

Expected (and required before belief): all_bite == true.

    py -3.14 builds/backup/_bite_hmac_copyhash.py
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
STAGED = (REPO / "_delme" / "predispose_cosmos_backup_hmac_20260831T120514Z"
          / "cosmos_backup.py")
OUT = HERE / "_bite_hmac_copyhash.json"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def old_check_seal_sha256_only(mod, obj, key=None):
    """The HMAC branch deleted. This is what the unpinned claim was."""
    s = obj.get("seal")
    if not s:
        raise mod.BackupRefusal("NO_SEAL", "artifact has no seal")
    body = {k: v for k, v in obj.items() if k != "seal"}
    digest = mod.hashlib.sha256(mod._canonical(body)).hexdigest()
    if digest != s.get("sha256"):
        raise mod.BackupRefusal("SEAL_MISMATCH", "seal sha256 mismatch — artifact altered")
    # HMAC branch ABSENT — a keyed caller is indistinguishable from an unkeyed one.


def old_do_backup_no_rehash(mod, source_root, dest_root, key=None):
    """Copy then seal. No re-hash of the copies. The green-log shape."""
    source_root = Path(source_root).resolve()
    manifest = mod.build_manifest(source_root)
    stamp = "BITE"
    set_dir = Path(dest_root) / f"{source_root.name}-{stamp}"
    target = mod.LocalDirTarget(set_dir, create=True)
    for rel in manifest["files"]:
        target.store(rel, mod._child(source_root, rel))
    target.put_artifact(mod.MANIFEST_NAME, mod.seal(manifest, key))
    return set_dir


def main() -> int:
    if not STAGED.is_file():
        raise SystemExit(f"missing staged incumbent {STAGED}")
    old = _load(STAGED, "cosmos_backup_hmac_incumbent")

    rec = {
        "schema": "cosmos-bite/1",
        "what": "HMAC seal + verify-on-write asserted in prose, unpinned",
        "staged": str(STAGED),
        "hmac_forged_old_passed": None,
        "hmac_forged_old_kind": None,
        "hmac_null_pre_fix_crash": None,
        "hmac_null_pre_fix_kind": None,
        "copy_hash_old_succeeded": None,
        "copy_hash_old_kind": None,
        "copy_hash_old_manifest_sealed": None,
        "all_bite": False,
    }

    KEY = b"bite-hmac-key-not-a-secret"
    sealed = old.seal({"n": 1}, KEY)
    forged = dict(sealed)
    forged["seal"] = dict(sealed["seal"])
    forged["seal"]["hmac_sha256"] = "0" * 64
    try:
        old_check_seal_sha256_only(old, forged, KEY)
        rec["hmac_forged_old_passed"] = True
        rec["hmac_forged_old_kind"] = None
    except old.BackupRefusal as e:
        rec["hmac_forged_old_passed"] = False
        rec["hmac_forged_old_kind"] = e.kind
    except Exception as e:  # noqa: BLE001
        rec["hmac_forged_old_passed"] = False
        rec["hmac_forged_old_kind"] = type(e).__name__

    nul = dict(sealed)
    nul["seal"] = dict(sealed["seal"])
    nul["seal"]["hmac_sha256"] = None
    try:
        old.check_seal(nul, KEY)
        rec["hmac_null_pre_fix_crash"] = None
        rec["hmac_null_pre_fix_kind"] = "PASSED"
    except old.BackupRefusal as e:
        rec["hmac_null_pre_fix_crash"] = None
        rec["hmac_null_pre_fix_kind"] = e.kind
    except Exception as e:  # noqa: BLE001
        rec["hmac_null_pre_fix_crash"] = type(e).__name__
        rec["hmac_null_pre_fix_kind"] = None

    tmp = Path(tempfile.mkdtemp(prefix="cosmos_bite_copyhash_"))
    try:
        src = tmp / "src"
        dest = tmp / "dest"
        src.mkdir()
        dest.mkdir()
        (src / "a.txt").write_text("alpha\n", encoding="utf-8", newline="\n")
        orig_store = old.LocalDirTarget.store

        def corrupt_store(self, rel, src_path):
            orig_store(self, rel, src_path)
            p = self.data_path(rel)
            blob = bytearray(p.read_bytes())
            if blob:
                blob[0] ^= 0xFF
                p.write_bytes(bytes(blob))

        old.LocalDirTarget.store = corrupt_store
        try:
            set_dir = old_do_backup_no_rehash(old, src, dest, KEY)
            rec["copy_hash_old_succeeded"] = True
            rec["copy_hash_old_kind"] = None
            rec["copy_hash_old_manifest_sealed"] = (set_dir / old.MANIFEST_NAME).is_file()
        except old.BackupRefusal as e:
            rec["copy_hash_old_succeeded"] = False
            rec["copy_hash_old_kind"] = e.kind
            rec["copy_hash_old_manifest_sealed"] = False
        except Exception as e:  # noqa: BLE001
            rec["copy_hash_old_succeeded"] = False
            rec["copy_hash_old_kind"] = type(e).__name__
            rec["copy_hash_old_manifest_sealed"] = False
        finally:
            old.LocalDirTarget.store = orig_store
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    rec["all_bite"] = bool(
        rec["hmac_forged_old_passed"] is True
        and rec["hmac_forged_old_kind"] is None
        and rec["hmac_null_pre_fix_crash"] == "TypeError"
        and rec["hmac_null_pre_fix_kind"] is None
        and rec["copy_hash_old_succeeded"] is True
        and rec["copy_hash_old_kind"] is None
        and rec["copy_hash_old_manifest_sealed"] is True
    )
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    sys.exit(main())
