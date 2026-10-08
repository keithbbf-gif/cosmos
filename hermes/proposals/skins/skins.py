"""Terminal-safe skin text. Plain status lines, no terminal reads."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TypeVar

from cosmos_hermes import Refuse, bound_text, redact, secret_shape

SCHEMA = "cosmos-hermes-skins/1"
FIELD_CAP = 80
CUSTOM_CAP = 80
_POLICY_LIMIT = 32
_HOLD_NOTE = "Set display.skin by hand. This call writes nothing."
_ORIGINS = frozenset({"builtin", "custom"})
_POLICIES = frozenset({"plain"})
_SEGMENTS = ("label", "banner", "spinner", "session", "card", "note", "light")
_SEGMENT_SET = frozenset(_SEGMENTS)
# C0, DEL, C1, line separators, and bidi overrides. NUL is refused by bound_text.
_CONTROLS = frozenset(
    [chr(code) for code in range(0x20)]
    + [chr(0x7F)]
    + [chr(code) for code in range(0x80, 0xA0)]
    + list("\u2028\u2029\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069")
)
_DELETE = {ord(char): None for char in _CONTROLS}
_NAME_CHARS = frozenset("abcdefghijklmnopqrstuvwxyz0123456789-")
_BUILTIN_SPEC: tuple[tuple[str, str, str, str, str], ...] = (
    ("default", "Hermes Agent", "(._.)", "Hermes", "|"),
    ("ares", "Ares Agent", "forging", "Ares", "|"),
    ("mono", "Hermes Agent", "plain", "Hermes", "|"),
    ("slate", "Hermes Agent", "steady", "Hermes", "|"),
    ("daylight", "Hermes Agent", "clear", "Hermes", "|"),
    ("warm-lightmode", "Hermes Agent", "warm", "Hermes", "|"),
    ("poseidon", "Poseidon Agent", "charting", "Poseidon", "|"),
    ("sisyphus", "Sisyphus Agent", "pushing", "Sisyphus", "|"),
    ("charizard", "Charizard Agent", "banking", "Charizard", "|"),
)
_T = TypeVar("_T")


def _blank(kind: type[_T]) -> _T:
    return object.__new__(kind)


def _strip(text: str) -> str:
    return text.translate(_DELETE)


def _recorded_cap(cap: object) -> int:
    """Ignore a request above 80. Do not raise the policy cap."""
    if isinstance(cap, bool) or not isinstance(cap, int):
        raise Refuse("NOT_INT")
    if cap < 1:
        raise Refuse("BAD_LIMIT")
    if cap > FIELD_CAP:
        return FIELD_CAP
    return cap


def _good_name(text: str) -> bool:
    if text == "" or text[0] == "-" or text[-1] == "-":
        return False
    hyphen = False
    for char in text:
        if char == "-":
            if hyphen:
                return False
            hyphen = True
            continue
        hyphen = False
        if char not in _NAME_CHARS:
            return False
    return True


def _text_field(value: object, cap: int, *, allow_empty: bool) -> str:
    cleaned = _strip(bound_text(value, cap))
    if secret_shape(cleaned):
        raise Refuse("SECRET")
    if not allow_empty and cleaned == "":
        raise Refuse("BAD_SKIN")
    return cleaned


def _name(value: object, cap: int) -> str:
    raw = bound_text(value, cap)
    cleaned = _strip(raw)
    if secret_shape(cleaned):
        raise Refuse("SECRET")
    if cleaned != raw or not _good_name(cleaned):
        raise Refuse("BAD_NAME")
    return cleaned


def _seal(
    name: object,
    banner: object,
    spinner: object,
    label: object,
    prefix: object,
    cap: object,
    schema: object,
) -> Skin:
    if schema != SCHEMA:
        raise Refuse("BAD_SCHEMA")
    recorded = _recorded_cap(cap)
    row = _blank(Skin)
    object.__setattr__(row, "name", _name(name, recorded))
    object.__setattr__(row, "banner", _text_field(banner, recorded, allow_empty=False))
    object.__setattr__(row, "spinner", _text_field(spinner, recorded, allow_empty=True))
    object.__setattr__(row, "label", _text_field(label, recorded, allow_empty=True))
    object.__setattr__(row, "prefix", _text_field(prefix, recorded, allow_empty=True))
    object.__setattr__(row, "cap", recorded)
    object.__setattr__(row, "schema", SCHEMA)
    return row


@dataclass(frozen=True, slots=True)
class Skin:
    """One skin after control stripping. `cap` is the cap that was enforced."""

    name: str
    banner: str
    spinner: str
    label: str
    prefix: str
    cap: int = FIELD_CAP
    schema: str = SCHEMA

    def __post_init__(self) -> None:
        sealed = _seal(
            self.name,
            self.banner,
            self.spinner,
            self.label,
            self.prefix,
            self.cap,
            self.schema,
        )
        object.__setattr__(self, "name", sealed.name)
        object.__setattr__(self, "banner", sealed.banner)
        object.__setattr__(self, "spinner", sealed.spinner)
        object.__setattr__(self, "label", sealed.label)
        object.__setattr__(self, "prefix", sealed.prefix)
        object.__setattr__(self, "cap", sealed.cap)
        object.__setattr__(self, "schema", sealed.schema)

    def __repr__(self) -> str:
        return (
            "Skin("
            f"name={redact(self.name)!r}, "
            f"banner={redact(self.banner)!r}, "
            f"spinner={redact(self.spinner)!r}, "
            f"label={redact(self.label)!r}, "
            f"prefix={redact(self.prefix)!r}, "
            f"cap={self.cap}, schema={self.schema!r})"
        )


def define(
    name: object,
    banner: object,
    spinner: object,
    label: object,
    prefix: object,
    cap: object = FIELD_CAP,
) -> Skin:
    """Store one skin. Controls are removed. A higher cap is ignored."""
    return _seal(name, banner, spinner, label, prefix, cap, SCHEMA)


_BUILTINS: tuple[Skin, ...] = tuple(
    define(name, banner, spinner, label, prefix)
    for name, banner, spinner, label, prefix in _BUILTIN_SPEC
)
_BUILTIN_ORDER: tuple[str, ...] = tuple(row.name for row in _BUILTINS)
_BUILTIN_NAMES: frozenset[str] = frozenset(_BUILTIN_ORDER)
_BUILTIN_BY_NAME: dict[str, Skin] = {row.name: row for row in _BUILTINS}


@dataclass(frozen=True, slots=True)
class Pick:
    """Session skin. Custom wins over a built-in with the same name."""

    schema: str
    name: str
    banner: str
    spinner: str
    label: str
    prefix: str
    cap: int
    origin: str

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        if self.origin not in _ORIGINS:
            raise Refuse("BAD_ORIGIN")
        checked = _seal(
            self.name,
            self.banner,
            self.spinner,
            self.label,
            self.prefix,
            self.cap,
            SCHEMA,
        )
        object.__setattr__(self, "schema", SCHEMA)
        object.__setattr__(self, "name", checked.name)
        object.__setattr__(self, "banner", checked.banner)
        object.__setattr__(self, "spinner", checked.spinner)
        object.__setattr__(self, "label", checked.label)
        object.__setattr__(self, "prefix", checked.prefix)
        object.__setattr__(self, "cap", checked.cap)

    def __repr__(self) -> str:
        return (
            "Pick("
            f"schema={self.schema!r}, name={redact(self.name)!r}, "
            f"banner={redact(self.banner)!r}, spinner={redact(self.spinner)!r}, "
            f"label={redact(self.label)!r}, prefix={redact(self.prefix)!r}, "
            f"cap={self.cap}, origin={self.origin!r})"
        )


def _copy_pick(row: Skin, origin: str) -> Pick:
    if origin not in _ORIGINS:
        raise Refuse("BAD_ORIGIN")
    picked = _blank(Pick)
    object.__setattr__(picked, "schema", SCHEMA)
    object.__setattr__(picked, "name", row.name)
    object.__setattr__(picked, "banner", row.banner)
    object.__setattr__(picked, "spinner", row.spinner)
    object.__setattr__(picked, "label", row.label)
    object.__setattr__(picked, "prefix", row.prefix)
    object.__setattr__(picked, "cap", row.cap)
    object.__setattr__(picked, "origin", origin)
    return picked


@dataclass(frozen=True, slots=True)
class Catalog:
    """Built-in names, then custom-only names. `cap` is the field policy."""

    schema: str
    names: tuple[str, ...]
    cap: int

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        if isinstance(self.cap, bool) or not isinstance(self.cap, int):
            raise Refuse("NOT_INT")
        if self.cap != FIELD_CAP:
            raise Refuse("BAD_LIMIT")
        if isinstance(self.names, (str, bytes)) or not isinstance(self.names, tuple):
            raise Refuse("BAD_SKIN")
        width = len(_BUILTIN_ORDER)
        if self.names[:width] != _BUILTIN_ORDER:
            raise Refuse("BAD_SKIN")
        seen = set(_BUILTIN_NAMES)
        for name in self.names[width:]:
            if name in seen:
                raise Refuse("DUPLICATE")
            _name(name, FIELD_CAP)
            seen.add(name)

    def __repr__(self) -> str:
        shown = ", ".join(repr(redact(name)) for name in self.names)
        return f"Catalog(schema={self.schema!r}, names=({shown}), cap={self.cap})"


@dataclass(frozen=True, slots=True)
class Hold:
    """Human persist descriptor. This record writes nothing."""

    schema: str
    name: str
    cap: int
    note: str

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        recorded = _recorded_cap(self.cap)
        name = _name(self.name, recorded)
        if self.note != _HOLD_NOTE:
            raise Refuse("BAD_SKIN")
        object.__setattr__(self, "schema", SCHEMA)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "cap", recorded)

    def __repr__(self) -> str:
        return (
            "Hold("
            f"schema={self.schema!r}, name={redact(self.name)!r}, "
            f"cap={self.cap}, note={self.note!r})"
        )


@dataclass(frozen=True, slots=True)
class Snapshot:
    """Custom rows emitted by define. Built-ins stay on the module."""

    schema: str
    skins: tuple[Skin, ...]
    cap: int

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        if isinstance(self.cap, bool) or not isinstance(self.cap, int):
            raise Refuse("NOT_INT")
        if self.cap != FIELD_CAP:
            raise Refuse("BAD_LIMIT")
        if isinstance(self.skins, (str, bytes)) or not isinstance(self.skins, tuple):
            raise Refuse("BAD_SKIN")
        if len(self.skins) > CUSTOM_CAP:
            raise Refuse("OVER_COUNT")
        seen: set[str] = set()
        for item in self.skins:
            if type(item) is not Skin:
                raise Refuse("BAD_SKIN")
            if item.name in seen:
                raise Refuse("DUPLICATE")
            seen.add(item.name)


@dataclass(frozen=True, slots=True)
class Status:
    """One plain status line. `skipped` names segments that did not fit."""

    schema: str
    name: str
    line: str
    policy: str
    cap: int
    skipped: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        policy = bound_text(self.policy, _POLICY_LIMIT)
        if policy not in _POLICIES:
            raise Refuse("BAD_POLICY")
        recorded = _recorded_cap(self.cap)
        skipped = _skipped(self.skipped)
        name = _name(self.name, recorded)
        line = bound_text(self.line, recorded)
        if line == "" or _strip(line) != line:
            raise Refuse("BAD_SKIN")
        if secret_shape(line):
            raise Refuse("SECRET")
        object.__setattr__(self, "schema", SCHEMA)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "line", line)
        object.__setattr__(self, "policy", policy)
        object.__setattr__(self, "cap", recorded)
        object.__setattr__(self, "skipped", skipped)

    def __repr__(self) -> str:
        return (
            "Status("
            f"schema={self.schema!r}, name={redact(self.name)!r}, "
            f"line={redact(self.line)!r}, policy={self.policy!r}, "
            f"cap={self.cap}, skipped={self.skipped!r})"
        )


def _skipped(value: object) -> tuple[str, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, tuple):
        raise Refuse("BAD_SKIN")
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str) or item not in _SEGMENT_SET or item in seen:
            raise Refuse("BAD_SKIN")
        seen.add(item)
    return value


def builtin_skins() -> tuple[Skin, ...]:
    """Return the nine built-in skins in documented order."""
    return _BUILTINS


def _custom_rows(custom: object) -> tuple[tuple[Skin, ...], dict[str, Skin]]:
    if isinstance(custom, (str, bytes)) or not isinstance(custom, Sequence):
        raise Refuse("BAD_SKIN")
    if len(custom) > CUSTOM_CAP:
        raise Refuse("OVER_COUNT")
    rows: list[Skin] = []
    indexed: dict[str, Skin] = {}
    for item in custom:
        if len(rows) >= CUSTOM_CAP:
            raise Refuse("OVER_COUNT")
        if type(item) is not Skin:
            raise Refuse("BAD_SKIN")
        if item.name in indexed:
            raise Refuse("DUPLICATE")
        indexed[item.name] = item
        rows.append(item)
    return tuple(rows), indexed


def _catalog_names(rows: tuple[Skin, ...]) -> tuple[str, ...]:
    names = list(_BUILTIN_ORDER)
    seen = set(_BUILTIN_NAMES)
    for row in rows:
        if row.name not in seen:
            seen.add(row.name)
            names.append(row.name)
    return tuple(names)


def _new_catalog(names: tuple[str, ...]) -> Catalog:
    listed = _blank(Catalog)
    object.__setattr__(listed, "schema", SCHEMA)
    object.__setattr__(listed, "names", names)
    object.__setattr__(listed, "cap", FIELD_CAP)
    return listed


def catalog(custom: object = ()) -> Catalog:
    """List built-in names, then custom names that do not replace a built-in."""
    rows, _indexed = _custom_rows(custom)
    return _new_catalog(_catalog_names(rows))


def pick(name: object, custom: object = ()) -> Pick:
    """Select a session skin. An unknown name is refused."""
    wanted = _name(name, FIELD_CAP)
    _rows, indexed = _custom_rows(custom)
    found = indexed.get(wanted)
    if found is not None:
        return _copy_pick(found, "custom")
    builtin = _BUILTIN_BY_NAME.get(wanted)
    if builtin is not None:
        return _copy_pick(builtin, "builtin")
    raise Refuse("UNKNOWN")


def hold(name: object, custom: object = ()) -> Hold:
    """Tell a human to set the default skin. Writes nothing."""
    chosen = pick(name, custom)
    kept = _blank(Hold)
    object.__setattr__(kept, "schema", SCHEMA)
    object.__setattr__(kept, "name", chosen.name)
    object.__setattr__(kept, "cap", chosen.cap)
    object.__setattr__(kept, "note", _HOLD_NOTE)
    return kept


def snapshot(custom: object = ()) -> Snapshot:
    """Freeze the custom rows the caller already defined."""
    rows, _indexed = _custom_rows(custom)
    snap = _blank(Snapshot)
    object.__setattr__(snap, "schema", SCHEMA)
    object.__setattr__(snap, "skins", rows)
    object.__setattr__(snap, "cap", FIELD_CAP)
    return snap


def rebuild(snap: object) -> Catalog:
    """Reproduce the catalog from a snapshot of emitted skins."""
    if type(snap) is not Snapshot:
        raise Refuse("BAD_SKIN")
    if snap.schema != SCHEMA:
        raise Refuse("BAD_SCHEMA")
    if snap.cap != FIELD_CAP:
        raise Refuse("BAD_LIMIT")
    return catalog(snap.skins)


def _pack(
    values: tuple[str, str, str, str, str, str, str],
    sep: str,
    cap: int,
) -> tuple[str, tuple[str, ...]]:
    if sep == "" or _strip(sep) != sep:
        raise Refuse("BAD_SKIN")
    chunks: list[str] = []
    skipped: list[str] = []
    used = 0
    for key, text in zip(_SEGMENTS, values, strict=True):
        if text == "":
            continue
        extra = len(text) if not chunks else len(sep) + len(text)
        if extra > cap - used:
            skipped.append(key)
            continue
        chunks.append(text)
        used += extra
    if not chunks:
        raise Refuse("BAD_SKIN")
    return sep.join(chunks), tuple(skipped)


def _new_status(
    name: str,
    line: str,
    policy: str,
    cap: int,
    skipped: tuple[str, ...],
) -> Status:
    shown = _blank(Status)
    object.__setattr__(shown, "schema", SCHEMA)
    object.__setattr__(shown, "name", name)
    object.__setattr__(shown, "line", line)
    object.__setattr__(shown, "policy", policy)
    object.__setattr__(shown, "cap", cap)
    object.__setattr__(shown, "skipped", skipped)
    return shown


def render(
    name: object,
    session: object,
    card: object,
    note: object,
    light: object,
    custom: object = (),
    policy: object = "plain",
    cap: object = FIELD_CAP,
) -> Status:
    """One status line. `plain` adds no ANSI. Unknown skins are refused."""
    policy_text = bound_text(policy, _POLICY_LIMIT)
    if policy_text not in _POLICIES:
        raise Refuse("BAD_POLICY")
    recorded = _recorded_cap(cap)
    session_text = _text_field(session, recorded, allow_empty=False)
    card_text = _text_field(card, recorded, allow_empty=False)
    note_text = _text_field(note, recorded, allow_empty=False)
    light_text = _text_field(light, recorded, allow_empty=False)
    chosen = pick(name, custom)
    sep = chosen.prefix if chosen.prefix != "" else " "
    line, skipped = _pack(
        (
            chosen.label,
            chosen.banner,
            chosen.spinner,
            session_text,
            card_text,
            note_text,
            light_text,
        ),
        sep,
        recorded,
    )
    if _strip(line) != line:
        raise Refuse("BAD_SKIN")
    if secret_shape(line):
        raise Refuse("SECRET")
    return _new_status(chosen.name, line, policy_text, recorded, skipped)


__all__ = [
    "CUSTOM_CAP",
    "FIELD_CAP",
    "SCHEMA",
    "Catalog",
    "Hold",
    "Pick",
    "Skin",
    "Snapshot",
    "Status",
    "builtin_skins",
    "catalog",
    "define",
    "hold",
    "pick",
    "rebuild",
    "render",
    "snapshot",
]
