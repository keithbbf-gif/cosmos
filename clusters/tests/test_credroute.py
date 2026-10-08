"""Credential routes. A path pointer is stored. Secrets are not stored."""

from __future__ import annotations

import pytest

from clusters.credroute import get_route, set_route
from clusters.mesh import create_project
from clusters.refuse import SECRET_KEYS, Refuse
from clusters.sessions import open_session
from clusters.store import Store


def _seat(tmp_path):
    store = Store(tmp_path / "s")
    project = create_project(store, name="web", root=str(tmp_path / "web"))
    session = open_session(store, project_id=project["id"], door="codex", task="login")
    return store, session["id"]


def test_path_pointer_is_stored_and_not_copied(tmp_path):
    # The path is a pointer. The file is not opened. Secrets are not stored.
    store, session_id = _seat(tmp_path)
    path = str(tmp_path / "cli" / "login.json")
    row = set_route(store, session_id=session_id, route="browser-login", path=path)
    assert row["id"] == f"route-{session_id}"
    assert row["session_id"] == session_id
    assert row["route"] == "browser-login"
    assert row["path"] == path
    assert row["present"] is True
    assert row["copied"] is False
    assert not (tmp_path / "cli" / "login.json").exists()
    got = get_route(store, session_id)
    assert got["path"] == path
    assert got["copied"] is False
    assert got["present"] is True
    body = store.fold("cred_route")[-1]["body"]
    assert body["copied"] is False
    assert body["path"] == path
    assert store.fold("cred_route")[-1]["kind"] == "cred_route"
    for key in SECRET_KEYS:
        assert key not in body
        assert key not in row


@pytest.mark.parametrize("route", ["device-auth", "env-key"])
def test_login_labels_store_a_pointer(tmp_path, route):
    store, session_id = _seat(tmp_path)
    path = str(tmp_path / "cli" / "state.json")
    row = set_route(store, session_id=session_id, route=route, path=path)
    assert row["route"] == route
    assert row["path"] == path
    assert row["copied"] is False
    assert get_route(store, session_id)["copied"] is False


@pytest.mark.parametrize("route", ["KEY=value", "browser-login token=abc", "="])
def test_route_containing_equals_refuses(tmp_path, route):
    store, session_id = _seat(tmp_path)
    path = str(tmp_path / "cli" / "login.json")
    with pytest.raises(Refuse) as refused:
        set_route(store, session_id=session_id, route=route, path=path)
    assert refused.value.code == "SECRET"
    assert refused.value.detail == "route"
    assert store.fold("cred_route") == []
    with pytest.raises(Refuse) as missing:
        get_route(store, session_id)
    assert missing.value.code == "ROUTE"
    assert missing.value.detail == "missing"


def test_live_path_refuses(tmp_path):
    # The live path is only a string. This test does not open it.
    store, session_id = _seat(tmp_path)
    live = r"V:\A\Ai\COSMOS\live\auth.json"
    with pytest.raises(Refuse) as refused:
        set_route(store, session_id=session_id, route="browser-login", path=live)
    assert refused.value.code == "LIVE_TREE"
    assert refused.value.detail == live
    assert store.fold("cred_route") == []


@pytest.mark.parametrize("route", ["", "x" * 81, "browser\nlogin", "device\rauth"])
def test_route_shape_refuses(tmp_path, route):
    store, session_id = _seat(tmp_path)
    with pytest.raises(Refuse) as refused:
        set_route(
            store,
            session_id=session_id,
            route=route,
            path=str(tmp_path / "cli" / "login.json"),
        )
    assert refused.value.code == "ROUTE"
    assert store.fold("cred_route") == []


def test_route_of_eighty_characters_is_kept(tmp_path):
    store, session_id = _seat(tmp_path)
    route = "r" * 80
    path = str(tmp_path / "cli" / "login.json")
    row = set_route(store, session_id=session_id, route=route, path=path)
    assert row["route"] == route
    assert row["copied"] is False


def test_missing_session_refuses(tmp_path):
    store, _session_id = _seat(tmp_path)
    with pytest.raises(Refuse) as refused:
        set_route(
            store,
            session_id="ses-missing",
            route="env-key",
            path=str(tmp_path / "cli" / "login.json"),
        )
    assert refused.value.code == "SESSION"
    assert refused.value.detail == "ses-missing"
    with pytest.raises(Refuse) as missing:
        get_route(store, "ses-missing")
    assert missing.value.code == "SESSION"
    assert missing.value.detail == "ses-missing"
    assert store.fold("cred_route") == []


def test_missing_row_refuses(tmp_path):
    store, session_id = _seat(tmp_path)
    with pytest.raises(Refuse) as refused:
        get_route(store, session_id)
    assert refused.value.code == "ROUTE"
    assert refused.value.detail == "missing"
    assert store.fold("cred_route") == []
