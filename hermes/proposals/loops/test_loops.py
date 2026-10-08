"""Cap 8, recorded stop_reason, and session loop commands."""

from __future__ import annotations

import ast
import inspect
from collections.abc import Callable
from dataclasses import replace
from typing import Any, cast

import pytest

import loops
from cosmos_hermes import Refuse
from loops import (
    INTERVAL_CAP,
    MIN_INTERVAL_S,
    POLICY_CAP,
    SCHEMA,
    SELF_CEILING_S,
    SELF_FLOOR_S,
    Board,
    Capped,
    Loop,
    define,
    rebuild,
    snapshot,
    tick,
)


def _expect(code: str, fn: Callable[[], object]) -> None:
    with pytest.raises(Refuse) as caught:
        fn()
    assert caught.value.code == code


def _ninth(loop: Loop) -> Loop:
    with pytest.raises(Capped) as caught:
        tick(loop)
    return caught.value.loop


def _story() -> tuple[Loop, Loop, Loop, Board, Loop]:
    plan = define(
        "check kiln",
        8,
        prompt="Check the kiln, then write the glaze card for Mira",
        until="the cone has dropped",
        interval_s=120,
    )
    light = define(
        "porch light",
        2,
        prompt="Note the porch light in the evening session",
        interval_s=60,
    )
    session = loops.install(loops.install(loops.make_board(), light), plan)
    walked = plan
    for _step in range(POLICY_CAP):
        walked = tick(walked)
    wider = define(
        "check kiln",
        24,
        prompt="Check the kiln, then write the glaze card for Mira",
        interval_s=120,
    )
    return plan, walked, _ninth(walked), session, wider


def test_schema_policy_and_no_run_loop() -> None:
    assert SCHEMA == "cosmos-hermes-loops/1"
    assert loops.SCHEMA == SCHEMA
    assert POLICY_CAP == 8
    assert MIN_INTERVAL_S == 30
    assert SELF_FLOOR_S == 60
    assert SELF_CEILING_S == 900
    assert INTERVAL_CAP == 86_400
    expected = (
        "INTERVAL_CAP",
        "MIN_INTERVAL_S",
        "POLICY_CAP",
        "SCHEMA",
        "SELF_CEILING_S",
        "SELF_FLOOR_S",
        "Board",
        "Capped",
        "Loop",
        "LoopStatus",
        "Snapshot",
        "complete",
        "current",
        "define",
        "install",
        "interrupt",
        "judge",
        "make_board",
        "note_reply",
        "pause",
        "rebuild",
        "resume",
        "snapshot",
        "status",
        "stop",
        "tick",
    )
    assert loops.__all__ == list(expected)
    for name in expected:
        assert hasattr(loops, name)
    tree = ast.parse(inspect.getsource(loops))
    assert not any(isinstance(node, ast.While) for node in ast.walk(tree))
    source = inspect.getsource(loops)
    assert "while True" not in source
    assert "while 1" not in source


def test_example_loops() -> None:
    one = _story()
    two = _story()
    assert one == two
    plan, walked, stopped, session, wider = one
    assert plan.schema == SCHEMA
    assert plan.name == "check kiln"
    assert plan.interval_s == 120
    assert plan.requested_interval == 120
    assert plan.kind == "FIXED"
    assert plan.requested == POLICY_CAP
    assert plan.cap == POLICY_CAP
    assert plan.effective == POLICY_CAP
    assert plan.until == "the cone has dropped"
    assert walked.ticks == POLICY_CAP
    assert walked.status == "ACTIVE"
    assert walked.stop_reason == ""
    assert stopped.status == "STOPPED"
    assert stopped.stop_reason == "LOOP_CAP"
    assert stopped.ticks == POLICY_CAP
    assert stopped.effective == POLICY_CAP
    assert loops.current(session).name == "check kiln"
    assert wider.requested == 24
    assert wider.cap == POLICY_CAP
    assert wider.effective == POLICY_CAP
    assert wider.interval_s == 120
    copied = rebuild(snapshot(walked))
    assert copied == walked
    assert copied is not walked
    assert rebuild(copied) == copied
    assert rebuild(stopped) == stopped

    def five_seconds() -> None:
        define("check kiln", 8, prompt="Check the kiln", interval_s=5)

    _expect("OUT_OF_RANGE", five_seconds)


