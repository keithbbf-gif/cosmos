"""One fencing token per card. A second gateway cannot mark the same card running.

The claim log is a hash chain. ``rebuild`` replays it. No thread and no spawn.
"""

from __future__ import annotations

import hashlib
import hmac
import re
from dataclasses import dataclass
from typing import Final, Literal, NoReturn

from cosmos_hermes import Refuse, bound_int, bound_text, const_eq, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-kanban_fleet/1"
CARD_CAP: Final[int] = 32
LOG_CAP: Final[int] = 256
NAME_CAP: Final[int] = 64
FENCE_CAP: Final[int] = 128
CLOCK_HI: Final[int] = 4_000_000_000
MAX_CONFIRMING_RETRIES: Final[int] = 1
RETRY_CLASS: Final[str] = "STALE"

_CAP_HI: Final[int] = 1_000_000_000
_BODY_MAX: Final[int] = 256
_GENESIS: Final[str] = "0" * 64
_KINDS: Final[frozenset[str]] = frozenset(
    {"policy", "claim", "renew", "release", "retry", "cap"}
)
_HELD_KINDS: Final[frozenset[str]] = frozenset({"renew", "release", "retry", "cap"})
_DIGITS: Final[frozenset[str]] = frozenset("0123456789")
_NAME: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$")
_FENCE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")

_Kind = Literal["claim", "renew", "release", "retry", "cap"]
_Judge = Literal["renew", "fence", "stale"]


@dataclass(frozen=True, slots=True)
class Policy:
    """Caps that are enforced. A higher ask is stored and is not applied."""

    schema: str
    card_cap: int
    log_cap: int
    asked_card_cap: int
    asked_log_cap: int
    card_capped: bool
    log_capped: bool

    def __repr__(self) -> str:
        return (
            f"Policy(card_cap={self.card_cap}, log_cap={self.log_cap}, "
            f"asked_card_cap={self.asked_card_cap}, asked_log_cap={self.asked_log_cap})"
        )


@dataclass(frozen=True, slots=True)
class Claim:
    """Descriptor for a new hold or a renew. Carries no fence."""

    schema: str
    card: str
    gateway: str
    renewed: bool
    at: int
    digest: str

    def __repr__(self) -> str:
        return (
            f"Claim(card={self.card!r}, gateway={self.gateway!r}, "
            f"renewed={self.renewed}, at={self.at})"
        )


@dataclass(frozen=True, slots=True)
class Release:
    """Descriptor for a release. Recording it does not stop a process."""

    schema: str
    card: str
    gateway: str
    at: int
    digest: str

    def __repr__(self) -> str:
        return f"Release(card={self.card!r}, gateway={self.gateway!r}, at={self.at})"


@dataclass(frozen=True, slots=True)
class Hold:
    """Public holder of one card. The fence stays in the log."""

    card: str
    gateway: str


@dataclass(frozen=True, slots=True)
class FleetStatus:
    """Point-in-time projection. Reading it does not claim."""

    schema: str
    holds: tuple[Hold, ...]
    records: int
    last_at: int
    card_cap: int
    log_cap: int
    asked_card_cap: int
    asked_log_cap: int
    card_capped: bool
    log_capped: bool


@dataclass(frozen=True, slots=True)
class ClaimRecord:
    """One committed row. ``digest`` is sha256 of ``prev`` and ``body``."""

    prev: str
    body: str
    digest: str

    def __post_init__(self) -> None:
        _vet(self.prev, self.body, self.digest)

    def __repr__(self) -> str:
        return f"ClaimRecord(digest={self.digest!r})"


@dataclass(frozen=True, slots=True)
class _Live:
    gateway: str
    fence: str
    tries: int
    locked: bool


def _chain(prev: str, body: str) -> str:
    return hashlib.sha256(f"{prev}\n{body}".encode("utf-8")).hexdigest()


def _note(prev: str, body: str) -> ClaimRecord:
    digest = _chain(prev, body)
    record = ClaimRecord.__new__(ClaimRecord)
    object.__setattr__(record, "prev", prev)
    object.__setattr__(record, "body", body)
    object.__setattr__(record, "digest", digest)
    return record


