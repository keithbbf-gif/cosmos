"""Curated user and memory notes. No disk write."""

from __future__ import annotations

import re
from dataclasses import dataclass

from cosmos_hermes import Refuse, bound_text, const_eq, secret_shape

SCHEMA = "cosmos-hermes-memory/1"
ENTRY_CAP = 40
HISTORY_CAP = 16
KEY_LIMIT = 64
TEXT_LIMIT = 2000
MEMORY_CHARS = 2200
USER_CHARS = 1375
_SNAPSHOT_LIMIT = 96_000

_SECTION_LIMITS: dict[str, int] = {
    "memory": MEMORY_CHARS,
    "user": USER_CHARS,
}
SECTIONS = frozenset(_SECTION_LIMITS)
_KEY_RE = re.compile(r"[a-z0-9][a-z0-9-]{0,63}")
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


def _cap(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("NOT_INT")
    if value < 1:
        raise Refuse("BAD_LIMIT")
    if value > ENTRY_CAP:
        return ENTRY_CAP
    return value


def _section_limit(section: str) -> int:
    limit = _SECTION_LIMITS.get(section)
    if limit is None:
        raise Refuse("BAD_SECTION")
    return limit


def _has_invisible(text: str) -> bool:
    return any(char in _INVISIBLE for char in text)


def _note_id(section: str, key: str) -> str:
    """Length-prefixed id. Section and key stay unambiguous without a split."""
    return f"{len(section)}:{section}:{key}"


def _classify(section: str, key: str) -> tuple[str, str, str]:
    if section not in SECTIONS:
        raise Refuse("BAD_SECTION")
    if key == "":
        raise Refuse("EMPTY")
    if _KEY_RE.fullmatch(key) is None:
        raise Refuse("BAD_KEY")
    return section, key, _note_id(section, key)


def _key_parts(section: object, key: object) -> tuple[str, str, str]:
    section_s = bound_text(section, TEXT_LIMIT)
    key_s = bound_text(key, KEY_LIMIT)
    if secret_shape(section_s) or secret_shape(key_s):
        raise Refuse("SECRET")
    if _has_invisible(section_s) or _has_invisible(key_s):
        raise Refuse("INVISIBLE")
    return _classify(section_s, key_s)


def _parts(
    section: object,
    key: object,
    text: object,
    history: object,
) -> tuple[str, str, str, tuple[str, ...], str]:
    section_s = bound_text(section, TEXT_LIMIT)
    key_s = bound_text(key, KEY_LIMIT)
    text_s = bound_text(text, TEXT_LIMIT)
    if not isinstance(history, tuple):
        raise Refuse("BAD_STORE")
    if len(history) > HISTORY_CAP:
        raise Refuse("OVER_HISTORY")
    prior: list[str] = []
    for item in history:
        prior.append(bound_text(item, TEXT_LIMIT))
    if secret_shape(section_s) or secret_shape(key_s) or secret_shape(text_s):
        raise Refuse("SECRET")
    for item in prior:
        if secret_shape(item):
            raise Refuse("SECRET")
    if _has_invisible(section_s) or _has_invisible(key_s) or _has_invisible(text_s):
        raise Refuse("INVISIBLE")
    for item in prior:
        if _has_invisible(item):
            raise Refuse("INVISIBLE")
    if text_s == "":
        raise Refuse("EMPTY")
    for item in prior:
        if item == "":
            raise Refuse("EMPTY")
    _section, _key, note_id = _classify(section_s, key_s)
    return section_s, key_s, text_s, tuple(prior), note_id


def _check_id(supplied: object, derived: str) -> None:
    if supplied == "":
        return
    shown = bound_text(supplied, TEXT_LIMIT)
    if secret_shape(shown):
        raise Refuse("SECRET")
    if not const_eq(shown, derived):
        raise Refuse("BAD_ID")


def _measure(rows: tuple[Entry, ...] | tuple[Record, ...]) -> None:
    seen: set[str] = set()
    totals: dict[str, int] = {"memory": 0, "user": 0}
    for item in rows:
        if item.note_id in seen:
            raise Refuse("DUP_ID")
        seen.add(item.note_id)
        limit = _section_limit(item.section)
        used = totals[item.section] + len(item.text)
        if used > limit:
            raise Refuse("OVER_CHARS", str(limit))
        totals[item.section] = used


@dataclass(frozen=True, slots=True)
class Entry:
    """One live note. `history` is prior text for this id, oldest first."""

    section: str
    key: str
    text: str
    history: tuple[str, ...] = ()
    note_id: str = ""

    def __post_init__(self) -> None:
        section, key, text, history, derived = _parts(
            self.section, self.key, self.text, self.history
        )
        _check_id(self.note_id, derived)
        object.__setattr__(self, "section", section)
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "text", text)
        object.__setattr__(self, "history", history)
        object.__setattr__(self, "note_id", derived)


