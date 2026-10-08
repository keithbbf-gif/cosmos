"""Delegation records. A fence and a lease gate every child. The parent gets a summary and does not start a process."""

from __future__ import annotations

import hashlib
import hmac
import json
import re
from dataclasses import dataclass, replace

from cosmos_hermes import Refuse, bound_int, bound_text, const_eq, secret_shape

SCHEMA = "cosmos-hermes-delegation/1"
SCHEMA_MISS = "SCHEMA_MISS"
POLICY_DEPTH = 2
POLICY_CHILDREN = 3
POLICY_ITERATIONS = 8
POLICY_LEASE_S = 450
POLICY_NOTE_BUDGET = 512
EXECUTES = False

_REQUEST_HI = 1_000_000_000
_TEXT_LIMIT = 4_000
_TOOL_LIMIT = 32
_NOTE_LIMIT = 32
_SCHEMA_LIMIT = 16
_BATCH_LIMIT = 32
_BODY_LIMIT = 48_000
_CLOCK_HI = 4_000_000_000
_ID_SCAN = 10_000

ALWAYS_STRIP = frozenset(
    {
        "mail:send",
        "wo:propose",
        "seat:take",
        "spend:admin",
        "approval:grant",
        "principal:admin",
    }
)
CLASSIFIED = ALWAYS_STRIP | {"delegate", "read:docs", "files:read"}
_STATUSES = frozenset({"OPEN", "DONE", "REPORTED"})
_FAILURES = frozenset({"", SCHEMA_MISS})
_KINDS = frozenset({"BOARD", "REGISTER", "OPEN", "RETRY", "COMPLETE", "REPORT"})

_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$")
_FENCE = re.compile(r"^f[1-9][0-9]{0,5}$")
_HEX = re.compile(r"^[0-9a-f]{64}$")
_CODE_FENCE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.IGNORECASE | re.DOTALL)
_GENESIS = "0" * 64

type Json = str | int | bool | None | list[str]


def _ceiling(asked: int, policy: int) -> int:
    # A caller who asks for more than policy does not raise the cap.
    if asked > policy:
        return policy
    return asked


@dataclass(frozen=True, slots=True)
class Caps:
    """Requested caps beside the caps that are actually enforced."""

    requested_depth: int
    requested_children: int
    requested_iterations: int
    requested_lease_s: int
    max_depth: int
    max_children: int
    max_iterations: int
    max_lease_s: int

    def __post_init__(self) -> None:
        _real_int(self.requested_depth, 1, _REQUEST_HI)
        _real_int(self.requested_children, 1, _REQUEST_HI)
        _real_int(self.requested_iterations, 1, _REQUEST_HI)
        _real_int(self.requested_lease_s, 1, _REQUEST_HI)
        if self.max_depth != _ceiling(self.requested_depth, POLICY_DEPTH):
            raise Refuse("BAD_BOARD")
        if self.max_children != _ceiling(self.requested_children, POLICY_CHILDREN):
            raise Refuse("BAD_BOARD")
        if self.max_iterations != _ceiling(self.requested_iterations, POLICY_ITERATIONS):
            raise Refuse("BAD_BOARD")
        if self.max_lease_s != _ceiling(self.requested_lease_s, POLICY_LEASE_S):
            raise Refuse("BAD_BOARD")


@dataclass(frozen=True, slots=True)
class Parent:
    """A depth-0 principal. `fence` is the token later children must present."""

    parent_id: str
    credential_id: str
    opened_at: int
    fence: str

    def __post_init__(self) -> None:
        _real_int(self.opened_at, 0, _CLOCK_HI)
        if _ID.fullmatch(self.parent_id) is None or _ID.fullmatch(self.credential_id) is None:
            raise Refuse("BAD_ID")
        if _FENCE.fullmatch(self.fence) is None:
            raise Refuse("BAD_FENCE")


