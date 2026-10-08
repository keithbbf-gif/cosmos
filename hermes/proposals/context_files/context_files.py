"""Pack project context and a soul note. Paths stay inside a PathJail.

This module reads files it is given. It does not walk parents, write, or spawn.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Literal

from cosmos_hermes import PathJail, Refuse, bound_text, const_eq, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-context_files/1"
FILE_CAP: Final[int] = 32_000
TOTAL_CAP: Final[int] = 64_000
BYTE_CAP: Final[int] = FILE_CAP * 4
MAX_ITEMS: Final[int] = 64
NAME_CAP: Final[int] = 64

PROJECT_PRIORITY: Final[tuple[str, ...]] = (
    ".hermes.md",
    "HERMES.md",
    "AGENTS.override.md",
    "AGENTS.md",
    "CLAUDE.md",
    ".cursorrules",
)
LEGAL_NAMES: Final[tuple[str, ...]] = PROJECT_PRIORITY + ("COSMOS.md", "SOUL.md")

_LEGAL: Final[frozenset[str]] = frozenset(LEGAL_NAMES)
_PROJECT_RANK: Final[dict[str, int]] = {
    name: index for index, name in enumerate(PROJECT_PRIORITY)
}
_MDC: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,40}\.mdc\Z")
_PHRASE: Final[re.Pattern[str]] = re.compile(
    r"ignore(?:\s+all)?\s+previous\s+instructions"
    r"|disregard\s+(?:your|the)\s+rules"
    r"|system\s+prompt\s+override"
    r"|do\s+not\s+tell\s+the\s+user"
    r"|don't\s+tell\s+the\s+user",
    re.IGNORECASE,
)
_HIDDEN_DIV: Final[re.Pattern[str]] = re.compile(r"display\s*:\s*none", re.IGNORECASE)
_HTML_COMMENT: Final[re.Pattern[str]] = re.compile(r"<!--")
_CURL_KEY: Final[re.Pattern[str]] = re.compile(
    r"curl\b.{0,120}\$(?:API_KEY|api_key)",
    re.IGNORECASE,
)
_SECRET_FILE: Final[re.Pattern[str]] = re.compile(
    r"\bcat\s+(?:\.env\b|credentials\b)",
    re.IGNORECASE,
)
_MARKS: Final[re.Pattern[str]] = re.compile(
    "[\u200b\u200c\u200d\u2060\ufeff\u202a-\u202e\u2066-\u2069]"
)
_SKIP_REASONS: Final[frozenset[str]] = frozenset(
    {"ILLEGAL_NAME", "EMPTY", "GUARD_ESCAPE", "SUPERSEDED"}
)
_CAP_LABELS: Final[frozenset[str]] = frozenset({"file_cap", "total_cap"})
_INTRO: Final[str] = (
    "# Project Context\n\n"
    "The following project context files have been loaded and should be followed:"
)

_Verdict = Literal["ok", "dropped"]


@dataclass(frozen=True, slots=True)
class IncludedFile:
    """One context file that was kept."""

    name: str
    text: str
    chars: int


@dataclass(frozen=True, slots=True)
class SkippedFile:
    """A pair left out for a reason other than the total budget."""

    name: str
    reason: str


@dataclass(frozen=True, slots=True)
class DroppedFile:
    """A chosen file the remaining total could not hold."""

    name: str
    reason: str


@dataclass(frozen=True, slots=True)
class ContextPack:
    """Prompt text plus the files that produced it."""

    schema: str
    files: tuple[IncludedFile, ...]
    skipped: tuple[SkippedFile, ...]
    dropped: tuple[DroppedFile, ...]
    prompt: str
    file_cap: int
    total_cap: int
    policy_file_cap: int
    policy_total_cap: int
    chars: int
    ignored_caps: tuple[str, ...]
    verdict: _Verdict


@dataclass(frozen=True, slots=True)
class _Claim:
    text: str


def _context_name(name: str) -> bool:
    return name in _LEGAL or _MDC.fullmatch(name) is not None


def _guarded(text: str) -> bool:
    if _PHRASE.search(text) is not None:
        return True
    if _HIDDEN_DIV.search(text) is not None:
        return True
    if _HTML_COMMENT.search(text) is not None:
        return True
    if _CURL_KEY.search(text) is not None:
        return True
    if _SECRET_FILE.search(text) is not None:
        return True
    return _MARKS.search(text) is not None


def _one_cap(requested: object, policy: int, label: str, ignored: list[str]) -> int:
    if requested is None:
        return policy
    if isinstance(requested, bool) or not isinstance(requested, int) or requested < 1:
        raise Refuse("BAD_LIMIT")
    if requested > policy:
        ignored.append(label)
        return policy
    return requested


def _caps(
    file_cap: object, total_cap: object
) -> tuple[int, int, tuple[str, ...]]:
    ignored: list[str] = []
    effective_file = _one_cap(file_cap, FILE_CAP, "file_cap", ignored)
    effective_total = _one_cap(total_cap, TOTAL_CAP, "total_cap", ignored)
    return effective_file, effective_total, tuple(ignored)


def _name(value: object) -> str:
    name = bound_text(value, NAME_CAP)
    if secret_shape(name):
        raise Refuse("SECRET_SHAPE")
    if ".." in name:
        raise Refuse("DOTDOT")
    if name == "" or name == "." or "/" in name or "\\" in name:
        raise Refuse("BAD_PATH")
    return name


def _body(value: object, file_cap: int, label: str) -> str:
    text = bound_text(value, file_cap)
    if secret_shape(text):
        raise Refuse("SECRET_SHAPE", label)
    return text


def _pairs(entries: object) -> list[tuple[object, object]]:
    if isinstance(entries, (str, bytes, bytearray)) or not isinstance(entries, (list, tuple)):
        raise Refuse("NOT_LIST")
    if len(entries) > MAX_ITEMS:
        raise Refuse("TOO_MANY", str(MAX_ITEMS))
    pairs: list[tuple[object, object]] = []
    for item in entries:
        if isinstance(item, (str, bytes, bytearray)) or not isinstance(item, (list, tuple)):
            raise Refuse("BAD_PAIR")
        if len(item) != 2:
            raise Refuse("BAD_PAIR")
        pairs.append((item[0], item[1]))
    return pairs


def _path_items(entries: object) -> list[object]:
    if isinstance(entries, (str, bytes, bytearray)) or not isinstance(entries, (list, tuple)):
        raise Refuse("NOT_LIST")
    if len(entries) > MAX_ITEMS:
        raise Refuse("TOO_MANY", str(MAX_ITEMS))
    items: list[object] = []
    for item in entries:
        if isinstance(item, (list, tuple)):
            raise Refuse("BAD_PAIR")
        items.append(item)
    return items


def _jail(jail: object) -> PathJail:
    if not isinstance(jail, PathJail):
        raise Refuse("BAD_JAIL")
    return jail


def _read_text(path: Path, file_cap: int, label: str) -> str:
    if not path.exists():
        raise Refuse("MISSING", label)
    if not path.is_file():
        raise Refuse("NOT_FILE", label)
    try:
        with path.open("rb") as handle:
            blob = handle.read(BYTE_CAP + 1)
    except OSError:
        raise Refuse("UNREADABLE", label) from None
    if len(blob) > BYTE_CAP:
        raise Refuse("OVERSIZE", str(BYTE_CAP))
    try:
        decoded = blob.decode("utf-8")
    except UnicodeDecodeError:
        raise Refuse("NOT_UTF8", label) from None
    text = bound_text(decoded, file_cap)
    if secret_shape(text):
        raise Refuse("SECRET_SHAPE", label)
    return text


def _one_path(held: PathJail, raw: object, file_cap: int) -> SkippedFile | tuple[str, str]:
    text_path = bound_text(raw)
    if secret_shape(text_path):
        raise Refuse("SECRET_SHAPE")
    resolved = held.contain(text_path)
    checked = bound_text(resolved.name, NAME_CAP)
    if secret_shape(checked):
        raise Refuse("SECRET_SHAPE")
    if not _context_name(checked):
        return SkippedFile(checked, "ILLEGAL_NAME")
    return checked, _read_text(resolved, file_cap, checked)


def _rank(name: str) -> tuple[int, str]:
    if name == "SOUL.md":
        return (3, "")
    if name == "COSMOS.md":
        return (2, "")
    project = _PROJECT_RANK.get(name)
    if project is not None:
        return (0, f"{project:02d}")
    return (1, name)


def _render(files: tuple[IncludedFile, ...]) -> str:
    parts: list[str] = []
    project_open = False
    for item in files:
        if item.name == "SOUL.md":
            if parts:
                parts.append("\n\n")
            parts.append(item.text)
            continue
        if not project_open:
            parts.append(_INTRO)
            parts.append(f"\n\n## {item.name}\n\n{item.text}")
            project_open = True
            continue
        parts.append(f"\n\n## {item.name}\n\n{item.text}")
    return "".join(parts)


def _take(name: str, text: str, chosen: list[tuple[str, str]], skipped: list[SkippedFile]) -> None:
    if text.strip() == "":
        skipped.append(SkippedFile(name, "EMPTY"))
        return
    if _guarded(text):
        skipped.append(SkippedFile(name, "GUARD_ESCAPE"))
        return
    chosen.append((name, text))


def _pack(
    pairs: list[tuple[str, str]],
    skipped: list[SkippedFile],
    file_cap: int,
    total_cap: int,
    ignored: tuple[str, ...],
) -> ContextPack:
    held: dict[str, _Claim] = {}
    for name, text in pairs:
        if not _context_name(name):
            skipped.append(SkippedFile(name, "ILLEGAL_NAME"))
            continue
        if name in held:
            raise Refuse("DUPLICATE", name)
        held[name] = _Claim(text)
    winner: str | None = None
    for legal in PROJECT_PRIORITY:
        if legal in held:
            winner = legal
            break
    chosen: list[tuple[str, str]] = []
    if winner is not None:
        _take(winner, held[winner].text, chosen, skipped)
        for legal in PROJECT_PRIORITY:
            if legal == winner or legal not in held:
                continue
            skipped.append(SkippedFile(legal, "SUPERSEDED"))
    mdc_names = sorted(name for name in held if _MDC.fullmatch(name) is not None)
    if winner is None:
        for name in mdc_names:
            _take(name, held[name].text, chosen, skipped)
    else:
        for name in mdc_names:
            skipped.append(SkippedFile(name, "SUPERSEDED"))
    cosmos = held.get("COSMOS.md")
    if cosmos is not None:
        _take("COSMOS.md", cosmos.text, chosen, skipped)
    soul = held.get("SOUL.md")
    if soul is not None:
        _take("SOUL.md", soul.text, chosen, skipped)
    included: list[IncludedFile] = []
    dropped: list[DroppedFile] = []
    used = 0
    for name, text in chosen:
        if used + len(text) > total_cap:
            dropped.append(DroppedFile(name, "OVERSIZE"))
            continue
        used += len(text)
        included.append(IncludedFile(name, text, len(text)))
    files = tuple(included)
    prompt = bound_text(_render(files))
    verdict: _Verdict = "dropped" if dropped else "ok"
    return ContextPack(
        schema=SCHEMA,
        files=files,
        skipped=tuple(skipped),
        dropped=tuple(dropped),
        prompt=prompt,
        file_cap=file_cap,
        total_cap=total_cap,
        policy_file_cap=FILE_CAP,
        policy_total_cap=TOTAL_CAP,
        chars=used,
        ignored_caps=ignored,
        verdict=verdict,
    )


def assemble(
    entries: object,
    *,
    file_cap: object = None,
    total_cap: object = None,
) -> ContextPack:
    """Pack caller-supplied `(name, text)` pairs. A higher cap is ignored.

    One project file wins, in `PROJECT_PRIORITY` order. `SOUL.md` and
    `COSMOS.md` stay beside that winner. A file past the file cap raises
    `OVERSIZE`. A file that does not fit the remaining total is skipped.
    """
    effective_file, effective_total, ignored = _caps(file_cap, total_cap)
    parsed: list[tuple[str, str]] = []
    for raw_name, raw_text in _pairs(entries):
        name = _name(raw_name)
        parsed.append((name, _body(raw_text, effective_file, name)))
    return _pack(parsed, [], effective_file, effective_total, ignored)


def load(
    jail: object,
    paths: object,
    *,
    file_cap: object = None,
    total_cap: object = None,
) -> ContextPack:
    """Read absolute paths inside `jail` and pack the context names.

    A path that leaves the grant, or a `..` segment, refuses before the read.
    """
    held = _jail(jail)
    effective_file, effective_total, ignored = _caps(file_cap, total_cap)
    skipped: list[SkippedFile] = []
    parsed: list[tuple[str, str]] = []
    for raw in _path_items(paths):
        found = _one_path(held, raw, effective_file)
        if isinstance(found, SkippedFile):
            skipped.append(found)
            continue
        parsed.append(found)
    return _pack(parsed, skipped, effective_file, effective_total, ignored)


def _cap_field(value: object, policy: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("BAD_PACK")
    if value < 1 or value > policy:
        raise Refuse("BAD_PACK")
    return value


def _check_ignored(labels: object, file_cap: int, total_cap: int) -> tuple[str, ...]:
    if not isinstance(labels, tuple):
        raise Refuse("BAD_PACK")
    seen: set[str] = set()
    clean: list[str] = []
    for label in labels:
        if not isinstance(label, str) or label not in _CAP_LABELS or label in seen:
            raise Refuse("BAD_PACK")
        seen.add(label)
        clean.append(label)
    if "file_cap" in seen and file_cap != FILE_CAP:
        raise Refuse("BAD_PACK")
    if "total_cap" in seen and total_cap != TOTAL_CAP:
        raise Refuse("BAD_PACK")
    return tuple(clean)


def _check_included(item: object, file_cap: int) -> IncludedFile:
    if not isinstance(item, IncludedFile):
        raise Refuse("BAD_PACK")
    name = bound_text(item.name, NAME_CAP)
    if secret_shape(name):
        raise Refuse("SECRET_SHAPE")
    if not _context_name(name):
        raise Refuse("BAD_PACK")
    text = bound_text(item.text, file_cap)
    if secret_shape(text):
        raise Refuse("SECRET_SHAPE", name)
    if _guarded(text):
        raise Refuse("BAD_PACK")
    if isinstance(item.chars, bool) or not isinstance(item.chars, int) or item.chars != len(text):
        raise Refuse("BAD_PACK")
    return IncludedFile(name, text, item.chars)


def _check_files(files: object, file_cap: int) -> tuple[IncludedFile, ...]:
    if not isinstance(files, tuple):
        raise Refuse("BAD_PACK")
    checked = tuple(_check_included(item, file_cap) for item in files)
    seen: set[str] = set()
    project = 0
    last_rank: tuple[int, str] | None = None
    for item in checked:
        if item.name in seen:
            raise Refuse("DUPLICATE", item.name)
        seen.add(item.name)
        if item.name in _PROJECT_RANK:
            project += 1
        rank = _rank(item.name)
        if last_rank is not None and rank < last_rank:
            raise Refuse("BAD_PACK")
        last_rank = rank
    if project > 1:
        raise Refuse("BAD_PACK")
    return checked


def _check_skipped(skipped: object) -> tuple[SkippedFile, ...]:
    if not isinstance(skipped, tuple):
        raise Refuse("BAD_PACK")
    clean: list[SkippedFile] = []
    for item in skipped:
        if not isinstance(item, SkippedFile):
            raise Refuse("BAD_PACK")
        name = bound_text(item.name, NAME_CAP)
        if secret_shape(name):
            raise Refuse("SECRET_SHAPE")
        if item.reason not in _SKIP_REASONS:
            raise Refuse("BAD_PACK")
        clean.append(SkippedFile(name, item.reason))
    return tuple(clean)


def _check_dropped(dropped: object) -> tuple[DroppedFile, ...]:
    if not isinstance(dropped, tuple):
        raise Refuse("BAD_PACK")
    clean: list[DroppedFile] = []
    for item in dropped:
        if not isinstance(item, DroppedFile):
            raise Refuse("BAD_PACK")
        name = bound_text(item.name, NAME_CAP)
        if secret_shape(name):
            raise Refuse("SECRET_SHAPE")
        if not _context_name(name) or item.reason != "OVERSIZE":
            raise Refuse("BAD_PACK")
        clean.append(DroppedFile(name, item.reason))
    return tuple(clean)


def rebuild(pack: object) -> ContextPack:
    """Return an equal pack when the recorded files reproduce the prompt."""
    if not isinstance(pack, ContextPack):
        raise Refuse("BAD_PACK")
    if not const_eq(pack.schema, SCHEMA):
        raise Refuse("BAD_SCHEMA")
    file_cap = _cap_field(pack.file_cap, FILE_CAP)
    total_cap = _cap_field(pack.total_cap, TOTAL_CAP)
    if pack.policy_file_cap != FILE_CAP or pack.policy_total_cap != TOTAL_CAP:
        raise Refuse("BAD_PACK")
    ignored = _check_ignored(pack.ignored_caps, file_cap, total_cap)
    files = _check_files(pack.files, file_cap)
    skipped = _check_skipped(pack.skipped)
    dropped = _check_dropped(pack.dropped)
    prompt = bound_text(_render(files))
    if not const_eq(prompt, pack.prompt):
        raise Refuse("BAD_PACK")
    chars = 0
    for item in files:
        chars += item.chars
        if chars > total_cap:
            raise Refuse("OVERSIZE", str(total_cap))
    if chars != pack.chars:
        raise Refuse("BAD_PACK")
    verdict: _Verdict = "dropped" if dropped else "ok"
    if pack.verdict != verdict:
        raise Refuse("BAD_PACK")
    return ContextPack(
        schema=SCHEMA,
        files=files,
        skipped=skipped,
        dropped=dropped,
        prompt=prompt,
        file_cap=file_cap,
        total_cap=total_cap,
        policy_file_cap=FILE_CAP,
        policy_total_cap=TOTAL_CAP,
        chars=chars,
        ignored_caps=ignored,
        verdict=verdict,
    )


__all__ = [
    "BYTE_CAP",
    "FILE_CAP",
    "LEGAL_NAMES",
    "MAX_ITEMS",
    "NAME_CAP",
    "PROJECT_PRIORITY",
    "SCHEMA",
    "TOTAL_CAP",
    "ContextPack",
    "DroppedFile",
    "IncludedFile",
    "SkippedFile",
    "assemble",
    "load",
    "rebuild",
]
