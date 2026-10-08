"""Host notes. Values are not stored and nothing is probed."""

from __future__ import annotations

import pytest

from clusters.hostnote import FACTS, HOSTS, set_env_name, set_host
from clusters.mesh import create_project
from clusters.refuse import Refuse
from clusters.sessions import open_session
from clusters.store import Store


def _seat(tmp_path):
    store = Store(tmp_path / "s")
    project = create_project(store, name="web", root=str(tmp_path / "web"))
    session = open_session(store, project_id=project["id"], door="codex", task="host")
    return store, session["id"]


def test_host_and_fact_sets():
    assert HOSTS == ("windows", "linux", "mac")
    assert FACTS == ("voice", "sandbox", "git-bash", "plain-shell")


def test_windows_voice_is_a_note_and_is_not_probed(tmp_path):
    # Values are not stored and nothing is probed.
    store, session_id = _seat(tmp_path)
    row = set_host(
        store,
        session_id=session_id,
        host="windows",
        fact="voice",
        enabled=True,
    )
    assert row["id"] == f"host-{session_id}-voice"
    assert row["session_id"] == session_id
    assert row["host"] == "windows"
    assert row["fact"] == "voice"
    assert row["enabled"] is True
    assert row["probed"] is False
    assert row["_verdict"] == "RECORDED"
    event = store.fold("host_note")[-1]
    assert event["kind"] == "host_note"
    assert event["seq"] == row["_seq"]
    assert event["body"] == {
        "id": f"host-{session_id}-voice",
        "session_id": session_id,
        "host": "windows",
        "fact": "voice",
        "enabled": True,
        "probed": False,
    }
    assert "value" not in event["body"]
    again = set_host(
        store,
        session_id=session_id,
        host="windows",
        fact="voice",
        enabled=False,
    )
    assert again["id"] == row["id"]
    assert again["enabled"] is False
    assert again["probed"] is False
    assert store.view("host_note")[row["id"]]["probed"] is False


def test_bad_host_refuses(tmp_path):
    store, session_id = _seat(tmp_path)
    with pytest.raises(Refuse) as refused:
        set_host(
            store,
            session_id=session_id,
            host="bsd",
            fact="voice",
            enabled=True,
        )
    assert refused.value.code == "HOST"
    assert refused.value.detail == ""
    assert store.fold("host_note") == []


def test_bad_fact_and_non_bool_flag_refuse(tmp_path):
    store, session_id = _seat(tmp_path)
    with pytest.raises(Refuse) as refused:
        set_host(
            store,
            session_id=session_id,
            host="linux",
            fact="shell",
            enabled=True,
        )
    assert refused.value.code == "FACT"
    assert refused.value.detail == ""
    with pytest.raises(Refuse) as flagged:
        set_host(
            store,
            session_id=session_id,
            host="mac",
            fact="sandbox",
            enabled=1,
        )
    assert flagged.value.code == "FACT"
    assert flagged.value.detail == "flag"
    assert store.fold("host_note") == []


def test_missing_session_refuses(tmp_path):
    store, _session_id = _seat(tmp_path)
    with pytest.raises(Refuse) as refused:
        set_host(
            store,
            session_id="ses-missing",
            host="windows",
            fact="voice",
            enabled=True,
        )
    assert refused.value.code == "SESSION"
    assert refused.value.detail == "ses-missing"
    with pytest.raises(Refuse) as named:
        set_env_name(store, session_id="ses-missing", name="BASE_URL")
    assert named.value.code == "SESSION"
    assert named.value.detail == "ses-missing"
    assert store.fold("host_note") == []
    assert store.fold("env_name") == []


def test_api_key_name_is_refused(tmp_path):
    store, session_id = _seat(tmp_path)
    with pytest.raises(Refuse) as refused:
        set_env_name(store, session_id=session_id, name="API_KEY")
    assert refused.value.code == "SECRET"
    assert refused.value.detail == "API_KEY"
    assert store.fold("env_name") == []


@pytest.mark.parametrize(
    "name",
    [
        "TOKEN",
        "SECRET",
        "PASSWORD",
        "AUTHORIZATION",
        "CREDENTIAL",
        "ACCESS_TOKEN",
        "REFRESH_TOKEN",
        "MY_TOKEN",
        "MY_SECRET",
        "MY_PASSWORD",
        "MY_API_KEY",
    ],
)
def test_secret_names_and_suffixes_refuse(tmp_path, name):
    store, session_id = _seat(tmp_path)
    with pytest.raises(Refuse) as refused:
        set_env_name(store, session_id=session_id, name=name)
    assert refused.value.code == "SECRET"
    assert refused.value.detail == name
    assert store.fold("env_name") == []


def test_base_url_is_accepted_without_a_value(tmp_path):
    # Values are not stored and nothing is probed.
    store, session_id = _seat(tmp_path)
    with pytest.raises(TypeError):
        set_env_name(
            store,
            session_id=session_id,
            name="BASE_URL",
            value="present-only",
        )
    assert store.fold("env_name") == []
    row = set_env_name(store, session_id=session_id, name="BASE_URL")
    assert row["id"] == f"env-{session_id}-BASE_URL"
    assert row["session_id"] == session_id
    assert row["name"] == "BASE_URL"
    assert row["present"] is True
    assert "value" not in row
    event = store.fold("env_name")[-1]
    assert event["kind"] == "env_name"
    assert event["body"] == {
        "id": f"env-{session_id}-BASE_URL",
        "session_id": session_id,
        "name": "BASE_URL",
        "present": True,
    }
    assert "value" not in event["body"]


def test_env_name_of_eighty_characters_is_kept(tmp_path):
    store, session_id = _seat(tmp_path)
    name = "A" * 80
    row = set_env_name(store, session_id=session_id, name=name)
    assert row["name"] == name
    assert row["present"] is True
    assert "value" not in row
    assert "value" not in store.fold("env_name")[-1]["body"]


@pytest.mark.parametrize(
    "name",
    ["", "a", "base_url", "BASE URL", "BASE_URL\n", "1URL", "_URL", "A" * 81, "BASE-URL"],
)
def test_env_shape_refuses(tmp_path, name):
    store, session_id = _seat(tmp_path)
    with pytest.raises(Refuse) as refused:
        set_env_name(store, session_id=session_id, name=name)
    assert refused.value.code == "ENV"
    assert store.fold("env_name") == []
