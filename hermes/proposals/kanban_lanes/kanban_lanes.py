"""Lane assignments, one crash retry, and an argv list. Nothing is started."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Final

from cosmos_hermes import Refuse, bound_int, bound_text, const_eq, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-kanban_lanes/1"
POLICY_WORKER_CAP: Final[int] = 4
RETRY_FAILURE: Final[str] = "crash"

_REQUEST_HI: Final[int] = 1_000_000_000
_CLOCK_HI: Final[int] = 4_000_000_000
_TEXT: Final[int] = 64
_BODY: Final[int] = 4_096
_ALLOW_MAX: Final[int] = 32
_LANE_MAX: Final[int] = 32
_ASSIGN_MAX: Final[int] = 256
_EVENT_MAX: Final[int] = 512
_GENESIS: Final[str] = "0" * 64

_LANE_FIELDS: Final[int] = 9
_ASSIGN_FIELDS: Final[int] = 8
_RETRY_FIELDS: Final[int] = 9
_CRASH_FIELDS: Final[int] = 4
_TERM_FIELDS: Final[int] = 5

_KINDS: Final[frozenset[str]] = frozenset({"profile", "external"})
_STATUSES: Final[frozenset[str]] = frozenset(
    {"ASSIGNED", "REQUEUED", "COMPLETE", "REVIEW", "BLOCKED"}
)
_CLOSED: Final[frozenset[str]] = frozenset({"COMPLETE", "REVIEW", "BLOCKED"})
_ACTIONS: Final[dict[str, str]] = {
    "COMPLETE": "COMPLETE",
    "REVIEW": "REVIEW",
    "BLOCK": "BLOCKED",
}
_META: Final[frozenset[str]] = frozenset(
    {";", "|", "&", "<", ">", "$", "`", "\\", '"', "'", "*", "?"}
)
_ID: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$")
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")
_INT: Final[re.Pattern[str]] = re.compile(r"^(0|[1-9][0-9]{0,9})$")
_UNSET: Final[object] = object()


def _shell(text: str) -> bool:
    for char in text:
        if char.isspace() or char in _META:
            return True
    return False


def _ident(value: object, *, missing: str) -> str:
    if value is None:
        raise Refuse(missing)
    if type(value) is not str:
        raise Refuse("NOT_TEXT")
    text = bound_text(value, _TEXT)
    if text == "":
        raise Refuse(missing)
    if secret_shape(text):
        raise Refuse("SECRET")
    if _shell(text):
        raise Refuse("SHELL_STRING")
    if _ID.fullmatch(text) is None:
        raise Refuse("BAD_ID")
    return text


def _word(value: object) -> str:
    return _ident(value, missing="EMPTY_ARG")


def _fence(value: object) -> str:
    if value is None:
        raise Refuse("BAD_FENCE")
    if type(value) is not str:
        raise Refuse("NOT_TEXT")
    text = bound_text(value, _TEXT)
    if text == "":
        raise Refuse("BAD_FENCE")
    if secret_shape(text):
        raise Refuse("SECRET")
    if _shell(text) or _ID.fullmatch(text) is None:
        raise Refuse("BAD_FENCE")
    return text


def _kind(value: object) -> str:
    text = _ident(value, missing="UNKNOWN_MODE")
    if text not in _KINDS:
        raise Refuse("UNKNOWN_MODE")
    return text


def _allow(value: object) -> tuple[str, ...]:
    if type(value) is not list and type(value) is not tuple:
        raise Refuse("EMPTY_ALLOW")
    if len(value) == 0:
        raise Refuse("EMPTY_ALLOW")
    if len(value) > _ALLOW_MAX:
        raise Refuse("OVERSIZE", str(_ALLOW_MAX))
    seen: set[str] = set()
    rows: list[str] = []
    for item in value:
        token = _word(item)
        if token in seen:
            raise Refuse("DUPLICATE")
        seen.add(token)
        rows.append(token)
    return tuple(rows)


def _clock(value: object) -> int:
    return bound_int(value, 0, _CLOCK_HI)


def _requested(value: object) -> int:
    return bound_int(value, 1, _REQUEST_HI)


def _action(value: object) -> str:
    if type(value) is not str:
        raise Refuse("UNCLASSIFIED")
    text = bound_text(value, 32)
    if secret_shape(text):
        raise Refuse("SECRET")
    if text not in _ACTIONS:
        raise Refuse("UNCLASSIFIED")
    return text


def _outcome(action: str) -> str:
    status = _ACTIONS.get(action)
    if status is None:
        raise Refuse("UNCLASSIFIED")
    return status


def _failure(value: object) -> str:
    if value is None:
        raise Refuse("NO_RETRY")
    return _ident(value, missing="NO_RETRY")


def _nat(text: str, hi: int) -> int:
    if _INT.fullmatch(text) is None:
        raise Refuse("BAD_EVENT")
    return bound_int(int(text), 0, hi)


def _digest(prev: str, body: str) -> str:
    if not prev.isascii() or not body.isascii():
        raise Refuse("BAD_EVENT")
    return hashlib.sha256((prev + "\n" + body).encode("ascii")).hexdigest()


def _parts(body: str, count: int) -> tuple[str, ...]:
    pieces = body.split("|")
    if len(pieces) != count:
        raise Refuse("BAD_EVENT")
    return tuple(pieces)


def _field(parts: tuple[str, ...], index: int) -> str:
    if index < 0 or index >= len(parts):
        raise Refuse("BAD_EVENT")
    return parts[index]


@dataclass(frozen=True, slots=True)
class Lane:
    """One assignee. `worker_cap` is the cap that is enforced."""

    lane_id: str
    assignee: str
    kind: str
    worker_cap: int
    requested_cap: int
    policy_cap: int
    credential_id: str
    allow: tuple[str, ...]
    schema: str

    def __post_init__(self) -> None:
        if type(self.schema) is not str or self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        if _ident(self.lane_id, missing="BAD_ID") != self.lane_id:
            raise Refuse("BAD_ID")
        if _ident(self.assignee, missing="BAD_ID") != self.assignee:
            raise Refuse("BAD_ID")
        if type(self.kind) is not str:
            raise Refuse("UNKNOWN_MODE")
        if _ident(self.kind, missing="UNKNOWN_MODE") not in _KINDS:
            raise Refuse("UNKNOWN_MODE")
        if type(self.policy_cap) is not int or type(self.worker_cap) is not int:
            raise Refuse("NOT_INT")
        if self.policy_cap != POLICY_WORKER_CAP:
            raise Refuse("BAD_LIMIT")
        asked = _requested(self.requested_cap)
        if self.worker_cap != min(asked, POLICY_WORKER_CAP):
            raise Refuse("BAD_LIMIT")
        if _ident(self.credential_id, missing="MISSING_CRED") != self.credential_id:
            raise Refuse("MISSING_CRED")
        if _allow(self.allow) != self.allow:
            raise Refuse("DUPLICATE")


@dataclass(frozen=True, slots=True)
class Assignment:
    """One card claimed by one lane. No process id is stored."""

    assignment_id: str
    lane_id: str
    card_id: str
    status: str
    crashes: int
    requeues: int
    argv: tuple[str, str]
    fence: str
    opened_at: int
    schema: str

    def __post_init__(self) -> None:
        if type(self.schema) is not str or self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        if type(self.status) is not str or self.status not in _STATUSES:
            raise Refuse("BAD_ASSIGNMENT")
        if type(self.crashes) is not int or type(self.requeues) is not int:
            raise Refuse("NOT_INT")
        if self.crashes != self.requeues or self.crashes not in (0, 1):
            raise Refuse("BAD_ASSIGNMENT")
        if self.status == "REQUEUED" and self.crashes != 1:
            raise Refuse("BAD_ASSIGNMENT")
        if _clock(self.opened_at) != self.opened_at:
            raise Refuse("OUT_OF_RANGE")
        if type(self.argv) is not tuple or len(self.argv) != 2:
            raise Refuse("BAD_ARGV")
        if _word(self.argv[0]) != self.argv[0] or _word(self.argv[1]) != self.argv[1]:
            raise Refuse("BAD_ARGV")
        if _ident(self.assignment_id, missing="BAD_ID") != self.assignment_id:
            raise Refuse("BAD_ID")
        if _ident(self.lane_id, missing="BAD_ID") != self.lane_id:
            raise Refuse("BAD_ID")
        if _ident(self.card_id, missing="BAD_ID") != self.card_id:
            raise Refuse("BAD_ID")
        if _fence(self.fence) != self.fence:
            raise Refuse("BAD_FENCE")


@dataclass(frozen=True, slots=True)
class Event:
    """One hash-chained ledger row. `body` is the transition."""

    event_id: str
    prev_sha: str
    body: str
    sha: str
    schema: str

    def __post_init__(self) -> None:
        if type(self.schema) is not str or self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        if (
            type(self.body) is not str
            or type(self.prev_sha) is not str
            or type(self.sha) is not str
            or type(self.event_id) is not str
        ):
            raise Refuse("BAD_EVENT")
        body = bound_text(self.body, _BODY)
        if secret_shape(body):
            raise Refuse("SECRET")
        if _HEX.fullmatch(self.prev_sha) is None or _HEX.fullmatch(self.sha) is None:
            raise Refuse("CHAIN")
        digest = _digest(self.prev_sha, body)
        if self.sha != digest or self.event_id != digest:
            raise Refuse("CHAIN")


@dataclass(slots=True)
class _Fold:
    lanes: list[Lane]
    assignments: list[Assignment]
    lane_of: dict[str, Lane]
    allow_of: dict[str, frozenset[str]]
    owners: set[str]
    latest: dict[str, Assignment]
    by_id: dict[str, int]
    fences: set[str]
    occupy: dict[str, int]
    at: int


def _new_fold() -> _Fold:
    return _Fold(
        lanes=[],
        assignments=[],
        lane_of={},
        allow_of={},
        owners=set(),
        latest={},
        by_id={},
        fences=set(),
        occupy={},
        at=0,
    )


def _time(fold: _Fold, moment: int) -> None:
    if moment < fold.at:
        raise Refuse("STALE")
    fold.at = moment


def _next_id(fold: _Fold) -> str:
    ident = "a" + str(len(fold.assignments) + 1)
    if ident in fold.by_id:
        raise Refuse("DUPLICATE")
    return ident


def _remember(fold: _Fold, row: Assignment) -> None:
    fold.by_id[row.assignment_id] = len(fold.assignments)
    fold.assignments.append(row)
    fold.latest[row.card_id] = row
    fold.fences.add(row.fence)
    if row.status == "ASSIGNED":
        fold.occupy[row.lane_id] = fold.occupy.get(row.lane_id, 0) + 1


def _replace(fold: _Fold, current: Assignment, row: Assignment) -> None:
    index = fold.by_id.get(current.assignment_id)
    if index is None:
        raise Refuse("UNKNOWN_ASSIGNMENT")
    if fold.latest.get(current.card_id) is not current:
        raise Refuse("BAD_ASSIGNMENT")
    if current.status == "ASSIGNED":
        held = fold.occupy.get(current.lane_id, 0)
        if held < 1:
            raise Refuse("BAD_ASSIGNMENT")
        fold.occupy[current.lane_id] = held - 1
    fold.assignments[index] = row
    fold.latest[row.card_id] = row
    if row.status == "ASSIGNED":
        fold.occupy[row.lane_id] = fold.occupy.get(row.lane_id, 0) + 1


def _lane_body(lane: Lane) -> str:
    return "|".join(
        (
            "L",
            lane.lane_id,
            lane.assignee,
            lane.kind,
            str(lane.worker_cap),
            str(lane.requested_cap),
            str(lane.policy_cap),
            lane.credential_id,
            ",".join(lane.allow),
        )
    )


def _on_lane(fold: _Fold, body: str) -> None:
    parts = _parts(body, _LANE_FIELDS)
    lane_id = _ident(_field(parts, 1), missing="BAD_ID")
    assignee = _ident(_field(parts, 2), missing="BAD_ID")
    kind = _kind(_field(parts, 3))
    worker = _nat(_field(parts, 4), _REQUEST_HI)
    requested = _nat(_field(parts, 5), _REQUEST_HI)
    policy = _nat(_field(parts, 6), _REQUEST_HI)
    cred = _ident(_field(parts, 7), missing="MISSING_CRED")
    allow_text = _field(parts, 8)
    if allow_text == "":
        raise Refuse("EMPTY_ALLOW")
    allow = _allow(tuple(allow_text.split(",")))
    if lane_id in fold.lane_of or assignee in fold.owners:
        raise Refuse("DUPLICATE")
    if len(fold.lanes) >= _LANE_MAX:
        raise Refuse("OVERSIZE", str(_LANE_MAX))
    lane = Lane(
        lane_id=lane_id,
        assignee=assignee,
        kind=kind,
        worker_cap=worker,
        requested_cap=requested,
        policy_cap=policy,
        credential_id=cred,
        allow=allow,
        schema=SCHEMA,
    )
    fold.lanes.append(lane)
    fold.lane_of[lane.lane_id] = lane
    fold.allow_of[lane.lane_id] = frozenset(lane.allow)
    fold.owners.add(lane.assignee)


def _gate(
    fold: _Fold,
    lane_id: str,
    cred: str,
    interp: str,
    fence: str,
    moment: int,
) -> Lane:
    lane = fold.lane_of.get(lane_id)
    if lane is None:
        raise Refuse("UNKNOWN_LANE")
    if not const_eq(cred, lane.credential_id):
        raise Refuse("CRED_MISMATCH")
    allowed = fold.allow_of.get(lane_id)
    if allowed is None or interp not in allowed:
        raise Refuse("NOT_ALLOWED")
    if fence in fold.fences:
        raise Refuse("REPLAY")
    _time(fold, moment)
    return lane


def _room(fold: _Fold, lane: Lane) -> None:
    if fold.occupy.get(lane.lane_id, 0) >= lane.worker_cap:
        raise Refuse("LANE_FULL", str(lane.worker_cap))
    if len(fold.assignments) >= _ASSIGN_MAX:
        raise Refuse("OVERSIZE", str(_ASSIGN_MAX))


def _on_assign(fold: _Fold, body: str) -> None:
    parts = _parts(body, _ASSIGN_FIELDS)
    lane_id = _ident(_field(parts, 1), missing="BAD_ID")
    card_id = _ident(_field(parts, 2), missing="BAD_ID")
    interp = _word(_field(parts, 3))
    script = _word(_field(parts, 4))
    fence = _fence(_field(parts, 5))
    moment = _nat(_field(parts, 6), _CLOCK_HI)
    cred = _ident(_field(parts, 7), missing="MISSING_CRED")
    lane = _gate(fold, lane_id, cred, interp, fence, moment)
    prior = fold.latest.get(card_id)
    if prior is not None:
        if prior.lane_id != lane_id:
            raise Refuse("DUPLICATE")
        if prior.status == "ASSIGNED":
            raise Refuse("DUPLICATE")
        if prior.status == "REQUEUED":
            raise Refuse("NO_RETRY")
        if prior.status in _CLOSED:
            raise Refuse("CLOSED")
        raise Refuse("BAD_ASSIGNMENT")
    _room(fold, lane)
    _remember(
        fold,
        Assignment(
            assignment_id=_next_id(fold),
            lane_id=lane.lane_id,
            card_id=card_id,
            status="ASSIGNED",
            crashes=0,
            requeues=0,
            argv=(interp, script),
            fence=fence,
            opened_at=moment,
            schema=SCHEMA,
        ),
    )


def _on_retry(fold: _Fold, body: str) -> None:
    parts = _parts(body, _RETRY_FIELDS)
    lane_id = _ident(_field(parts, 1), missing="BAD_ID")
    card_id = _ident(_field(parts, 2), missing="BAD_ID")
    interp = _word(_field(parts, 3))
    script = _word(_field(parts, 4))
    fence = _fence(_field(parts, 5))
    moment = _nat(_field(parts, 6), _CLOCK_HI)
    cred = _ident(_field(parts, 7), missing="MISSING_CRED")
    failure = _failure(_field(parts, 8))
    lane = _gate(fold, lane_id, cred, interp, fence, moment)
    prior = fold.latest.get(card_id)
    if prior is None:
        raise Refuse("NO_RETRY")
    if prior.lane_id != lane_id:
        raise Refuse("DUPLICATE")
    if prior.status in _CLOSED:
        raise Refuse("CLOSED")
    if prior.status == "ASSIGNED":
        if prior.requeues >= 1:
            raise Refuse("RETRY_CAP", "1")
        raise Refuse("NO_RETRY")
    if prior.status != "REQUEUED" or prior.crashes != 1 or prior.requeues != 1:
        raise Refuse("RETRY_CAP", "1")
    if not const_eq(failure, RETRY_FAILURE):
        raise Refuse("NO_RETRY")
    _room(fold, lane)
    _remember(
        fold,
        Assignment(
            assignment_id=_next_id(fold),
            lane_id=lane.lane_id,
            card_id=card_id,
            status="ASSIGNED",
            crashes=prior.crashes,
            requeues=prior.requeues,
            argv=(interp, script),
            fence=fence,
            opened_at=moment,
            schema=SCHEMA,
        ),
    )


def _row(fold: _Fold, assignment_id: str) -> Assignment:
    index = fold.by_id.get(assignment_id)
    if index is None:
        raise Refuse("UNKNOWN_ASSIGNMENT")
    return fold.assignments[index]


def _on_crash(fold: _Fold, body: str) -> None:
    parts = _parts(body, _CRASH_FIELDS)
    assignment_id = _ident(_field(parts, 1), missing="BAD_ID")
    fence = _fence(_field(parts, 2))
    moment = _nat(_field(parts, 3), _CLOCK_HI)
    current = _row(fold, assignment_id)
    _time(fold, moment)
    if not const_eq(fence, current.fence):
        raise Refuse("STALE")
    if current.crashes >= 1 or current.requeues >= 1:
        raise Refuse("REQUEUE_CAP", "1")
    if current.status != "ASSIGNED":
        raise Refuse("NOT_ASSIGNED")
    _replace(
        fold,
        current,
        Assignment(
            assignment_id=current.assignment_id,
            lane_id=current.lane_id,
            card_id=current.card_id,
            status="REQUEUED",
            crashes=1,
            requeues=1,
            argv=current.argv,
            fence=current.fence,
            opened_at=current.opened_at,
            schema=SCHEMA,
        ),
    )


def _on_terminate(fold: _Fold, body: str) -> None:
    parts = _parts(body, _TERM_FIELDS)
    assignment_id = _ident(_field(parts, 1), missing="BAD_ID")
    action = _action(_field(parts, 2))
    fence = _fence(_field(parts, 3))
    moment = _nat(_field(parts, 4), _CLOCK_HI)
    current = _row(fold, assignment_id)
    _time(fold, moment)
    if not const_eq(fence, current.fence):
        raise Refuse("STALE")
    if current.status != "ASSIGNED":
        raise Refuse("NOT_ASSIGNED")
    _replace(
        fold,
        current,
        Assignment(
            assignment_id=current.assignment_id,
            lane_id=current.lane_id,
            card_id=current.card_id,
            status=_outcome(action),
            crashes=current.crashes,
            requeues=current.requeues,
            argv=current.argv,
            fence=current.fence,
            opened_at=current.opened_at,
            schema=SCHEMA,
        ),
    )


def _replay(events: tuple[Event, ...]) -> tuple[tuple[Lane, ...], tuple[Assignment, ...], int]:
    fold = _new_fold()
    for event in events:
        kind = event.body.split("|", 1)[0]
        if kind == "L":
            _on_lane(fold, event.body)
        elif kind == "A":
            _on_assign(fold, event.body)
        elif kind == "R":
            _on_retry(fold, event.body)
        elif kind == "C":
            _on_crash(fold, event.body)
        elif kind == "T":
            _on_terminate(fold, event.body)
        else:
            raise Refuse("BAD_EVENT")
    for lane in fold.lanes:
        if fold.occupy.get(lane.lane_id, 0) > lane.worker_cap:
            raise Refuse("LANE_FULL", str(lane.worker_cap))
    return tuple(fold.lanes), tuple(fold.assignments), fold.at


def _last_event(events: tuple[Event, ...]) -> Event:
    if len(events) == 0:
        raise Refuse("BAD_EVENT")
    return events[len(events) - 1]


def _seal(prev: str, body: str) -> Event:
    text = bound_text(body, _BODY)
    digest = _digest(prev, text)
    return Event(event_id=digest, prev_sha=prev, body=text, sha=digest, schema=SCHEMA)


def _chain(events: tuple[Event, ...], body: str) -> tuple[Event, ...]:
    if len(events) > _EVENT_MAX - 1:
        raise Refuse("OVERSIZE", str(_EVENT_MAX))
    prev = _GENESIS if len(events) == 0 else _last_event(events).sha
    return events + (_seal(prev, body),)


def _event_rows(value: object) -> tuple[Event, ...]:
    if type(value) is not tuple and type(value) is not list:
        raise Refuse("BAD_EVENT")
    if len(value) > _EVENT_MAX:
        raise Refuse("OVERSIZE", str(_EVENT_MAX))
    rows: list[Event] = []
    seen: set[str] = set()
    expect = _GENESIS
    for item in value:
        if type(item) is not Event:
            raise Refuse("BAD_EVENT")
        if item.event_id in seen:
            raise Refuse("DUPLICATE")
        seen.add(item.event_id)
        if item.prev_sha != expect:
            raise Refuse("CHAIN")
        expect = item.sha
        rows.append(item)
    return tuple(rows)


def _as_board(value: object) -> Board:
    if type(value) is not Board:
        raise Refuse("BAD_BOARD")
    return value


def _lane_rows(value: object) -> tuple[Lane, ...]:
    if type(value) is not list and type(value) is not tuple:
        raise Refuse("BAD_BOARD")
    if len(value) > _LANE_MAX:
        raise Refuse("OVERSIZE", str(_LANE_MAX))
    rows: list[Lane] = []
    seen: set[str] = set()
    owners: set[str] = set()
    for item in value:
        if type(item) is not Lane:
            raise Refuse("BAD_LANE")
        if item.lane_id in seen or item.assignee in owners:
            raise Refuse("DUPLICATE")
        seen.add(item.lane_id)
        owners.add(item.assignee)
        rows.append(item)
    return tuple(rows)


def _argv(interpreter: object, script: object) -> tuple[str, str]:
    words = spec_argv(interpreter, script)
    if len(words) != 2:
        raise Refuse("BAD_ARGV")
    return words[0], words[1]


def _latest(board: Board, card_id: str) -> Assignment | None:
    found: Assignment | None = None
    for row in board.assignments:
        if row.card_id == card_id:
            found = row
    return found


def _by_id(board: Board, assignment_id: str) -> Assignment:
    for row in board.assignments:
        if row.assignment_id == assignment_id:
            return row
    raise Refuse("UNKNOWN_ASSIGNMENT")


def _lanes(board: Board) -> dict[str, Lane]:
    return {lane.lane_id: lane for lane in board.lanes}


@dataclass(frozen=True, slots=True)
class Board:
    """Assignment ledger. The kanban kernel stays the authority for lifecycle truth."""

    lanes: tuple[Lane, ...]
    assignments: tuple[Assignment, ...]
    events: tuple[Event, ...]
    at: int
    schema: str

    def __post_init__(self) -> None:
        if type(self.schema) is not str or self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        if (
            type(self.lanes) is not tuple
            or type(self.assignments) is not tuple
            or type(self.events) is not tuple
        ):
            raise Refuse("BAD_BOARD")
        if (
            len(self.lanes) > _LANE_MAX
            or len(self.assignments) > _ASSIGN_MAX
            or len(self.events) > _EVENT_MAX
        ):
            raise Refuse("OVERSIZE", str(_EVENT_MAX))
        if type(self.at) is not int:
            raise Refuse("NOT_INT")
        if _clock(self.at) != self.at:
            raise Refuse("OUT_OF_RANGE")
        for lane in self.lanes:
            if type(lane) is not Lane:
                raise Refuse("BAD_LANE")
        for row in self.assignments:
            if type(row) is not Assignment:
                raise Refuse("BAD_ASSIGNMENT")
        _event_rows(self.events)
        lanes, rows, at = _replay(self.events)
        if self.lanes != lanes or self.assignments != rows or self.at != at:
            raise Refuse("BAD_BOARD")


def make_lane(
    lane_id: object,
    assignee: object,
    kind: object,
    *,
    credential_id: object,
    allow: object,
    requested_cap: object = POLICY_WORKER_CAP,
) -> Lane:
    """Record a lane. A request above the policy cap does not raise `worker_cap`."""
    asked = _requested(requested_cap)
    return Lane(
        lane_id=_ident(lane_id, missing="BAD_ID"),
        assignee=_ident(assignee, missing="BAD_ID"),
        kind=_kind(kind),
        worker_cap=min(asked, POLICY_WORKER_CAP),
        requested_cap=asked,
        policy_cap=POLICY_WORKER_CAP,
        credential_id=_ident(credential_id, missing="MISSING_CRED"),
        allow=_allow(allow),
        schema=SCHEMA,
    )


def make_board(lanes: object = ()) -> Board:
    """Copy lane records into an empty assignment ledger."""
    rows = _lane_rows(lanes)
    events: tuple[Event, ...] = ()
    for lane in rows:
        events = _chain(events, _lane_body(lane))
    return Board(lanes=rows, assignments=(), events=events, at=0, schema=SCHEMA)


def spec_argv(interpreter: object, script: object = _UNSET) -> list[str]:
    """Return `[interpreter, script]`. A lone string is shell syntax and is refused.

    The list is a fresh descriptor. This function does not start a worker.
    """
    if script is _UNSET:
        if type(interpreter) is str:
            text = bound_text(interpreter, _TEXT)
            if secret_shape(text):
                raise Refuse("SECRET")
            raise Refuse("SHELL_STRING")
        raise Refuse("BAD_ARGV")
    return [_word(interpreter), _word(script)]


def assign(
    board: object,
    lane_id: object,
    card_id: object,
    interpreter: object,
    script: object,
    *,
    now: object,
    credential_id: object,
    fence: object,
) -> tuple[Board, Assignment]:
    """Claim one slot for a new card. The argv is stored and not executed."""
    state = _as_board(board)
    lane_text = _ident(lane_id, missing="BAD_ID")
    card_text = _ident(card_id, missing="BAD_ID")
    interp, script_text = _argv(interpreter, script)
    fence_text = _fence(fence)
    moment = _clock(now)
    cred = _ident(credential_id, missing="MISSING_CRED")
    body = "|".join(
        ("A", lane_text, card_text, interp, script_text, fence_text, str(moment), cred)
    )
    built = rebuild(_chain(state.events, body))
    row = _latest(built, card_text)
    if row is None:
        raise Refuse("UNKNOWN_ASSIGNMENT")
    return built, row


def retry(
    board: object,
    lane_id: object,
    card_id: object,
    interpreter: object,
    script: object,
    *,
    now: object,
    credential_id: object,
    fence: object,
    failure: object,
) -> tuple[Board, Assignment]:
    """One confirming retry, and only when `failure` is `crash`."""
    state = _as_board(board)
    lane_text = _ident(lane_id, missing="BAD_ID")
    card_text = _ident(card_id, missing="BAD_ID")
    interp, script_text = _argv(interpreter, script)
    fence_text = _fence(fence)
    moment = _clock(now)
    cred = _ident(credential_id, missing="MISSING_CRED")
    failure_text = _failure(failure)
    body = "|".join(
        (
            "R",
            lane_text,
            card_text,
            interp,
            script_text,
            fence_text,
            str(moment),
            cred,
            failure_text,
        )
    )
    built = rebuild(_chain(state.events, body))
    row = _latest(built, card_text)
    if row is None:
        raise Refuse("UNKNOWN_ASSIGNMENT")
    return built, row


def crash(
    board: object,
    assignment_id: object,
    *,
    fence: object,
    now: object,
) -> tuple[Board, Assignment]:
    """Record one crash and one requeue. A second crash on that claim refuses."""
    state = _as_board(board)
    ident = _ident(assignment_id, missing="BAD_ID")
    fence_text = _fence(fence)
    moment = _clock(now)
    body = "|".join(("C", ident, fence_text, str(moment)))
    built = rebuild(_chain(state.events, body))
    return built, _by_id(built, ident)


def terminate(
    board: object,
    assignment_id: object,
    action: object,
    *,
    fence: object,
    now: object,
) -> tuple[Board, Assignment]:
    """Record COMPLETE, REVIEW, or BLOCK. The action is not performed."""
    state = _as_board(board)
    ident = _ident(assignment_id, missing="BAD_ID")
    action_text = _action(action)
    fence_text = _fence(fence)
    moment = _clock(now)
    body = "|".join(("T", ident, action_text, fence_text, str(moment)))
    built = rebuild(_chain(state.events, body))
    return built, _by_id(built, ident)


def spawn(
    board: object,
    lane_id: object,
    card_id: object,
    *,
    now: object,
    credential_id: object,
) -> None:
    """Refuse. An assignment is not a process, and this does not start one."""
    state = _as_board(board)
    ident = _ident(lane_id, missing="BAD_ID")
    card = _ident(card_id, missing="BAD_ID")
    moment = _clock(now)
    cred = _ident(credential_id, missing="MISSING_CRED")
    lane = _lanes(state).get(ident)
    if lane is None:
        raise Refuse("UNKNOWN_LANE")
    if not const_eq(cred, lane.credential_id):
        raise Refuse("CRED_MISMATCH")
    found = _latest(state, card)
    if found is None or found.lane_id != ident:
        raise Refuse("UNKNOWN_ASSIGNMENT")
    if moment < state.at:
        raise Refuse("STALE")
    raise Refuse("NO_SPAWN")


def rebuild(events: object) -> Board:
    """Replay the event log. The public board matches, or this refuses."""
    rows = _event_rows(events)
    lanes, assignments, at = _replay(rows)
    return Board(lanes=lanes, assignments=assignments, events=rows, at=at, schema=SCHEMA)


__all__ = [
    "POLICY_WORKER_CAP",
    "RETRY_FAILURE",
    "SCHEMA",
    "Assignment",
    "Board",
    "Event",
    "Lane",
    "assign",
    "crash",
    "make_board",
    "make_lane",
    "rebuild",
    "retry",
    "spawn",
    "spec_argv",
    "terminate",
]
