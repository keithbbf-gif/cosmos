#!/usr/bin/env python3
"""Fixtures for the cDeck meter window. No live meter and no live ledger."""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_meter_window import UNMEASURED, MeterWindowError, meter_window

NOW = "2026-09-23T15:00:00Z"
TODAY_MIDNIGHT = "2026-09-23T00:00:00Z"
YESTERDAY = "2026-09-22T18:00:00Z"
WEEK_START = "2026-09-17T00:00:00Z"  # oldest UTC day of the 7 that end today
BEFORE_WEEK = "2026-09-16T00:00:00Z"
NEXT_MIDNIGHT = "2026-09-24T00:00:00Z"


def _epoch(iso: str) -> float:
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp()


def _settled(iso: str, *, tin=8, tout=3, usd=0.5, tokens=True):
    """SPEND_SETTLED shape: ledger ``t`` plus payload ``measured_usd`` / ``tokens``."""
    payload = {
        "rail": "fixture",
        "rid": "r-fixture",
        "measured_usd": usd,
        "worst_case_usd": 9,
        "provenance": "UNPRICED" if usd is None else "measured",
    }
    if tokens:
        payload["tokens"] = {"in": tin, "out": tout}
    return {"event": "SPEND_SETTLED", "t": _epoch(iso), "payload": payload}


def _blank():
    return {"tokens_in": UNMEASURED, "tokens_out": UNMEASURED, "usd": UNMEASURED}


def test_empty():
    assert meter_window([], NOW) == {"today": _blank(), "week": _blank()}
    assert meter_window(None, _epoch(NOW)) == {"today": _blank(), "week": _blank()}


def test_single_event_today():
    got = meter_window([_settled(NOW, tin=8, tout=3, usd=0.5)], NOW)
    assert got["today"] == {"tokens_in": 8, "tokens_out": 3, "usd": 0.5}
    assert got["week"] == {"tokens_in": 8, "tokens_out": 3, "usd": 0.5}
    assert got["today"] == meter_window(
        [_settled(NOW, tin=8, tout=3, usd=0.5)], _epoch(NOW),
    )["today"]


def test_yesterday_excluded_from_today_included_in_week():
    rows = [
        _settled(NOW, tin=8, tout=3, usd=0.5),
        _settled(YESTERDAY, tin=2, tout=4, usd=0.25),
    ]
    got = meter_window(rows, NOW)
    assert got["today"] == {"tokens_in": 8, "tokens_out": 3, "usd": 0.5}
    assert got["week"] == {"tokens_in": 10, "tokens_out": 7, "usd": 0.75}


def test_boundary_midnight_utc():
    clock = TODAY_MIDNIGHT
    rows = [
        _settled(TODAY_MIDNIGHT, tin=1, tout=1, usd=0.1),
        _settled("2026-09-22T23:59:59Z", tin=4, tout=4, usd=0.4),
        _settled(WEEK_START, tin=2, tout=2, usd=0.2),
        _settled(BEFORE_WEEK, tin=9, tout=9, usd=0.9),
        _settled(NEXT_MIDNIGHT, tin=7, tout=7, usd=0.7),
        # +01:00 01:00 is 00:00Z — the new UTC day, not the previous one.
        _settled("2026-09-23T01:00:00+01:00", tin=1, tout=0, usd=0),
    ]
    # The last row uses the same helper, which rewrites the offset via fromisoformat.
    got = meter_window(rows, clock)
    assert got["today"] == {"tokens_in": 2, "tokens_out": 1, "usd": 0.1}
    # yesterday 4 + week-start 2 + today 1 + offset-midnight 1; before-week and next day out
    assert got["week"] == {"tokens_in": 8, "tokens_out": 7, "usd": 0.7}
    outside = meter_window([_settled("2026-09-15T12:00:00Z", tin=5, tout=5, usd=1)], NOW)
    assert outside == {"today": _blank(), "week": _blank()}


def test_unpriced_events():
    only = _settled(NOW, tin=6, tout=1, usd=None)
    assert meter_window([only], NOW)["today"] == {
        "tokens_in": 6, "tokens_out": 1, "usd": UNMEASURED,
    }
    mixed = meter_window([
        _settled(NOW, tin=6, tout=1, usd=0.5),
        {
            "event": "RUN_UNPRICED",
            "at": "2026-09-23T16:00:00+00:00",
            "tokens": {"in": 1, "out": 1},
            "cost": {"worst_case_usd": 4},
        },
        {
            "event": "SPEND_RESERVED",
            "t": _epoch(NOW),
            "payload": {"worst_case_usd": 9, "rail": "fixture"},
        },
    ], NOW)
    assert mixed["today"] == {"tokens_in": 7, "tokens_out": 2, "usd": 0.5}
    assert mixed["week"]["usd"] == 0.5


def test_present_zero_and_missing_count():
    zeros = {
        "at": TODAY_MIDNIGHT,
        "tokens_in": 0,
        "tokens_out": 0,
        "usd": 0,
        "cost_kind": "ESTIMATE",
    }
    got = meter_window([zeros], NOW)["today"]
    assert got == {"tokens_in": 0, "tokens_out": 0, "usd": 0}
    assert not isinstance(got["tokens_in"], str)
    assert not isinstance(got["usd"], str)

    missing_out = meter_window([
        {"t": _epoch(NOW), "tokens_in": 4, "usd": 0.2},
    ], NOW)["today"]
    assert missing_out["tokens_in"] == 4
    assert missing_out["tokens_out"] == UNMEASURED
    assert missing_out["usd"] == 0.2

    # Yesterday has no OUT count. Today is complete. Week must not invent 0.
    split = meter_window([
        _settled(NOW, tin=5, tout=1, usd=0.3),
        {"at": YESTERDAY, "tokens_in": 2, "usd": 0.1, "cost_kind": "MEASURED"},
    ], NOW)
    assert split["today"] == {"tokens_in": 5, "tokens_out": 1, "usd": 0.3}
    assert split["week"]["tokens_in"] == 7
    assert split["week"]["tokens_out"] == UNMEASURED
    assert split["week"]["usd"] == 0.4


def test_bad_row_refused_not_counted():
    good = _settled(NOW, tin=8, tout=3, usd=0.5)
    bad = {"event": "SPEND_SETTLED", "t": _epoch(NOW), "payload": {
        "measured_usd": 1, "provenance": "measured",
        "tokens": {"in": -5, "out": 1},
    }}
    try:
        meter_window([good, bad], NOW)
    except MeterWindowError as exc:
        assert exc.kind == "BAD_ROW"
    else:
        raise AssertionError("bad row was counted")
    try:
        meter_window([good, "nope"], NOW)
    except MeterWindowError as exc:
        assert exc.kind == "BAD_ROW"
    else:
        raise AssertionError("non-object row was counted")
    try:
        meter_window([{"at": "2026-09-23T15:00:00", "tokens_in": 1, "tokens_out": 1, "usd": 1}], NOW)
    except MeterWindowError as exc:
        assert exc.kind == "BAD_ROW"
    else:
        raise AssertionError("naive timestamp was counted")