def test_define_success_and_same_inputs() -> None:
    left = define("deploy", 4, prompt="check the deploy", until="it is live", interval_s=45)
    right = define("deploy", 4, prompt="check the deploy", until="it is live", interval_s=45)
    assert left == right
    assert left.schema == SCHEMA
    assert left.name == "deploy"
    assert left.prompt == "check the deploy"
    assert left.until == "it is live"
    assert left.requested == 4
    assert left.cap == POLICY_CAP
    assert left.effective == 4
    assert left.ticks == 0
    assert left.stop_reason == ""
    assert left.status == "ACTIVE"
    assert left.kind == "FIXED"
    assert left.requested_interval == 45
    assert left.interval_s == 45
    assert left.next_interval_s == 45
    assert left.goal_deferred is False
    named = define("deploy", 4)
    assert named.prompt == "deploy"
    assert named.kind == "SELF"
    assert named.requested_interval is None
    assert named.interval_s == SELF_FLOOR_S
    assert named.next_interval_s == SELF_FLOOR_S
    view = loops.status(left)
    assert view.schema == SCHEMA
    assert view.remaining == 4
    assert view.interval_s == 45
    assert view.next_interval_s == 45
    assert view.cap == POLICY_CAP
    blob = repr(left) + repr(view) + repr(snapshot(left))
    assert "sk-" not in blob
    assert "api_key" not in blob
    assert "Bearer" not in blob


def test_higher_request_records_stop_reason_at_cap() -> None:
    loop = define("deploy", 50)
    assert loop.requested == 50
    assert loop.cap == 8
    assert loop.effective == 8
    stepped = loop
    for _index in range(POLICY_CAP):
        stepped = tick(stepped)
    assert stepped.ticks == POLICY_CAP
    assert stepped.stop_reason == ""
    assert stepped.status == "ACTIVE"
    assert loop.ticks == 0
    assert tick(loop) == tick(loop)
    err_loop = _ninth(stepped)
    assert err_loop.stop_reason == "LOOP_CAP"
    assert err_loop.status == "STOPPED"
    assert err_loop.ticks == POLICY_CAP
    assert err_loop.requested == 50
    assert err_loop.effective == 8
    assert stepped.stop_reason == ""

    def again() -> None:
        tick(err_loop)

    def resume_stopped() -> None:
        loops.resume(err_loop)

    _expect("STOPPED", again)
    _expect("STOPPED", resume_stopped)


def test_lower_request_exact_policy_and_method() -> None:
    short = define("short", 3)
    assert short.requested == 3
    assert short.effective == 3
    assert short.cap == POLICY_CAP
    done = tick(tick(tick(short)))
    assert done.ticks == 3
    assert _ninth(done).stop_reason == "LOOP_CAP"
    exact = define("exact", POLICY_CAP)
    assert exact.requested == POLICY_CAP
    assert exact.effective == POLICY_CAP
    assert exact.tick() == tick(exact)
    one = define("one", 1)
    assert tick(one).ticks == 1

    def over_one() -> None:
        tick(tick(one))

    _expect("LOOP_CAP", over_one)


def test_goal_defers_without_spending() -> None:
    loop = define("watch", 1)
    held = tick(loop, goal_active=True)
    assert held.ticks == 0
    assert held.goal_deferred is True
    assert tick(held, goal_active=True) is held
    spent = tick(held, goal_active=False)
    assert spent.ticks == 1
    assert spent.goal_deferred is False
    boundary = define("watch", 8)
    for _index in range(POLICY_CAP):
        boundary = tick(boundary)
    deferred = tick(boundary, goal_active=True)
    assert deferred.ticks == POLICY_CAP
    assert deferred.stop_reason == ""
    assert deferred.goal_deferred is True
    assert _ninth(deferred).stop_reason == "LOOP_CAP"


