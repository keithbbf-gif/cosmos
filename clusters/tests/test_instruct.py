"""Instruction and MCP paths. Bodies are not read. Python 3.11."""

from __future__ import annotations

import hashlib

import pytest

from clusters.instruct import add_instruction, list_instructions, set_import
from clusters.mesh import create_project
from clusters.refuse import Refuse
from clusters.store import Store


def _store(tmp_path):
    store = Store(tmp_path / "c")
    project = create_project(store, name="web", root=str(tmp_path / "web"))
    return store, project["id"]


def test_agents_path(tmp_path):
    store, project_id = _store(tmp_path)
    path = str(tmp_path / "AGENTS.md")
    later = str(tmp_path / "skills")
    # Bodies are not read. The named file is not opened, so it need not exist.
    row = add_instruction(store, project_id=project_id, kind="agents", path=path)
    add_instruction(store, project_id=project_id, kind="skills", path=later)
    digest = hashlib.sha256(path.encode()).hexdigest()[:12]
    assert row["id"] == f"ins-{project_id}-{digest}"
    assert row["project_id"] == project_id
    assert row["kind"] == "agents"
    assert row["path"] == path
    assert row["imported"] == ""
    assert "body" not in row
    listed = list_instructions(store, project_id)
    assert [item["path"] for item in listed] == sorted([path, later])
    assert listed[0]["kind"] == "agents"


def test_bad_kind(tmp_path):
    store, project_id = _store(tmp_path)
    with pytest.raises(Refuse) as refused:
        add_instruction(store, project_id=project_id, kind="guide", path="AGENTS.md")
    assert refused.value.code == "KIND"


def test_live_path(tmp_path):
    store, project_id = _store(tmp_path)
    with pytest.raises(Refuse) as refused:
        add_instruction(
            store,
            project_id=project_id,
            kind="mcp",
            path=r"V:\A\Ai\COSMOS\live\mcp.json",
        )
    assert refused.value.code == "LIVE_TREE"


def test_skipped_import_written_false(tmp_path):
    store, project_id = _store(tmp_path)
    row = set_import(store, project_id=project_id, result="skipped")
    assert row["id"] == f"import-{project_id}"
    assert row["project_id"] == project_id
    assert row["result"] == "skipped"
    assert row["written"] is False
