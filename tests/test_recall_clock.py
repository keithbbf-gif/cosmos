#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Recall clock + GET /api/v1/recall never-mkdir pins."""
from __future__ import annotations

import json
import sys
import tempfile
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "cosmos"))

from cosmos_kernel import install  # noqa: E402
from cosmos_paths import CosmosPaths  # noqa: E402
from cosmos_recall import snapshot  # noqa: E402
from cosmos_recall_clock import CLOCK_ID, TASK_NAME, emit_plan  # noqa: E402
from cosmos_service import Service  # noqa: E402


def test_clock_matrix_row():
    from cosmos_own_clocks import CLOCKS
    hits = [c for c in CLOCKS if c["id"] == CLOCK_ID]
    assert len(hits) == 1
    row = hits[0]
    assert row["task"] == TASK_NAME
    assert row["script"] == "cosmos_recall_clock.py"
    assert row["heartbeat"] == "recall_clock_heartbeat.json"
    assert "15" in row["cadence"]


def test_get_never_mkdir():
    td = Path(tempfile.mkdtemp(prefix="recall_get_"))
    root = install(td / "live", tree_id="recall-get-never-mkdir")
    paths = CosmosPaths(str(root), expected_tree_id="recall-get-never-mkdir")
    before = paths.role("state", "recall").exists()
    snap = snapshot(paths)
    after = paths.role("state", "recall").exists()
    assert snap["kind"] == "UNMEASURED"
    assert not before and not after


def test_http_get_recall():
    td = Path(tempfile.mkdtemp(prefix="recall_http_"))
    root = install(td / "live", tree_id="recall-http")
    k = __import__("cosmos_kernel").Kernel(root, worker="recall-test")
    svc = Service(k, port=0)
    svc.serve_background()
    try:
        req = urllib.request.Request(
            f"http://127.0.0.1:{svc.port}/api/v1/recall")
        req.add_header("Authorization", "Bearer " + svc.token)
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        assert resp.status == 200
        assert body.get("kind") == "UNMEASURED"
        assert body.get("tree_id") == "recall-http"
    finally:
        svc.shutdown()


def test_plan_task_shape():
    td = Path(tempfile.mkdtemp(prefix="recall_plan_"))
    root = install(td / "live", tree_id="recall-plan")
    plan = emit_plan(str(root))
    assert plan["clock_id"] == 27
    assert plan["task_name"] == TASK_NAME
    assert "minute" in plan["cadence"]
    assert "15" in plan["cadence"]
    assert "--once" in plan["tr"]


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
