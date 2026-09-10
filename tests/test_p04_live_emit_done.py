#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P04: runtime_bind on work-order DONE requires live emit (not rc=0 alone)."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root))
sys.path.insert(0, str(_root / "cosmos"))

from cosmos_live_emit import LiveEmitError, quote_tree_id  # noqa: E402
from cosmos_paths import CosmosPaths, write_sentinel  # noqa: E402
from cosmos_work_order import drop_order, file_done, pickup_order, work_order_dirs  # noqa: E402
from cosmos_workspace import output_path  # noqa: E402

GROK_RAW = {
    "Agent": "xAI | Grok | grok-4.6",
    "Context source": ["docs/WORK_ORDER_SPEC.md"],
    "Task": "p04 test",
    "Target & scope": "workspace out/ only",
    "Timestamp": "2026-09-02T12:00:00-05:00",
    "Output": "proposals | result.md",
}


def _install():
    td = Path(tempfile.mkdtemp(prefix="p04_done_"))
    repo = td
    live = td / "live"
    write_sentinel(live, tree_id="p04-test")
    (repo / "docs").mkdir(parents=True)
    (repo / "docs" / "WORK_ORDER_SPEC.md").write_text("# spec\n", encoding="utf-8")
    (live / "state").mkdir(parents=True, exist_ok=True)
    (live / "work").mkdir(parents=True, exist_ok=True)
    return repo, live, CosmosPaths(live)


def _pick_with_output(paths, repo, *, order_id: str, runtime_bind=None):
    raw = dict(GROK_RAW)
    if runtime_bind is True:
        raw["runtime_bind"] = True
    drop = drop_order(paths, raw, order_id=order_id)
    rec = pickup_order(paths, drop, repo_tree=repo)
    out = output_path(Path(rec["_workspace"]), "proposals", "result.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("product\n", encoding="utf-8")
    rec["_output_path"] = str(out)
    return rec


def test_quote_tree_id_helper():
    assert quote_tree_id({"ready": True, "tree_id": "KMesh-COSMOS-live"}) == (
        "KMesh-COSMOS-live")
    assert quote_tree_id({}) is None


def test_default_runtime_bind_off_done_without_emit():
    repo, _live, paths = _install()
    rec = _pick_with_output(paths, repo, order_id="wo-p04-off")

    def refuse(_paths):
        raise LiveEmitError("MISSING_EMIT", "would fail if consulted")

    done = file_done(
        paths, rec, run_rec={"rc": 0}, check_rails=False, live_probe=refuse)
    assert done["state"] == "DONE"
    dirs = work_order_dirs(paths)
    assert (dirs["assigned"] / "wo-p04-off.json").is_file()


def test_runtime_bind_missing_emit_failed():
    repo, _live, paths = _install()
    rec = _pick_with_output(
        paths, repo, order_id="wo-p04-miss", runtime_bind=True)

    def refuse(_paths):
        raise LiveEmitError("MISSING_EMIT", "core down")

    failed = file_done(
        paths, rec, run_rec={"rc": 0}, check_rails=False, live_probe=refuse)
    assert failed["state"] == "FAILED"
    assert failed["fail_kind"] == "MISSING_EMIT"
    assert failed["output_exists"] is True
    dirs = work_order_dirs(paths)
    assert (dirs["failed"] / "wo-p04-miss.json").is_file()


def test_runtime_bind_emit_ok_done():
    repo, _live, paths = _install()
    rec = _pick_with_output(
        paths, repo, order_id="wo-p04-ok", runtime_bind=True)
    good = {"ready": True, "tree_id": "KMesh-COSMOS-live"}

    def ok_http(method, url, body, headers):  # noqa: ARG001
        return 200, good

    from cosmos_live_emit import require_live_emit

    done = file_done(
        paths, rec, run_rec={"rc": 0}, check_rails=False,
        live_probe=lambda _p: require_live_emit(http=ok_http, token="x"))
    assert done["state"] == "DONE"
    assert done.get("live_emit", {}).get("tree_id") == "KMesh-COSMOS-live"


def main() -> int:
    tests = [
        test_quote_tree_id_helper,
        test_default_runtime_bind_off_done_without_emit,
        test_runtime_bind_missing_emit_failed,
        test_runtime_bind_emit_ok_done,
    ]
    bad = 0
    for fn in tests:
        try:
            fn()
            print(f"  OK  {fn.__name__}")
        except Exception as e:  # noqa: BLE001
            bad += 1
            print(f"  FAIL {fn.__name__}  {type(e).__name__}: {e}")
    print(f"{len(tests) - bad}/{len(tests)} passed")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
