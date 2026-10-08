"""Priced image plan. A descriptor only: no bytes, no network, no key material."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, replace
from typing import Final

from cosmos_hermes import Refuse, bound_int, bound_text, const_eq, redact, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-image_gen/1"
PROMPT_CAP: Final[int] = 2000
SOURCE_CAP: Final[int] = 16
MAX_CENTS: Final[int] = 100_000_000
DEFAULT_MODEL: Final[str] = "flux-2-klein"
ASPECTS: Final[tuple[str, ...]] = ("landscape", "square", "portrait")
_MAX_PRICE_KEYS: Final[int] = 32
_REBUILD_CAP: Final[int] = 64

_CRED: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$")
_SHA: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")
_SURROGATE: Final[re.Pattern[str]] = re.compile(r"[\ud800-\udfff]")
_ASPECT_SET: Final[frozenset[str]] = frozenset(ASPECTS)
_QUALITIES: Final[frozenset[str]] = frozenset(("", "medium"))
_SIZES: Final[dict[str, dict[str, str]]] = {
    "preset": {
        "landscape": "landscape_16_9",
        "square": "square_hd",
        "portrait": "portrait_16_9",
    },
    "ratio": {
        "landscape": "16:9",
        "square": "1:1",
        "portrait": "9:16",
    },
    "gpt15": {
        "landscape": "1536x1024",
        "square": "1024x1024",
        "portrait": "1024x1536",
    },
    "gpt2": {
        "landscape": "landscape_4_3",
        "square": "square_hd",
        "portrait": "portrait_4_3",
    },
}
_FAMILIES: Final[frozenset[str]] = frozenset(_SIZES)


def _text(value: object, limit: int) -> str:
    text = bound_text(value, limit)
    if _SURROGATE.search(text) is not None:
        raise Refuse("NOT_TEXT")
    if secret_shape(text):
        raise Refuse("SECRET")
    return text


def _sha256_hex(value: object) -> str:
    if not isinstance(value, str):
        raise Refuse("NOT_TEXT")
    if "\x00" in value:
        raise Refuse("NULL_BYTE")
    if _SHA.fullmatch(value) is None:
        raise Refuse("BAD_JOB")
    return value


def _digest(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def _native(size_family: str, aspect: str) -> str:
    family = _SIZES.get(size_family)
    if family is None:
        raise Refuse("BAD_CATALOG")
    size = family.get(aspect)
    if size is None:
        raise Refuse("BAD_ASPECT")
    return size


def _aspect(value: object) -> str:
    text = _text(value, PROMPT_CAP)
    if text not in _ASPECT_SET:
        raise Refuse("BAD_ASPECT")
    return text


def _flag(value: object) -> bool:
    if type(value) is not bool:
        if isinstance(value, str):
            _text(value, PROMPT_CAP)
        raise Refuse("BAD_FLAG")
    return value


def _count(value: object) -> int:
    if isinstance(value, str):
        _text(value, PROMPT_CAP)
    return bound_int(value, 0, SOURCE_CAP)


def _cents(value: object) -> int:
    if isinstance(value, str):
        _text(value, PROMPT_CAP)
    return bound_int(value, 0, MAX_CENTS)


def _caps(prompt_cap: object, source_cap: object) -> None:
    if type(prompt_cap) is not int or type(source_cap) is not int:
        raise Refuse("NOT_INT")
    if prompt_cap != PROMPT_CAP or source_cap != SOURCE_CAP:
        raise Refuse("BAD_CAP")


def _prompt(value: object) -> str:
    text = _text(value, PROMPT_CAP)
    if text.strip() == "":
        raise Refuse("EMPTY")
    return text


def _credential(value: object) -> str:
    if isinstance(value, str) and value == "":
        raise Refuse("MISSING_CREDENTIAL")
    ident = _text(value, 64)
    if _CRED.fullmatch(ident) is None:
        raise Refuse("BAD_CREDENTIAL")
    return ident


def _prices(prices: object) -> dict[str, int]:
    if isinstance(prices, str):
        _text(prices, PROMPT_CAP)
        raise Refuse("BAD_PRICES")
    if type(prices) is not dict:
        raise Refuse("BAD_PRICES")
    if len(prices) > _MAX_PRICE_KEYS:
        raise Refuse("BAD_PRICES")
    clean: dict[str, int] = {}
    for key, value in prices.items():
        if not isinstance(key, str):
            raise Refuse("BAD_PRICES")
        name = _text(key, PROMPT_CAP)
        if name.strip() == "":
            raise Refuse("BAD_PRICES")
        if isinstance(value, str):
            _text(value, PROMPT_CAP)
        clean[name] = bound_int(value, 0, MAX_CENTS)
    return clean


def _ignore_cap(cap: object) -> None:
    """PROMPT_CAP is the recorded policy. A caller's number does not raise it."""
    if cap is None:
        return
    if isinstance(cap, str):
        _text(cap, PROMPT_CAP)
        raise Refuse("NOT_INT")
    if type(cap) is not int:
        raise Refuse("NOT_INT")
    if cap < 0:
        raise Refuse("OUT_OF_RANGE")


