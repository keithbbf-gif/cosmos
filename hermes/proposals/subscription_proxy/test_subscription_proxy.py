"""Loopback forward plan: redacted bearer, policy cap, rebuild, no socket."""

from __future__ import annotations

import ast
import hashlib
from collections.abc import Callable
from pathlib import Path
from typing import NamedTuple

import pytest

import subscription_proxy
from cosmos_hermes import Refuse, redact, secret_shape
from subscription_proxy import (
    ALLOW_CAP,
    BODY_CAP,
    HEADER_CAP,
    LOOPBACK,
    PATHS,
    SCHEMA,
    VALUE_CAP,
    ForwardPlan,
    adapters,
    connect,
    forward,
    listen,
    rebuild,
    snapshot,
)

TOKEN = "harborsessiontoken"
ALLOW = ("nous", "xai")
_DIGEST = 6
_CAP = 7
_HOST = 1
_LOG = 9
_BODY = 5


def _expect(code: str, func: Callable[[], object]) -> None:
    with pytest.raises(Refuse) as caught:
        func()
    assert caught.value.code == code


def _run(
    func: Callable[..., object],
    /,
    *args: object,
    **kwargs: object,
) -> Callable[[], object]:
    def call() -> object:
        return func(*args, **kwargs)

    return call


def _headers(
    path: str = "/v1/chat/completions",
    *,
    auth: str | None = f"Bearer {TOKEN}",
    cred: str | None = "nous-portal",
) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = [("Host", "127.0.0.1")]
    if auth is not None:
        rows.append(("Authorization", auth))
    rows.append(("path", path))
    if cred is not None:
        rows.append(("x-credential-id", cred))
    rows.append(("Content-Type", "application/json"))
    return rows


def _dump(rows: list[tuple[str, str]]) -> str:
    lines: list[str] = []
    for name, value in rows:
        if name.casefold() == "authorization":
            payload = value if value.casefold().startswith("bearer") else f"Bearer {value}"
            lines.append(f"{name} {payload}")
            continue
        lines.append(f"{name}: {value}")
    return "\n".join(lines)


def _direct(
    *,
    upstream: str = "xai",
    host: str = LOOPBACK,
    path: str = "/v1/chat/completions",
    credential_id: str = "cred-sub",
    headers: tuple[tuple[str, str], ...] = (),
    body: bytes = b"{}",
    body_sha256: str = "",
    cap: int = BODY_CAP,
    clamped: bool = False,
    log_line: str = "Host: 127.0.0.1",
    schema: str = SCHEMA,
) -> ForwardPlan:
    digest = hashlib.sha256(body).hexdigest() if body_sha256 == "" else body_sha256
    return ForwardPlan(
        upstream=upstream,
        host=host,
        path=path,
        credential_id=credential_id,
        headers=headers,
        body=body,
        body_sha256=digest,
        cap=cap,
        clamped=clamped,
        log_line=log_line,
        schema=schema,
    )


def _with(plan: ForwardPlan, index: int, value: object) -> tuple[object, ...]:
    items = list(snapshot(plan))
    items[index] = value
    return tuple(items)


def _at_cap(limit: object) -> Callable[[], object]:
    def call() -> object:
        return forward("nous", _headers(), b"{}", ALLOW, cap=limit)

    return call


def _at_host(host: object) -> Callable[[], object]:
    def call() -> object:
        return forward("nous", _headers(), b"{}", ALLOW, host=host)

    return call


class _Story(NamedTuple):
    plan: ForwardPlan
    rebuilt: ForwardPlan
    wide: ForwardPlan
    body_code: str
    embedded_code: str


def _embedded() -> ForwardPlan:
    return _direct(log_line="model api_key=harbor-secret-value")


def _body_key() -> ForwardPlan:
    rows = _headers(cred="cred-sub")
    return forward(
        "xai",
        rows,
        b'{"model":"grok-4","api_key=harbor-secret-value"}',
        ("xai",),
        host=LOOPBACK,
    )


