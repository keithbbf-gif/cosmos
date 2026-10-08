"""Fence claims, the claim log, and rebuild."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import pytest

from cosmos_hermes import Refuse, secret_shape
from kanban_fleet import (
    CARD_CAP,
    CLOCK_HI,
    FENCE_CAP,
    LOG_CAP,
    MAX_CONFIRMING_RETRIES,
    NAME_CAP,
    RETRY_CLASS,
    SCHEMA,
    ClaimRecord,
    Fleet,
    Hold,
    rebuild,
)


def _at(rows: tuple[ClaimRecord, ...], index: int) -> ClaimRecord:
    if index < 0 or index >= len(rows):
        raise AssertionError(index)
    return rows[index]


def _seal(prev: str, body: str) -> ClaimRecord:
    digest = hashlib.sha256(f"{prev}\n{body}".encode("utf-8")).hexdigest()
    return ClaimRecord(prev, body, digest)


def _refused_claim(fleet: Fleet, gateway: str, fence: str, at: int) -> str:
    try:
        fleet.claim("bisque", gateway, fence, at=at)
    except Refuse as exc:
        return exc.code
    raise AssertionError(gateway)


@dataclass(frozen=True, slots=True)
class _Story:
    first_gateway: str
    first_renewed: bool
    web_blocked: str
    released_gateway: str
    second_gateway: str
    second_renewed: bool
    rebuilt_match: bool
    renew_after: bool
    kiln_blocked: str
    digests: tuple[str, ...]


def _kiln_story() -> _Story:
    fleet = Fleet()
    first = fleet.claim("bisque", "kiln", "f-1", at=1_700_000_100)
    web_blocked = _refused_claim(fleet, "web", "f-9", 1_700_000_110)
    released = fleet.release("bisque", "kiln", "f-1", at=1_700_000_120)
    second = fleet.claim("bisque", "web", "f-2", at=1_700_000_130)
    rebuilt = rebuild(fleet.records())
    match = rebuilt.status() == fleet.status()
    renewed = rebuilt.claim("bisque", "web", "f-2", at=1_700_000_140)
    kiln_blocked = _refused_claim(rebuilt, "kiln", "f-3", 1_700_000_150)
    digests = tuple(row.digest for row in fleet.records())
    return _Story(
        first_gateway=first.gateway,
        first_renewed=first.renewed,
        web_blocked=web_blocked,
        released_gateway=released.gateway,
        second_gateway=second.gateway,
        second_renewed=second.renewed,
        rebuilt_match=match,
        renew_after=renewed.renewed,
        kiln_blocked=kiln_blocked,
        digests=digests,
    )


def test_schema() -> None:
    assert SCHEMA == "cosmos-hermes-kanban_fleet/1"
    assert RETRY_CLASS == "STALE"
    assert MAX_CONFIRMING_RETRIES == 1
    fleet = Fleet()
    assert fleet.status().schema == SCHEMA
    assert fleet.policy().schema == SCHEMA
    assert fleet.policy().card_cap == CARD_CAP
    assert fleet.policy().log_cap == LOG_CAP


def test_success_path_and_repr() -> None:
    fleet = Fleet()
    first = fleet.claim("bisque", "default", "fence-1", at=1)
    assert first.renewed is False
    assert first.gateway == "default"
    assert first.schema == SCHEMA
    again = fleet.claim("bisque", "default", "fence-1", at=2)
    assert again.renewed is True
    assert fleet.hold("bisque") == Hold("bisque", "default")
    released = fleet.release("bisque", "default", "fence-1", at=3)
    assert released.card == "bisque"
    assert released.gateway == "default"
    with pytest.raises(Refuse) as gone:
        fleet.hold("bisque")
    assert gone.value.code == "UNKNOWN_CARD"
    rebuilt = rebuild(fleet.records())
    assert rebuilt.status() == fleet.status()
    assert rebuilt.records() == fleet.records()
    assert rebuilt.policy() == fleet.policy()
    for item in (fleet, fleet.status(), fleet.policy(), first, again, released):
        assert secret_shape(repr(item)) is False
    for row in fleet.records():
        text = repr(row)
        assert "fence-1" not in text
        assert secret_shape(text) is False


def test_example_kanban_fleet() -> None:
    left = _kiln_story()
    right = _kiln_story()
    assert left == right
    assert left.first_gateway == "kiln"
    assert left.first_renewed is False
    assert left.web_blocked == "FENCE"
    assert left.released_gateway == "kiln"
    assert left.second_gateway == "web"
    assert left.second_renewed is False
    assert left.rebuilt_match is True
    assert left.renew_after is True
    assert left.kiln_blocked == "FENCE"
    assert len(left.digests) == 4


def test_other_gateway_is_fence() -> None:
    fleet = Fleet()
    fleet.claim("bisque", "kiln", "f-1", at=1)
    before = fleet.status()
    with pytest.raises(Refuse) as claimed:
        fleet.claim("bisque", "web", "f-2", at=2)
    assert claimed.value.code == "FENCE"
    with pytest.raises(Refuse) as released:
        fleet.release("bisque", "web", "f-1", at=2)
    assert released.value.code == "FENCE"
    assert fleet.status() == before
    assert fleet.hold("bisque").gateway == "kiln"


def test_unknown_card() -> None:
    fleet = Fleet()
    with pytest.raises(Refuse) as released:
        fleet.release("bisque", "kiln", "f-1", at=1)
    assert released.value.code == "UNKNOWN_CARD"
    with pytest.raises(Refuse) as missing:
        fleet.hold("glaze")
    assert missing.value.code == "UNKNOWN_CARD"
    assert fleet.status().holds == ()


def test_release_bounds_inputs() -> None:
    fleet = Fleet()
    fleet.claim("bisque", "kiln", "f-1", at=1)
    with pytest.raises(Refuse) as text:
        fleet.release("bisque", None, "f-1", at=2)
    assert text.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as empty:
        fleet.release("bisque", "kiln", "", at=2)
    assert empty.value.code == "EMPTY"
    with pytest.raises(Refuse) as secret:
        fleet.release("bisque", "kiln", "sk-abcdefghij", at=2)
    assert secret.value.code == "SECRET"
    assert fleet.hold("bisque").gateway == "kiln"
    assert len(fleet.records()) == 2


def test_stale_fence_retries_once() -> None:
    fleet = Fleet()
    fleet.claim("bisque", "kiln", "f-1", at=1)
    with pytest.raises(Refuse) as stale:
        fleet.claim("bisque", "kiln", "f-2", at=2)
    assert stale.value.code == "STALE"
    assert stale.value.code == RETRY_CLASS
    renewed = fleet.claim("bisque", "kiln", "f-1", at=3)
    assert renewed.renewed is True
    with pytest.raises(Refuse) as again:
        fleet.release("bisque", "kiln", "f-9", at=4)
    assert again.value.code == "STALE"
    with pytest.raises(Refuse) as capped:
        fleet.release("bisque", "kiln", "f-8", at=5)
    assert capped.value.code == "RETRY_CAP"
    with pytest.raises(Refuse) as stuck:
        fleet.release("bisque", "kiln", "f-1", at=6)
    assert stuck.value.code == "RETRY_CAP"
    with pytest.raises(Refuse) as other:
        fleet.claim("bisque", "web", "f-3", at=6)
    assert other.value.code == "FENCE"
    rebuilt = rebuild(fleet.records())
    with pytest.raises(Refuse) as still:
        rebuilt.release("bisque", "kiln", "f-1", at=7)
    assert still.value.code == "RETRY_CAP"
    assert rebuilt.hold("bisque").gateway == "kiln"
    assert rebuilt.status().holds == fleet.status().holds


def test_replay_of_released_fence() -> None:
    fleet = Fleet()
    fleet.claim("bisque", "kiln", "f-1", at=1)
    fleet.release("bisque", "kiln", "f-1", at=2)
    with pytest.raises(Refuse) as blocked:
        fleet.claim("bisque", "web", "f-1", at=3)
    assert blocked.value.code == "REPLAY"
    taken = fleet.claim("bisque", "web", "f-2", at=3)
    assert taken.gateway == "web"
    assert taken.renewed is False
    rebuilt = rebuild(fleet.records())
    assert rebuilt.hold("bisque").gateway == "web"
    rebuilt.release("bisque", "web", "f-2", at=4)
    with pytest.raises(Refuse) as again:
        rebuilt.claim("bisque", "kiln", "f-1", at=5)
    assert again.value.code == "REPLAY"
    fresh = rebuilt.claim("bisque", "kiln", "f-3", at=5)
    assert fresh.gateway == "kiln"
    assert fresh.renewed is False


def test_clock_moves_forward_only() -> None:
    fleet = Fleet()
    fleet.claim("bisque", "kiln", "f-1", at=10)
    with pytest.raises(Refuse) as blocked:
        fleet.claim("glaze", "kiln", "f-2", at=9)
    assert blocked.value.code == "CLOCK"
    with pytest.raises(Refuse) as renew:
        fleet.claim("bisque", "kiln", "f-1", at=9)
    assert renew.value.code == "CLOCK"
    assert fleet.status().holds == (Hold("bisque", "kiln"),)
    assert len(fleet.records()) == 2
    fleet.claim("glaze", "writer", "f-2", at=10)
    assert fleet.status().holds == (Hold("bisque", "kiln"), Hold("glaze", "writer"))


def test_policy_cap_is_not_raised() -> None:
    fleet = Fleet(card_cap=10_000, log_cap=10_000)
    view = fleet.policy()
    assert view.card_cap == CARD_CAP
    assert view.log_cap == LOG_CAP
    assert view.asked_card_cap == 10_000
    assert view.asked_log_cap == 10_000
    assert view.card_capped is True
    assert view.log_capped is True
    rebuilt = rebuild(fleet.records())
    assert rebuilt.policy() == fleet.policy()
    assert rebuilt.status() == fleet.status()
    cards = Fleet(card_cap=1)
    cards.claim("bisque", "kiln", "f-1", at=1)
    with pytest.raises(Refuse) as full:
        cards.claim("glaze", "kiln", "f-2", at=2)
    assert full.value.code == "CAP"
    cards.release("bisque", "kiln", "f-1", at=2)
    moved = cards.claim("glaze", "kiln", "f-2", at=3)
    assert moved.gateway == "kiln"
    logs = Fleet(log_cap=2)
    logs.claim("bisque", "kiln", "f-1", at=1)
    with pytest.raises(Refuse) as capped:
        logs.release("bisque", "kiln", "f-1", at=2)
    assert capped.value.code == "CAP"
    assert logs.hold("bisque").gateway == "kiln"
    with pytest.raises(Refuse) as flag:
        Fleet(card_cap=True)
    assert flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as zero:
        Fleet(log_cap=0)
    assert zero.value.code == "OUT_OF_RANGE"


def test_malformed_inputs() -> None:
    fleet = Fleet()
    cases: tuple[tuple[str, object, object, object, object], ...] = (
        ("NOT_TEXT", 1, "kiln", "f-1", 1),
        ("NOT_TEXT", "bisque", None, "f-1", 1),
        ("NOT_TEXT", "bisque", "kiln", b"f-1", 1),
        ("NULL_BYTE", "bis\x00que", "kiln", "f-1", 1),
        ("OVERSIZE", "a" * (NAME_CAP + 1), "kiln", "f-1", 1),
        ("OVERSIZE", "bisque", "kiln", "f" * (FENCE_CAP + 1), 1),
        ("EMPTY", "", "kiln", "f-1", 1),
        ("EMPTY", "bisque", "", "f-1", 1),
        ("EMPTY", "bisque", "kiln", "", 1),
        ("BAD_ID", "bisque glaze", "kiln", "f-1", 1),
        ("BAD_ID", "bisque", "kiln", "f 1", 1),
        ("SECRET", "sk-abcdefghij", "kiln", "f-1", 1),
        ("SECRET", "bisque", "api_key=abcdef", "f-1", 1),
        ("SECRET", "bisque", "kiln", "Bearer abcdefghijk", 1),
        ("NOT_INT", "bisque", "kiln", "f-1", True),
        ("NOT_INT", "bisque", "kiln", "f-1", "1"),
        ("OUT_OF_RANGE", "bisque", "kiln", "f-1", -1),
        ("OUT_OF_RANGE", "bisque", "kiln", "f-1", CLOCK_HI + 1),
    )
    for code, card, gateway, fence, at in cases:
        with pytest.raises(Refuse) as blocked:
            fleet.claim(card, gateway, fence, at=at)
        assert blocked.value.code == code
    assert fleet.status().records == 1
    assert fleet.status().holds == ()


def test_chain_duplicate_and_bad_record() -> None:
    fleet = Fleet()
    fleet.claim("bisque", "kiln", "f-1", at=1)
    fleet.release("bisque", "kiln", "f-1", at=2)
    rows = fleet.records()
    with pytest.raises(Refuse) as chain:
        rebuild((_at(rows, 0), _at(rows, 2), _at(rows, 1)))
    assert chain.value.code == "CHAIN"
    first = _at(rows, 0)
    with pytest.raises(Refuse) as mismatch:
        ClaimRecord(first.prev, first.body, "ab" * 32)
    assert mismatch.value.code == "CHAIN"
    second = _at(rows, 1)
    forged = _seal(second.digest, second.body)
    with pytest.raises(Refuse) as dup:
        rebuild((_at(rows, 0), second, forged))
    assert dup.value.code == "DUPLICATE"
    naked = _seal("0" * 64, "claim\t1\tbisque\tkiln\tf-1\t1\t0")
    with pytest.raises(Refuse) as missing_policy:
        rebuild((naked,))
    assert missing_policy.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as empty:
        rebuild(())
    assert empty.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as kind:
        rebuild(("nope",))
    assert kind.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as shape:
        ClaimRecord("0" * 64, "broken", "cd" * 32)
    assert shape.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as listed:
        rebuild([])
    assert listed.value.code == "BAD_RECORD"
