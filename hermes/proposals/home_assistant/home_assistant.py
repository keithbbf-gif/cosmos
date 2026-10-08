"""Home Assistant tool descriptors. classify returns CONFIRM. run calls nothing.

Four tools: ha_list_entities, ha_get_state, ha_list_services, ha_call_service.
The record is an approval descriptor. No REST, websocket, or device call.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, replace
from typing import Final, cast

from cosmos_hermes import Refuse, bound_int, bound_text, const_eq, redact, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-home_assistant/1"
CONFIRM: Final[str] = "CONFIRM"
FAILURE: Final[str] = "STALE"

POLICY_FIELDS: Final[int] = 4
POLICY_LIST: Final[int] = 32
POLICY_STATE: Final[int] = 1
POLICY_BUDGET: Final[int] = 80
POLICY_ITEMS: Final[int] = 32

ENTITY_CAP: Final[int] = 80
NAME_CAP: Final[int] = 64
AREA_CAP: Final[int] = 48
CRED_CAP: Final[int] = 64
MAX_STAMP: Final[int] = 4_102_444_800

TOOLS: Final[tuple[str, ...]] = (
    "ha_list_entities",
    "ha_get_state",
    "ha_list_services",
    "ha_call_service",
)

BLOCKED_DOMAINS: Final[tuple[str, ...]] = (
    "command_line",
    "hassio",
    "pyscript",
    "python_script",
    "rest_command",
    "shell_command",
)

_ZERO: Final[str] = "0" * 64
_KIND_SERVICE: Final[str] = "service"
_KIND_STATE: Final[str] = "state"
_KIND_LIST_ENTITIES: Final[str] = "list_entities"
_KIND_LIST_SERVICES: Final[str] = "list_services"
_KINDS: Final[frozenset[str]] = frozenset(
    {_KIND_SERVICE, _KIND_STATE, _KIND_LIST_ENTITIES, _KIND_LIST_SERVICES}
)
_LIST_KINDS: Final[frozenset[str]] = frozenset({_KIND_LIST_ENTITIES, _KIND_LIST_SERVICES})
_POLICY: Final[dict[str, int]] = {
    _KIND_SERVICE: POLICY_FIELDS,
    _KIND_STATE: POLICY_STATE,
    _KIND_LIST_ENTITIES: POLICY_LIST,
    _KIND_LIST_SERVICES: POLICY_LIST,
}

_BLOCKED: Final[frozenset[str]] = frozenset(BLOCKED_DOMAINS)
_META: Final[frozenset[str]] = frozenset(";|&`$<>(){}\\!\"'#*?~\n\r\t%^[]")
_COLORS: Final[frozenset[str]] = frozenset(
    {
        "blue",
        "cold_white",
        "green",
        "orange",
        "pink",
        "purple",
        "red",
        "warm_white",
        "white",
        "yellow",
    }
)
_HVAC: Final[frozenset[str]] = frozenset(
    {"auto", "cool", "dry", "fan_only", "heat", "heat_cool", "off"}
)
_NONE: Final[frozenset[str]] = frozenset()

_SERVICES: Final[dict[str, frozenset[str]]] = {
    "climate": frozenset(
        {"set_hvac_mode", "set_temperature", "toggle", "turn_off", "turn_on"}
    ),
    "cover": frozenset(
        {"close_cover", "open_cover", "set_cover_position", "stop_cover", "toggle"}
    ),
    "fan": frozenset({"set_percentage", "toggle", "turn_off", "turn_on"}),
    "light": frozenset({"toggle", "turn_off", "turn_on"}),
    "media_player": frozenset(
        {
            "media_pause",
            "media_play",
            "media_stop",
            "set_volume_level",
            "toggle",
            "turn_off",
            "turn_on",
        }
    ),
    "scene": frozenset({"turn_on"}),
    "script": frozenset({"toggle", "turn_off", "turn_on"}),
    "switch": frozenset({"toggle", "turn_off", "turn_on"}),
}

CALL_DOMAINS: Final[tuple[str, ...]] = tuple(sorted(_SERVICES))
_CALL: Final[frozenset[str]] = frozenset(CALL_DOMAINS)
_READ_EXTRA: Final[tuple[str, ...]] = (
    "alarm_control_panel",
    "binary_sensor",
    "camera",
    "lock",
    "person",
    "sensor",
    "weather",
)
READ_DOMAINS: Final[tuple[str, ...]] = tuple(sorted(set(CALL_DOMAINS).union(_READ_EXTRA)))
_READ: Final[frozenset[str]] = frozenset(READ_DOMAINS)

SERVICES: Final[tuple[str, ...]] = tuple(
    sorted(f"{domain}.{name}" for domain, names in _SERVICES.items() for name in names)
)

_DATA: Final[dict[tuple[str, str], frozenset[str]]] = {
    ("climate", "set_hvac_mode"): frozenset({"hvac_mode"}),
    ("climate", "set_temperature"): frozenset({"hvac_mode", "temperature"}),
    ("cover", "set_cover_position"): frozenset({"position"}),
    ("fan", "set_percentage"): frozenset({"percentage"}),
    ("light", "turn_on"): frozenset({"brightness", "color_name"}),
    ("media_player", "set_volume_level"): frozenset({"volume_level"}),
}
_INTS: Final[dict[str, tuple[int, int]]] = {
    "brightness": (0, 255),
    "percentage": (0, 100),
    "position": (0, 100),
    "temperature": (0, 40),
    "volume_level": (0, 100),
}

_ENTITY: Final[re.Pattern[str]] = re.compile(r"^[a-z_][a-z0-9_]*\.[a-z0-9_]+$")
_NAME: Final[re.Pattern[str]] = re.compile(r"^[a-z_][a-z0-9_]*$")
_AREA: Final[re.Pattern[str]] = re.compile(r"^[a-z0-9](?:[a-z0-9 _-]{0,47})$")
_CRED: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$")
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")
_DIGITS: Final[re.Pattern[str]] = re.compile(r"^[0-9]+$")


def _has_meta(text: str) -> bool:
    return any(char in _META for char in text)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _cred(value: object) -> str:
    if value is None:
        raise Refuse("NO_CRED")
    text = bound_text(value, CRED_CAP)
    if text == "":
        raise Refuse("NO_CRED")
    if secret_shape(text):
        raise Refuse("SECRET")
    if _CRED.fullmatch(text) is None:
        raise Refuse("BAD_CRED")
    return text


def _clamp(value: object, policy: int, label: str) -> tuple[int, int, tuple[str, ...]]:
    """Ignore a request above `policy`. A lower request at or above 1 is kept."""
    if value is None:
        return policy, policy, ()
    if type(value) is not int:
        raise Refuse("NOT_INT")
    if value < 1:
        raise Refuse("OUT_OF_RANGE", f"1..{policy}")
    if value > policy:
        return policy, value, (label,)
    return value, value, ()


def _check_clamp(
    applied: object,
    requested: object,
    clamped: object,
    policy: int,
    label: str,
) -> None:
    if type(applied) is not int or type(requested) is not int:
        raise Refuse("NOT_INT")
    if type(clamped) is not tuple:
        raise Refuse("BAD_CAP")
    got_applied, got_requested, got_clamped = _clamp(requested, policy, label)
    if applied != got_applied or requested != got_requested or clamped != got_clamped:
        raise Refuse("BAD_CAP")


def _split_entity(value: object) -> tuple[str, str]:
    text = bound_text(value, ENTITY_CAP)
    if text == "":
        raise Refuse("EMPTY")
    if secret_shape(text):
        raise Refuse("SECRET")
    if _has_meta(text) or _ENTITY.fullmatch(text) is None:
        raise Refuse("BAD_ENTITY")
    parts = text.split(".")
    if len(parts) != 2:
        raise Refuse("BAD_ENTITY")
    domain = parts[0]
    name = parts[1]
    if domain == "" or name == "" or "." in name:
        raise Refuse("BAD_ENTITY")
    if domain in _BLOCKED:
        raise Refuse("BLOCKED_DOMAIN")
    if domain not in _READ:
        raise Refuse("BAD_DOMAIN")
    return domain, name


def _action(value: object) -> str:
    text = bound_text(value, NAME_CAP)
    if text == "":
        raise Refuse("EMPTY")
    if secret_shape(text):
        raise Refuse("SECRET")
    if _has_meta(text):
        raise Refuse("BAD_ENTITY")
    if _NAME.fullmatch(text) is None:
        raise Refuse("BAD_SERVICE")
    return text


def _optional_domain(value: object) -> str:
    text = bound_text(value, NAME_CAP)
    if text == "":
        return ""
    if secret_shape(text):
        raise Refuse("SECRET")
    if _has_meta(text):
        raise Refuse("BAD_ENTITY")
    if _NAME.fullmatch(text) is None:
        raise Refuse("BAD_DOMAIN")
    if text in _BLOCKED:
        raise Refuse("BLOCKED_DOMAIN")
    if text not in _READ:
        raise Refuse("BAD_DOMAIN")
    return text


def _area(value: object) -> str:
    text = bound_text(value, AREA_CAP)
    if text == "":
        return ""
    if secret_shape(text):
        raise Refuse("SECRET")
    if _has_meta(text):
        raise Refuse("BAD_ENTITY")
    if text != text.strip() or "  " in text or _AREA.fullmatch(text) is None:
        raise Refuse("BAD_AREA")
    return text


def _field_value(key: str, value: object) -> str:
    if key in _INTS:
        lo, hi = _INTS[key]
        return str(bound_int(value, lo, hi))
    if type(value) is not str:
        raise Refuse("NOT_TEXT")
    text = bound_text(value, NAME_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    if _has_meta(text):
        raise Refuse("BAD_ENTITY")
    if key == "color_name" and text in _COLORS:
        return text
    if key == "hvac_mode" and text in _HVAC:
        return text
    raise Refuse("BAD_DATA")


def _scan_secret(value: object) -> None:
    if type(value) is not str:
        return
    text = bound_text(value, NAME_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    if _has_meta(text):
        raise Refuse("BAD_ENTITY")


def _field_sort(field: Field) -> str:
    return field.key


def _parse_data(
    domain: str, action: str, raw: object, cap: int
) -> tuple[Field, ...]:
    if raw is None:
        return ()
    if type(raw) is not dict:
        raise Refuse("NOT_MAP")
    mapping = cast(dict[object, object], raw)
    allowed = _DATA.get((domain, action), _NONE)
    if len(mapping) > cap:
        for key, value in mapping.items():
            _scan_secret(key)
            _scan_secret(value)
        raise Refuse("BAD_DATA")
    built: list[Field] = []
    for key, value in mapping.items():
        if type(key) is not str:
            raise Refuse("NOT_TEXT")
        name = bound_text(key, NAME_CAP)
        if secret_shape(name):
            raise Refuse("SECRET")
        if _has_meta(name):
            raise Refuse("BAD_ENTITY")
        if name not in allowed:
            raise Refuse("BAD_DATA")
        built.append(Field(key=name, value=_field_value(name, value)))
    built.sort(key=_field_sort)
    return tuple(built)


def _content_line(
    kind: str,
    entity: str,
    action: str,
    domain: str,
    area: str,
    data: tuple[Field, ...],
    cred_id: str,
    cap: int,
    requested_cap: int,
    clamped: tuple[str, ...],
) -> str:
    body = ",".join(f"{field.key}={field.value}" for field in data)
    flags = ",".join(clamped)
    return (
        f"{SCHEMA}|{kind}|{entity}|{action}|{domain}|{area}|{body}|"
        f"{cred_id}|{cap}|{requested_cap}|{flags}"
    )


def _weight_of(
    entity: str,
    action: str,
    domain: str,
    area: str,
    data: tuple[Field, ...],
) -> int:
    total = len(entity) + len(action) + len(domain) + len(area)
    for field in data:
        total += len(field.key) + len(field.value) + 1
    if total < 1:
        return 1
    return total


def _rows(items: object) -> tuple[object, ...]:
    if type(items) is not list and type(items) is not tuple:
        raise Refuse("NOT_LIST")
    boxed = cast(list[object] | tuple[object, ...], items)
    if len(boxed) > POLICY_ITEMS:
        raise Refuse("OVERSIZE", str(POLICY_ITEMS))
    return tuple(boxed)


def _hex64(value: object) -> str:
    if type(value) is not str or _HEX.fullmatch(value) is None:
        raise Refuse("BAD_RECORD")
    return value


def _count(value: object, *, empty_ok: bool) -> int:
    if type(value) is not int:
        raise Refuse("NOT_INT")
    if value < 0 or (value == 0 and not empty_ok):
        raise Refuse("BAD_RECORD")
    return value


def _canon_stored(key: str, value: str) -> None:
    if key in _INTS:
        lo, hi = _INTS[key]
        if _DIGITS.fullmatch(value) is None or (len(value) > 1 and value.startswith("0")):
            raise Refuse("BAD_DATA")
        number = int(value)
        if number < lo or number > hi or str(number) != value:
            raise Refuse("OUT_OF_RANGE", f"{lo}..{hi}")
        return
    if key == "color_name" and value in _COLORS:
        return
    if key == "hvac_mode" and value in _HVAC:
        return
    raise Refuse("BAD_DATA")


def _scan_fields(data: tuple[Field, ...]) -> None:
    for field in data:
        if type(field) is not Field:
            raise Refuse("BAD_DATA")
        if secret_shape(field.key) or secret_shape(field.value):
            raise Refuse("SECRET")
        if _has_meta(field.key) or _has_meta(field.value):
            raise Refuse("BAD_ENTITY")


def _audit_data(domain: str, action: str, data: tuple[Field, ...], cap: int) -> None:
    _scan_fields(data)
    if len(data) > cap:
        raise Refuse("BAD_DATA")
    allowed = _DATA.get((domain, action), _NONE)
    keys: list[str] = []
    for field in data:
        if field.key not in allowed:
            raise Refuse("BAD_DATA")
        _canon_stored(field.key, field.value)
        keys.append(field.key)
    if len(set(keys)) != len(keys):
        raise Refuse("DUPLICATE")
    if keys != sorted(keys):
        raise Refuse("BAD_RECORD")


def _reject_extra_text(value: str, *, code: str) -> None:
    if value == "":
        return
    if secret_shape(value):
        raise Refuse("SECRET")
    if _has_meta(value):
        raise Refuse("BAD_ENTITY")
    raise Refuse(code)


def _audit_call(call: Call) -> None:
    if type(call.schema) is not str or call.schema != SCHEMA:
        raise Refuse("BAD_SCHEMA")
    if type(call.code) is not str or call.code != CONFIRM:
        raise Refuse("UNCLASSIFIED")
    if type(call.kind) is not str or call.kind not in _KINDS:
        raise Refuse("BAD_KIND")
    if type(call.entity) is not str or type(call.action) is not str:
        raise Refuse("NOT_TEXT")
    if type(call.domain) is not str or type(call.area) is not str:
        raise Refuse("NOT_TEXT")
    if type(call.data) is not tuple:
        raise Refuse("BAD_DATA")
    checked = _cred(call.cred_id)
    if not const_eq(checked, call.cred_id):
        raise Refuse("BAD_CRED")
    if type(call.attempt) is not int:
        raise Refuse("NOT_INT")
    if call.attempt < 1 or call.attempt > 2:
        raise Refuse("OUT_OF_RANGE", "1..2")
    policy = _POLICY[call.kind]
    _check_clamp(call.cap, call.requested_cap, call.clamped, policy, "cap")
    if call.kind in _LIST_KINDS:
        if call.entity != "":
            _split_entity(call.entity)
            raise Refuse("BAD_KIND")
        if call.action != "":
            _action(call.action)
            raise Refuse("BAD_KIND")
        if call.data != ():
            _scan_fields(call.data)
            raise Refuse("BAD_KIND")
        domain = _optional_domain(call.domain)
        if domain != call.domain:
            raise Refuse("BAD_DOMAIN")
        if call.kind == _KIND_LIST_SERVICES:
            _reject_extra_text(call.area, code="BAD_AREA")
        else:
            area = _area(call.area)
            if area != call.area:
                raise Refuse("BAD_AREA")
    elif call.kind == _KIND_STATE:
        domain, _name = _split_entity(call.entity)
        if call.domain != domain:
            raise Refuse("BAD_DOMAIN")
        _reject_extra_text(call.action, code="BAD_KIND")
        _reject_extra_text(call.area, code="BAD_AREA")
        if call.data != ():
            _scan_fields(call.data)
            raise Refuse("BAD_KIND")
    else:
        domain, _name = _split_entity(call.entity)
        if domain not in _CALL:
            raise Refuse("BAD_DOMAIN")
        if call.domain != domain:
            raise Refuse("BAD_DOMAIN")
        verb = _action(call.action)
        if verb != call.action or verb not in _SERVICES[domain]:
            raise Refuse("BAD_SERVICE")
        _reject_extra_text(call.area, code="BAD_AREA")
        _audit_data(domain, verb, call.data, call.cap)
    digest = _sha(
        _content_line(
            call.kind,
            call.entity,
            call.action,
            call.domain,
            call.area,
            call.data,
            call.cred_id,
            call.cap,
            call.requested_cap,
            call.clamped,
        )
    )
    if digest != call.digest:
        raise Refuse("BROKEN_CHAIN")


def _step_line(prev: str, call_digest: str, source: int, cost: int) -> str:
    return f"{prev}|{call_digest}|{source}|{cost}"


def _skip_line(skip: Skip) -> str:
    return f"skip|{skip.source}|{skip.cost}|{skip.reason}|{skip.call.digest}"


def _header(
    cred_id: str,
    now: int,
    seen: int | None,
    budget: int,
    requested_budget: int,
    clamped: tuple[str, ...],
) -> str:
    seen_text = "" if seen is None else str(seen)
    flags = ",".join(clamped)
    return f"{SCHEMA}|{cred_id}|{now}|{seen_text}|{budget}|{requested_budget}|{flags}"


def _plan_digest(
    cred_id: str,
    now: int,
    seen: int | None,
    budget: int,
    requested_budget: int,
    clamped: tuple[str, ...],
    steps: tuple[Step, ...],
    skipped: tuple[Skip, ...],
) -> str:
    parts = [_header(cred_id, now, seen, budget, requested_budget, clamped)]
    for skip in skipped:
        parts.append(_skip_line(skip))
    for step in steps:
        parts.append(step.digest)
    return _sha("\n".join(parts))


def _owned(call: Call, cred_id: str) -> None:
    _audit_call(call)
    if call.schema != SCHEMA:
        raise Refuse("BAD_SCHEMA")
    if not const_eq(call.cred_id, cred_id):
        raise Refuse("MISMATCH")


def _verify_plan(plan: Plan) -> None:
    if type(plan.schema) is not str or plan.schema != SCHEMA:
        raise Refuse("BAD_SCHEMA")
    cred = _cred(plan.cred_id)
    if not const_eq(cred, plan.cred_id):
        raise Refuse("BAD_CRED")
    stamp = bound_int(plan.now, 0, MAX_STAMP)
    if stamp != plan.now:
        raise Refuse("OUT_OF_RANGE")
    if plan.seen is not None:
        prior = bound_int(plan.seen, 0, MAX_STAMP)
        if prior != plan.seen or stamp < prior:
            raise Refuse("STALE")
    _check_clamp(plan.budget, plan.requested_budget, plan.clamped, POLICY_BUDGET, "budget")
    if type(plan.steps) is not tuple or type(plan.skipped) is not tuple:
        raise Refuse("BAD_RECORD")
    total = len(plan.steps) + len(plan.skipped)
    if total > POLICY_ITEMS:
        raise Refuse("OVERSIZE", str(POLICY_ITEMS))
    digests: set[str] = set()
    occupied: dict[int, Step | Skip] = {}
    for step in plan.steps:
        if type(step) is not Step:
            raise Refuse("BAD_RECORD")
        _owned(step.call, cred)
        if step.call.digest in digests:
            raise Refuse("DUPLICATE")
        digests.add(step.call.digest)
        if step.source in occupied:
            raise Refuse("BAD_RECORD")
        occupied[step.source] = step
    for skip in plan.skipped:
        if type(skip) is not Skip:
            raise Refuse("BAD_RECORD")
        _owned(skip.call, cred)
        if skip.call.digest in digests:
            raise Refuse("DUPLICATE")
        digests.add(skip.call.digest)
        if skip.source in occupied:
            raise Refuse("BAD_RECORD")
        occupied[skip.source] = skip
    if set(occupied) != set(range(total)):
        raise Refuse("BAD_RECORD")
    spent = 0
    prev = _ZERO
    kept = 0
    for source in range(total):
        item = occupied[source]
        if type(item) is Step:
            if item is not plan.steps[kept]:
                raise Refuse("BAD_RECORD")
            cost = _weight_of(
                item.call.entity,
                item.call.action,
                item.call.domain,
                item.call.area,
                item.call.data,
            )
            if item.cost != cost or cost > plan.budget - spent:
                raise Refuse("BAD_RECORD")
            if item.prev != prev:
                raise Refuse("BROKEN_CHAIN")
            expect = _sha(_step_line(prev, item.call.digest, item.source, item.cost))
            if item.digest != expect:
                raise Refuse("BROKEN_CHAIN")
            prev = item.digest
            spent += cost
            kept += 1
            continue
        if type(item) is not Skip:
            raise Refuse("BAD_RECORD")
        cost = _weight_of(
            item.call.entity,
            item.call.action,
            item.call.domain,
            item.call.area,
            item.call.data,
        )
        if item.reason != "BUDGET" or item.cost != cost or cost <= plan.budget - spent:
            raise Refuse("BAD_RECORD")
    expect_plan = _plan_digest(
        plan.cred_id,
        plan.now,
        plan.seen,
        plan.budget,
        plan.requested_budget,
        plan.clamped,
        plan.steps,
        plan.skipped,
    )
    if expect_plan != plan.digest:
        raise Refuse("BROKEN_CHAIN")


@dataclass(frozen=True, slots=True, kw_only=True)
class Field:
    """One service-data pair. The value is canonical text, not a live command."""

    key: str
    value: str

    def __post_init__(self) -> None:
        key = bound_text(self.key, NAME_CAP)
        value = bound_text(self.value, NAME_CAP)
        if key != self.key or value != self.value or key == "" or value == "":
            raise Refuse("BAD_DATA")
        if secret_shape(key) or secret_shape(value):
            raise Refuse("SECRET")

    def __repr__(self) -> str:
        return redact(f"Field(key={self.key!r}, value={self.value!r})")


@dataclass(frozen=True, slots=True, kw_only=True)
class Call:
    """One held tool call. `code` is CONFIRM. Holding it does not dispatch it."""

    schema: str
    kind: str
    code: str
    entity: str
    action: str
    domain: str
    area: str
    data: tuple[Field, ...]
    cred_id: str
    cap: int
    requested_cap: int
    clamped: tuple[str, ...]
    attempt: int
    digest: str

    def __post_init__(self) -> None:
        _audit_call(self)

    def __repr__(self) -> str:
        return redact(
            f"Call(kind={self.kind!r}, entity={self.entity!r}, "
            f"action={self.action!r}, cap={self.cap})"
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class Step:
    """One kept plan row. `prev` links the prior kept digest."""

    call: Call
    prev: str
    digest: str
    source: int
    cost: int

    def __post_init__(self) -> None:
        if type(self.call) is not Call:
            raise Refuse("BAD_KIND")
        _hex64(self.prev)
        _hex64(self.digest)
        _count(self.source, empty_ok=True)
        _count(self.cost, empty_ok=False)

    def __repr__(self) -> str:
        return redact(f"Step(source={self.source}, cost={self.cost}, call={self.call!r})")


@dataclass(frozen=True, slots=True, kw_only=True)
class Skip:
    """One call the budget did not take. Later calls are still considered."""

    call: Call
    source: int
    cost: int
    reason: str

    def __post_init__(self) -> None:
        if type(self.call) is not Call:
            raise Refuse("BAD_KIND")
        _count(self.source, empty_ok=True)
        _count(self.cost, empty_ok=False)
        if self.reason != "BUDGET":
            raise Refuse("BAD_RECORD")

    def __repr__(self) -> str:
        return redact(
            f"Skip(source={self.source}, cost={self.cost}, reason={self.reason!r})"
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class Plan:
    """A budgeted list of held calls. Rebuilding it replays the same rows."""

    schema: str
    cred_id: str
    now: int
    seen: int | None
    budget: int
    requested_budget: int
    clamped: tuple[str, ...]
    steps: tuple[Step, ...]
    skipped: tuple[Skip, ...]
    digest: str

    def __post_init__(self) -> None:
        _verify_plan(self)

    def __repr__(self) -> str:
        return redact(
            f"Plan(steps={len(self.steps)}, skipped={len(self.skipped)}, budget={self.budget})"
        )


class Home:
    """Disabled until `enable` is given a credential id. There is no off switch."""

    __slots__ = ("_cred", "_on")

    def __init__(self) -> None:
        self._cred = ""
        self._on = False

    def __repr__(self) -> str:
        state = "enabled" if self._on else "disabled"
        return redact(f"Home({state})")

    @property
    def enabled(self) -> bool:
        return self._on

    @enabled.setter
    def enabled(self, value: object) -> None:
        del value
        raise Refuse("UNCLASSIFIED")

    @property
    def credential_id(self) -> str:
        return self._cred

    @credential_id.setter
    def credential_id(self, value: object) -> None:
        del value
        raise Refuse("UNCLASSIFIED")

    def enable(self, cred_id: object = None) -> None:
        """Arm descriptors for one credential id. A different second id refuses."""
        cred = _cred(cred_id)
        if self._on:
            if not const_eq(self._cred, cred):
                raise Refuse("MISMATCH")
            return
        self._cred = cred
        self._on = True

    def service(
        self,
        entity: object,
        action: object,
        data: object = None,
        *,
        cap: object = None,
    ) -> Call:
        """Describe ha_call_service. The device is not called."""
        if not self._on:
            raise Refuse("DISABLED")
        applied, requested, clamped = _clamp(cap, POLICY_FIELDS, "cap")
        domain, _name = _split_entity(entity)
        if domain not in _CALL:
            raise Refuse("BAD_DOMAIN")
        verb = _action(action)
        if verb not in _SERVICES[domain]:
            raise Refuse("BAD_SERVICE")
        fields = _parse_data(domain, verb, data, applied)
        return self._make(
            kind=_KIND_SERVICE,
            entity=bound_text(entity, ENTITY_CAP),
            action=verb,
            domain=domain,
            area="",
            data=fields,
            cap=applied,
            requested_cap=requested,
            clamped=clamped,
        )

    def state(self, entity: object, *, cap: object = None) -> Call:
        """Describe ha_get_state. The sensor is not read."""
        if not self._on:
            raise Refuse("DISABLED")
        applied, requested, clamped = _clamp(cap, POLICY_STATE, "cap")
        domain, _name = _split_entity(entity)
        return self._make(
            kind=_KIND_STATE,
            entity=bound_text(entity, ENTITY_CAP),
            action="",
            domain=domain,
            area="",
            data=(),
            cap=applied,
            requested_cap=requested,
            clamped=clamped,
        )

    def list_entities(
        self,
        domain: object = "",
        area: object = "",
        *,
        cap: object = None,
    ) -> Call:
        """Describe ha_list_entities. No entity list is fetched."""
        if not self._on:
            raise Refuse("DISABLED")
        applied, requested, clamped = _clamp(cap, POLICY_LIST, "cap")
        chosen = _optional_domain(domain)
        room = _area(area)
        return self._make(
            kind=_KIND_LIST_ENTITIES,
            entity="",
            action="",
            domain=chosen,
            area=room,
            data=(),
            cap=applied,
            requested_cap=requested,
            clamped=clamped,
        )

    def list_services(self, domain: object = "", *, cap: object = None) -> Call:
        """Describe ha_list_services. No service list is fetched."""
        if not self._on:
            raise Refuse("DISABLED")
        applied, requested, clamped = _clamp(cap, POLICY_LIST, "cap")
        chosen = _optional_domain(domain)
        return self._make(
            kind=_KIND_LIST_SERVICES,
            entity="",
            action="",
            domain=chosen,
            area="",
            data=(),
            cap=applied,
            requested_cap=requested,
            clamped=clamped,
        )

    def plan(
        self,
        items: object,
        *,
        now: object,
        budget: object = None,
        seen: object = None,
    ) -> Plan:
        """Keep calls that fit the remaining budget. Skip the ones that do not."""
        if not self._on:
            raise Refuse("DISABLED")
        rows = _rows(items)
        stamp = bound_int(now, 0, MAX_STAMP)
        prior: int | None
        if seen is None:
            prior = None
        else:
            prior = bound_int(seen, 0, MAX_STAMP)
            if stamp < prior:
                raise Refuse("STALE")
        applied, requested, clamped = _clamp(budget, POLICY_BUDGET, "budget")
        cred = self._cred
        steps: list[Step] = []
        skips: list[Skip] = []
        seen_digest: set[str] = set()
        spent = 0
        prev = _ZERO
        for source, item in enumerate(rows):
            if type(item) is not Call:
                raise Refuse("BAD_KIND")
            if item.schema != SCHEMA:
                raise Refuse("BAD_SCHEMA")
            if not const_eq(item.cred_id, cred):
                raise Refuse("MISMATCH")
            if item.digest in seen_digest:
                raise Refuse("DUPLICATE")
            seen_digest.add(item.digest)
            cost = _weight_of(item.entity, item.action, item.domain, item.area, item.data)
            if cost > applied - spent:
                skips.append(Skip(call=item, source=source, cost=cost, reason="BUDGET"))
                continue
            digest = _sha(_step_line(prev, item.digest, source, cost))
            steps.append(
                Step(call=item, prev=prev, digest=digest, source=source, cost=cost)
            )
            prev = digest
            spent += cost
        kept = tuple(steps)
        held = tuple(skips)
        plan_digest = _plan_digest(
            cred, stamp, prior, applied, requested, clamped, kept, held
        )
        return Plan(
            schema=SCHEMA,
            cred_id=cred,
            now=stamp,
            seen=prior,
            budget=applied,
            requested_budget=requested,
            clamped=clamped,
            steps=kept,
            skipped=held,
            digest=plan_digest,
        )

    def _make(
        self,
        *,
        kind: str,
        entity: str,
        action: str,
        domain: str,
        area: str,
        data: tuple[Field, ...],
        cap: int,
        requested_cap: int,
        clamped: tuple[str, ...],
    ) -> Call:
        digest = _sha(
            _content_line(
                kind,
                entity,
                action,
                domain,
                area,
                data,
                self._cred,
                cap,
                requested_cap,
                clamped,
            )
        )
        return Call(
            schema=SCHEMA,
            kind=kind,
            code=CONFIRM,
            entity=entity,
            action=action,
            domain=domain,
            area=area,
            data=data,
            cred_id=self._cred,
            cap=cap,
            requested_cap=requested_cap,
            clamped=clamped,
            attempt=1,
            digest=digest,
        )


def catalog(domain: object) -> tuple[str, ...]:
    """Return the call services this module would allow. This does not query a host."""
    text = bound_text(domain, NAME_CAP)
    if text == "":
        raise Refuse("EMPTY")
    if secret_shape(text):
        raise Refuse("SECRET")
    if _has_meta(text):
        raise Refuse("BAD_ENTITY")
    if _NAME.fullmatch(text) is None:
        raise Refuse("BAD_DOMAIN")
    if text in _BLOCKED:
        raise Refuse("BLOCKED_DOMAIN")
    if text not in _READ:
        raise Refuse("BAD_DOMAIN")
    allowed = _SERVICES.get(text)
    if allowed is None:
        return ()
    return tuple(sorted(allowed))


def classify(call: object) -> str:
    """Return CONFIRM for one valid call. Anything else refuses."""
    if type(call) is not Call:
        raise Refuse("UNCLASSIFIED")
    _audit_call(call)
    return CONFIRM


def run(call: object) -> None:
    """Never call Home Assistant. A legal call still raises NOT_RUN."""
    classify(call)
    raise Refuse("NOT_RUN")


def retry(call: object, failure: object) -> Call:
    """One confirming retry, and only after STALE. The device is still not called."""
    if type(call) is not Call:
        raise Refuse("UNCLASSIFIED")
    _audit_call(call)
    if failure is None:
        raise Refuse("EMPTY")
    label = bound_text(failure, NAME_CAP)
    if label == "":
        raise Refuse("EMPTY")
    if secret_shape(label):
        raise Refuse("SECRET")
    if not const_eq(label, FAILURE):
        raise Refuse("NO_RETRY")
    if call.attempt >= 2:
        raise Refuse("RETRY_CAP")
    return replace(call, attempt=call.attempt + 1)


def rebuild(plan: object) -> Plan:
    """Replay one plan snapshot. The result equals the input. Nothing is executed."""
    if type(plan) is not Plan:
        raise Refuse("BAD_RECORD")
    fresh = Plan(
        schema=plan.schema,
        cred_id=plan.cred_id,
        now=plan.now,
        seen=plan.seen,
        budget=plan.budget,
        requested_budget=plan.requested_budget,
        clamped=plan.clamped,
        steps=plan.steps,
        skipped=plan.skipped,
        digest=plan.digest,
    )
    if fresh != plan:
        raise Refuse("BROKEN_CHAIN")
    return fresh


def weight(call: object) -> int:
    """Return the plan cost of one valid call."""
    if type(call) is not Call:
        raise Refuse("BAD_KIND")
    _audit_call(call)
    return _weight_of(call.entity, call.action, call.domain, call.area, call.data)


__all__ = [
    "AREA_CAP",
    "BLOCKED_DOMAINS",
    "CALL_DOMAINS",
    "CONFIRM",
    "CRED_CAP",
    "Call",
    "ENTITY_CAP",
    "FAILURE",
    "Field",
    "Home",
    "MAX_STAMP",
    "NAME_CAP",
    "POLICY_BUDGET",
    "POLICY_FIELDS",
    "POLICY_ITEMS",
    "POLICY_LIST",
    "POLICY_STATE",
    "Plan",
    "READ_DOMAINS",
    "SCHEMA",
    "SERVICES",
    "Skip",
    "Step",
    "TOOLS",
    "catalog",
    "classify",
    "rebuild",
    "retry",
    "run",
    "weight",
]
