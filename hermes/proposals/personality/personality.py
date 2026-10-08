"""Soul text is the first block of the prefix. Empty persona text refuses."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from cosmos_hermes import Refuse, bound_text, const_eq, redact, secret_shape

SCHEMA = "cosmos-hermes-personality/1"
TOTAL_CAP = 8000
CATALOG_CAP = 32
NAME_LIMIT = 32
FALLBACK_SOUL = "You are the COSMOS assistant. Be direct. Match the reply to the ask."

_JOIN = "\n\n"
_CLEAR = frozenset({"none", "default", "neutral"})
_GUARD = re.compile(r"disable\s+approval|yolo|no\s+restrictions", re.IGNORECASE)
_NAME = re.compile(r"[a-z0-9][a-z0-9_-]{0,31}")
_HEX = frozenset("0123456789abcdef")
_INVISIBLE = frozenset(
    chr(code)
    for code in (
        0x7F,
        0x200B,
        0x200C,
        0x200D,
        0x200E,
        0x200F,
        0x2028,
        0x2029,
        0x202A,
        0x202B,
        0x202C,
        0x202D,
        0x202E,
        0x2060,
        0x2066,
        0x2067,
        0x2068,
        0x2069,
        0xFEFF,
    )
) | frozenset(chr(code) for code in range(0x00, 0x20) if code not in (0x09, 0x0A))
_BUILTIN_ROWS: tuple[tuple[str, str], ...] = (
    ("helpful", "Be a friendly general-purpose assistant. Stay useful and plain."),
    ("concise", "Be brief. Use the fewest words that stay accurate."),
    ("technical", "Be a precise technical expert. Name the limit and the mechanism."),
    ("creative", "Offer several distinct options, then pick one and say why."),
    ("teacher", "Teach with one short example, then one check question."),
    ("kawaii", "Warm and playful. A little sparkle is enough. Stay clear."),
    ("catgirl", "Light cat-like asides are fine. Keep the substance intact."),
    ("pirate", "Speak like a practical captain. Keep the technical facts straight."),
    ("shakespeare", "Use elevated prose. Do not hide the meaning under the flourish."),
    ("surfer", "Easygoing tone. The advice itself stays concrete."),
    ("noir", "Dry hard-boiled narration. Keep the facts colder than the mood."),
    ("uwu", "Very soft tone. Do not soften a warning into a joke."),
    ("philosopher", "Name the assumption, then the consequence. Keep it short."),
    ("hype", "Energetic wording. Do not invent results to sound excited."),
)
BUILTIN_NAMES: tuple[str, ...] = tuple(name for name, _text in _BUILTIN_ROWS)
_BUILTIN_SET = frozenset(BUILTIN_NAMES)


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _match_hash(supplied: object, digest: str) -> str:
    text = bound_text(supplied, 64)
    if len(text) != 64 or any(char not in _HEX for char in text) or not const_eq(text, digest):
        raise Refuse("HASH_MISMATCH")
    return digest


def _invisible(text: str) -> bool:
    return any(char in _INVISIBLE for char in text)


def _screen(value: object, *, allow_blank: bool) -> str:
    text = bound_text(value, TOTAL_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    if _invisible(text):
        raise Refuse("INVISIBLE")
    if _GUARD.search(text) is not None:
        raise Refuse("GUARD_ESCAPE")
    if text.strip() == "":
        if allow_blank:
            return ""
        raise Refuse("EMPTY")
    return text


def _load_builtins(rows: tuple[tuple[str, str], ...]) -> dict[str, str]:
    table: dict[str, str] = {}
    for name, text in rows:
        if name in table:
            raise Refuse("DUP_NAME")
        table[name] = _screen(text, allow_blank=False)
    return table


_BUILTIN: dict[str, str] = _load_builtins(_BUILTIN_ROWS)


def _label(value: object, *, allow_clear: bool) -> str:
    text = bound_text(value, NAME_LIMIT)
    if secret_shape(text):
        raise Refuse("SECRET")
    if _invisible(text):
        raise Refuse("INVISIBLE")
    if _GUARD.search(text) is not None:
        raise Refuse("GUARD_ESCAPE")
    canonical = text.strip().casefold()
    if canonical == "":
        raise Refuse("EMPTY")
    if _NAME.fullmatch(canonical) is None:
        raise Refuse("BAD_NAME")
    if canonical in _CLEAR:
        if allow_clear:
            return canonical
        raise Refuse("BAD_NAME")
    return canonical


def _cap(value: object) -> int:
    """Record the policy cap. A request above 8000 does not raise it."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("NOT_INT")
    if value < 1:
        raise Refuse("BAD_LIMIT")
    if value > TOTAL_CAP:
        return TOTAL_CAP
    return value