def _story() -> _Story:
    """Mina's loopback session asks xai to summarize the Harbor card."""
    rows = _headers(cred="cred-sub")
    body = b'{"model":"grok-4","messages":[{"role":"user","content":"Summarize the Harbor card"}]}'
    plan = forward("xai", rows, body, ("xai", "nous"), host=LOOPBACK)
    wide = forward("xai", rows, body, ("xai",), cap=1_000_000, host=LOOPBACK)
    body_code = ""
    embedded_code = ""
    try:
        _body_key()
    except Refuse as err:
        body_code = err.code
    try:
        _embedded()
    except Refuse as err:
        embedded_code = err.code
    return _Story(
        plan=plan,
        rebuilt=rebuild(snapshot(plan)),
        wide=wide,
        body_code=body_code,
        embedded_code=embedded_code,
    )


def test_example_subscription_proxy() -> None:
    first = _story()
    second = _story()
    assert first == second
    assert first.plan == first.rebuilt
    assert first.plan.upstream == "xai"
    assert first.plan.host == LOOPBACK
    assert first.plan.credential_id == "cred-sub"
    assert first.plan.path == "/v1/chat/completions"
    assert first.plan.schema == SCHEMA
    assert first.wide.cap == BODY_CAP
    assert first.wide.clamped is True
    assert first.wide.cap == first.plan.cap
    assert first.body_code == "SECRET"
    assert first.embedded_code == "SECRET"
    shown = repr(first)
    assert TOKEN not in shown
    assert "api_key=" not in shown
    assert "Harbor" not in first.plan.log_line
    assert not secret_shape(shown)
    assert "Bearer " not in shown


def test_schema_success_and_redacted_log() -> None:
    assert SCHEMA == "cosmos-hermes-subscription_proxy/1"
    assert adapters() == ("nous", "xai")
    assert PATHS == (
        "/v1/chat/completions",
        "/v1/completions",
        "/v1/embeddings",
        "/v1/models",
    )
    assert list(subscription_proxy.__all__) == [
        "ALLOW_CAP",
        "BODY_CAP",
        "HEADER_CAP",
        "LOOPBACK",
        "PATHS",
        "PROVIDERS",
        "SCHEMA",
        "VALUE_CAP",
        "ForwardPlan",
        "adapters",
        "connect",
        "forward",
        "listen",
        "rebuild",
        "snapshot",
    ]
    rows = _headers()
    body = b'{"model":"Hermes-4-70B"}'
    plan = forward("nous", rows, body, ALLOW)
    assert plan == forward("nous", rows, bytearray(body), ("xai", "nous"))
    assert rebuild(plan) == plan
    assert plan.schema == SCHEMA
    assert plan.upstream == "nous"
    assert plan.host == "127.0.0.1"
    assert plan.path == "/v1/chat/completions"
    assert plan.credential_id == "nous-portal"
    assert plan.cap == BODY_CAP
    assert plan.clamped is False
    assert plan.body == body
    assert plan.body_sha256 == hashlib.sha256(body).hexdigest()
    assert plan.headers == (
        ("Host", "127.0.0.1"),
        ("Content-Type", "application/json"),
    )
    assert plan.log_line == redact(_dump(rows))
    assert TOKEN not in plan.log_line
    assert f"Bearer {TOKEN}" not in plan.log_line
    assert "Authorization [redacted-bearer]" in plan.log_line
    naive = redact(f"Authorization: Bearer {TOKEN}")
    assert TOKEN in naive
    text = repr(plan)
    assert TOKEN not in text
    assert not secret_shape(text)
    assert "Bearer " not in text
    assert "qqqq" not in text
    for path in PATHS:
        got = forward("xai", _headers(path, cred="xai-main"), b"", ("xai",))
        assert got.path == path
        assert got.upstream == "xai"
        assert got.host == LOOPBACK
        assert TOKEN not in got.log_line
    mapped = {
        "Host": "127.0.0.1",
        "Authorization": f"Bearer {TOKEN}",
        "path": "/v1/models",
        "x-credential-id": "cred-sub",
        "X-Trace": ["alpha", "beta"],
    }
    listed = forward("xai", mapped, b"", ("xai",))
    assert listed.credential_id == "cred-sub"
    assert listed.headers == (
        ("Host", "127.0.0.1"),
        ("X-Trace", "alpha"),
        ("X-Trace", "beta"),
    )
    assert TOKEN not in listed.log_line


