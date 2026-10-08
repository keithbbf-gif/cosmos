"""Messaging platform parse, text descriptors, and tool notes. No network.

A platform stays disabled until a credential id is set. Messaging platforms
refuse a terminal tool, including stock presets that bundle one.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Final, cast

from cosmos_hermes import Refuse, bound_text, redact, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-platforms/1"
TEXT_CAP: Final[int] = 4000
REQUEST_CAP: Final[int] = 256_000

PLATFORM_IDS: Final[tuple[str, ...]] = (
    "cli",
    "telegram",
    "discord",
    "slack",
    "whatsapp",
    "signal",
    "matrix",
    "mattermost",
    "email",
    "sms",
    "dingtalk",
    "feishu",
    "wecom",
    "weixin",
    "qq",
    "yuanbao",
    "bluebubbles",
    "homeassistant",
    "teams",
    "google_chat",
)

# Names that grant a terminal, including presets that ship with one.
# `hermes-telegram` is the preset class: naming it must not turn a shell on.
TERMINAL_TOOLS: Final[tuple[str, ...]] = (
    "coding",
    "debugging",
    "hermes-bluebubbles",
    "hermes-cli",
    "hermes-dingtalk",
    "hermes-discord",
    "hermes-email",
    "hermes-feishu",
    "hermes-gateway",
    "hermes-google-chat",
    "hermes-homeassistant",
    "hermes-matrix",
    "hermes-mattermost",
    "hermes-qq",
    "hermes-signal",
    "hermes-slack",
    "hermes-sms",
    "hermes-teams",
    "hermes-telegram",
    "hermes-wecom",
    "hermes-weixin",
    "hermes-whatsapp",
    "hermes-yuanbao",
    "process",
    "shell",
    "terminal",
)

SAFE_TOOLS: Final[tuple[str, ...]] = (
    "clarify",
    "memory",
    "todo",
    "vision",
    "web",
)

_NAME_CAP: Final[int] = 64
_SECRET_CAP: Final[int] = 128
_PLATFORM_SET: Final[frozenset[str]] = frozenset(PLATFORM_IDS)
_MESSAGING: Final[frozenset[str]] = frozenset(name for name in PLATFORM_IDS if name != "cli")
_TERMINAL: Final[frozenset[str]] = frozenset(TERMINAL_TOOLS)
_SAFE: Final[frozenset[str]] = frozenset(SAFE_TOOLS)

_CRED_RE: Final[re.Pattern[str]] = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}")
_TOOL_RE: Final[re.Pattern[str]] = re.compile(r"[a-z][a-z0-9_-]{0,63}")
_TELEGRAM_BOT: Final[re.Pattern[str]] = re.compile(r"\d{8,12}:[A-Za-z0-9_-]{30,}")
_SLACK_BOT: Final[re.Pattern[str]] = re.compile(r"xox[aboprs]-[A-Za-z0-9-]{8,}")
_DISCORD_BOT: Final[re.Pattern[str]] = re.compile(r"(?i)\bBot\s+[A-Za-z0-9._-]{24,}")
_BOT_ASSIGN: Final[re.Pattern[str]] = re.compile(r"(?i)bot[_-]?token\s*[:=]\s*\S+")


def _is_secret(text: str) -> bool:
    """True for key shapes and raw messaging bot tokens. One scan each."""
    return bool(
        secret_shape(text)
        or _TELEGRAM_BOT.search(text) is not None
        or _SLACK_BOT.search(text) is not None
        or _DISCORD_BOT.search(text) is not None
        or _BOT_ASSIGN.search(text) is not None
    )


def _show(text: str) -> str:
    """Scrub bot-token shapes, then the shared key shapes, once."""
    cleaned = _BOT_ASSIGN.sub("[redacted-bot]", text)
    cleaned = _DISCORD_BOT.sub("[redacted-bot]", cleaned)
    cleaned = _SLACK_BOT.sub("[redacted-bot]", cleaned)
    cleaned = _TELEGRAM_BOT.sub("[redacted-bot]", cleaned)
    return redact(cleaned)


def _platform(value: object) -> str:
    text = bound_text(value, _NAME_CAP)
    if text not in _PLATFORM_SET:
        raise Refuse("UNKNOWN_PLATFORM")
    return text


def _secret_id(value: object) -> str:
    text = bound_text(value, _SECRET_CAP)
    if text.strip() == "":
        raise Refuse("NO_SECRET")
    if _is_secret(text):
        raise Refuse("SECRET")
    if _CRED_RE.fullmatch(text) is None:
        raise Refuse("BAD_ID")
    return text


def _public_text(value: object) -> str:
    """Bound stored text. Empty refuses. A blank prefix of a real message stays."""
    text = bound_text(value)
    if text == "":
        raise Refuse("EMPTY")
    if _is_secret(text):
        raise Refuse("SECRET")
    return text


def _message(value: object) -> str:
    text = _public_text(value)
    if text.strip() == "":
        raise Refuse("EMPTY")
    return text


def _tool_name(value: object) -> str:
    text = bound_text(value, _NAME_CAP)
    if _is_secret(text):
        raise Refuse("SECRET")
    if _TOOL_RE.fullmatch(text) is None:
        raise Refuse("BAD_NAME")
    return text


def _applied_cap(requested: object) -> tuple[int, int]:
    """Applied cap never exceeds 4000. The asked value is kept when it fits."""
    if requested is None:
        return TEXT_CAP, TEXT_CAP
    if type(requested) is not int:
        raise Refuse("BAD_CAP")
    if requested < 1 or requested > REQUEST_CAP:
        raise Refuse("BAD_CAP")
    applied = TEXT_CAP if requested > TEXT_CAP else requested
    return applied, requested


@dataclass(frozen=True, slots=True)
class Enabled:
    """One platform bound to a credential id."""

    platform_id: str
    secret_id: str

    def __post_init__(self) -> None:
        name = _platform(self.platform_id)
        secret = _secret_id(self.secret_id)
        if name != self.platform_id or secret != self.secret_id:
            raise Refuse("BAD_RECORD")

    def __repr__(self) -> str:
        return _show(f"Enabled(platform_id={self.platform_id!r}, secret_id={self.secret_id!r})")


@dataclass(frozen=True, slots=True)
class Inbound:
    """Parsed text for one enabled platform."""

    platform_id: str
    text: str

    def __post_init__(self) -> None:
        name = _platform(self.platform_id)
        if name != self.platform_id or type(self.text) is not str:
            raise Refuse("BAD_RECORD")
        checked = _message(self.text)
        if checked != self.text:
            raise Refuse("BAD_RECORD")

    def __repr__(self) -> str:
        return _show(f"Inbound(platform_id={self.platform_id!r}, text={self.text!r})")


@dataclass(frozen=True, slots=True)
class Outbound:
    """Text descriptor. `cap` is the applied policy cap, never above 4000."""

    platform_id: str
    text: str
    cap: int
    requested: int
    truncated: bool

    def __post_init__(self) -> None:
        name = _platform(self.platform_id)
        if name != self.platform_id or type(self.text) is not str or type(self.truncated) is not bool:
            raise Refuse("BAD_RECORD")
        if type(self.cap) is not int or type(self.requested) is not int:
            raise Refuse("BAD_CAP")
        checked = _public_text(self.text)
        if checked != self.text:
            raise Refuse("BAD_RECORD")
        if self.cap < 1 or self.cap > TEXT_CAP or self.requested < 1 or self.requested > REQUEST_CAP:
            raise Refuse("BAD_CAP")
        if self.requested > TEXT_CAP:
            if self.cap != TEXT_CAP:
                raise Refuse("BAD_CAP")
        elif self.cap != self.requested:
            raise Refuse("BAD_CAP")
        if len(self.text) > self.cap or (len(self.text) < self.cap and self.truncated):
            raise Refuse("BAD_RECORD")

    def __repr__(self) -> str:
        body = (
            f"Outbound(platform_id={self.platform_id!r}, text={self.text!r}, "
            f"cap={self.cap!r}, requested={self.requested!r}, truncated={self.truncated!r})"
        )
        return _show(body)


@dataclass(frozen=True, slots=True)
class ToolNote:
    """A named tool on one platform. `runs` is always false. This is not a process."""

    platform_id: str
    name: str
    runs: bool

    def __post_init__(self) -> None:
        platform = _platform(self.platform_id)
        tool = _tool_name(self.name)
        if platform != self.platform_id or tool != self.name or type(self.runs) is not bool:
            raise Refuse("BAD_RECORD")
        if tool in _TERMINAL and platform in _MESSAGING:
            raise Refuse("MESSAGING_TERMINAL")
        if tool not in _SAFE and tool not in _TERMINAL:
            raise Refuse("UNKNOWN_TOOL")
        if self.runs:
            raise Refuse("BAD_RECORD")

    def __repr__(self) -> str:
        return _show(f"ToolNote(platform_id={self.platform_id!r}, name={self.name!r}, runs={self.runs!r})")


@dataclass(frozen=True, slots=True)
class Platforms:
    """Caller-held enablement. Every id starts disabled."""

    enabled: tuple[Enabled, ...] = ()
    _index: dict[str, Enabled] = field(default_factory=dict, init=False, compare=False, repr=False)

    def __post_init__(self) -> None:
        if type(self.enabled) is not tuple:
            raise Refuse("BAD_RECORD")
        index: dict[str, Enabled] = {}
        for row in self.enabled:
            if type(row) is not Enabled:
                raise Refuse("BAD_RECORD")
            if row.platform_id in index:
                raise Refuse("DUPLICATE")
            index[row.platform_id] = row
        object.__setattr__(self, "_index", index)

    def __repr__(self) -> str:
        return _show(f"Platforms(enabled={self.enabled!r})")

    def _require(self, name: str) -> Enabled:
        row = self._index.get(name)
        if row is None:
            raise Refuse("DISABLED", name)
        return row

    def enable(self, platform_id: object, secret_id: object) -> Platforms:
        """Return a desk with `platform_id` enabled under the credential id."""
        name = _platform(platform_id)
        secret = _secret_id(secret_id)
        kept: list[Enabled] = []
        replaced = False
        for row in self.enabled:
            if row.platform_id == name:
                kept.append(Enabled(name, secret))
                replaced = True
            else:
                kept.append(row)
        if not replaced:
            kept.append(Enabled(name, secret))
        return Platforms(tuple(kept))

    def parse(self, platform_id: object, text: object) -> Inbound:
        """Return inbound text. A disabled id refuses before the text is read."""
        name = _platform(platform_id)
        self._require(name)
        return Inbound(name, _message(text))

    def format_out(self, platform_id: object, text: object, cap: object = None) -> Outbound:
        """Cut text to the applied cap. A request above 4000 stores 4000."""
        return self._descriptor(platform_id, text, cap)

    def send(self, platform_id: object, text: object, cap: object = None) -> Outbound:
        """Return a text descriptor. Nothing is transmitted."""
        return self._descriptor(platform_id, text, cap)

    def _descriptor(self, platform_id: object, text: object, cap: object) -> Outbound:
        name = _platform(platform_id)
        self._require(name)
        body = _message(text)
        applied, asked = _applied_cap(cap)
        truncated = len(body) > applied
        shown = body[:applied] if truncated else body
        return Outbound(name, shown, applied, asked, truncated)

    def request_tool(self, platform_id: object, name: object) -> ToolNote:
        """Name a tool. Messaging platforms refuse a terminal. The note does not run."""
        platform = _platform(platform_id)
        self._require(platform)
        return ToolNote(platform, _tool_name(name), False)


def rebuild(records: object) -> Platforms:
    """Reproduce a desk from the enabled rows it emitted."""
    if type(records) is not tuple:
        raise Refuse("BAD_RECORD")
    return Platforms(cast(tuple[Enabled, ...], records))


__all__ = [
    "PLATFORM_IDS",
    "REQUEST_CAP",
    "SAFE_TOOLS",
    "SCHEMA",
    "TERMINAL_TOOLS",
    "TEXT_CAP",
    "Enabled",
    "Inbound",
    "Outbound",
    "Platforms",
    "ToolNote",
    "rebuild",
]
