#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: P04 runtime_bind requires live emit; default off keeps DONE on Output.

    py -3.14 cosmos/_bite_p04_live_emit.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent / "cosmos"
sys.path.insert(0, str(HERE))

from cosmos_live_emit import LiveEmitError, quote_tree_id, require_live_emit  # noqa: E402
from cosmos_paths import CosmosPaths, write_sentinel  # noqa: E402
from cosmos_work_order import drop_order, file_done, pickup_order  # noqa: E402
from cosmos_workspace import output_path  # noqa: E402

OUT = HERE / "_bite_p04_live_emit.json"

GROK_RAW = {
    "Agent": "xAI | Grok | grok-4.6",
    "Context source": ["docs/WORK_ORDER_SPEC.md"],
    "Task": "bite emit",
    "Target & scope": "workspace out/ only",
    "Timestamp": "2026-09-02T12:00:00-05:00",
    "Output": "proposals | result.md",
}


def _install():
    td = Path(tempfile.mkdtemp(prefix="cosmos_bite_p04_"))
    repo = td
    live = td / "live"
    write_sentinel(live, tree_id="p04-bite")
    for name in ("cosmos", "docs"):
        (repo / name).mkdir(parents=True, exist_ok=True)
    (repo / "docs" / "WORK_ORDER_SPEC.md").write_text("# spec\n", encoding="utf-8")
    (live / "state").mkdir(parents=True, exist_ok=True)
    (live / "work").mkdir(parents=True, exist_ok=True)
    (live / "config").mkdir(parents=True, exist_ok=True)
    return repo, live, CosmosPaths(live)


def main() -> int:
    good_status = {"ready": True, "tree_id": "KMesh-COSMOS-live"}
    assert quote_tree_id(good_status) == "KMesh-COSMOS-live"
    assert quote_tree_id({"tree_id": "other"}) == "other"

    def ok_http(method, url, body, headers):  # noqa: ARG001
        return 200, good_status

    emit = require_live_emit(http=ok_http, token="t")
    assert emit.get("tree_id") == "KMesh-COSMOS-live"

    missing = None
    try:
        require_live_emit(http=lambda *a: (200, {"ready": True, "tree_id": "wrong"}))
    except LiveEmitError as e:
        missing = e.kind
    assert missing == "MISSING_EMIT"

    repo, live, paths = _install()
    drop = drop_order(paths, GROK_RAW, order_id="wo-p04-bite-off")
    rec = pickup_order(paths, drop, repo_tree=repo)
    out = output_path(Path(rec["_workspace"]), "proposals", "result.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("ok\n", encoding="utf-8")
    rec["_output_path"] = str(out)
    done_off = file_done(
        paths, rec, run_rec={"rc": 0}, check_rails=False, live_probe=lambda _p: emit)
    assert done_off.get("state") == "DONE"

    drop2 = drop_order(paths, {**GROK_RAW, "runtime_bind": True}, order_id="wo-p04-bite-on")
    rec2 = pickup_order(paths, drop2, repo_tree=repo)
    out2 = output_path(Path(rec2["_workspace"]), "proposals", "result.md")
    out2.parent.mkdir(parents=True, exist_ok=True)
    out2.write_text("ok\n", encoding="utf-8")
    rec2["_output_path"] = str(out2)

    def refuse(_paths):
        raise LiveEmitError("MISSING_EMIT", "no core")

    failed = file_done(
        paths, rec2, run_rec={"rc": 0}, check_rails=False, live_probe=refuse)
    assert failed.get("state") == "FAILED"
    assert failed.get("fail_kind") == "MISSING_EMIT"

    drop3 = drop_order(
        paths, {**GROK_RAW, "runtime_bind": True}, order_id="wo-p04-bite-pass")
    rec3 = pickup_order(paths, drop3, repo_tree=repo)
    out3 = output_path(Path(rec3["_workspace"]), "proposals", "result.md")
    out3.parent.mkdir(parents=True, exist_ok=True)
    out3.write_text("ok\n", encoding="utf-8")
    rec3["_output_path"] = str(out3)
    passed = file_done(
        paths, rec3, run_rec={"rc": 0}, check_rails=False,
        live_probe=lambda _p: require_live_emit(http=ok_http))
    assert passed.get("state") == "DONE"
    assert passed.get("live_emit", {}).get("tree_id") == "KMesh-COSMOS-live"

    rec = {
        "quote_helper": quote_tree_id(good_status) == "KMesh-COSMOS-live",
        "missing_emit_kind": missing == "MISSING_EMIT",
        "default_bind_off_done": done_off.get("state") == "DONE",
        "bind_on_missing_failed": failed.get("fail_kind") == "MISSING_EMIT",
        "bind_on_emit_done": passed.get("state") == "DONE",
    }
    rec["all_bite"] = all(rec.values())
    OUT.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
