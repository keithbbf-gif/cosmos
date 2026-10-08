"""Session questions and an inert checklist. A todo is stored and does not run."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import NoReturn, cast

from cosmos_hermes import Refuse, bound_int, bound_text, const_eq, secret_shape

SCHEMA = "cosmos-hermes-clarify_todo/1"
TODO_CAP = 32
QUESTION_CAP = 5
TEXT_LIMIT = 500
KINDS = frozenset({"plan", "shell"})

# A checklist line that asks for a shell stays a label. It is not argv.
_SHELL_ASK = re.compile(
    r"(?i)(?:"
    r"\b(?:run|exec|execute|invoke)\s+(?:an?\s+|the\s+)?(?:shell|bash|sh|zsh|cmd|powershell|pwsh)\b"
    r"|\b(?:bash|zsh|sh|powershell|pwsh|cmd(?:\.exe)?)\s+(?:-c|/c)\b"
    r"|\b(?:/bin/sh|/bin/bash|cmd\.exe)\b"
    r"|\|\s*(?:ba)?sh\b"
    r"|\|\s*(?:powershell|pwsh)\b"
    r")"
)


def _cap(requested: object, policy: int) -> int:
    if isinstance(requested, bool) or not isinstance(requested, int):
        raise Refuse("NOT_INT")
    if requested < 1:
        raise Refuse("BAD_LIMIT")
    if requested > policy:
        return policy
    return requested


def _line(value: object) -> str:
    text = bound_text(value, TEXT_LIMIT)
    if secret_shape(text):
        raise Refuse("SECRET")
    cleaned = text.strip()
    if cleaned == "":
        raise Refuse("EMPTY")
    return cleaned


def _kind(text: str, claimed: object) -> str:
    found = "shell" if _SHELL_ASK.search(text) is not None else "plan"
    if claimed == "":
        return found
    if not isinstance(claimed, str) or claimed not in KINDS or claimed != found:
        raise Refuse("BAD_KIND")
    return found


def _live_schema(value: object) -> None:
    if not isinstance(value, str) or len(value) != len(SCHEMA) or not const_eq(value, SCHEMA):
        raise Refuse("STALE")


def _with_done(item: Todo) -> Todo:
    clone = object.__new__(Todo)
    object.__setattr__(clone, "id", item.id)
    object.__setattr__(clone, "text", item.text)
    object.__setattr__(clone, "done", True)
    object.__setattr__(clone, "kind", item.kind)
    return clone


@dataclass(frozen=True, slots=True)
class Todo:
    """One checklist line. `done` is a flag. `kind` is a label, not a launch."""

    id: int
    text: str
    done: bool = False
    kind: str = ""

    def __post_init__(self) -> None:
        item_id = bound_int(self.id, 1, TODO_CAP)
        if not isinstance(self.done, bool):
            raise Refuse("BAD_LIST")
        text = _line(self.text)
        kind = _kind(text, self.kind)
        object.__setattr__(self, "id", item_id)
        object.__setattr__(self, "text", text)
        object.__setattr__(self, "kind", kind)


@dataclass(frozen=True, slots=True)
class TodoList:
    """Frozen items plus the recorded cap. The cap never rises above 32."""

    items: tuple[Todo, ...] = ()
    cap: int = TODO_CAP
    schema: str = SCHEMA

    def __post_init__(self) -> None:
        _live_schema(self.schema)
        recorded = _cap(self.cap, TODO_CAP)
        if not isinstance(self.items, tuple):
            raise Refuse("BAD_LIST")
        if len(self.items) > recorded:
            raise Refuse("TODO_CAP")
        seen: set[int] = set()
        expected = 1
        for item in self.items:
            if not isinstance(item, Todo):
                raise Refuse("BAD_LIST")
            if item.id in seen:
                raise Refuse("DUPLICATE")
            seen.add(item.id)
            if item.id != expected:
                raise Refuse("BAD_LIST")
            expected += 1
        object.__setattr__(self, "cap", recorded)


@dataclass(frozen=True, slots=True)
class Clarify:
    """A frozen batch of question text. The caller’s list is not kept."""

    questions: tuple[str, ...]
    cap: int

    def __post_init__(self) -> None:
        recorded = _cap(self.cap, QUESTION_CAP)
        if not isinstance(self.questions, tuple):
            raise Refuse("BAD_QUESTIONS")
        if len(self.questions) == 0:
            raise Refuse("NOTHING_TO_ASK")
        if len(self.questions) > recorded:
            raise Refuse("QUESTION_CAP")
        cleaned: list[str] = []
        for item in self.questions:
            cleaned.append(_line(item))
        object.__setattr__(self, "questions", tuple(cleaned))
        object.__setattr__(self, "cap", recorded)


@dataclass(frozen=True, slots=True)
class Record:
    """One emitted checklist row. Rebuild checks it again."""

    schema: str
    id: int
    text: str
    done: bool
    kind: str

    def __post_init__(self) -> None:
        _live_schema(self.schema)
        item_id = bound_int(self.id, 1, TODO_CAP)
        if not isinstance(self.done, bool):
            raise Refuse("BAD_LIST")
        text = _line(self.text)
        kind = _kind(text, self.kind)
        object.__setattr__(self, "id", item_id)
        object.__setattr__(self, "text", text)
        object.__setattr__(self, "kind", kind)


@dataclass(frozen=True, slots=True)
class Snapshot:
    """The emitted checklist. A foreign schema is stale."""

    schema: str
    cap: int
    items: tuple[Record, ...]

    def __post_init__(self) -> None:
        _live_schema(self.schema)
        recorded = _cap(self.cap, TODO_CAP)
        if not isinstance(self.items, tuple):
            raise Refuse("BAD_LIST")
        if len(self.items) > recorded:
            raise Refuse("TODO_CAP")
        seen: set[int] = set()
        expected = 1
        for item in self.items:
            if not isinstance(item, Record):
                raise Refuse("BAD_LIST")
            if item.id in seen:
                raise Refuse("DUPLICATE")
            seen.add(item.id)
            if item.id != expected:
                raise Refuse("BAD_LIST")
            expected += 1
        object.__setattr__(self, "cap", recorded)


def clarify(questions: object, requested_cap: object = QUESTION_CAP) -> Clarify:
    """Return a frozen copy of the questions. The batch size never rises above 5."""
    if isinstance(questions, list):
        raw: tuple[object, ...] = tuple(questions)
    elif isinstance(questions, tuple):
        raw = questions
    else:
        raise Refuse("BAD_QUESTIONS")
    if isinstance(requested_cap, bool) or not isinstance(requested_cap, int):
        raise Refuse("NOT_INT")
    return Clarify(questions=cast(tuple[str, ...], raw), cap=requested_cap)


def open_list(requested_cap: object = TODO_CAP) -> TodoList:
    """Return an empty list. A requested cap above 32 is recorded as 32."""
    return TodoList(items=(), cap=_cap(requested_cap, TODO_CAP))


def add_todo(
    text: object,
    todo_list: object = None,
    requested_cap: object = TODO_CAP,
) -> TodoList:
    """Append one open item. A supplied list keeps its cap."""
    if todo_list is None:
        current = open_list(requested_cap)
    else:
        current = _list(todo_list)
        _cap(requested_cap, TODO_CAP)
    if len(current.items) >= current.cap:
        _line(text)
        raise Refuse("TODO_CAP")
    item = Todo(id=len(current.items) + 1, text=cast(str, text), done=False)
    return TodoList(items=current.items + (item,), cap=current.cap)


def done(item_id: object, todo_list: object) -> TodoList:
    """Mark `item_id` done. A second call returns the same list."""
    current = _list(todo_list)
    if isinstance(item_id, bool) or not isinstance(item_id, int):
        raise Refuse("NOT_INT")
    updated: list[Todo] = []
    found = False
    for item in current.items:
        if item.id == item_id:
            found = True
            if item.done:
                return current
            updated.append(_with_done(item))
            continue
        updated.append(item)
    if not found:
        raise Refuse("UNKNOWN_TODO")
    return TodoList(items=tuple(updated), cap=current.cap)


def snapshot(todo_list: object) -> Snapshot:
    """Emit the checklist. The copy does not run a line."""
    current = _list(todo_list)
    rows = tuple(
        Record(schema=SCHEMA, id=item.id, text=item.text, done=item.done, kind=item.kind)
        for item in current.items
    )
    return Snapshot(schema=SCHEMA, cap=current.cap, items=rows)


def rebuild(payload: object) -> TodoList:
    """Restore a checklist from a snapshot."""
    if not isinstance(payload, Snapshot):
        raise Refuse("BAD_LIST")
    items = tuple(
        Todo(id=row.id, text=row.text, done=row.done, kind=row.kind) for row in payload.items
    )
    return TodoList(items=items, cap=payload.cap, schema=payload.schema)


def run(todo_list: object = None, item_id: object = None) -> NoReturn:
    """Refuse. Looking up a line does not run it."""
    if item_id is not None and todo_list is None:
        raise Refuse("BAD_LIST")
    if todo_list is not None:
        current = _list(todo_list)
        if item_id is not None:
            if isinstance(item_id, bool) or not isinstance(item_id, int):
                raise Refuse("NOT_INT")
            ids = {item.id for item in current.items}
            if item_id not in ids:
                raise Refuse("UNKNOWN_TODO")
    raise Refuse("NOT_A_TOOL")


def _list(todo_list: object) -> TodoList:
    if not isinstance(todo_list, TodoList):
        raise Refuse("BAD_LIST")
    return todo_list


__all__ = [
    "KINDS",
    "QUESTION_CAP",
    "SCHEMA",
    "TEXT_LIMIT",
    "TODO_CAP",
    "Clarify",
    "Record",
    "Snapshot",
    "Todo",
    "TodoList",
    "add_todo",
    "clarify",
    "done",
    "open_list",
    "rebuild",
    "run",
    "snapshot",
]
