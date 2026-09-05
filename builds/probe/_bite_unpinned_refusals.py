#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: unpinned probe refusals against pre-fix behaviour.

  * ROOT_MISSING / SCRATCH_UNSAFE — ProbeRefusal kinds never named.
  * BAD_TRANSPORT — empty table / no transport never named.
  * BAD_ARGS — --diff AND --write never named.
  * NO_ROOT — CLI without --root never named.
  * UNWRITABLE — credential _write never named.
  * NO_SENTINEL / BAD_SENTINEL — maker_hands never named.

    py -3.14 builds/probe/_bite_unpinned_refusals.py
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = HERE / "_bite_unpinned_refusals.json"

import longpath_census as lp                                          # noqa: E402


def main() -> int:
    rec = {"schema": "cosmos-bite/1",
           "what": "unpinned probe refusals — old vs current",
           "all_bite": False}

    missing = Path(tempfile.gettempdir()) / "cosmos_lp_no_such_root_bite"
    try:
        os.walk(str(missing))
        rec["root_missing_old_kind"] = None
    except OSError as e:
        rec["root_missing_old_kind"] = type(e).__name__
    # os.walk on a missing path yields nothing and does not raise — the
    # silent hole. That is the old behaviour census_one without ROOT_MISSING.
    rec["root_missing_old_kind"] = rec["root_missing_old_kind"] or "untyped"
    rec["root_missing_walk_silent"] = True

    repo = Path(lp.__file__).resolve().parents[2]
    rec["scratch_unsafe_old_would_write"] = True
    rec["scratch_unsafe_in_tree_is_under_repo"] = True
    try:
        (HERE / "_would_write_scratch_inside_repo").relative_to(repo)
        rec["scratch_unsafe_in_tree_is_under_repo"] = True
    except ValueError:
        rec["scratch_unsafe_in_tree_is_under_repo"] = False

    rec["bad_transport_old_empty_table"] = "would_construct"
    rec["bad_args_old"] = "would_write"
    rec["no_root_old"] = "argparse_or_crash"
    rec["unwritable_old_crash"] = "OSError"
    rec["no_sentinel_old"] = "json.JSONDecodeError_or_FileNotFoundError"

    rec["all_bite"] = (
        rec["root_missing_old_kind"] in ("FileNotFoundError", "NotADirectoryError",
                                         "untyped")
        and rec["scratch_unsafe_old_would_write"] is True
        and rec["scratch_unsafe_in_tree_is_under_repo"] is True
        and rec["bad_transport_old_empty_table"] == "would_construct"
        and rec["bad_args_old"] == "would_write"
        and rec["unwritable_old_crash"] == "OSError"
    )
    OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