def _parse_u(text: str, lo: int, hi: int) -> int:
    if text == "0":
        value = 0
    elif text == "" or len(text) > 10 or text[0] == "0":
        raise Refuse("BAD_RECORD")
    else:
        for ch in text:
            if ch not in _DIGITS:
                raise Refuse("BAD_RECORD")
        value = int(text)
    try:
        return bound_int(value, lo, hi)
    except Refuse as exc:
        if exc.code == "OUT_OF_RANGE":
            raise Refuse("BAD_RECORD") from None
        raise


def _name(value: object) -> str:
    text = bound_text(value, NAME_CAP)
    if text == "":
        raise Refuse("EMPTY")
    if secret_shape(text):
        raise Refuse("SECRET")
    if _NAME.fullmatch(text) is None:
        raise Refuse("BAD_ID")
    return text


def _fence(value: object) -> str:
    text = bound_text(value, FENCE_CAP)
    if text == "":
        raise Refuse("EMPTY")
    if secret_shape(text):
        raise Refuse("SECRET")
    if _FENCE.fullmatch(text) is None:
        raise Refuse("BAD_ID")
    return text


def _clock(value: object) -> int:
    return bound_int(value, 0, CLOCK_HI)


def _resolve(asked: object, ceiling: int) -> tuple[int, int, bool]:
    if asked is None:
        return ceiling, ceiling, False
    raw = bound_int(asked, 1, _CAP_HI)
    if raw > ceiling:
        return ceiling, raw, True
    return raw, raw, False


def _encode_flags(card_capped: bool, log_capped: bool) -> str:
    return str((1 if card_capped else 0) + (2 if log_capped else 0))


def _flag_pair(
    text: str,
    applied_card: int,
    applied_log: int,
    asked_card: int,
    asked_log: int,
) -> tuple[bool, bool]:
    if text not in {"0", "1", "2", "3"}:
        raise Refuse("BAD_RECORD")
    card_capped = text in {"1", "3"}
    log_capped = text in {"2", "3"}
    if card_capped != (asked_card > CARD_CAP):
        raise Refuse("BAD_RECORD")
    if log_capped != (asked_log > LOG_CAP):
        raise Refuse("BAD_RECORD")
    if applied_card != (CARD_CAP if card_capped else asked_card):
        raise Refuse("BAD_RECORD")
    if applied_log != (LOG_CAP if log_capped else asked_log):
        raise Refuse("BAD_RECORD")
    return card_capped, log_capped


def _tries_ok(kind: str, tries: str) -> None:
    if kind in {"claim", "renew", "release"} and tries != "0":
        raise Refuse("BAD_RECORD")
    if kind == "retry" and tries != "1":
        raise Refuse("BAD_RECORD")
    if kind == "cap" and tries != "2":
        raise Refuse("BAD_RECORD")
    if kind == "policy" and tries not in {"0", "1", "2", "3"}:
        raise Refuse("BAD_RECORD")


def _shape(body: str) -> None:
    if "\n" in body or "\r" in body or "\t\t" in body:
        raise Refuse("BAD_RECORD")
    parts = body.split("\t")
    if len(parts) != 7:
        raise Refuse("BAD_RECORD")
    kind = parts[0]
    if kind not in _KINDS or parts[1] == "":
        raise Refuse("BAD_RECORD")
    if kind == "policy":
        applied_card = _parse_u(parts[2], 1, CARD_CAP)
        applied_log = _parse_u(parts[3], 1, LOG_CAP)
        asked_card = _parse_u(parts[4], 1, _CAP_HI)
        asked_log = _parse_u(parts[5], 1, _CAP_HI)
        _flag_pair(parts[6], applied_card, applied_log, asked_card, asked_log)
        return
    _name(parts[2])
    _name(parts[3])
    _fence(parts[4])
    _parse_u(parts[5], 0, CLOCK_HI)
    _tries_ok(kind, parts[6])


def _vet(prev: object, body: object, digest: object) -> None:
    prev_text = bound_text(prev, 64)
    body_text = bound_text(body, _BODY_MAX)
    digest_text = bound_text(digest, 64)
    if secret_shape(body_text):
        raise Refuse("SECRET")
    if _HEX.fullmatch(prev_text) is None or _HEX.fullmatch(digest_text) is None:
        raise Refuse("BAD_RECORD")
    _shape(body_text)
    expected = _chain(prev_text, body_text)
    if not hmac.compare_digest(digest_text, expected):
        raise Refuse("CHAIN")


