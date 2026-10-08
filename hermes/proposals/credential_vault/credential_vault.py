"""Purpose-bound credential ids. Sealed blobs stay sealed.

The vault stores an id, exact origins, and visible metadata.
It never stores or returns key material.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Final, Literal, TypeVar

from cosmos_hermes import Refuse, bound_int, bound_text, const_eq, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-credential_vault/1"
POLICY_CAP: Final[int] = 32
POLICY_BUDGET: Final[int] = 256
POLICY_ORIGINS: Final[int] = 4
POLICY_HISTORY: Final[int] = 128
FIELD_CAP: Final[int] = 8

_ID_CAP: Final[int] = 32
_LABEL_CAP: Final[int] = 64
_LOGIN_CAP: Final[int] = 64
_ORIGIN_CAP: Final[int] = 256
_NAME_CAP: Final[int] = 32
_SCAN: Final[int] = 512
_CAP_HI: Final[int] = 1_000_000
_BUDGET_HI: Final[int] = 1_000_000
_STAMP_HI: Final[int] = 4_000_000_000
_GENESIS: Final[str] = "0" * 64

Kind = Literal["login", "address", "card", "totp", "passkey", "approval"]
Source = Literal["local", "onepassword", "bitwarden"]
Session = Literal["interactive", "headless"]
Action = Literal["FILL", "WAIT"]
Op = Literal["PUT", "REMOVE", "UNLOCK", "DISABLE"]

_KINDS: Final[tuple[Kind, ...]] = (
    "login",
    "address",
    "card",
    "totp",
    "passkey",
    "approval",
)
_SOURCES: Final[tuple[Source, ...]] = ("local", "onepassword", "bitwarden")
_MANAGERS: Final[tuple[Source, ...]] = ("onepassword", "bitwarden")
_SESSIONS: Final[tuple[Session, ...]] = ("interactive", "headless")
_OPS: Final[tuple[Op, ...]] = ("PUT", "REMOVE", "UNLOCK", "DISABLE")
_WAIT: Final[frozenset[str]] = frozenset(("passkey", "approval"))
_KIND_SET: Final[frozenset[str]] = frozenset(_KINDS)
_SOURCE_SET: Final[frozenset[str]] = frozenset(_SOURCES)
_MANAGER_SET: Final[frozenset[str]] = frozenset(_MANAGERS)
_SESSION_SET: Final[frozenset[str]] = frozenset(_SESSIONS)
_OP_SET: Final[frozenset[str]] = frozenset(_OPS)

_ID_RE: Final[re.Pattern[str]] = re.compile(
    r"^[a-z0-9](?:[a-z0-9-]{0,30}[a-z0-9])?$"
)
_LABEL_RE: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9 ._'()-]{0,63}$"
)
_LOGIN_RE: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9.@+_/-]{0,63}$"
)
_ORIGIN_RE: Final[re.Pattern[str]] = re.compile(
    r"^https://[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
    r"(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+$"
)
_HEX64_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class CapNote:
    """Applied item cap. `clamped` means a higher request was ignored."""

    applied: int
    requested: int
    clamped: bool

    def __repr__(self) -> str:
        return (
            f"CapNote(applied={self.applied}, requested={self.requested}, "
            f"clamped={self.clamped})"
        )


@dataclass(frozen=True, slots=True)
class Item:
    """Visible vault metadata. No secret field."""

    cred_id: str
    kind: str
    origins: tuple[str, ...]
    label: str
    login_id: str
    source: str
    fields: int

    def weight(self) -> int:
        total = (
            len(self.cred_id)
            + len(self.kind)
            + len(self.label)
            + len(self.login_id)
            + len(self.source)
            + self.fields
        )
        for origin in self.origins:
            total += len(origin)
        return total

    def __repr__(self) -> str:
        return (
            f"Item(cred_id={self.cred_id!r}, kind={self.kind!r}, "
            f"origins={self.origins!r}, label={self.label!r}, "
            f"login_id={self.login_id!r}, source={self.source!r}, "
            f"fields={self.fields})"
        )


@dataclass(frozen=True, slots=True)
class Resolution:
    """What a caller may see after a purpose match. The id, not the blob."""

    cred_id: str
    purpose: str
    action: Action
    filled_fields: int
    kind: str

    def __repr__(self) -> str:
        return (
            f"Resolution(cred_id={self.cred_id!r}, purpose={self.purpose!r}, "
            f"action={self.action!r}, filled_fields={self.filled_fields}, "
            f"kind={self.kind!r})"
        )


@dataclass(frozen=True, slots=True)
class Selection:
    """One catalog pass for a single origin."""

    purpose: str
    applied_budget: int
    requested_budget: int
    clamped: bool
    items: tuple[Item, ...]
    skipped: tuple[str, ...]

    def __repr__(self) -> str:
        ids = tuple(item.cred_id for item in self.items)
        return (
            f"Selection(purpose={self.purpose!r}, applied_budget={self.applied_budget}, "
            f"requested_budget={self.requested_budget}, clamped={self.clamped}, "
            f"ids={ids!r}, skipped={self.skipped!r})"
        )


@dataclass(frozen=True, slots=True)
class Record:
    """One hash-chained mutation. Public fields only."""

    seq: int
    stamp: int
    op: str
    cred_id: str
    kind: str
    origins: tuple[str, ...]
    label: str
    login_id: str
    source: str
    fields: int
    prev: str
    digest: str

    def __repr__(self) -> str:
        return (
            f"Record(seq={self.seq}, stamp={self.stamp}, op={self.op!r}, "
            f"cred_id={self.cred_id!r}, kind={self.kind!r}, origins={self.origins!r}, "
            f"label={self.label!r}, login_id={self.login_id!r}, source={self.source!r}, "
            f"fields={self.fields})"
        )


@dataclass(frozen=True, slots=True)
class Snapshot:
    """Public state. `rebuild` of `records` reproduces it."""

    schema: str
    session: str
    cap: CapNote
    ids: tuple[str, ...]
    items: tuple[Item, ...]
    unlocked: tuple[str, ...]
    disabled: tuple[str, ...]
    records: tuple[Record, ...]

    def __repr__(self) -> str:
        return (
            f"Snapshot(schema={self.schema!r}, session={self.session!r}, "
            f"cap={self.cap.applied}, ids={self.ids!r}, "
            f"unlocked={self.unlocked!r}, disabled={self.disabled!r}, "
            f"n_records={len(self.records)})"
        )


def _digest(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _body(rec: Record) -> str:
    origins = ",".join(rec.origins)
    return (
        f"{rec.seq}|{rec.stamp}|{rec.op}|{rec.cred_id}|{rec.kind}|{origins}|"
        f"{rec.label}|{rec.login_id}|{rec.source}|{rec.fields}|{rec.prev}"
    )


_Name = TypeVar("_Name", bound=str)


def _edge(value: object, limit: int) -> str:
    """Bound, then refuse key shapes, then apply the field cap."""
    text = bound_text(value, _SCAN)
    if secret_shape(text):
        raise Refuse("SECRET")
    if len(text) > limit:
        raise Refuse("OVERSIZE", str(limit))
    return text


def _named(
    value: object,
    options: tuple[_Name, ...],
    allowed: frozenset[str],
    code: str,
) -> _Name:
    text = _edge(value, _NAME_CAP)
    if text == "":
        raise Refuse("EMPTY")
    if text not in allowed:
        raise Refuse(code)
    for name in options:
        if name == text:
            return name
    raise Refuse(code)


def _kind(value: object) -> Kind:
    return _named(value, _KINDS, _KIND_SET, "BAD_KIND")


def _source(value: object) -> Source:
    return _named(value, _SOURCES, _SOURCE_SET, "BAD_SOURCE")


def _manager(value: object) -> Source:
    return _named(value, _MANAGERS, _MANAGER_SET, "BAD_SOURCE")


def _session(value: object) -> Session:
    return _named(value, _SESSIONS, _SESSION_SET, "BAD_SESSION")


def _ident(value: object) -> str:
    text = _edge(value, _ID_CAP)
    if text == "":
        raise Refuse("EMPTY")
    if _ID_RE.fullmatch(text) is None:
        raise Refuse("BAD_ID")
    return text


def _label(value: object) -> str:
    text = _edge(value, _LABEL_CAP)
    if text == "":
        raise Refuse("EMPTY")
    if _LABEL_RE.fullmatch(text) is None:
        raise Refuse("BAD_LABEL")
    return text


def _login(value: object) -> str:
    text = _edge(value, _LOGIN_CAP)
    if text == "":
        return ""
    if _LOGIN_RE.fullmatch(text) is None:
        raise Refuse("BAD_LOGIN")
    return text


def _origin(value: object) -> str:
    text = _edge(value, _ORIGIN_CAP)
    if text == "":
        raise Refuse("EMPTY")
    if _ORIGIN_RE.fullmatch(text) is None:
        raise Refuse("BAD_ORIGIN")
    return text


def _origins(value: object) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        raise Refuse("NOT_TUPLE")
    if len(value) == 0:
        raise Refuse("EMPTY")
    if len(value) > POLICY_ORIGINS:
        raise Refuse("CAP", str(POLICY_ORIGINS))
    found: list[str] = []
    seen: set[str] = set()
    for part in value:
        origin = _origin(part)
        if origin in seen:
            raise Refuse("DUPLICATE")
        seen.add(origin)
        found.append(origin)
    return tuple(found)


def _fields(value: object) -> int:
    return bound_int(value, 1, FIELD_CAP)


def _stamp(value: object) -> int:
    return bound_int(value, 0, _STAMP_HI)


def _flag(value: object) -> bool:
    if isinstance(value, bool):
        return value
    raise Refuse("NOT_BOOL")


def _budget(value: object) -> tuple[int, int, bool]:
    requested = bound_int(value, 0, _BUDGET_HI)
    # Policy budget wins. A higher request is recorded and not applied.
    applied = POLICY_BUDGET if requested > POLICY_BUDGET else requested
    return applied, requested, requested > POLICY_BUDGET


def _cap(value: object) -> tuple[int, int, bool]:
    requested = bound_int(value, 1, _CAP_HI)
    applied = POLICY_CAP if requested > POLICY_CAP else requested
    return applied, requested, requested > POLICY_CAP


def _detected(value: object) -> frozenset[str]:
    if not isinstance(value, tuple):
        raise Refuse("NOT_TUPLE")
    if len(value) > len(_MANAGERS):
        raise Refuse("CAP", str(len(_MANAGERS)))
    found: set[str] = set()
    for part in value:
        name = _manager(part)
        if name in found:
            raise Refuse("DUPLICATE")
        found.add(name)
    return frozenset(found)


def _purpose_hit(item: Item, purpose: str) -> bool:
    for origin in item.origins:
        if const_eq(origin, purpose):
            return True
    return False


def _plain_int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("BAD_RECORD")
    return value


def _plain_str(value: object) -> str:
    if not isinstance(value, str):
        raise Refuse("BAD_RECORD")
    return value


def _as_record(value: object) -> Record:
    if not isinstance(value, Record):
        raise Refuse("BAD_RECORD")
    return value


def _record_shape(rec: Record) -> None:
    seq = _plain_int(rec.seq)
    stamp = _plain_int(rec.stamp)
    fields = _plain_int(rec.fields)
    op = _plain_str(rec.op)
    cred_id = _plain_str(rec.cred_id)
    kind = _plain_str(rec.kind)
    label = _plain_str(rec.label)
    login_id = _plain_str(rec.login_id)
    source = _plain_str(rec.source)
    prev = _plain_str(rec.prev)
    digest = _plain_str(rec.digest)
    if not isinstance(rec.origins, tuple):
        raise Refuse("BAD_RECORD")
    if seq != rec.seq or stamp != rec.stamp or fields != rec.fields:
        raise Refuse("BAD_RECORD")
    if op not in _OP_SET:
        raise Refuse("BAD_RECORD")
    if _HEX64_RE.fullmatch(prev) is None or _HEX64_RE.fullmatch(digest) is None:
        raise Refuse("BAD_RECORD")
    if cred_id != rec.cred_id or kind != rec.kind or label != rec.label:
        raise Refuse("BAD_RECORD")
    if login_id != rec.login_id or source != rec.source:
        raise Refuse("BAD_RECORD")
    for part in rec.origins:
        if not isinstance(part, str):
            raise Refuse("BAD_RECORD")


def _semantics(rec: Record) -> None:
    """Re-check a record with the same edge rules as a live call."""
    if rec.op == "PUT":
        _ident(rec.cred_id)
        _kind(rec.kind)
        _origins(rec.origins)
        _label(rec.label)
        _login(rec.login_id)
        _source(rec.source)
        _fields(rec.fields)
        return
    if rec.op == "REMOVE":
        _ident(rec.cred_id)
        if rec.kind != "" or rec.origins != () or rec.label != "" or rec.login_id != "":
            raise Refuse("BAD_RECORD")
        if rec.source != "" or rec.fields != 0:
            raise Refuse("BAD_RECORD")
        return
    if rec.op not in _OP_SET:
        raise Refuse("BAD_RECORD")
    _manager(rec.source)
    if rec.cred_id != "" or rec.kind != "" or rec.origins != () or rec.label != "":
        raise Refuse("BAD_RECORD")
    if rec.login_id != "" or rec.fields != 0:
        raise Refuse("BAD_RECORD")


def _check_chain(records: tuple[object, ...]) -> tuple[Record, ...]:
    if len(records) > POLICY_HISTORY:
        raise Refuse("CAP", str(POLICY_HISTORY))
    prev_digest = _GENESIS
    prev_stamp: int | None = None
    checked: list[Record] = []
    for index, raw in enumerate(records, start=1):
        rec = _as_record(raw)
        _record_shape(rec)
        _semantics(rec)
        _stamp(rec.stamp)
        if rec.seq != index:
            raise Refuse("CHAIN")
        if prev_stamp is not None and rec.stamp <= prev_stamp:
            raise Refuse("STALE")
        if not const_eq(rec.prev, prev_digest):
            raise Refuse("CHAIN")
        digest = _digest(_body(rec))
        if not const_eq(digest, rec.digest):
            raise Refuse("CHAIN")
        prev_digest = digest
        prev_stamp = rec.stamp
        checked.append(rec)
    return tuple(checked)


def store_plaintext(value: object) -> None:
    """Refuse plaintext. A raw key shape refuses as SECRET."""
    text = bound_text(value)
    if secret_shape(text):
        raise Refuse("SECRET")
    raise Refuse("PLAINTEXT")


class CredentialVault:
    """In-memory id gate. `resolve` returns the credential id, never the blob."""

    __slots__ = (
        "_applied",
        "_requested",
        "_clamped",
        "_session",
        "_detected",
        "_items",
        "_unlocked",
        "_disabled",
        "_records",
        "_last",
        "_seen",
    )

    _applied: int
    _requested: int
    _clamped: bool
    _session: Session
    _detected: frozenset[str]
    _items: dict[str, Item]
    _unlocked: set[str]
    _disabled: set[str]
    _records: list[Record]
    _last: int | None
    _seen: set[str]

    def __init__(
        self,
        session: object = None,
        *,
        cap: object = POLICY_CAP,
        detected: object = (),
    ) -> None:
        self._session = _session(session)
        self._applied, self._requested, self._clamped = _cap(cap)
        self._detected = _detected(detected)
        self._items = {}
        self._unlocked = set()
        self._disabled = set()
        self._records = []
        self._last = None
        self._seen = set()

    @property
    def cap_note(self) -> CapNote:
        return CapNote(
            applied=self._applied,
            requested=self._requested,
            clamped=self._clamped,
        )

    @property
    def session(self) -> str:
        return self._session

    def records(self) -> tuple[Record, ...]:
        return tuple(self._records)

    def list_ids(self) -> tuple[str, ...]:
        """Sorted credential ids. No labels, origins, or blobs."""
        return tuple(sorted(self._items))

    def snapshot(self) -> Snapshot:
        keys = tuple(sorted(self._items))
        items = tuple(self._items[key] for key in keys)
        return Snapshot(
            schema=SCHEMA,
            session=self._session,
            cap=self.cap_note,
            ids=tuple(item.cred_id for item in items),
            items=items,
            unlocked=tuple(sorted(self._unlocked)),
            disabled=tuple(sorted(self._disabled)),
            records=self.records(),
        )

    def put(
        self,
        cred_id: object = None,
        origins: object = None,
        *,
        kind: object = None,
        label: object = None,
        stamp: object = None,
        login_id: object = "",
        source: object = "local",
        fields: object = 1,
    ) -> Record:
        """Store a credential id bound to exact origins."""
        ident = _ident(cred_id)
        origin_v = _origins(origins)
        kind_v = _kind(kind)
        label_v = _label(label)
        login_v = _login(login_id)
        source_v = _source(source)
        fields_v = _fields(fields)
        stamp_v = _stamp(stamp)
        self._source_ok(source_v)
        self._write_stamp(stamp_v)
        if ident in self._items:
            raise Refuse("DUPLICATE")
        if len(self._items) >= self._applied:
            raise Refuse("CAP", str(self._applied))
        rec = self._seal(
            "PUT",
            cred_id=ident,
            kind=kind_v,
            origins=origin_v,
            label=label_v,
            login_id=login_v,
            source=source_v,
            fields=fields_v,
            stamp=stamp_v,
        )
        self._apply(rec)
        return rec

    def remove(self, cred_id: object = None, *, stamp: object = None) -> Record:
        ident = _ident(cred_id)
        stamp_v = _stamp(stamp)
        self._write_stamp(stamp_v)
        if self._lookup(ident) is None:
            raise Refuse("UNKNOWN")
        rec = self._seal(
            "REMOVE",
            cred_id=ident,
            kind="",
            origins=(),
            label="",
            login_id="",
            source="",
            fields=0,
            stamp=stamp_v,
        )
        self._apply(rec)
        return rec

    def unlock(self, source: object = None, *, stamp: object = None) -> Record:
        """Record a human unlock. Headless sessions cannot answer."""
        name = _manager(source)
        stamp_v = _stamp(stamp)
        if self._session == "headless":
            raise Refuse("HEADLESS")
        if name not in self._detected:
            raise Refuse("BAD_SOURCE")
        if name in self._disabled:
            raise Refuse("DISABLED")
        if name in self._unlocked:
            raise Refuse("REPLAY")
        self._write_stamp(stamp_v)
        rec = self._seal(
            "UNLOCK",
            cred_id="",
            kind="",
            origins=(),
            label="",
            login_id="",
            source=name,
            fields=0,
            stamp=stamp_v,
        )
        self._apply(rec)
        return rec

    def disable(self, source: object = None, *, stamp: object = None) -> Record:
        """Opt out of a detected manager. Local sealed logins stay."""
        name = _manager(source)
        stamp_v = _stamp(stamp)
        if name not in self._detected:
            raise Refuse("BAD_SOURCE")
        if name in self._disabled:
            raise Refuse("REPLAY")
        self._write_stamp(stamp_v)
        rec = self._seal(
            "DISABLE",
            cred_id="",
            kind="",
            origins=(),
            label="",
            login_id="",
            source=name,
            fields=0,
            stamp=stamp_v,
        )
        self._apply(rec)
        return rec

    def item(self, cred_id: object = None, *, stamp: object = None) -> Item:
        ident = _ident(cred_id)
        stamp_v = _stamp(stamp)
        self._read_stamp(stamp_v)
        found = self._lookup(ident)
        if found is None:
            raise Refuse("UNKNOWN")
        return found

    def resolve(
        self,
        cred_id: object = None,
        purpose: object = None,
        *,
        stamp: object = None,
        confirm: object = False,
    ) -> Resolution:
        """Return the id when `purpose` matches a stored origin exactly."""
        ident = _ident(cred_id)
        purpose_v = _origin(purpose)
        stamp_v = _stamp(stamp)
        confirm_v = _flag(confirm)
        self._read_stamp(stamp_v)
        found = self._lookup(ident)
        if found is None:
            if self._session == "headless":
                raise Refuse("PROMPT_UNAVAILABLE")
            raise Refuse("UNKNOWN")
        if not _purpose_hit(found, purpose_v):
            raise Refuse("PURPOSE")
        self._release(found)
        if found.kind == "card":
            if self._session == "headless":
                raise Refuse("HEADLESS")
            if not confirm_v:
                raise Refuse("NEED_CONFIRM")
        action: Action = "WAIT" if found.kind in _WAIT else "FILL"
        filled = 0 if action == "WAIT" else found.fields
        return Resolution(
            cred_id=ident,
            purpose=purpose_v,
            action=action,
            filled_fields=filled,
            kind=found.kind,
        )

    def select(
        self,
        purpose: object = None,
        budget: object = None,
        *,
        stamp: object = None,
    ) -> Selection:
        """Catalog one origin. Skip items that do not fit; keep later ones."""
        purpose_v = _origin(purpose)
        applied, requested, clamped = _budget(budget)
        stamp_v = _stamp(stamp)
        self._read_stamp(stamp_v)
        remaining = applied
        chosen: list[Item] = []
        skipped: list[str] = []
        for ident in sorted(self._items):
            found = self._items[ident]
            if not _purpose_hit(found, purpose_v):
                continue
            cost = found.weight()
            if cost > remaining:
                skipped.append(found.cred_id)
                continue
            chosen.append(found)
            remaining -= cost
        return Selection(
            purpose=purpose_v,
            applied_budget=applied,
            requested_budget=requested,
            clamped=clamped,
            items=tuple(chosen),
            skipped=tuple(skipped),
        )

    def mint(self, cred_id: object = None, *, stamp: object = None) -> None:
        """Refuse to mint a code. The seed stays in the sealed blob."""
        ident = _ident(cred_id)
        stamp_v = _stamp(stamp)
        self._read_stamp(stamp_v)
        found = self._lookup(ident)
        if found is None:
            raise Refuse("UNKNOWN")
        self._release(found)
        raise Refuse("SEALED")

    def reveal(self) -> None:
        """Refuse to open a sealed blob."""
        raise Refuse("SEALED")

    def store_plaintext(self, value: object) -> None:
        """Refuse plaintext. The vault has no secret field."""
        store_plaintext(value)

    def __repr__(self) -> str:
        return (
            f"CredentialVault(session={self._session!r}, cap={self._applied}, "
            f"clamped={self._clamped}, ids={tuple(sorted(self._items))!r})"
        )

    def _lookup(self, ident: str) -> Item | None:
        found = self._items.get(ident)
        if found is None or not const_eq(found.cred_id, ident):
            return None
        return found

    def _source_ok(self, source: str) -> None:
        if source == "local":
            return
        if source not in self._detected:
            raise Refuse("BAD_SOURCE")
        if source in self._disabled:
            raise Refuse("DISABLED")

    def _release(self, found: Item) -> None:
        if found.source == "local":
            return
        if found.source in self._disabled:
            raise Refuse("DISABLED")
        if self._session == "headless":
            raise Refuse("UNAVAILABLE")
        if found.source not in self._unlocked:
            raise Refuse("LOCKED")

    def _write_stamp(self, stamp: int) -> None:
        last = self._last
        if last is not None and stamp <= last:
            raise Refuse("STALE")

    def _read_stamp(self, stamp: int) -> None:
        last = self._last
        if last is not None and stamp < last:
            raise Refuse("STALE")

    def _seal(
        self,
        op: Op,
        *,
        cred_id: str,
        kind: str,
        origins: tuple[str, ...],
        label: str,
        login_id: str,
        source: str,
        fields: int,
        stamp: int,
    ) -> Record:
        if len(self._records) >= POLICY_HISTORY:
            raise Refuse("CAP", str(POLICY_HISTORY))
        seq = len(self._records) + 1
        prev = _GENESIS if not self._records else self._records[seq - 2].digest
        rec = Record(
            seq=seq,
            stamp=stamp,
            op=op,
            cred_id=cred_id,
            kind=kind,
            origins=origins,
            label=label,
            login_id=login_id,
            source=source,
            fields=fields,
            prev=prev,
            digest="",
        )
        digest = _digest(_body(rec))
        if digest in self._seen:
            raise Refuse("REPLAY")
        return Record(
            seq=seq,
            stamp=stamp,
            op=op,
            cred_id=cred_id,
            kind=kind,
            origins=origins,
            label=label,
            login_id=login_id,
            source=source,
            fields=fields,
            prev=prev,
            digest=digest,
        )

    def _apply(self, rec: Record) -> None:
        if rec.digest in self._seen:
            raise Refuse("REPLAY")
        if rec.op == "PUT":
            if rec.cred_id in self._items:
                raise Refuse("DUPLICATE")
            if len(self._items) >= self._applied:
                raise Refuse("CAP", str(self._applied))
            self._items[rec.cred_id] = Item(
                cred_id=rec.cred_id,
                kind=rec.kind,
                origins=rec.origins,
                label=rec.label,
                login_id=rec.login_id,
                source=rec.source,
                fields=rec.fields,
            )
        elif rec.op == "REMOVE":
            if rec.cred_id not in self._items:
                raise Refuse("UNKNOWN")
            del self._items[rec.cred_id]
        elif rec.op == "UNLOCK":
            if rec.source not in self._detected:
                raise Refuse("BAD_SOURCE")
            if rec.source in self._disabled:
                raise Refuse("DISABLED")
            if rec.source in self._unlocked:
                raise Refuse("REPLAY")
            self._unlocked.add(rec.source)
        elif rec.op == "DISABLE":
            if rec.source not in self._detected:
                raise Refuse("BAD_SOURCE")
            if rec.source in self._disabled:
                raise Refuse("REPLAY")
            self._disabled.add(rec.source)
            self._unlocked.discard(rec.source)
        else:
            raise Refuse("BAD_RECORD")
        self._records.append(rec)
        self._seen.add(rec.digest)
        self._last = rec.stamp


def rebuild(
    records: object = None,
    session: object = None,
    *,
    cap: object = POLICY_CAP,
    detected: object = (),
) -> CredentialVault:
    """Replay caller-supplied records into the same public snapshot."""
    if not isinstance(records, tuple):
        raise Refuse("NOT_TUPLE")
    checked = _check_chain(records)
    vault = CredentialVault(session, cap=cap, detected=detected)
    for rec in checked:
        vault._apply(rec)
    return vault


__all__ = [
    "FIELD_CAP",
    "POLICY_BUDGET",
    "POLICY_CAP",
    "POLICY_HISTORY",
    "POLICY_ORIGINS",
    "SCHEMA",
    "CapNote",
    "CredentialVault",
    "Item",
    "Record",
    "Resolution",
    "Selection",
    "Snapshot",
    "rebuild",
    "store_plaintext",
]
