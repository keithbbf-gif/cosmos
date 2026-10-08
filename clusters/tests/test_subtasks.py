"""Kanban subtasks. One level, records only."""

from __future__ import annotations

import pytest

from clusters.board import add_task, list_tasks
from clusters.mesh import create_project
from clusters.refuse import Refuse
from clusters.store import Store
from clusters.subtasks import add_subtask, list_subtasks

_CARD = (
    "id",
    "project_id",
    "title",
    "body",
    "column",
    "door",
    "hero",
    "model",
    "labels",
    "workspace",
    "session_id",
)


def _board(tmp_path):
    store = Store(tmp_path / "s")
    project = create_project(store, name="repo", root=str(tmp_path / "repo"))
    return store, project["id"]


def test_add_subtask_records_pending_child(tmp_path):
    store, project_id = _board(tmp_path)
    parent = add_task(store, project_id=project_id, title="Parent card")
    child = add_subtask(
        store,
        parent_id=parent["id"],
        title="Child card",
        body="notes",
    )
    assert child["parent_id"] == parent["id"]
    assert child["op"] == "subtask"
    assert child["column"] == "pending"
    assert child["project_id"] == project_id
    assert child["title"] == "Child card"
    assert child["body"] == "notes"
    assert child["session_id"] == ""
    assert child["labels"] == []
    for key in _CARD:
        assert key in child
    events = [
        row["body"]
        for row in store.fold("task")
        if row["body"].get("id") == child["id"]
    ]
    assert [row["op"] for row in events] == ["add", "subtask"]
    assert "parent_id" not in events[0]
    for key in _CARD:
        assert key in events[1]
    assert events[1]["parent_id"] == parent["id"]
    assert events[1]["op"] == "subtask"
    assert not any(str(key).startswith("_") for key in events[1])
    listed = list_tasks(store, project_id)
    again = next(row for row in listed if row["id"] == child["id"])
    assert again["parent_id"] == parent["id"]
    assert again["column"] == "pending"
    assert again["title"] == "Child card"
    assert store.view("task")[parent["id"]]["column"] == "pending"
    assert "parent_id" not in store.view("task")[parent["id"]]
    assert store.view("session") == {}


def test_default_body_is_empty(tmp_path):
    store, project_id = _board(tmp_path)
    parent = add_task(store, project_id=project_id, title="Parent card")
    child = add_subtask(store, parent_id=parent["id"], title="Bare child")
    assert child["body"] == ""
    assert child["column"] == "pending"


def test_missing_parent_refuses(tmp_path):
    store, project_id = _board(tmp_path)
    before = len(store.fold("task"))
    with pytest.raises(Refuse) as refused:
        add_subtask(store, parent_id="tsk-missing", title="Orphan")
    assert refused.value.code == "TASK"
    assert refused.value.detail == "tsk-missing"
    with pytest.raises(Refuse) as listed:
        list_subtasks(store, "tsk-missing")
    assert listed.value.code == "TASK"
    assert listed.value.detail == "tsk-missing"
    assert len(store.fold("task")) == before
    assert list_tasks(store, project_id) == []


def test_nested_subtask_refuses(tmp_path):
    store, project_id = _board(tmp_path)
    parent = add_task(store, project_id=project_id, title="Parent card")
    child = add_subtask(store, parent_id=parent["id"], title="Child card")
    before = len(store.fold("task"))
    with pytest.raises(Refuse) as refused:
        add_subtask(store, parent_id=child["id"], title="Grandchild")
    assert refused.value.code == "SUBTASK"
    assert refused.value.detail == "nested"
    assert len(store.fold("task")) == before
    assert [row["id"] for row in list_subtasks(store, parent["id"])] == [child["id"]]
    assert list_subtasks(store, child["id"]) == []
    assert store.view("task")[child["id"]]["column"] == "pending"


def test_list_subtasks_sorts_only_matching_children(tmp_path):
    store, project_id = _board(tmp_path)
    first = add_task(store, project_id=project_id, title="First")
    second = add_task(store, project_id=project_id, title="Second")
    one = add_subtask(store, parent_id=first["id"], title="One")
    two = add_subtask(store, parent_id=first["id"], title="Two", body="kept")
    other = add_subtask(store, parent_id=second["id"], title="Other")
    listed = list_subtasks(store, first["id"])
    assert [row["id"] for row in listed] == sorted(row["id"] for row in (one, two))
    assert {row["id"] for row in listed} == {one["id"], two["id"]}
    assert other["id"] not in {row["id"] for row in listed}
    kept = next(row for row in listed if row["id"] == two["id"])
    assert kept["body"] == "kept"
    assert kept["parent_id"] == first["id"]
    assert list_subtasks(store, second["id"])[0]["id"] == other["id"]


def test_blank_title_does_not_record_a_child(tmp_path):
    store, project_id = _board(tmp_path)
    parent = add_task(store, project_id=project_id, title="Parent card")
    before = len(store.fold("task"))
    with pytest.raises(Refuse) as refused:
        add_subtask(store, parent_id=parent["id"], title="  ")
    assert refused.value.code == "TITLE"
    assert len(store.fold("task")) == before
    assert list_subtasks(store, parent["id"]) == []
