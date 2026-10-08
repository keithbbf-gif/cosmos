"""Auto Kanban queue paths. Drag, lightning, and a new card."""

from __future__ import annotations

import pytest

from clusters.board import add_task
from clusters.lane import queue_drag, queue_lightning, queue_new, set_defaults
from clusters.mesh import create_project
from clusters.refuse import Refuse
from clusters.store import Store


def _project(tmp_path):
    store = Store(tmp_path / "s")
    project = create_project(store, name="repo", root=str(tmp_path / "repo"))
    return store, project["id"]


def test_drag_without_defaults_refuses(tmp_path):
    store, project_id = _project(tmp_path)
    task = add_task(store, project_id=project_id, title="Write the lane")
    with pytest.raises(Refuse) as refused:
        queue_drag(store, task["id"])
    assert refused.value.code == "DEFAULTS"
    assert store.view("task")[task["id"]]["column"] == "pending"
    assert store.view("session") == {}


def test_set_defaults_then_drag_copies_door(tmp_path):
    store, project_id = _project(tmp_path)
    other = create_project(store, name="other", root=str(tmp_path / "other"))
    task = add_task(store, project_id=project_id, title="Write the lane")
    saved = set_defaults(
        store,
        project_id=project_id,
        door="codex",
        hero="sol",
        model="gpt",
        reasoning="high",
        permission="turbo",
        workspace="branch",
    )
    set_defaults(store, project_id=other["id"], door="pi", hero="luna")
    assert saved["id"] == f"defaults-{project_id}"
    assert saved["op"] == "set"
    queued = queue_drag(store, task["id"])
    assert queued["column"] == "auto"
    assert queued["op"] == "queue"
    assert queued["door"] == "codex"
    assert queued["hero"] == "sol"
    assert queued["model"] == "gpt"
    assert queued["reasoning"] == "high"
    assert queued["permission"] == "turbo"
    assert queued["workspace"] == "branch"
    assert queued["session_id"] == ""
    assert "plan" not in queued
    event = store.fold("task")[-1]["body"]
    assert event["op"] == "queue"
    assert all(not str(key).startswith("_") for key in event)
    assert store.view("session") == {}
    with pytest.raises(Refuse) as refused:
        queue_drag(store, task["id"])
    assert refused.value.code == "QUEUE"
    assert store.view("task")[task["id"]]["column"] == "auto"


def test_lightning_override_does_not_change_defaults(tmp_path):
    store, project_id = _project(tmp_path)
    task = add_task(store, project_id=project_id, title="Override once")
    set_defaults(
        store,
        project_id=project_id,
        door="cosmos-code",
        hero="sol",
        reasoning="medium",
    )
    defaults_id = f"defaults-{project_id}"
    before = dict(store.view("auto_defaults")[defaults_id])
    queued = queue_lightning(store, task["id"], reasoning="max")
    assert queued["column"] == "auto"
    assert queued["op"] == "lightning"
    assert queued["reasoning"] == "max"
    assert queued["door"] == "cosmos-code"
    assert queued["hero"] == "sol"
    assert queued["session_id"] == ""
    assert store.view("auto_defaults")[defaults_id] == before
    assert store.view("session") == {}
    fresh = add_task(store, project_id=project_id, title="New with one override")
    created = queue_new(store, project_id=project_id, title="New with one override", reasoning="max")
    assert created["id"] != fresh["id"]
    assert created["column"] == "auto"
    assert created["op"] == "lightning"
    assert created["reasoning"] == "max"
    assert created["door"] == "cosmos-code"
    assert store.view("auto_defaults")[defaults_id] == before


def test_queue_new_without_overrides_lands_in_auto(tmp_path):
    store, project_id = _project(tmp_path)
    set_defaults(
        store,
        project_id=project_id,
        door="opencode",
        hero="mini",
        model="gpt",
    )
    queued = queue_new(
        store,
        project_id=project_id,
        title="Already auto",
        body="notes",
        labels=["lane"],
    )
    assert queued["column"] == "auto"
    assert queued["op"] == "queue"
    assert queued["title"] == "Already auto"
    assert queued["body"] == "notes"
    assert queued["labels"] == ["lane"]
    assert queued["door"] == "opencode"
    assert queued["hero"] == "mini"
    assert queued["model"] == "gpt"
    assert queued["reasoning"] == "medium"
    assert queued["permission"] == "default"
    assert queued["workspace"] == "worktree"
    assert queued["session_id"] == ""
    bodies = [row["body"] for row in store.fold("task") if row["body"]["id"] == queued["id"]]
    assert [row["column"] for row in bodies] == ["pending", "auto"]
    assert [row["op"] for row in bodies] == ["add", "queue"]
    assert store.view("session") == {}


def test_reasoning_huge_refuses(tmp_path):
    store, project_id = _project(tmp_path)
    with pytest.raises(Refuse) as refused:
        set_defaults(store, project_id=project_id, door="codex", reasoning="huge")
    assert refused.value.code == "DEFAULTS"
    assert store.view("auto_defaults") == {}
    set_defaults(store, project_id=project_id, door="codex", reasoning="low")
    task = add_task(store, project_id=project_id, title="Stay pending")
    before = dict(store.view("auto_defaults")[f"defaults-{project_id}"])
    with pytest.raises(Refuse) as refused:
        queue_lightning(store, task["id"], reasoning="huge")
    assert refused.value.code == "DEFAULTS"
    assert store.view("task")[task["id"]]["column"] == "pending"
    assert store.view("auto_defaults")[f"defaults-{project_id}"] == before


def test_workspace_live_refuses(tmp_path):
    store, project_id = _project(tmp_path)
    with pytest.raises(Refuse) as refused:
        set_defaults(store, project_id=project_id, door="codex", workspace="live")
    assert refused.value.code == "DEFAULTS"
    assert store.view("auto_defaults") == {}
    set_defaults(store, project_id=project_id, door="codex", workspace="folder")
    task = add_task(store, project_id=project_id, title="Stay pending")
    before = dict(store.view("auto_defaults")[f"defaults-{project_id}"])
    with pytest.raises(Refuse) as refused:
        queue_lightning(store, task["id"], workspace="live")
    assert refused.value.code == "DEFAULTS"
    assert store.view("task")[task["id"]]["column"] == "pending"
    assert store.view("auto_defaults")[f"defaults-{project_id}"]["workspace"] == "folder"
    assert store.view("auto_defaults")[f"defaults-{project_id}"] == before
