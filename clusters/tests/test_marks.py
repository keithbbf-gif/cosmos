"""History bookmarks. A hide flag stays in the jsonl; the body is not copied."""

from __future__ import annotations

import json

import pytest

from clusters.history import add_message
from clusters.marks import add_bookmark, hide_bookmark, list_bookmarks
from clusters.mesh import create_project
from clusters.refuse import Refuse
from clusters.sessions import open_session
from clusters.store import Store


def _bookmark_bodies(store: Store) -> list[dict]:
    bodies: list[dict] = []
    for line in store.path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row["kind"] == "bookmark":
            bodies.append(row["body"])
    return bodies


def test_missing_session_refuses(tmp_path):
    store = Store(tmp_path / "h")
    project = create_project(store, name="web", root=str(tmp_path / "repo"))
    open_session(store, project_id=project["id"], door="codex", task="stay")
    with pytest.raises(Refuse) as refused:
        add_bookmark(store, session_id="ses-missing", note="later")
    assert refused.value.code == "SESSION"


def test_bookmark_then_list(tmp_path):
    store = Store(tmp_path / "h")
    project = create_project(store, name="web", root=str(tmp_path / "repo"))
    session = open_session(store, project_id=project["id"], door="codex", task="stay")
    message = add_message(
        store,
        session_id=session["id"],
        role="user",
        kind="user",
        body="add dark mode",
    )
    marked = add_bookmark(
        store,
        session_id=session["id"],
        message_id=message["id"],
        note="theme",
    )
    plain = add_bookmark(store, session_id=session["id"])
    assert marked["session_id"] == session["id"]
    assert marked["message_id"] == message["id"]
    assert marked["note"] == "theme"
    assert marked["removed"] is False
    assert plain["note"] == ""
    assert plain["message_id"] == ""
    assert "body" not in marked
    listed = list_bookmarks(store, session_id=session["id"])
    assert [row["id"] for row in listed] == sorted([marked["id"], plain["id"]])
    assert list_bookmarks(store, session_id="ses-other") == []
    for body in _bookmark_bodies(store):
        assert "body" not in body
        assert "add dark mode" not in json.dumps(body)


def test_hide_removes_from_list_and_keeps_jsonl(tmp_path):
    store = Store(tmp_path / "h")
    project = create_project(store, name="web", root=str(tmp_path / "repo"))
    session = open_session(store, project_id=project["id"], door="codex", task="stay")
    marked = add_bookmark(store, session_id=session["id"], note="keep")
    hidden = hide_bookmark(store, marked["id"])
    assert hidden["id"] == marked["id"]
    assert hidden["removed"] is True
    assert list_bookmarks(store) == []
    assert list_bookmarks(store, session_id=session["id"]) == []
    bodies = [body for body in _bookmark_bodies(store) if body["id"] == marked["id"]]
    assert [body["removed"] for body in bodies] == [False, True]
    with pytest.raises(Refuse) as refused:
        hide_bookmark(store, "bmk-missing")
    assert refused.value.code == "BOOKMARK"


def test_message_on_another_session_refuses(tmp_path):
    store = Store(tmp_path / "h")
    web = create_project(store, name="web", root=str(tmp_path / "repo"))
    other = create_project(store, name="other", root=str(tmp_path / "other"))
    here = open_session(store, project_id=web["id"], door="codex", task="stay")
    there = open_session(store, project_id=other["id"], door="codex", task="stay")
    foreign = add_message(
        store,
        session_id=there["id"],
        role="user",
        kind="user",
        body="dark mode elsewhere",
    )
    with pytest.raises(Refuse) as refused:
        add_bookmark(store, session_id=here["id"], message_id=foreign["id"])
    assert refused.value.code == "MESSAGE"
    assert refused.value.detail == foreign["id"]
    with pytest.raises(Refuse) as missing:
        add_bookmark(store, session_id=here["id"], message_id="msg-missing")
    assert missing.value.code == "MESSAGE"
    assert list_bookmarks(store) == []


def test_note_must_be_one_line(tmp_path):
    store = Store(tmp_path / "h")
    project = create_project(store, name="web", root=str(tmp_path / "repo"))
    session = open_session(store, project_id=project["id"], door="codex", task="stay")
    with pytest.raises(Refuse) as broken:
        add_bookmark(store, session_id=session["id"], note="two\nlines")
    assert broken.value.code == "NOTE"
    with pytest.raises(Refuse) as long_note:
        add_bookmark(store, session_id=session["id"], note="x" * 241)
    assert long_note.value.code == "NOTE"
    kept = add_bookmark(store, session_id=session["id"], note="x" * 240)
    assert kept["note"] == "x" * 240
    assert list_bookmarks(store)[0]["id"] == kept["id"]
