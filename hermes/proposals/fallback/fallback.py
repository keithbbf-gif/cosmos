"""One backup for a named failure class.

The first eligible refusal on a turn selects that backup. The next refusal
ends the chain. A new turn id starts on the primary again. Nothing here
opens a socket or sleeps.
"""

from __future__ import annotations

import hashlib
import hmac
import re
from dataclasses import dataclass
from typing import Final

from cosmos_hermes import Refuse, bound_int, bound_text, const_eq, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-fallback/1"
POLICY_CAP: Final[int] = 1
CHANNELS: Final[tuple[str, ...]] = ("chat", "vision", "compress")
ELIGIBLE: Final[tuple[str, ...]] = (
    "RATE",
    "HTTP_429",
    "TIMEOUT",
    "SERVER",
    "HTTP_500",
    "HTTP_502",
    "HTTP_503",
)
TERMINAL: Final[tuple[str, ...]] = (
    "HTTP_400",
    "HTTP_401",
    "HTTP_402",
    "HTTP_403",
    "HTTP_404",
    "HTTP_501",
    "HTTP_504",
)

_CHANNEL_SET: Final[frozenset[str]] = frozenset(CHANNELS)
_ELIGIBLE_SET: Final[frozenset[str]] = frozenset(ELIGIBLE)
_TERMINAL_SET: Final[frozenset[str]] = frozenset(TERMINAL)
_MAX_CANDIDATES: Final[int] = 8
_MAX_ALLOW: Final[int] = 32
_MAX_RECORDS: Final[int] = 64
_CAP_HI: Final[int] = 1_000_000
_AT_HI: Final[int] = 4_000_000_000
_GENESIS: Final[str] = "0" * 64

_ID: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_MODEL: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")
_CODE: Final[re.Pattern[str]] = re.compile(r"^[A-Z][A-Z0-9_]{1,31}$")
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")


def _bad_shape(text: str) -> bool:
    if "://" in text or text.startswith("//") or "\\" in text or ".." in text:
        return True
    return any(ord(ch) < 32 or ch.isspace() for ch in text)


def _label(
    value: object,
    limit: int,
    pattern: re.Pattern[str],
    code: str,
    empty_code: str | None = None,
) -> str:
    text = bound_text(value, limit)
    if text == "":
        raise Refuse(code if empty_code is None else empty_code)
    if secret_shape(text):
        raise Refuse("SECRET")
    if _bad_shape(text) or pattern.fullmatch(text) is None:
        raise Refuse(code)
    return text


def _endpoint_id(value: object) -> str:
    return _label(value, 64, _ID, "BAD_ROUTE")


def _provider(value: object, code: str) -> str:
    return _label(value, 64, _ID, code)


def _model(value: object) -> str:
    return _label(value, 128, _MODEL, "BAD_ROUTE")


def _credential(value: object) -> str:
    return _label(value, 64, _ID, "BAD_ROUTE", "MISSING_CRED")


def _turn_id(value: object) -> str:
    return _label(value, 64, _ID, "BAD_TURN")


def _channel(value: object) -> str:
    text = bound_text(value, 16)
    if secret_shape(text):
        raise Refuse("SECRET")
    if text not in _CHANNEL_SET:
        raise Refuse("BAD_CHANNEL")
    return text


def _code_token(value: object) -> str:
    return _label(value, 32, _CODE, "BAD_CODE")


def _stamp(value: object) -> int:
    return bound_int(value, 0, _AT_HI)


