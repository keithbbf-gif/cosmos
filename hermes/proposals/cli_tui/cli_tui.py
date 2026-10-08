"""Slash descriptors for one composer.

`parse` returns a record. It does not read stdin, draw a screen, or run a command.
"""

from __future__ import annotations

from dataclasses import dataclass

from cosmos_hermes import Refuse, bound_int, bound_text, const_eq, secret_shape

SCHEMA = "cosmos-hermes-cli_tui/1"
HISTORY_CAP = 50
BUFFER_CAP = 32
LINE_CAP = 4_000
JOIN_CAP = BUFFER_CAP * LINE_CAP + (BUFFER_CAP - 1)
ASK_MAX = 1_000_000_000
INDEX_MAX = 10_000
EFFECT = "none"
COMMANDS = ("help", "tools", "model", "approval", "rollback", "interrupt")

_PAD = " \t"
_NAME_CHARS = frozenset("abcdefghijklmnopqrstuvwxyz0123456789_-")
_MODEL_CHARS = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._:/-@"
)
_DIGITS = frozenset("0123456789")
_APPROVAL = ("show", "manual")
_APPROVAL_SET = frozenset(_APPROVAL)
_COMMAND_SET = frozenset(COMMANDS)
_NO_ARG = frozenset(("help", "tools", "interrupt"))
_CANON = {name: name for name in COMMANDS}
_FAKE_SLASH = frozenset("\uff0f\u2215\u2044\u29f8")
_BAD_CHARS = frozenset(
    chr(code)
    for code in (
        *range(0x7F, 0xA0),
        0x061C,
        0x200B,
        0x200C,
        0x200D,
        0x200E,
        0x200F,
        0x2028,
        0x2029,
        0x202A,
        0x202B,
        0x202C,
        0x202D,
        0x202E,
        0x2060,
        0x2066,
        0x2067,
        0x2068,
        0x2069,
        0xFEFF,
    )
)

__all__ = [
    "ASK_MAX",
    "BUFFER_CAP",
    "COMMANDS",
    "EFFECT",
    "HISTORY_CAP",
    "INDEX_MAX",
    "JOIN_CAP",
    "LINE_CAP",
    "SCHEMA",
    "Buffer",
    "Descriptor",
    "HistoryItem",
    "Interrupt",
    "Plain",
    "Policy",
    "Session",
    "Transcript",
    "parse",
    "rebuild",
    "restore",
]


def _flag(value: object) -> bool:
    if value is True:
        return True
    if value is False:
        return False
    raise Refuse("BAD_FLAG")


