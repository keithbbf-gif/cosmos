"""Lane assignments, policy cap, one crash retry, and a spawn that refuses."""

from __future__ import annotations

import ast
import hashlib
import threading
from collections.abc import Callable
from pathlib import Path

import pytest

from cosmos_hermes import Refuse, secret_shape
from kanban_lanes import (
    POLICY_WORKER_CAP,
    RETRY_FAILURE,
    SCHEMA,
    Assignment,
    Board,
    Event,
    Lane,
    assign,
    crash,
    make_board,
    make_lane,
    rebuild,
    retry,
    spawn,
    spec_argv,
    terminate,
)


def _err(fn: Callable[[], object]) -> Refuse:
    with pytest.raises(Refuse) as caught:
        fn()
    err = caught.value
    assert secret_shape(str(err)) is False
    assert secret_shape(repr(err)) is False
    return err


def _lane_at(board: Board, index: int) -> Lane:
    rows = board.lanes
    if index < 0 or index >= len(rows):
        raise AssertionError(index)
    return rows[index]


def _asg(board: Board, index: int) -> Assignment:
    rows = board.assignments
    if index < 0 or index >= len(rows):
        raise AssertionError(index)
    return rows[index]


def _ev(board: Board, index: int) -> Event:
    rows = board.events
    if index < 0 or index >= len(rows):
        raise AssertionError(index)
    return rows[index]


def _past(board: Board, index: int) -> bool:
    return index >= len(board.assignments)


def _kiln(cap: object = POLICY_WORKER_CAP, kind: str = "profile") -> Lane:
    return make_lane(
        "kiln",
        "kiln",
        kind,
        credential_id="cred-kiln",
        allow=("py",),
        requested_cap=cap,
    )


def _web() -> Lane:
    return make_lane(
        "web",
        "web",
        "external",
        credential_id="cred-web",
        allow=("py",),
    )


def _board(cap: object = POLICY_WORKER_CAP) -> Board:
    return make_board((_kiln(cap),))


def _put(
    board: Board,
    card: str,
    *,
    now: int,
    fence: str,
    lane: str = "kiln",
    cred: str = "cred-kiln",
    script: str = "job.py",
) -> tuple[Board, Assignment]:
    return assign(
        board,
        lane,
        card,
        "py",
        script,
        now=now,
        credential_id=cred,
        fence=fence,
    )


def _story() -> tuple[Board, str, str]:
    kiln = make_lane(
        "kiln",
        "kiln",
        "profile",
        credential_id="cred-kiln",
        allow=("py",),
        requested_cap=9,
    )
    web = _web()
    board = make_board((kiln, web))
    board, _card = _put(board, "porch-card", now=1_711_000_100, fence="session-card", script="form.py")
    board, _note = _put(board, "glaze-note", now=1_711_000_110, fence="session-note", script="note.py")
    board, _light = _put(
        board,
        "shop-light",
        now=1_711_000_120,
        fence="session-light",
        lane="web",
        cred="cred-web",
        script="lamp.py",
    )
    projected = rebuild(board.events)
    if projected != board:
        raise AssertionError("rebuild")
    code = ""
    detail = ""
    try:
        spawn(
            projected,
            "kiln",
            "porch-card",
            now=1_711_000_130,
            credential_id="cred-kiln",
        )
    except Refuse as exc:
        code = exc.code
        detail = exc.detail
    else:
        raise AssertionError("spawn returned")
    return projected, code, detail


def test_example_kanban_lanes() -> None:
    before = threading.active_count()
    first = _story()
    second = _story()
    after = threading.active_count()
    assert first == second
    assert after == before
    board, code, detail = first
    assert code == "NO_SPAWN"
    assert detail == ""
    assert SCHEMA == "cosmos-hermes-kanban_lanes/1"
    assert board.schema == SCHEMA
    assert board.at == 1_711_000_120
    kiln = _lane_at(board, 0)
    web = _lane_at(board, 1)
    assert kiln.lane_id == "kiln"
    assert kiln.kind == "profile"
    assert kiln.requested_cap == 9
    assert kiln.worker_cap == POLICY_WORKER_CAP == 4
    assert kiln.policy_cap == 4
    assert web.lane_id == "web"
    assert web.kind == "external"
    assert _asg(board, 0).card_id == "porch-card"
    assert _asg(board, 0).status == "ASSIGNED"
    assert _asg(board, 0).assignment_id == "a1"
    assert _asg(board, 1).card_id == "glaze-note"
    assert _asg(board, 2).card_id == "shop-light"
    assert _asg(board, 2).lane_id == "web"
    assert _past(board, 3) is True
    assert rebuild(board.events) == board
    assert rebuild(board.events) is not board
    text = repr(board)
    assert secret_shape(text) is False
    assert "sk-" not in text
    assert "api_key" not in text
    assert "Bearer" not in text
    assert "pid" not in Assignment.__dataclass_fields__