def test_authorization_without_bearer_word_is_still_redacted() -> None:
    rows = _headers(auth=TOKEN, path="/v1/embeddings")
    plan = forward("nous", rows, b"", ALLOW)
    assert plan.log_line == redact(_dump(rows))
    assert TOKEN not in plan.log_line
    assert "[redacted-bearer]" in plan.log_line
    assert TOKEN not in repr(plan)
    client_key = _headers(auth="api_key=abcdefghij0123", cred="cred-sub")
    stripped = forward("xai", client_key, b"{}", ("xai",), host=LOOPBACK)
    assert "api_key=" not in stripped.log_line
    assert "abcdefghij0123" not in stripped.log_line
    assert "api_key=" not in repr(stripped)
    assert all(name.casefold() != "authorization" for name, _value in stripped.headers)
    short = _headers(auth="Bearer ab")
    quiet = forward("nous", short, b"", ALLOW)
    assert "Bearer ab" not in quiet.log_line
    assert "Bearer " not in repr(quiet)


def test_unknown_upstream_and_double_auth() -> None:
    rows = _headers()
    body = b"{}"
    _expect("UNKNOWN_UPSTREAM", _run(forward, "openai", rows, body, ALLOW))
    _expect("UNKNOWN_UPSTREAM", _run(forward, "nous", rows, body, ()))
    _expect("UNKNOWN_UPSTREAM", _run(forward, "xai", rows, body, ("nous",)))
    doubled = [*rows, ("authorization", "Bearer zzzzzzzzzzzz")]
    _expect("DOUBLE_AUTH", _run(forward, "nous", doubled, body, ALLOW))
    mapping: dict[str, object] = {
        "Authorization": [f"Bearer {TOKEN}", "Bearer zzzzzzzzzzzz"],
        "path": "/v1/models",
        "x-credential-id": "nous-portal",
    }
    _expect("DOUBLE_AUTH", _run(forward, "nous", mapping, b"", ("nous",)))
    _expect("UNKNOWN_UPSTREAM", _run(forward, "nope", doubled, body, ALLOW))
    bare = _headers(auth=None, path="/v1/models")
    quiet = forward("nous", bare, b"", ("nous",))
    assert "authorization" not in quiet.log_line.casefold()
    assert quiet.path == "/v1/models"


def test_body_cap_is_policy() -> None:
    rows = _headers(path="/v1/models")
    exact = b"q" * BODY_CAP
    plan = forward("nous", rows, exact, ALLOW, cap=2**20)
    assert plan.cap == BODY_CAP
    assert plan.clamped is True
    assert plan.body == exact
    assert len(plan.body) == 65536
    assert str(2**20) not in repr(plan)
    assert "qqqq" not in repr(plan)
    assert TOKEN not in plan.log_line
    _expect("OVERSIZE", _run(forward, "nous", rows, exact + b"q", ALLOW))
    low = forward("nous", rows, b"{}", ALLOW, cap=8)
    assert low.cap == 8
    assert low.clamped is False

    def over_low() -> object:
        return forward("nous", rows, b"123456789", ALLOW, cap=8)

    _expect("OVERSIZE", over_low)
    _expect("BAD_LIMIT", _at_cap(0))
    _expect("BAD_LIMIT", _at_cap(-1))
    _expect("NOT_INT", _at_cap(True))
    _expect("NOT_INT", _at_cap(1.5))
    default = forward("nous", rows, b"", ALLOW)
    assert default.cap == BODY_CAP
    assert default.clamped is False