@dataclass(frozen=True, slots=True)
class Child:
    """One delegated task. `executes` stays false: this record is not a process."""

    child_id: str
    parent_id: str
    depth: int
    goal: str
    summary: str
    granted: tuple[str, ...]
    stripped: tuple[str, ...]
    iterations: int
    requested_iterations: int
    status: str
    opened_at: int
    lease_until: int
    requested_lease_s: int
    credential_id: str
    fence: str
    context: tuple[str, ...] = ()
    schema_keys: tuple[str, ...] = ()
    schema_attempts: int = 0
    schema_valid: bool | None = None
    schema_errors: tuple[str, ...] = ()
    failure_class: str = ""
    closed_at: int | None = None
    executes: bool = False

    def __post_init__(self) -> None:
        if self.executes is not False:
            raise Refuse("NO_SPAWN")
        if self.status not in _STATUSES:
            raise Refuse("BAD_BOARD")
        if self.schema_attempts not in (0, 1):
            raise Refuse("BAD_BOARD")
        if self.failure_class not in _FAILURES:
            raise Refuse("BAD_BOARD")
        if self.schema_valid is not None and not isinstance(self.schema_valid, bool):
            raise Refuse("BAD_BOARD")
        if self.closed_at is not None:
            _real_int(self.closed_at, 0, _CLOCK_HI)
        _real_int(self.depth, 1, POLICY_DEPTH)
        _real_int(self.opened_at, 0, _CLOCK_HI)
        _real_int(self.lease_until, 0, _CLOCK_HI)
        _real_int(self.iterations, 1, POLICY_ITERATIONS)
        _real_int(self.requested_iterations, 1, _REQUEST_HI)
        _real_int(self.requested_lease_s, 1, _REQUEST_HI)
        if self.lease_until < self.opened_at:
            raise Refuse("CLOCK")
        if self.lease_until - self.opened_at > POLICY_LEASE_S:
            raise Refuse("BAD_BOARD")
        if self.status == "OPEN" and self.closed_at is not None:
            raise Refuse("BAD_BOARD")
        if self.status != "OPEN" and self.closed_at is None:
            raise Refuse("BAD_BOARD")
        if self.closed_at is not None and self.closed_at < self.opened_at:
            raise Refuse("CLOCK")
        for name in (self.child_id, self.parent_id, self.credential_id, self.goal, self.summary):
            if not isinstance(name, str):
                raise Refuse("BAD_BOARD")
        if _FENCE.fullmatch(self.fence) is None:
            raise Refuse("BAD_FENCE")
        _str_tuple(self.granted)
        _str_tuple(self.stripped)
        _str_tuple(self.context)
        _str_tuple(self.schema_keys)
        _str_tuple(self.schema_errors)


@dataclass(frozen=True, slots=True)
class Fact:
    """One hash-chained decision. `prev` is the prior digest, or the genesis digest."""

    seq: int
    kind: str
    body: str
    prev: str
    digest: str

    def __post_init__(self) -> None:
        _real_int(self.seq, 1, _REQUEST_HI)
        if self.kind not in _KINDS:
            raise Refuse("BROKEN_CHAIN")
        if not isinstance(self.body, str):
            raise Refuse("BROKEN_CHAIN")
        if _HEX.fullmatch(self.prev) is None or _HEX.fullmatch(self.digest) is None:
            raise Refuse("BROKEN_CHAIN")


@dataclass(frozen=True, slots=True)
class Board:
    """Folded decision record. Authority stays on the scheduler ledger."""

    caps: Caps
    parents: tuple[Parent, ...]
    children: tuple[Child, ...]
    facts: tuple[Fact, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.caps, Caps):
            raise Refuse("BAD_BOARD")
        if not isinstance(self.parents, tuple) or not isinstance(self.children, tuple):
            raise Refuse("BAD_BOARD")
        if not isinstance(self.facts, tuple):
            raise Refuse("BAD_BOARD")


@dataclass(frozen=True, slots=True)
class Snapshot:
    """Public projection. `rebuild` of the same facts reproduces it."""

    schema: str
    max_depth: int
    max_children: int
    max_iterations: int
    max_lease_s: int
    parent_ids: tuple[str, ...]
    child_ids: tuple[str, ...]
    fences: tuple[str, ...]
    statuses: tuple[str, ...]
    summaries: tuple[str, ...]
    executes: tuple[bool, ...]
    digests: tuple[str, ...]


def make_board(
    requested_depth: object = POLICY_DEPTH,
    requested_children: object = POLICY_CHILDREN,
    requested_iterations: object = POLICY_ITERATIONS,
    requested_lease_s: object = POLICY_LEASE_S,
) -> Board:
    """Store the caller's caps. A request above policy does not raise the cap."""
    asked_depth = bound_int(requested_depth, 1, _REQUEST_HI)
    asked_children = bound_int(requested_children, 1, _REQUEST_HI)
    asked_iterations = bound_int(requested_iterations, 1, _REQUEST_HI)
    asked_lease = bound_int(requested_lease_s, 1, _REQUEST_HI)
    caps = Caps(
        requested_depth=asked_depth,
        requested_children=asked_children,
        requested_iterations=asked_iterations,
        requested_lease_s=asked_lease,
        max_depth=_ceiling(asked_depth, POLICY_DEPTH),
        max_children=_ceiling(asked_children, POLICY_CHILDREN),
        max_iterations=_ceiling(asked_iterations, POLICY_ITERATIONS),
        max_lease_s=_ceiling(asked_lease, POLICY_LEASE_S),
    )
    return _from_facts((_make_fact((), "BOARD", _cap_fields(caps)),))


def register(
    board: object,
    parent_id: object,
    *,
    now: object,
    credential_id: object,
) -> tuple[Board, Parent]:
    """Record a depth-0 parent and issue its fence. A repeated id refuses."""
    state = _board(board)
    ident = _ident(parent_id)
    moment = _now(now)
    cred = _credential(credential_id)
    if _known(state, ident):
        raise Refuse("DUPLICATE")
    fence = _fresh_fence(state)
    updated = _append(
        state,
        "REGISTER",
        {
            "parent_id": ident,
            "credential_id": cred,
            "opened_at": moment,
            "fence": fence,
        },
    )
    return updated, _must_parent(updated, ident)