def _tail_is(text: str, token: str) -> bool:
    if len(text) < len(token):
        return False
    return text[-len(token) :].casefold() == token


def _head_is(text: str, token: str) -> bool:
    if len(text) < len(token):
        return False
    return text[: len(token)].casefold() == token


def _crosses(soul: str, style: str) -> bool:
    left = soul.rstrip()
    right = style.lstrip()
    if _tail_is(left, "disable") and _head_is(right, "approval"):
        return True
    return _tail_is(left, "no") and _head_is(right, "restrictions")


def _fit(soul_text: str, style_text: str, cap: int) -> None:
    if style_text != "" and _crosses(soul_text, style_text):
        raise Refuse("GUARD_ESCAPE")
    extra = 0 if style_text == "" else len(_JOIN) + len(style_text)
    if len(soul_text) + extra > cap:
        raise Refuse("OVERSIZE", str(cap))


def _render(soul_text: str, style_text: str) -> str:
    if style_text == "":
        return soul_text
    return soul_text + _JOIN + style_text


def _resolve(overlay: dict[str, str], name: str) -> str | None:
    found = overlay.get(name)
    if found is not None:
        return found
    return _BUILTIN.get(name)


def _stored_pair(name: object, text: object, overlay: dict[str, str]) -> tuple[str, str]:
    style = _screen(text, allow_blank=True)
    if name == "":
        if style != "":
            raise Refuse("BAD_PRESET")
        return "", ""
    label = _label(name, allow_clear=False)
    if style == "":
        raise Refuse("EMPTY")
    expected = _resolve(overlay, label)
    if expected is not None and expected != style:
        raise Refuse("BAD_PRESET")
    return label, style


@dataclass(frozen=True, slots=True)
class Preset:
    """One named overlay. Clear-names are commands, not presets."""

    name: str
    text: str

    def __post_init__(self) -> None:
        name = _label(self.name, allow_clear=False)
        text = _screen(self.text, allow_blank=False)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "text", text)

    def __repr__(self) -> str:
        return f"Preset(name={self.name!r}, text={redact(self.text)!r})"


def _seal_preset(name: str, text: str) -> Preset:
    """Pack a name and style line that already passed the gate."""
    preset = object.__new__(Preset)
    object.__setattr__(preset, "name", name)
    object.__setattr__(preset, "text", text)
    return preset


def _catalog(value: object) -> tuple[Preset, ...]:
    if not isinstance(value, tuple):
        raise Refuse("BAD_PRESET")
    if len(value) > CATALOG_CAP:
        raise Refuse("CATALOG_CAP")
    items: list[Preset] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, Preset):
            raise Refuse("BAD_PRESET")
        if item.name in seen:
            raise Refuse("DUP_NAME")
        seen.add(item.name)
        items.append(item)
    return tuple(items)


def _preset_map(items: tuple[Preset, ...]) -> dict[str, str]:
    return {item.name: item.text for item in items}


def _activate(preset: object, items: tuple[Preset, ...]) -> tuple[str, str]:
    if isinstance(preset, Preset):
        return preset.name, preset.text
    label = _label(preset, allow_clear=True)
    if label in _CLEAR:
        return "", ""
    expected = _resolve(_preset_map(items), label)
    if expected is None:
        raise Refuse("UNKNOWN_PRESET")
    return label, expected


@dataclass(frozen=True, slots=True)
class Session:
    """Frozen soul plus the preset selected for this session."""

    schema: str
    soul_text: str
    soul_sha256: str
    preset_name: str
    preset_text: str
    catalog: tuple[Preset, ...] = ()
    cap: int = TOTAL_CAP

    def __post_init__(self) -> None:
        if not isinstance(self.schema, str) or self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        soul_text = _screen(self.soul_text, allow_blank=False)
        digest = _digest(soul_text)
        soul_sha256 = _match_hash(self.soul_sha256, digest)
        items = _catalog(self.catalog)
        preset_name, preset_text = _stored_pair(self.preset_name, self.preset_text, _preset_map(items))
        cap = _cap(self.cap)
        _fit(soul_text, preset_text, cap)
        object.__setattr__(self, "schema", SCHEMA)
        object.__setattr__(self, "soul_text", soul_text)
        object.__setattr__(self, "soul_sha256", soul_sha256)
        object.__setattr__(self, "preset_name", preset_name)
        object.__setattr__(self, "preset_text", preset_text)
        object.__setattr__(self, "catalog", items)
        object.__setattr__(self, "cap", cap)

    @property
    def soul_hash(self) -> str:
        return self.soul_sha256

    @property
    def selection(self) -> str:
        if self.preset_name == "":
            return "none"
        return self.preset_name

    def __repr__(self) -> str:
        return (
            "Session("
            f"schema={self.schema!r}, "
            f"soul_text={redact(self.soul_text)!r}, "
            f"soul_sha256={self.soul_sha256!r}, "
            f"preset_name={self.preset_name!r}, "
            f"preset_text={redact(self.preset_text)!r}, "
            f"catalog={self.catalog!r}, "
            f"cap={self.cap})"
        )