def test_refusal_codes() -> None:
    rows = _headers()
    body = b"{}"
    _expect("BAD_ALLOW", _run(forward, "nous", rows, body, "nous"))
    _expect("SECRET", _run(forward, "nous", rows, body, ("sk-abcdefghij",)))
    _expect("BAD_ALLOW", _run(forward, "nous", rows, body, ("openai",)))
    _expect("DUPLICATE", _run(forward, "nous", rows, body, ("nous", "nous")))
    _expect("BAD_UPSTREAM", _run(forward, "NOPE", rows, body, ALLOW))
    _expect("BAD_UPSTREAM", _run(forward, "", rows, body, ALLOW))
    _expect("SECRET", _run(forward, "sk-abcdefghij", rows, body, ALLOW))
    _expect("NOT_TEXT", _run(forward, 12, rows, body, ALLOW))
    _expect("NULL_BYTE", _run(forward, "nous\x00", rows, body, ALLOW))
    _expect("OVERSIZE", _run(forward, "n" * 33, rows, body, ALLOW))
    _expect("NOT_BYTES", _run(forward, "nous", rows, "{}", ALLOW))
    _expect("MISSING_CRED", _run(forward, "nous", {"path": "/v1/models"}, body, ALLOW))
    _expect("MISSING_CRED", _run(forward, "nous", _headers(cred=""), body, ALLOW))
    _expect("BAD_CRED", _run(forward, "nous", _headers(cred="bad cred"), body, ALLOW))
    _expect("SECRET", _run(forward, "nous", _headers(cred="sk-abcdefghij"), body, ALLOW))
    _expect("SECRET", _run(forward, "nous", _headers(cred="Bearer abcdefghij"), body, ALLOW))
    creds = [*rows, ("x-credential-id", "other-id")]
    _expect("DUPLICATE", _run(forward, "nous", creds, body, ALLOW))
    _expect(
        "BAD_PATH",
        _run(forward, "nous", _headers(path="/v1/images/generations"), body, ALLOW),
    )
    _expect(
        "BAD_PATH",
        _run(forward, "nous", [("x-credential-id", "nous-portal")], body, ALLOW),
    )
    two_paths = [*_headers(), ("path", "/v1/models")]
    _expect("BAD_PATH", _run(forward, "nous", two_paths, body, ALLOW))
    _expect("BAD_HEADERS", _run(forward, "nous", 5, body, ALLOW))
    wide = [(f"h{i}", "v") for i in range(HEADER_CAP + 1)]
    _expect("BAD_HEADERS", _run(forward, "nous", wide, body, ALLOW))
    _expect("BAD_HEADER", _run(forward, "nous", [("bad name", "v")], body, ALLOW))
    _expect("BAD_HEADER", _run(forward, "nous", [("X-Note", "line\nbreak")], body, ALLOW))
    _expect("SECRET", _run(forward, "nous", [("X-Note", "Bearer abcdefghij")], body, ALLOW))
    _expect("SECRET", _run(forward, "nous", rows, b'{"k":"sk-abcdefghij"}', ALLOW))
    _expect("SECRET", _run(forward, "nous", rows, b"api_key=abcdefghij", ALLOW))
    _expect("SECRET", _run(forward, "nous", rows, b"api_key=abcdefghij\xff", ALLOW))
    echoed = [*rows, ("X-Copy", TOKEN)]
    _expect("SECRET", _run(forward, "nous", echoed, body, ALLOW))
    _expect("SECRET", _run(forward, "nous", rows, TOKEN.encode("utf-8"), ALLOW))
    huge_allow = tuple(f"p{i}" for i in range(ALLOW_CAP + 1))
    _expect("BAD_ALLOW", _run(forward, "nous", rows, body, huge_allow))
    long_cred = "a" * (64 + 1)
    _expect("OVERSIZE", _run(forward, "nous", _headers(cred=long_cred), body, ALLOW))
    long_value = "v" * (VALUE_CAP + 1)
    _expect("OVERSIZE", _run(forward, "nous", [("X-Note", long_value)], body, ALLOW))
    _expect("PUBLIC_HOST", _at_host("0.0.0.0"))
    _expect("PUBLIC_HOST", _at_host("localhost"))
    _expect("PUBLIC_HOST", _at_host(""))
    _expect("NOT_TEXT", _at_host(12))
    _expect("SECRET", _at_host("sk-abcdefghij"))
    _expect("NO_SOCKET", listen)
    _expect("NO_SOCKET", _run(listen, "0.0.0.0", 8645))
    _expect("NO_SOCKET", _run(listen, "127.0.0.1", 8645))
    _expect("NO_SOCKET", connect)
    _expect("NO_SOCKET", _run(connect, "api.x.ai", 443))


