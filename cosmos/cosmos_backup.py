#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_backup - integrated backup with per-file hash verification and REHEARSED
restore (F5 builder). Keith's ruling: a requirement, not a script.

CANON HONORED: a backup is a scheduled job with a verification, or it is not a backup;
a copy with no hash comparison is not a verification; restore rehearsal is a first-class
operation that RUNS, not documentation. Targets are pluggable paths (local dir today;
LAN/cloud mounts are the same call - the target is a path, the POLICY says off-machine).
"""
from __future__ import annotations

import hashlib
import shutil
import time
from pathlib import Path

from cosmos_ledger import Ledger


class BackupError(RuntimeError):
    """kind in {VERIFY_MISMATCH, TARGET_MISSING, EMPTY_SCOPE, REHEARSAL_FAILED}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class Backup:
    def __init__(self, ledger: Ledger, clock=time.time):
        self.ledger = ledger
        self._clock = clock

    def run(self, src: Path, target: Path) -> dict:
        """Copy src tree -> target/<stamp>/, hash-verify EVERY file, fail loudly on any
        mismatch, ledger the result with counts. Nothing at the target is ever deleted."""
        src, target = Path(src), Path(target)
        files = [p for p in src.rglob("*") if p.is_file()]
        if not files:
            raise BackupError("EMPTY_SCOPE",
                              f"{src} holds no files - an empty backup that reports OK "
                              f"is the green-log-over-nothing defect")
        if not target.parent.exists():
            raise BackupError("TARGET_MISSING", f"{target.parent} does not exist - a "
                                                f"backup to nowhere must not look like one")
        stamp = time.strftime("%Y%m%dT%H%M%S", time.localtime(self._clock()))
        dest = target / stamp
        manifest = {}
        for p in files:
            rel = p.relative_to(src)
            d = dest / rel
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, d)
            hs, hd = _sha(p), _sha(d)
            if hs != hd:
                self.ledger.append("BACKUP_FAILED",
                                   {"src": str(src), "dest": str(dest),
                                    "file": str(rel), "detail": "hash mismatch"})
                raise BackupError("VERIFY_MISMATCH", f"{rel}: {hs[:12]} != {hd[:12]}")
            manifest[str(rel)] = hs
        (dest / "_MANIFEST.sha256.json").write_text(
            __import__("json").dumps(manifest, indent=1, sort_keys=True), encoding="utf-8")
        self.ledger.append("BACKUP_VERIFIED",
                           {"src": str(src), "dest": str(dest),
                            "files": len(manifest), "verified": len(manifest)})
        return {"dest": dest, "files": len(manifest)}

    def rehearse_restore(self, backup_dest: Path, scratch: Path) -> dict:
        """RESTORE INTO ISOLATION and verify against the stored manifest. This RUNS -
        a restore nobody has rehearsed is a hope."""
        import json
        backup_dest, scratch = Path(backup_dest), Path(scratch)
        mf = backup_dest / "_MANIFEST.sha256.json"
        if not mf.exists():
            raise BackupError("REHEARSAL_FAILED", f"no manifest at {mf}")
        manifest = json.loads(mf.read_text(encoding="utf-8"))
        scratch.mkdir(parents=True, exist_ok=True)
        bad = []
        for rel, want in manifest.items():
            # STAGE-7 K3 FIX (OA C-02 / GEM IND-004, MEASURED): manifest keys were used
            # verbatim, so an absolute key or one with `..` wrote ARBITRARY files. Confine
            # both source and dest under their roots; a key that escapes is REFUSED.
            r = str(rel)
            if r.startswith(("/", "\\")) or (len(r) > 1 and r[1] == ":") or ".." in \
                    r.replace("\\", "/").split("/"):
                raise BackupError("REHEARSAL_FAILED",
                                  f"manifest key {rel!r} is absolute or traverses - "
                                  f"refusing to restore outside the scratch root")
            srcf = backup_dest / rel
            outf = scratch / rel
            try:
                outf.resolve().relative_to(scratch.resolve())
                srcf.resolve().relative_to(backup_dest.resolve())
            except ValueError:
                raise BackupError("REHEARSAL_FAILED",
                                  f"manifest key {rel!r} escapes containment")
            outf.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(srcf, outf)
            if _sha(outf) != want:
                bad.append(rel)
        if bad:
            self.ledger.append("RESTORE_REHEARSAL_FAILED",
                               {"dest": str(backup_dest), "bad": bad[:20]})
            raise BackupError("REHEARSAL_FAILED", f"{len(bad)} files failed hash on restore")
        self.ledger.append("RESTORE_REHEARSAL_PASSED",
                           {"dest": str(backup_dest), "files": len(manifest),
                            "scratch": str(scratch)})
        return {"files": len(manifest), "scratch": scratch}