"""Per-platform tool allow and deny resolution.

An empty allow list enables nothing. Preset names expand to toolset tuples.
Any platform other than cli whose resolved allow list still contains a
terminal tool refuses. Deny drops a toolset. A named tool drop keeps later tools.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Final

from cosmos_hermes import Refuse, bound_text, const_eq, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-tools_toolsets/1"

NAME_CAP: Final[int] = 64
LIST_CAP: Final[int] = 32
REGISTRY_CAP: Final[int] = 64

RISKS: Final[frozenset[str]] = frozenset({"read", "write", "terminal", "net", "admin"})

PLATFORMS: Final[tuple[str, ...]] = (
    "cli",
    "acp",
    "api_server",
    "cron",
    "gateway",
    "webhook",
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
    "wecom_callback",
    "weixin",
    "qq",
    "qqbot",
    "yuanbao",
    "bluebubbles",
    "homeassistant",
    "teams",
    "google_chat",
)

_PLATFORM_IDS: Final[frozenset[str]] = frozenset(PLATFORMS)
_NAME_RE: Final[re.Pattern[str]] = re.compile(r"[a-z][a-z0-9_-]*")
_TERMINAL: Final[str] = "terminal"

_CLI: Final[tuple[str, ...]] = (
    "file",
    "terminal",
    "web",
    "browser",
    "memory",
    "skills",
    "vision",
    "image_gen",
    "todo",
    "tts",
    "delegation",
    "code_execution",
    "cronjob",
    "session_search",
    "clarify",
    "computer_use",
    "homeassistant",
    "kanban",
)
_ACP_DROP: Final[frozenset[str]] = frozenset(
    {"clarify", "cronjob", "image_gen", "tts", "computer_use", "homeassistant", "kanban"}
)
_API_DROP: Final[frozenset[str]] = frozenset({"clarify", "tts", "computer_use", "kanban"})
_SAME_AS_CLI: Final[tuple[str, ...]] = (
    "hermes-cli",
    "hermes-cron",
    "hermes-telegram",
    "hermes-slack",
    "hermes-whatsapp",
    "hermes-signal",
    "hermes-matrix",
    "hermes-mattermost",
    "hermes-email",
    "hermes-sms",
    "hermes-bluebubbles",
    "hermes-dingtalk",
    "hermes-qqbot",
    "hermes-wecom",
    "hermes-wecom-callback",
    "hermes-weixin",
    "hermes-homeassistant",
)

__all__ = [
    "LIST_CAP",
    "NAME_CAP",
    "PLATFORMS",
    "PRESETS",
    "REGISTRY_CAP",
    "RISKS",
    "SCHEMA",
    "Catalog",
    "Effective",
    "Tool",
    "effective",
    "new_catalog",
    "rebuild",
    "register",
]


def _uniq(names: tuple[str, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    found: list[str] = []
    for name in names:
        if name in seen:
            continue
        seen.add(name)
        found.append(name)
    return tuple(found)


def _build_presets() -> dict[str, tuple[str, ...]]:
    table: dict[str, tuple[str, ...]] = {key: _CLI for key in _SAME_AS_CLI}
    table["debugging"] = ("file", "terminal", "web")
    table["coding"] = (
        "file",
        "terminal",
        "search",
        "web",
        "skills",
        "browser",
        "todo",
        "memory",
        "session_search",
        "clarify",
        "code_execution",
        "delegation",
        "vision",
    )
    table["safe"] = ("image_gen", "vision", "web")
    table["hermes-discord"] = _uniq(_CLI + ("discord", "discord_admin"))
    table["hermes-feishu"] = _uniq(_CLI + ("feishu_doc", "feishu_drive"))
    table["hermes-yuanbao"] = _uniq(_CLI + ("yuanbao",))
    table["hermes-acp"] = tuple(name for name in _CLI if name not in _ACP_DROP)
    table["hermes-api-server"] = tuple(name for name in _CLI if name not in _API_DROP)
    table["hermes-webhook"] = ("web", "vision", "clarify")
    table["hermes-gateway"] = _uniq(
        _CLI + ("discord", "discord_admin", "feishu_doc", "feishu_drive", "yuanbao")
    )
    return table


PRESETS: Final[Mapping[str, tuple[str, ...]]] = MappingProxyType(_build_presets())


def _policy_request(requested: object) -> None:
    """Accept a positive int. The recorded cap stays the policy value."""
    if type(requested) is not int or requested < 1:
        raise Refuse("BAD_CAP")


def _name(value: object) -> str:
    text = bound_text(value, NAME_CAP)
    if secret_shape(text):
        raise Refuse("SECRET_SHAPE")
    if _NAME_RE.fullmatch(text) is None:
        raise Refuse("BAD_NAME")
    return text


def _risk(value: object) -> str:
    text = bound_text(value, NAME_CAP)
    if secret_shape(text):
        raise Refuse("SECRET_SHAPE")
    if text not in RISKS:
        raise Refuse("BAD_RISK")
    return text


def _names(value: object) -> tuple[str, ...]:
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Sequence):
        raise Refuse("NOT_LIST")
    if len(value) > LIST_CAP:
        raise Refuse("OVER_CAP", str(LIST_CAP))
    found: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        if index >= LIST_CAP:
            raise Refuse("OVER_CAP", str(LIST_CAP))
        name = _name(item)
        if name in seen:
            raise Refuse("DUPLICATE")
        seen.add(name)
        found.append(name)
    return tuple(found)


def _expand(names: tuple[str, ...]) -> tuple[str, ...]:
    found: list[str] = []
    seen: set[str] = set()
    for name in names:
        members = PRESETS.get(name)
        parts = (name,) if members is None else members
        for part in parts:
            if part in seen:
                continue
            seen.add(part)
            found.append(part)
            if len(found) > LIST_CAP:
                raise Refuse("OVER_CAP", str(LIST_CAP))
    return tuple(found)


def _cli(platform: str) -> bool:
    return const_eq(platform, "cli")


@dataclass(frozen=True, slots=True)
class Tool:
    """One registered tool. `risk` is read, write, terminal, net, or admin."""

    name: str
    toolset: str
    risk: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _name(self.name))
        object.__setattr__(self, "toolset", _name(self.toolset))
        object.__setattr__(self, "risk", _risk(self.risk))


@dataclass(frozen=True, slots=True)
class Catalog:
    """Frozen registry. Stored caps are the policy caps."""

    tools: tuple[Tool, ...] = ()
    name_cap: int = NAME_CAP
    registry_cap: int = REGISTRY_CAP

    def __post_init__(self) -> None:
        if type(self.name_cap) is not int or self.name_cap < 1:
            raise Refuse("BAD_CAP")
        if type(self.registry_cap) is not int or self.registry_cap < 1:
            raise Refuse("BAD_CAP")
        object.__setattr__(self, "name_cap", NAME_CAP)
        object.__setattr__(self, "registry_cap", REGISTRY_CAP)
        if type(self.tools) is not tuple:
            raise Refuse("BAD_RECORD")
        if len(self.tools) > REGISTRY_CAP:
            raise Refuse("OVER_CAP", str(REGISTRY_CAP))
        seen: set[str] = set()
        for tool in self.tools:
            if type(tool) is not Tool:
                raise Refuse("BAD_RECORD")
            if tool.name in seen:
                raise Refuse("DUPLICATE")
            seen.add(tool.name)


@dataclass(frozen=True, slots=True)
class Effective:
    """Tools enabled for one platform. Caps are the policy caps."""

    platform: str
    tools: tuple[Tool, ...]
    toolsets: tuple[str, ...] = ()
    name_cap: int = NAME_CAP
    list_cap: int = LIST_CAP

    def __post_init__(self) -> None:
        if type(self.name_cap) is not int or self.name_cap < 1:
            raise Refuse("BAD_CAP")
        if type(self.list_cap) is not int or self.list_cap < 1:
            raise Refuse("BAD_CAP")
        object.__setattr__(self, "name_cap", NAME_CAP)
        object.__setattr__(self, "list_cap", LIST_CAP)
        if type(self.platform) is not str or type(self.tools) is not tuple or type(self.toolsets) is not tuple:
            raise Refuse("BAD_RECORD")
        platform = _name(self.platform)
        if platform not in _PLATFORM_IDS:
            raise Refuse("UNKNOWN_PLATFORM")
        object.__setattr__(self, "platform", platform)
        seen: set[str] = set()
        for name in self.toolsets:
            checked = _name(name)
            if checked != name or name in seen:
                raise Refuse("BAD_RECORD")
            seen.add(name)
        live: set[str] = set()
        for tool in self.tools:
            if type(tool) is not Tool:
                raise Refuse("BAD_RECORD")
            live.add(tool.toolset)
        if seen != live:
            raise Refuse("BAD_RECORD")
        if not _cli(platform) and (
            _TERMINAL in seen
            or any(tool.toolset == _TERMINAL or tool.risk == _TERMINAL for tool in self.tools)
        ):
            raise Refuse("MESSAGING_TERMINAL")


def new_catalog(*, name_cap: object = NAME_CAP, registry_cap: object = REGISTRY_CAP) -> Catalog:
    """Return an empty catalog. A cap request does not move the policy cap."""
    _policy_request(name_cap)
    _policy_request(registry_cap)
    return Catalog(tools=())


def register(
    catalog: object,
    name: object,
    toolset: object,
    risk: object,
    *,
    name_cap: object = NAME_CAP,
    registry_cap: object = REGISTRY_CAP,
) -> Catalog:
    """Return a new catalog with one tool appended."""
    if type(catalog) is not Catalog:
        raise Refuse("BAD_RECORD")
    _policy_request(name_cap)
    _policy_request(registry_cap)
    tool = Tool(_name(name), _name(toolset), _risk(risk))
    if tool.name in {existing.name for existing in catalog.tools}:
        raise Refuse("DUPLICATE")
    if len(catalog.tools) >= REGISTRY_CAP:
        raise Refuse("OVER_CAP", str(REGISTRY_CAP))
    return Catalog(tools=catalog.tools + (tool,))


def rebuild(records: object) -> Catalog:
    """Rebuild a catalog from tool records. The same records return an equal catalog."""
    if isinstance(records, (str, bytes, bytearray)) or not isinstance(records, Sequence):
        raise Refuse("NOT_LIST")
    if len(records) > REGISTRY_CAP:
        raise Refuse("OVER_CAP", str(REGISTRY_CAP))
    catalog = new_catalog()
    for index, item in enumerate(records):
        if index >= REGISTRY_CAP:
            raise Refuse("OVER_CAP", str(REGISTRY_CAP))
        if type(item) is not Tool:
            raise Refuse("BAD_RECORD")
        catalog = register(catalog, item.name, item.toolset, item.risk)
    return catalog


def effective(
    platform: object,
    allow: object,
    deny: object = None,
    *,
    catalog: object,
    disabled_tools: object = None,
    name_cap: object = NAME_CAP,
    list_cap: object = LIST_CAP,
) -> Effective:
    """Return tools whose resolved toolset is allowed and not denied.

    `allow` None is a missing platform config. None and an empty allow raise
    EMPTY_ALLOW. Preset names expand before the terminal check. On any platform
    other than cli, a resolved allow list that still contains the terminal
    toolset raises MESSAGING_TERMINAL, including when deny names it too.
    A selected tool whose risk is terminal raises the same code. `all` and `*`
    do not expand. Named disabled tools are dropped; later allowed tools stay.
    """
    if type(catalog) is not Catalog:
        raise Refuse("BAD_RECORD")
    _policy_request(name_cap)
    _policy_request(list_cap)
    if len(catalog.tools) > REGISTRY_CAP:
        raise Refuse("OVER_CAP", str(REGISTRY_CAP))
    platform_name = _name(platform)
    if platform_name not in _PLATFORM_IDS:
        raise Refuse("UNKNOWN_PLATFORM")
    if allow is None:
        raise Refuse("EMPTY_ALLOW", "missing")
    allowed_names = _names(allow)
    if not allowed_names:
        raise Refuse("EMPTY_ALLOW", "empty")
    denied_names = () if deny is None else _names(deny)
    disabled_names = () if disabled_tools is None else _names(disabled_tools)
    allowed = _expand(allowed_names)
    denied = _expand(denied_names)
    # Terminal is decided on the resolved names before unknown tokens, so a
    # messaging preset cannot hide a terminal grant behind a later bad name.
    cli = _cli(platform_name)
    allowed_set = set(allowed)
    if not cli and _TERMINAL in allowed_set:
        raise Refuse("MESSAGING_TERMINAL")
    known = {tool.toolset for tool in catalog.tools}
    known_tools = {tool.name for tool in catalog.tools}
    for label in allowed:
        if label not in known:
            raise Refuse("UNKNOWN_TOOLSET", label)
    for label in denied:
        if label not in known:
            raise Refuse("UNKNOWN_TOOLSET", label)
    for label in disabled_names:
        if label not in known_tools:
            raise Refuse("UNKNOWN_TOOL", label)
    denied_set = set(denied)
    disabled_set = set(disabled_names)
    opened = tuple(name for name in allowed if name not in denied_set)
    opened_set = set(opened)
    chosen: list[Tool] = []
    for tool in catalog.tools:
        if tool.toolset not in opened_set or tool.name in disabled_set:
            continue
        if not cli and tool.risk == _TERMINAL:
            raise Refuse("MESSAGING_TERMINAL")
        chosen.append(tool)
    live = {tool.toolset for tool in chosen}
    toolsets = tuple(name for name in opened if name in live)
    return Effective(
        platform=platform_name,
        tools=tuple(chosen),
        toolsets=toolsets,
        name_cap=NAME_CAP,
        list_cap=LIST_CAP,
    )
