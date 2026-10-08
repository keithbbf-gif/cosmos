"""Per-tool Nous gateway descriptors for web, image, tts, and browser.

Credential ids only. `vision` shares the browser slot (`browser_vision`).
Terminal and Modal are not in this bundle. No HTTP and no subprocess.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Final

from cosmos_hermes import Refuse, bound_int, bound_text, const_eq, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-tool_gateway/1"
TOOLS: Final[tuple[str, ...]] = ("web", "image", "tts", "browser")
OPS: Final[tuple[tuple[str, tuple[str, ...]], ...]] = (
    ("web", ("search", "extract")),
    ("image", ("generate",)),
    ("tts", ("speak",)),
    ("browser", ("navigate", "click", "type", "vision")),
)
PROVIDERS: Final[tuple[str, ...]] = (
    "nous",
    "firecrawl",
    "searxng",
    "fal",
    "openai",
    "elevenlabs",
    "browser-use",
    "browserbase",
    "camofox",
)
IMAGE_MODELS: Final[tuple[str, ...]] = (
    "flux-2-klein",
    "flux-2-pro",
    "gpt-image",
    "nano-banana",
    "seedream",
    "ideogram",
    "recraft",
    "qwen",
    "krea-2-medium",
    "krea-2-large",
    "krea-2-medium-turbo",
)
CRED_CAP: Final[int] = 64
NAME_CAP: Final[int] = 64
ARG_CAP: Final[int] = 400
MODEL_CAP: Final[int] = 64
CALL_CAP: Final[int] = 8
BATCH_BUDGET: Final[int] = 1024
LIST_CAP: Final[int] = 32
DEFAULT_MODEL: Final[str] = "flux-2-klein"
RETRY_CLASS: Final[str] = "RATE_LIMIT"
GENESIS: Final[str] = "0" * 64

_AT_MAX: Final[int] = 4_102_444_800
_TOOL_SET: Final[frozenset[str]] = frozenset(TOOLS)
_TERMINAL: Final[frozenset[str]] = frozenset({"terminal", "modal"})
_ALIAS: Final[dict[str, str]] = {"vision": "browser"}
_OPS: Final[dict[str, frozenset[str]]] = {name: frozenset(ops) for name, ops in OPS}
_PROVIDER_FOR: Final[dict[str, frozenset[str]]] = {
    "web": frozenset({"nous", "firecrawl", "searxng"}),
    "image": frozenset({"nous", "fal"}),
    "tts": frozenset({"nous", "openai", "elevenlabs"}),
    "browser": frozenset({"nous", "browser-use", "browserbase", "camofox"}),
}
_MODEL_SET: Final[frozenset[str]] = frozenset(IMAGE_MODELS)
_KREA: Final[frozenset[str]] = frozenset(
    {"krea-2-medium", "krea-2-large", "krea-2-medium-turbo"}
)
_ENTITLED: Final[frozenset[str]] = frozenset({"paid", "pool"})
_REASONS: Final[frozenset[str]] = frozenset({"explicit", "env", "declined", "active", "open"})
_CODES: Final[frozenset[str]] = frozenset({"READY", "RETRY"})
_VIAS: Final[frozenset[str]] = frozenset({"gateway", "direct"})
_HEX: Final[frozenset[str]] = frozenset("0123456789abcdef")
_ORDER: Final[dict[str, int]] = {name: index for index, name in enumerate(TOOLS)}
_CRED_KEYS: Final[int] = len(TOOLS) + len(_TERMINAL)
_URL_OPS: Final[frozenset[str]] = frozenset({"extract", "navigate"})

_ID: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_REF: Final[re.Pattern[str]] = re.compile(r"^@[A-Za-z0-9][A-Za-z0-9_-]{0,31}$")
_PROVIDER: Final[re.Pattern[str]] = re.compile(r"^[a-z0-9][a-z0-9-]{0,31}$")


def _dump(parts: list[object]) -> str:
    return json.dumps(parts, separators=(",", ":"), ensure_ascii=True)


def _link(prev: str, body: str) -> str:
    return hashlib.sha256(f"{prev}\n{body}".encode("utf-8")).hexdigest()


def _hex64(text: str) -> bool:
    return len(text) == 64 and all(ch in _HEX for ch in text)


def _cap(requested: object) -> CapNote:
    """Policy ceiling is `CRED_CAP`. A higher request is recorded and ignored."""
    if type(requested) is not int:
        raise Refuse("NOT_INT")
    if requested < 1:
        raise Refuse("BAD_LIMIT")
    if requested > CRED_CAP:
        return CapNote(applied=CRED_CAP, requested=requested, clamped=True)
    return CapNote(applied=requested, requested=requested, clamped=False)


def _batch_budget(value: object) -> tuple[int, int, bool]:
    if value is None:
        return BATCH_BUDGET, BATCH_BUDGET, False
    if type(value) is not int:
        raise Refuse("NOT_INT")
    if value < 1:
        raise Refuse("BAD_LIMIT")
    if value > BATCH_BUDGET:
        return BATCH_BUDGET, value, True
    return value, value, False


def _moment(value: object) -> int:
    return bound_int(value, 0, _AT_MAX)


def _classify(name: object) -> tuple[str, bool]:
    text = bound_text(name, NAME_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    if text in _TERMINAL:
        return text, False
    if text in _ALIAS:
        return _ALIAS[text], True
    if text not in _TOOL_SET:
        raise Refuse("BAD_TOOL")
    return text, False


def _catalog(name: object) -> str:
    kind, _aliased = _classify(name)
    if kind in _TERMINAL:
        raise Refuse("NOT_GATEWAY")
    return kind


def _cred(value: object, cap: int) -> str:
    if type(cap) is not int or cap < 1 or cap > CRED_CAP:
        raise Refuse("BAD_CAP")
    if value is None:
        raise Refuse("NO_CRED")
    text = bound_text(value)
    if len(text) > cap:
        raise Refuse("OVERSIZE", str(cap))
    if secret_shape(text):
        raise Refuse("SECRET")
    if text.strip() == "":
        raise Refuse("NO_CRED")
    if _ID.fullmatch(text) is None:
        raise Refuse("BAD_CRED")
    return text


def _provider(tool: str, value: object) -> str:
    text = bound_text(value, NAME_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    if _PROVIDER.fullmatch(text) is None or text not in _PROVIDER_FOR[tool]:
        raise Refuse("BAD_PROVIDER")
    return text


def _op(kind: str, op: object, aliased: bool) -> str:
    text = bound_text(op, NAME_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    if aliased and text != "vision":
        raise Refuse("BAD_OP")
    allowed = _OPS.get(kind)
    if allowed is None or text not in allowed:
        raise Refuse("BAD_OP")
    return text


def _checked_arg(tool: str, op: str, arg: object) -> str:
    text = bound_text(arg, ARG_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    cleaned = text.strip()
    if cleaned == "":
        raise Refuse("EMPTY")
    if op in _URL_OPS:
        _url(cleaned)
    elif op == "click" and _REF.fullmatch(cleaned) is None:
        raise Refuse("BAD_ARG")
    return cleaned


def _url(text: str) -> None:
    if ".." in text or "\\" in text or "@" in text or any(ch.isspace() for ch in text):
        raise Refuse("BAD_URL")
    if text.startswith("https://"):
        rest = text[8:]
    elif text.startswith("http://"):
        rest = text[7:]
    else:
        raise Refuse("BAD_URL")
    if rest == "" or ("." not in rest and "/" not in rest):
        raise Refuse("BAD_URL")


def _reject_override(model: object) -> None:
    """Image model is pinned once. A per-call model is not an override."""
    if model is None:
        return
    text = bound_text(model, MODEL_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    raise Refuse("OVERRIDE")


def _failure(value: object) -> str:
    text = bound_text(value, NAME_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    if text == "":
        raise Refuse("BAD_FAILURE")
    return text


def _call_id(value: object) -> str:
    text = bound_text(value, 64)
    if not _hex64(text):
        raise Refuse("BAD_CALL")
    return text


def _allow_items(allow: object) -> tuple[object, ...]:
    if allow is None:
        raise Refuse("EMPTY_ALLOW")
    if isinstance(allow, (str, bytes, bytearray)):
        raise Refuse("NOT_LIST")
    if type(allow) is not list and type(allow) is not tuple:
        raise Refuse("NOT_LIST")
    if len(allow) == 0:
        raise Refuse("EMPTY_ALLOW")
    if len(allow) > len(TOOLS):
        raise Refuse("OVERSIZE", str(len(TOOLS)))
    return tuple(allow)


def _cred_map(creds: object) -> dict[str, object]:
    if type(creds) is not dict:
        raise Refuse("NOT_MAP")
    if len(creds) > _CRED_KEYS:
        raise Refuse("OVERSIZE", str(_CRED_KEYS))
    out: dict[str, object] = {}
    for key, value in creds.items():
        kind, _aliased = _classify(key)
        if kind in out:
            raise Refuse("DUPLICATE")
        out[kind] = value
    return out


def _rows(items: object) -> tuple[object, ...]:
    if items is None:
        raise Refuse("EMPTY")
    if isinstance(items, (str, bytes, bytearray)):
        raise Refuse("NOT_LIST")
    if type(items) is not list and type(items) is not tuple:
        raise Refuse("NOT_LIST")
    if len(items) == 0:
        raise Refuse("EMPTY")
    if len(items) > LIST_CAP:
        raise Refuse("OVERSIZE", str(LIST_CAP))
    return tuple(items)


def _triple(item: object) -> tuple[object, object, object]:
    if type(item) is not tuple and type(item) is not list:
        raise Refuse("BAD_CALL")
    if len(item) != 3:
        raise Refuse("BAD_CALL")
    return (item[0], item[1], item[2])


def _ascending(names: object, blocked: set[str], code: str) -> set[str]:
    if type(names) is not tuple:
        raise Refuse("BAD_SNAPSHOT")
    seen: set[str] = set()
    last = -1
    for name in names:
        if type(name) is not str or name not in _ORDER:
            raise Refuse("BAD_SNAPSHOT")
        pos = _ORDER[name]
        if name in seen:
            raise Refuse("DUPLICATE")
        if pos <= last:
            raise Refuse("BAD_SNAPSHOT")
        if name in blocked:
            raise Refuse(code)
        last = pos
        seen.add(name)
    return seen


@dataclass(frozen=True, slots=True)
class CapNote:
    """Credential-id cap in force. `clamped` means a higher request was ignored."""

    applied: int
    requested: int
    clamped: bool

    def __post_init__(self) -> None:
        if type(self.applied) is not int or type(self.requested) is not int or type(self.clamped) is not bool:
            raise Refuse("BAD_CAP")
        if self.applied < 1 or self.applied > CRED_CAP:
            raise Refuse("BAD_CAP")
        if self.clamped:
            if self.requested <= CRED_CAP or self.applied != CRED_CAP:
                raise Refuse("BAD_CAP")
            return
        if self.requested != self.applied:
            raise Refuse("BAD_CAP")

    def __repr__(self) -> str:
        return f"CapNote(applied={self.applied}, requested={self.requested}, clamped={self.clamped})"


@dataclass(frozen=True, slots=True)
class Route:
    """One tool route. The credential id is a handle, never key material."""

    name: str
    cred_id: str
    provider: str
    via: str

    def __post_init__(self) -> None:
        if self.name not in _TOOL_SET:
            raise Refuse("BAD_TOOL")
        if self.via not in _VIAS:
            raise Refuse("BAD_STATE")
        allowed = _PROVIDER_FOR[self.name]
        if self.provider not in allowed:
            raise Refuse("BAD_PROVIDER")
        if self.via == "gateway" and self.provider != "nous":
            raise Refuse("BAD_PROVIDER")
        if self.via == "direct" and self.provider == "nous":
            raise Refuse("BAD_PROVIDER")
        checked = _cred(self.cred_id, CRED_CAP)
        if checked != self.cred_id:
            raise Refuse("BAD_CRED")

    def __repr__(self) -> str:
        return f"Route(name={self.name!r}, provider={self.provider!r}, via={self.via!r})"


@dataclass(frozen=True, slots=True)
class Offer:
    """Checklist row. `checked` is the pre-check, not an enablement."""

    name: str
    offered: bool
    checked: bool
    reason: str

    def __post_init__(self) -> None:
        if self.name not in _TOOL_SET:
            raise Refuse("BAD_TOOL")
        if type(self.offered) is not bool or type(self.checked) is not bool:
            raise Refuse("NOT_BOOL")
        if self.reason not in _REASONS:
            raise Refuse("BAD_STATE")
        if self.reason == "open" and not (self.offered and self.checked):
            raise Refuse("BAD_STATE")
        if self.reason == "explicit" and (self.offered or self.checked):
            raise Refuse("BAD_STATE")
        if self.reason in {"env", "declined"} and (not self.offered or self.checked):
            raise Refuse("BAD_STATE")
        if self.reason == "active" and (self.offered or self.checked):
            raise Refuse("BAD_STATE")


@dataclass(frozen=True, slots=True)
class Call:
    """One gateway descriptor. Building it does not fetch, draw, speak, or browse."""

    schema: str
    tool: str
    op: str
    arg: str
    model: str
    at: int
    seq: int
    prev: str
    code: str
    digest: str = ""
    call_id: str = ""

    def __post_init__(self) -> None:
        if type(self.schema) is not str or self.schema != SCHEMA:
            raise Refuse("BAD_SNAPSHOT")
        if self.tool not in _TOOL_SET:
            raise Refuse("BAD_TOOL")
        if self.code not in _CODES:
            raise Refuse("BAD_CALL")
        allowed = _OPS[self.tool]
        if self.op not in allowed:
            raise Refuse("BAD_OP")
        if type(self.prev) is not str or not _hex64(self.prev):
            raise Refuse("BROKEN_CHAIN")
        if type(self.at) is not int:
            raise Refuse("NOT_INT")
        if self.at < 0 or self.at > _AT_MAX:
            raise Refuse("OUT_OF_RANGE", f"0..{_AT_MAX}")
        if type(self.seq) is not int or self.seq < 1 or self.seq > CALL_CAP:
            raise Refuse("BAD_SNAPSHOT")
        cleaned = _checked_arg(self.tool, self.op, self.arg)
        if cleaned != self.arg:
            raise Refuse("BAD_ARG")
        if self.tool == "image":
            if self.model not in _MODEL_SET:
                raise Refuse("BAD_MODEL")
        elif self.model != "":
            raise Refuse("BAD_MODEL")
        body = _dump([SCHEMA, self.tool, self.op, self.arg, self.model, self.at, self.seq, self.code])
        digest = _link(self.prev, body)
        if self.digest != "" and self.digest != digest:
            raise Refuse("BROKEN_CHAIN")
        if self.call_id != "" and self.call_id != digest:
            raise Refuse("BROKEN_CHAIN")
        object.__setattr__(self, "digest", digest)
        object.__setattr__(self, "call_id", digest)


@dataclass(frozen=True, slots=True)
class Batch:
    """Descriptors that fit `budget`. `skipped` counts arguments that did not fit."""

    calls: tuple[Call, ...]
    skipped: int
    budget: int
    requested: int
    clamped: bool

    def __post_init__(self) -> None:
        if type(self.skipped) is not int or self.skipped < 0:
            raise Refuse("BAD_CAP")
        if type(self.budget) is not int or type(self.requested) is not int or type(self.clamped) is not bool:
            raise Refuse("BAD_CAP")
        if self.budget < 1 or self.budget > BATCH_BUDGET:
            raise Refuse("BAD_CAP")
        if self.clamped:
            if self.requested <= BATCH_BUDGET or self.budget != BATCH_BUDGET:
                raise Refuse("BAD_CAP")
        elif self.requested != self.budget:
            raise Refuse("BAD_CAP")
        if type(self.calls) is not tuple:
            raise Refuse("BAD_CALL")
        for call in self.calls:
            if type(call) is not Call:
                raise Refuse("BAD_CALL")


@dataclass(frozen=True, slots=True)
class _Ready:
    tool: str
    op: str
    arg: str
    model: str
    size: int


@dataclass(frozen=True, slots=True)
class Snapshot:
    """Public gateway state. `rebuild` accepts only a chain that links to `fence`."""

    schema: str
    cap: CapNote
    routes: tuple[tuple[str, str], ...]
    declined: tuple[str, ...]
    pinned: tuple[tuple[str, str, str], ...]
    env: tuple[str, ...]
    model: str
    entitled: str
    calls: tuple[Call, ...]
    retried: tuple[str, ...]
    fence: str

    def __post_init__(self) -> None:
        if type(self.schema) is not str or self.schema != SCHEMA:
            raise Refuse("BAD_SNAPSHOT")
        if type(self.cap) is not CapNote:
            raise Refuse("BAD_CAP")
        if self.model not in _MODEL_SET:
            raise Refuse("BAD_MODEL")
        if self.entitled != "" and self.entitled not in _ENTITLED:
            raise Refuse("BAD_KIND")
        if self.entitled == "pool" and self.model in _KREA:
            raise Refuse("POOL")
        routed = _route_table(self.routes, self.cap.applied)
        pinned = _pin_table(self.pinned, self.cap.applied, routed)
        blocked = routed | pinned
        _ascending(self.declined, blocked, "BAD_SNAPSHOT")
        _ascending(self.env, blocked, "BAD_SNAPSHOT")
        _chain(self.calls, self.retried, self.fence)

    def __repr__(self) -> str:
        enabled = ",".join(name for name, _cred_id in self.routes)
        direct = ",".join(f"{name}:{provider}" for name, provider, _cred_id in self.pinned)
        return (
            f"Snapshot(enabled=({enabled}), direct=({direct}), "
            f"model={self.model!r}, entitled={self.entitled!r}, "
            f"calls={len(self.calls)}, fence={self.fence!r})"
        )


def _route_table(routes: object, cap: int) -> set[str]:
    if type(routes) is not tuple:
        raise Refuse("BAD_SNAPSHOT")
    seen: set[str] = set()
    last = -1
    for row in routes:
        if type(row) is not tuple or len(row) != 2:
            raise Refuse("BAD_SNAPSHOT")
        name, cred = row
        if type(name) is not str or name not in _ORDER:
            raise Refuse("BAD_SNAPSHOT")
        pos = _ORDER[name]
        if name in seen or pos <= last:
            raise Refuse("DUPLICATE" if name in seen else "BAD_SNAPSHOT")
        _cred(cred, cap)
        last = pos
        seen.add(name)
    return seen


def _pin_table(pinned: object, cap: int, routed: set[str]) -> set[str]:
    if type(pinned) is not tuple:
        raise Refuse("BAD_SNAPSHOT")
    seen: set[str] = set()
    last = -1
    for row in pinned:
        if type(row) is not tuple or len(row) != 3:
            raise Refuse("BAD_SNAPSHOT")
        name, provider, cred = row
        if type(name) is not str or name not in _ORDER:
            raise Refuse("BAD_SNAPSHOT")
        pos = _ORDER[name]
        if name in seen or pos <= last:
            raise Refuse("DUPLICATE" if name in seen else "BAD_SNAPSHOT")
        if name in routed:
            raise Refuse("BAD_SNAPSHOT")
        if type(provider) is not str or provider not in _PROVIDER_FOR[name] or provider == "nous":
            raise Refuse("BAD_PROVIDER")
        _cred(cred, cap)
        last = pos
        seen.add(name)
    return seen


def _chain(calls: object, retried: object, fence: object) -> None:
    if type(calls) is not tuple or type(retried) is not tuple:
        raise Refuse("BAD_SNAPSHOT")
    if len(calls) > CALL_CAP:
        raise Refuse("CALL_CAP")
    prev = GENESIS
    seen: set[str] = set()
    ready: set[str] = set()
    for index, call in enumerate(calls):
        if type(call) is not Call:
            raise Refuse("BAD_SNAPSHOT")
        if call.call_id in seen:
            raise Refuse("DUPLICATE")
        if call.seq != index + 1 or call.prev != prev:
            raise Refuse("BROKEN_CHAIN" if call.prev != prev else "BAD_SNAPSHOT")
        seen.add(call.call_id)
        if call.code == "READY":
            ready.add(call.call_id)
        prev = call.digest
    if type(fence) is not str or not _hex64(fence):
        raise Refuse("BAD_SNAPSHOT")
    if fence != prev:
        raise Refuse("STALE")
    seen_retry: set[str] = set()
    for ident in retried:
        if type(ident) is not str or ident not in ready or ident in seen_retry:
            raise Refuse("BAD_SNAPSHOT")
        seen_retry.add(ident)


def rebuild(snapshot: object) -> Snapshot:
    """Return the same public state when the chain, fence, and routes verify."""
    if type(snapshot) is not Snapshot:
        raise Refuse("BAD_SNAPSHOT")
    return Snapshot(
        schema=snapshot.schema,
        cap=snapshot.cap,
        routes=snapshot.routes,
        declined=snapshot.declined,
        pinned=snapshot.pinned,
        env=snapshot.env,
        model=snapshot.model,
        entitled=snapshot.entitled,
        calls=snapshot.calls,
        retried=snapshot.retried,
        fence=snapshot.fence,
    )


class ToolGateway:
    """Enablement plus call descriptors. Each catalog tool starts off."""

    __slots__ = (
        "_note",
        "_on",
        "_declined",
        "_pinned",
        "_env",
        "_model",
        "_entitled",
        "_calls",
        "_by_id",
        "_retry_order",
        "_retried",
        "_fence",
    )

    def __init__(self, cred_cap: object = CRED_CAP) -> None:
        self._note = _cap(cred_cap)
        self._on: dict[str, str] = {}
        self._declined: set[str] = set()
        self._pinned: dict[str, tuple[str, str]] = {}
        self._env: set[str] = set()
        self._model = DEFAULT_MODEL
        self._entitled = ""
        self._calls: list[Call] = []
        self._by_id: dict[str, Call] = {}
        self._retry_order: list[str] = []
        self._retried: set[str] = set()
        self._fence = GENESIS

    @property
    def cap_note(self) -> CapNote:
        return self._note

    def entitle(self, kind: object) -> str:
        """Record `paid` or `pool`. There is no off switch. Pool cannot fund Krea."""
        text = bound_text(kind, NAME_CAP)
        if secret_shape(text):
            raise Refuse("SECRET")
        if text not in _ENTITLED:
            raise Refuse("BAD_KIND")
        if text == "pool" and self._model in _KREA:
            raise Refuse("POOL")
        self._entitled = text
        return text

    def enable(self, name: object, cred_id: object) -> Route:
        """Enable one tool. A blank id raises `NO_CRED` and leaves that tool off."""
        kind, _aliased = _classify(name)
        if kind in _TERMINAL:
            _cred(cred_id, self._note.applied)
            raise Refuse("NOT_GATEWAY")
        try:
            cred = _cred(cred_id, self._note.applied)
        except Refuse as err:
            if err.code == "NO_CRED":
                self._on.pop(kind, None)
            raise
        if kind in self._declined:
            raise Refuse("DECLINED")
        if kind in self._pinned:
            raise Refuse("PINNED")
        self._on[kind] = cred
        self._env.discard(kind)
        return Route(name=kind, cred_id=cred, provider="nous", via="gateway")

    def admit(self, allow: object, creds: object) -> tuple[Route, ...]:
        """Enable every named tool. An empty allow enables nothing and clears nothing."""
        items = _allow_items(allow)
        cred_map = _cred_map(creds)
        planned: list[tuple[str, str]] = []
        seen: set[str] = set()
        for item in items:
            kind, _aliased = _classify(item)
            if kind in seen:
                raise Refuse("DUPLICATE")
            seen.add(kind)
            raw = cred_map.get(kind)
            if raw is None:
                raise Refuse("NO_CRED")
            cred = _cred(raw, self._note.applied)
            if kind in _TERMINAL:
                raise Refuse("NOT_GATEWAY")
            if kind in self._pinned:
                raise Refuse("PINNED")
            if kind in self._declined:
                raise Refuse("DECLINED")
            planned.append((kind, cred))
        for kind, cred in planned:
            self._on[kind] = cred
            self._env.discard(kind)
        return tuple(
            Route(name=kind, cred_id=cred, provider="nous", via="gateway") for kind, cred in planned
        )

    def decline(self, name: object) -> str:
        """Stick a decline and drop gateway enablement. A direct pin is left alone."""
        kind = _catalog(name)
        if kind in self._pinned:
            raise Refuse("PINNED")
        self._on.pop(kind, None)
        self._declined.add(kind)
        return kind

    def clear_decline(self, name: object) -> str:
        """Drop a decline. This does not enable the tool."""
        kind = _catalog(name)
        if kind not in self._declined:
            raise Refuse("BAD_STATE")
        self._declined.remove(kind)
        return kind

    def select(self, name: object, provider: object, cred_id: object) -> Route:
        """Store the selection. A direct provider never falls back to nous."""
        kind, _aliased = _classify(name)
        if kind in _TERMINAL:
            _cred(cred_id, self._note.applied)
            raise Refuse("NOT_GATEWAY")
        prov = _provider(kind, provider)
        cred = _cred(cred_id, self._note.applied)
        self._declined.discard(kind)
        self._env.discard(kind)
        if prov == "nous":
            self._pinned.pop(kind, None)
            self._on[kind] = cred
            return Route(name=kind, cred_id=cred, provider="nous", via="gateway")
        self._on.pop(kind, None)
        self._pinned[kind] = (prov, cred)
        return Route(name=kind, cred_id=cred, provider=prov, via="direct")

    def legacy(self, name: object, flag: object, cred_id: object) -> Route:
        """`use_gateway: true` reads as nous. False is not an off switch."""
        if type(flag) is not bool:
            raise Refuse("NOT_BOOL")
        if flag is False:
            kind, _aliased = _classify(name)
            if kind in _TERMINAL:
                _cred(cred_id, self._note.applied)
                raise Refuse("NOT_GATEWAY")
            raise Refuse("LEGACY")
        return self.select(name, "nous", cred_id)

    def note_env(self, name: object) -> str:
        """Remember an env-only backend. It does not enable the tool."""
        kind = _catalog(name)
        if kind in self._pinned or kind in self._on:
            raise Refuse("PINNED")
        self._env.add(kind)
        return kind

    def pin_model(self, model: object) -> str:
        """Pin the image model. Later generate calls cannot override it."""
        text = bound_text(model, MODEL_CAP)
        if secret_shape(text):
            raise Refuse("SECRET")
        if text not in _MODEL_SET:
            raise Refuse("BAD_MODEL")
        if text in _KREA and self._entitled == "pool":
            raise Refuse("POOL")
        self._model = text
        return text

    def plan(self) -> tuple[str, ...]:
        """Return nous-enabled names in catalog order. Direct pins stay out."""
        enabled = self._on
        return tuple(name for name in TOOLS if name in enabled)

    def offers(self) -> tuple[Offer, ...]:
        """Checklist. Explicit backends are not offered. Env-only stays unchecked."""
        rows: list[Offer] = []
        pinned = self._pinned
        enabled = self._on
        declined = self._declined
        env = self._env
        for name in TOOLS:
            if name in pinned:
                rows.append(Offer(name, False, False, "explicit"))
            elif name in enabled:
                rows.append(Offer(name, False, False, "active"))
            elif name in declined:
                rows.append(Offer(name, True, False, "declined"))
            elif name in env:
                rows.append(Offer(name, True, False, "env"))
            else:
                rows.append(Offer(name, True, True, "open"))
        return tuple(rows)

    def call(
        self,
        name: object,
        op: object,
        arg: object,
        at: object,
        cred_id: object = None,
        model: object = None,
    ) -> Call:
        """Return one descriptor. A missing terminal id is `NO_CRED`."""
        moment = _moment(at)
        ready = self._ready(name, op, arg, cred_id, model)
        if len(self._calls) >= CALL_CAP:
            raise Refuse("CALL_CAP")
        return self._append(ready, moment, "READY")

    def dispatch(self, items: object, at: object, budget: object = None) -> Batch:
        """One pass. Skip an argument that does not fit. Keep a later one that does."""
        moment = _moment(at)
        applied, requested, clamped = _batch_budget(budget)
        specs: list[_Ready] = []
        for item in _rows(items):
            name, op, arg = _triple(item)
            specs.append(self._ready(name, op, arg, None, None))
        kept: list[_Ready] = []
        skipped = 0
        remaining = applied
        room = CALL_CAP - len(self._calls)
        for spec in specs:
            if spec.size > remaining:
                skipped += 1
                continue
            if len(kept) >= room:
                raise Refuse("CALL_CAP")
            kept.append(spec)
            remaining -= spec.size
        calls = tuple(self._append(spec, moment, "READY") for spec in kept)
        return Batch(calls=calls, skipped=skipped, budget=applied, requested=requested, clamped=clamped)

    def retry(self, call_id: object, failure: object, at: object) -> Call:
        """One confirming retry, and only for `RATE_LIMIT`."""
        ident = _call_id(call_id)
        fail = _failure(failure)
        moment = _moment(at)
        found = self._by_id.get(ident)
        if found is None:
            raise Refuse("BAD_CALL")
        if found.code != "READY" or not const_eq(fail, RETRY_CLASS):
            raise Refuse("NO_RETRY")
        if ident in self._retried:
            raise Refuse("RETRY_CAP")
        if len(self._calls) >= CALL_CAP:
            raise Refuse("CALL_CAP")
        ready = _Ready(
            tool=found.tool,
            op=found.op,
            arg=found.arg,
            model=found.model,
            size=len(found.arg),
        )
        record = self._append(ready, moment, "RETRY")
        self._retried.add(ident)
        self._retry_order.append(ident)
        return record

    def snapshot(self) -> Snapshot:
        """Freeze routes, pins, and the call chain."""
        routes = tuple((name, self._on[name]) for name in TOOLS if name in self._on)
        declined = tuple(name for name in TOOLS if name in self._declined)
        env = tuple(name for name in TOOLS if name in self._env)
        pinned: list[tuple[str, str, str]] = []
        for name in TOOLS:
            row = self._pinned.get(name)
            if row is not None:
                provider, cred = row
                pinned.append((name, provider, cred))
        return Snapshot(
            schema=SCHEMA,
            cap=self._note,
            routes=routes,
            declined=declined,
            pinned=tuple(pinned),
            env=env,
            model=self._model,
            entitled=self._entitled,
            calls=tuple(self._calls),
            retried=tuple(self._retry_order),
            fence=self._fence,
        )

    @classmethod
    def load(cls, snapshot: object) -> ToolGateway:
        """Rebuild a gateway whose snapshot equals `snapshot`."""
        snap = rebuild(snapshot)
        gate = cls(snap.cap.requested)
        if gate._note != snap.cap:
            raise Refuse("BAD_CAP")
        gate._on = {name: cred for name, cred in snap.routes}
        gate._declined = set(snap.declined)
        gate._pinned = {name: (provider, cred) for name, provider, cred in snap.pinned}
        gate._env = set(snap.env)
        gate._model = snap.model
        gate._entitled = snap.entitled
        gate._calls = list(snap.calls)
        gate._by_id = {call.call_id: call for call in snap.calls}
        gate._retry_order = list(snap.retried)
        gate._retried = set(snap.retried)
        gate._fence = snap.fence
        return gate

    def _ready(
        self,
        name: object,
        op: object,
        arg: object,
        cred_id: object,
        model: object,
    ) -> _Ready:
        _reject_override(model)
        kind, aliased = _classify(name)
        if kind in _TERMINAL:
            _cred(cred_id, self._note.applied)
            raise Refuse("NOT_GATEWAY")
        operation = _op(kind, op, aliased)
        supplied: str | None
        if cred_id is not None:
            supplied = _cred(cred_id, self._note.applied)
        else:
            supplied = None
        if kind in self._pinned:
            raise Refuse("DIRECT")
        stored = self._on.get(kind)
        if stored is None:
            raise Refuse("OFF")
        if supplied is not None and not const_eq(supplied, stored):
            raise Refuse("STALE")
        if self._entitled == "":
            raise Refuse("NO_ENTITLE")
        cleaned = _checked_arg(kind, operation, arg)
        pinned_model = ""
        if kind == "image" and operation == "generate":
            if self._model in _KREA and self._entitled == "pool":
                raise Refuse("POOL")
            pinned_model = self._model
        return _Ready(tool=kind, op=operation, arg=cleaned, model=pinned_model, size=len(cleaned))

    def _append(self, ready: _Ready, at: int, code: str) -> Call:
        record = Call(
            schema=SCHEMA,
            tool=ready.tool,
            op=ready.op,
            arg=ready.arg,
            model=ready.model,
            at=at,
            seq=len(self._calls) + 1,
            prev=self._fence,
            code=code,
        )
        self._calls.append(record)
        self._by_id[record.call_id] = record
        self._fence = record.digest
        return record

    def __repr__(self) -> str:
        shown = ",".join(self.plan())
        return (
            f"ToolGateway(enabled=({shown}), cred_cap={self._note.applied}, "
            f"entitled={self._entitled!r}, model={self._model!r})"
        )


__all__ = [
    "ARG_CAP",
    "BATCH_BUDGET",
    "CALL_CAP",
    "CRED_CAP",
    "DEFAULT_MODEL",
    "GENESIS",
    "IMAGE_MODELS",
    "LIST_CAP",
    "MODEL_CAP",
    "NAME_CAP",
    "OPS",
    "PROVIDERS",
    "RETRY_CLASS",
    "SCHEMA",
    "TOOLS",
    "Batch",
    "Call",
    "CapNote",
    "Offer",
    "Route",
    "Snapshot",
    "ToolGateway",
    "rebuild",
]
