"""Spend-gated video plan. A descriptor only: no render and no key material."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, replace
from typing import Final, NoReturn

from cosmos_hermes import Refuse, bound_int, bound_text, const_eq, redact, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-video_gen/1"
PROMPT_CAP: Final[int] = 2000
MIN_SECONDS: Final[int] = 1
POLICY_SECONDS: Final[int] = 12
ASK_CEILING: Final[int] = 86_400
MAX_CENTS: Final[int] = 100_000_000
MODELS: Final[tuple[str, ...]] = ("grok-video", "local-noop")

_MAX_PRICE_KEYS: Final[int] = 32
_REBUILD_CAP: Final[int] = 64
_CRED: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$")
_SURROGATE: Final[re.Pattern[str]] = re.compile(r"[\ud800-\udfff]")
_MODEL_SET: Final[frozenset[str]] = frozenset(MODELS)


def duration_lo() -> int:
    """Lowest accepted duration in seconds. Zero is below this bound."""
    return MIN_SECONDS


def duration_hi() -> int:
    """Policy duration cap in seconds. A higher ask records this cap."""
    return POLICY_SECONDS


def _text(value: object, limit: int) -> str:
    text = bound_text(value, limit)
    if _SURROGATE.search(text) is not None:
        raise Refuse("NOT_TEXT")
    if secret_shape(text):
        raise Refuse("SECRET")
    return text


def _as_str(value: object) -> str:
    if isinstance(value, str):
        return value
    raise Refuse("NOT_TEXT")


def _model(model: object) -> str:
    name = _text(model, PROMPT_CAP)
    if name not in _MODEL_SET:
        raise Refuse("UNKNOWN_MODEL")
    return name


def _allow(model: object) -> str:
    """Allowlist check. A known id is not secret-scanned here; the seal scans it."""
    name = _as_str(model)
    if name in _MODEL_SET:
        return name
    _text(name, PROMPT_CAP)
    raise Refuse("UNKNOWN_MODEL")


def _prompt(prompt: object) -> str:
    text = _text(prompt, PROMPT_CAP)
    if text.strip() == "":
        raise Refuse("EMPTY")
    return text


def apply_duration(seconds: object) -> tuple[int, int, bool]:
    """Return applied seconds, the ask, and whether the policy cap was recorded.

    Asks above `duration_hi` and at most `ASK_CEILING` record the policy cap.
    Asks below `duration_lo` refuse. The cap is never raised.
    """
    if isinstance(seconds, str):
        _text(seconds, PROMPT_CAP)
        raise Refuse("NOT_INT")
    asked = bound_int(seconds, duration_lo(), ASK_CEILING)
    hi = duration_hi()
    if asked > hi:
        return hi, asked, True
    return asked, asked, False


def apply_prompt_cap(cap: object) -> int:
    """Return the policy prompt cap. A caller's number does not change it."""
    if cap is None:
        return PROMPT_CAP
    if isinstance(cap, str):
        _text(cap, PROMPT_CAP)
        raise Refuse("NOT_INT")
    if type(cap) is not int:
        raise Refuse("NOT_INT")
    if cap < 1:
        raise Refuse("OUT_OF_RANGE")
    return PROMPT_CAP


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


def _lookup(model: str, prices: object) -> int:
    table = _prices(prices)
    if model not in table:
        raise Refuse("UNPRICED")
    return table[model]


def _seal_duration(
    seconds: object,
    requested_seconds: object,
    duration_cap: object,
    capped: object,
) -> None:
    if (
        type(seconds) is not int
        or type(requested_seconds) is not int
        or type(duration_cap) is not int
    ):
        raise Refuse("NOT_INT")
    if duration_cap != duration_hi():
        raise Refuse("BAD_CAP")
    if type(capped) is not bool:
        raise Refuse("BAD_FLAG")
    applied, asked, cut = apply_duration(requested_seconds)
    if seconds != applied or asked != requested_seconds or cut is not capped:
        raise Refuse("BAD_CAP")


def _seal_cents(cents: object) -> int:
    if isinstance(cents, str):
        _text(cents, PROMPT_CAP)
    return bound_int(cents, 0, MAX_CENTS)


