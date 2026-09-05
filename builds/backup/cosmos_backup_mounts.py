#!/usr/bin/env python3
"""cosmos_backup_mounts.py — GDX / ODX / Seagate ES.3 as PATH backup targets (F-48).

WHY THIS EXISTS. `cosmos_backup.BackupTarget` already copies to a directory.
The WISHLIST P0 targets that are not this volume — Google Drive (GDX), OneDrive
(ODX), and a Seagate Constellation ES.3 once Keith installs it — failed as
`NotImplementedError` seams because nobody named a dest. They are not APIs and
they need no credential: they are mounts. A missing dest is a typed refusal,
not a stub, so the night the dest lands the same code starts working.

WHAT IS IMPLEMENTED, WITHOUT INVENTING A PATH:
  * `backup_targets.json` under the runtime `config` role names each dest.
    No dest is ever guessed from a well-known drive letter. Existence is not
    identity (the empty-dir scar): an optional `identity` block is checked.
  * `bind()` proves the dest is an existing directory on a DIFFERENT volume
    from the source, then returns it. `push()` is `cosmos_backup.do_backup`
    against that dest — verify-on-write, sealed manifest, never a second
    copier. Rehearse-restore is the same engine.
  * Cloud kinds (gdx, odx) REFUSE a scope holding key material (same scan as
    R2 — they sync off-machine in the clear). ES.3 is a local disk Keith owns
    and still refuses: a stolen disk is the same exposure.
  * `D:\\R2Cloner` is FORBIDDEN as a dest before the filesystem is touched.

WHAT IS NOT HERE: Keith names the dest in config (and installs the ES.3).
This module never reads, lists, or copies key material. Stdlib only.

  py -3.14 builds/backup/cosmos_backup_mounts.py preflight --config <cfg> --source <tree>
  py -3.14 builds/backup/cosmos_backup_mounts.py selfcheck --source <tree> --scratch <dir>
  py -3.14 builds/backup/cosmos_backup_mounts.py push --kind gdx --config <cfg> --source <tree>
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import cosmos_backup as cb                      # noqa: E402
import cosmos_backup_r2 as r2                   # noqa: E402
from cosmos_backup import BackupRefusal         # noqa: E402

SCHEMA = "cosmos-backup-targets/1"
CONFIG_NAME = "backup_targets.json"
KINDS = ("gdx", "odx", "es3")
CLOUD_KINDS = frozenset(("gdx", "odx"))
# Named so a reader can match the WISHLIST drive. NEVER used as a dest path.
ES3_MODEL = "ST3000NM0033"
RECEIPT_NAME = "MOUNT_PUSH.json"


# ------------------------------------------------------------------ probe (ITC)

class MountProbe:
    """What a destination IS. Production uses the real filesystem; tests inject."""

    def is_dir(self, path: Path) -> bool:
        return cb._xisdir(path)

    def volume_id(self, path: Path) -> str:
        """Same value for two paths on the same volume, different across volumes.

        Drive letter is not identity (`subst`, mount points). Volume serial is.
        """
        resolved = Path(path)
        if os.name == "nt":
            serial, _label = _win_volume(resolved)
            if serial is not None:
                return f"vol:{serial:08X}"
            drive = os.path.splitdrive(str(resolved.resolve()))[0]
            if drive:
                return f"drive:{drive.upper()}"
        try:
            return f"dev:{os.stat(cb._x(resolved)).st_dev}"
        except OSError as e:
            raise BackupRefusal("DRIVE_NOT_MOUNTED",
                                f"{path}: {type(e).__name__}: {e}") from e

    def volume_label(self, path: Path) -> str | None:
        if os.name != "nt":
            return None
        _serial, label = _win_volume(path)
        return label or None

    def model(self, path: Path) -> str | None:
        """Disk model. Unmeasured here on purpose: WMI is not stdlib.

        `identity.kind=model` therefore REFUSES IDENTITY_UNMEASURED unless a
        test (or a future probe) injects a value. Fail-closed, never guessed.
        """
        return None

    def read_sentinel(self, path: Path) -> dict | None:
        if not cb._xisfile(path):
            return None
        try:
            obj = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        return obj if isinstance(obj, dict) else None


class FakeProbe(MountProbe):
    """Injected probe. Volume ids are declared, never discovered."""

    def __init__(self, volumes: dict[str, str] | None = None,
                 labels: dict[str, str] | None = None,
                 models: dict[str, str] | None = None,
                 sentinels: dict[str, dict] | None = None,
                 missing: set[str] | None = None):
        self.volumes = dict(volumes or {})
        self.labels = dict(labels or {})
        self.models = dict(models or {})
        self.sentinels = dict(sentinels or {})
        self.missing = set(missing or ())

    def _key(self, path: Path) -> str:
        return str(Path(path))

    def is_dir(self, path: Path) -> bool:
        if self._key(path) in self.missing:
            return False
        return super().is_dir(path)

    def volume_id(self, path: Path) -> str:
        k = self._key(path)
        if k in self.volumes:
            return self.volumes[k]
        resolved = str(Path(path).resolve()) if cb._xexists(path) else k
        if resolved in self.volumes:
            return self.volumes[resolved]
        for known, vid in self.volumes.items():
            if resolved.startswith(known.rstrip("\\/") + os.sep) or k.startswith(known):
                return vid
        raise BackupRefusal("DRIVE_NOT_MOUNTED", f"FakeProbe has no volume id for {path}")

    def volume_label(self, path: Path) -> str | None:
        return self.labels.get(self._key(path), self.labels.get(str(Path(path).resolve()) if cb._xexists(path) else "", None))

    def model(self, path: Path) -> str | None:
        return self.models.get(self._key(path))

    def read_sentinel(self, path: Path) -> dict | None:
        k = self._key(path)
        if k in self.sentinels:
            return self.sentinels[k]
        return super().read_sentinel(path)


def _win_volume(path: Path) -> tuple[int | None, str]:
    """(serial, label) via GetVolumeInformationW. No subprocess."""
    import ctypes
    from ctypes import wintypes
    kernel32 = ctypes.windll.kernel32
    root = ctypes.create_unicode_buffer(260)
    if not kernel32.GetVolumePathNameW(str(path), root, 260):
        return None, ""
    label_buf = ctypes.create_unicode_buffer(261)
    fs_buf = ctypes.create_unicode_buffer(261)
    serial = wintypes.DWORD()
    max_comp = wintypes.DWORD()
    flags = wintypes.DWORD()
    ok = kernel32.GetVolumeInformationW(
        root.value, label_buf, 261, ctypes.byref(serial), ctypes.byref(max_comp),
        ctypes.byref(flags), fs_buf, 261)
    if not ok:
        return None, ""
    return int(serial.value), label_buf.value


# ------------------------------------------------------------------ config

def guard_dest(dest: Path) -> Path:
    """The plaintext key store is never a legal destination."""
    s = str(Path(dest)).replace("/", "\\").lower()
    for bad in r2.FORBIDDEN_PREFIXES:
        if s.startswith(bad.replace("/", "\\")):
            raise BackupRefusal(
                "FORBIDDEN_DEST",
                f"{dest} is inside a plaintext key store this tool never touches")
    return Path(dest)


def load_config(path: Path) -> dict:
    p = Path(path)
    if not p.is_file():
        raise BackupRefusal("NO_CONFIG",
                            f"no backup_targets.json at {p} "
                            "(Keith names dest paths; COSMOS never invents them)")
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise BackupRefusal("BAD_CONFIG",
                            f"{p} is not readable JSON: {type(e).__name__}") from e
    if not isinstance(obj, dict):
        raise BackupRefusal("BAD_CONFIG", f"{p} is not a JSON object")
    targets = obj.get("targets")
    if not isinstance(targets, dict):
        raise BackupRefusal("BAD_CONFIG", f"{p} has no 'targets' object")
    return obj


def spec_for(kind: str, config: dict | None, dest: Path | None) -> dict:
    if kind not in KINDS:
        raise BackupRefusal("BAD_KIND", f"kind {kind!r} is not one of {KINDS}")
    if dest is not None:
        p = Path(dest)
        if not p.is_absolute():
            raise BackupRefusal("BAD_CONFIG",
                                "dest must be an absolute path (no invented root)")
        return {"kind": kind, "dest": p, "identity": None, "source": "arg"}
    if config is None:
        raise BackupRefusal("NO_CONFIG",
                            f"{kind} dest comes from {CONFIG_NAME} targets.{kind}.dest "
                            "or --dest, never invented")
    if not isinstance(config, dict):
        raise BackupRefusal(
            "BAD_CONFIG",
            f"config is {type(config).__name__}, not an object")
    targets = config.get("targets")
    if targets is not None and not isinstance(targets, dict):
        raise BackupRefusal(
            "BAD_CONFIG",
            f"{CONFIG_NAME} targets is {type(targets).__name__}, not an object")
    row = (targets or {}).get(kind)
    if not isinstance(row, dict):
        raise BackupRefusal("NO_DEST",
                            f"{CONFIG_NAME} has no targets.{kind} row")
    raw = row.get("dest")
    if not isinstance(raw, str) or not raw.strip():
        raise BackupRefusal("NO_DEST",
                            f"targets.{kind}.dest is empty — Keith names it")
    p = Path(raw.strip())
    if not p.is_absolute():
        raise BackupRefusal("BAD_CONFIG",
                            f"targets.{kind}.dest must be absolute, got {raw!r}")
    ident = row.get("identity")
    if ident is not None and not isinstance(ident, dict):
        raise BackupRefusal("BAD_CONFIG", f"targets.{kind}.identity is not an object")
    return {"kind": kind, "dest": p, "identity": ident, "source": "config"}


# ------------------------------------------------------------------ bind

def _check_identity(spec: dict, probe: MountProbe) -> None:
    ident = spec.get("identity")
    if not ident:
        return
    kind = ident.get("kind")
    expect = ident.get("value")
    dest = spec["dest"]
    if kind == "volume_serial":
        got = probe.volume_id(dest)
        want = str(expect)
        if not want.startswith("vol:"):
            want = f"vol:{want.replace('-', '').upper()}"
        if got.upper() != want.upper():
            raise BackupRefusal("IDENTITY_MISMATCH",
                                f"{spec['kind']} volume {got} != declared {want}")
    elif kind == "volume_label":
        got = probe.volume_label(dest) or ""
        if got != str(expect):
            raise BackupRefusal("IDENTITY_MISMATCH",
                                f"{spec['kind']} label {got!r} != declared {expect!r}")
    elif kind == "model":
        got = probe.model(dest)
        if got is None:
            raise BackupRefusal("IDENTITY_UNMEASURED",
                                f"{spec['kind']} identity.kind=model has no probe "
                                f"(stdlib cannot read disk model; use volume_serial "
                                f"or a sentinel file)")
        if got != str(expect):
            raise BackupRefusal("IDENTITY_MISMATCH",
                                f"{spec['kind']} model {got!r} != declared {expect!r}")
    elif kind == "sentinel":
        name = ident.get("name") or ".cosmos-backup-target.json"
        sent_path = dest / name
        obj = probe.read_sentinel(sent_path)
        if obj is None:
            raise BackupRefusal("IDENTITY_MISSING",
                                f"sentinel {sent_path} is absent or not JSON — "
                                "existence of the dest dir is not identity")
        expect_obj = ident.get("expect") if isinstance(ident.get("expect"), dict) else {"value": expect}
        for k, v in (expect_obj or {}).items():
            if obj.get(k) != v:
                raise BackupRefusal("IDENTITY_MISMATCH",
                                    f"sentinel field {k}={obj.get(k)!r} != {v!r}")
    else:
        raise BackupRefusal("BAD_CONFIG",
                            f"identity.kind {kind!r} is not volume_serial|volume_label|"
                            "model|sentinel")


def bind(kind: str, *, dest: Path | None = None, config_path: Path | None = None,
         config: dict | None = None, probe: MountProbe | None = None,
         source: Path | None = None) -> Path:
    """Prove dest is a legal, mounted, different-volume target. Return it.

    Nothing is created. A dest that does not exist is DRIVE_NOT_MOUNTED — the
    ES.3 is not installed, DriveFS is not mounted, OneDrive is signed out.
    """
    probe = probe or MountProbe()
    if config is None and config_path is not None:
        config = load_config(Path(config_path))
    spec = spec_for(kind, config, dest)
    dest_p = guard_dest(spec["dest"])
    if not probe.is_dir(dest_p):
        raise BackupRefusal(
            "DRIVE_NOT_MOUNTED",
            f"{kind} dest is not a directory: {dest_p} "
            + ("(Seagate ES.3 ST3000NM0033 is not installed)" if kind == "es3"
               else "(mount is absent — DriveFS/OneDrive not signed in, or dest not created)"))
    _check_identity(spec, probe)
    if source is not None:
        src = Path(source)
        try:
            src_vol = probe.volume_id(src)
            dst_vol = probe.volume_id(dest_p)
        except BackupRefusal:
            raise
        if src_vol == dst_vol:
            raise BackupRefusal(
                "SAME_VOLUME",
                f"{kind} dest {dest_p} is volume {dst_vol}, the same as source "
                f"{src} — a drive failure takes both (the gap this adapter exists to close)")
    return dest_p


# ------------------------------------------------------------------ push / preflight

def push(source: Path, kind: str, *, dest: Path | None = None,
         config_path: Path | None = None, config: dict | None = None,
         probe: MountProbe | None = None, key: bytes | None = None,
         excludes=cb.DEFAULT_EXCLUDES) -> dict:
    """bind → secret scan → do_backup (verify-on-write) → sealed receipt."""
    source = Path(source)
    dest_p = bind(kind, dest=dest, config_path=config_path, config=config,
                  probe=probe, source=source)
    manifest = cb.build_manifest(source, excludes)
    offenders = r2.scan_secrets(manifest)
    if offenders:
        raise BackupRefusal(
            "SECRETS_IN_SCOPE",
            f"{len(offenders)} file(s) in scope hold key material and this target "
            f"is UNENCRYPTED: {', '.join(offenders[:5])}"
            f"{' …' if len(offenders) > 5 else ''} — exclude them or encrypt first")
    set_dir = cb.do_backup(source, dest_p, excludes, key)
    receipt = cb.seal({
        "format": cb.FORMAT, "kind": "MOUNT_PUSH_OK", "schema": SCHEMA,
        "at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "target_kind": kind, "cloud": kind in CLOUD_KINDS,
        "source_root": str(source.resolve()),
        "dest": str(dest_p), "set_dir": str(set_dir),
        "files_pushed": manifest["file_count"],
        "bytes_pushed": manifest["total_bytes"],
        "secrets_in_scope": [],
    }, key)
    cb._write_json_atomic(set_dir / RECEIPT_NAME, receipt)
    return receipt


def preflight(config_path: Path | None, source: Path | None,
              probe: MountProbe | None = None) -> dict:
    """Configured vs missing, measured. No dest is invented. No key is read."""
    probe = probe or MountProbe()
    blockers, notes, rows = [], [], {}
    cfg = None
    cfg_state = "ABSENT"
    if config_path is not None:
        try:
            cfg = load_config(Path(config_path))
            cfg_state = "PRESENT"
        except BackupRefusal as e:
            cfg_state = e.kind
            blockers.append(f"config: {e.kind}")
    for kind in KINDS:
        rec = {"kind": kind, "state": "NO_DEST"}
        try:
            dest_p = bind(kind, config=cfg, config_path=None if cfg is not None else config_path,
                          probe=probe, source=source)
            rec.update({"state": "READY", "dest": str(dest_p),
                        "volume": probe.volume_id(dest_p)})
        except BackupRefusal as e:
            rec.update({"state": e.kind, "detail": e.detail})
            blockers.append(f"{kind}: {e.kind}")
        rows[kind] = rec
    scope = None
    if source is not None:
        try:
            m = cb.build_manifest(Path(source))
            offenders = r2.scan_secrets(m)
            scope = {"files": m["file_count"], "bytes": m["total_bytes"],
                     "secrets_in_scope": offenders}
            if offenders:
                blockers.append(f"{len(offenders)} file(s) in scope hold key material")
        except BackupRefusal as e:
            scope = {"refused": e.kind, "detail": e.detail}
            blockers.append(f"scope: {e.kind}")
    notes.append(f"ES.3 expected model {ES3_MODEL} — named in WISHLIST, never used as a dest")
    notes.append("GDX/ODX dests are config rows, never X: or OneDrive literals in code")
    return {"format": cb.FORMAT, "kind": "MOUNT_PREFLIGHT", "schema": SCHEMA,
            "at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "adapter_implemented": True,
            "config": {"state": cfg_state, "name": CONFIG_NAME},
            "targets": rows, "scope": scope, "notes": notes, "blockers": blockers,
            "status": "READY" if not blockers else "BLOCKED"}


SELFCHECK_KIND = "gdx"


def selfcheck(source: Path, scratch: Path, key: bytes | None = None) -> dict:
    """Prove bind → scan → backup → rehearse against a fake two-volume world.

    Dest is a temp dir on this machine; FakeProbe *declares* it a different
    volume so SAME_VOLUME does not fire. Nothing reaches a real mount.
    """
    source = Path(source)
    scratch = Path(scratch)
    dest = scratch / "dest"
    dest.mkdir(parents=True, exist_ok=True)
    probe = FakeProbe(volumes={
        str(source.resolve()): "vol:SELFCHECK-SRC",
        str(dest): "vol:SELFCHECK-GDX",
        str(dest.resolve()): "vol:SELFCHECK-GDX",
    })
    receipt = push(source, SELFCHECK_KIND, dest=dest, probe=probe, key=key)
    proof = cb.do_rehearse(Path(receipt["set_dir"]), scratch / "rehearse", key)
    return {**receipt, "probe": "FakeProbe", "rehearsal": str(proof),
            "rehearsal_kind": "REHEARSAL_PASS"}


# ------------------------------------------------------------------ CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--key-file", help="optional HMAC key file for sealing artifacts")
    sub = ap.add_subparsers(dest="cmd", required=True)

    pf = sub.add_parser("preflight", help="configured vs missing (no dest invented)")
    pf.add_argument("--config")
    pf.add_argument("--source")

    sc = sub.add_parser("selfcheck", help="prove the path offline against FakeProbe")
    sc.add_argument("--source", required=True)
    sc.add_argument("--scratch", required=True)

    ps = sub.add_parser("push", help="bind dest, copy, re-hash")
    ps.add_argument("--kind", required=True, choices=KINDS)
    ps.add_argument("--source", required=True)
    ps.add_argument("--config")
    ps.add_argument("--dest", help="absolute dest (overrides config for this run)")
    ps.add_argument("--exclude", action="append", default=list(cb.DEFAULT_EXCLUDES))

    args = ap.parse_args(argv)
    key = Path(args.key_file).read_bytes().strip() if args.key_file else None
    try:
        if args.cmd == "preflight":
            out = preflight(Path(args.config) if args.config else None,
                            Path(args.source) if args.source else None)
            print(json.dumps(out, indent=2, sort_keys=True))
            return 0 if out["status"] == "READY" else 2
        if args.cmd == "selfcheck":
            out = selfcheck(Path(args.source), Path(args.scratch), key)
            print(json.dumps({k: out[k] for k in
                              ("kind", "target_kind", "files_pushed", "bytes_pushed",
                               "set_dir", "rehearsal_kind", "probe") if k in out},
                             indent=2, sort_keys=True))
            return 0
        receipt = push(Path(args.source), args.kind,
                       dest=Path(args.dest) if args.dest else None,
                       config_path=Path(args.config) if args.config else None,
                       key=key, excludes=tuple(args.exclude))
        print(json.dumps({k: receipt[k] for k in
                          ("kind", "target_kind", "files_pushed", "bytes_pushed",
                           "set_dir", "dest") if k in receipt},
                         indent=2, sort_keys=True))
        return 0
    except BackupRefusal as e:
        print(json.dumps({"refused": True, "kind": e.kind, "detail": e.detail}),
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
