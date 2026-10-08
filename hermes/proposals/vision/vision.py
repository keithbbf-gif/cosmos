"""Spend-gated vision descriptor. Local rasters only. No model call and no socket."""

from __future__ import annotations

import hashlib
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Final, NoReturn, cast

from cosmos_hermes import (
    PathJail,
    Refuse,
    bound_bytes,
    bound_int,
    bound_text,
    const_eq,
    redact,
    secret_shape,
)
from cosmos_hermes.bounds import MAX_BYTES

SCHEMA: Final[str] = "cosmos-hermes-vision/1"
BYTE_CAP: Final[int] = 2_000_000
EMBED_CAP: Final[int] = 262_144
CALL_CAP: Final[int] = 3
COUNT_CAP: Final[int] = 8
PROMPT_CAP: Final[int] = 2_000
CRED_CAP: Final[int] = 64
PATH_CAP: Final[int] = 4_096
MAX_CENTS: Final[int] = 100_000_000

_AT_MAX: Final[int] = 4_102_444_800
_MEDIA: Final[frozenset[str]] = frozenset(
    {"image/png", "image/jpeg", "image/gif", "image/webp"}
)
_SOURCES: Final[frozenset[str]] = frozenset({"bytes", "path"})
_MODES: Final[frozenset[str]] = frozenset({"auto", "native", "text"})
_ROUTES: Final[frozenset[str]] = frozenset({"describe", "native"})
_HEX: Final[frozenset[str]] = frozenset("0123456789abcdef")
_CRED_START: Final[frozenset[str]] = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
)
_CRED_REST: Final[frozenset[str]] = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._:-"
)
_PNG: Final[bytes] = b"\x89PNG\r\n\x1a\n"
_JPEG: Final[bytes] = b"\xff\xd8\xff"
_GIF: Final[tuple[bytes, ...]] = (b"GIF87a", b"GIF89a")


def _hex64(value: str) -> bool:
    return len(value) == 64 and all(ch in _HEX for ch in value)


def _skip_ids(raw: tuple[str, ...], seen: set[str], banned: set[str]) -> None:
    found: set[str] = set()
    for ident in raw:
        if type(ident) is not str or not _hex64(ident) or ident in seen or ident in banned:
            raise Refuse("BAD_RECORDS")
        if ident in found:
            raise Refuse("DUPLICATE")
        found.add(ident)


def _schema(value: object) -> bool:
    return isinstance(value, str) and const_eq(value, SCHEMA)


def _credential(value: object) -> str:
    if value is None:
        raise Refuse("NO_CRED")
    if type(value) is not str:
        raise Refuse("BAD_CRED")
    if value == "":
        raise Refuse("NO_CRED")
    if len(value) > CRED_CAP or "\x00" in value:
        raise Refuse("BAD_CRED")
    if secret_shape(value):
        raise Refuse("SECRET")
    if value[0] not in _CRED_START or any(ch not in _CRED_REST for ch in value):
        raise Refuse("BAD_CRED")
    return value