def _seal_session(
    soul_text: str,
    soul_sha256: str,
    preset_name: str,
    preset_text: str,
    catalog: tuple[Preset, ...],
    cap: int,
) -> Session:
    """Pack fields that the caller already screened. Public Session still checks."""
    session = object.__new__(Session)
    object.__setattr__(session, "schema", SCHEMA)
    object.__setattr__(session, "soul_text", soul_text)
    object.__setattr__(session, "soul_sha256", soul_sha256)
    object.__setattr__(session, "preset_name", preset_name)
    object.__setattr__(session, "preset_text", preset_text)
    object.__setattr__(session, "catalog", catalog)
    object.__setattr__(session, "cap", cap)
    return session


@dataclass(frozen=True, slots=True)
class Record:
    """One catalog row in a records bundle."""

    name: str
    text: str

    def __post_init__(self) -> None:
        name = _label(self.name, allow_clear=False)
        text = _screen(self.text, allow_blank=False)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "text", text)

    def __repr__(self) -> str:
        return f"Record(name={self.name!r}, text={redact(self.text)!r})"


def _seal_record(name: str, text: str) -> Record:
    """Pack a catalog row copied from a preset that already passed the gate."""
    row = object.__new__(Record)
    object.__setattr__(row, "name", name)
    object.__setattr__(row, "text", text)
    return row


def _record_rows(value: object) -> tuple[Record, ...]:
    if not isinstance(value, tuple):
        raise Refuse("BAD_PRESET")
    if len(value) > CATALOG_CAP:
        raise Refuse("CATALOG_CAP")
    items: list[Record] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, Record):
            raise Refuse("BAD_PRESET")
        if item.name in seen:
            raise Refuse("DUP_NAME")
        seen.add(item.name)
        items.append(item)
    return tuple(items)


def _record_map(items: tuple[Record, ...]) -> dict[str, str]:
    return {item.name: item.text for item in items}


@dataclass(frozen=True, slots=True)
class Records:
    """Snapshot of a session. rebuild returns an equal session."""

    schema: str
    soul_text: str
    soul_sha256: str
    preset_name: str
    preset_text: str
    catalog: tuple[Record, ...]
    cap: int

    def __post_init__(self) -> None:
        if not isinstance(self.schema, str) or self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        soul_text = _screen(self.soul_text, allow_blank=False)
        digest = _digest(soul_text)
        soul_sha256 = _match_hash(self.soul_sha256, digest)
        catalog = _record_rows(self.catalog)
        preset_name, preset_text = _stored_pair(
            self.preset_name, self.preset_text, _record_map(catalog)
        )
        cap = _cap(self.cap)
        _fit(soul_text, preset_text, cap)
        object.__setattr__(self, "schema", SCHEMA)
        object.__setattr__(self, "soul_text", soul_text)
        object.__setattr__(self, "soul_sha256", soul_sha256)
        object.__setattr__(self, "preset_name", preset_name)
        object.__setattr__(self, "preset_text", preset_text)
        object.__setattr__(self, "catalog", catalog)
        object.__setattr__(self, "cap", cap)

    def __repr__(self) -> str:
        return (
            "Records("
            f"schema={self.schema!r}, "
            f"soul_text={redact(self.soul_text)!r}, "
            f"soul_sha256={self.soul_sha256!r}, "
            f"preset_name={self.preset_name!r}, "
            f"preset_text={redact(self.preset_text)!r}, "
            f"catalog={self.catalog!r}, "
            f"cap={self.cap})"
        )


def _seal_records(
    soul_text: str,
    soul_sha256: str,
    preset_name: str,
    preset_text: str,
    catalog: tuple[Record, ...],
    cap: int,
) -> Records:
    """Pack a bundle copied from a session that already passed the gate."""
    bundle = object.__new__(Records)
    object.__setattr__(bundle, "schema", SCHEMA)
    object.__setattr__(bundle, "soul_text", soul_text)
    object.__setattr__(bundle, "soul_sha256", soul_sha256)
    object.__setattr__(bundle, "preset_name", preset_name)
    object.__setattr__(bundle, "preset_text", preset_text)
    object.__setattr__(bundle, "catalog", catalog)
    object.__setattr__(bundle, "cap", cap)
    return bundle


