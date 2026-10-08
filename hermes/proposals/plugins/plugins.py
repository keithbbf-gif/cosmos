"""Admit host-injected plugin callables. A path is never imported."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import cast

from cosmos_hermes import Refuse, bound_int, bound_text, const_eq, secret_shape

SCHEMA = "cosmos-hermes-plugins/1"
POLICY_CAP = 32
CATALOG_BUDGET = 512
TEXT_CAP = 256
GENESIS = "0" * 64
KINDS: tuple[str, ...] = ("tool", "memory", "context")
PERMISSIONS: tuple[str, ...] = (
    "tools.override",
    "llm.provider_override",
    "llm.model_override",
    "llm.agent_id_override",
    "llm.profile_override",
    "llm.task_override",
    "gateway.platform_actions",
)

_ASK_HI = 1_000_000
_NAME_CAP = 64
_TOKEN_CAP = 64
_DESCRIPTION_CAP = 128
_EXCLUSIVE = frozenset(("memory", "context"))
_NAME = re.compile(r"^[a-z][a-z0-9-]{0,63}$")
_CALL = re.compile(r"^call-[0-9]{4}$")
_HEX = re.compile(r"^[0-9a-f]{64}$")
_DESC = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 .,':_-]{0,127}$")

_Handler = Callable[[str], str]


def _plain(value: object, limit: int) -> str:
    text = bound_text(value, limit)
    if secret_shape(text):
        raise Refuse("SECRET")
    return text


def _name(value: object) -> str:
    text = _plain(value, _NAME_CAP)
    if _NAME.fullmatch(text) is None:
        raise Refuse("BAD_NAME")
    return text


def _signer(value: object) -> str:
    text = _plain(value, _NAME_CAP)
    if text == "":
        raise Refuse("MISSING_CRED")
    if _NAME.fullmatch(text) is None:
        raise Refuse("BAD_CRED")
    return text


def _kind(value: object) -> str:
    text = _plain(value, _TOKEN_CAP)
    for item in KINDS:
        if const_eq(text, item):
            return item
    raise Refuse("BAD_KIND")


def _catalog_token(value: object) -> str:
    text = _plain(value, _TOKEN_CAP)
    for item in PERMISSIONS:
        if const_eq(text, item):
            return item
    raise Refuse("UNCLASSIFIED")


def _call_id(value: object) -> str:
    text = _plain(value, _NAME_CAP)
    if _CALL.fullmatch(text) is None:
        raise Refuse("BAD_ID")
    return text


def _description(value: object) -> str:
    text = _plain(value, _DESCRIPTION_CAP)
    if _DESC.fullmatch(text) is None:
        raise Refuse("BAD_TEXT")
    return text


def _hex(value: object, code: str) -> str:
    text = _plain(value, 64)
    if _HEX.fullmatch(text) is None:
        raise Refuse(code)
    return text


def _tokens(value: object) -> tuple[str, ...]:
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Sequence):
        raise Refuse("NOT_LIST")
    if len(value) > POLICY_CAP:
        raise Refuse("OVERSIZE", str(POLICY_CAP))
    found: list[str] = []
    seen: set[str] = set()
    raw = cast(Sequence[object], value)
    for item in raw:
        token = _catalog_token(item)
        if token in seen:
            raise Refuse("DUPLICATE")
        seen.add(token)
        found.append(token)
    return tuple(found)


def _name_seq(value: object, *, empty: str | None) -> tuple[str, ...]:
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Sequence):
        raise Refuse("NOT_LIST")
    if len(value) > POLICY_CAP:
        raise Refuse("OVERSIZE", str(POLICY_CAP))
    found: list[str] = []
    seen: set[str] = set()
    raw = cast(Sequence[object], value)
    for item in raw:
        name = _name(item)
        if name in seen:
            raise Refuse("DUPLICATE")
        seen.add(name)
        found.append(name)
    if empty is not None and len(found) == 0:
        raise Refuse(empty)
    return tuple(found)


def _name_tuple(value: object) -> tuple[str, ...]:
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, tuple):
        raise Refuse("NOT_LIST")
    if len(value) > POLICY_CAP:
        raise Refuse("OVERSIZE", str(POLICY_CAP))
    found: list[str] = []
    seen: set[str] = set()
    raw = cast(tuple[object, ...], value)
    for item in raw:
        name = _name(item)
        if name in seen:
            raise Refuse("DUPLICATE")
        seen.add(name)
        found.append(name)
    return tuple(found)


def _limit(value: object, policy: int) -> tuple[int, int]:
    """Return `(requested, applied)`. Applied never exceeds `policy`."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("NOT_INT")
    if value < 1 or value > _ASK_HI:
        raise Refuse("OUT_OF_RANGE", f"1..{_ASK_HI}")
    applied = policy if value > policy else value
    return value, applied


