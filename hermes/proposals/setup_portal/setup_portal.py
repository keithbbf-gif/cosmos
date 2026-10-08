"""Portal setup plan. The hash is the record. No port and no secret on disk.

Credential ids only. `open_port` and `save` refuse. A later service would
execute the descriptor.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final, cast

from cosmos_hermes import Refuse, bound_int, bound_text, const_eq, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-setup_portal/1"
NAME_CAP: Final[int] = 32
TOOL_CAP: Final[int] = 4
CRED_CAP: Final[int] = 8
CRED_LEN: Final[int] = 64
TOOLS: Final[tuple[str, ...]] = ("browser", "image", "tts", "web")
LOOPBACK: Final[str] = "127.0.0.1"
RETRY_CLASS: Final[str] = "CALLBACK_UNREACHABLE"
MAX_CONFIRMING_RETRIES: Final[int] = 1

_ASK_HI: Final[int] = 1_000_000_000
_PORT_HI: Final[int] = 65535
_DEPTH_CAP: Final[int] = 8
_WIDTH: Final[int] = 32
_INT_LO: Final[int] = 0
_INT_HI: Final[int] = 1_000_000
_HOST_CAP: Final[int] = 253
_HASH_LEN: Final[int] = 64
_ALLOWED: Final[frozenset[str]] = frozenset(TOOLS)
_NAME: Final[re.Pattern[str]] = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
_RECORD_KEYS: Final[frozenset[str]] = frozenset(
    {
        "clamped",
        "cred_cap",
        "cred_ids",
        "listens",
        "name_cap",
        "plan_hash",
        "provider",
        "requested_cred_cap",
        "requested_name_cap",
        "requested_tool_cap",
        "schema",
        "tool_cap",
        "tools",
    }
)


@dataclass(frozen=True, slots=True)
class Plan:
    """One portal setup. `plan_hash` is sha256 of the canonical JSON body.

    `listens` is always false. Caps above policy are stored as requested and
    applied at the ceiling.
    """

    provider: str
    tools: tuple[str, ...]
    cred_ids: tuple[str, ...]
    plan_hash: str
    name_cap: int
    tool_cap: int
    cred_cap: int
    requested_name_cap: int
    requested_tool_cap: int
    requested_cred_cap: int
    clamped: bool
    listens: bool
    schema: str

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_RECORD")
        if type(self.listens) is not bool:
            raise Refuse("NOT_BOOL")
        if self.listens:
            raise Refuse("NO_SOCKET")
        if type(self.clamped) is not bool:
            raise Refuse("NOT_BOOL")
        applied_name = _applied(self.requested_name_cap, NAME_CAP)[0]
        applied_tool = _applied(self.requested_tool_cap, TOOL_CAP)[0]
        applied_cred = _applied(self.requested_cred_cap, CRED_CAP)[0]
        if (
            applied_name != self.name_cap
            or applied_tool != self.tool_cap
            or applied_cred != self.cred_cap
            or self.clamped
            is not _is_clamped(
                self.requested_name_cap,
                self.requested_tool_cap,
                self.requested_cred_cap,
            )
        ):
            raise Refuse("BAD_RECORD")
        provider = _named(self.provider, self.name_cap, "BAD_PROVIDER")
        tools = _tools(self.tools, self.tool_cap)
        cred_ids = _creds(self.cred_ids, self.cred_cap)
        if tools != self.tools:
            object.__setattr__(self, "tools", tools)
        if cred_ids != self.cred_ids:
            object.__setattr__(self, "cred_ids", cred_ids)
        digest = _digest(provider, tools, cred_ids)
        # Empty plan_hash is the seal sentinel. A stored digest is checked once.
        if self.plan_hash == "":
            object.__setattr__(self, "plan_hash", digest)
            return
        token = bound_text(self.plan_hash, _HASH_LEN)
        if secret_shape(token):
            raise Refuse("SECRET")
        if len(token) != _HASH_LEN or not const_eq(token, digest):
            raise Refuse("CHAIN")


@dataclass(frozen=True, slots=True)
class Confirm:
    """The one allowed confirming retry. Nothing is dialed."""

    plan_hash: str
    failure: str
    retries: int


def _is_clamped(name_asked: int, tool_asked: int, cred_asked: int) -> bool:
    return name_asked > NAME_CAP or tool_asked > TOOL_CAP or cred_asked > CRED_CAP


def _applied(asked: object, ceiling: int) -> tuple[int, int]:
    """Return `(applied, requested)`. A request above `ceiling` is ignored."""
    if type(asked) is not int:
        raise Refuse("NOT_INT")
    if asked < 1 or asked > _ASK_HI:
        raise Refuse("BAD_LIMIT")
    if asked > ceiling:
        return ceiling, asked
    return asked, asked


def _named(value: object, limit: int, code: str) -> str:
    text = bound_text(value, limit)
    if secret_shape(text):
        raise Refuse("SECRET")
    if _NAME.fullmatch(text) is None:
        raise Refuse(code)
    return text


def _string_tuple(value: object, shape: str, empty: str, cap: int) -> tuple[str, ...]:
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, (list, tuple)):
        raise Refuse(shape)
    count = len(value)
    if count == 0:
        raise Refuse(empty)
    if count > cap:
        raise Refuse("TOO_MANY")
    out: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise Refuse("NOT_TEXT")
        out.append(item)
    return tuple(out)


def _tools(items: tuple[str, ...], cap: int) -> tuple[str, ...]:
    if len(items) == 0:
        raise Refuse("EMPTY_ALLOW")
    if len(items) > cap:
        raise Refuse("TOO_MANY")
    seen: set[str] = set()
    for item in items:
        text = bound_text(item, NAME_CAP)
        if secret_shape(text):
            raise Refuse("SECRET")
        if text not in _ALLOWED:
            raise Refuse("BAD_TOOL")
        if text in seen:
            raise Refuse("DUPLICATE")
        seen.add(text)
    return tuple(sorted(seen))


def _creds(items: tuple[str, ...], cap: int) -> tuple[str, ...]:
    if len(items) == 0:
        raise Refuse("MISSING_ID")
    if len(items) > cap:
        raise Refuse("TOO_MANY")
    seen: set[str] = set()
    for item in items:
        text = _named(item, CRED_LEN, "BAD_CRED")
        if text in seen:
            raise Refuse("DUPLICATE")
        seen.add(text)
    return tuple(sorted(seen))


def _digest(provider: str, tools: tuple[str, ...], cred_ids: tuple[str, ...]) -> str:
    body: dict[str, object] = {
        "cred_ids": list(cred_ids),
        "provider": provider,
        "schema": SCHEMA,
        "tools": list(tools),
    }
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def plan(
    provider: object,
    tools: object,
    cred_ids: object,
    *,
    name_cap: object = NAME_CAP,
    tool_cap: object = TOOL_CAP,
    cred_cap: object = CRED_CAP,
) -> Plan:
    """Return a frozen portal plan. Order of tools and cred ids does not matter."""
    applied_name, requested_name = _applied(name_cap, NAME_CAP)
    applied_tool, requested_tool = _applied(tool_cap, TOOL_CAP)
    applied_cred, requested_cred = _applied(cred_cap, CRED_CAP)
    if not isinstance(provider, str):
        raise Refuse("NOT_TEXT")
    tool_values = _string_tuple(tools, "BAD_TOOL", "EMPTY_ALLOW", applied_tool)
    cred_values = _string_tuple(cred_ids, "BAD_CRED", "MISSING_ID", applied_cred)
    return Plan(
        provider=provider,
        tools=tool_values,
        cred_ids=cred_values,
        plan_hash="",
        name_cap=applied_name,
        tool_cap=applied_tool,
        cred_cap=applied_cred,
        requested_name_cap=requested_name,
        requested_tool_cap=requested_tool,
        requested_cred_cap=requested_cred,
        clamped=_is_clamped(requested_name, requested_tool, requested_cred),
        listens=False,
        schema=SCHEMA,
    )


def _scan_seq(items: list[object] | tuple[object, ...], depth: int) -> None:
    if depth >= _DEPTH_CAP:
        raise Refuse("TOO_DEEP")
    count = 0
    for item in items:
        count += 1
        if count > _WIDTH:
            raise Refuse("TOO_MANY")
        _scan(item, depth + 1)


def _scan_mapping(mapping: Mapping[object, object], depth: int) -> None:
    if depth >= _DEPTH_CAP:
        raise Refuse("TOO_DEEP")
    count = 0
    for key, item in mapping.items():
        count += 1
        if count > _WIDTH:
            raise Refuse("TOO_MANY")
        if type(key) is not str:
            raise Refuse("BAD_KEY")
        text = bound_text(key)
        if text == "":
            raise Refuse("BAD_KEY")
        if secret_shape(text):
            raise Refuse("SECRET")
        _scan(item, depth + 1)


def _scan(value: object, depth: int) -> None:
    if type(value) is str:
        text = bound_text(value)
        if secret_shape(text):
            raise Refuse("SECRET")
        return
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        bound_int(value, _INT_LO, _INT_HI)
        return
    if type(value) is list:
        _scan_seq(cast(list[object], value), depth)
        return
    if type(value) is tuple:
        _scan_seq(cast(tuple[object, ...], value), depth)
        return
    if isinstance(value, Mapping):
        _scan_mapping(cast(Mapping[object, object], value), depth)
        return
    raise Refuse("BAD_VALUE")


def persist(mapping: object) -> Mapping[str, object]:
    """Return `mapping` when no string is secret-shaped. Writes nothing."""
    if not isinstance(mapping, Mapping):
        raise Refuse("BAD_MAPPING")
    _scan_mapping(cast(Mapping[object, object], mapping), 0)
    return cast(Mapping[str, object], mapping)


def save(mapping: object) -> None:
    """Refuse to write. Secret-shaped text is `SECRET`. A clean mapping is `NO_DISK`."""
    persist(mapping)
    raise Refuse("NO_DISK")


def open_port(host: object = LOOPBACK, port: object = 0) -> None:
    """Refuse to bind. A portal callback is a later service, not this module."""
    text = bound_text(host, _HOST_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    if not const_eq(text, LOOPBACK):
        raise Refuse("BAD_HOST")
    if type(port) is not int:
        raise Refuse("NOT_INT")
    if port < 0 or port > _PORT_HI:
        raise Refuse("BAD_LIMIT")
    raise Refuse("NO_SOCKET")


def snapshot(made: object) -> dict[str, object]:
    """Public record of `made`. Replaying it through `rebuild` returns an equal plan."""
    if type(made) is not Plan:
        raise Refuse("BAD_PLAN")
    return {
        "clamped": made.clamped,
        "cred_cap": made.cred_cap,
        "cred_ids": list(made.cred_ids),
        "listens": made.listens,
        "name_cap": made.name_cap,
        "plan_hash": made.plan_hash,
        "provider": made.provider,
        "requested_cred_cap": made.requested_cred_cap,
        "requested_name_cap": made.requested_name_cap,
        "requested_tool_cap": made.requested_tool_cap,
        "schema": made.schema,
        "tool_cap": made.tool_cap,
        "tools": list(made.tools),
    }


def _take(mapping: Mapping[object, object], key: str) -> object:
    if key not in mapping:
        raise Refuse("BAD_RECORD")
    return mapping[key]


def _flag(value: object) -> bool:
    if type(value) is not bool:
        raise Refuse("NOT_BOOL")
    return value


def _record_int(value: object) -> int:
    if type(value) is not int:
        raise Refuse("NOT_INT")
    return value


def rebuild(record: object) -> Plan:
    """Reproduce a plan from `snapshot`. A mismatched hash is `CHAIN`."""
    if not isinstance(record, Mapping):
        raise Refuse("BAD_RECORD")
    mapping = cast(Mapping[object, object], record)
    keys: set[str] = set()
    for key in mapping:
        if type(key) is not str:
            raise Refuse("BAD_RECORD")
        keys.add(key)
    if keys != _RECORD_KEYS:
        raise Refuse("BAD_RECORD")
    if type(_take(mapping, "schema")) is not str or not const_eq(
        cast(str, _take(mapping, "schema")),
        SCHEMA,
    ):
        raise Refuse("BAD_RECORD")
    if _flag(_take(mapping, "listens")):
        raise Refuse("NO_SOCKET")
    clamped = _flag(_take(mapping, "clamped"))
    claimed = _take(mapping, "plan_hash")
    if type(claimed) is not str:
        raise Refuse("BAD_RECORD")
    claimed_text = bound_text(claimed, _HASH_LEN)
    if secret_shape(claimed_text):
        raise Refuse("SECRET")
    made = plan(
        _take(mapping, "provider"),
        _take(mapping, "tools"),
        _take(mapping, "cred_ids"),
        name_cap=_record_int(_take(mapping, "requested_name_cap")),
        tool_cap=_record_int(_take(mapping, "requested_tool_cap")),
        cred_cap=_record_int(_take(mapping, "requested_cred_cap")),
    )
    if (
        made.name_cap != _record_int(_take(mapping, "name_cap"))
        or made.tool_cap != _record_int(_take(mapping, "tool_cap"))
        or made.cred_cap != _record_int(_take(mapping, "cred_cap"))
        or made.clamped is not clamped
    ):
        raise Refuse("BAD_RECORD")
    if len(claimed_text) != _HASH_LEN or not const_eq(claimed_text, made.plan_hash):
        raise Refuse("CHAIN")
    return made


def same(left: object, right: object) -> bool:
    """True when both plans seal the same provider, tools, and credential ids."""
    if type(left) is not Plan or type(right) is not Plan:
        raise Refuse("BAD_PLAN")
    if not const_eq(left.plan_hash, right.plan_hash):
        return False
    return (
        left.provider == right.provider
        and left.tools == right.tools
        and left.cred_ids == right.cred_ids
    )


def confirm(made: object, failure: object, seen: object = 0) -> Confirm:
    """Authorize one confirming retry for `CALLBACK_UNREACHABLE`. Does not dial."""
    if type(made) is not Plan:
        raise Refuse("BAD_PLAN")
    if type(seen) is not int:
        raise Refuse("NOT_INT")
    if seen < 0 or seen > _ASK_HI:
        raise Refuse("BAD_LIMIT")
    text = bound_text(failure, NAME_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    if not const_eq(text, RETRY_CLASS):
        raise Refuse("UNCLASSIFIED")
    if seen >= MAX_CONFIRMING_RETRIES:
        raise Refuse("RETRY")
    return Confirm(plan_hash=made.plan_hash, failure=RETRY_CLASS, retries=seen + 1)


__all__ = [
    "CRED_CAP",
    "CRED_LEN",
    "Confirm",
    "LOOPBACK",
    "MAX_CONFIRMING_RETRIES",
    "NAME_CAP",
    "Plan",
    "RETRY_CLASS",
    "SCHEMA",
    "TOOL_CAP",
    "TOOLS",
    "confirm",
    "open_port",
    "persist",
    "plan",
    "rebuild",
    "same",
    "save",
    "snapshot",
]
