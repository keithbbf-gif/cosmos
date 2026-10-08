"""Cluster composition and packs."""

from __future__ import annotations

import pytest

from clusters.mesh import (
    add_member,
    attach_pack,
    create_cluster,
    create_project,
    set_manager,
    set_project_shortcut,
)
from clusters.refuse import Refuse
from clusters.sessions import open_session
from clusters.store import Store


def test_subcluster_and_pack_and_shortcut(tmp_path):
    store = Store(tmp_path / "m")
    project = create_project(store, name="api", root=str(tmp_path / "api"))
    parent = create_cluster(store, name="backend", project_id=project["id"])
    child = create_cluster(store, name="auth", project_id=project["id"], parent_id=parent["id"])
    linked = add_member(store, parent["id"], member_kind="cluster", member_id=child["id"])
    assert linked["members"] == [{"kind": "cluster", "id": child["id"]}]
    worker = open_session(store, project_id=project["id"], door="codex", task="handler")
    lead = open_session(
        store, project_id=project["id"], door="cosmos-code", role="coordinator", task="manage"
    )
    with_agent = add_member(store, parent["id"], member_kind="agent", member_id=worker["id"])
    assert {"kind": "agent", "id": worker["id"]} in with_agent["members"]
    managed = set_manager(store, parent["id"], lead["id"])
    assert managed["manager_id"] == lead["id"]
    pack = attach_pack(
        store,
        scope="cluster",
        target_id=parent["id"],
        rules=["no live writes"],
        skills=["pytest"],
        wrappers=["role = CODER"],
        environments=["worktree"],
    )
    assert pack["scope"] == "cluster"
    pinned = set_project_shortcut(store, project["id"], 1)
    assert pinned["shortcut"] == 1
    with pytest.raises(Refuse):
        set_project_shortcut(store, project["id"], 7)
    with pytest.raises(Refuse):
        create_project(store, name="live", root=r"V:\A\Ai\COSMOS\live")
