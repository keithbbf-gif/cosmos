"""Parser, loopback route table, and bearer tests. No listener. No network."""

from __future__ import annotations

from pathlib import Path
from typing import cast

import pytest

from api_server import (
    BODY_TEXT_CAP,
    DEFAULT_PORT,
    FENCE_CAP,
    LOOPBACK_HOST,
    POLICY_RUN_CAP,
    POLICY_TEXT_BUDGET,
    SCHEMA,
    BearerCheck,
    BindCheck,
    ChatMessage,
    ChatRequest,
    Resolution,
    Route,
    RouteTable,
    check_bearer,
    check_bind,
    describe_loopback,
    parse_chat,
    rebuild,
    resolve,
)
from cosmos_hermes import Refuse

_Story = tuple[RouteTable, Resolution, Resolution, ChatRequest, str, str]


def _body(
    content: str = "Hello",
    *,
    model: str = "hermes-agent",
    stream: bool | None = None,
    extra: tuple[dict[str, str], ...] = (),
) -> dict[object, object]:
    messages: list[object] = [{"role": "user", "content": content}, *extra]
    body: dict[object, object] = {"model": model, "messages": messages}
    if stream is not None:
        body["stream"] = stream
    return body


def _overhead(content_len: int) -> int:
    sample = _body("x" * content_len, model="m")
    parts = ["model", "m", "messages", "role", "user", "content", "x" * content_len]
    assert sum(len(part) for part in parts) == (
        len("model") + len("m") + len("messages") + len("role") + len("user") + len("content") + content_len
    )
    assert sample["model"] == "m"
    return len("model") + 1 + len("messages") + len("role") + len("user") + len("content")


def _route(table: RouteTable, method: str, path: str) -> Route:
    for row in table.routes:
        if row.method == method and row.path == path:
            return row
    raise AssertionError(method)


def _table(story: _Story) -> RouteTable:
    return story[0]


def _health(story: _Story) -> Resolution:
    return story[1]


def _session(story: _Story) -> Resolution:
    return story[2]


def _chat(story: _Story) -> ChatRequest:
    return story[3]


def _bind_code(story: _Story) -> str:
    return story[4]


def _bearer_code(story: _Story) -> str:
    return story[5]


def _note(chat: ChatRequest) -> ChatMessage:
    return chat.messages[1]


def test_schema_success_and_same_input() -> None:
    assert SCHEMA == "cosmos-hermes-api_server/1"
    body: dict[object, object] = {
        "model": "hermes-agent",
        "messages": [
            {"role": "system", "content": "You are a Python expert."},
            {"role": "user", "content": "Write a fibonacci function"},
        ],
        "stream": True,
    }
    first = parse_chat(body)
    second = parse_chat(body)
    assert first == second
    assert isinstance(first, ChatRequest)
    assert first.schema == SCHEMA
    assert first.model == "hermes-agent"
    assert first.stream is True
    assert first.cap == POLICY_RUN_CAP
    assert [item.role for item in first.messages] == ["system", "user"]
    assert first.messages[1].content == "Write a fibonacci function"
    quiet = parse_chat(_body())
    assert quiet.stream is False
    assert quiet.messages[0] == ChatMessage("user", "Hello")


def test_bad_body() -> None:
    cases: tuple[dict[object, object], ...] = (
        {},
        {"model": "hermes-agent"},
        {"messages": [{"role": "user", "content": "Hi"}]},
        {"model": 1, "messages": [{"role": "user", "content": "Hi"}]},
        {"model": "hermes-agent", "messages": "Hi"},
        {"model": "   ", "messages": [{"role": "user", "content": "Hi"}]},
        {"model": "hermes-agent", "messages": []},
        {"model": "hermes-agent", "messages": ["Hi"]},
        {"model": "hermes-agent", "messages": [{"role": "user"}]},
        {"model": "hermes-agent", "messages": [{"role": "developer", "content": "Hi"}]},
        {"model": "hermes-agent", "messages": [{"role": "user", "content": ["Hi"]}]},
        {"model": "hermes-agent", "messages": ({"role": "user", "content": "Hi"},)},
    )
    for body in cases:
        with pytest.raises(Refuse) as caught:
            parse_chat(body)
        assert caught.value.code == "BAD_BODY"
    with pytest.raises(Refuse) as nested:
        parse_chat(cast(dict[object, object], ["nope"]))
    assert nested.value.code == "BAD_BODY"
    with pytest.raises(Refuse) as flagged:
        parse_chat(_body(stream=cast(bool, "yes")))
    assert flagged.value.code == "BAD_BODY"
    deep: object = {"role": "user", "content": "Hi"}
    for _ in range(40):
        deep = [deep]
    with pytest.raises(Refuse) as too_deep:
        parse_chat(cast(dict[object, object], {"model": "m", "messages": deep}))
    assert too_deep.value.code == "BAD_BODY"


