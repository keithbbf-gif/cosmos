"""Per-tool Allow, Ask, or Deny. The category matrix does not store this.

The tool is not called. A missing name stays ask and is not an allow.

Python 3.11.
"""

from __future__ import annotations

import pytest

from clusters.mesh import create_project
from clusters.refuse import Refuse
from clusters.store import Store
from clusters.toolperm import LEVELS, set_tool, tool_level


def _store(tmp_path):
    store = Store(tmp_path / "c")
    project = create_project(store, name="web", root=str(tmp_path / "web"))
    return store, project["id"]


def test_deny_is_stored_and_the_tool_is_not_called(tmp_path):
    # The tool is not called. Deny is only a stored choice.
    store, project_id = _store(tmp_path)
    saved = set_tool(
        store,
        project_id=project_id,
        server_id="box",
        tool="fs_read",
        level="deny",
    )
    assert saved["id"] == f"tool-{project_id}-box-fs_read"
    assert saved["project_id"] == project_id
    assert saved["server_id"] == "box"
    assert saved["tool"] == "fs_read"
    assert saved["level"] == "deny"
    again = tool_level(
        store, project_id=project_id, server_id="box", tool="fs_read"
    )
    assert again["level"] == "deny"
    assert again["stored"] is True
    event = store.fold("tool_perm")[-1]
    assert event["kind"] == "tool_perm"
    assert event["body"]["level"] == "deny"
    assert event["body"]["id"] == saved["id"]
    assert {row["kind"] for row in store.fold()} == {"project", "tool_perm"}


def test_bad_level_refuses(tmp_path):
    store, project_id = _store(tmp_path)
    assert "yolo" not in LEVELS
    with pytest.raises(Refuse) as refused:
        set_tool(
            store,
            project_id=project_id,
            server_id="box",
            tool="fs_read",
            level="yolo",
        )
    assert refused.value.code == "TOOL"
    assert refused.value.detail == "level"
    assert store.fold("tool_perm") == []


def test_missing_tool_stays_ask_with_stored_false(tmp_path):
    # The tool is not called. A missing name is not an allow.
    store, project_id = _store(tmp_path)
    missing = tool_level(
        store, project_id=project_id, server_id="box", tool="fs_read"
    )
    assert missing["level"] == "ask"
    assert missing["stored"] is False
    assert missing["level"] != "allow"
    assert store.fold("tool_perm") == []
    set_tool(
        store,
        project_id=project_id,
        server_id="box",
        tool="fs_write",
        level="deny",
    )
    other = tool_level(
        store, project_id=project_id, server_id="box", tool="fs_read"
    )
    assert other["level"] == "ask"
    assert other["stored"] is False


def test_bad_server_and_name_refuse(tmp_path):
    store, project_id = _store(tmp_path)
    with pytest.raises(Refuse) as server:
        set_tool(
            store,
            project_id=project_id,
            server_id="box\nextra",
            tool="fs_read",
            level="deny",
        )
    assert server.value.code == "TOOL"
    assert server.value.detail == "server"
    with pytest.raises(Refuse) as name:
        set_tool(
            store,
            project_id=project_id,
            server_id="box",
            tool="n" * 81,
            level="ask",
        )
    assert name.value.code == "TOOL"
    assert name.value.detail == "name"
    assert store.fold("tool_perm") == []
    kept = set_tool(
        store,
        project_id=project_id,
        server_id="s" * 80,
        tool="t",
        level="ask",
    )
    assert kept["server_id"] == "s" * 80
    assert kept["level"] == "ask"


def test_missing_project_refuses(tmp_path):
    store = Store(tmp_path / "c")
    with pytest.raises(Refuse) as refused:
        set_tool(
            store,
            project_id="prj-missing",
            server_id="box",
            tool="fs_read",
            level="deny",
        )
    assert refused.value.code == "PROJECT"
    assert refused.value.detail == "prj-missing"
    with pytest.raises(Refuse) as read:
        tool_level(
            store, project_id="prj-missing", server_id="box", tool="fs_read"
        )
    assert read.value.code == "PROJECT"
    assert read.value.detail == ""
    assert store.fold("tool_perm") == []
