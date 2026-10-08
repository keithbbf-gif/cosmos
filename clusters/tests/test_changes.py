"""Change records keep hashes. Git actions stay unexecuted plans."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from clusters.changes import (
    list_changes,
    plan_worktree,
    propose_commit,
    record_change,
    request_push,
)
from clusters.mesh import create_project
from clusters.refuse import Refuse
from clusters.sessions import open_session
from clusters.store import Store


def _open(tmp_path):
    store = Store(tmp_path / "c")
    project = create_project(store, name="web", root=str(tmp_path / "web"))
    session = open_session(store, project_id=project["id"], door="codex", task="edit")
    return store, session["id"]


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_record_change_stores_hashes_not_raw_before(tmp_path):
    store, session_id = _open(tmp_path)
    before = "RAW_BEFORE_BODY_SHOULD_NOT_LAND"
    after = "RAW_AFTER_BODY_SHOULD_NOT_LAND"
    row = record_change(
        store,
        session_id=session_id,
        path=str(tmp_path / "web" / "a.py"),
        before=before,
        after=after,
        diff="@@",
    )
    assert row["before_hash"] == _sha(before)
    assert row["after_hash"] == _sha(after)
    assert row["_verdict"] == "VERIFIED"
    assert "before" not in row
    assert "after" not in row
    raw = store.path.read_text(encoding="utf-8")
    assert before not in raw
    assert after not in raw
    listed = list_changes(store, session_id)
    assert [item["id"] for item in listed] == [row["id"]]


def test_record_change_live_tree_refuses(tmp_path):
    store, session_id = _open(tmp_path)
    with pytest.raises(Refuse) as refused:
        record_change(
            store,
            session_id=session_id,
            path=r"V:\A\Ai\COSMOS\live\x.py",
            before="a",
            after="b",
            diff="d",
        )
    assert refused.value.code == "LIVE_TREE"


def test_missing_session_refuses(tmp_path):
    store = Store(tmp_path / "c")
    with pytest.raises(Refuse) as refused:
        record_change(
            store,
            session_id="ses-missing",
            path="a.py",
            before="a",
            after="b",
            diff="d",
        )
    assert refused.value.code == "SESSION"


def test_plan_worktree_does_not_create_directory(tmp_path):
    store, session_id = _open(tmp_path)
    repo = tmp_path / "repo"
    repo.mkdir()
    row = plan_worktree(store, session_id=session_id, repo=str(repo))
    planned = Path(repo) / ".clusters" / "worktrees" / session_id
    assert Path(row["planned"]) == planned
    assert planned.exists() is False
    assert row["executed"] is False
    assert row["command"] == f'git worktree add "{planned}" HEAD'


def test_propose_commit_lists_files_without_executing(tmp_path):
    store, session_id = _open(tmp_path)
    after = "beta-body"
    record_change(
        store,
        session_id=session_id,
        path="src/a.py",
        before="alpha-body",
        after=after,
        diff="+beta",
    )
    with pytest.raises(Refuse) as refused:
        propose_commit(store, session_id=session_id, summary=" ")
    assert refused.value.code == "SUMMARY"
    proposal = propose_commit(store, session_id=session_id, summary="note the edit")
    assert proposal["executed"] is False
    assert proposal["session_id"] == session_id
    assert proposal["summary"] == "note the edit"
    assert proposal["files"] == ["src/a.py"]
    assert proposal["hashes"] == [_sha(after)]


def test_request_push_main_is_protected(tmp_path):
    store, session_id = _open(tmp_path)
    with pytest.raises(Refuse) as refused:
        request_push(store, session_id=session_id, branch="main", confirmed=True)
    assert refused.value.code == "PROTECTED"


def test_request_push_feature_needs_confirm(tmp_path):
    store, session_id = _open(tmp_path)
    with pytest.raises(Refuse) as refused:
        request_push(store, session_id=session_id, branch="feature/demo", confirmed=False)
    assert refused.value.code == "CONFIRM"


def test_request_push_feature_confirmed_does_not_push(tmp_path):
    store, session_id = _open(tmp_path)
    row = request_push(store, session_id=session_id, branch="feature/demo", confirmed=True)
    assert row["pushed"] is False
    assert row["executed"] is False
    assert row["branch"] == "feature/demo"
