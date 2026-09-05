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
import os
import shutil
import stat as _stat
import time
from pathlib import Path

from cosmos_ledger import Ledger


class BackupError(RuntimeError):
    """kind in {VERIFY_MISMATCH, TARGET_MISSING, EMPTY_SCOPE, REHEARSAL_FAILED,
    SOURCE_UNREADABLE}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


# ---------------------------------------------------------------- MAX_PATH
#
# Win32 caps a path at MAX_PATH (260 incl. the NUL, so 259 usable) unless it carries
# the `\\?\` extended-length prefix. Measured 2026-08-31 on this machine:
# HKLM\SYSTEM\CurrentControlSet\Control\FileSystem\LongPathsEnabled = 0.
#
# WITHOUT the prefix this module SILENTLY OMITTED such files and still appended
# BACKUP_VERIFIED - measured against a real 262-char file: files_on_disk 2,
# files reported 1, ledger event BACKUP_VERIFIED. That is the green-log defect the
# canon names, emitted by the one module whose whole job is to be trustworthy.
# `Path.rglob('*')` returns the name and `p.is_file()` then swallows winerror=3 and
# answers False, so the file is filtered out without an error anywhere.
#
# Caveats of `\\?\`, all honored below: it disables ALL path normalization (the path
# must already be absolute, backslash-separated, and free of . / .. - os.path.abspath
# guarantees that), a relative path cannot be prefixed, UNC becomes \\?\UNC\server\share,
# and it is Windows-only (identity on POSIX, so this module stays portable).
_XP = "\\\\?\\"


def _x(p) -> str:
    r"""Extended-length form of a path. Identity on POSIX. Never double-prefixes."""
    s = str(p)
    if os.name != "nt" or s.startswith(_XP):
        return s
    if s.startswith("\\\\"):
        return _XP + "UNC" + s[1:]
    return _XP + os.path.abspath(s)


def _walk_files(root: Path):
    r"""Yield (relative_path, extended_absolute_path) for every regular file under root.

    Replaces `rglob('*') + is_file()`. Two changes, both required:
      * the ROOT carries the `\\?\` prefix, so every descendant inherits it and files
        past MAX_PATH are SEEN rather than filtered out by an error-swallowing test;
      * os.walk's default onerror=None is replaced, so a directory that cannot be
        enumerated REFUSES instead of vanishing. A subtree the backup cannot list is a
        hole in the backup, not a subtree to skip.
    """
    def _refuse(err: OSError):
        raise BackupError("SOURCE_UNREADABLE",
                          f"cannot enumerate {getattr(err, 'filename', '?')}: "
                          f"{type(err).__name__}: {err} - a directory this backup "
                          f"cannot read is a HOLE, not a subtree to skip")

    xroot = _x(Path(root).resolve())
    cut = len(xroot.rstrip("\\/")) + 1
    for dirpath, dirnames, filenames in os.walk(xroot, onerror=_refuse):
        dirnames.sort()
        for name in sorted(filenames):
            full = os.path.join(dirpath, name)
            try:
                mode = os.lstat(full).st_mode
            except OSError as e:
                raise BackupError("SOURCE_UNREADABLE",
                                  f"{full}: {type(e).__name__}: {e}") from e
            if _stat.S_ISREG(mode):
                yield Path(full[cut:]), full


def _sha(p) -> str:
    h = hashlib.sha256()
    with open(_x(p), "rb") as fh:
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
        files = list(_walk_files(src))
        if not files:
            raise BackupError("EMPTY_SCOPE",
                              f"{src} holds no files - an empty backup that reports OK "
                              f"is the green-log-over-nothing defect")
        if not os.path.exists(_x(target.parent)):
            raise BackupError("TARGET_MISSING", f"{target.parent} does not exist - a "
                                                f"backup to nowhere must not look like one")
        stamp = time.strftime("%Y%m%dT%H%M%S", time.localtime(self._clock()))
        dest = target / stamp
        manifest = {}
        for rel, xsrc in files:
            d = dest / rel
            os.makedirs(_x(d.parent), exist_ok=True)
            shutil.copy2(xsrc, _x(d))
            hs, hd = _sha(xsrc), _sha(d)
            if hs != hd:
                self.ledger.append("BACKUP_FAILED",
                                   {"src": str(src), "dest": str(dest),
                                    "file": str(rel), "detail": "hash mismatch"})
                raise BackupError("VERIFY_MISMATCH", f"{rel}: {hs[:12]} != {hd[:12]}")
            manifest[str(rel)] = hs
        with open(_x(dest / "_MANIFEST.sha256.json"), "w", encoding="utf-8") as fh:
            fh.write(__import__("json").dumps(manifest, indent=1, sort_keys=True))
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
        if not os.path.exists(_x(mf)):
            raise BackupError("REHEARSAL_FAILED", f"no manifest at {mf}")
        with open(_x(mf), "r", encoding="utf-8") as fh:
            manifest = json.loads(fh.read())
        os.makedirs(_x(scratch), exist_ok=True)
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
            os.makedirs(_x(outf.parent), exist_ok=True)
            shutil.copy2(_x(srcf), _x(outf))
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