@dataclass(frozen=True, slots=True)
class Record:
    """One row of `records()`. `note_id` must be the derived id."""

    note_id: str
    section: str
    key: str
    text: str
    history: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        section, key, text, history, derived = _parts(
            self.section, self.key, self.text, self.history
        )
        if self.note_id == "":
            raise Refuse("BAD_ID")
        _check_id(self.note_id, derived)
        object.__setattr__(self, "note_id", derived)
        object.__setattr__(self, "section", section)
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "text", text)
        object.__setattr__(self, "history", history)


@dataclass(frozen=True, slots=True)
class Memory:
    """Frozen notes plus the recorded cap. The cap never rises above 40."""

    entries: tuple[Entry, ...] = ()
    cap: int = ENTRY_CAP

    def __post_init__(self) -> None:
        cap = _cap(self.cap)
        entries = self.entries
        if not isinstance(entries, tuple):
            raise Refuse("BAD_STORE")
        if len(entries) > ENTRY_CAP:
            raise Refuse("OVER_COUNT")
        for item in entries:
            if not isinstance(item, Entry):
                raise Refuse("BAD_STORE")
        if len(entries) > cap:
            raise Refuse("OVER_COUNT")
        _measure(entries)
        object.__setattr__(self, "cap", cap)


@dataclass(frozen=True, slots=True)
class Records:
    """Cap plus rows. `rebuild` of this value reproduces the store."""

    cap: int
    rows: tuple[Record, ...] = ()

    def __post_init__(self) -> None:
        cap = _cap(self.cap)
        rows = self.rows
        if not isinstance(rows, tuple):
            raise Refuse("BAD_STORE")
        if len(rows) > ENTRY_CAP:
            raise Refuse("OVER_COUNT")
        for item in rows:
            if not isinstance(item, Record):
                raise Refuse("BAD_STORE")
        if len(rows) > cap:
            raise Refuse("OVER_COUNT")
        _measure(rows)
        object.__setattr__(self, "cap", cap)


@dataclass(frozen=True, slots=True)
class Snapshot:
    """Prompt block captured for one session. Later adds do not change it."""

    text: str
    count: int

    def __post_init__(self) -> None:
        text = bound_text(self.text, _SNAPSHOT_LIMIT)
        if secret_shape(text):
            raise Refuse("SECRET")
        if isinstance(self.count, bool) or not isinstance(self.count, int):
            raise Refuse("NOT_INT")
        if self.count < 0 or self.count > ENTRY_CAP:
            raise Refuse("BAD_LIMIT")
        object.__setattr__(self, "text", text)
        object.__setattr__(self, "count", self.count)


def _store(store: object) -> Memory:
    if not isinstance(store, Memory):
        raise Refuse("BAD_STORE")
    return store


def _seal(
    section: str,
    key: str,
    text: str,
    history: tuple[str, ...],
    note_id: str,
) -> Entry:
    """Pack fields that `_parts` already accepted. Public `Entry` still checks."""
    entry = object.__new__(Entry)
    object.__setattr__(entry, "section", section)
    object.__setattr__(entry, "key", key)
    object.__setattr__(entry, "text", text)
    object.__setattr__(entry, "history", history)
    object.__setattr__(entry, "note_id", note_id)
    return entry


def empty(requested_cap: object = ENTRY_CAP) -> Memory:
    """Return an empty store. A requested cap above 40 is recorded as 40."""
    return Memory((), _cap(requested_cap))


