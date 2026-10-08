"""Thread state. Settling does not close the session."""

from __future__ import annotations

import pytest

from clusters.history import add_message
from clusters.mesh import create_project
from clusters.refuse import Refuse
from clusters.sessions import get_session, open_session
from clusters.store import Store
from clusters.thread import get_thread, set_thread


def _open(tmp_path):
    store = Store(tmp_path / "s")
    project = create_project(store, name="web", root=str(tmp_path / "repo"))
    session = open_session(store, project_id=project["id"], door="codex", task="stay")
    return store, session


def test_three_states_last_write_wins(tmp_path):
    store, session = _open(tmp_path)
    active = set_thread(store, session_id=session["id"], state="active")
    assert active["id"] == f"thread-{session['id']}"
    assert active["op"] == "set"
    assert active["session_id"] == session["id"]
    assert active["state"] == "active"
    assert active["until"] == 0
    assert active["closed"] is False
    assert get_thread(store, session["id"])["state"] == "active"

    snoozed = set_thread(store, session_id=session["id"], state="snoozed", until=1_700_000_000)
    assert snoozed["state"] == "snoozed"
    assert snoozed["until"] == 1_700_000_000
    assert snoozed["closed"] is False
    floated = set_thread(store, session_id=session["id"], state="snoozed", until=1.5)
    assert floated["until"] == 1.5
    assert get_thread(store, session["id"])["state"] == "snoozed"

    settled = set_thread(store, session_id=session["id"], state="settled")
    assert settled["state"] == "settled"
    assert settled["until"] == 0
    assert settled["closed"] is False
    assert get_thread(store, session["id"])["state"] == "settled"
    assert len(store.view("thread")) == 1
    assert len(store.fold("thread")) == 4
    body = store.fold("thread")[-1]["body"]
    assert body == {
        "id": f"thread-{session['id']}",
        "op": "set",
        "session_id": session["id"],
        "state": "settled",
        "until": 0,
        "closed": False,
    }


def test_snooze_without_until_refuses(tmp_path):
    store, session = _open(tmp_path)
    before = len(store.fold("thread"))
    with pytest.raises(Refuse) as refused:
        set_thread(store, session_id=session["id"], state="snoozed")
    assert refused.value.code == "UNTIL"
    with pytest.raises(Refuse) as flagged:
        set_thread(store, session_id=session["id"], state="snoozed", until=True)
    assert flagged.value.code == "UNTIL"
    assert len(store.fold("thread")) == before


def test_settled_with_until_refuses(tmp_path):
    store, session = _open(tmp_path)
    before = len(store.fold("thread"))
    with pytest.raises(Refuse) as settled:
        set_thread(store, session_id=session["id"], state="settled", until=10)
    assert settled.value.code == "UNTIL"
    with pytest.raises(Refuse) as active:
        set_thread(store, session_id=session["id"], state="active", until=10)
    assert active.value.code == "UNTIL"
    with pytest.raises(Refuse) as pinned:
        set_thread(store, session_id=session["id"], state="pinned")
    assert pinned.value.code == "STATE"
    assert len(store.fold("thread")) == before


def test_settled_leaves_the_session_open(tmp_path):
    store, session = _open(tmp_path)
    kept = add_message(
        store, session_id=session["id"], role="user", kind="user", body="keep me"
    )
    # Settling does not close the session.
    before_open = get_session(store, session["id"])["open"]
    session_events = len(store.fold("session"))
    row = set_thread(store, session_id=session["id"], state="settled")
    assert row["state"] == "settled"
    assert row["closed"] is False
    after = get_session(store, session["id"])
    assert before_open is True
    assert after["open"] is True
    assert after["open"] == before_open
    assert len(store.fold("session")) == session_events
    assert store.view("message")[kept["id"]]["body"] == "keep me"


def test_missing_session_and_missing_thread(tmp_path):
    store, session = _open(tmp_path)
    with pytest.raises(Refuse) as missing_set:
        set_thread(store, session_id="ses-missing", state="active")
    assert missing_set.value.code == "SESSION"
    assert missing_set.value.detail == "ses-missing"
    with pytest.raises(Refuse) as missing_get:
        get_thread(store, "ses-missing")
    assert missing_get.value.code == "SESSION"
    assert missing_get.value.detail == "ses-missing"
    with pytest.raises(Refuse) as missing_thread:
        get_thread(store, session["id"])
    assert missing_thread.value.code == "THREAD"
    assert missing_thread.value.detail == "missing"
    assert store.fold("thread") == []
