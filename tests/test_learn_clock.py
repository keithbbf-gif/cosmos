#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Learn-style clock: --once JSONL authority, propose STYLE, never PREFIX."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "cosmos"))

from cosmos_kernel import install  # noqa: E402
from cosmos_learn_clock import (  # noqa: E402
    ACTION_KINDS, CLOCK_ID, REQUIRED_FIELDS, TASK_NAME, XFER_SCHEMA,
    emit_plan, field_gaps, main, poll_once, snapshot, standup,
)
from cosmos_paths import CosmosPaths  # noqa: E402


def test_clock_matrix_row():
    from cosmos_own_clocks import CLOCKS
    hits = [c for c in CLOCKS if c["id"] == CLOCK_ID]
    assert len(hits) == 1
    row = hits[0]
    assert row["task"] == TASK_NAME
    assert row["script"] == "cosmos_learn_clock.py"
    assert row["heartbeat"] == "learn_clock_heartbeat.json"
    assert "15" in row["cadence"]
    assert row["vehicle"] == "schtasks /sc minute /mo 15 --once"


def test_get_never_mkdir_session_ideas(tmp_path):
    root = install(tmp_path / "live", tree_id="learn-get-never-mkdir")
    paths = CosmosPaths(str(root), expected_tree_id="learn-get-never-mkdir")
    ideas = paths.role("state", "session-ideas")
    before = ideas.exists()
    snap = snapshot(paths)
    after = ideas.exists()
    assert snap["kind"] == "UNMEASURED"
    assert not before and not after
    assert not paths.role("work", "propose", "learn-style").exists()


def test_missing_fields_are_unmeasured():
    assert "checker.score" in REQUIRED_FIELDS
    assert "xfer.kind" in REQUIRED_FIELDS
    rec = {"schema": XFER_SCHEMA, "model": "x"}
    gaps = field_gaps(rec)
    assert "chair" in gaps
    assert "checker.score" in gaps
    assert "xfer.kind" in gaps


def test_once_proposes_style_not_prefix(tmp_path):
    root = install(tmp_path / "live", tree_id="learn-style-propose")
    paths = CosmosPaths(str(root), expected_tree_id="learn-style-propose")
    ideas = paths.role("state", "session-ideas")
    ideas.mkdir()
    prefix = paths.role("state", "PREFIX.md")
    prefix.write_text("CACHE PREFIX\n", encoding="utf-8")
    row = {
        "schema": XFER_SCHEMA,
        "model": "grok-4.6",
        "chair": "CCr",
        "pack": "farm",
        "cached_tokens": 1024,
        "http": 429,
        "checker": {"score": 0.4},
        "xfer": {"kind": "FAIL"},
        "prompt_path": "state/session-ideas/WRAP.md",
    }
    (ideas / "xfer.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
    (ideas / "WRAP.md").write_text("wrap\n", encoding="utf-8")
    before = prefix.read_bytes()
    rec = poll_once(str(root))
    assert rec["ok"] is True
    assert rec["proposed"] == 1
    style = paths.role("work", "propose", "learn-style", "STYLE.md")
    assert style.is_file()
    assert "- [xfer]" in style.read_text(encoding="utf-8")
    assert prefix.read_bytes() == before
    assert rec["reviews"]["sets"]["WRAP"]


def test_cli_once_required(tmp_path):
    root = install(tmp_path / "live", tree_id="learn-cli-once")
    assert main(["--root", str(root)]) == 2
    assert main(["--root", str(root), "--once"]) == 0


def test_standup_already(tmp_path):
    root = install(tmp_path / "live", tree_id="learn-standup")
    rec = standup(
        str(root),
        query=lambda _n: {"ok": True, "name": TASK_NAME},
        create=lambda *a, **k: {"ok": False, "out": "should-not-create"},
    )
    assert rec["started"] == "already"
    assert rec["keith_cmd"] is None


def test_plan_task_shape(tmp_path):
    root = install(tmp_path / "live", tree_id="learn-plan")
    plan = emit_plan(str(root))
    assert plan["clock_id"] == 28
    assert plan["task_name"] == TASK_NAME
    assert "minute" in plan["cadence"]
    assert "15" in plan["cadence"]
    assert "--once" in plan["tr"]


def test_action_kinds():
    assert ACTION_KINDS == frozenset({"FAIL", "DROP", "HTTP_429"})


def test_selftest_subprocess():
    script = REPO / "cosmos" / "cosmos_learn_clock.py"
    p = subprocess.run(
        [sys.executable, str(script), "--selftest"],
        capture_output=True, text=True, cwd=str(REPO), timeout=60,
    )
    assert p.returncode == 0, p.stdout + p.stderr
    assert "OpenRouter" not in p.stdout or "does not import OpenRouter" in p.stdout


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