def _seal_quote(
    model: object,
    prompt: object,
    seconds: object,
    requested_seconds: object,
    duration_cap: object,
    capped: object,
    cents: object,
    prompt_cap: object,
) -> tuple[str, str, int]:
    if type(prompt_cap) is not int:
        raise Refuse("NOT_INT")
    if prompt_cap != PROMPT_CAP:
        raise Refuse("BAD_CAP")
    chosen = _model(model)
    text = _prompt(prompt)
    _seal_duration(seconds, requested_seconds, duration_cap, capped)
    quote = _seal_cents(cents)
    return chosen, text, quote


def _credential(value: object) -> str:
    if isinstance(value, str) and value.strip() == "":
        raise Refuse("MISSING_CREDENTIAL")
    ident = _text(value, 64)
    if _CRED.fullmatch(ident) is None:
        raise Refuse("BAD_CREDENTIAL")
    return ident


def _piece(text: str) -> str:
    return f"{len(text)}:{text}"


def _plan_id(
    *,
    model: str,
    prompt: str,
    seconds: int,
    requested_seconds: int,
    cents: int,
    credential_id: str,
    capped: bool,
) -> str:
    parts = (
        _piece(SCHEMA),
        _piece(model),
        _piece(str(seconds)),
        _piece(str(requested_seconds)),
        _piece(str(cents)),
        _piece("1" if capped else "0"),
        _piece(credential_id),
        _piece(prompt),
    )
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()


def _rows(records: object) -> tuple[object, ...] | list[object]:
    if isinstance(records, (str, bytes, bytearray)):
        raise Refuse("BAD_PLAN")
    if isinstance(records, list):
        return records
    if isinstance(records, tuple):
        return records
    raise Refuse("BAD_PLAN")


def _as_plan(item: object) -> VideoPlan:
    if type(item) is not VideoPlan:
        raise Refuse("BAD_PLAN")
    return item


@dataclass(frozen=True, slots=True, kw_only=True)
class VideoRequest:
    """Priced clip before a credential is bound. Holding one does not render."""

    model: str
    prompt: str
    seconds: int
    requested_seconds: int
    duration_cap: int
    capped: bool
    cents: int
    prompt_cap: int
    spend_required: bool = True
    schema: str = SCHEMA

    def __post_init__(self) -> None:
        if type(self.schema) is not str or self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        if type(self.spend_required) is not bool:
            raise Refuse("BAD_FLAG")
        _seal_quote(
            self.model,
            self.prompt,
            self.seconds,
            self.requested_seconds,
            self.duration_cap,
            self.capped,
            self.cents,
            self.prompt_cap,
        )
        object.__setattr__(self, "spend_required", True)

    def __repr__(self) -> str:
        body = (
            f"VideoRequest(model={self.model!r}, seconds={self.seconds}, "
            f"requested_seconds={self.requested_seconds}, duration_cap={self.duration_cap}, "
            f"capped={self.capped}, cents={self.cents}, prompt_cap={self.prompt_cap}, "
            f"spend_required={self.spend_required}, schema={self.schema!r})"
        )
        return redact(body)


