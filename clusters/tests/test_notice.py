"""Attention is a reason and the store clock. Noting does not notify."""

from __future__ import annotations

import pytest

from clusters.mesh import create_project
from clusters.notice import list_attention, note_attention
from clusters.refuse import SECRET_KEYS, Refuse
from clusters.sessions import open_session
from clusters.store import Store

REASONS = ("approval", "failed", "question", "finished")


def _store(tmp_path):
    store = Store(tmp_path / "s")
    project = create_project(store, name="web", root=str(tmp_path / "web"))
    return store, project["id"]


@pytest.mark.parametrize("reason", REASONS)
def test_each_reason_records_time_without_notifying(tmp_path, reason):
    store, project_id = _store(tmp_path)
    session = open_session(store, project_id=project_id, door="codex", task="wait")
    before = dict(store.view("session")[session["id"]])
    noted = note_attention(store, session_id=session["id"], reason=reason)
    assert noted == {"session_id": session["id"], "reason": reason, "id": noted["id"]}
    assert noted["id"].startswith("att-")
    assert store.view("session")[session["id"]] == before
    events = store.fold("attention")
    assert len(events) == 1
    assert events[0]["kind"] == "attention"
    assert events[0]["body"] == {
        "id": noted["id"],
        "session_id": session["id"],
        "reason": reason,
    }
    assert "at" not in events[0]["body"]
    assert isinstance(events[0]["at"], float)
    assert store.fold("notification") == []
    listed = list_attention(store, session["id"])
    assert len(listed) == 1
    assert listed[0]["id"] == noted["id"]
    assert listed[0]["session_id"] == session["id"]
    assert listed[0]["reason"] == reason
    assert listed[0]["at"] == events[0]["at"]
    for key in SECRET_KEYS:
        assert key not in listed[0]


def test_bad_reason_refuses(tmp_path):
    store, project_id = _store(tmp_path)
    session = open_session(store, project_id=project_id, door="codex", task="wait")
    with pytest.raises(Refuse) as refused:
        note_attention(store, session_id=session["id"], reason="ping")
    assert refused.value.code == "REASON"
    assert refused.value.detail == "ping"
    assert store.fold("attention") == []
    assert store.fold("notification") == []


def test_missing_session_refuses(tmp_path):
    store, project_id = _store(tmp_path)
    open_session(store, project_id=project_id, door="codex", task="wait")
    with pytest.raises(Refuse) as refused:
        note_attention(store, session_id="ses-missing", reason="failed")
    assert refused.value.code == "SESSION"
    assert refused.value.detail == "ses-missing"
    assert store.fold("attention") == []


def test_list_filters_by_session_and_sorts_by_id(tmp_path):
    store, project_id = _store(tmp_path)
    first = open_session(store, project_id=project_id, door="codex", task="one")
    second = open_session(store, project_id=project_id, door="pi", task="two")
    approval = note_attention(store, session_id=first["id"], reason="approval")
    failed = note_attention(store, session_id=second["id"], reason="failed")
    question = note_attention(store, session_id=first["id"], reason="question")
    finished = note_attention(store, session_id=second["id"], reason="finished")
    one = list_attention(store, first["id"])
    assert [row["id"] for row in one] == sorted([approval["id"], question["id"]])
    assert {row["reason"] for row in one} == {"approval", "question"}
    assert all(row["session_id"] == first["id"] for row in one)
    two = list_attention(store, second["id"])
    assert [row["id"] for row in two] == sorted([failed["id"], finished["id"]])
    everything = list_attention(store)
    assert everything == list_attention(store, "")
    assert [row["id"] for row in everything] == sorted(
        [approval["id"], failed["id"], question["id"], finished["id"]]
    )
    assert list_attention(store, "ses-missing") == []
    for row in everything:
        for key in SECRET_KEYS:
            assert key not in row
