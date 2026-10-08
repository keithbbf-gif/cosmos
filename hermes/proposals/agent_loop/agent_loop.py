"""Turn machine for one Hermes-shaped agent run.

Policy cap is 8. The driver is ``range``, not an open loop.
A named tool failure is handed back once. The same class again stops.
No network, socket, subprocess, thread, or clock.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Literal, cast

from cosmos_hermes import Refuse, bound_text, const_eq, redact, secret_shape
from cosmos_hermes.bounds import MAX_TEXT

SCHEMA = "cosmos-hermes-agent_loop/1"
POLICY_MAX_TURNS = 8
_MAX_REQUEST = 100_000
_GENESIS = "0" * 64
STATES: tuple[str, ...] = ("idle", "tool", "observe", "stop")
FAILURE_CLASSES: tuple[str, ...] = ("DENIED", "MISSING", "TIMEOUT", "TOOL_FAULT")

_RETRYABLE = frozenset(FAILURE_CLASSES)
_ROLES = frozenset(("user", "assistant", "tool"))
_FROM_MODEL = frozenset(
    {"BAD_TOOL", "DONE", "EMPTY", "INTERRUPTED", "NO_ALLOW", "SECRET", "UNKNOWN_TOOL"}
)
_FROM_TOOL = frozenset({"INTERRUPTED", "SECRET", "TOOL_LOOP", "UNCLASSIFIED"})
_RAISE_THROUGH = frozenset(
    {"BAD_LIMIT", "BAD_NOTE", "BAD_RECORD", "BAD_TOOL_RESULT", "NOT_INT", "NOT_TEXT", "NULL_BYTE", "OVERSIZE"}
)
_TOOL_MARK = "tool:"
_NAME = re.compile(r"[a-z][a-z0-9_]{0,31}\Z")
_CODE = re.compile(r"[A-Z0-9_]{2,40}\Z")
_HEX = re.compile(r"[0-9a-f]{64}\Z")

State = Literal["idle", "tool", "observe", "stop"]
Role = Literal["user", "assistant", "tool"]


@dataclass(frozen=True, slots=True)
class Policy:
    """Caller budget versus the policy cap. ``ignored`` means the request was above 8."""

    requested: int
    applied: int
    ignored: bool

    def __post_init__(self) -> None:
        if type(self.requested) is not int or type(self.applied) is not int or type(self.ignored) is not bool:
            raise Refuse("BAD_POLICY")
        if self.requested < 1 or self.requested > _MAX_REQUEST:
            raise Refuse("BAD_POLICY")
        expect = POLICY_MAX_TURNS if self.requested > POLICY_MAX_TURNS else self.requested
        if self.applied != expect or self.ignored != (self.requested > POLICY_MAX_TURNS):
            raise Refuse("BAD_POLICY")


@dataclass(frozen=True, slots=True)
class Note:
    """One transcript line. Tool args stay opaque text."""

    role: str
    text: str

    def __post_init__(self) -> None:
        if self.role not in _ROLES:
            raise Refuse("BAD_NOTE")
        bound_text(self.text)
        if secret_shape(self.text):
            raise Refuse("SECRET")


@dataclass(frozen=True, slots=True)
class ToolAsk:
    """One tool the sample named. ``args`` is not evaluated."""

    name: str
    args: str

    def __post_init__(self) -> None:
        if _NAME.fullmatch(self.name) is None:
            raise Refuse("BAD_TOOL")
        bound_text(self.args)
        if secret_shape(self.args):
            raise Refuse("SECRET")


@dataclass(frozen=True, slots=True)
class ToolResult:
    """A tool outcome the caller already produced. ``ok`` false carries an error code."""

    ok: bool
    code: str
    text: str

    def __post_init__(self) -> None:
        if type(self.ok) is not bool or type(self.code) is not str or type(self.text) is not str:
            raise Refuse("BAD_TOOL_RESULT")
        text = bound_text(self.text)
        if secret_shape(text):
            object.__setattr__(self, "ok", False)
            object.__setattr__(self, "code", "SECRET")
            object.__setattr__(self, "text", redact(text))
            return
        if self.ok:
            if self.code != "":
                raise Refuse("BAD_TOOL_RESULT")
            return
        if _CODE.fullmatch(self.code) is None:
            raise Refuse("BAD_TOOL_RESULT")


@dataclass(frozen=True, slots=True)
class Record:
    """One edge of the machine. ``code`` is empty while that edge is still open."""

    state: str
    turn: int
    code: str
    detail: str
    text: str
    prev: str
    sha: str

    def __post_init__(self) -> None:
        if self.state not in STATES:
            raise Refuse("BAD_RECORD")
        if type(self.turn) is not int or self.turn < 0 or self.turn > POLICY_MAX_TURNS:
            raise Refuse("BAD_RECORD")
        if type(self.code) is not str or type(self.detail) is not str or type(self.text) is not str:
            raise Refuse("BAD_RECORD")
        if self.code != "" and _CODE.fullmatch(self.code) is None:
            raise Refuse("BAD_RECORD")
        if len(self.detail) > 200 or _HEX.fullmatch(self.prev) is None or _HEX.fullmatch(self.sha) is None:
            raise Refuse("BAD_RECORD")
        bound_text(self.text)
        if secret_shape(self.detail) or secret_shape(self.text):
            raise Refuse("SECRET")


@dataclass(frozen=True, slots=True)
class Halt:
    """Terminal record. Two runs with the same samples produce equal halts."""

    schema: str
    state: State
    code: str
    turns: int
    policy: Policy
    text: str
    records: tuple[Record, ...]
    notes: tuple[Note, ...]


@dataclass(frozen=True, slots=True)
class Snapshot:
    """Public state of a machine. ``rebuild`` replays ``records`` back to this value."""

    schema: str
    state: str
    turn: int
    policy: Policy
    code: str
    text: str
    records: tuple[Record, ...]
    notes: tuple[Note, ...]
    seen: tuple[str, ...]
    latched: bool
    ask: str

    def __post_init__(self) -> None:
        if self.schema != SCHEMA or self.state not in STATES:
            raise Refuse("BAD_SNAPSHOT")
        if type(self.turn) is not int or self.turn < 0 or self.turn > POLICY_MAX_TURNS:
            raise Refuse("BAD_SNAPSHOT")
        if type(self.policy) is not Policy or type(self.latched) is not bool:
            raise Refuse("BAD_SNAPSHOT")
        if type(self.code) is not str or type(self.text) is not str or type(self.ask) is not str:
            raise Refuse("BAD_SNAPSHOT")
        if self.code != "" and _CODE.fullmatch(self.code) is None:
            raise Refuse("BAD_SNAPSHOT")
        if self.ask != "" and _NAME.fullmatch(self.ask) is None:
            raise Refuse("BAD_SNAPSHOT")
        bound_text(self.text)
        bound_text(self.ask, 32)
        if (
            type(self.records) is not tuple
            or type(self.notes) is not tuple
            or type(self.seen) is not tuple
        ):
            raise Refuse("BAD_SNAPSHOT")
        if any(type(item) is not Record for item in self.records):
            raise Refuse("BAD_SNAPSHOT")
        if any(type(item) is not Note for item in self.notes):
            raise Refuse("BAD_SNAPSHOT")
        if any(type(item) is not str or _CODE.fullmatch(item) is None for item in self.seen):
            raise Refuse("BAD_SNAPSHOT")


Model = Callable[[tuple[Note, ...]], str]


def clamp_turns(requested: object) -> Policy:
    """Record the caller budget. A request above 8 is ignored, not granted."""
    if type(requested) is not int:
        raise Refuse("NOT_INT")
    if requested < 1:
        raise Refuse("OUT_OF_RANGE", "1..")
    stored = _MAX_REQUEST if requested > _MAX_REQUEST else requested
    applied = POLICY_MAX_TURNS if stored > POLICY_MAX_TURNS else stored
    return Policy(stored, applied, stored > POLICY_MAX_TURNS)


def _link(prev: str, state: str, turn: int, code: str, detail: str, text: str) -> str:
    payload = "\n".join((prev, state, str(turn), code, detail, text))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _parse_tool(text: str) -> tuple[str, str] | None:
    """A first line of ``tool:<name>`` is one tool ask. Anything else is a final answer."""
    line, sep, rest = text.partition("\n")
    if line.endswith("\r"):
        line = line[:-1]
    if not line.startswith(_TOOL_MARK):
        return None
    if sep == "":
        rest = ""
    return line[len(_TOOL_MARK) :], rest


def _error_note(code: str, text: str) -> str:
    if text == "":
        return code
    prefix = code + "\n"
    room = MAX_TEXT - len(prefix)
    if len(text) <= room:
        return prefix + text
    return prefix + text[:room]


def _take_tools(tools: object) -> dict[str, Callable[[str], ToolResult]]:
    if tools is None:
        return {}
    if not isinstance(tools, Mapping):
        raise Refuse("BAD_TOOLS")
    cleaned: dict[str, Callable[[str], ToolResult]] = {}
    for key, value in tools.items():
        if type(key) is not str or _NAME.fullmatch(key) is None or not callable(value):
            raise Refuse("BAD_TOOL")
        cleaned[key] = cast(Callable[[str], ToolResult], value)
    return cleaned


def _last(items: list[str]) -> str:
    if len(items) == 0:
        raise Refuse("BROKEN_CHAIN")
    return items[len(items) - 1]


def _derive(snapshot: Snapshot) -> Snapshot:
    notes = snapshot.notes
    if len(notes) == 0:
        raise Refuse("BROKEN_CHAIN")
    assistants: list[str] = []
    tool_notes: list[str] = []
    for index, note in enumerate(notes):
        if secret_shape(note.text):
            raise Refuse("SECRET")
        if index == 0:
            if note.role != "user" or note.text.strip() == "":
                raise Refuse("BROKEN_CHAIN")
            continue
        if note.role == "assistant":
            assistants.append(note.text)
            continue
        if note.role == "tool":
            tool_notes.append(note.text)
            continue
        raise Refuse("BROKEN_CHAIN")
    state = "idle"
    turn = 0
    seen: list[str] = []
    seen_set: set[str] = set()
    code = ""
    final_text = ""
    ask = ""
    tool_rows: list[Record] = []
    observe_text: list[str] = []
    prev = _GENESIS
    for record in snapshot.records:
        expect = _link(prev, record.state, record.turn, record.code, record.detail, record.text)
        if record.prev != prev or not const_eq(expect, record.sha):
            raise Refuse("BROKEN_CHAIN")
        prev = record.sha
        if record.state == "tool":
            if state not in ("idle", "observe") or record.turn != turn + 1 or record.code != "":
                raise Refuse("BROKEN_CHAIN")
            if _NAME.fullmatch(record.detail) is None:
                raise Refuse("BROKEN_CHAIN")
            state = "tool"
            turn = record.turn
            ask = record.detail
            tool_rows.append(record)
            continue
        if record.state == "observe":
            if state != "tool" or record.turn != turn:
                raise Refuse("BROKEN_CHAIN")
            if record.code == "":
                pass
            elif record.code not in _RETRYABLE or record.code in seen_set:
                raise Refuse("BROKEN_CHAIN")
            else:
                seen_set.add(record.code)
                seen.append(record.code)
            state = "observe"
            ask = ""
            turn = record.turn
            observe_text.append(record.text)
            continue
        if record.state != "stop" or state == "stop":
            raise Refuse("BROKEN_CHAIN")
        if record.code == "MAX_TURNS":
            if state != "observe" or record.turn != turn:
                raise Refuse("BROKEN_CHAIN")
        elif state == "tool":
            if record.code not in _FROM_TOOL or record.turn != turn:
                raise Refuse("BROKEN_CHAIN")
        elif state in ("idle", "observe") and record.code in _FROM_MODEL and record.turn == turn + 1:
            pass
        else:
            raise Refuse("BROKEN_CHAIN")
        state = "stop"
        turn = record.turn
        code = record.code
        final_text = record.text
        ask = ""
    if state == "tool" and snapshot.latched:
        raise Refuse("BROKEN_CHAIN")
    if code == "INTERRUPTED" and not snapshot.latched:
        raise Refuse("STALE")
    extra = 1 if code == "DONE" else 0
    if len(assistants) != len(tool_rows) + extra:
        raise Refuse("BROKEN_CHAIN")
    if len(tool_notes) != len(observe_text) or tuple(tool_notes) != tuple(observe_text):
        raise Refuse("BROKEN_CHAIN")
    paired = assistants[:-1] if code == "DONE" else assistants
    if len(paired) != len(tool_rows):
        raise Refuse("BROKEN_CHAIN")
    for note_text, row in zip(paired, tool_rows, strict=True):
        parsed = _parse_tool(note_text)
        if parsed is None or parsed[0] != row.detail or parsed[1] != row.text:
            raise Refuse("BROKEN_CHAIN")
    if code == "DONE" and _last(assistants) != final_text:
        raise Refuse("BROKEN_CHAIN")
    if secret_shape(final_text):
        raise Refuse("SECRET")
    return Snapshot(
        schema=SCHEMA,
        state=state,
        turn=turn,
        policy=snapshot.policy,
        code=code,
        text=final_text,
        records=snapshot.records,
        notes=snapshot.notes,
        seen=tuple(seen),
        latched=snapshot.latched,
        ask=ask,
    )


def rebuild(snapshot: object) -> Snapshot:
    """Replay the record chain. The same public state comes back, or a refusal."""
    if type(snapshot) is not Snapshot:
        raise Refuse("BAD_SNAPSHOT")
    derived = _derive(snapshot)
    if derived != snapshot:
        raise Refuse("STALE")
    return derived


class AgentLoop:
    """Eight-turn machine. One confirming retry for a named failure class.

    The driver is ``range``, not an open loop. A ninth model step raises
    ``POLICY_CAP`` and writes nothing.
    """

    __slots__ = (
        "_allow",
        "_ask",
        "_final",
        "_head",
        "_latched",
        "_notes",
        "_policy",
        "_ran",
        "_records",
        "_seen",
        "_state",
        "_tools",
        "_turn",
    )

    def __init__(
        self,
        task: object,
        tools: object = None,
        requested_turns: object = POLICY_MAX_TURNS,
    ) -> None:
        policy = clamp_turns(requested_turns)
        task_text = bound_text(task)
        if task_text.strip() == "":
            raise Refuse("EMPTY_TASK")
        if secret_shape(task_text):
            raise Refuse("SECRET")
        table = _take_tools(tools)
        self._policy: Policy = policy
        self._tools: dict[str, Callable[[str], ToolResult]] = table
        self._allow: frozenset[str] = frozenset(table)
        self._state: State = "idle"
        self._turn: int = 0
        self._records: list[Record] = []
        self._notes: list[Note] = [Note("user", task_text)]
        self._seen: dict[str, None] = {}
        self._ask: ToolAsk | None = None
        self._latched: bool = False
        self._final: Record | None = None
        self._ran: bool = False
        self._head: str = _GENESIS

    def __repr__(self) -> str:
        return f"AgentLoop(state={self._state!r}, turn={self._turn}, applied={self._policy.applied})"

    @property
    def state(self) -> State:
        return self._state

    @property
    def policy(self) -> Policy:
        return self._policy

    @property
    def turn(self) -> int:
        return self._turn

    def transcript(self) -> tuple[Note, ...]:
        """History the next sample may see. The tuple is a snapshot."""
        return tuple(self._notes)

    def snapshot(self) -> Snapshot:
        """Frozen public state, including the record chain."""
        code = "" if self._final is None else self._final.code
        text = "" if self._final is None else self._final.text
        ask = "" if self._ask is None else self._ask.name
        return Snapshot(
            schema=SCHEMA,
            state=self._state,
            turn=self._turn,
            policy=self._policy,
            code=code,
            text=text,
            records=tuple(self._records),
            notes=tuple(self._notes),
            seen=tuple(self._seen),
            latched=self._latched,
            ask=ask,
        )

    def step(self, model_text: object = "", tool_result: object = None) -> Record:
        """Advance one edge. Model text is taken from idle or observe; a tool result from tool."""
        if self._state == "stop":
            raise Refuse("ALREADY_STOPPED")
        if self._state in ("idle", "observe"):
            if tool_result is not None:
                raise Refuse("BAD_STATE")
            return self._on_model(model_text)
        if tool_result is None:
            raise Refuse("NEED_TOOL_RESULT")
        if model_text != "":
            raise Refuse("BAD_STATE")
        return self._on_tool(tool_result)

    def interrupt(self) -> Record:
        """Stop before the pending tool. With no tool pending, latch the next one."""
        if self._state == "stop":
            raise Refuse("ALREADY_STOPPED")
        self._latched = True
        if self._state == "tool":
            return self._stop("INTERRUPTED", "before tool", checked=True)
        return self._token(self._state, "latched")

    def run(
        self,
        model: Model,
        *,
        before_tool: Callable[[ToolAsk], None] | None = None,
    ) -> Halt:
        """Sample ``model`` at most ``policy.applied`` times. A pending tool is optional."""
        phase = self._state
        if self._ran or self._turn != 0 or phase != "idle":
            raise Refuse("ALREADY_STOPPED" if phase == "stop" else "BAD_STATE")
        self._ran = True
        for _index in range(self._policy.applied):
            phase = self._state
            if phase == "stop":
                break
            if phase not in ("idle", "observe"):
                raise Refuse("BAD_STATE")
            self.step(model(self.transcript()))
            phase = self._state
            if phase != "tool":
                break
            if self._ask is None:
                raise Refuse("BAD_STATE")
            if before_tool is not None:
                before_tool(self._ask)
            phase = self._state
            if phase != "tool" or self._ask is None:
                break
            self._execute(self._ask)
            phase = self._state
            if phase == "stop":
                break
        else:
            phase = self._state
            if phase != "stop":
                self._stop("MAX_TURNS", str(self._policy.applied), checked=True)
        return self.halt()

    def halt(self) -> Halt:
        """The terminal record. Refuses when the machine has not stopped."""
        if self._final is None or self._state != "stop":
            raise Refuse("NOT_STOPPED")
        return Halt(
            schema=SCHEMA,
            state="stop",
            code=self._final.code,
            turns=self._turn,
            policy=self._policy,
            text=self._final.text,
            records=tuple(self._records),
            notes=tuple(self._notes),
        )

    def _on_model(self, model_text: object) -> Record:
        if self._turn >= self._policy.applied:
            if self._policy.applied >= POLICY_MAX_TURNS:
                raise Refuse("POLICY_CAP", str(POLICY_MAX_TURNS))
            return self._stop("MAX_TURNS", str(self._policy.applied), checked=True)
        text = bound_text(model_text)
        hidden = secret_shape(text)
        self._turn += 1
        if hidden:
            return self._stop("SECRET", redact(text), checked=True)
        if text.strip() == "":
            return self._stop("EMPTY", "", checked=True)
        parsed = _parse_tool(text)
        if parsed is None:
            note = Note("assistant", text)
            record = self._prepare("stop", "DONE", text, text)
            self._notes.append(note)
            return self._commit(record, "stop")
        name, args = parsed
        if self._latched:
            return self._stop("INTERRUPTED", "before tool", checked=True)
        if len(self._allow) == 0:
            return self._stop("NO_ALLOW", name, checked=True)
        if _NAME.fullmatch(name) is None:
            return self._stop("BAD_TOOL", name, checked=True)
        if name not in self._allow:
            return self._stop("UNKNOWN_TOOL", name, checked=True)
        ask = ToolAsk(name, args)
        note = Note("assistant", text)
        record = self._prepare("tool", "", name, args)
        self._notes.append(note)
        self._ask = ask
        return self._commit(record, "tool")

    def _on_tool(self, tool_result: object) -> Record:
        if type(tool_result) is not ToolResult or type(tool_result.ok) is not bool:
            raise Refuse("BAD_TOOL_RESULT")
        if tool_result.code == "SECRET":
            return self._stop("SECRET", tool_result.text, checked=True)
        if tool_result.ok:
            if tool_result.code != "":
                raise Refuse("BAD_TOOL_RESULT")
            note = Note("tool", tool_result.text)
            record = self._prepare("observe", "", "", tool_result.text)
            self._notes.append(note)
            self._ask = None
            return self._commit(record, "observe")
        if _CODE.fullmatch(tool_result.code) is None:
            raise Refuse("BAD_TOOL_RESULT")
        if tool_result.code not in _RETRYABLE:
            return self._stop("UNCLASSIFIED", tool_result.code, checked=True)
        if tool_result.code in self._seen:
            return self._stop("TOOL_LOOP", tool_result.code, checked=True)
        shown = _error_note(tool_result.code, tool_result.text)
        note = Note("tool", shown)
        record = self._prepare("observe", tool_result.code, tool_result.text, shown)
        self._seen[tool_result.code] = None
        self._notes.append(note)
        self._ask = None
        return self._commit(record, "observe")

    def _execute(self, ask: ToolAsk) -> Record:
        if self._state == "stop":
            raise Refuse("ALREADY_STOPPED")
        if self._latched or self._state != "tool":
            return self._stop("INTERRUPTED", "before tool", checked=True)
        fn = self._tools.get(ask.name)
        if fn is None:
            return self._stop("UNKNOWN_TOOL", ask.name, checked=True)
        try:
            outcome = fn(ask.args)
        except Refuse as exc:
            detail = exc.detail
            hidden = secret_shape(detail)
            if exc.code == "SECRET" or hidden:
                shown = redact(detail) if hidden else detail
                return self._stop("SECRET", shown, checked=True)
            if exc.code in _RAISE_THROUGH:
                raise
            outcome = ToolResult(False, exc.code, detail)
        except Exception as exc:
            outcome = ToolResult(False, "TOOL_FAULT", type(exc).__name__)
        return self.step("", outcome)

    def _prepare(self, state: str, code: str, detail: str, text: str) -> Record:
        short = detail if len(detail) <= 200 else detail[:200]
        digest = _link(self._head, state, self._turn, code, short, text)
        return Record(state, self._turn, code, short, text, self._head, digest)

    def _commit(self, record: Record, state: State) -> Record:
        self._records.append(record)
        self._head = record.sha
        if state == "stop":
            self._state = "stop"
            self._ask = None
            self._final = record
        else:
            self._state = state
        return record

    def _stop(self, code: str, detail: str, *, checked: bool) -> Record:
        if self._state == "stop":
            raise Refuse("ALREADY_STOPPED")
        if not checked and secret_shape(detail):
            detail = redact(detail)
            code = "SECRET"
        kept = detail if code in {"DONE", "SECRET"} else ""
        record = self._prepare("stop", code, detail, kept)
        return self._commit(record, "stop")

    def _token(self, state: str, detail: str) -> Record:
        digest = _link(self._head, state, self._turn, "", detail, "")
        return Record(state, self._turn, "", detail, "", self._head, digest)


def run(
    model: Model,
    *,
    task: object,
    tools: object = None,
    requested_turns: object = POLICY_MAX_TURNS,
    before_tool: Callable[[AgentLoop, ToolAsk], None] | None = None,
) -> Halt:
    """Open a machine and drive it from ``model``."""
    machine = AgentLoop(task, tools, requested_turns)
    if before_tool is None:
        return machine.run(model)
    hook: Callable[[AgentLoop, ToolAsk], None] = before_tool

    def _bridge(ask: ToolAsk) -> None:
        hook(machine, ask)

    return machine.run(model, before_tool=_bridge)


__all__ = [
    "FAILURE_CLASSES",
    "POLICY_MAX_TURNS",
    "SCHEMA",
    "STATES",
    "AgentLoop",
    "Halt",
    "Model",
    "Note",
    "Policy",
    "Record",
    "Role",
    "Snapshot",
    "State",
    "ToolAsk",
    "ToolResult",
    "clamp_turns",
    "rebuild",
    "run",
]
