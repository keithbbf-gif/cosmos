#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Push builds/ to GDX after a point-in-time freeze so SOURCE_MUTATED cannot
fire on a concurrent cvm-dt/cdeck writer. Secrets scan is labels-only.

Never reads, prints, or copies key bodies. Never writes live/logs (clock
heartbeat is the clock's). Artifact is builds/backup/_gdx_builds_push.json.

    py -3.14 builds/backup/_emit_gdx_builds_push.py
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import cosmos_backup as cb
import cosmos_backup_mounts as mounts
import cosmos_backup_r2 as r2
from cosmos_backup_freeze import FrozenTree

BUILDS = Path(r"V:\A\Ai\COSMOS\builds")
CONFIG = Path(r"V:\A\Ai\COSMOS\live\config\backup_targets.json")
FREEZE_PARENT = Path(r"D:\COSMOS_BACKUP\_delme")
OUT = HERE / "_gdx_builds_push.json"
CACERT_REL = "cvm-dt/vendor/whisper_site/certifi/cacert.pem"


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _scan_pem_and_shapes(root: Path, excludes) -> dict:
    """Classify PEM-like names by BEGIN label. Never returns bodies."""
    pem_public = 0
    pem_hits = []
    path_hits = []
    cacert = None
    n = 0
    for rel in cb.iter_files(root, excludes):
        n += 1
        low = rel.replace("\\", "/").lower()
        name = low.rsplit("/", 1)[-1]
        if (name in r2.SECRET_NAMES or low.endswith(r2.SECRET_SUFFIXES)
                or any(f in low for f in r2.SECRET_PATH_FRAGMENTS)):
            path_hits.append(rel)
            continue
        if not low.endswith(cb.PEM_CLASSIFY_SUFFIXES):
            continue
        kind = cb.classify_pem_file(root / rel)
        labels = sorted(cb.read_pem_begin_labels(root / rel))
        if rel.replace("\\", "/") == CACERT_REL:
            cacert = {"rel": rel, "kind": kind, "labels": labels,
                      "size": (root / rel).stat().st_size, "body_emitted": False}
        if kind != "public":
            pem_hits.append({"rel": rel, "kind": kind, "labels": labels})
        else:
            pem_public += 1
    return {
        "file_count": n,
        "pem_public": pem_public,
        "pem_hits": pem_hits,
        "path_hits": path_hits,
        "cacert": cacert,
        "secrets_in_scope": bool(pem_hits or path_hits),
    }


def main() -> int:
    t0 = time.time()
    rec: dict = {
        "schema": "cosmos-bite/1",
        "what": "gdx/builds PUSH after freeze; certifi public, private still refuses",
        "measured_utc": _utcnow(),
        "tree_id": "KMesh-COSMOS-live",
        "source": str(BUILDS),
    }
    excludes = cb.DEFAULT_EXCLUDES
    rec["scan"] = _scan_pem_and_shapes(BUILDS, excludes)
    if rec["scan"]["secrets_in_scope"]:
        rec.update({"ok": False, "state": "REFUSED", "kind": "SECRETS_IN_SCOPE",
                    "detail": "scan named non-public PEM or secret path-shape; not pushing"})
        OUT.write_text(json.dumps(rec, indent=1, default=str) + "\n", encoding="utf-8")
        print(json.dumps(rec, indent=1, default=str))
        return 2

    dest = mounts.bind("gdx", config_path=CONFIG, source=BUILDS)
    rec["dest"] = str(dest)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    freeze_dest = FREEZE_PARENT / f"predispose_freeze_builds_{stamp}"
    rec["freeze_dest"] = str(freeze_dest)
    t_freeze = time.time()
    handle = FrozenTree.capture(BUILDS, freeze_dest, excludes=excludes)
    handle._owned = False  # never-delete: Keith stages _delme
    rec["freeze"] = {
        "kind": handle.info().get("kind"),
        "owned": False,
        "elapsed_s": round(time.time() - t_freeze, 3),
    }

    t_push = time.time()
    try:
        set_dir = cb.do_backup(BUILDS, dest, excludes=excludes, freeze=handle)
        rec["push"] = {
            "ok": True,
            "state": "PUSHED",
            "kind": "MOUNT_PUSH_OK",
            "set_dir": str(set_dir),
            "elapsed_s": round(time.time() - t_push, 3),
        }
        man_path = set_dir / cb.MANIFEST_NAME
        if man_path.is_file():
            man = json.loads(man_path.read_text(encoding="utf-8"))
            rec["push"]["file_count"] = man.get("file_count")
            rec["push"]["total_bytes"] = man.get("total_bytes")
            rec["push"]["cacert_in_manifest"] = CACERT_REL in (man.get("files") or {})
            rec["push"]["manifest_sealed"] = "seal" in man
        rec["ok"] = True
        rec["state"] = "PUSHED"
    except cb.BackupRefusal as e:
        rec["push"] = {
            "ok": False,
            "state": "REFUSED",
            "kind": e.kind,
            "detail": e.detail,
            "elapsed_s": round(time.time() - t_push, 3),
        }
        rec["ok"] = False
        rec["state"] = "REFUSED"
        rec["kind"] = e.kind
    rec["elapsed_s"] = round(time.time() - t0, 3)
    OUT.write_text(json.dumps(rec, indent=1, default=str) + "\n", encoding="utf-8")
    # Print a redacted summary: paths and kinds, never PEM bodies.
    summary = {
        "ok": rec.get("ok"),
        "state": rec.get("state"),
        "kind": rec.get("kind") or rec.get("push", {}).get("kind"),
        "set_dir": rec.get("push", {}).get("set_dir"),
        "file_count": rec.get("push", {}).get("file_count"),
        "total_bytes": rec.get("push", {}).get("total_bytes"),
        "cacert_kind": (rec.get("scan") or {}).get("cacert", {}) or {},
        "secrets_in_scope": rec["scan"]["secrets_in_scope"],
        "elapsed_s": rec["elapsed_s"],
        "artifact": str(OUT),
    }
    if isinstance(summary["cacert_kind"], dict):
        summary["cacert_kind"] = {
            "kind": summary["cacert_kind"].get("kind"),
            "labels": summary["cacert_kind"].get("labels"),
            "size": summary["cacert_kind"].get("size"),
        }
    print(json.dumps(summary, indent=1, default=str))
    return 0 if rec.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
