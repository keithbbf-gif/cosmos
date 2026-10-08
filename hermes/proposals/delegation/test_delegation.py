"""Delegation caps, fences, leases, and the summary-only parent view."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import replace

import pytest

from cosmos_hermes import Refuse
from delegation import (
    ALWAYS_STRIP,
    CLASSIFIED,
    EXECUTES,
    POLICY_CHILDREN,
    POLICY_DEPTH,
    POLICY_ITERATIONS,
    POLICY_LEASE_S,
    POLICY_NOTE_BUDGET,
    SCHEMA,
    SCHEMA_MISS,
    Board,
    Caps,
    Child,
    Fact,
    Parent,
    complete,
    make_board,
    open_batch,
    open_child,
    parent_view,
    present,
    rebuild,
    register,
    report_stale,
    snapshot,
    strip_tools,
)

_TOOLS = (
    "read:docs",
    "delegate",
    "mail:send",
    "wo:propose",
    "seat:take",
    "spend:admin",
    "approval:grant",
    "principal:admin",
    "files:read",
)


def _code(call: Callable[[], object]) -> str:
    with pytest.raises(Refuse) as caught:
        call()
    return caught.value.code


def _nth_child(children: tuple[Child, ...], index: int) -> Child:
    if index < 0 or index >= len(children):
        raise AssertionError("index")
    return children[index]


def _nth_fact(facts: tuple[Fact, ...], index: int) -> Fact:
    if index < 0 or index >= len(facts):
        raise AssertionError("index")
    return facts[index]


def _session() -> tuple[Board, Parent, Child]:
    board = make_board()
    board, parent = register(board, "mina-session", now=100, credential_id="cred-mina")
    board, child = open_child(
        board,
        parent.parent_id,
        "Read the note on card gate-14",
        ["files:read", "read:docs"],
        now=100,
        credential_id="cred-mina",
        fence=parent.fence,
    )
    return (board, parent, child)


def test_schema_policy_and_no_spawn() -> None:
    assert SCHEMA == "cosmos-hermes-delegation/1"
    assert EXECUTES is False
    board = make_board()
    assert board.caps.max_depth == POLICY_DEPTH == 2
    assert board.caps.max_children == POLICY_CHILDREN == 3
    assert board.caps.max_iterations == POLICY_ITERATIONS == 8
    assert board.caps.max_lease_s == POLICY_LEASE_S == 450
    assert ALWAYS_STRIP <= CLASSIFIED
    assert "principal:admin" in ALWAYS_STRIP
    module = inspect.getmodule(make_board)
    assert module is not None
    source = inspect.getsource(module)
    for banned in ("subprocess", "Popen", "socket", "urllib", "requests", "pickle", "cosmos_delegate"):
        assert banned not in source
    assert "transcript" not in source


def test_success_summary_and_rebuild() -> None:
    board, parent, child = _session()
    assert isinstance(child, Child)
    assert child.status == "OPEN"
    assert child.depth == 1
    assert child.executes is False
    assert child.iterations == POLICY_ITERATIONS
    assert child.fence == "f2"
    assert parent_view(board, child.child_id, child.fence) == ""
    assert parent_view(board, child.child_id, parent.fence) == ""
    board, done = complete(board, child.child_id, "gate holds", now=120, fence=child.fence)
    assert done.status == "DONE"
    assert done.summary == "gate holds"
    assert parent_view(board, done.child_id, parent.fence) == "gate holds"
    assert "transcript" not in Child.__dataclass_fields__
    assert snapshot(rebuild(board.facts)) == snapshot(board)
    blob = repr(done) + repr(board)
    assert "sk-" not in blob
    assert "api_key" not in blob
    assert "Bearer" not in blob


def test_request_above_policy_is_stored() -> None:
    board = make_board(9, 9, 90, 9_000)
    assert board.caps.requested_depth == 9
    assert board.caps.max_depth == POLICY_DEPTH
    assert board.caps.requested_children == 9
    assert board.caps.max_children == POLICY_CHILDREN
    assert board.caps.requested_iterations == 90
    assert board.caps.max_iterations == POLICY_ITERATIONS
    assert board.caps.requested_lease_s == 9_000
    assert board.caps.max_lease_s == POLICY_LEASE_S
    board, parent = register(board, "mina-session", now=1, credential_id="cred-mina")
    board, child = open_child(
        board,
        parent.parent_id,
        "survey the gate",
        ["read:docs"],
        now=1,
        credential_id="cred-mina",
        fence=parent.fence,
        requested_iterations=10_000,
        requested_lease_s=10_000,
    )
    assert child.requested_iterations == 10_000
    assert child.iterations == POLICY_ITERATIONS
    assert child.requested_lease_s == 10_000
    assert child.lease_until - child.opened_at == POLICY_LEASE_S
    for index in range(2):
        board, _ignored = open_child(
            board,
            parent.parent_id,
            f"more {index}",
            ["read:docs"],
            now=1,
            credential_id="cred-mina",
            fence=parent.fence,
        )
    assert len(board.children) == POLICY_CHILDREN

    def overflow() -> object:
        return open_child(
            board,
            parent.parent_id,
            "overflow",
            ["read:docs"],
            now=1,
            credential_id="cred-mina",
            fence=parent.fence,
        )

    assert _code(overflow) == "CONCURRENCY"
    assert len(board.children) == POLICY_CHILDREN

    def raised_caps() -> object:
        return Caps(9, 9, 90, 9_000, 9, 9, 90, 9_000)

    assert _code(raised_caps) == "BAD_BOARD"


def test_request_below_policy_is_honored() -> None:
    board = make_board(1, 1, 3, 30)
    assert board.caps.max_depth == 1
    assert board.caps.max_children == 1
    assert board.caps.max_iterations == 3
    assert board.caps.max_lease_s == 30
    board, parent = register(board, "mina-session", now=1, credential_id="cred-mina")
    board, child = open_child(
        board,
        parent.parent_id,
        "short task",
        ["read:docs", "delegate"],
        now=1,
        credential_id="cred-mina",
        fence=parent.fence,
        requested_iterations=3,
        requested_lease_s=30,
    )
    assert child.iterations == 3
    assert child.lease_until - child.opened_at == 30
    assert "delegate" in child.stripped

    def second() -> object:
        return open_child(
            board,
            parent.parent_id,
            "second",
            ["read:docs"],
            now=1,
            credential_id="cred-mina",
            fence=parent.fence,
        )

    assert _code(second) == "CONCURRENCY"


def test_depth_strips_delegate_then_refuses() -> None:
    board = make_board(9, 3, 8, 450)
    assert board.caps.max_depth == POLICY_DEPTH
    board, parent = register(board, "mina-session", now=10, credential_id="cred-mina")
    granted, stripped = strip_tools(list(_TOOLS), 1, 9)
    assert "delegate" in granted
    assert set(ALWAYS_STRIP).isdisjoint(granted)
    assert _code(_depth_past) == "DEPTH"
    leaf_granted, leaf_stripped = strip_tools(list(_TOOLS), 2, 9)
    assert "delegate" not in leaf_granted
    assert "delegate" in leaf_stripped
    tight_granted, _tight_stripped = strip_tools(list(_TOOLS), 1, 1)
    assert "delegate" not in tight_granted
    board, child = open_child(
        board,
        parent.parent_id,
        "first",
        list(_TOOLS),
        now=10,
        credential_id="cred-mina",
        fence=parent.fence,
    )
    assert child.depth == 1
    assert "delegate" in child.granted
    assert set(ALWAYS_STRIP).isdisjoint(set(child.granted))
    board, grand = open_child(
        board,
        child.child_id,
        "second",
        list(_TOOLS),
        now=11,
        credential_id="cred-mina",
        fence=child.fence,
    )
    assert grand.depth == 2
    assert "delegate" in grand.stripped
    ids = tuple(item.child_id for item in board.children)

    def third() -> object:
        return open_child(
            board,
            grand.child_id,
            "third",
            ["read:docs"],
            now=12,
            credential_id="cred-mina",
            fence=grand.fence,
        )

    assert _code(third) == "DEPTH"
    assert tuple(item.child_id for item in board.children) == ids


def _depth_past() -> object:
    return strip_tools(list(_TOOLS), 2, 1)


def test_fence_wrong_and_stale_lease() -> None:
    board = make_board(2, 3, 8, 30)
    board, parent = register(board, "mina-session", now=100, credential_id="cred-mina")
    board, child = open_child(
        board,
        parent.parent_id,
        "Read the note on card gate-14",
        ["read:docs", "delegate"],
        now=100,
        credential_id="cred-mina",
        fence=parent.fence,
    )
    before = board.children

    def wrong_sibling() -> object:
        return open_child(
            board,
            parent.parent_id,
            "Check card gate-15",
            ["read:docs"],
            now=101,
            credential_id="cred-mina",
            fence="f999",
        )

    assert _code(wrong_sibling) == "FENCE"
    assert board.children is before
    board, second = open_child(
        board,
        parent.parent_id,
        "Check card gate-15",
        ["read:docs"],
        now=101,
        credential_id="cred-mina",
        fence=parent.fence,
    )
    assert second.fence != child.fence
    assert second.executes is False

    def stale_open() -> object:
        return open_child(
            board,
            child.child_id,
            "too late",
            ["read:docs"],
            now=child.lease_until + 1,
            credential_id="cred-mina",
            fence=child.fence,
        )

    assert _code(stale_open) == "STALE_LEASE"
    assert len(board.children) == 2

    def stale_present() -> object:
        return present(board, child.child_id, child.fence, now=child.lease_until + 1)

    assert _code(stale_present) == "STALE_LEASE"
    updated, reported = report_stale(
        board,
        child.child_id,
        now=child.lease_until + 1,
        fence=child.fence,
    )
    assert reported.status == "REPORTED"

    def stale_fence() -> object:
        return present(updated, reported.child_id, reported.fence, now=child.lease_until + 2)

    assert _code(stale_fence) == "STALE_FENCE"
    same, again = report_stale(
        updated,
        reported.child_id,
        now=child.lease_until + 3,
        fence=reported.fence,
    )
    assert same is updated
    assert again.child_id == reported.child_id


def test_batch_over_cap_adds_nothing() -> None:
    board = make_board(2, 2, 8, 40)
    board, parent = register(board, "mina-session", now=10, credential_id="cred-mina")

    def overrun() -> object:
        return open_batch(
            board,
            parent.parent_id,
            ("read card gate-14", "read card gate-15", "read card gate-16"),
            ["read:docs"],
            now=10,
            credential_id="cred-mina",
            fence=parent.fence,
        )

    assert _code(overrun) == "CONCURRENCY"
    assert len(board.children) == 0
    board, kids = open_batch(
        board,
        parent.parent_id,
        ("read card gate-14", "read card gate-15"),
        ["read:docs"],
        now=10,
        credential_id="cred-mina",
        fence=parent.fence,
    )
    assert len(kids) == 2
    assert _nth_child(kids, 0).executes is False
    assert _nth_child(kids, 1).fence != _nth_child(kids, 0).fence

    def poisoned() -> object:
        return open_batch(
            board,
            parent.parent_id,
            ("read card gate-16", "  "),
            ["read:docs"],
            now=11,
            credential_id="cred-mina",
            fence=parent.fence,
        )

    assert _code(poisoned) == "EMPTY_GOAL"
    assert len(board.children) == 2


def test_notes_skip_what_does_not_fit() -> None:
    board = make_board()
    board, parent = register(board, "mina-session", now=10, credential_id="cred-mina")
    big = "N" * (POLICY_NOTE_BUDGET + 80)
    later_big = "M" * (POLICY_NOTE_BUDGET - 10)
    board, child = open_child(
        board,
        parent.parent_id,
        "Read the note on card gate-14",
        ["read:docs"],
        now=10,
        credential_id="cred-mina",
        fence=parent.fence,
        notes=(big, "note on card gate-14", later_big, "dock light"),
    )
    assert child.context == ("note on card gate-14", "dock light")
    assert big not in child.context
    assert later_big not in child.context


def test_schema_one_retry_keeps_the_text() -> None:
    board = make_board()
    board, parent = register(board, "mina-session", now=100, credential_id="cred-mina")
    board, child = open_child(
        board,
        parent.parent_id,
        "Report the dock light",
        ["read:docs"],
        now=100,
        credential_id="cred-mina",
        fence=parent.fence,
        schema_keys=("light",),
    )
    board, pending = complete(board, child.child_id, "the lamp is dark", now=110, fence=child.fence)
    assert pending.status == "OPEN"
    assert pending.schema_attempts == 1
    assert pending.failure_class == SCHEMA_MISS
    assert pending.schema_errors == ("not-object",)
    assert parent_view(board, pending.child_id, parent.fence) == ""
    assert len(board.children) == 1
    board, kept = complete(board, child.child_id, '{"seen": "lamp"}', now=120, fence=child.fence)
    assert kept.status == "DONE"
    assert kept.schema_valid is False
    assert kept.schema_attempts == 1
    assert kept.schema_errors == ("missing:light",)
    assert kept.summary == '{"seen": "lamp"}'
    assert parent_view(board, kept.child_id, child.fence) == kept.summary
    assert kept.executes is False

    def third() -> object:
        return complete(board, kept.child_id, '{"light": "green"}', now=130, fence=child.fence)

    assert _code(third) == "NOT_OPEN"
    board, other = open_child(
        board,
        parent.parent_id,
        "Report the dock light again",
        ["read:docs"],
        now=140,
        credential_id="cred-mina",
        fence=parent.fence,
        schema_keys=("light",),
    )
    prose = 'the dock light is green {"light": "green"}'
    board, done = complete(board, other.child_id, prose, now=150, fence=other.fence)
    assert done.schema_valid is True
    assert done.schema_attempts == 0
    fenced = '```json\n{"light": "green"}\n```'
    board, third_child = open_child(
        board,
        parent.parent_id,
        "One more lamp check",
        ["read:docs"],
        now=160,
        credential_id="cred-mina",
        fence=parent.fence,
        schema_keys=("light",),
    )
    updated, fenced_done = complete(board, third_child.child_id, fenced, now=170, fence=third_child.fence)
    assert fenced_done.schema_valid is True
    assert snapshot(rebuild(updated.facts)) == snapshot(updated)


def test_report_does_not_open_a_replacement() -> None:
    board, _parent, child = _session()
    before = tuple(item.child_id for item in board.children)

    def fresh() -> object:
        return report_stale(board, child.child_id, now=120, fence=child.fence)

    assert _code(fresh) == "FRESH"
    updated, reported = report_stale(board, child.child_id, now=child.lease_until + 1, fence=child.fence)
    assert reported.status == "REPORTED"
    assert tuple(item.child_id for item in updated.children) == before
    assert len(updated.facts) == len(board.facts) + 1


def test_secret_does_not_echo() -> None:
    def leak() -> object:
        return register(make_board(), "mina-session", now=1, credential_id="sk-livekeyvalue")

    with pytest.raises(Refuse) as caught:
        leak()
    assert caught.value.code == "SECRET"
    assert caught.value.detail == ""
    assert "livekeyvalue" not in repr(caught.value)
    board, parent, _child = _session()

    def goal() -> object:
        return open_child(
            board,
            parent.parent_id,
            "api_key=supersecretvalue",
            ["read:docs"],
            now=110,
            credential_id="cred-mina",
            fence=parent.fence,
        )

    with pytest.raises(Refuse) as goal_caught:
        goal()
    assert goal_caught.value.code == "SECRET"
    assert "supersecretvalue" not in repr(goal_caught.value)

    def bearer() -> object:
        return complete(
            board,
            _nth_child(board.children, 0).child_id,
            "Bearer abcdefghijkl",
            now=110,
            fence=_nth_child(board.children, 0).fence,
        )

    assert _code(bearer) == "SECRET"


def test_refusal_codes() -> None:
    board, parent, child = _session()
    seen: set[str] = set()

    def check(code: str, call: Callable[[], object]) -> None:
        assert _code(call) == code
        seen.add(code)

    def bad_board() -> object:
        return open_child(
            None,
            "mina-session",
            "goal",
            ["read:docs"],
            now=100,
            credential_id="cred-mina",
            fence="f1",
        )

    def bad_fence() -> object:
        return present(board, child.child_id, "f0", now=110)

    def bad_id() -> object:
        return register(make_board(), "bad id", now=1, credential_id="cred-mina")

    def broken() -> object:
        first = _nth_fact(board.facts, 0)
        second = _nth_fact(board.facts, 1)
        forged = Fact(
            seq=second.seq,
            kind=second.kind,
            body=second.body,
            prev=second.prev,
            digest="0" * 64,
        )
        return rebuild((first, forged))

    def clock() -> object:
        return complete(board, child.child_id, "early", now=99, fence=child.fence)

    def concurrency() -> object:
        full = make_board()
        full, host = register(full, "mina-session", now=10, credential_id="cred-mina")
        for index in range(POLICY_CHILDREN):
            full, _ignored = open_child(
                full,
                host.parent_id,
                f"job {index}",
                ["read:docs"],
                now=10,
                credential_id="cred-mina",
                fence=host.fence,
            )
        return open_child(
            full,
            host.parent_id,
            "one more",
            ["read:docs"],
            now=10,
            credential_id="cred-mina",
            fence=host.fence,
        )

    def cred() -> object:
        return open_child(
            board,
            parent.parent_id,
            "goal",
            ["read:docs"],
            now=110,
            credential_id="cred-other",
            fence=parent.fence,
        )

    def depth() -> object:
        shallow = make_board(1, 2, 4, 30)
        shallow, host = register(shallow, "mina-session", now=50, credential_id="cred-mina")
        shallow, leaf = open_child(
            shallow,
            host.parent_id,
            "leaf",
            ["read:docs"],
            now=50,
            credential_id="cred-mina",
            fence=host.fence,
        )
        return open_child(
            shallow,
            leaf.child_id,
            "deeper",
            ["read:docs"],
            now=51,
            credential_id="cred-mina",
            fence=leaf.fence,
        )

    def duplicate() -> object:
        return register(board, "mina-session", now=101, credential_id="cred-mina")

    def empty_allow() -> object:
        return open_child(
            board,
            parent.parent_id,
            "goal",
            [],
            now=110,
            credential_id="cred-mina",
            fence=parent.fence,
        )

    def empty_goal() -> object:
        return open_child(
            board,
            parent.parent_id,
            "  ",
            ["read:docs"],
            now=110,
            credential_id="cred-mina",
            fence=parent.fence,
        )

    def empty_note() -> object:
        return open_child(
            board,
            parent.parent_id,
            "goal",
            ["read:docs"],
            now=110,
            credential_id="cred-mina",
            fence=parent.fence,
            notes=("  ",),
        )

    def empty_schema() -> object:
        return open_child(
            board,
            parent.parent_id,
            "goal",
            ["read:docs"],
            now=110,
            credential_id="cred-mina",
            fence=parent.fence,
            schema_keys=(),
        )

    def empty_summary() -> object:
        return complete(board, child.child_id, "  ", now=110, fence=child.fence)

    def fence() -> object:
        return present(board, child.child_id, "f999", now=110)

    def fresh() -> object:
        return report_stale(board, child.child_id, now=120, fence=child.fence)

    def missing_cred() -> object:
        return register(make_board(), "mina-session", now=1, credential_id="")

    def no_spawn() -> object:
        return replace(child, executes=True)

    def not_int() -> object:
        return open_child(
            board,
            parent.parent_id,
            "goal",
            ["read:docs"],
            now=True,
            credential_id="cred-mina",
            fence=parent.fence,
        )

    def not_list() -> object:
        return open_child(
            board,
            parent.parent_id,
            "goal",
            "read:docs",
            now=110,
            credential_id="cred-mina",
            fence=parent.fence,
        )

    def not_open() -> object:
        updated, done = complete(board, child.child_id, "gate holds", now=120, fence=child.fence)
        return complete(updated, done.child_id, "again", now=130, fence=child.fence)

    def not_text() -> object:
        return open_child(
            board,
            parent.parent_id,
            None,
            ["read:docs"],
            now=110,
            credential_id="cred-mina",
            fence=parent.fence,
        )

    def null_byte() -> object:
        return open_child(
            board,
            parent.parent_id,
            "a\x00b",
            ["read:docs"],
            now=110,
            credential_id="cred-mina",
            fence=parent.fence,
        )

    def out_of_range() -> object:
        return open_child(
            board,
            parent.parent_id,
            "goal",
            ["read:docs"],
            now=110,
            credential_id="cred-mina",
            fence=parent.fence,
            requested_iterations=0,
        )

    def oversize() -> object:
        return open_child(
            board,
            parent.parent_id,
            "x" * 4001,
            ["read:docs"],
            now=110,
            credential_id="cred-mina",
            fence=parent.fence,
        )

    def secret() -> object:
        return register(make_board(), "mina-session", now=1, credential_id="sk-livekeyvalue")

    def stale_fence() -> object:
        updated, reported = report_stale(
            board,
            child.child_id,
            now=child.lease_until + 1,
            fence=child.fence,
        )
        return present(updated, reported.child_id, reported.fence, now=child.lease_until + 2)

    def stale_lease() -> object:
        return present(board, child.child_id, child.fence, now=child.lease_until + 1)

    def unclassified() -> object:
        return open_child(
            board,
            parent.parent_id,
            "goal",
            ["yolo"],
            now=110,
            credential_id="cred-mina",
            fence=parent.fence,
        )

    def unknown_child() -> object:
        return parent_view(board, "c9", child.fence)

    def unknown_parent() -> object:
        return open_child(
            make_board(),
            "missing",
            "goal",
            ["read:docs"],
            now=1,
            credential_id="cred-mina",
            fence="f1",
        )

    check("BAD_BOARD", bad_board)
    check("BAD_FENCE", bad_fence)
    check("BAD_ID", bad_id)
    check("BROKEN_CHAIN", broken)
    check("CLOCK", clock)
    check("CONCURRENCY", concurrency)
    check("CRED_MISMATCH", cred)
    check("DEPTH", depth)
    check("DUPLICATE", duplicate)
    check("EMPTY_ALLOW", empty_allow)
    check("EMPTY_GOAL", empty_goal)
    check("EMPTY_NOTE", empty_note)
    check("EMPTY_SCHEMA", empty_schema)
    check("EMPTY_SUMMARY", empty_summary)
    check("FENCE", fence)
    check("FRESH", fresh)
    check("MISSING_CRED", missing_cred)
    check("NO_SPAWN", no_spawn)
    check("NOT_INT", not_int)
    check("NOT_LIST", not_list)
    check("NOT_OPEN", not_open)
    check("NOT_TEXT", not_text)
    check("NULL_BYTE", null_byte)
    check("OUT_OF_RANGE", out_of_range)
    check("OVERSIZE", oversize)
    check("SECRET", secret)
    check("STALE_FENCE", stale_fence)
    check("STALE_LEASE", stale_lease)
    check("UNCLASSIFIED", unclassified)
    check("UNKNOWN_CHILD", unknown_child)
    check("UNKNOWN_PARENT", unknown_parent)
    assert len(seen) == 31


def _example() -> tuple[object, ...]:
    board = make_board(1, 2, 4, 30)
    board, parent = register(board, "mina-session", now=1_700_000_100, credential_id="cred-mina")
    board, child = open_child(
        board,
        parent.parent_id,
        "Read the note on card gate-14 and report the dock light",
        ["files:read", "read:docs", "delegate", "mail:send", "principal:admin"],
        now=1_700_000_100,
        credential_id="cred-mina",
        fence=parent.fence,
        requested_iterations=20,
        requested_lease_s=900,
        notes=("N" * 600, "note on card gate-14", "N" * 500, "dock light"),
    )
    before = board.children

    def wrong_open() -> object:
        return open_child(
            board,
            parent.parent_id,
            "Check the west lamp on card gate-15",
            ["read:docs"],
            now=1_700_000_101,
            credential_id="cred-mina",
            fence="f999",
        )

    def too_deep() -> object:
        return open_child(
            board,
            child.child_id,
            "Open another child for the same lamp",
            ["read:docs"],
            now=1_700_000_101,
            credential_id="cred-mina",
            fence=child.fence,
        )

    def wrong_present() -> object:
        return present(board, child.child_id, "f999", now=1_700_000_101)

    def stale() -> object:
        return present(board, child.child_id, child.fence, now=child.lease_until + 1)

    wrong = _code(wrong_open)
    depth_code = _code(too_deep)
    present_code = _code(wrong_present)
    stale_code = _code(stale)
    assert board.children is before
    assert len(board.children) == 1
    assert child.executes is False
    assert child.depth == board.caps.max_depth == 1
    assert child.iterations == 4
    assert child.requested_iterations == 20
    assert child.lease_until - child.opened_at == 30
    assert board.caps.max_children == 2
    assert wrong == "FENCE"
    assert depth_code == "DEPTH"
    assert present_code == "FENCE"
    assert stale_code == "STALE_LEASE"
    assert "delegate" in child.stripped
    assert child.context == ("note on card gate-14", "dock light")
    board, done = complete(
        board,
        child.child_id,
        "the dock light is green",
        now=1_700_000_110,
        fence=child.fence,
    )
    view = parent_view(board, done.child_id, parent.fence)
    assert view == "the dock light is green"
    assert len(board.children) == 1
    assert done.executes is False
    assert snapshot(rebuild(board.facts)) == snapshot(board)
    return (
        SCHEMA,
        board.caps.max_depth,
        board.caps.max_children,
        board.caps.max_iterations,
        board.caps.max_lease_s,
        parent.fence,
        child.child_id,
        child.fence,
        child.depth,
        child.iterations,
        child.requested_iterations,
        child.lease_until - child.opened_at,
        child.requested_lease_s,
        child.granted,
        child.stripped,
        child.context,
        child.executes,
        wrong,
        depth_code,
        present_code,
        stale_code,
        len(board.children),
        done.summary,
        done.status,
        view,
        snapshot(board),
    )


def test_example_delegation() -> None:
    assert _example() == _example()
