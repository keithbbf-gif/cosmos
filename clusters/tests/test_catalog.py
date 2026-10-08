"""Doors, accounts, MCP flags, pairing, and notes."""

from __future__ import annotations

import hashlib

import pytest

from clusters.catalog import (
    add_account,
    add_shortcut,
    bind_account,
    emit,
    enable_all_mcp,
    list_doors,
    list_mcp,
    list_notes,
    list_shortcuts,
    mobile_message,
    pair_mobile,
    see,
    set_desktop,
)
from clusters.mesh import create_project
from clusters.refuse import Refuse, scrub
from clusters.sessions import open_session, set_status
from clusters.store import Store


def _store(tmp_path):
    store = Store(tmp_path / "c")
    project = create_project(store, name="web", root=str(tmp_path / "web"))
    return store, project["id"]


def test_list_doors_marks_codex_grok_and_kimi():
    doors = {row["id"]: row for row in list_doors()}
    assert doors["codex"]["seated"] is True
    assert doors["grok"]["executable"] is False
    assert doors["kimi"]["seated"] is False


def test_add_account_refuses_kimi_and_secrets(tmp_path):
    store = Store(tmp_path / "c")
    profile = str(tmp_path / "profiles" / "claude")
    with pytest.raises(Refuse) as kimi:
        add_account(store, provider="kimi", label="kimi", profile_dir=profile)
    assert kimi.value.code == "PROVIDER"
    with pytest.raises(Refuse) as secret:
        scrub({"token": "abc"})
    assert secret.value.code == "SECRET"
    with pytest.raises(Refuse) as passed:
        add_account(
            store,
            provider="claude",
            label="home",
            profile_dir=profile,
            token="abc",
        )
    assert passed.value.code == "SECRET"
    row = add_account(store, provider="claude", label="home", profile_dir=profile)
    assert row["provider"] == "claude"
    assert row["is_default"] is True
    assert "token" not in row
    second = add_account(store, provider="claude", label="other", profile_dir=profile)
    assert second["is_default"] is False
    assert "token" not in second


def test_bind_account_refuses_while_working(tmp_path):
    store, project_id = _store(tmp_path)
    profile = str(tmp_path / "profiles" / "codex")
    claude = add_account(store, provider="claude", label="c", profile_dir=profile)
    codex = add_account(store, provider="codex", label="x", profile_dir=profile)
    session = open_session(store, project_id=project_id, door="codex", task="edit")
    with pytest.raises(Refuse) as mismatch:
        bind_account(store, session["id"], claude["id"])
    assert mismatch.value.code == "PROVIDER"
    bound = bind_account(store, session["id"], codex["id"])
    assert bound["account_id"] == codex["id"]
    set_status(
        store,
        session["id"],
        "working",
        evidence={"source": "door", "observed": "turn 1"},
    )
    with pytest.raises(Refuse) as refused:
        bind_account(store, session["id"], codex["id"])
    assert refused.value.code == "ACCOUNT_SWITCH"


def test_enable_all_mcp_enables_notion_and_playwright(tmp_path):
    store, project_id = _store(tmp_path)
    before = {row["id"]: row["enabled"] for row in list_mcp(store, project_id)}
    assert before["notion"] is False
    assert before["playwright"] is False
    enabled = enable_all_mcp(store, project_id=project_id)
    assert "notion" in enabled["enabled"]
    assert "playwright" in enabled["enabled"]
    after = {row["id"]: row["enabled"] for row in list_mcp(store, project_id)}
    assert after["notion"] is True
    assert after["playwright"] is True


def test_agent_shortcuts_have_no_numeric_cap(tmp_path):
    store = Store(tmp_path / "c")
    for index in range(7):
        add_shortcut(store, kind="agent", binding=f"a{index}", target=f"agent-{index}")
    assert len(list_shortcuts(store)) == 7
    with pytest.raises(Refuse) as refused:
        add_shortcut(store, kind="project", binding="1", target="web")
    assert refused.value.code == "SHORTCUT"


def test_pair_token_is_not_in_the_jsonl(tmp_path):
    store = Store(tmp_path / "c")
    paired = pair_mobile(store)
    text = store.path.read_text(encoding="utf-8")
    digest = hashlib.sha256(paired["token"].encode()).hexdigest()
    assert paired["token"] not in text
    assert "token_hash" in text
    assert digest in text


def test_mobile_message_offline_then_accepts_and_rejects_bad_token(tmp_path):
    store, project_id = _store(tmp_path)
    session = open_session(store, project_id=project_id, door="codex", task="ping")
    paired = pair_mobile(store)
    with pytest.raises(Refuse) as offline:
        mobile_message(
            store,
            token=paired["token"],
            session_id=session["id"],
            body="hello",
        )
    assert offline.value.code == "OFFLINE"
    assert set_desktop(store, online=True) == {"online": True}
    accepted = mobile_message(
        store,
        token=paired["token"],
        session_id=session["id"],
        body="hello",
    )
    assert accepted == {"accepted": True, "session_id": session["id"]}
    with pytest.raises(Refuse) as bad:
        mobile_message(
            store,
            token="0" * 32,
            session_id=session["id"],
            body="hello",
        )
    assert bad.value.code == "PAIR"
    text = store.path.read_text(encoding="utf-8")
    assert paired["token"] not in text


def test_emit_needs_input_then_see_flips_seen(tmp_path):
    store, project_id = _store(tmp_path)
    session = open_session(store, project_id=project_id, door="codex", task="ask")
    note = emit(store, session_id=session["id"], kind="needs_input", detail="which file")
    assert note["note"] == "needs_input"
    assert note["seen"] is False
    assert note["id"] in {row["id"] for row in list_notes(store, unseen_only=True)}
    flipped = see(store, note["id"])
    assert flipped["seen"] is True
    assert flipped["note"] == "needs_input"
    assert note["id"] not in {row["id"] for row in list_notes(store, unseen_only=True)}
    with pytest.raises(Refuse) as missing:
        see(store, "ntf-missing")
    assert missing.value.code == "NOTE"