def _stored_budget(applied: object, requested: object) -> tuple[int, int]:
    if isinstance(applied, bool) or not isinstance(applied, int):
        raise Refuse("NOT_INT")
    if isinstance(requested, bool) or not isinstance(requested, int):
        raise Refuse("NOT_INT")
    if requested < 1 or requested > _ASK_HI:
        raise Refuse("OUT_OF_RANGE", f"1..{_ASK_HI}")
    if applied < 1 or applied > CATALOG_BUDGET:
        raise Refuse("OUT_OF_RANGE", f"1..{CATALOG_BUDGET}")
    if requested > CATALOG_BUDGET:
        if applied != CATALOG_BUDGET:
            raise Refuse("OUT_OF_RANGE", str(CATALOG_BUDGET))
    elif applied != requested:
        raise Refuse("OUT_OF_RANGE", str(requested))
    return applied, requested


def _handler(value: object) -> _Handler:
    if isinstance(value, type) or not callable(value):
        raise Refuse("NOT_CALLABLE")
    return cast(_Handler, value)


def _mapping(value: object) -> Mapping[object, object]:
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Mapping):
        raise Refuse("NOT_MAP")
    if len(value) > POLICY_CAP:
        raise Refuse("OVERSIZE", str(POLICY_CAP))
    return cast(Mapping[object, object], value)


def _named_map(value: object) -> dict[str, object]:
    raw = _mapping(value)
    found: dict[str, object] = {}
    for key, item in raw.items():
        name = _name(key)
        if name in found:
            raise Refuse("DUPLICATE")
        found[name] = item
    return found


def _links(value: object) -> tuple[Link, ...]:
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Sequence):
        raise Refuse("NOT_LIST")
    if len(value) > POLICY_CAP:
        raise Refuse("OVERSIZE", str(POLICY_CAP))
    found: list[Link] = []
    raw = cast(Sequence[object], value)
    for item in raw:
        if not isinstance(item, Link):
            raise Refuse("BROKEN_CHAIN")
        found.append(item)
    return tuple(found)


def _granted(requested: tuple[str, ...], allowed: tuple[str, ...]) -> None:
    grant = set(allowed)
    for token in requested:
        if token not in grant:
            raise Refuse("PERMISSION", token)


def _seal_checked(signer: str, name: str) -> str:
    payload = f"{SCHEMA}|{signer}|{name}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _link_digest(
    prior: str,
    seq: int,
    name: str,
    callable_id: str,
    kind: str,
    permissions: tuple[str, ...],
    description: str,
) -> str:
    # Description text cannot contain a newline, so each join row is one field.
    payload = "\n".join(
        (
            SCHEMA,
            prior,
            str(seq),
            name,
            callable_id,
            kind,
            ",".join(permissions),
            description,
        )
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def seal(signer: object, name: object) -> str:
    """Consent digest for one name. Not a certificate and not a private key."""
    return _seal_checked(_signer(signer), _name(name))


def load_from_path(path: object) -> None:
    """Refuse every disk import. The argument is not opened."""
    del path
    raise Refuse("IMPORT")


@dataclass(frozen=True, slots=True)
class Plugin:
    """Public admission. The callable stays on the registry."""

    name: str
    callable_id: str
    kind: str

    def __post_init__(self) -> None:
        name = _name(self.name)
        callable_id = _call_id(self.callable_id)
        kind = _kind(self.kind)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "callable_id", callable_id)
        object.__setattr__(self, "kind", kind)


@dataclass(frozen=True, slots=True)
class Link:
    """One chain record. `prior` is the previous digest, or `GENESIS`."""

    seq: int
    name: str
    callable_id: str
    kind: str
    permissions: tuple[str, ...]
    description: str
    prior: str
    digest: str

    def __post_init__(self) -> None:
        seq = bound_int(self.seq, 1, POLICY_CAP)
        name = _name(self.name)
        callable_id = _call_id(self.callable_id)
        kind = _kind(self.kind)
        permissions = _tokens(self.permissions)
        description = _description(self.description)
        prior = _hex(self.prior, "BROKEN_CHAIN")
        digest = _hex(self.digest, "BROKEN_CHAIN")
        object.__setattr__(self, "seq", seq)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "callable_id", callable_id)
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "permissions", permissions)
        object.__setattr__(self, "description", description)
        object.__setattr__(self, "prior", prior)
        object.__setattr__(self, "digest", digest)


