"""Day-one bearer and install key. Scratch plus PathJail. No tmp paths."""

from __future__ import annotations

import base64
import hashlib
import os
from collections.abc import Callable
from pathlib import Path
from secrets import SCHEMA, acknowledge, mint, write_files

import pytest

from cosmos_federation import PathJail, Refuse

_TOKEN_RAW = bytes(range(24))
_KEY_RAW = bytes(range(32))
_EPOCH = 1_700_000_000


def _draw_pair() -> Callable[[int], bytes]:
    pending = [_TOKEN_RAW, _KEY_RAW]

    def draw(n: int) -> bytes:
        blob = pending.pop(0)
        if len(blob) != n:
            raise AssertionError(n)
        return blob

    return draw


def _bearer() -> str:
    return base64.urlsafe_b64encode(_TOKEN_RAW).rstrip(b"=").decode("ascii")


def test_schema_names_this_slot() -> None:
    assert SCHEMA == "cosmos-federation-secrets/1"


def test_mint_matches_token_urlsafe_and_hashes_file_bodies() -> None:
    minted = mint(_draw_pair(), _EPOCH)
    bearer = _bearer()
    assert minted.show_token == bearer
    assert "=" not in bearer
    assert minted.install_key == _KEY_RAW
    assert minted.minted_epoch == _EPOCH
    assert minted.token_id == hashlib.sha256(bearer.encode("utf-8")).hexdigest()[:12]
    assert minted.key_id == hashlib.sha256(_KEY_RAW).hexdigest()[:12]
    assert len(minted.token_id) == 12
    assert len(minted.key_id) == 12
    text = repr(minted)
    assert bearer not in text
    assert _KEY_RAW.hex() not in text
    assert "held" in text


def test_acknowledge_then_repr_omits_bearer() -> None:
    minted = mint(_draw_pair(), _EPOCH)
    bearer = minted.show_token
    key = minted.install_key
    assert isinstance(bearer, str) and bearer != ""
    assert key is not None
    acked = acknowledge(minted)
    text = repr(acked)
    assert bearer not in text
    assert key.hex() not in text
    assert repr(key) not in text
    assert acked.show_token is None
    assert acked.install_key is None
    assert acked.token_id == minted.token_id
    assert acked.key_id == minted.key_id
    assert acked.minted_epoch == minted.minted_epoch
    assert acknowledge(acked) == acked


def test_write_files_reads_back_owner_mode(scratch: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    jail = PathJail(scratch)
    minted = mint(_draw_pair(), _EPOCH)
    bearer = minted.show_token
    key = minted.install_key
    assert bearer is not None and key is not None
    modes: list[int] = []
    real_open = os.open

    def spy(path: str, flags: int, mode: int = 0o777) -> int:
        modes.append(mode)
        assert flags & os.O_CREAT
        assert flags & os.O_TRUNC
        assert flags & os.O_WRONLY
        return real_open(path, flags, mode)

    monkeypatch.setattr(os, "open", spy)
    write_files(jail, bearer, key)
    assert modes == [0o600, 0o600]
    token_path = jail.contain("config/api_token.txt")
    key_path = jail.contain("config/install_key.bin")
    assert token_path.read_bytes() == bearer.encode("utf-8")
    assert b"\n" not in token_path.read_bytes()
    assert key_path.read_bytes() == key
    assert scratch.resolve() in token_path.parents
    assert scratch.resolve() in key_path.parents


def test_write_files_refuses_secret_shaped_bearer(scratch: Path) -> None:
    jail = PathJail(scratch)
    shaped = "sk-" + ("a" * 12)
    with pytest.raises(Refuse) as caught:
        write_files(jail, shaped, bytes(32))
    assert caught.value.code == "SECRET_SHAPE"
    padded = "\n" + "xai-" + ("b" * 8) + " "
    with pytest.raises(Refuse) as caught:
        write_files(jail, padded, bytes(32))
    assert caught.value.code == "SECRET_SHAPE"
    assert list(scratch.iterdir()) == []


def test_blank_token_and_bad_key_write_nothing(scratch: Path) -> None:
    jail = PathJail(scratch)
    good_key = bytes(32)
    for token in ("", " ", "\n", "\t\r"):
        with pytest.raises(Refuse) as caught:
            write_files(jail, token, good_key)
        assert caught.value.code == "BLANK_TOKEN"
    for key in (b"", b"\x00" * 31, b"\x00" * 33):
        with pytest.raises(Refuse) as caught:
            write_files(jail, "dayone-bearer", key)
        assert caught.value.code == "BAD_KEY"
    assert list(scratch.iterdir()) == []


def test_short_draw_refuses() -> None:
    def draw(n: int) -> bytes:
        return b"\x00" * (n - 1)

    with pytest.raises(Refuse) as caught:
        mint(draw, _EPOCH)
    assert caught.value.code == "DRAW"


def test_bad_epoch_does_not_draw() -> None:
    def draw(n: int) -> bytes:
        raise AssertionError(n)

    for now in (-1, True):
        with pytest.raises(Refuse) as caught:
            mint(draw, now)
        assert caught.value.code == "BOUND"
