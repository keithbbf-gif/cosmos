#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: round-6 unpinned backup refusals against CURRENT code.

Documented-but-never-tested, plus garbage that still crashes untyped:

  * acquire(freeze="yes") / freeze=1                         — BAD_FREEZE?
  * FrozenTree.capture onto an occupied dest                  — FREEZE_DEST_OCCUPIED?
  * do_backup(..., freeze="yes") must not create a set
  * seal([]) / seal(None)                                     — crash?
  * scan_secrets({}) / scan_secrets([]) / files=str           — crash or silent?
  * local_clock bind_local relative dest                      — BAD_CONFIG?
  * local_clock dest-is-a-file                                — typed?
  * local_clock targets.local is a list                       — typed?

Expected before a pin: all_bite == true (at least one crash or silent-pass
where a kind is required).

    py -3.14 builds/backup/_bite_unpinned_round6.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = HERE / "_bite_unpinned_round6.json"

import cosmos_backup as cb                                            # noqa: E402
import cosmos_backup_freeze as fz                                     # noqa: E402
import cosmos_backup_mounts as mounts                                 # noqa: E402
import cosmos_local_clock as lc                                       # noqa: E402
import cosmos_backup_r2 as r2                                         # noqa: E402


def _catch(fn):
    try:
        got = fn()
        preview = type(got).__name__
        if got is not None and not isinstance(got, (bool, int)):
            try:
                preview = f"{type(got).__name__}:{str(got)[:60]}"
            except Exception:                                         # noqa: BLE001
                preview = type(got).__name__
        return {"kind": None, "crash": None, "returned": type(got).__name__,
                "value_preview": preview}
    except cb.BackupRefusal as e:
        return {"kind": e.kind, "crash": None, "returned": None,
                "value_preview": None}
    except Exception as e:                                            # noqa: BLE001
        return {"kind": None, "crash": type(e).__name__, "returned": None,
                "value_preview": str(e)[:80]}


