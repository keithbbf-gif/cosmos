#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_nlcron — Hermes job-language cadence parser (named fold).

Maps a natural-language cadence onto the COSMOS Windows-clock vehicles
already owned by schtasks + WD2. Parser only. Does not create tasks,
does not spawn the native scheduler binary, does not start a detached
daemon, and does not add an in-process timer, sleep-loop, cron, Core
thread, or HTTP route.

    schtasks floor is 1 minute. Anything faster is detached_daemon
    (the --loop process + 1-min self-heal + onlogon relaunch live in
    the clock standup; this fold only names the vehicle).

Returned dict reuses cosmos_clock.plan_create / tr_cmdline field shapes:

    mode        schtasks | detached_daemon | onlogon
    interval_s  float | None
    schtasks    {sc, mo, st} | None     # plan_create kwargs
    tr_extra    tuple                   # *extra for tr_cmdline
    clocks      CLOCKS label | None     # unique cosmos_own_clocks match

Unparseable or ambiguous phrases raise NlcronError kind=UNRECOGNIZED.
Never a silent default. Sub-minute phrases are detached_daemon — never
schtasks /sc minute with mo<1. schtasks /mo ceilings are minute 1..1439,
hourly 1..23, and daily 1..365. An exact multiple of a day uses DAILY.
Anything else that is not an exact legal modifier is UNRECOGNIZED — not
a rounded modifier and not an invented /st.

    py -3.14 cosmos\\cosmos_nlcron.py --selftest
"""
from __future__ import annotations

import re
import sys
from typing import Any

SCHEMA = "cosmos-nlcron/1"
MODES = frozenset({"schtasks", "detached_daemon", "onlogon"})
SCHTASKS_FLOOR_S = 60.0
# schtasks /Create /mo ceilings (Microsoft schtasks-create).
_MINUTE_MAX = 1439
_HOUR_MAX = 23
_DAY_MAX = 365

_WS = re.compile(r"\s+")
_ONLOGON = re.compile(
    r"^(on logon|at logon|onlogon|on-logon|on login|at login|on-login)$"
)
_DAILY = re.compile(
    r"^(?:daily|every day|each day)(?: at)? "
    r"(\d{1,2}):(\d{2})(?:\s*(am|pm))?$"
)
_HOURLY = re.compile(
    r"^(hourly|every hour|once an hour|every 1 ?h(?:ou)?rs?)$"
)
_EVERY = re.compile(
    r"^every (\d+(?:\.\d+)?) ?"
    r"(s|sec|secs|second|seconds|m|min|mins|minute|minutes|"
    r"h|hr|hrs|hour|hours)$"
)
_BARE = re.compile(r"^(\d+(?:\.\d+)?)(s|m|h)$")
_EVERY_WORD = {
    "every second": (1.0, "s"),
    "once a second": (1.0, "s"),
    "every minute": (1.0, "m"),
    "once a minute": (1.0, "m"),
}

_SEC_UNITS = frozenset({"s", "sec", "secs", "second", "seconds"})
_MIN_UNITS = frozenset({"m", "min", "mins", "minute", "minutes"})
_HOUR_UNITS = frozenset({"h", "hr", "hrs", "hour", "hours"})


class NlcronError(RuntimeError):
    """kind=UNRECOGNIZED. Unparseable or ambiguous cadence. Never a silent default."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _norm(phrase: str) -> str:
    return _WS.sub(" ", phrase.replace("\u00a0", " ").strip().lower())


def _schtasks_shape(sc: str, mo: int | None = None,
                    st: str | None = None) -> dict[str, Any]:
    """plan_create schedule kwargs. Keys always present so callers can splat."""
    return {"sc": sc, "mo": mo, "st": st}


def _result(mode: str, interval_s: float | None,
            schtasks: dict[str, Any] | None,
            tr_extra: tuple[str, ...]) -> dict[str, Any]:
    rec = {
        "mode": mode,
        "interval_s": interval_s,
        "schtasks": None if schtasks is None else dict(schtasks),
        "tr_extra": tuple(tr_extra),
        "clocks": None,
    }
    rec["clocks"] = _clocks_label(rec)
    return rec


