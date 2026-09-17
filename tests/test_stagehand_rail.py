#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stagehand DOM adapter UNDER playwright-dom.

Pins that fail if the adapter:
  * mkdir's on GET (action-cache snapshot)
  * claims kernel_attached=true by default
  * lets browser_run_code_unsafe through
  * replaces playwright-dom or becomes a scheduler / second Core
"""
from __future__ import annotations

import ast
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_mcp_client import DEFAULT_DENY  # noqa: E402
from cosmos_stagehand_rail import (  # noqa: E402
    DENY,
    LINK_ID,
    UNDERLAY,
    UNSAFE_TOOL,
    _selftest,
    cache_dir,
    default_spec,
    merge_spec,
    snapshot_cache,
    StagehandRail,
    StagehandRailError,
)


def test_stagehand_rail_selftest():
    assert _selftest() == 0


def test_get_never_mkdirs():
    """Behavioral pin: snapshot_cache (GET) must not create the cache role."""
    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths

    td = Path(tempfile.mkdtemp(prefix="stagehand_get_mkdir_"))
    root = install(td / "live", tree_id="spike-stagehand-get")
    paths = CosmosPaths(root)
    role = cache_dir(paths)
    assert not role.exists(), "install must not pre-create stagehand cache role"
    rec = snapshot_cache(paths)
    assert rec["kind"] == "UNMEASURED"
    assert rec["n_obs"] == 0
    assert rec["kernel_attached"] is False
    assert not role.exists(), "GET snapshot_cache mkdir'd state/stagehand_rail/"


def test_get_fold_source_has_no_mkdir():
    """AST pin: snapshot_cache body must not call mkdir."""
    src = (ROOT / "cosmos" / "cosmos_stagehand_rail.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    fn = None
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "snapshot_cache":
            fn = node
            break
    assert fn is not None, "snapshot_cache missing"
    calls = []
    for n in ast.walk(fn):
        if isinstance(n, ast.Call):
            name = ""
            if isinstance(n.func, ast.Attribute):
                name = n.func.attr
            elif isinstance(n.func, ast.Name):
                name = n.func.id
            calls.append(name)
    assert "mkdir" not in calls, f"GET fold called mkdir: {calls}"
    doc = ast.get_docstring(fn) or ""
    assert "Never mkdir" in doc


def test_default_kernel_attached_is_false():
    spec = default_spec()
    assert spec["kernel_attached"] is False
    claimed = merge_spec({
        "schema": spec["schema"],
        "rail_type": "DOM",
        "kernel_attached": True,
    })
    assert claimed["kernel_attached"] is False
    assert StagehandRail.kind == "DOM"
    rail = StagehandRail(spec, client_factory=lambda: (_ for _ in ()).throw(
        StagehandRailError("UNREACHABLE", "no transport")))
    try:
        rail.probe()
    except Exception:  # noqa: BLE001
        pass
    ident = rail.last_identity()
    if ident is not None:
        assert ident.get("kernel_attached") is not True


def test_browser_run_code_unsafe_stays_denied():
    assert UNSAFE_TOOL == "browser_run_code_unsafe"
    assert UNSAFE_TOOL in DEFAULT_DENY
    assert UNSAFE_TOOL in DENY
    spec = default_spec()
    assert spec["unsafe_denied"] is True
    rail = StagehandRail(spec, client_factory=_denied_factory)
    out = rail.dispatch({"verb": UNSAFE_TOOL, "instruction": "rce"})
    assert out["ok"] is False
    assert out["kind"] == "DENIED"


def _denied_factory():
    from cosmos_mcp_client import FakeTransport, McpClient

    def handler(msg):
        method = msg.get("method")
        rid = msg.get("id")
        if method == "initialize":
            return {"jsonrpc": "2.0", "id": rid, "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "Stagehand", "version": "4.0.2"},
            }}
        if method == "notifications/initialized":
            return None
        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": rid, "result": {
                "tools": [{"name": UNSAFE_TOOL}],
            }}
        return {"jsonrpc": "2.0", "id": rid, "result": {
            "content": [{"type": "text", "text": "should-not-run"}],
        }}

    return McpClient(
        transport=FakeTransport(handler),
        timeout_s=2,
        denylist=DENY,
    )


def test_playwright_stays_not_second_core():
    from cosmos_playwright_rail import LINK_ID as PW

    assert PW == "playwright-dom"
    assert LINK_ID == "stagehand-dom"
    assert LINK_ID != PW
    assert UNDERLAY == PW
    spec = default_spec()
    assert spec["replaces_playwright"] is False
    assert spec["is_scheduler"] is False
    kernel_src = (ROOT / "cosmos" / "cosmos_kernel.py").read_text(encoding="utf-8")
    assert "cosmos_stagehand_rail" not in kernel_src
    assert "stagehand-dom" not in kernel_src
    sched = (ROOT / "cosmos" / "cosmos_stagehand_rail.py").read_text(encoding="utf-8")
    assert "import cosmos_sch" + "ed" not in sched
    assert "from cosmos_sch" + "ed" not in sched
    assert "claim_next" not in sched


def test_merge_refuses_playwright_takeover_and_scheduler_dst():
    try:
        merge_spec({
            "schema": default_spec()["schema"],
            "rail_type": "DOM",
            "link_id": "playwright-dom",
        })
        raised = None
    except StagehandRailError as e:
        raised = e.kind
    assert raised == "BAD_SPEC"
    try:
        merge_spec({
            "schema": default_spec()["schema"],
            "rail_type": "DOM",
            "dst": "sched",
        })
        raised = None
    except StagehandRailError as e:
        raised = e.kind
    assert raised == "BAD_SPEC"


if __name__ == "__main__":
    sys.exit(_selftest())