@dataclass(frozen=True, slots=True)
class Result:
    """Text returned by one injected callable."""

    name: str
    callable_id: str
    text: str

    def __post_init__(self) -> None:
        name = _name(self.name)
        callable_id = _call_id(self.callable_id)
        text = _plain(self.text, TEXT_CAP)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "callable_id", callable_id)
        object.__setattr__(self, "text", text)


@dataclass(frozen=True, slots=True)
class Catalog:
    """Names that fit the budget, then names that were skipped."""

    names: tuple[str, ...]
    skipped: tuple[str, ...]
    budget: int
    requested: int

    def __post_init__(self) -> None:
        names = _name_tuple(self.names)
        skipped = _name_tuple(self.skipped)
        if set(names) & set(skipped):
            raise Refuse("DUPLICATE")
        budget, requested = _stored_budget(self.budget, self.requested)
        object.__setattr__(self, "names", names)
        object.__setattr__(self, "skipped", skipped)
        object.__setattr__(self, "budget", budget)
        object.__setattr__(self, "requested", requested)


@dataclass(frozen=True, slots=True)
class _Held:
    plugin: Plugin
    link: Link
    handler: _Handler = field(repr=False, compare=False)


class Registry:
    """In-memory admissions. Call runs only an allowlisted injected callable."""

    __slots__ = (
        "_allow",
        "_deny",
        "_signer",
        "_requested",
        "_applied",
        "_order",
        "_by_name",
        "_exclusive",
        "_fence",
    )

    _allow: frozenset[str]
    _deny: frozenset[str]
    _signer: str
    _requested: int
    _applied: int
    _order: list[_Held]
    _by_name: dict[str, _Held]
    _exclusive: dict[str, str]
    _fence: str

    def __init__(
        self,
        allow: object,
        signer: object,
        cap: object = POLICY_CAP,
        deny: object = (),
    ) -> None:
        allow_names = _name_seq(allow, empty="EMPTY_ALLOW")
        deny_names = _name_seq(deny, empty=None)
        checked = _signer(signer)
        requested, applied = _limit(cap, POLICY_CAP)
        self._allow = frozenset(allow_names)
        self._deny = frozenset(deny_names)
        self._signer = checked
        self._requested = requested
        self._applied = applied
        self._order = []
        self._by_name = {}
        self._exclusive = {}
        self._fence = GENESIS

    def __repr__(self) -> str:
        return (
            f"Registry(cap={self._applied}, requested={self._requested}, "
            f"count={len(self._order)}, fence={self._fence})"
        )

    @property
    def cap(self) -> int:
        """Cap in force. A higher request is ignored."""
        return self._applied

    @property
    def requested(self) -> int:
        """Cap the caller asked for. It may sit above `cap`."""
        return self._requested

    @property
    def fence(self) -> str:
        """Chain head. An empty registry is `GENESIS`."""
        return self._fence

    def entries(self) -> tuple[Plugin, ...]:
        """Admissions in registration order."""
        return tuple(held.plugin for held in self._order)

    def links(self) -> tuple[Link, ...]:
        """Chain records in registration order."""
        return tuple(held.link for held in self._order)

    def get(self, name: object) -> Plugin:
        """Return one admission. This does not run the callable."""
        checked = _name(name)
        held = self._by_name.get(checked)
        if held is None:
            raise Refuse("ABSENT", checked)
        return held.plugin

    def register(
        self,
        name: object,
        kind: object,
        permissions: object,
        grant: object,
        handler: object,
        signature: object,
        description: object,
    ) -> Plugin:
        """Admit one plugin when the seal matches and the name is allowlisted."""
        checked = _name(name)
        checked_kind = _kind(kind)
        blurb = _description(description)
        requested = _tokens(permissions)
        allowed = _tokens(grant)
        _granted(requested, allowed)
        checked_handler = _handler(handler)
        signed = _hex(signature, "UNSIGNED")
        if checked in self._deny:
            raise Refuse("DENIED", checked)
        if checked not in self._allow:
            raise Refuse("NOT_ALLOWED", checked)
        expected = _seal_checked(self._signer, checked)
        if not const_eq(signed, expected):
            raise Refuse("UNSIGNED")
        held = self._admit(checked, checked_kind, requested, blurb, checked_handler)
        return held.plugin

    def call(self, name: object, text: object) -> Result:
        """Run the injected callable for an allowlisted, admitted name."""
        checked = _name(name)
        payload = _plain(text, TEXT_CAP)
        if checked in self._deny:
            raise Refuse("DENIED", checked)
        if checked not in self._allow:
            raise Refuse("NOT_ALLOWED", checked)
        held = self._by_name.get(checked)
        if held is None:
            raise Refuse("UNKNOWN", checked)
        raw = self._invoke(held.handler, payload)
        return Result(checked, held.plugin.callable_id, raw)

    def catalog(self, budget: object = CATALOG_BUDGET) -> Catalog:
        """One pass. Skip a description that does not fit, then continue."""
        requested, applied = _limit(budget, CATALOG_BUDGET)
        remaining = applied
        names: list[str] = []
        skipped: list[str] = []
        for held in self._order:
            cost = len(held.link.description)
            if cost > remaining:
                skipped.append(held.plugin.name)
                continue
            names.append(held.plugin.name)
            remaining -= cost
        return Catalog(tuple(names), tuple(skipped), applied, requested)

    def load_from_path(self, path: object) -> None:
        """Refuse disk import. Stored rows stay as they are."""
        load_from_path(path)

    @classmethod
    def rebuild(
        cls,
        links: object,
        handlers: object,
        signatures: object,
        allow: object,
        signer: object,
        fence: object,
        cap: object = POLICY_CAP,
        deny: object = (),
    ) -> Registry:
        """Replay links. The same public entries come back, or the chain refuses."""
        registry = cls(allow, signer, cap, deny)
        rows = _links(links)
        if len(rows) > registry.cap:
            raise Refuse("FULL")
        handler_map = _named_map(handlers)
        signature_map = _named_map(signatures)
        checked_fence = _hex(fence, "BAD_FENCE")
        prior = GENESIS
        seen: set[str] = set()
        ready: list[tuple[Link, _Handler]] = []
        for index, link in enumerate(rows, start=1):
            if link.seq != index:
                raise Refuse("BROKEN_CHAIN", "seq")
            if not const_eq(link.callable_id, f"call-{index:04d}"):
                raise Refuse("BROKEN_CHAIN", "id")
            if not const_eq(link.prior, prior):
                raise Refuse("BROKEN_CHAIN", "prior")
            if link.name in registry._deny:
                raise Refuse("DENIED", link.name)
            if link.name not in registry._allow:
                raise Refuse("NOT_ALLOWED", link.name)
            if link.name not in handler_map:
                raise Refuse("NOT_CALLABLE")
            if link.name not in signature_map:
                raise Refuse("UNSIGNED")
            handler = _handler(handler_map[link.name])
            signed = _hex(signature_map[link.name], "UNSIGNED")
            if not const_eq(signed, _seal_checked(registry._signer, link.name)):
                raise Refuse("UNSIGNED")
            if link.name in seen:
                raise Refuse("DUPLICATE")
            seen.add(link.name)
            ready.append((link, handler))
            prior = link.digest
        for extra in handler_map:
            if extra not in seen:
                raise Refuse("UNKNOWN", extra)
        for extra in signature_map:
            if extra not in seen:
                raise Refuse("UNKNOWN", extra)
        for link, handler in ready:
            held = registry._admit(
                link.name,
                link.kind,
                link.permissions,
                link.description,
                handler,
            )
            if held.link != link:
                raise Refuse("BROKEN_CHAIN", "digest")
        if not const_eq(registry.fence, checked_fence):
            raise Refuse("STALE")
        return registry

    def _admit(
        self,
        name: str,
        kind: str,
        permissions: tuple[str, ...],
        description: str,
        handler: _Handler,
    ) -> _Held:
        if name in self._by_name:
            raise Refuse("DUPLICATE")
        if kind in _EXCLUSIVE and kind in self._exclusive:
            raise Refuse("EXCLUSIVE", kind)
        if len(self._order) >= self._applied:
            raise Refuse("FULL")
        seq = len(self._order) + 1
        callable_id = f"call-{seq:04d}"
        prior = self._fence
        digest = _link_digest(prior, seq, name, callable_id, kind, permissions, description)
        plugin = Plugin(name, callable_id, kind)
        link = Link(seq, name, callable_id, kind, permissions, description, prior, digest)
        held = _Held(plugin, link, handler)
        self._order.append(held)
        self._by_name[name] = held
        if kind in _EXCLUSIVE:
            self._exclusive[kind] = name
        self._fence = digest
        return held

    def _invoke(self, handler: _Handler, payload: str) -> str:
        try:
            raw: object = handler(payload)
        except Refuse:
            raise
        except Exception:
            raise Refuse("PLUGIN_FAIL") from None
        if isinstance(raw, Refuse):
            raise raw
        if not isinstance(raw, str):
            raise Refuse("BAD_RESULT")
        return raw


__all__ = [
    "CATALOG_BUDGET",
    "GENESIS",
    "KINDS",
    "PERMISSIONS",
    "POLICY_CAP",
    "SCHEMA",
    "TEXT_CAP",
    "Catalog",
    "Link",
    "Plugin",
    "Registry",
    "Result",
    "load_from_path",
    "seal",
]