def _unrecognized(phrase: str, why: str) -> None:
    raise NlcronError(
        "UNRECOGNIZED",
        f"unparseable or ambiguous cadence {phrase!r}: {why}",
    )


def _as_positive_float(raw: str) -> float | None:
    try:
        n = float(raw)
    except ValueError:
        return None
    if n != n or n <= 0.0:  # NaN or non-positive
        return None
    if n == float("inf"):
        return None
    return n


def _finite(n: float) -> bool:
    return n == n and n != float("inf") and n != float("-inf")


def _seconds(n: float, unit: str) -> float | None:
    if unit in _SEC_UNITS:
        total = n
    elif unit in _MIN_UNITS:
        total = n * 60.0
    elif unit in _HOUR_UNITS:
        total = n * 3600.0
    else:
        return None
    # Unit scale can overflow a finite count to inf. That is not a cadence.
    if not _finite(total) or total <= 0.0:
        return None
    return total


def _whole_int(n: int | float) -> int | None:
    try:
        out = int(n)
    except (OverflowError, ValueError):
        return None
    return out


def _from_interval(total_s: float) -> dict[str, Any] | None:
    """Map a clear interval onto a vehicle. Do not round. Do not invent /st."""
    if not _finite(total_s) or total_s <= 0.0:
        return None
    if total_s < SCHTASKS_FLOOR_S:
        return _result("detached_daemon", float(total_s), None, ("--loop",))
    minutes = total_s / 60.0
    if not _finite(minutes):
        return None
    nearest = round(minutes)
    if abs(minutes - nearest) > 1e-9:
        # Whole seconds that are not a whole minute (e.g. 90s): schtasks
        # cannot express them and rounding would be a silent default.
        return _result("detached_daemon", float(total_s), None, ("--loop",))
    mo = _whole_int(nearest)
    if mo is None or mo < 1:
        return None
    if mo % 60 == 0:
        hours = mo // 60
        if hours == 1:
            return _result(
                "schtasks", 3600.0,
                _schtasks_shape("HOURLY"),
                ("--once",),
            )
        if hours <= _HOUR_MAX:
            return _result(
                "schtasks", float(hours * 3600),
                _schtasks_shape("HOURLY", mo=hours),
                ("--once",),
            )
        # HOURLY /mo stops at 23. An exact day count still has one vehicle.
        if hours % 24 == 0:
            days = hours // 24
            if 1 <= days <= _DAY_MAX:
                return _result(
                    "schtasks", float(days * 86400),
                    _schtasks_shape("DAILY", mo=None if days == 1 else days),
                    ("--once",),
                )
        return None
    if mo > _MINUTE_MAX:
        return None
    return _result(
        "schtasks", float(mo * 60),
        _schtasks_shape("minute", mo=mo),
        ("--once",),
    )


def _match_onlogon(text: str) -> dict[str, Any] | None:
    if not _ONLOGON.match(text):
        return None
    return _result(
        "onlogon", None,
        _schtasks_shape("onlogon"),
        ("--loop",),
    )


def _hhmm(hour: int, minute: int) -> str | None:
    if minute < 0 or minute > 59:
        return None
    if hour < 0 or hour > 23:
        return None
    return f"{hour:02d}:{minute:02d}"


def _match_daily(text: str) -> dict[str, Any] | None:
    m = _DAILY.match(text)
    if not m:
        return None
    hour = int(m.group(1))
    minute = int(m.group(2))
    ampm = m.group(3)
    if ampm:
        if hour < 1 or hour > 12:
            return None
        hour = hour % 12
        if ampm == "pm":
            hour += 12
    st = _hhmm(hour, minute)
    if st is None:
        return None
    return _result(
        "schtasks", None,
        _schtasks_shape("DAILY", st=st),
        ("--once",),
    )


