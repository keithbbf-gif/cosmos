#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: P03 GET /api/v1/porosity — JSONL authority, GET never mkdir.

1. Delete SQLite projection only → GET 200 folds from obs.jsonl.
2. Absent store → GET does not mkdir; kind=UNMEASURED n_obs=0.
3. No invented pair when empty.

    py -3.14 cosmos/_bite_p03_get_never_mkdir.py
"""
from __future__ import annotations

import json
import sys
import tempfile
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent / "cosmos"
sys.path.insert(0, str(HERE))

from cosmos_kernel import Kernel, install  # noqa: E402
from cosmos_porosity import (  # noqa: E402
    SCHEMA,
    db_path,
    empty_snapshot,
    obs_path,
    record_pair,
    snapshot,
    store_dir,
)
from cosmos_service import Service  # noqa: E402

OUT = HERE / "_bite_p03_get_never_mkdir.json"


def _get(svc: Service, path: str = "/api/v1/porosity") -> tuple[int, dict]:
    req = urllib.request.Request(f"http://127.0.0.1:{svc.port}{path}")
    req.add_header("Authorization", "Bearer " + svc.token)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_bite_p03_"))
    root = install(td / "live", tree_id="p03-get-never-mkdir")
    k = Kernel(root, worker="p03")
    paths = k.paths

    # --- Bite 2: absent store, direct snapshot + HTTP GET ---
    snap_absent = snapshot(paths)
    store_before = store_dir(paths).exists()
    svc = Service(k, port=0)
    svc.serve_background()
    try:
        st_empty, body_empty = _get(svc)
    finally:
        svc.shutdown()
    store_after_empty = store_dir(paths).exists()

    absent_direct = (
        snap_absent["kind"] == "UNMEASURED"
        and snap_absent["n_obs"] == 0
        and snap_absent["n_pairs"] == 0
        and snap_absent["pairs"] == []
        and snap_absent["schema"] == SCHEMA
        and not store_before
        and not store_after_empty
    )
    absent_http = (
        st_empty == 200
        and body_empty.get("kind") == "UNMEASURED"
        and body_empty.get("n_obs") == 0
        and body_empty.get("n_pairs") == 0
        and body_empty.get("pairs") == []
        and not store_after_empty
    )

    # --- Bite 1: JSONL authority survives SQLite deletion ---
    record_pair(
        paths,
        "google/gemma-4-26b-a4b-it:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        axis="coding",
        disagree=True,
        error_mag=7,
        profile="forge",
        action="bite",
    )
    had_jsonl = obs_path(paths).is_file()
    had_sqlite = db_path(paths).is_file()
    db_path(paths).unlink()
    sqlite_gone = not db_path(paths).is_file()

    snap_jsonl = snapshot(paths)
    svc2 = Service(k, port=0)
    svc2.serve_background()
    try:
        st_jsonl, body_jsonl = _get(svc2)
    finally:
        svc2.shutdown()

    jsonl_direct = (
        had_jsonl
        and had_sqlite
        and sqlite_gone
        and snap_jsonl["n_obs"] == 1
        and snap_jsonl["n_pairs"] == 1
        and snap_jsonl["kind"] == "MEASURED"
        and not db_path(paths).is_file()
    )
    jsonl_http = (
        st_jsonl == 200
        and body_jsonl.get("n_obs") == 1
        and body_jsonl.get("n_pairs") == 1
        and body_jsonl.get("kind") == "MEASURED"
        and not db_path(paths).is_file()
    )

    empty_ref = empty_snapshot()
    no_invented_pair = (
        empty_ref["kind"] == "UNMEASURED"
        and empty_ref["n_obs"] == 0
        and empty_ref["pairs"] == []
    )

    rec = {
        "schema": SCHEMA,
        "absent_store_direct": absent_direct,
        "absent_store_http": absent_http,
        "jsonl_without_sqlite_direct": jsonl_direct,
        "jsonl_without_sqlite_http": jsonl_http,
        "empty_snapshot_no_invented_pair": no_invented_pair,
    }
    rec["all_bite"] = all(
        rec[k] is True
        for k in rec
        if k not in ("schema", "all_bite")
    )
    OUT.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
