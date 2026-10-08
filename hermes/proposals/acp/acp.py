"""Editor messages as data. No editor is started and no command is run."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Final

from cosmos_hermes import PathJail, Refuse, bound_int, bound_text, const_eq, redact, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-acp/1"
TEXT_CAP: Final[int] = 32_000
PROTOCOL: Final[int] = 2
NEED_APPROVAL: Final[str] = "NEED_APPROVAL"
AGENT_NAME: Final[str] = "cosmos-hermes"
AGENT_TITLE: Final[str] = "COSMOS Hermes"
AGENT_VERSION: Final[str] = "1"
SESSION_CAP: Final[int] = 32
MESSAGE_CAP: Final[int] = 32
SEEN_CAP: Final[int] = 48
NODE_CAP: Final[int] = 32
DEPTH_CAP: Final[int] = 8
KINDS: Final[tuple[str, ...]] = ("prompt", "tool", "diff", "terminal")
METHODS: Final[tuple[str, ...]] = (
    "initialize",
    "session/cancel",
    "session/close",
    "session/list",
    "session/new",
    "session/prompt",
    "session/resume",
)

_METHOD_CAP: Final[int] = 64
_NAME_CAP: Final[int] = 128
_ID_MAX: Final[int] = 2_147_483_647
_VERSION_MAX: Final[int] = 1_000_000
_INT_MAX: Final[int] = 10**12
_DISPLAY: Final[frozenset[str]] = frozenset({"prompt", "tool", "diff"})
_METHOD_SET: Final[frozenset[str]] = frozenset(METHODS)
_REPLY_METHODS: Final[frozenset[str]] = _METHOD_SET | {"session/update"}
_REPLY_CODES: Final[frozenset[str]] = frozenset({"CANCELLED", "OK"})
_CHOICES: Final[frozenset[str]] = frozenset(
    {"allow_always", "allow_once", "allow_session", "deny", "error", "timeout"}
)
_CHOICE_CODE: Final[dict[str, str]] = {
    "allow_always": "ALLOW_ALWAYS",
    "allow_once": "ALLOW_ONCE",
    "allow_session": "ALLOW_SESSION",
    "deny": "DENY",
    "error": "DENY",
    "timeout": "DENY",
}
_METHOD_SHAPE: Final[re.Pattern[str]] = re.compile(r"^[a-z][a-z0-9/_-]{0,63}$")
_NAME: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z][A-Za-z0-9._-]{0,63}$")
_TITLE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ._-]{0,63}$")
_VERSION: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+-]{0,31}$")
_MODEL: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z][A-Za-z0-9_.:/+@-]{0,63}$")
_SESSION: Final[re.Pattern[str]] = re.compile(r"^sess-[1-9][0-9]{0,8}$")
_MSG: Final[re.Pattern[str]] = re.compile(r"^msg-[1-9][0-9]{0,8}$")
_ID: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
_TOKEN: Final[re.Pattern[str]] = re.compile(
    r"^(?:n:(?:0|[1-9][0-9]{0,9})|s:[A-Za-z0-9._-]{1,64})$"
)
_CONTROL: Final[re.Pattern[str]] = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

__all__ = [
    "AGENT_NAME",
    "AGENT_TITLE",
    "AGENT_VERSION",
    "DEPTH_CAP",
    "KINDS",
    "MESSAGE_CAP",
    "METHODS",
    "NEED_APPROVAL",
    "NODE_CAP",
    "PROTOCOL",
    "SCHEMA",
    "SEEN_CAP",
    "SESSION_CAP",
    "TEXT_CAP",
    "Approval",
    "Desk",
    "DisplayRecord",
    "Exchange",
    "Reply",
    "Session",
    "TerminalRecord",
    "Turn",
    "answer",
    "decide",
    "message",
    "open_desk",
    "rebuild",
]


def _applied(cap: object) -> int:
    """Honor a lower cap. A higher ask stays at the policy cap."""
    if cap is None:
        return TEXT_CAP
    if isinstance(cap, bool) or not isinstance(cap, int) or cap < 1:
        raise Refuse("BAD_LIMIT")
    if cap > TEXT_CAP:
        return TEXT_CAP
    return cap


def _stored(cap: object, policy: object) -> int:
    if isinstance(policy, bool) or not isinstance(policy, int) or policy != TEXT_CAP:
        raise Refuse("BAD_LIMIT")
    if isinstance(cap, bool) or not isinstance(cap, int) or cap < 1 or cap > TEXT_CAP:
        raise Refuse("BAD_LIMIT")
    return cap


def _schema(value: object) -> None:
    if not isinstance(value, str) or value != SCHEMA:
        raise Refuse("BAD_SCHEMA")


def _plain(value: object, cap: int) -> str:
    text = bound_text(value, cap)
    if secret_shape(text):
        raise Refuse("SECRET")
    if _CONTROL.search(text) is not None:
        raise Refuse("BAD_TEXT")
    return text


def _dump(payload: dict[str, object]) -> str:
    try:
        encoded = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    except (TypeError, ValueError):
        raise Refuse("BAD_MESSAGE") from None
    return bound_text(encoded, TEXT_CAP)


def _as_dict(value: object, code: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise Refuse(code)
    out: dict[str, object] = {}
    for key, item in value.items():
        if not isinstance(key, str):
            raise Refuse(code)
        out[key] = item
    return out


def _check(value: object, depth: int) -> None:
    if depth > DEPTH_CAP:
        raise Refuse("TOO_DEEP")
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, float):
        raise Refuse("BAD_MESSAGE")
    if isinstance(value, int):
        bound_int(value, -_INT_MAX, _INT_MAX)
        return
    if isinstance(value, str):
        text = bound_text(value, TEXT_CAP)
        if secret_shape(text):
            raise Refuse("SECRET")
        return
    if isinstance(value, list):
        if len(value) > NODE_CAP:
            raise Refuse("TOO_MANY")
        for item in value:
            _check(item, depth + 1)
        return
    if isinstance(value, dict):
        if len(value) > NODE_CAP:
            raise Refuse("TOO_MANY")
        for key, item in value.items():
            if not isinstance(key, str):
                raise Refuse("BAD_MESSAGE")
            name = bound_text(key, _NAME_CAP)
            if secret_shape(name):
                raise Refuse("SECRET")
            _check(item, depth + 1)
        return
    raise Refuse("BAD_MESSAGE")


def _load(raw: str) -> dict[str, object]:
    try:
        loaded: object = json.loads(raw)
    except json.JSONDecodeError:
        raise Refuse("BAD_MESSAGE") from None
    except RecursionError:
        raise Refuse("TOO_DEEP") from None
    if not isinstance(loaded, dict):
        raise Refuse("BAD_MESSAGE")
    frame = _as_dict(loaded, "BAD_MESSAGE")
    if "error" in frame or "result" in frame:
        raise Refuse("BAD_MESSAGE")
    _check(frame, 1)
    if frame.get("jsonrpc") != "2.0":
        raise Refuse("BAD_MESSAGE")
    return frame


def _method(frame: dict[str, object]) -> str:
    if "method" not in frame:
        raise Refuse("BAD_METHOD")
    label = bound_text(frame["method"], _METHOD_CAP)
    if secret_shape(label):
        raise Refuse("SECRET")
    if _METHOD_SHAPE.fullmatch(label) is None:
        raise Refuse("BAD_METHOD")
    return label


def _request_id(frame: dict[str, object]) -> int | str:
    if "id" not in frame or frame["id"] is None:
        raise Refuse("BAD_ID")
    ident = frame["id"]
    if isinstance(ident, bool) or isinstance(ident, float):
        raise Refuse("BAD_ID")
    if isinstance(ident, int):
        return bound_int(ident, 0, _ID_MAX)
    if isinstance(ident, str):
        text = bound_text(ident, _METHOD_CAP)
        if _ID.fullmatch(text) is None:
            raise Refuse("BAD_ID")
        return text
    raise Refuse("BAD_ID")


def _id_token(request_id: int | str) -> str:
    if isinstance(request_id, int):
        token = f"n:{request_id}"
    else:
        token = f"s:{request_id}"
    if _TOKEN.fullmatch(token) is None:
        raise Refuse("BAD_ID")
    return token


def _params(frame: dict[str, object]) -> dict[str, object]:
    if "params" not in frame:
        raise Refuse("BAD_PARAMS")
    return _as_dict(frame["params"], "BAD_PARAMS")


def _grant_key(jail: PathJail) -> tuple[str, ...]:
    return tuple(path.as_posix() for path in jail.grants)


def _jail(value: object, grants: tuple[str, ...]) -> PathJail:
    if not isinstance(value, PathJail):
        raise Refuse("BAD_JAIL")
    if _grant_key(value) != grants:
        raise Refuse("BAD_JAIL")
    return value


def _allow(value: object) -> tuple[str, ...]:
    # Names may only narrow METHODS. A name outside that set cannot widen it.
    if value is None:
        return METHODS
    if isinstance(value, str) or not isinstance(value, (list, tuple)):
        raise Refuse("BAD_PARAMS")
    if len(value) == 0:
        raise Refuse("EMPTY_ALLOW")
    if len(value) > len(METHODS):
        raise Refuse("TOO_MANY")
    seen: set[str] = set()
    names: list[str] = []
    for item in value:
        label = bound_text(item, _METHOD_CAP)
        if secret_shape(label):
            raise Refuse("SECRET")
        if _METHOD_SHAPE.fullmatch(label) is None or label not in _METHOD_SET:
            raise Refuse("BAD_METHOD")
        if label in seen:
            raise Refuse("DUPLICATE")
        seen.add(label)
        names.append(label)
    names.sort()
    return tuple(names)


def _methods(value: tuple[str, ...]) -> tuple[str, ...]:
    if len(value) == 0:
        raise Refuse("EMPTY_ALLOW")
    if len(value) > len(METHODS):
        raise Refuse("TOO_MANY")
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str):
            raise Refuse("BAD_METHOD")
        if item not in _METHOD_SET:
            raise Refuse("BAD_METHOD")
        if item in seen:
            raise Refuse("DUPLICATE")
        seen.add(item)
    ordered = tuple(sorted(seen))
    if ordered != value:
        raise Refuse("BAD_PARAMS")
    return ordered


def _no_mcp(params: dict[str, object]) -> None:
    if "mcpServers" not in params:
        return
    servers = params["mcpServers"]
    if not isinstance(servers, list):
        raise Refuse("BAD_PARAMS")
    if len(servers) > 0:
        raise Refuse("MCP_REFUSED")


def _no_extra_roots(params: dict[str, object]) -> None:
    if "additionalDirectories" not in params:
        return
    extra = params["additionalDirectories"]
    if not isinstance(extra, list):
        raise Refuse("BAD_PARAMS")
    if len(extra) > 0:
        raise Refuse("UNSUPPORTED")


def _model_label(params: dict[str, object]) -> str:
    if "model" not in params:
        return ""
    if params["model"] is None:
        raise Refuse("BAD_PARAMS")
    label = bound_text(params["model"], _NAME_CAP)
    if secret_shape(label):
        raise Refuse("SECRET")
    if _MODEL.fullmatch(label) is None:
        raise Refuse("BAD_PARAMS")
    return label


def _cwd(params: dict[str, object], jail: PathJail, cap: int) -> str:
    if "cwd" not in params:
        raise Refuse("BAD_PARAMS")
    raw = bound_text(params["cwd"], cap)
    if secret_shape(raw):
        raise Refuse("SECRET")
    return jail.contain(raw).as_posix()


def _session_key(params: dict[str, object]) -> str:
    if "sessionId" not in params:
        raise Refuse("BAD_PARAMS")
    label = bound_text(params["sessionId"], _NAME_CAP)
    if secret_shape(label):
        raise Refuse("SECRET")
    if _SESSION.fullmatch(label) is None:
        raise Refuse("BAD_ID")
    return label


def _blocks(params: dict[str, object], cap: int) -> tuple[str, ...]:
    if "prompt" not in params:
        raise Refuse("BAD_PARAMS")
    raw = params["prompt"]
    if not isinstance(raw, list):
        raise Refuse("BAD_PARAMS")
    if len(raw) == 0:
        raise Refuse("EMPTY")
    if len(raw) > NODE_CAP:
        raise Refuse("TOO_MANY")
    parts: list[str] = []
    total = 0
    for item in raw:
        if not isinstance(item, dict):
            raise Refuse("BAD_CONTENT")
        block = _as_dict(item, "BAD_CONTENT")
        if block.get("type") != "text" or "text" not in block:
            raise Refuse("BAD_CONTENT")
        text = _plain(block["text"], cap)
        if text.strip() == "":
            raise Refuse("EMPTY")
        total += len(text)
        if total > cap:
            raise Refuse("OVERSIZE", str(cap))
        parts.append(text)
    return tuple(parts)


def _info(params: dict[str, object]) -> tuple[str, str, str, int]:
    if "protocolVersion" not in params:
        raise Refuse("BAD_VERSION")
    client_protocol = bound_int(params["protocolVersion"], 1, _VERSION_MAX)
    if "info" not in params:
        raise Refuse("BAD_PARAMS")
    info = _as_dict(params["info"], "BAD_PARAMS")
    if "name" not in info or "version" not in info:
        raise Refuse("BAD_PARAMS")
    name = bound_text(info["name"], _NAME_CAP)
    version = bound_text(info["version"], _NAME_CAP)
    if secret_shape(name) or secret_shape(version):
        raise Refuse("SECRET")
    if _NAME.fullmatch(name) is None or _VERSION.fullmatch(version) is None:
        raise Refuse("BAD_PARAMS")
    title = name
    if "title" in info and info["title"] is not None:
        title = bound_text(info["title"], _NAME_CAP)
        if secret_shape(title):
            raise Refuse("SECRET")
        if _TITLE.fullmatch(title) is None:
            raise Refuse("BAD_PARAMS")
    if "capabilities" in params and params["capabilities"] is not None:
        _as_dict(params["capabilities"], "BAD_PARAMS")
    return name, title, version, client_protocol


def _message_id(number: int) -> str:
    label = f"msg-{number}"
    if _MSG.fullmatch(label) is None:
        raise Refuse("BAD_ID")
    return label


def _session_id(number: int) -> str:
    label = f"sess-{number}"
    if _SESSION.fullmatch(label) is None:
        raise Refuse("BAD_ID")
    return label


def _content(blocks: tuple[str, ...]) -> list[object]:
    rows: list[object] = []
    for block in blocks:
        rows.append({"text": block, "type": "text"})
    return rows


@dataclass(frozen=True, slots=True)
class DisplayRecord:
    """One prompt, tool, or diff line for an editor to render."""

    kind: str
    text: str
    cap: int
    policy_cap: int
    schema: str

    def __post_init__(self) -> None:
        _schema(self.schema)
        applied = _stored(self.cap, self.policy_cap)
        label = _plain(self.kind, _METHOD_CAP)
        if label not in _DISPLAY:
            raise Refuse("BAD_KIND")
        body = _plain(self.text, applied)
        if body.strip() == "":
            raise Refuse("EMPTY")

    def __repr__(self) -> str:
        return (
            "DisplayRecord("
            f"kind={redact(self.kind)!r}, text={redact(self.text)!r}, "
            f"cap={self.cap}, policy_cap={self.policy_cap}, schema={self.schema!r})"
        )


@dataclass(frozen=True, slots=True)
class TerminalRecord:
    """One terminal line. `code` is NEED_APPROVAL. The text is not started."""

    kind: str
    text: str
    code: str
    cap: int
    policy_cap: int
    schema: str

    def __post_init__(self) -> None:
        _schema(self.schema)
        if not isinstance(self.code, str) or self.code != NEED_APPROVAL:
            raise Refuse("BAD_CODE")
        applied = _stored(self.cap, self.policy_cap)
        label = _plain(self.kind, _METHOD_CAP)
        if label != "terminal":
            raise Refuse("BAD_KIND")
        body = _plain(self.text, applied)
        if body.strip() == "":
            raise Refuse("EMPTY")

    def __repr__(self) -> str:
        return (
            "TerminalRecord("
            f"kind={redact(self.kind)!r}, text={redact(self.text)!r}, "
            f"code={self.code!r}, cap={self.cap}, policy_cap={self.policy_cap}, "
            f"schema={self.schema!r})"
        )


@dataclass(frozen=True, slots=True)
class Approval:
    """An editor choice. `runs` and `persisted` stay false."""

    schema: str
    choice: str
    code: str
    runs: bool
    persisted: bool

    def __post_init__(self) -> None:
        _schema(self.schema)
        if self.choice not in _CHOICES:
            raise Refuse("BAD_CHOICE")
        if self.code != _CHOICE_CODE[self.choice]:
            raise Refuse("BAD_CODE")
        if self.runs is not False:
            raise Refuse("NOT_RUN")
        if self.persisted is not False:
            raise Refuse("PERSIST")

    def __repr__(self) -> str:
        return (
            "Approval("
            f"schema={self.schema!r}, choice={redact(self.choice)!r}, "
            f"code={self.code!r}, runs={self.runs!r}, persisted={self.persisted!r})"
        )


@dataclass(frozen=True, slots=True)
class Turn:
    """One inserted user message. Blocks stay text."""

    message_id: str
    blocks: tuple[str, ...]

    def __post_init__(self) -> None:
        if _MSG.fullmatch(self.message_id) is None:
            raise Refuse("BAD_ID")
        if not isinstance(self.blocks, tuple) or len(self.blocks) == 0 or len(self.blocks) > NODE_CAP:
            raise Refuse("BAD_CONTENT")
        total = 0
        for block in self.blocks:
            text = _plain(block, TEXT_CAP)
            if text.strip() == "":
                raise Refuse("EMPTY")
            total += len(text)
            if total > TEXT_CAP:
                raise Refuse("OVERSIZE", str(TEXT_CAP))

    def __repr__(self) -> str:
        shown = tuple(redact(block) for block in self.blocks)
        return f"Turn(message_id={self.message_id!r}, blocks={shown!r})"


@dataclass(frozen=True, slots=True)
class Session:
    """One ACP session. `cancelled` is a flag. Nothing is started."""

    session_id: str
    cwd: str
    model: str
    history: tuple[Turn, ...]
    cancelled: bool
    closed: bool

    def __post_init__(self) -> None:
        if _SESSION.fullmatch(self.session_id) is None:
            raise Refuse("BAD_ID")
        path = bound_text(self.cwd, TEXT_CAP)
        if secret_shape(path):
            raise Refuse("SECRET")
        if self.model != "":
            label = bound_text(self.model, _NAME_CAP)
            if secret_shape(label) or _MODEL.fullmatch(label) is None:
                raise Refuse("BAD_PARAMS")
        if not isinstance(self.history, tuple) or len(self.history) > MESSAGE_CAP:
            raise Refuse("TOO_MANY")
        for turn in self.history:
            if not isinstance(turn, Turn):
                raise Refuse("BAD_PARAMS")
        if not isinstance(self.cancelled, bool) or not isinstance(self.closed, bool):
            raise Refuse("BAD_PARAMS")

    def __repr__(self) -> str:
        return (
            "Session("
            f"session_id={self.session_id!r}, cwd={redact(self.cwd)!r}, "
            f"model={redact(self.model)!r}, history={self.history!r}, "
            f"cancelled={self.cancelled!r}, closed={self.closed!r})"
        )


@dataclass(frozen=True, slots=True)
class Reply:
    """One JSON-RPC object. `sent` is false: nothing is written to a host."""

    schema: str
    method: str
    request_id: str
    body: str
    code: str
    sent: bool
    cap: int
    policy_cap: int

    def __post_init__(self) -> None:
        _schema(self.schema)
        if self.method not in _REPLY_METHODS:
            raise Refuse("BAD_METHOD")
        if self.code not in _REPLY_CODES:
            raise Refuse("BAD_CODE")
        if self.sent is not False:
            raise Refuse("NOT_SENT")
        _stored(self.cap, self.policy_cap)
        if self.method == "session/update":
            if self.request_id != "":
                raise Refuse("BAD_ID")
        elif _TOKEN.fullmatch(self.request_id) is None:
            raise Refuse("BAD_ID")
        body = bound_text(self.body, TEXT_CAP)
        if secret_shape(body):
            raise Refuse("SECRET")
        if body.strip() == "":
            raise Refuse("EMPTY")

    def __repr__(self) -> str:
        return (
            "Reply("
            f"schema={self.schema!r}, method={self.method!r}, "
            f"request_id={self.request_id!r}, body={redact(self.body)!r}, "
            f"code={self.code!r}, sent={self.sent!r}, cap={self.cap}, "
            f"policy_cap={self.policy_cap})"
        )


@dataclass(frozen=True, slots=True)
class Desk:
    """In-memory ACP desk. Sessions are records, not processes."""

    schema: str
    initialized: bool
    protocol: int
    client_name: str
    client_title: str
    client_version: str
    client_protocol: int
    sessions: tuple[Session, ...]
    seen: tuple[str, ...]
    next_message: int
    grants: tuple[str, ...]
    methods: tuple[str, ...]
    cap: int
    policy_cap: int

    def __post_init__(self) -> None:
        _schema(self.schema)
        _stored(self.cap, self.policy_cap)
        _methods(self.methods)
        if not isinstance(self.initialized, bool):
            raise Refuse("BAD_PARAMS")
        if not isinstance(self.grants, tuple) or len(self.grants) == 0:
            raise Refuse("NO_GRANT")
        if not isinstance(self.sessions, tuple) or len(self.sessions) > SESSION_CAP:
            raise Refuse("TOO_MANY")
        if not isinstance(self.seen, tuple) or len(self.seen) > SEEN_CAP:
            raise Refuse("TOO_MANY")
        bound_int(self.next_message, 1, MESSAGE_CAP + 1)
        jail = PathJail(self.grants)
        if self.initialized:
            if self.protocol != PROTOCOL:
                raise Refuse("BAD_VERSION")
            if _NAME.fullmatch(self.client_name) is None:
                raise Refuse("BAD_PARAMS")
            if _TITLE.fullmatch(self.client_title) is None:
                raise Refuse("BAD_PARAMS")
            if _VERSION.fullmatch(self.client_version) is None:
                raise Refuse("BAD_PARAMS")
            bound_int(self.client_protocol, 1, _VERSION_MAX)
        else:
            if self.protocol != 0 or self.client_protocol != 0:
                raise Refuse("BAD_VERSION")
            if self.client_name != "" or self.client_title != "" or self.client_version != "":
                raise Refuse("BAD_PARAMS")
            if len(self.sessions) != 0:
                raise Refuse("NOT_READY")
        seen: set[str] = set()
        for token in self.seen:
            if not isinstance(token, str) or _TOKEN.fullmatch(token) is None:
                raise Refuse("BAD_ID")
            if token in seen:
                raise Refuse("DUPLICATE")
            seen.add(token)
        ids: set[str] = set()
        expected = tuple(_session_id(index) for index in range(1, len(self.sessions) + 1))
        actual: list[str] = []
        for session in self.sessions:
            if not isinstance(session, Session):
                raise Refuse("BAD_PARAMS")
            actual.append(session.session_id)
            held = jail.contain(session.cwd).as_posix()
            if held != session.cwd:
                raise Refuse("MISMATCH")
            for turn in session.history:
                if turn.message_id in ids:
                    raise Refuse("DUPLICATE")
                ids.add(turn.message_id)
        if tuple(actual) != expected:
            raise Refuse("BAD_ID")
        if len(ids) != self.next_message - 1:
            raise Refuse("BAD_PARAMS")

    def __repr__(self) -> str:
        return (
            "Desk("
            f"schema={self.schema!r}, initialized={self.initialized!r}, "
            f"protocol={self.protocol!r}, client_name={redact(self.client_name)!r}, "
            f"client_title={redact(self.client_title)!r}, "
            f"client_version={redact(self.client_version)!r}, "
            f"client_protocol={self.client_protocol!r}, sessions={self.sessions!r}, "
            f"seen={self.seen!r}, next_message={self.next_message!r}, "
            f"grants={tuple(redact(item) for item in self.grants)!r}, "
            f"methods={self.methods!r}, cap={self.cap}, policy_cap={self.policy_cap})"
        )


@dataclass(frozen=True, slots=True)
class Exchange:
    """The next desk, the reply, and notifications that were not sent."""

    desk: Desk
    reply: Reply
    notes: tuple[Reply, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.desk, Desk) or not isinstance(self.reply, Reply):
            raise Refuse("BAD_MESSAGE")
        if not isinstance(self.notes, tuple):
            raise Refuse("BAD_MESSAGE")
        for note in self.notes:
            if not isinstance(note, Reply):
                raise Refuse("BAD_MESSAGE")
            if note.method != "session/update":
                raise Refuse("BAD_METHOD")

    def __repr__(self) -> str:
        return f"Exchange(desk={self.desk!r}, reply={self.reply!r}, notes={self.notes!r})"


def _follow(
    desk: Desk,
    *,
    initialized: bool | None = None,
    protocol: int | None = None,
    client_name: str | None = None,
    client_title: str | None = None,
    client_version: str | None = None,
    client_protocol: int | None = None,
    sessions: tuple[Session, ...] | None = None,
    seen: tuple[str, ...] | None = None,
    next_message: int | None = None,
) -> Desk:
    return Desk(
        schema=SCHEMA,
        initialized=desk.initialized if initialized is None else initialized,
        protocol=desk.protocol if protocol is None else protocol,
        client_name=desk.client_name if client_name is None else client_name,
        client_title=desk.client_title if client_title is None else client_title,
        client_version=desk.client_version if client_version is None else client_version,
        client_protocol=desk.client_protocol if client_protocol is None else client_protocol,
        sessions=desk.sessions if sessions is None else sessions,
        seen=desk.seen if seen is None else seen,
        next_message=desk.next_message if next_message is None else next_message,
        grants=desk.grants,
        methods=desk.methods,
        cap=desk.cap,
        policy_cap=TEXT_CAP,
    )


def _at(sessions: tuple[Session, ...], index: int) -> Session:
    if isinstance(index, bool) or not isinstance(index, int):
        raise Refuse("UNKNOWN_SESSION")
    if index < 0 or index >= len(sessions):
        raise Refuse("UNKNOWN_SESSION")
    return sessions[index]


def _index(desk: Desk, session_id: str) -> int:
    found = -1
    for index, item in enumerate(desk.sessions):
        if const_eq(item.session_id, session_id):
            if found != -1:
                raise Refuse("DUPLICATE")
            found = index
    if found < 0:
        raise Refuse("UNKNOWN_SESSION")
    return found


def _put(desk: Desk, index: int, session: Session) -> tuple[Session, ...]:
    _at(desk.sessions, index)
    rows = list(desk.sessions)
    rows[index] = session
    return tuple(rows)


def _reply(
    method: str,
    request_id: str,
    payload: dict[str, object],
    cap: int,
    code: str,
) -> Reply:
    return Reply(
        schema=SCHEMA,
        method=method,
        request_id=request_id,
        body=_dump(payload),
        code=code,
        sent=False,
        cap=cap,
        policy_cap=TEXT_CAP,
    )


def _result(request_id: int | str, result: dict[str, object], method: str, token: str, cap: int) -> Reply:
    payload: dict[str, object] = {"id": request_id, "jsonrpc": "2.0", "result": result}
    return _reply(method, token, payload, cap, "OK")


def _user_note(session_id: str, turn: Turn, cap: int) -> Reply:
    update: dict[str, object] = {
        "content": _content(turn.blocks),
        "messageId": turn.message_id,
        "sessionUpdate": "user_message",
    }
    params: dict[str, object] = {"sessionId": session_id, "update": update}
    payload: dict[str, object] = {"jsonrpc": "2.0", "method": "session/update", "params": params}
    return _reply("session/update", "", payload, cap, "OK")


def _cancel_note(session_id: str, cap: int) -> Reply:
    update: dict[str, object] = {
        "sessionUpdate": "state_update",
        "state": "idle",
        "stopReason": "cancelled",
    }
    params: dict[str, object] = {"sessionId": session_id, "update": update}
    payload: dict[str, object] = {"jsonrpc": "2.0", "method": "session/update", "params": params}
    return _reply("session/update", "", payload, cap, "CANCELLED")


def _stamp(desk: Desk, token: str) -> tuple[str, ...]:
    if token in set(desk.seen):
        raise Refuse("DUPLICATE")
    if len(desk.seen) >= SEEN_CAP:
        raise Refuse("TOO_MANY")
    return desk.seen + (token,)


def _initialize(desk: Desk, frame: dict[str, object], request_id: int | str, token: str) -> Exchange:
    if desk.initialized:
        raise Refuse("ALREADY")
    name, title, version, client_protocol = _info(_params(frame))
    result: dict[str, object] = {
        "authMethods": [],
        "capabilities": {"session": {}},
        "info": {"name": AGENT_NAME, "title": AGENT_TITLE, "version": AGENT_VERSION},
        "protocolVersion": PROTOCOL,
    }
    reply = _result(request_id, result, "initialize", token, desk.cap)
    nxt = _follow(
        desk,
        initialized=True,
        protocol=PROTOCOL,
        client_name=name,
        client_title=title,
        client_version=version,
        client_protocol=client_protocol,
        seen=_stamp(desk, token),
    )
    return Exchange(desk=nxt, reply=reply, notes=())


def _new(
    desk: Desk,
    frame: dict[str, object],
    jail: PathJail,
    request_id: int | str,
    token: str,
) -> Exchange:
    if len(desk.sessions) >= SESSION_CAP:
        raise Refuse("TOO_MANY")
    params = _params(frame)
    _no_mcp(params)
    _no_extra_roots(params)
    session = Session(
        session_id=_session_id(len(desk.sessions) + 1),
        cwd=_cwd(params, jail, desk.cap),
        model=_model_label(params),
        history=(),
        cancelled=False,
        closed=False,
    )
    result: dict[str, object] = {"sessionId": session.session_id}
    reply = _result(request_id, result, "session/new", token, desk.cap)
    nxt = _follow(desk, sessions=desk.sessions + (session,), seen=_stamp(desk, token))
    return Exchange(desk=nxt, reply=reply, notes=())


def _list(desk: Desk, frame: dict[str, object], request_id: int | str, token: str) -> Exchange:
    params = _params(frame)
    if len(params) > 0:
        raise Refuse("BAD_PARAMS")
    rows: list[object] = []
    for session in desk.sessions:
        if session.closed:
            continue
        rows.append(
            {
                "cwd": session.cwd,
                "model": session.model,
                "sessionId": session.session_id,
            }
        )
    reply = _result(request_id, {"sessions": rows}, "session/list", token, desk.cap)
    return Exchange(desk=_follow(desk, seen=_stamp(desk, token)), reply=reply, notes=())


def _prompt(desk: Desk, frame: dict[str, object], request_id: int | str, token: str) -> Exchange:
    if desk.next_message > MESSAGE_CAP:
        raise Refuse("TOO_MANY")
    params = _params(frame)
    session_id = _session_key(params)
    index = _index(desk, session_id)
    current = _at(desk.sessions, index)
    if current.closed:
        raise Refuse("CLOSED")
    turn = Turn(message_id=_message_id(desk.next_message), blocks=_blocks(params, desk.cap))
    updated = Session(
        session_id=current.session_id,
        cwd=current.cwd,
        model=current.model,
        history=current.history + (turn,),
        cancelled=False,
        closed=False,
    )
    result: dict[str, object] = {"messageId": turn.message_id}
    reply = _result(request_id, result, "session/prompt", token, desk.cap)
    note = _user_note(updated.session_id, turn, desk.cap)
    nxt = _follow(
        desk,
        sessions=_put(desk, index, updated),
        seen=_stamp(desk, token),
        next_message=desk.next_message + 1,
    )
    return Exchange(desk=nxt, reply=reply, notes=(note,))


def _close(
    desk: Desk,
    frame: dict[str, object],
    jail: PathJail,
    request_id: int | str,
    token: str,
) -> Exchange:
    params = _params(frame)
    _no_mcp(params)
    session_id = _session_key(params)
    index = _index(desk, session_id)
    current = _at(desk.sessions, index)
    if current.closed:
        raise Refuse("STALE")
    if "cwd" in params:
        held = _cwd(params, jail, desk.cap)
        if not const_eq(held, current.cwd):
            raise Refuse("MISMATCH")
    updated = Session(
        session_id=current.session_id,
        cwd=current.cwd,
        model=current.model,
        history=current.history,
        cancelled=True,
        closed=True,
    )
    reply = _result(request_id, {}, "session/close", token, desk.cap)
    nxt = _follow(desk, sessions=_put(desk, index, updated), seen=_stamp(desk, token))
    return Exchange(desk=nxt, reply=reply, notes=())


def _resume(
    desk: Desk,
    frame: dict[str, object],
    jail: PathJail,
    request_id: int | str,
    token: str,
) -> Exchange:
    params = _params(frame)
    _no_mcp(params)
    _no_extra_roots(params)
    session_id = _session_key(params)
    index = _index(desk, session_id)
    current = _at(desk.sessions, index)
    if current.closed:
        raise Refuse("STALE")
    held = _cwd(params, jail, desk.cap)
    if not const_eq(held, current.cwd):
        raise Refuse("MISMATCH")
    replay = False
    if "replayFrom" in params and params["replayFrom"] is not None:
        cursor = _as_dict(params["replayFrom"], "BAD_PARAMS")
        if set(cursor) != {"type"} or cursor.get("type") != "start":
            raise Refuse("BAD_PARAMS")
        replay = True
    notes: tuple[Reply, ...] = ()
    if replay:
        rows = tuple(_user_note(current.session_id, turn, desk.cap) for turn in current.history)
        notes = rows
    reply = _result(request_id, {}, "session/resume", token, desk.cap)
    nxt = _follow(desk, seen=_stamp(desk, token))
    return Exchange(desk=nxt, reply=reply, notes=notes)


def _cancel(desk: Desk, frame: dict[str, object]) -> Exchange:
    if "id" in frame:
        raise Refuse("BAD_NOTIFY")
    if not desk.initialized:
        raise Refuse("NOT_READY")
    params = _params(frame)
    session_id = _session_key(params)
    index = _index(desk, session_id)
    current = _at(desk.sessions, index)
    if current.closed:
        raise Refuse("CLOSED")
    updated = Session(
        session_id=current.session_id,
        cwd=current.cwd,
        model=current.model,
        history=current.history,
        cancelled=True,
        closed=False,
    )
    reply = _cancel_note(updated.session_id, desk.cap)
    nxt = _follow(desk, sessions=_put(desk, index, updated))
    return Exchange(desk=nxt, reply=reply, notes=())


def rebuild(
    sessions: tuple[Session, ...],
    seen: tuple[str, ...],
    *,
    initialized: bool,
    protocol: int,
    client_name: str,
    client_title: str,
    client_version: str,
    client_protocol: int,
    next_message: int,
    grants: tuple[str, ...],
    methods: tuple[str, ...],
    cap: int,
) -> Desk:
    """Build a desk from public records. The same records return the same desk."""
    copied: list[Session] = []
    for session in sessions:
        if not isinstance(session, Session):
            raise Refuse("BAD_PARAMS")
        turns = tuple(Turn(turn.message_id, turn.blocks) for turn in session.history)
        copied.append(
            Session(
                session_id=session.session_id,
                cwd=session.cwd,
                model=session.model,
                history=turns,
                cancelled=session.cancelled,
                closed=session.closed,
            )
        )
    return Desk(
        schema=SCHEMA,
        initialized=initialized,
        protocol=protocol,
        client_name=client_name,
        client_title=client_title,
        client_version=client_version,
        client_protocol=client_protocol,
        sessions=tuple(copied),
        seen=seen,
        next_message=next_message,
        grants=grants,
        methods=methods,
        cap=cap,
        policy_cap=TEXT_CAP,
    )


def open_desk(jail: object, cap: object = None, allow: object = None) -> Desk:
    """Bind a path grant and a method allowlist. Nothing is listening."""
    if not isinstance(jail, PathJail):
        raise Refuse("BAD_JAIL")
    applied = _applied(cap)
    grants = _grant_key(jail)
    for grant in grants:
        bound_text(grant, TEXT_CAP)
        if secret_shape(grant):
            raise Refuse("SECRET")
    return Desk(
        schema=SCHEMA,
        initialized=False,
        protocol=0,
        client_name="",
        client_title="",
        client_version="",
        client_protocol=0,
        sessions=(),
        seen=(),
        next_message=1,
        grants=grants,
        methods=_allow(allow),
        cap=applied,
        policy_cap=TEXT_CAP,
    )


def answer(desk: object, raw: object, jail: object) -> Exchange:
    """Parse one editor message and return the next desk plus a reply."""
    if not isinstance(desk, Desk):
        raise Refuse("BAD_MESSAGE")
    held = _jail(jail, desk.grants)
    frame = _load(bound_text(raw, desk.cap))
    method = _method(frame)
    if method not in set(desk.methods):
        raise Refuse("UNKNOWN_METHOD")
    if method == "session/cancel":
        return _cancel(desk, frame)
    request_id = _request_id(frame)
    token = _id_token(request_id)
    if token in set(desk.seen):
        raise Refuse("DUPLICATE")
    if method == "initialize":
        return _initialize(desk, frame, request_id, token)
    if not desk.initialized:
        raise Refuse("NOT_READY")
    if method == "session/new":
        return _new(desk, frame, held, request_id, token)
    if method == "session/list":
        return _list(desk, frame, request_id, token)
    if method == "session/prompt":
        return _prompt(desk, frame, request_id, token)
    if method == "session/close":
        return _close(desk, frame, held, request_id, token)
    if method == "session/resume":
        return _resume(desk, frame, held, request_id, token)
    raise Refuse("UNKNOWN_METHOD")


def message(kind: object, text: object, cap: object = None) -> DisplayRecord | TerminalRecord:
    """Classify one editor line. A terminal line is NEED_APPROVAL and is not run."""
    applied = _applied(cap)
    label = _plain(kind, _METHOD_CAP)
    if label not in _DISPLAY and label != "terminal":
        raise Refuse("BAD_MESSAGE")
    body = _plain(text, applied)
    if body.strip() == "":
        raise Refuse("EMPTY")
    if label == "terminal":
        return TerminalRecord(
            kind=label,
            text=body,
            code=NEED_APPROVAL,
            cap=applied,
            policy_cap=TEXT_CAP,
            schema=SCHEMA,
        )
    return DisplayRecord(
        kind=label,
        text=body,
        cap=applied,
        policy_cap=TEXT_CAP,
        schema=SCHEMA,
    )


def decide(choice: object) -> Approval:
    """Record an approval choice. Timeout and error deny. The line is not run."""
    label = bound_text(choice, _METHOD_CAP)
    if secret_shape(label):
        raise Refuse("SECRET")
    if label not in _CHOICES:
        raise Refuse("BAD_CHOICE")
    return Approval(
        schema=SCHEMA,
        choice=label,
        code=_CHOICE_CODE[label],
        runs=False,
        persisted=False,
    )