def _match_hourly(text: str) -> dict[str, Any] | None:
    if not _HOURLY.match(text):
        return None
    return _result(
        "schtasks", 3600.0,
        _schtasks_shape("HOURLY"),
        ("--once",),
    )


def _match_every(text: str) -> dict[str, Any] | None:
    m = _EVERY.match(text)
    if not m:
        return None
    n = _as_positive_float(m.group(1))
    if n is None:
        return None
    total = _seconds(n, m.group(2))
    if total is None:
        return None
    return _from_interval(total)


def _match_bare(text: str) -> dict[str, Any] | None:
    # CLOCKS dialect: "15s", "5m", "1m", "hourly" is elsewhere.
    m = _BARE.match(text)
    if not m:
        return None
    n = _as_positive_float(m.group(1))
    if n is None:
        return None
    total = _seconds(n, m.group(2))
    if total is None:
        return None
    return _from_interval(total)


def _match_every_word(text: str) -> dict[str, Any] | None:
    pair = _EVERY_WORD.get(text)
    if pair is None:
        return None
    n, unit = pair
    total = _seconds(n, unit)
    if total is None:
        return None
    return _from_interval(total)


def _freeze(rec: dict[str, Any]) -> tuple:
    st = rec.get("schtasks")
    st_key = None if st is None else (st.get("sc"), st.get("mo"), st.get("st"))
    return (rec.get("mode"), rec.get("interval_s"), st_key, rec.get("tr_extra"))


_MATCHERS = (
    _match_onlogon,
    _match_daily,
    _match_hourly,
    _match_every,
    _match_bare,
    _match_every_word,
)


def _clocks_label(rec: dict[str, Any]) -> str | None:
    """Unique CLOCKS[*].clock when the cadence token matches exactly.

    Compound CLOCKS cadences ('15s loop / 1-min self-heal') are not an
    exact token and do not steal the label from the simple row.
    Hourly is three clocks — not unique, so no label. On logon is many.
    """
    from cosmos_own_clocks import CLOCKS  # noqa: WPS433 — read-only table

    mode = rec.get("mode")
    interval_s = rec.get("interval_s")
    st = rec.get("schtasks") or {}
    token = None
    if mode == "detached_daemon" and isinstance(interval_s, (int, float)):
        iv = float(interval_s)
        whole = _whole_int(iv) if _finite(iv) else None
        if whole is None:
            token = None
        elif iv == whole:
            token = f"{whole}s"
        else:
            token = f"{iv}s"
    elif mode == "schtasks":
        sc = st.get("sc")
        mo = st.get("mo")
        start = st.get("st")
        if sc == "minute" and isinstance(mo, int) and mo >= 1:
            token = f"{mo}m"
        elif sc == "HOURLY" and mo in (None, 1):
            token = "hourly"
        elif sc == "DAILY" and isinstance(start, str) and start:
            # '07/11/19/23 daily' lists hours. Match HH:00 only — a substring
            # of the hour would label 07:30 (and 11:45, 19:01) as Backup.
            hh, sep, mm = start.partition(":")
            if sep != ":" or mm != "00" or len(hh) != 2 or not hh.isdigit():
                return None
            hits: list[str] = []
            for c in CLOCKS:
                cad = str(c.get("cadence") or "")
                if "daily" not in cad.lower():
                    continue
                hours = {
                    f"{int(part):02d}"
                    for part in cad.replace("/", " ").split()
                    if part.isdigit()
                }
                if hh in hours:
                    hits.append(c["clock"])
            return hits[0] if len(hits) == 1 else None
    if token is None:
        return None
    hits = [c["clock"] for c in CLOCKS if str(c.get("cadence") or "") == token]
    return hits[0] if len(hits) == 1 else None


