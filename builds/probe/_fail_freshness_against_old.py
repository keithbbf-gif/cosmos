#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fail-against-old: staged pre-stamp artifacts are UNFINGERPRINTED.

Required before belief. Points at the never-delete incumbents, not the
live files (those get stamped after this bite). Every registered artifact
that existed pre-stamp must still be UNFINGERPRINTED in the staged copy.

    py -3.14 builds/probe/_fail_freshness_against_old.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

import artifact_freshness as af                                         # noqa: E402

STAGED = HERE / "_delme" / "predispose_claim_artifacts_20260831T133500Z"
OUT = HERE / "_fail_freshness_against_old.json"

# artifact rel in the live tree -> filename in the staged dir
STAGED_NAMES = {
    "builds/probe/_longpath_behaviour.json": "_longpath_behaviour.json",
    "builds/probe/_tools_surface_live.json": "_tools_surface_live.json",
    "builds/probe/_blockers_freshness.json": "_blockers_freshness.json",
    "builds/probe/MESH_STATUS.json": "MESH_STATUS.json",
    "builds/backup/_f43_mutate_retire_live.json": "_f43_mutate_retire_live.json",
    "builds/backup/_f47_live_adapter.json": "_f47_live_adapter.json",
    "builds/backup/_hmac_copyhash_live.json": "_hmac_copyhash_live.json",
    "builds/backup/_stage_restore_live.json": "_stage_restore_live.json",
    "builds/backup/_f54_live_preflight.json": "_f54_live_preflight.json",
    "builds/probe/_f41_live_apply_refused.json": "_f41_live_apply_refused.json",
}


def main() -> int:
    rows = []
    for art, srcs, hint in af.CLAIM_ARTIFACTS:
        name = STAGED_NAMES.get(art)
        path = STAGED / name if name else None
        live = af.fingerprint(REPO, srcs)
        if path is None or not path.is_file():
            rows.append({"artifact": art, "kind": "STAGED_ABSENT", "ok": False})
            continue
        rec = json.loads(path.read_text(encoding="utf-8"))
        out = af.compare(rec.get("describes"), live)
        rows.append({"artifact": art, "kind": out["kind"], "ok": out["kind"] == "UNFINGERPRINTED"})
    bad = [r for r in rows if not r["ok"]]
    doc = {
        "schema": "cosmos-fail-against-old/1",
        "staged": str(STAGED),
        "all_new_pins_failed": all(r["kind"] == "UNFINGERPRINTED" for r in rows) and len(rows) == 10,
        "rows": rows,
        "checked": len(rows),
        "unfingerprinted": sum(1 for r in rows if r["kind"] == "UNFINGERPRINTED"),
    }
    OUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8", newline="\n")
    print(json.dumps(doc, indent=2, sort_keys=True))
    return 0 if doc["all_new_pins_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
