#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-measure the two backup fixes. Labels only — never prints key bodies.

(a) lock files out of local scope; in-scope unreadables still SOURCE_UNREADABLE;
    files already landed under D:\\COSMOS_BACKUP.
(b) certifi CA bundle is public (not SECRETS_IN_SCOPE); a private-key envelope
    still refuses. Does NOT push gdx/builds (that's _emit_gdx_builds_push.py).

    py -3.14 builds/backup/_emit_backup_confirm_live.py
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import cosmos_backup as cb
import cosmos_local_clock as lc
import cosmos_backup_r2 as r2

REPO = Path(r"V:\A\Ai\COSMOS")
LIVE_LOGS = REPO / "live" / "logs"
CACERT = REPO / "builds" / "cvm-dt" / "vendor" / "whisper_site" / "certifi" / "cacert.pem"
DEST_ROOT = Path(r"D:\COSMOS_BACKUP")
OUT = HERE / "_backup_confirm_live.json"

# Synthetic envelopes — not live key material. BEGIN labels only.
_PUBLIC = (
    "-----BEGIN CERTIFICATE-----\n"
    "MIIBkTCB+wIJAKH\n"
    "-----END CERTIFICATE-----\n"
)
_PRIVATE = (
    "-----BEGIN RSA PRIVATE KEY-----\n"
    "MIIEowIBAAKCAQEA\n"
    "-----END RSA PRIVATE KEY-----\n"
)


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _count_under(root: Path) -> dict:
    files = 0
    bytes_ = 0
    locks = 0
    live_config = 0
    if not root.is_dir():
        return {"exists": False}
    for dirpath, dirnames, filenames in os.walk(root):
        for name in filenames:
            files += 1
            p = Path(dirpath) / name
            try:
                bytes_ += p.stat().st_size
            except OSError:
                pass
            rel = str(p.relative_to(root)).replace("\\", "/")
            if rel.endswith(".lock") or name.endswith(".lock"):
                locks += 1
            if "/live/config/" in "/" + rel or rel.startswith("live/config/"):
                live_config += 1
    return {
        "exists": True,
        "files": files,
        "bytes": bytes_,
        "lock_files": locks,
        "live_config_files": live_config,
        "manifest": (root.parent / "MANIFEST.json").is_file()
        if root.name == "data" else (root / "MANIFEST.json").is_file(),
        "incident": sorted(p.name for p in root.parent.glob("INCIDENT-*.json"))
        if root.name == "data" else sorted(p.name for p in root.glob("INCIDENT-*.json")),
    }


def main() -> int:
    rec: dict = {
        "schema": "cosmos-bite/1",
        "what": "re-measure local lock-scope + PEM classify on the live tree",
        "measured_utc": _utcnow(),
        "tree_id": "KMesh-COSMOS-live",
    }

    daemon_lock = LIVE_LOGS / "cdeck_feed.lock"
    rec["daemon_lock"] = {
        "path": "live/logs/cdeck_feed.lock",
        "exists": daemon_lock.is_file(),
    }

    # (a) walker with LOCAL_DEFAULT_EXCLUDES must not name *.lock and must
    # not raise SOURCE_UNREADABLE on the live daemon lock.
    locks_in_scope = []
    try:
        n = 0
        for rel in cb.iter_files(REPO, lc.LOCAL_DEFAULT_EXCLUDES):
            n += 1
            name = rel.rsplit("/", 1)[-1]
            if name.endswith(".lock"):
                locks_in_scope.append(rel)
        rec["local_scope"] = {
            "kind": "ok",
            "iter_files_count": n,
            "locks_in_scope": locks_in_scope,
            "locks_in_scope_count": len(locks_in_scope),
            "excludes": list(lc.LOCAL_DEFAULT_EXCLUDES),
            "not_kind": "SOURCE_UNREADABLE",
        }
    except cb.BackupRefusal as e:
        rec["local_scope"] = {
            "kind": e.kind,
            "detail": e.detail,
            "locks_in_scope": locks_in_scope,
        }

    # Dest sets already landed (never-delete). Quote counts, not contents.
    dest_sets = {}
    if DEST_ROOT.is_dir():
        for p in sorted(DEST_ROOT.iterdir()):
            if p.is_dir() and p.name.startswith("COSMOS-"):
                dest_sets[p.name] = _count_under(p / "data")
    rec["dest"] = {"root": str(DEST_ROOT), "sets": dest_sets}

    # (b) live certifi: labels only.
    if CACERT.is_file():
        labels = sorted(cb.read_pem_begin_labels(CACERT))
        rec["cacert"] = {
            "path": "builds/cvm-dt/vendor/whisper_site/certifi/cacert.pem",
            "size": CACERT.stat().st_size,
            "labels": labels,
            "kind": cb.pem_label_kind(labels),
            "body_emitted": False,
        }
        fake_manifest = {
            "source_root": str(REPO / "builds"),
            "files": {
                "cvm-dt/vendor/whisper_site/certifi/cacert.pem": {"size": 1},
            },
        }
        rec["cacert"]["scan_hits"] = r2.scan_secrets(fake_manifest)
    else:
        rec["cacert"] = {"exists": False}

    # Planted private envelope in scratch — never on the live tree.
    scratch = Path(tempfile.mkdtemp(prefix="cosmos_pem_confirm_"))
    try:
        src = scratch / "src"
        dest = scratch / "dest"
        src.mkdir()
        (src / "ok.txt").write_text("ok\n", encoding="utf-8", newline="\n")
        (src / "signing.key").write_text(_PRIVATE, encoding="utf-8", newline="\n")
        try:
            cb.do_backup(src, dest)
            rec["private_key_scratch"] = {"kind": "UNEXPECTED_OK", "set_created": dest.exists()}
        except cb.BackupRefusal as e:
            rec["private_key_scratch"] = {
                "kind": e.kind,
                "names_signing_key": "signing.key" in (e.detail or ""),
                "set_created": dest.exists(),
                "body_emitted": False,
            }
        # Public CA shape in scratch is NOT a secret.
        src2 = scratch / "src2"
        dest2 = scratch / "dest2"
        src2.mkdir()
        pem = src2 / "vendor" / "certifi" / "cacert.pem"
        pem.parent.mkdir(parents=True)
        pem.write_text(_PUBLIC, encoding="utf-8", newline="\n")
        (src2 / "ok.txt").write_text("ok\n", encoding="utf-8", newline="\n")
        try:
            set_dir = cb.do_backup(src2, dest2)
            rec["public_ca_scratch"] = {
                "kind": "BACKUP_OK",
                "cacert_in_manifest": "vendor/certifi/cacert.pem"
                in json.loads((set_dir / cb.MANIFEST_NAME).read_text(encoding="utf-8"))["files"],
            }
        except cb.BackupRefusal as e:
            rec["public_ca_scratch"] = {"kind": e.kind, "detail": e.detail[:200]}
    finally:
        # test scratch only
        import shutil
        shutil.rmtree(scratch, True)

    rec["ok"] = (
        rec.get("local_scope", {}).get("kind") == "ok"
        and rec.get("local_scope", {}).get("locks_in_scope_count") == 0
        and rec.get("cacert", {}).get("kind") == "public"
        and rec.get("cacert", {}).get("scan_hits") == []
        and rec.get("private_key_scratch", {}).get("kind") == "SECRETS_IN_SCOPE"
        and rec.get("public_ca_scratch", {}).get("kind") == "BACKUP_OK"
        and bool(dest_sets)
    )
    OUT.write_text(json.dumps(rec, indent=1, default=str) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=1, default=str))
    return 0 if rec["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
