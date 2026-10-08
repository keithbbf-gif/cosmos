"""Frozen UI catalogs. A missing key raises MISSING. No download."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Final, NoReturn, cast

from cosmos_hermes import Refuse, bound_text, const_eq, redact, secret_shape

SCHEMA: Final = "cosmos-hermes-language_packs/1"
LOCALE_CAP: Final = 32
TABLE_CAP: Final = 256
KEY_CAP: Final = 128
VALUE_CAP: Final = 4_000
ENDONYM_CAP: Final = 64
DEPTH_CAP: Final = 8
STEP_CAP: Final = 1
_LOCALE_LIMIT: Final = 16
_SCHEMA_LIMIT: Final = 80
_REFERENCE: Final = "en"

SURFACES: Final[frozenset[str]] = frozenset({"core", "tui", "desktop"})
LAYERS: Final[frozenset[str]] = frozenset({"plugin", "overlay", "bundled"})
_LAYER_RANK: Final[dict[str, int]] = {"bundled": 0, "overlay": 1, "plugin": 2}
_RESERVED: Final[frozenset[str]] = frozenset({"on", "off", "yes", "no"})
_STATUSES: Final[frozenset[str]] = frozenset({"HIT", "FALLBACK"})
_SOURCES: Final[frozenset[str]] = frozenset({"display", "env"})

_LOCALE_RE: Final = re.compile(r"^[a-z]{2}(-[A-Z]{2})?$")
_SEGMENT_RE: Final = re.compile(r"^[a-z][a-z0-9_]*$")
_NAMED_RE: Final = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_INDEX_RE: Final = re.compile(r"^[0-9]+$")

_Slot = tuple[str, str, str]


def _empty_names() -> frozenset[str]:
    return frozenset()


def _empty_index() -> dict[_Slot, Phrase]:
    return {}


def _empty_locales() -> dict[str, LocaleMeta]:
    return {}


def _schema(value: object) -> None:
    if type(value) is not str or len(value) > _SCHEMA_LIMIT or "\x00" in value:
        raise Refuse("BAD_SCHEMA")
    try:
        ok = const_eq(value, SCHEMA)
    except UnicodeEncodeError as err:
        raise Refuse("BAD_SCHEMA") from err
    if not ok:
        raise Refuse("BAD_SCHEMA")


def _recorded(value: object, policy: int) -> int:
    """Policy cap. A higher request is ignored and is not stored."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("BAD_LIMIT")
    if value > policy:
        return policy
    if value != policy:
        raise Refuse("BAD_LIMIT")
    return value


def _note_cap(requested: object, policy: int) -> None:
    if requested is None:
        return
    _recorded(requested, policy)


def _locale(value: object) -> str:
    text = bound_text(value, _LOCALE_LIMIT)
    if _LOCALE_RE.fullmatch(text) is None:
        raise Refuse("BAD_LOCALE")
    return text


def _endonym(value: object) -> str:
    text = bound_text(value, ENDONYM_CAP)
    if text == "":
        raise Refuse("EMPTY")
    if secret_shape(text):
        raise Refuse("SECRET")
    return text


def _surface(value: object) -> str:
    text = bound_text(value, KEY_CAP)
    if text not in SURFACES:
        raise Refuse("BAD_SURFACE")
    return text


def _layer(value: object) -> str:
    text = bound_text(value, KEY_CAP)
    if text not in LAYERS:
        raise Refuse("BAD_LAYER")
    return text


def _flag(value: object) -> bool:
    if type(value) is not bool:
        raise Refuse("BAD_FLAG")
    return value


