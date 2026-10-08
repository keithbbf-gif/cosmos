"""Desktop action descriptors. Classification is CONFIRM. Dispatch never runs.

Coordinates are a normalized 0..10000 space. No pointer, keyboard, capture,
or driver is touched.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from typing import Final, NoReturn

from cosmos_hermes import PathJail, Refuse, bound_int, bound_text, const_eq, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-computer_use/1"
CONFIRM: Final[str] = "CONFIRM"
STALE_CAPTURE: Final[str] = "STALE_CAPTURE"
COORD_MIN: Final[int] = 0
COORD_MAX: Final[int] = 10_000
POLICY_CAPTURES: Final[int] = 20
POLICY_TEXT: Final[int] = 4_000
REQUEST_CEILING: Final[int] = 1_000_000

ACTIONS: Final[tuple[str, ...]] = ("move", "click", "type", "key", "screenshot")
MODES: Final[tuple[str, ...]] = ("standard", "bounded")

_ACTIONS: Final[frozenset[str]] = frozenset(ACTIONS)
_MODES: Final[frozenset[str]] = frozenset(MODES)
_DEFAULT_ALLOWLIST: Final[tuple[str, ...]] = tuple(sorted(ACTIONS))
_SURFACES: Final[frozenset[str]] = frozenset({"background", "foreground"})
_POINT_KINDS: Final[frozenset[str]] = frozenset({"move", "click"})
_POLICY_CHORD: Final[int] = 4
_POLICY_APPS: Final[int] = 32
_LABEL: Final[int] = 64
_DICT_KEYS: Final[frozenset[str]] = frozenset(
    {
        "kind",
        "x",
        "y",
        "text",
        "keys",
        "mode",
        "surface",
        "screen",
        "session",
        "apps",
        "allowlist",
        "manifest",
        "jail",
        "captures",
        "text_chars",
        "attempt",
    }
)
_ALIASES: Final[dict[str, str]] = {
    "ctrl": "control",
    "ctl": "control",
    "cmd": "command",
    "opt": "option",
    "esc": "escape",
    "enter": "return",
    "win": "meta",
    "super": "meta",
    "windows": "meta",
    "pgup": "pageup",
    "pgdn": "pagedown",
    "spacebar": "space",
    "del": "delete",
}
_KEY_NAMES: Final[frozenset[str]] = frozenset(
    {
        "return",
        "escape",
        "tab",
        "space",
        "delete",
        "backspace",
        "up",
        "down",
        "left",
        "right",
        "home",
        "end",
        "pageup",
        "pagedown",
        "command",
        "option",
        "alt",
        "control",
        "shift",
        "meta",
        *tuple(f"f{index}" for index in range(1, 25)),
        *tuple("abcdefghijklmnopqrstuvwxyz0123456789"),
    }
)
_BLOCKED_CHORDS: Final[frozenset[frozenset[str]]] = frozenset(
    {
        frozenset({"command", "shift", "delete"}),
        frozenset({"shift", "delete"}),
        frozenset({"meta", "l"}),
        frozenset({"command", "shift", "q"}),
        frozenset({"control", "command", "q"}),
        frozenset({"control", "alt", "delete"}),
    }
)
_BLOCKED_TYPE: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(r"(?i)\bcurl\b[^|\n]{0,240}\|\s*(?:bash|sh)\b"),
    re.compile(r"(?i)\bsudo\s+rm\s+-rf\s+/(?:\s|$)"),
    re.compile(r"(?i)(?:^|[\s;&|])rm\s+-rf\s+/(?:\s|$)"),
    re.compile(r":\(\)\s*\{\s*:\|:&\s*\}\s*;\s*:"),
)
_SESSION: Final[re.Pattern[str]] = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}")
_PATH_MARKS: Final[frozenset[str]] = frozenset("/\\:")


@dataclass(frozen=True, slots=True)
class Caps:
    """Policy ceilings actually recorded, plus the numbers the caller asked for."""

    captures: int
    text_chars: int
    requested_captures: int
    requested_text_chars: int
    clamped: tuple[str, ...]

    def __post_init__(self) -> None:
        _check_caps(self)


@dataclass(frozen=True, slots=True)
class Action:
    """One desktop descriptor. `code` is CONFIRM. Holding one does not dispatch it."""

    schema: str
    kind: str
    code: str
    mode: str
    x: int | None
    y: int | None
    text: str
    keys: tuple[str, ...]
    surface: str
    screen: str
    session: str
    apps: tuple[str, ...]
    allowlist: tuple[str, ...]
    manifest: str
    grants: tuple[str, ...]
    caps: Caps
    attempt: int

    def __post_init__(self) -> None:
        _audit(self)


def move(
    x: object,
    y: object,
    *,
    mode: object = "standard",
    surface: object = "background",
    screen: object = "",
    session: object = "",
    apps: object = (),
    allowlist: object = _DEFAULT_ALLOWLIST,
    manifest: object = None,
    jail: object = None,
    captures: object = POLICY_CAPTURES,
    text_chars: object = POLICY_TEXT,
) -> Action:
    """Describe a pointer move. Nothing moves."""
    return _build(
        "move",
        x=x,
        y=y,
        text="",
        keys=(),
        mode=mode,
        surface=surface,
        screen=screen,
        session=session,
        apps=apps,
        allowlist=allowlist,
        manifest=manifest,
        jail=jail,
        captures=captures,
        text_chars=text_chars,
    )


def click(
    x: object,
    y: object,
    *,
    mode: object = "standard",
    surface: object = "background",
    screen: object = "",
    session: object = "",
    apps: object = (),
    allowlist: object = _DEFAULT_ALLOWLIST,
    manifest: object = None,
    jail: object = None,
    captures: object = POLICY_CAPTURES,
    text_chars: object = POLICY_TEXT,
) -> Action:
    """Describe a click. Nothing is clicked."""
    return _build(
        "click",
        x=x,
        y=y,
        text="",
        keys=(),
        mode=mode,
        surface=surface,
        screen=screen,
        session=session,
        apps=apps,
        allowlist=allowlist,
        manifest=manifest,
        jail=jail,
        captures=captures,
        text_chars=text_chars,
    )


def type_text(
    text: object,
    x: object = None,
    y: object = None,
    *,
    mode: object = "standard",
    surface: object = "background",
    screen: object = "",
    session: object = "",
    apps: object = (),
    allowlist: object = _DEFAULT_ALLOWLIST,
    manifest: object = None,
    jail: object = None,
    captures: object = POLICY_CAPTURES,
    text_chars: object = POLICY_TEXT,
) -> Action:
    """Describe typed text. Nothing is typed."""
    return _build(
        "type",
        x=x,
        y=y,
        text=text,
        keys=(),
        mode=mode,
        surface=surface,
        screen=screen,
        session=session,
        apps=apps,
        allowlist=allowlist,
        manifest=manifest,
        jail=jail,
        captures=captures,
        text_chars=text_chars,
    )


def key(
    keys: object,
    x: object = None,
    y: object = None,
    *,
    mode: object = "standard",
    surface: object = "background",
    screen: object = "",
    session: object = "",
    apps: object = (),
    allowlist: object = _DEFAULT_ALLOWLIST,
    manifest: object = None,
    jail: object = None,
    captures: object = POLICY_CAPTURES,
    text_chars: object = POLICY_TEXT,
) -> Action:
    """Describe a key chord. Nothing is pressed."""
    return _build(
        "key",
        x=x,
        y=y,
        text="",
        keys=keys,
        mode=mode,
        surface=surface,
        screen=screen,
        session=session,
        apps=apps,
        allowlist=allowlist,
        manifest=manifest,
        jail=jail,
        captures=captures,
        text_chars=text_chars,
    )


def screenshot(
    x: object = None,
    y: object = None,
    *,
    mode: object = "standard",
    surface: object = "background",
    screen: object = "",
    session: object = "",
    apps: object = (),
    allowlist: object = _DEFAULT_ALLOWLIST,
    manifest: object = None,
    jail: object = None,
    captures: object = POLICY_CAPTURES,
    text_chars: object = POLICY_TEXT,
) -> Action:
    """Describe a capture. No pixels are read."""
    return _build(
        "screenshot",
        x=x,
        y=y,
        text="",
        keys=(),
        mode=mode,
        surface=surface,
        screen=screen,
        session=session,
        apps=apps,
        allowlist=allowlist,
        manifest=manifest,
        jail=jail,
        captures=captures,
        text_chars=text_chars,
    )


def classify(action: object) -> str:
    """Return CONFIRM for every legal desktop action, including click and move."""
    accepted = _known(action)
    if not const_eq(accepted.code, CONFIRM):
        raise Refuse("UNCLASSIFIED")
    return CONFIRM


def run(action: object) -> NoReturn:
    """Refuse dispatch. The action is not sent to a device."""
    del action
    raise Refuse("NOT_RUN")


def retry(action: object, failure: object) -> Action:
    """One confirming retry, and only after STALE_CAPTURE."""
    if type(action) is not Action:
        raise Refuse("BAD_ACTION")
    _audit(action)
    label = _plain(failure, _LABEL)
    if not const_eq(label, STALE_CAPTURE):
        raise Refuse("NO_RETRY")
    if action.attempt >= 2:
        raise Refuse("RETRY_CAP")
    return replace(action, attempt=action.attempt + 1)


def rebuild(action: object) -> Action:
    """Reproduce one public descriptor from its fields or a field dict."""
    if type(action) is not Action:
        return _known(action)
    fresh = _reissue(action)
    if fresh != action:
        raise Refuse("BAD_ACTION")
    return fresh


def _build(
    kind: object,
    *,
    x: object,
    y: object,
    text: object,
    keys: object,
    mode: object,
    surface: object,
    screen: object,
    session: object,
    apps: object,
    allowlist: object,
    manifest: object,
    jail: object,
    captures: object,
    text_chars: object,
    attempt: object = 1,
) -> Action:
    chosen = _kind(kind)
    chosen_mode = _mode(mode)
    px, py = _point(x, y, required=chosen in _POINT_KINDS)
    face = _surface(surface)
    display = _screen(screen)
    label = _session(session)
    listed = _allowlist(allowlist, chosen)
    named = _apps(apps, chosen_mode)
    caps = _make_caps(captures, text_chars)
    body = _body(text, chosen, caps.text_chars)
    chord = _chord(keys, chosen)
    path, grants = _manifest(manifest, jail, chosen_mode)
    return Action(
        schema=SCHEMA,
        kind=chosen,
        code=CONFIRM,
        mode=chosen_mode,
        x=px,
        y=py,
        text=body,
        keys=chord,
        surface=face,
        screen=display,
        session=label,
        apps=named,
        allowlist=listed,
        manifest=path,
        grants=grants,
        caps=caps,
        attempt=_attempt(attempt),
    )


def _reissue(action: Action) -> Action:
    manifest: object = None if action.manifest == "" else action.manifest
    jail: object = None if action.grants == () else PathJail(action.grants)
    return _build(
        action.kind,
        x=action.x,
        y=action.y,
        text=action.text,
        keys=action.keys,
        mode=action.mode,
        surface=action.surface,
        screen=action.screen,
        session=action.session,
        apps=action.apps,
        allowlist=action.allowlist,
        manifest=manifest,
        jail=jail,
        captures=action.caps.requested_captures,
        text_chars=action.caps.requested_text_chars,
        attempt=action.attempt,
    )


def _known(action: object) -> Action:
    if type(action) is Action:
        _audit(action)
        return action
    if type(action) is not dict:
        raise Refuse("BAD_ACTION")
    typed: dict[str, object] = {}
    for key_name, value in action.items():
        if not isinstance(key_name, str):
            raise Refuse("BAD_ACTION")
        typed[key_name] = value
    if not set(typed).issubset(_DICT_KEYS):
        raise Refuse("BAD_ACTION")
    if "kind" not in typed:
        raise Refuse("UNCLASSIFIED")
    return _build(
        typed["kind"],
        x=typed.get("x"),
        y=typed.get("y"),
        text=typed.get("text", ""),
        keys=typed.get("keys", ()),
        mode=typed.get("mode", "standard"),
        surface=typed.get("surface", "background"),
        screen=typed.get("screen", ""),
        session=typed.get("session", ""),
        apps=typed.get("apps", ()),
        allowlist=typed.get("allowlist", _DEFAULT_ALLOWLIST),
        manifest=typed.get("manifest"),
        jail=typed.get("jail"),
        captures=typed.get("captures", POLICY_CAPTURES),
        text_chars=typed.get("text_chars", POLICY_TEXT),
        attempt=typed.get("attempt", 1),
    )


def _audit(action: Action) -> None:
    if type(action.caps) is not Caps:
        raise Refuse("BAD_CAP")
    if not const_eq(action.schema, SCHEMA):
        raise Refuse("BAD_SCHEMA")
    if not const_eq(action.code, CONFIRM):
        raise Refuse("UNCLASSIFIED")
    kind = _kind(action.kind)
    mode = _mode(action.mode)
    if kind != action.kind or mode != action.mode:
        raise Refuse("UNCLASSIFIED")
    fresh = _make_caps(action.caps.requested_captures, action.caps.requested_text_chars)
    if fresh != action.caps:
        raise Refuse("BAD_CAP")
    px, py = _point(action.x, action.y, required=kind in _POINT_KINDS)
    if (px, py) != (action.x, action.y):
        raise Refuse("BAD_COORD")
    if _body(action.text, kind, action.caps.text_chars) != action.text:
        raise Refuse("BAD_TEXT")
    if _chord(action.keys, kind) != action.keys:
        raise Refuse("BAD_KEY")
    if _surface(action.surface) != action.surface:
        raise Refuse("BAD_SURFACE")
    if _screen(action.screen) != action.screen:
        raise Refuse("BAD_SCREEN")
    if _session(action.session) != action.session:
        raise Refuse("BAD_SESSION")
    if _allowlist(action.allowlist, kind) != action.allowlist:
        raise Refuse("BAD_ALLOWLIST")
    if _apps(action.apps, mode) != action.apps:
        raise Refuse("BAD_ALLOWLIST")
    _recheck_manifest(action.manifest, action.grants)
    if mode != "bounded" and action.manifest != "":
        raise Refuse("BAD_MODE")
    if _attempt(action.attempt) != action.attempt:
        raise Refuse("OUT_OF_RANGE")


def _check_caps(caps: Caps) -> None:
    for value in (caps.captures, caps.text_chars, caps.requested_captures, caps.requested_text_chars):
        if isinstance(value, bool) or not isinstance(value, int):
            raise Refuse("NOT_INT")
    if caps.captures < 1 or caps.captures > POLICY_CAPTURES:
        raise Refuse("BAD_CAP")
    if caps.text_chars < 1 or caps.text_chars > POLICY_TEXT:
        raise Refuse("BAD_CAP")
    if caps.requested_captures < 1 or caps.requested_captures > REQUEST_CEILING:
        raise Refuse("OUT_OF_RANGE")
    if caps.requested_text_chars < 1 or caps.requested_text_chars > REQUEST_CEILING:
        raise Refuse("OUT_OF_RANGE")
    expected: list[str] = []
    if caps.requested_captures > POLICY_CAPTURES:
        if caps.captures != POLICY_CAPTURES:
            raise Refuse("BAD_CAP")
        expected.append("captures")
    elif caps.captures != caps.requested_captures:
        raise Refuse("BAD_CAP")
    if caps.requested_text_chars > POLICY_TEXT:
        if caps.text_chars != POLICY_TEXT:
            raise Refuse("BAD_CAP")
        expected.append("text_chars")
    elif caps.text_chars != caps.requested_text_chars:
        raise Refuse("BAD_CAP")
    if caps.clamped != tuple(expected):
        raise Refuse("BAD_CAP")


def _make_caps(captures: object, text_chars: object) -> Caps:
    kept_captures, asked_captures, cut_captures = _clamp(captures, POLICY_CAPTURES)
    kept_text, asked_text, cut_text = _clamp(text_chars, POLICY_TEXT)
    clamped: list[str] = []
    if cut_captures:
        clamped.append("captures")
    if cut_text:
        clamped.append("text_chars")
    return Caps(
        captures=kept_captures,
        text_chars=kept_text,
        requested_captures=asked_captures,
        requested_text_chars=asked_text,
        clamped=tuple(clamped),
    )


def _clamp(raw: object, policy: int) -> tuple[int, int, bool]:
    asked = bound_int(raw, 1, REQUEST_CEILING)
    if asked > policy:
        return policy, asked, True
    return asked, asked, False


def _plain(value: object, limit: int) -> str:
    raw = bound_text(value, limit)
    if secret_shape(raw):
        raise Refuse("SECRET_SHAPE")
    return raw


def _kind(value: object) -> str:
    raw = _plain(value, 32)
    if raw not in _ACTIONS:
        raise Refuse("UNCLASSIFIED")
    return raw


def _mode(value: object) -> str:
    raw = _plain(value, 32)
    if raw not in _MODES:
        raise Refuse("BAD_MODE")
    return raw


def _point(x: object, y: object, *, required: bool) -> tuple[int | None, int | None]:
    if x is None and y is None:
        if required:
            raise Refuse("BAD_COORD")
        return None, None
    if x is None or y is None:
        raise Refuse("BAD_COORD")
    return _coord(x), _coord(y)


def _coord(value: object) -> int:
    try:
        return bound_int(value, COORD_MIN, COORD_MAX)
    except Refuse as refused:
        if refused.code == "OUT_OF_RANGE":
            raise Refuse("BAD_COORD") from None
        raise


def _body(value: object, kind: str, limit: int) -> str:
    if kind != "type":
        if value is None or value == "":
            return ""
        _plain(value, limit)
        raise Refuse("BAD_TEXT")
    raw = _plain(value, limit)
    if raw == "" or raw != raw.strip() or any(ord(char) < 32 for char in raw):
        raise Refuse("BAD_TEXT")
    for pattern in _BLOCKED_TYPE:
        if pattern.search(raw):
            raise Refuse("BLOCKED_TYPE")
    return raw


def _chord(value: object, kind: str) -> tuple[str, ...]:
    if isinstance(value, str) or not isinstance(value, (list, tuple)):
        raise Refuse("BAD_KEY")
    if kind != "key":
        if len(value) != 0:
            raise Refuse("BAD_KEY")
        return ()
    if len(value) == 0 or len(value) > _POLICY_CHORD:
        raise Refuse("BAD_KEY")
    names = tuple(_one_key(item) for item in value)
    if len(set(names)) != len(names):
        raise Refuse("BAD_KEY")
    if _contains_block(names):
        raise Refuse("BLOCKED_KEY")
    return names


def _contains_block(names: tuple[str, ...]) -> bool:
    """True when the pressed set contains a lock, logout, or delete chord."""
    pressed = frozenset(names)
    for blocked in _BLOCKED_CHORDS:
        if blocked <= pressed:
            return True
    return False


def _one_key(value: object) -> str:
    raw = _plain(value, 16)
    if raw != raw.strip() or any(ord(char) < 32 for char in raw):
        raise Refuse("BAD_KEY")
    folded = _ALIASES.get(raw.lower(), raw.lower())
    if folded not in _KEY_NAMES:
        raise Refuse("BAD_KEY")
    return folded


def _surface(value: object) -> str:
    raw = _plain(value, 16)
    if raw not in _SURFACES:
        raise Refuse("BAD_SURFACE")
    return raw


def _screen(value: object) -> str:
    raw = _plain(value, _LABEL)
    if raw == "":
        return ""
    if raw != raw.strip() or any(ord(char) < 32 or char in _PATH_MARKS for char in raw):
        raise Refuse("BAD_SCREEN")
    return raw


def _session(value: object) -> str:
    raw = _plain(value, _LABEL)
    if raw == "":
        return ""
    if _SESSION.fullmatch(raw) is None:
        raise Refuse("BAD_SESSION")
    return raw


def _allowlist(value: object, kind: str) -> tuple[str, ...]:
    if isinstance(value, str) or not isinstance(value, (list, tuple)):
        raise Refuse("BAD_ALLOWLIST")
    if len(value) == 0:
        raise Refuse("EMPTY_ALLOWLIST")
    if len(value) > len(_ACTIONS):
        raise Refuse("BAD_ALLOWLIST")
    seen: set[str] = set()
    for item in value:
        raw = _plain(item, 32)
        if raw not in _ACTIONS:
            raise Refuse("BAD_ALLOWLIST")
        if raw in seen:
            raise Refuse("BAD_ALLOWLIST")
        seen.add(raw)
    if kind not in seen:
        raise Refuse("NOT_LISTED")
    return tuple(sorted(seen))


def _app_name(value: object) -> str:
    raw = _plain(value, _LABEL)
    if raw == "" or raw != raw.strip() or any(ord(char) < 32 or char in _PATH_MARKS for char in raw):
        raise Refuse("BAD_ALLOWLIST")
    return raw


def _apps(value: object, mode: str) -> tuple[str, ...]:
    if isinstance(value, str) or not isinstance(value, (list, tuple)):
        raise Refuse("BAD_ALLOWLIST")
    if len(value) > _POLICY_APPS:
        raise Refuse("BAD_ALLOWLIST")
    seen: set[str] = set()
    for item in value:
        name = _app_name(item)
        if name in seen:
            raise Refuse("BAD_ALLOWLIST")
        seen.add(name)
    named = tuple(sorted(seen))
    if mode == "bounded" and named == ():
        raise Refuse("EMPTY_ALLOWLIST")
    if mode == "standard" and named != ():
        raise Refuse("BAD_ALLOWLIST")
    return named


def _manifest(raw: object, jail: object, mode: str) -> tuple[str, tuple[str, ...]]:
    if raw is None or raw == "":
        if jail is not None:
            raise Refuse("BAD_JAIL")
        return "", ()
    if mode != "bounded":
        raise Refuse("BAD_MODE")
    if not isinstance(jail, PathJail):
        raise Refuse("BAD_JAIL")
    text = _plain(raw, 4096)
    resolved = str(jail.contain(text))
    grants = tuple(str(path) for path in jail.grants)
    _recheck_manifest(resolved, grants)
    return resolved, grants


def _recheck_manifest(manifest: object, grants: object) -> None:
    if not isinstance(manifest, str) or not isinstance(grants, tuple):
        raise Refuse("BAD_PATH")
    if any(not isinstance(item, str) for item in grants):
        raise Refuse("BAD_PATH")
    if manifest == "":
        if grants != ():
            raise Refuse("BAD_PATH")
        return
    if secret_shape(manifest):
        raise Refuse("SECRET_SHAPE")
    if len(grants) == 0:
        raise Refuse("NO_GRANT")
    resolved = str(PathJail(grants).contain(manifest))
    if resolved != manifest:
        raise Refuse("OUTSIDE_GRANT")


def _attempt(value: object) -> int:
    return bound_int(value, 1, 2)


__all__ = [
    "ACTIONS",
    "CONFIRM",
    "COORD_MAX",
    "COORD_MIN",
    "MODES",
    "POLICY_CAPTURES",
    "POLICY_TEXT",
    "REQUEST_CEILING",
    "SCHEMA",
    "STALE_CAPTURE",
    "Action",
    "Caps",
    "classify",
    "click",
    "key",
    "move",
    "rebuild",
    "retry",
    "run",
    "screenshot",
    "type_text",
]