def parse_cadence(phrase: str) -> dict[str, Any]:
    """Parse one Hermes cadence phrase onto a COSMOS clock vehicle.

    Fail-closed: anything unparseable or ambiguous raises NlcronError
    kind=UNRECOGNIZED. Does not create a task. Does not spawn a process.
    """
    if not isinstance(phrase, str):
        _unrecognized(phrase, f"not text ({type(phrase).__name__})")
    text = _norm(phrase)
    if not text:
        _unrecognized(phrase, "empty")

    found: list[dict[str, Any]] = []
    seen: set[tuple] = set()
    for matcher in _MATCHERS:
        rec = matcher(text)
        if rec is None:
            continue
        key = _freeze(rec)
        if key in seen:
            continue
        seen.add(key)
        found.append(rec)

    if len(found) != 1:
        _unrecognized(phrase, "no unique vehicle")
    rec = found[0]
    if rec["mode"] not in MODES:
        _unrecognized(phrase, "internal mode not in vehicle set")
    sch = rec.get("schtasks")
    if rec["mode"] == "detached_daemon":
        if sch is not None:
            _unrecognized(phrase, "sub-minute must not carry schtasks")
    if (sch is not None and sch.get("sc") == "minute"
            and (sch.get("mo") is None or int(sch["mo"]) < 1)):
        _unrecognized(phrase, "schtasks minute mo<1 is refused")
    return rec


