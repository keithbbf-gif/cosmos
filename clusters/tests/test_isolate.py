"""Isolation intent is stored. Git is not run."""

from __future__ import annotations

import pytest

from clusters.board import add_task
from clusters.isolate import plan_isolation
from clusters.mesh import create_project
from clusters.refuse import Refuse
from clusters.store import Store


def _task(tmp_path):
    store = Store(tmp_path / "s")
    project = create_project(store, name="repo", root=str(tmp_path / "repo"))
    task = add_task(store, project_id=project["id"], title="Isolate the seat")
    return store, task["id"]


def test_own_worktree_records_intent(tmp_path):
    # Git is not run. The row is the operator's intent only.
    store, task_id = _task(tmp_path)
    row = plan_isolation(
        store,
        task_id=task_id,
        base_ref="main",
        share="own",
        workspace="worktree",
        paths=["src/a.py"],
    )
    assert row["id"].startswith("iso-")
    assert row["task_id"] == task_id
    assert row["base_ref"] == "main"
    assert row["share"] == "own"
    assert row["workspace"] == "worktree"
    assert row["why"] == ""
    assert row["paths"] == ["src/a.py"]
    assert row["executed"] is False
    assert row["git"] is False
    assert row["_verdict"] == "RECORDED"
    event = store.fold("isolation")[-1]
    assert event["kind"] == "isolation"
    assert event["body"]["executed"] is False
    assert event["body"]["git"] is False
    assert store.view("worktree") == {}


def test_folder_with_why(tmp_path):
    store, task_id = _task(tmp_path)
    reason = "repo has no commits; using the project folder"
    row = plan_isolation(
        store,
        task_id=task_id,
        base_ref="main",
        share="share",
        workspace="folder",
        why=reason,
    )
    assert row["share"] == "share"
    assert row["workspace"] == "folder"
    assert row["why"] == reason
    assert row["paths"] == []
    assert row["executed"] is False
    assert row["git"] is False


def test_folder_without_why_refuses(tmp_path):
    store, task_id = _task(tmp_path)
    with pytest.raises(Refuse) as refused:
        plan_isolation(
            store,
            task_id=task_id,
            base_ref="main",
            share="own",
            workspace="folder",
        )
    assert refused.value.code == "WHY"
    assert store.view("isolation") == {}


def test_origin_main_is_accepted_as_a_name(tmp_path):
    store, task_id = _task(tmp_path)
    row = plan_isolation(
        store,
        task_id=task_id,
        base_ref="origin/main",
        share="own",
        workspace="worktree",
    )
    assert row["base_ref"] == "origin/main"
    assert row["executed"] is False
    assert row["git"] is False


def test_dotdot_path_refused(tmp_path):
    store, task_id = _task(tmp_path)
    with pytest.raises(Refuse) as refused:
        plan_isolation(
            store,
            task_id=task_id,
            base_ref="main",
            share="own",
            workspace="worktree",
            paths=["../secret"],
        )
    assert refused.value.code == "PATH"
    assert store.view("isolation") == {}


def test_missing_task_refuses(tmp_path):
    store = Store(tmp_path / "s")
    with pytest.raises(Refuse) as refused:
        plan_isolation(
            store,
            task_id="tsk-missing",
            base_ref="main",
            share="own",
            workspace="worktree",
        )
    assert refused.value.code == "TASK"
    assert refused.value.detail == "tsk-missing"
