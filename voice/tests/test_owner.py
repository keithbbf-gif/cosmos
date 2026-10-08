"""AudioOwner exclusivity, renewal, and expiry on an injected clock."""

from __future__ import annotations

import time
from collections.abc import Callable
from itertools import count

from cosmos_voice.errors import VoiceError
from cosmos_voice.owner import AudioOwner
from cosmos_voice.types import OWNER_TTL_S


class CellClock:
    """List clock. ``stamps[0]`` is the reading; ``set`` replaces it."""

    def __init__(self, start: float = 0.0) -> None:
        self.stamps = [start]

    def __call__(self) -> float:
        return self.stamps[0]

    def set(self, at: float) -> None:
        self.stamps[0] = at


def _raised(kind: str, call: Callable[[], object]) -> VoiceError:
    try:
        call()
    except VoiceError as err:
        assert err.kind == kind
        return err
    raise AssertionError(kind)


def _claim(owner: AudioOwner, name: str) -> Callable[[], object]:
    def call() -> object:
        return owner.claim(name)

    return call


def test_default_clock_is_monotonic() -> None:
    """Omitting ``now`` uses ``time.monotonic`` and the shared 30s ttl."""
    owner = AudioOwner()
    before = time.monotonic()
    row = owner.claim("phone")
    after = time.monotonic()
    expires = row["expires_at"]
    assert isinstance(expires, float)
    assert before + OWNER_TTL_S <= expires <= after + OWNER_TTL_S
    assert row["owner"] == "phone"
    assert row["expired"] is False
    assert owner.current() == "phone"
    assert owner.expired() is False


def test_bad_mode_rejects_non_holders() -> None:
    """``none`` and unknown names are not holders."""
    clock = CellClock(0.0)
    owner = AudioOwner(now=clock, ttl_s=10.0)
    for name in ("none", "", "PHONE", "both", "desktop "):
        err = _raised("BAD_MODE", _claim(owner, name))
        assert err.detail == "owner must be phone or desktop"
    assert owner.current() == "none"
    assert owner.expired() is False
    assert owner.allows_capture("phone") is False
    assert owner.allows_playback("desktop") is False


def test_exclusive_claim_is_busy_until_expiry() -> None:
    """A live holder blocks the other side. Expiry frees the lease."""
    clock = CellClock(0.0)
    owner = AudioOwner(now=clock, ttl_s=10.0)
    owner.claim("phone")
    err = _raised("AUDIO_BUSY", lambda: owner.claim("desktop"))
    assert err.detail == "phone"
    assert owner.current() == "phone"
    assert owner.allows_capture("phone") is True
    assert owner.allows_playback("phone") is True
    assert owner.allows_capture("desktop") is False
    assert owner.allows_playback("desktop") is False
    assert owner.allows_capture("none") is False
    clock.set(10.0)
    assert owner.expired() is True
    assert owner.current() == "none"
    assert owner.allows_capture("phone") is False
    assert owner.allows_playback("phone") is False
    taken = owner.claim("desktop")
    assert taken["owner"] == "desktop"
    assert taken["expired"] is False
    assert owner.current() == "desktop"
    assert owner.allows_playback("desktop") is True
    assert owner.allows_capture("phone") is False


def test_same_owner_renews_deadline() -> None:
    """A second claim by the holder moves the deadline forward."""
    clock = CellClock(0.0)
    owner = AudioOwner(now=clock, ttl_s=10.0)
    first = owner.claim("phone")
    assert first["expires_at"] == 10.0
    clock.set(4.0)
    second = owner.claim("phone")
    assert second["owner"] == "phone"
    assert second["expires_at"] == 14.0
    assert second["expired"] is False
    clock.set(12.0)
    assert owner.current() == "phone"
    assert owner.expired() is False
    clock.set(14.0)
    assert owner.expired() is True
    assert owner.current() == "none"


def test_release_only_by_live_holder() -> None:
    """The holder may release. The other side, and a second release, are busy."""
    clock = CellClock(1.0)
    owner = AudioOwner(now=clock, ttl_s=5.0)
    owner.claim("desktop")
    err = _raised("AUDIO_BUSY", lambda: owner.release("phone"))
    assert err.detail == "desktop"
    assert owner.current() == "desktop"
    row = owner.release("desktop")
    assert row["owner"] == "none"
    assert row["expired"] is False
    assert row["expires_at"] == 0.0
    assert owner.current() == "none"
    assert owner.expired() is False
    assert owner.allows_capture("desktop") is False
    assert owner.allows_playback("desktop") is False
    idle = _raised("AUDIO_BUSY", lambda: owner.release("desktop"))
    assert idle.detail == "none"
    owner.claim("phone")
    assert owner.current() == "phone"


def test_expired_holder_cannot_release() -> None:
    """After the deadline the old name is not the holder."""
    clock = CellClock(0.0)
    owner = AudioOwner(now=clock, ttl_s=3.0)
    owner.claim("phone")
    clock.set(3.0)
    err = _raised("AUDIO_BUSY", lambda: owner.release("phone"))
    assert err.detail == "none"
    assert owner.current() == "none"


def test_list_clock_pops_once_per_call() -> None:
    """A list of stamps is the clock. Each public call reads it once."""
    stamps = [0.0, 5.0, 5.0, 5.0, 31.0]

    def now() -> float:
        return stamps.pop(0)

    owner = AudioOwner(now=now, ttl_s=30.0)
    owner.claim("desktop")
    assert owner.current() == "desktop"
    assert owner.allows_capture("desktop") is True
    assert owner.expired() is False
    assert owner.current() == "none"
    assert stamps == []


def test_counter_clock_expires_on_the_deadline() -> None:
    """An itertools counter is a valid injected clock."""
    ticks = count(0, 15)

    def now() -> float:
        return float(next(ticks))

    owner = AudioOwner(now=now, ttl_s=30.0)
    owner.claim("phone")
    assert owner.current() == "phone"
    assert owner.expired() is True
    assert owner.allows_playback("phone") is False
    assert owner.allows_capture("desktop") is False