def test_body_text_cap_and_exact_fit() -> None:
    overhead = _overhead(1)
    room = BODY_TEXT_CAP - overhead
    fitted = parse_chat(_body("c" * room, model="m"))
    assert len(fitted.messages[0].content) == room
    with pytest.raises(Refuse) as one_more:
        parse_chat(_body("c" * (room + 1), model="m"))
    assert one_more.value.code == "OVERSIZE"
    with pytest.raises(Refuse) as single:
        parse_chat(_body("a" * (BODY_TEXT_CAP + 1)))
    assert single.value.code == "OVERSIZE"
    half = "b" * ((BODY_TEXT_CAP // 2) + 1)
    with pytest.raises(Refuse) as total:
        parse_chat(
            {
                "model": "m",
                "messages": [
                    {"role": "user", "content": half},
                    {"role": "user", "content": half},
                ],
            }
        )
    assert total.value.code == "OVERSIZE"


def test_null_secret_and_repr() -> None:
    with pytest.raises(Refuse) as nul:
        parse_chat(_body("bad\x00text"))
    assert nul.value.code == "NULL_BYTE"
    raw = "see sk-livekeyvalue"
    with pytest.raises(Refuse) as secret:
        parse_chat(_body(raw))
    assert secret.value.code == "SECRET"
    assert "sk-livekeyvalue" not in str(secret.value)
    with pytest.raises(Refuse) as bearer_line:
        parse_chat(_body("Authorization: Bearer abcdefghijk"))
    assert bearer_line.value.code == "SECRET"
    with pytest.raises(Refuse) as assigned:
        parse_chat(_body("token=supersecret"))
    assert assigned.value.code == "SECRET"
    kept = parse_chat(_body("ordinary note"))
    blob = repr(kept) + repr(kept.messages[0])
    assert "sk-" not in blob
    assert "Bearer " not in blob
    assert "api_key=" not in blob
    with pytest.raises(Refuse) as built:
        ChatMessage("user", "sk-livekeyvalue")
    assert built.value.code == "SECRET"
    with pytest.raises(Refuse) as model_secret:
        ChatRequest(
            schema=SCHEMA,
            model="sk-livekeyvalue",
            messages=(ChatMessage("user", "Hi"),),
            stream=False,
            cap=1,
        )
    assert model_secret.value.code == "SECRET"
    assert "sk-livekeyvalue" not in str(model_secret.value)


def test_bind() -> None:
    closed = check_bind(LOOPBACK_HOST, False)
    opened = check_bind(LOOPBACK_HOST, True)
    assert isinstance(closed, BindCheck)
    assert closed.host == LOOPBACK_HOST
    assert closed.loopback is True
    assert closed.public_grant is False
    assert opened.loopback is True
    assert opened.public_grant is True
    assert closed.schema == SCHEMA
    granted = check_bind("0.0.0.0", True)
    assert granted.loopback is False
    assert granted.public_grant is True
    assert granted.host == "0.0.0.0"
    other = check_bind("10.1.2.3", True)
    assert other.host == "10.1.2.3"
    assert other.loopback is False
    wide = check_bind("255.255.255.255", True)
    assert wide.host == "255.255.255.255"
    assert wide.loopback is False
    for host in ("0.0.0.0", "10.1.2.3", "localhost", "::1", "127.0.0.2", "", "   "):
        with pytest.raises(Refuse) as caught:
            check_bind(host, False)
        assert caught.value.code == "PUBLIC_BIND"
    with pytest.raises(Refuse) as blank:
        check_bind("   ", True)
    assert blank.value.code == "PUBLIC_BIND"
    for host in ("localhost", "::1", "127.0.0.1 ", "bad host", "127.0.0.01", "256.1.1.1", "1.2.3"):
        with pytest.raises(Refuse) as shaped:
            check_bind(host, True)
        assert shaped.value.code == "BAD_HOST"
    with pytest.raises(Refuse) as grant:
        check_bind(LOOPBACK_HOST, cast(bool, 1))
    assert grant.value.code == "BAD_GRANT"
    with pytest.raises(Refuse) as text:
        check_bind(12, False)
    assert text.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as host_nul:
        check_bind("127.0.0.1\x00", False)
    assert host_nul.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as host_secret:
        check_bind("sk-livekeyvalue", True)
    assert host_secret.value.code == "SECRET"
    assert "sk-livekeyvalue" not in str(host_secret.value)
    with pytest.raises(Refuse) as huge:
        check_bind("1" * 254, False)
    assert huge.value.code == "OVERSIZE"


def test_bearer() -> None:
    token = "local-dev-token"
    matched = check_bearer(token, token)
    assert isinstance(matched, BearerCheck)
    assert matched.accepted is True
    assert matched.schema == SCHEMA
    assert token not in repr(matched)
    with pytest.raises(Refuse) as empty:
        check_bearer(token, "")
    assert empty.value.code == "NO_BEARER"
    with pytest.raises(Refuse) as both_empty:
        check_bearer("", "   ")
    assert both_empty.value.code == "NO_BEARER"
    with pytest.raises(Refuse) as mismatch:
        check_bearer("other-token", token)
    assert mismatch.value.code == "BAD_BEARER"
    assert token not in str(mismatch.value)
    with pytest.raises(Refuse) as space:
        check_bearer(token + " ", token)
    assert space.value.code == "BAD_BEARER"
    with pytest.raises(Refuse) as missing:
        check_bearer("", token)
    assert missing.value.code == "BAD_BEARER"
    raw = "sk-livekeyvalue"
    with pytest.raises(Refuse) as secret:
        check_bearer(raw, raw)
    assert secret.value.code == "SECRET"
    assert raw not in str(secret.value)
    with pytest.raises(Refuse) as header:
        check_bearer("Bearer abcdefghijk", "abcdefghi")
    assert header.value.code == "SECRET"
    with pytest.raises(Refuse) as presented:
        check_bearer(None, token)
    assert presented.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as expected:
        check_bearer(token, None)
    assert expected.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as rejected:
        BearerCheck(schema=SCHEMA, accepted=False)
    assert rejected.value.code == "BAD_BEARER"


def test_cap_is_recorded_and_not_raised() -> None:
    high = parse_chat(_body(), requested_cap=POLICY_RUN_CAP + 1000)
    assert high.cap == POLICY_RUN_CAP
    low = parse_chat(_body(), requested_cap=3)
    assert low.cap == 3
    default = parse_chat(_body())
    assert default.cap == POLICY_RUN_CAP
    clamped = ChatRequest(
        schema="other",
        model="hermes-agent",
        messages=(ChatMessage("assistant", "done"),),
        stream=False,
        cap=99,
    )
    assert clamped.cap == POLICY_RUN_CAP
    assert clamped.schema == SCHEMA
    floor = ChatRequest(
        schema=SCHEMA,
        model="hermes-agent",
        messages=(ChatMessage("tool", "ok"),),
        stream=False,
        cap=1,
    )
    assert floor.cap == 1
    with pytest.raises(Refuse) as zero:
        parse_chat(_body(), requested_cap=0)
    assert zero.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as negative:
        parse_chat(_body(), requested_cap=-4)
    assert negative.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as flag:
        parse_chat(_body(), requested_cap=True)
    assert flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as text:
        parse_chat(_body(), requested_cap="10")
    assert text.value.code == "NOT_INT"
    with pytest.raises(Refuse) as direct:
        ChatRequest(
            schema=SCHEMA,
            model="hermes-agent",
            messages=(ChatMessage("user", "Hi"),),
            stream=False,
            cap=cast(int, False),
        )
    assert direct.value.code == "NOT_INT"


def test_loopback_routes_are_descriptors() -> None:
    card = "card-ada-desk"
    table = describe_loopback(LOOPBACK_HOST, card, public_grant=True)
    again = describe_loopback(LOOPBACK_HOST, card, public_grant=True)
    assert table == again
    assert table.schema == SCHEMA
    assert table.host == LOOPBACK_HOST
    assert table.port == DEFAULT_PORT
    assert table.bearer_id == card
    assert table.run_cap == POLICY_RUN_CAP
    assert table.budget == POLICY_TEXT_BUDGET
    assert table.fence == 0
    assert table.public_grant is False
    assert table.listens is False
    assert table.kind == "descriptor"
    assert len(table.chain) == 64
    health = _route(table, "GET", "/health")
    session = _route(table, "POST", "/session")
    assert health.kind == "descriptor"
    assert health.executes is False
    assert health.auth == "none"
    assert health.starts_run is False
    assert session.kind == "descriptor"
    assert session.executes is False
    assert session.auth == "bearer"
    assert session.starts_run is True
    assert "GET /health" in table.names
    assert "POST /session" in table.names
    probed = resolve(table, "GET /health", fence=0)
    opened = resolve(table, "POST /session", card, fence=0)
    assert probed == resolve(table, "GET /health", fence=0)
    assert isinstance(probed, Resolution)
    assert probed.method == "GET"
    assert probed.path == "/health"
    assert probed.executes is False
    assert probed.listens is False
    assert probed.kind == "descriptor"
    assert probed.starts_run is False
    assert opened.path == "/session"
    assert opened.starts_run is True
    assert opened.executes is False
    assert opened.run_cap == POLICY_RUN_CAP
    assert card not in repr(probed)
    assert card not in repr(opened)
    detail = resolve(table, "GET /health/detailed", card, fence=0)
    assert detail.auth == "bearer"
    assert detail.executes is False
    narrow = describe_loopback(LOOPBACK_HOST, card, routes=("GET /health", "POST /session"))
    assert tuple(f"{row.method} {row.path}" for row in narrow.routes) == ("GET /health", "POST /session")
    with pytest.raises(Refuse) as hidden:
        resolve(narrow, "POST /v1/chat/completions", card, fence=0)
    assert hidden.value.code == "UNKNOWN_ROUTE"
    forced = Route(
        schema="nope",
        method="GET",
        path="/health",
        auth="bearer",
        starts_run=True,
        cost=health.cost,
        executes=True,
        kind="listener",
    )
    assert forced == health
    raised = describe_loopback(
        LOOPBACK_HOST,
        card,
        requested_cap=POLICY_RUN_CAP + 40,
        text_budget=POLICY_TEXT_BUDGET + 80,
        public_grant=True,
    )
    assert raised.run_cap == POLICY_RUN_CAP
    assert raised.budget == POLICY_TEXT_BUDGET
    assert raised.public_grant is False
    assert len(raised.routes) == len(table.routes)


def test_route_refusals() -> None:
    card = "card-ada-desk"
    table = describe_loopback(LOOPBACK_HOST, card, fence=4)
    for host in ("0.0.0.0", "10.1.2.3", "localhost", "::1", "127.0.0.2", "", "   "):
        with pytest.raises(Refuse) as caught:
            describe_loopback(host, card, public_grant=True)
        assert caught.value.code == "NOT_LOOPBACK"
    with pytest.raises(Refuse) as missing:
        describe_loopback(LOOPBACK_HOST, None)
    assert missing.value.code == "NO_BEARER"
    with pytest.raises(Refuse) as blank:
        describe_loopback(LOOPBACK_HOST, "   ")
    assert blank.value.code == "NO_BEARER"
    with pytest.raises(Refuse) as shaped:
        describe_loopback(LOOPBACK_HOST, "card ada")
    assert shaped.value.code == "BAD_BEARER"
    with pytest.raises(Refuse) as secret:
        describe_loopback(LOOPBACK_HOST, "sk-livekeyvalue")
    assert secret.value.code == "SECRET"
    assert "sk-livekeyvalue" not in str(secret.value)
    with pytest.raises(Refuse) as host_type:
        describe_loopback(12, card)
    assert host_type.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as grant:
        describe_loopback(LOOPBACK_HOST, card, public_grant=cast(bool, "yes"))
    assert grant.value.code == "BAD_GRANT"
    with pytest.raises(Refuse) as port:
        describe_loopback(LOOPBACK_HOST, card, port=0)
    assert port.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as fence:
        describe_loopback(LOOPBACK_HOST, card, fence=FENCE_CAP + 1)
    assert fence.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as line:
        resolve(table, "GET", fence=4)
    assert line.value.code == "BAD_TARGET"
    with pytest.raises(Refuse) as spaced:
        resolve(table, "GET  /health", fence=4)
    assert spaced.value.code == "BAD_TARGET"
    with pytest.raises(Refuse) as method:
        resolve(table, "GOT /health", fence=4)
    assert method.value.code == "BAD_METHOD"
    with pytest.raises(Refuse) as path:
        resolve(table, "GET /Health", fence=4)
    assert path.value.code == "BAD_PATH"
    with pytest.raises(Refuse) as query:
        resolve(table, "GET /health?ready=1", fence=4)
    assert query.value.code == "BAD_PATH"
    with pytest.raises(Refuse) as unknown:
        resolve(table, "GET /api/jobs", fence=4)
    assert unknown.value.code == "UNKNOWN_ROUTE"
    with pytest.raises(Refuse) as stale:
        resolve(table, "GET /health", fence=3)
    assert stale.value.code == "STALE"
    with pytest.raises(Refuse) as no_fence:
        resolve(table, "GET /health")
    assert no_fence.value.code == "STALE"
    with pytest.raises(Refuse) as flag:
        resolve(table, "GET /health", fence=True)
    assert flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as absent:
        resolve(table, "POST /session", fence=4)
    assert absent.value.code == "NO_BEARER"
    with pytest.raises(Refuse) as blank_presented:
        resolve(table, "POST /session", "   ", fence=4)
    assert blank_presented.value.code == "NO_BEARER"
    with pytest.raises(Refuse) as mismatch:
        resolve(table, "POST /session", "card-other-desk", fence=4)
    assert mismatch.value.code == "BAD_BEARER"
    assert card not in str(mismatch.value)
    with pytest.raises(Refuse) as wrong_health:
        resolve(table, "GET /health", "card-other-desk", fence=4)
    assert wrong_health.value.code == "BAD_BEARER"
    with pytest.raises(Refuse) as presented_secret:
        resolve(table, "GET /health", "sk-livekeyvalue", fence=4)
    assert presented_secret.value.code == "SECRET"
    with pytest.raises(Refuse) as long_line:
        resolve(table, "x" * 129, fence=4)
    assert long_line.value.code == "OVERSIZE"
    with pytest.raises(Refuse) as dup:
        describe_loopback(LOOPBACK_HOST, card, routes=("GET /health", "GET /health"))
    assert dup.value.code == "DUPLICATE"
    with pytest.raises(Refuse) as empty:
        describe_loopback(LOOPBACK_HOST, card, routes=())
    assert empty.value.code == "EMPTY_ROUTES"
    with pytest.raises(Refuse) as text_routes:
        describe_loopback(LOOPBACK_HOST, card, routes="GET /health")
    assert text_routes.value.code == "BAD_BODY"
    with pytest.raises(Refuse) as item:
        describe_loopback(LOOPBACK_HOST, card, routes=(cast(str, 5),))
    assert item.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as budget_flag:
        describe_loopback(LOOPBACK_HOST, card, text_budget=True)
    assert budget_flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as budget_zero:
        describe_loopback(LOOPBACK_HOST, card, text_budget=0)
    assert budget_zero.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as bad_table:
        resolve("table", "GET /health", fence=0)
    assert bad_table.value.code == "BAD_TABLE"
    with pytest.raises(Refuse) as bad_rebuild:
        rebuild(None)
    assert bad_rebuild.value.code == "BAD_TABLE"
    with pytest.raises(Refuse) as auth:
        Route(
            schema=SCHEMA,
            method="GET",
            path="/health",
            auth="open",
            starts_run=False,
            cost=_route(table, "GET", "/health").cost,
            executes=False,
        )
    assert auth.value.code == "BAD_AUTH"
    with pytest.raises(Refuse) as flag_row:
        Route(
            schema=SCHEMA,
            method="GET",
            path="/health",
            auth="none",
            starts_run=cast(bool, 1),
            cost=_route(table, "GET", "/health").cost,
            executes=False,
        )
    assert flag_row.value.code == "NOT_BOOL"
    with pytest.raises(Refuse) as cost:
        Route(
            schema=SCHEMA,
            method="GET",
            path="/health",
            auth="none",
            starts_run=False,
            cost=_route(table, "GET", "/health").cost + 1,
            executes=False,
        )
    assert cost.value.code == "BROKEN_CHAIN"
    with pytest.raises(Refuse) as chain_type:
        RouteTable(
            schema=SCHEMA,
            host=LOOPBACK_HOST,
            port=DEFAULT_PORT,
            bearer_id=card,
            run_cap=POLICY_RUN_CAP,
            budget=POLICY_TEXT_BUDGET,
            fence=0,
            public_grant=False,
            listens=False,
            routes=table.routes,
            chain=cast(str, 5),
        )
    assert chain_type.value.code == "NOT_TEXT"


def test_budget_skips_without_abandoning_later_routes() -> None:
    card = "card-ada-desk"
    full = describe_loopback(LOOPBACK_HOST, card)
    fat = _route(full, "POST", "/v1/chat/completions")
    health = _route(full, "GET", "/health")
    session = _route(full, "POST", "/session")
    assert fat.cost > health.cost
    assert session.cost > health.cost
    tight = describe_loopback(
        LOOPBACK_HOST,
        card,
        routes=("POST /v1/chat/completions", "POST /session", "GET /health"),
        text_budget=health.cost,
    )
    assert tuple(row.path for row in tight.routes) == ("/health",)
    assert tight.budget == health.cost
    roomy = health.cost + session.cost
    assert fat.cost > roomy
    kept = describe_loopback(
        LOOPBACK_HOST,
        card,
        routes=("POST /v1/chat/completions", "GET /health", "POST /session"),
        text_budget=roomy,
    )
    assert tuple(f"{row.method} {row.path}" for row in kept.routes) == ("GET /health", "POST /session")
    assert kept.budget == roomy
    with pytest.raises(Refuse) as none:
        describe_loopback(
            LOOPBACK_HOST,
            card,
            routes=("POST /v1/chat/completions",),
            text_budget=health.cost,
        )
    assert none.value.code == "EMPTY_ROUTES"
    clamped = RouteTable(
        schema="other",
        host=full.host,
        port=full.port,
        bearer_id=full.bearer_id,
        run_cap=POLICY_RUN_CAP + 9,
        budget=POLICY_TEXT_BUDGET + 5,
        fence=full.fence,
        public_grant=True,
        listens=True,
        routes=full.routes,
        kind="listener",
    )
    assert clamped.run_cap == POLICY_RUN_CAP
    assert clamped.budget == POLICY_TEXT_BUDGET
    assert clamped.public_grant is False
    assert clamped.listens is False
    assert clamped.kind == "descriptor"
    assert clamped.schema == SCHEMA
    assert clamped.routes == full.routes
    with pytest.raises(Refuse) as broken:
        RouteTable(
            schema=SCHEMA,
            host=LOOPBACK_HOST,
            port=DEFAULT_PORT,
            bearer_id=card,
            run_cap=POLICY_RUN_CAP,
            budget=health.cost,
            fence=0,
            public_grant=False,
            listens=False,
            routes=(fat, health),
            chain="0" * 64,
        )
    assert broken.value.code == "BROKEN_CHAIN"


def test_rebuild_matches_records() -> None:
    card = "card-ada-desk"
    table = describe_loopback(LOOPBACK_HOST, card, fence=6, port=8642, requested_cap=4)
    fresh = rebuild(table)
    assert fresh == table
    assert rebuild(fresh) == table
    with pytest.raises(Refuse) as caught:
        RouteTable(
            schema=SCHEMA,
            host=table.host,
            port=table.port,
            bearer_id=table.bearer_id,
            run_cap=table.run_cap,
            budget=table.budget,
            fence=table.fence,
            public_grant=False,
            listens=False,
            routes=table.routes,
            chain="0" * 64,
        )
    assert caught.value.code == "BROKEN_CHAIN"
    health = _route(table, "GET", "/health")
    with pytest.raises(Refuse) as dup:
        RouteTable(
            schema=SCHEMA,
            host=table.host,
            port=table.port,
            bearer_id=table.bearer_id,
            run_cap=table.run_cap,
            budget=table.budget,
            fence=table.fence,
            public_grant=False,
            listens=False,
            routes=(health, health),
        )
    assert dup.value.code == "DUPLICATE"
    with pytest.raises(Refuse) as empty:
        RouteTable(
            schema=SCHEMA,
            host=table.host,
            port=table.port,
            bearer_id=table.bearer_id,
            run_cap=table.run_cap,
            budget=table.budget,
            fence=table.fence,
            public_grant=False,
            listens=False,
            routes=(),
        )
    assert empty.value.code == "EMPTY_ROUTES"
    with pytest.raises(Refuse) as listed:
        RouteTable(
            schema=SCHEMA,
            host=table.host,
            port=table.port,
            bearer_id=table.bearer_id,
            run_cap=table.run_cap,
            budget=table.budget,
            fence=table.fence,
            public_grant=False,
            listens=False,
            routes=cast(tuple[Route, ...], [health]),
        )
    assert listed.value.code == "BAD_BODY"


def test_example_api_server() -> None:
    """Ada's card names the loopback desk. The studio light session stays a descriptor."""

    def run() -> _Story:
        card = "card-ada-desk"
        note = "Ada left the studio light on"
        table = describe_loopback(LOOPBACK_HOST, card, fence=7)
        health = resolve(table, "GET /health", fence=7)
        session = resolve(table, "POST /session", card, fence=7)
        chat = parse_chat(
            {
                "model": "hermes-agent",
                "messages": [
                    {"role": "system", "content": "You keep the studio light notes."},
                    {"role": "user", "content": note},
                ],
            }
        )
        bind_code = "UNCAUGHT"
        bearer_code = "UNCAUGHT"
        try:
            describe_loopback("10.1.2.3", card, fence=7)
        except Refuse as refused:
            bind_code = refused.code
        try:
            describe_loopback(LOOPBACK_HOST, "", fence=7)
        except Refuse as refused:
            bearer_code = refused.code
        return table, health, session, chat, bind_code, bearer_code

    first = run()
    second = run()
    assert first == second
    table = _table(first)
    health = _health(first)
    session = _session(first)
    chat = _chat(first)
    assert table.host == LOOPBACK_HOST
    assert table.port == DEFAULT_PORT
    assert table.listens is False
    assert table.kind == "descriptor"
    assert table.bearer_id == "card-ada-desk"
    assert "GET /health" in table.names
    assert "POST /session" in table.names
    assert health.method == "GET"
    assert health.path == "/health"
    assert health.auth == "none"
    assert health.executes is False
    assert health.listens is False
    assert health.kind == "descriptor"
    assert health.fence == 7
    assert session.method == "POST"
    assert session.path == "/session"
    assert session.auth == "bearer"
    assert session.starts_run is True
    assert session.executes is False
    assert session.listens is False
    assert session.kind == "descriptor"
    assert _note(chat).content == "Ada left the studio light on"
    assert chat.model == "hermes-agent"
    assert chat.cap == POLICY_RUN_CAP
    assert _bind_code(first) == "NOT_LOOPBACK"
    assert _bearer_code(first) == "NO_BEARER"
    assert rebuild(table) == table


def test_source_stays_closed() -> None:
    text = Path(__file__).with_name("api_server.py").read_text(encoding="utf-8")
    for banned in (
        "socket",
        "subprocess",
        "urllib",
        "requests",
        "pickle",
        "eval(",
        "exec(",
        "threading",
        "http.server",
    ):
        assert banned not in text
    assert text.count("compile(") == text.count("re.compile(")