def _selftest() -> int:
    results: list[tuple[str, bool, str]] = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    r15 = parse_cadence("every 15s")
    check(
        "every 15s is detached_daemon 15s, no schtasks",
        lambda: r15["mode"] == "detached_daemon"
        and r15["interval_s"] == 15.0
        and r15["schtasks"] is None
        and r15["tr_extra"] == ("--loop",)
        and r15["clocks"] == "COSMOS Activity Clock (Watchdog2)",
    )

    r5 = parse_cadence("every 5m")
    check(
        "every 5m is schtasks minute/5 (Ledger Verify)",
        lambda: r5["mode"] == "schtasks"
        and r5["interval_s"] == 300.0
        and r5["schtasks"] == {"sc": "minute", "mo": 5, "st": None}
        and r5["tr_extra"] == ("--once",)
        and r5["clocks"] == "COSMOS Ledger Verify",
    )

    rh = parse_cadence("hourly")
    check(
        "hourly is schtasks HOURLY (CLOCKS hourly is not unique)",
        lambda: rh["mode"] == "schtasks"
        and rh["interval_s"] == 3600.0
        and rh["schtasks"] == {"sc": "HOURLY", "mo": None, "st": None}
        and rh["clocks"] is None,
    )

    rd = parse_cadence("daily 07:00")
    check(
        "daily 07:00 is schtasks DAILY /st 07:00 (Backup)",
        lambda: rd["mode"] == "schtasks"
        and rd["interval_s"] is None
        and rd["schtasks"] == {"sc": "DAILY", "mo": None, "st": "07:00"}
        and rd["clocks"] == "COSMOS Backup",
    )

    rl = parse_cadence("on logon")
    check(
        "on logon is onlogon vehicle, plan_create sc=onlogon",
        lambda: rl["mode"] == "onlogon"
        and rl["interval_s"] is None
        and rl["schtasks"] == {"sc": "onlogon", "mo": None, "st": None}
        and rl["tr_extra"] == ("--loop",),
    )

    def _garbage():
        try:
            parse_cadence("garbage")
        except NlcronError as e:
            return e.kind == "UNRECOGNIZED"
        return False

    check("garbage is UNRECOGNIZED", _garbage)

    def _exact_labels_and_ceilings():
        off = parse_cadence("daily 07:30")
        day = parse_cadence("every 24 hours")
        two = parse_cadence("every 48h")
        legal_hour = parse_cadence("every 23 hours")
        legal_minute = parse_cadence("every 1439 minutes")
        if off["schtasks"] != {"sc": "DAILY", "mo": None, "st": "07:30"}:
            return False
        if off["clocks"] is not None:
            return False
        if day["schtasks"] != {"sc": "DAILY", "mo": None, "st": None}:
            return False
        if day["interval_s"] != 86400.0 or day["tr_extra"] != ("--once",):
            return False
        if two["schtasks"] != {"sc": "DAILY", "mo": 2, "st": None}:
            return False
        if legal_hour["schtasks"] != {"sc": "HOURLY", "mo": 23, "st": None}:
            return False
        if legal_minute["schtasks"] != {"sc": "minute", "mo": 1439, "st": None}:
            return False
        for phrase in ("every 25 hours", "every 1441 minutes",
                       "every " + ("1" + "0" * 307) + "h"):
            try:
                parse_cadence(phrase)
            except NlcronError as e:
                if e.kind != "UNRECOGNIZED":
                    return False
            else:
                return False
        return True

    check("daily label is HH:00 only; /mo stays inside schtasks ceilings",
          _exact_labels_and_ceilings)

    def _no_silent():
        for phrase in ("", "every", "15", "daily", "every 15",
                       "every 15s and hourly", "soon"):
            try:
                parse_cadence(phrase)
            except NlcronError as e:
                if e.kind != "UNRECOGNIZED":
                    return False
            else:
                return False
        return True

    check("empty / unitless / mixed phrases never silent-default", _no_silent)

    def _plan_shapes():
        from pathlib import Path

        from cosmos_clock import plan_create, tr_cmdline

        argv5 = plan_create(
            "COSMOS Ledger Verify", "tr",
            r5["schtasks"]["sc"],
            mo=r5["schtasks"]["mo"],
            st=r5["schtasks"]["st"],
        )
        argvd = plan_create(
            "COSMOS Backup 07", "tr",
            rd["schtasks"]["sc"],
            mo=rd["schtasks"]["mo"],
            st=rd["schtasks"]["st"],
        )
        argvl = plan_create(
            "COSMOS Watchdog2 Logon", "tr",
            rl["schtasks"]["sc"],
            mo=rl["schtasks"]["mo"],
            st=rl["schtasks"]["st"],
        )
        here = Path(__file__).resolve()
        tr = tr_cmdline(here, ".", *r15["tr_extra"])
        return (
            argv5[argv5.index("/sc") + 1] == "minute"
            and argv5[argv5.index("/mo") + 1] == "5"
            and "/st" not in argv5
            and argvd[argvd.index("/sc") + 1] == "DAILY"
            and argvd[argvd.index("/st") + 1] == "07:00"
            and argvl[argvl.index("/sc") + 1] == "onlogon"
            and "--loop" in tr
            and int(r5["schtasks"]["mo"]) >= 1
        )

    check("plan_create / tr_cmdline accept returned field shapes", _plan_shapes)

    import ast
    from pathlib import Path as _Path

    tree = ast.parse(_Path(__file__).read_text(encoding="utf-8"))
    imports = set()
    calls = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for alias in n.names:
                imports.add(alias.name.split(".", 1)[0])
        elif isinstance(n, ast.ImportFrom) and n.module:
            imports.add(n.module.split(".", 1)[0])
        elif isinstance(n, ast.Call):
            if isinstance(n.func, ast.Name):
                calls.add(n.func.id)
            elif isinstance(n.func, ast.Attribute):
                calls.add(n.func.attr)
    banned_imp = {"subprocess", "asyncio", "threading", "sched"}
    banned_call = {
        "create_task", "run_schtasks", "spawn_detached", "spawn_wmi",
        "Popen", "system", "Timer",
    }
    src_ok = not (imports & banned_imp) and not (calls & banned_call)
    check("source is parser-only (no spawn / timer / schtasks write)",
          lambda: src_ok)

    bad = [(label, e) for label, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (nlcron parser; no in-process cron)"
          % ("PASS" if not bad else "FAIL", len(results)))
    return 0 if not bad else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(_selftest())
    print("usage: py -3.14 cosmos\\cosmos_nlcron.py --selftest", file=sys.stderr)
    raise SystemExit(2)