def main() -> int:
    rec = {"schema": "cosmos-bite/1",
           "what": "round6 unpinned backup refusals — current vs claimed"}
    tmp = Path(tempfile.mkdtemp(prefix="cosmos_bite6_"))
    try:
        src = tmp / "src"
        src.mkdir()
        (src / "a.txt").write_text("alpha\n", encoding="utf-8", newline="\n")
        dest = tmp / "dest"
        dest.mkdir()

        a = _catch(lambda: fz.acquire(src, "yes"))
        rec["freeze_yes"] = a
        b = _catch(lambda: fz.acquire(src, 1))
        rec["freeze_int"] = b
        c = _catch(lambda: fz.acquire(src, ""))
        rec["freeze_empty"] = c

        occupied = tmp / "frozen_occupied"
        occupied.mkdir()
        (occupied / "x").write_text("stay", encoding="utf-8")
        d = _catch(lambda: fz.FrozenTree.capture(src, occupied))
        rec["freeze_dest_occupied_dir"] = d
        rec["occupied_dir_untouched"] = (occupied / "x").is_file()

        occupied_file = tmp / "frozen_file"
        occupied_file.write_text("not-a-dir", encoding="utf-8")
        e = _catch(lambda: fz.FrozenTree.capture(src, occupied_file))
        rec["freeze_dest_occupied_file"] = e
        rec["occupied_file_untouched"] = occupied_file.is_file() and not occupied_file.is_dir()

        f = _catch(lambda: cb.do_backup(src, dest, freeze="yes"))
        rec["do_backup_freeze_yes"] = f
        rec["do_backup_freeze_yes_created"] = dest.exists() and any(dest.iterdir())

        g = _catch(lambda: cb.seal([]))
        rec["seal_array"] = g
        h = _catch(lambda: cb.seal(None))
        rec["seal_none"] = h
        i = _catch(lambda: cb.seal("x"))
        rec["seal_str"] = i

        j = _catch(lambda: cb.scan_secrets({}))
        rec["scan_empty_obj"] = j
        k = _catch(lambda: cb.scan_secrets([]))
        rec["scan_array"] = k
        m = _catch(lambda: r2.scan_secrets({"files": "install_key.bin"}))
        rec["scan_files_str"] = m
        n = _catch(lambda: r2.scan_secrets({"files": None}))
        rec["scan_files_none"] = n
        o = _catch(lambda: r2.scan_secrets({"files": 1}))
        rec["scan_files_int"] = o

        p = _catch(lambda: lc.bind_local(Path("relative/dest"), src,
                                         probe=mounts.FakeProbe()))
        rec["local_relative_dest"] = p

        dest_file = tmp / "dest_is_file"
        dest_file.write_text("not-a-dir", encoding="utf-8")
        probe = mounts.FakeProbe(volumes={
            str(src): "vol:SRC", str(src.resolve()): "vol:SRC",
            str(dest_file): "vol:DST", str(dest_file.resolve()): "vol:DST",
        })
        q = _catch(lambda: lc.bind_local(dest_file, src, probe=probe))
        rec["local_dest_is_file"] = q
        rec["local_dest_file_untouched"] = dest_file.is_file()

        root = tmp / "live"
        root.mkdir()
        (root / ".cosmos-root.json").write_text(
            json.dumps({"system": "COSMOS", "tree_id": "KMesh-COSMOS-test",
                        "schema_version": 1}), encoding="utf-8")
        for role in ("logs", "config", "work", "state"):
            (root / role).mkdir()
        paths = lc.CosmosPaths(root)
        cfg = paths.config(lc.CONFIG_NAME)
        cfg.write_text(json.dumps({
            "schema": "cosmos-backup-targets/1",
            "targets": {"local": ["not", "a", "row"]},
        }), encoding="utf-8")
        r = _catch(lambda: lc.tick(paths, cfg, force=True))
        rec["local_targets_list"] = r
        rec["local_targets_list_heartbeat_kind"] = r.get("kind")
        rec["local_targets_list_crash"] = r.get("crash")
        # tick swallows BackupRefusal into rec["kind"]; _catch on tick()
        # returns the heartbeat dict, not a raise.
        if r.get("returned") == "dict":
            rec["local_targets_list"] = {
                "kind": None, "crash": None, "returned": "dict",
                "value_preview": r.get("value_preview"),
            }
            try:
                hb = json.loads(paths.logs(lc.HEARTBEAT_NAME).read_text(encoding="utf-8"))
                rec["local_targets_list_hb_kind"] = hb.get("kind")
                rec["local_targets_list_hb_state"] = hb.get("state")
            except Exception as ex:                                   # noqa: BLE001
                rec["local_targets_list_hb_err"] = type(ex).__name__

        # Classify: a bite is a crash, a silent-pass where a kind is
        # required, or a documented kind that no suite names.
        bites = []
        for name in ("freeze_yes", "freeze_int", "freeze_empty",
                     "freeze_dest_occupied_dir", "freeze_dest_occupied_file",
                     "do_backup_freeze_yes",
                     "seal_array", "seal_none", "seal_str",
                     "scan_empty_obj", "scan_array", "scan_files_str",
                     "scan_files_none", "scan_files_int",
                     "local_relative_dest", "local_dest_is_file"):
            row = rec.get(name) or {}
            if row.get("crash"):
                bites.append(name)
            elif row.get("kind") is None and name.startswith(("seal_", "scan_",
                                                              "freeze_", "do_backup",
                                                              "local_")):
                bites.append(name + ":silent")
        rec["bites"] = bites
        rec["all_bite"] = bool(bites)
        rec["documented_freeze_kinds_exist"] = (
            (rec["freeze_yes"].get("kind") == "BAD_FREEZE")
            and (rec["freeze_dest_occupied_dir"].get("kind") == "FREEZE_DEST_OCCUPIED")
        )
        rec["untyped_seal"] = rec["seal_array"].get("crash")
        rec["untyped_scan"] = rec["scan_empty_obj"].get("crash") or rec["scan_array"].get("crash")
        rec["scan_files_str_silent"] = (
            rec["scan_files_str"].get("kind") is None
            and rec["scan_files_str"].get("crash") is None
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    OUT.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: rec[k] for k in rec if k not in ()}, indent=2, default=str))
    print("all_bite", rec["all_bite"], "bites", rec["bites"])
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
