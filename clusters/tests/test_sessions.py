"""Session cap, evidence, and close confirmation."""

from __future__ import annotations

import pytest

from clusters.mesh import create_project
from clusters.refuse import Refuse
from clusters.sessions import (
    close_session,
    list_sessions,
    list_titles,
    open_session,
    set_status,
    set_title,
)
from clusters.store import Store


def _store(tmp_path):
    store = Store(tmp_path / "s")
    project = create_project(store, name="web", root=str(tmp_path / "web"))
    return store, project["id"]


def test_open_lists_and_pins_coordinator_first(tmp_path):
    store, project_id = _store(tmp_path)
    worker = open_session(store, project_id=project_id, door="codex", task="fix the link")
    lead = open_session(
        store, project_id=project_id, door="cosmos-code", role="coordinator", task="plan"
    )
    assert worker["status"] == "idle"
    assert worker["resume"] is True
    ordered = list_sessions(store, project_id)
    assert ordered[0]["id"] == lead["id"]


def test_finished_without_evidence_does_not_flip(tmp_path):
    store, project_id = _store(tmp_path)
    session = open_session(store, project_id=project_id, door="pi", task="tests")
    reported = set_status(store, session["id"], "finished", evidence={"source": "log"})
    assert reported["verified_status"] == "idle"
    assert reported["pending_report"] == "finished"
    assert reported["_verdict"] == "UNMEASURED"
    proven = set_status(
        store,
        session["id"],
        "finished",
        evidence={"source": "pytest", "observed": "12 passed"},
    )
    assert proven["verified_status"] == "finished"


def test_title_claim_needs_evidence(tmp_path):
    store, project_id = _store(tmp_path)
    session = open_session(store, project_id=project_id, door="opencode", task="rename")
    held = set_title(store, session["id"], "editing auth", evidence=None)
    assert held["verified_title"].startswith("opencode:")
    moved = set_title(
        store,
        session["id"],
        "editing auth",
        evidence={"source": "stdout", "observed": "editing auth"},
    )
    assert moved["verified_title"] == "editing auth"


def test_busy_child_close_needs_confirm(tmp_path):
    store, project_id = _store(tmp_path)
    parent = open_session(store, project_id=project_id, door="codex", role="coordinator", task="lead")
    child = open_session(
        store,
        project_id=project_id,
        door="codex",
        task="implement",
        parent_id=parent["id"],
    )
    set_status(
        store,
        child["id"],
        "working",
        evidence={"source": "door", "observed": "turn 1"},
    )
    with pytest.raises(Refuse) as refused:
        close_session(store, child["id"], confirm=False)
    assert refused.value.code == "CONFIRM"
    closed = close_session(store, child["id"], confirm=True)
    assert closed["open"] is False


def test_needs_input_without_evidence_does_not_flip(tmp_path):
    store, project_id = _store(tmp_path)
    session = open_session(store, project_id=project_id, door="codex", task="wait")
    held = set_status(store, session["id"], "needs_input")
    assert held["verified_status"] == "idle"
    assert held["pending_report"] == "needs_input"
    shown = set_status(
        store,
        session["id"],
        "needs_input",
        evidence={"source": "door", "observed": "approval prompt"},
    )
    assert shown["verified_status"] == "needs_input"


def test_new_session_takes_the_default_account(tmp_path):
    store, project_id = _store(tmp_path)
    from clusters.catalog import add_account

    account = add_account(
        store, provider="codex", label="main", profile_dir=str(tmp_path / "codex-home")
    )
    session = open_session(store, project_id=project_id, door="codex", task="use default")
    assert session["account_id"] == account["id"]


def test_unknown_door_refuses(tmp_path):
    store, project_id = _store(tmp_path)
    with pytest.raises(Refuse):
        open_session(store, project_id=project_id, door="not-a-door", task="x")


def test_unverified_title_does_not_record_history(tmp_path):
    store, project_id = _store(tmp_path)
    session = open_session(store, project_id=project_id, door="opencode", task="rename")
    original = session["title"]
    held = set_title(store, session["id"], "editing auth", evidence=None)
    assert held["title"] == original
    assert held["verified_title"] == original
    assert held["reported_title"] == "editing auth"
    assert list_titles(store, session["id"]) == []


def test_verified_title_change_records_one_row(tmp_path):
    store, project_id = _store(tmp_path)
    session = open_session(store, project_id=project_id, door="opencode", task="rename")
    evidence = {"source": "stdout", "observed": "editing auth"}
    moved = set_title(store, session["id"], "editing auth", evidence=evidence)
    assert moved["title"] == "editing auth"
    assert moved["verified_title"] == "editing auth"
    rows = list_titles(store, session["id"])
    assert len(rows) == 1
    assert rows[0]["session_id"] == session["id"]
    assert rows[0]["title"] == "editing auth"
    assert rows[0]["id"].startswith("ttl-")
    assert rows[0]["_verdict"] == "VERIFIED"


def test_same_verified_title_does_not_add_a_second_row(tmp_path):
    store, project_id = _store(tmp_path)
    session = open_session(store, project_id=project_id, door="opencode", task="rename")
    evidence = {"source": "stdout", "observed": "editing auth"}
    set_title(store, session["id"], "editing auth", evidence=evidence)
    set_title(store, session["id"], "editing auth", evidence=evidence)
    rows = list_titles(store, session["id"])
    assert len(rows) == 1
    assert rows[0]["title"] == "editing auth"


def test_list_titles_is_seq_order(tmp_path):
    store, project_id = _store(tmp_path)
    session = open_session(store, project_id=project_id, door="codex", task="one")
    other = open_session(store, project_id=project_id, door="pi", task="two")
    set_title(
        store,
        session["id"],
        "alpha",
        evidence={"source": "stdout", "observed": "alpha"},
    )
    set_title(
        store,
        other["id"],
        "other title",
        evidence={"source": "stdout", "observed": "other title"},
    )
    set_title(
        store,
        session["id"],
        "beta",
        evidence={"source": "stdout", "observed": "beta"},
    )
    rows = list_titles(store, session["id"])
    assert [row["title"] for row in rows] == ["alpha", "beta"]
    assert rows[0]["_seq"] < rows[1]["_seq"]
    other_rows = list_titles(store, other["id"])
    assert [row["title"] for row in other_rows] == ["other title"]
    with pytest.raises(Refuse) as refused:
        list_titles(store, "ses-missing")
    assert refused.value.code == "SESSION"
    assert refused.value.detail == "ses-missing"