def test_commands_until_and_cadence() -> None:
    loop = define("queue", 4, until="depth is zero")
    paused = loops.pause(loop)
    assert paused.status == "PAUSED"
    assert paused.stop_reason == ""

    def tick_paused() -> None:
        tick(paused)

    def pause_paused() -> None:
        loops.pause(paused)

    _expect("PAUSED", tick_paused)
    _expect("NOT_ACTIVE", pause_paused)
    resumed = loops.resume(paused)
    assert resumed.status == "ACTIVE"
    assert tick(resumed).ticks == 1
    cancelled = loops.interrupt(loop)
    assert cancelled.status == "PAUSED"
    assert loops.resume(cancelled).status == "ACTIVE"
    ended = loops.stop(loop)
    assert ended.stop_reason == "STOP"
    assert ended.status == "STOPPED"

    def stop_ended() -> None:
        loops.stop(ended)

    def tick_ended() -> None:
        tick(ended)

    _expect("STOPPED", stop_ended)
    _expect("STOPPED", tick_ended)
    finished = loops.complete(paused)
    assert finished.stop_reason == "LOOP_COMPLETE"

    def complete_finished() -> None:
        loops.complete(finished)

    _expect("STOPPED", complete_finished)
    same = loops.judge(loop, "CONTINUE")
    assert same is loop
    achieved = loops.judge(loop, "ACHIEVED")
    assert achieved.status == "STOPPED"
    assert achieved.stop_reason == "UNTIL"
    blocked = loops.judge(loop, "UNACHIEVABLE")
    assert blocked.status == "PAUSED"
    assert blocked.stop_reason == "UNTIL"

    def tick_blocked() -> None:
        tick(blocked)

    _expect("PAUSED", tick_blocked)
    cleared = loops.resume(blocked)
    assert cleared.stop_reason == ""
    assert cleared.status == "ACTIVE"
    paced = define("migrate", 4)
    first = loops.note_reply(paced, "digest-a")
    assert first.next_interval_s == SELF_FLOOR_S
    second = loops.note_reply(first, "digest-a")
    assert second.next_interval_s == 120
    third = loops.note_reply(second, "digest-a")
    assert third.next_interval_s == 240
    fourth = loops.note_reply(third, "digest-a")
    assert fourth.next_interval_s == 480
    fifth = loops.note_reply(fourth, "digest-a")
    assert fifth.next_interval_s == SELF_CEILING_S
    sixth = loops.note_reply(fifth, "digest-a")
    assert sixth.next_interval_s == SELF_CEILING_S
    snapped = loops.note_reply(sixth, "digest-b")
    assert snapped.next_interval_s == SELF_FLOOR_S
    assert snapped.last_digest == "digest-b"
    floor = define("fixed", 2, interval_s=MIN_INTERVAL_S)
    assert floor.requested_interval == MIN_INTERVAL_S
    assert floor.interval_s == MIN_INTERVAL_S
    assert floor.kind == "FIXED"
    top = define("day", 1, interval_s=INTERVAL_CAP)
    assert top.interval_s == INTERVAL_CAP
    kiln = define("check kiln", 8, interval_s=120)
    assert kiln.interval_s == 120
    assert kiln.effective == POLICY_CAP

    def note_fixed() -> None:
        loops.note_reply(floor, "digest-a")

    _expect("NOT_SELF", note_fixed)
    board = loops.make_board()

    def empty_board() -> None:
        loops.current(board)

    _expect("EMPTY", empty_board)
    held = loops.install(board, loop)
    replaced = loops.install(held, define("other", 2))
    assert loops.current(replaced).name == "other"
    assert loops.current(held).name == "queue"
    view = loops.status(snapped)
    assert view.kind == "SELF"
    assert view.interval_s == SELF_FLOOR_S
    assert view.until == ""
    assert view.goal_deferred is False
    assert rebuild(snapshot(snapped)) == snapped


