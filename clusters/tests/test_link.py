"""Finished work waits in testing. The move is not a completion."""

from __future__ import annotations

from clusters.board import add_task, move_task
from clusters.catalog import list_notes
from clusters.link import on_status
from clusters.mesh import create_project
from clusters.sessions import open_session
from clusters.store import Store

_PASS = {"source": "pytest", "observed": "1 passed"}


def _board(tmp_path):
    store = Store(tmp_path / "s")
    project = create_project(store, name="repo", root=str(tmp_path / "repo"))
    session = open_session(
        store, project_id=project["id"], door="cosmos-code", task="Fix the link"
    )
    task = add_task(store, project_id=project["id"], title="Fix the link")
    move_task(
        store,
        task["id"],
        "in_progress",
        evidence={"session_id": session["id"]},
    )
    return store, session, task


def test_finished_moves_card_to_testing_and_notes(tmp_path):
    store, session, task = _board(tmp_path)
    result = on_status(store, session["id"], "finished", evidence=_PASS)
    assert result["session_id"] == session["id"]
    assert result["verified_status"] == "finished"
    assert result["moved"] == [task["id"]]
    assert result["noted"] is True
    card = store.view("task")[task["id"]]
    assert card["column"] == "in_testing"
    assert card["column"] != "completed"
    notes = [
        row
        for row in list_notes(store)
        if row["session_id"] == session["id"] and row["note"] == "finished"
    ]
    assert notes
    assert notes[0]["detail"] == "finished"


def test_finished_without_evidence_does_not_move(tmp_path):
    store, session, task = _board(tmp_path)
    previous = store.view("session")[session["id"]]["verified_status"]
    result = on_status(store, session["id"], "finished")
    assert result["verified_status"] == previous
    assert result["moved"] == []
    assert result["noted"] is False
    assert store.view("task")[task["id"]]["column"] == "in_progress"
    assert list_notes(store) == []


def test_needs_input_emits_and_leaves_the_card(tmp_path):
    store, session, task = _board(tmp_path)
    result = on_status(
        store,
        session["id"],
        "needs_input",
        evidence={"source": "door", "observed": "waiting"},
    )
    assert result["verified_status"] == "needs_input"
    assert result["noted"] is True
    assert result["moved"] == []
    assert store.view("task")[task["id"]]["column"] == "in_progress"
    notes = list_notes(store)
    assert len(notes) == 1
    assert notes[0]["note"] == "needs_input"
    assert notes[0]["session_id"] == session["id"]
    assert notes[0]["detail"] == "needs_input"


def test_moved_card_is_not_completed(tmp_path):
    store, session, task = _board(tmp_path)
    on_status(store, session["id"], "finished", evidence=_PASS)
    card = store.view("task")[task["id"]]
    assert card["column"] == "in_testing"
    assert card["column"] != "completed"


def test_same_finished_status_without_evidence_holds_a_later_card(tmp_path):
    store, session, task = _board(tmp_path)
    on_status(store, session["id"], "finished", evidence=_PASS)
    later = add_task(store, project_id=store.view("task")[task["id"]]["project_id"], title="Next")
    move_task(
        store,
        later["id"],
        "in_progress",
        evidence={"session_id": session["id"]},
    )
    result = on_status(store, session["id"], "finished")
    assert result["verified_status"] == "finished"
    assert result["moved"] == []
    assert result["held"] == [later["id"]]
    assert result["noted"] is False
    assert store.view("task")[later["id"]]["column"] == "in_progress"
    assert len(list_notes(store)) == 1
