"""Session loop descriptors. One tick is one wakeup. Nothing here runs a prompt."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Final, Literal

from cosmos_hermes import Refuse, bound_int, bound_text, const_eq, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-loops/1"
POLICY_CAP: Final[int] = 8
MIN_INTERVAL_S: Final[int] = 30
SELF_FLOOR_S: Final[int] = 60
SELF_CEILING_S: Final[int] = 900
INTERVAL_CAP: Final[int] = 86_400

_REQUEST_HI: Final[int] = 1_000_000_000
_NAME: Final[int] = 200
_PROMPT: Final[int] = 2_000
_UNTIL: Final[int] = 500
_DIGEST: Final[int] = 128
_CTRL: Final[frozenset[str]] = frozenset(chr(code) for code in range(32))

StatusName = Literal["ACTIVE", "PAUSED", "STOPPED"]
KindName = Literal["FIXED", "SELF"]
StopName = Literal["", "LOOP_CAP", "LOOP_COMPLETE", "STOP", "UNTIL"]
VerdictName = Literal["ACHIEVED", "CONTINUE", "UNACHIEVABLE"]

_STATUSES: Final[dict[str, StatusName]] = {
    "ACTIVE": "ACTIVE",
    "PAUSED": "PAUSED",
    "STOPPED": "STOPPED",
}
_KINDS: Final[dict[str, KindName]] = {"FIXED": "FIXED", "SELF": "SELF"}
_STOPS: Final[dict[str, StopName]] = {
    "": "",
    "LOOP_CAP": "LOOP_CAP",
    "LOOP_COMPLETE": "LOOP_COMPLETE",
    "STOP": "STOP",
    "UNTIL": "UNTIL",
}
_VERDICTS: Final[dict[str, VerdictName]] = {
    "ACHIEVED": "ACHIEVED",
    "CONTINUE": "CONTINUE",
    "UNACHIEVABLE": "UNACHIEVABLE",
}


def _ladder(floor: int, ceiling: int) -> tuple[int, ...]:
    values: list[int] = []
    current = floor
    for _step in range(8):
        values.append(current)
        doubled = current * 2
        if doubled >= ceiling:
            if ceiling != current:
                values.append(ceiling)
            break
        current = doubled
    return tuple(values)


_SELF_LADDER: Final[tuple[int, ...]] = _ladder(SELF_FLOOR_S, SELF_CEILING_S)
_SELF_STEPS: Final[frozenset[int]] = frozenset(_SELF_LADDER)


def _bound(value: object, limit: int) -> str:
    text = bound_text(value, limit)
    if secret_shape(text):
        raise Refuse("SECRET")
    return text


def _shaped(text: str, *, bad: str) -> str:
    if text != text.strip() or any(char in _CTRL for char in text):
        raise Refuse(bad)
    return text


def _required(value: object, limit: int, *, empty: str, bad: str) -> str:
    text = _bound(value, limit)
    if text.strip() == "":
        raise Refuse(empty)
    return _shaped(text, bad=bad)


def _optional(value: object, limit: int, *, bad: str) -> str:
    text = _bound(value, limit)
    if text == "":
        return ""
    if text.strip() == "":
        raise Refuse(bad)
    return _shaped(text, bad=bad)


def _schema(value: object) -> str:
    if value != SCHEMA:
        raise Refuse("BAD_LOOP")
    return SCHEMA


def _requested(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("NOT_INT")
    if value == 0:
        raise Refuse("UNLIMITED")
    return bound_int(value, 1, _REQUEST_HI)


def _effective(requested: int, effective: object) -> int:
    enforced = bound_int(effective, 1, POLICY_CAP)
    ceiling = POLICY_CAP if requested > POLICY_CAP else requested
    if enforced != ceiling:
        raise Refuse("BAD_CAP")
    return enforced


def _cap(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value != POLICY_CAP:
        raise Refuse("BAD_CAP")
    return POLICY_CAP


def _ticks(value: object, effective: int) -> int:
    spent = bound_int(value, 0, POLICY_CAP)
    if spent > effective:
        raise Refuse("BAD_CAP")
    return spent


def _status_name(value: object) -> StatusName:
    if not isinstance(value, str):
        raise Refuse("BAD_STATUS")
    found = _STATUSES.get(value)
    if found is None:
        raise Refuse("BAD_STATUS")
    return found


def _kind(value: object) -> KindName:
    if not isinstance(value, str):
        raise Refuse("BAD_KIND")
    found = _KINDS.get(value)
    if found is None:
        raise Refuse("BAD_KIND")
    return found


def _stop(value: object) -> StopName:
    if not isinstance(value, str):
        raise Refuse("BAD_STATUS")
    found = _STOPS.get(value)
    if found is None:
        raise Refuse("BAD_STATUS")
    return found


def _verdict(value: object) -> VerdictName:
    label = _required(value, 32, empty="BAD_VERDICT", bad="BAD_VERDICT")
    found = _VERDICTS.get(label)
    if found is None:
        raise Refuse("BAD_VERDICT")
    return found


def _flag(value: object) -> bool:
    if not isinstance(value, bool):
        raise Refuse("NOT_BOOL")
    return value


def _consistent(
    status: StatusName,
    stop_reason: StopName,
    ticks: int,
    effective: int,
    goal_deferred: bool,
) -> None:
    if goal_deferred and status != "ACTIVE":
        raise Refuse("BAD_STATUS")
    if status == "ACTIVE":
        if stop_reason != "":
            raise Refuse("BAD_STATUS")
        return
    if status == "PAUSED":
        if stop_reason != "" and stop_reason != "UNTIL":
            raise Refuse("BAD_STATUS")
        return
    if stop_reason == "":
        raise Refuse("BAD_STATUS")
    if stop_reason == "LOOP_CAP" and ticks != effective:
        raise Refuse("BAD_CAP")


def _cadence(
    kind: KindName,
    requested_interval: object,
    interval_s: object,
    next_interval_s: object,
) -> None:
    if kind == "SELF":
        if requested_interval is not None:
            raise Refuse("BAD_CAP")
        bound_int(interval_s, SELF_FLOOR_S, SELF_FLOOR_S)
        nxt = bound_int(next_interval_s, SELF_FLOOR_S, SELF_CEILING_S)
        if nxt not in _SELF_STEPS:
            raise Refuse("BAD_CAP")
        return
    asked = bound_int(requested_interval, MIN_INTERVAL_S, INTERVAL_CAP)
    stored = bound_int(interval_s, MIN_INTERVAL_S, INTERVAL_CAP)
    nxt = bound_int(next_interval_s, MIN_INTERVAL_S, INTERVAL_CAP)
    if stored != asked or nxt != stored:
        raise Refuse("BAD_CAP")


def _backoff(current: int) -> int:
    doubled = current * 2
    if doubled > SELF_CEILING_S:
        return SELF_CEILING_S
    return doubled


def _vet(
    schema: object,
    name: object,
    prompt: object,
    requested: object,
    cap: object,
    effective: object,
    ticks: object,
    stop_reason: object,
    status: object,
    kind: object,
    requested_interval: object,
    interval_s: object,
    next_interval_s: object,
    until: object,
    last_digest: object,
    goal_deferred: object,
) -> None:
    _schema(schema)
    _required(name, _NAME, empty="EMPTY", bad="BAD_NAME")
    _required(prompt, _PROMPT, empty="EMPTY", bad="BAD_PROMPT")
    _optional(until, _UNTIL, bad="BAD_UNTIL")
    _optional(last_digest, _DIGEST, bad="BAD_DIGEST")
    asked = _requested(requested)
    _cap(cap)
    enforced = _effective(asked, effective)
    spent = _ticks(ticks, enforced)
    state = _status_name(status)
    reason = _stop(stop_reason)
    deferred = _flag(goal_deferred)
    _consistent(state, reason, spent, enforced, deferred)
    mode = _kind(kind)
    _cadence(mode, requested_interval, interval_s, next_interval_s)


@dataclass(frozen=True, slots=True)
class Loop:
    """One session loop. The clock that fires it lives outside this module."""

    schema: str
    name: str
    prompt: str
    requested: int
    cap: int
    effective: int
    ticks: int
    stop_reason: StopName
    status: StatusName
    kind: KindName
    requested_interval: int | None
    interval_s: int
    next_interval_s: int
    until: str
    last_digest: str
    goal_deferred: bool

    def __post_init__(self) -> None:
        _vet(
            self.schema,
            self.name,
            self.prompt,
            self.requested,
            self.cap,
            self.effective,
            self.ticks,
            self.stop_reason,
            self.status,
            self.kind,
            self.requested_interval,
            self.interval_s,
            self.next_interval_s,
            self.until,
            self.last_digest,
            self.goal_deferred,
        )

    def tick(self, *, goal_active: object = False) -> Loop:
        """Same record `tick` returns. This object is not changed."""
        return _advance(self, goal_active=goal_active)


@dataclass(frozen=True, slots=True)
class Snapshot:
    """Public fields of one loop. `rebuild` returns the loop they describe."""

    schema: str
    name: str
    prompt: str
    requested: int
    cap: int
    effective: int
    ticks: int
    stop_reason: StopName
    status: StatusName
    kind: KindName
    requested_interval: int | None
    interval_s: int
    next_interval_s: int
    until: str
    last_digest: str
    goal_deferred: bool

    def __post_init__(self) -> None:
        _vet(
            self.schema,
            self.name,
            self.prompt,
            self.requested,
            self.cap,
            self.effective,
            self.ticks,
            self.stop_reason,
            self.status,
            self.kind,
            self.requested_interval,
            self.interval_s,
            self.next_interval_s,
            self.until,
            self.last_digest,
            self.goal_deferred,
        )


@dataclass(frozen=True, slots=True)
class LoopStatus:
    """`/loop status` view. `next_interval_s` is a duration, not a timestamp."""

    schema: str
    name: str
    ticks: int
    requested: int
    cap: int
    effective: int
    remaining: int
    stop_reason: StopName
    status: StatusName
    kind: KindName
    interval_s: int
    next_interval_s: int
    goal_deferred: bool
    until: str

    def __post_init__(self) -> None:
        _schema(self.schema)
        _required(self.name, _NAME, empty="EMPTY", bad="BAD_NAME")
        asked = _requested(self.requested)
        _cap(self.cap)
        enforced = _effective(asked, self.effective)
        spent = _ticks(self.ticks, enforced)
        left = bound_int(self.remaining, 0, POLICY_CAP)
        if left != enforced - spent:
            raise Refuse("BAD_CAP")
        reason = _stop(self.stop_reason)
        state = _status_name(self.status)
        deferred = _flag(self.goal_deferred)
        _consistent(state, reason, spent, enforced, deferred)
        mode = _kind(self.kind)
        if mode == "SELF":
            _cadence(mode, None, self.interval_s, self.next_interval_s)
        else:
            _cadence(mode, self.interval_s, self.interval_s, self.next_interval_s)
        _optional(self.until, _UNTIL, bad="BAD_UNTIL")


@dataclass(frozen=True, slots=True)
class Board:
    """The one loop a session may hold."""

    loop: Loop | None

    def __post_init__(self) -> None:
        if self.loop is not None and not isinstance(self.loop, Loop):
            raise Refuse("BAD_BOARD")


class Capped(Refuse):
    """Tick that would pass `effective`. `loop.stop_reason` is `LOOP_CAP`."""

    loop: Loop

    def __init__(self, loop: Loop) -> None:
        if not isinstance(loop, Loop):
            raise Refuse("BAD_LOOP")
        if loop.status != "STOPPED" or loop.stop_reason != "LOOP_CAP":
            raise Refuse("BAD_STATUS")
        super().__init__("LOOP_CAP")
        self.loop = loop


def _loop(value: object) -> Loop:
    if not isinstance(value, Loop):
        raise Refuse("BAD_LOOP")
    return value


def _spawn(record: Loop | Snapshot) -> Loop:
    return Loop(
        schema=record.schema,
        name=record.name,
        prompt=record.prompt,
        requested=record.requested,
        cap=record.cap,
        effective=record.effective,
        ticks=record.ticks,
        stop_reason=record.stop_reason,
        status=record.status,
        kind=record.kind,
        requested_interval=record.requested_interval,
        interval_s=record.interval_s,
        next_interval_s=record.next_interval_s,
        until=record.until,
        last_digest=record.last_digest,
        goal_deferred=record.goal_deferred,
    )


def _active(value: object) -> Loop:
    current = _loop(value)
    if current.status == "STOPPED":
        raise Refuse("STOPPED")
    if current.status != "ACTIVE":
        raise Refuse("NOT_ACTIVE")
    return current


def _advance(loop: object, *, goal_active: object) -> Loop:
    current = _loop(loop)
    if current.status == "STOPPED":
        raise Refuse("STOPPED")
    if current.status == "PAUSED":
        raise Refuse("PAUSED")
    if not isinstance(goal_active, bool):
        raise Refuse("NOT_BOOL")
    if goal_active:
        if current.goal_deferred:
            return current
        return replace(current, goal_deferred=True)
    if current.ticks >= current.effective:
        stopped = replace(
            current,
            status="STOPPED",
            stop_reason="LOOP_CAP",
            goal_deferred=False,
        )
        raise Capped(stopped)
    return replace(current, ticks=current.ticks + 1, goal_deferred=False)


def define(
    name: object,
    max_iters: object,
    *,
    prompt: object = "",
    interval_s: object | None = None,
    until: object = "",
) -> Loop:
    """Return one loop. A `max_iters` above 8 is stored; `effective` stays 8.

    A fixed interval outside 30..86400 seconds raises `OUT_OF_RANGE`.
    `interval_s=None` selects the self-paced ladder.
    """
    chosen = _required(name, _NAME, empty="EMPTY", bad="BAD_NAME")
    asked = _requested(max_iters)
    enforced = POLICY_CAP if asked > POLICY_CAP else asked
    if prompt == "":
        chosen_prompt = chosen
    else:
        chosen_prompt = _required(prompt, _PROMPT, empty="EMPTY", bad="BAD_PROMPT")
    chosen_until = _optional(until, _UNTIL, bad="BAD_UNTIL")
    if interval_s is None:
        mode: KindName = "SELF"
        requested_interval: int | None = None
        stored = SELF_FLOOR_S
        nxt = SELF_FLOOR_S
    else:
        mode = "FIXED"
        requested_interval = bound_int(interval_s, MIN_INTERVAL_S, INTERVAL_CAP)
        stored = requested_interval
        nxt = stored
    return Loop(
        schema=SCHEMA,
        name=chosen,
        prompt=chosen_prompt,
        requested=asked,
        cap=POLICY_CAP,
        effective=enforced,
        ticks=0,
        stop_reason="",
        status="ACTIVE",
        kind=mode,
        requested_interval=requested_interval,
        interval_s=stored,
        next_interval_s=nxt,
        until=chosen_until,
        last_digest="",
        goal_deferred=False,
    )


def tick(loop: object, *, goal_active: object = False) -> Loop:
    """Increment `ticks` by one.

    The call that would pass `effective` raises `LOOP_CAP` and carries the
    stopped record on `Capped.loop`, with `stop_reason` set to `LOOP_CAP`.
    """
    return _advance(loop, goal_active=goal_active)


def pause(loop: object) -> Loop:
    """Stop firing and keep the loop."""
    current = _loop(loop)
    if current.status == "STOPPED":
        raise Refuse("STOPPED")
    if current.status != "ACTIVE":
        raise Refuse("NOT_ACTIVE")
    return replace(current, status="PAUSED", goal_deferred=False)


def interrupt(loop: object) -> Loop:
    """A cancelled wakeup pauses the loop."""
    return pause(loop)


def resume(loop: object) -> Loop:
    """Continue a paused loop. A stopped loop stays stopped."""
    current = _loop(loop)
    if current.status == "STOPPED":
        raise Refuse("STOPPED")
    if current.status != "PAUSED":
        raise Refuse("NOT_PAUSED")
    return replace(current, status="ACTIVE", stop_reason="", goal_deferred=False)


def stop(loop: object) -> Loop:
    """End the loop. `stop_reason` becomes `STOP`."""
    current = _loop(loop)
    if current.status == "STOPPED":
        raise Refuse("STOPPED")
    return replace(current, status="STOPPED", stop_reason="STOP", goal_deferred=False)


def complete(loop: object) -> Loop:
    """The agent finished. `stop_reason` becomes `LOOP_COMPLETE`."""
    current = _loop(loop)
    if current.status == "STOPPED":
        raise Refuse("STOPPED")
    return replace(current, status="STOPPED", stop_reason="LOOP_COMPLETE", goal_deferred=False)


def judge(loop: object, verdict: object) -> Loop:
    """Apply a caller verdict. This module does not score the until-text."""
    current = _active(loop)
    if current.until == "":
        raise Refuse("NO_UNTIL")
    label = _verdict(verdict)
    if label == "CONTINUE":
        return current
    if label == "ACHIEVED":
        return replace(current, status="STOPPED", stop_reason="UNTIL", goal_deferred=False)
    return replace(current, status="PAUSED", stop_reason="UNTIL", goal_deferred=False)


def note_reply(loop: object, digest: object) -> Loop:
    """Self-paced only. The same digest backs off. A new digest snaps to the floor."""
    current = _active(loop)
    if current.kind != "SELF":
        raise Refuse("NOT_SELF")
    text = _required(digest, _DIGEST, empty="EMPTY", bad="BAD_DIGEST")
    if current.last_digest != "" and const_eq(current.last_digest, text):
        nxt = _backoff(current.next_interval_s)
    else:
        nxt = SELF_FLOOR_S
    return replace(current, last_digest=text, next_interval_s=nxt, goal_deferred=False)


def status(loop: object) -> LoopStatus:
    """Return cadence, ticks, and the next interval. No clock is read."""
    current = _loop(loop)
    return LoopStatus(
        schema=SCHEMA,
        name=current.name,
        ticks=current.ticks,
        requested=current.requested,
        cap=current.cap,
        effective=current.effective,
        remaining=current.effective - current.ticks,
        stop_reason=current.stop_reason,
        status=current.status,
        kind=current.kind,
        interval_s=current.interval_s,
        next_interval_s=current.next_interval_s,
        goal_deferred=current.goal_deferred,
        until=current.until,
    )


def snapshot(loop: object) -> Snapshot:
    """Copy the public fields of one loop."""
    current = _loop(loop)
    return Snapshot(
        schema=current.schema,
        name=current.name,
        prompt=current.prompt,
        requested=current.requested,
        cap=current.cap,
        effective=current.effective,
        ticks=current.ticks,
        stop_reason=current.stop_reason,
        status=current.status,
        kind=current.kind,
        requested_interval=current.requested_interval,
        interval_s=current.interval_s,
        next_interval_s=current.next_interval_s,
        until=current.until,
        last_digest=current.last_digest,
        goal_deferred=current.goal_deferred,
    )


def rebuild(record: object) -> Loop:
    """Return the loop a snapshot or a loop describes. The result is a new object."""
    if isinstance(record, (Loop, Snapshot)):
        return _spawn(record)
    raise Refuse("BAD_LOOP")


def make_board() -> Board:
    """Return a session that holds no loop yet."""
    return Board(loop=None)


def install(holder: object, loop: object) -> Board:
    """Keep one loop. A later install replaces the earlier one."""
    if not isinstance(holder, Board):
        raise Refuse("BAD_BOARD")
    return Board(loop=_loop(loop))


def current(holder: object) -> Loop:
    """Return the session loop. An empty session refuses `EMPTY`."""
    if not isinstance(holder, Board):
        raise Refuse("BAD_BOARD")
    if holder.loop is None:
        raise Refuse("EMPTY")
    return holder.loop


__all__ = [
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
]