def _prompt(value: object) -> str:
    text = bound_text(value, PROMPT_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    if text.strip() == "":
        raise Refuse("EMPTY")
    return text


def _ceiling(value: object, policy: int) -> int:
    """Record `policy` when the caller asks for more. Never raise the ceiling."""
    if value is None:
        return policy
    if type(value) is not int:
        raise Refuse("NOT_INT")
    if value < 1:
        raise Refuse("OUT_OF_RANGE", f"1..{policy}")
    if value > policy:
        return policy
    return value


def _ingest_cap(value: object) -> int:
    if type(value) is not int:
        raise Refuse("NOT_INT")
    if value > BYTE_CAP:
        return BYTE_CAP
    if value != BYTE_CAP:
        raise Refuse("BAD_CAP")
    return BYTE_CAP


def _prices(value: object) -> dict[str, int]:
    if type(value) is not dict:
        if isinstance(value, str) and secret_shape(value):
            raise Refuse("SECRET")
        raise Refuse("BAD_PRICES")
    if len(value) > len(_ROUTES):
        raise Refuse("BAD_PRICES")
    clean: dict[str, int] = {}
    for key, item in value.items():
        if type(key) is not str:
            raise Refuse("BAD_PRICES")
        name = bound_text(key, CRED_CAP)
        if secret_shape(name):
            raise Refuse("SECRET")
        if name not in _ROUTES:
            raise Refuse("BAD_PRICES")
        clean[name] = bound_int(item, 0, MAX_CENTS)
    return clean


def _quote(table: dict[str, int], route: str) -> int:
    for key, cents in table.items():
        if const_eq(key, route):
            return cents
    raise Refuse("UNPRICED")


def _call_map(value: object) -> dict[str, int]:
    if value is None:
        return {}
    if type(value) is not dict:
        raise Refuse("BAD_CALLS")
    if len(value) > COUNT_CAP:
        raise Refuse("OVERSIZE", str(COUNT_CAP))
    clean: dict[str, int] = {}
    for key, count in value.items():
        if type(key) is not str:
            raise Refuse("BAD_CALLS")
        name = bound_text(key, CRED_CAP)
        if secret_shape(name):
            raise Refuse("SECRET")
        if not _hex64(name):
            raise Refuse("BAD_DIGEST")
        clean[name] = bound_int(count, 0, CALL_CAP)
    return clean


def _used(image_id: str, calls: dict[str, int]) -> int:
    for key, count in calls.items():
        if const_eq(key, image_id):
            return count
    return 0


def _rows(images: object) -> tuple[object, ...] | list[object]:
    if type(images) is tuple:
        return cast(tuple[object, ...], images)
    if type(images) is list:
        return cast(list[object], images)
    raise Refuse("BAD_IMAGE")


def _media_type(blob: bytes | bytearray) -> str:
    if blob.startswith(_PNG):
        return "image/png"
    if blob.startswith(_JPEG):
        return "image/jpeg"
    if blob.startswith(_GIF):
        return "image/gif"
    if len(blob) >= 12 and blob[:4] == b"RIFF" and blob[8:12] == b"WEBP":
        return "image/webp"
    raise Refuse("UNSUPPORTED_FORMAT", "png-jpeg-gif-webp")


def _bound_image(data: bytes | bytearray) -> bytes:
    # bound_bytes refuses a limit above MAX_BYTES, so a legal image is windowed.
    parts: list[bytes] = []
    offset = 0
    size = len(data)
    while offset < size:
        part = bound_bytes(data[offset : offset + MAX_BYTES])
        parts.append(part)
        offset += len(part)
    if len(parts) == 1:
        return parts[0]
    return b"".join(parts)


def _seal(data: bytes | bytearray, source: str) -> LocalImage:
    if source not in _SOURCES:
        raise Refuse("BAD_SOURCE")
    if len(data) < 1:
        raise Refuse("EMPTY")
    if len(data) > BYTE_CAP:
        raise Refuse("OVERSIZE", str(BYTE_CAP))
    bounded = _bound_image(data)
    media = _media_type(bounded)
    return LocalImage(
        image_id=hashlib.sha256(bounded).hexdigest(),
        nbytes=len(bounded),
        byte_cap=BYTE_CAP,
        media_type=media,
        source=source,
        schema=SCHEMA,
    )


def _read_once(resolved: Path, size: int) -> bytes | None:
    try:
        with resolved.open("rb") as handle:
            return handle.read(size + 1)
    except OSError:
        return None


def _read_exact(resolved: Path, size: int) -> bytes:
    """One confirming retry when the read raises OSError or misses `size`."""
    first = _read_once(resolved, size)
    if first is not None and len(first) == size:
        return first
    second = _read_once(resolved, size)
    if second is not None and len(second) == size:
        return second
    raise Refuse("UNREADABLE")


def _path_text(value: object) -> str:
    if type(value) is not str:
        raise Refuse("BAD_PATH")
    if value == "" or len(value) > PATH_CAP:
        raise Refuse("BAD_PATH")
    if "\x00" in value:
        raise Refuse("NULL_BYTE")
    if secret_shape(value):
        raise Refuse("SECRET")
    return value


@dataclass(frozen=True, slots=True, kw_only=True)
class LocalImage:
    """One admitted raster. The id is the sha256. Pixels stay with the caller."""

    image_id: str
    nbytes: int
    byte_cap: int
    media_type: str
    source: str
    schema: str = SCHEMA

    def __post_init__(self) -> None:
        if not _schema(self.schema):
            raise Refuse("BAD_SCHEMA")
        cap = _ingest_cap(self.byte_cap)
        object.__setattr__(self, "byte_cap", cap)
        if type(self.nbytes) is not int:
            raise Refuse("NOT_INT")
        if self.nbytes < 1:
            raise Refuse("EMPTY")
        if self.nbytes > cap:
            raise Refuse("OVERSIZE", str(cap))
        if type(self.image_id) is not str or not _hex64(self.image_id):
            raise Refuse("BAD_DIGEST")
        if type(self.media_type) is not str or self.media_type not in _MEDIA:
            raise Refuse("BAD_MEDIA")
        if type(self.source) is not str or self.source not in _SOURCES:
            raise Refuse("BAD_SOURCE")

    def __repr__(self) -> str:
        return redact(
            f"LocalImage(image_id={self.image_id!r}, nbytes={self.nbytes}, "
            f"byte_cap={self.byte_cap}, media_type={self.media_type!r}, "
            f"source={self.source!r}, schema={self.schema!r})"
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class VisionRequest:
    """One priced local image. Building it does not call a model."""

    image_id: str
    credential_id: str
    prompt: str
    route: str
    cents: int
    priced: bool
    nbytes: int
    byte_cap: int
    embed_cap: int
    call_cap: int
    calls_used: int
    media_type: str
    source: str
    at: int
    prompt_sha256: str
    fits_embed: bool = False
    spend_required: bool = True
    schema: str = SCHEMA

    def __post_init__(self) -> None:
        if not _schema(self.schema):
            raise Refuse("BAD_SCHEMA")
        byte_cap = _ceiling(self.byte_cap, BYTE_CAP)
        embed_cap = _ceiling(self.embed_cap, EMBED_CAP)
        call_cap = _ceiling(self.call_cap, CALL_CAP)
        object.__setattr__(self, "byte_cap", byte_cap)
        object.__setattr__(self, "embed_cap", embed_cap)
        object.__setattr__(self, "call_cap", call_cap)
        if type(self.nbytes) is not int:
            raise Refuse("NOT_INT")
        if self.nbytes < 1:
            raise Refuse("EMPTY")
        if self.nbytes > byte_cap:
            raise Refuse("OVERSIZE", str(byte_cap))
        if type(self.calls_used) is not int:
            raise Refuse("NOT_INT")
        if self.calls_used < 1 or self.calls_used > call_cap:
            raise Refuse("CALLS")
        bound_int(self.cents, 0, MAX_CENTS)
        bound_int(self.at, 0, _AT_MAX)
        ident = _credential(self.credential_id)
        if not const_eq(ident, self.credential_id):
            raise Refuse("BAD_CRED")
        if type(self.route) is not str or self.route not in _ROUTES:
            raise Refuse("BAD_ROUTE")
        if type(self.media_type) is not str or self.media_type not in _MEDIA:
            raise Refuse("BAD_MEDIA")
        if type(self.source) is not str or self.source not in _SOURCES:
            raise Refuse("BAD_SOURCE")
        if self.priced is not True:
            raise Refuse("UNPRICED")
        if type(self.image_id) is not str or not _hex64(self.image_id):
            raise Refuse("BAD_DIGEST")
        text = _prompt(self.prompt)
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if not const_eq(digest, self.prompt_sha256):
            raise Refuse("BAD_DIGEST")
        object.__setattr__(self, "fits_embed", self.nbytes <= embed_cap)
        object.__setattr__(self, "spend_required", True)

    def __repr__(self) -> str:
        return redact(
            "VisionRequest("
            f"image_id={self.image_id!r}, credential_id={self.credential_id!r}, "
            f"route={self.route!r}, cents={self.cents}, priced={self.priced}, "
            f"nbytes={self.nbytes}, byte_cap={self.byte_cap}, embed_cap={self.embed_cap}, "
            f"call_cap={self.call_cap}, calls_used={self.calls_used}, "
            f"media_type={self.media_type!r}, source={self.source!r}, "
            f"fits_embed={self.fits_embed}, spend_required={self.spend_required}, "
            f"schema={self.schema!r}, at={self.at}, prompt_sha256={self.prompt_sha256!r})"
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class VisionBatch:
    """Images kept in one pass, plus the ids that did not fit."""

    requests: tuple[VisionRequest, ...]
    skipped_size: tuple[str, ...]
    skipped_calls: tuple[str, ...]
    byte_cap: int
    embed_cap: int
    call_cap: int
    credential_id: str
    route: str
    cents: int
    priced: bool
    at: int
    spend_required: bool = True
    schema: str = SCHEMA

    def __post_init__(self) -> None:
        if not _schema(self.schema):
            raise Refuse("BAD_SCHEMA")
        object.__setattr__(self, "spend_required", True)
        if self.priced is not True:
            raise Refuse("UNPRICED")
        if type(self.byte_cap) is not int or type(self.embed_cap) is not int or type(self.call_cap) is not int:
            raise Refuse("NOT_INT")
        if type(self.cents) is not int or type(self.at) is not int:
            raise Refuse("NOT_INT")
        if type(self.requests) is not tuple:
            raise Refuse("BAD_RECORDS")
        if len(self.requests) < 1:
            raise Refuse("EMPTY")
        if type(self.skipped_size) is not tuple or type(self.skipped_calls) is not tuple:
            raise Refuse("BAD_RECORDS")
        seen: set[str] = set()
        prompt = ""
        for item in self.requests:
            if type(item) is not VisionRequest:
                raise Refuse("BAD_RECORDS")
            if item.image_id in seen:
                raise Refuse("DUPLICATE")
            seen.add(item.image_id)
            if item.byte_cap != self.byte_cap or item.embed_cap != self.embed_cap or item.call_cap != self.call_cap:
                raise Refuse("BAD_CAP")
            if (
                not const_eq(item.credential_id, self.credential_id)
                or not const_eq(item.route, self.route)
                or item.cents != self.cents
                or item.at != self.at
                or item.priced is not True
                or not const_eq(item.schema, SCHEMA)
            ):
                raise Refuse("BAD_RECORDS")
            if prompt == "":
                prompt = item.prompt
            elif not const_eq(item.prompt, prompt):
                raise Refuse("BAD_RECORDS")
        _skip_ids(self.skipped_size, seen, set[str]())
        _skip_ids(self.skipped_calls, seen, set(self.skipped_size))

    def __repr__(self) -> str:
        return redact(
            "VisionBatch("
            f"schema={self.schema!r}, requests={len(self.requests)}, "
            f"skipped_size={len(self.skipped_size)}, skipped_calls={len(self.skipped_calls)}, "
            f"byte_cap={self.byte_cap}, embed_cap={self.embed_cap}, call_cap={self.call_cap}, "
            f"credential_id={self.credential_id!r}, route={self.route!r}, cents={self.cents}, "
            f"priced={self.priced}, spend_required={self.spend_required}, at={self.at})"
        )


def _one(
    image: LocalImage,
    *,
    used: int,
    credential_id: str,
    prompt: str,
    route: str,
    cents: int,
    byte_cap: int,
    embed_cap: int,
    call_cap: int,
    at: int,
    prompt_sha256: str,
) -> VisionRequest:
    return VisionRequest(
        image_id=image.image_id,
        credential_id=credential_id,
        prompt=prompt,
        route=route,
        cents=cents,
        priced=True,
        nbytes=image.nbytes,
        byte_cap=byte_cap,
        embed_cap=embed_cap,
        call_cap=call_cap,
        calls_used=used + 1,
        media_type=image.media_type,
        source=image.source,
        at=at,
        prompt_sha256=prompt_sha256,
        fits_embed=image.nbytes <= embed_cap,
        spend_required=True,
        schema=SCHEMA,
    )


def _build(
    images: object,
    credential_id: object,
    prompt: object,
    prices: object,
    mode: object,
    vision_capable: object,
    auxiliary: object,
    byte_cap: object,
    embed_cap: object,
    call_cap: object,
    calls: object,
    at: object,
) -> VisionBatch:
    rows = _rows(images)
    if len(rows) > COUNT_CAP:
        raise Refuse("OVERSIZE", str(COUNT_CAP))
    if len(rows) < 1:
        raise Refuse("EMPTY")
    recorded_byte = _ceiling(byte_cap, BYTE_CAP)
    recorded_embed = _ceiling(embed_cap, EMBED_CAP)
    recorded_call = _ceiling(call_cap, CALL_CAP)
    ident = _credential(credential_id)
    if not const_eq(ident, credential_id if isinstance(credential_id, str) else ""):
        raise Refuse("BAD_CRED")
    text = _prompt(prompt)
    route = choose_route(mode, vision_capable, auxiliary)
    table = _prices(prices)
    cents = _quote(table, route)
    stamp = bound_int(at, 0, _AT_MAX)
    call_map = _call_map(calls)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    kept: list[VisionRequest] = []
    skipped_size: list[str] = []
    skipped_calls: list[str] = []
    seen: set[str] = set()
    remaining = recorded_byte
    for image in rows:
        if type(image) is not LocalImage:
            raise Refuse("BAD_IMAGE")
        if image.image_id in seen:
            raise Refuse("DUPLICATE")
        seen.add(image.image_id)
        used = _used(image.image_id, call_map)
        if used >= recorded_call:
            skipped_calls.append(image.image_id)
            continue
        if image.nbytes > remaining:
            skipped_size.append(image.image_id)
            continue
        kept.append(
            _one(
                image,
                used=used,
                credential_id=ident,
                prompt=text,
                route=route,
                cents=cents,
                byte_cap=recorded_byte,
                embed_cap=recorded_embed,
                call_cap=recorded_call,
                at=stamp,
                prompt_sha256=digest,
            )
        )
        remaining -= image.nbytes
    if not kept:
        if len(skipped_calls) == len(rows) and len(skipped_size) == 0:
            raise Refuse("CALLS")
        if len(skipped_size) == len(rows) and len(skipped_calls) == 0:
            raise Refuse("OVERSIZE", str(recorded_byte))
        raise Refuse("EMPTY")
    return VisionBatch(
        requests=tuple(kept),
        skipped_size=tuple(skipped_size),
        skipped_calls=tuple(skipped_calls),
        byte_cap=recorded_byte,
        embed_cap=recorded_embed,
        call_cap=recorded_call,
        credential_id=ident,
        route=route,
        cents=cents,
        priced=True,
        at=stamp,
        spend_required=True,
        schema=SCHEMA,
    )


def _only(batch: VisionBatch) -> VisionRequest:
    for item in batch.requests:
        return item
    raise Refuse("EMPTY")


def _rebox(item: VisionRequest) -> VisionRequest:
    return VisionRequest(
        image_id=item.image_id,
        credential_id=item.credential_id,
        prompt=item.prompt,
        route=item.route,
        cents=item.cents,
        priced=item.priced,
        nbytes=item.nbytes,
        byte_cap=item.byte_cap,
        embed_cap=item.embed_cap,
        call_cap=item.call_cap,
        calls_used=item.calls_used,
        media_type=item.media_type,
        source=item.source,
        at=item.at,
        prompt_sha256=item.prompt_sha256,
        fits_embed=item.fits_embed,
        spend_required=item.spend_required,
        schema=item.schema,
    )


def choose_route(mode: object, vision_capable: object, auxiliary: object) -> str:
    """Map auto, native, and text onto describe or native. off and yolo refuse."""
    if type(mode) is not str:
        raise Refuse("BAD_MODE")
    label = bound_text(mode, CRED_CAP)
    if secret_shape(label):
        raise Refuse("SECRET")
    if label not in _MODES:
        raise Refuse("BAD_MODE")
    if type(vision_capable) is not bool or type(auxiliary) is not bool:
        raise Refuse("BAD_FLAG")
    if label == "native":
        return "native"
    if label == "text":
        return "describe"
    if vision_capable is True and auxiliary is False:
        return "native"
    return "describe"


def from_bytes(data: object) -> LocalImage:
    """Hash one raster image. The ingest ceiling is BYTE_CAP. No model call."""
    if type(data) is not bytes and type(data) is not bytearray:
        raise Refuse("NOT_BYTES")
    return _seal(data, "bytes")


def from_path(jail: object, path: object) -> LocalImage:
    """Read one granted image. Never more than BYTE_CAP bytes. No model call."""
    if type(jail) is not PathJail:
        raise Refuse("BAD_JAIL")
    raw = _path_text(path)
    resolved = jail.contain(raw)
    try:
        info = resolved.stat()
    except FileNotFoundError:
        raise Refuse("NOT_FILE") from None
    except OSError:
        raise Refuse("UNREADABLE") from None
    if type(info.st_mode) is not int or not stat.S_ISREG(info.st_mode):
        raise Refuse("NOT_FILE")
    if type(info.st_size) is not int:
        raise Refuse("UNREADABLE")
    if info.st_size < 1:
        raise Refuse("EMPTY")
    if info.st_size > BYTE_CAP:
        raise Refuse("OVERSIZE", str(BYTE_CAP))
    blob = _read_exact(resolved, info.st_size)
    return _seal(blob, "path")


def from_url(url: object) -> NoReturn:
    """Remote images are not fetched."""
    text = bound_text(url)
    if secret_shape(text):
        raise Refuse("SECRET")
    raise Refuse("NO_FETCH")


def request(
    image: object,
    credential_id: object,
    prompt: object,
    prices: object,
    *,
    mode: object = "text",
    vision_capable: object = False,
    auxiliary: object = False,
    byte_cap: object = None,
    embed_cap: object = None,
    call_cap: object = None,
    calls: object = None,
    at: object,
) -> VisionRequest:
    """Price one local image id. A higher cap is ignored. Does not call a model."""
    if type(image) is not LocalImage:
        raise Refuse("BAD_IMAGE")
    batch = _build(
        (image,),
        credential_id,
        prompt,
        prices,
        mode,
        vision_capable,
        auxiliary,
        byte_cap,
        embed_cap,
        call_cap,
        calls,
        at,
    )
    return _only(batch)


def assemble(
    images: object,
    credential_id: object,
    prompt: object,
    prices: object,
    *,
    mode: object = "text",
    vision_capable: object = False,
    auxiliary: object = False,
    byte_cap: object = None,
    embed_cap: object = None,
    call_cap: object = None,
    calls: object = None,
    at: object,
) -> VisionBatch:
    """One pass. Skip an image that does not fit. Keep a later image that does."""
    return _build(
        images,
        credential_id,
        prompt,
        prices,
        mode,
        vision_capable,
        auxiliary,
        byte_cap,
        embed_cap,
        call_cap,
        calls,
        at,
    )


def rebuild(records: object) -> VisionBatch:
    """Replay a batch. The same records return the same public state."""
    if type(records) is not VisionBatch:
        raise Refuse("BAD_RECORDS")
    boxed: list[VisionRequest] = []
    for item in records.requests:
        boxed.append(_rebox(item))
    return VisionBatch(
        requests=tuple(boxed),
        skipped_size=records.skipped_size,
        skipped_calls=records.skipped_calls,
        byte_cap=records.byte_cap,
        embed_cap=records.embed_cap,
        call_cap=records.call_cap,
        credential_id=records.credential_id,
        route=records.route,
        cents=records.cents,
        priced=records.priced,
        at=records.at,
        spend_required=True,
        schema=records.schema,
    )


__all__ = [
    "BYTE_CAP",
    "CALL_CAP",
    "COUNT_CAP",
    "CRED_CAP",
    "EMBED_CAP",
    "LocalImage",
    "MAX_CENTS",
    "PATH_CAP",
    "PROMPT_CAP",
    "SCHEMA",
    "VisionBatch",
    "VisionRequest",
    "assemble",
    "choose_route",
    "from_bytes",
    "from_path",
    "from_url",
    "rebuild",
    "request",
]
