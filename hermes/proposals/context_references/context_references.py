"""Expand @file, @folder, @diff, and @url markers from caller-supplied text.

A URL becomes a fetch descriptor. This module does not perform network.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Final

from cosmos_hermes import Refuse, bound_int, bound_text, const_eq, redact, secret_shape

SCHEMA: Final = "cosmos-hermes-context_references/1"
POLICY_CAP: Final = 64_000
ENTRY_CAP: Final = 200
NAME_CAP: Final = 200
_CAP_FLOOR: Final = 1
_DECODE_PASSES: Final = 4
_PORT_DIGITS: Final = 5
_NEED_FETCH: Final = "NEED_FETCH"
_OVERSIZE: Final = "OVERSIZE"
_FILE: Final = "file:"
_FOLDER: Final = "folder:"
_URL: Final = "url:"
_FENCE: Final = "--- Attached Context ---"
_TRAILING: Final = frozenset(",.;!?")
_HEX: Final = frozenset("0123456789abcdefABCDEF")
_KINDS: Final = frozenset({"file", "folder", "diff", "url"})
_DRIVE: Final = re.compile(r"^[A-Za-z]:")
_FILE_SCHEME: Final = re.compile(r"^file:", re.IGNORECASE)
_HOST: Final = re.compile(
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)*"
)
_PATH: Final = re.compile(r"[A-Za-z0-9._~\-/?#&=%+;$,!*'():\[\]]+")


@dataclass(frozen=True, slots=True, repr=False)
class ContextRecord:
    """One expanded reference. URL records carry code NEED_FETCH and no page body."""

    kind: str
    name: str
    text: str
    code: str

    def __post_init__(self) -> None:
        if self.kind == "url":
            if self.name != "" or not const_eq(self.code, _NEED_FETCH):
                raise Refuse("BAD_REF")
            _seal_url(self.text)
            return
        if self.kind not in _KINDS or self.kind == "url" or self.code != "":
            raise Refuse("BAD_REF")
        if self.kind == "diff":
            if self.name != "":
                raise Refuse("BAD_NAME")
        else:
            _reject_bad_name(self.name)
        _seal_payload(self.text)

    def __repr__(self) -> str:
        if self.kind == "url":
            return f"ContextRecord(kind='url', code={self.code!r}, url={redact(self.text)!r})"
        return (
            f"ContextRecord(kind={self.kind!r}, name={redact(self.name)!r}, chars={len(self.text)})"
        )


@dataclass(frozen=True, slots=True, repr=False)
class FetchDescriptor:
    """A URL the DOM rail may fetch later. Construction does not open a socket."""

    url: str
    code: str = _NEED_FETCH

    def __post_init__(self) -> None:
        if not const_eq(self.code, _NEED_FETCH):
            raise Refuse("BAD_REF")
        _seal_url(self.url)

    def __repr__(self) -> str:
        return f"FetchDescriptor(code={self.code!r}, url={redact(self.url)!r})"


@dataclass(frozen=True, slots=True, repr=False)
class SkippedRef:
    """A reference left out because it did not fit the remaining payload budget."""

    kind: str
    name: str
    reason: str

    def __post_init__(self) -> None:
        if self.reason != _OVERSIZE:
            raise Refuse("BAD_REF")
        if self.kind == "url":
            _seal_url(self.name)
            return
        if self.kind == "diff":
            if self.name != "":
                raise Refuse("BAD_NAME")
            return
        if self.kind not in {"file", "folder"}:
            raise Refuse("BAD_REF")
        _reject_bad_name(self.name)

    def __repr__(self) -> str:
        shown = redact(self.name) if self.kind == "url" else self.name
        return f"SkippedRef(kind={self.kind!r}, name={shown!r}, reason={self.reason!r})"


@dataclass(frozen=True, slots=True, repr=False)
class ExpandedContext:
    """Rendered message plus the records that produced the attached section."""

    schema: str
    text: str
    records: tuple[ContextRecord, ...]
    cap: int
    skipped: tuple[SkippedRef, ...] = ()

    def __post_init__(self) -> None:
        if not const_eq(self.schema, SCHEMA):
            raise Refuse("BAD_REF")
        bound_int(self.cap, _CAP_FLOOR, POLICY_CAP)
        if not isinstance(self.text, str) or not isinstance(self.records, tuple):
            raise Refuse("BAD_REF")
        if not isinstance(self.skipped, tuple):
            raise Refuse("BAD_REF")
        if "\x00" in self.text:
            raise Refuse("NULL_BYTE")
        if len(self.records) + len(self.skipped) > ENTRY_CAP:
            raise Refuse("BAD_REF", "count")
        total = 0
        for record in self.records:
            if not isinstance(record, ContextRecord):
                raise Refuse("BAD_REF")
            total += len(record.text)
            if total > self.cap:
                raise Refuse("OVERSIZE", str(self.cap))
        for item in self.skipped:
            if not isinstance(item, SkippedRef):
                raise Refuse("BAD_REF")
        if secret_shape(self.text):
            raise Refuse("SECRET")

    def __repr__(self) -> str:
        return (
            f"ExpandedContext(schema={self.schema!r}, cap={self.cap}, "
            f"records={len(self.records)}, skipped={len(self.skipped)})"
        )


def expand(
    message: object,
    *,
    files: object = None,
    folders: object = None,
    diff: object = None,
    cap: object = None,
) -> ExpandedContext:
    """Expand context references. A URL is a NEED_FETCH descriptor and is not fetched."""
    raw = bound_text(message)
    if secret_shape(raw):
        raise Refuse("SECRET")
    effective = _resolve_cap(cap)
    file_map = _catalog(files, "files")
    folder_map = _catalog(folders, "folders")
    diff_text = _supplied_diff(diff)

    records: list[ContextRecord] = []
    skipped: list[SkippedRef] = []
    markers: list[str] = []
    spans: list[tuple[int, int]] = []
    used = 0
    index = 0
    length = len(raw)
    while True:
        start = raw.find("@", index)
        if start < 0:
            break
        stop = start + 1
        while stop < length and not raw[stop].isspace():
            stop += 1
        kind, arg, kept = _interpret(raw[start + 1 : stop])
        if len(records) + len(skipped) >= ENTRY_CAP:
            raise Refuse("BAD_REF", "count")
        spans.append((start, start + 1 + kept))
        if kind == "file":
            body = _lookup(file_map, arg)
            used = _keep(records, skipped, markers, "file", arg, body, effective, used)
        elif kind == "folder":
            body = _lookup(folder_map, arg)
            used = _keep(records, skipped, markers, "folder", arg, body, effective, used)
        elif kind == "diff":
            if diff_text is None:
                raise Refuse("MISSING", "diff")
            used = _keep(records, skipped, markers, "diff", "", diff_text, effective, used)
        else:
            used = _keep(records, skipped, markers, "url", "", arg, effective, used)
        index = stop

    inline = _stitch(raw, spans, markers)
    text = _attach(inline, records)
    return ExpandedContext(SCHEMA, text, tuple(records), effective, tuple(skipped))


def descriptors(expanded: object) -> tuple[FetchDescriptor, ...]:
    """Return NEED_FETCH descriptors in order. This does not perform network."""
    if not isinstance(expanded, ExpandedContext):
        raise Refuse("BAD_REF")
    found: list[FetchDescriptor] = []
    for record in expanded.records:
        if record.kind == "url":
            found.append(FetchDescriptor(record.text, record.code))
    return tuple(found)


def rebuild(expanded: object) -> ExpandedContext:
    """Re-project public state from the emitted records. A mismatched fence is STALE."""
    if not isinstance(expanded, ExpandedContext):
        raise Refuse("BAD_REF")
    suffix = _suffix(expanded.records)
    if suffix:
        if not expanded.text.endswith(suffix):
            raise Refuse("STALE")
        inline = expanded.text[: -len(suffix)]
    else:
        inline = expanded.text
    text = _attach(inline, list(expanded.records))
    if text != expanded.text:
        raise Refuse("STALE")
    return ExpandedContext(SCHEMA, text, expanded.records, expanded.cap, expanded.skipped)


def _resolve_cap(cap: object) -> int:
    if cap is None:
        return POLICY_CAP
    if isinstance(cap, bool) or not isinstance(cap, int):
        raise Refuse("NOT_INT")
    if cap < _CAP_FLOOR:
        raise Refuse("OUT_OF_RANGE", f"{_CAP_FLOOR}..{POLICY_CAP}")
    if cap > POLICY_CAP:
        return POLICY_CAP
    return cap


def _catalog(value: object, label: str) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise Refuse("BAD_CATALOG", label)
    if len(value) > ENTRY_CAP:
        raise Refuse("BAD_CATALOG", label)
    clean: dict[str, str] = {}
    for key, item in value.items():
        if not isinstance(key, str):
            raise Refuse("NOT_TEXT")
        name = _catalog_key(key)
        if name in clean:
            raise Refuse("BAD_CATALOG", "duplicate")
        clean[name] = _payload(item)
    return clean


def _catalog_key(key: str) -> str:
    canonical = unicodedata.normalize("NFKC", bound_text(key, NAME_CAP))
    if len(canonical) > NAME_CAP:
        raise Refuse("OVERSIZE", str(NAME_CAP))
    return _reject_bad_name(canonical)


def _payload(value: object) -> str:
    text = bound_text(value, POLICY_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    return text


def _supplied_diff(diff: object) -> str | None:
    if diff is None:
        return None
    return _payload(diff)


def _lookup(catalog: dict[str, str], name: str) -> str:
    if name not in catalog:
        raise Refuse("MISSING", name)
    return catalog[name]


def _keep(
    records: list[ContextRecord],
    skipped: list[SkippedRef],
    markers: list[str],
    kind: str,
    name: str,
    text: str,
    cap: int,
    used: int,
) -> int:
    if used + len(text) > cap:
        skipped.append(SkippedRef(kind, text if kind == "url" else name, _OVERSIZE))
        markers.append(_marker(kind, name, skipped=True))
        return used
    if kind == "url":
        records.append(ContextRecord("url", "", text, _NEED_FETCH))
    elif kind == "diff":
        records.append(ContextRecord("diff", "", text, ""))
    else:
        records.append(ContextRecord(kind, name, text, ""))
    markers.append(_marker(kind, name, skipped=False))
    return used + len(text)


def _interpret(raw_body: str) -> tuple[str, str, int]:
    original = bound_text(raw_body)
    if original == "":
        raise Refuse("BAD_REF")
    kept = len(_strip_tail(original))
    if kept == 0:
        raise Refuse("BAD_REF")
    canonical = unicodedata.normalize("NFKC", original)
    body = _strip_tail(canonical)
    if body == "":
        raise Refuse("BAD_REF")
    if body == "diff":
        return ("diff", "", kept)
    if body.startswith(_FILE):
        name = _name_from_token(canonical[len(_FILE) :])
        return ("file", name, kept)
    if body.startswith(_FOLDER):
        name = _name_from_token(canonical[len(_FOLDER) :])
        return ("folder", name, kept)
    if body.startswith(_URL):
        url = _url_from_token(canonical[len(_URL) :])
        return ("url", url, kept)
    if secret_shape(original) or secret_shape(canonical):
        raise Refuse("SECRET")
    raise Refuse("BAD_REF")


def _name_from_token(raw_name: str) -> str:
    canonical = unicodedata.normalize("NFKC", raw_name)
    stripped = _strip_tail(canonical)
    if secret_shape(canonical) or secret_shape(stripped):
        raise Refuse("SECRET")
    if not _layers_safe(canonical, url=False):
        raise Refuse("BAD_NAME")
    return _reject_bad_name(stripped)


def _url_from_token(raw_url: str) -> str:
    canonical = unicodedata.normalize("NFKC", raw_url)
    if secret_shape(canonical):
        raise Refuse("SECRET")
    if not _layers_safe(canonical, url=True):
        raise Refuse("BAD_REF")
    url = _strip_tail(canonical)
    if url != canonical and secret_shape(url):
        raise Refuse("SECRET")
    sealed = _seal_url(url)
    return sealed


def _reject_bad_name(name: str) -> str:
    checked = bound_text(name, NAME_CAP)
    if checked != unicodedata.normalize("NFKC", checked):
        raise Refuse("BAD_NAME")
    if secret_shape(checked):
        raise Refuse("SECRET")
    if not _layers_safe(checked, url=False):
        raise Refuse("BAD_NAME")
    return checked


def _seal_payload(text: str) -> str:
    checked = bound_text(text, POLICY_CAP)
    if secret_shape(checked):
        raise Refuse("SECRET")
    return checked


def _seal_url(url: str) -> str:
    checked = bound_text(url, POLICY_CAP)
    if checked != unicodedata.normalize("NFKC", checked):
        raise Refuse("BAD_REF")
    if secret_shape(checked):
        raise Refuse("SECRET")
    if not _layers_safe(checked, url=True) or not _http_shape(checked):
        raise Refuse("BAD_REF")
    return checked


def _layers_safe(value: str, *, url: bool) -> bool:
    if "%" not in value:
        return not _layer_bad(value, url=url)
    current = value
    for _ in range(_DECODE_PASSES):
        if _layer_bad(current, url=url):
            return False
        decoded = _percent_decode(current)
        if decoded is None or _layer_bad(decoded, url=url):
            return False
        if decoded == current:
            return True
        current = decoded
    return False


def _layer_bad(value: str, *, url: bool) -> bool:
    if ".." in value or "\\" in value or "\x00" in value:
        return True
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        return True
    if url:
        return "@" in value or _FILE_SCHEME.match(value) is not None
    if value == "" or value == "." or "/" in value or _DRIVE.match(value) is not None:
        return True
    return any(char.isspace() for char in value)


def _percent_decode(value: str) -> str | None:
    if "%" not in value:
        return value
    parts: list[str] = []
    index = 0
    length = len(value)
    while index < length:
        char = value[index]
        if char != "%":
            parts.append(char)
            index += 1
            continue
        if index + 2 >= length:
            return None
        pair = value[index + 1 : index + 3]
        if pair[0] not in _HEX or pair[1] not in _HEX:
            return None
        parts.append(chr(int(pair, 16)))
        index += 3
    return "".join(parts)


def _http_shape(url: str) -> bool:
    if url == "" or any(char.isspace() or ord(char) < 32 or ord(char) == 127 for char in url):
        return False
    if _FILE_SCHEME.match(url) is not None:
        return False
    lowered = url.lower()
    if lowered.startswith("https://"):
        rest = url[8:]
    elif lowered.startswith("http://"):
        rest = url[7:]
    else:
        return False
    if rest == "":
        return False
    hostport, extra = _split_host(rest)
    if hostport == "" or hostport.startswith(":"):
        return False
    hostname, colon, port = hostport.partition(":")
    if colon:
        if len(port) > _PORT_DIGITS or not port.isdigit():
            return False
        number = int(port)
        if number < 1 or number > 65535:
            return False
    if _HOST.fullmatch(hostname) is None:
        return False
    if extra and _PATH.fullmatch(extra) is None:
        return False
    return True


def _split_host(rest: str) -> tuple[str, str]:
    cut = len(rest)
    for mark in "/?#":
        found = rest.find(mark)
        if found != -1 and found < cut:
            cut = found
    return rest[:cut], rest[cut:]


def _strip_tail(body: str) -> str:
    end = len(body)
    while end > 0 and body[end - 1] in _TRAILING:
        end -= 1
    return body[:end]


def _marker(kind: str, name: str, *, skipped: bool) -> str:
    if skipped:
        if kind == "diff":
            return "[diff SKIPPED]"
        if kind == "url":
            return "[url SKIPPED]"
        return f"[{kind}:{name} SKIPPED]"
    if kind == "diff":
        return "[diff]"
    if kind == "url":
        return "[url NEED_FETCH]"
    return f"[{kind}:{name}]"


def _stitch(message: str, spans: list[tuple[int, int]], markers: list[str]) -> str:
    if len(spans) != len(markers):
        raise Refuse("BAD_REF")
    pieces: list[str] = []
    cursor = 0
    for index, marker in enumerate(markers):
        start, end = spans[index]
        pieces.append(message[cursor:start])
        pieces.append(marker)
        cursor = end
    pieces.append(message[cursor:])
    return "".join(pieces)


def _heading(record: ContextRecord) -> str:
    if record.kind == "diff":
        return "--- diff ---"
    if record.kind == "url":
        return f"--- url {record.code} ---"
    return f"--- {record.kind}:{record.name} ---"


def _attach(inline: str, records: list[ContextRecord]) -> str:
    if not records:
        return inline
    lines = [inline, "", _FENCE]
    for record in records:
        lines.append(_heading(record))
        lines.append(record.text)
    return "\n".join(lines)


def _suffix(records: tuple[ContextRecord, ...]) -> str:
    if not records:
        return ""
    return _attach("", list(records))


__all__ = [
    "ENTRY_CAP",
    "NAME_CAP",
    "POLICY_CAP",
    "SCHEMA",
    "ContextRecord",
    "ExpandedContext",
    "FetchDescriptor",
    "SkippedRef",
    "descriptors",
    "expand",
    "rebuild",
]
