"""Room mentions become reply plans. A bot cannot approve a tool.

Messaging cannot enable a terminal. The records are a projection a later
ledger append would store. Nothing here dials out, spawns, or grants.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, replace
from typing import Final

from cosmos_hermes import Refuse, bound_int, bound_text, const_eq, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-bot_mode/1"
REPLY_KIND: Final[str] = "reply"
GENESIS: Final[str] = "0" * 64
POLICY_ROSTER: Final[int] = 20
POLICY_FANOUT: Final[int] = 3
POLICY_SCREEN: Final[int] = 20

_ASK_HI: Final[int] = 1_000_000_000
_ID_LIMIT: Final[int] = 64
_TOKEN_LIMIT: Final[int] = 64
_SPECIALTY_LIMIT: Final[int] = 80
_STATUS_LIMIT: Final[int] = 16
_TEXT_LIMIT: Final[int] = 4_000
_ID_RE: Final[re.Pattern[str]] = re.compile(r"^[a-z][a-z0-9-]{0,31}$")
_TOKEN_RE: Final[re.Pattern[str]] = re.compile(r"^[a-z][a-z0-9-]{0,63}$")
_HEX_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")
# A preceding address character means an email, not a mention.
_MENTION_RE: Final[re.Pattern[str]] = re.compile(
    r"(?<![A-Za-z0-9._%+\-])@([A-Za-z][A-Za-z0-9-]{0,31})(?![A-Za-z0-9_-])"
)
_STATUSES: Final[frozenset[str]] = frozenset({"ready", "held"})
_APPROVAL_WORDS: Final[frozenset[str]] = frozenset(
    {
        "approve",
        "approved",
        "approves",
        "approving",
        "authorise",
        "authorised",
        "authorises",
        "authorising",
        "authorize",
        "authorized",
        "authorizes",
        "authorizing",
        "grant",
        "granted",
        "granting",
        "grants",
    }
)
_YOLO_WORDS: Final[frozenset[str]] = frozenset({"yolo"})
_ENABLE_VERBS: Final[frozenset[str]] = frozenset(
    {
        "enable",
        "enabled",
        "enables",
        "enabling",
        "execute",
        "executed",
        "executes",
        "executing",
        "open",
        "opened",
        "opening",
        "opens",
        "run",
        "running",
        "runs",
        "spawn",
        "spawned",
        "spawning",
        "spawns",
        "start",
        "started",
        "starting",
        "starts",
    }
)
_TERMINAL_NOUNS: Final[frozenset[str]] = frozenset(
    {
        "command",
        "commands",
        "shell",
        "shells",
        "terminal",
        "terminals",
    }
)
_TOOL_NOUNS: Final[frozenset[str]] = _TERMINAL_NOUNS | frozenset({"tool", "tools"})
_INTENT_RE: Final[re.Pattern[str]] = re.compile(
    "(?i)(?:/(?:approve|yolo|terminal)\\b|\\b(?:"
    + "|".join(sorted(_APPROVAL_WORDS | _ENABLE_VERBS | _TOOL_NOUNS | _YOLO_WORDS))
    + ")\\b)"
)


def _check_cap(requested: int, applied: int, policy: int) -> None:
    if isinstance(requested, bool) or isinstance(applied, bool):
        raise Refuse("BAD_LIMIT")
    if not isinstance(requested, int) or not isinstance(applied, int):
        raise Refuse("BAD_LIMIT")
    if requested < 1 or requested > _ASK_HI or applied < 1 or applied > policy:
        raise Refuse("BAD_LIMIT")
    if requested <= policy and applied != requested:
        raise Refuse("BAD_LIMIT")
    if requested > policy and applied != policy:
        raise Refuse("BAD_LIMIT")


def _policy(value: object, policy: int) -> tuple[int, int]:
    if value is None:
        return policy, policy
    asked = bound_int(value, 1, _ASK_HI)
    applied = policy if asked > policy else asked
    return applied, asked


def _utf8(value: str) -> str:
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        raise Refuse("NOT_TEXT") from None
    return value


def _controls(text: str) -> bool:
    return any(ord(char) < 32 or ord(char) == 127 for char in text)


def _intent(text: str) -> str | None:
    """Return a refusal code when the text asks for a grant or a terminal."""
    saw_approval = False
    saw_tool = False
    saw_enable = False
    saw_terminal = False
    saw_yolo = False
    saw_slash_terminal = False
    for match in _INTENT_RE.finditer(text):
        raw = match.group(0).lower()
        if raw.startswith("/"):
            word = raw[1:]
            if word == "terminal":
                saw_slash_terminal = True
            else:
                saw_yolo = True
            continue
        if raw in _YOLO_WORDS:
            saw_yolo = True
        if raw in _APPROVAL_WORDS:
            saw_approval = True
        if raw in _TOOL_NOUNS:
            saw_tool = True
        if raw in _ENABLE_VERBS:
            saw_enable = True
        if raw in _TERMINAL_NOUNS:
            saw_terminal = True
    if saw_yolo or (saw_approval and saw_tool):
        return "BOT_APPROVAL"
    if saw_slash_terminal or (saw_enable and saw_terminal):
        return "NO_TERMINAL"
    return None


def _bot_id(value: object) -> str:
    text = _utf8(bound_text(value, _ID_LIMIT))
    if secret_shape(text):
        raise Refuse("SECRET")
    if _ID_RE.fullmatch(text) is None:
        raise Refuse("BAD_ID")
    return text


def _specialty(value: object) -> str:
    text = _utf8(bound_text(value, _SPECIALTY_LIMIT))
    if secret_shape(text):
        raise Refuse("SECRET")
    if text == "" or text != text.strip() or _controls(text):
        raise Refuse("BAD_SPECIALTY")
    if _intent(text) is not None:
        raise Refuse("BAD_SPECIALTY")
    return text


def _status(value: object) -> str:
    text = _utf8(bound_text(value, _STATUS_LIMIT))
    if text not in _STATUSES:
        raise Refuse("BAD_STATUS")
    return text


def _token(value: object, code: str) -> str:
    text = _utf8(bound_text(value, _TOKEN_LIMIT))
    if secret_shape(text):
        raise Refuse("SECRET")
    if _TOKEN_RE.fullmatch(text) is None:
        raise Refuse(code)
    return text


def _room(value: object) -> str:
    return _token(value, "BAD_ROOM")


def _sender(value: object) -> str:
    return _token(value, "BAD_SENDER")


def _message(value: object) -> str:
    text = _utf8(bound_text(value, _TEXT_LIMIT))
    if secret_shape(text):
        raise Refuse("SECRET")
    return text


def _flag(value: object) -> bool:
    if type(value) is not bool:
        raise Refuse("BAD_FLAG")
    return value


def _mentions(text: str) -> tuple[str, ...]:
    found: list[str] = []
    for match in _MENTION_RE.finditer(text):
        found.append(match.group(1).lower())
    return tuple(found)


def _unique(tokens: tuple[str, ...]) -> tuple[str, ...]:
    ordered: list[str] = []
    seen: set[str] = set()
    for token in tokens:
        if token in seen and any(const_eq(token, prior) for prior in ordered):
            continue
        seen.add(token)
        ordered.append(token)
    return tuple(ordered)


def _hex64(value: object) -> str:
    if not isinstance(value, str) or len(value) != 64 or _HEX_RE.fullmatch(value) is None:
        raise Refuse("BAD_RECORD")
    return value


def _record_digest(seq: int, bot_id: str, specialty: str, status: str, prev: str) -> str:
    payload = f"{seq}|{bot_id}|{specialty}|{status}|{prev}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class Caps:
    """Asked caps and the caps that are actually enforced."""

    requested_roster: int
    requested_fanout: int
    requested_screen: int
    roster: int
    fanout: int
    screen: int

    def __post_init__(self) -> None:
        _check_cap(self.requested_roster, self.roster, POLICY_ROSTER)
        _check_cap(self.requested_fanout, self.fanout, POLICY_FANOUT)
        _check_cap(self.requested_screen, self.screen, POLICY_SCREEN)


@dataclass(frozen=True, slots=True)
class Bot:
    """One specialist. `status` is `ready` or `held`."""

    bot_id: str
    specialty: str
    status: str

    def __post_init__(self) -> None:
        _bot_id(self.bot_id)
        _specialty(self.specialty)
        _status(self.status)


@dataclass(frozen=True, slots=True)
class Roster:
    """In-memory roster. The live authority is a later ledger append."""

    caps: Caps
    bots: tuple[Bot, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.caps, Caps):
            raise Refuse("BAD_ROSTER")
        if not isinstance(self.bots, tuple):
            raise Refuse("BAD_ROSTER")
        if len(self.bots) > self.caps.roster:
            raise Refuse("BOT_CAP")
        seen: set[str] = set()
        for bot in self.bots:
            if not isinstance(bot, Bot):
                raise Refuse("BAD_ROSTER")
            if bot.bot_id in seen and any(const_eq(bot.bot_id, prior) for prior in seen):
                raise Refuse("DUPLICATE")
            seen.add(bot.bot_id)


@dataclass(frozen=True, slots=True)
class RoomMessage:
    """One room line. The text stays here and does not ride on the reply plan."""

    room: str
    sender: str
    text: str

    def __post_init__(self) -> None:
        _room(self.room)
        _sender(self.sender)
        _message(self.text)


@dataclass(frozen=True, slots=True)
class ReplyPlan:
    """A mention route. Kind is reply. Terminal and tool approval stay off."""

    room: str
    sender: str
    bot_ids: tuple[str, ...]
    specialties: tuple[str, ...]
    rounds: tuple[int, ...]
    kind: str
    fanout: bool
    enables_terminal: bool
    approves_tool: bool

    def __post_init__(self) -> None:
        if type(self.kind) is not str or self.kind != REPLY_KIND:
            raise Refuse("BAD_KIND")
        if (
            type(self.fanout) is not bool
            or type(self.enables_terminal) is not bool
            or type(self.approves_tool) is not bool
        ):
            raise Refuse("BAD_FLAG")
        if self.enables_terminal:
            raise Refuse("NO_TERMINAL")
        if self.approves_tool:
            raise Refuse("BOT_APPROVAL")
        _room(self.room)
        _sender(self.sender)
        if (
            not isinstance(self.bot_ids, tuple)
            or not isinstance(self.specialties, tuple)
            or not isinstance(self.rounds, tuple)
        ):
            raise Refuse("BAD_PLAN")
        count = len(self.bot_ids)
        if count < 1:
            raise Refuse("NO_MENTION")
        if count > POLICY_FANOUT:
            raise Refuse("FANOUT_CAP")
        if count > 1 and not self.fanout:
            raise Refuse("NEED_FANOUT")
        if len(self.specialties) != count or len(self.rounds) != count:
            raise Refuse("BAD_PLAN")
        seen: set[str] = set()
        for index, ident in enumerate(self.bot_ids):
            checked = _bot_id(ident)
            if checked in seen and any(const_eq(checked, prior) for prior in seen):
                raise Refuse("DUPLICATE")
            seen.add(checked)
            _specialty(self.specialties[index])
            number = self.rounds[index]
            if type(number) is not int or number != index + 1:
                raise Refuse("BAD_PLAN")


@dataclass(frozen=True, slots=True)
class Record:
    """One roster link. `digest` is the sha256 of the body and `prev`."""

    seq: int
    bot_id: str
    specialty: str
    status: str
    prev: str
    digest: str

    def __post_init__(self) -> None:
        seq = bound_int(self.seq, 1, POLICY_ROSTER)
        ident = _bot_id(self.bot_id)
        role = _specialty(self.specialty)
        flag = _status(self.status)
        prev = _hex64(self.prev)
        digest = _hex64(self.digest)
        expected = _record_digest(seq, ident, role, flag, prev)
        if not const_eq(expected, digest):
            raise Refuse("BROKEN")


def _seal_snapshot(
    requested_roster: object,
    requested_fanout: object,
    requested_screen: object,
    records: object,
    tip: object,
) -> None:
    asked_roster = bound_int(requested_roster, 1, _ASK_HI)
    bound_int(requested_fanout, 1, _ASK_HI)
    bound_int(requested_screen, 1, _ASK_HI)
    applied = POLICY_ROSTER if asked_roster > POLICY_ROSTER else asked_roster
    if not isinstance(records, tuple):
        raise Refuse("BAD_RECORD")
    if len(records) > applied:
        raise Refuse("BOT_CAP")
    if not isinstance(tip, str):
        raise Refuse("BAD_RECORD")
    prev = GENESIS
    seen: set[str] = set()
    for index, record in enumerate(records, start=1):
        if not isinstance(record, Record):
            raise Refuse("BAD_RECORD")
        if record.seq != index or not const_eq(record.prev, prev):
            raise Refuse("STALE")
        if record.bot_id in seen and any(const_eq(record.bot_id, prior) for prior in seen):
            raise Refuse("DUPLICATE")
        seen.add(record.bot_id)
        prev = record.digest
    expected_tip = prev if records else GENESIS
    if not const_eq(tip, expected_tip):
        raise Refuse("STALE")


@dataclass(frozen=True, slots=True)
class Snapshot:
    """Hash-chained roster projection. `rebuild` reads this and nothing else."""

    requested_roster: int
    requested_fanout: int
    requested_screen: int
    records: tuple[Record, ...]
    tip: str

    def __post_init__(self) -> None:
        _seal_snapshot(
            self.requested_roster,
            self.requested_fanout,
            self.requested_screen,
            self.records,
            self.tip,
        )


def _roster(value: object) -> Roster:
    if not isinstance(value, Roster):
        raise Refuse("BAD_ROSTER")
    return value


def _note(value: object) -> RoomMessage:
    if not isinstance(value, RoomMessage):
        raise Refuse("BAD_MESSAGE")
    return value


def _index(bots: tuple[Bot, ...]) -> dict[str, Bot]:
    found: dict[str, Bot] = {}
    for bot in bots:
        found[bot.bot_id] = bot
    return found


def _resolve(index: dict[str, Bot], token: str) -> Bot:
    bot = index.get(token)
    if bot is None or not const_eq(bot.bot_id, token):
        raise Refuse("NO_BOT")
    return bot


def make_roster(
    requested_roster: object = None,
    requested_fanout: object = None,
    requested_screen: object = None,
) -> Roster:
    """Store asked caps. A request above policy does not raise the cap."""
    roster_applied, roster_asked = _policy(requested_roster, POLICY_ROSTER)
    fanout_applied, fanout_asked = _policy(requested_fanout, POLICY_FANOUT)
    screen_applied, screen_asked = _policy(requested_screen, POLICY_SCREEN)
    caps = Caps(
        requested_roster=roster_asked,
        requested_fanout=fanout_asked,
        requested_screen=screen_asked,
        roster=roster_applied,
        fanout=fanout_applied,
        screen=screen_applied,
    )
    return Roster(caps=caps, bots=())


def register(
    roster: object,
    bot_id: object,
    specialty: object,
    *,
    status: object = "ready",
) -> Roster:
    """Append one specialist. The next id past the roster cap raises BOT_CAP."""
    state = _roster(roster)
    if not isinstance(bot_id, str) or not isinstance(specialty, str) or not isinstance(status, str):
        raise Refuse("NOT_TEXT")
    added = Bot(bot_id=bot_id, specialty=specialty, status=status)
    seen = {bot.bot_id for bot in state.bots}
    if added.bot_id in seen:
        for bot in state.bots:
            if const_eq(bot.bot_id, added.bot_id):
                raise Refuse("DUPLICATE")
        raise Refuse("DUPLICATE")
    if len(state.bots) >= state.caps.roster:
        raise Refuse("BOT_CAP")
    return replace(state, bots=state.bots + (added,))


def room_message(room: object, sender: object, text: object) -> RoomMessage:
    """Bind a room token, a sender token, and the line of text."""
    if not isinstance(room, str) or not isinstance(sender, str) or not isinstance(text, str):
        raise Refuse("NOT_TEXT")
    return RoomMessage(room=room, sender=sender, text=text)


def route(
    roster: object,
    note: object,
    *,
    fanout: object = False,
    mode: object = None,
) -> ReplyPlan:
    """Resolve @mentions into a reply plan. The caller text is not copied."""
    if mode is not None:
        raise Refuse("BAD_MODE")
    state = _roster(roster)
    message = _note(note)
    wide = _flag(fanout)
    reason = _intent(message.text)
    if reason is not None:
        raise Refuse(reason)
    found = _unique(_mentions(message.text))
    if not found:
        raise Refuse("NO_MENTION")
    index = _index(state.bots)
    picked = tuple(_resolve(index, token) for token in found)
    for bot in picked:
        if bot.status != "ready":
            raise Refuse("HELD")
    for bot in picked:
        if const_eq(bot.bot_id, message.sender):
            raise Refuse("SELF")
    count = len(picked)
    if count > state.caps.fanout:
        raise Refuse("FANOUT_CAP")
    if count > 1 and not wide:
        raise Refuse("NEED_FANOUT")
    return ReplyPlan(
        room=message.room,
        sender=message.sender,
        bot_ids=tuple(bot.bot_id for bot in picked),
        specialties=tuple(bot.specialty for bot in picked),
        rounds=tuple(range(1, count + 1)),
        kind=REPLY_KIND,
        fanout=wide,
        enables_terminal=False,
        approves_tool=False,
    )


def approve(*_args: object, **_kwargs: object) -> None:
    """A bot cannot approve a tool."""
    raise Refuse("BOT_APPROVAL")


def enable_terminal(*_args: object, **_kwargs: object) -> None:
    """Messaging cannot enable a terminal."""
    raise Refuse("NO_TERMINAL")


def screen(roster: object, limit: object = None) -> tuple[str, ...]:
    """Return pane lines of id, specialty, and status. The window stops at the cap."""
    state = _roster(roster)
    window = state.caps.screen
    if limit is not None:
        asked = bound_int(limit, 1, _ASK_HI)
        if asked < window:
            window = asked
    lines: list[str] = []
    for bot in state.bots:
        if len(lines) >= window:
            break
        lines.append(f"{bot.bot_id}\t{bot.specialty}\t{bot.status}")
    return tuple(lines)


def snapshot(roster: object) -> Snapshot:
    """Emit the roster as one hash chain. The same roster emits the same chain."""
    state = _roster(roster)
    records: list[Record] = []
    prev = GENESIS
    for seq, bot in enumerate(state.bots, start=1):
        digest = _record_digest(seq, bot.bot_id, bot.specialty, bot.status, prev)
        records.append(
            Record(
                seq=seq,
                bot_id=bot.bot_id,
                specialty=bot.specialty,
                status=bot.status,
                prev=prev,
                digest=digest,
            )
        )
        prev = digest
    tip = GENESIS if not records else prev
    return Snapshot(
        requested_roster=state.caps.requested_roster,
        requested_fanout=state.caps.requested_fanout,
        requested_screen=state.caps.requested_screen,
        records=tuple(records),
        tip=tip,
    )


def rebuild(image: object) -> Roster:
    """Replay a snapshot into the same public roster."""
    if not isinstance(image, Snapshot):
        raise Refuse("BAD_RECORD")
    state = make_roster(
        image.requested_roster,
        image.requested_fanout,
        image.requested_screen,
    )
    for record in image.records:
        state = register(state, record.bot_id, record.specialty, status=record.status)
    return state


__all__ = [
    "GENESIS",
    "POLICY_FANOUT",
    "POLICY_ROSTER",
    "POLICY_SCREEN",
    "REPLY_KIND",
    "SCHEMA",
    "Bot",
    "Caps",
    "Record",
    "ReplyPlan",
    "RoomMessage",
    "Roster",
    "Snapshot",
    "approve",
    "enable_terminal",
    "make_roster",
    "rebuild",
    "register",
    "room_message",
    "route",
    "screen",
    "snapshot",
]
