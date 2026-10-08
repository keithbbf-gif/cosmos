"""Parse a Hermes cadence into a clock vehicle. Does not schedule or spawn."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, replace
from decimal import Decimal, InvalidOperation
from typing import NamedTuple, NoReturn

from cosmos_hermes import Refuse, bound_text, const_eq, secret_shape

SCHEMA = "cosmos-hermes-cron/1"
POLICY_CAP = 256
FLOOR_S = 60.0
MAX_INTERVAL_S = 31_536_000  # 365 days. schtasks cannot be asked to go past this.
# schtasks /mo ceilings: minute 1439, hourly 23, daily 365, weekly 52.
_MINUTE_MAX = 1439
_HOUR_MAX = 23
_DAY_MAX = 365
_WEEK_MAX = 52
MODES = frozenset({"schtasks", "detached_daemon", "onlogon"})
_SC = frozenset({"minute", "HOURLY", "DAILY", "WEEKLY", "MONTHLY", "onlogon"})
# Cron 0 and 7 are both Sunday. Lists are stored Monday-first, one label each.
_WEEK_ORDER = ("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")
_DOW_NUM = {0: "SUN", 1: "MON", 2: "TUE", 3: "WED", 4: "THU", 5: "FRI", 6: "SAT", 7: "SUN"}
_POS = {label: number for number, label in _DOW_NUM.items() if number < 7}
_DOW_NAMES = {
    "sun": "SUN",
    "sunday": "SUN",
    "mon": "MON",
    "monday": "MON",
    "tue": "TUE",
    "tuesday": "TUE",
    "wed": "WED",
    "wednesday": "WED",
    "thu": "THU",
    "thursday": "THU",
    "fri": "FRI",
    "friday": "FRI",
    "sat": "SAT",
    "saturday": "SAT",
}
_WEEKDAYS = ",".join(_WEEK_ORDER[:5])
_UNIT_SECONDS = {
    "s": 1,
    "sec": 1,
    "secs": 1,
    "second": 1,
    "seconds": 1,
    "m": 60,
    "min": 60,
    "mins": 60,
    "minute": 60,
    "minutes": 60,
    "h": 3600,
    "hr": 3600,
    "hrs": 3600,
    "hour": 3600,
    "hours": 3600,
}
_ONCE = ("--once",)
_LOOP = ("--loop",)

_WS = re.compile(r"\s+")
_ATOM = r"(?:\d+|[a-z]+)"
_FIELD = re.compile(rf"^(?:\*|\*/[1-9]\d*|{_ATOM}(?:-{_ATOM})?(?:,{_ATOM}(?:-{_ATOM})?)*)$")
_ST = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")
_ONLOGON = re.compile(r"^(?:on logon|at logon|onlogon|on-logon|on login|at login|on-login)$")
_HOURLY = re.compile(r"^(?:hourly|every hour|once an hour)$")
_WEEKLY = re.compile(r"^(?:weekly|every week)$")
_DAILY_AT = re.compile(r"^(?:every day at|daily at) ([0-9]{1,2}):([0-9]{2})$")
_WEEKDAY_AT = re.compile(r"^(?:every weekday|weekdays) at ([0-9]{1,2}):([0-9]{2})$")
_EVERY = re.compile(
    r"^every (\d+(?:\.\d+)?) ?"
    r"(seconds|second|secs|sec|minutes|minute|mins|min|hours|hour|hrs|hr|s|m|h)$"
)
_IN_PROCESS = re.compile(r"(?:^|\s)in this process(?:\s|$)|^(?:run|start|register)(?:\s|$)")


class _Tok(NamedTuple):
    kind: str
    number: int | None
    name: str | None


def _canon_forms() -> frozenset[str]:
    forms: set[str] = set()
    width = len(_WEEK_ORDER)
    for mask in range(1, 1 << width):
        picked = [name for bit, name in enumerate(_WEEK_ORDER) if mask & (1 << bit)]
        forms.add(",".join(picked))
    return frozenset(forms)


_CANON_DAYS = _canon_forms()


@dataclass(frozen=True, slots=True)
class Schedule:
    """schtasks fields plus `day` when the cadence names one or more weekdays."""

    sc: str
    mo: int | None
    st: str | None
    day: str | None


@dataclass(frozen=True, slots=True)
class Cadence:
    """Frozen clock vehicle. `paused` is a flag, not a running timer."""

    mode: str
    interval_s: float | None
    schtasks: Schedule | None
    paused: bool
    cap: int
    tr_extra: tuple[str, ...]

    def __post_init__(self) -> None:
        _validate(self)


@dataclass(frozen=True, slots=True)
class Emitted:
    """Frozen snapshot. `rebuild` checks `schema` and does not trust it blindly."""

    schema: str
    mode: str
    interval_s: float | None
    sc: str | None
    mo: int | None
    st: str | None
    day: str | None
    paused: bool
    cap: int
    tr_extra: tuple[str, ...]

    def __post_init__(self) -> None:
        _validate_emitted(self)


def _plain_int(value: object, lo: int, hi: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("BAD_RECORD")
    if value < lo or value > hi:
        raise Refuse("BAD_RECORD")
    return value


def _plain_float(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, float):
        raise Refuse("BAD_RECORD")
    if value != value or value == float("inf") or value == float("-inf"):
        raise Refuse("BAD_RECORD")
    return value


def _small_int(raw: str, lo: int, hi: int) -> int | None:
    if not raw.isdigit() or len(raw) > 7:
        return None
    value = int(raw)
    if value < lo or value > hi:
        return None
    return value


def _validate_emitted(rec: Emitted) -> None:
    if type(rec.schema) is not str or not 1 <= len(rec.schema) <= 64:
        raise Refuse("BAD_RECORD")
    if any(ord(ch) < 33 or ord(ch) > 126 for ch in rec.schema):
        raise Refuse("BAD_RECORD")
    if type(rec.mode) is not str or len(rec.mode) > 32:
        raise Refuse("BAD_RECORD")
    if rec.interval_s is not None:
        _plain_float(rec.interval_s)
    if rec.sc is not None and type(rec.sc) is not str:
        raise Refuse("BAD_RECORD")
    if rec.mo is not None:
        _plain_int(rec.mo, 0, 1_000_000)
    if rec.st is not None and type(rec.st) is not str:
        raise Refuse("BAD_RECORD")
    if rec.day is not None and (type(rec.day) is not str or len(rec.day) > 64):
        raise Refuse("BAD_RECORD")
    if type(rec.paused) is not bool:
        raise Refuse("BAD_RECORD")
    if isinstance(rec.cap, bool) or type(rec.cap) is not int:
        raise Refuse("BAD_RECORD")
    extra = rec.tr_extra
    if type(extra) is not tuple or any(type(item) is not str for item in extra):
        raise Refuse("BAD_RECORD")


def _validate(rec: Cadence) -> None:
    if rec.mode not in MODES:
        raise Refuse("BAD_RECORD")
    if type(rec.paused) is not bool:
        raise Refuse("BAD_RECORD")
    cap = rec.cap
    if isinstance(cap, bool) or not isinstance(cap, int) or cap < 1 or cap > POLICY_CAP:
        raise Refuse("BAD_LIMIT")
    extra = rec.tr_extra
    if not isinstance(extra, tuple) or any(type(item) is not str for item in extra):
        raise Refuse("BAD_RECORD")
    if rec.mode == "detached_daemon":
        if rec.schtasks is not None or extra != _LOOP:
            raise Refuse("BAD_RECORD")
        interval = _plain_float(rec.interval_s)
        if not 0.0 < interval < FLOOR_S:
            raise Refuse("BAD_RECORD")
        return
    if extra != _ONCE if rec.mode == "schtasks" else extra != _LOOP:
        raise Refuse("BAD_RECORD")
    plan = rec.schtasks
    if not isinstance(plan, Schedule) or plan.sc not in _SC:
        raise Refuse("BAD_RECORD")
    if (rec.mode == "onlogon") != (plan.sc == "onlogon"):
        raise Refuse("BAD_RECORD")
    st = plan.st
    if st is not None and (type(st) is not str or _ST.fullmatch(st) is None):
        raise Refuse("BAD_RECORD")
    day = plan.day
    if day is not None and (type(day) is not str or len(day) > 64):
        raise Refuse("BAD_RECORD")
    _validate_plan(rec, plan)


def _validate_plan(rec: Cadence, plan: Schedule) -> None:
    sc = plan.sc
    if sc == "minute":
        mo = _plain_int(plan.mo, 1, _MINUTE_MAX)
        if plan.st is not None or plan.day is not None:
            raise Refuse("BAD_RECORD")
        if rec.interval_s != float(mo * 60):
            raise Refuse("BAD_RECORD")
        return
    if sc == "HOURLY":
        hours = 1 if plan.mo is None else _plain_int(plan.mo, 1, _HOUR_MAX)
        if plan.day is not None or (plan.st is not None and not plan.st.startswith("00:")):
            raise Refuse("BAD_RECORD")
        if rec.interval_s != float(hours * 3600):
            raise Refuse("BAD_RECORD")
        return
    if sc == "DAILY":
        days = 1 if plan.mo is None else _plain_int(plan.mo, 1, _DAY_MAX)
        if plan.day is not None:
            raise Refuse("BAD_RECORD")
        if plan.st is None:
            if rec.interval_s != float(days * 86400):
                raise Refuse("BAD_RECORD")
        elif plan.mo not in (None, 1) or rec.interval_s is not None:
            raise Refuse("BAD_RECORD")
        return
    if sc == "WEEKLY":
        weeks = 1 if plan.mo is None else _plain_int(plan.mo, 1, _WEEK_MAX)
        anchored = plan.st is not None or plan.day is not None
        if anchored:
            if plan.st is None or plan.day not in _CANON_DAYS or rec.interval_s is not None:
                raise Refuse("BAD_RECORD")
            return
        if rec.interval_s != float(weeks * 7 * 86400):
            raise Refuse("BAD_RECORD")
        return
    if sc == "MONTHLY":
        if plan.mo is not None:
            _plain_int(plan.mo, 1, 12)
        if rec.interval_s is not None or plan.st is None or not _month_day(plan.day):
            raise Refuse("BAD_RECORD")
        return
    if plan.mo is not None or plan.st is not None or plan.day is not None or rec.interval_s is not None:
        raise Refuse("BAD_RECORD")


def _month_day(day: str | None) -> bool:
    if day is None or len(day) > 2 or not day.isdigit():
        return False
    value = int(day)
    return 1 <= value <= 31 and str(value) == day


def _resolve_cap(requested: object) -> int:
    if requested is None:
        return POLICY_CAP
    if isinstance(requested, bool) or not isinstance(requested, int):
        raise Refuse("NOT_INT")
    if requested < 1:
        raise Refuse("BAD_LIMIT")
    if requested > POLICY_CAP:
        return POLICY_CAP
    return requested


def _norm(phrase: str) -> str:
    return _WS.sub(" ", phrase.strip().lower())


def _clock(hour: int, minute: int) -> str | None:
    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
        return None
    return f"{hour:02d}:{minute:02d}"


def _clock_from(hour_raw: str, minute_raw: str) -> str | None:
    hour = _small_int(hour_raw, 0, 23)
    minute = _small_int(minute_raw, 0, 59)
    if hour is None or minute is None:
        return None
    return _clock(hour, minute)


def _make(
    mode: str,
    interval_s: float | None,
    schtasks: Schedule | None,
    cap: int,
    tr_extra: tuple[str, ...],
) -> Cadence:
    return Cadence(
        mode=mode,
        interval_s=interval_s,
        schtasks=schtasks,
        paused=False,
        cap=cap,
        tr_extra=tr_extra,
    )


def _minute_vehicle(minutes: int, cap: int) -> Cadence:
    return _make("schtasks", float(minutes * 60), Schedule("minute", minutes, None, None), cap, _ONCE)


def _hourly_vehicle(hours: int, minute: int, cap: int) -> Cadence:
    stamped = None if minute == 0 else _clock(0, minute)
    mo = None if hours == 1 else hours
    return _make("schtasks", float(hours * 3600), Schedule("HOURLY", mo, stamped, None), cap, _ONCE)


def _positive_decimal(raw: str) -> Decimal | None:
    try:
        number = Decimal(raw)
    except InvalidOperation:
        return None
    if not number.is_finite() or number <= 0:
        return None
    return number


def _from_total(total: Decimal, cap: int) -> Cadence | None:
    if not total.is_finite() or total <= 0:
        return None
    if total > Decimal(MAX_INTERVAL_S):
        raise Refuse("OUT_OF_RANGE", f"1..{MAX_INTERVAL_S}")
    if total < Decimal(FLOOR_S):
        interval = float(total)
        if not 0.0 < interval < FLOOR_S:
            return None
        return _make("detached_daemon", interval, None, cap, _LOOP)
    # Above the floor, only whole minutes map. Do not round onto a vehicle.
    if (total % Decimal(60)) != 0:
        return None
    minutes = int(total // Decimal(60))
    if minutes % 60 != 0:
        if minutes < 1 or minutes > _MINUTE_MAX:
            return None
        return _minute_vehicle(minutes, cap)
    hours = minutes // 60
    if hours <= _HOUR_MAX:
        return _hourly_vehicle(hours, 0, cap)
    if hours % 24 != 0:
        return None
    days = hours // 24
    if days < 1 or days > _DAY_MAX:
        return None
    mo = None if days == 1 else days
    return _make("schtasks", float(days * 86400), Schedule("DAILY", mo, None, None), cap, _ONCE)


def _token(part: str) -> _Tok | None:
    if part == "*":
        return _Tok("star", None, None)
    if part.startswith("*/"):
        step = _small_int(part[2:], 1, 10_000)
        if step is None:
            return None
        return _Tok("step", step, None)
    if part.isdigit():
        number = _small_int(part, 0, 10_000_000)
        if number is None:
            return None
        return _Tok("number", number, None)
    if part.isalpha():
        return _Tok("name", None, part)
    return None


def _dow_one(token: str) -> str | None:
    if token.isdigit():
        number = _small_int(token, 0, 7)
        if number is None:
            return None
        return _DOW_NUM.get(number)
    return _DOW_NAMES.get(token.lower())


def _dow_pos(token: str, *, end: bool) -> int | None:
    if token.isdigit():
        return _small_int(token, 0, 7)
    name = _DOW_NAMES.get(token.lower())
    if name is None:
        return None
    pos = _POS.get(name)
    if pos is None:
        return None
    if end and pos == 0:
        return 7
    return pos


def _expand_range(start_tok: str, end_tok: str) -> set[str] | None:
    if start_tok == end_tok:
        one = _dow_one(start_tok)
        if one is None:
            return None
        return {one}
    start = _dow_pos(start_tok, end=False)
    stop = _dow_pos(end_tok, end=True)
    if start is None or stop is None or start > stop:
        return None
    found: set[str] = set()
    for number in range(start, stop + 1):
        label = _DOW_NUM.get(number)
        if label is None:
            return None
        found.add(label)
    return found


def _dow_span(token: str) -> str | None:
    pieces = token.split(",")
    if len(pieces) > 7:
        return None
    found: set[str] = set()
    for piece in pieces:
        if piece == "":
            return None
        halves = piece.split("-")
        if len(halves) > 2:
            return None
        if len(halves) == 2:
            left, right = halves
            if left == "" or right == "":
                return None
            part = _expand_range(left, right)
            if part is None or found & part:
                return None
            found.update(part)
            continue
        one = _dow_one(piece)
        if one is None or one in found:
            return None
        found.add(one)
    if not found:
        return None
    day = ",".join(name for name in _WEEK_ORDER if name in found)
    if day not in _CANON_DAYS:
        return None
    return day


def _weekly_at(minute_s: str, hour_s: str, dow_s: str, cap: int) -> Cadence | None:
    day = _dow_span(dow_s)
    stamped = _clock_from(hour_s, minute_s)
    if day is None or stamped is None:
        return None
    return _make("schtasks", None, Schedule("WEEKLY", None, stamped, day), cap, _ONCE)


def _from_cron(parts: list[str], cap: int) -> Cadence | None:
    if len(parts) != 5:
        raise Refuse("UNRECOGNIZED", "cron field count")
    minute_s, hour_s, dom_s, month_s, dow_s = parts
    if month_s != "*":
        return None
    if dom_s == "*" and dow_s != "*" and minute_s.isdigit() and hour_s.isdigit():
        return _weekly_at(minute_s, hour_s, dow_s, cap)
    toks: list[_Tok] = []
    for part in parts:
        tok = _token(part)
        if tok is None:
            return None
        toks.append(tok)
    if len(toks) != 5:
        raise Refuse("UNRECOGNIZED", "cron field count")
    minute, hour, dom, _month, dow = toks
    if minute.kind == "step" and hour.kind == "star" and dom.kind == "star" and dow.kind == "star":
        step = minute.number
        if step is None or step < 1 or step > 59:
            return None
        return _minute_vehicle(step, cap)
    if minute.kind == "star" and hour.kind == "star" and dom.kind == "star" and dow.kind == "star":
        return _minute_vehicle(1, cap)
    if minute.kind == "number" and dom.kind == "star" and dow.kind == "star":
        clock_minute = minute.number
        if clock_minute is None or clock_minute < 0 or clock_minute > 59:
            return None
        if hour.kind == "star":
            return _hourly_vehicle(1, clock_minute, cap)
        if hour.kind == "step":
            step_h = hour.number
            if step_h is None or step_h < 1 or step_h > _HOUR_MAX:
                return None
            return _hourly_vehicle(step_h, clock_minute, cap)
        if hour.kind == "number" and hour.number is not None:
            stamped = _clock(hour.number, clock_minute)
            if stamped is None:
                return None
            return _make("schtasks", None, Schedule("DAILY", None, stamped, None), cap, _ONCE)
        return None
    if minute.kind == "number" and hour.kind == "number" and dom.kind == "number" and dow.kind == "star":
        if minute.number is None or hour.number is None or dom.number is None:
            return None
        stamped = _clock(hour.number, minute.number)
        if stamped is None or not _month_day(str(dom.number)):
            return None
        return _make(
            "schtasks",
            None,
            Schedule("MONTHLY", None, stamped, str(dom.number)),
            cap,
            _ONCE,
        )
    return None


def _match_onlogon(text: str, cap: int) -> Cadence | None:
    if _ONLOGON.fullmatch(text) is None:
        return None
    return _make("onlogon", None, Schedule("onlogon", None, None, None), cap, _LOOP)


def _match_hourly(text: str, cap: int) -> Cadence | None:
    if _HOURLY.fullmatch(text) is None:
        return None
    return _hourly_vehicle(1, 0, cap)


def _match_weekly(text: str, cap: int) -> Cadence | None:
    if _WEEKLY.fullmatch(text) is None:
        return None
    return _make("schtasks", float(7 * 86400), Schedule("WEEKLY", None, None, None), cap, _ONCE)


def _match_daily(text: str, cap: int) -> Cadence | None:
    match = _DAILY_AT.fullmatch(text)
    if match is None:
        return None
    hour_raw = match.group(1)
    minute_raw = match.group(2)
    if hour_raw is None or minute_raw is None:
        return None
    stamped = _clock_from(hour_raw, minute_raw)
    if stamped is None:
        return None
    return _make("schtasks", None, Schedule("DAILY", None, stamped, None), cap, _ONCE)


def _match_weekday(text: str, cap: int) -> Cadence | None:
    match = _WEEKDAY_AT.fullmatch(text)
    if match is None:
        return None
    hour_raw = match.group(1)
    minute_raw = match.group(2)
    if hour_raw is None or minute_raw is None:
        return None
    stamped = _clock_from(hour_raw, minute_raw)
    if stamped is None:
        return None
    return _make("schtasks", None, Schedule("WEEKLY", None, stamped, _WEEKDAYS), cap, _ONCE)


def _match_every(text: str, cap: int) -> Cadence | None:
    match = _EVERY.fullmatch(text)
    if match is None:
        return None
    raw = match.group(1)
    unit_name = match.group(2)
    if raw is None or unit_name is None:
        return None
    number = _positive_decimal(raw)
    unit = _UNIT_SECONDS.get(unit_name)
    if number is None or unit is None:
        return None
    return _from_total(number * Decimal(unit), cap)


def _freeze(rec: Cadence) -> tuple[object, ...]:
    plan = rec.schtasks
    shape = None if plan is None else (plan.sc, plan.mo, plan.st, plan.day)
    return (rec.mode, rec.interval_s, shape, rec.tr_extra)


def _from_phrase(text: str, cap: int) -> Cadence | None:
    matchers: tuple[Callable[[str, int], Cadence | None], ...] = (
        _match_onlogon,
        _match_daily,
        _match_weekday,
        _match_hourly,
        _match_weekly,
        _match_every,
    )
    found: list[Cadence] = []
    seen: set[tuple[object, ...]] = set()
    for matcher in matchers:
        rec = matcher(text, cap)
        if rec is None:
            continue
        key = _freeze(rec)
        if key in seen:
            continue
        seen.add(key)
        found.append(rec)
    if len(found) != 1:
        return None
    return found[0]


def parse(text: object, *, cap: object = None) -> Cadence:
    """Return one vehicle for a 5-field expression or a closed phrase."""
    limit = _resolve_cap(cap)
    raw = bound_text(text, limit)
    if secret_shape(raw.lower()):
        raise Refuse("SECRET", "secret-shaped cadence")
    norm = _norm(raw)
    if norm == "":
        raise Refuse("UNRECOGNIZED", "empty")
    if _IN_PROCESS.search(norm) is not None:
        raise Refuse("IN_PROCESS", "descriptor only")
    parts = norm.split(" ")
    if len(parts) == 5 and all(_FIELD.fullmatch(part) is not None for part in parts):
        rec = _from_cron(parts, limit)
    else:
        rec = _from_phrase(norm, limit)
    if rec is None or rec.mode not in MODES:
        raise Refuse("UNRECOGNIZED", "no unique vehicle")
    return rec


def pause(record: object) -> Cadence:
    """Return a copy with the paused flag set."""
    if not isinstance(record, Cadence):
        raise Refuse("BAD_RECORD")
    return replace(record, paused=True)


def resume(record: object) -> Cadence:
    """Return a copy with the paused flag cleared."""
    if not isinstance(record, Cadence):
        raise Refuse("BAD_RECORD")
    return replace(record, paused=False)


def snapshot(record: object) -> Emitted:
    """Return the stored shape of a cadence. It does not read a clock."""
    if not isinstance(record, Cadence):
        raise Refuse("BAD_RECORD")
    plan = record.schtasks
    return Emitted(
        schema=SCHEMA,
        mode=record.mode,
        interval_s=record.interval_s,
        sc=None if plan is None else plan.sc,
        mo=None if plan is None else plan.mo,
        st=None if plan is None else plan.st,
        day=None if plan is None else plan.day,
        paused=record.paused,
        cap=record.cap,
        tr_extra=tuple(record.tr_extra),
    )


def rebuild(payload: object) -> Cadence:
    """Restore a cadence from a snapshot. A foreign schema is stale."""
    if not isinstance(payload, Emitted):
        raise Refuse("BAD_RECORD")
    if not const_eq(payload.schema, SCHEMA):
        raise Refuse("STALE")
    plan = None
    if payload.sc is not None or payload.mo is not None or payload.st is not None or payload.day is not None:
        if type(payload.sc) is not str:
            raise Refuse("BAD_RECORD")
        plan = Schedule(payload.sc, payload.mo, payload.st, payload.day)
    return Cadence(
        mode=payload.mode,
        interval_s=payload.interval_s,
        schtasks=plan,
        paused=payload.paused,
        cap=payload.cap,
        tr_extra=payload.tr_extra,
    )


def run(record: object) -> NoReturn:
    """Refuse an in-process fire. The cadence stays a descriptor."""
    if not isinstance(record, Cadence):
        raise Refuse("BAD_RECORD")
    raise Refuse("IN_PROCESS", "descriptor only")


__all__ = [
    "FLOOR_S",
    "MAX_INTERVAL_S",
    "MODES",
    "POLICY_CAP",
    "SCHEMA",
    "Cadence",
    "Emitted",
    "Schedule",
    "parse",
    "pause",
    "rebuild",
    "resume",
    "run",
    "snapshot",
]