def _plan_id(
    *,
    model: str,
    credential_id: str,
    cents: int,
    upscale_cents: int,
    aspect: str,
    native_size: str,
    upscale: bool,
    sources: int,
    quality: str,
    prompt_sha256: str,
) -> str:
    parts = (
        model,
        credential_id,
        str(cents),
        str(upscale_cents),
        aspect,
        native_size,
        "1" if upscale else "0",
        str(sources),
        quality,
        prompt_sha256,
    )
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()


def _rows(records: object) -> tuple[object, ...] | list[object]:
    if isinstance(records, (str, bytes, bytearray)):
        raise Refuse("BAD_ORDER")
    if isinstance(records, list):
        return records
    if isinstance(records, tuple):
        return records
    raise Refuse("BAD_ORDER")


@dataclass(frozen=True, slots=True, kw_only=True)
class ModelSpec:
    """One allowlisted image model."""

    model_id: str
    size_family: str
    edit: bool
    quality: str

    def __post_init__(self) -> None:
        _text(self.model_id, PROMPT_CAP)
        family = _text(self.size_family, PROMPT_CAP)
        if family not in _FAMILIES:
            raise Refuse("BAD_CATALOG")
        if type(self.edit) is not bool:
            raise Refuse("BAD_FLAG")
        grade = _text(self.quality, PROMPT_CAP)
        if grade not in _QUALITIES:
            raise Refuse("BAD_QUALITY")

    def __repr__(self) -> str:
        body = (
            f"ModelSpec(model_id={self.model_id!r}, size_family={self.size_family!r}, "
            f"edit={self.edit}, quality={self.quality!r})"
        )
        return redact(body)


def _index(specs: tuple[ModelSpec, ...]) -> dict[str, ModelSpec]:
    found: dict[str, ModelSpec] = {}
    for spec in specs:
        if spec.model_id in found:
            raise Refuse("BAD_CATALOG")
        found[spec.model_id] = spec
    return found


_CATALOG: Final[tuple[ModelSpec, ...]] = (
    ModelSpec(model_id="flux-2-klein", size_family="preset", edit=True, quality=""),
    ModelSpec(model_id="flux-2-pro", size_family="preset", edit=True, quality=""),
    ModelSpec(model_id="gpt-image-1.5", size_family="gpt15", edit=True, quality="medium"),
    ModelSpec(model_id="gpt-image-2", size_family="gpt2", edit=True, quality="medium"),
    ModelSpec(model_id="nano-banana-pro", size_family="ratio", edit=True, quality=""),
    ModelSpec(model_id="ideogram-v3", size_family="preset", edit=True, quality=""),
    ModelSpec(model_id="recraft-v4", size_family="preset", edit=False, quality=""),
    ModelSpec(model_id="qwen-image", size_family="preset", edit=True, quality=""),
    ModelSpec(model_id="z-image-turbo", size_family="preset", edit=False, quality=""),
    ModelSpec(model_id="krea-v2", size_family="preset", edit=False, quality=""),
)
CATALOG: Final[tuple[ModelSpec, ...]] = _CATALOG
MODELS: Final[tuple[str, ...]] = tuple(spec.model_id for spec in _CATALOG)
_BY_ID: Final[dict[str, ModelSpec]] = _index(_CATALOG)