def test_interval_below_floor_refuses() -> None:
    def five() -> None:
        define("check kiln", 8, interval_s=5)

    def ten() -> None:
        define("fixed", 2, interval_s=10)

    def twenty_nine() -> None:
        define("fixed", 2, interval_s=29)

    def over_day() -> None:
        define("fixed", 2, interval_s=INTERVAL_CAP + 1)

    def zero() -> None:
        define("fixed", 2, interval_s=0)

    def flagged() -> None:
        define("fixed", 2, interval_s=True)

    _expect("OUT_OF_RANGE", five)
    _expect("OUT_OF_RANGE", ten)
    _expect("OUT_OF_RANGE", twenty_nine)
    _expect("OUT_OF_RANGE", over_day)
    _expect("OUT_OF_RANGE", zero)
    _expect("NOT_INT", flagged)


def test_refusal_codes() -> None:
    loop = define("job", 2, until="done", interval_s=40)
    paused = loops.pause(loop)

    def not_text() -> None:
        define(1, 1)

    def nul() -> None:
        define("bad\x00", 1)

    def oversize() -> None:
        define("a" * 201, 1)

    def empty_name() -> None:
        define("", 1)

    def blank_name() -> None:
        define("   ", 1)

    def bad_name() -> None:
        define(" job", 1)

    def bool_iters() -> None:
        define("job", True)

    def text_iters() -> None:
        define("job", "8")

    def unlimited() -> None:
        define("job", 0)

    def negative() -> None:
        define("job", -1)

    def huge() -> None:
        define("job", 10**12)

    def bad_prompt() -> None:
        define("job", 1, prompt="\nnope")

    def empty_prompt() -> None:
        define("job", 1, prompt="  ")

    def bad_until() -> None:
        define("job", 1, until=" later")

    def text_interval() -> None:
        define("job", 1, interval_s="30")

    def bad_loop() -> None:
        tick("nope")

    def bad_bool() -> None:
        tick(loop, goal_active=1)

    def not_paused() -> None:
        loops.resume(loop)

    def no_until() -> None:
        loops.judge(define("job", 1), "CONTINUE")

    def bad_verdict() -> None:
        loops.judge(loop, "MAYBE")

    def judge_paused() -> None:
        loops.judge(paused, "CONTINUE")

    def empty_digest() -> None:
        loops.note_reply(define("paced", 1), "")

    def bad_digest() -> None:
        loops.note_reply(define("paced", 1), " digest")

    def note_paused() -> None:
        loops.note_reply(paused, "digest")

    def bad_board() -> None:
        loops.install("board", loop)

    def bad_schema() -> None:
        replace(loop, schema="nope")

    def bad_cap() -> None:
        replace(loop, cap=9)

    def bad_effective() -> None:
        replace(loop, effective=8)

    def ticks_over_effective() -> None:
        replace(loop, ticks=4)

    def ticks_over_policy() -> None:
        replace(loop, ticks=9)

    def ticks_negative() -> None:
        replace(loop, ticks=-1)

    def ticks_bool() -> None:
        replace(loop, ticks=cast(Any, True))

    def requested_zero() -> None:
        replace(loop, requested=0)

    def bad_kind() -> None:
        replace(loop, kind=cast(Any, "NOPE"))

    def bad_status() -> None:
        replace(loop, status=cast(Any, "NOPE"))

    def active_with_stop() -> None:
        replace(loop, stop_reason="STOP")

    def bad_flag() -> None:
        replace(loop, goal_deferred=cast(Any, "yes"))

    def off_cadence() -> None:
        replace(loop, next_interval_s=90)

    def board_shape() -> None:
        Board(loop=cast(Any, "nope"))

    def rebuild_map() -> None:
        rebuild(cast(Any, {"name": "job"}))

    def install_snapshot() -> None:
        loops.install(loops.make_board(), snapshot(loop))

    _expect("NOT_TEXT", not_text)
    _expect("NULL_BYTE", nul)
    _expect("OVERSIZE", oversize)
    _expect("EMPTY", empty_name)
    _expect("EMPTY", blank_name)
    _expect("BAD_NAME", bad_name)
    _expect("NOT_INT", bool_iters)
    _expect("NOT_INT", text_iters)
    _expect("UNLIMITED", unlimited)
    _expect("OUT_OF_RANGE", negative)
    _expect("OUT_OF_RANGE", huge)
    _expect("BAD_PROMPT", bad_prompt)
    _expect("EMPTY", empty_prompt)
    _expect("BAD_UNTIL", bad_until)
    _expect("NOT_INT", text_interval)
    _expect("BAD_LOOP", bad_loop)
    _expect("NOT_BOOL", bad_bool)
    _expect("NOT_PAUSED", not_paused)
    _expect("NO_UNTIL", no_until)
    _expect("BAD_VERDICT", bad_verdict)
    _expect("NOT_ACTIVE", judge_paused)
    _expect("EMPTY", empty_digest)
    _expect("BAD_DIGEST", bad_digest)
    _expect("NOT_ACTIVE", note_paused)
    _expect("BAD_BOARD", bad_board)
    _expect("BAD_LOOP", bad_schema)
    _expect("BAD_CAP", bad_cap)
    _expect("BAD_CAP", bad_effective)
    _expect("BAD_CAP", ticks_over_effective)
    _expect("OUT_OF_RANGE", ticks_over_policy)
    _expect("OUT_OF_RANGE", ticks_negative)
    _expect("NOT_INT", ticks_bool)
    _expect("UNLIMITED", requested_zero)
    _expect("BAD_KIND", bad_kind)
    _expect("BAD_STATUS", bad_status)
    _expect("BAD_STATUS", active_with_stop)
    _expect("NOT_BOOL", bad_flag)
    _expect("BAD_CAP", off_cadence)
    _expect("BAD_BOARD", board_shape)
    _expect("BAD_LOOP", rebuild_map)
    _expect("BAD_LOOP", install_snapshot)
    secrets = ("sk-abcdefghijklmnop", "Bearer abcdefghij", "api_key=abcdefghij")

    def secret_name(raw: str) -> Callable[[], None]:
        def run() -> None:
            define(raw, 1)

        return run

    def secret_prompt() -> None:
        define("kiln", 1, prompt="sk-abcdefghijklmnop")

    def secret_until() -> None:
        define("kiln", 1, until="api_key=abcdefghij")

    def secret_digest() -> None:
        loops.note_reply(define("paced", 1), "Bearer abcdefghij")

    for raw in secrets:
        _expect("SECRET", secret_name(raw))
        with pytest.raises(Refuse) as caught:
            define(raw, 1)
        assert raw not in str(caught.value)
        assert raw not in repr(caught.value)
    _expect("SECRET", secret_prompt)
    _expect("SECRET", secret_until)
    _expect("SECRET", secret_digest)
    stopped = loops.stop(loop)
    capped = replace(
        stopped,
        stop_reason="LOOP_CAP",
        ticks=stopped.effective,
        effective=stopped.effective,
    )
    assert capped.stop_reason == "LOOP_CAP"

    def capped_ticks() -> None:
        replace(capped, ticks=0)

    def deferred_stopped() -> None:
        replace(stopped, goal_deferred=True)

    def bad_capped() -> None:
        Capped(cast(Any, "no"))

    _expect("BAD_CAP", capped_ticks)
    _expect("BAD_STATUS", deferred_stopped)
    _expect("BAD_LOOP", bad_capped)


def test_status_refuses_a_forged_view() -> None:
    loop = define("job", 2, until="done", interval_s=40)
    view = loops.status(loop)

    def active_stopped() -> None:
        replace(view, stop_reason="STOP")

    def off_ladder() -> None:
        paced = loops.status(define("paced", 2))
        replace(paced, next_interval_s=100)

    def fixed_drift() -> None:
        replace(view, next_interval_s=90)

    def deferred_view() -> None:
        replace(view, status="PAUSED", stop_reason="", goal_deferred=True)

    _expect("BAD_STATUS", active_stopped)
    _expect("BAD_CAP", off_ladder)
    _expect("BAD_CAP", fixed_drift)
    _expect("BAD_STATUS", deferred_view)
    assert view.interval_s == 40
    assert rebuild(snapshot(loop)) == loop