def _requested_cap(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("NOT_INT")
    if value < 1:
        raise Refuse("BAD_CAP")
    if value > _CAP_HI:
        raise Refuse("OUT_OF_RANGE", f"1..{_CAP_HI}")
    return value


def _exact_cap(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("NOT_INT")
    if value != POLICY_CAP:
        raise Refuse("BAD_CAP")
    return POLICY_CAP


def _kept_count(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("NOT_INT")
    if value not in (0, 1):
        raise Refuse("BAD_CAP")
    return value


def _dropped_count(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("NOT_INT")
    if value < 0 or value > _MAX_CANDIDATES - 1:
        raise Refuse("BAD_CAP")
    return value


def _body(
    turn_id: str,
    channel: str,
    primary_id: str,
    fallback_id: str,
    endpoint_id: str,
    code: str,
    at: int,
) -> str:
    return "\n".join((turn_id, channel, primary_id, fallback_id, endpoint_id, code, str(at)))


def _link(prev: str, body: str) -> str:
    try:
        raw = f"{prev}\n{body}".encode("ascii")
    except UnicodeEncodeError as err:
        raise Refuse("BAD_CHAIN") from err
    return hashlib.sha256(raw).hexdigest()


def _digest_eq(left: object, right: object) -> bool:
    if not isinstance(left, str) or not isinstance(right, str) or len(left) != len(right):
        return False
    try:
        raw_left = left.encode("ascii")
        raw_right = right.encode("ascii")
    except UnicodeEncodeError:
        return False
    return hmac.compare_digest(raw_left, raw_right)


def _prev_hex(value: object) -> str:
    text = bound_text(value, 64)
    if _HEX.fullmatch(text) is None:
        raise Refuse("BROKEN_CHAIN")
    return text


def _seen_id(endpoint_id: str, seen: list[str]) -> bool:
    for item in seen:
        if const_eq(endpoint_id, item):
            return True
    return False


def _as_policy(value: object) -> Policy:
    if not isinstance(value, Policy):
        raise Refuse("BAD_ROUTE")
    return value


def _parse_records(value: object) -> tuple[Record, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, (tuple, list)):
        raise Refuse("BAD_CHAIN")
    if len(value) > _MAX_RECORDS:
        raise Refuse("OVERSIZE", str(_MAX_RECORDS))
    rows: list[Record] = []
    for item in value:
        if not isinstance(item, Record):
            raise Refuse("BAD_CHAIN")
        rows.append(item)
    return tuple(rows)


def _at_record(rows: tuple[Record, ...], index: int) -> Record:
    if index < 0 or index >= len(rows):
        raise Refuse("BAD_CHAIN")
    return rows[index]


def _one(rows: tuple[Record, ...]) -> Record:
    if len(rows) != 1:
        raise Refuse("BAD_CHAIN")
    return _at_record(rows, 0)


def _allow_names(allow: object) -> tuple[str, ...]:
    if isinstance(allow, (str, bytes)) or not isinstance(allow, (tuple, list)):
        raise Refuse("BAD_ALLOW")
    if len(allow) == 0:
        raise Refuse("EMPTY_ALLOW")
    if len(allow) > _MAX_ALLOW:
        raise Refuse("OVERSIZE", str(_MAX_ALLOW))
    names: list[str] = []
    seen: set[str] = set()
    for item in allow:
        name = _provider(item, "BAD_ALLOW")
        if name in seen:
            raise Refuse("DUPLICATE")
        seen.add(name)
        names.append(name)
    return tuple(names)


def _candidates(fallbacks: object) -> tuple[Endpoint, ...]:
    if isinstance(fallbacks, (str, bytes)) or not isinstance(fallbacks, (tuple, list)):
        raise Refuse("BAD_ROUTE")
    if len(fallbacks) > _MAX_CANDIDATES:
        raise Refuse("OVERSIZE", str(_MAX_CANDIDATES))
    rows: list[Endpoint] = []
    for item in fallbacks:
        if not isinstance(item, Endpoint):
            raise Refuse("BAD_ROUTE")
        rows.append(item)
    return tuple(rows)


@dataclass(frozen=True, slots=True)
class Endpoint:
    """Primary or backup route. The credential field is an id, never key material."""

    endpoint_id: str
    provider: str
    model: str
    credential_id: str

    def __post_init__(self) -> None:
        _endpoint_id(self.endpoint_id)
        _provider(self.provider, "BAD_ROUTE")
        _model(self.model)
        _credential(self.credential_id)


@dataclass(frozen=True, slots=True)
class Record:
    """One refusal linked to the previous record in the session log."""

    turn_id: str
    channel: str
    primary_id: str
    fallback_id: str
    endpoint_id: str
    code: str
    at: int
    prev: str
    link: str

    def __post_init__(self) -> None:
        turn_id = _turn_id(self.turn_id)
        channel = _channel(self.channel)
        primary_id = _endpoint_id(self.primary_id)
        fallback_id = _endpoint_id(self.fallback_id)
        endpoint_id = _endpoint_id(self.endpoint_id)
        code = _code_token(self.code)
        at = _stamp(self.at)
        prev = _prev_hex(self.prev)
        body = _body(turn_id, channel, primary_id, fallback_id, endpoint_id, code, at)
        if not _digest_eq(self.link, _link(prev, body)):
            raise Refuse("BROKEN_CHAIN")


@dataclass(frozen=True, slots=True)
class Choice:
    """The one confirming backup. `used_after` is always the policy cap."""

    turn_id: str
    channel: str
    fallback_id: str
    provider: str
    model: str
    credential_id: str
    used_after: int
    error_code: str
    record: Record

    def __post_init__(self) -> None:
        turn_id = _turn_id(self.turn_id)
        channel = _channel(self.channel)
        fallback_id = _endpoint_id(self.fallback_id)
        _provider(self.provider, "BAD_ROUTE")
        _model(self.model)
        _credential(self.credential_id)
        if isinstance(self.used_after, bool) or not isinstance(self.used_after, int):
            raise Refuse("NOT_INT")
        if self.used_after != POLICY_CAP:
            raise Refuse("BAD_CAP")
        code = _code_token(self.error_code)
        if code not in _ELIGIBLE_SET:
            raise Refuse("NO_FALLBACK")
        if not isinstance(self.record, Record):
            raise Refuse("BAD_CHAIN")
        if self.record.turn_id != turn_id or self.record.channel != channel:
            raise Refuse("BAD_CHAIN")
        if self.record.code != code:
            raise Refuse("BAD_CHAIN")
        if const_eq(self.record.endpoint_id, fallback_id):
            raise Refuse("BAD_ROUTE")


@dataclass(frozen=True, slots=True)
class Turn:
    """Public state of one turn and channel after replay."""

    turn_id: str
    channel: str
    active_id: str
    spent: int
    ended: bool
    codes: tuple[str, ...]

    def __post_init__(self) -> None:
        _turn_id(self.turn_id)
        _channel(self.channel)
        if not isinstance(self.ended, bool):
            raise Refuse("BAD_CHAIN")
        if isinstance(self.spent, bool) or not isinstance(self.spent, int):
            raise Refuse("NOT_INT")
        if self.spent != POLICY_CAP:
            raise Refuse("BAD_CAP")
        if not isinstance(self.codes, tuple):
            raise Refuse("BAD_CHAIN")
        if self.ended:
            if self.active_id != "":
                raise Refuse("BAD_CHAIN")
            if len(self.codes) != 2:
                raise Refuse("BAD_CHAIN")
        else:
            _endpoint_id(self.active_id)
            if len(self.codes) != 1:
                raise Refuse("BAD_CHAIN")
        first = _code_at(self.codes, 0)
        if first not in _ELIGIBLE_SET:
            raise Refuse("NO_FALLBACK")
        if self.ended:
            second = _code_at(self.codes, 1)
            if second not in _ELIGIBLE_SET and second not in _TERMINAL_SET:
                raise Refuse("UNCLASSIFIED")


def _code_at(codes: tuple[str, ...], index: int) -> str:
    if index < 0 or index >= len(codes):
        raise Refuse("BAD_CHAIN")
    return _code_token(codes[index])


@dataclass(frozen=True, slots=True)
class Snapshot:
    """Replay of a session log. Same records, same snapshot."""

    schema: str
    cap: int
    turns: tuple[Turn, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.schema, str) or not const_eq(self.schema, SCHEMA):
            raise Refuse("BAD_CHAIN")
        _exact_cap(self.cap)
        if not isinstance(self.turns, tuple):
            raise Refuse("BAD_CHAIN")
        if len(self.turns) > _MAX_RECORDS:
            raise Refuse("OVERSIZE", str(_MAX_RECORDS))
        seen: set[tuple[str, str]] = set()
        for turn in self.turns:
            if not isinstance(turn, Turn):
                raise Refuse("BAD_CHAIN")
            key = (turn.turn_id, turn.channel)
            if key in seen:
                raise Refuse("DUPLICATE")
            seen.add(key)


@dataclass(frozen=True, slots=True)
class Policy:
    """Primary plus at most one fallback. `cap` stays at the policy cap."""

    primary: Endpoint
    fallback: Endpoint | None
    allow: tuple[str, ...]
    cap: int
    requested: int
    kept: int
    dropped: int

    def __post_init__(self) -> None:
        if not isinstance(self.primary, Endpoint):
            raise Refuse("BAD_ROUTE")
        if self.fallback is not None and not isinstance(self.fallback, Endpoint):
            raise Refuse("BAD_ROUTE")
        cap = _exact_cap(self.cap)
        requested = _requested_cap(self.requested)
        kept = _kept_count(self.kept)
        dropped = _dropped_count(self.dropped)
        names = _allow_names(self.allow)
        object.__setattr__(self, "allow", names)
        object.__setattr__(self, "cap", cap)
        object.__setattr__(self, "requested", requested)
        object.__setattr__(self, "kept", kept)
        object.__setattr__(self, "dropped", dropped)
        allowed = set(names)
        if self.primary.provider not in allowed:
            raise Refuse("NOT_ALLOWED")
        if kept == 0 and (self.fallback is not None or dropped != 0):
            raise Refuse("BAD_CAP")
        if kept == 1 and self.fallback is None:
            raise Refuse("BAD_CAP")
        backup = self.fallback
        if backup is None:
            return
        if backup.provider not in allowed:
            raise Refuse("NOT_ALLOWED")
        if backup.provider == self.primary.provider:
            raise Refuse("SAME_PROVIDER")
        if const_eq(backup.endpoint_id, self.primary.endpoint_id):
            raise Refuse("BAD_ROUTE")


def configure(
    primary: object,
    fallbacks: object,
    allow: object,
    cap: object = POLICY_CAP,
) -> Policy:
    """Keep the first fallback. A higher cap is recorded and not applied."""
    if not isinstance(primary, Endpoint):
        raise Refuse("BAD_ROUTE")
    requested = _requested_cap(cap)
    names = _allow_names(allow)
    allowed = set(names)
    if primary.provider not in allowed:
        raise Refuse("NOT_ALLOWED")
    rows = _candidates(fallbacks)
    seen: list[str] = [primary.endpoint_id]
    chosen: Endpoint | None = None
    dropped = 0
    for item in rows:
        if item.provider not in allowed:
            raise Refuse("NOT_ALLOWED")
        if item.provider == primary.provider:
            raise Refuse("SAME_PROVIDER")
        if _seen_id(item.endpoint_id, seen):
            raise Refuse("BAD_ROUTE")
        seen.append(item.endpoint_id)
        if chosen is None:
            chosen = item
        else:
            dropped += 1
    kept = 0 if chosen is None else 1
    return Policy(primary, chosen, names, POLICY_CAP, requested, kept, dropped)


def _bind(policy: Policy, row: Record) -> None:
    backup = policy.fallback
    if backup is None:
        raise Refuse("NO_FALLBACK")
    if not const_eq(row.primary_id, policy.primary.endpoint_id):
        raise Refuse("BAD_ROUTE")
    if not const_eq(row.fallback_id, backup.endpoint_id):
        raise Refuse("BAD_ROUTE")
    if not (
        const_eq(row.endpoint_id, policy.primary.endpoint_id)
        or const_eq(row.endpoint_id, backup.endpoint_id)
    ):
        raise Refuse("BAD_ROUTE")


def _walk(policy: Policy, records: object) -> tuple[Record, ...]:
    rows = _parse_records(records)
    prev = _GENESIS
    last_at = -1
    seen: set[str] = set()
    for row in rows:
        if row.link in seen:
            raise Refuse("DUPLICATE")
        if not _digest_eq(row.prev, prev):
            raise Refuse("BROKEN_CHAIN")
        if seen and row.at <= last_at:
            raise Refuse("STALE")
        _bind(policy, row)
        seen.add(row.link)
        prev = row.link
        last_at = row.at
    return rows


def _tail(rows: tuple[Record, ...]) -> tuple[str, int]:
    if len(rows) == 0:
        return _GENESIS, -1
    last = _at_record(rows, len(rows) - 1)
    return last.link, last.at


def _rows_for(rows: tuple[Record, ...], turn_id: str, channel: str) -> tuple[Record, ...]:
    matched: list[Record] = []
    for row in rows:
        if row.turn_id == turn_id and row.channel == channel:
            matched.append(row)
    return tuple(matched)


def _armed(policy: Policy) -> Endpoint:
    backup = policy.fallback
    if backup is None:
        raise Refuse("NO_FALLBACK")
    return backup


def fail(
    policy: object,
    turn_id: object,
    channel: object,
    endpoint_id: object,
    code: object,
    at: object,
    prior: object = (),
) -> Record:
    """Append one refusal. The second fact on a turn closes that chain."""
    bound = _as_policy(policy)
    turn = _turn_id(turn_id)
    name = _channel(channel)
    endpoint = _endpoint_id(endpoint_id)
    token = _code_token(code)
    stamp = _stamp(at)
    walked = _walk(bound, prior)
    if len(walked) >= _MAX_RECORDS:
        raise Refuse("OVERSIZE", str(_MAX_RECORDS))
    prev, last_at = _tail(walked)
    if len(walked) != 0 and stamp <= last_at:
        raise Refuse("STALE")
    matched = _rows_for(walked, turn, name)
    if len(matched) >= 2:
        raise Refuse("EXHAUSTED")
    if len(matched) == 0:
        if not const_eq(endpoint, bound.primary.endpoint_id):
            raise Refuse("BAD_ROUTE")
        if token not in _ELIGIBLE_SET:
            if token in _TERMINAL_SET:
                raise Refuse("NO_FALLBACK")
            raise Refuse("UNCLASSIFIED")
    backup = _armed(bound)
    if len(matched) != 0:
        previous = _one(matched)
        if not const_eq(previous.endpoint_id, bound.primary.endpoint_id):
            raise Refuse("BAD_CHAIN")
        if previous.code not in _ELIGIBLE_SET:
            raise Refuse("BAD_CHAIN")
        if not const_eq(endpoint, backup.endpoint_id):
            raise Refuse("BAD_ROUTE")
        if token not in _ELIGIBLE_SET and token not in _TERMINAL_SET:
            raise Refuse("UNCLASSIFIED")
    body = _body(
        turn,
        name,
        bound.primary.endpoint_id,
        backup.endpoint_id,
        endpoint,
        token,
        stamp,
    )
    return Record(
        turn,
        name,
        bound.primary.endpoint_id,
        backup.endpoint_id,
        endpoint,
        token,
        stamp,
        prev,
        _link(prev, body),
    )


def switch(policy: object, turn_id: object, channel: object, records: object) -> Choice:
    """Select the backup once. A turn that already holds two refusals ends."""
    bound = _as_policy(policy)
    turn = _turn_id(turn_id)
    name = _channel(channel)
    rows = _walk(bound, records)
    backup = _armed(bound)
    matched = _rows_for(rows, turn, name)
    if len(matched) >= 2:
        raise Refuse("EXHAUSTED")
    if len(matched) == 0:
        raise Refuse("NO_FALLBACK")
    only = _one(matched)
    if not const_eq(only.endpoint_id, bound.primary.endpoint_id):
        raise Refuse("BAD_ROUTE")
    if only.code not in _ELIGIBLE_SET:
        raise Refuse("NO_FALLBACK")
    return Choice(
        turn,
        name,
        backup.endpoint_id,
        backup.provider,
        backup.model,
        backup.credential_id,
        POLICY_CAP,
        only.code,
        only,
    )


def _turn_from(policy: Policy, bucket: tuple[Record, ...]) -> Turn:
    count = len(bucket)
    if count > 2:
        raise Refuse("EXHAUSTED")
    if count < 1:
        raise Refuse("BAD_CHAIN")
    backup = _armed(policy)
    first = _at_record(bucket, 0)
    if not const_eq(first.endpoint_id, policy.primary.endpoint_id):
        raise Refuse("BAD_ROUTE")
    if first.code not in _ELIGIBLE_SET:
        raise Refuse("NO_FALLBACK")
    if count == 1:
        return Turn(first.turn_id, first.channel, backup.endpoint_id, POLICY_CAP, False, (first.code,))
    second = _at_record(bucket, 1)
    if not const_eq(second.endpoint_id, backup.endpoint_id):
        raise Refuse("BAD_ROUTE")
    if second.code not in _ELIGIBLE_SET and second.code not in _TERMINAL_SET:
        raise Refuse("UNCLASSIFIED")
    return Turn(
        first.turn_id,
        first.channel,
        "",
        POLICY_CAP,
        True,
        (first.code, second.code),
    )


def rebuild(policy: object, records: object) -> Snapshot:
    """Replay the log. Two refusals on a turn leave it ended and with no route."""
    bound = _as_policy(policy)
    rows = _walk(bound, records)
    groups: dict[tuple[str, str], list[Record]] = {}
    for row in rows:
        key = (row.turn_id, row.channel)
        bucket = groups.get(key)
        if bucket is None:
            bucket = []
            groups[key] = bucket
        bucket.append(row)
    turns: list[Turn] = []
    for bucket in groups.values():
        turns.append(_turn_from(bound, tuple(bucket)))
    return Snapshot(SCHEMA, POLICY_CAP, tuple(turns))


__all__ = [
    "CHANNELS",
    "ELIGIBLE",
    "POLICY_CAP",
    "SCHEMA",
    "TERMINAL",
    "Choice",
    "Endpoint",
    "Policy",
    "Record",
    "Snapshot",
    "Turn",
    "configure",
    "fail",
    "rebuild",
    "switch",
]
