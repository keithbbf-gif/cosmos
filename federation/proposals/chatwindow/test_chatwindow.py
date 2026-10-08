"""Pins for the day-one chat window and the one-time loopback nonce."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from chatwindow import COOKIE_NAME, SCHEMA, Cookie, issue_nonce, page, redeem
from cosmos_federation import NONCE_TTL_S, ROUTE_CHAT, Refuse, secret_shape


def _draw(raw: bytes) -> Callable[[int], bytes]:
    def draw(n: int) -> bytes:
        assert len(raw) == n
        return raw

    return draw


def test_redeem_success_sets_loopback_cookie() -> None:
    nonce = issue_nonce(_draw(bytes(range(16))), 1_700_000_000)
    cookie = redeem(nonce, nonce.code, 1_700_000_000, False)
    assert isinstance(cookie, Cookie)
    assert cookie.name == COOKIE_NAME
    assert cookie.http_only is True
    assert cookie.host == "127.0.0.1"
    assert cookie.value_id == nonce.value_id
    assert cookie.value_id != nonce.code
    assert nonce.code not in repr(nonce)
    assert nonce.code not in repr(cookie)
    assert not secret_shape(repr(nonce))
    assert not secret_shape(repr(cookie))
    assert SCHEMA == "cosmos-federation-chatwindow/1"


def test_redeem_refuses_remote_without_spending() -> None:
    nonce = issue_nonce(_draw(bytes(range(16, 32))), 50)
    try:
        redeem(nonce, nonce.code, 50, True)
    except Refuse as exc:
        assert exc.code == "REMOTE"
    else:
        raise AssertionError("remote")
    cookie = redeem(nonce, nonce.code, 50, False)
    assert cookie.value_id == nonce.value_id


def test_redeem_refuses_mismatch_without_spending() -> None:
    nonce = issue_nonce(_draw(bytes(range(32, 48))), 10)
    try:
        redeem(nonce, "ab" * 16, 10, False)
    except Refuse as exc:
        assert exc.code == "NONCE"
    else:
        raise AssertionError("mismatch")
    assert redeem(nonce, nonce.code, 10, False).http_only is True


def test_redeem_refuses_replay() -> None:
    nonce = issue_nonce(_draw(bytes(range(48, 64))), 20)
    assert redeem(nonce, nonce.code, 20, False).host == "127.0.0.1"
    try:
        redeem(nonce, nonce.code, 20, False)
    except Refuse as exc:
        assert exc.code == "NONCE_USED"
    else:
        raise AssertionError("replay")


def test_redeem_refuses_expiry_and_accepts_the_ttl_edge() -> None:
    issued = 80
    nonce = issue_nonce(_draw(bytes((9,)) * 16), issued)
    try:
        redeem(nonce, nonce.code, issued + NONCE_TTL_S + 1, False)
    except Refuse as exc:
        assert exc.code == "NONCE_EXPIRED"
    else:
        raise AssertionError("expired")
    fresh = issue_nonce(_draw(bytes((7,)) * 16), issued)
    cookie = redeem(fresh, fresh.code, issued + NONCE_TTL_S, False)
    assert cookie.value_id == fresh.value_id
    assert cookie.http_only is True


def test_page_matches_dayone_html_and_has_no_secret() -> None:
    html = page()
    disk = Path(__file__).resolve().parent.joinpath("dayone.html").read_text(encoding="utf-8")
    assert html == disk
    assert "sk-" not in html.casefold()
    assert "bearer" not in html.casefold()
    assert "nonce" not in html.casefold()
    assert not secret_shape(html)
    assert ROUTE_CHAT in html
    assert "No messages yet." in html
    assert "<ol id=\"transcript\"></ol>" in html
    assert "usd_micros" in html
    assert "JSON.stringify" in html
    assert "http://127.0.0.1:8770/dayone" in html
    assert "<style>" in html and "</style>" in html
    assert "<script>" in html and "</script>" in html
    for invented in ("How can I help", "As an AI", "Hello, I"):
        assert invented not in html
