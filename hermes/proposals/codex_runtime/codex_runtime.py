"""Argv descriptor for a Codex app-server role. This module does not start a process."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Final

from cosmos_hermes import Refuse, bound_int, bound_text, const_eq, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-codex_runtime/1"
EXTRA_CAP: Final[int] = 8
ARG_CAP: Final[int] = 256
MODEL_CAP: Final[int] = 128
FORBIDDEN_FLAGS: Final[tuple[str, ...]] = (
    "--danger-full-access",
    "--full-auto",
    "--ignore-user-config",
    "--approve-for-me",
)
JUDGE_SANDBOX: Final[str] = "read-only"
CODER_SANDBOX: Final[str] = "workspace-write"

_ARGV0: Final[str] = "codex"
_SUBCOMMAND: Final[str] = "app-server"
_SAFE_FLAG: Final[str] = "--color"
_SAFE_VALUE: Final[str] = "never"
_ROLE_CAP: Final[int] = 16
_WORKSPACE_CAP: Final[int] = 64
_REQUEST_HI: Final[int] = 1_000_000
_HARD_EXTRA: Final[int] = 64
_HEAD: Final[int] = 6
_ROLES: Final[frozenset[str]] = frozenset({"judge", "coder"})
_BANNED_NAMES: Final[frozenset[str]] = frozenset({"off", "yolo", "auto"})
_ALNUM: Final[frozenset[str]] = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
)
_NAME_CHARS: Final[frozenset[str]] = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
)
_MODEL_CHARS: Final[frozenset[str]] = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._:-"
)
_META: Final[frozenset[str]] = frozenset(
    (
        ";",
        "|",
        "&",
        "<",
        ">",
        "$",
        "`",
        "\\",
        '"',
        "'",
        "*",
        "?",
        "(",
        ")",
        "{",
        "}",
        "[",
        "]",
        "!",
        "#",
        "~",
    )
)
_CANON: Final[dict[str, str]] = {
    "--danger-full-access": "--danger-full-access",
    "--full-auto": "--full-auto",
    "--ignore-user-config": "--ignore-user-config",
    "--approve-for-me": "--approve-for-me",
    "--yolo": "--yolo",
    "--dangerously-bypass-approvals-and-sandbox": "--dangerously-bypass-approvals-and-sandbox",
    "danger-full-access": "--danger-full-access",
    ":danger-full-access": "--danger-full-access",
    "danger-no-sandbox": "--danger-full-access",
    ":danger-no-sandbox": "--danger-full-access",
}

__all__ = [
    "ARG_CAP",
    "CODER_SANDBOX",
    "EXTRA_CAP",
    "FORBIDDEN_FLAGS",
    "JUDGE_SANDBOX",
    "MODEL_CAP",
    "SCHEMA",
    "Plan",
    "argv_for",
    "plan",
    "rebuild",
    "run",
]


@dataclass(frozen=True, slots=True)
class Plan:
    """Frozen argv descriptor. Holding one does not start Codex."""

    argv: tuple[str, ...]
    role: str
    model: str
    workspace: str
    sandbox: str
    requested_extra_cap: int
    extra_cap: int
    policy_cap: int
    schema: str = SCHEMA

    def __post_init__(self) -> None:
        if not const_eq(self.schema, SCHEMA):
            raise Refuse("BAD_SCHEMA")
        _stored_caps(self.requested_extra_cap, self.extra_cap, self.policy_cap)
        role = _role(self.role)
        _workspace(self.workspace)
        _model(self.model)
        if _sandbox_for(role) != self.sandbox:
            raise Refuse("UNSANDBOXED")
        _match_argv(self.argv, self.model, self.sandbox, self.extra_cap)


def plan(
    role: object,
    model: object,
    extra: object = (),
    *,
    workspace: object = None,
    extra_cap: object = None,
) -> Plan:
    """Build one argv descriptor for a named workspace and model."""
    chosen = _role(role)
    picked = _model(model)
    named = _workspace(workspace)
    sandbox = _sandbox_for(chosen)
    tokens = _collect(extra)
    asked, applied = _resolve_cap(extra_cap)
    if len(tokens) > applied:
        raise Refuse("OVER_CAP", str(applied))
    accepted = _pairs(tokens)
    argv = (_ARGV0, _SUBCOMMAND, "-m", picked, "--sandbox", sandbox, *accepted)
    return Plan(
        argv=argv,
        role=chosen,
        model=picked,
        workspace=named,
        sandbox=sandbox,
        requested_extra_cap=asked,
        extra_cap=applied,
        policy_cap=EXTRA_CAP,
        schema=SCHEMA,
    )


def argv_for(
    role: object,
    model: object,
    extra: object = (),
    *,
    workspace: object = None,
    extra_cap: object = None,
) -> list[str]:
    """Return a new argv list. The process is not started."""
    return list(plan(role, model, extra, workspace=workspace, extra_cap=extra_cap).argv)


def rebuild(record: object) -> Plan:
    """Re-seal a plan. The same public fields yield an equal plan."""
    if type(record) is not Plan:
        raise Refuse("BAD_PLAN")
    sealed = Plan(
        argv=record.argv,
        role=record.role,
        model=record.model,
        workspace=record.workspace,
        sandbox=record.sandbox,
        requested_extra_cap=record.requested_extra_cap,
        extra_cap=record.extra_cap,
        policy_cap=record.policy_cap,
        schema=record.schema,
    )
    if sealed != record:
        raise Refuse("BAD_ARGV")
    return sealed


def run(descriptor: object) -> None:
    """Refuse to start Codex. A descriptor is not a process."""
    if type(descriptor) is Plan:
        rebuild(descriptor)
    raise Refuse("NOT_RUN")


def _stored_caps(requested: object, applied: object, policy: object) -> None:
    if type(requested) is not int or type(applied) is not int or type(policy) is not int:
        raise Refuse("NOT_INT")
    if requested < 0 or requested > _REQUEST_HI:
        raise Refuse("OUT_OF_RANGE", f"0..{_REQUEST_HI}")
    if policy != EXTRA_CAP or applied < 0 or applied > EXTRA_CAP or applied > requested:
        raise Refuse("BAD_LIMIT")


def _sandbox_for(role: str) -> str:
    if role == "judge":
        return JUDGE_SANDBOX
    if role == "coder":
        return CODER_SANDBOX
    raise Refuse("UNKNOWN_ROLE")


def _role(value: object) -> str:
    text = bound_text(value, _ROLE_CAP)
    if text == "":
        raise Refuse("UNKNOWN_ROLE")
    _edge(text)
    if text not in _ROLES:
        raise Refuse("UNKNOWN_ROLE")
    return text


def _workspace(value: object) -> str:
    if value is None:
        raise Refuse("BAD_WORKSPACE")
    text = bound_text(value, _WORKSPACE_CAP)
    if text == "":
        raise Refuse("BAD_WORKSPACE")
    _edge(text)
    if (
        text in _BANNED_NAMES
        or ".." in text
        or text[0] not in _ALNUM
        or not _chars_ok(text, _NAME_CHARS)
    ):
        raise Refuse("BAD_WORKSPACE")
    return text


def _model(value: object) -> str:
    text = bound_text(value, MODEL_CAP)
    if text == "":
        raise Refuse("EMPTY_MODEL")
    _edge(text)
    if ".." in text or text[0] not in _ALNUM:
        raise Refuse("BAD_MODEL")
    parts = text.split("/")
    for part in parts:
        if part == "" or part[0] not in _ALNUM or not _chars_ok(part, _MODEL_CHARS):
            raise Refuse("BAD_MODEL")
    return text


def _resolve_cap(requested: object) -> tuple[int, int]:
    if requested is None:
        return EXTRA_CAP, EXTRA_CAP
    asked = bound_int(requested, 0, _REQUEST_HI)
    applied = asked if asked < EXTRA_CAP else EXTRA_CAP
    return asked, applied


def _collect(extra: object) -> tuple[str, ...]:
    if isinstance(extra, str):
        return (_screen(bound_text(extra, ARG_CAP), "NOT_LIST"),)
    if isinstance(extra, (bytes, bytearray)) or not isinstance(extra, Sequence):
        raise Refuse("NOT_LIST")
    cleaned: list[str] = []
    for raw in extra:
        if len(cleaned) >= _HARD_EXTRA:
            raise Refuse("OVER_CAP", str(EXTRA_CAP))
        cleaned.append(_screen(bound_text(raw, ARG_CAP), "BAD_ARG"))
    return tuple(cleaned)


def _screen(text: str, space_code: str) -> str:
    if text == "":
        raise Refuse("EMPTY_ARG")
    _edge(text)
    if _bad_chars(text):
        raise Refuse(space_code)
    if ".." in text or not _chars_ok(text, _NAME_CHARS):
        raise Refuse("BAD_ARG")
    return text


def _edge(text: str) -> None:
    if secret_shape(text):
        raise Refuse("SECRET_SHAPE")
    if _has_meta(text):
        raise Refuse("SHELL_META")
    canon = _forbidden_canon(text)
    if canon != "":
        raise Refuse("FORBIDDEN", canon)


def _pairs(tokens: tuple[str, ...]) -> tuple[str, ...]:
    count = len(tokens)
    if count % 2 != 0:
        raise Refuse("UNCLASSIFIED")
    accepted: list[str] = []
    index = 0
    while index < count:
        flag = tokens[index]
        value = tokens[index + 1]
        if flag != _SAFE_FLAG or value != _SAFE_VALUE:
            raise Refuse("UNCLASSIFIED")
        accepted.append(flag)
        accepted.append(value)
        index += 2
    return tuple(accepted)


def _match_argv(argv: object, model: str, sandbox: str, applied: int) -> None:
    row = _tuple_row(argv)
    expected = (_ARGV0, _SUBCOMMAND, "-m", model, "--sandbox", sandbox)
    head: list[str] = []
    tail: list[str] = []
    for item in row:
        if type(item) is not str:
            raise Refuse("BAD_ARGV")
        if len(head) < _HEAD:
            head.append(item)
            continue
        if len(tail) >= _HARD_EXTRA:
            raise Refuse("OVER_CAP", str(EXTRA_CAP))
        tail.append(_screen(item, "BAD_ARG"))
    if len(head) != _HEAD:
        raise Refuse("BAD_ARGV")
    if len(tail) > applied or len(tail) > EXTRA_CAP:
        raise Refuse("OVER_CAP", str(applied))
    for index, want in enumerate(expected):
        if head[index] != want:
            raise Refuse("BAD_ARGV")
    _pairs(tuple(tail))


def _tuple_row(argv: object) -> tuple[object, ...]:
    if type(argv) is not tuple:
        raise Refuse("BAD_ARGV")
    items: list[object] = []
    for item in argv:
        items.append(item)
    return tuple(items)


def _chars_ok(text: str, allowed: frozenset[str]) -> bool:
    return all(ch in allowed for ch in text)


def _has_meta(text: str) -> bool:
    return any(ch in _META for ch in text)


def _bad_chars(text: str) -> bool:
    return any(ch.isspace() or ord(ch) < 32 or ord(ch) == 127 for ch in text)


def _forbidden_canon(text: str) -> str:
    folded = text.strip().lower()
    found = _piece(folded)
    if found != "":
        return found
    if not any(ch.isspace() for ch in folded):
        return ""
    for part in folded.split():
        found = _piece(part)
        if found != "":
            return found
    return ""


def _piece(piece: str) -> str:
    found = _CANON.get(piece, "")
    if found != "" or "=" not in piece:
        return found
    head, _, tail = piece.partition("=")
    found = _CANON.get(head, "")
    if found != "":
        return found
    return _CANON.get(tail, "")
