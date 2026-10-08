"""Spotify descriptors. Disabled until a credential id is enabled. No HTTP."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Final

from cosmos_hermes import Refuse, bound_int, bound_text, const_eq, redact, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-spotify/1"
QUERY_CAP: Final[int] = 200
PAGE_CAP: Final[int] = 50
BATCH_CAP: Final[int] = 20
CHAR_BUDGET: Final[int] = 64
CRED_CAP: Final[int] = 64
DEVICE_CAP: Final[int] = 64
ID_CAP: Final[int] = 64
INPUT_CAP: Final[int] = 40
OFFSET_MAX: Final[int] = 1_000
POSITION_MAX: Final[int] = 86_400_000
VOLUME_MAX: Final[int] = 100
ROW_CAP: Final[int] = 32
RETRY_CLASS: Final[str] = "HTTP_401"
GENESIS: Final[str] = "0" * 64
_CLOCK_MAX: Final[int] = 4_000_000_000_000
_BODY_CAP: Final[int] = 80_000
_URI_CAP: Final[int] = 64

TOOLS: Final[tuple[str, ...]] = (
    "playback",
    "devices",
    "queue",
    "search",
    "playlists",
    "albums",
    "library",
)
SEARCH_TYPES: Final[tuple[str, ...]] = (
    "track",
    "album",
    "artist",
    "playlist",
    "show",
    "episode",
)

_TOOL_SET: Final[frozenset[str]] = frozenset(TOOLS)
_TYPE_SET: Final[frozenset[str]] = frozenset(SEARCH_TYPES)
_TIERS: Final[frozenset[str]] = frozenset({"free", "premium", "unverified"})
_REPEAT: Final[frozenset[str]] = frozenset({"track", "context", "off"})
_BITS: Final[frozenset[str]] = frozenset({"true", "false"})
_SIDES: Final[frozenset[str]] = frozenset({"before", "after"})
_KINDS: Final[frozenset[str]] = frozenset({"tracks", "albums"})
_VISIBILITY: Final[frozenset[str]] = frozenset({"public", "private", "collaborative"})
_FAILURES: Final[frozenset[str]] = frozenset(
    {"HTTP_401", "HTTP_403", "HTTP_429", "HTTP_204"}
)
_ROW_KINDS: Final[frozenset[str]] = frozenset(
    {"enable", "play", "action", "pack", "confirm"}
)
_DIGITS: Final[frozenset[str]] = frozenset("0123456789")
_UNESC: Final[dict[str, str]] = {
    "25": "%",
    "26": "&",
    "3D": "=",
    "2C": ",",
    "0A": "\n",
    "0D": "\r",
    "7C": "|",
}

_CRED_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$")
_DEVICE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$")
_ID_RE = re.compile(r"^[A-Za-z0-9]{22}$")
_MARKET_RE = re.compile(r"^[A-Z]{2}$")
_SNAPSHOT_RE = re.compile(r"^[A-Za-z0-9]{1,64}$")
_HEX_RE = re.compile(r"^[0-9a-f]{64}$")

_ENABLE_KEYS: Final[tuple[str, ...]] = ("cred", "tier")
_PLAY_KEYS: Final[tuple[str, ...]] = ("cred", "tier", "track", "device", "position", "cap")
_ACTION_KEYS: Final[tuple[str, ...]] = (
    "cred",
    "tier",
    "tool",
    "action",
    "subject",
    "extra",
    "skipped",
    "device",
    "limit",
    "offset",
    "number",
    "flag",
    "premium",
    "cap",
)
_PACK_KEYS: Final[tuple[str, ...]] = ("cred", "budget", "cap", "titles", "kept", "skipped")
_NOTE_KEYS: Final[tuple[str, ...]] = ("cred", "code", "attempt")


@dataclass(frozen=True, slots=True)
class _Spec:
    tool: str
    action: str
    premium: bool
    device: str
    subject: str
    items: str
    number: str
    flag: str
    offset: str
    cap_kind: str


def _specs() -> dict[tuple[str, str], _Spec]:
    rows: tuple[tuple[str, str, bool, str, str, str, str, str, str, str], ...] = (
        ("playback", "get_state", False, "no", "no", "no", "no", "no", "no", "text"),
        ("playback", "get_currently_playing", False, "no", "no", "no", "no", "no", "no", "text"),
        ("playback", "pause", True, "opt", "no", "no", "no", "no", "no", "text"),
        ("playback", "next", True, "opt", "no", "no", "no", "no", "no", "text"),
        ("playback", "previous", True, "opt", "no", "no", "no", "no", "no", "text"),
        ("playback", "seek", True, "opt", "no", "no", "position", "no", "no", "text"),
        ("playback", "set_repeat", True, "opt", "no", "no", "no", "repeat", "no", "text"),
        ("playback", "set_shuffle", True, "opt", "no", "no", "no", "shuffle", "no", "text"),
        ("playback", "set_volume", True, "opt", "no", "no", "volume", "no", "no", "text"),
        ("playback", "recently_played", False, "no", "no", "no", "cursor", "side", "page", "page"),
        ("devices", "list", False, "no", "no", "no", "no", "no", "no", "text"),
        ("devices", "transfer", True, "req", "no", "no", "no", "start", "no", "text"),
        ("queue", "get", False, "no", "no", "no", "no", "no", "no", "text"),
        ("queue", "add", True, "opt", "track", "no", "no", "no", "no", "text"),
        ("search", "search", False, "no", "query", "types", "no", "market", "page", "search"),
        ("playlists", "list", False, "no", "no", "no", "no", "no", "page", "page"),
        ("playlists", "get", False, "no", "playlist", "no", "no", "no", "no", "text"),
        ("playlists", "create", False, "no", "name", "no", "no", "visibility", "no", "text"),
        ("playlists", "add_items", False, "no", "playlist", "ids", "no", "no", "index", "batch"),
        ("playlists", "remove_items", False, "no", "playlist", "ids", "no", "snapshot", "no", "batch"),
        ("playlists", "update_details", False, "no", "playlist", "no", "no", "visibility", "no", "text"),
        ("albums", "get", False, "no", "album", "no", "no", "no", "no", "text"),
        ("albums", "tracks", False, "no", "album", "no", "no", "no", "page", "page"),
        ("library", "list", False, "no", "no", "no", "no", "kind", "page", "page"),
        ("library", "save", False, "no", "no", "ids", "no", "kind", "no", "batch"),
        ("library", "remove", False, "no", "no", "ids", "no", "kind", "no", "batch"),
    )
    found: dict[tuple[str, str], _Spec] = {}
    for row in rows:
        spec = _Spec(
            tool=row[0],
            action=row[1],
            premium=row[2],
            device=row[3],
            subject=row[4],
            items=row[5],
            number=row[6],
            flag=row[7],
            offset=row[8],
            cap_kind=row[9],
        )
        found[(spec.tool, spec.action)] = spec
    return found


_SPECS: Final[dict[tuple[str, str], _Spec]] = _specs()


def _schema(value: object) -> None:
    if not isinstance(value, str):
        raise Refuse("BAD_SCHEMA")
    text = bound_text(value, 64)
    if secret_shape(text):
        raise Refuse("SECRET")
    if not const_eq(text, SCHEMA):
        raise Refuse("BAD_SCHEMA")


def _no_controls(text: str) -> None:
    for char in text:
        code = ord(char)
        if code < 32 or code == 127:
            raise Refuse("BAD_TEXT")


def _clamp(value: object, policy: int) -> int:
    """Ignore a request above `policy`. Bool is not an int."""
    if value is None:
        return policy
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("NOT_INT")
    if value < 1:
        raise Refuse("OUT_OF_RANGE", f"1..{policy}")
    if value > policy:
        return policy
    return value


def _now(value: object) -> int:
    return bound_int(value, 0, _CLOCK_MAX)


def _cred(value: object) -> str:
    text = bound_text(value, CRED_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    _no_controls(text)
    if text.strip() == "":
        raise Refuse("MISSING_CREDENTIAL")
    if text != text.strip() or ".." in text or _CRED_RE.fullmatch(text) is None:
        raise Refuse("BAD_CREDENTIAL")
    return text


def _tier(value: object) -> str:
    text = bound_text(value, 16)
    if secret_shape(text):
        raise Refuse("SECRET")
    _no_controls(text)
    if text not in _TIERS:
        raise Refuse("BAD_TIER")
    return text


def _device(value: object, *, required: bool) -> str:
    text = bound_text(value, DEVICE_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    _no_controls(text)
    if text == "":
        if required:
            raise Refuse("MISSING_DEVICE")
        return ""
    if ".." in text or _DEVICE_RE.fullmatch(text) is None:
        raise Refuse("BAD_DEVICE")
    return text


def _track(value: object, limit: int) -> str:
    text = bound_text(value, limit)
    if secret_shape(text):
        raise Refuse("SECRET")
    _no_controls(text)
    if text.strip() == "":
        raise Refuse("MISSING_SUBJECT")
    if text != text.strip():
        raise Refuse("BAD_TRACK")
    if ":" not in text:
        if _ID_RE.fullmatch(text) is None:
            raise Refuse("BAD_TRACK")
        return text
    parts = text.split(":")
    if len(parts) != 3:
        raise Refuse("BAD_TRACK")
    scheme, kind, ident = parts
    if scheme != "spotify" or kind != "track" or _ID_RE.fullmatch(ident) is None:
        raise Refuse("BAD_TRACK")
    return ident


def _spotify_id(value: object, code: str) -> str:
    text = bound_text(value, ID_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    _no_controls(text)
    if text.strip() == "":
        raise Refuse("MISSING_SUBJECT")
    if text != text.strip() or ":" in text or _ID_RE.fullmatch(text) is None:
        raise Refuse(code)
    return text


def _phrase(value: object, limit: int) -> str:
    text = bound_text(value, limit)
    if secret_shape(text):
        raise Refuse("SECRET")
    _no_controls(text)
    stripped = text.strip()
    if stripped == "":
        raise Refuse("EMPTY")
    return stripped


def _as_tuple(value: object) -> tuple[object, ...]:
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, tuple):
        raise Refuse("BAD_ITEMS")
    found: list[object] = []
    for item in value:
        found.append(item)
    return tuple(found)


def _types(raw: tuple[object, ...]) -> tuple[str, ...]:
    if len(raw) == 0:
        raise Refuse("EMPTY")
    if len(raw) > len(SEARCH_TYPES):
        raise Refuse("OVERSIZE", str(len(SEARCH_TYPES)))
    seen: set[str] = set()
    chosen: list[str] = []
    for item in raw:
        text = bound_text(item, 16)
        if secret_shape(text):
            raise Refuse("SECRET")
        _no_controls(text)
        if text not in _TYPE_SET:
            raise Refuse("BAD_TYPE")
        if text in seen:
            raise Refuse("DUPLICATE")
        seen.add(text)
        chosen.append(text)
    return tuple(chosen)


def _budget_ids(raw: tuple[object, ...], budget: int) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Keep ids that fit. Skip later ids once the count budget is spent."""
    if len(raw) > INPUT_CAP:
        raise Refuse("OVERSIZE", str(INPUT_CAP))
    seen: set[str] = set()
    kept: list[str] = []
    skipped: list[str] = []
    remaining = budget
    for item in raw:
        ident = _track(item, _URI_CAP)
        if ident in seen:
            raise Refuse("DUPLICATE")
        seen.add(ident)
        if remaining < 1:
            skipped.append(ident)
            continue
        remaining -= 1
        kept.append(ident)
    return tuple(kept), tuple(skipped)


