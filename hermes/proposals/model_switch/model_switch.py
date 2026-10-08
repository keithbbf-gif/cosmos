"""Pin one session model against a caller allowlist.

An id outside the list is refused. Nothing here rewrites ``auto`` onto
another model, calls a provider, or writes config.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final

from cosmos_hermes import Refuse, bound_int, bound_text, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-model_switch/1"
POLICY_CAP: Final[int] = 32
ASK_CAP: Final[int] = 1_000_000
MODEL_CAP: Final[int] = 128
SESSION_CAP: Final[int] = 64

_MODEL: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")
_SESSION: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_ROUTER: Final[re.Pattern[str]] = re.compile(r"auto|router", re.IGNORECASE)


def _plain(value: object, limit: int) -> str:
    # A str subclass can lie about equality. Membership sees a real str.
    if isinstance(value, str) and type(value) is not str:
        try:
            value = str.encode(value, "utf-8").decode("utf-8")
        except UnicodeError:
            raise Refuse("NOT_TEXT") from None
    text = bound_text(value, limit)
    if secret_shape(text):
        raise Refuse("SECRET")
    return text


def _path_shaped(text: str) -> bool:
    if "\\" in text or ".." in text:
        return True
    if "/" not in text:
        return False
    for part in text.split("/"):
        if part == "" or part == ".":
            return True
    return False


def _session_id(value: object) -> str:
    text = _plain(value, SESSION_CAP)
    if _SESSION.fullmatch(text) is None or _path_shaped(text):
        raise Refuse("BAD_SESSION")
    return text


def _model(value: object, *, empty_ok: bool) -> str:
    text = _plain(value, MODEL_CAP)
    if text == "":
        if empty_ok:
            return ""
        raise Refuse("BAD_MODEL")
    if _MODEL.fullmatch(text) is None or _path_shaped(text):
        raise Refuse("BAD_MODEL")
    return text


def _router_id(model_id: str) -> bool:
    return _ROUTER.search(model_id) is not None


def _effective(asked: int) -> int:
    if asked > POLICY_CAP:
        return POLICY_CAP
    return asked


def _ceiling(cap: object) -> tuple[int, int]:
    if type(cap) is not int:
        raise Refuse("NOT_INT")
    asked = bound_int(cap, 1, ASK_CAP)
    return _effective(asked), asked


def _recorded_caps(cap: object, asked_cap: object, policy_cap: object) -> tuple[int, int]:
    if type(policy_cap) is not int or policy_cap != POLICY_CAP:
        raise Refuse("BAD_CAP")
    if type(asked_cap) is not int:
        raise Refuse("NOT_INT")
    if asked_cap < 1 or asked_cap > ASK_CAP:
        raise Refuse("OUT_OF_RANGE", f"1..{ASK_CAP}")
    effective = _effective(asked_cap)
    if type(cap) is not int or cap != effective:
        raise Refuse("BAD_CAP")
    return effective, asked_cap


def _names(values: object, limit: int) -> tuple[str, ...]:
    # Exact list or tuple, read by index. A subclass or a generator is not a grant.
    if type(values) is not list and type(values) is not tuple:
        raise Refuse("BAD_ALLOW")
    count = len(values)
    if count == 0:
        raise Refuse("EMPTY_ALLOW")
    if count > limit:
        raise Refuse("OVERSIZE", str(limit))
    found: list[str] = []
    seen: set[str] = set()
    for index in range(count):
        name = _model(values[index], empty_ok=False)
        if name in seen:
            raise Refuse("DUPLICATE")
        seen.add(name)
        found.append(name)
    return tuple(found)


def _admits(model_id: str, names: tuple[str, ...]) -> bool:
    return model_id in set(names)


@dataclass(frozen=True, slots=True)
class Session:
    """One chat. ``pin`` is the model already in force, or empty when none is."""

    session_id: str
    pin: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "session_id", _session_id(self.session_id))
        object.__setattr__(self, "pin", _model(self.pin, empty_ok=True))


@dataclass(frozen=True, slots=True)
class Switch:
    """The pin change. ``previous`` is the old pin. ``pin`` is the new pin.

    ``allow`` is the grant that was checked. A pin outside it is ``PIN_REFUSED``.
    """

    schema: str
    session_id: str
    previous: str
    pin: str
    allow: tuple[str, ...]
    allow_routers: bool
    cap: int
    asked_cap: int
    policy_cap: int

    def __post_init__(self) -> None:
        if type(self.schema) is not str or self.schema != SCHEMA:
            raise Refuse("BAD_RECORD")
        session_id = _session_id(self.session_id)
        previous = _model(self.previous, empty_ok=True)
        chosen = _model(self.pin, empty_ok=False)
        if type(self.allow_routers) is not bool:
            raise Refuse("BAD_FLAG")
        effective, asked = _recorded_caps(self.cap, self.asked_cap, self.policy_cap)
        names = _names(self.allow, effective)
        if not _admits(chosen, names):
            raise Refuse("PIN_REFUSED")
        if not self.allow_routers and _router_id(chosen):
            raise Refuse("ROUTER")
        object.__setattr__(self, "schema", SCHEMA)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "previous", previous)
        object.__setattr__(self, "pin", chosen)
        object.__setattr__(self, "allow", names)
        object.__setattr__(self, "cap", effective)
        object.__setattr__(self, "asked_cap", asked)
        object.__setattr__(self, "policy_cap", POLICY_CAP)


def set_model(
    session: object,
    model: object,
    allow: object,
    allow_routers: object = False,
    *,
    cap: object = POLICY_CAP,
) -> Switch:
    """Record ``previous`` and the new pin when ``model`` is on ``allow``.

    An empty allowlist is ``EMPTY_ALLOW``. A model off the list is
    ``PIN_REFUSED``. There is no fallback onto another listed id. An id
    whose text contains ``auto`` or ``router`` is ``ROUTER`` unless
    ``allow_routers`` is true. The previous pin may already be a router id.
    A requested cap above ``POLICY_CAP`` is ignored and the policy cap is recorded.
    """
    if type(session) is not Session:
        raise Refuse("BAD_SESSION")
    session_id = _session_id(session.session_id)
    previous = _model(session.pin, empty_ok=True)
    chosen = _model(model, empty_ok=False)
    if type(allow_routers) is not bool:
        raise Refuse("BAD_FLAG")
    effective, asked = _ceiling(cap)
    names = _names(allow, effective)
    if not _admits(chosen, names):
        raise Refuse("PIN_REFUSED")
    if not allow_routers and _router_id(chosen):
        raise Refuse("ROUTER")
    return Switch(
        schema=SCHEMA,
        session_id=session_id,
        previous=previous,
        pin=chosen,
        allow=names,
        allow_routers=allow_routers,
        cap=effective,
        asked_cap=asked,
        policy_cap=POLICY_CAP,
    )


def rebuild(record: object) -> Switch:
    """Replay one switch. The same record comes back; a non-switch is ``BAD_RECORD``."""
    if type(record) is not Switch:
        raise Refuse("BAD_RECORD")
    return set_model(
        Session(record.session_id, record.previous),
        record.pin,
        record.allow,
        record.allow_routers,
        cap=record.asked_cap,
    )


__all__ = [
    "ASK_CAP",
    "MODEL_CAP",
    "POLICY_CAP",
    "SCHEMA",
    "SESSION_CAP",
    "Session",
    "Switch",
    "rebuild",
    "set_model",
]
