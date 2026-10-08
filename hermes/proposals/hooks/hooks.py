"""Lifecycle hooks for the harness. Callers run injected callables inline.

A refusing hook latches. A result that names a tool outside the action
allowlist is a guard escape. The policy cap is 16. Lines commit only after
every selected hook admits, so a latch cannot leave a partial transcript.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from typing import cast

from cosmos_hermes import PathJail, Refuse, bound_int, bound_text, const_eq, redact, secret_shape

SCHEMA = "cosmos-hermes-hooks/1"
POLICY_CAP = 16
ALLOW_CAP = 32
TEXT_CAP = 500
NOTE_CAP = 500
ASK_CAP = 1_000_000
TRANSCRIPT_CAP = 256
STAMP_MAX = 4_000_000_000

POINTS: tuple[str, ...] = ("pre_tool", "post_tool", "stop", "gateway")
PLAN_TOOLS: tuple[str, ...] = ("read", "glob", "grep", "oracle")
GATEWAY_EVENTS: tuple[str, ...] = (
    "gateway:startup",
    "session:start",
    "session:end",
    "session:reset",
    "session:compress",
    "agent:start",
    "agent:step",
    "agent:end",
    "reaction:added",
    "reaction:removed",
)
COMMAND_WILDCARD = "command:*"
_COMMAND_PREFIX = "command:"

_NAME = re.compile(r"^[a-z][a-z0-9_-]{0,31}$")
_TOOL = re.compile(r"^[a-z][a-z0-9_]{0,31}$")
_CRED = re.compile(r"^[A-Za-z][A-Za-z0-9_.:-]{0,63}$")
_TOOL_MARK = re.compile(r"(?<![A-Za-z0-9_])tool:([a-z][a-z0-9_]{0,31})\b")
_POINT_SET = frozenset(POINTS)
_PLAN_SET = frozenset(PLAN_TOOLS)
_GATEWAY_SET = frozenset(GATEWAY_EVENTS)
_MODES = frozenset(("plan", "act"))
_TOOL_POINT_SET = frozenset(("pre_tool", "post_tool"))
_OUTCOME_KEYS = frozenset(("note", "tool_names"))
_KINDS: dict[str, frozenset[str]] = {
    "pre_tool": frozenset(("observe", "mutate")),
    "post_tool": frozenset(("observe",)),
    "stop": frozenset(("halt",)),
    "gateway": frozenset(("dispatch",)),
}


@dataclass(frozen=True, slots=True)
class Action:
    """One classified call. Fields are already bounded."""

    point: str
    kind: str
    mode: str
    event: str
    tool: str
    allowed: tuple[str, ...]
    text: str
    path: str
    stamp: int
    confirm: bool
    schema: str = SCHEMA


@dataclass(frozen=True, slots=True)
class Outcome:
    """What a hook may return besides None or Refuse."""

    note: str = ""
    tool_names: tuple[str, ...] = ()


HookFn = Callable[[Action], Outcome | Refuse | None]


@dataclass(frozen=True, slots=True)
class Line:
    """One admitted hook. The point keeps a pre pass distinct from a post pass."""

    point: str
    name: str
    tool: str
    note: str
    event: str
    stamp: int


@dataclass(frozen=True, slots=True)
class Verdict:
    """Admission record. A refusal is a Refuse, not a verdict."""

    schema: str
    point: str
    code: str
    ran: tuple[str, ...]
    cap: int
    asked_cap: int
    policy_cap: int
    tools: tuple[str, ...]
    notes: tuple[str, ...]
    path: str
    stamp: int
    event: str
    lines: tuple[Line, ...]


@dataclass(frozen=True, slots=True)
class Hook:
    """One registered callable. `events` is empty outside gateway."""

    name: str
    point: str
    events: tuple[str, ...]
    fn: HookFn = field(repr=False)
    exact: frozenset[str] = field(repr=False, compare=False)
    wild: bool = field(repr=False, compare=False)


def _text(value: object, limit: int) -> str:
    text = bound_text(value, limit)
    if secret_shape(text):
        raise Refuse("SECRET")
    return text


def _point(raw: object) -> str:
    text = _text(raw, 32)
    if text not in _POINT_SET:
        raise Refuse("UNKNOWN_POINT")
    return text


def _kind(raw: object, point: str) -> str:
    text = _text(raw, 32)
    kinds = _KINDS.get(point)
    if kinds is None or text not in kinds:
        raise Refuse("UNCLASSIFIED")
    return text


def _mode(raw: object) -> str:
    text = _text(raw, 16)
    if text not in _MODES:
        raise Refuse("UNKNOWN_MODE")
    return text


def _confirm(raw: object) -> bool:
    if not isinstance(raw, bool):
        raise Refuse("BAD_CONFIRM")
    return raw


def _hook_name(raw: object) -> str:
    text = _text(raw, 32)
    if _NAME.fullmatch(text) is None:
        raise Refuse("BAD_NAME")
    return text


def _tool_name(raw: object) -> str:
    text = _text(raw, 32)
    if _TOOL.fullmatch(text) is None:
        raise Refuse("BAD_TOOL")
    return text


def _require_tool(raw: object) -> str:
    if isinstance(raw, str) and raw == "":
        raise Refuse("MISSING_TOOL")
    return _tool_name(raw)


def _absent_tool(raw: object) -> str:
    text = _text(raw, 32)
    if text != "":
        raise Refuse("UNCLASSIFIED")
    return ""


def _line_tool(point: str, raw: object) -> str:
    if point in _TOOL_POINT_SET:
        return _require_tool(raw)
    return _absent_tool(raw)


def _valid_event(text: str) -> bool:
    if text in _GATEWAY_SET:
        return True
    if not text.startswith(_COMMAND_PREFIX):
        return False
    return _NAME.fullmatch(text[len(_COMMAND_PREFIX) :]) is not None


def _event_for(point: str, raw: object) -> str:
    text = _text(raw, 64)
    if point != "gateway":
        if text != "":
            raise Refuse("BAD_EVENTS")
        return ""
    if not _valid_event(text):
        raise Refuse("UNKNOWN_EVENT")
    return text


def _subscription(raw: object) -> str:
    text = _text(raw, 64)
    if text == COMMAND_WILDCARD:
        return text
    if not _valid_event(text):
        raise Refuse("UNKNOWN_EVENT")
    return text


def _as_rows(raw: object, code: str) -> tuple[object, ...] | list[object]:
    if isinstance(raw, str) or not isinstance(raw, (tuple, list)):
        raise Refuse(code)
    return raw


def _events(raw: object, point: str) -> tuple[str, ...]:
    rows = _as_rows(raw, "BAD_EVENTS")
    if len(rows) > ALLOW_CAP:
        raise Refuse("BAD_EVENTS")
    if point != "gateway":
        if len(rows) != 0:
            raise Refuse("BAD_EVENTS")
        return ()
    if len(rows) == 0:
        raise Refuse("EMPTY_EVENTS")
    chosen: list[str] = []
    seen: set[str] = set()
    for item in rows:
        name = _subscription(item)
        if name in seen:
            continue
        seen.add(name)
        chosen.append(name)
    return tuple(chosen)


def _event_index(events: tuple[str, ...]) -> tuple[frozenset[str], bool]:
    wild = COMMAND_WILDCARD in events
    if not wild:
        return frozenset(events), False
    return frozenset(item for item in events if item != COMMAND_WILDCARD), True


def _allowlist(raw: object, *, required: bool) -> tuple[str, ...]:
    rows = _as_rows(raw, "BAD_ALLOW")
    if required and len(rows) == 0:
        raise Refuse("EMPTY_ALLOW")
    if len(rows) > ALLOW_CAP:
        raise Refuse("BAD_ALLOW")
    chosen: list[str] = []
    seen: set[str] = set()
    for item in rows:
        name = _tool_name(item)
        if name in seen:
            continue
        seen.add(name)
        chosen.append(name)
    if required and len(chosen) == 0:
        raise Refuse("EMPTY_ALLOW")
    return tuple(chosen)


def _tools(
    point: str,
    mode: str,
    tool: object,
    allowed: object,
) -> tuple[str, tuple[str, ...]]:
    needs = point in _TOOL_POINT_SET
    names = _allowlist(allowed, required=needs)
    if not needs:
        return _absent_tool(tool), names
    granted = frozenset(names)
    if mode == "plan":
        for name in names:
            if name not in _PLAN_SET:
                raise Refuse("PLAN_MODE", name)
    chosen = _require_tool(tool)
    if chosen not in granted:
        raise Refuse("NOT_ALLOWED", chosen)
    if mode == "plan" and chosen not in _PLAN_SET:
        raise Refuse("PLAN_MODE", chosen)
    return chosen, names


def _credential(raw: object) -> str:
    if isinstance(raw, str) and raw == "":
        return ""
    text = _text(raw, 64)
    if _CRED.fullmatch(text) is None:
        raise Refuse("BAD_CRED")
    return text


def _resolve_path(raw: object, jail: object) -> str:
    text = _text(raw, 4096)
    if text == "":
        return ""
    if not isinstance(jail, PathJail):
        raise Refuse("NO_GRANT")
    return str(jail.contain(text))


def _lift(refused: Refuse) -> Refuse:
    detail = refused.detail
    if detail == "" or not secret_shape(detail):
        return refused
    scrubbed = redact(detail)
    if secret_shape(scrubbed):
        return Refuse(refused.code, "")
    return Refuse(refused.code, scrubbed)


def _scan_note(note: str, allowed: frozenset[str]) -> None:
    for mark in _TOOL_MARK.findall(note):
        if mark not in allowed:
            raise Refuse("GUARD_ESCAPE", mark)


def _clean_names(raw: object, allowed: frozenset[str]) -> tuple[str, ...]:
    if isinstance(raw, str) or not isinstance(raw, (tuple, list)):
        raise Refuse("BAD_RESULT", "tool_names")
    if len(raw) > ALLOW_CAP:
        raise Refuse("BAD_RESULT", "tool_names")
    chosen: list[str] = []
    for item in raw:
        name = _tool_name(item)
        if name not in allowed:
            raise Refuse("GUARD_ESCAPE", name)
        chosen.append(name)
    return tuple(chosen)


def _as_dict(result: object) -> dict[str, object] | None:
    if not isinstance(result, dict):
        return None
    mapped: dict[str, object] = {}
    for key, value in result.items():
        if not isinstance(key, str):
            raise Refuse("BAD_RESULT", "keys")
        mapped[key] = value
    return mapped


def _coerce(result: object, allowed: frozenset[str]) -> Outcome | None:
    if result is None:
        return None
    if isinstance(result, Outcome):
        note = _text(result.note, NOTE_CAP)
        _scan_note(note, allowed)
        return Outcome(note, _clean_names(result.tool_names, allowed))
    mapped = _as_dict(result)
    if mapped is None:
        raise Refuse("BAD_RESULT")
    for key in mapped:
        if key in _OUTCOME_KEYS:
            continue
        if _TOOL.fullmatch(key) is not None and key not in allowed:
            raise Refuse("GUARD_ESCAPE", key)
        raise Refuse("BAD_RESULT", "keys")
    note_raw = mapped.get("note", "")
    names_raw = mapped.get("tool_names", ())
    if not isinstance(note_raw, str):
        raise Refuse("BAD_RESULT", "note")
    note = _text(note_raw, NOTE_CAP)
    _scan_note(note, allowed)
    return Outcome(note, _clean_names(names_raw, allowed))


def _call(hook: Hook, action: Action) -> object:
    try:
        result: object = hook.fn(action)
    except Refuse as refused:
        return _lift(refused)
    except Exception:
        raise Refuse("HOOK_FAIL", hook.name) from None
    if isinstance(result, Refuse):
        return _lift(result)
    return result


def _subscribed(hook: Hook, event: str) -> bool:
    if event in hook.exact:
        return True
    return hook.wild and event.startswith(_COMMAND_PREFIX)


def _asked_cap(raw: object) -> int:
    if isinstance(raw, bool) or not isinstance(raw, int):
        raise Refuse("BAD_CAP")
    if raw < 1 or raw > ASK_CAP:
        raise Refuse("BAD_CAP")
    return raw


def _checked_line(raw: object) -> Line:
    if not isinstance(raw, Line):
        raise Refuse("BAD_RESULT")
    point = _point(raw.point)
    name = _hook_name(raw.name)
    tool = _line_tool(point, raw.tool)
    note = _text(raw.note, NOTE_CAP)
    event = _event_for(point, raw.event)
    stamp = bound_int(raw.stamp, 0, STAMP_MAX)
    return Line(point, name, tool, note, event, stamp)


def rebuild(lines: object) -> tuple[Line, ...]:
    """Validate an emitted transcript and return the same lines.

    An exact copy of a line is `DUPLICATE`. A stamp that moves backwards is
    `STALE`. Callables are not restored.
    """
    rows = _as_rows(lines, "BAD_RESULT")
    if len(rows) > TRANSCRIPT_CAP:
        raise Refuse("OVERSIZE", str(TRANSCRIPT_CAP))
    cleaned: list[Line] = []
    seen: set[Line] = set()
    previous = -1
    for row in rows:
        line = _checked_line(row)
        if line in seen:
            raise Refuse("DUPLICATE", line.name)
        if line.stamp < previous:
            raise Refuse("STALE")
        seen.add(line)
        cleaned.append(line)
        previous = line.stamp
    return tuple(cleaned)


def _refuse_disk(path: object) -> None:
    if isinstance(path, str):
        text = bound_text(path, 4096)
        if secret_shape(text):
            raise Refuse("SECRET")
    raise Refuse("IMPORT")


def load_from_path(path: object) -> None:
    """Refuse plugin and hook discovery from disk. The path is not opened."""
    _refuse_disk(path)


class Registry:
    """Ordered hooks. A higher cap request is recorded and ignored."""

    __slots__ = (
        "_asked",
        "_busy",
        "_by_name",
        "_by_point",
        "_cap",
        "_cred",
        "_hooks",
        "_lines",
    )

    _asked: int
    _cap: int
    _cred: str
    _hooks: list[Hook]
    _by_name: dict[str, Hook]
    _by_point: dict[str, list[Hook]]
    _lines: list[Line]
    _busy: bool

    def __init__(self, *, cap: object = POLICY_CAP, credential_id: object = "") -> None:
        self._asked = _asked_cap(cap)
        # Policy cap wins. A larger request is recorded and does not raise the ceiling.
        self._cap = POLICY_CAP if self._asked > POLICY_CAP else self._asked
        self._cred = _credential(credential_id)
        self._hooks = []
        self._by_name = {}
        self._by_point = {point: [] for point in POINTS}
        self._lines = []
        self._busy = False

    def __repr__(self) -> str:
        return f"Registry(cap={self._cap}, hooks={len(self._hooks)})"

    @property
    def cap(self) -> int:
        return self._cap

    @property
    def asked_cap(self) -> int:
        return self._asked

    @property
    def policy_cap(self) -> int:
        return POLICY_CAP

    @property
    def hooks(self) -> tuple[Hook, ...]:
        return tuple(self._hooks)

    def transcript(self) -> tuple[Line, ...]:
        """Admitted lines so far. A refused fire adds nothing."""
        return tuple(self._lines)

    def get(self, name: object) -> Hook:
        """Return the hook registered under `name`."""
        checked = _hook_name(name)
        found = self._by_name.get(checked)
        if found is None:
            raise Refuse("UNKNOWN_HOOK")
        return found

    def register(
        self,
        name: object,
        point: object,
        fn: object,
        *,
        events: object = (),
    ) -> Hook:
        """Register one callable. The next hook past the cap refuses."""
        if self._busy:
            raise Refuse("REENTER")
        hook_name = _hook_name(name)
        hook_point = _point(point)
        hook_events = _events(events, hook_point)
        if not callable(fn):
            raise Refuse("NOT_CALLABLE")
        if hook_name in self._by_name:
            raise Refuse("DUPLICATE", hook_name)
        if len(self._hooks) >= self._cap:
            raise Refuse("HOOK_CAP", str(self._cap))
        exact, wild = _event_index(hook_events)
        hook = Hook(
            name=hook_name,
            point=hook_point,
            events=hook_events,
            fn=cast(HookFn, fn),
            exact=exact,
            wild=wild,
        )
        self._hooks.append(hook)
        self._by_name[hook_name] = hook
        self._by_point[hook_point].append(hook)
        return hook

    def load_from_path(self, path: object) -> None:
        """Refuse disk discovery. Stored hooks stay as they are."""
        _refuse_disk(path)

    def fire(
        self,
        point: object,
        *,
        kind: object,
        mode: object,
        tool: object = "",
        allowed: object = (),
        event: object = "",
        text: object = "",
        path: object = "",
        jail: object = None,
        credential_id: object = "",
        stamp: object,
        confirm: object = False,
    ) -> Verdict:
        """Run matching hooks in registration order. A latch skips the rest."""
        if self._busy:
            raise Refuse("REENTER")
        self._busy = True
        try:
            return self._run(
                point,
                kind=kind,
                mode=mode,
                tool=tool,
                allowed=allowed,
                event=event,
                text=text,
                path=path,
                jail=jail,
                credential_id=credential_id,
                stamp=stamp,
                confirm=confirm,
            )
        finally:
            self._busy = False

    def _run(
        self,
        point: object,
        *,
        kind: object,
        mode: object,
        tool: object,
        allowed: object,
        event: object,
        text: object,
        path: object,
        jail: object,
        credential_id: object,
        stamp: object,
        confirm: object,
    ) -> Verdict:
        chosen = _point(point)
        action_kind = _kind(kind, chosen)
        action_mode = _mode(mode)
        action_stamp = bound_int(stamp, 0, STAMP_MAX)
        action_confirm = _confirm(confirm)
        body = _text(text, TEXT_CAP)
        action_event = _event_for(chosen, event)
        action_tool, names = _tools(chosen, action_mode, tool, allowed)
        self._match_cred(credential_id, required=chosen == "gateway")
        held = _resolve_path(path, jail)
        action = Action(
            point=chosen,
            kind=action_kind,
            mode=action_mode,
            event=action_event,
            tool=action_tool,
            allowed=names,
            text=body,
            path=held,
            stamp=action_stamp,
            confirm=action_confirm,
        )
        allowed_set = frozenset(names)
        ran: list[str] = []
        notes: list[str] = []
        built: list[Line] = []
        for hook in self._selected(chosen, action_event):
            note = self._apply(hook, action, allowed_set)
            ran.append(hook.name)
            if note != "":
                notes.append(note)
            built.append(
                Line(
                    point=chosen,
                    name=hook.name,
                    tool=action_tool,
                    note=note,
                    event=action_event,
                    stamp=action_stamp,
                )
            )
        # Commit only with the verdict. A latch above leaves the log unchanged.
        lines = tuple(built)
        verdict = Verdict(
            schema=SCHEMA,
            point=chosen,
            code="ADMIT",
            ran=tuple(ran),
            cap=self._cap,
            asked_cap=self._asked,
            policy_cap=POLICY_CAP,
            tools=names,
            notes=tuple(notes),
            path=held,
            stamp=action_stamp,
            event=action_event,
            lines=lines,
        )
        self._lines.extend(lines)
        return verdict

    def _selected(self, point: str, event: str) -> tuple[Hook, ...]:
        row = self._by_point.get(point)
        if row is None:
            raise Refuse("UNKNOWN_POINT")
        if point != "gateway":
            return tuple(row)
        return tuple(hook for hook in row if _subscribed(hook, event))

    def _apply(self, hook: Hook, action: Action, allowed: frozenset[str]) -> str:
        result = _call(hook, action)
        # CONFIRM is the only retried class, and only once.
        if isinstance(result, Refuse) and result.code == "CONFIRM" and not action.confirm:
            result = _call(hook, replace(action, confirm=True))
        if isinstance(result, Refuse):
            raise result
        outcome = _coerce(result, allowed)
        if outcome is None:
            return ""
        return outcome.note

    def _match_cred(self, raw: object, *, required: bool) -> None:
        got = _credential(raw)
        if required:
            if got == "" or self._cred == "":
                raise Refuse("MISSING_CRED")
            if not const_eq(got, self._cred):
                raise Refuse("CRED_MISMATCH")
            return
        if got == "" or self._cred == "":
            return
        if not const_eq(got, self._cred):
            raise Refuse("CRED_MISMATCH")


__all__ = [
    "ALLOW_CAP",
    "ASK_CAP",
    "COMMAND_WILDCARD",
    "GATEWAY_EVENTS",
    "NOTE_CAP",
    "PLAN_TOOLS",
    "POINTS",
    "POLICY_CAP",
    "SCHEMA",
    "TEXT_CAP",
    "TRANSCRIPT_CAP",
    "Action",
    "Hook",
    "HookFn",
    "Line",
    "Outcome",
    "Registry",
    "Verdict",
    "load_from_path",
    "rebuild",
]
