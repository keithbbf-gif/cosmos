#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: COSMOS Claude Code CLI rail (Anthropic node).

Isolated from the live runtime root and the live `claude` binary. Fake run.
Proves: rail attaches with boot_compose; argv carries --model +
--permission-mode dontAsk + --add-dir=workspace; a 2-part Agent spec is
refused; this module has no bts_ import.
Does not invoke the live Claude Code CLI and does not write the authority
ledger.
"""
from __future__ import annotations

import ast
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_claude_rail import (  # noqa: E402
    DEFAULT_MODEL,
    LINK_ID,
    ClaudeRail,
    ClaudeRailError,
    _selftest,
    attach_to_kernel,
    parse_agent_spec,
)
from cosmos_kernel import Kernel, install  # noqa: E402


def _flag(argv, name):
    if name in argv:
        return argv[argv.index(name) + 1]
    prefix = name + "="
    for a in argv:
        if a.startswith(prefix):
            return a[len(prefix):]
    return None


def _fake_which(name):
    if name == "claude":
        return r"C:\npm\claude.CMD"
    return None


def _fake_clone(src, dest):
    Path(dest).mkdir(parents=True, exist_ok=True)
    return {"ok": True, "how": "fake", "src": str(src), "dest": str(dest)}


def _fake_run(argv, cwd=None, timeout_s=60, env=None, stdin=None):
    argv = list(argv)
    if "--version" in argv:
        return {"rc": 0, "out": "2.1.220 (Claude Code)\n", "err": "",
                "timed_out": False, "elapsed_s": 0.1}
    if "-p" in argv:
        body = {
            "type": "result",
            "subtype": "success",
            "is_error": False,
            "result": "ALIVE via claude-cli",
            "session_id": "sess-test-1",
            "model": DEFAULT_MODEL,
        }
        return {"rc": 1, "out": json.dumps(body) + "\n", "err": "",
                "timed_out": False, "elapsed_s": 0.2}
    return {"rc": 404, "out": "", "err": "unexpected",
            "timed_out": False, "elapsed_s": 0.0}


def _installed():
    td = Path(tempfile.mkdtemp(prefix="cosmos_claude_rail_t_"))
    root = install(td / "live", tree_id="test-claude-rail")
    keyp = root / "config" / "anthropic_api_key.txt"
    keyp.write_text("sk-ant-api03-" + ("a" * 32) + "31ab", encoding="utf-8")
    ws = td / "attempt"
    ws.mkdir()
    return root, keyp, ws


def test_claude_rail_attaches():
    root, keyp, _ws = _installed()
    k = Kernel(root, worker="claude-rail-test")
    att = attach_to_kernel(
        k, k.adapters, run=_fake_run, which=_fake_which, clone=_fake_clone,
        boot_compose=True)
    assert att["link_id"] == LINK_ID
    assert LINK_ID in k.registry.state()
    assert LINK_ID in k.adapters
    refused = False
    try:
        attach_to_kernel(k, {}, run=_fake_run, which=_fake_which,
                         clone=_fake_clone)
    except ClaudeRailError as e:
        refused = e.kind == "REFUSED"
    assert refused, "attach without boot_compose must refuse authority"


def test_claude_argv_model_dontask_add_dir():
    root, keyp, ws = _installed()
    rail = ClaudeRail(
        keyp, None, run=_fake_run, which=_fake_which, clone=_fake_clone,
        live_root=root)
    out = rail.dispatch({
        "prompt": "hello",
        "workspace": str(ws),
        "skip_clone": True,
        "model": DEFAULT_MODEL,
        "timeout_s": 5,
    })
    argv = out.get("argv") or (rail._calls[-1]["argv"] if rail._calls else [])
    assert _flag(argv, "--model") == DEFAULT_MODEL, argv
    assert _flag(argv, "--permission-mode") == "dontAsk", argv
    assert _flag(argv, "--add-dir") == str(ws), argv
    assert "-p" in argv
    assert out.get("done") is True


def test_two_part_agent_spec_refused():
    raised = False
    try:
        parse_agent_spec("Anthropic | Opus")
    except ClaudeRailError as e:
        raised = e.kind == "BAD_INPUT"
    assert raised, "2-part Agent spec must be BAD_INPUT"
    root, keyp, ws = _installed()
    rail = ClaudeRail(
        keyp, None, run=_fake_run, which=_fake_which, clone=_fake_clone,
        live_root=root)
    rec = rail.dispatch({
        "prompt": "x",
        "workspace": str(ws),
        "skip_clone": True,
        "Agent": "Anthropic | Sonnet",
    })
    assert rec.get("kind") == "BAD_INPUT"
    assert rec.get("done") is False
    parsed = parse_agent_spec("Anthropic | Opus | claude-opus-5")
    assert parsed["model"] == "claude-opus-5"


def test_no_bts_import():
    src = Path(__file__).resolve().parent.parent / "cosmos" / "cosmos_claude_rail.py"
    tree = ast.parse(src.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                assert not (a.name == "bts_" or a.name.startswith("bts_")), a.name
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            assert not (mod == "bts_" or mod.startswith("bts_")), mod


def test_claude_rail():
    assert _selftest() == 0


if __name__ == "__main__":
    test_no_bts_import()
    test_two_part_agent_spec_refused()
    test_claude_argv_model_dontask_add_dir()
    test_claude_rail_attaches()
    rc = _selftest()
    print("OK  test_claude_rail named asserts + selftest rc=%s" % rc)
    raise SystemExit(rc)
