#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Live values for F-43 freeze. Never points at live/backups. Never reads
a credential. FrozenTree backup of a scratch tree + a VSS probe that
creates-and-deletes a shadow (or types VSS_UNAVAILABLE). Output:
`builds/backup/_f43_freeze_live.json`.

    py -3.14 builds/backup/_emit_f43_freeze_live.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

import cosmos_backup as cb
import cosmos_backup_freeze as fz

HERE = Path(__file__).resolve().parent
OUT = HERE / "_f43_freeze_live.json"
KEY = b"test-hmac-key-not-a-real-secret"


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="cosmos_f43_freeze_live_"))
    rec = {"schema": "cosmos-backup-live/1", "scratch": str(tmp)}
    try:
        src = tmp / "src"
        dest = tmp / "dest"
        src.mkdir()
        (src / "a.txt").write_text("alpha\n", encoding="utf-8", newline="\n")
        orig_hash = cb.sha256_file(src / "a.txt")
        handle = fz.FrozenTree.capture(src, tmp / "frozen")
        (src / "a.txt").write_bytes(b"MUTATED-LIVE\n")
        set_dir = cb.do_backup(src, dest, key=KEY, freeze=handle)
        manifest = json.loads((set_dir / cb.MANIFEST_NAME).read_text(encoding="utf-8"))
        rec["frozen_kind"] = manifest.get("freeze", {}).get("kind")
        rec["frozen_hash"] = manifest["files"]["a.txt"]["sha256"]
        rec["live_hash"] = cb.sha256_file(src / "a.txt")
        rec["orig_hash"] = orig_hash
        rec["frozen_survived"] = (
            rec["frozen_hash"] == orig_hash
            and rec["frozen_hash"] != rec["live_hash"]
            and rec["frozen_kind"] == "copy"
        )

        probe = fz.probe("V:\\")
        rec["vss_kind"] = probe.get("kind")
        rec["vss_detail"] = probe.get("detail")
        rec["vss_drive_type"] = probe.get("drive_type")
        rec["vss_filesystem"] = probe.get("filesystem")
        rec["vss_released"] = probe.get("released")
        rec["vss_ok_typed"] = probe.get("ok")
        rec["vss_binding"] = probe.get("binding")
        rec["vss_shadow_id"] = probe.get("shadow_id")

        rec["ok"] = (
            rec["frozen_survived"] is True
            and rec["vss_ok_typed"] is True
            and rec["vss_kind"] in ("ok", "VSS_UNAVAILABLE")
        )
    except Exception as e:  # noqa: BLE001
        rec["ok"] = False
        rec["crash"] = f"{type(e).__name__}: {e}"
    finally:
        shutil.rmtree(tmp, True)

    sys.path.insert(0, str(HERE.parent / "probe"))
    import artifact_freshness as af                                    # noqa: WPS433
    af.write_stamped(OUT, rec, HERE.parents[1],
                     ["builds/backup/cosmos_backup.py",
                      "builds/backup/cosmos_backup_freeze.py"])
    print(json.dumps(rec, indent=2, default=str))
    return 0 if rec.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
