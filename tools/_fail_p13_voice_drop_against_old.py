#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pin: pre-validation ingest wrote malformed JSON straight to the bucket.

Current file_drop calls parse_order and refuses BAD_INPUT. This script proves
the old naive path would have landed a missing-Agent drop (the scar P13 closes).

    py -3.14 cosmos/_fail_p13_voice_drop_against_old.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent / "cosmos"
sys.path.insert(0, str(HERE))

from cosmos_paths import CosmosPaths, write_sentinel  # noqa: E402
from cosmos_sgh_drop_ingest import GH_DROP_PATH, file_drop  # noqa: E402
from cosmos_work_order import OrderError, work_order_dirs  # noqa: E402


def naive_bucket_write(paths: CosmosPaths, *, name: str, raw: dict) -> Path:
    dest = work_order_dirs(paths)["bucket"] / name
    dest.write_text(json.dumps(raw), encoding="utf-8")
    return dest


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_fail_p13_"))
    live = td / "live"
    write_sentinel(live, tree_id="p13-fail-old")
    (live / "state").mkdir(parents=True, exist_ok=True)
    paths = CosmosPaths(live)
    malformed = {
        "Context source": "docs/AGENT_BRIEF.md [read*]",
        "Task": "no Agent",
        "Target & scope": "x",
        "Timestamp": "2026-09-10T12:00:00-05:00",
        "Output": "out | x.txt",
    }
    fetched = {
        "name": "wo-malformed.json",
        "path": f"{GH_DROP_PATH}/wo-malformed.json",
        "sha": "sha-old",
        "text": json.dumps(malformed),
    }
    old_dest = naive_bucket_write(paths, name="wo-malformed.json", raw=malformed)
    old_body = json.loads(old_dest.read_text(encoding="utf-8")) if old_dest.is_file() else {}
    old_landed = old_dest.is_file() and "Agent" not in old_body

    new_kind = None
    try:
        file_drop(paths, fetched)
    except OrderError as e:
        new_kind = e.kind

    ok = old_landed and new_kind == "BAD_INPUT"
    print(json.dumps({
        "old_naive_landed_without_agent": old_landed,
        "new_file_drop_kind": new_kind,
        "pin_passes": ok,
    }, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