def _dotted(value: object) -> str:
    text = bound_text(value, KEY_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    if text == "":
        raise Refuse("BAD_KEY")
    parts = text.split(".")
    if any(part == "" for part in parts):
        raise Refuse("BAD_KEY")
    for part in parts:
        if part in _RESERVED or _SEGMENT_RE.fullmatch(part) is None:
            raise Refuse("BAD_KEY")
    return text


def _value(value: object) -> str:
    if type(value) is not str:
        raise Refuse("NOT_TEXT")
    text = bound_text(value, VALUE_CAP)
    if text == "":
        raise Refuse("EMPTY")
    if secret_shape(text):
        raise Refuse("SECRET")
    return text


def _join(prefix: str, dotted: str) -> str:
    full = dotted if prefix == "" else f"{prefix}.{dotted}"
    if len(full) > KEY_CAP:
        raise Refuse("OVERSIZE", str(KEY_CAP))
    return full


def _names(text: str, surface: str) -> frozenset[str]:
    """Named placeholders on core. Positional placeholders on tui and desktop."""
    found: set[str] = set()
    index = 0
    length = len(text)
    pattern = _NAMED_RE if surface == "core" else _INDEX_RE
    while index < length:
        char = text[index]
        if char == "{":
            if index + 1 < length and text[index + 1] == "{":
                index += 2
                continue
            end = text.find("}", index + 1)
            if end < 0:
                raise Refuse("BAD_PLACEHOLDER")
            body = text[index + 1 : end]
            if pattern.fullmatch(body) is None:
                raise Refuse("BAD_PLACEHOLDER")
            found.add(body)
            index = end + 1
            continue
        if char == "}":
            if index + 1 < length and text[index + 1] == "}":
                index += 2
                continue
            raise Refuse("BAD_PLACEHOLDER")
        index += 1
    return frozenset(found)


def _flatten(table: object) -> tuple[tuple[str, str], ...]:
    if type(table) is not dict:
        raise Refuse("BAD_TABLE")
    found: dict[str, str] = {}

    def walk(node: dict[object, object], prefix: str, depth: int) -> None:
        if depth > DEPTH_CAP:
            raise Refuse("BAD_TABLE")
        if len(node) == 0:
            if prefix != "":
                raise Refuse("EMPTY")
            return
        for raw_key, raw_val in node.items():
            full = _join(prefix, _dotted(raw_key))
            if type(raw_val) is dict:
                walk(cast(dict[object, object], raw_val), full, depth + 1)
                continue
            if full in found:
                raise Refuse("DUPLICATE")
            found[full] = _value(raw_val)
            if len(found) > TABLE_CAP:
                raise Refuse("OVER_CAP", str(TABLE_CAP))

    walk(cast(dict[object, object], table), "", 1)
    return tuple(found.items())


def _winners(phrases: tuple[Phrase, ...]) -> dict[_Slot, Phrase]:
    chosen: dict[_Slot, Phrase] = {}
    rank_at: dict[_Slot, int] = {}
    for phrase in phrases:
        slot = (phrase.locale, phrase.surface, phrase.key)
        rank = _LAYER_RANK[phrase.layer]
        prev = rank_at.get(slot)
        if prev is None or rank >= prev:
            chosen[slot] = phrase
            rank_at[slot] = rank
    return chosen


def _agree(phrases: tuple[Phrase, ...], index: dict[_Slot, Phrase]) -> None:
    for phrase in phrases:
        if phrase.locale == _REFERENCE:
            continue
        english = index.get((_REFERENCE, phrase.surface, phrase.key))
        if english is None:
            continue
        if phrase.names != english.names:
            raise Refuse("BAD_PLACEHOLDER")


def _meta(book: Catalog, tag: str) -> LocaleMeta:
    found = book.locale_index.get(tag)
    if found is None:
        raise Refuse("BAD_LOCALE")
    return found


@dataclass(frozen=True, slots=True, repr=False)
class LocaleMeta:
    """One registered locale. `endonym` is the switcher label."""

    locale: str
    endonym: str
    rtl: bool

    def __post_init__(self) -> None:
        _locale(self.locale)
        _endonym(self.endonym)
        _flag(self.rtl)

    def __repr__(self) -> str:
        return (
            f"LocaleMeta(locale={self.locale!r}, endonym={redact(self.endonym)!r}, rtl={self.rtl!r})"
        )


@dataclass(frozen=True, slots=True, repr=False)
class Phrase:
    """One UI string on one surface and one layer."""

    locale: str
    key: str
    text: str
    surface: str
    layer: str
    names: frozenset[str] = field(default_factory=_empty_names, repr=False)

    def __post_init__(self) -> None:
        _locale(self.locale)
        _dotted(self.key)
        _value(self.text)
        _surface(self.surface)
        _layer(self.layer)
        object.__setattr__(self, "names", _names(self.text, self.surface))

    def __repr__(self) -> str:
        return (
            f"Phrase(locale={self.locale!r}, key={self.key!r}, surface={self.surface!r}, "
            f"layer={self.layer!r}, chars={len(self.text)})"
        )


@dataclass(frozen=True, slots=True, repr=False)
class Catalog:
    """Frozen projection of caller-supplied tables. Caps are the policy caps."""

    schema: str
    locales: tuple[LocaleMeta, ...]
    phrases: tuple[Phrase, ...]
    table_cap: int = TABLE_CAP
    locale_cap: int = LOCALE_CAP
    value_cap: int = VALUE_CAP
    index: dict[_Slot, Phrase] = field(default_factory=_empty_index, compare=False, repr=False)
    locale_index: dict[str, LocaleMeta] = field(
        default_factory=_empty_locales, compare=False, repr=False
    )

    def __post_init__(self) -> None:
        _schema(self.schema)
        object.__setattr__(self, "table_cap", _recorded(self.table_cap, TABLE_CAP))
        object.__setattr__(self, "locale_cap", _recorded(self.locale_cap, LOCALE_CAP))
        object.__setattr__(self, "value_cap", _recorded(self.value_cap, VALUE_CAP))
        if type(self.locales) is not tuple or type(self.phrases) is not tuple:
            raise Refuse("BAD_CATALOG")
        if len(self.locales) > self.locale_cap:
            raise Refuse("OVER_CAP", str(self.locale_cap))
        seen_locales: set[str] = set()
        for meta in self.locales:
            if type(meta) is not LocaleMeta:
                raise Refuse("BAD_CATALOG")
            if meta.locale in seen_locales:
                raise Refuse("DUPLICATE")
            seen_locales.add(meta.locale)
        seen_phrase: set[tuple[str, str, str, str]] = set()
        counts: dict[tuple[str, str], int] = {}
        for phrase in self.phrases:
            if type(phrase) is not Phrase:
                raise Refuse("BAD_CATALOG")
            if phrase.locale not in seen_locales:
                raise Refuse("BAD_CATALOG")
            ident = (phrase.locale, phrase.surface, phrase.layer, phrase.key)
            if ident in seen_phrase:
                raise Refuse("DUPLICATE")
            seen_phrase.add(ident)
            slot = (phrase.locale, phrase.surface)
            counts[slot] = counts.get(slot, 0) + 1
            if counts[slot] > self.table_cap:
                raise Refuse("OVER_CAP", str(self.table_cap))
        winners = _winners(self.phrases)
        object.__setattr__(self, "index", winners)
        object.__setattr__(self, "locale_index", {meta.locale: meta for meta in self.locales})
        _agree(self.phrases, winners)

    def __repr__(self) -> str:
        return (
            f"Catalog(schema={self.schema!r}, locales={len(self.locales)}, "
            f"phrases={len(self.phrases)}, table_cap={self.table_cap})"
        )


@dataclass(frozen=True, slots=True, repr=False)
class LookupHit:
    """One resolved string. A miss is `Refuse('MISSING')`, never an empty string."""

    locale: str
    key: str
    text: str
    status: str
    surface: str
    layer: str
    source: str
    step: int
    step_cap: int = STEP_CAP
    schema: str = SCHEMA

    def __post_init__(self) -> None:
        _schema(self.schema)
        object.__setattr__(self, "step_cap", _recorded(self.step_cap, STEP_CAP))
        _locale(self.locale)
        _dotted(self.key)
        _surface(self.surface)
        if self.status not in _STATUSES:
            raise Refuse("BAD_STATUS")
        _layer(self.layer)
        source = _locale(self.source)
        if type(self.step) is not int:
            raise Refuse("BAD_RECORD")
        direct = self.status == "HIT"
        if direct and (source != self.locale or self.step != 0):
            raise Refuse("BAD_RECORD")
        if not direct and (source == self.locale or self.step != 1):
            raise Refuse("BAD_RECORD")
        _value(self.text)
        _names(self.text, self.surface)

    def __repr__(self) -> str:
        return (
            f"LookupHit(locale={self.locale!r}, key={self.key!r}, status={self.status!r}, "
            f"surface={self.surface!r}, layer={self.layer!r}, source={self.source!r}, "
            f"step={self.step!r}, chars={len(self.text)})"
        )


@dataclass(frozen=True, slots=True, repr=False)
class LanguageChoice:
    """Descriptor for a later UI. `env` is the HERMES_LANGUAGE override."""

    schema: str
    locale: str
    source: str
    endonym: str
    rtl: bool

    def __post_init__(self) -> None:
        _schema(self.schema)
        _locale(self.locale)
        if self.source not in _SOURCES:
            raise Refuse("BAD_SOURCE")
        _endonym(self.endonym)
        _flag(self.rtl)

    def __repr__(self) -> str:
        return (
            f"LanguageChoice(locale={self.locale!r}, source={self.source!r}, "
            f"endonym={redact(self.endonym)!r}, rtl={self.rtl!r})"
        )


def _empty() -> Catalog:
    return Catalog(SCHEMA, (), ())


def _require_catalog(catalog: object) -> Catalog:
    if type(catalog) is not Catalog:
        raise Refuse("BAD_CATALOG")
    return catalog


def _hit(tag: str, token: str, face: str, phrase: Phrase, *, step: int) -> LookupHit:
    status = "HIT" if step == 0 else "FALLBACK"
    return LookupHit(tag, token, phrase.text, status, face, phrase.layer, phrase.locale, step, STEP_CAP, SCHEMA)


def add(
    locale: object,
    table: object,
    catalog: object = None,
    *,
    surface: object = "core",
    layer: object = "plugin",
    endonym: object = None,
    rtl: object = False,
    table_cap: object = None,
    locale_cap: object = None,
    value_cap: object = None,
) -> Catalog:
    """Record one partial table. A higher cap is ignored. The policy cap is stored."""
    tag = _locale(locale)
    face = _surface(surface)
    band = _layer(layer)
    flag = _flag(rtl)
    _note_cap(table_cap, TABLE_CAP)
    _note_cap(locale_cap, LOCALE_CAP)
    _note_cap(value_cap, VALUE_CAP)
    book = _empty() if catalog is None else _require_catalog(catalog)
    label = _endonym(tag if endonym is None else endonym)
    leaves = _flatten(table)
    fresh = tuple(Phrase(tag, key, text, face, band) for key, text in leaves)
    keys = {key for key, _text in leaves}
    kept = tuple(
        phrase
        for phrase in book.phrases
        if not (
            phrase.locale == tag
            and phrase.surface == face
            and phrase.layer == band
            and phrase.key in keys
        )
    )
    count = len(fresh)
    for phrase in kept:
        if phrase.locale == tag and phrase.surface == face:
            count += 1
    if count > TABLE_CAP:
        raise Refuse("OVER_CAP", str(TABLE_CAP))
    metas: list[LocaleMeta] = []
    replaced = False
    for meta in book.locales:
        if meta.locale == tag:
            metas.append(LocaleMeta(tag, label, flag))
            replaced = True
        else:
            metas.append(meta)
    if not replaced:
        if len(metas) >= LOCALE_CAP:
            raise Refuse("OVER_CAP", str(LOCALE_CAP))
        metas.append(LocaleMeta(tag, label, flag))
    return Catalog(SCHEMA, tuple(metas), kept + fresh, TABLE_CAP, LOCALE_CAP, VALUE_CAP)


def lookup(
    locale: object,
    key: object,
    catalog: object = None,
    *,
    surface: object = "core",
) -> LookupHit:
    """Resolve one key on one locale. Plugin beats overlay. Overlay beats bundled.

    A missing key raises MISSING. It does not return an empty string or the raw key.
    English is not substituted. Call `fallback` for one explicit step.
    """
    book = _empty() if catalog is None else _require_catalog(catalog)
    tag = _locale(locale)
    _meta(book, tag)
    face = _surface(surface)
    token = _dotted(key)
    phrase = book.index.get((tag, face, token))
    if phrase is None:
        raise Refuse("MISSING")
    return _hit(tag, token, face, phrase, step=0)


def fallback(
    locale: object,
    key: object,
    catalog: object,
    onto: object,
    *,
    surface: object = "core",
    step_cap: object = None,
) -> LookupHit:
    """One explicit step from `locale` onto `onto`. The hit records the source.

    A list or tuple is a chain and raises BAD_FALLBACK. The asked locale is used
    when it has the key. Otherwise `onto` is read once. A third locale is not read.
    """
    if isinstance(onto, (list, tuple)):
        raise Refuse("BAD_FALLBACK")
    _note_cap(step_cap, STEP_CAP)
    book = _require_catalog(catalog)
    tag = _locale(locale)
    other = _locale(onto)
    if tag == other:
        raise Refuse("BAD_FALLBACK")
    _meta(book, tag)
    _meta(book, other)
    face = _surface(surface)
    token = _dotted(key)
    primary = book.index.get((tag, face, token))
    if primary is not None:
        return _hit(tag, token, face, primary, step=0)
    phrase = book.index.get((other, face, token))
    if phrase is None:
        raise Refuse("MISSING")
    return _hit(tag, token, face, phrase, step=1)


def choose(locale: object, catalog: object, env: object = None) -> LanguageChoice:
    """Pick a registered locale. A non-empty env overrides display."""
    book = _require_catalog(catalog)
    if env is None or (type(env) is str and env == ""):
        tag = _locale(locale)
        source = "display"
    else:
        tag = _locale(env)
        source = "env"
    meta = _meta(book, tag)
    return LanguageChoice(SCHEMA, tag, source, meta.endonym, meta.rtl)


def languages(catalog: object) -> tuple[str, ...]:
    """Locales in the order they were first added."""
    book = _require_catalog(catalog)
    return tuple(meta.locale for meta in book.locales)


def rebuild(catalog: object) -> Catalog:
    """Replay locales and phrases. The result equals the public catalog."""
    book = _require_catalog(catalog)
    return Catalog(SCHEMA, book.locales, book.phrases, TABLE_CAP, LOCALE_CAP, VALUE_CAP)


def fetch(source: object = "") -> NoReturn:
    """Packs are not downloaded."""
    if source != "":
        if type(source) is not str:
            raise Refuse("NOT_TEXT")
        text = bound_text(source, VALUE_CAP)
        if secret_shape(text):
            raise Refuse("SECRET")
    raise Refuse("NO_FETCH")


__all__ = [
    "DEPTH_CAP",
    "ENDONYM_CAP",
    "KEY_CAP",
    "LAYERS",
    "LOCALE_CAP",
    "SCHEMA",
    "STEP_CAP",
    "SURFACES",
    "TABLE_CAP",
    "VALUE_CAP",
    "Catalog",
    "LanguageChoice",
    "LocaleMeta",
    "LookupHit",
    "Phrase",
    "add",
    "choose",
    "fallback",
    "fetch",
    "languages",
    "lookup",
    "rebuild",
]
