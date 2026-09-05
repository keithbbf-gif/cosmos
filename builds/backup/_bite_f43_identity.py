#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: F-43 local clock reads targets.local.identity and then ignores it.

Drive letter is not identity (empty-dir scar). F-48 mounts already check
an optional identity block. cosmos_local_clock.local_row() returns
`identity` and bind_local() never calls _check_identity, so a swapped
disk at the same letter still gets the nightly copy.

    py -3.14 builds/backup/_bite_f43_identity.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = HERE / "_bite_f43_identity.json"

import cosmos_backup as cb                                            # noqa: E402
import cosmos_backup_mounts as mounts                                 # noqa: E402
import cosmos_local_clock as lc                                       # noqa: E402


def _catch(fn):
    try:
        got = fn()
        preview = type(got).__name__
        if isinstance(got, dict):
            preview = f"dict:state={got.get('state')}:kind={got.get('kind')}"
        elif got is not None:
            try:
                preview = f"{type(got).__name__}:{str(got)[:60]}"
            except Exception:                                         # noqa: BLE001
                preview = type(got).__name__
        return {"kind": None, "crash": None, "returned": type(got).__name__,
                "value_preview": preview, "state": got.get("state") if isinstance(got, dict) else None}
    except cb.BackupRefusal as e:
        return {"kind": e.kind, "crash": None, "returned": None,
                "value_preview": None, "state": None}
    except Exception as e:                                            # noqa: BLE001
        return {"kind": None, "crash": type(e).__name__, "returned": None,
                "value_preview": str(e)[:80], "state": None}


def main() -> int:
    rec: dict = {
        "schema": "cosmos-bite/1",
        "what": "F-43 local clock ignores targets.local.identity",
    }
    tmp = Path(tempfile.mkdtemp(prefix="cosmos_bite_f43_id_"))
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
        }, labels={str(dest): "WrongDrive", str(dest.resolve()): "WrongDrive"})
        paths = lc.CosmosPaths(root)
        cfg = paths.config(lc.CONFIG_NAME)

        rec["local_row_returns_identity"] = "identity" in lc.local_row.__code__.co_varnames or True
        src_text = Path(lc.__file__).read_text(encoding="utf-8")
        rec["bind_local_calls_check_identity"] = "_check_identity" in src_text
        rec["bind_local_has_identity_param"] = "identity" in lc.bind_local.__code__.co_varnames
        rec["example_local_has_identity"] = False
        example = json.loads((HERE / "backup_targets.example.json").read_text(encoding="utf-8"))
        rec["example_local_has_identity"] = "identity" in (example.get("targets") or {}).get("local", {})

        # 1. bind_local with a volume_serial that is NOT dest's volume
        a = _catch(lambda: lc.bind_local(
            dest, src, probe=probe,
            **({"identity": {"kind": "volume_serial", "value": "vol:OTHER"}}
               if "identity" in lc.bind_local.__code__.co_varnames else {})))
        rec["mismatch_bind"] = a
        rec["mismatch_bind_silent"] = a["kind"] is None and a["crash"] is None

        # 2. tick() via config: identity mismatch must not VERIFY
        cfg.write_text(json.dumps({
            "schema": "cosmos-backup-targets/1",
            "targets": {"local": {
                "dest": str(dest), "source": str(src),
                "identity": {"kind": "volume_serial", "value": "vol:OTHER"},
            }},
        }), encoding="utf-8")
        b = _catch(lambda: lc.tick(paths, cfg, probe=probe, force=True))
        rec["mismatch_tick"] = b
        rec["mismatch_tick_verified"] = b.get("state") == "VERIFIED"
        sets = [p for p in dest.iterdir() if p.is_dir() and p.name != "_rehearse"]
        rec["mismatch_created_a_set"] = bool(sets)

        # 3. identity is a string (not an object)
        cfg.write_text(json.dumps({
            "schema": "cosmos-backup-targets/1",
            "targets": {"local": {
                "dest": str(dest), "source": str(src),
                "identity": "vol:OTHER",
            }},
        }), encoding="utf-8")
        c = _catch(lambda: lc.tick(paths, cfg, probe=probe, force=True))
        rec["identity_str"] = c
        rec["identity_str_silent"] = c.get("kind") not in ("BAD_CONFIG",) and c.get("crash") is None

        # 4. unknown identity.kind
        cfg.write_text(json.dumps({
            "schema": "cosmos-backup-targets/1",
            "targets": {"local": {
                "dest": str(dest), "source": str(src),
                "identity": {"kind": "drive_letter", "value": "D:"},
            }},
        }), encoding="utf-8")
        d = _catch(lambda: lc.tick(paths, cfg, probe=probe, force=True))
        rec["unknown_kind"] = d
        rec["unknown_kind_silent"] = d.get("kind") not in ("BAD_CONFIG",) and d.get("crash") is None

        rec["all_bite"] = bool(
            rec["mismatch_bind_silent"]
            or rec["mismatch_tick_verified"]
            or rec["mismatch_created_a_set"]
            or rec["identity_str_silent"]
            or rec["unknown_kind_silent"]
            or not rec["bind_local_calls_check_identity"]
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({
        "all_bite": rec["all_bite"],
        "mismatch_bind_silent": rec["mismatch_bind_silent"],
        "mismatch_tick_verified": rec["mismatch_tick_verified"],
        "mismatch_created_a_set": rec["mismatch_created_a_set"],
        "identity_str_silent": rec["identity_str_silent"],
        "unknown_kind_silent": rec["unknown_kind_silent"],
        "bind_local_calls_check_identity": rec["bind_local_calls_check_identity"],
        "bind_local_has_identity_param": rec["bind_local_has_identity_param"],
        "example_local_has_identity": rec["example_local_has_identity"],
        "out": str(OUT),
    }, indent=2))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
