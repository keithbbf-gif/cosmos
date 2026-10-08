"""Account holds a person and a door id. It does not hold key bytes."""

from __future__ import annotations

from account import SCHEMA, Account, open_account
from cosmos_federation import Refuse, secret_shape


def test_open_account_keeps_a_person_and_a_door_id() -> None:
    account = open_account("Ada", "OpenRouter", "cred-peer-1", 1_700_000_000)
    assert isinstance(account, Account)
    assert account.name == "Ada"
    assert account.door == "openrouter"
    assert account.credential_id == "cred-peer-1"
    assert account.created_epoch == 1_700_000_000
    assert SCHEMA == "cosmos-federation-account/1"
    assert "cred-peer-1" in repr(account)
    assert "sk-" not in repr(account)
    assert not any(
        isinstance(part, (bytes, bytearray))
        for part in (account.name, account.door, account.credential_id)
    )
    xai = open_account("Bea", "xai", "cred-peer-2", 0)
    assert xai.door == "xai"
    assert xai.created_epoch == 0


def test_anthropic_stays_off() -> None:
    try:
        open_account("Ada", "anthropic", "cred-peer-1", 0)
    except Refuse as exc:
        assert exc.code == "ANTHROPIC_OFF"
    else:
        raise AssertionError("anthropic")


def test_secret_shaped_credential_id_is_refused() -> None:
    raw = "sk-" + "a" * 12
    assert secret_shape(raw)
    try:
        open_account("Ada", "openrouter", raw, 0)
    except Refuse as exc:
        assert exc.code == "SECRET"
        assert raw not in str(exc)
        assert "sk-" not in str(exc)
    else:
        raise AssertionError("secret")
    long_raw = "sk-" + "c" * 90
    try:
        open_account("Ada", "openrouter", long_raw, 0)
    except Refuse as exc:
        assert exc.code == "SECRET"
        assert long_raw not in str(exc)
    else:
        raise AssertionError("long secret")
    long_name = "sk-" + "d" * 90
    try:
        open_account(long_name, "openrouter", "cred-peer-1", 0)
    except Refuse as exc:
        assert exc.code == "SECRET"
        assert exc.detail == ""
        assert long_name not in str(exc)
    else:
        raise AssertionError("long name")


def test_repr_stays_clean_if_a_caller_pokes_a_secret() -> None:
    account = open_account("Ada", "xai", "cred-peer-1", 0)
    raw = "sk-" + "b" * 12
    object.__setattr__(account, "credential_id", raw)
    text = repr(account)
    assert raw not in text
    assert "sk-" not in text


def test_bounds_refuse_blank_name_and_negative_now() -> None:
    try:
        open_account("  ", "openrouter", "cred-peer-1", 0)
    except Refuse as exc:
        assert exc.code == "BOUND"
        assert exc.detail == "name"
    else:
        raise AssertionError("blank")
    try:
        open_account("n" * 81, "openrouter", "cred-peer-1", 0)
    except Refuse as exc:
        assert exc.code == "BOUND"
        assert exc.detail == "name"
    else:
        raise AssertionError("long")
    kept = open_account("n" * 80, "openrouter", "cred-peer-1", 0)
    assert len(kept.name) == 80
    try:
        open_account("Ada", "openrouter", "cred-peer-1", -1)
    except Refuse as exc:
        assert exc.code == "BOUND"
        assert exc.detail == "now"
    else:
        raise AssertionError("now")
    try:
        open_account("Ada", "openrouter", "", 0)
    except Refuse as exc:
        assert exc.code == "BOUND"
        assert exc.detail == "credential_id"
    else:
        raise AssertionError("id")
    try:
        open_account("Ada", "other", "cred-peer-1", 0)
    except Refuse as exc:
        assert exc.code == "DOOR"
    else:
        raise AssertionError("door")