def test_plan_integrity_and_rebuild() -> None:
    rows = _headers(cred="cred-sub")
    body = b'{"model":"grok-4"}'
    plan = forward("xai", rows, body, ("xai",), host=LOOPBACK)
    assert rebuild(snapshot(plan)) == plan
    assert rebuild(plan) == plan
    assert snapshot(plan)[0] == "xai"
    assert snapshot(plan)[_HOST] == LOOPBACK
    _expect("SECRET", _embedded)
    _expect("SECRET", _run(_direct, log_line=f"Authorization Bearer {TOKEN}"))
    _expect("SECRET", _run(_direct, log_line=f"[redacted-assignment] {TOKEN}"))
    _expect("SECRET", _run(_direct, log_line="Authorization Bearer ab"))
    _expect(
        "SECRET",
        _run(_direct, headers=(("X-Note", "api_key=abcdefghij"),)),
    )
    _expect("SECRET", _run(_direct, body=b"api_key=abcdefghij"))
    _expect("BAD_PLAN", _run(_direct, body_sha256="0" * 64))
    _expect("BAD_LIMIT", _run(_direct, cap=BODY_CAP + 1))
    _expect("BAD_PLAN", _run(_direct, clamped=True, cap=8))
    _expect("BAD_PLAN", _run(_direct, schema="cosmos-hermes-subscription_proxy/2"))
    _expect("BAD_UPSTREAM", _run(_direct, upstream="openai"))
    _expect("PUBLIC_HOST", _run(_direct, host="0.0.0.0"))
    _expect("BAD_PLAN", _run(_direct, headers=(("Authorization", "kept"),)))
    _expect("BAD_PLAN", _run(rebuild, ("only",)))
    _expect("BAD_PLAN", _run(snapshot, "plan"))
    _expect("BAD_PLAN", _run(rebuild, _with(plan, _DIGEST, "0" * 64)))
    _expect("NOT_INT", _run(rebuild, _with(plan, _CAP, True)))
    _expect("PUBLIC_HOST", _run(rebuild, _with(plan, _HOST, "10.0.0.8")))
    _expect("SECRET", _run(rebuild, _with(plan, _LOG, "api_key=abcdefghij")))
    _expect("NOT_BYTES", _run(rebuild, _with(plan, _BODY, "not-bytes")))
    _expect("OVERSIZE", _run(_direct, body=b"12345", cap=4))


def test_source_imports_no_socket() -> None:
    tree = ast.parse(Path(subscription_proxy.__file__).read_text(encoding="utf-8"))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            modules.add(node.module.split(".")[0])
    assert modules.isdisjoint({"socket", "urllib", "requests", "subprocess", "http", "pickle"})
    assert "cosmos_hermes" in modules
    names = set(subscription_proxy.__all__)
    assert {"forward", "listen", "connect", "snapshot", "rebuild"}.issubset(names)
