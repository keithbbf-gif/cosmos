#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Emit the F-43 identity leftover proof. Scratch root only — no live/logs write.

    py -3.14 builds/backup/_emit_f43_identity_live.py
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = HERE / "_f43_identity_live.json"

import cosmos_backup_mounts as mounts                                 # noqa: E402
import cosmos_local_clock as lc                                       # noqa: E402


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="cosmos_f43_id_live_"))
    rec: dict = {
        "schema": "cosmos-backup-live/1",
        "measured_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scratch": str(tmp),
    }
    try:
        root = tmp / "live"
        root.mkdir()
        (root / ".cosmos-root.json").write_text(
            json.dumps({"system": "COSMOS", "tree_id": "KMesh-COSMOS-live",
                        "schema_version": 1}), encoding="utf-8")
        for role in ("logs", "config", "work", "state"):
            (root / role).mkdir()
        src = tmp / "src"
        src.mkdir()
        (src / "a.txt").write_text("alpha\n", encoding="utf-8", newline="\n")
        dest = tmp / "dest"
        dest.mkdir()
        probe = mounts.FakeProbe(volumes={
            str(src): "vol:SRC", str(src.resolve()): "vol:SRC",
            str(dest): "vol:DST", str(dest.resolve()): "vol:DST",
        })
        paths = lc.CosmosPaths(root)
        cfg = paths.config(lc.CONFIG_NAME)
        cfg.write_text(json.dumps({
            "schema": "cosmos-backup-targets/1",
            "targets": {"local": {
                "dest": str(dest), "source": str(src),
                "identity": {"kind": "volume_serial", "value": "vol:OTHER"},
            }},
        }), encoding="utf-8")
        mismatch = lc.tick(paths, cfg, probe=probe, force=True)
        sets = [p.name for p in dest.iterdir() if p.is_dir() and p.name != "_rehearse"]
        rec["mismatch"] = {
            "state": mismatch.get("state"),
            "kind": mismatch.get("kind"),
            "ok": mismatch.get("ok"),
            "off_volume_copy_exists": mismatch.get("off_volume_copy_exists"),
            "sets": sets,
        }
        cfg.write_text(json.dumps({
            "schema": "cosmos-backup-targets/1",
            "targets": {"local": {
                "dest": str(dest), "source": str(src),
                "identity": {"kind": "volume_serial", "value": "vol:DST"},
            }},
        }), encoding="utf-8")
        match = lc.tick(paths, cfg, probe=probe, force=True)
        rec["match"] = {
            "state": match.get("state"),
            "kind": match.get("kind"),
            "ok": match.get("ok"),
        }
        rec["ok"] = (
            rec["mismatch"]["kind"] == "IDENTITY_MISMATCH"
            and rec["mismatch"]["sets"] == []
            and rec["match"]["state"] == "VERIFIED"
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    rec["describes"] = {}
    for rel in ("cosmos_local_clock.py", "backup_targets.example.json",
                "test_local_clock.py"):
        p = HERE / rel
        rec["describes"][f"builds/backup/{rel}"] = {
            "exists": p.is_file(),
            "bytes": p.stat().st_size,
            "sha256": _sha(p),
        }
    rec["describes_schema"] = "cosmos-claim-artifact-freshness/1"
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": rec["ok"],
        "mismatch_kind": rec["mismatch"]["kind"],
        "mismatch_sets": rec["mismatch"]["sets"],
        "match_state": rec["match"]["state"],
        "out": str(OUT),
        "clock_bytes": rec["describes"]["builds/backup/cosmos_local_clock.py"]["bytes"],
        "clock_sha256": rec["describes"]["builds/backup/cosmos_local_clock.py"]["sha256"],
    }, indent=2))
    return 0 if rec["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