def _model(model: object) -> ModelSpec:
    name = _text(model, PROMPT_CAP)
    spec = _BY_ID.get(name)
    if spec is None:
        raise Refuse("UNKNOWN_MODEL")
    return spec


def _bind(
    *,
    priced: object,
    prompt_cap: object,
    source_cap: object,
    model: object,
    prompt: object,
    aspect: object,
    native_size: object,
    quality: object,
    upscale: object,
    cents: object,
    upscale_cents: object,
    sources: object,
) -> ModelSpec:
    if priced is not True:
        raise Refuse("UNPRICED")
    _caps(prompt_cap, source_cap)
    spec = _model(model)
    _prompt(prompt)
    chosen = _aspect(aspect)
    size = _text(native_size, PROMPT_CAP)
    if size != _native(spec.size_family, chosen):
        raise Refuse("BAD_ASPECT")
    grade = _text(quality, PROMPT_CAP)
    if grade != spec.quality:
        raise Refuse("BAD_QUALITY")
    flag = _flag(upscale)
    _cents(cents)
    extra = _cents(upscale_cents)
    count = _count(sources)
    if flag is False and extra != 0:
        raise Refuse("BAD_FLAG")
    if count > 0 and spec.edit is False:
        raise Refuse("NO_EDIT")
    return spec


@dataclass(frozen=True, slots=True, kw_only=True)
class ImageRequest:
    """Frozen priced image request. `priced` is true only when cents were quoted."""

    model: str
    prompt: str
    cents: int
    priced: bool
    prompt_cap: int
    aspect: str
    native_size: str
    upscale: bool
    upscale_cents: int
    sources: int
    source_cap: int
    quality: str

    def __post_init__(self) -> None:
        _bind(
            priced=self.priced,
            prompt_cap=self.prompt_cap,
            source_cap=self.source_cap,
            model=self.model,
            prompt=self.prompt,
            aspect=self.aspect,
            native_size=self.native_size,
            quality=self.quality,
            upscale=self.upscale,
            cents=self.cents,
            upscale_cents=self.upscale_cents,
            sources=self.sources,
        )

    def __repr__(self) -> str:
        body = (
            f"ImageRequest(model={self.model!r}, cents={self.cents}, priced={self.priced}, "
            f"prompt_cap={self.prompt_cap}, aspect={self.aspect!r}, "
            f"native_size={self.native_size!r}, upscale={self.upscale}, "
            f"upscale_cents={self.upscale_cents}, sources={self.sources}, "
            f"source_cap={self.source_cap}, quality={self.quality!r})"
        )
        return redact(body)


@dataclass(frozen=True, slots=True, kw_only=True)
class GenerationJob:
    """Spend-gated plan. Building it does not generate bytes or dial out."""

    model: str
    prompt: str
    credential_id: str
    cents: int
    upscale_cents: int
    priced: bool
    prompt_cap: int
    aspect: str
    native_size: str
    upscale: bool
    sources: int
    source_cap: int
    quality: str
    prompt_sha256: str
    plan_id: str

    def __post_init__(self) -> None:
        spec = _bind(
            priced=self.priced,
            prompt_cap=self.prompt_cap,
            source_cap=self.source_cap,
            model=self.model,
            prompt=self.prompt,
            aspect=self.aspect,
            native_size=self.native_size,
            quality=self.quality,
            upscale=self.upscale,
            cents=self.cents,
            upscale_cents=self.upscale_cents,
            sources=self.sources,
        )
        ident = _credential(self.credential_id)
        digest = _digest(self.prompt)
        got = _sha256_hex(self.prompt_sha256)
        if not const_eq(got, digest):
            raise Refuse("BAD_JOB")
        expected = _plan_id(
            model=spec.model_id,
            credential_id=ident,
            cents=self.cents,
            upscale_cents=self.upscale_cents,
            aspect=self.aspect,
            native_size=self.native_size,
            upscale=self.upscale,
            sources=self.sources,
            quality=spec.quality,
            prompt_sha256=got,
        )
        if not const_eq(_sha256_hex(self.plan_id), expected):
            raise Refuse("BAD_JOB")

    def __repr__(self) -> str:
        body = (
            f"GenerationJob(model={self.model!r}, credential_id={self.credential_id!r}, "
            f"cents={self.cents}, upscale_cents={self.upscale_cents}, priced={self.priced}, "
            f"prompt_cap={self.prompt_cap}, aspect={self.aspect!r}, "
            f"native_size={self.native_size!r}, upscale={self.upscale}, "
            f"sources={self.sources}, source_cap={self.source_cap}, quality={self.quality!r}, "
            f"prompt_sha256={self.prompt_sha256!r}, plan_id={self.plan_id!r})"
        )
        return redact(body)


