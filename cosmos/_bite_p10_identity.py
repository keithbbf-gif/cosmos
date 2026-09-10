#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: P10 resolver — existence is not identity (PLAN D2).

Dir exists without `.cosmos-root.json`, or sentinel content mismatch, must be
IDENTITY_MISMATCH via `cosmos_paths` (no second resolver).

    py -3.14 cosmos/_bite_p10_identity.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from cosmos_paths import CosmosPathError, CosmosPaths, SENTINEL_NAME, write_sentinel  # noqa: E402

OUT = HERE / "_bite_p10_identity.json"


def _kind(fn) -> str | None:
    try:
        fn()
    except CosmosPathError as e:
        return e.kind
    return None


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_bite_p10_"))
    try:
        empty = td / "mesh_scar_empty"
        empty.mkdir()

        good = td / "good_root"
        write_sentinel(good, tree_id="bite-p10-a")

        wrong_system = td / "wrong_system"
        wrong_system.mkdir()
        (wrong_system / SENTINEL_NAME).write_text(
            json.dumps({"system": "NOT-COSMOS", "tree_id": "x"}), encoding="utf-8"
        )

        empty_no_sentinel = _kind(lambda: CosmosPaths(empty))
        wrong_system_kind = _kind(lambda: CosmosPaths(wrong_system))
        wrong_tree_id = _kind(
            lambda: CosmosPaths(good, expected_tree_id="not-your-tree")
        )

        ok = None
        try:
            CosmosPaths(good, expected_tree_id="bite-p10-a")
            ok = True
        except CosmosPathError:
            ok = False

        rec = {
            "schema": "cosmos-bite/1",
            "what": "P10 cosmos_paths sentinel identity (existence != identity)",
            "empty_dir_kind": empty_no_sentinel,
            "sentinel_content_mismatch_kind": wrong_system_kind,
            "tree_id_mismatch_kind": wrong_tree_id,
            "valid_root_ok": ok is True,
        }
        rec["all_bite"] = (
            rec["empty_dir_kind"] == "IDENTITY_MISMATCH"
            and rec["sentinel_content_mismatch_kind"] == "IDENTITY_MISMATCH"
            and rec["tree_id_mismatch_kind"] == "IDENTITY_MISMATCH"
            and rec["valid_root_ok"] is True
        )
    finally:
        shutil.rmtree(td, ignore_errors=True)

    OUT.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