def _judge(live: _Live, gate: str, token: str) -> _Judge:
    gate_ok = const_eq(live.gateway, gate)
    token_ok = const_eq(live.fence, token)
    if gate_ok and token_ok:
        return "renew"
    if gate_ok:
        return "stale"
    return "fence"


def _as_records(records: object) -> tuple[ClaimRecord, ...]:
    if not isinstance(records, tuple) or len(records) == 0:
        raise Refuse("BAD_RECORD")
    out: list[ClaimRecord] = []
    for item in records:
        if not isinstance(item, ClaimRecord):
            raise Refuse("BAD_RECORD")
        out.append(item)
    return tuple(out)


class Fleet:
    """In-memory fence table for one board. Methods never start a gateway."""

    __slots__ = (
        "_records",
        "_ids",
        "_holds",
        "_burned",
        "_last_at",
        "_policy",
    )

    _records: list[ClaimRecord]
    _ids: set[str]
    _holds: dict[str, _Live]
    _burned: dict[str, tuple[str, ...]]
    _last_at: int
    _policy: Policy | None

    def __init__(
        self,
        *,
        card_cap: object = None,
        log_cap: object = None,
    ) -> None:
        """Open an empty log. A cap above policy is recorded and is not applied."""
        self._blank()
        applied_card, asked_card, card_capped = _resolve(card_cap, CARD_CAP)
        applied_log, asked_log, log_capped = _resolve(log_cap, LOG_CAP)
        self._commit_policy(
            applied_card,
            applied_log,
            asked_card,
            asked_log,
            card_capped,
            log_capped,
        )

    def claim(self, card: object, gateway: object, fence: object, *, at: object) -> Claim:
        """Hold ``card`` or renew the same gateway and fence."""
        card_id = _name(card)
        gate = _name(gateway)
        token = _fence(fence)
        stamp = _clock(at)
        live = self._holds.get(card_id)
        if live is None:
            record = self._commit_event("claim", card_id, gate, token, stamp, "0", checked=True)
            return Claim(SCHEMA, card_id, gate, False, stamp, record.digest)
        return self._claim_held(live, card_id, gate, token, stamp)

    def release(self, card: object, gateway: object, fence: object, *, at: object) -> Release:
        """Drop a hold. Only the holding gateway and live fence may release."""
        card_id = _name(card)
        gate = _name(gateway)
        token = _fence(fence)
        stamp = _clock(at)
        live = self._holds.get(card_id)
        if live is None:
            raise Refuse("UNKNOWN_CARD")
        kind = _judge(live, gate, token)
        if kind == "fence":
            raise Refuse("FENCE")
        if stamp < self._last_at:
            raise Refuse("CLOCK")
        if live.locked:
            raise Refuse("RETRY_CAP")
        if kind == "stale":
            self._mismatch(live, card_id, gate, token, stamp)
        record = self._commit_event(
            "release", card_id, gate, token, stamp, "0", checked=True
        )
        return Release(SCHEMA, card_id, gate, stamp, record.digest)

    def hold(self, card: object) -> Hold:
        """Return the current holder. An unknown card is refused."""
        card_id = _name(card)
        live = self._holds.get(card_id)
        if live is None:
            raise Refuse("UNKNOWN_CARD")
        return Hold(card_id, live.gateway)

    def status(self) -> FleetStatus:
        """Return holds and caps. This does not claim or release."""
        policy = self._require_policy()
        cards = sorted(self._holds)
        holds = tuple(Hold(card, self._holds[card].gateway) for card in cards)
        return FleetStatus(
            schema=SCHEMA,
            holds=holds,
            records=len(self._records),
            last_at=self._last_at,
            card_cap=policy.card_cap,
            log_cap=policy.log_cap,
            asked_card_cap=policy.asked_card_cap,
            asked_log_cap=policy.asked_log_cap,
            card_capped=policy.card_capped,
            log_capped=policy.log_capped,
        )

    def policy(self) -> Policy:
        """Return the caps that are enforced."""
        return self._require_policy()

    def records(self) -> tuple[ClaimRecord, ...]:
        """Return the chain. ``rebuild`` of this tuple reproduces ``status``."""
        return tuple(self._records)

    def __repr__(self) -> str:
        return f"Fleet(holds={len(self._holds)}, records={len(self._records)})"

    def _blank(self) -> None:
        self._records = []
        self._ids = set()
        self._holds = {}
        self._burned = {}
        self._last_at = 0
        self._policy = None

    def _require_policy(self) -> Policy:
        policy = self._policy
        if policy is None:
            raise Refuse("BAD_RECORD")
        return policy

    def _room(self) -> None:
        if len(self._records) >= self._require_policy().log_cap:
            raise Refuse("CAP")

    def _claim_held(self, live: _Live, card: str, gate: str, token: str, stamp: int) -> Claim:
        kind = _judge(live, gate, token)
        if kind == "fence":
            raise Refuse("FENCE")
        if stamp < self._last_at:
            raise Refuse("CLOCK")
        if live.locked:
            raise Refuse("RETRY_CAP")
        if kind == "renew":
            record = self._commit_event("renew", card, gate, token, stamp, "0", checked=True)
            return Claim(SCHEMA, card, gate, True, stamp, record.digest)
        self._mismatch(live, card, gate, token, stamp)

    def _mismatch(self, live: _Live, card: str, gate: str, token: str, stamp: int) -> NoReturn:
        if live.tries >= MAX_CONFIRMING_RETRIES:
            self._commit_event("cap", card, gate, token, stamp, "2", checked=True)
            raise Refuse("RETRY_CAP")
        self._commit_event("retry", card, gate, token, stamp, "1", checked=True)
        raise Refuse(RETRY_CLASS)

    def _commit_policy(
        self,
        applied_card: int,
        applied_log: int,
        asked_card: int,
        asked_log: int,
        card_capped: bool,
        log_capped: bool,
    ) -> None:
        body = "\t".join(
            (
                "policy",
                "1",
                str(applied_card),
                str(applied_log),
                str(asked_card),
                str(asked_log),
                _encode_flags(card_capped, log_capped),
            )
        )
        record = _note(_GENESIS, body)
        self._apply(record, checked=True)
        self._records.append(record)

    def _commit_event(
        self,
        kind: _Kind,
        card: str,
        gateway: str,
        fence: str,
        stamp: int,
        tries: str,
        *,
        checked: bool,
    ) -> ClaimRecord:
        self._room()
        rid = str(len(self._records) + 1)
        body = "\t".join((kind, rid, card, gateway, fence, str(stamp), tries))
        prev = self._records[-1].digest if self._records else _GENESIS
        record = _note(prev, body)
        self._apply(record, checked=checked)
        self._records.append(record)
        return record

    def _apply(self, record: ClaimRecord, *, checked: bool) -> None:
        parts = record.body.split("\t")
        if len(parts) != 7:
            raise Refuse("BAD_RECORD")
        kind = parts[0]
        rid = parts[1]
        if rid in self._ids:
            raise Refuse("DUPLICATE")
        if rid != str(len(self._records) + 1):
            raise Refuse("BAD_RECORD")
        if kind == "policy":
            self._apply_policy(parts)
        elif self._policy is None:
            raise Refuse("BAD_RECORD")
        elif kind == "claim":
            self._apply_claim(parts)
        elif kind in _HELD_KINDS:
            self._apply_held(parts, kind, checked=checked)
        else:
            raise Refuse("BAD_RECORD")
        self._ids.add(rid)

    def _apply_policy(self, parts: list[str]) -> None:
        if self._policy is not None or self._records:
            raise Refuse("BAD_RECORD")
        applied_card = _parse_u(parts[2], 1, CARD_CAP)
        applied_log = _parse_u(parts[3], 1, LOG_CAP)
        asked_card = _parse_u(parts[4], 1, _CAP_HI)
        asked_log = _parse_u(parts[5], 1, _CAP_HI)
        card_capped, log_capped = _flag_pair(
            parts[6], applied_card, applied_log, asked_card, asked_log
        )
        self._policy = Policy(
            SCHEMA,
            applied_card,
            applied_log,
            asked_card,
            asked_log,
            card_capped,
            log_capped,
        )

    def _apply_claim(self, parts: list[str]) -> None:
        if parts[6] != "0":
            raise Refuse("BAD_RECORD")
        card = parts[2]
        gate = parts[3]
        token = parts[4]
        stamp = _parse_u(parts[5], 0, CLOCK_HI)
        if card in self._holds:
            raise Refuse("BAD_RECORD")
        if stamp < self._last_at:
            raise Refuse("CLOCK")
        if self._seen_fence(card, token):
            raise Refuse("REPLAY")
        if len(self._holds) >= self._require_policy().card_cap:
            raise Refuse("CAP")
        self._holds[card] = _Live(gate, token, 0, False)
        self._burn(card, token)
        self._last_at = stamp

    def _apply_held(self, parts: list[str], kind: str, *, checked: bool) -> None:
        card = parts[2]
        gate = parts[3]
        token = parts[4]
        stamp = _parse_u(parts[5], 0, CLOCK_HI)
        tries = _parse_u(parts[6], 0, 2)
        live = self._holds.get(card)
        if live is None:
            raise Refuse("BAD_RECORD")
        if stamp < self._last_at:
            raise Refuse("CLOCK")
        if not checked:
            self._require_judgment(live, gate, token, kind)
        if kind == "renew":
            if live.locked or tries != 0:
                raise Refuse("BAD_RECORD")
            self._holds[card] = _Live(live.gateway, live.fence, 0, False)
            self._last_at = stamp
            return
        if kind == "release":
            if live.locked or tries != 0:
                raise Refuse("BAD_RECORD")
            removed = self._holds.pop(card, None)
            if removed is None:
                raise Refuse("BAD_RECORD")
            self._last_at = stamp
            return
        if kind == "retry":
            if live.locked or live.tries != 0 or tries != 1:
                raise Refuse("BAD_RECORD")
            self._burn(card, token)
            self._holds[card] = _Live(live.gateway, live.fence, 1, False)
            self._last_at = stamp
            return
        if kind == "cap":
            if live.locked or live.tries != 1 or tries != 2:
                raise Refuse("BAD_RECORD")
            self._burn(card, token)
            self._holds[card] = _Live(live.gateway, live.fence, 2, True)
            self._last_at = stamp
            return
        raise Refuse("BAD_RECORD")

    def _require_judgment(self, live: _Live, gate: str, token: str, kind: str) -> None:
        judged = _judge(live, gate, token)
        if kind in {"renew", "release"} and judged != "renew":
            raise Refuse("BAD_RECORD")
        if kind in {"retry", "cap"} and judged != "stale":
            raise Refuse("BAD_RECORD")

    def _seen_fence(self, card: str, token: str) -> bool:
        found = False
        for old in self._burned.get(card, ()):
            if const_eq(old, token):
                found = True
        return found

    def _burn(self, card: str, token: str) -> None:
        current = self._burned.get(card, ())
        self._burned[card] = (*current, token)


def rebuild(records: object) -> Fleet:
    """Replay a claim log. The same records produce the same public status."""
    rows = _as_records(records)
    fleet = Fleet.__new__(Fleet)
    fleet._blank()
    prev = _GENESIS
    for record in rows:
        _vet(record.prev, record.body, record.digest)
        if not hmac.compare_digest(record.prev, prev):
            raise Refuse("CHAIN")
        if fleet._policy is not None:
            fleet._room()
        fleet._apply(record, checked=False)
        fleet._records.append(record)
        prev = record.digest
    if fleet._policy is None:
        raise Refuse("BAD_RECORD")
    return fleet


__all__ = [
    "CARD_CAP",
    "CLOCK_HI",
    "FENCE_CAP",
    "LOG_CAP",
    "MAX_CONFIRMING_RETRIES",
    "NAME_CAP",
    "RETRY_CLASS",
    "SCHEMA",
    "Claim",
    "ClaimRecord",
    "Fleet",
    "FleetStatus",
    "Hold",
    "Policy",
    "Release",
    "rebuild",
]