@dataclass(frozen=True, slots=True, kw_only=True)
class VideoPlan:
    """Credential-bound clip. `renders` stays false. Holding one does not render."""

    model: str
    prompt: str
    seconds: int
    requested_seconds: int
    duration_cap: int
    capped: bool
    cents: int
    prompt_cap: int
    credential_id: str
    spend_required: bool = True
    renders: bool = False
    schema: str = SCHEMA
    plan_id: str = ""

    def __post_init__(self) -> None:
        if type(self.schema) is not str or self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        if type(self.spend_required) is not bool or type(self.renders) is not bool:
            raise Refuse("BAD_FLAG")
        chosen, text, quote = _seal_quote(
            self.model,
            self.prompt,
            self.seconds,
            self.requested_seconds,
            self.duration_cap,
            self.capped,
            self.cents,
            self.prompt_cap,
        )
        ident = _credential(self.credential_id)
        object.__setattr__(self, "spend_required", True)
        object.__setattr__(self, "renders", False)
        expected = _plan_id(
            model=chosen,
            prompt=text,
            seconds=self.seconds,
            requested_seconds=self.requested_seconds,
            cents=quote,
            credential_id=ident,
            capped=self.capped,
        )
        if type(self.plan_id) is not str:
            raise Refuse("NOT_TEXT")
        if secret_shape(self.plan_id):
            raise Refuse("SECRET")
        if self.plan_id == "":
            object.__setattr__(self, "plan_id", expected)
            return
        if not const_eq(self.plan_id, expected):
            raise Refuse("BAD_PLAN")

    def __repr__(self) -> str:
        body = (
            f"VideoPlan(model={self.model!r}, seconds={self.seconds}, "
            f"requested_seconds={self.requested_seconds}, duration_cap={self.duration_cap}, "
            f"capped={self.capped}, cents={self.cents}, prompt_cap={self.prompt_cap}, "
            f"spend_required={self.spend_required}, credential_id={self.credential_id!r}, "
            f"renders={self.renders}, schema={self.schema!r}, plan_id={self.plan_id!r})"
        )
        return redact(body)


def _fields(
    model: object,
    prompt: object,
    seconds: object,
    prices: object,
    cap: object,
) -> tuple[str, str, int, int, bool, int, int]:
    recorded = apply_prompt_cap(cap)
    chosen = _allow(model)
    text = _prompt(prompt)
    quote = _lookup(chosen, prices)
    applied, asked, cut = apply_duration(seconds)
    return chosen, text, applied, asked, cut, quote, recorded


def request(
    model: object,
    prompt: object,
    seconds: object,
    prices: object,
    *,
    cap: object = None,
) -> VideoRequest:
    """Price one allowlisted clip. Does not bind a credential and does not render."""
    chosen, text, applied, asked, cut, quote, recorded = _fields(
        model, prompt, seconds, prices, cap
    )
    return VideoRequest(
        model=chosen,
        prompt=text,
        seconds=applied,
        requested_seconds=asked,
        duration_cap=duration_hi(),
        capped=cut,
        cents=quote,
        prompt_cap=recorded,
        spend_required=True,
        schema=SCHEMA,
    )


def plan(
    model: object,
    prompt: object,
    seconds: object,
    prices: object,
    credential_id: object,
    *,
    cap: object = None,
) -> VideoPlan:
    """Price one clip and bind a credential id. Does not render."""
    ident = _credential(credential_id)
    chosen, text, applied, asked, cut, quote, recorded = _fields(
        model, prompt, seconds, prices, cap
    )
    return VideoPlan(
        model=chosen,
        prompt=text,
        seconds=applied,
        requested_seconds=asked,
        duration_cap=duration_hi(),
        capped=cut,
        cents=quote,
        prompt_cap=recorded,
        credential_id=ident,
        spend_required=True,
        renders=False,
        schema=SCHEMA,
        plan_id="",
    )


def rebuild(records: object) -> tuple[VideoPlan, ...]:
    """Replay plans from the rows `plan` emitted. A repeated plan id refuses."""
    rows = _rows(records)
    if len(rows) == 0:
        raise Refuse("EMPTY")
    if len(rows) > _REBUILD_CAP:
        raise Refuse("BAD_PLAN")
    seen: set[str] = set()
    out: list[VideoPlan] = []
    for item in rows:
        chosen = _as_plan(item)
        if chosen.plan_id in seen:
            raise Refuse("REPLAY")
        seen.add(chosen.plan_id)
        out.append(replace(chosen))
    return tuple(out)


def run(plan: object) -> NoReturn:
    """Validate a plan, then refuse. This function does not render a video."""
    _as_plan(plan)
    raise Refuse("NOT_RENDER")


__all__ = [
    "ASK_CEILING",
    "MAX_CENTS",
    "MIN_SECONDS",
    "MODELS",
    "POLICY_SECONDS",
    "PROMPT_CAP",
    "SCHEMA",
    "VideoPlan",
    "VideoRequest",
    "apply_duration",
    "apply_prompt_cap",
    "duration_hi",
    "duration_lo",
    "plan",
    "rebuild",
    "request",
    "run",
]
