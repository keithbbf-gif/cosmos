"""Conflict outcomes are stored. Git is not run and the file is not changed."""

from __future__ import annotations

import pytest

from clusters.conflict import OUTCOMES, list_conflicts, record_conflict
from clusters.mesh import create_project
from clusters.refuse import Refuse
from clusters.sessions import open_session
from clusters.store import Store


def _open(tmp_path):
    store = Store(tmp_path / "c")
    project = create_project(store, name="web", root=str(tmp_path / "web"))
    session = open_session(store, project_id=project["id"], door="codex", task="edit")
    return store, session["id"]


def test_outcomes():
    assert OUTCOMES == ("unresolved", "agent-resolved", "operator")


def test_unresolved_is_stored_and_not_executed(tmp_path):
    # Git is not run. The path is not written or resolved.
    store, session_id = _open(tmp_path)
    path = tmp_path / "web" / "a.py"
    path.parent.mkdir()
    path.write_text("kept\n", encoding="utf-8")
    row = record_conflict(
        store,
        session_id=session_id,
        path=str(path),
        outcome="unresolved",
    )
    assert row["id"].startswith("cfl-")
    assert len(row["id"]) == 16
    assert row["session_id"] == session_id
    assert row["path"] == str(path)
    assert row["outcome"] == "unresolved"
    assert row["executed"] is False
    assert row["_verdict"] == "RECORDED"
    event = store.fold("conflict")[-1]
    assert event["kind"] == "conflict"
    assert event["seq"] == row["_seq"]
    assert event["body"] == {
        "id": row["id"],
        "session_id": session_id,
        "path": str(path),
        "outcome": "unresolved",
        "executed": False,
    }
    assert path.read_text(encoding="utf-8") == "kept\n"
    listed = list_conflicts(store, session_id)
    assert [item["id"] for item in listed] == [row["id"]]
    assert listed[0]["executed"] is False
    assert listed[0]["outcome"] == "unresolved"
    assert path.read_text(encoding="utf-8") == "kept\n"


@pytest.mark.parametrize("outcome", ["agent-resolved", "operator"])
def test_named_outcomes_stay_unexecuted(tmp_path, outcome):
    # Git is not run. A missing path is not created.
    store, session_id = _open(tmp_path)
    path = tmp_path / "web" / "b.py"
    row = record_conflict(
        store,
        session_id=session_id,
        path=str(path),
        outcome=outcome,
    )
    assert row["outcome"] == outcome
    assert row["executed"] is False
    assert store.fold("conflict")[-1]["body"]["executed"] is False
    assert path.exists() is False


def test_bad_outcome_refuses(tmp_path):
    store, session_id = _open(tmp_path)
    path = tmp_path / "web" / "a.py"
    with pytest.raises(Refuse) as refused:
        record_conflict(
            store,
            session_id=session_id,
            path=str(path),
            outcome="merged",
        )
    assert refused.value.code == "OUTCOME"
    assert refused.value.detail == ""
    assert store.fold("conflict") == []
    assert path.exists() is False


def test_live_path_refuses(tmp_path):
    # Git is not run. The live path is only a string. This test does not open it.
    store, session_id = _open(tmp_path)
    live = r"V:\A\Ai\COSMOS\live\x.py"
    with pytest.raises(Refuse) as refused:
        record_conflict(
            store,
            session_id=session_id,
            path=live,
            outcome="unresolved",
        )
    assert refused.value.code == "LIVE_TREE"
    assert refused.value.detail == live
    assert store.fold("conflict") == []


def test_missing_session_refuses(tmp_path):
    store, _session_id = _open(tmp_path)
    with pytest.raises(Refuse) as refused:
        record_conflict(
            store,
            session_id="ses-missing",
            path="a.py",
            outcome="unresolved",
        )
    assert refused.value.code == "SESSION"
    assert refused.value.detail == "ses-missing"
    assert store.fold("conflict") == []


def test_list_conflicts_filters_session_and_sorts(tmp_path):
    # Git is not run. Listing does not open the paths.
    store, first = _open(tmp_path)
    project_id = store.view("session")[first]["project_id"]
    second = open_session(store, project_id=project_id, door="codex", task="other")["id"]
    one = record_conflict(store, session_id=first, path="a.py", outcome="agent-resolved")
    two = record_conflict(store, session_id=first, path="b.py", outcome="operator")
    other = record_conflict(store, session_id=second, path="c.py", outcome="unresolved")
    listed = list_conflicts(store, first)
    assert [row["id"] for row in listed] == sorted([one["id"], two["id"]])
    assert all(row["executed"] is False for row in listed)
    assert other["id"] not in [row["id"] for row in listed]
    everything = list_conflicts(store)
    assert [row["id"] for row in everything] == sorted([one["id"], two["id"], other["id"]])
    assert list_conflicts(store, "ses-other") == []
