"""MCP client descriptors for COSMOS. Messages and filters only. No process is started."""

from __future__ import annotations

import fnmatch
import json
import math
import re
from collections.abc import Mapping
from dataclasses import dataclass, field

from cosmos_hermes import (
    PathJail,
    Refuse,
    bound_bytes,
    bound_int,
    bound_text,
    const_eq,
    redact,
    secret_shape,
)

SCHEMA = "cosmos-hermes-mcp/1"
PROTOCOL = "2024-11-05"
CLIENT_NAME = "cosmos-hermes-mcp"
CLIENT_VERSION = "1"
TOKEN_CAP = 4096
TIMEOUT_CAP = 30
DISCOVERY_CAP = 4
WINDOW_CAP = 120
DESC_BUDGET = 4_000
MAX_DEPTH = 8
MAX_TOOLS = 256
MAX_ITEMS = 64
MAX_NAME = 128
MAX_SERVER = 64
MAX_ARG = 512
MAX_ARGS = 32
MAX_PROMPT = 8_000
MAX_JSON = 32_000
MAX_URL = 512
MAX_STAMP = 10**12
MAX_INT = 10**12
POLICY_DENY: tuple[str, ...] = ("browser_run_code_unsafe",)
_POLICY_DENY = frozenset(POLICY_DENY)
_METHODS = frozenset({"initialize", "tools/list", "tools/call", "notifications/initialized"})
_RESERVED = frozenset({"mcp", "modelcontextprotocol"})
_RETRY = "TIMEOUT"
_SERVER = re.compile(r"^[A-Za-z][A-Za-z0-9._-]{0,63}$")
_TOOL = re.compile(r"^[A-Za-z0-9_.:@+-]{1,128}$")
_PATTERN = re.compile(r"^[A-Za-z0-9_.:@+*?\[\]-]{1,128}$")
_MODEL = re.compile(r"^[A-Za-z0-9_.:/+@-]{1,128}$")
_CRED = re.compile(r"^[A-Za-z][A-Za-z0-9_.:-]{0,63}$")
_GLOB = re.compile(r"[*?[]")
_NON_ALNUM = re.compile(r"[^A-Za-z0-9]+")
_URL_BAD = re.compile(r"[\s\x00-\x1f\x7f\\]")
_META_LABEL = r"[A-Za-z](?:[A-Za-z0-9-]*[A-Za-z0-9])?"
_META_KEY = re.compile(
    rf"^(?:{_META_LABEL}(?:\.{_META_LABEL})*/)?"
    rf"(?:[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?)?$"
)
_TAG_STRIP = re.compile(
    "\U0001F3F4[\U000E0020-\U000E007E]+\U000E007F|[\U000E0000-\U000E007F]"
)

JsonValue = None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]


def _repr(kind: str, values: Mapping[str, object]) -> str:
    parts: list[str] = []
    for key, value in values.items():
        if isinstance(value, str):
            parts.append(f"{key}={redact(value)!r}")
        else:
            parts.append(f"{key}={value!r}")
    return f"{kind}({', '.join(parts)})"


def _keep_flag(match: re.Match[str]) -> str:
    token = match.group(0)
    if token[:1] == "\U0001F3F4":
        return token
    return ""


def _strip_tags(text: str) -> str:
    return _TAG_STRIP.sub(_keep_flag, text)


def _require_server(server_id: object, grants: object) -> str:
    if isinstance(grants, (str, bytes, bytearray)) or not isinstance(grants, (set, frozenset, list, tuple)):
        raise Refuse("BAD_GRANTS")
    if not isinstance(server_id, str) or len(server_id) > MAX_SERVER or server_id == "":
        raise Refuse("BAD_SERVER")
    sid = bound_text(server_id, MAX_SERVER)
    sid_secret = secret_shape(sid)
    if sid_secret or _SERVER.fullmatch(sid) is None:
        raise Refuse("SECRET_SHAPE" if sid_secret else "BAD_SERVER")
    for item in grants:
        if not isinstance(item, str) or item == "" or len(item) > MAX_SERVER:
            raise Refuse("BAD_GRANTS")
        grant = bound_text(item, MAX_SERVER)
        if secret_shape(grant):
            raise Refuse("SECRET_SHAPE")
        if const_eq(sid, grant):
            return sid
    raise Refuse("UNKNOWN_SERVER")