def add(store: object, section: object, key: object, text: object) -> Memory:
    """Insert `key` or replace it. The same text returns the same store."""
    current = _store(store)
    section_s, key_s, text_s, _, note_id = _parts(section, key, text, ())
    draft = _seal(section_s, key_s, text_s, (), note_id)
    by_id: dict[str, Entry] = {}
    used = 0
    for item in current.entries:
        by_id[item.note_id] = item
        if item.section == draft.section:
            used += len(item.text)
    match = by_id.get(draft.note_id)
    limit = _section_limit(draft.section)
    if match is not None:
        if const_eq(match.text, draft.text):
            return current
        if used - len(match.text) + len(draft.text) > limit:
            raise Refuse("OVER_CHARS", str(limit))
        prior = match.history + (match.text,)
        if len(prior) > HISTORY_CAP:
            raise Refuse("OVER_HISTORY")
        replacement = _seal(draft.section, draft.key, draft.text, prior, draft.note_id)
        updated = tuple(replacement if item is match else item for item in current.entries)
        return Memory(updated, current.cap)
    if len(current.entries) >= current.cap:
        raise Refuse("OVER_COUNT")
    if used + len(draft.text) > limit:
        raise Refuse("OVER_CHARS", str(limit))
    return Memory(current.entries + (draft,), current.cap)


def remove(store: object, section: object, key: object) -> Memory:
    """Drop one note by id. A missing id refuses. Writes nothing."""
    current = _store(store)
    note_id = _key_parts(section, key)[2]
    by_id = {item.note_id: item for item in current.entries}
    match = by_id.get(note_id)
    if match is None:
        raise Refuse("MISSING")
    kept = tuple(item for item in current.entries if item is not match)
    return Memory(kept, current.cap)


def records(store: object) -> Records:
    """Emit the cap and the current rows."""
    current = _store(store)
    rows = tuple(
        Record(item.note_id, item.section, item.key, item.text, item.history)
        for item in current.entries
    )
    return Records(current.cap, rows)


def rebuild(source: object) -> Memory:
    """Reproduce the store from `records(store)`."""
    if not isinstance(source, Records):
        raise Refuse("BAD_STORE")
    entries = tuple(
        Entry(row.section, row.key, row.text, row.history, row.note_id) for row in source.rows
    )
    return Memory(entries, source.cap)


def render(store: object) -> str:
    """Live prompt block. History stays out of the block."""
    current = _store(store)
    grouped: dict[str, list[str]] = {"memory": [], "user": []}
    totals: dict[str, int] = {"memory": 0, "user": 0}
    for item in current.entries:
        lines = grouped.get(item.section)
        if lines is None or item.section not in totals:
            raise Refuse("BAD_SECTION")
        lines.append(f"{item.key}: {item.text}")
        totals[item.section] += len(item.text)
    blocks: list[str] = []
    for section, title in (("memory", "MEMORY"), ("user", "USER")):
        limit = _section_limit(section)
        used = totals[section]
        pct = (used * 100) // limit
        blocks.append(f"{title} [{pct}% {used}/{limit}]\n" + "\n§\n".join(grouped[section]))
    return "\n\n".join(blocks)


def snapshot(store: object) -> Snapshot:
    """Freeze `render` for this session. Does not read a clock."""
    current = _store(store)
    return Snapshot(render(current), len(current.entries))


def nudge(store: object) -> str:
    """Tell a human to persist this store. Writes nothing."""
    current = _store(store)
    return (
        f"Persist {len(current.entries)} of {current.cap} curated memory entries by hand. "
        "This call writes nothing."
    )


__all__ = [
    "SCHEMA",
    "SECTIONS",
    "ENTRY_CAP",
    "HISTORY_CAP",
    "KEY_LIMIT",
    "TEXT_LIMIT",
    "MEMORY_CHARS",
    "USER_CHARS",
    "Entry",
    "Record",
    "Records",
    "Memory",
    "Snapshot",
    "empty",
    "add",
    "remove",
    "records",
    "rebuild",
    "render",
    "snapshot",
    "nudge",
]