def _whole(value: object, lo: int, hi: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < lo or value > hi:
        raise Refuse("BAD_LIMIT")
    return value


def _secrets(text: str) -> None:
    if secret_shape(text):
        raise Refuse("SECRET")
    if "\n" not in text:
        return
    # The composer inserts the newline. The second look is the joined key.
    if secret_shape(text.replace("\n", "")):
        raise Refuse("SECRET")


def _controls(text: str) -> None:
    for char in text:
        code = ord(char)
        if code < 32:
            if char != "\t":
                raise Refuse("BAD_LINE")
        elif code >= 0x7F and char in _BAD_CHARS:
            raise Refuse("BAD_LINE")


def _one_line(value: object) -> str:
    text = bound_text(value, LINE_CAP)
    _controls(text)
    _secrets(text)
    return text


def _stored(text: str, *, slash: bool) -> str:
    raw = bound_text(text, JOIN_CAP)
    parts = raw.split("\n")
    if slash and len(parts) != 1:
        raise Refuse("BAD_LINE")
    if len(parts) > BUFFER_CAP:
        raise Refuse("BUFFER_FULL")
    for part in parts:
        if len(part) > LINE_CAP:
            raise Refuse("OVERSIZE", str(LINE_CAP))
        _controls(part)
    _secrets(raw)
    return raw


def _split(body: str) -> tuple[str, ...]:
    parts: list[str] = []
    current: list[str] = []
    for char in body:
        if char in _PAD:
            if current:
                parts.append("".join(current))
                current = []
            continue
        current.append(char)
    if current:
        parts.append("".join(current))
    return tuple(parts)


def _command(token: str) -> str:
    folded = token.casefold()
    if folded == "" or any(char not in _NAME_CHARS for char in folded):
        raise Refuse("UNKNOWN_COMMAND")
    found = _CANON.get(folded)
    if found is None or not const_eq(folded, found):
        detail = folded if len(folded) <= 32 else ""
        raise Refuse("UNKNOWN_COMMAND", detail)
    return found


def _detail(token: str) -> str:
    if len(token) <= 32 and all(char in _NAME_CHARS for char in token):
        return token
    return ""


def _model_arg(token: str) -> str:
    if token == "" or len(token) > 128 or any(char not in _MODEL_CHARS for char in token):
        raise Refuse("BAD_ARGS")
    return token


def _approval_arg(token: str) -> str:
    mode = token.casefold()
    if mode not in _APPROVAL_SET:
        raise Refuse("BAD_MODE", _detail(mode))
    for item in _APPROVAL:
        if const_eq(mode, item):
            return item
    raise Refuse("BAD_MODE", _detail(mode))


def _index(token: str) -> int:
    if token == "" or len(token) > 6 or any(char not in _DIGITS for char in token):
        raise Refuse("BAD_INDEX")
    number = int(token)
    if number < 1:
        raise Refuse("BAD_INDEX")
    return bound_int(number, 1, INDEX_MAX)


def _available(value: object) -> int | None:
    if value is None:
        return None
    return bound_int(value, 0, INDEX_MAX)


def _resolve(asked: object, ceiling: int) -> tuple[int, int, bool]:
    if asked is None:
        return ceiling, ceiling, False
    if isinstance(asked, bool) or not isinstance(asked, int) or asked < 1 or asked > ASK_MAX:
        raise Refuse("BAD_LIMIT")
    if asked > ceiling:
        return ceiling, asked, True
    return asked, asked, False


def _pair(value: object) -> tuple[str, ...]:
    if not isinstance(value, tuple) or any(not isinstance(item, str) for item in value):
        raise Refuse("BAD_ARGS")
    return value


def _agree(text: str, name: str) -> None:
    found = parse(text)
    if not isinstance(found, Descriptor) or found.name != name:
        raise Refuse("BAD_KIND")


@dataclass(frozen=True, slots=True)
class Policy:
    """Caps in force. A higher ask is stored and is not applied."""

    schema: str
    history_cap: int
    asked_history_cap: int
    history_capped: bool
    buffer_cap: int
    asked_buffer_cap: int
    buffer_capped: bool

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        history_cap = _whole(self.history_cap, 1, HISTORY_CAP)
        asked_history = _whole(self.asked_history_cap, 1, ASK_MAX)
        buffer_cap = _whole(self.buffer_cap, 1, BUFFER_CAP)
        asked_buffer = _whole(self.asked_buffer_cap, 1, ASK_MAX)
        history_capped = _flag(self.history_capped)
        buffer_capped = _flag(self.buffer_capped)
        if history_cap != min(asked_history, HISTORY_CAP) or buffer_cap != min(asked_buffer, BUFFER_CAP):
            raise Refuse("BAD_LIMIT")
        if history_capped is not (asked_history > HISTORY_CAP):
            raise Refuse("BAD_LIMIT")
        if buffer_capped is not (asked_buffer > BUFFER_CAP):
            raise Refuse("BAD_LIMIT")


@dataclass(frozen=True, slots=True)
class Descriptor:
    """One slash command. `effect` is `none` because nothing has run."""

    schema: str
    name: str
    args: tuple[str, ...]
    index: int | None
    catalog: tuple[str, ...]
    effect: str

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        if not isinstance(self.effect, str) or self.effect != EFFECT:
            raise Refuse("BAD_EFFECT")
        if not isinstance(self.name, str):
            raise Refuse("NOT_TEXT")
        if self.name not in _COMMAND_SET:
            raise Refuse("UNKNOWN_COMMAND")
        args = _pair(self.args)
        catalog = _pair(self.catalog)
        for arg in args:
            bound_text(arg, LINE_CAP)
            _controls(arg)
            _secrets(arg)
        expected = COMMANDS if self.name == "help" else ()
        if catalog != expected:
            raise Refuse("BAD_ARGS")
        if self.name in _NO_ARG:
            if args != () or self.index is not None:
                raise Refuse("BAD_ARGS")
            return
        if self.name == "model":
            if self.index is not None or len(args) > 1:
                raise Refuse("BAD_ARGS")
            if len(args) == 1:
                _model_arg(args[0])
            return
        if self.name == "approval":
            if self.index is not None or len(args) > 1:
                raise Refuse("BAD_ARGS")
            if len(args) == 1:
                canonical = _approval_arg(args[0])
                if args[0] != canonical:
                    raise Refuse("BAD_ARGS")
            return
        _check_rollback(args, self.index)


def _check_rollback(args: tuple[str, ...], index: int | None) -> None:
    if len(args) > 1:
        raise Refuse("BAD_ARGS")
    if index is None:
        if args != ():
            raise Refuse("BAD_INDEX")
        return
    if isinstance(index, bool) or type(index) is not int:
        raise Refuse("BAD_INDEX")
    held = bound_int(index, 1, INDEX_MAX)
    if args != (str(held),):
        raise Refuse("BAD_INDEX")


@dataclass(frozen=True, slots=True)
class Plain:
    """A non-slash line, or a flushed multiline buffer. It has no command name."""

    schema: str
    text: str
    kind: str

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        if self.kind != "text":
            raise Refuse("BAD_KIND")
        _stored(self.text, slash=False)


@dataclass(frozen=True, slots=True)
class HistoryItem:
    """One accepted line. The oldest item drops after the history cap."""

    schema: str
    kind: str
    text: str
    name: str

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        if self.kind not in ("slash", "text"):
            raise Refuse("BAD_KIND")
        _stored(self.text, slash=self.kind == "slash")
        bound_text(self.name, LINE_CAP)
        _controls(self.name)
        _secrets(self.name)
        if self.kind == "text":
            if self.name != "":
                raise Refuse("BAD_KIND")
            return
        if self.name not in _COMMAND_SET:
            raise Refuse("UNKNOWN_COMMAND")
        _agree(self.text, self.name)


@dataclass(frozen=True, slots=True)
class Buffer:
    """Multiline composer snapshot. Lines are text, not commands."""

    schema: str
    lines: tuple[str, ...]
    text: str
    count: int
    cap: int
    policy_cap: int
    asked_cap: int
    capped: bool

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        if self.policy_cap != BUFFER_CAP:
            raise Refuse("BAD_LIMIT")
        capped = _flag(self.capped)
        count = _whole(self.count, 0, BUFFER_CAP)
        cap = _whole(self.cap, 1, BUFFER_CAP)
        asked = _whole(self.asked_cap, 1, ASK_MAX)
        if cap != min(asked, BUFFER_CAP) or capped is not (asked > BUFFER_CAP):
            raise Refuse("BAD_LIMIT")
        if not isinstance(self.lines, tuple):
            raise Refuse("BAD_KIND")
        if count != len(self.lines):
            raise Refuse("BAD_KIND")
        if count > cap:
            raise Refuse("BUFFER_FULL")
        for line in self.lines:
            _one_line(line)
        joined = "\n".join(self.lines)
        if self.text != joined:
            raise Refuse("BAD_KIND")
        _secrets(joined)


@dataclass(frozen=True, slots=True)
class Interrupt:
    """The flag `interrupt` sets. Parsing `/interrupt` does not build this."""

    schema: str
    flagged: bool

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        if _flag(self.flagged) is not True:
            raise Refuse("BAD_FLAG")


@dataclass(frozen=True, slots=True)
class Transcript:
    """Public composer state. `rebuild` returns an equal transcript."""

    schema: str
    policy: Policy
    history: tuple[HistoryItem, ...]
    lines: tuple[str, ...]
    interrupted: bool
    misses: int

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        if not isinstance(self.policy, Policy):
            raise Refuse("BAD_SCHEMA")
        policy = Policy(
            self.policy.schema,
            self.policy.history_cap,
            self.policy.asked_history_cap,
            self.policy.history_capped,
            self.policy.buffer_cap,
            self.policy.asked_buffer_cap,
            self.policy.buffer_capped,
        )
        interrupted = _flag(self.interrupted)
        if isinstance(self.misses, bool) or not isinstance(self.misses, int) or self.misses not in (0, 1):
            raise Refuse("BAD_LIMIT")
        if not isinstance(self.history, tuple) or not isinstance(self.lines, tuple):
            raise Refuse("BAD_KIND")
        if len(self.history) > policy.history_cap:
            raise Refuse("BAD_LIMIT")
        if len(self.lines) > policy.buffer_cap:
            raise Refuse("BUFFER_FULL")
        checked: list[HistoryItem] = []
        for item in self.history:
            if not isinstance(item, HistoryItem):
                raise Refuse("BAD_KIND")
            checked.append(HistoryItem(item.schema, item.kind, item.text, item.name))
        held: list[str] = []
        for line in self.lines:
            held.append(_one_line(line))
        _secrets("\n".join(held))
        if tuple(checked) != self.history or tuple(held) != self.lines or interrupted is not self.interrupted:
            raise Refuse("BAD_KIND")


def _descriptor(
    name: str,
    args: tuple[str, ...] = (),
    index: int | None = None,
) -> Descriptor:
    catalog = COMMANDS if name == "help" else ()
    return Descriptor(SCHEMA, name, args, index, catalog, EFFECT)


def _dispatch(name: str, args: tuple[str, ...], checkpoints: object) -> Descriptor:
    if name in _NO_ARG:
        if len(args) != 0:
            raise Refuse("BAD_ARGS")
        return _descriptor(name)
    if name == "model":
        if len(args) > 1:
            raise Refuse("BAD_ARGS")
        if len(args) == 1:
            _model_arg(args[0])
        return _descriptor(name, args)
    if name == "approval":
        if len(args) > 1:
            raise Refuse("BAD_ARGS")
        held = (_approval_arg(args[0]),) if len(args) == 1 else ()
        return _descriptor(name, held)
    if len(args) > 1:
        raise Refuse("BAD_ARGS")
    if len(args) == 0:
        return _descriptor("rollback")
    index = _index(args[0])
    available = _available(checkpoints)
    if available is not None and index > available:
        raise Refuse("ROLLBACK_MISS", str(index))
    return _descriptor("rollback", (str(index),), index)


def parse(line: object, *, checkpoints: object = None) -> Descriptor | Plain:
    """Classify one line. This does not touch history, the buffer, or the flag."""
    text = _one_line(line)
    stripped = text.strip(_PAD)
    if stripped[:1] in _FAKE_SLASH:
        raise Refuse("BAD_LINE")
    if stripped == "" or not stripped.startswith("/"):
        return Plain(SCHEMA, text, "text")
    if stripped == "/" or stripped.startswith("/ ") or stripped.startswith("/\t"):
        raise Refuse("UNKNOWN_COMMAND")
    parts = _split(stripped[1:])
    if len(parts) == 0:
        raise Refuse("UNKNOWN_COMMAND")
    return _dispatch(_command(parts[0]), parts[1:], checkpoints)


class Session:
    """One composer. Records stay in memory. Descriptors do not execute."""

    __slots__ = ("_policy", "_history", "_lines", "_flag", "_misses")

    def __init__(self, history_cap: object = None, buffer_cap: object = None) -> None:
        history_applied, history_asked, history_capped = _resolve(history_cap, HISTORY_CAP)
        buffer_applied, buffer_asked, buffer_capped = _resolve(buffer_cap, BUFFER_CAP)
        self._policy = Policy(
            SCHEMA,
            history_applied,
            history_asked,
            history_capped,
            buffer_applied,
            buffer_asked,
            buffer_capped,
        )
        self._history: list[HistoryItem] = []
        self._lines: list[str] = []
        self._flag: bool = False
        self._misses: int = 0

    def __repr__(self) -> str:
        return (
            f"Session(history={len(self._history)}, buffer={len(self._lines)}, "
            f"interrupted={self._flag})"
        )

    @property
    def policy(self) -> Policy:
        return self._policy

    @property
    def history(self) -> tuple[HistoryItem, ...]:
        return tuple(self._history)

    @property
    def buffer(self) -> Buffer:
        return Buffer(
            SCHEMA,
            tuple(self._lines),
            "\n".join(self._lines),
            len(self._lines),
            self._policy.buffer_cap,
            BUFFER_CAP,
            self._policy.asked_buffer_cap,
            self._policy.buffer_capped,
        )

    @property
    def interrupted(self) -> bool:
        return self._flag

    def transcript(self) -> Transcript:
        """Freeze history, the draft buffer, the flag, and the miss count."""
        return Transcript(
            SCHEMA,
            self._policy,
            tuple(self._history),
            tuple(self._lines),
            self._flag,
            self._misses,
        )

    def _push(self, kind: str, text: str, name: str) -> None:
        self._history.append(HistoryItem(SCHEMA, kind, text, name))
        extra = len(self._history) - self._policy.history_cap
        if extra > 0:
            del self._history[:extra]

    def _remember(self, line: object, item: Descriptor | Plain) -> None:
        if isinstance(item, Descriptor):
            self._push("slash", _one_line(line), item.name)
            return
        self._push("text", item.text, "")

    def accept(self, line: object, *, checkpoints: object = None) -> Descriptor | Plain:
        """Parse one line and keep it. `ROLLBACK_MISS` may be retried once."""
        try:
            item = parse(line, checkpoints=checkpoints)
        except Refuse as exc:
            if exc.code != "ROLLBACK_MISS":
                raise
            if self._misses >= 1:
                raise Refuse("RETRY_CAP") from None
            self._misses = 1
            raise
        if isinstance(item, Descriptor) and item.name == "rollback" and item.index is not None:
            self._misses = 0
        self._remember(line, item)
        return item

    def append_line(self, line: object) -> Buffer:
        """Add one line to the multiline buffer. A slash is still text here."""
        text = _one_line(line)
        if len(self._lines) >= self._policy.buffer_cap:
            raise Refuse("BUFFER_FULL")
        pending = (*self._lines, text)
        _secrets("\n".join(pending))
        self._lines.append(text)
        return self.buffer

    def flush(self) -> Plain:
        """Join the buffer into one plain record and clear it."""
        if len(self._lines) == 0:
            raise Refuse("EMPTY_BUFFER")
        text = "\n".join(self._lines)
        plain = Plain(SCHEMA, text, "text")
        self._push("text", text, "")
        self._lines.clear()
        return plain

    def interrupt(self) -> Interrupt:
        """Set the interrupt flag. This does not parse a slash command."""
        self._flag = True
        return Interrupt(SCHEMA, True)


def rebuild(record: object) -> Transcript:
    """Re-check a transcript and return the same public state."""
    if not isinstance(record, Transcript):
        raise Refuse("BAD_KIND")
    return Transcript(
        record.schema,
        record.policy,
        record.history,
        record.lines,
        record.interrupted,
        record.misses,
    )


def restore(record: object) -> Session:
    """Open a session whose transcript equals `record`."""
    fresh = rebuild(record)
    session = Session(
        history_cap=fresh.policy.asked_history_cap,
        buffer_cap=fresh.policy.asked_buffer_cap,
    )
    if session.policy != fresh.policy:
        raise Refuse("BAD_LIMIT")
    session._history = list(fresh.history)
    session._lines = list(fresh.lines)
    session._flag = fresh.interrupted
    session._misses = fresh.misses
    return session