def _select(titles: tuple[str, ...], budget: int) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Skip a title larger than the characters still open. Later titles stay in play."""
    seen: set[str] = set()
    kept: list[str] = []
    skipped: list[str] = []
    remaining = budget
    for title in titles:
        if title in seen:
            raise Refuse("DUPLICATE")
        seen.add(title)
        cost = len(title)
        if cost > remaining:
            skipped.append(title)
            continue
        remaining -= cost
        kept.append(title)
    return tuple(kept), tuple(skipped)


def _flag(kind: str, value: object) -> str:
    if not isinstance(value, str):
        raise Refuse("NOT_TEXT")
    if secret_shape(value):
        raise Refuse("SECRET")
    _no_controls(value)
    if kind == "no":
        if value != "":
            raise Refuse("UNEXPECTED")
        return ""
    if kind == "market":
        if value == "":
            return ""
        if _MARKET_RE.fullmatch(value) is None:
            raise Refuse("BAD_MARKET")
        return value
    if kind == "side":
        if value == "":
            return ""
        if value not in _SIDES:
            raise Refuse("BAD_FLAG")
        return value
    if kind == "snapshot":
        if value == "":
            return ""
        if _SNAPSHOT_RE.fullmatch(value) is None:
            raise Refuse("BAD_FLAG")
        return value
    if kind == "repeat":
        if value == "":
            raise Refuse("MISSING_SUBJECT")
        if value not in _REPEAT:
            raise Refuse("BAD_FLAG")
        return value
    if kind == "shuffle" or kind == "start":
        if value == "":
            raise Refuse("MISSING_SUBJECT")
        if value not in _BITS:
            raise Refuse("BAD_FLAG")
        return value
    if kind == "kind":
        if value == "":
            raise Refuse("MISSING_SUBJECT")
        if value not in _KINDS:
            raise Refuse("BAD_FLAG")
        return value
    if kind == "visibility":
        if value == "":
            raise Refuse("MISSING_SUBJECT")
        if value not in _VISIBILITY:
            raise Refuse("BAD_FLAG")
        return value
    raise Refuse("BAD_PLAN")


def _number(kind: str, value: object, flag: str) -> int:
    if kind == "no":
        return _idle_number(value)
    if kind == "position":
        if value is None:
            raise Refuse("MISSING_SUBJECT")
        return bound_int(value, 0, POSITION_MAX)
    if kind == "volume":
        if value is None:
            raise Refuse("MISSING_SUBJECT")
        return bound_int(value, 0, VOLUME_MAX)
    if kind == "cursor":
        if flag == "":
            return _idle_number(value)
        if value is None:
            raise Refuse("MISSING_SUBJECT")
        return bound_int(value, 0, _CLOCK_MAX)
    raise Refuse("BAD_PLAN")


def _idle_number(value: object) -> int:
    if isinstance(value, bool):
        raise Refuse("NOT_INT")
    if value is None or value == 0:
        return 0
    if not isinstance(value, int):
        raise Refuse("NOT_INT")
    raise Refuse("UNEXPECTED")


def _policy_cap(kind: str) -> int:
    if kind == "page":
        return PAGE_CAP
    if kind == "batch":
        return BATCH_CAP
    return QUERY_CAP


def _lookup(tool: object, action: object) -> _Spec:
    if not isinstance(tool, str):
        raise Refuse("BAD_TOOL")
    tool_text = bound_text(tool, 32)
    if secret_shape(tool_text):
        raise Refuse("SECRET")
    _no_controls(tool_text)
    if tool_text not in _TOOL_SET:
        raise Refuse("BAD_TOOL")
    if not isinstance(action, str):
        raise Refuse("BAD_ACTION")
    action_text = bound_text(action, 32)
    if secret_shape(action_text):
        raise Refuse("SECRET")
    _no_controls(action_text)
    found = _SPECS.get((tool_text, action_text))
    if found is None:
        raise Refuse("BAD_ACTION")
    return found


def _esc(text: str) -> str:
    return (
        text.replace("%", "%25")
        .replace("&", "%26")
        .replace("=", "%3D")
        .replace(",", "%2C")
        .replace("|", "%7C")
        .replace("\n", "%0A")
        .replace("\r", "%0D")
    )


def _unesc(text: str) -> str:
    if "%" not in text:
        return text
    out: list[str] = []
    index = 0
    size = len(text)
    while index < size:
        char = text[index]
        if char != "%":
            out.append(char)
            index += 1
            continue
        if index + 3 > size:
            raise Refuse("BAD_RECORD")
        key = text[index + 1 : index + 3]
        piece = _UNESC.get(key)
        if piece is None:
            raise Refuse("BAD_RECORD")
        out.append(piece)
        index += 3
    return "".join(out)


def _encode(pairs: tuple[tuple[str, str], ...]) -> str:
    return "&".join(key + "=" + _esc(value) for key, value in pairs)


def _decode(body: str, keys: tuple[str, ...]) -> dict[str, str]:
    parts = body.split("&")
    if len(parts) != len(keys):
        raise Refuse("BAD_RECORD")
    found: dict[str, str] = {}
    index = 0
    for part in parts:
        key, sep, value = part.partition("=")
        expect = keys[index]
        if sep != "=" or key != expect:
            raise Refuse("BAD_RECORD")
        found[key] = _unesc(value)
        index += 1
    return found


def _join(items: tuple[str, ...]) -> str:
    return ",".join(_esc(item) for item in items)


def _split_items(text: str) -> tuple[str, ...]:
    if text == "":
        return ()
    return tuple(_unesc(part) for part in text.split(","))


def _parse_int(text: str, hi: int) -> int:
    if text == "0":
        return 0
    if text == "" or text[0] == "0" or any(ch not in _DIGITS for ch in text):
        raise Refuse("BAD_RECORD")
    if len(text) > 16:
        raise Refuse("BAD_RECORD")
    value = int(text)
    if value > hi:
        raise Refuse("BAD_RECORD")
    return value


def _parse_bit(text: str) -> bool:
    if text == "1":
        return True
    if text == "0":
        return False
    raise Refuse("BAD_RECORD")


def _digest(seq: int, kind: str, body: str, prev: str, at: int) -> str:
    raw = f"{SCHEMA}|{seq}|{kind}|{body}|{prev}|{at}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _failure(value: object) -> str:
    text = bound_text(value, 32)
    if secret_shape(text):
        raise Refuse("SECRET")
    _no_controls(text)
    if text not in _FAILURES:
        raise Refuse("NOT_RETRYABLE")
    return text


@dataclass(frozen=True, slots=True, kw_only=True)
class Play:
    """One non-executing play of a single track id."""

    schema: str
    credential_id: str
    tier: str
    track_id: str
    uri: str
    device_id: str
    position_ms: int
    cap: int
    premium: bool
    executes: bool
    at: int

    def __post_init__(self) -> None:
        _schema(self.schema)
        if self.executes is not False or self.premium is not True:
            raise Refuse("BAD_PLAN")
        if type(self.cap) is not int or self.cap != QUERY_CAP:
            raise Refuse("BAD_CAP")
        rank = _tier(self.tier)
        if not const_eq(rank, self.tier):
            raise Refuse("BAD_TIER")
        if rank == "free":
            raise Refuse("PREMIUM")
        checked = _cred(self.credential_id)
        if not const_eq(checked, self.credential_id):
            raise Refuse("BAD_CREDENTIAL")
        ident = _track(self.track_id, QUERY_CAP)
        if not const_eq(ident, self.track_id):
            raise Refuse("BAD_TRACK")
        if self.uri != "spotify:track:" + ident:
            raise Refuse("BAD_PLAN")
        device = _device(self.device_id, required=False)
        if device != self.device_id:
            raise Refuse("BAD_DEVICE")
        bound_int(self.position_ms, 0, POSITION_MAX)
        bound_int(self.at, 0, _CLOCK_MAX)

    def __repr__(self) -> str:
        body = (
            "Play("
            f"schema={self.schema!r}, credential_id={self.credential_id!r}, "
            f"tier={self.tier!r}, track_id={self.track_id!r}, uri={self.uri!r}, "
            f"device_id={self.device_id!r}, position_ms={self.position_ms}, "
            f"cap={self.cap}, premium={self.premium}, executes={self.executes}, at={self.at})"
        )
        return redact(body)


@dataclass(frozen=True, slots=True, kw_only=True)
class Action:
    """One catalog or playback descriptor. `executes` stays false."""

    schema: str
    tool: str
    action: str
    credential_id: str
    tier: str
    subject: str
    extra: tuple[str, ...]
    skipped: tuple[str, ...]
    device_id: str
    limit: int
    offset: int
    number: int
    flag: str
    premium: bool
    executes: bool
    cap: int
    at: int

    def __post_init__(self) -> None:
        _check_action(self)

    def __repr__(self) -> str:
        body = (
            "Action("
            f"tool={self.tool!r}, action={self.action!r}, "
            f"credential_id={self.credential_id!r}, tier={self.tier!r}, "
            f"subject={self.subject!r}, extra={len(self.extra)}, "
            f"skipped={len(self.skipped)}, device_id={self.device_id!r}, "
            f"limit={self.limit}, offset={self.offset}, number={self.number}, "
            f"flag={self.flag!r}, premium={self.premium}, executes={self.executes}, "
            f"cap={self.cap}, at={self.at})"
        )
        return redact(body)


def _check_action(plan: Action) -> None:
    _schema(plan.schema)
    if plan.executes is not False:
        raise Refuse("BAD_PLAN")
    spec = _lookup(plan.tool, plan.action)
    if plan.premium is not spec.premium:
        raise Refuse("BAD_PLAN")
    rank = _tier(plan.tier)
    if not const_eq(rank, plan.tier):
        raise Refuse("BAD_TIER")
    if spec.premium and rank == "free":
        raise Refuse("PREMIUM")
    checked = _cred(plan.credential_id)
    if not const_eq(checked, plan.credential_id):
        raise Refuse("BAD_CREDENTIAL")
    expected = _policy_cap(spec.cap_kind)
    if type(plan.cap) is not int or plan.cap != expected:
        raise Refuse("BAD_CAP")
    if type(plan.limit) is not int or type(plan.offset) is not int or type(plan.number) is not int:
        raise Refuse("BAD_PLAN")
    _check_bounds(spec, plan)
    _check_subject(spec, plan.subject)
    _check_items(spec, plan.extra, plan.skipped, plan.limit)
    flag = _flag(spec.flag, plan.flag)
    if flag != plan.flag:
        raise Refuse("BAD_PLAN")
    number = _number(spec.number, plan.number, flag)
    if number != plan.number:
        raise Refuse("BAD_PLAN")
    device = _stored_device(spec, plan.device_id)
    if device != plan.device_id:
        raise Refuse("BAD_DEVICE")
    bound_int(plan.at, 0, _CLOCK_MAX)


def _check_bounds(spec: _Spec, plan: Action) -> None:
    if spec.cap_kind == "text":
        if plan.limit != 0:
            raise Refuse("UNEXPECTED")
    elif spec.cap_kind == "search" or spec.cap_kind == "page":
        if plan.limit < 1 or plan.limit > PAGE_CAP:
            raise Refuse("BAD_CAP")
    elif plan.limit < 1 or plan.limit > BATCH_CAP:
        raise Refuse("BAD_CAP")
    if spec.offset == "no":
        if plan.offset != 0:
            raise Refuse("UNEXPECTED")
        return
    if plan.offset < 0 or plan.offset > OFFSET_MAX:
        raise Refuse("OUT_OF_RANGE")


def _check_subject(spec: _Spec, subject: str) -> None:
    if spec.subject == "no":
        if subject != "":
            raise Refuse("UNEXPECTED")
        return
    if spec.subject == "query" or spec.subject == "name":
        phrase = _phrase(subject, QUERY_CAP)
        if phrase != subject:
            raise Refuse("BAD_PLAN")
        return
    if spec.subject == "track":
        ident = _track(subject, QUERY_CAP)
        if not const_eq(ident, subject):
            raise Refuse("BAD_TRACK")
        return
    if spec.subject == "album" or spec.subject == "playlist":
        ident = _spotify_id(subject, "BAD_ID")
        if not const_eq(ident, subject):
            raise Refuse("BAD_ID")
        return
    raise Refuse("BAD_PLAN")


def _check_items(
    spec: _Spec,
    extra: tuple[str, ...],
    skipped: tuple[str, ...],
    limit: int,
) -> None:
    if type(extra) is not tuple or type(skipped) is not tuple:
        raise Refuse("BAD_ITEMS")
    if spec.items == "no":
        if extra != () or skipped != ():
            raise Refuse("UNEXPECTED")
        return
    if spec.items == "types":
        if skipped != () or _types(extra) != extra:
            raise Refuse("BAD_PLAN")
        return
    if spec.items != "ids":
        raise Refuse("BAD_PLAN")
    combined = extra + skipped
    kept, later = _budget_ids(combined, limit)
    if kept != extra or later != skipped:
        raise Refuse("BAD_PLAN")


def _stored_device(spec: _Spec, device_id: str) -> str:
    if spec.device == "no":
        if device_id != "":
            raise Refuse("UNEXPECTED")
        return ""
    return _device(device_id, required=spec.device == "req")


@dataclass(frozen=True, slots=True, kw_only=True)
class Packed:
    """Titles that fit a character budget, plus the titles that were skipped."""

    schema: str
    credential_id: str
    titles: tuple[str, ...]
    kept: tuple[str, ...]
    skipped: tuple[str, ...]
    budget: int
    cap: int
    executes: bool
    at: int

    def __post_init__(self) -> None:
        _schema(self.schema)
        if self.executes is not False:
            raise Refuse("BAD_PLAN")
        if type(self.cap) is not int or self.cap != CHAR_BUDGET:
            raise Refuse("BAD_CAP")
        if type(self.budget) is not int or self.budget < 1 or self.budget > CHAR_BUDGET:
            raise Refuse("BAD_CAP")
        checked = _cred(self.credential_id)
        if not const_eq(checked, self.credential_id):
            raise Refuse("BAD_CREDENTIAL")
        if type(self.titles) is not tuple or len(self.titles) == 0:
            raise Refuse("EMPTY")
        if len(self.titles) > INPUT_CAP:
            raise Refuse("OVERSIZE", str(INPUT_CAP))
        cleaned: list[str] = []
        for item in self.titles:
            cleaned.append(_phrase(item, QUERY_CAP))
        canonical = tuple(cleaned)
        if canonical != self.titles:
            raise Refuse("BAD_PLAN")
        kept, skipped = _select(canonical, self.budget)
        if type(self.kept) is not tuple or type(self.skipped) is not tuple:
            raise Refuse("BAD_ITEMS")
        if kept != self.kept or skipped != self.skipped:
            raise Refuse("BAD_PLAN")
        bound_int(self.at, 0, _CLOCK_MAX)

    def __repr__(self) -> str:
        body = (
            "Packed("
            f"credential_id={self.credential_id!r}, kept={len(self.kept)}, "
            f"skipped={len(self.skipped)}, budget={self.budget}, cap={self.cap}, "
            f"executes={self.executes}, at={self.at})"
        )
        return redact(body)


@dataclass(frozen=True, slots=True, kw_only=True)
class Note:
    """One confirming retry for HTTP 401. This note does not refresh a token."""

    schema: str
    credential_id: str
    code: str
    attempt: int
    executes: bool
    at: int

    def __post_init__(self) -> None:
        _schema(self.schema)
        if self.executes is not False:
            raise Refuse("BAD_PLAN")
        if type(self.attempt) is not int or self.attempt != 1:
            raise Refuse("BAD_PLAN")
        if self.code != RETRY_CLASS:
            raise Refuse("NOT_RETRYABLE")
        checked = _cred(self.credential_id)
        if not const_eq(checked, self.credential_id):
            raise Refuse("BAD_CREDENTIAL")
        bound_int(self.at, 0, _CLOCK_MAX)

    def __repr__(self) -> str:
        body = (
            "Note("
            f"credential_id={self.credential_id!r}, code={self.code!r}, "
            f"attempt={self.attempt}, executes={self.executes}, at={self.at})"
        )
        return redact(body)


@dataclass(frozen=True, slots=True, kw_only=True)
class Row:
    """One hash-linked ledger row. The digest covers the body once."""

    schema: str
    seq: int
    kind: str
    body: str
    prev: str
    digest: str
    at: int

    def __post_init__(self) -> None:
        _schema(self.schema)
        if type(self.seq) is not int or self.seq < 0 or self.seq >= ROW_CAP:
            raise Refuse("BAD_RECORD")
        if self.kind not in _ROW_KINDS:
            raise Refuse("BAD_RECORD")
        if type(self.at) is not int or self.at < 0 or self.at > _CLOCK_MAX:
            raise Refuse("BAD_RECORD")
        if not isinstance(self.body, str) or len(self.body) > _BODY_CAP:
            raise Refuse("BAD_RECORD")
        if secret_shape(self.body) or secret_shape(self.kind):
            raise Refuse("SECRET")
        if not isinstance(self.prev, str) or _HEX_RE.fullmatch(self.prev) is None:
            raise Refuse("CHAIN")
        expect = _digest(self.seq, self.kind, self.body, self.prev, self.at)
        if not isinstance(self.digest, str) or not const_eq(self.digest, expect):
            raise Refuse("CHAIN")

    def __repr__(self) -> str:
        return redact(
            f"Row(seq={self.seq}, kind={self.kind!r}, at={self.at}, digest={self.digest!r})"
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class Snapshot:
    """Public state restored from the ledger."""

    schema: str
    enabled: bool
    credential_id: str
    tier: str
    plays: tuple[Play, ...]
    actions: tuple[Action, ...]
    packed: tuple[Packed, ...]
    notes: tuple[Note, ...]
    at: int
    tip: str

    def __post_init__(self) -> None:
        _schema(self.schema)
        if not isinstance(self.enabled, bool):
            raise Refuse("BAD_PLAN")
        if not isinstance(self.tip, str) or _HEX_RE.fullmatch(self.tip) is None:
            raise Refuse("CHAIN")
        bound_int(self.at, 0, _CLOCK_MAX)
        _check_group(self.plays, Play)
        _check_group(self.actions, Action)
        _check_group(self.packed, Packed)
        _check_group(self.notes, Note)
        if not self.enabled:
            if (
                self.credential_id != ""
                or self.tier != ""
                or self.plays != ()
                or self.actions != ()
                or self.packed != ()
                or self.notes != ()
                or self.at != 0
                or not const_eq(self.tip, GENESIS)
            ):
                raise Refuse("BAD_PLAN")
            return
        checked = _cred(self.credential_id)
        if not const_eq(checked, self.credential_id):
            raise Refuse("BAD_CREDENTIAL")
        rank = _tier(self.tier)
        if not const_eq(rank, self.tier):
            raise Refuse("BAD_TIER")

    def __repr__(self) -> str:
        state = "enabled" if self.enabled else "disabled"
        return redact(
            f"Snapshot({state}, credential_id={self.credential_id!r}, tier={self.tier!r}, "
            f"plays={len(self.plays)}, actions={len(self.actions)}, at={self.at})"
        )


def _check_group(items: object, kind: type[object]) -> None:
    if type(items) is not tuple:
        raise Refuse("BAD_PLAN")
    for item in items:
        if type(item) is not kind:
            raise Refuse("BAD_PLAN")


def _empty_snapshot() -> Snapshot:
    return Snapshot(
        schema=SCHEMA,
        enabled=False,
        credential_id="",
        tier="",
        plays=(),
        actions=(),
        packed=(),
        notes=(),
        at=0,
        tip=GENESIS,
    )


class Spotify:
    """Opt-in Spotify plans. Starts disabled. There is no off switch and no token."""

    __slots__ = (
        "_actions",
        "_at",
        "_confirms",
        "_cred",
        "_notes",
        "_on",
        "_packed",
        "_plays",
        "_rows",
        "_tier",
    )

    def __init__(self) -> None:
        self._on = False
        self._cred = ""
        self._tier = ""
        self._at = -1
        self._confirms = 0
        self._rows: list[Row] = []
        self._plays: list[Play] = []
        self._actions: list[Action] = []
        self._packed: list[Packed] = []
        self._notes: list[Note] = []

    def __repr__(self) -> str:
        if not self._on:
            return "Spotify(disabled)"
        return redact(
            f"Spotify(enabled, credential_id={self._cred!r}, tier={self._tier!r})"
        )

    @property
    def enabled(self) -> bool:
        return self._on

    @property
    def credential_id(self) -> str:
        if not self._on:
            return ""
        return self._cred

    @property
    def tier(self) -> str:
        if not self._on:
            return ""
        return self._tier

    def enable(self, credential_id: object, *, tier: object = "unverified", now: object) -> None:
        """Arm plans with a credential id. A raw token is refused. There is no off."""
        cred = _cred(credential_id)
        rank = _tier(tier)
        moment = _now(now)
        if self._on:
            if not (const_eq(cred, self._cred) and const_eq(rank, self._tier)):
                raise Refuse("CRED_LOCKED")
            if moment < self._at:
                raise Refuse("STALE")
            return
        body = _encode((("cred", cred), ("tier", rank)))
        self._commit("enable", body, moment)
        self._on = True
        self._cred = cred
        self._tier = rank

    def play(
        self,
        track_id: object,
        *,
        device_id: object = "",
        position_ms: object = 0,
        cap: object = None,
        now: object,
    ) -> Play:
        """Return a play descriptor. Disabled calls raise DISABLED. No socket."""
        if not self._on:
            raise Refuse("DISABLED")
        applied = _clamp(cap, QUERY_CAP)
        ident = _track(track_id, applied)
        device = _device(device_id, required=False)
        position = bound_int(position_ms, 0, POSITION_MAX)
        moment = _now(now)
        plan = Play(
            schema=SCHEMA,
            credential_id=self._cred,
            tier=self._tier,
            track_id=ident,
            uri="spotify:track:" + ident,
            device_id=device,
            position_ms=position,
            cap=QUERY_CAP,
            premium=True,
            executes=False,
            at=moment,
        )
        body = _encode(
            (
                ("cred", plan.credential_id),
                ("tier", plan.tier),
                ("track", plan.track_id),
                ("device", plan.device_id),
                ("position", str(plan.position_ms)),
                ("cap", str(plan.cap)),
            )
        )
        self._commit("play", body, moment)
        self._plays.append(plan)
        return plan

    def pause(self, *, device_id: object = "", cap: object = None, now: object) -> Action:
        """Return a pause descriptor. Premium accounts only. No socket."""
        return self.act("playback", "pause", device_id=device_id, cap=cap, now=now)

    def search(
        self,
        query: object,
        *,
        types: object = None,
        limit: object = None,
        offset: object = 0,
        market: object = "",
        cap: object = None,
        now: object,
    ) -> Action:
        """Return a catalog search descriptor. The query is required."""
        return self.act(
            "search",
            "search",
            subject=query,
            items=types,
            limit=limit,
            offset=offset,
            flag=market,
            cap=cap,
            now=now,
        )

    def act(
        self,
        tool: object,
        action: object,
        *,
        subject: object = "",
        items: object = None,
        device_id: object = "",
        limit: object = None,
        offset: object = 0,
        number: object = None,
        flag: object = "",
        cap: object = None,
        now: object,
    ) -> Action:
        """Return one tool descriptor. A higher cap is ignored. No socket."""
        if not self._on:
            raise Refuse("DISABLED")
        spec = _lookup(tool, action)
        text_limit = _clamp(cap, QUERY_CAP)
        applied_limit = _applied_limit(spec, limit)
        moved = bound_int(offset, 0, OFFSET_MAX)
        if spec.offset == "no" and moved != 0:
            raise Refuse("UNEXPECTED")
        stored_flag = _flag(spec.flag, flag)
        stored_number = _number(spec.number, number, stored_flag)
        device = _input_device(spec, device_id)
        stored_subject = _input_subject(spec, subject, text_limit)
        extra, skipped = _input_items(spec, items, applied_limit)
        if spec.premium and self._tier == "free":
            raise Refuse("PREMIUM")
        moment = _now(now)
        plan = Action(
            schema=SCHEMA,
            tool=spec.tool,
            action=spec.action,
            credential_id=self._cred,
            tier=self._tier,
            subject=stored_subject,
            extra=extra,
            skipped=skipped,
            device_id=device,
            limit=applied_limit,
            offset=moved,
            number=stored_number,
            flag=stored_flag,
            premium=spec.premium,
            executes=False,
            cap=_policy_cap(spec.cap_kind),
            at=moment,
        )
        body = _encode(_action_pairs(plan))
        self._commit("action", body, moment)
        self._actions.append(plan)
        return plan

    def pack(self, titles: object, *, budget: object = None, now: object) -> Packed:
        """Pack titles under the character budget. Skip a title that does not fit."""
        if not self._on:
            raise Refuse("DISABLED")
        applied = _clamp(budget, CHAR_BUDGET)
        raw = _as_tuple(titles)
        if len(raw) == 0:
            raise Refuse("EMPTY")
        if len(raw) > INPUT_CAP:
            raise Refuse("OVERSIZE", str(INPUT_CAP))
        cleaned: list[str] = []
        seen: set[str] = set()
        for item in raw:
            title = _phrase(item, QUERY_CAP)
            if title in seen:
                raise Refuse("DUPLICATE")
            seen.add(title)
            cleaned.append(title)
        canonical = tuple(cleaned)
        kept, skipped = _select(canonical, applied)
        moment = _now(now)
        packed = Packed(
            schema=SCHEMA,
            credential_id=self._cred,
            titles=canonical,
            kept=kept,
            skipped=skipped,
            budget=applied,
            cap=CHAR_BUDGET,
            executes=False,
            at=moment,
        )
        body = _encode(
            (
                ("cred", packed.credential_id),
                ("budget", str(packed.budget)),
                ("cap", str(packed.cap)),
                ("titles", _join(packed.titles)),
                ("kept", _join(packed.kept)),
                ("skipped", _join(packed.skipped)),
            )
        )
        self._commit("pack", body, moment)
        self._packed.append(packed)
        return packed

    def note_failure(self, code: object, *, confirm: object = False, now: object) -> Note:
        """Record one confirming retry for HTTP 401. A second one is refused."""
        if not self._on:
            raise Refuse("DISABLED")
        moment = _now(now)
        if not isinstance(confirm, bool):
            raise Refuse("BAD_FLAG")
        label = _failure(code)
        if label != RETRY_CLASS or confirm is not True:
            raise Refuse("NOT_RETRYABLE")
        if self._confirms != 0:
            raise Refuse("RETRY_SPENT")
        note = Note(
            schema=SCHEMA,
            credential_id=self._cred,
            code=RETRY_CLASS,
            attempt=1,
            executes=False,
            at=moment,
        )
        body = _encode(
            (
                ("cred", note.credential_id),
                ("code", note.code),
                ("attempt", str(note.attempt)),
            )
        )
        self._commit("confirm", body, moment)
        self._confirms = 1
        self._notes.append(note)
        return note

    def records(self) -> tuple[Row, ...]:
        """Ledger rows in commit order."""
        return tuple(self._rows)

    def snapshot(self) -> Snapshot:
        """Public state. Equal to `rebuild` of `records`."""
        if not self._on:
            return _empty_snapshot()
        tip = GENESIS if not self._rows else self._rows[-1].digest
        moment = 0 if self._at < 0 else self._at
        return Snapshot(
            schema=SCHEMA,
            enabled=True,
            credential_id=self._cred,
            tier=self._tier,
            plays=tuple(self._plays),
            actions=tuple(self._actions),
            packed=tuple(self._packed),
            notes=tuple(self._notes),
            at=moment,
            tip=tip,
        )

    def _commit(self, kind: str, body: str, moment: int) -> None:
        if self._at >= 0 and moment <= self._at:
            raise Refuse("STALE")
        if len(self._rows) >= ROW_CAP:
            raise Refuse("OVERSIZE", str(ROW_CAP))
        prev = GENESIS if not self._rows else self._rows[-1].digest
        seq = len(self._rows)
        digest = _digest(seq, kind, body, prev, moment)
        row = Row(
            schema=SCHEMA,
            seq=seq,
            kind=kind,
            body=body,
            prev=prev,
            digest=digest,
            at=moment,
        )
        self._rows.append(row)
        self._at = moment


def _applied_limit(spec: _Spec, limit: object) -> int:
    if spec.cap_kind == "text":
        if limit is not None:
            raise Refuse("UNEXPECTED")
        return 0
    if spec.cap_kind == "batch":
        return _clamp(limit, BATCH_CAP)
    return _clamp(limit, PAGE_CAP)


def _input_device(spec: _Spec, device_id: object) -> str:
    if not isinstance(device_id, str):
        raise Refuse("NOT_TEXT")
    if spec.device == "no":
        if device_id != "":
            raise Refuse("UNEXPECTED")
        return ""
    return _device(device_id, required=spec.device == "req")


def _input_subject(spec: _Spec, subject: object, text_limit: int) -> str:
    if spec.subject == "no":
        if subject != "":
            raise Refuse("UNEXPECTED")
        return ""
    if spec.subject == "query" or spec.subject == "name":
        return _phrase(subject, text_limit)
    if spec.subject == "track":
        return _track(subject, _URI_CAP)
    if spec.subject == "album" or spec.subject == "playlist":
        return _spotify_id(subject, "BAD_ID")
    raise Refuse("BAD_PLAN")


def _input_items(
    spec: _Spec,
    items: object,
    budget: int,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if spec.items == "no":
        if items is not None:
            raise Refuse("UNEXPECTED")
        return (), ()
    if spec.items == "types":
        raw = ("track",) if items is None else _as_tuple(items)
        return _types(raw), ()
    if items is None:
        raise Refuse("EMPTY")
    raw = _as_tuple(items)
    if len(raw) == 0:
        raise Refuse("EMPTY")
    return _budget_ids(raw, budget)


def _action_pairs(plan: Action) -> tuple[tuple[str, str], ...]:
    bit = "1" if plan.premium else "0"
    return (
        ("cred", plan.credential_id),
        ("tier", plan.tier),
        ("tool", plan.tool),
        ("action", plan.action),
        ("subject", plan.subject),
        ("extra", _join(plan.extra)),
        ("skipped", _join(plan.skipped)),
        ("device", plan.device_id),
        ("limit", str(plan.limit)),
        ("offset", str(plan.offset)),
        ("number", str(plan.number)),
        ("flag", plan.flag),
        ("premium", bit),
        ("cap", str(plan.cap)),
    )


def _row_at(rows: tuple[Row, ...], index: int) -> Row:
    if index < 0 or index >= len(rows):
        raise Refuse("CHAIN")
    return rows[index]


def rebuild(rows: object) -> Snapshot:
    """Replay caller-supplied rows into the same public snapshot."""
    parsed = _parse_rows(rows)
    if len(parsed) == 0:
        return _empty_snapshot()
    cred = ""
    rank = ""
    plays: list[Play] = []
    actions: list[Action] = []
    packed: list[Packed] = []
    notes: list[Note] = []
    previous = ""
    last_at = -1
    index = 0
    for row in parsed:
        if row.seq != index:
            raise Refuse("CHAIN")
        if index == 0:
            if row.kind != "enable" or not const_eq(row.prev, GENESIS):
                raise Refuse("CHAIN")
        elif row.prev != previous:
            raise Refuse("CHAIN")
        if last_at >= 0 and row.at <= last_at:
            raise Refuse("STALE")
        cred, rank = _apply_row(row, cred, rank, plays, actions, packed, notes)
        previous = row.digest
        last_at = row.at
        index += 1
    tip = previous if previous != "" else GENESIS
    moment = 0 if last_at < 0 else last_at
    return Snapshot(
        schema=SCHEMA,
        enabled=True,
        credential_id=cred,
        tier=rank,
        plays=tuple(plays),
        actions=tuple(actions),
        packed=tuple(packed),
        notes=tuple(notes),
        at=moment,
        tip=tip,
    )


def _parse_rows(rows: object) -> tuple[Row, ...]:
    if isinstance(rows, (str, bytes, bytearray)) or not isinstance(rows, tuple):
        raise Refuse("BAD_RECORD")
    parsed: list[Row] = []
    for item in rows:
        if type(item) is not Row:
            raise Refuse("BAD_RECORD")
        parsed.append(item)
    return tuple(parsed)


def _apply_row(
    row: Row,
    cred: str,
    rank: str,
    plays: list[Play],
    actions: list[Action],
    packed: list[Packed],
    notes: list[Note],
) -> tuple[str, str]:
    if row.kind == "enable":
        if cred != "":
            raise Refuse("CHAIN")
        return _apply_enable(row), _enable_tier(row)
    if cred == "":
        raise Refuse("CHAIN")
    if row.kind == "play":
        plays.append(_apply_play(row, cred, rank))
        return cred, rank
    if row.kind == "action":
        actions.append(_apply_action(row, cred, rank))
        return cred, rank
    if row.kind == "pack":
        packed.append(_apply_pack(row, cred))
        return cred, rank
    if row.kind == "confirm":
        if len(notes) != 0:
            raise Refuse("RETRY_SPENT")
        notes.append(_apply_note(row, cred))
        return cred, rank
    raise Refuse("BAD_RECORD")


def _enable_tier(row: Row) -> str:
    found = _decode(row.body, _ENABLE_KEYS)
    rank = _tier(found["tier"])
    if not const_eq(rank, found["tier"]):
        raise Refuse("BAD_TIER")
    return rank


def _apply_enable(row: Row) -> str:
    found = _decode(row.body, _ENABLE_KEYS)
    cred = _cred(found["cred"])
    if not const_eq(cred, found["cred"]):
        raise Refuse("BAD_CREDENTIAL")
    return cred


def _match(found: str, expect: str) -> None:
    if not const_eq(found, expect):
        raise Refuse("BAD_RECORD")


def _apply_play(row: Row, cred: str, rank: str) -> Play:
    found = _decode(row.body, _PLAY_KEYS)
    _match(found["cred"], cred)
    _match(found["tier"], rank)
    ident = found["track"]
    return Play(
        schema=SCHEMA,
        credential_id=cred,
        tier=rank,
        track_id=ident,
        uri="spotify:track:" + ident,
        device_id=found["device"],
        position_ms=_parse_int(found["position"], POSITION_MAX),
        cap=_parse_int(found["cap"], QUERY_CAP),
        premium=True,
        executes=False,
        at=row.at,
    )


def _apply_action(row: Row, cred: str, rank: str) -> Action:
    found = _decode(row.body, _ACTION_KEYS)
    _match(found["cred"], cred)
    _match(found["tier"], rank)
    return Action(
        schema=SCHEMA,
        tool=found["tool"],
        action=found["action"],
        credential_id=cred,
        tier=rank,
        subject=found["subject"],
        extra=_split_items(found["extra"]),
        skipped=_split_items(found["skipped"]),
        device_id=found["device"],
        limit=_parse_int(found["limit"], _CLOCK_MAX),
        offset=_parse_int(found["offset"], OFFSET_MAX),
        number=_parse_int(found["number"], _CLOCK_MAX),
        flag=found["flag"],
        premium=_parse_bit(found["premium"]),
        executes=False,
        cap=_parse_int(found["cap"], QUERY_CAP),
        at=row.at,
    )


def _apply_pack(row: Row, cred: str) -> Packed:
    found = _decode(row.body, _PACK_KEYS)
    _match(found["cred"], cred)
    return Packed(
        schema=SCHEMA,
        credential_id=cred,
        titles=_split_items(found["titles"]),
        kept=_split_items(found["kept"]),
        skipped=_split_items(found["skipped"]),
        budget=_parse_int(found["budget"], CHAR_BUDGET),
        cap=_parse_int(found["cap"], CHAR_BUDGET),
        executes=False,
        at=row.at,
    )


def _apply_note(row: Row, cred: str) -> Note:
    found = _decode(row.body, _NOTE_KEYS)
    _match(found["cred"], cred)
    return Note(
        schema=SCHEMA,
        credential_id=cred,
        code=found["code"],
        attempt=_parse_int(found["attempt"], 1),
        executes=False,
        at=row.at,
    )


def run(descriptor: object) -> None:
    """Descriptors are not executed here."""
    if (
        type(descriptor) is Play
        or type(descriptor) is Action
        or type(descriptor) is Packed
        or type(descriptor) is Note
    ):
        raise Refuse("NOT_RUN")
    raise Refuse("BAD_PLAN")


def classify_status(code: object) -> str:
    """Name a caller-supplied HTTP status. This does not perform a request."""
    if isinstance(code, bool) or not isinstance(code, int):
        raise Refuse("NOT_INT")
    found = _STATUS.get(code)
    if found is None:
        raise Refuse("UNCLASSIFIED")
    return found


_STATUS: Final[dict[int, str]] = {
    204: "empty",
    401: "refresh",
    403: "forbidden",
    429: "rate",
}


__all__ = [
    "BATCH_CAP",
    "CHAR_BUDGET",
    "CRED_CAP",
    "DEVICE_CAP",
    "GENESIS",
    "ID_CAP",
    "INPUT_CAP",
    "OFFSET_MAX",
    "PAGE_CAP",
    "POSITION_MAX",
    "QUERY_CAP",
    "RETRY_CLASS",
    "ROW_CAP",
    "SCHEMA",
    "SEARCH_TYPES",
    "TOOLS",
    "VOLUME_MAX",
    "Action",
    "Note",
    "Packed",
    "Play",
    "Row",
    "Snapshot",
    "Spotify",
    "classify_status",
    "rebuild",
    "run",
]