def _request_id(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("BAD_RPC")
    if value < 0 or value > 2_147_483_647:
        raise Refuse("BAD_RPC")
    return bound_int(value, 0, 2_147_483_647)


def _stamp(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("BAD_CAP")
    if value < 0 or value > MAX_STAMP:
        raise Refuse("BAD_CAP")
    return bound_int(value, 0, MAX_STAMP)


def _bounded_int(value: object, lo: int, hi: int, code: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse(code)
    if value < lo or value > hi:
        raise Refuse(code)
    return bound_int(value, lo, hi)


def _string_set(value: object, *, empty: str | None, pattern: re.Pattern[str] = _PATTERN) -> tuple[str, ...]:
    if value is None:
        if empty is None:
            raise Refuse("BAD_FILTER")
        raise Refuse(empty)
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, (set, frozenset, list, tuple)):
        raise Refuse("BAD_FILTER")
    if len(value) == 0:
        if empty is None:
            return ()
        raise Refuse(empty)
    if len(value) > MAX_TOOLS:
        raise Refuse("TOO_MANY")
    out: list[str] = []
    for item in value:
        if not isinstance(item, str) or item == "" or len(item) > MAX_NAME:
            raise Refuse("BAD_NAME")
        text = bound_text(item, MAX_NAME)
        shaped = secret_shape(text)
        if shaped or pattern.fullmatch(text) is None:
            raise Refuse("SECRET_SHAPE" if shaped else "BAD_NAME")
        out.append(text)
    return tuple(out)


def _tool_name(value: object) -> str:
    if not isinstance(value, str) or value == "" or len(value) > MAX_NAME:
        raise Refuse("BAD_NAME")
    text = bound_text(value, MAX_NAME)
    shaped = secret_shape(text)
    if shaped or _TOOL.fullmatch(text) is None:
        raise Refuse("SECRET_SHAPE" if shaped else "BAD_NAME")
    return text


def _slug_text(text: str) -> str:
    slug = _NON_ALNUM.sub("_", text).strip("_").lower()
    if slug == "" or _TOOL.fullmatch(slug) is None:
        raise Refuse("BAD_NAME")
    return slug


def _mode(value: object, allowed: frozenset[str]) -> str:
    if not isinstance(value, str):
        raise Refuse("UNKNOWN_MODE")
    text = bound_text(value, 32)
    shaped = secret_shape(text)
    if shaped or text in {"off", "yolo"} or text not in allowed:
        raise Refuse("SECRET_SHAPE" if shaped else "UNKNOWN_MODE")
    return text


def _clamp(requested: object, cap: int) -> tuple[int, int]:
    asked = _bounded_int(requested, 1, 1_000_000_000, "BAD_CAP")
    applied = cap if asked > cap else asked
    return asked, applied


def _split_patterns(patterns: tuple[str, ...]) -> tuple[frozenset[str], tuple[str, ...]]:
    exact: set[str] = set()
    globs: list[str] = []
    for pattern in patterns:
        if _GLOB.search(pattern) is None:
            exact.add(pattern)
        else:
            globs.append(pattern)
    return frozenset(exact), tuple(globs)


def _glob_hit(name: str, globs: tuple[str, ...]) -> bool:
    for pattern in globs:
        if fnmatch.fnmatchcase(name, pattern):
            return True
    return False


def _reserved_meta(key: str) -> bool:
    prefix, sep, _name = key.partition("/")
    if sep == "":
        return False
    labels = prefix.split(".")
    if len(labels) >= 2 and labels[1] in _RESERVED:
        return True
    for index, label in enumerate(labels):
        if label in _RESERVED and index < len(labels) - 1:
            return True
    return False


def _check_json(value: object, depth: int) -> JsonValue:
    if depth >= MAX_DEPTH:
        raise Refuse("TOO_DEEP")
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        if value < -MAX_INT or value > MAX_INT:
            raise Refuse("BAD_ARGS")
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise Refuse("BAD_ARGS")
        return value
    if isinstance(value, str):
        text = sanitize_text(value)
        if secret_shape(text):
            raise Refuse("SECRET_SHAPE")
        return text
    if isinstance(value, list):
        if len(value) > MAX_ITEMS:
            raise Refuse("TOO_MANY")
        return [_check_json(item, depth + 1) for item in value]
    if isinstance(value, dict):
        if len(value) > MAX_ITEMS:
            raise Refuse("TOO_MANY")
        out: dict[str, JsonValue] = {}
        for key, item in value.items():
            if not isinstance(key, str) or key == "" or len(key) > MAX_NAME:
                raise Refuse("BAD_ARGS")
            name = bound_text(key, MAX_NAME)
            shaped = secret_shape(name)
            if shaped or _strip_tags(name) != name:
                raise Refuse("SECRET_SHAPE" if shaped else "BAD_ARGS")
            out[name] = _check_json(item, depth + 1)
        return out
    raise Refuse("BAD_ARGS")


def _dump(value: object) -> str:
    try:
        encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    except (TypeError, ValueError) as exc:
        raise Refuse("BAD_RPC") from exc
    return bound_text(encoded, MAX_JSON)


def _object(body: str) -> dict[str, object]:
    try:
        loaded: object = json.loads(body)
    except json.JSONDecodeError as exc:
        raise Refuse("BAD_RPC") from exc
    if not isinstance(loaded, dict):
        raise Refuse("BAD_RPC")
    out: dict[str, object] = {}
    for key, value in loaded.items():
        if not isinstance(key, str):
            raise Refuse("BAD_RPC")
        out[key] = value
    return out


def _grant_pair(item: object) -> tuple[str, tuple[str, ...]]:
    if isinstance(item, ToolGrant):
        return item.server_id, item.tools
    if isinstance(item, tuple) and len(item) == 2:
        server_raw = item[0]
        tools_raw = item[1]
        if isinstance(server_raw, str) and isinstance(tools_raw, tuple):
            names: list[str] = []
            for name in tools_raw:
                if not isinstance(name, str):
                    raise Refuse("BAD_NAME")
                names.append(name)
            return server_raw, tuple(names)
    raise Refuse("BAD_GRANT")


@dataclass(frozen=True, slots=True)
class RpcMessage:
    """One JSON-RPC 2.0 object. `server_id` is local authority and is not on the wire."""

    server_id: str
    jsonrpc: str
    method: str
    request_id: int | None
    params_body: str

    def __post_init__(self) -> None:
        if self.jsonrpc != "2.0" or self.method not in _METHODS:
            raise Refuse("BAD_RPC")
        if self.method == "notifications/initialized":
            if self.request_id is not None:
                raise Refuse("BAD_RPC")
        elif self.request_id is None:
            raise Refuse("BAD_RPC")
        server_secret = secret_shape(self.server_id)
        if server_secret or _SERVER.fullmatch(self.server_id) is None:
            raise Refuse("SECRET_SHAPE" if server_secret else "BAD_SERVER")
        if secret_shape(self.params_body):
            raise Refuse("SECRET_SHAPE")

    def __repr__(self) -> str:
        return _repr(
            "RpcMessage",
            {
                "server_id": self.server_id,
                "jsonrpc": self.jsonrpc,
                "method": self.method,
                "request_id": self.request_id,
                "params_body": self.params_body,
            },
        )

    def params(self) -> dict[str, object]:
        return _object(self.params_body)

    def payload(self) -> dict[str, object]:
        body: dict[str, object] = {"jsonrpc": self.jsonrpc, "method": self.method}
        if self.request_id is not None:
            body["id"] = self.request_id
        body["params"] = self.params()
        return body


@dataclass(frozen=True, slots=True)
class SamplingRequest:
    """An unapproved sampling ask. Caps on the record are the policy caps."""

    server_id: str
    model: str
    prompt: str
    requested_max_tokens: int
    max_tokens: int
    token_cap: int
    requested_timeout_s: int
    timeout_s: int
    timeout_cap: int
    code: str
    approved: bool

    def __post_init__(self) -> None:
        if self.approved or self.code != "SAMPLING_CONFIRM":
            raise Refuse("SELF_APPROVAL")
        if (
            self.token_cap != TOKEN_CAP
            or self.timeout_cap != TIMEOUT_CAP
            or self.max_tokens > self.token_cap
            or self.timeout_s > self.timeout_cap
            or self.max_tokens < 1
            or self.timeout_s < 1
        ):
            raise Refuse("CAP_RAISED")
        if secret_shape(self.prompt) or secret_shape(self.model) or secret_shape(self.server_id):
            raise Refuse("SECRET_SHAPE")

    def __repr__(self) -> str:
        return _repr(
            "SamplingRequest",
            {
                "server_id": self.server_id,
                "model": self.model,
                "prompt": self.prompt,
                "requested_max_tokens": self.requested_max_tokens,
                "max_tokens": self.max_tokens,
                "token_cap": self.token_cap,
                "requested_timeout_s": self.requested_timeout_s,
                "timeout_s": self.timeout_s,
                "timeout_cap": self.timeout_cap,
                "code": self.code,
                "approved": self.approved,
            },
        )


@dataclass(frozen=True, slots=True)
class ElicitationRequest:
    """A form ask for a person. URL mode is refused. The record does not approve itself."""

    server_id: str
    mode: str
    code: str
    approved: bool

    def __post_init__(self) -> None:
        if self.approved or self.code != "ELICIT_CONFIRM" or self.mode != "form":
            raise Refuse("SELF_APPROVAL")
        if secret_shape(self.server_id):
            raise Refuse("SECRET_SHAPE")

    def __repr__(self) -> str:
        return _repr(
            "ElicitationRequest",
            {"server_id": self.server_id, "mode": self.mode, "code": self.code, "approved": self.approved},
        )


@dataclass(frozen=True, slots=True)
class StdioSpec:
    """Argv and a jailed working directory. `spawned` stays false."""

    server_id: str
    argv: tuple[str, ...]
    cwd: str
    spawned: bool

    def __post_init__(self) -> None:
        if self.spawned:
            raise Refuse("SELF_SPAWN")
        if secret_shape(self.server_id) or secret_shape(self.cwd) or any(secret_shape(arg) for arg in self.argv):
            raise Refuse("SECRET_SHAPE")

    def __repr__(self) -> str:
        return _repr(
            "StdioSpec",
            {"server_id": self.server_id, "argv": self.argv, "cwd": self.cwd, "spawned": self.spawned},
        )


@dataclass(frozen=True, slots=True)
class HttpTarget:
    """A remote endpoint descriptor. `connected` stays false. No header map is stored."""

    server_id: str
    url: str
    credential_id: str
    connected: bool

    def __post_init__(self) -> None:
        if self.connected:
            raise Refuse("SELF_CONNECT")
        if secret_shape(self.server_id) or secret_shape(self.url) or secret_shape(self.credential_id):
            raise Refuse("SECRET_SHAPE")

    def __repr__(self) -> str:
        return _repr(
            "HttpTarget",
            {
                "server_id": self.server_id,
                "url": self.url,
                "credential_id": self.credential_id,
                "connected": self.connected,
            },
        )


@dataclass(frozen=True, slots=True)
class DiscoveryLimit:
    """How many servers a later pass may contact. Zero is not unlimited."""

    requested: int
    applied: int
    cap: int

    def __post_init__(self) -> None:
        if self.cap != DISCOVERY_CAP or self.applied < 1 or self.applied > self.cap:
            raise Refuse("CAP_RAISED")

    def __repr__(self) -> str:
        return _repr(
            "DiscoveryLimit",
            {"requested": self.requested, "applied": self.applied, "cap": self.cap},
        )


@dataclass(frozen=True, slots=True)
class Freshness:
    """Applied age window. A caller cannot raise `cap`."""

    requested: int
    applied: int
    cap: int
    age_s: int

    def __post_init__(self) -> None:
        if self.cap != WINDOW_CAP or self.applied < 1 or self.applied > self.cap or self.requested < 1:
            raise Refuse("CAP_RAISED")
        if self.age_s < 0 or self.age_s > self.applied:
            raise Refuse("STALE")

    def __repr__(self) -> str:
        return _repr(
            "Freshness",
            {"requested": self.requested, "applied": self.applied, "cap": self.cap, "age_s": self.age_s},
        )


@dataclass(frozen=True, slots=True)
class ConfirmingRetry:
    """The single retry allowed for TIMEOUT."""

    failure: str
    attempt: int

    def __post_init__(self) -> None:
        if self.failure != _RETRY or self.attempt != 1:
            raise Refuse("NO_RETRY")

    def __repr__(self) -> str:
        return _repr("ConfirmingRetry", {"failure": self.failure, "attempt": self.attempt})


@dataclass(frozen=True, slots=True)
class ToolView:
    """Model-facing name and a sanitized description."""

    server_id: str
    name: str
    description: str

    def __post_init__(self) -> None:
        server_secret = secret_shape(self.server_id)
        if server_secret or _SERVER.fullmatch(self.server_id) is None:
            raise Refuse("SECRET_SHAPE" if server_secret else "BAD_SERVER")
        name_secret = secret_shape(self.name)
        if name_secret or _TOOL.fullmatch(self.name) is None:
            raise Refuse("SECRET_SHAPE" if name_secret else "BAD_NAME")
        if secret_shape(self.description):
            raise Refuse("SECRET_SHAPE")

    def __repr__(self) -> str:
        return _repr(
            "ToolView",
            {"server_id": self.server_id, "name": self.name, "description": self.description},
        )


@dataclass(frozen=True, slots=True)
class ToolGrant:
    """Exact tool names injected for one server. Empty is not a grant."""

    server_id: str
    tools: tuple[str, ...]
    _index: frozenset[str] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        server_secret = secret_shape(self.server_id)
        if server_secret or _SERVER.fullmatch(self.server_id) is None:
            raise Refuse("SECRET_SHAPE" if server_secret else "BAD_SERVER")
        if len(self.tools) == 0:
            raise Refuse("EMPTY_ALLOW")
        if len(self.tools) > MAX_TOOLS:
            raise Refuse("TOO_MANY")
        seen: set[str] = set()
        for name in self.tools:
            if not isinstance(name, str) or name == "" or len(name) > MAX_NAME:
                raise Refuse("BAD_NAME")
            shaped = secret_shape(name)
            if shaped or _TOOL.fullmatch(name) is None:
                raise Refuse("SECRET_SHAPE" if shaped else "BAD_NAME")
            if name in _POLICY_DENY:
                raise Refuse("TOOL_DENIED")
            if name in seen:
                raise Refuse("DUPLICATE")
            seen.add(name)
        object.__setattr__(self, "_index", frozenset(seen))

    def __repr__(self) -> str:
        shown = tuple(redact(name) for name in self.tools)
        return _repr("ToolGrant", {"server_id": self.server_id, "tools": shown})

    def allows(self, name: str) -> bool:
        return name in self._index


@dataclass(frozen=True, slots=True)
class ToolPick:
    """Views that fit a description budget. The cap is policy."""

    requested: int
    applied: int
    cap: int
    views: tuple[ToolView, ...]

    def __post_init__(self) -> None:
        if self.cap != DESC_BUDGET or self.applied < 1 or self.applied > self.cap or self.requested < 1:
            raise Refuse("CAP_RAISED")
        if not isinstance(self.views, tuple):
            raise Refuse("BAD_NAMES")
        for view in self.views:
            if not isinstance(view, ToolView):
                raise Refuse("BAD_NAME")

    def __repr__(self) -> str:
        return _repr(
            "ToolPick",
            {
                "requested": self.requested,
                "applied": self.applied,
                "cap": self.cap,
                "views": self.views,
            },
        )


def _message(server_id: str, method: str, request_id: int | None, params: Mapping[str, JsonValue]) -> RpcMessage:
    return RpcMessage(
        server_id=server_id,
        jsonrpc="2.0",
        method=method,
        request_id=request_id,
        params_body=_dump(dict(params)),
    )


def initialize(request_id: object, server_id: str, grants: object) -> RpcMessage:
    """Build an initialize request for a granted server."""
    sid = _require_server(server_id, grants)
    params: dict[str, JsonValue] = {
        "protocolVersion": PROTOCOL,
        "capabilities": {},
        "clientInfo": {"name": CLIENT_NAME, "version": CLIENT_VERSION},
    }
    return _message(sid, "initialize", _request_id(request_id), params)


def tools_list(request_id: object, server_id: str, grants: object) -> RpcMessage:
    """Build a tools/list request for a granted server."""
    sid = _require_server(server_id, grants)
    return _message(sid, "tools/list", _request_id(request_id), {})


def tools_call(
    request_id: object,
    server_id: str,
    grants: object,
    name: object,
    arguments: object,
) -> RpcMessage:
    """Build a tools/call object. This does not enable the tool."""
    sid = _require_server(server_id, grants)
    tool = _tool_name(name)
    if not isinstance(arguments, Mapping):
        raise Refuse("BAD_ARGS")
    checked = _check_json(dict(arguments), 0)
    if not isinstance(checked, dict):
        raise Refuse("BAD_ARGS")
    params: dict[str, JsonValue] = {"name": tool, "arguments": checked}
    return _message(sid, "tools/call", _request_id(request_id), params)


def initialized(server_id: str, grants: object) -> RpcMessage:
    """Build the initialized notification. It carries no id."""
    sid = _require_server(server_id, grants)
    return _message(sid, "notifications/initialized", None, {})


def encode_frame(message: object) -> str:
    """Newline-delimited JSON. The string is not written to a pipe."""
    if not isinstance(message, RpcMessage):
        raise Refuse("BAD_RPC")
    return _dump(message.payload()) + "\n"


def parse_frame(raw: object, server_id: str, grants: object) -> RpcMessage:
    """Bind one NDJSON frame to a granted server. Policy-denied tool names refuse."""
    sid = _require_server(server_id, grants)
    if not isinstance(raw, (bytes, bytearray)):
        raise Refuse("BAD_RPC")
    if len(raw) > MAX_JSON:
        raise Refuse("BAD_RPC")
    blob = bound_bytes(raw, MAX_JSON)
    try:
        text = blob.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise Refuse("BAD_RPC") from exc
    if "\x00" in text:
        raise Refuse("BAD_RPC")
    line = text.strip("\r\n")
    if line == "" or "\n" in line or "\r" in line:
        raise Refuse("BAD_RPC")
    loaded = _object(line)
    version = loaded.get("jsonrpc")
    method = loaded.get("method")
    if version != "2.0" or not isinstance(method, str):
        raise Refuse("BAD_RPC")
    if len(method) > 64:
        raise Refuse("BAD_RPC")
    method_text = bound_text(method, 64)
    if secret_shape(method_text):
        raise Refuse("SECRET_SHAPE")
    if method_text not in _METHODS:
        raise Refuse("UNKNOWN_MODE")
    if method_text == "notifications/initialized":
        if "id" in loaded:
            raise Refuse("BAD_RPC")
        request_id: int | None = None
    else:
        request_id = _request_id(loaded.get("id"))
    params = loaded.get("params", {})
    if not isinstance(params, dict):
        raise Refuse("BAD_RPC")
    checked = _check_json(params, 0)
    if not isinstance(checked, dict):
        raise Refuse("BAD_RPC")
    if method_text == "tools/call":
        raw_tool = params.get("name")
        tool = checked.get("name")
        if not isinstance(raw_tool, str) or raw_tool != tool:
            raise Refuse("BAD_NAME")
        checked_name = _tool_name(raw_tool)
        if checked_name in _POLICY_DENY:
            raise Refuse("TOOL_DENIED")
        if "arguments" in checked and not isinstance(checked["arguments"], dict):
            raise Refuse("BAD_ARGS")
    return RpcMessage(
        server_id=sid,
        jsonrpc="2.0",
        method=method_text,
        request_id=request_id,
        params_body=_dump(checked),
    )


def _filter_checked(
    names: tuple[str, ...],
    allowed: tuple[str, ...],
    blocked: tuple[str, ...],
) -> list[str]:
    allow_exact, allow_globs = _split_patterns(allowed)
    deny_exact, deny_globs = _split_patterns(blocked)
    kept: list[str] = []
    seen: set[str] = set()
    for name in names:
        if name in seen:
            continue
        seen.add(name)
        if name in deny_exact or _glob_hit(name, deny_globs):
            continue
        if name not in allow_exact and not _glob_hit(name, allow_globs):
            continue
        kept.append(name)
    return kept


def filter_tools(names: object, allow: object, deny: object) -> list[str]:
    """Return names that match allow and miss deny. Deny wins. Empty allow refuses."""
    allowed = _string_set(allow, empty="EMPTY_ALLOW")
    blocked = _string_set(deny, empty=None)
    if isinstance(names, (str, bytes, bytearray)) or not isinstance(names, (list, tuple)):
        raise Refuse("BAD_NAMES")
    if len(names) > MAX_TOOLS:
        raise Refuse("TOO_MANY")
    checked: list[str] = []
    for item in names:
        checked.append(_tool_name(item))
    return _filter_checked(tuple(checked), allowed, blocked)


def guarded_tools_call(
    request_id: object,
    server_id: str,
    grants: object,
    name: object,
    arguments: object,
    allow: object,
    deny: object,
) -> RpcMessage:
    """Build tools/call only when the name survives allow, caller deny, and POLICY_DENY."""
    tool = _tool_name(name)
    allowed = _string_set(allow, empty="EMPTY_ALLOW")
    blocked = _string_set(deny, empty=None)
    merged: list[str] = []
    seen: set[str] = set()
    for pattern in (*POLICY_DENY, *blocked):
        if pattern in seen:
            continue
        seen.add(pattern)
        merged.append(pattern)
    if tool not in _filter_checked((tool,), allowed, tuple(merged)):
        raise Refuse("TOOL_DENIED")
    return tools_call(request_id, server_id, grants, tool, arguments)


def admit_tools(server_id: str, grants: object, allow: object) -> ToolGrant:
    """Enable exactly the injected names. An empty allow enables nothing."""
    sid = _require_server(server_id, grants)
    names = _string_set(allow, empty="EMPTY_ALLOW", pattern=_TOOL)
    return ToolGrant(server_id=sid, tools=names)


def resolve_tool(grant: object, name: object) -> str:
    """Return `name` when the injected grant lists it. Any other name refuses."""
    if not isinstance(grant, ToolGrant):
        raise Refuse("BAD_GRANT")
    tool = _tool_name(name)
    if tool in _POLICY_DENY or not grant.allows(tool):
        raise Refuse("TOOL_DENIED")
    return tool


def rebuild(records: object) -> tuple[ToolGrant, ...]:
    """Reproduce grants from admitted records or `(server_id, tools)` pairs."""
    if isinstance(records, (str, bytes, bytearray)) or not isinstance(records, (list, tuple)):
        raise Refuse("BAD_NAMES")
    if len(records) > MAX_TOOLS:
        raise Refuse("TOO_MANY")
    seen: set[str] = set()
    out: list[ToolGrant] = []
    for item in records:
        server_id, tools = _grant_pair(item)
        if server_id in seen:
            raise Refuse("DUPLICATE")
        seen.add(server_id)
        out.append(ToolGrant(server_id=server_id, tools=tools))
    return tuple(out)


def snapshot(records: object) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Plain pairs. `rebuild` of this value matches `rebuild` of the records."""
    return tuple((row.server_id, row.tools) for row in rebuild(records))


def load_from_path(path: object) -> None:
    """Refuse a disk load. The path is not opened."""
    if isinstance(path, str):
        if len(path) > MAX_URL:
            raise Refuse("DISK_IMPORT")
        text = bound_text(path, MAX_URL)
        if secret_shape(text):
            raise Refuse("SECRET_SHAPE")
    raise Refuse("DISK_IMPORT")


def connect(target: object) -> None:
    """Refuse a live connection. The descriptor is not opened."""
    del target
    raise Refuse("NO_CONNECT")


def note_id(seen: object, request_id: object) -> frozenset[int]:
    """Return `seen` plus `request_id`. A repeated id refuses."""
    if isinstance(seen, (str, bytes, bytearray)) or not isinstance(seen, (set, frozenset)):
        raise Refuse("BAD_RPC")
    rid = _request_id(request_id)
    found: set[int] = set()
    for item in seen:
        found.add(_request_id(item))
    if rid in found:
        raise Refuse("REPLAY")
    found.add(rid)
    return frozenset(found)


def accept_window(now: object, issued_at: object, window_s: object) -> Freshness:
    """Return the applied window. A late or future stamp refuses. The cap is policy."""
    current = _stamp(now)
    issued = _stamp(issued_at)
    requested = _bounded_int(window_s, 1, 1_000_000_000, "BAD_CAP")
    applied = WINDOW_CAP if requested > WINDOW_CAP else requested
    if current < issued:
        raise Refuse("STALE")
    age = current - issued
    if age > applied:
        raise Refuse("STALE")
    return Freshness(requested=requested, applied=applied, cap=WINDOW_CAP, age_s=age)


def sampling_request(
    server_id: str,
    grants: object,
    model: object,
    models: object,
    prompt: object,
    max_tokens: object,
    timeout_s: object,
    mode: object = "confirm",
) -> SamplingRequest:
    """Return an unapproved SAMPLING_CONFIRM record. A higher cap is ignored."""
    sid = _require_server(server_id, grants)
    _mode(mode, frozenset({"confirm"}))
    if not isinstance(model, str) or not isinstance(prompt, str):
        raise Refuse("BAD_NAME")
    if len(model) > MAX_NAME:
        raise Refuse("BAD_NAME")
    chosen = bound_text(model, MAX_NAME)
    chosen_secret = secret_shape(chosen)
    if chosen_secret or _MODEL.fullmatch(chosen) is None:
        raise Refuse("SECRET_SHAPE" if chosen_secret else "BAD_NAME")
    allowed = _string_set(models, empty="EMPTY_ALLOW", pattern=_MODEL)
    if not any(const_eq(chosen, item) for item in allowed):
        raise Refuse("UNKNOWN_MODEL")
    text = sanitize_text(prompt)
    prompt_secret = secret_shape(text)
    if text == "" or prompt_secret:
        raise Refuse("SECRET_SHAPE" if prompt_secret else "BAD_NAME")
    asked_tokens, tokens = _clamp(max_tokens, TOKEN_CAP)
    asked_timeout, timeout = _clamp(timeout_s, TIMEOUT_CAP)
    return SamplingRequest(
        server_id=sid,
        model=chosen,
        prompt=text,
        requested_max_tokens=asked_tokens,
        max_tokens=tokens,
        token_cap=TOKEN_CAP,
        requested_timeout_s=asked_timeout,
        timeout_s=timeout,
        timeout_cap=TIMEOUT_CAP,
        code="SAMPLING_CONFIRM",
        approved=False,
    )


def elicitation_request(server_id: str, grants: object, mode: object) -> ElicitationRequest:
    """Return an unapproved form elicitation. URL mode and yolo refuse."""
    sid = _require_server(server_id, grants)
    if not isinstance(mode, str):
        raise Refuse("UNKNOWN_MODE")
    kind = bound_text(mode, 32)
    kind_secret = secret_shape(kind)
    if kind_secret or kind in {"off", "yolo", "approve"}:
        raise Refuse("SECRET_SHAPE" if kind_secret else "UNKNOWN_MODE")
    if kind == "url":
        raise Refuse("URL_ELICITATION")
    if kind != "form":
        raise Refuse("UNKNOWN_MODE")
    return ElicitationRequest(server_id=sid, mode="form", code="ELICIT_CONFIRM", approved=False)


def unspawned_argv(server_id: str, command: object, grants: object) -> list[str]:
    """Return a copy of argv. A string command is a shell and is refused."""
    if isinstance(command, str):
        if len(command) > MAX_ARG:
            raise Refuse("SHELL_STRING")
        bound_text(command, MAX_ARG)
        if secret_shape(command):
            raise Refuse("SECRET_SHAPE")
        raise Refuse("SHELL_STRING")
    _require_server(server_id, grants)
    if isinstance(command, tuple):
        items: list[object] = list(command)
    elif isinstance(command, list):
        items = list(command)
    else:
        raise Refuse("BAD_ARGV")
    if len(items) == 0:
        raise Refuse("EMPTY_ARGV")
    if len(items) > MAX_ARGS:
        raise Refuse("TOO_MANY")
    argv: list[str] = []
    for item in items:
        if not isinstance(item, str) or item == "" or len(item) > MAX_ARG:
            raise Refuse("BAD_ARGV")
        text = bound_text(item, MAX_ARG)
        if secret_shape(text):
            raise Refuse("SECRET_SHAPE")
        argv.append(text)
    return argv


def stdio_spec(server_id: str, command: object, grants: object, cwd: object, roots: object) -> StdioSpec:
    """Jail `cwd` and return argv without starting a process."""
    argv = unspawned_argv(server_id, command, grants)
    if not isinstance(cwd, str) or cwd == "" or len(cwd) > MAX_URL:
        raise Refuse("BAD_PATH")
    if isinstance(roots, (str, bytes, bytearray)) or not isinstance(roots, (list, tuple)) or len(roots) == 0:
        raise Refuse("NO_GRANT")
    checked: list[str] = []
    for root in roots:
        if not isinstance(root, str) or root == "" or len(root) > MAX_URL:
            raise Refuse("NO_GRANT")
        checked.append(bound_text(root, MAX_URL))
    jail = PathJail(checked)
    resolved = jail.contain(bound_text(cwd, MAX_URL))
    return StdioSpec(
        server_id=_require_server(server_id, grants),
        argv=tuple(argv),
        cwd=str(resolved),
        spawned=False,
    )


def _url(value: object) -> str:
    if not isinstance(value, str) or value == "" or len(value) > MAX_URL:
        raise Refuse("BAD_URL")
    text = bound_text(value, MAX_URL)
    shaped = secret_shape(text)
    if shaped or _URL_BAD.search(text) is not None:
        raise Refuse("SECRET_SHAPE" if shaped else "BAD_URL")
    if text.startswith("https://"):
        rest = text[len("https://") :]
    elif text.startswith("http://"):
        rest = text[len("http://") :]
    else:
        raise Refuse("BAD_URL")
    if rest == "" or rest.startswith("/") or "@" in rest[: rest.find("/") if "/" in rest else len(rest)]:
        raise Refuse("BAD_URL")
    return text


def http_target(server_id: str, url: object, credential_id: object, grants: object) -> HttpTarget:
    """Record an endpoint and a credential id. Raw key material refuses. Nothing connects."""
    sid = _require_server(server_id, grants)
    if not isinstance(credential_id, str):
        raise Refuse("BAD_CREDENTIAL")
    if credential_id == "":
        raise Refuse("MISSING_CREDENTIAL")
    if len(credential_id) > MAX_SERVER:
        raise Refuse("BAD_CREDENTIAL")
    cred = bound_text(credential_id, MAX_SERVER)
    if secret_shape(cred):
        raise Refuse("SECRET_SHAPE")
    if _CRED.fullmatch(cred) is None:
        raise Refuse("BAD_CREDENTIAL")
    return HttpTarget(server_id=sid, url=_url(url), credential_id=cred, connected=False)


def discovery_limit(requested: object) -> DiscoveryLimit:
    """Clamp discovery concurrency. A request of zero still applies the policy cap."""
    asked = _bounded_int(requested, 0, 1_000_000_000, "BAD_CAP")
    applied = DISCOVERY_CAP if asked == 0 or asked > DISCOVERY_CAP else asked
    return DiscoveryLimit(requested=asked, applied=applied, cap=DISCOVERY_CAP)


def confirming_retry(failure: object, prior: object) -> ConfirmingRetry:
    """Allow one retry when the failure is TIMEOUT and no retry has been spent."""
    if not isinstance(failure, str):
        raise Refuse("NO_RETRY")
    kind = bound_text(failure, 32)
    shaped = secret_shape(kind)
    if shaped or kind != _RETRY:
        raise Refuse("SECRET_SHAPE" if shaped else "NO_RETRY")
    spent = _bounded_int(prior, 0, 1_000_000, "NO_RETRY")
    if spent >= 1:
        raise Refuse("RETRY_EXHAUSTED")
    return ConfirmingRetry(failure=_RETRY, attempt=1)


def registered_name(server_id: str, tool_name: object) -> str:
    """Prefix a tool as mcp_<server>_<tool>."""
    if not isinstance(server_id, str) or server_id == "" or len(server_id) > MAX_SERVER:
        raise Refuse("BAD_SERVER")
    sid = bound_text(server_id, MAX_SERVER)
    shaped = secret_shape(sid)
    if shaped or _SERVER.fullmatch(sid) is None:
        raise Refuse("SECRET_SHAPE" if shaped else "BAD_SERVER")
    return f"mcp_{_slug_text(sid)}_{_slug_text(_tool_name(tool_name))}"


def utility_tools(
    server_id: str,
    grants: object,
    *,
    resources: object,
    prompts: object,
    supports_resources: object,
    supports_prompts: object,
) -> tuple[str, ...]:
    """Register resource and prompt wrappers only when config and the server both allow them."""
    sid = _require_server(server_id, grants)
    flags = (resources, prompts, supports_resources, supports_prompts)
    if any(not isinstance(flag, bool) for flag in flags):
        raise Refuse("UNKNOWN_MODE")
    names: list[str] = []
    if resources is True and supports_resources is True:
        names.append(registered_name(sid, "list_resources"))
        names.append(registered_name(sid, "read_resource"))
    if prompts is True and supports_prompts is True:
        names.append(registered_name(sid, "list_prompts"))
        names.append(registered_name(sid, "get_prompt"))
    return tuple(names)


def present_tool(server_id: str, grants: object, name: object, description: object) -> ToolView:
    """Prefix the tool and sanitize its description."""
    sid = _require_server(server_id, grants)
    text = sanitize_text(description)
    if secret_shape(text):
        raise Refuse("SECRET_SHAPE")
    return ToolView(server_id=sid, name=registered_name(sid, name), description=text)


def select_views(views: object, budget: object) -> ToolPick:
    """One pass. Skip a description that does not fit. Keep a later view that does."""
    if isinstance(views, (str, bytes, bytearray)) or not isinstance(views, (list, tuple)):
        raise Refuse("BAD_NAMES")
    if len(views) > MAX_TOOLS:
        raise Refuse("TOO_MANY")
    requested = _bounded_int(budget, 1, 1_000_000_000, "BAD_CAP")
    applied = DESC_BUDGET if requested > DESC_BUDGET else requested
    remaining = applied
    kept: list[ToolView] = []
    for item in views:
        if not isinstance(item, ToolView):
            raise Refuse("BAD_NAME")
        size = len(item.description)
        if size > remaining:
            continue
        remaining -= size
        kept.append(item)
    return ToolPick(requested=requested, applied=applied, cap=DESC_BUDGET, views=tuple(kept))


def sanitize_text(value: object) -> str:
    """Strip invisible tag characters. A regional-flag tag sequence stays."""
    if not isinstance(value, str):
        raise Refuse("NOT_TEXT")
    return _strip_tags(bound_text(value, MAX_PROMPT))


def visible_meta(meta: object) -> dict[str, object]:
    """Keep vendor `_meta`. Drop a reserved `modelcontextprotocol` or `mcp` prefix."""
    if isinstance(meta, (str, bytes, bytearray)) or not isinstance(meta, Mapping):
        raise Refuse("BAD_META")
    if len(meta) > MAX_ITEMS:
        raise Refuse("TOO_MANY")
    kept: dict[str, object] = {}
    for key, value in meta.items():
        if not isinstance(key, str) or key == "" or len(key) > MAX_NAME:
            raise Refuse("BAD_META")
        name = bound_text(key, MAX_NAME)
        if secret_shape(name):
            raise Refuse("SECRET_SHAPE")
        if _META_KEY.fullmatch(name) is None:
            raise Refuse("BAD_META")
        if _reserved_meta(name):
            continue
        kept[name] = _check_json(value, 0)
    return kept


__all__ = [
    "CLIENT_NAME",
    "CLIENT_VERSION",
    "DESC_BUDGET",
    "DISCOVERY_CAP",
    "MAX_DEPTH",
    "POLICY_DENY",
    "PROTOCOL",
    "SCHEMA",
    "TIMEOUT_CAP",
    "TOKEN_CAP",
    "WINDOW_CAP",
    "ConfirmingRetry",
    "DiscoveryLimit",
    "ElicitationRequest",
    "Freshness",
    "HttpTarget",
    "RpcMessage",
    "SamplingRequest",
    "StdioSpec",
    "ToolGrant",
    "ToolPick",
    "ToolView",
    "accept_window",
    "admit_tools",
    "confirming_retry",
    "connect",
    "discovery_limit",
    "elicitation_request",
    "encode_frame",
    "filter_tools",
    "guarded_tools_call",
    "http_target",
    "initialize",
    "initialized",
    "load_from_path",
    "note_id",
    "parse_frame",
    "present_tool",
    "rebuild",
    "registered_name",
    "resolve_tool",
    "sampling_request",
    "sanitize_text",
    "select_views",
    "snapshot",
    "stdio_spec",
    "tools_call",
    "tools_list",
    "unspawned_argv",
    "utility_tools",
    "visible_meta",
]
