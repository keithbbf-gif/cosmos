"""Seat flags the mode row does not store. Nothing is fetched or written.

Python 3.11. create_project and open_session make the seat. Storing a
channel, a Kimi role, or a lock path does not fetch and does not write
the lock. written stays false.
"""

from __future__ import annotations

import pytest

from clusters.mesh import create_project
from clusters.refuse import Refuse
from clusters.seatflag import CHANNELS, ROLES, get_seat_flags, set_seat_flags
from clusters.sessions import open_session
from clusters.store import Store


def _session(tmp_path, door="kimi"):
    store = Store(tmp_path / "s")
    project = create_project(store, name="web", root=str(tmp_path / "web"))
    session = open_session(store, project_id=project["id"], door=door, task="flags")
    return store, session["id"]


def test_stable_and_coder_stay_unwritten(tmp_path):
    # Nothing is fetched or written. stable and coder are stored names.
    store, session_id = _session(tmp_path)
    saved = set_seat_flags(
        store,
        session_id=session_id,
        channel="stable",
        role="coder",
        tool_search=False,
        web_fetch=False,
        hooks_off=True,
        auto_update=False,
        lock_path="",
    )
    assert saved["id"] == f"flag-{session_id}"
    assert saved["session_id"] == session_id
    assert saved["channel"] == "stable"
    assert saved["role"] == "coder"
    assert saved["tool_search"] is False
    assert saved["web_fetch"] is False
    assert saved["hooks_off"] is True
    assert saved["auto_update"] is False
    assert saved["lock_path"] == ""
    assert saved["written"] is False
    assert saved["fetched"] is False
    shown = get_seat_flags(store, session_id)
    assert shown["channel"] == "stable"
    assert shown["role"] == "coder"
    assert shown["written"] is False
    assert shown["fetched"] is False
    body = store.fold("seat_flag")[-1]["body"]
    assert body["channel"] == "stable"
    assert body["role"] == "coder"
    assert body["written"] is False
    assert body["fetched"] is False
    assert {row["kind"] for row in store.fold()} == {"project", "session", "seat_flag"}


def test_bad_channel_refuses(tmp_path):
    store, session_id = _session(tmp_path)
    assert "nightly" not in CHANNELS
    with pytest.raises(Refuse) as refused:
        set_seat_flags(store, session_id=session_id, channel="nightly", role="coder")
    assert refused.value.code == "CHANNEL"
    assert store.view("seat_flag") == {}


def test_live_lock_path_refuses(tmp_path):
    # Nothing is fetched or written. A live lock path is refused before a row.
    store, session_id = _session(tmp_path)
    path = r"V:\A\Ai\COSMOS\live\update.lock"
    with pytest.raises(Refuse) as refused:
        set_seat_flags(
            store,
            session_id=session_id,
            channel="stable",
            role="coder",
            lock_path=path,
        )
    assert refused.value.code == "LIVE_TREE"
    assert store.view("seat_flag") == {}


def test_written_stays_false_on_read(tmp_path):
    # Nothing is fetched or written. A stored true is forced false on read.
    store, session_id = _session(tmp_path)
    store.append(
        "seat_flag",
        {
            "id": f"flag-{session_id}",
            "session_id": session_id,
            "channel": "stable",
            "role": "coder",
            "tool_search": False,
            "web_fetch": False,
            "hooks_off": False,
            "auto_update": False,
            "lock_path": "",
            "written": True,
            "fetched": True,
        },
    )
    shown = get_seat_flags(store, session_id)
    assert shown["channel"] == "stable"
    assert shown["role"] == "coder"
    assert shown["written"] is False
    assert shown["fetched"] is False


def test_lock_path_is_stored_and_not_opened(tmp_path):
    # Nothing is fetched or written. The path is a name. The file is not created.
    store, session_id = _session(tmp_path)
    path = str(tmp_path / "update.lock")
    saved = set_seat_flags(
        store,
        session_id=session_id,
        channel="latest",
        role="plan",
        lock_path=path,
    )
    assert saved["channel"] == "latest"
    assert saved["role"] == "plan"
    assert saved["lock_path"] == path
    assert saved["written"] is False
    assert saved["fetched"] is False
    assert saved["auto_update"] is False
    assert not (tmp_path / "update.lock").exists()
    assert get_seat_flags(store, session_id)["written"] is False


def test_bad_role_and_non_bool_refuse(tmp_path):
    store, session_id = _session(tmp_path)
    assert "worker" not in ROLES
    with pytest.raises(Refuse) as role:
        set_seat_flags(store, session_id=session_id, role="worker")
    assert role.value.code == "ROLE"
    with pytest.raises(Refuse) as flag:
        set_seat_flags(store, session_id=session_id, tool_search=0)
    assert flag.value.code == "FLAG"
    assert flag.value.detail == ""
    assert store.view("seat_flag") == {}
    kept = set_seat_flags(store, session_id=session_id, role="")
    assert kept["channel"] == "stable"
    assert kept["role"] == ""
    assert kept["written"] is False
    assert kept["fetched"] is False


def test_missing_session_and_missing_row(tmp_path):
    store = Store(tmp_path / "s")
    with pytest.raises(Refuse) as refused:
        set_seat_flags(store, session_id="ses-missing", channel="stable", role="coder")
    assert refused.value.code == "SESSION"
    assert refused.value.detail == "ses-missing"
    project = create_project(store, name="web", root=str(tmp_path / "web"))
    session = open_session(store, project_id=project["id"], door="kimi", task="flags")
    with pytest.raises(Refuse) as missing_session:
        get_seat_flags(store, "ses-missing")
    assert missing_session.value.code == "SESSION"
    assert missing_session.value.detail == ""
    with pytest.raises(Refuse) as missing_row:
        get_seat_flags(store, session["id"])
    assert missing_row.value.code == "FLAG"
    assert missing_row.value.detail == "missing"
