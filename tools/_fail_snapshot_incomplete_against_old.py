#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the SNAPSHOT_INCOMPLETE pins FAIL against the staged pre-change clock.

A pin that PASSES on the old module is not a pin.

  py -3.14 cosmos/_fail_snapshot_incomplete_against_old.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent.parent / "cosmos"
REPO = HERE.parent
OLD = (REPO / "_delme" / "predispose_cosmos_backup_20260831T012245"
       / "cosmos_backup_clock.py")
OUT = HERE / "_fail_snapshot_incomplete_against_old.json"

sys.path.insert(0, str(HERE))


def _load(path: Path):
    spec = importlib.util.spec_from_file_location("cosmos_backup_clock_old", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["cosmos_backup_clock_old"] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    from cosmos_backup import BackupError
    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths

    old = _load(OLD)
    td = Path(tempfile.mkdtemp(prefix="cosmos_fail_snap_"))
    root = install(td / "live", tree_id="fail-snapshot-incomplete")
    man = root / "queue" / "manifests"
    man.mkdir(parents=True, exist_ok=True)
    for i in range(5):
        (man / ("m%d.json" % i)).write_text("{}", encoding="utf-8")
    paths = CosmosPaths(root)
    stage = paths.backups("_snapshot")
    pins = []

    def pin(name, fn):
        try:
            ok = bool(fn())
            err = ""
        except Exception as e:  # noqa: BLE001
            ok = False
            err = "%s: %s" % (type(e).__name__, e)
        pins.append({"name": name, "passed_on_old": ok, "err": err})

    rec = old._copy_tree_files(man, td / "d0")
    pin("_copy_tree_files returns a dict record",
        lambda: isinstance(rec, dict)
        and {"copied", "truncated", "unreadable", "skipped_large"} <= set(rec))

    rec2 = old._copy_tree_files(man, td / "d1", limit=2)
    pin("_copy_tree_files(limit=2) declares truncated=True",
        lambda: isinstance(rec2, dict) and rec2.get("truncated") is True)

    def _raises_incomplete():
        with mock.patch.object(old, "STAGE_LIMIT", 2, create=True):
            try:
                old.assemble_snapshot(paths, stage)
            except BackupError as e:
                return e.kind == "SNAPSHOT_INCOMPLETE"
            except Exception as e:  # noqa: BLE001
                return getattr(e, "kind", None) == "SNAPSHOT_INCOMPLETE"
            return False

    pin("assemble_snapshot with STAGE_LIMIT=2 raises SNAPSHOT_INCOMPLETE",
        _raises_incomplete)

    def _names_subtree():
        with mock.patch.object(old, "STAGE_LIMIT", 2, create=True):
            try:
                old.assemble_snapshot(paths, stage)
            except Exception as e:  # noqa: BLE001
                return (getattr(e, "kind", None) == "SNAPSHOT_INCOMPLETE"
                        and "queue/manifests" in str(e))
            return False

    pin("SNAPSHOT_INCOMPLETE names queue/manifests",
        _names_subtree)

    def _poll_failed():
        with mock.patch.object(old, "STAGE_LIMIT", 2, create=True):
            r = old.poll_once(str(root), force=True)
        return (r.get("ok") is False and r.get("state") == "FAILED"
                and r.get("kind") == "SNAPSHOT_INCOMPLETE")

    pin("poll_once truncated scope is FAILED SNAPSHOT_INCOMPLETE",
        _poll_failed)

    def _no_verified():
        led = root / "ledger" / "authority.jsonl"
        txt = led.read_text(encoding="utf-8") if led.is_file() else ""
        return "BACKUP_VERIFIED" not in txt

    pin("no BACKUP_VERIFIED over a truncated scope (after STAGE_LIMIT=2 poll)",
        _no_verified)

    failed = [p for p in pins if not p["passed_on_old"]]
    out = {
        "old_path": str(OLD),
        "pins": pins,
        "pin_count": len(pins),
        "failed_on_old": len(failed),
        "all_new_pins_failed": len(failed) == len(pins) and len(pins) > 0,
    }
    OUT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 0 if out["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
