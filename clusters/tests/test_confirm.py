"""A git confirm stores an outside read. It does not run git or push."""

from __future__ import annotations

import pytest

from clusters.confirm import record_confirm
from clusters.mesh import create_project
from clusters.refuse import Refuse
from clusters.sessions import open_session
from clusters.store import Store


def _open(tmp_path):
    store = Store(tmp_path / "c")
    project = create_project(store, name="web", root=str(tmp_path / "web"))
    session = open_session(store, project_id=project["id"], door="codex", task="look")
    return store, session["id"]


def test_missing_session_refuses(tmp_path):
    store, _session_id = _open(tmp_path)
    with pytest.raises(Refuse) as refused:
        record_confirm(store, session_id="ses-missing", branch="topic", clean=True)
    assert refused.value.code == "SESSION"
    assert refused.value.detail == "ses-missing"
    assert store.fold("git_confirm") == []


def test_newline_branch_refuses(tmp_path):
    store, session_id = _open(tmp_path)
    with pytest.raises(Refuse) as refused:
        record_confirm(store, session_id=session_id, branch="topic\nmain", clean=True)
    assert refused.value.code == "BRANCH"
    assert store.fold("git_confirm") == []


def test_branch_length_bounds(tmp_path):
    store, session_id = _open(tmp_path)
    with pytest.raises(Refuse) as refused:
        record_confirm(store, session_id=session_id, branch="", clean=True)
    assert refused.value.code == "BRANCH"
    long_name = "b" * 121
    with pytest.raises(Refuse) as refused:
        record_confirm(store, session_id=session_id, branch=long_name, clean=True)
    assert refused.value.code == "BRANCH"
    held = record_confirm(
        store,
        session_id=session_id,
        branch="b" * 120,
        clean=True,
        evidence=None,
    )
    assert held["confirmed"] is False
    assert held["executed"] is False
    assert store.fold("git_confirm")[-1]["body"]["branch"] == "b" * 120


@pytest.mark.parametrize("clean", [0, 1, "true", None])
def test_non_bool_clean_refuses(tmp_path, clean):
    store, session_id = _open(tmp_path)
    with pytest.raises(Refuse) as refused:
        record_confirm(store, session_id=session_id, branch="topic", clean=clean)
    assert refused.value.code == "CLEAN"
    assert store.fold("git_confirm") == []


@pytest.mark.parametrize(
    "evidence",
    [None, {}, {"source": "git status"}, {"observed": "topic"}, {"source": "  ", "observed": "topic"}],
)
def test_unmeasured_evidence_leaves_confirmed_false(tmp_path, evidence):
    store, session_id = _open(tmp_path)
    row = record_confirm(
        store,
        session_id=session_id,
        branch="topic",
        clean=True,
        evidence=evidence,
    )
    assert row["summary"] == "topic clean"
    assert row["confirmed"] is False
    assert row["verdict"] == "UNMEASURED"
    assert row["executed"] is False
    stored = store.fold("git_confirm")[-1]
    assert stored["kind"] == "git_confirm"
    assert stored["claim"] == "git-read"
    assert stored["verdict"] == "UNMEASURED"
    assert stored["body"]["confirmed"] is False
    assert stored["body"]["executed"] is False
    assert stored["body"]["clean"] is True
    assert str(stored["body"]["id"]).startswith("gcf-")


def test_source_and_observed_confirm_without_push(tmp_path):
    store, session_id = _open(tmp_path)
    row = record_confirm(
        store,
        session_id=session_id,
        branch="main",
        clean=False,
        evidence={"source": "git status", "observed": "main dirty"},
    )
    assert row == {
        "summary": "main dirty",
        "confirmed": True,
        "verdict": "VERIFIED",
        "executed": False,
    }
    stored = store.fold("git_confirm")[-1]
    assert stored["claim"] == "git-read"
    assert stored["verdict"] == "VERIFIED"
    assert stored["body"]["branch"] == "main"
    assert stored["body"]["clean"] is False
    assert stored["body"]["confirmed"] is True
    assert stored["body"]["executed"] is False
    assert stored["body"]["session_id"] == session_id
    assert str(stored["body"]["id"]).startswith("gcf-")
    assert store.fold("push_intent") == []
