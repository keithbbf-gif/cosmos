"""Work-style text and attached image paths. Records only. Paths are not opened."""

from __future__ import annotations

import pytest

from clusters.attach import attach
from clusters.board import add_task
from clusters.mesh import create_project
from clusters.refuse import Refuse
from clusters.store import Store

_KEPT = (
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
    task = add_task(
        store,
        project_id=project["id"],
        title="First card",
        body="Ship the note",
        door="codex",
        hero="sol",
        model="gpt",
        labels=["kanban"],
        workspace="worktree",
    )
    return store, task


def test_normal_attach_keeps_pending(tmp_path):
    store, task = _board(tmp_path)
    attached = attach(store, task_id=task["id"], work_style="Normal")
    assert attached["op"] == "attach"
    assert attached["work_style"] == "Normal"
    assert attached["style_text"] == ""
    assert attached["images"] == []
    assert attached["column"] == "pending"
    for key in _KEPT:
        assert attached[key] == task[key]
    event = store.fold("task")[-1]["body"]
    assert event["op"] == "attach"
    assert event["column"] == "pending"
    assert not any(str(key).startswith("_") for key in event)
    for key in _KEPT:
        assert event[key] == task[key]
    assert [row["kind"] for row in store.fold()] == ["project", "task", "task"]
    assert store.view("session") == {}
    assert "plan" not in attached


def test_blocker_instruction_is_stored(tmp_path):
    store, task = _board(tmp_path)
    text = "Ask only when a choice blocks the card."
    shot = str(tmp_path / "shot.png")
    attached = attach(
        store,
        task_id=task["id"],
        work_style="Ask only for blockers",
        style_text=text,
        images=[shot],
    )
    assert attached["work_style"] == "Ask only for blockers"
    assert attached["style_text"] == text
    assert attached["images"] == [shot]
    assert attached["column"] == "pending"
    assert attached["op"] == "attach"
    for key in _KEPT:
        assert attached[key] == task[key]
    assert store.view("session") == {}


def test_best_judgment_accepts_eight_images(tmp_path):
    store, task = _board(tmp_path)
    text = "x" * 240
    images = [str(tmp_path / f"pic{index}.png") for index in range(8)]
    attached = attach(
        store,
        task_id=task["id"],
        work_style="Use best judgment",
        style_text=text,
        images=images,
    )
    assert attached["work_style"] == "Use best judgment"
    assert attached["style_text"] == text
    assert attached["images"] == images
    assert len(attached["images"]) == 8
    assert attached["column"] == "pending"
    assert store.view("task")[task["id"]]["column"] == "pending"
    assert store.view("session") == {}


def test_bad_style_refuses(tmp_path):
    store, task = _board(tmp_path)
    with pytest.raises(Refuse) as refused:
        attach(store, task_id=task["id"], work_style="best judgment")
    assert refused.value.code == "STYLE"
    assert refused.value.detail == "best judgment"
    row = store.view("task")[task["id"]]
    assert row["column"] == "pending"
    assert row["op"] == "add"
    assert "work_style" not in row
    assert store.view("session") == {}


def test_ninth_image_refuses(tmp_path):
    store, task = _board(tmp_path)
    images = [str(tmp_path / f"pic{index}.png") for index in range(9)]
    with pytest.raises(Refuse) as refused:
        attach(
            store,
            task_id=task["id"],
            work_style="Ask only for blockers",
            style_text="Stop only when blocked.",
            images=images,
        )
    assert refused.value.code == "STYLE"
    assert refused.value.detail == "images"
    row = store.view("task")[task["id"]]
    assert row["column"] == "pending"
    assert row["op"] == "add"
    assert "images" not in row
    assert [row["kind"] for row in store.fold()] == ["project", "task"]


def test_live_image_path_refuses(tmp_path):
    store, task = _board(tmp_path)
    live = r"V:\A\Ai\COSMOS\live\pic.png"
    with pytest.raises(Refuse) as refused:
        attach(store, task_id=task["id"], work_style="Normal", images=[live])
    assert refused.value.code == "LIVE_TREE"
    assert refused.value.detail == live
    row = store.view("task")[task["id"]]
    assert row["column"] == "pending"
    assert row["op"] == "add"
    assert "images" not in row
    assert store.view("session") == {}


def test_style_text_rules_refuse(tmp_path):
    store, task = _board(tmp_path)
    cases = (
        ("Normal", "Be brief."),
        ("Ask only for blockers", ""),
        ("Use best judgment", "one\ntwo"),
        ("Ask only for blockers", "a\rb"),
        ("Use best judgment", "x" * 241),
    )
    for work_style, style_text in cases:
        with pytest.raises(Refuse) as refused:
            attach(store, task_id=task["id"], work_style=work_style, style_text=style_text)
        assert refused.value.code == "STYLE"
        assert refused.value.detail == "text"
    row = store.view("task")[task["id"]]
    assert row["column"] == "pending"
    assert row["op"] == "add"


def test_missing_task_refuses(tmp_path):
    store, _task = _board(tmp_path)
    with pytest.raises(Refuse) as refused:
        attach(store, task_id="tsk-missing", work_style="Normal")
    assert refused.value.code == "TASK"
    assert refused.value.detail == "tsk-missing"
    assert store.view("session") == {}
