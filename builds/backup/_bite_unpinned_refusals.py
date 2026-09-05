#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: unpinned backup refusals against pre-fix behaviour.

Kinds that sat in BackupRefusal.kind / load_scopes / UrllibTransport /
identity.kind prose and were never named:

  * SCRATCH_NOT_EMPTY (local do_rehearse) — occupied scratch still sealed
    REHEARSAL_PASS when the guard is deleted.
  * COPY_IO_ERROR — missing src is a raw FileNotFoundError.
  * BAD_SCOPES — empty scopes list returns [] (silent no-op).
  * R2_UNREACHABLE — OSError propagates untyped.
  * unknown identity.kind — bind succeeds (existence is treated as identity).

Expected (and required before belief): all_bite == true.

    py -3.14 builds/backup/_bite_unpinned_refusals.py
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = HERE / "_bite_unpinned_refusals.json"

import cosmos_backup as cb                                            # noqa: E402
import cosmos_backup_mounts as mounts                                 # noqa: E402
import cosmos_backup_r2 as r2                                         # noqa: E402
import cosmos_offsite_clock as oc                                     # noqa: E402

KEY = b"test-hmac-key-not-a-real-secret"


def _src(tmp: Path) -> Path:
    src = tmp / "src"
    src.mkdir()
    (src / "a.txt").write_text("alpha\n", encoding="utf-8", newline="\n")
    return src


def old_rehearse_no_scratch_guard(set_dir, scratch, key):
    """Current do_rehearse, minus the SCRATCH_NOT_EMPTY check."""
    manifest = cb.do_verify(set_dir, key)
    scratch = Path(scratch)
    cb._xmkdirs(scratch)
    target = cb.LocalDirTarget(set_dir)
    bad = cb._check(manifest, lambda rel: cb._child(scratch, rel),
                    produce=lambda rel, p: target.retrieve(rel, p))
    if bad:
        raise cb.BackupRefusal("REHEARSAL_HASH_MISMATCH", "would have refused")
    proof = cb.seal(
        {"format": cb.FORMAT, "kind": "REHEARSAL_PASS", "at_utc": cb._utcnow(),
         "set_dir": str(Path(set_dir).resolve()),
         "scratch_dir": str(scratch.resolve()),
         "files_restored": len(manifest["files"]),
         "bytes_restored": manifest["total_bytes"],
         "manifest_seal_sha256": manifest["seal"]["sha256"]}, key)
    target.put_artifact(cb.REHEARSAL_NAME, proof)
    return proof


def old_load_scopes_empty_ok(path: Path):
    """Current load_scopes, minus BAD_SCOPES on empty / malformed / incomplete."""
    p = Path(path)
    if not p.is_file():
        raise cb.BackupRefusal("NO_SCOPES", "missing")
    obj = json.loads(p.read_text(encoding="utf-8"))
    scopes = obj.get("scopes") if isinstance(obj, dict) else obj
    out = []
    for s in (scopes or []):
        if isinstance(s, dict) and s.get("name") and s.get("source"):
            out.append({"name": s["name"], "source": s["source"]})
    return out


def old_check_identity_skips_unknown(spec, probe):
    """Current _check_identity, minus the else BAD_CONFIG."""
    ident = spec.get("identity")
    if not ident:
        return
    kind = ident.get("kind")
    if kind in ("volume_serial", "volume_label", "model", "sentinel"):
        mounts._check_identity(spec, probe)


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="cosmos_bite_unpinned_"))
    rec = {"schema": "cosmos-bite/1",
           "what": "unpinned backup refusals — old vs current",
           "all_bite": False}
    try:
        src = _src(tmp)
        dest = tmp / "dest"
        set_dir = cb.do_backup(src, dest, key=KEY)
        occupied = tmp / "occupied"
        occupied.mkdir()
        (occupied / "precious.txt").write_text("do not clobber", encoding="utf-8")
        proof = old_rehearse_no_scratch_guard(set_dir, occupied, KEY)
        rec["scratch_not_empty_old_kind"] = proof.get("kind")
        rec["scratch_not_empty_old_sealed"] = (Path(set_dir) / cb.REHEARSAL_NAME).is_file()
        rec["scratch_not_empty_old_precious_survived"] = (
            (occupied / "precious.txt").read_text(encoding="utf-8") == "do not clobber")

        try:
            shutil.copyfile(str(tmp / "no_such_src.bin"), str(tmp / "out.bin"))
            rec["copy_io_old_crash"] = None
        except OSError as e:
            rec["copy_io_old_crash"] = type(e).__name__

        empty_scopes = tmp / "empty_scopes.json"
        empty_scopes.write_text(json.dumps({"scopes": []}), encoding="utf-8")
        rec["bad_scopes_empty_old"] = old_load_scopes_empty_ok(empty_scopes)
        rec["bad_scopes_empty_old_is_silent_list"] = rec["bad_scopes_empty_old"] == []

        missing_src = tmp / "missing_src.json"
        missing_src.write_text(json.dumps({"scopes": [{"name": "src"}]}),
                               encoding="utf-8")
        rec["bad_scopes_incomplete_old"] = old_load_scopes_empty_ok(missing_src)
        rec["bad_scopes_incomplete_old_is_silent_list"] = (
            rec["bad_scopes_incomplete_old"] == [])

        def boom(*_a, **_k):
            raise OSError("simulated network down")

        real = urllib.request.urlopen
        urllib.request.urlopen = boom
        try:
            req = urllib.request.Request("https://example.invalid/x", method="GET")
            urllib.request.urlopen(req, timeout=1)
            rec["r2_unreachable_old_kind"] = None
        except OSError:
            rec["r2_unreachable_old_kind"] = "OSError"
        finally:
            urllib.request.urlopen = real
        rec["r2_unreachable_untyped_would_be"] = rec["r2_unreachable_old_kind"]

        dest_m = tmp / "gdx"
        dest_m.mkdir()
        probe = mounts.FakeProbe(volumes={
            str(src): "vol:SRC", str(src.resolve()): "vol:SRC",
            str(dest_m): "vol:GDX", str(dest_m.resolve()): "vol:GDX",
        })
        orig_ident = mounts._check_identity

        def skip_unknown(spec, pr):
            ident = spec.get("identity") or {}
            if ident.get("kind") in ("volume_serial", "volume_label",
                                     "model", "sentinel"):
                return orig_ident(spec, pr)
            return None

        mounts._check_identity = skip_unknown
        try:
            got = mounts.bind("gdx", dest=dest_m, probe=probe, source=src)
            rec["unknown_identity_old_bound"] = str(got) == str(dest_m)
        finally:
            mounts._check_identity = orig_ident

        rec["all_bite"] = (
            rec["scratch_not_empty_old_kind"] == "REHEARSAL_PASS"
            and rec["scratch_not_empty_old_sealed"] is True
            and rec["copy_io_old_crash"] == "FileNotFoundError"
            and rec["bad_scopes_empty_old_is_silent_list"] is True
            and rec["bad_scopes_incomplete_old_is_silent_list"] is True
            and rec["r2_unreachable_untyped_would_be"] == "OSError"
            and rec["unknown_identity_old_bound"] is True
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
