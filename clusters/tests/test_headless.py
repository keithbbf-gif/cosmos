"""Headless intent is stored on a seat. grok.exe does not start.

Python 3.11. create_project and open_session make the seat. A plan stores
the format, turn cap, and sandbox. It does not run grok -p.
"""

from __future__ import annotations

import pytest

from clusters.headless import FORMATS, get_headless, plan_headless
from clusters.mesh import create_project
from clusters.refuse import Refuse
from clusters.sessions import open_session
from clusters.store import Store


def _open(tmp_path):
    store = Store(tmp_path / "s")
    project = create_project(store, name="web", root=str(tmp_path / "web"))
    session = open_session(store, project_id=project["id"], door="grok", task="headless")
    return store, session


def test_formats():
    assert FORMATS == ("plain", "json", "streaming-json")


def test_json_format_started_false(tmp_path):
    # grok.exe does not start. The plan is stored and not executed.
    store, session = _open(tmp_path)
    saved = plan_headless(
        store,
        session_id=session["id"],
        output_format="json",
    )
    assert saved["id"] == f"headless-{session['id']}"
    assert saved["session_id"] == session["id"]
    assert saved["output_format"] == "json"
    assert saved["max_turns"] == 1
    assert saved["sandbox"] == ""
    assert saved["executed"] is False
    assert saved["started"] is False
    assert saved["_verdict"] == "RECORDED"
    again = get_headless(store, session["id"])
    assert again["output_format"] == "json"
    assert again["max_turns"] == 1
    assert again["started"] is False
    assert again["executed"] is False
    event = store.fold("headless")[-1]
    assert event["kind"] == "headless"
    assert event["body"] == {
        "id": f"headless-{session['id']}",
        "session_id": session["id"],
        "output_format": "json",
        "max_turns": 1,
        "sandbox": "",
        "executed": False,
        "started": False,
    }
    assert "api_key" not in event["body"]
    assert "token" not in event["body"]
    assert "command" not in event["body"]
    assert "--dangerously-skip-permissions" not in event["body"].values()
    assert "--full-auto" not in event["body"].values()
    wide = "w" * 80
    edged = plan_headless(
        store,
        session_id=session["id"],
        output_format="streaming-json",
        max_turns=50,
        sandbox=wide,
    )
    assert edged["output_format"] == "streaming-json"
    assert edged["max_turns"] == 50
    assert edged["sandbox"] == wide
    assert edged["started"] is False
    assert edged["executed"] is False
    assert get_headless(store, session["id"])["started"] is False


def test_max_turns_zero_refused(tmp_path):
    store, session = _open(tmp_path)
    with pytest.raises(Refuse) as refused:
        plan_headless(store, session_id=session["id"], output_format="json", max_turns=0)
    assert refused.value.code == "TURNS"
    assert refused.value.detail == ""
    assert store.fold("headless") == []
    assert store.view("headless") == {}


@pytest.mark.parametrize("turns", [True, False, 51, -1, 1.0, "1"])
def test_bad_turns_refuse(tmp_path, turns):
    store, session = _open(tmp_path)
    with pytest.raises(Refuse) as refused:
        plan_headless(store, session_id=session["id"], max_turns=turns)
    assert refused.value.code == "TURNS"
    assert store.fold("headless") == []


def test_bad_format_and_sandbox_refuse(tmp_path):
    store, session = _open(tmp_path)
    with pytest.raises(Refuse) as refused:
        plan_headless(store, session_id=session["id"], output_format="yaml")
    assert refused.value.code == "FORMAT"
    assert refused.value.detail == ""
    with pytest.raises(Refuse) as broken:
        plan_headless(store, session_id=session["id"], sandbox="work\nspace")
    assert broken.value.code == "SANDBOX"
    with pytest.raises(Refuse) as long:
        plan_headless(store, session_id=session["id"], sandbox="w" * 81)
    assert long.value.code == "SANDBOX"
    with pytest.raises(Refuse) as flagged:
        plan_headless(store, session_id=session["id"], sandbox="--full-auto")
    assert flagged.value.code == "SANDBOX"
    with pytest.raises(Refuse) as skip:
        plan_headless(
            store,
            session_id=session["id"],
            sandbox="--dangerously-skip-permissions",
        )
    assert skip.value.code == "SANDBOX"
    assert store.fold("headless") == []
    plain = plan_headless(store, session_id=session["id"], sandbox="workspace-write")
    assert plain["output_format"] == "plain"
    assert plain["sandbox"] == "workspace-write"
    assert plain["started"] is False
    assert plain["executed"] is False


def test_secret_and_command_are_not_parameters(tmp_path):
    store, session = _open(tmp_path)
    with pytest.raises(TypeError):
        plan_headless(store, session_id=session["id"], api_key="present")
    with pytest.raises(TypeError):
        plan_headless(store, session_id=session["id"], token="present")
    with pytest.raises(TypeError):
        plan_headless(store, session_id=session["id"], command="grok -p")
    assert store.fold("headless") == []


def test_read_forces_started_and_executed_false(tmp_path):
    store, session = _open(tmp_path)
    saved = plan_headless(
        store,
        session_id=session["id"],
        output_format="json",
        max_turns=2,
        sandbox="workspace-write",
    )
    assert saved["started"] is False
    assert saved["executed"] is False
    # grok.exe does not start. A later fold may say otherwise. The read does not.
    store.append(
        "headless",
        {
            "id": f"headless-{session['id']}",
            "started": True,
            "executed": True,
            "command": "grok -p",
            "api_key": "",
            "token": "",
        },
    )
    again = get_headless(store, session["id"])
    assert again["started"] is False
    assert again["executed"] is False
    assert again["output_format"] == "json"
    assert again["max_turns"] == 2
    assert again["sandbox"] == "workspace-write"
    assert "command" not in again
    assert "api_key" not in again
    assert "token" not in again
    assert store.fold("headless")[-1]["body"]["started"] is True
    assert store.fold("headless")[-1]["body"]["executed"] is True


def test_missing_session_and_missing_row(tmp_path):
    store = Store(tmp_path / "s")
    with pytest.raises(Refuse) as refused:
        plan_headless(store, session_id="ses-missing", output_format="json")
    assert refused.value.code == "SESSION"
    assert refused.value.detail == "ses-missing"
    with pytest.raises(Refuse) as missing_get:
        get_headless(store, "ses-missing")
    assert missing_get.value.code == "SESSION"
    assert missing_get.value.detail == ""
    _store, session = _open(tmp_path)
    with pytest.raises(Refuse) as missing_row:
        get_headless(_store, session["id"])
    assert missing_row.value.code == "HEADLESS"
    assert missing_row.value.detail == "missing"
    assert _store.fold("headless") == []
