#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Query channel --once. Channel 1 of three. No LLM spawn. No second daemon.

    py -3.14 cosmos\\cosmos_query_channel.py --root <live> --once
    py -3.14 cosmos\\cosmos_query_channel.py --selftest
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_paths import CosmosPaths, write_sentinel  # noqa: E402

SCHEMA = "cosmos-query-channel/1"


def queries_dir(paths: CosmosPaths) -> Path:
    return paths.role("state", "queries")


def replies_dir(paths: CosmosPaths) -> Path:
    return paths.role("state", "queries", "replies")


def once(root: str) -> dict:
    """List open q-*.json. GET never mkdir. Missing dir = UNMEASURED."""
    paths = CosmosPaths(root)
    qdir = queries_dir(paths)
    if not qdir.is_dir():
        return {
            "ok": True,
            "kind": "UNMEASURED",
            "schema": SCHEMA,
            "n_open": 0,
            "n_answered": 0,
            "open": [],
            "note": "queries/ absent; GET never mkdir",
        }
    open_rows = []
    answered = 0
    rdir = replies_dir(paths)
    for p in sorted(qdir.glob("q-*.json")):
        if p.name.endswith(".tmp"):
            continue
        try:
            raw = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError, UnicodeDecodeError):
            continue
        if not isinstance(raw, dict):
            continue
        stamp = p.stem
        reply = rdir / f"{stamp}-reply.json" if rdir.is_dir() else None
        has_reply = bool(reply and reply.is_file())
        status = str(raw.get("status") or ("answered" if has_reply else "open"))
        if status == "answered" or has_reply:
            answered += 1
            continue
        open_rows.append({"id": stamp, "status": "open", "path": str(p)})
    return {
        "ok": True,
        "kind": "MEASURED",
        "schema": SCHEMA,
        "n_open": len(open_rows),
        "n_answered": answered,
        "open": open_rows,
        "note": "daemon lists; orch writes replies. No spawn.",
    }


def _selftest() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_qch_"))
    live = td / "live"
    write_sentinel(live, tree_id="qch-selftest")
    empty = once(str(live))
    assert empty["kind"] == "UNMEASURED" and empty["n_open"] == 0
    assert not (live / "state" / "queries").exists()
    qdir = live / "state" / "queries"
    qdir.mkdir(parents=True)
    (qdir / "q-20260919T010000.json").write_text(
        json.dumps({"status": "open", "q": "ping"}), encoding="utf-8")
    got = once(str(live))
    assert got["kind"] == "MEASURED" and got["n_open"] == 1
    print("SELFTEST PASS - 2 checks (UNMEASURED no mkdir; MEASURED lists open)")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if not a.once:
        print("missing --once (no in-process loop)", file=sys.stderr)
        return 2
    if not a.root:
        print("missing --root", file=sys.stderr)
        return 2
    rec = once(a.root)
    print(json.dumps(rec, indent=2))
    return 0 if rec.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
