#!/usr/bin/env python3
"""UTC day and trailing-week fold for the cDeck meter strip.

Pure. The caller injects events and the clock. This module does not open
the ledger, the meter file, or the wall clock.

``week`` is seven UTC dates ending today (today plus the six days before
it). A timestamp exactly on a midnight belongs to the day that starts
then, not the day that ended. A count the row does not carry stays
``UNMEASURED`` for that window — it is not stored as zero. A carried 0
stays 0. Dollars sum only the rows that carried a price; the window is
``UNMEASURED`` only when none of them did.
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from datetime import datetime, timedelta, timezone

UNMEASURED = "UNMEASURED"
TRAILING_DAYS = 7

_SKIP_EVENTS = frozenset({
    "BUDGET_SET",
    "SPEND_RESERVED",
    "SPEND_RELEASED",
    "SPEND_DENIED",
    "RUN_FAILED",
    "CREDIT_PURCHASED",
    "CREDIT_GRANTED",
    "TOLL_ACCRUED",
    "QUOTA_HIT",
})
_COUNT_EVENTS = frozenset({
    "SPEND_SETTLED",
    "RUN_SETTLED",
    "RUN_UNPRICED",
})
_UNPRICED = frozenset({"unpriced", "unmeasured"})
_PRICED = frozenset({"measured", "estimate", "billed"})


class MeterWindowError(RuntimeError):
    """kind in {BAD_INPUT, BAD_CLOCK, BAD_ROW}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def meter_window(events, clock) -> dict:
    """Today and the trailing 7 UTC days.

    Each side is ``tokens_in``, ``tokens_out``, and ``usd``. ``clock`` is
    an epoch (int or float) or an offset-aware ISO timestamp.
    """
    now = _parse_clock(clock)
    rows = _read_rows(events)
    start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    week_start = start - timedelta(days=TRAILING_DAYS - 1)
    return {
        "today": _fold(rows, start, end),
        "week": _fold(rows, week_start, end),
    }


def _parse_clock(clock) -> datetime:
    try:
        return _as_utc(clock, "BAD_CLOCK", "clock")
    except MeterWindowError:
        raise
    except (TypeError, ValueError, OverflowError, OSError) as exc:
        raise MeterWindowError("BAD_CLOCK", "clock is not an epoch or UTC ISO time") from exc


def _read_rows(events) -> list[dict]:
    if events is None:
        return []
    if isinstance(events, (str, bytes)) or not isinstance(events, Sequence):
        raise MeterWindowError("BAD_INPUT", "events must be a list of rows")
    rows: list[dict] = []
    for index, event in enumerate(events):
        row = _read_row(event, index)
        if row is not None:
            rows.append(row)
    return rows


def _read_row(event, index: int) -> dict | None:
    where = f"row {index}"
    if not isinstance(event, dict):
        raise MeterWindowError("BAD_ROW", f"{where} is not an object")
    name = event.get("event")
    if name is not None:
        if not isinstance(name, str):
            raise MeterWindowError("BAD_ROW", f"{where} event name is not a string")
        if name in _SKIP_EVENTS:
            return None
        if name not in _COUNT_EVENTS:
            raise MeterWindowError("BAD_ROW", f"{where} event {name!r} is not a meter row")
    source = _source(event)
    if name is None and not _has_meter_fields(source):
        raise MeterWindowError("BAD_ROW", f"{where} has no meter fields")
    try:
        when = _row_time(event, where)
        tokens_in = _pick_count(source, "in", where)
        tokens_out = _pick_count(source, "out", where)
        usd = _price(source, where)
    except MeterWindowError:
        raise
    except (TypeError, ValueError, OverflowError, OSError) as exc:
        raise MeterWindowError("BAD_ROW", f"{where} could not be read") from exc
    return {
        "at": when,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "usd": usd,
    }


def _source(event: dict) -> dict:
    payload = event.get("payload")
    if not isinstance(payload, dict):
        return event
    merged = dict(event)
    merged.update(payload)
    return merged


def _has_meter_fields(source: dict) -> bool:
    return any(key in source for key in (
        "tokens_in", "tokens_out", "prompt_tokens", "completion_tokens",
        "measured_usd", "usd", "cost", "tokens",
    ))


def _row_time(event: dict, where: str) -> datetime:
    found: list[datetime] = []
    for key in ("t", "at"):
        if key in event:
            found.append(_as_utc(event[key], "BAD_ROW", f"{where} {key}"))
    payload = event.get("payload")
    if isinstance(payload, dict):
        for key in ("t", "at"):
            if key in payload:
                found.append(_as_utc(payload[key], "BAD_ROW", f"{where} payload.{key}"))
    if not found:
        raise MeterWindowError("BAD_ROW", f"{where} has no t or at")
    first = found[0]
    for other in found[1:]:
        if other != first:
            raise MeterWindowError("BAD_ROW", f"{where} timestamps disagree")
    return first


