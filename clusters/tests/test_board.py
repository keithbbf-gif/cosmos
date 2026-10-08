"""Kanban columns, review gates, and the auto lane."""

from __future__ import annotations

import pytest

from clusters.board import add_task, auto_tick, list_tasks, move_task, set_auto_limit
from clusters.mesh import create_project
from clusters.refuse import Refuse
from clusters.sessions import open_session
from clusters.store import Store


def _board(tmp_path):
    store = Store(tmp_path / "s")
    project = create_project(store, name="repo", root=str(tmp_path / "repo"))
    return store, project["id"]


def test_add_task_defaults_to_pending(tmp_path):
    store, project_id = _board(tmp_path)
    task = add_task(store, project_id=project_id, title="Write the board")
    assert task["column"] == "pending"
    assert task["op"] == "add"
    assert task["session_id"] == ""
    assert task["project_id"] == project_id
    assert list_tasks(store, project_id)[0]["id"] == task["id"]


def test_complete_from_pending_is_review(tmp_path):
    store, project_id = _board(tmp_path)
    task = add_task(store, project_id=project_id, title="Ship it")
    with pytest.raises(Refuse) as refused:
        move_task(
            store,
            task["id"],
            "completed",
            evidence={"source": "reviewer", "observed": "looks done"},
        )
    assert refused.value.code == "REVIEW"
    assert list_tasks(store, project_id)[0]["column"] == "pending"


def test_review_path_reaches_completed(tmp_path):
    store, project_id = _board(tmp_path)
    task = add_task(store, project_id=project_id, title="Fix the link")
    session = open_session(store, project_id=project_id, door="codex", task="Fix the link")
    working = move_task(
        store,
        task["id"],
        "in_progress",
        evidence={"session_id": session["id"]},
    )
    assert working["column"] == "in_progress"
    assert working["session_id"] == session["id"]
    testing = move_task(
        store,
        task["id"],
        "in_testing",
        evidence={"source": "pytest", "observed": "passed"},
    )
    assert testing["column"] == "in_testing"
    done = move_task(
        store,
        task["id"],
        "completed",
        evidence={"source": "reviewer", "observed": "accepted"},
    )
    assert done["column"] == "completed"


def test_auto_tick_starts_sol_without_executing(tmp_path):
    store, project_id = _board(tmp_path)
    task = add_task(
        store,
        project_id=project_id,
        title="Add one function that returns 1.",
        column="auto",
        hero="sol",
        door="cosmos-code",
    )
    result = auto_tick(store, project_id=project_id)
    assert result["executed"] is False
    assert result["started"] == [task["id"]]
    assert result["limit"] == 2
    row = list_tasks(store, project_id)[0]
    assert row["column"] == "in_progress"
    assert row["plan"]["seated"] is False
    assert row["plan"]["started"] is False
    session = store.view("session")[row["session_id"]]
    assert session["open"] is True
    assert session["hero"] == "sol"
    assert session["door"] == "cosmos-code"
    assert session["task"] == "Add one function that returns 1."


def test_auto_limit_zero_refuses(tmp_path):
    store, _project_id = _board(tmp_path)
    with pytest.raises(Refuse) as refused:
        set_auto_limit(store, 0)
    assert refused.value.code == "LIMIT"
