"""Floor, liveness, and a stale watermark for a session heartbeat."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from cosmos_hermes import Refuse, secret_shape
from heartbeat import (
    MIN_INTERVAL_S,
    POLICY_CAP,
    SCHEMA,
    Beat,
    Heartbeat,
    Interval,
    Snapshot,
    rebuild,
)


def _refuse(call: Callable[[], object]) -> str:
    with pytest.raises(Refuse) as caught:
        call()
    return caught.value.code


def _story() -> tuple[Beat, Beat, Beat, str, Snapshot, bool]:
    """Nora pins the porch-light session on the field-notes card."""
    session = Heartbeat(90)
    opened = session.beat(100, True)
    note = session.beat(130, False)

    def late() -> None:
        session.beat(90, True)

    stale = _refuse(late)
    assert stale == "STALE"
    assert session.last_at == 130
    assert session.alive is True
    assert session.task_ok is False
    cleared = session.beat(400, True)
    assert session.miss(400) is False
    assert session.miss(490) is False
    due = session.miss(491)
    snap = session.snapshot()
    assert snap == rebuild(90, (opened, note, cleared))
    assert snap.alive is True
    assert snap.task_ok is True
    assert snap.last_at == 400
    return (opened, note, cleared, stale, snap, due)


def test_example_heartbeat() -> None:
    assert _story() == _story()


def test_schema_floor_and_failed_task_stays_alive() -> None:
    assert SCHEMA == "cosmos-hermes-heartbeat/1"
    assert MIN_INTERVAL_S == 15
    assert POLICY_CAP == 2_147_483_647
    low = Heartbeat(5)
    assert low.requested_s == 5
    assert low.interval_s == 15
    assert low.interval == Interval(5, 15)
    assert low.alive is False
    assert low.task_ok is None
    assert low.last_at is None
    assert low.snapshot() == Snapshot(SCHEMA, 5, 15, False, None, None)
    failed = low.beat(100, False)
    assert failed.schema == SCHEMA
    assert failed.at == 100
    assert failed.alive is True
    assert failed.task_ok is False
    assert failed.requested_s == 5
    assert failed.interval_s == 15
    assert low.alive is True
    assert low.task_ok is False
    assert low.last_at == 100
    assert low.miss(100) is False
    assert low.miss(115) is False
    assert low.miss(116) is True
    other = Heartbeat(5)
    assert other.beat(100, False) == failed
    assert low.snapshot() == rebuild(5, (failed,))
    text = repr(low) + repr(low.interval) + repr(failed) + repr(low.snapshot())
    assert "sk-" not in text
    assert "Bearer" not in text
    assert "api_key=" not in text
    assert secret_shape(text) is False


def test_cap_records_request_and_keeps_floor() -> None:
    assert Heartbeat(0).interval == Interval(0, 15)
    assert Heartbeat(14).interval == Interval(14, 15)
    exact = Heartbeat(15)
    assert exact.requested_s == 15
    assert exact.interval_s == 15
    wide = Heartbeat(POLICY_CAP)
    assert wide.requested_s == POLICY_CAP
    assert wide.interval_s == POLICY_CAP
    wide.beat(0, True)
    assert wide.miss(POLICY_CAP) is False
    assert wide.alive is True
    assert wide.task_ok is True

    def above() -> None:
        Heartbeat(POLICY_CAP + 1)

    assert _refuse(above) == "OUT_OF_RANGE"
    assert POLICY_CAP == 2_147_483_647
    held = Heartbeat(1)
    held.beat(0, False)
    assert held.miss(15) is False
    assert held.miss(16) is True
    assert held.alive is True
    assert held.task_ok is False


def test_fresh_100_and_130_then_90_is_stale() -> None:
    session = Heartbeat(30)
    first = session.beat(100, True)
    second = session.beat(130, False)
    assert first.at == 100
    assert second.at == 130
    assert second.alive is True
    assert second.task_ok is False
    before = session.snapshot()

    def late() -> None:
        session.beat(90, True)

    assert _refuse(late) == "STALE"

    def same() -> None:
        session.beat(130, True)

    assert _refuse(same) == "REPLAY"

    def early_miss() -> None:
        session.miss(129)

    assert _refuse(early_miss) == "STALE"
    assert session.snapshot() == before
    assert session.last_at == 130
    assert session.task_ok is False
    assert session.miss(130) is False
    assert session.miss(160) is False
    assert session.miss(161) is True


def test_miss_is_strict_and_one_beat_clears_a_gap() -> None:
    pulse = Heartbeat(30)
    assert pulse.interval_s == 30
    pulse.beat(0, True)
    assert pulse.miss(30) is False
    assert pulse.miss(31) is True
    assert pulse.miss(10_000) is True
    assert pulse.last_at == 0
    again = pulse.beat(10_000, False)
    assert again.alive is True
    assert again.task_ok is False
    assert pulse.miss(10_000) is False
    assert pulse.miss(10_030) is False
    assert pulse.miss(10_031) is True
    held = pulse.snapshot()

    def replay() -> None:
        pulse.beat(10_000, True)

    assert _refuse(replay) == "REPLAY"
    assert pulse.snapshot() == held
    moved = pulse.beat(10_031, True)
    assert moved.alive is True
    assert moved.task_ok is True
    assert pulse.miss(10_031) is False


def test_rebuild_reproduces_public_state() -> None:
    pulse = Heartbeat(15)
    first = pulse.beat(100, True)
    second = pulse.beat(130, False)
    snap = pulse.snapshot()
    assert snap == rebuild(15, (first, second))
    assert rebuild(15, ()) == Heartbeat(15).snapshot()
    other = Heartbeat(40)
    foreign = other.beat(200, True)

    def mixed() -> None:
        rebuild(15, (first, foreign))

    assert _refuse(mixed) == "MISMATCH"
    assert pulse.snapshot() == snap

    def reversed_rows() -> None:
        rebuild(15, (second, first))

    assert _refuse(reversed_rows) == "STALE"

    def duplicated() -> None:
        rebuild(15, (first, first))

    assert _refuse(duplicated) == "REPLAY"


def test_refusal_codes() -> None:
    def not_int_bool() -> None:
        Heartbeat(True)

    def not_int_float() -> None:
        Heartbeat(15.0)

    def not_int_text() -> None:
        Heartbeat("15")

    def not_int_none() -> None:
        Heartbeat(None)

    def below_range() -> None:
        Heartbeat(-1)

    def above_cap() -> None:
        Heartbeat(POLICY_CAP + 1)

    assert _refuse(not_int_bool) == "NOT_INT"
    assert _refuse(not_int_float) == "NOT_INT"
    assert _refuse(not_int_text) == "NOT_INT"
    assert _refuse(not_int_none) == "NOT_INT"
    assert _refuse(below_range) == "OUT_OF_RANGE"
    assert _refuse(above_cap) == "OUT_OF_RANGE"
    bare = Heartbeat(15)

    def no_beat() -> None:
        bare.miss(0)

    def miss_bool() -> None:
        bare.miss(True)

    def miss_low() -> None:
        bare.miss(-1)

    def beat_bool() -> None:
        bare.beat(True, True)

    def beat_low() -> None:
        bare.beat(-1, True)

    def beat_high() -> None:
        bare.beat(10**18 + 1, True)

    def beat_none() -> None:
        bare.beat(0, None)

    def beat_one() -> None:
        bare.beat(0, 1)

    def beat_text() -> None:
        bare.beat(0, "no")

    assert _refuse(no_beat) == "NO_BEAT"
    assert bare.alive is False
    assert _refuse(miss_bool) == "NOT_INT"
    assert _refuse(miss_low) == "OUT_OF_RANGE"
    assert _refuse(beat_bool) == "NOT_INT"
    assert _refuse(beat_low) == "OUT_OF_RANGE"
    assert _refuse(beat_high) == "OUT_OF_RANGE"
    assert _refuse(beat_none) == "NOT_BOOL"
    assert _refuse(beat_one) == "NOT_BOOL"
    assert _refuse(beat_text) == "NOT_BOOL"
    assert bare.last_at is None

    def bad_interval() -> None:
        Interval(4, 16)

    def interval_low_effective() -> None:
        Interval(4, 14)

    def interval_low_requested() -> None:
        Interval(-1, 15)

    def interval_bool() -> None:
        Interval(True, 15)

    def interval_above() -> None:
        Interval(POLICY_CAP + 1, 15)

    assert _refuse(bad_interval) == "BAD_INTERVAL"
    assert _refuse(interval_low_effective) == "OUT_OF_RANGE"
    assert _refuse(interval_low_requested) == "OUT_OF_RANGE"
    assert _refuse(interval_bool) == "NOT_INT"
    assert _refuse(interval_above) == "OUT_OF_RANGE"
    assert Interval(0, 15) == Heartbeat(0).interval

    def not_alive() -> None:
        Beat(SCHEMA, 0, False, True, 15, 15)

    def alive_one() -> None:
        Beat(SCHEMA, 0, 1, True, 15, 15)  # type: ignore[arg-type]

    def task_zero() -> None:
        Beat(SCHEMA, 0, True, 0, 15, 15)  # type: ignore[arg-type]

    def interval_too_small() -> None:
        Beat(SCHEMA, 0, True, True, 5, 5)

    def interval_disagrees() -> None:
        Beat(SCHEMA, 0, True, True, 40, 15)

    def beat_negative() -> None:
        Beat(SCHEMA, -1, True, True, 15, 15)

    def bad_schema() -> None:
        Beat("cosmos-hermes-heartbeat/2", 0, True, True, 15, 15)

    def schema_not_text() -> None:
        Beat(15, 0, True, True, 15, 15)  # type: ignore[arg-type]

    def schema_nul() -> None:
        Beat("bad\x00schema", 0, True, True, 15, 15)

    def schema_oversize() -> None:
        Beat("x" * 65, 0, True, True, 15, 15)

    assert _refuse(not_alive) == "NOT_ALIVE"
    assert _refuse(alive_one) == "NOT_BOOL"
    assert _refuse(task_zero) == "NOT_BOOL"
    assert _refuse(interval_too_small) == "OUT_OF_RANGE"
    assert _refuse(interval_disagrees) == "BAD_INTERVAL"
    assert _refuse(beat_negative) == "OUT_OF_RANGE"
    assert _refuse(bad_schema) == "BAD_SCHEMA"
    assert _refuse(schema_not_text) == "NOT_TEXT"
    assert _refuse(schema_nul) == "NULL_BYTE"
    assert _refuse(schema_oversize) == "OVERSIZE"
    assert Beat(SCHEMA, 0, True, False, 5, 15).alive is True

    def snapshot_mismatch() -> None:
        Snapshot(SCHEMA, 15, 15, True, None, None)

    def snapshot_not_alive() -> None:
        Snapshot(SCHEMA, 15, 15, False, True, 10)

    def bad_rows() -> None:
        rebuild(15, [Beat(SCHEMA, 0, True, True, 15, 15)])

    def bad_row() -> None:
        rebuild(15, ("beat",))

    assert _refuse(snapshot_mismatch) == "MISMATCH"
    assert _refuse(snapshot_not_alive) == "NOT_ALIVE"
    assert _refuse(bad_rows) == "BAD_RECORD"
    assert _refuse(bad_row) == "BAD_RECORD"
    fresh = Heartbeat(15).beat(3, True)
    assert rebuild(15, (fresh,)).last_at == fresh.at


def test_module_has_no_thread_sleep_or_io() -> None:
    source = Path(__file__).with_name("heartbeat.py").read_text(encoding="utf-8")
    for banned in (
        "threading",
        "subprocess",
        "socket",
        "urllib",
        "requests",
        "pickle",
        "time.sleep",
        "time.time",
        "eval(",
        "exec(",
        "compile(",
        "__import__",
    ):
        assert banned not in source
