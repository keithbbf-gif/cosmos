#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: pre-fix cosmos_backup_clock silently truncates and still 'succeeds'.

Loads _delme/predispose_cosmos_backup_20260831T012245/cosmos_backup_clock.py
and records the four facts the SNAPSHOT_INCOMPLETE pin exists to close:

  * _copy_tree_files returns a bare int (a hole cannot be expressed)
  * limit=2 on 5 files returns 2 and does not raise
  * assemble_snapshot of 5 files returns a count (no SNAPSHOT_INCOMPLETE)
  * STAGE_LIMIT is not a patchable module constant

  py -3.14 cosmos/_bite_snapshot_incomplete.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
OLD = (REPO / "_delme" / "predispose_cosmos_backup_20260831T012245"
       / "cosmos_backup_clock.py")
OUT = HERE / "_bite_snapshot_incomplete.json"

sys.path.insert(0, str(HERE))


def _load(path: Path):
    spec = importlib.util.spec_from_file_location("cosmos_backup_clock_old", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["cosmos_backup_clock_old"] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths

    old = _load(OLD)
    td = Path(tempfile.mkdtemp(prefix="cosmos_bite_snap_"))
    root = install(td / "live", tree_id="bite-snapshot-incomplete")
    man = root / "queue" / "manifests"
    man.mkdir(parents=True, exist_ok=True)
    for i in range(5):
        (man / ("m%d.json" % i)).write_text("{}", encoding="utf-8")
    dest = td / "copy"
    returned = old._copy_tree_files(man, dest, limit=2)
    raised = None
    n = None
    try:
        n = old.assemble_snapshot(CosmosPaths(root), Path(td / "stage"))
    except Exception as e:  # noqa: BLE001
        raised = "%s:%s" % (type(e).__name__, getattr(e, "kind", e))

    bite = {
        "copy_returns_bare_int": isinstance(returned, int),
        "copy_returned": returned if not isinstance(returned, dict) else sorted(returned),
        "silent_truncate_copied_2_of_5": returned == 2,
        "assemble_did_not_raise": raised is None,
        "assemble_returned": n,
        "assemble_raised": raised,
        "has_stage_limit": hasattr(old, "STAGE_LIMIT"),
        "has_snapshot_incomplete_in_source": "SNAPSHOT_INCOMPLETE" in OLD.read_text(
            encoding="utf-8"),
    }
    bite["all_bite"] = (
        bite["copy_returns_bare_int"]
        and bite["silent_truncate_copied_2_of_5"]
        and bite["assemble_did_not_raise"]
        and not bite["has_stage_limit"]
        and not bite["has_snapshot_incomplete_in_source"]
    )
    OUT.write_text(json.dumps(bite, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(bite, indent=2))
    return 0 if bite["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
