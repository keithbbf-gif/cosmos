#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-measure ADAPTERS['r2']() against the CURRENT cosmos_backup.py.

No credential is opened: the factory REFUSES NO_CREDENTIALS before a
transport is built. Stamps describes so a later edit cannot hide here.

    py -3.14 builds/backup/_emit_f47_live.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cosmos_backup as cb

HERE = Path(__file__).resolve().parent
OUT = HERE / "_f47_live_adapter.json"


def main() -> int:
    rec = {
        "schema": "cosmos-f47-live-adapter/1",
        "writes": 0,
        "raised": False,
        "kind": None,
        "detail": None,
        "has_do_rehearse_target": hasattr(cb, "do_rehearse_target"),
        "adapter_is_factory": callable(cb.ADAPTERS.get("r2")),
        "default_excludes": list(getattr(cb, "DEFAULT_EXCLUDES", ())),
    }
    try:
        cb.ADAPTERS["r2"]()
        rec["raised"] = False
        rec["kind"] = None
    except cb.BackupRefusal as e:
        rec["raised"] = True
        rec["kind"] = e.kind
        rec["detail"] = str(e)
    rec["ok"] = rec["kind"] == "NO_CREDENTIALS" and rec["writes"] == 0
    sys.path.insert(0, str(HERE.parent / "probe"))
    import artifact_freshness as af                                    # noqa: WPS433
    af.write_stamped(OUT, rec, HERE.parents[1],
                     ["builds/backup/cosmos_backup.py"])
    print(json.dumps(rec, indent=2, default=str))
    return 0 if rec["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
