"""Room mode, cancel intent, mobile follow, and keyboard seeds."""

from __future__ import annotations

import pytest

from clusters.catalog import list_shortcuts, pair_mobile, set_desktop
from clusters.mesh import create_project
from clusters.refuse import Refuse
from clusters.room import cancel, follow, seed_keys, set_mode
from clusters.sessions import get_session, open_session
from clusters.store import Store


def _store(tmp_path):
    store = Store(tmp_path / "c")
    project = create_project(store, name="web", root=str(tmp_path / "repo"))
    return store, project["id"]


def test_cursor_agent_accepts_plan_and_refuses_yolo(tmp_path):
    store, project_id = _store(tmp_path)
    session = open_session(store, project_id=project_id, door="cursor-agent", task="plan")
    shown = set_mode(store, session["id"], "plan")
    assert shown["mode"] == "plan"
    assert shown["id"] == session["id"]
    with pytest.raises(Refuse) as refused:
        set_mode(store, session["id"], "yolo")
    assert refused.value.code == "MODE"
    assert get_session(store, session["id"])["mode"] == "plan"


def test_cosmos_code_accepts_default_and_refuses_plan(tmp_path):
    store, project_id = _store(tmp_path)
    session = open_session(store, project_id=project_id, door="cosmos-code", task="rail")
    shown = set_mode(store, session["id"], "default")
    assert shown["mode"] == "default"
    with pytest.raises(Refuse) as refused:
        set_mode(store, session["id"], "plan")
    assert refused.value.code == "MODE"
    assert get_session(store, session["id"])["mode"] == "default"


def test_cancel_records_intent_and_does_not_execute(tmp_path):
    store, project_id = _store(tmp_path)
    session = open_session(store, project_id=project_id, door="cursor-agent", task="stop")
    result = cancel(store, session["id"])
    assert result["killed"] is False
    assert result["executed"] is False
    row_id = f"cancel-{session['id']}"
    assert store.view("cancel")[row_id]["executed"] is False
    assert store.view("cancel")[row_id]["executed"] is False
    assert store.view("cancel")[row_id]["killed"] is False


def test_follow_before_desktop_online_refuses(tmp_path):
    store, project_id = _store(tmp_path)
    open_session(store, project_id=project_id, door="cosmos-code", task="wait")
    paired = pair_mobile(store)
    with pytest.raises(Refuse) as refused:
        follow(store, token=paired["token"])
    assert refused.value.code == "OFFLINE"


def test_follow_returns_open_session_and_keeps_token_out_of_jsonl(tmp_path):
    store, project_id = _store(tmp_path)
    session = open_session(store, project_id=project_id, door="cursor-agent", task="watch")
    paired = pair_mobile(store)
    assert set_desktop(store, online=True) == {"online": True}
    found = follow(store, token=paired["token"])
    assert any(
        row["id"] == session["id"] and row["open"] is True for row in found["sessions"]
    )
    for row in found["sessions"]:
        assert "token" not in row
        assert "api_key" not in row
    text = store.path.read_text(encoding="utf-8")
    assert paired["token"] not in text


def test_seed_keys_twice_adds_four_then_zero(tmp_path):
    store, _project_id = _store(tmp_path)
    first = seed_keys(store)
    assert first["seeded"] == 4
    second = seed_keys(store)
    assert second["seeded"] == 0
    keys = [row for row in list_shortcuts(store) if row["kind"] == "key"]
    assert len(keys) == 4
    assert {row["binding"]: row["target"] for row in keys} == {
        "ctrl+n": "new-session",
        "ctrl+k": "search-history",
        "ctrl+b": "task-board",
        "ctrl+shift+t": "turbo",
    }
