"""Door ids are stored on a seat. This does not resume.

Python 3.11. create_project and open_session make the seat. A conversation
id is not a resume claim, and this does not call the harness.
"""

from __future__ import annotations

import pytest

from clusters.doorid import get_door_id, set_door_id
from clusters.mesh import create_project
from clusters.refuse import Refuse
from clusters.sessions import open_session
from clusters.store import Store


def _open(tmp_path):
    store = Store(tmp_path / "s")
    project = create_project(store, name="web", root=str(tmp_path / "web"))
    session = open_session(store, project_id=project["id"], door="codex", task="door")
    return store, session


def test_good_id(tmp_path):
    store, session = _open(tmp_path)
    saved = set_door_id(
        store,
        session_id=session["id"],
        conversation_id="agy-conv-7f3a",
        home="native",
    )
    assert saved["id"] == f"doorid-{session['id']}"
    assert saved["session_id"] == session["id"]
    assert saved["conversation_id"] == "agy-conv-7f3a"
    assert saved["home"] == "native"
    assert saved["resume_claimed"] is False
    again = get_door_id(store, session["id"])
    assert again["conversation_id"] == "agy-conv-7f3a"
    assert again["home"] == "native"
    assert again["resume_claimed"] is False
    other = open_session(store, project_id=session["project_id"], door="codex", task="wsl")
    wsl = set_door_id(
        store,
        session_id=other["id"],
        conversation_id="kimi-ses-9",
        home="wsl",
    )
    assert wsl["home"] == "wsl"
    assert wsl["conversation_id"] == "kimi-ses-9"
    assert wsl["resume_claimed"] is False
    assert get_door_id(store, other["id"])["resume_claimed"] is False
    event = store.fold("door_id")[0]
    assert event["kind"] == "door_id"
    assert event["body"]["resume_claimed"] is False
    assert event["body"]["home"] == "native"
    wide = "c" * 120
    edged = set_door_id(
        store,
        session_id=session["id"],
        conversation_id=wide,
        home="native",
    )
    assert edged["conversation_id"] == wide
    assert edged["resume_claimed"] is False
    assert get_door_id(store, session["id"])["conversation_id"] == wide


def test_bad_home(tmp_path):
    store, session = _open(tmp_path)
    with pytest.raises(Refuse) as refused:
        set_door_id(
            store,
            session_id=session["id"],
            conversation_id="agy-conv-7f3a",
            home="linux",
        )
    assert refused.value.code == "HOME"
    assert refused.value.detail == ""
    assert store.view("door_id") == {}
    assert store.fold("door_id") == []


def test_empty_id(tmp_path):
    store, session = _open(tmp_path)
    with pytest.raises(Refuse) as refused:
        set_door_id(
            store,
            session_id=session["id"],
            conversation_id="",
            home="native",
        )
    assert refused.value.code == "DOOR_ID"
    assert refused.value.detail == ""
    with pytest.raises(Refuse) as broken:
        set_door_id(
            store,
            session_id=session["id"],
            conversation_id="agy\nconv",
            home="wsl",
        )
    assert broken.value.code == "DOOR_ID"
    with pytest.raises(Refuse) as long:
        set_door_id(
            store,
            session_id=session["id"],
            conversation_id="c" * 121,
            home="native",
        )
    assert long.value.code == "DOOR_ID"
    assert store.view("door_id") == {}
    assert store.fold("door_id") == []


def test_resume_claimed_false(tmp_path):
    store, session = _open(tmp_path)
    saved = set_door_id(
        store,
        session_id=session["id"],
        conversation_id="agy-conv-7f3a",
        home="native",
    )
    assert saved["resume_claimed"] is False
    assert get_door_id(store, session["id"])["resume_claimed"] is False
    # A later fold may say otherwise. The read still does not resume.
    store.append(
        "door_id",
        {
            "id": f"doorid-{session['id']}",
            "resume_claimed": True,
        },
    )
    again = get_door_id(store, session["id"])
    assert again["resume_claimed"] is False
    assert again["conversation_id"] == "agy-conv-7f3a"
    assert again["home"] == "native"
    assert store.fold("door_id")[-1]["body"]["resume_claimed"] is True


def test_missing_session_and_missing_row(tmp_path):
    store = Store(tmp_path / "s")
    with pytest.raises(Refuse) as refused:
        set_door_id(
            store,
            session_id="ses-missing",
            conversation_id="agy-conv-7f3a",
            home="native",
        )
    assert refused.value.code == "SESSION"
    assert refused.value.detail == "ses-missing"
    with pytest.raises(Refuse) as missing_get:
        get_door_id(store, "ses-missing")
    assert missing_get.value.code == "SESSION"
    assert missing_get.value.detail == ""
    _store, session = _open(tmp_path)
    with pytest.raises(Refuse) as missing_row:
        get_door_id(_store, session["id"])
    assert missing_row.value.code == "DOOR_ID"
    assert missing_row.value.detail == "missing"
