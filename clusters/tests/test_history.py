"""Transcript search and resume pointers."""

from __future__ import annotations

import pytest

from clusters.history import add_message, resume_pointer, search
from clusters.mesh import create_project
from clusters.refuse import Refuse
from clusters.sessions import open_session
from clusters.store import Store


def test_message_on_unknown_session_refuses(tmp_path):
    store = Store(tmp_path / "h")
    project = create_project(store, name="web", root=str(tmp_path / "repo"))
    open_session(store, project_id=project["id"], door="codex", task="stay")
    with pytest.raises(Refuse) as refused:
        add_message(store, session_id="ses-missing", role="user", kind="user", body="hello")
    assert refused.value.code == "SESSION"


def test_search_finds_dark_mode_and_filters_project(tmp_path):
    store = Store(tmp_path / "h")
    web = create_project(store, name="web", root=str(tmp_path / "repo"))
    other = create_project(store, name="other", root=str(tmp_path / "repo"))
    here = open_session(store, project_id=web["id"], door="codex", task="theme")
    there = open_session(store, project_id=other["id"], door="codex", task="theme")
    first = add_message(store, session_id=here["id"], role="user", kind="user", body="add dark mode")
    elsewhere = add_message(
        store, session_id=there["id"], role="user", kind="user", body="dark mode elsewhere"
    )
    second = add_message(
        store, session_id=here["id"], role="agent", kind="agent", body="dark mode polish"
    )
    assert first["sender_id"] == ""
    assert first["project_id"] == web["id"]
    hits = search(store, "dark mode", project_id=web["id"])
    assert [row["id"] for row in hits] == [second["id"], first["id"]]
    assert elsewhere["id"] not in {row["id"] for row in hits}
    assert search(store, "") == []


def test_search_is_case_insensitive(tmp_path):
    store = Store(tmp_path / "h")
    project = create_project(store, name="web", root=str(tmp_path / "repo"))
    session = open_session(store, project_id=project["id"], door="codex", task="theme")
    add_message(store, session_id=session["id"], role="user", kind="user", body="Ship Dark Mode")
    found = search(store, "dark mode")
    assert len(found) == 1
    assert found[0]["body"] == "Ship Dark Mode"


def test_resume_pointer_codex_is_catalog_only(tmp_path):
    store = Store(tmp_path / "h")
    project = create_project(store, name="web", root=str(tmp_path / "repo"))
    session = open_session(store, project_id=project["id"], door="codex", task="continue")
    first = add_message(store, session_id=session["id"], role="user", kind="user", body="start")
    second = add_message(
        store,
        session_id=session["id"],
        role="agent",
        kind="agent",
        body="ack",
        resume_of=first["id"],
        sender_id="agent-1",
    )
    pointer = resume_pointer(store, session["id"])
    assert pointer["resume"] is True
    assert pointer["claimed"] is False
    assert pointer["session_id"] == session["id"]
    assert pointer["chain"] == [session["id"], first["id"], second["id"]]


def test_resume_pointer_kimi_cannot_resume(tmp_path):
    store = Store(tmp_path / "h")
    project = create_project(store, name="web", root=str(tmp_path / "repo"))
    session = open_session(store, project_id=project["id"], door="kimi", task="read")
    pointer = resume_pointer(store, session["id"])
    assert pointer["resume"] is False
    assert pointer["claimed"] is False
    assert pointer["chain"] == [session["id"]]
