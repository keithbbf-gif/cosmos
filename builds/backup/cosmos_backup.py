#!/usr/bin/env python3
"""cosmos_backup.py — COSMOS Bulletproof Backup daemon (P0).

PROPOSED build artifact — lives under builds/backup/, touches no cosmos/ core.
(NOTE: `cosmos/cosmos_backup.py` is a DIFFERENT, ledger-integrated module driven by
`cosmos_backup_clock`. Same module name, different tree; do not conflate them.)

Verified, rehearsed, scheduled, fail-closed, heartbeated backup:

  * build a per-file sha256 manifest of a source root,
  * copy every file into a timestamped backup set and RE-HASH the copies
    (verify-on-write),
  * verify an existing backup set byte-for-byte against its sealed manifest,
  * rehearse-restore into a scratch directory and re-hash the restored files,
    emitting a sealed REHEARSAL result artifact that PROVES restorability,
  * RESTORE a verified set back over a real tree — the round trip a backup
    exists for. Displaced files are moved aside into a stage dir, never
    deleted, never overwritten in place,
  * heartbeat each cycle; on ANY mismatch REFUSE (non-zero exit) and emit an
    INCIDENT artifact. Nothing is ever repaired in place, nothing is deleted,
  * refuse SOURCE_MUTATED if a source file changes after it is hashed (a torn
    snapshot is internally consistent and would VERIFY — that is the green-log),
  * optional `--freeze` / freeze=True copies from a VSS shadow of the source
    volume (F-43 gap 3). No shadow is typed VSS_UNAVAILABLE — never a silent
    live-tree copy under a freeze flag. Tests inject FrozenTree,
  * retire oldest finished sets by staging them to _delme/ (never delete;
    keep < 1 is KEEP_TOO_SMALL).

Every refusal is typed: `BackupRefusal.kind` is machine-readable and the CLI
prints it as JSON on stderr, so a caller branches on the kind, not on prose.

Scheduling: designed for Windows Task Scheduler —
  schtasks /Create /TN COSMOS_Backup /SC HOURLY
      /TR "py -3.14 <this file> run --once --source V:\\A\\Ai\\COSMOS --dest-root <dest>"
`run --interval N` is the fallback internal loop for when schtasks is not
registered. No paths are hard-coded: every root arrives as a parameter.

Targets: "local" is implemented here. GDX (Google Drive), ODX (OneDrive) and
the Seagate ES.3 are PATH mounts implemented in `cosmos_backup_mounts.py` —
dest comes from config/backup_targets.json, never invented. R2 is the same
shape as those mounts: `ADAPTERS["r2"]()` without a credential REFUSES
typed `NO_CREDENTIALS` (never a NotImplementedError stub). The real
`cosmos_backup_r2.R2Target` is returned when credentials + an injected
transport are supplied. Keith places the file; this module never invents
one and never prints a value from one.

Stdlib only. Portable: pathlib + os.replace, POSIX-style relative keys in the
manifest, target runtime py -3.14 on Windows. Spawns no subprocess, so there is
no console window to suppress.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import hmac as _hmac
import json
import os
import re
import shutil
import stat as _stat
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

FORMAT = "cosmos-backup/1"
MANIFEST_NAME = "MANIFEST.json"
REHEARSAL_NAME = "REHEARSAL.json"
HEARTBEAT_NAME = "HEARTBEAT.json"
DATA_DIR = "data"
RETIRE_DIR = "_delme"
DEFAULT_EXCLUDES = (".git", "__pycache__")
CHUNK = 1024 * 1024


class BackupRefusal(RuntimeError):
    """Fail-closed refusal. `kind` is the machine-readable contract; never caught to continue.

    kind ∈ {SOURCE_NOT_DIR, SOURCE_EMPTY, SOURCE_UNREADABLE, SOURCE_MUTATED, SET_EXISTS,
            NOT_A_BACKUP_SET, NO_SEAL, SEAL_MISMATCH, SEAL_HMAC_MISMATCH,
            UNSAFE_MANIFEST_KEY, COPY_IO_ERROR, COPY_HASH_MISMATCH, VERIFY_HASH_MISMATCH,
            SCRATCH_NOT_EMPTY, REHEARSAL_HASH_MISMATCH, RESTORE_DEST_OCCUPIED,
            STAGE_OCCUPIED, RESTORE_HASH_MISMATCH, NO_CREDENTIALS,
            DEST_NOT_DIR, KEEP_TOO_SMALL, RETIRE_DEST_OCCUPIED,
            SECRETS_IN_SCOPE, VSS_UNAVAILABLE, BAD_FREEZE, FREEZE_DEST_OCCUPIED,
            BAD_EXCLUDES}
    """

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        self.detail = detail
        super().__init__(f"REFUSE[{kind}]: {detail}")


# ---------------------------------------------------------------- MAX_PATH
#
# Windows Win32 calls cap a path at MAX_PATH (260 INCLUDING the NUL, so 259 usable)
# unless it carries the `\\?\` extended-length prefix. Measured on this machine
# 2026-08-31: HKLM\SYSTEM\CurrentControlSet\Control\FileSystem\LongPathsEnabled = 0,
# and the three WISHLIST trees hold 2,143 files past that limit (2,125 of them under
# V:\Ai, deepest 412 chars).
#
# WITHOUT the prefix a walker loses them in two DIFFERENT ways, and only one of them
# is visible:
#   class A (2,103 files) - the directory lists, the file path is too long. The name
#       comes back from the walk; stat()/open() then fail winerror=3. `Path.is_file()`
#       SWALLOWS that and returns False, so a filter on is_file() drops the file
#       WITHOUT EVER RAISING. Measured on the real tree: iter_files selected 5 of
#       2,129 files under V:\Ai\_session_logs\_mcp_logs and raised nothing.
#   class B (40 files) - the DIRECTORY path is itself too long. scandir cannot descend
#       and os.walk's default onerror=None swallows that too; the subtree is never seen.
#
# Both are the green-log defect the canon names: coverage claimed over a hole. The fix
# is two-part and both parts are required - prefix the ROOT (every descendant inherits
# it) AND refuse loudly on any enumeration error instead of letting os.walk eat it.
#
# CAVEATS of `\\?\`, all of which the helpers below honor:
#   * it disables ALL path normalization. The path must already be ABSOLUTE, use only
#     `\` separators, and contain no `.` / `..` components - os.path.abspath does this.
#   * a relative path cannot be prefixed at all.
#   * UNC takes a different shape: \\server\share -> \\?\UNC\server\share.
#   * it is Windows-only. On POSIX these helpers are the identity function, so the
#     module stays portable and its behaviour on Linux/macOS is unchanged.
#   * it lifts the limit to ~32,767 chars, and lets COSMOS read files Explorer and
#     most other tools still cannot. Restoring such a file onto a tree whose own root
#     is long needs the prefix on the DESTINATION too - hence _xcopy/_xmkdirs.
#
# Deliberately a local helper rather than an import of cosmos_paths.extended: this
# module is stdlib-only and root-agnostic by design (every root arrives as a
# parameter), and importing the resolver would require a COSMOS root to exist.

_XP = "\\\\?\\"


def _x(p) -> str:
    r"""Extended-length form of a path. Identity on POSIX. Never double-prefixes."""
    s = str(p)
    if os.name != "nt" or s.startswith(_XP):
        return s
    if s.startswith("\\\\"):
        return _XP + "UNC" + s[1:]
    return _XP + os.path.abspath(s)


def _abs(p) -> Path:
    """Absolute path that does not collapse a VSS device object onto the live volume."""
    p = Path(p)
    s = str(p)
    if "HarddiskVolumeShadowCopy" in s or s.startswith("\\\\?\\GLOBALROOT"):
        return p
    return p.resolve()


def _xstat(p, *, follow: bool = True):
    return os.stat(_x(p), follow_symlinks=follow)


def _xexists(p) -> bool:
    return os.path.lexists(_x(p))


def _xisfile(p) -> bool:
    try:
        return _stat.S_ISREG(_xstat(p).st_mode)
    except OSError:
        return False


def _xisdir(p) -> bool:
    try:
        return _stat.S_ISDIR(_xstat(p).st_mode)
    except OSError:
        return False


def _xmkdirs(p) -> None:
    os.makedirs(_x(p), exist_ok=True)


# ---------------------------------------------------------------- hashing / seals

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(_x(path), "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


def _canonical(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def seal(obj: dict, key: bytes | None = None) -> dict:
    """Return obj + a 'seal' over its canonical JSON (sha256, plus HMAC if keyed).

    A non-object is NO_SEAL, never AttributeError on .items(). check_seal
    already typed this; seal() of [] / None / a string was the remaining
    untyped crash (bite `_bite_unpinned_round6.json`).
    """
    if not isinstance(obj, dict):
        raise BackupRefusal("NO_SEAL", "artifact is not a JSON object")
    body = {k: v for k, v in obj.items() if k != "seal"}
    digest = hashlib.sha256(_canonical(body)).hexdigest()
    s = {"algo": "sha256", "sha256": digest}
    if key:
        s["hmac_sha256"] = _hmac.new(key, _canonical(body), hashlib.sha256).hexdigest()
    return {**body, "seal": s}


def check_seal(obj: dict, key: bytes | None = None) -> None:
    """REFUSE if the seal does not match the body.

    HMAC is the 'ours' half: a matching sha256 with a forged, missing, or
    null hmac_sha256 is SEAL_HMAC_MISMATCH, never a crash. compare_digest
    TypeErrors on None (measured on the incumbent); coerce first.
    """
    if not isinstance(obj, dict):
        raise BackupRefusal("NO_SEAL", "artifact is not a JSON object")
    s = obj.get("seal")
    if not isinstance(s, dict) or not s:
        raise BackupRefusal("NO_SEAL", "artifact has no seal")
    body = {k: v for k, v in obj.items() if k != "seal"}
    if hashlib.sha256(_canonical(body)).hexdigest() != s.get("sha256"):
        raise BackupRefusal("SEAL_MISMATCH", "seal sha256 mismatch — artifact altered")
    if key:
        got = s.get("hmac_sha256", "")
        want = _hmac.new(key, _canonical(body), hashlib.sha256).hexdigest()
        try:
            match = isinstance(got, str) and _hmac.compare_digest(want, got)
        except (TypeError, ValueError):
            match = False
        if not match:
            raise BackupRefusal("SEAL_HMAC_MISMATCH", "seal HMAC mismatch — artifact not ours")


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _write_json_atomic(path: Path, obj: dict) -> None:
    tmp = path.with_name(path.name + ".tmp")
    with open(_x(tmp), "w", encoding="utf-8") as fh:
        fh.write(json.dumps(obj, indent=2, sort_keys=True))
    os.replace(_x(tmp), _x(path))  # atomic on Windows and POSIX


def _child(root: Path, rel: str) -> Path:
    """Join a manifest key under root, REFUSING anything that could escape it.

    A manifest read back from disk is only as trustworthy as its seal, and
    without --key-file that seal is a bare sha256 anyone can recompute. So the
    containment check lives at the CONSUMER, where the write happens — the scar
    the core module already carries (STAGE-7 K3 / OA C-02): manifest keys were
    used verbatim, so an absolute or `..` key wrote ARBITRARY files.
    """
    r = str(rel).replace("\\", "/")
    parts = tuple(p for p in r.split("/") if p)
    if not parts or r.startswith("/") or ".." in parts or (len(r) > 1 and r[1] == ":"):
        raise BackupRefusal("UNSAFE_MANIFEST_KEY",
                            f"manifest key {rel!r} is empty, absolute or traverses")
    root = Path(root)
    p = root.joinpath(*parts)
    try:
        _abs(p).relative_to(_abs(root))
    except ValueError:
        raise BackupRefusal("UNSAFE_MANIFEST_KEY",
                            f"manifest key {rel!r} escapes {root}") from None
    return p


# ---------------------------------------------------------------- manifest

def _norm_rel(rel: str) -> str:
    return str(rel).replace("\\", "/").strip("/")


def _excludes_of(excludes):
    """Patterns as a list/tuple/set, or empty. A string is BAD_EXCLUDES.

    Bite `_bite_unpinned_round7.json`: is_excluded(..., "git") returned a
    bool (characters as patterns); is_excluded(..., 1) TypeError'd.
    """
    if excludes is None:
        return ()
    if isinstance(excludes, (str, bytes)) or not isinstance(
            excludes, (list, tuple, set, frozenset)):
        raise BackupRefusal(
            "BAD_EXCLUDES",
            f"excludes is {type(excludes).__name__}, not a list of patterns")
    return excludes


def is_excluded(rel: str, excludes) -> bool:
    """True if this POSIX-style relative path is out of backup scope.

    Patterns (any match is enough), decided BEFORE lstat/open so an
    exclusive-locked file that is not data never becomes SOURCE_UNREADABLE:

      * exact basename — `.git`, `__pycache__`, `_delme`. Matches a path
        whose last component equals the pattern (the walk prunes that
        directory and never descends). Same behaviour as the predecessor
        `name in excludes` / `d not in excludes`.
      * suffix glob — `*.lock` matches any basename (`cdeck_feed.lock`,
        `authority.jsonl.lock`). A .lock is a writer fence, not the data.
      * relative path prefix — `live/logs` matches that path and every
        descendant, and does NOT match `live/logstash`. Slash-boundary.
      * relative glob — `live/**/*.tmp` via fnmatch on the full rel.

    A file that does NOT match, and cannot be read, still REFUSES. This
    function only changes what is in scope; it is not a silent-skip.

    excludes must be a list/tuple/set of pattern strings, or None (empty).
    A string iterates as characters ("git" would match a file named "g")
    — that is the green-log. An int TypeErrors. Both are BAD_EXCLUDES.
    Bite `_bite_unpinned_round7.json`.
    """
    excludes = _excludes_of(excludes)
    rel = _norm_rel(rel)
    if not rel:
        return False
    name = rel.rsplit("/", 1)[-1]
    parts = rel.split("/")
    for raw in excludes:
        pat = _norm_rel(raw)
        if not pat:
            continue
        if "/" in pat:
            if any(c in pat for c in "*?["):
                if fnmatch.fnmatch(rel, pat):
                    return True
            elif rel == pat or rel.startswith(pat + "/"):
                return True
        elif any(c in pat for c in "*?["):
            if fnmatch.fnmatch(name, pat):
                return True
        elif name == pat or pat in parts:
            return True
    return False


def iter_files(root: Path, excludes: frozenset[str] | tuple[str, ...] | list[str] = ()):
    r"""Yield POSIX-style relative paths of regular files under root (no symlinks).

    Walks through the `\\?\` prefix so files past MAX_PATH are SEEN, and refuses on
    any directory it cannot enumerate so files past MAX_PATH are never silently
    dropped. The prefix goes on the ROOT once; every descendant inherits it, which
    is why this is a two-line change and not a sprinkling of conversions.

    One lstat per entry decides symlink-vs-regular. The predecessor asked twice
    (`is_symlink()` then `is_file()`) and both answers were error-swallowing, which
    is precisely how 2,103 unreadable files became an unreported hole.

    Exclude matching (see is_excluded) runs BEFORE lstat/open. A .lock held by a
    live daemon is out of scope; a genuinely unreadable in-scope data file still
    REFUSES SOURCE_UNREADABLE — that refusal is correct and must stay fail-closed.
    """
    def _refuse(err: OSError):
        # os.walk's default is onerror=None — it EATS scandir failures. A directory
        # the backup cannot list is a hole in the backup, not a subtree to skip.
        raise BackupRefusal("SOURCE_UNREADABLE",
                            f"cannot enumerate {getattr(err, 'filename', '?')}: "
                            f"{type(err).__name__}: {err}") from err

    excludes = _excludes_of(excludes)
    xroot = _x(_abs(root))
    cut = len(xroot.rstrip("\\/")) + 1
    for dirpath, dirnames, filenames in os.walk(xroot, onerror=_refuse):
        rel_dir = dirpath[cut:].replace("\\", "/") if len(dirpath) > cut else ""
        keep_dirs = []
        for d in sorted(dirnames):
            child = f"{rel_dir}/{d}" if rel_dir else d
            if is_excluded(child, excludes):
                continue
            mode = _lstat_mode(os.path.join(dirpath, d))
            if _stat.S_ISLNK(mode):
                continue
            keep_dirs.append(d)
        dirnames[:] = keep_dirs
        for name in sorted(filenames):
            child = f"{rel_dir}/{name}" if rel_dir else name
            if is_excluded(child, excludes):
                continue
            full = os.path.join(dirpath, name)
            mode = _lstat_mode(full)
            if _stat.S_ISLNK(mode) or not _stat.S_ISREG(mode):
                continue
            # Root (GitLab python image) can still open mode 000. Copying that
            # as VERIFIED is a hole: the operator marked the file unreadable.
            if (mode & 0o444) == 0:
                raise BackupRefusal(
                    "SOURCE_UNREADABLE",
                    f"{child}: mode {mode & 0o777:o} has no read bits")
            yield full[cut:].replace("\\", "/")


def _lstat_mode(full: str) -> int:
    """st_mode of an already-extended path, or REFUSE. Never returns a guess.

    A soft `return 0` here would restore the exact defect this module just fixed:
    an unreadable entry quietly failing the is-regular test and vanishing.
    """
    try:
        return os.lstat(full).st_mode
    except OSError as e:
        raise BackupRefusal("SOURCE_UNREADABLE",
                            f"{full}: {type(e).__name__}: {e}") from e


def build_manifest(source_root: Path, excludes=DEFAULT_EXCLUDES) -> dict:
    source_root = _abs(source_root)
    if not _xisdir(source_root):
        raise BackupRefusal("SOURCE_NOT_DIR", f"source root is not a directory: {source_root}")
    files = {}
    total = 0
    excludes = _excludes_of(excludes)
    for rel in iter_files(source_root, frozenset(excludes)):
        p = source_root / rel
        try:
            st = _xstat(p)
            digest = sha256_file(p)
        except OSError as e:
            # The live fleet is RUNNING: files get locked and vanish mid-walk. That is
            # a HOLE in the backup, not a file to skip quietly — name it and refuse.
            raise BackupRefusal("SOURCE_UNREADABLE",
                                f"{rel}: {type(e).__name__}: {e}") from e
        files[rel] = {"sha256": digest, "size": st.st_size, "mtime": st.st_mtime}
        total += st.st_size
    if not files:
        raise BackupRefusal("SOURCE_EMPTY",
                            f"nothing to back up under {source_root} "
                            "(empty source is treated as a fault, not a no-op)")
    return {"format": FORMAT, "created_utc": _utcnow(),
            "source_root": str(source_root), "excludes": sorted(excludes),
            "file_count": len(files), "total_bytes": total, "files": files}


# PEM / certificate classification.
# Public certificates (CA bundles, leaf certs, CSRs, public keys) are NOT key
# material. Private-key envelopes ARE. Unknown BEGIN labels, empty files, and
# unreadable files are ambiguous and REFUSE (fail-closed). The scanner inspects
# BEGIN labels only — it never emits, logs, or copies bodies.
PEM_CLASSIFY_SUFFIXES = (".pem", ".key", ".crt", ".cer", ".cert")
_PUBLIC_PEM_LABELS = frozenset({
    "CERTIFICATE",
    "TRUSTED CERTIFICATE",
    "X509 CRL",
    "CERTIFICATE REQUEST",
    "NEW CERTIFICATE REQUEST",
    "PUBLIC KEY",
    "RSA PUBLIC KEY",
    "DSA PUBLIC KEY",
    "EC PUBLIC KEY",
    "SSH2 PUBLIC KEY",
    "PGP PUBLIC KEY BLOCK",
    "DH PARAMETERS",
    "EC PARAMETERS",
    "PKCS7",
    "CMS",
    "ATTRIBUTE CERTIFICATE",
})
_PRIVATE_PEM_LABELS = frozenset({
    "RSA PRIVATE KEY",
    "EC PRIVATE KEY",
    "DSA PRIVATE KEY",
    "OPENSSH PRIVATE KEY",
    "PGP PRIVATE KEY BLOCK",
    "PGP PRIVATE KEY",
    "ENCRYPTED PRIVATE KEY",
    "PRIVATE KEY",
    "ANY PRIVATE KEY",
    "SSH2 ENCRYPTED PRIVATE KEY",
})
_BEGIN_RE = re.compile(br"-----BEGIN ([A-Z][A-Z0-9 ]{0,60})-----")
_PEM_OVERLAP = 80


def pem_label_kind(labels) -> str:
    """Classify a set of PEM BEGIN labels: 'public', 'private', or 'ambiguous'.

    Never sees file bytes. Any unknown label or an empty set is ambiguous.
    A private label wins over public (a cert+key bundle is key material).
    None is empty (ambiguous). A string is ONE label, never iterated as
    characters (bite `_bite_unpinned_round7.json` — "PRIVATE KEY" was
    ambiguous because P,R,I,V… were unknown labels). A non-iterable is
    ambiguous, never TypeError.
    """
    if labels is None:
        labels = ()
    elif isinstance(labels, (str, bytes)):
        labels = (labels.decode("ascii", "replace")
                  if isinstance(labels, bytes) else labels,)
    try:
        labs = {str(x).strip().upper() for x in labels}
    except TypeError:
        return "ambiguous"
    if not labs:
        return "ambiguous"
    if labs - _PUBLIC_PEM_LABELS - _PRIVATE_PEM_LABELS:
        return "ambiguous"
    if labs & _PRIVATE_PEM_LABELS:
        return "private"
    return "public"


def read_pem_begin_labels(path: Path) -> set[str]:
    """Return the set of PEM BEGIN labels in *path*. Never returns bodies.

    Unreadable / missing files yield an empty set (callers treat as ambiguous).
    """
    labels: set[str] = set()
    try:
        with open(_x(path), "rb") as fh:
            leftover = b""
            while True:
                chunk = fh.read(CHUNK)
                if not chunk:
                    break
                data = leftover + chunk
                for m in _BEGIN_RE.finditer(data):
                    labels.add(m.group(1).decode("ascii"))
                leftover = data[-_PEM_OVERLAP:] if len(data) > _PEM_OVERLAP else data
    except OSError:
        return set()
    return labels


def classify_pem_file(path: Path) -> str:
    """'public' | 'private' | 'ambiguous'. Labels only; never emits bytes."""
    return pem_label_kind(read_pem_begin_labels(path))


def scan_secrets(manifest: dict) -> list[str]:
    """Manifest keys whose CONTENT is key material. Prints no value.

    Credential path-shapes (install_key.bin, api_token.txt, .pfx, .p12, …) still
    refuse by name — those files are never opened. PEM-like suffixes (.pem,
    .key, .crt, .cer, .cert) are classified by BEGIN label: a public CA bundle
    is not key material; a private-key envelope is; anything ambiguous refuses.
    Lazy-imports the r2 scanner so this module stays the single backup engine
    and r2 stays the single list of secret path shapes.
    """
    import cosmos_backup_r2 as r2
    return r2.scan_secrets(manifest)


# ---------------------------------------------------------------- targets (adapter seam)

class BackupTarget:
    """Adapter seam. Implementations move bytes; all verification stays in the daemon."""

    def store(self, rel: str, src: Path) -> None: raise NotImplementedError
    def retrieve(self, rel: str, dst: Path) -> None: raise NotImplementedError
    def put_artifact(self, name: str, obj: dict) -> None: raise NotImplementedError
    def get_artifact(self, name: str) -> dict: raise NotImplementedError


class LocalDirTarget(BackupTarget):
    """A timestamped backup-set directory: <set>/data/<rel> + sealed artifacts."""

    def __init__(self, set_dir: Path, create: bool = False):
        self.set_dir = Path(set_dir)
        if create:
            if _xexists(self.set_dir):
                raise BackupRefusal("SET_EXISTS", f"backup set already exists: {self.set_dir} "
                                                  "(never overwrite a prior set)")
            _xmkdirs(self.set_dir / DATA_DIR)
        elif not _xisdir(self.set_dir / DATA_DIR):
            raise BackupRefusal("NOT_A_BACKUP_SET", f"no data/ under {self.set_dir}")

    def data_path(self, rel: str) -> Path:
        return _child(self.set_dir / DATA_DIR, rel)

    def store(self, rel: str, src: Path) -> None:
        _copy(src, self.data_path(rel))

    def retrieve(self, rel: str, dst: Path) -> None:
        _copy(self.data_path(rel), dst)

    def put_artifact(self, name: str, obj: dict) -> None:
        _write_json_atomic(self.set_dir / name, obj)

    def get_artifact(self, name: str) -> dict:
        p = self.set_dir / name
        try:
            with open(_x(p), "r", encoding="utf-8") as fh:
                obj = json.loads(fh.read())
        except (OSError, ValueError, UnicodeDecodeError) as e:
            raise BackupRefusal("NOT_A_BACKUP_SET",
                                f"{name} under {self.set_dir} is unreadable: "
                                f"{type(e).__name__}: {e}") from e
        if not isinstance(obj, dict):
            raise BackupRefusal("NOT_A_BACKUP_SET",
                                f"{name} under {self.set_dir} is not a JSON object")
        return obj


def _copy(src: Path, dst: Path) -> None:
    _xmkdirs(dst.parent)
    try:
        shutil.copyfile(_x(src), _x(dst))
    except OSError as e:
        raise BackupRefusal("COPY_IO_ERROR", f"{src} -> {dst}: {type(e).__name__}: {e}") from e


class _MountDirTarget(LocalDirTarget):
    """GDX / ODX / ES.3: dest is CONFIG or an absolute --dest, never invented.

    Bytes still move through LocalDirTarget (verify-on-write, retrieve, seal).
    `bind()` in cosmos_backup_mounts proves the dest is mounted and on a
    different volume before this class creates a set under it.
    """
    KIND = "?"

    def __init__(self, dest=None, create: bool = False, *, config=None,
                 config_path=None, probe=None, source=None):
        import cosmos_backup_mounts as mounts
        root = mounts.bind(self.KIND,
                           dest=None if dest is None else Path(dest),
                           config=config, config_path=config_path,
                           probe=probe, source=source)
        if create:
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
            set_dir, n = root / stamp, 1
            while _xexists(set_dir):
                set_dir = root / f"{stamp}-{n}"
                n += 1
        else:
            set_dir = Path(dest) if dest is not None else root
        super().__init__(set_dir, create=create)


class GDXTarget(_MountDirTarget):
    KIND = "gdx"


class ODXTarget(_MountDirTarget):
    KIND = "odx"


class ES3Target(_MountDirTarget):
    KIND = "es3"


def r2_adapter(credentials=None, prefix="cosmos", transport=None, **_kwargs):
    """ADAPTERS['r2'] factory. Without a credential this is a typed
    NO_CREDENTIALS, never a NotImplementedError stub — same shape as
    gdx/odx/es3 (NO_CONFIG). The night the file lands, the same call
    starts working. Lazy-imports cosmos_backup_r2 so this module can
    load without a circular import (r2 imports this file at top level).

    credentials: path to r2_credentials.json, OR an already-built
    R2Credentials object (tests / selfcheck). A missing path is
    NO_CREDENTIALS. Values are never printed.
    transport: injected. Production passes UrllibTransport; tests
    pass MemoryTransport. Defaulting to UrllibTransport only happens
    AFTER a credential is present, so a missing credential cannot
    open a socket.
    """
    import cosmos_backup_r2 as r2mod
    if credentials is None:
        raise BackupRefusal(
            "NO_CREDENTIALS",
            "R2 adapter needs a credentials path; Keith places "
            "r2_credentials.json under the runtime config role "
            "(account_id, access_key_id, secret_access_key, bucket).")
    if isinstance(credentials, r2mod.R2Credentials):
        creds = credentials
    else:
        creds = r2mod.load_credentials(Path(credentials))
    if transport is None:
        transport = r2mod.UrllibTransport()
    return r2mod.R2Target(creds, prefix=prefix or "cosmos", transport=transport)


# Name kept so ADAPTERS["r2"] still looks like the sibling classes.
R2Target = r2_adapter


ADAPTERS = {"local": LocalDirTarget, "gdx": GDXTarget, "odx": ODXTarget,
            "es3": ES3Target, "r2": r2_adapter}


# ---------------------------------------------------------------- incidents / heartbeat

def emit_incident(where: Path, kind: str, detail: dict, key: bytes | None) -> Path:
    _xmkdirs(where)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    path, n = where / f"INCIDENT-{stamp}.json", 1
    while _xexists(path):  # never overwrite
        path = where / f"INCIDENT-{stamp}-{n}.json"
        n += 1
    _write_json_atomic(path, seal(
        {"format": FORMAT, "kind": kind, "at_utc": _utcnow(), "detail": detail}, key))
    return path


def heartbeat(hb_path: Path, status: str, detail: dict | None = None) -> None:
    _xmkdirs(hb_path.parent)
    _write_json_atomic(hb_path, {"format": FORMAT, "at_utc": _utcnow(),
                                 "status": status, "detail": detail or {}})


def list_backup_sets(dest_root: Path) -> list[Path]:
    """Finished sets only: data/ AND MANIFEST.json. Incomplete SOURCE_MUTATED
    leftovers (data/, no MANIFEST) are not counted as copies worth keeping.
    `_delme/` and `_rehearse/` are never sets.
    """
    dest_root = Path(dest_root)
    if not _xisdir(dest_root):
        raise BackupRefusal("DEST_NOT_DIR",
                            f"dest root is not a directory: {dest_root}")
    try:
        names = os.listdir(_x(dest_root))
    except OSError as e:
        raise BackupRefusal("DEST_NOT_DIR",
                            f"cannot list {dest_root}: {type(e).__name__}: {e}") from e
    sets: list[Path] = []
    for name in names:
        if name in (RETIRE_DIR, "_rehearse"):
            continue
        p = dest_root / name
        if _xisdir(p) and _xisdir(p / DATA_DIR) and _xisfile(p / MANIFEST_NAME):
            sets.append(p)
    sets.sort(key=lambda p: p.name)
    return sets


def _xmove(src: Path, dst: Path) -> None:
    """Move a directory aside. Never deletes. Dest must not already exist."""
    if _xexists(dst):
        raise BackupRefusal("RETIRE_DEST_OCCUPIED",
                            f"retire dest already exists: {dst}")
    _xmkdirs(Path(dst).parent)
    try:
        os.rename(_x(src), _x(dst))
    except OSError:
        try:
            shutil.move(str(src), str(dst))
        except OSError as e:
            raise BackupRefusal(
                "COPY_IO_ERROR",
                f"retire move {src} -> {dst}: {type(e).__name__}: {e}") from e
    if _xisdir(src):
        raise BackupRefusal("COPY_IO_ERROR",
                            f"retire left source in place: {src}")
    if not _xisdir(dst):
        raise BackupRefusal("COPY_IO_ERROR",
                            f"retire dest missing after move: {dst}")


def do_retire(dest_root: Path, keep: int, retire_root: Path | None = None,
              key: bytes | None = None) -> dict:
    """Stage oldest finished sets aside. Never deletes.

    keep < 1 is KEEP_TOO_SMALL — retiring the last remaining copy is
    forbidden (COVERAGE.md gap 5 is 'no policy', not 'delete everything').
    Older sets move to dest_root/_delme/predispose_<set>_<utc>/ (or
    --retire-root). Keith deletes at his leisure. R2 lifecycle is NOT
    this function (offsite_clock never DELETEs).
    """
    if not isinstance(keep, int) or isinstance(keep, bool) or keep < 1:
        raise BackupRefusal("KEEP_TOO_SMALL",
                            f"keep={keep!r} must be an int >= 1; "
                            "retiring the last remaining set is forbidden")
    dest_root = Path(dest_root)
    sets = list_backup_sets(dest_root)
    to_keep = sets[-keep:] if len(sets) >= keep else list(sets)
    to_retire = sets[:-keep] if len(sets) > keep else []
    retire_root = (Path(retire_root) if retire_root is not None
                   else dest_root / RETIRE_DIR)
    moved: list[dict] = []
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    for s in to_retire:
        dest = retire_root / f"predispose_{s.name}_{stamp}"
        n = 1
        while _xexists(dest):
            dest = retire_root / f"predispose_{s.name}_{stamp}-{n}"
            n += 1
        _xmove(s, dest)
        moved.append({"from": str(s), "to": str(dest)})
    receipt = seal({
        "format": FORMAT,
        "kind": "RETIRE_OK",
        "at_utc": _utcnow(),
        "keep": keep,
        "kept": [str(p) for p in to_keep],
        "retired": moved,
        "never_deleted": True,
    }, key)
    rec_path, n = dest_root / f"RETIRE-{stamp}.json", 1
    while _xexists(rec_path):
        rec_path = dest_root / f"RETIRE-{stamp}-{n}.json"
        n += 1
    _write_json_atomic(rec_path, receipt)
    return receipt


# ---------------------------------------------------------------- operations

def _files_map(manifest: dict) -> dict:
    """manifest.files as a {rel: {sha256, ...}} object. Else NOT_A_BACKUP_SET.

    scan_secrets was typed in round 6b; source_drift / _check / do_verify
    still KeyError'd a missing files field and AttributeError'd a string
    (bite `_bite_unpinned_round7.json`). A files value that is not a
    {sha256} object is the same hole — entry["sha256"] TypeError.
    """
    if not isinstance(manifest, dict):
        raise BackupRefusal("NOT_A_BACKUP_SET", "manifest is not a JSON object")
    files = manifest.get("files")
    if not isinstance(files, dict):
        raise BackupRefusal(
            "NOT_A_BACKUP_SET",
            f"manifest.files is {type(files).__name__}, not an object")
    return files


def _check(manifest: dict, path_of, produce=None, stop_first: bool = False) -> dict:
    """Materialize (optional) then RE-HASH every manifest entry. Returns mismatches.

    The one hash-comparison loop shared by backup, verify, rehearse and restore —
    a second copy of it is a second place for the verification to go soft.
    """
    bad: dict[str, dict] = {}
    for rel, entry in _files_map(manifest).items():
        if not isinstance(rel, str):
            raise BackupRefusal(
                "NOT_A_BACKUP_SET",
                f"manifest.files key is {type(rel).__name__}, not a path")
        if not isinstance(entry, dict) or not isinstance(entry.get("sha256"), str):
            raise BackupRefusal(
                "NOT_A_BACKUP_SET",
                f"manifest.files[{rel!r}] is not a sha256 object")
        p = path_of(rel)
        if produce is not None:
            produce(rel, p)
        got = sha256_file(p) if _xisfile(p) else "<MISSING>"
        if got != entry["sha256"]:
            bad[rel] = {"expected": entry["sha256"], "got": got}
            if stop_first:
                break
    return bad


def source_drift(source_root: Path, manifest: dict) -> dict:
    """Re-hash every source file the manifest named. Returns mismatches.

    Copy-hash (COPY_HASH_MISMATCH) catches a copy that does not match the
    hash taken at walk time. It does NOT catch a torn snapshot: file A is
    hashed and copied, then A mutates on the source, then B is copied, then
    the set is sealed. Copies match the manifest, so VERIFY is green, but
    the set is not a single point in time (COVERAGE.md gap 3). Sealing that
    as VERIFIED is the green-log defect. Re-hash the live sources after the
    copies land; any drift is SOURCE_MUTATED and MANIFEST is not sealed.
    """
    source_root = _abs(source_root)
    bad: dict[str, dict] = {}
    for rel, entry in _files_map(manifest).items():
        if not isinstance(rel, str):
            raise BackupRefusal(
                "NOT_A_BACKUP_SET",
                f"manifest.files key is {type(rel).__name__}, not a path")
        if not isinstance(entry, dict) or not isinstance(entry.get("sha256"), str):
            raise BackupRefusal(
                "NOT_A_BACKUP_SET",
                f"manifest.files[{rel!r}] is not a sha256 object")
        p = _child(source_root, rel)
        got = sha256_file(p) if _xisfile(p) else "<MISSING>"
        if got != entry["sha256"]:
            bad[rel] = {"expected": entry["sha256"], "got": got}
    return bad


def do_backup(source_root: Path, dest_root: Path, excludes=DEFAULT_EXCLUDES,
              key: bytes | None = None, freeze=None) -> Path:
    """Manifest → copy → RE-HASH the copies → re-hash sources → sealed manifest.

    freeze=None (default): walk the live source; SOURCE_MUTATED still
    catches a torn snapshot. freeze=True: VSS shadow; VSS_UNAVAILABLE
    if the shadow cannot be created (never silently copies the live
    tree under a freeze flag). freeze=handle: injected FrozenTree.
    """
    source_root = Path(source_root).resolve()
    dest_root = Path(dest_root)
    if _xexists(dest_root) and not _xisdir(dest_root):
        raise BackupRefusal("DEST_NOT_DIR",
                            f"dest root is not a directory: {dest_root}")
    handle = None
    read_root = source_root
    freeze_info = None
    try:
        if freeze not in (None, False):
            from cosmos_backup_freeze import acquire
            handle = acquire(source_root, freeze)
            read_root = _abs(handle.read_root())
            freeze_info = handle.info()
        manifest = build_manifest(read_root, excludes)
        if freeze_info is not None:
            manifest["freeze"] = freeze_info
        offenders = scan_secrets(manifest)
        if offenders:
            raise BackupRefusal(
                "SECRETS_IN_SCOPE",
                f"{len(offenders)} file(s) in scope hold key material; "
                f"this backup will not copy them: {offenders[:8]}")
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        set_dir, n = dest_root / f"{source_root.name}-{stamp}", 1
        while _xexists(set_dir):
            set_dir = Path(dest_root) / f"{source_root.name}-{stamp}-{n}"
            n += 1
        target = LocalDirTarget(set_dir, create=True)
        bad = _check(manifest, target.data_path,
                     produce=lambda rel, _p: target.store(rel, _child(read_root, rel)),
                     stop_first=True)  # a bad copy means bad hardware: stop, don't grind on
        if bad:
            emit_incident(set_dir, "COPY_HASH_MISMATCH", {"mismatches": bad}, key)
            raise BackupRefusal("COPY_HASH_MISMATCH",
                                f"copy of {', '.join(bad)} does not hash-match source")
        drift = source_drift(read_root, manifest)
        if drift:
            emit_incident(set_dir, "SOURCE_MUTATED", {"mismatches": drift}, key)
            raise BackupRefusal(
                "SOURCE_MUTATED",
                f"source changed under {read_root} during backup: {', '.join(drift)}")
        target.put_artifact(MANIFEST_NAME, seal(manifest, key))
        return set_dir
    finally:
        if handle is not None:
            handle.release()


def do_verify(set_dir: Path, key: bytes | None = None) -> dict:
    """Re-hash every stored file against the sealed manifest. REFUSE on any drift."""
    target = LocalDirTarget(set_dir)
    manifest = target.get_artifact(MANIFEST_NAME)
    check_seal(manifest, key)
    bad = _check(manifest, target.data_path)
    if bad:
        emit_incident(Path(set_dir), "VERIFY_HASH_MISMATCH", {"mismatches": bad}, key)
        raise BackupRefusal("VERIFY_HASH_MISMATCH",
                            f"{len(bad)} file(s) in {set_dir} fail hash verification")
    return manifest


def do_rehearse_target(target: BackupTarget, scratch_dir: Path,
                       key: bytes | None = None) -> dict:
    """Restore from ANY BackupTarget into scratch, re-hash, seal REHEARSAL.json
    onto the target. Gate B of R2_OFFSITE_PLAN: the same engine that proves a
    local set also proves an R2 prefix (MemoryTransport offline, Urllib on the
    wire). Returns the sealed proof dict. Needs no credential of its own —
    the target already carries (or refuses) that.

    Does NOT call do_verify: that helper is LocalDirTarget-shaped. Remote
    verify is the retrieve+re-hash this function already is.
    """
    manifest = target.get_artifact(MANIFEST_NAME)
    check_seal(manifest, key)
    scratch = Path(scratch_dir)
    if _xisdir(scratch) and os.listdir(_x(scratch)):
        raise BackupRefusal("SCRATCH_NOT_EMPTY", f"rehearsal scratch not empty: {scratch} "
                                                 "(will not overwrite; nothing is ever deleted)")
    _xmkdirs(scratch)
    bad = _check(manifest, lambda rel: _child(scratch, rel),
                 produce=lambda rel, p: target.retrieve(rel, p))
    if bad:
        raise BackupRefusal("REHEARSAL_HASH_MISMATCH",
                            f"rehearsal restore failed re-hash for {len(bad)} file(s)")
    proof = seal(
        {"format": FORMAT, "kind": "REHEARSAL_PASS", "at_utc": _utcnow(),
         "scratch_dir": str(scratch.resolve()),
         "files_restored": len(manifest["files"]),
         "bytes_restored": manifest["total_bytes"],
         "manifest_seal_sha256": manifest["seal"]["sha256"],
         "target": type(target).__name__}, key)
    target.put_artifact(REHEARSAL_NAME, proof)
    return proof


def do_rehearse(set_dir: Path, scratch_dir: Path, key: bytes | None = None) -> Path:
    """Restore to scratch, re-hash, emit sealed REHEARSAL.json. The PROOF gate."""
    manifest = do_verify(set_dir, key)              # backup must verify first
    scratch = Path(scratch_dir)
    if _xisdir(scratch) and os.listdir(_x(scratch)):
        raise BackupRefusal("SCRATCH_NOT_EMPTY", f"rehearsal scratch not empty: {scratch} "
                                                 "(will not overwrite; nothing is ever deleted)")
    _xmkdirs(scratch)
    target = LocalDirTarget(set_dir)
    bad = _check(manifest, lambda rel: _child(scratch, rel),
                 produce=lambda rel, p: target.retrieve(rel, p))
    if bad:
        emit_incident(Path(set_dir), "REHEARSAL_HASH_MISMATCH", {"mismatches": bad}, key)
        raise BackupRefusal("REHEARSAL_HASH_MISMATCH",
                            f"rehearsal restore failed re-hash for {len(bad)} file(s)")
    target.put_artifact(REHEARSAL_NAME, seal(
        {"format": FORMAT, "kind": "REHEARSAL_PASS", "at_utc": _utcnow(),
         "set_dir": str(Path(set_dir).resolve()), "scratch_dir": str(scratch.resolve()),
         "files_restored": len(manifest["files"]),
         "bytes_restored": manifest["total_bytes"],
         "manifest_seal_sha256": manifest["seal"]["sha256"]}, key))
    return Path(set_dir) / REHEARSAL_NAME


def do_restore(set_dir: Path, dest_root: Path, key: bytes | None = None,
               stage_dir: Path | None = None) -> dict:
    """Restore a VERIFIED set back over a real tree — the round trip, not a rehearsal.

    A file already at the destination is MOVED ASIDE into stage_dir first (never
    deleted, never overwritten in place); with no stage_dir an occupied
    destination is a typed refusal. Every restored file is re-hashed against the
    sealed manifest before this returns. Returns a sealed RESTORE receipt.
    """
    manifest = do_verify(set_dir, key)              # never restore from an unverified set
    target = LocalDirTarget(set_dir)
    dest_root = Path(dest_root)
    stage = Path(stage_dir) if stage_dir else None
    displaced: list[str] = []

    def produce(rel: str, dst: Path) -> None:
        if _xexists(dst):
            if stage is None:
                raise BackupRefusal("RESTORE_DEST_OCCUPIED",
                                    f"{dst} exists and no stage dir was given "
                                    "(nothing is ever overwritten in place)")
            keep = _child(stage, rel)
            if _xexists(keep):
                raise BackupRefusal("STAGE_OCCUPIED", f"stage slot already used: {keep}")
            _xmkdirs(keep.parent)
            try:
                os.replace(_x(dst), _x(keep))
            except OSError:
                shutil.move(_x(dst), _x(keep))      # stage may live on another volume
            displaced.append(rel)
        target.retrieve(rel, dst)

    bad = _check(manifest, lambda rel: _child(dest_root, rel), produce=produce)
    if bad:
        emit_incident(Path(set_dir), "RESTORE_HASH_MISMATCH",
                      {"mismatches": bad, "displaced": displaced}, key)
        raise BackupRefusal("RESTORE_HASH_MISMATCH",
                            f"{len(bad)} restored file(s) fail re-hash under {dest_root}")
    return seal({"format": FORMAT, "kind": "RESTORE_OK", "at_utc": _utcnow(),
                 "set_dir": str(Path(set_dir).resolve()),
                 "dest_root": str(dest_root.resolve()),
                 "files_restored": len(manifest["files"]),
                 "bytes_restored": manifest["total_bytes"],
                 "displaced": sorted(displaced),
                 "stage_dir": str(stage.resolve()) if stage else None,
                 "manifest_seal_sha256": manifest["seal"]["sha256"]}, key)


def run_once(sources: list[Path], dest_root: Path, excludes, key: bytes | None,
             keep: int | None = None, freeze=None) -> list[dict]:
    """One full cycle per source: backup → verify → rehearse → optional retire.

    Returns the completed-set records (source, set, proof) so a clock can
    quote file_count / total_bytes from the sealed MANIFEST. rc=0 is not
    done — those numbers are.
    """
    hb = Path(dest_root) / HEARTBEAT_NAME
    heartbeat(hb, "CYCLE_START", {"sources": [str(s) for s in sources]})
    done = []
    try:
        for src in sources:
            set_dir = do_backup(src, dest_root, excludes, key, freeze=freeze)
            proof = do_rehearse(set_dir, Path(dest_root) / "_rehearse" /
                                (set_dir.name + "-scratch"), key)
            done.append({"source": str(src), "set": str(set_dir), "proof": str(proof)})
        retire_receipt = None
        if keep is not None:
            retire_receipt = do_retire(Path(dest_root), keep, key=key)
    except BackupRefusal as e:
        heartbeat(hb, "REFUSED", {"kind": e.kind, "error": str(e), "completed": done})
        raise
    except Exception as e:
        # An untyped crash used to leave the heartbeat reading CYCLE_START forever —
        # silence that looks like a slow run, not a dead one. Say so, then re-raise.
        detail = {"error": f"{type(e).__name__}: {e}", "completed": done}
        emit_incident(Path(dest_root), "CYCLE_CRASHED", detail, key)
        heartbeat(hb, "CRASHED", detail)
        raise
    heartbeat(hb, "OK", {"completed": done,
                         "retire": None if keep is None else retire_receipt})
    return done


# ---------------------------------------------------------------- CLI

def _key_from(args) -> bytes | None:
    return Path(args.key_file).read_bytes().strip() if args.key_file else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--key-file", help="optional HMAC key file for sealing artifacts")
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("backup", help="back up one source root into a new set")
    b.add_argument("--source", required=True)
    b.add_argument("--dest-root", required=True)
    b.add_argument("--exclude", action="append", default=list(DEFAULT_EXCLUDES))
    b.add_argument("--freeze", action="store_true",
                   help="copy from a VSS shadow; VSS_UNAVAILABLE if the "
                        "shadow cannot be created (never silently copies the live tree)")

    v = sub.add_parser("verify", help="re-hash an existing backup set")
    v.add_argument("--backup-dir", required=True)

    r = sub.add_parser("rehearse", help="restore to scratch and prove it re-hashes")
    r.add_argument("--backup-dir", required=True)
    r.add_argument("--scratch", required=True)

    x = sub.add_parser("restore", help="restore a verified set back over a real tree")
    x.add_argument("--backup-dir", required=True)
    x.add_argument("--dest-root", required=True)
    x.add_argument("--stage-dir", help="where displaced files are moved aside "
                                       "(required to restore over existing files)")

    run = sub.add_parser("run", help="full cycle(s); schtasks calls --once")
    run.add_argument("--source", action="append", required=True)
    run.add_argument("--dest-root", required=True)
    run.add_argument("--exclude", action="append", default=list(DEFAULT_EXCLUDES))
    run.add_argument("--keep", type=int, default=None,
                     help="after a successful cycle, stage older sets aside; "
                          "omit to keep all (no invented policy)")
    run.add_argument("--freeze", action="store_true",
                     help="copy from a VSS shadow; VSS_UNAVAILABLE if the "
                          "shadow cannot be created (never silently copies the live tree)")
    g = run.add_mutually_exclusive_group(required=True)
    g.add_argument("--once", action="store_true")
    g.add_argument("--interval", type=int, metavar="SECONDS",
                   help="fallback internal loop when schtasks is not registered")

    t = sub.add_parser("retire", help="stage oldest backup sets aside; never delete")
    t.add_argument("--dest-root", required=True)
    t.add_argument("--keep", type=int, required=True,
                   help="newest N finished sets stay; older ones move to _delme/")
    t.add_argument("--retire-root", default=None,
                   help="default: dest-root/_delme")

    args = ap.parse_args(argv)
    key = _key_from(args)
    try:
        if args.cmd == "backup":
            print(do_backup(Path(args.source), Path(args.dest_root),
                            tuple(args.exclude), key,
                            freeze=True if getattr(args, "freeze", False) else None))
        elif args.cmd == "verify":
            m = do_verify(Path(args.backup_dir), key)
            print(f"VERIFIED {m['file_count']} files, {m['total_bytes']} bytes")
        elif args.cmd == "rehearse":
            print(do_rehearse(Path(args.backup_dir), Path(args.scratch), key))
        elif args.cmd == "restore":
            print(json.dumps(do_restore(Path(args.backup_dir), Path(args.dest_root),
                                        key, args.stage_dir), indent=2, sort_keys=True))
        elif args.cmd == "retire":
            rec = do_retire(Path(args.dest_root), args.keep,
                            None if args.retire_root is None else Path(args.retire_root),
                            key)
            print(json.dumps(rec, indent=2, sort_keys=True, default=str))
        elif args.cmd == "run":
            srcs = [Path(s) for s in args.source]
            freeze = True if getattr(args, "freeze", False) else None
            if args.once:
                run_once(srcs, Path(args.dest_root), tuple(args.exclude), key,
                         keep=args.keep, freeze=freeze)
            else:
                while True:
                    run_once(srcs, Path(args.dest_root), tuple(args.exclude), key,
                             keep=args.keep, freeze=freeze)
                    time.sleep(args.interval)
    except BackupRefusal as e:
        print(json.dumps({"refused": True, "kind": e.kind, "detail": e.detail}),
              file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