@dataclass(frozen=True, slots=True)
class Prefix:
    """Soul block first, then at most one style line."""

    schema: str
    soul_text: str
    style_text: str
    soul_sha256: str
    cap: int

    def __post_init__(self) -> None:
        if not isinstance(self.schema, str) or self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        soul_text = _screen(self.soul_text, allow_blank=False)
        style_text = _screen(self.style_text, allow_blank=True)
        digest = _digest(soul_text)
        soul_sha256 = _match_hash(self.soul_sha256, digest)
        cap = _cap(self.cap)
        _fit(soul_text, style_text, cap)
        object.__setattr__(self, "schema", SCHEMA)
        object.__setattr__(self, "soul_text", soul_text)
        object.__setattr__(self, "style_text", style_text)
        object.__setattr__(self, "soul_sha256", soul_sha256)
        object.__setattr__(self, "cap", cap)

    @property
    def text(self) -> str:
        return _render(self.soul_text, self.style_text)

    def __repr__(self) -> str:
        return (
            "Prefix("
            f"schema={self.schema!r}, "
            f"soul_text={redact(self.soul_text)!r}, "
            f"style_text={redact(self.style_text)!r}, "
            f"soul_sha256={self.soul_sha256!r}, "
            f"cap={self.cap})"
        )


def _seal_prefix(soul_text: str, style_text: str, soul_sha256: str, cap: int) -> Prefix:
    """Pack a prefix from a session that already passed the gate."""
    block = object.__new__(Prefix)
    object.__setattr__(block, "schema", SCHEMA)
    object.__setattr__(block, "soul_text", soul_text)
    object.__setattr__(block, "style_text", style_text)
    object.__setattr__(block, "soul_sha256", soul_sha256)
    object.__setattr__(block, "cap", cap)
    return block


def _as_session(value: object) -> Session:
    if not isinstance(value, Session):
        raise Refuse("BAD_SESSION")
    return value


def assemble(soul: object, preset: object) -> str:
    """Put soul text first, then one style line. Names are not resolved here."""
    soul_text = _screen(soul, allow_blank=False)
    style_text = _screen(preset, allow_blank=True)
    _fit(soul_text, style_text, TOTAL_CAP)
    return _render(soul_text, style_text)


def open_session(
    soul: object,
    preset: object = "none",
    catalog: object = (),
    requested_cap: object = TOTAL_CAP,
) -> Session:
    """Freeze a soul hash and one preset. A cap above 8000 is recorded as 8000."""
    soul_text = _screen(soul, allow_blank=False)
    items = _catalog(catalog)
    preset_name, preset_text = _activate(preset, items)
    cap = _cap(requested_cap)
    _fit(soul_text, preset_text, cap)
    return _seal_session(soul_text, _digest(soul_text), preset_name, preset_text, items, cap)


def swap_preset(session: object, preset: object) -> Session:
    """Replace the session preset. The soul sha256 stays the same."""
    current = _as_session(session)
    preset_name, preset_text = _activate(preset, current.catalog)
    _fit(current.soul_text, preset_text, current.cap)
    return _seal_session(
        current.soul_text,
        current.soul_sha256,
        preset_name,
        preset_text,
        current.catalog,
        current.cap,
    )


def prompt(session: object) -> str:
    """Return the prefix string. Soul text is the first block."""
    current = _as_session(session)
    return _render(current.soul_text, current.preset_text)


def prefix(session: object) -> Prefix:
    """Freeze that prefix. Rebuilding the session reproduces it."""
    current = _as_session(session)
    return _seal_prefix(current.soul_text, current.preset_text, current.soul_sha256, current.cap)


def list_presets(session: object) -> tuple[str, ...]:
    """List none, the built-ins, then catalog-only names, in that order."""
    current = _as_session(session)
    extra = tuple(item.name for item in current.catalog if item.name not in _BUILTIN_SET)
    return ("none",) + BUILTIN_NAMES + extra


def records(session: object) -> Records:
    """Emit the session bundle that rebuild accepts."""
    current = _as_session(session)
    rows = tuple(_seal_record(item.name, item.text) for item in current.catalog)
    return _seal_records(
        current.soul_text,
        current.soul_sha256,
        current.preset_name,
        current.preset_text,
        rows,
        current.cap,
    )


def rebuild(source: object) -> Session:
    """Return the session those records describe."""
    if not isinstance(source, Records):
        raise Refuse("BAD_SESSION")
    items = tuple(_seal_preset(row.name, row.text) for row in source.catalog)
    return _seal_session(
        source.soul_text,
        source.soul_sha256,
        source.preset_name,
        source.preset_text,
        items,
        source.cap,
    )


__all__ = [
    "BUILTIN_NAMES",
    "CATALOG_CAP",
    "FALLBACK_SOUL",
    "NAME_LIMIT",
    "SCHEMA",
    "TOTAL_CAP",
    "Prefix",
    "Preset",
    "Record",
    "Records",
    "Session",
    "assemble",
    "list_presets",
    "open_session",
    "prefix",
    "prompt",
    "rebuild",
    "records",
    "swap_preset",
]
