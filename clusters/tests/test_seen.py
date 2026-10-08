"""Review column. An unseen path stays open. This does not commit."""

from __future__ import annotations

import hashlib

import pytest

from clusters.mesh import create_project
from clusters.refuse import Refuse
from clusters.seen import mark_seen, review_paths
from clusters.sessions import open_session
from clusters.store import Store


def _seat(tmp_path):
    store = Store(tmp_path / "s")
    project = create_project(store, name="web", root=str(tmp_path / "web"))
    session = open_session(store, project_id=project["id"], door="codex", task="review")
    return store, session["id"]


def test_missing_session_refuses(tmp_path):
    store, _session_id = _seat(tmp_path)
    with pytest.raises(Refuse) as marked:
        mark_seen(store, session_id="ses-missing", path="src/a.py")
    assert marked.value.code == "SESSION"
    assert marked.value.detail == "ses-missing"
    with pytest.raises(Refuse) as reviewed:
        review_paths(store, "ses-missing")
    assert reviewed.value.code == "SESSION"
    assert reviewed.value.detail == "ses-missing"
    assert store.fold("seen") == []


def test_unseen_path_counts_as_open_until_marked(tmp_path):
    # Marking the path seen drops the open count. It does not commit.
    store, session_id = _seat(tmp_path)
    path = str(tmp_path / "src" / "a.py")
    digest = hashlib.sha256(path.encode()).hexdigest()[:12]
    row_id = f"seen-{session_id}-{digest}"
    assert review_paths(store, session_id) == {
        "session_id": session_id,
        "open": 0,
        "accepted": False,
    }
    unseen = mark_seen(store, session_id=session_id, path=path, seen=False)
    assert unseen["id"] == row_id
    assert unseen["session_id"] == session_id
    assert unseen["path"] == path
    assert unseen["seen"] is False
    assert unseen["accepted"] is False
    opened = review_paths(store, session_id)
    assert opened["open"] == 1
    assert opened["accepted"] is False
    seen = mark_seen(store, session_id=session_id, path=path, seen=True)
    assert seen["id"] == row_id
    assert seen["seen"] is True
    assert seen["accepted"] is False
    dropped = review_paths(store, session_id)
    assert dropped == {"session_id": session_id, "open": 0, "accepted": False}
    stored = store.fold("seen")
    assert [row["kind"] for row in stored] == ["seen", "seen"]
    assert [row["body"]["seen"] for row in stored] == [False, True]
    assert all(row["body"]["accepted"] is False for row in stored)
    assert store.view("task") == {}
    assert store.fold("commit_proposal") == []


def test_live_path_refuses(tmp_path):
    store, session_id = _seat(tmp_path)
    live = r"V:\A\Ai\COSMOS\live\src\a.py"
    with pytest.raises(Refuse) as refused:
        mark_seen(store, session_id=session_id, path=live)
    assert refused.value.code == "LIVE_TREE"
    assert refused.value.detail == live
    assert store.fold("seen") == []
    assert review_paths(store, session_id)["accepted"] is False
    assert review_paths(store, session_id)["open"] == 0


@pytest.mark.parametrize("seen", [0, 1, "true", None])
def test_non_bool_seen_refuses(tmp_path, seen):
    store, session_id = _seat(tmp_path)
    with pytest.raises(Refuse) as refused:
        mark_seen(store, session_id=session_id, path="src/a.py", seen=seen)
    assert refused.value.code == "SEEN"
    assert store.fold("seen") == []
    assert review_paths(store, session_id)["accepted"] is False


def test_dotdot_path_refuses(tmp_path):
    store, session_id = _seat(tmp_path)
    with pytest.raises(Refuse) as refused:
        mark_seen(store, session_id=session_id, path="../secret")
    assert refused.value.code == "PATH"
    assert store.fold("seen") == []
