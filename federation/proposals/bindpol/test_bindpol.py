"""Pins for the day-one bind policy."""

from __future__ import annotations

from collections.abc import Callable
from typing import cast

from bindpol import SCHEMA, Bind, decide
from cosmos_federation import DEFAULT_HOST, DEFAULT_PORT, Refuse, secret_shape


def _code(call: Callable[[], object]) -> str:
    try:
        call()
    except Refuse as exc:
        return exc.code
    raise AssertionError("expected Refuse")


def test_schema_and_public_names() -> None:
    assert SCHEMA == "cosmos-federation-bindpol/1"
    assert __import__("bindpol").__all__ == ["SCHEMA", "Bind", "decide"]


def test_default_loopback_is_http_bearer() -> None:
    got = decide(DEFAULT_HOST, DEFAULT_PORT, False, False, False)
    assert got == Bind(host="127.0.0.1", port=8770, scheme="http", auth="bearer")
    assert got.host == DEFAULT_HOST
    assert got.port == DEFAULT_PORT
    assert got.scheme == "http"
    assert got.auth == "bearer"
    assert not secret_shape(repr(got))


def test_open_auth_on_loopback() -> None:
    assert _code(lambda: decide(DEFAULT_HOST, DEFAULT_PORT, False, False, True)) == "OPEN_AUTH"


def test_open_auth_on_remote_tls() -> None:
    assert _code(lambda: decide("0.0.0.0", DEFAULT_PORT, True, True, True)) == "OPEN_AUTH"


def test_open_auth_wins_over_remote_plain() -> None:
    assert _code(lambda: decide("0.0.0.0", DEFAULT_PORT, True, False, True)) == "OPEN_AUTH"


def test_remote_without_tls_is_remote_plain() -> None:
    assert _code(lambda: decide("0.0.0.0", DEFAULT_PORT, True, False, False)) == "REMOTE_PLAIN"
    assert _code(lambda: decide(DEFAULT_HOST, DEFAULT_PORT, True, False, False)) == "REMOTE_PLAIN"


def test_remote_tls_wildcard_is_https_bearer() -> None:
    got = decide("0.0.0.0", DEFAULT_PORT, True, True, False)
    assert got == Bind(host="0.0.0.0", port=8770, scheme="https", auth="bearer")
    assert got.scheme == "https"
    assert got.auth == "bearer"
    assert not secret_shape(repr(got))


def test_wildcard_without_remote_is_host() -> None:
    assert _code(lambda: decide("0.0.0.0", DEFAULT_PORT, False, True, False)) == "HOST"


def test_remote_tls_loopback_disagrees() -> None:
    assert _code(lambda: decide(DEFAULT_HOST, DEFAULT_PORT, True, True, False)) == "HOST"


def test_other_hosts_refuse() -> None:
    assert _code(lambda: decide("localhost", DEFAULT_PORT, False, False, False)) == "HOST"
    assert _code(lambda: decide("::1", DEFAULT_PORT, False, False, False)) == "HOST"
    assert _code(lambda: decide("192.168.1.5", DEFAULT_PORT, False, False, False)) == "HOST"
    assert _code(lambda: decide("", DEFAULT_PORT, False, False, False)) == "BOUND"


def test_port_bounds() -> None:
    assert decide(DEFAULT_HOST, 1, False, False, False).port == 1
    assert decide(DEFAULT_HOST, 65535, False, False, False).port == 65535
    assert _code(lambda: decide(DEFAULT_HOST, 0, False, False, False)) == "PORT"
    assert _code(lambda: decide(DEFAULT_HOST, 65536, False, False, False)) == "PORT"
    assert _code(lambda: decide(DEFAULT_HOST, -1, False, False, False)) == "PORT"
    assert _code(lambda: decide(DEFAULT_HOST, cast(int, True), False, False, False)) == "PORT"


def test_flags_must_be_bools() -> None:
    assert _code(
        lambda: decide(DEFAULT_HOST, DEFAULT_PORT, cast(bool, 1), False, False)
    ) == "BOUND"


def test_loopback_tls_is_https() -> None:
    got = decide(DEFAULT_HOST, DEFAULT_PORT, False, True, False)
    assert got.scheme == "https"
    assert got.host == DEFAULT_HOST


def test_record_cannot_store_an_open_or_cleartext_wildcard() -> None:
    assert _code(lambda: Bind("0.0.0.0", 8770, "http", "bearer")) == "REMOTE_PLAIN"
    assert _code(lambda: Bind(DEFAULT_HOST, 8770, "http", "none")) == "OPEN_AUTH"
    assert _code(lambda: Bind(DEFAULT_HOST, 8770, "ftp", "bearer")) == "SCHEME"


def test_bind_is_slotted() -> None:
    assert "__slots__" in Bind.__dict__ or hasattr(Bind, "__slots__")
