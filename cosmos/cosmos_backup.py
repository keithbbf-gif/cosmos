#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""cosmos_backup - integrated backup with per-file hash verification and REHEARSED
restore (F5 builder). Keith's ruling: a requirement, not a script.

CANON HONORED: a backup is a scheduled job with a verification, or it is not a backup;
a copy with no hash comparison is not a verification; restore rehearsal is a first-class
operation that RUNS, not documentation. Targets are pluggable paths (local dir today;
LAN/cloud mounts are the same call - the target is a path, the POLICY says off-machine).

MAX_PATH SCAR (measured 2026-08-31, docs/LONGPATH_FINDING.md). Win32 caps a path at
MAX_PATH - 260 chars INCLUDING the NUL, so 259 usable - unless the path carries the
`\\?\` extended-length prefix. On this machine
HKLM\SYSTEM\CurrentControlSet\Control\FileSystem\LongPathsEnabled = 0, and the three
WISHLIST trees hold 2,143 files past that limit (deepest 412 chars).

Without the prefix this module SILENTLY OMITTED such files and still appended
BACKUP_VERIFIED. Against a real 3-file fixture: files on disk 3, files backed up 1,
ledger event BACKUP_VERIFIED with "files": 1 - no error anywhere. That is the
green-log-over-a-hole defect the canon names, emitted by the one module whose entire
job is to be trustworthy. Two distinct causes, and a fix for one is not a fix for the
other:

  class A  the directory lists but the FILE path is too long. `rglob('*')` returns the
           name; `p.is_file()` then SWALLOWS winerror=3 and answers False, so the
           filter drops the file without raising. Measured on the real tree:
           5 of 2,129 files selected, nothing raised.
  class B  the DIRECTORY path is itself too long. scandir cannot descend and
           `os.walk`'s default onerror=None eats that too - the subtree is never seen.

The fix is therefore two-part and BOTH parts are required: prefix the ROOT once (every
descendant inherits it through os.walk) AND refuse loudly on any enumeration or stat
error instead of letting it become a False. A backup that could not read something
REFUSES (kind SOURCE_UNREADABLE); it never reports VERIFIED over a scope it shortened.

The prefix helper is `cosmos_paths.extended` - the resolver's canonical implementation
(same module family, no import-time side effects), imported rather than re-declared so
there is exactly ONE `\\?\` implementation in cosmos/. Its caveats, all honored there:
the prefix disables ALL path normalization so the path must already be absolute and
free of `.`/`..` (abspath), UNC takes the `\\?\UNC\server\share` shape, and it is
Windows-only - identity on POSIX, so this module stays portable.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat as _stat
import time
from pathlib import Path

from cosmos_ledger import Ledger
from cosmos_paths import extended as _x


class BackupError(RuntimeError):
    """kind in {VERIFY_MISMATCH, TARGET_MISSING, EMPTY_SCOPE, REHEARSAL_FAILED,
    SOURCE_UNREADABLE, SECRETS_IN_SCOPE, SNAPSHOT_INCOMPLETE}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


# Paths whose CONTENT is key material. Matched on the relative path only —
# the scan never opens a file, never prints a value. Same name list as
# builds/backup/cosmos_backup_r2.py (COVERAGE.md gap 4): a local copy of
# install_key.bin is the same exposure as an off-machine copy.
SECRET_SUFFIXES = ("_key.txt", "_key.bin", "_credentials.json", "_token.txt",
                   ".pem", ".pfx", ".p12")
SECRET_NAMES = ("api_token.txt", "install_key.bin", "id_rsa", ".env", ".npmrc")
SECRET_PATH_FRAGMENTS = (".git/config",)


def scan_secrets(rels) -> list[str]:
    """Relative paths whose CONTENT is key material. Reads no file, prints no value.

    Accepts an iterable of relative paths, or a manifest dict whose `files`
    value is a dict or list of those paths (the r2 / builds/backup shape).
    """
    if isinstance(rels, dict):
        files = rels.get("files", rels)
        if isinstance(files, dict):
            rels = list(files.keys())
        else:
            rels = list(files)
    hits = []
    for rel in rels:
        low = str(rel).replace("\\", "/").lower()
        name = low.rsplit("/", 1)[-1]
        if (name in SECRET_NAMES or low.endswith(SECRET_SUFFIXES)
                or any(f in low for f in SECRET_PATH_FRAGMENTS)):
            hits.append(str(rel))
    return sorted(hits)


def refuse_secrets(root: Path) -> list[str]:
    """Raise SECRETS_IN_SCOPE if *root* holds a secret-named file.

    Call BEFORE creating a backup dest. Returns the (empty) offender list
    when the tree is clean so callers can record `writes:0` on the refuse
    path without a second walk.
    """
    files = list(_walk_files(Path(root)))
    offenders = scan_secrets([str(rel) for rel, _ in files])
    if offenders:
        raise BackupError(
            "SECRETS_IN_SCOPE",
            f"{len(offenders)} file(s) in scope hold key material; "
            f"this backup will not copy them: {offenders[:8]}")
    return offenders


def _walk_files(root: Path):
    r"""Yield (relative Path, extended absolute path) for every regular file under root.

    Replaces `rglob('*') + is_file()`, which lost every file past MAX_PATH. One lstat
    per entry decides symlink-vs-regular; the predecessor asked twice (is_symlink then
    is_file) and BOTH answers swallowed errors, which is exactly how an unreadable file
    became an unreported hole.
    """
    def _refuse(err: OSError):
        # os.walk's default is onerror=None - it EATS scandir failures. A directory the
        # backup cannot list is a HOLE in the backup, not a subtree to skip quietly.
        raise BackupError("SOURCE_UNREADABLE",
                          f"cannot enumerate {getattr(err, 'filename', '?')}: "
                          f"{type(err).__name__}: {err}")

    xroot = _x(Path(root).resolve())
    cut = len(xroot.rstrip("\\/")) + 1
    for dirpath, dirnames, filenames in os.walk(xroot, onerror=_refuse):
        dirnames.sort()
        for name in sorted(filenames):
            full = os.path.join(dirpath, name)
            try:
                mode = os.lstat(full).st_mode
            except OSError as e:
                # Never `continue` here. A soft skip would restore the exact defect
                # this module just fixed: an unreadable entry quietly failing the
                # is-regular test and vanishing from a backup reported VERIFIED.
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
    def __init__(self, ledger: Ledger, clock=time.time, node=None):
        self.ledger = ledger
        self._clock = clock
        # FOLLOW_KEYS identity. Callers that have a resolver pass
        # paths.sentinel.system ("COSMOS") — never a guessed rail. Absent
        # node is not invented: a Backup(ledger) in a unit test stays
        # unstamped. The live clock and CLI always pass it.
        self.node = node

    def _append(self, event: str, payload: dict) -> None:
        body = dict(payload)
        if self.node:
            body["node"] = self.node
        self.ledger.append(event, body)

    def run(self, src: Path, target: Path) -> dict:
        """Copy src tree -> target/<stamp>/, hash-verify EVERY file, fail loudly on any
        mismatch, ledger the result with counts. Nothing at the target is ever deleted."""
        src, target = Path(src), Path(target)
        files = list(_walk_files(src))
        if not files:
            raise BackupError("EMPTY_SCOPE",
                              f"{src} holds no files - an empty backup that reports OK "
                              f"is the green-log-over-nothing defect")
        offenders = scan_secrets([str(rel) for rel, _ in files])
        if offenders:
            raise BackupError(
                "SECRETS_IN_SCOPE",
                f"{len(offenders)} file(s) in scope hold key material; "
                f"this backup will not copy them: {offenders[:8]}")
        if not os.path.exists(_x(target.parent)):
            raise BackupError("TARGET_MISSING", f"{target.parent} does not exist - a "
                                                f"backup to nowhere must not look like one")
        stamp = time.strftime("%Y%m%dT%H%M%S", time.localtime(self._clock()))
        dest = target / stamp
        manifest = {}
        for rel, xsrc in files:
            # the DESTINATION needs the prefix too: a backup-set dir plus a 240-char
            # relative key is longer than the source that was already past the limit.
            d = dest / rel
            os.makedirs(_x(d.parent), exist_ok=True)
            shutil.copy2(xsrc, _x(d))
            hs, hd = _sha(xsrc), _sha(d)
            if hs != hd:
                self._append("BACKUP_FAILED",
                             {"src": str(src), "dest": str(dest),
                              "file": str(rel), "detail": "hash mismatch"})
                raise BackupError("VERIFY_MISMATCH", f"{rel}: {hs[:12]} != {hd[:12]}")
            manifest[str(rel)] = hs
        with open(_x(dest / "_MANIFEST.sha256.json"), "w", encoding="utf-8") as fh:
            fh.write(json.dumps(manifest, indent=1, sort_keys=True))
        self._append("BACKUP_VERIFIED",
                     {"src": str(src), "dest": str(dest),
                      "files": len(manifest), "verified": len(manifest)})
        return {"dest": dest, "files": len(manifest)}

    def rehearse_restore(self, backup_dest: Path, scratch: Path) -> dict:
        """RESTORE INTO ISOLATION and verify against the stored manifest. This RUNS -
        a restore nobody has rehearsed is a hope."""
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
            self._append("RESTORE_REHEARSAL_FAILED",
                         {"dest": str(backup_dest), "bad": bad[:20]})
            raise BackupError("REHEARSAL_FAILED", f"{len(bad)} files failed hash on restore")
        self._append("RESTORE_REHEARSAL_PASSED",
                     {"dest": str(backup_dest), "files": len(manifest),
                      "scratch": str(scratch)})
        return {"files": len(manifest), "scratch": scratch}
