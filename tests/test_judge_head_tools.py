#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pins for the 2026-09-24 leftovers: partner, judge run, head gate, code tools."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(_here.parent / "cosmos"))

from cosmos_code_tools import CodeToolError, CodeTools, VERBS, contract_rows  # noqa: E402
from cosmos_head_gate import head_gate, measure_ahead  # noqa: E402
from cosmos_judge_run import (  # noqa: E402
    ATTEMPT_SCHEMA, attempts_path, autopsy_fail, judge_idle_gate, judge_run,
    read_attempts, wo_partner,
)
from cosmos_paths import CosmosPaths, write_sentinel  # noqa: E402
from cosmos_warn import WarnRefuse  # noqa: E402


def test_wo_partner_minute_and_unmeasured():
    order = {
        "order_id": "a",
        "Timestamp": "2026-09-24T16:30:00-05:00",
        "Task": "ONE bite: wo_partner",
        "state": "FAILED",
    }
    partner = {
        "order_id": "b",
        "Timestamp": "2026-09-24T16:30:44-05:00",
        "Task": "other",
        "state": "DONE",
    }
    hit = wo_partner(order, [order, partner])
    assert hit["partner_id"] == "b"
    assert hit["partner_state"] == "DONE"
    miss = wo_partner(order, [])
    assert miss["partner_state"] == "UNMEASURED"
    assert miss["partner_id"] is None


def test_judge_run_reuses_prefix():
    first = judge_run(model="luna", prefix="FAT", attempt=1)
    second = judge_run(model="someone-else", prefix="NEW", attempt=2, prior=first)
    assert second["minted"] is False
    assert second["model"] == "luna"
    assert second["prefix"] == "FAT"
    assert judge_idle_gate(4, False) == "leave"
    assert judge_idle_gate(22, False) == "sit"
    assert judge_idle_gate(0, True, n_pairs=1) == "sit"


def test_fail_autopsy_appends_jsonl_without_get_mkdir():
    td = Path(tempfile.mkdtemp(prefix="cosmos_judge_pin_"))
    live = td / "live"
    write_sentinel(live, tree_id="judge-pin")
    paths = CosmosPaths(live)
    snap = read_attempts(paths)
    assert snap["kind"] == "UNMEASURED"
    assert snap["n"] == 0
    assert not attempts_path(paths).exists()
    extra = autopsy_fail(
        paths,
        {"order_id": "wo-a", "Timestamp": "2026-09-24T16:40:00-05:00",
         "Task": "a", "state": "FAILED"},
        "REFUSED", "silent",
        siblings=[{
            "order_id": "wo-b", "Timestamp": "2026-09-24T16:40:09-05:00",
            "Task": "b", "state": "DONE",
        }],
    )
    assert extra["xfer"] == "GAC_RESEAT"
    assert extra["follow_up_oid"] is None
    rows = read_attempts(paths)["rows"]
    assert len(rows) == 1
    assert rows[0]["schema"] == ATTEMPT_SCHEMA
    assert rows[0]["partner_id"] == "wo-b"


def test_head_gate_refuses_ahead_and_unmeasured():
    assert head_gate(".", run=lambda _c, _r: "0")["synced"] is True
    try:
        head_gate(".", run=lambda _c, _r: "3")
    except WarnRefuse as e:
        assert e.kind == "NOT_SYNCED"
    else:
        raise AssertionError("ahead must refuse")
    try:
        head_gate(".", run=lambda _c, _r: (_ for _ in ()).throw(OSError("no git")))
    except WarnRefuse as e:
        assert e.kind == "HEAD_UNMEASURED"
    else:
        raise AssertionError("unmeasured must refuse")
    assert measure_ahead(".", run=lambda _c, _r: (_ for _ in ()).throw(OSError("x"))) == -1


def test_code_tools_stay_inside_the_allowlist():
    td = Path(tempfile.mkdtemp(prefix="cosmos_tools_pin_"))
    tools = CodeTools([td])
    tools.Write("note.md", "one\n")
    assert "one" in tools.Read("note.md")["text"]
    tools.Edit("note.md", "one", "two")
    assert tools.Grep("two", td)["n"] == 1
    try:
        tools.Write(td / "api_token.txt", "secret")
    except CodeToolError as e:
        assert e.kind == "REFUSED"
    else:
        raise AssertionError("token name must refuse")
    try:
        tools.Bash(["grok.exe", "--single"])
    except CodeToolError as e:
        assert e.kind == "REFUSED"
    else:
        raise AssertionError("grok.exe must refuse")
    assert [row["name"] for row in contract_rows()] == list(VERBS)
    blob = json.dumps(tools.Glob("*.md", td))
    assert "note.md" in blob
