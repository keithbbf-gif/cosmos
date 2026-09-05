#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""New F-43 identity pins MUST FAIL against the staged predecessor.

Staged at builds/backup/_delme/predispose_f43_identity_20260831T162758Z/

Predecessor (measured `_bite_f43_identity.json`):
  * bind_local has no identity param
  * tick() with a volume_serial mismatch VERIFIED and created a set
  * identity as a string was silent
  * unknown identity.kind was silent
  * example local row had no identity key

    py -3.14 builds/backup/_fail_f43_identity_against_old.py
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "_fail_f43_identity_against_old.json"
OLD = HERE / "_delme" / "predispose_f43_identity_20260831T162758Z"

NEW_PINS = (
    "bind_has_identity_param",
    "mismatch_tick_is_IDENTITY_MISMATCH",
    "mismatch_created_no_set",
    "identity_str_is_BAD_CONFIG",
    "unknown_kind_is_BAD_CONFIG",
    "example_local_has_identity",
)


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    sys.path.insert(0, str(HERE))
    if not (OLD / "cosmos_local_clock.py").is_file():
        raise SystemExit(f"missing predecessor {OLD}")
    old_lc = _load(OLD / "cosmos_local_clock.py", "old_local_clock_f43_id")
    import cosmos_backup_mounts as mounts  # noqa: E402

    tmp = Path(tempfile.mkdtemp(prefix="cosmos_fail_f43_id_"))
    pins = {k: False for k in NEW_PINS}
    detail: dict = {}
    try:
        root = tmp / "live"
        root.mkdir()
        (root / ".cosmos-root.json").write_text(
            json.dumps({"system": "COSMOS", "tree_id": "KMesh-COSMOS-test",
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
        paths = old_lc.CosmosPaths(root)
        cfg = paths.config(old_lc.CONFIG_NAME)

        pins["bind_has_identity_param"] = (
            "identity" in old_lc.bind_local.__code__.co_varnames)

        cfg.write_text(json.dumps({
            "schema": "cosmos-backup-targets/1",
            "targets": {"local": {
                "dest": str(dest), "source": str(src),
                "identity": {"kind": "volume_serial", "value": "vol:OTHER"},
            }},
        }), encoding="utf-8")
        rec = old_lc.tick(paths, cfg, probe=probe, force=True)
        detail["mismatch_tick"] = {"state": rec.get("state"), "kind": rec.get("kind")}
        pins["mismatch_tick_is_IDENTITY_MISMATCH"] = rec.get("kind") == "IDENTITY_MISMATCH"
        sets = [p for p in dest.iterdir() if p.is_dir() and p.name != "_rehearse"]
        pins["mismatch_created_no_set"] = not sets
        detail["mismatch_set_count"] = len(sets)

        cfg.write_text(json.dumps({
            "schema": "cosmos-backup-targets/1",
            "targets": {"local": {
                "dest": str(dest), "source": str(src),
                "identity": "vol:OTHER",
            }},
        }), encoding="utf-8")
        rec2 = old_lc.tick(paths, cfg, probe=probe, force=True)
        detail["identity_str"] = {"state": rec2.get("state"), "kind": rec2.get("kind")}
        pins["identity_str_is_BAD_CONFIG"] = rec2.get("kind") == "BAD_CONFIG"

        cfg.write_text(json.dumps({
            "schema": "cosmos-backup-targets/1",
            "targets": {"local": {
                "dest": str(dest), "source": str(src),
                "identity": {"kind": "drive_letter", "value": "D:"},
            }},
        }), encoding="utf-8")
        rec3 = old_lc.tick(paths, cfg, probe=probe, force=True)
        detail["unknown_kind"] = {"state": rec3.get("state"), "kind": rec3.get("kind")}
        pins["unknown_kind_is_BAD_CONFIG"] = rec3.get("kind") == "BAD_CONFIG"

        example = json.loads(
            (OLD / "backup_targets.example.json").read_text(encoding="utf-8"))
        pins["example_local_has_identity"] = (
            "identity" in (example.get("targets") or {}).get("local", {}))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    rec_out = {
        "what": "new F-43 identity pins FAIL against predecessor (identity unread)",
        "predecessor": str(OLD),
        "pins": pins,
        "detail": detail,
        "failed_pins": [k for k in NEW_PINS if pins[k] is False],
        "passed_pins": [k for k in NEW_PINS if pins[k] is True],
    }
    rec_out["all_new_pins_failed"] = all(pins[k] is False for k in NEW_PINS)
    OUT.write_text(json.dumps(rec_out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({
        "all_new_pins_failed": rec_out["all_new_pins_failed"],
        "failed": rec_out["failed_pins"],
        "passed": rec_out["passed_pins"],
        "detail": detail,
    }, indent=2))
    return 0 if rec_out["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
