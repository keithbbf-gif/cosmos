"""Git guards stay refused. A review bundle is not a pull request."""

from __future__ import annotations

import pytest

from clusters.changes import list_changes, record_change
from clusters.gitx import classify, propose_message, propose_review
from clusters.mesh import create_project
from clusters.refuse import Refuse
from clusters.sessions import open_session
from clusters.store import Store


def _open(tmp_path):
    store = Store(tmp_path / "c")
    project = create_project(store, name="web", root=str(tmp_path / "web"))
    session = open_session(store, project_id=project["id"], door="codex", task="edit")
    return store, session["id"]


def _change(store, session_id: str, path: str) -> None:
    record_change(
        store,
        session_id=session_id,
        path=path,
        before="old",
        after="new",
        diff="+new",
    )


def test_classify_force_push_is_refused():
    assert classify("git push --force origin x") == {"op": "force_push", "refused": True}


def test_classify_status_is_read():
    assert classify("git status") == {"op": "read", "refused": False}


@pytest.mark.parametrize(
    "command,op,refused",
    [
        ("git push -f origin x", "force_push", True),
        ("git push origin x", "push", True),
        ("git push --force-with-lease origin x", "push", True),
        ("git branch -d topic", "branch_delete", True),
        ("git branch -D topic", "branch_delete", True),
        ("git merge topic", "merge", True),
        ("git diff", "read", False),
        ("git log", "read", False),
        ("git log -f", "read", False),
        ("git rev-parse HEAD", "read", False),
        ("git commit -m note", "other", False),
    ],
)
def test_classify_turbo_guards(command, op, refused):
    assert classify(command) == {"op": op, "refused": refused}


def test_propose_message_without_evidence_uses_diff(tmp_path):
    store, session_id = _open(tmp_path)
    path = "src/a.py"
    _change(store, session_id, path)
    listed = list_changes(store, session_id)
    row = propose_message(store, session_id=session_id)
    assert row["source"] == "diff"
    assert row["committed"] is False
    assert row["executed"] is False
    assert row["verdict"] == "UNMEASURED"
    assert path in row["files"]
    assert row["files"] == [path]
    assert row["summary"] == f"Review 1 file(s) {path} {listed[0]['after_hash']}"
    stored = store.fold("commit_text")
    assert stored[-1]["body"]["executed"] is False
    assert stored[-1]["body"]["committed"] is False
    assert stored[-1]["body"]["style"] == "detailed"
    assert stored[-1]["body"]["id"].startswith("ctx-")


def test_propose_message_concise_is_subject_only(tmp_path):
    store, session_id = _open(tmp_path)
    _change(store, session_id, "src/a.py")
    _change(store, session_id, "src/b.py")
    listed = list_changes(store, session_id)
    row = propose_message(store, session_id=session_id, style="concise")
    assert row["summary"] == "Review 2 file(s)"
    assert row["files"] == [item["path"] for item in listed]
    assert row["source"] == "diff"
    assert row["style"] == "concise"
    assert row["executed"] is False
    assert row["committed"] is False
    assert row["verdict"] == "UNMEASURED"
    for item in listed:
        assert item["path"] not in row["summary"]
        assert item["after_hash"] not in row["summary"]
    stored = store.fold("commit_text")
    body = stored[-1]["body"]
    assert body["summary"] == "Review 2 file(s)"
    assert body["style"] == "concise"
    assert body["files"] == row["files"]
    assert body["executed"] is False
    assert body["committed"] is False


def test_propose_message_unknown_style(tmp_path):
    store, session_id = _open(tmp_path)
    _change(store, session_id, "src/a.py")
    with pytest.raises(Refuse) as refused:
        propose_message(store, session_id=session_id, style="terse")
    assert refused.value.code == "STYLE"
    assert refused.value.detail == "terse"
    assert store.fold("commit_text") == []


def test_propose_message_verified_uses_observed(tmp_path):
    store, session_id = _open(tmp_path)
    _change(store, session_id, "src/a.py")
    observed = "Ship the new text"
    row = propose_message(
        store,
        session_id=session_id,
        evidence={"source": "codex", "observed": observed},
    )
    assert row["summary"] == observed
    assert row["source"] == "model"
    assert row["verdict"] == "VERIFIED"
    assert row["committed"] is False
    assert row["executed"] is False
    assert row["files"] == ["src/a.py"]
    assert store.fold("commit_text")[-1]["body"]["style"] == "detailed"


def test_propose_message_concise_verified_keeps_observed(tmp_path):
    store, session_id = _open(tmp_path)
    _change(store, session_id, "src/a.py")
    observed = "Ship the new text"
    row = propose_message(
        store,
        session_id=session_id,
        evidence={"source": "codex", "observed": observed},
        style="concise",
    )
    assert row["summary"] == observed
    assert row["source"] == "model"
    assert row["style"] == "concise"
    assert row["verdict"] == "VERIFIED"
    assert row["committed"] is False
    assert row["executed"] is False
    assert row["files"] == ["src/a.py"]
    body = store.fold("commit_text")[-1]["body"]
    assert body["summary"] == observed
    assert body["style"] == "concise"
    assert body["files"] == ["src/a.py"]
    assert body["committed"] is False
    assert body["executed"] is False


def test_propose_message_missing_session(tmp_path):
    store = Store(tmp_path / "c")
    with pytest.raises(Refuse) as refused:
        propose_message(store, session_id="ses-missing")
    assert refused.value.code == "SESSION"


def test_propose_review_is_not_a_pull_request(tmp_path):
    store, session_id = _open(tmp_path)
    row = propose_review(store, session_id=session_id, summary="Review the edit")
    assert row["pr"] is False
    assert row["pushed"] is False
    assert row["executed"] is False
    assert row["id"].startswith("rev-")
    stored = store.fold("review")
    assert stored[-1]["body"]["pr"] is False
    assert stored[-1]["body"]["pushed"] is False
    assert stored[-1]["body"]["executed"] is False


def test_propose_review_blank_summary(tmp_path):
    store, session_id = _open(tmp_path)
    with pytest.raises(Refuse) as refused:
        propose_review(store, session_id=session_id, summary=" ")
    assert refused.value.code == "SUMMARY"
