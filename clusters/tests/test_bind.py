"""Seat binding is a stored CLI name and model. This does not launch."""

from __future__ import annotations

import pytest

from clusters.bind import bind_seat, get_binding
from clusters.mesh import create_project
from clusters.models import DOORS
from clusters.refuse import Refuse
from clusters.sessions import open_session
from clusters.store import Store


def _open(tmp_path, door: str = "codex"):
    store = Store(tmp_path / "s")
    project = create_project(store, name="web", root=str(tmp_path / "web"))
    session = open_session(store, project_id=project["id"], door=door, task="bind")
    return store, session


def test_bind_codex_stores_the_model_unstarted(tmp_path):
    store, session = _open(tmp_path)
    row = bind_seat(store, session_id=session["id"], door="codex", model="gpt-5.4")
    assert row["id"] == f"bind-{session['id']}"
    assert row["session_id"] == session["id"]
    assert row["door"] == "codex"
    assert row["model"] == "gpt-5.4"
    assert row["started"] is False
    assert row["installed"] is False
    assert row["executed"] is False
    event = store.fold("binding")[-1]
    assert event["kind"] == "binding"
    assert event["body"]["started"] is False
    again = get_binding(store, session["id"])
    assert again["door"] == "codex"
    assert again["model"] == "gpt-5.4"
    assert again["started"] is False


def test_unknown_door_refuses(tmp_path):
    store, session = _open(tmp_path)
    with pytest.raises(Refuse) as refused:
        bind_seat(store, session_id=session["id"], door="not-a-door", model="gpt")
    assert refused.value.code == "UNKNOWN_DOOR"
    assert refused.value.detail == "not-a-door"
    assert store.view("binding") == {}


def test_grok_door_is_stored_as_a_name_and_stays_unstarted(tmp_path):
    # Door "grok" is in the catalog. This does not launch.
    assert "grok" in DOORS
    store, session = _open(tmp_path, door="grok")
    row = bind_seat(store, session_id=session["id"], door="grok", model="grok-4")
    assert row["door"] == "grok"
    assert row["model"] == "grok-4"
    assert row["started"] is False
    assert row["installed"] is False
    assert row["executed"] is False
    assert get_binding(store, session["id"])["started"] is False


def test_missing_session_refuses(tmp_path):
    store = Store(tmp_path / "s")
    with pytest.raises(Refuse) as refused:
        bind_seat(store, session_id="ses-missing", door="codex", model="gpt")
    assert refused.value.code == "SESSION"
    assert refused.value.detail == "ses-missing"
    with pytest.raises(Refuse) as missing:
        get_binding(store, "ses-missing")
    assert missing.value.code == "SESSION"
    assert missing.value.detail == ""


def test_missing_binding_refuses(tmp_path):
    store, session = _open(tmp_path)
    with pytest.raises(Refuse) as refused:
        get_binding(store, session["id"])
    assert refused.value.code == "BINDING"
    assert refused.value.detail == "missing"


def test_model_must_be_one_line_of_at_most_80(tmp_path):
    store, session = _open(tmp_path)
    for bad in ("", "x" * 81, "gpt\n5", "gpt\r5"):
        with pytest.raises(Refuse) as refused:
            bind_seat(store, session_id=session["id"], door="codex", model=bad)
        assert refused.value.code == "MODEL"
    kept = bind_seat(store, session_id=session["id"], door="codex", model="m" * 80)
    assert kept["model"] == "m" * 80
    assert kept["started"] is False
