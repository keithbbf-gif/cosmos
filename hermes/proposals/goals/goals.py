"""Standing goals as records. The predicate id is a name, not code.

A goal stays open until the caller supplies evidence that names the predicate.
Missing evidence refuses. Nothing here compiles or calls the predicate.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, replace
from typing import Final

from cosmos_hermes import Refuse, bound_int, bound_text, const_eq, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-goals/1"
TURN_CAP: Final[int] = 20
TEXT_CAP: Final[int] = 4_000
ALLOW_CAP: Final[int] = 32
RETRY_FAILURE: Final[str] = "JUDGE_GAP"

_ASK_HI: Final[int] = 1_000_000
_NOW_MAX: Final[int] = 4_000_000_000
_PREDICATE_BOUND: Final[int] = 256
_ID: Final[re.Pattern[str]] = re.compile(r"^[a-z0-9_]{1,32}$")
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")
_MARK_RE: Final[re.Pattern[str]] = re.compile(
    "[\u200b\u200c\u200d\u2060\ufeff\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069]"
)
_DISABLE_RE: Final[re.Pattern[str]] = re.compile(r"disable\s+approval", re.IGNORECASE)
_TERMINALS: Final[frozenset[str]] = frozenset({"done", "refused"})
_STATES: Final[frozenset[str]] = frozenset({"open", "done", "refused"})


def _same(left: str, right: str) -> bool:
    return const_eq(left, right)


def _text(value: object, limit: int) -> str:
    text = bound_text(value, limit)
    if type(text) is not str:
        raise Refuse("NOT_TEXT")
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        raise Refuse("NOT_TEXT") from None
    return text


def _plain(text: str) -> str:
    return _MARK_RE.sub("", text)


def _guard_ready(text: str, plain: str) -> None:
    if secret_shape(text) or (plain != text and secret_shape(plain)):
        raise Refuse("GUARD_ESCAPE")
    if _DISABLE_RE.search(plain) is not None:
        raise Refuse("GUARD_ESCAPE")


def _guard(text: str) -> None:
    _guard_ready(text, _plain(text))


def _schema(value: object) -> None:
    token = _text(value, 64)
    if not _same(token, SCHEMA):
        raise Refuse("BAD_SCHEMA")


def _predicate(value: object) -> str:
    """Accept a short name. Parentheses and any other shape are not a predicate."""
    text = _text(value, _PREDICATE_BOUND)
    if "(" in text or _ID.fullmatch(text) is None:
        raise Refuse("BAD_PREDICATE")
    return text


def _body(value: object) -> str:
    text = _text(value, TEXT_CAP)
    plain = _plain(text)
    if plain.strip() == "":
        raise Refuse("EMPTY_GOAL")
    _guard_ready(text, plain)
    return text


def _reason(value: object) -> str:
    if value == "":
        return ""
    text = _text(value, TEXT_CAP)
    plain = _plain(text)
    if plain.strip() == "":
        return ""
    _guard_ready(text, plain)
    return text


def _policy(asked: object) -> Policy:
    value = bound_int(asked, 1, _ASK_HI)
    if value > TURN_CAP:
        return Policy(asked_turns=value, turn_cap=TURN_CAP, capped=True)
    return Policy(asked_turns=value, turn_cap=value, capped=False)


def _check_policy(policy: object) -> Policy:
    if not isinstance(policy, Policy):
        raise Refuse("BAD_POLICY")
    if isinstance(policy.asked_turns, bool) or not isinstance(policy.asked_turns, int):
        raise Refuse("NOT_INT")
    if isinstance(policy.turn_cap, bool) or not isinstance(policy.turn_cap, int):
        raise Refuse("NOT_INT")
    if type(policy.capped) is not bool:
        raise Refuse("BAD_POLICY")
    if policy.asked_turns < 1 or policy.asked_turns > _ASK_HI:
        raise Refuse("OUT_OF_RANGE", f"1..{_ASK_HI}")
    if policy.turn_cap < 1 or policy.turn_cap > TURN_CAP:
        raise Refuse("BAD_POLICY")
    if policy.asked_turns > TURN_CAP:
        if policy.turn_cap != TURN_CAP or policy.capped is not True:
            raise Refuse("BAD_POLICY")
    elif policy.turn_cap != policy.asked_turns or policy.capped is not False:
        raise Refuse("BAD_POLICY")
    return policy


def _moment(value: object, floor: int) -> int:
    if value is None:
        return floor
    moment = bound_int(value, 0, _NOW_MAX)
    if moment < floor:
        raise Refuse("CLOCK")
    return moment


def _allow(predicate_id: str, allow: object) -> None:
    if allow is None:
        return
    if isinstance(allow, (str, bytes, bytearray)) or not isinstance(allow, (list, tuple, set, frozenset)):
        raise Refuse("NOT_LIST")
    if len(allow) == 0:
        raise Refuse("EMPTY_ALLOW")
    if len(allow) > ALLOW_CAP:
        raise Refuse("OVERSIZE", str(ALLOW_CAP))
    seen: set[str] = set()
    for item in allow:
        name = _predicate(item)
        if name in seen:
            raise Refuse("DUPLICATE")
        seen.add(name)
    if predicate_id not in seen:
        raise Refuse("NOT_LISTED")


def _terminal(value: object) -> str:
    token = _text(value, 16)
    if token not in _TERMINALS:
        raise Refuse("BAD_STATUS")
    return token


def _state(value: object) -> str:
    token = _text(value, 16)
    if token not in _STATES:
        raise Refuse("BAD_STATUS")
    return token


def _stored_evidence(state: str, predicate_id: str, evidence_id: object) -> str:
    shown = _text(evidence_id, _PREDICATE_BOUND)
    if shown == "":
        if state == "done":
            raise Refuse("UNMET")
        return ""
    if state != "done":
        raise Refuse("BAD_EVIDENCE")
    ident = _predicate(shown)
    if not _same(ident, predicate_id):
        raise Refuse("UNMET")
    return ident


def _matched(expected: str, evidence: object) -> str:
    if evidence is None:
        raise Refuse("UNMET")
    if type(evidence) is Evidence:
        _schema(evidence.schema)
        if not _same(evidence.predicate_id, expected):
            raise Refuse("UNMET")
        return evidence.predicate_id
    if type(evidence) is not str:
        raise Refuse("BAD_EVIDENCE")
    name = _predicate(evidence)
    if not _same(name, expected):
        raise Refuse("UNMET")
    return name


def _canon(
    schema: str,
    text: str,
    predicate_id: str,
    state: str,
    turns_used: int,
    asked_turns: int,
    turn_cap: int,
    capped: bool,
    reason: str,
    created_at: int,
    updated_at: int,
    retries: int,
    evidence_id: str,
) -> str:
    parts = (
        schema,
        text,
        predicate_id,
        state,
        str(turns_used),
        str(asked_turns),
        str(turn_cap),
        "1" if capped else "0",
        reason,
        str(created_at),
        str(updated_at),
        str(retries),
        evidence_id,
    )
    return "\n".join(f"{len(part)}:{part}" for part in parts)


def _digest_hex(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _goal_canon(goal: Goal) -> str:
    return _canon(
        goal.schema,
        goal.text,
        goal.predicate_id,
        goal.state,
        goal.turns_used,
        goal.policy.asked_turns,
        goal.policy.turn_cap,
        goal.policy.capped,
        goal.reason,
        goal.created_at,
        goal.updated_at,
        goal.retries,
        goal.evidence_id,
    )


@dataclass(frozen=True, slots=True)
class Policy:
    """Asked turn budget and the budget that is actually enforced."""

    asked_turns: int
    turn_cap: int
    capped: bool


@dataclass(frozen=True, slots=True)
class Evidence:
    """Caller-supplied proof that one named predicate holds. Not executed."""

    schema: str
    predicate_id: str
    note: str

    def __post_init__(self) -> None:
        _schema(self.schema)
        _predicate(self.predicate_id)
        _reason(self.note)

    def __repr__(self) -> str:
        return f"Evidence(schema={self.schema!r}, predicate_id={self.predicate_id!r})"


@dataclass(frozen=True, slots=True)
class Continuation:
    """A later clock may feed this turn. This module does not run it."""

    schema: str
    predicate_id: str
    turn: int
    turn_cap: int
    note: str

    def __post_init__(self) -> None:
        _schema(self.schema)
        _predicate(self.predicate_id)
        cap = bound_int(self.turn_cap, 1, TURN_CAP)
        turn = bound_int(self.turn, 1, TURN_CAP)
        if turn > cap:
            raise Refuse("BUDGET")
        _reason(self.note)

    def __repr__(self) -> str:
        return (
            f"Continuation(schema={self.schema!r}, predicate_id={self.predicate_id!r}, "
            f"turn={self.turn!r}, turn_cap={self.turn_cap!r})"
        )


@dataclass(frozen=True, slots=True)
class Goal:
    """One standing goal. `predicate_id` is data. Nothing here calls it."""

    schema: str
    text: str
    predicate_id: str
    state: str
    turns_used: int
    policy: Policy
    reason: str
    created_at: int
    updated_at: int
    retries: int
    evidence_id: str

    def __post_init__(self) -> None:
        _schema(self.schema)
        predicate_id = _predicate(self.predicate_id)
        _body(self.text)
        _reason(self.reason)
        policy = _check_policy(self.policy)
        state = _state(self.state)
        _stored_evidence(state, predicate_id, self.evidence_id)
        bound_int(self.turns_used, 0, policy.turn_cap)
        bound_int(self.retries, 0, 1)
        created = bound_int(self.created_at, 0, _NOW_MAX)
        updated = bound_int(self.updated_at, 0, _NOW_MAX)
        if updated < created:
            raise Refuse("CLOCK")

    def status(self) -> str:
        """Return `open`, `done`, or `refused`."""
        return _state(self.state)

    def mark(
        self,
        verdict: object,
        now: object = None,
        *,
        reason: object = "",
        evidence: object = None,
    ) -> Goal:
        """Close an open goal. `done` requires evidence that names the predicate."""
        why = _reason(reason)
        chosen = _terminal(verdict)
        if not _same(self.state, "open"):
            raise Refuse("NOT_OPEN")
        if chosen == "done":
            evidence_id = _matched(self.predicate_id, evidence)
        else:
            if evidence is not None:
                raise Refuse("BAD_EVIDENCE")
            evidence_id = ""
        moment = _moment(now, self.updated_at)
        kept = why if why != "" else self.reason
        return replace(
            self,
            state=chosen,
            reason=kept,
            updated_at=moment,
            evidence_id=evidence_id,
        )

    def advance(self, now: object = None, *, note: object = "") -> tuple[Goal, Continuation]:
        """Record one continuation turn under the effective cap. Does not meet the goal."""
        extra = _reason(note)
        if not _same(self.state, "open"):
            raise Refuse("NOT_OPEN")
        if self.turns_used >= self.policy.turn_cap:
            raise Refuse("BUDGET")
        moment = _moment(now, self.updated_at)
        nxt = self.turns_used + 1
        kept = extra if extra != "" else self.reason
        goal = replace(self, turns_used=nxt, reason=kept, updated_at=moment)
        step = Continuation(
            schema=SCHEMA,
            predicate_id=self.predicate_id,
            turn=nxt,
            turn_cap=self.policy.turn_cap,
            note=extra,
        )
        return goal, step

    def gap(self, failure: object = None, now: object = None) -> Goal:
        """Confirm `JUDGE_GAP` once. The next gap raises `RETRY_CAP`. Not evidence."""
        if failure is None:
            code = RETRY_FAILURE
        else:
            code = _text(failure, 40)
            _guard(code)
        if not _same(code, RETRY_FAILURE):
            raise Refuse("UNCLASSIFIED")
        if not _same(self.state, "open"):
            raise Refuse("NOT_OPEN")
        if self.retries >= 1:
            raise Refuse("RETRY_CAP")
        moment = _moment(now, self.updated_at)
        return replace(self, retries=self.retries + 1, updated_at=moment)

    def __repr__(self) -> str:
        return (
            f"Goal(schema={self.schema!r}, predicate_id={self.predicate_id!r}, "
            f"state={self.state!r}, turns_used={self.turns_used!r}, "
            f"turn_cap={self.policy.turn_cap!r}, evidence_id={self.evidence_id!r})"
        )


@dataclass(frozen=True, slots=True)
class Record:
    """Ledger row for one goal. `rebuild` reproduces the public goal."""

    schema: str
    text: str
    predicate_id: str
    state: str
    turns_used: int
    asked_turns: int
    turn_cap: int
    capped: bool
    reason: str
    created_at: int
    updated_at: int
    retries: int
    evidence_id: str
    digest: str

    def __post_init__(self) -> None:
        goal = Goal(
            schema=self.schema,
            text=self.text,
            predicate_id=self.predicate_id,
            state=self.state,
            turns_used=self.turns_used,
            policy=Policy(
                asked_turns=self.asked_turns,
                turn_cap=self.turn_cap,
                capped=self.capped,
            ),
            reason=self.reason,
            created_at=self.created_at,
            updated_at=self.updated_at,
            retries=self.retries,
            evidence_id=self.evidence_id,
        )
        digest = _text(self.digest, 64)
        if _HEX.fullmatch(digest) is None:
            raise Refuse("CHAIN")
        if not _same(digest, _digest_hex(_goal_canon(goal))):
            raise Refuse("CHAIN")

    def __repr__(self) -> str:
        return (
            f"Record(schema={self.schema!r}, predicate_id={self.predicate_id!r}, "
            f"state={self.state!r}, evidence_id={self.evidence_id!r})"
        )


def create(
    text: object,
    predicate_id: object,
    now: object = None,
    *,
    max_turns: object = TURN_CAP,
    allow: object = None,
) -> Goal:
    """Store one open goal. `predicate_id` is kept as text and is never called."""
    ident = _predicate(predicate_id)
    _allow(ident, allow)
    body = _body(text)
    policy = _policy(max_turns)
    moment = _moment(now, 0)
    return Goal(
        schema=SCHEMA,
        text=body,
        predicate_id=ident,
        state="open",
        turns_used=0,
        policy=policy,
        reason="",
        created_at=moment,
        updated_at=moment,
        retries=0,
        evidence_id="",
    )


def prove(predicate_id: object, note: object = "") -> Evidence:
    """Name a predicate as evidence. The note is text and is never executed."""
    return Evidence(schema=SCHEMA, predicate_id=_predicate(predicate_id), note=_reason(note))


def emit(goal: object) -> Record:
    """Return the ledger row for `goal`. A non-goal raises `BAD_RECORD`."""
    if type(goal) is not Goal:
        raise Refuse("BAD_RECORD")
    return Record(
        schema=goal.schema,
        text=goal.text,
        predicate_id=goal.predicate_id,
        state=goal.state,
        turns_used=goal.turns_used,
        asked_turns=goal.policy.asked_turns,
        turn_cap=goal.policy.turn_cap,
        capped=goal.policy.capped,
        reason=goal.reason,
        created_at=goal.created_at,
        updated_at=goal.updated_at,
        retries=goal.retries,
        evidence_id=goal.evidence_id,
        digest=_digest_hex(_goal_canon(goal)),
    )


def rebuild(record: object) -> Goal:
    """Reproduce the goal from `emit`. A bad row raises `BAD_RECORD`."""
    if type(record) is not Record:
        raise Refuse("BAD_RECORD")
    return Goal(
        schema=record.schema,
        text=record.text,
        predicate_id=record.predicate_id,
        state=record.state,
        turns_used=record.turns_used,
        policy=Policy(
            asked_turns=record.asked_turns,
            turn_cap=record.turn_cap,
            capped=record.capped,
        ),
        reason=record.reason,
        created_at=record.created_at,
        updated_at=record.updated_at,
        retries=record.retries,
        evidence_id=record.evidence_id,
    )


__all__ = [
    "ALLOW_CAP",
    "RETRY_FAILURE",
    "SCHEMA",
    "TEXT_CAP",
    "TURN_CAP",
    "Continuation",
    "Evidence",
    "Goal",
    "Policy",
    "Record",
    "create",
    "emit",
    "prove",
    "rebuild",
]
