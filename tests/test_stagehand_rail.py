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
    DEFERRED_NOTE,
    LINK_ID,
    UNDERLAY,
    UNSAFE_TOOL,
    _fake_factory,
    _selftest,
    cache_dir,
    default_spec,
    merge_spec,
    parse_locator_intent,
    refused_act,
    snapshot_cache,
    StagehandAdapter,
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
    assert StagehandAdapter is StagehandRail


def test_act_refuses_eval_javascript_cookie():
    spec = default_spec()
    rail = StagehandRail(spec, client_factory=_denied_factory)
    for instr in ("eval(1)", "javascript:alert(1)", "document.cookie"):
        out = rail.act(instr)
        assert out["ok"] is False
        assert out["kind"] == "DENIED"
        assert out.get("text_trust") == "UNTRUSTED"
    assert refused_act("eval document.body")
    assert refused_act("javascript:void(0)")
    assert refused_act("", {"url": "javascript:alert(1)"})
    assert refused_act("document.cookie")
    assert not refused_act("dismiss the modal")


def test_locator_uncomposed_is_fail_open():
    """No playwright-dom bound → keep deferred record. No second DOM stack."""
    spec = default_spec()
    rail = StagehandRail(spec, client_factory=_denied_factory)
    out = rail.act("click #tree")
    assert out["ok"] is True
    assert out.get("note") == DEFERRED_NOTE
    assert out.get("locator_dispatched") is False
    assert out.get("underlay_composed") is False
    assert out.get("text_trust") == "UNTRUSTED"
    assert out.get("dom_is_untrusted") is True
    assert rail._underlay is None
    assert parse_locator_intent("click #tree")["op"] == "click"
    assert parse_locator_intent("goto http://127.0.0.1/")["op"] == "goto"
    assert parse_locator_intent("type hi into #q")["op"] == "type"
    assert parse_locator_intent("fill #e with x")["op"] == "fill"
    assert parse_locator_intent("press Enter")["op"] == "press"
    assert parse_locator_intent("dismiss the modal") is None


def test_locator_composed_dispatches_playwright():
    from cosmos_playwright_rail import PlaywrightRail, default_spec as pw_spec
    from cosmos_playwright_rail import _fake_factory as pw_fake

    spec = default_spec()
    pw = PlaywrightRail(pw_spec(), client_factory=pw_fake("spike-sh-loc"))
    rail = StagehandAdapter(spec, client_factory=_denied_factory, underlay=pw)
    out = rail.act("click #tree")
    assert out["ok"] is True
    assert out.get("locator_dispatched") is True
    assert out.get("underlay_composed") is True
    assert out.get("underlay_node") == "playwright-dom"
    assert out.get("tool") == "browser_click"
    assert out.get("text_trust") == "UNTRUSTED"
    assert out.get("dom_is_untrusted") is True
    assert rail.act("goto http://127.0.0.1:9/").get("tool") == "browser_navigate"
    assert rail.act("type hi into #q").get("tool") == "browser_type"
    assert rail.act("fill #e with x").get("tool") == "browser_fill_form"
    assert rail.act("press Enter").get("tool") == "browser_press_key"
    pw.close()


def test_observe_extract_never_mkdirs():
    """Behavioral pin: observe/extract must not create the cache role."""
    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths

    td = Path(tempfile.mkdtemp(prefix="stagehand_obs_mkdir_"))
    root = install(td / "live", tree_id="spike-stagehand-obs")
    paths = CosmosPaths(root)
    rail = StagehandRail(
        default_spec(), client_factory=_fake_factory(paths.sentinel.tree_id))
    try:
        obs = rail.observe("find the marker")
        ext = rail.extract(
            "extract gate marker",
            schema={"type": "object", "required": ["tree_id"],
                    "properties": {"tree_id": {"type": "string"}}},
        )
    finally:
        rail.close()
    assert obs["ok"] and ext["ok"]
    assert obs.get("text_trust") == "UNTRUSTED"
    assert ext.get("text_trust") == "UNTRUSTED"
    assert not cache_dir(paths).exists()


def test_observe_extract_source_has_no_mkdir():
    """AST pin: observe/extract bodies must not call mkdir (GET fold)."""
    src = (ROOT / "cosmos" / "cosmos_stagehand_rail.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    cls = None
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "StagehandRail":
            cls = node
            break
    assert cls is not None
    found = set()
    for item in cls.body:
        if isinstance(item, ast.FunctionDef) and item.name in ("observe", "extract"):
            found.add(item.name)
            calls = []
            for n in ast.walk(item):
                if isinstance(n, ast.Call):
                    name = ""
                    if isinstance(n.func, ast.Attribute):
                        name = n.func.attr
                    elif isinstance(n.func, ast.Name):
                        name = n.func.id
                    calls.append(name)
            assert "mkdir" not in calls, f"{item.name} called mkdir: {calls}"
    assert found == {"observe", "extract"}


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
