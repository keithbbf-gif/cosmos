"""Pins for the Core route table and the three day-one gaps."""

from __future__ import annotations

from typing import Literal, cast

from cosmos_federation import ROUTE_CHAT, ROUTE_PAGE, ROUTE_SETUP, Refuse, secret_shape
from routes import SCHEMA, Route, table

_DAY_ONE_WHY = (
    "the chat window and the wizard need this route and Core does not have it yet"
)
_Phase = Literal["EXISTS", "DAY_ONE"]
_Method = Literal["GET", "POST"]


def _by(method: str, path: str) -> Route:
    matches = [row for row in table() if row.method == method and row.path == path]
    assert len(matches) == 1
    return matches[0]


def test_schema_and_table_shape() -> None:
    assert SCHEMA == "cosmos-federation-routes/1"
    rows = table()
    assert table() is rows
    assert isinstance(rows, tuple)
    assert rows
    keys = [(row.method, row.path) for row in rows]
    assert len(keys) == len(set(keys))
    for row in rows:
        assert row.phase in {"EXISTS", "DAY_ONE"}
        assert row.method in {"GET", "POST"}
        assert row.path.startswith("/")
        assert not secret_shape(repr(row))
        assert not hasattr(row, "__dict__")


def test_agents_and_cdeck_exist_and_dayone_chat_does_not() -> None:
    agents = _by("GET", "/api/v1/agents")
    cdeck = _by("GET", "/cdeck")
    chat = _by("POST", "/api/v1/dayone/chat")
    assert agents.phase == "EXISTS"
    assert cdeck.phase == "EXISTS"
    assert chat.phase == "DAY_ONE"
    assert chat.path == ROUTE_CHAT
    assert chat.why == _DAY_ONE_WHY
    assert [row for row in table() if row.path == "/api/v1/agents" and row.method != "GET"] == []
    assert [row for row in table() if row.path == "/cdeck" and row.method != "GET"] == []


def test_day_one_routes_are_the_product_constants() -> None:
    day = tuple(row for row in table() if row.phase == "DAY_ONE")
    assert [(row.method, row.path) for row in day] == [
        ("GET", ROUTE_PAGE),
        ("POST", ROUTE_SETUP),
        ("POST", ROUTE_CHAT),
    ]
    for row in day:
        assert row.why == _DAY_ONE_WHY
    exists = {row.path for row in table() if row.phase == "EXISTS"}
    assert ROUTE_PAGE not in exists
    assert ROUTE_SETUP not in exists
    assert ROUTE_CHAT not in exists
    assert "/dayone" not in exists
    assert "/api/v1/dayone/setup" not in exists
    assert "/api/v1/dayone/chat" not in exists


def test_paths_with_two_handlers_are_two_rows() -> None:
    spend = {(row.method, row.phase) for row in table() if row.path == "/api/v1/spend"}
    seats = {(row.method, row.phase) for row in table() if row.path == "/api/v1/seats"}
    pilot = {(row.method, row.phase) for row in table() if row.path == "/api/v1/pilot"}
    assert spend == {("GET", "EXISTS"), ("POST", "EXISTS")}
    assert seats == {("GET", "EXISTS"), ("POST", "EXISTS")}
    assert pilot == {("GET", "EXISTS"), ("POST", "EXISTS")}
    paths = {row.path for row in table()}
    assert "/cdeck/" in paths
    assert "/xtalk/" in paths
    assert "/cdeck/app.js" not in paths
    assert "/xtalk/xtalk.js" not in paths


def test_route_is_frozen_and_refuses_a_bad_row() -> None:
    row = _by("GET", "/cdeck")
    try:
        row.path = "/other"  # type: ignore[misc]
    except AttributeError:
        pass
    else:
        raise AssertionError("frozen")
    try:
        Route("GET", "relative", "EXISTS", "not absolute")
    except Refuse as exc:
        assert exc.code == "PATH"
    else:
        raise AssertionError("path")
    try:
        Route(
            "GET",
            "/api/v1/status",
            cast(_Phase, "LATER"),
            "not a phase this slot owns",
        )
    except Refuse as exc:
        assert exc.code == "PHASE"
    else:
        raise AssertionError("phase")
    try:
        Route(cast(_Method, "PUT"), "/api/v1/status", "EXISTS", "no such method")
    except Refuse as exc:
        assert exc.code == "METHOD"
    else:
        raise AssertionError("method")
    try:
        Route("GET", ROUTE_PAGE, "EXISTS", "core does not serve this page")
    except Refuse as exc:
        assert exc.code == "ROUTE"
    else:
        raise AssertionError("exists")
    try:
        Route("POST", ROUTE_CHAT, "DAY_ONE", "some other reason")
    except Refuse as exc:
        assert exc.code == "ROUTE"
    else:
        raise AssertionError("why")
    try:
        Route("GET", "/cdeck", "EXISTS", "")
    except Refuse as exc:
        assert exc.code == "BOUND"
    else:
        raise AssertionError("bound")