def _as_utc(value, kind: str, where: str) -> datetime:
    if isinstance(value, bool) or value is None:
        raise MeterWindowError(kind, f"{where} is not an epoch or UTC ISO time")
    if isinstance(value, (int, float)):
        if not math.isfinite(float(value)):
            raise MeterWindowError(kind, f"{where} is not a finite epoch")
        try:
            return datetime.fromtimestamp(float(value), timezone.utc)
        except (OverflowError, OSError, ValueError) as exc:
            raise MeterWindowError(kind, f"{where} is not a finite epoch") from exc
    if isinstance(value, datetime):
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            raise MeterWindowError(kind, f"{where} has no UTC offset")
        return value.astimezone(timezone.utc)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            raise MeterWindowError(kind, f"{where} is blank")
        if text.endswith(("Z", "z")):
            text = text[:-1] + "+00:00"
        try:
            parsed = datetime.fromisoformat(text)
        except ValueError as exc:
            raise MeterWindowError(kind, f"{where} is not an epoch or UTC ISO time") from exc
        if parsed.tzinfo is None or parsed.tzinfo.utcoffset(parsed) is None:
            # A date with no clock is that UTC midnight (the new day).
            # A clock with no offset is refused — local time is not UTC.
            if "T" in text or " " in text:
                raise MeterWindowError(kind, f"{where} has no UTC offset")
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    raise MeterWindowError(kind, f"{where} is not an epoch or UTC ISO time")


def _pick_count(source: dict, side: str, where: str) -> int | None:
    flat_key = "tokens_in" if side == "in" else "tokens_out"
    usage_key = "prompt_tokens" if side == "in" else "completion_tokens"
    seen: list[int | None] = []
    if flat_key in source:
        seen.append(_count(source.get(flat_key), f"{where} {flat_key}"))
    tokens = source.get("tokens") if "tokens" in source else None
    if "tokens" in source and tokens is not None:
        if not isinstance(tokens, dict):
            raise MeterWindowError("BAD_ROW", f"{where} tokens is not an object")
        if side in tokens:
            seen.append(_count(tokens.get(side), f"{where} tokens.{side}"))
    if usage_key in source:
        seen.append(_count(source.get(usage_key), f"{where} {usage_key}"))
    if not seen:
        return None
    if any(item is None for item in seen) and any(item is not None for item in seen):
        raise MeterWindowError("BAD_ROW", f"{where} token aliases disagree")
    if any(item is None for item in seen):
        return None
    first = seen[0]
    if any(item != first for item in seen):
        raise MeterWindowError("BAD_ROW", f"{where} token aliases disagree")
    return first


def _count(value, where: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise MeterWindowError("BAD_ROW", f"{where} is not a count >= 0")
    return value


def _price(source: dict, where: str) -> float | None:
    found: list[float | None] = []
    saw = False
    if "measured_usd" in source or "provenance" in source:
        saw = True
        found.append(_amount(
            source.get("measured_usd"),
            "measured_usd" in source,
            source.get("provenance"),
            f"{where} measured_usd",
        ))
    if "usd" in source and not isinstance(source.get("usd"), dict):
        saw = True
        found.append(_amount(
            source.get("usd"),
            True,
            source.get("cost_kind"),
            f"{where} usd",
        ))
    if "cost" in source:
        cost = source.get("cost")
        if isinstance(cost, dict):
            if "measured_usd" in cost or "provenance" in cost:
                saw = True
                found.append(_amount(
                    cost.get("measured_usd"),
                    "measured_usd" in cost,
                    cost.get("provenance"),
                    f"{where} cost.measured_usd",
                ))
        elif cost is not None:
            saw = True
            found.append(_amount(cost, True, None, f"{where} cost"))
    if not saw:
        return None
    numbers = [item for item in found if item is not None]
    if numbers and any(item is None for item in found):
        raise MeterWindowError("BAD_ROW", f"{where} prices disagree")
    if not numbers:
        return None
    first = numbers[0]
    for other in numbers[1:]:
        if abs(other - first) > 1e-9:
            raise MeterWindowError("BAD_ROW", f"{where} prices disagree")
    return first


def _amount(value, present: bool, provenance, where: str) -> float | None:
    label = _provenance(provenance, where)
    number = _money(value, where) if present else None
    if label in _UNPRICED:
        if present and value is not None:
            raise MeterWindowError("BAD_ROW", f"{where} is unpriced but carries a number")
        return None
    if label in {"measured", "billed"}:
        if number is None:
            raise MeterWindowError("BAD_ROW", f"{where} provenance requires a price")
        return number
    return number


def _provenance(value, where: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise MeterWindowError("BAD_ROW", f"{where} provenance is not a string")
    label = value.strip().lower()
    if label not in _UNPRICED and label not in _PRICED:
        raise MeterWindowError("BAD_ROW", f"{where} provenance {value!r} is unknown")
    return label


def _money(value, where: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise MeterWindowError("BAD_ROW", f"{where} is not a dollar amount >= 0")
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise MeterWindowError("BAD_ROW", f"{where} is not a dollar amount >= 0")
    return number


def _fold(rows: list[dict], start: datetime, end: datetime) -> dict:
    inside = [row for row in rows if start <= row["at"] < end]
    return {
        "tokens_in": _fold_count([row["tokens_in"] for row in inside]),
        "tokens_out": _fold_count([row["tokens_out"] for row in inside]),
        "usd": _fold_usd([row["usd"] for row in inside]),
    }


def _fold_count(values: list[int | None]) -> int | str:
    if not values or any(value is None for value in values):
        return UNMEASURED
    return sum(values)


def _fold_usd(values: list[float | None]) -> float | str:
    priced = [value for value in values if value is not None]
    if not priced:
        return UNMEASURED
    return round(sum(priced), 6)