def native_size(model: str, aspect: str = "square") -> str:
    """Return the model's native size token for an aspect."""
    spec = _model(model)
    chosen = _aspect(aspect)
    return _native(spec.size_family, chosen)


def request(
    model: str,
    prompt: str,
    prices: dict[str, int],
    *,
    aspect: str = "square",
    upscale: bool = False,
    sources: int = 0,
    cap: int | None = None,
) -> ImageRequest:
    """Price one allowlisted image request. Does not generate an image."""
    _ignore_cap(cap)
    spec = _model(model)
    table = _prices(prices)
    if spec.model_id not in table:
        raise Refuse("UNPRICED")
    chosen = _aspect(aspect)
    flag = _flag(upscale)
    count = _count(sources)
    if count > 0 and spec.edit is False:
        raise Refuse("NO_EDIT")
    extra = 0
    if flag is True:
        if "upscale" not in table:
            raise Refuse("UNPRICED")
        extra = table["upscale"]
    return ImageRequest(
        model=spec.model_id,
        prompt=prompt,
        cents=table[spec.model_id],
        priced=True,
        prompt_cap=PROMPT_CAP,
        aspect=chosen,
        native_size=_native(spec.size_family, chosen),
        upscale=flag,
        upscale_cents=extra,
        sources=count,
        source_cap=SOURCE_CAP,
        quality=spec.quality,
    )


def dispatch(order: ImageRequest, credential_id: str) -> GenerationJob:
    """Bind a credential id to a priced request. Returns a plan, not image bytes."""
    raw: object = order
    if type(raw) is not ImageRequest:
        raise Refuse("BAD_ORDER")
    ident = _credential(credential_id)
    digest = _digest(order.prompt)
    plan = _plan_id(
        model=order.model,
        credential_id=ident,
        cents=order.cents,
        upscale_cents=order.upscale_cents,
        aspect=order.aspect,
        native_size=order.native_size,
        upscale=order.upscale,
        sources=order.sources,
        quality=order.quality,
        prompt_sha256=digest,
    )
    return GenerationJob(
        model=order.model,
        prompt=order.prompt,
        credential_id=ident,
        cents=order.cents,
        upscale_cents=order.upscale_cents,
        priced=True,
        prompt_cap=order.prompt_cap,
        aspect=order.aspect,
        native_size=order.native_size,
        upscale=order.upscale,
        sources=order.sources,
        source_cap=order.source_cap,
        quality=order.quality,
        prompt_sha256=digest,
        plan_id=plan,
    )


def rebuild(records: object) -> tuple[GenerationJob, ...]:
    """Replay emitted plans. A repeated plan id or a broken digest refuses."""
    rows = _rows(records)
    if len(rows) == 0:
        raise Refuse("EMPTY")
    if len(rows) > _REBUILD_CAP:
        raise Refuse("BAD_ORDER")
    seen: set[str] = set()
    out: list[GenerationJob] = []
    for item in rows:
        if type(item) is not GenerationJob:
            raise Refuse("BAD_ORDER")
        if item.plan_id in seen:
            raise Refuse("REPLAY")
        seen.add(item.plan_id)
        out.append(replace(item))
    return tuple(out)


__all__ = [
    "ASPECTS",
    "CATALOG",
    "DEFAULT_MODEL",
    "MAX_CENTS",
    "MODELS",
    "PROMPT_CAP",
    "SCHEMA",
    "SOURCE_CAP",
    "GenerationJob",
    "ImageRequest",
    "ModelSpec",
    "dispatch",
    "native_size",
    "rebuild",
    "request",
]
