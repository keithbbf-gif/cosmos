#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-measure HMAC live kinds against the CURRENT cosmos_backup.py.

Scratch only. Never opens a credential. Stamps describes so a later edit
of the module cannot hide behind this file.

    py -3.14 builds/backup/_emit_hmac_copyhash_live.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

import cosmos_backup as cb

HERE = Path(__file__).resolve().parent
OUT = HERE / "_hmac_copyhash_live.json"
KEY = b"live-hmac-key-not-a-secret"


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="cosmos_hmac_live_"))
    rec = {
        "schema": "cosmos-hmac-copyhash-live/1",
        "check_seal_file": str((HERE / "cosmos_backup.py").resolve()),
    }
    try:
        src = tmp / "src"
        dest = tmp / "dest"
        src.mkdir()
        dest.mkdir()
        (src / "a.txt").write_text("alpha\n", encoding="utf-8", newline="\n")
        set_dir = cb.do_backup(src, dest, key=KEY)
        sealed = json.loads((set_dir / cb.MANIFEST_NAME).read_text(encoding="utf-8"))

        forged = json.loads(json.dumps(sealed))
        forged["seal"]["hmac_sha256"] = "0" * 64
        try:
            cb.check_seal(forged, KEY)
            rec["forged_hmac_kind"] = "PASSED"
        except cb.BackupRefusal as e:
            rec["forged_hmac_kind"] = e.kind

        nul = json.loads(json.dumps(sealed))
        nul["seal"]["hmac_sha256"] = None
        rec["null_hmac_crash"] = None
        try:
            cb.check_seal(nul, KEY)
            rec["null_hmac_kind"] = "PASSED"
        except cb.BackupRefusal as e:
            rec["null_hmac_kind"] = e.kind
        except Exception as e:                                        # noqa: BLE001
            rec["null_hmac_kind"] = None
            rec["null_hmac_crash"] = type(e).__name__
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    rec["ok"] = (rec.get("forged_hmac_kind") == "SEAL_HMAC_MISMATCH"
                 and rec.get("null_hmac_kind") == "SEAL_HMAC_MISMATCH"
                 and rec.get("null_hmac_crash") is None)
    sys.path.insert(0, str(HERE.parent / "probe"))
    import artifact_freshness as af                                    # noqa: WPS433
    af.write_stamped(OUT, rec, HERE.parents[1],
                     ["builds/backup/cosmos_backup.py"])
    print(json.dumps(rec, indent=2, default=str))
    return 0 if rec["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
