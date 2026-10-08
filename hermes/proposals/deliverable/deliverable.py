"""Hash-check one relative artifact against a caller snapshot. No upload."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Final, NoReturn

from cosmos_hermes import Refuse, bound_bytes, bound_int, bound_text, const_eq, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-deliverable/1"
POLICY_CAP: Final[int] = 1_048_576
NAME_CAP: Final[int] = 240

_MEDIA_CAP: Final[int] = 32
_DIGEST_CAP: Final[int] = 64
_HEX: Final[frozenset[str]] = frozenset("0123456789abcdef")
_CONTROLS: Final[frozenset[str]] = frozenset(chr(code) for code in range(32))
_MARKS: Final[frozenset[str]] = frozenset('<>:"|?*\\')

_EXT: Final[dict[str, frozenset[str]]] = {
    "image": frozenset({"png", "jpg", "jpeg", "gif", "webp", "bmp", "tiff", "svg"}),
    "video": frozenset({"mp4", "mov", "avi", "mkv", "webm", "3gp"}),
    "audio": frozenset({"mp3", "m2a", "wav", "ogg", "opus", "m4a", "flac"}),
    "document": frozenset({"pdf", "docx", "doc", "odt", "rtf", "txt", "md", "epub"}),
    "data": frozenset({"xlsx", "xls", "ods", "csv", "tsv", "json", "xml", "yaml", "yml"}),
    "geospatial": frozenset({"kmz", "kml", "geojson", "gpx"}),
    "presentation": frozenset({"pptx", "ppt", "odp", "key"}),
    "archive": frozenset({"zip", "tar", "gz", "tgz", "bz2", "xz", "7z", "rar", "apk", "ipa"}),
    "web": frozenset({"html", "htm"}),
}

_DISPOSITION: Final[dict[str, str]] = {
    "image": "inline",
    "video": "inline",
    "audio": "voice",
    "document": "file",
    "data": "file",
    "geospatial": "file",
    "presentation": "file",
    "archive": "file",
    "web": "file",
}

_SOURCE: Final[frozenset[str]] = frozenset(
    {
        "py",
        "pyc",
        "pyo",
        "pyw",
        "log",
        "js",
        "mjs",
        "cjs",
        "ts",
        "tsx",
        "jsx",
        "c",
        "h",
        "cpp",
        "hpp",
        "cc",
        "hh",
        "rs",
        "go",
        "java",
        "rb",
        "php",
        "sh",
        "bash",
        "zsh",
        "ps1",
        "bat",
        "cmd",
        "cs",
        "swift",
        "kt",
        "scala",
        "lua",
        "pl",
        "r",
        "sql",
        "toml",
        "ini",
        "cfg",
        "conf",
        "env",
    }
)


def _hex_values() -> dict[str, int]:
    values = {char: index for index, char in enumerate("0123456789abcdef")}
    values.update({char: 10 + index for index, char in enumerate("ABCDEF")})
    return values


def _by_ext() -> dict[str, str]:
    index: dict[str, str] = {}
    for media, exts in _EXT.items():
        for ext in exts:
            if ext in index:
                raise Refuse("BAD_MEDIA")
            index[ext] = media
    return index


_HEX_VALUE: Final[dict[str, int]] = _hex_values()
_BY_EXT: Final[dict[str, str]] = _by_ext()


@dataclass(frozen=True, slots=True)
class Deliverable:
    """One snapshot entry whose sha256 matches. Bytes stay with the caller."""

    name: str
    media: str
    extension: str
    disposition: str
    sha256: str
    size: int
    cap: int
    schema: str = SCHEMA

    def __post_init__(self) -> None:
        schema_obj: object = self.schema
        if type(schema_obj) is not str or schema_obj != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        size_obj: object = self.size
        cap_obj: object = self.cap
        if type(size_obj) is not int:
            raise Refuse("NOT_INT")
        if type(cap_obj) is not int:
            raise Refuse("NOT_INT")
        if cap_obj < 1 or cap_obj > POLICY_CAP:
            raise Refuse("BAD_LIMIT")
        if size_obj < 1 or size_obj > cap_obj:
            raise Refuse("OVERSIZE", str(cap_obj))
        name = _relative_name(self.name)
        if name != self.name:
            raise Refuse("BAD_NAME")
        ext = _extension(name)
        media = bound_text(self.media, _MEDIA_CAP)
        extension = bound_text(self.extension, _MEDIA_CAP)
        disposition = bound_text(self.disposition, _MEDIA_CAP)
        digest = _digest(self.sha256)
        if secret_shape(media) or secret_shape(extension):
            raise Refuse("SECRET")
        if ext in _SOURCE or extension in _SOURCE:
            raise Refuse("SOURCE")
        if ext != extension or _BY_EXT.get(extension) != media:
            raise Refuse("BAD_MEDIA")
        if _DISPOSITION.get(media) != disposition:
            raise Refuse("BAD_MEDIA")
        if digest != self.sha256:
            raise Refuse("BAD_DIGEST")


def _secret(text: str) -> None:
    if secret_shape(text):
        raise Refuse("SECRET")


def _dots(part: str) -> bool:
    if part == "":
        return False
    for char in part:
        if char != ".":
            return False
    return True


def _slash_only(text: str) -> bool:
    if text == "":
        return False
    for char in text:
        if char != "/" and char != ".":
            return False
    return True


def _bad_name(text: str) -> bool:
    if text == "" or text.startswith("~") or _slash_only(text):
        return True
    for char in text:
        if char in _CONTROLS or char in _MARKS:
            return True
    for part in text.split("/"):
        if part == ".":
            continue
        if part == "" or _dots(part):
            return True
        if part != part.strip(" ") or part.endswith("."):
            return True
    return False


def _percent_decode(text: str) -> str:
    """Strict %HH as UTF-8. A NUL byte is NULL_BYTE. Anything else malformed is BAD_NAME."""
    raw = bytearray()
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        if char != "%":
            raw.extend(char.encode("utf-8"))
            index += 1
            continue
        if index + 2 >= length:
            raise Refuse("BAD_NAME")
        hi = _HEX_VALUE.get(text[index + 1])
        lo = _HEX_VALUE.get(text[index + 2])
        if hi is None or lo is None:
            raise Refuse("BAD_NAME")
        raw.append(hi * 16 + lo)
        index += 3
    if 0 in raw:
        raise Refuse("NULL_BYTE")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        raise Refuse("BAD_NAME") from None


def _relative_name(name: object) -> str:
    text = bound_text(name, NAME_CAP)
    _secret(text)
    if "%" in text:
        decoded = bound_text(_percent_decode(text), NAME_CAP)
        _secret(decoded)
        raise Refuse("BAD_NAME")
    if _bad_name(text):
        raise Refuse("BAD_NAME")
    return text


def _extension(name: str) -> str:
    slash = name.rfind("/")
    last = name if slash < 0 else name[slash + 1 :]
    dot = last.rfind(".")
    if dot < 0:
        raise Refuse("BAD_MEDIA")
    stem = last[:dot]
    ext = last[dot + 1 :]
    if stem == "" or ext == "" or _dots(stem) or stem.endswith(".") or stem.endswith(" "):
        raise Refuse("BAD_NAME")
    folded = ext.lower()
    if not folded.isascii() or not folded.isalnum():
        raise Refuse("BAD_MEDIA")
    return folded


def _media(value: object, ext: str) -> str:
    text = bound_text(value, _MEDIA_CAP)
    _secret(text)
    if ext in _SOURCE:
        raise Refuse("SOURCE")
    found = _BY_EXT.get(ext)
    if found is None or not const_eq(found, text):
        raise Refuse("BAD_MEDIA")
    return found


def _digest(value: object) -> str:
    text = bound_text(value, _DIGEST_CAP)
    _secret(text)
    if len(text) != 64 or any(char not in _HEX for char in text):
        raise Refuse("BAD_DIGEST")
    return text


def _applied_cap(cap: object) -> int:
    """Keep a tighter positive cap. A request above the policy cap is ignored."""
    if cap is None:
        return POLICY_CAP
    if type(cap) is not int:
        raise Refuse("BAD_LIMIT")
    if cap > POLICY_CAP:
        return POLICY_CAP
    return bound_int(cap, 1, POLICY_CAP)


def _snapshot_bytes(snapshot: object, key: str) -> bytes | bytearray:
    if type(snapshot) is not dict:
        raise Refuse("NOT_MAP")
    if key not in snapshot:
        raise Refuse("INCOMPLETE")
    raw: object = snapshot[key]
    if type(raw) is bytes or type(raw) is bytearray:
        return raw
    raise Refuse("NOT_BYTES")


def _scan_secret(blob: bytes) -> None:
    """One latin-1 pass. NUL is stripped so a split key shape still refuses."""
    text = blob.decode("latin-1")
    if "\x00" in text:
        text = text.replace("\x00", "")
    if text != "" and secret_shape(text):
        raise Refuse("SECRET")


def _sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def _expect(
    name: object,
    media: object,
    sha256_hex: object,
    snapshot: object,
    cap: object,
) -> Deliverable:
    if type(snapshot) is not dict:
        raise Refuse("NOT_MAP")
    checked = _relative_name(name)
    ext = _extension(checked)
    media_name = _media(media, ext)
    claimed = _digest(sha256_hex)
    applied = _applied_cap(cap)
    raw = _snapshot_bytes(snapshot, checked)
    if len(raw) < 1:
        raise Refuse("EMPTY")
    blob = bound_bytes(raw, applied)
    _scan_secret(blob)
    actual = _sha256(blob)
    if not const_eq(actual, claimed):
        raise Refuse("HASH")
    disposition = _DISPOSITION.get(media_name)
    if disposition is None:
        raise Refuse("BAD_MEDIA")
    return Deliverable(
        name=checked,
        media=media_name,
        extension=ext,
        disposition=disposition,
        sha256=actual,
        size=len(blob),
        cap=applied,
        schema=SCHEMA,
    )


def expect(
    name: str,
    media: str,
    sha256_hex: str,
    snapshot: dict[str, bytes],
    cap: int | None = None,
) -> Deliverable:
    """Return a frozen record when the snapshot bytes match name, media, and sha256."""
    return _expect(name, media, sha256_hex, snapshot, cap)


def upload(*_args: object, **_kwargs: object) -> NoReturn:
    """Native chat upload is not this process."""
    raise Refuse("NO_UPLOAD")


__all__ = [
    "NAME_CAP",
    "POLICY_CAP",
    "SCHEMA",
    "Deliverable",
    "expect",
    "upload",
]