def test_policy_cap_and_freed_slot() -> None:
    raised = _kiln(100)
    assert raised.requested_cap == 100
    assert raised.worker_cap == 4
    assert raised.policy_cap == POLICY_WORKER_CAP
    board = make_board((raised,))
    for index in range(POLICY_WORKER_CAP):
        board, _row = _put(board, f"card-{index}", now=10 + index, fence=f"fence-{index}")
    held = board

    def extra() -> object:
        return _put(held, "card-extra", now=20, fence="fence-extra")

    full = _err(extra)
    assert full.code == "LANE_FULL"
    assert full.detail == "4"
    assert board is held

    tight = _board(1)
    tight, mug = _put(tight, "mug-card", now=30, fence="fence-mug")
    assert _lane_at(tight, 0).worker_cap == 1

    def lamp() -> object:
        return _put(tight, "lamp-card", now=31, fence="fence-lamp")

    blocked = _err(lamp)
    assert blocked.code == "LANE_FULL"
    assert blocked.detail == "1"
    tight, _crashed = crash(tight, mug.assignment_id, fence="fence-mug", now=32)
    assert _asg(tight, 0).status == "REQUEUED"
    tight, other = _put(tight, "lamp-card", now=33, fence="fence-lamp")
    assert other.status == "ASSIGNED"

    def retry_full() -> object:
        return retry(
            tight,
            "kiln",
            "mug-card",
            "py",
            "job.py",
            now=34,
            credential_id="cred-kiln",
            fence="fence-mug-2",
            failure=RETRY_FAILURE,
        )

    assert _err(retry_full).code == "LANE_FULL"
    tight, _done = terminate(tight, other.assignment_id, "COMPLETE", fence="fence-lamp", now=35)
    tight, again = retry(
        tight,
        "kiln",
        "mug-card",
        "py",
        "job.py",
        now=36,
        credential_id="cred-kiln",
        fence="fence-mug-2",
        failure="crash",
    )
    assert again.status == "ASSIGNED"
    assert again.crashes == 1
    assert again.requeues == 1
    assert again.assignment_id == "a3"


def test_one_crash_then_one_retry() -> None:
    assert RETRY_FAILURE == "crash"
    board, row = _put(_board(), "bowl-card", now=10, fence="fence-bowl")
    argv = spec_argv("py", "job.py")
    assert type(argv) is list
    assert argv == ["py", "job.py"]
    argv.append("extra")
    assert spec_argv("py", "job.py") == ["py", "job.py"]
    assert row.argv == ("py", "job.py")
    assert row.status == "ASSIGNED"
    board, row = crash(board, row.assignment_id, fence="fence-bowl", now=11)
    assert row.status == "REQUEUED"
    assert row.crashes == 1
    assert row.requeues == 1
    assert row.opened_at == 10
    assert board.at == 11
    saved = row

    def second_crash() -> object:
        return crash(board, saved.assignment_id, fence="fence-bowl", now=12)

    assert _err(second_crash).code == "REQUEUE_CAP"
    assert _err(second_crash).detail == "1"

    def direct() -> object:
        return _put(board, "bowl-card", now=13, fence="fence-direct")

    assert _err(direct).code == "NO_RETRY"

    def wrong() -> object:
        return retry(
            board,
            "kiln",
            "bowl-card",
            "py",
            "job.py",
            now=14,
            credential_id="cred-kiln",
            fence="fence-retry",
            failure="timeout",
        )

    assert _err(wrong).code == "NO_RETRY"
    board, retried = retry(
        board,
        "kiln",
        "bowl-card",
        "py",
        "again.py",
        now=15,
        credential_id="cred-kiln",
        fence="fence-retry",
        failure=RETRY_FAILURE,
    )
    assert retried.status == "ASSIGNED"
    assert retried.crashes == 1
    assert retried.argv == ("py", "again.py")
    assert _asg(board, 0).status == "REQUEUED"

    def second_retry() -> object:
        return retry(
            board,
            "kiln",
            "bowl-card",
            "py",
            "job.py",
            now=16,
            credential_id="cred-kiln",
            fence="fence-again",
            failure="crash",
        )

    assert _err(second_retry).code == "RETRY_CAP"

    def crash_retry() -> object:
        return crash(board, retried.assignment_id, fence="fence-retry", now=17)

    assert _err(crash_retry).code == "REQUEUE_CAP"
    board, done = terminate(board, retried.assignment_id, "COMPLETE", fence="fence-retry", now=18)
    assert done.status == "COMPLETE"
    board, review = _put(board, "review-note", now=19, fence="fence-review")
    board, review = terminate(board, review.assignment_id, "REVIEW", fence="fence-review", now=20)
    assert review.status == "REVIEW"
    board, blocked = _put(board, "block-light", now=21, fence="fence-block")
    board, blocked = terminate(board, blocked.assignment_id, "BLOCK", fence="fence-block", now=22)
    assert blocked.status == "BLOCKED"
    assert rebuild(board.events) == board
    with pytest.raises(AttributeError):
        setattr(done, "status", "DONE")


