"""Turbo permission matrix. Category allow does not lift a hard refusal."""

from __future__ import annotations

import pytest

from clusters.perms import decide, set_matrix
from clusters.refuse import Refuse
from clusters.store import Store


def test_set_matrix_rejects_yolo(tmp_path):
    store = Store(tmp_path / "p")
    with pytest.raises(Refuse) as raised:
        set_matrix(store, file="yolo")
    assert raised.value.code == "MATRIX"


def test_file_allow_does_not_override_destructive(tmp_path):
    store = Store(tmp_path / "p")
    set_matrix(store, file="allow")
    result = decide(store, category="file", command="rm -rf /tmp/x")
    assert result["decision"] == "refuse"
    assert result["code"] == "DESTRUCTIVE"


def test_force_push_refuses_when_git_allow_and_turbo(tmp_path):
    store = Store(tmp_path / "p")
    set_matrix(store, git="allow")
    result = decide(
        store,
        category="git",
        command="git push --force origin feature",
        turbo=True,
    )
    assert result["decision"] == "refuse"
    assert result["code"] == "FORCE_PUSH"


def test_merge_refuses(tmp_path):
    store = Store(tmp_path / "p")
    result = decide(store, category="git", command="git merge feature")
    assert result["decision"] == "refuse"
    assert result["code"] == "MERGE"


def test_branch_delete_refuses(tmp_path):
    store = Store(tmp_path / "p")
    result = decide(store, category="git", command="git branch -D old")
    assert result["decision"] == "refuse"
    assert result["code"] == "BRANCH_DELETE"


def test_shell_allow_pytest(tmp_path):
    store = Store(tmp_path / "p")
    set_matrix(store, shell="allow")
    result = decide(store, category="shell", command="pytest -q")
    assert result["decision"] == "allow"
    assert result["code"] == "OK"


def test_shell_without_matrix_asks(tmp_path):
    store = Store(tmp_path / "p")
    result = decide(store, category="shell", command="pytest -q")
    assert result["decision"] == "needs_approval"
    assert result["code"] == "ASK"


def test_network_deny_curl(tmp_path):
    store = Store(tmp_path / "p")
    set_matrix(store, network="deny")
    result = decide(store, category="network", command="curl https://example.com")
    assert result["decision"] == "refuse"
    assert result["code"] == "DENY"