def strip_tools(
    tools: object,
    depth: object,
    max_depth: object,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Split tools into granted and stripped names.

    `max_depth` above policy is clamped. `delegate` is stripped when `depth`
    equals that cap. A depth past the cap refuses and grants nothing.
    """
    asked_depth = bound_int(depth, 1, _REQUEST_HI)
    asked_cap = bound_int(max_depth, 1, _REQUEST_HI)
    cap = _ceiling(asked_cap, POLICY_DEPTH)
    if asked_depth > cap:
        raise Refuse("DEPTH")
    names = _tool_list(tools)
    granted: list[str] = []
    stripped: list[str] = []
    seen: set[str] = set()
    for name in names:
        if name in seen:
            continue
        seen.add(name)
        blocked = name in ALWAYS_STRIP or (name == "delegate" and asked_depth == cap)
        if blocked:
            stripped.append(name)
        else:
            granted.append(name)
    return tuple(granted), tuple(stripped)


def open_child(
    board: object,
    parent_id: object,
    goal: object,
    tools: object,
    *,
    now: object,
    credential_id: object,
    fence: object,
    requested_iterations: object = None,
    requested_lease_s: object = None,
    notes: object = None,
    schema_keys: object = None,
) -> tuple[Board, Child]:
    """Append one child descriptor. A wrong fence or a stale lease adds nothing."""
    state = _board(board)
    parent = _ident(parent_id)
    moment = _now(now)
    cred = _credential(credential_id)
    token = _fence(fence)
    text = _plain(goal, "EMPTY_GOAL")
    asked_iter, effective_iter = _budget(requested_iterations, state.caps.max_iterations)
    asked_lease, effective_lease = _budget(requested_lease_s, state.caps.max_lease_s)
    chosen = _take_notes(notes)
    keys = _schema_keys(schema_keys)
    actor = _actor(state, parent)
    _hold(actor, token, cred, moment)
    # Leave one clock tick after the lease so a stale report still fits.
    if effective_lease >= _CLOCK_HI or moment > _CLOCK_HI - effective_lease - 1:
        raise Refuse("OUT_OF_RANGE", f"0..{_CLOCK_HI}")
    depth = _actor_depth(actor) + 1
    if depth > state.caps.max_depth:
        raise Refuse("DEPTH")
    if _live(state, parent) >= state.caps.max_children:
        raise Refuse("CONCURRENCY")
    granted, stripped = strip_tools(tools, depth, state.caps.max_depth)
    child_id = _fresh_id(state)
    child_fence = _fresh_fence(state)
    updated = _append(
        state,
        "OPEN",
        {
            "child_id": child_id,
            "parent_id": parent,
            "depth": depth,
            "goal": text,
            "granted": list(granted),
            "stripped": list(stripped),
            "iterations": effective_iter,
            "requested_iterations": asked_iter,
            "opened_at": moment,
            "lease_until": moment + effective_lease,
            "requested_lease_s": asked_lease,
            "credential_id": cred,
            "fence": child_fence,
            "context": list(chosen),
            "schema_keys": list(keys),
        },
    )
    return updated, _must_child(updated, child_id)


def open_batch(
    board: object,
    parent_id: object,
    goals: object,
    tools: object,
    *,
    now: object,
    credential_id: object,
    fence: object,
    requested_iterations: object = None,
    requested_lease_s: object = None,
) -> tuple[Board, tuple[Child, ...]]:
    """Open every goal or none. A batch larger than the free slots is not truncated."""
    state = _board(board)
    parent = _ident(parent_id)
    moment = _now(now)
    cred = _credential(credential_id)
    token = _fence(fence)
    texts = _goals(goals)
    _budget(requested_iterations, state.caps.max_iterations)
    _budget(requested_lease_s, state.caps.max_lease_s)
    actor = _actor(state, parent)
    _hold(actor, token, cred, moment)
    depth = _actor_depth(actor) + 1
    if depth > state.caps.max_depth:
        raise Refuse("DEPTH")
    free = state.caps.max_children - _live(state, parent)
    if len(texts) > free:
        raise Refuse("CONCURRENCY")
    current = state
    opened: list[Child] = []
    for text in texts:
        current, child = open_child(
            current,
            parent,
            text,
            tools,
            now=moment,
            credential_id=cred,
            fence=token,
            requested_iterations=requested_iterations,
            requested_lease_s=requested_lease_s,
        )
        opened.append(child)
    return current, tuple(opened)


def present(board: object, child_id: object, fence: object, *, now: object) -> Child:
    """Return the open child when the fence matches and the lease is live."""
    state = _board(board)
    ident = _ident(child_id)
    token = _fence(fence)
    moment = _now(now)
    child = _must_child(state, ident)
    if not const_eq(token, child.fence):
        raise Refuse("FENCE")
    _ready(child, moment)
    return child


def complete(
    board: object,
    child_id: object,
    summary: object,
    *,
    now: object,
    fence: object,
) -> tuple[Board, Child]:
    """Store the summary the parent may read. One schema miss may be retried once."""
    state = _board(board)
    ident = _ident(child_id)
    token = _fence(fence)
    moment = _now(now)
    text = _plain(summary, "EMPTY_SUMMARY")
    child = _must_child(state, ident)
    if not const_eq(token, child.fence):
        raise Refuse("FENCE")
    _ready(child, moment)
    if len(child.schema_keys) == 0:
        return _finish(state, child, ident, text, moment, None, (), "")
    errors = _schema_errors(text, child.schema_keys)
    if errors and child.schema_attempts == 0:
        updated = _append(
            state,
            "RETRY",
            {
                "child_id": ident,
                "at": moment,
                "schema_errors": list(errors),
                "failure_class": SCHEMA_MISS,
            },
        )
        return updated, _must_child(updated, ident)
    valid = len(errors) == 0
    failure = "" if valid else SCHEMA_MISS
    kept = () if valid else errors
    return _finish(state, child, ident, text, moment, valid, kept, failure)


def parent_view(board: object, child_id: object, fence: object) -> str:
    """Return the child's summary. A wrong fence refuses. The running log is not stored."""
    state = _board(board)
    ident = _ident(child_id)
    token = _fence(fence)
    child = _must_child(state, ident)
    if not const_eq(token, child.fence) and not const_eq(token, _parent_fence(state, child.parent_id)):
        raise Refuse("FENCE")
    return child.summary


def report_stale(
    board: object,
    child_id: object,
    *,
    now: object,
    fence: object,
) -> tuple[Board, Child]:
    """Mark a child past its lease REPORTED. A second call returns the same board."""
    state = _board(board)
    ident = _ident(child_id)
    token = _fence(fence)
    moment = _now(now)
    child = _must_child(state, ident)
    if not const_eq(token, child.fence):
        raise Refuse("FENCE")
    if child.status == "REPORTED":
        return state, child
    if moment < child.opened_at:
        raise Refuse("CLOCK")
    if child.status != "OPEN":
        raise Refuse("NOT_OPEN")
    # The lease is the window fixed at open. Equal-to is still fresh.
    if moment <= child.lease_until:
        raise Refuse("FRESH")
    updated = _append(state, "REPORT", {"child_id": ident, "at": moment})
    return updated, _must_child(updated, ident)


def rebuild(facts: object) -> Board:
    """Fold `facts` after the hash chain checks. A broken link refuses."""
    if not isinstance(facts, tuple) or len(facts) == 0:
        raise Refuse("BAD_BOARD")
    checked: list[Fact] = []
    for item in facts:
        if not isinstance(item, Fact):
            raise Refuse("BAD_BOARD")
        checked.append(item)
    chain = tuple(checked)
    _verify(chain)
    return _from_facts(chain)


def snapshot(board: object) -> Snapshot:
    """Public fields a later reader can compare without the child log."""
    state = _board(board)
    return Snapshot(
        schema=SCHEMA,
        max_depth=state.caps.max_depth,
        max_children=state.caps.max_children,
        max_iterations=state.caps.max_iterations,
        max_lease_s=state.caps.max_lease_s,
        parent_ids=tuple(parent.parent_id for parent in state.parents),
        child_ids=tuple(child.child_id for child in state.children),
        fences=tuple(parent.fence for parent in state.parents)
        + tuple(child.fence for child in state.children),
        statuses=tuple(child.status for child in state.children),
        summaries=tuple(child.summary for child in state.children),
        executes=tuple(child.executes for child in state.children),
        digests=tuple(fact.digest for fact in state.facts),
    )


def _finish(
    state: Board,
    child: Child,
    ident: str,
    text: str,
    moment: int,
    valid: bool | None,
    errors: tuple[str, ...],
    failure: str,
) -> tuple[Board, Child]:
    done = replace(
        child,
        status="DONE",
        summary=text,
        schema_valid=valid,
        schema_errors=errors,
        failure_class=failure,
        closed_at=moment,
    )
    updated = _append(state, "COMPLETE", _complete_fields(ident, text, moment, valid, errors, failure))
    found = _must_child(updated, ident)
    if found.status != done.status or found.summary != done.summary:
        raise Refuse("BROKEN_CHAIN")
    return updated, found


def _complete_fields(
    ident: str,
    text: str,
    moment: int,
    valid: bool | None,
    errors: tuple[str, ...],
    failure: str,
) -> dict[str, Json]:
    return {
        "child_id": ident,
        "summary": text,
        "at": moment,
        "schema_valid": valid,
        "schema_errors": list(errors),
        "failure_class": failure,
    }


def _cap_fields(caps: Caps) -> dict[str, Json]:
    return {
        "schema": SCHEMA,
        "requested_depth": caps.requested_depth,
        "requested_children": caps.requested_children,
        "requested_iterations": caps.requested_iterations,
        "requested_lease_s": caps.requested_lease_s,
        "max_depth": caps.max_depth,
        "max_children": caps.max_children,
        "max_iterations": caps.max_iterations,
        "max_lease_s": caps.max_lease_s,
    }


def _real_int(value: object, lo: int, hi: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("NOT_INT")
    if value < lo or value > hi:
        raise Refuse("OUT_OF_RANGE", f"{lo}..{hi}")
    return value


def _str_tuple(value: object) -> None:
    if not isinstance(value, tuple):
        raise Refuse("BAD_BOARD")
    for item in value:
        if not isinstance(item, str):
            raise Refuse("BAD_BOARD")


def _board(value: object) -> Board:
    if not isinstance(value, Board):
        raise Refuse("BAD_BOARD")
    return value


def _now(value: object) -> int:
    return bound_int(value, 0, _CLOCK_HI)


def _ident(value: object) -> str:
    text = bound_text(value, 64)
    if secret_shape(text):
        raise Refuse("SECRET")
    if _ID.fullmatch(text) is None:
        raise Refuse("BAD_ID")
    return text


def _credential(value: object) -> str:
    text = bound_text(value, 80)
    if text == "":
        raise Refuse("MISSING_CRED")
    if secret_shape(text):
        raise Refuse("SECRET")
    if _ID.fullmatch(text) is None:
        raise Refuse("BAD_ID")
    return text


def _fence(value: object) -> str:
    text = bound_text(value, 16)
    if secret_shape(text):
        raise Refuse("SECRET")
    if _FENCE.fullmatch(text) is None:
        raise Refuse("BAD_FENCE")
    return text


def _plain(value: object, empty_code: str) -> str:
    text = bound_text(value, _TEXT_LIMIT).strip()
    if text == "":
        raise Refuse(empty_code)
    if secret_shape(text):
        raise Refuse("SECRET")
    return text


def _tool_list(tools: object) -> tuple[str, ...]:
    if not isinstance(tools, (list, tuple)):
        raise Refuse("NOT_LIST")
    if len(tools) == 0:
        raise Refuse("EMPTY_ALLOW")
    if len(tools) > _TOOL_LIMIT:
        raise Refuse("OVERSIZE", str(_TOOL_LIMIT))
    names: list[str] = []
    for item in tools:
        name = bound_text(item, 64)
        if secret_shape(name):
            raise Refuse("SECRET")
        if name not in CLASSIFIED:
            raise Refuse("UNCLASSIFIED")
        names.append(name)
    return tuple(names)


def _schema_keys(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, (list, tuple)):
        raise Refuse("NOT_LIST")
    if len(value) == 0:
        raise Refuse("EMPTY_SCHEMA")
    if len(value) > _SCHEMA_LIMIT:
        raise Refuse("OVERSIZE", str(_SCHEMA_LIMIT))
    keys: list[str] = []
    seen: set[str] = set()
    for item in value:
        key = _ident(item)
        if key in seen:
            raise Refuse("DUPLICATE")
        seen.add(key)
        keys.append(key)
    return tuple(keys)


def _take_notes(value: object) -> tuple[str, ...]:
    """One pass. A note that does not fit the remaining budget is skipped."""
    if value is None:
        return ()
    if not isinstance(value, (list, tuple)):
        raise Refuse("NOT_LIST")
    if len(value) > _NOTE_LIMIT:
        raise Refuse("OVERSIZE", str(_NOTE_LIMIT))
    chosen: list[str] = []
    remaining = POLICY_NOTE_BUDGET
    for item in value:
        text = bound_text(item, _TEXT_LIMIT).strip()
        if text == "":
            raise Refuse("EMPTY_NOTE")
        if secret_shape(text):
            raise Refuse("SECRET")
        size = len(text)
        if size > remaining:
            continue
        chosen.append(text)
        remaining -= size
    return tuple(chosen)


def _goals(value: object) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise Refuse("NOT_LIST")
    if len(value) == 0:
        raise Refuse("EMPTY_GOAL")
    if len(value) > _BATCH_LIMIT:
        raise Refuse("OVERSIZE", str(_BATCH_LIMIT))
    return tuple(_plain(item, "EMPTY_GOAL") for item in value)


def _budget(requested: object, ceiling: int) -> tuple[int, int]:
    if requested is None:
        return ceiling, ceiling
    asked = bound_int(requested, 1, _REQUEST_HI)
    if asked > ceiling:
        return asked, ceiling
    return asked, asked


def _known(board: Board, ident: str) -> bool:
    for parent in board.parents:
        if parent.parent_id == ident:
            return True
    for child in board.children:
        if child.child_id == ident:
            return True
    return False


def _actor(board: Board, ident: str) -> Parent | Child:
    for parent in board.parents:
        if parent.parent_id == ident:
            return parent
    for child in board.children:
        if child.child_id == ident:
            return child
    raise Refuse("UNKNOWN_PARENT")


def _must_parent(board: Board, ident: str) -> Parent:
    for parent in board.parents:
        if parent.parent_id == ident:
            return parent
    raise Refuse("UNKNOWN_PARENT")


def _must_child(board: Board, ident: str) -> Child:
    for child in board.children:
        if child.child_id == ident:
            return child
    raise Refuse("UNKNOWN_CHILD")


def _parent_fence(board: Board, parent_id: str) -> str:
    actor = _actor(board, parent_id)
    return actor.fence


def _actor_depth(actor: Parent | Child) -> int:
    if isinstance(actor, Parent):
        return 0
    return actor.depth


def _hold(actor: Parent | Child, token: str, cred: str, moment: int) -> None:
    if not const_eq(token, actor.fence):
        raise Refuse("FENCE")
    if not const_eq(cred, actor.credential_id):
        raise Refuse("CRED_MISMATCH")
    if isinstance(actor, Parent):
        if moment < actor.opened_at:
            raise Refuse("CLOCK")
        return
    _ready(actor, moment)


def _ready(child: Child, moment: int) -> None:
    if moment < child.opened_at:
        raise Refuse("CLOCK")
    if child.status == "REPORTED":
        raise Refuse("STALE_FENCE")
    if child.status != "OPEN":
        raise Refuse("NOT_OPEN")
    # Past the lease the fence is still the child's, but the lease refuses.
    if moment > child.lease_until:
        raise Refuse("STALE_LEASE")


def _live(board: Board, parent_id: str) -> int:
    count = 0
    for child in board.children:
        if child.parent_id == parent_id and child.status == "OPEN":
            count += 1
    return count


def _fresh_id(board: Board) -> str:
    taken = {parent.parent_id for parent in board.parents}
    taken.update(child.child_id for child in board.children)
    number = len(board.children) + 1
    scanned = 0
    while scanned <= _ID_SCAN:
        candidate = "c" + str(number)
        if candidate not in taken:
            return candidate
        number += 1
        scanned += 1
    raise Refuse("OVERSIZE")


def _fresh_fence(board: Board) -> str:
    taken = {parent.fence for parent in board.parents}
    taken.update(child.fence for child in board.children)
    number = len(taken) + 1
    scanned = 0
    while scanned <= _ID_SCAN:
        candidate = "f" + str(number)
        if candidate not in taken and _FENCE.fullmatch(candidate) is not None:
            return candidate
        number += 1
        scanned += 1
    raise Refuse("OVERSIZE")


def _canonical(fields: dict[str, Json]) -> str:
    return json.dumps(fields, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(prev: str, seq: int, kind: str, body: str) -> str:
    raw = prev + "\n" + str(seq) + "\n" + kind + "\n" + body
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _same(left: str, right: str) -> bool:
    if len(left) != len(right):
        return False
    return hmac.compare_digest(left, right)


def _make_fact(facts: tuple[Fact, ...], kind: str, fields: dict[str, Json]) -> Fact:
    if kind not in _KINDS:
        raise Refuse("BROKEN_CHAIN")
    prev = _GENESIS if len(facts) == 0 else _last(facts).digest
    seq = len(facts) + 1
    body = bound_text(_canonical(fields), _BODY_LIMIT)
    return Fact(seq=seq, kind=kind, body=body, prev=prev, digest=_digest(prev, seq, kind, body))


def _last(facts: tuple[Fact, ...]) -> Fact:
    if len(facts) == 0:
        raise Refuse("BROKEN_CHAIN")
    return facts[len(facts) - 1]


def _append(board: Board, kind: str, fields: dict[str, Json]) -> Board:
    fact = _make_fact(board.facts, kind, fields)
    return _from_facts(board.facts + (fact,))


def _verify(facts: tuple[Fact, ...]) -> None:
    prev = _GENESIS
    for index, fact in enumerate(facts, start=1):
        if fact.seq != index or fact.kind not in _KINDS or not _same(fact.prev, prev):
            raise Refuse("BROKEN_CHAIN")
        expect = _digest(fact.prev, fact.seq, fact.kind, fact.body)
        if not _same(expect, fact.digest):
            raise Refuse("BROKEN_CHAIN")
        prev = fact.digest


def _from_facts(facts: tuple[Fact, ...]) -> Board:
    caps, parents, children = _fold(facts)
    return Board(caps=caps, parents=tuple(parents), children=tuple(children), facts=facts)


def _fold(
    facts: tuple[Fact, ...],
) -> tuple[Caps, list[Parent], list[Child]]:
    caps: Caps | None = None
    parents: list[Parent] = []
    children: list[Child] = []
    by_parent: dict[str, Parent] = {}
    by_child: dict[str, int] = {}
    fences: set[str] = set()
    if len(facts) == 0 or facts[0].kind != "BOARD":
        raise Refuse("BROKEN_CHAIN")
    for fact in facts:
        fields = _parse(fact.body)
        if fact.kind == "BOARD":
            if caps is not None:
                raise Refuse("BROKEN_CHAIN")
            caps = _caps_from(fields)
        elif fact.kind == "REGISTER":
            if caps is None:
                raise Refuse("BROKEN_CHAIN")
            parent = _parent_from(fields)
            if parent.parent_id in by_parent or parent.parent_id in by_child or parent.fence in fences:
                raise Refuse("DUPLICATE")
            fences.add(parent.fence)
            by_parent[parent.parent_id] = parent
            parents.append(parent)
        elif fact.kind == "OPEN":
            if caps is None:
                raise Refuse("BROKEN_CHAIN")
            child = _child_from(fields)
            _guard_open(child, caps, by_parent, children, by_child, fences)
            fences.add(child.fence)
            by_child[child.child_id] = len(children)
            children.append(child)
        elif fact.kind == "RETRY":
            _apply_retry(fields, children, by_child)
        elif fact.kind == "COMPLETE":
            _apply_complete(fields, children, by_child)
        elif fact.kind == "REPORT":
            _apply_report(fields, children, by_child)
        else:
            raise Refuse("BROKEN_CHAIN")
    if caps is None:
        raise Refuse("BROKEN_CHAIN")
    return caps, parents, children


def _parse(body: str) -> dict[str, object]:
    try:
        loaded: object = json.loads(body)
    except json.JSONDecodeError:
        raise Refuse("BROKEN_CHAIN") from None
    if not isinstance(loaded, dict):
        raise Refuse("BROKEN_CHAIN")
    out: dict[str, object] = {}
    for key, item in loaded.items():
        if not isinstance(key, str):
            raise Refuse("BROKEN_CHAIN")
        out[key] = item
    return out


def _need_str(fields: dict[str, object], key: str) -> str:
    value = fields.get(key)
    if not isinstance(value, str):
        raise Refuse("BROKEN_CHAIN")
    return value


def _need_int(fields: dict[str, object], key: str, lo: int, hi: int) -> int:
    value = fields.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < lo or value > hi:
        raise Refuse("BROKEN_CHAIN")
    return value


def _need_strs(fields: dict[str, object], key: str) -> tuple[str, ...]:
    value = fields.get(key)
    if not isinstance(value, list):
        raise Refuse("BROKEN_CHAIN")
    out: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise Refuse("BROKEN_CHAIN")
        out.append(item)
    return tuple(out)


def _need_tristate(fields: dict[str, object], key: str) -> bool | None:
    if key not in fields:
        raise Refuse("BROKEN_CHAIN")
    value = fields[key]
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    raise Refuse("BROKEN_CHAIN")


def _caps_from(fields: dict[str, object]) -> Caps:
    if not const_eq(_need_str(fields, "schema"), SCHEMA):
        raise Refuse("BAD_BOARD")
    return Caps(
        requested_depth=_need_int(fields, "requested_depth", 1, _REQUEST_HI),
        requested_children=_need_int(fields, "requested_children", 1, _REQUEST_HI),
        requested_iterations=_need_int(fields, "requested_iterations", 1, _REQUEST_HI),
        requested_lease_s=_need_int(fields, "requested_lease_s", 1, _REQUEST_HI),
        max_depth=_need_int(fields, "max_depth", 1, POLICY_DEPTH),
        max_children=_need_int(fields, "max_children", 1, POLICY_CHILDREN),
        max_iterations=_need_int(fields, "max_iterations", 1, POLICY_ITERATIONS),
        max_lease_s=_need_int(fields, "max_lease_s", 1, POLICY_LEASE_S),
    )


def _parent_from(fields: dict[str, object]) -> Parent:
    return Parent(
        parent_id=_need_str(fields, "parent_id"),
        credential_id=_need_str(fields, "credential_id"),
        opened_at=_need_int(fields, "opened_at", 0, _CLOCK_HI),
        fence=_need_str(fields, "fence"),
    )


def _child_from(fields: dict[str, object]) -> Child:
    return Child(
        child_id=_need_str(fields, "child_id"),
        parent_id=_need_str(fields, "parent_id"),
        depth=_need_int(fields, "depth", 1, POLICY_DEPTH),
        goal=_need_str(fields, "goal"),
        summary="",
        granted=_need_strs(fields, "granted"),
        stripped=_need_strs(fields, "stripped"),
        iterations=_need_int(fields, "iterations", 1, POLICY_ITERATIONS),
        requested_iterations=_need_int(fields, "requested_iterations", 1, _REQUEST_HI),
        status="OPEN",
        opened_at=_need_int(fields, "opened_at", 0, _CLOCK_HI),
        lease_until=_need_int(fields, "lease_until", 0, _CLOCK_HI),
        requested_lease_s=_need_int(fields, "requested_lease_s", 1, _REQUEST_HI),
        credential_id=_need_str(fields, "credential_id"),
        fence=_need_str(fields, "fence"),
        context=_need_strs(fields, "context"),
        schema_keys=_need_strs(fields, "schema_keys"),
        executes=EXECUTES,
    )


def _guard_open(
    child: Child,
    caps: Caps,
    by_parent: dict[str, Parent],
    children: list[Child],
    by_child: dict[str, int],
    fences: set[str],
) -> None:
    if child.child_id in by_parent or child.child_id in by_child or child.fence in fences:
        raise Refuse("DUPLICATE")
    if child.iterations != min(child.requested_iterations, caps.max_iterations):
        raise Refuse("BROKEN_CHAIN")
    if child.lease_until - child.opened_at != min(child.requested_lease_s, caps.max_lease_s):
        raise Refuse("BROKEN_CHAIN")
    if child.depth > caps.max_depth:
        raise Refuse("BROKEN_CHAIN")
    granted = set(child.granted)
    stripped = set(child.stripped)
    if granted & stripped or not granted <= CLASSIFIED or not stripped <= CLASSIFIED:
        raise Refuse("BROKEN_CHAIN")
    if granted & ALWAYS_STRIP:
        raise Refuse("BROKEN_CHAIN")
    if child.depth == caps.max_depth and "delegate" in granted:
        raise Refuse("BROKEN_CHAIN")
    total = 0
    for note in child.context:
        total += len(note)
        if len(note) > POLICY_NOTE_BUDGET or total > POLICY_NOTE_BUDGET:
            raise Refuse("BROKEN_CHAIN")
    parent = by_parent.get(child.parent_id)
    if parent is not None:
        if child.opened_at < parent.opened_at or child.credential_id != parent.credential_id:
            raise Refuse("BROKEN_CHAIN")
        if child.depth != 1:
            raise Refuse("BROKEN_CHAIN")
        return
    index = by_child.get(child.parent_id)
    if index is None:
        raise Refuse("BROKEN_CHAIN")
    host = children[index]
    if host.status != "OPEN" or child.opened_at < host.opened_at or child.opened_at > host.lease_until:
        raise Refuse("BROKEN_CHAIN")
    if child.credential_id != host.credential_id or child.depth != host.depth + 1:
        raise Refuse("BROKEN_CHAIN")


def _slot(fields: dict[str, object], children: list[Child], by_child: dict[str, int]) -> tuple[int, Child]:
    ident = _need_str(fields, "child_id")
    index = by_child.get(ident)
    if index is None:
        raise Refuse("BROKEN_CHAIN")
    return index, children[index]


def _apply_retry(fields: dict[str, object], children: list[Child], by_child: dict[str, int]) -> None:
    index, current = _slot(fields, children, by_child)
    if current.status != "OPEN" or current.schema_attempts != 0 or len(current.schema_keys) == 0:
        raise Refuse("BROKEN_CHAIN")
    failure = _need_str(fields, "failure_class")
    if failure != SCHEMA_MISS:
        raise Refuse("BROKEN_CHAIN")
    _need_int(fields, "at", current.opened_at, current.lease_until)
    children[index] = replace(
        current,
        schema_attempts=1,
        schema_errors=_need_strs(fields, "schema_errors"),
        failure_class=SCHEMA_MISS,
    )


def _apply_complete(fields: dict[str, object], children: list[Child], by_child: dict[str, int]) -> None:
    index, current = _slot(fields, children, by_child)
    if current.status != "OPEN":
        raise Refuse("BROKEN_CHAIN")
    moment = _need_int(fields, "at", current.opened_at, current.lease_until)
    failure = _need_str(fields, "failure_class")
    if failure not in _FAILURES:
        raise Refuse("BROKEN_CHAIN")
    children[index] = replace(
        current,
        status="DONE",
        summary=_need_str(fields, "summary"),
        schema_valid=_need_tristate(fields, "schema_valid"),
        schema_errors=_need_strs(fields, "schema_errors"),
        failure_class=failure,
        closed_at=moment,
    )


def _apply_report(fields: dict[str, object], children: list[Child], by_child: dict[str, int]) -> None:
    index, current = _slot(fields, children, by_child)
    if current.status != "OPEN":
        raise Refuse("BROKEN_CHAIN")
    moment = _need_int(fields, "at", current.lease_until + 1, _CLOCK_HI)
    children[index] = replace(current, status="REPORTED", closed_at=moment)


def _schema_errors(summary: str, keys: tuple[str, ...]) -> tuple[str, ...]:
    found = _json_object(summary)
    if found is None:
        return ("not-object",)
    missing = [key for key in keys if key not in found]
    return tuple("missing:" + key for key in missing)


def _json_object(text: str) -> dict[str, object] | None:
    candidate = text.strip()
    fenced = _CODE_FENCE.search(candidate)
    if fenced is not None:
        inner = fenced.group(1)
        candidate = inner.strip() if inner is not None else ""
    elif not candidate.startswith("{"):
        start = candidate.find("{")
        end = candidate.rfind("}")
        if start < 0 or end <= start:
            return None
        candidate = candidate[start : end + 1]
    try:
        loaded: object = json.loads(candidate)
    except json.JSONDecodeError:
        return None
    if not isinstance(loaded, dict):
        return None
    out: dict[str, object] = {}
    for key, item in loaded.items():
        if not isinstance(key, str):
            return None
        out[key] = item
    return out


__all__ = [
    "ALWAYS_STRIP",
    "CLASSIFIED",
    "EXECUTES",
    "POLICY_CHILDREN",
    "POLICY_DEPTH",
    "POLICY_ITERATIONS",
    "POLICY_LEASE_S",
    "POLICY_NOTE_BUDGET",
    "SCHEMA",
    "SCHEMA_MISS",
    "Board",
    "Caps",
    "Child",
    "Fact",
    "Parent",
    "Snapshot",
    "complete",
    "make_board",
    "open_batch",
    "open_child",
    "parent_view",
    "present",
    "rebuild",
    "register",
    "report_stale",
    "snapshot",
    "strip_tools",
]