def test_spawn_starts_nothing() -> None:
    board, _row = _put(_board(), "porch-card", now=10, fence="session-card")
    before = threading.active_count()

    def go() -> None:
        spawn(board, "kiln", "porch-card", now=11, credential_id="cred-kiln")

    assert _err(go).code == "NO_SPAWN"
    assert threading.active_count() == before
    source = Path(assign.__code__.co_filename).read_text(encoding="utf-8")
    tree = ast.parse(source)
    banned = {
        "subprocess",
        "socket",
        "urllib",
        "requests",
        "pickle",
        "threading",
        "_thread",
        "asyncio",
        "multiprocessing",
        "http",
        "ctypes",
        "sched",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in banned
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            assert module.split(".")[0] not in banned
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in {"eval", "exec", "compile"}
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            assert node.func.attr not in {"Popen", "popen", "system", "fork", "start"}
        if isinstance(node, ast.Name):
            assert node.id not in {"Thread", "Popen", "Process"}


def _forged(body: str, prev: str = "0" * 64) -> Event:
    digest = hashlib.sha256((prev + "\n" + body).encode("ascii")).hexdigest()
    return Event(event_id=digest, prev_sha=prev, body=body, sha=digest, schema=SCHEMA)


def test_chain_rebuild_and_replay() -> None:
    board = make_board((_kiln(), _web()))
    first = _ev(board, 0)
    second = _ev(board, 1)

    def swapped() -> Board:
        return rebuild((second, first))

    def repeated() -> Board:
        return rebuild((first, first))

    def bad_sha() -> Event:
        return Event(
            event_id="0" * 64,
            prev_sha="0" * 64,
            body="NOPE",
            sha="0" * 64,
            schema=SCHEMA,
        )

    def bad_shape() -> Board:
        return rebuild((_forged("L|only"),))

    def not_event() -> Board:
        return rebuild(("nope",))

    assert _err(swapped).code == "CHAIN"
    assert _err(repeated).code == "DUPLICATE"
    assert _err(bad_sha).code == "CHAIN"
    assert _err(bad_shape).code == "BAD_EVENT"
    assert _err(not_event).code == "BAD_EVENT"
    assert rebuild(()) == make_board(())


class _Boom:
    def __eq__(self, other: object) -> bool:
        raise ValueError("eq")


def test_refusal_codes() -> None:
    board, row = _put(_board(), "bowl-card", now=10, fence="fence-bowl")
    seen: set[str] = set()

    def grab(code: str, fn: Callable[[], object]) -> None:
        err = _err(fn)
        assert err.code == code
        seen.add(code)

    def shell_one() -> object:
        return spec_argv("py job.py")

    def shell_meta() -> object:
        return spec_argv("py", "job.py;rm")

    def bad_list() -> object:
        return spec_argv(["py", "job.py"])

    def bad_none() -> object:
        return spec_argv(None)

    def empty_arg() -> object:
        return spec_argv("py", "")

    def secret_key() -> object:
        return spec_argv("sk-abcdefghij")

    def secret_assign() -> object:
        return spec_argv("py", "api_key=abcdefghij")

    def secret_bearer() -> object:
        return spec_argv("Bearer abcdefghij")

    def not_text() -> object:
        return spec_argv("py", 1)

    def null_byte() -> object:
        return spec_argv("p\x00y", "job.py")

    def oversize_text() -> object:
        return spec_argv("p" * 65, "job.py")

    def oversize_allow() -> object:
        tokens = tuple(f"t{index}" for index in range(33))
        return make_lane(
            "kiln",
            "kiln",
            "profile",
            credential_id="cred-kiln",
            allow=tokens,
        )

    def bad_id() -> object:
        return spec_argv("py", "job/py")

    def mode_off() -> object:
        return _kiln(kind="off")

    def mode_yolo() -> object:
        return _kiln(kind="yolo")

    def mode_container() -> object:
        return _kiln(kind="container")

    def mode_none() -> object:
        return make_lane(
            "kiln",
            "kiln",
            None,
            credential_id="cred-kiln",
            allow=("py",),
        )

    def empty_allow() -> object:
        return make_lane("kiln", "kiln", "profile", credential_id="cred-kiln", allow=())

    def string_allow() -> object:
        return make_lane("kiln", "kiln", "profile", credential_id="cred-kiln", allow="py")

    def missing_cred() -> object:
        return make_lane("kiln", "kiln", "profile", credential_id="", allow=("py",))

    def missing_none() -> object:
        return make_lane("kiln", "kiln", "profile", credential_id=None, allow=("py",))

    def secret_cred() -> object:
        return make_lane(
            "kiln",
            "kiln",
            "profile",
            credential_id="sk-abcdefghij",
            allow=("py",),
        )

    def cap_bool() -> object:
        return _kiln(True)

    def cap_text() -> object:
        return _kiln("4")

    def cap_zero() -> object:
        return _kiln(0)

    def cap_negative() -> object:
        return _kiln(-1)

    def clock_negative() -> object:
        return _put(board, "other-card", now=-1, fence="fence-other")

    def dup_allow() -> object:
        return make_lane(
            "kiln",
            "kiln",
            "profile",
            credential_id="cred-kiln",
            allow=("py", "py"),
        )

    def dup_lane() -> object:
        return make_board((_kiln(), _kiln()))

    def dup_owner() -> object:
        other = make_lane("web", "kiln", "external", credential_id="cred-web", allow=("py",))
        return make_board((_kiln(), other))

    def bad_board() -> object:
        return make_board("lane")

    def bad_lane() -> object:
        return make_board(("lane",))

    def assign_board() -> object:
        return assign(
            "board",
            "kiln",
            "other-card",
            "py",
            "job.py",
            now=11,
            credential_id="cred-kiln",
            fence="fence-other",
        )

    def unknown_lane() -> object:
        return assign(
            board,
            "missing",
            "other-card",
            "py",
            "job.py",
            now=11,
            credential_id="cred-kiln",
            fence="fence-other",
        )

    def cred_mismatch() -> object:
        return _put(board, "other-card", now=11, fence="fence-other", cred="cred-other")

    def not_allowed() -> object:
        return assign(
            board,
            "kiln",
            "other-card",
            "ruby",
            "job.py",
            now=11,
            credential_id="cred-kiln",
            fence="fence-other",
        )

    def duplicate_card() -> object:
        return _put(board, "bowl-card", now=11, fence="fence-other")

    def replay_fence() -> object:
        return _put(board, "other-card", now=11, fence="fence-bowl")

    def yolo_action() -> object:
        return terminate(board, row.assignment_id, "yolo", fence="fence-bowl", now=11)

    def off_action() -> object:
        return terminate(board, row.assignment_id, "off", fence="fence-bowl", now=11)

    def none_action() -> object:
        return terminate(board, row.assignment_id, None, fence="fence-bowl", now=11)

    def stale_clock() -> object:
        return crash(board, row.assignment_id, fence="fence-bowl", now=9)

    def stale_fence() -> object:
        return crash(board, row.assignment_id, fence="fence-other", now=11)

    def requeue_cap() -> object:
        crashed, _held = crash(board, row.assignment_id, fence="fence-bowl", now=11)
        return crash(crashed, row.assignment_id, fence="fence-bowl", now=12)

    def not_assigned() -> object:
        _closed, done = terminate(board, row.assignment_id, "COMPLETE", fence="fence-bowl", now=11)
        return crash(_closed, done.assignment_id, fence="fence-bowl", now=12)

    def closed() -> object:
        closed, _done = terminate(board, row.assignment_id, "COMPLETE", fence="fence-bowl", now=11)
        return _put(closed, "bowl-card", now=12, fence="fence-next")

    def no_retry_fresh() -> object:
        return retry(
            board,
            "kiln",
            "fresh-card",
            "py",
            "job.py",
            now=11,
            credential_id="cred-kiln",
            fence="fence-fresh",
            failure="crash",
        )

    def no_retry_class() -> object:
        crashed, _held = crash(board, row.assignment_id, fence="fence-bowl", now=11)
        return retry(
            crashed,
            "kiln",
            "bowl-card",
            "py",
            "job.py",
            now=12,
            credential_id="cred-kiln",
            fence="fence-class",
            failure="timeout",
        )

    def retry_cap() -> object:
        crashed, _held = crash(board, row.assignment_id, fence="fence-bowl", now=11)
        retried, _again = retry(
            crashed,
            "kiln",
            "bowl-card",
            "py",
            "job.py",
            now=12,
            credential_id="cred-kiln",
            fence="fence-once",
            failure="crash",
        )
        return retry(
            retried,
            "kiln",
            "bowl-card",
            "py",
            "job.py",
            now=13,
            credential_id="cred-kiln",
            fence="fence-twice",
            failure="crash",
        )

    def unknown_assignment() -> object:
        return crash(board, "a9", fence="fence-bowl", now=11)

    def bad_schema() -> object:
        lane = _kiln()
        return Lane(
            lane_id=lane.lane_id,
            assignee=lane.assignee,
            kind=lane.kind,
            worker_cap=lane.worker_cap,
            requested_cap=lane.requested_cap,
            policy_cap=lane.policy_cap,
            credential_id=lane.credential_id,
            allow=lane.allow,
            schema="nope",
        )

    def bad_limit() -> object:
        lane = _kiln()
        return Lane(
            lane_id=lane.lane_id,
            assignee=lane.assignee,
            kind=lane.kind,
            worker_cap=9,
            requested_cap=9,
            policy_cap=lane.policy_cap,
            credential_id=lane.credential_id,
            allow=lane.allow,
            schema=SCHEMA,
        )

    def bad_assignment() -> object:
        return Assignment(
            assignment_id=row.assignment_id,
            lane_id=row.lane_id,
            card_id=row.card_id,
            status="RUNNING",
            crashes=row.crashes,
            requeues=row.requeues,
            argv=row.argv,
            fence=row.fence,
            opened_at=row.opened_at,
            schema=SCHEMA,
        )

    def bad_event() -> object:
        return rebuild(None)

    def bad_fence() -> object:
        return _put(board, "other-card", now=11, fence="")

    def fence_none() -> object:
        return assign(
            board,
            "kiln",
            "other-card",
            "py",
            "job.py",
            now=11,
            credential_id="cred-kiln",
            fence=None,
        )

    def boom() -> object:
        return spec_argv(_Boom(), "job.py")

    def mismatch_board() -> object:
        lane = _kiln()
        return Board(lanes=(lane,), assignments=(), events=(), at=0, schema=SCHEMA)

    def no_spawn() -> object:
        spawn(board, "kiln", "bowl-card", now=11, credential_id="cred-kiln")
        return None

    def broken_chain() -> object:
        paired = make_board((_kiln(), _web()))
        return rebuild((_ev(paired, 1), _ev(paired, 0)))

    grab("SHELL_STRING", shell_one)
    grab("SHELL_STRING", shell_meta)
    grab("BAD_ARGV", bad_list)
    grab("BAD_ARGV", bad_none)
    grab("EMPTY_ARG", empty_arg)
    grab("SECRET", secret_key)
    grab("SECRET", secret_assign)
    grab("SECRET", secret_bearer)
    grab("NOT_TEXT", not_text)
    grab("NULL_BYTE", null_byte)
    grab("OVERSIZE", oversize_text)
    over = _err(oversize_allow)
    assert over.code == "OVERSIZE"
    assert over.detail == "32"
    seen.add("OVERSIZE")
    grab("BAD_ID", bad_id)
    grab("UNKNOWN_MODE", mode_off)
    grab("UNKNOWN_MODE", mode_yolo)
    grab("UNKNOWN_MODE", mode_container)
    grab("UNKNOWN_MODE", mode_none)
    grab("EMPTY_ALLOW", empty_allow)
    grab("EMPTY_ALLOW", string_allow)
    grab("MISSING_CRED", missing_cred)
    grab("MISSING_CRED", missing_none)
    grab("SECRET", secret_cred)
    grab("NOT_INT", cap_bool)
    grab("NOT_INT", cap_text)
    grab("OUT_OF_RANGE", cap_zero)
    grab("OUT_OF_RANGE", cap_negative)
    grab("OUT_OF_RANGE", clock_negative)
    grab("DUPLICATE", dup_allow)
    grab("DUPLICATE", dup_lane)
    grab("DUPLICATE", dup_owner)
    grab("BAD_BOARD", bad_board)
    grab("BAD_LANE", bad_lane)
    grab("BAD_BOARD", assign_board)
    grab("UNKNOWN_LANE", unknown_lane)
    grab("CRED_MISMATCH", cred_mismatch)
    grab("NOT_ALLOWED", not_allowed)
    grab("DUPLICATE", duplicate_card)
    grab("REPLAY", replay_fence)
    grab("UNCLASSIFIED", yolo_action)
    grab("UNCLASSIFIED", off_action)
    grab("UNCLASSIFIED", none_action)
    grab("STALE", stale_clock)
    grab("STALE", stale_fence)
    grab("REQUEUE_CAP", requeue_cap)
    grab("NOT_ASSIGNED", not_assigned)
    grab("CLOSED", closed)
    grab("NO_RETRY", no_retry_fresh)
    grab("NO_RETRY", no_retry_class)
    grab("RETRY_CAP", retry_cap)
    grab("UNKNOWN_ASSIGNMENT", unknown_assignment)
    grab("BAD_SCHEMA", bad_schema)
    grab("BAD_LIMIT", bad_limit)
    grab("BAD_ASSIGNMENT", bad_assignment)
    grab("BAD_EVENT", bad_event)
    grab("BAD_FENCE", bad_fence)
    grab("BAD_FENCE", fence_none)
    grab("NOT_TEXT", boom)
    grab("BAD_BOARD", mismatch_board)
    grab("NO_SPAWN", no_spawn)
    grab("LANE_FULL", _second_on_cap)
    grab("CHAIN", broken_chain)
    expected = {
        "BAD_ARGV",
        "BAD_ASSIGNMENT",
        "BAD_BOARD",
        "BAD_EVENT",
        "BAD_FENCE",
        "BAD_ID",
        "BAD_LANE",
        "BAD_LIMIT",
        "BAD_SCHEMA",
        "CHAIN",
        "CLOSED",
        "CRED_MISMATCH",
        "DUPLICATE",
        "EMPTY_ALLOW",
        "EMPTY_ARG",
        "LANE_FULL",
        "MISSING_CRED",
        "NOT_ALLOWED",
        "NOT_ASSIGNED",
        "NOT_INT",
        "NOT_TEXT",
        "NO_RETRY",
        "NO_SPAWN",
        "NULL_BYTE",
        "OUT_OF_RANGE",
        "OVERSIZE",
        "REPLAY",
        "REQUEUE_CAP",
        "RETRY_CAP",
        "SECRET",
        "SHELL_STRING",
        "STALE",
        "UNCLASSIFIED",
        "UNKNOWN_ASSIGNMENT",
        "UNKNOWN_LANE",
        "UNKNOWN_MODE",
    }
    assert expected <= seen


def _second_on_cap() -> object:
    board, _row = _put(_board(1), "mug-card", now=40, fence="fence-mug")
    return _put(board, "lamp-card", now=41, fence="fence-lamp")
