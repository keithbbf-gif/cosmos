"""Routine allowlist, extra limits, and hard refusals. Commands are not executed."""

from __future__ import annotations

import pytest

from clusters.policy import check_command, set_limits
from clusters.refuse import Refuse
from clusters.store import Store


def test_git_status_allows_without_turbo(tmp_path):
    store = Store(tmp_path / "p")
    result = check_command(store, command="git status", turbo=False)
    assert result["decision"] == "allow"
    assert result["code"] == "OK"
    padded = check_command(store, command="  git   status  ", turbo=False)
    assert padded["decision"] == "allow"
    assert padded["code"] == "OK"


def test_protected_push_refuses(tmp_path):
    store = Store(tmp_path / "p")
    result = check_command(store, command="git push origin main", turbo=False)
    assert result["decision"] == "refuse"
    assert result["code"] == "PROTECTED"
    forced = check_command(store, command="git push origin main", turbo=True)
    assert forced["decision"] == "refuse"
    assert forced["code"] == "PROTECTED"
    named = check_command(store, command="git push", branch="main", turbo=True)
    assert named["code"] == "PROTECTED"


def test_destructive_refuses_even_with_turbo(tmp_path):
    store = Store(tmp_path / "p")
    result = check_command(store, command="rm -rf /tmp/x", turbo=True)
    assert result["decision"] == "refuse"
    assert result["code"] == "DESTRUCTIVE"


def test_skip_permissions_flag_refuses(tmp_path):
    store = Store(tmp_path / "p")
    result = check_command(store, command="claude --dangerously-skip-permissions", turbo=True)
    assert result["decision"] == "refuse"
    assert result["code"] == "FLAG"
    assert result["detail"] == "--dangerously-skip-permissions"


def test_grok_exe_refuses(tmp_path):
    store = Store(tmp_path / "p")
    result = check_command(store, command="grok.exe --single", turbo=True)
    assert result["decision"] == "refuse"
    assert result["code"] == "FLAG"
    assert result["detail"] == "grok.exe"


@pytest.mark.parametrize(
    "command,detail",
    [
        ("codex --danger-full-access", "--danger-full-access"),
        ("codex --full-auto", "--full-auto"),
        ("claude --ignore-user-config", "--ignore-user-config"),
    ],
)
def test_other_hard_flags_refuse(tmp_path, command, detail):
    store = Store(tmp_path / "p")
    result = check_command(store, command=command, turbo=True)
    assert result["decision"] == "refuse"
    assert result["code"] == "FLAG"
    assert result["detail"] == detail


def test_commit_needs_approval_even_with_turbo(tmp_path):
    store = Store(tmp_path / "p")
    result = check_command(store, command="git commit -am stuff", turbo=True)
    assert result["decision"] == "needs_approval"
    assert result["code"] == "APPROVAL"
    assert result["decision"] != "allow"


def test_extra_deny_curl(tmp_path):
    store = Store(tmp_path / "p")
    saved = set_limits(store, deny=["curl"])
    assert saved == {"allow": [], "deny": ["curl"]}
    result = check_command(store, command="curl https://example.com", turbo=True)
    assert result["decision"] == "refuse"
    assert result["code"] == "DENY"
    assert result["detail"] == "curl"


def test_extra_allow_echo(tmp_path):
    store = Store(tmp_path / "p")
    saved = set_limits(store, allow=["echo"])
    assert saved == {"allow": ["echo"], "deny": []}
    result = check_command(store, command="echo hello", turbo=False)
    assert result["decision"] == "allow"
    assert result["code"] == "OK"


def test_live_tree_refuses(tmp_path):
    store = Store(tmp_path / "p")
    cosmos = check_command(store, command=r"type V:\A\Ai\COSMOS\live\state", turbo=True)
    assert cosmos["decision"] == "refuse"
    assert cosmos["code"] == "LIVE_TREE"
    slash = check_command(store, command="rg needle cosmos/live/notes")
    assert slash["code"] == "LIVE_TREE"
    ended = check_command(store, command="cat /var/data/live", turbo=True)
    assert ended["decision"] == "refuse"
    assert ended["code"] == "LIVE_TREE"
    word = check_command(store, command="git log --grep live")
    assert word["decision"] == "allow"


def test_shell_chain_is_not_an_allowlist_hit(tmp_path):
    store = Store(tmp_path / "p")
    for command in (
        "git status && echo ok",
        "git status || echo ok",
        "git status; echo ok",
        "git status | echo ok",
        "git status & echo ok",
        "git status `echo ok`",
        "git status $(echo ok)",
    ):
        result = check_command(store, command=command, turbo=True)
        assert result["decision"] == "needs_approval"
        assert result["code"] == "APPROVAL"
        assert result["detail"] == "shell chain"
    destructive = check_command(store, command="git status && rm -rf /tmp/x", turbo=True)
    assert destructive["code"] == "DESTRUCTIVE"
    set_limits(store, deny=["curl"])
    curl = check_command(store, command="pytest && curl https://example.com", turbo=True)
    assert curl["code"] == "DENY"
    assert curl["detail"] == "curl"
    # Deny matches the substring del, including inside a later token such as model.
    set_limits(store, deny=["del"])
    substring = check_command(store, command="git status && echo model", turbo=True)
    assert substring["code"] == "DENY"
    assert substring["detail"] == "del"
    assert check_command(store, command="git status", turbo=False)["code"] == "OK"


def test_protected_push_dash_c_and_refspec(tmp_path):
    store = Store(tmp_path / "p")
    refused = (
        "git -C repo push origin main",
        "git push origin HEAD:main",
        "git push origin refs/heads/main",
        "git push origin refs/heads/master",
    )
    for command in refused:
        result = check_command(store, command=command, turbo=True)
        assert result["decision"] == "refuse"
        assert result["code"] == "PROTECTED"
    feature = check_command(store, command="git -C repo push origin feature", turbo=True)
    assert feature["code"] == "APPROVAL"
    message = check_command(store, command="git commit -m git push origin main", turbo=True)
    assert message["code"] == "APPROVAL"


def test_live_segment_refuses_children(tmp_path):
    store = Store(tmp_path / "p")
    child = check_command(store, command=r"type live\state", turbo=True)
    assert child["code"] == "LIVE_TREE"
    nested = check_command(store, command="rg needle work/live/notes")
    assert nested["code"] == "LIVE_TREE"
    ledger = check_command(store, command="type live/ledger")
    assert ledger["code"] == "LIVE_TREE"
    assert check_command(store, command="git log --grep live")["code"] == "OK"


def test_limits_reject_newline_and_non_string(tmp_path):
    store = Store(tmp_path / "p")
    with pytest.raises(Refuse) as newline:
        set_limits(store, deny=["curl\nhttp"])
    assert newline.value.code == "LIMIT"
    with pytest.raises(Refuse) as bad_type:
        set_limits(store, allow=["echo", 1])  # type: ignore[list-item]
    assert bad_type.value.code == "LIMIT"
