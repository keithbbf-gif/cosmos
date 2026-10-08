"""Dashboard panels as a projection. Mutations are descriptors. No listener is started."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Final, cast

from cosmos_hermes import Refuse, bound_int, bound_text, const_eq, secret_shape

SCHEMA: Final = "cosmos-hermes-web_dashboard/1"
LOOPBACK: Final = "127.0.0.1"
DEFAULT_PORT: Final = 9119
ROW_CAP: Final = 20
WIDGET_CAP: Final = 8
VALUE_CAP: Final = 400
HOST_CAP: Final = 253
SCAN_CAP: Final = 64
NONCE_CAP: Final = 128
ACTION_CAP: Final = 64
BODY_CAP: Final = 400
RETRY_FAILURE: Final = "BAD_NONCE"
APPROVED: Final = "APPROVED"
DISPLAY: Final = "display"

_WIDGET: Final = re.compile(r"^[a-z0-9-]{1,32}$")
_PROFILE: Final = re.compile(r"^[a-z0-9-]{1,32}$")
_NONCE: Final = re.compile(r"^[A-Za-z0-9_\-]{8,128}$")
_GRANT_ID: Final = re.compile(r"^[A-Za-z0-9_.:\-]{1,80}$")
_SHA: Final = re.compile(r"^[0-9a-f]{64}$")
_IMPORT_LINE: Final = re.compile(r"(?m)^\s*import\s+([A-Za-z0-9_., \t]+)")
_FROM_LINE: Final = re.compile(
    r"(?m)^\s*from\s+([A-Za-z_][A-Za-z0-9_\.]*)\s+import\s+([A-Za-z0-9_, \t]+)"
)
# A whole identifier, then a call. `empty(` and `eggshell(` do not match.
_CALL_EXEC: Final = re.compile(
    r"(?<![A-Za-z0-9_])(?:pty|shell)\s*\("
    r"|"
    r"(?<![A-Za-z0-9_])(?:pty|shell|os|subprocess)\s*\.\s*"
    r"(?:spawn|system|popen|Popen|call|run)\s*\("
)
_HOST_CHARS: Final = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.:-"
)
_EXEC_PANELS: Final[frozenset[str]] = frozenset({"pty", "shell"})
_EXEC_IMPORTS: Final[frozenset[str]] = frozenset({"pty", "shell", "subprocess"})
_OS_CALLS: Final[frozenset[str]] = frozenset({"system", "popen"})
_FIELDS: Final[dict[str, tuple[str, ...]]] = {
    "status": ("version", "gateway", "active_sessions", "memory", "disk"),
    "chat": ("session", "workspace", "profile"),
    "config": ("section", "field", "value"),
    "env": ("key", "state", "preview"),
    "sessions": ("title", "source", "model", "messages", "preview"),
    "logs": ("file", "level", "component", "line"),
    "analytics": ("day", "sessions", "input_tokens", "output_tokens", "cost"),
    "cron": ("name", "schedule", "state", "deliver"),
    "profiles": ("name", "model", "skills", "gateway"),
    "skills": ("name", "category", "enabled"),
    "mcp": ("name", "enabled", "transport"),
    "webhooks": ("name", "events", "enabled"),
    "pairing": ("platform", "user", "state"),
    "channels": ("platform", "enabled", "connected"),
    "system": ("host", "gateway", "memory", "disk"),
    "spend": ("card", "note", "amount"),
    "queue": ("name", "note", "state"),
    "leases": ("session", "holder", "note"),
}
_FIELD_SET: Final[dict[str, frozenset[str]]] = {
    name: frozenset(fields) for name, fields in _FIELDS.items()
}
PANELS: Final = tuple(_FIELDS)
_ACTIONS: Final[frozenset[str]] = frozenset(
    {
        "config.save",
        "config.import",
        "env.set",
        "env.delete",
        "session.rename",
        "session.delete",
        "session.prune",
        "cron.create",
        "cron.pause",
        "cron.resume",
        "cron.trigger",
        "cron.edit",
        "cron.delete",
        "skill.toggle",
        "skill.install",
        "mcp.add",
        "mcp.remove",
        "mcp.toggle",
        "webhook.create",
        "webhook.delete",
        "webhook.toggle",
        "pairing.approve",
        "pairing.revoke",
        "pairing.clear",
        "channel.configure",
        "channel.toggle",
        "gateway.restart",
        "hook.create",
        "hook.delete",
        "memory.reset",
        "chat.open",
        "widget.add",
    }
)


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _root_name(token: str) -> str:
    head = token.strip().split(" ", 1)[0]
    return head.split(".", 1)[0]


def _exec_source(text: str) -> bool:
    """True when `text` imports or calls a pty or a shell. Not a substring test."""
    for match in _IMPORT_LINE.finditer(text):
        clause = match.group(1)
        if clause is None:
            continue
        for part in clause.split(","):
            if _root_name(part) in _EXEC_IMPORTS:
                return True
    for match in _FROM_LINE.finditer(text):
        module = match.group(1)
        names = match.group(2)
        if module is None or names is None:
            continue
        root = module.split(".", 1)[0]
        if root in _EXEC_IMPORTS:
            return True
        if root == "os":
            for part in names.split(","):
                if _root_name(part) in _OS_CALLS:
                    return True
    return _CALL_EXEC.search(text) is not None


def _panel_name(name: object) -> str:
    text = bound_text(name, SCAN_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    if text in _FIELD_SET:
        return text
    if text in _EXEC_PANELS or _exec_source(text):
        raise Refuse("BAD_PANEL")
    raise Refuse("UNKNOWN_PANEL")


def _profile(value: object) -> str:
    text = bound_text(value, SCAN_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    if _PROFILE.fullmatch(text) is None:
        raise Refuse("BAD_PROFILE")
    return text


def _key(panel: str, key: object) -> str:
    text = bound_text(key, SCAN_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    fields = _FIELD_SET.get(panel)
    if fields is None or text not in fields:
        raise Refuse("BAD_KEY")
    return text


def _value(value: object) -> str:
    text = bound_text(value, VALUE_CAP)
    if text == "":
        raise Refuse("BAD_ROW")
    if secret_shape(text):
        raise Refuse("SECRET")
    return text


def _action(action: object) -> str:
    text = bound_text(action, ACTION_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    if text == "":
        raise Refuse("BAD_ACTION")
    if text not in _ACTIONS:
        raise Refuse("UNCLASSIFIED")
    return text


def _nonce_shape(nonce: object, *, empty_code: str) -> str:
    if nonce is None:
        raise Refuse(empty_code)
    text = bound_text(nonce, NONCE_CAP)
    if text == "":
        raise Refuse(empty_code)
    if secret_shape(text):
        raise Refuse("SECRET")
    if _NONCE.fullmatch(text) is None:
        raise Refuse("BAD_NONCE")
    return text


def _widget_name(name: object) -> str:
    text = bound_text(name, SCAN_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    if _WIDGET.fullmatch(text) is None:
        raise Refuse("BAD_WIDGET")
    return text


def _public_grant(value: object) -> bool:
    if value is False or value is None:
        return False
    if value is True:
        return True
    if isinstance(value, str):
        text = bound_text(value, 80)
        if text == "":
            raise Refuse("BAD_GRANT")
        if secret_shape(text):
            raise Refuse("SECRET")
        if _GRANT_ID.fullmatch(text) is None:
            raise Refuse("BAD_GRANT")
        return True
    raise Refuse("BAD_GRANT")


def _widget_caps(cap: object) -> tuple[int, int, bool]:
    """Return applied cap, asked cap, and whether the ask was lowered."""
    if cap is None:
        return WIDGET_CAP, WIDGET_CAP, False
    if isinstance(cap, bool) or not isinstance(cap, int):
        raise Refuse("NOT_INT")
    if cap < 1:
        raise Refuse("BAD_LIMIT")
    if cap > WIDGET_CAP:
        return WIDGET_CAP, cap, True
    return cap, cap, False


def _row_window(limit: object) -> tuple[int, int, bool]:
    """Return applied limit, asked limit, and whether the ask was lowered."""
    if limit is None:
        return ROW_CAP, ROW_CAP, False
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise Refuse("NOT_INT")
    if limit < 1:
        raise Refuse("OUT_OF_RANGE", f"1..{ROW_CAP}")
    if limit > ROW_CAP:
        return ROW_CAP, limit, True
    return limit, limit, False


def _as_readings(rows: object) -> tuple[Reading, ...]:
    if isinstance(rows, (str, bytes)) or not isinstance(rows, Sequence):
        raise Refuse("BAD_ROW")
    sequence = cast(Sequence[object], rows)
    admitted: list[Reading] = []
    for row in sequence:
        if not isinstance(row, Reading):
            raise Refuse("BAD_ROW")
        admitted.append(row)
    return tuple(admitted)


def _group(rows: tuple[Reading, ...]) -> dict[tuple[str, str], tuple[Reading, ...]]:
    grouped: dict[tuple[str, str], list[Reading]] = {}
    for row in rows:
        key = (row.panel, row.profile)
        bucket = grouped.get(key)
        if bucket is None:
            grouped[key] = [row]
        else:
            bucket.append(row)
    return {key: tuple(bucket) for key, bucket in grouped.items()}


def _window(rows: tuple[Reading, ...], applied: int) -> tuple[Reading, ...]:
    """Prefix that fits the row window. Later rows of this bucket do not fit."""
    if applied >= len(rows):
        return rows
    chosen: list[Reading] = []
    for row in rows:
        if len(chosen) >= applied:
            break
        chosen.append(row)
    return tuple(chosen)


@dataclass(frozen=True, slots=True)
class Panel:
    """One read-only page description. It carries no nonce."""

    name: str
    fields: tuple[str, ...]
    schema: str

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        if self.name not in _FIELD_SET:
            raise Refuse("UNKNOWN_PANEL")
        fields = _FIELDS.get(self.name)
        if fields is None or not isinstance(self.fields, tuple) or self.fields != fields:
            raise Refuse("BAD_PANEL")


@dataclass(frozen=True, slots=True)
class Reading:
    """One caller-supplied cell. Secret-shaped text is refused, not stored."""

    panel: str
    key: str
    value: str
    profile: str = "default"

    def __post_init__(self) -> None:
        panel = _panel_name(self.panel)
        key = _key(panel, self.key)
        profile = _profile(self.profile)
        value = _value(self.value)
        if (
            panel != self.panel
            or key != self.key
            or profile != self.profile
            or value != self.value
        ):
            raise Refuse("BAD_ROW")


@dataclass(frozen=True, slots=True)
class PanelView:
    """Measured rows for one panel and profile. `cap` is policy and does not rise."""

    name: str
    profile: str
    rows: tuple[Reading, ...]
    cap: int
    limit: int
    asked_limit: int
    capped: bool
    schema: str

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        if self.name not in _FIELD_SET:
            raise Refuse("UNKNOWN_PANEL")
        if _PROFILE.fullmatch(self.profile) is None:
            raise Refuse("BAD_PROFILE")
        if type(self.cap) is not int or self.cap != ROW_CAP:
            raise Refuse("BAD_LIMIT")
        if isinstance(self.limit, bool) or not isinstance(self.limit, int):
            raise Refuse("NOT_INT")
        if isinstance(self.asked_limit, bool) or not isinstance(self.asked_limit, int):
            raise Refuse("NOT_INT")
        if not isinstance(self.capped, bool):
            raise Refuse("NOT_BOOL")
        if self.limit < 1 or self.limit > ROW_CAP:
            raise Refuse("OUT_OF_RANGE", f"1..{ROW_CAP}")
        if self.asked_limit < 1:
            raise Refuse("OUT_OF_RANGE", f"1..{ROW_CAP}")
        if self.capped:
            if self.asked_limit <= ROW_CAP or self.limit != ROW_CAP:
                raise Refuse("BAD_LIMIT")
        elif self.asked_limit != self.limit:
            raise Refuse("BAD_LIMIT")
        if not isinstance(self.rows, tuple) or len(self.rows) > self.limit:
            raise Refuse("BAD_ROW")
        for row in self.rows:
            if (
                not isinstance(row, Reading)
                or row.panel != self.name
                or row.profile != self.profile
            ):
                raise Refuse("BAD_ROW")


@dataclass(frozen=True, slots=True)
class Projection:
    """A measured replacement of the panel rows."""

    schema: str
    count: int
    cap: int

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        if isinstance(self.count, bool) or not isinstance(self.count, int) or self.count < 0:
            raise Refuse("BAD_ROW")
        if type(self.cap) is not int or self.cap != ROW_CAP:
            raise Refuse("BAD_LIMIT")


@dataclass(frozen=True, slots=True)
class Policy:
    """Widget and row ceilings. A higher widget ask is ignored and recorded."""

    widget_cap: int
    applied_widget_cap: int
    asked_widget_cap: int
    widget_capped: bool
    row_cap: int
    schema: str

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        if type(self.widget_cap) is not int or self.widget_cap != WIDGET_CAP:
            raise Refuse("BAD_LIMIT")
        if type(self.row_cap) is not int or self.row_cap != ROW_CAP:
            raise Refuse("BAD_LIMIT")
        if isinstance(self.applied_widget_cap, bool) or not isinstance(self.applied_widget_cap, int):
            raise Refuse("NOT_INT")
        if isinstance(self.asked_widget_cap, bool) or not isinstance(self.asked_widget_cap, int):
            raise Refuse("NOT_INT")
        if not isinstance(self.widget_capped, bool):
            raise Refuse("NOT_BOOL")
        if self.applied_widget_cap < 1 or self.applied_widget_cap > WIDGET_CAP:
            raise Refuse("BAD_LIMIT")
        if self.widget_capped:
            if self.asked_widget_cap <= WIDGET_CAP or self.applied_widget_cap != WIDGET_CAP:
                raise Refuse("BAD_LIMIT")
        elif self.asked_widget_cap != self.applied_widget_cap:
            raise Refuse("BAD_LIMIT")


@dataclass(frozen=True, slots=True)
class Widget:
    """One display id accepted into the projection."""

    name: str
    cap: int
    asked_cap: int
    capped: bool
    count: int
    schema: str

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        if secret_shape(self.name):
            raise Refuse("SECRET")
        if _WIDGET.fullmatch(self.name) is None:
            raise Refuse("BAD_WIDGET")
        if isinstance(self.cap, bool) or not isinstance(self.cap, int):
            raise Refuse("NOT_INT")
        if isinstance(self.asked_cap, bool) or not isinstance(self.asked_cap, int):
            raise Refuse("NOT_INT")
        if isinstance(self.count, bool) or not isinstance(self.count, int):
            raise Refuse("NOT_INT")
        if not isinstance(self.capped, bool):
            raise Refuse("NOT_BOOL")
        if self.cap < 1 or self.cap > WIDGET_CAP:
            raise Refuse("BAD_LIMIT")
        if self.count < 1 or self.count > self.cap:
            raise Refuse("AT_CAP")
        if self.capped:
            if self.asked_cap <= WIDGET_CAP or self.cap != WIDGET_CAP:
                raise Refuse("BAD_LIMIT")
        elif self.asked_cap != self.cap:
            raise Refuse("BAD_LIMIT")


@dataclass(frozen=True, slots=True)
class Grant:
    """Human approval for one action. The nonce itself is not kept on the record."""

    action: str
    nonce_sha: str
    schema: str

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        if self.action not in _ACTIONS:
            raise Refuse("UNCLASSIFIED")
        if _SHA.fullmatch(self.nonce_sha) is None:
            raise Refuse("BAD_NONCE")


@dataclass(frozen=True, slots=True)
class Mutation:
    """Approved write descriptor. Nothing is written and no process is started."""

    action: str
    nonce_sha: str
    code: str
    schema: str

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        if self.code != APPROVED:
            raise Refuse("BAD_CODE")
        if self.action not in _ACTIONS:
            raise Refuse("UNCLASSIFIED")
        if _SHA.fullmatch(self.nonce_sha) is None:
            raise Refuse("BAD_NONCE")


@dataclass(frozen=True, slots=True)
class BindPlan:
    """Later listen descriptor. Loopback is only 127.0.0.1 and needs no auth."""

    host: str
    port: int
    loopback: bool
    auth_required: bool
    public_grant: bool
    insecure_ignored: bool
    schema: str

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        if (
            not isinstance(self.loopback, bool)
            or not isinstance(self.auth_required, bool)
            or not isinstance(self.public_grant, bool)
            or not isinstance(self.insecure_ignored, bool)
        ):
            raise Refuse("NOT_BOOL")
        if isinstance(self.port, bool) or not isinstance(self.port, int):
            raise Refuse("NOT_INT")
        if self.port < 1 or self.port > 65535:
            raise Refuse("OUT_OF_RANGE", "1..65535")
        if self.host == "" or any(ch not in _HOST_CHARS for ch in self.host):
            raise Refuse("BAD_HOST")
        if secret_shape(self.host):
            raise Refuse("SECRET")
        if self.loopback != (self.host == LOOPBACK):
            raise Refuse("BAD_HOST")
        if self.loopback and self.auth_required:
            raise Refuse("PUBLIC_BIND")
        if not self.loopback and (not self.public_grant or not self.auth_required):
            raise Refuse("PUBLIC_BIND")


@dataclass(frozen=True, slots=True)
class Display:
    """Panel text that does not import or call a pty or a shell."""

    kind: str
    schema: str

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        kind = bound_text(self.kind, SCAN_CAP)
        if secret_shape(kind):
            raise Refuse("SECRET")
        if kind != DISPLAY:
            raise Refuse("BAD_PANEL")


def panels() -> tuple[Panel, ...]:
    """Return every page description. No nonce and no projection are required."""
    return tuple(panel(name) for name in PANELS)


def panel(name: object) -> Panel:
    """Return one page description. No nonce is required.

    `pty` and `shell` refuse. A name that only contains those letters does not.
    """
    checked = _panel_name(name)
    fields = _FIELDS.get(checked)
    if fields is None:
        raise Refuse("UNKNOWN_PANEL")
    return Panel(name=checked, fields=fields, schema=SCHEMA)


def screen(body: object) -> Display:
    """Accept display text. An import or a call of pty or shell is `BAD_PANEL`.

    The body is not stored and is not executed. `empty` and `eggshell` are display.
    """
    text = bound_text(body, BODY_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    if _exec_source(text):
        raise Refuse("BAD_PANEL")
    return Display(kind=DISPLAY, schema=SCHEMA)


def check_bind(
    host: object,
    public_grant: object = False,
    *,
    port: object = None,
    insecure: object = False,
) -> BindPlan:
    """Accept only 127.0.0.1 unless `public_grant` is set. No listener is opened.

    `insecure` does not weaken the check. A true value is recorded and ignored.
    """
    text = bound_text(host, HOST_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    if text == "" or any(ch not in _HOST_CHARS for ch in text):
        raise Refuse("BAD_HOST")
    granted = _public_grant(public_grant)
    if not isinstance(insecure, bool):
        raise Refuse("NOT_BOOL")
    applied_port = DEFAULT_PORT if port is None else bound_int(port, 1, 65535)
    loopback = text == LOOPBACK
    if not loopback and not granted:
        raise Refuse("PUBLIC_BIND")
    return BindPlan(
        host=text,
        port=applied_port,
        loopback=loopback,
        auth_required=not loopback,
        public_grant=granted,
        insecure_ignored=insecure,
        schema=SCHEMA,
    )


class Dashboard:
    """In-memory panel projection, widget names, and one-use mutation grants."""

    __slots__ = (
        "_rows",
        "_index",
        "_widgets",
        "_widget_ids",
        "_grants",
        "_used",
        "_retries",
        "_applied_cap",
        "_asked_cap",
        "_capped",
    )

    def __init__(self, widget_cap: object = None) -> None:
        applied, asked, capped = _widget_caps(widget_cap)
        self._rows: tuple[Reading, ...] | None = None
        self._index: dict[tuple[str, str], tuple[Reading, ...]] | None = None
        self._widgets: tuple[str, ...] = ()
        self._widget_ids: set[str] = set()
        self._grants: dict[str, str] = {}
        self._used: dict[str, str] = {}
        self._retries: dict[str, int] = {}
        self._applied_cap = applied
        self._asked_cap = asked
        self._capped = capped

    def __repr__(self) -> str:
        measured = self._rows is not None
        count = 0 if self._rows is None else len(self._rows)
        return (
            f"Dashboard(measured={measured}, rows={count}, "
            f"widgets={len(self._widgets)}, cap={self._applied_cap})"
        )

    def policy(self) -> Policy:
        """Return the recorded ceilings. The policy cap is never the caller's higher ask."""
        return Policy(
            widget_cap=WIDGET_CAP,
            applied_widget_cap=self._applied_cap,
            asked_widget_cap=self._asked_cap,
            widget_capped=self._capped,
            row_cap=ROW_CAP,
            schema=SCHEMA,
        )

    def rebuild(self, rows: object) -> Projection:
        """Replace the projection. A failed check leaves the previous rows in place."""
        admitted = _as_readings(rows)
        indexed = _group(admitted)
        self._rows = admitted
        self._index = indexed
        return Projection(schema=SCHEMA, count=len(admitted), cap=ROW_CAP)

    def records(self) -> tuple[Reading, ...]:
        """Return admitted rows in rebuild order. Unmeasured before the first rebuild."""
        if self._rows is None:
            raise Refuse("UNMEASURED")
        return self._rows

    def read(
        self,
        name: object,
        *,
        profile: object = "default",
        limit: object = None,
    ) -> PanelView:
        """Return stored rows for one panel. No nonce is accepted or required."""
        checked = _panel_name(name)
        who = _profile(profile)
        applied, asked, capped = _row_window(limit)
        if self._rows is None or self._index is None:
            raise Refuse("UNMEASURED")
        bucket = self._index.get((checked, who), ())
        return PanelView(
            name=checked,
            profile=who,
            rows=_window(bucket, applied),
            cap=ROW_CAP,
            limit=applied,
            asked_limit=asked,
            capped=capped,
            schema=SCHEMA,
        )

    def add_widget(self, name: object) -> Widget:
        """Record a display id matching `^[a-z0-9-]{1,32}$`. The applied cap is policy."""
        widget = _widget_name(name)
        if widget in self._widget_ids:
            raise Refuse("ALREADY")
        if len(self._widgets) >= self._applied_cap:
            raise Refuse("AT_CAP", str(self._applied_cap))
        issued = Widget(
            name=widget,
            cap=self._applied_cap,
            asked_cap=self._asked_cap,
            capped=self._capped,
            count=len(self._widgets) + 1,
            schema=SCHEMA,
        )
        self._widgets = (*self._widgets, widget)
        self._widget_ids.add(widget)
        return issued

    def widgets(self) -> tuple[str, ...]:
        """Return widget names in insertion order."""
        return self._widgets

    def grant(self, action: object, nonce: object) -> Grant:
        """Store one human nonce for `action`. Only the sha256 is kept. A spent nonce is `REPLAY`."""
        act = _action(action)
        token = _nonce_shape(nonce, empty_code="BAD_NONCE")
        digest = _sha256(token)
        used = self._used.get(act)
        if used is not None and const_eq(digest, used):
            raise Refuse("REPLAY")
        issued = Grant(action=act, nonce_sha=digest, schema=SCHEMA)
        self._grants[act] = digest
        self._retries.pop(act, None)
        return issued

    def mutate(self, action: object, nonce: object = "") -> Mutation:
        """Return an approved descriptor. An empty nonce is `NEED_APPROVAL`.

        A well-formed mismatch is `BAD_NONCE` once, then `RETRY_CAP`.
        A spent digest is `REPLAY` and does not consume that retry.
        """
        act = _action(action)
        token = _nonce_shape(nonce, empty_code="NEED_APPROVAL")
        digest = _sha256(token)
        used = self._used.get(act)
        if used is not None and const_eq(digest, used):
            raise Refuse("REPLAY")
        if self._retries.get(act, 0) >= 2:
            raise Refuse("RETRY_CAP")
        granted = self._grants.get(act)
        if granted is None:
            raise Refuse("UNGRANTED")
        if not const_eq(digest, granted):
            seen = self._retries.get(act, 0) + 1
            self._retries[act] = seen
            if seen >= 2:
                self._grants.pop(act, None)
                raise Refuse("RETRY_CAP")
            raise Refuse(RETRY_FAILURE)
        issued = Mutation(action=act, nonce_sha=digest, code=APPROVED, schema=SCHEMA)
        self._grants.pop(act, None)
        self._retries.pop(act, None)
        self._used[act] = digest
        return issued


_DEFAULT = Dashboard()


def policy() -> Policy:
    """Return ceilings for the process-local dashboard."""
    return _DEFAULT.policy()


def rebuild(rows: object) -> Projection:
    """Replace the process-local projection."""
    return _DEFAULT.rebuild(rows)


def records() -> tuple[Reading, ...]:
    """Return process-local admitted rows. Unmeasured before the first rebuild."""
    return _DEFAULT.records()


def read(
    name: object,
    *,
    profile: object = "default",
    limit: object = None,
) -> PanelView:
    """Read the process-local projection. No nonce."""
    return _DEFAULT.read(name, profile=profile, limit=limit)


def add_widget(name: object) -> Widget:
    """Record a widget name on the process-local dashboard."""
    return _DEFAULT.add_widget(name)


def widgets() -> tuple[str, ...]:
    """Return process-local widget names."""
    return _DEFAULT.widgets()


def grant(action: object, nonce: object) -> Grant:
    """Grant one nonce on the process-local dashboard."""
    return _DEFAULT.grant(action, nonce)


def mutate(action: object, nonce: object = "") -> Mutation:
    """Mutate through the process-local dashboard. An empty nonce is `NEED_APPROVAL`."""
    return _DEFAULT.mutate(action, nonce)


def reset() -> None:
    """Drop the process-local projection, widgets, and grants."""
    global _DEFAULT
    _DEFAULT = Dashboard()


__all__ = [
    "ACTION_CAP",
    "APPROVED",
    "BODY_CAP",
    "DEFAULT_PORT",
    "DISPLAY",
    "HOST_CAP",
    "LOOPBACK",
    "NONCE_CAP",
    "PANELS",
    "RETRY_FAILURE",
    "ROW_CAP",
    "SCAN_CAP",
    "SCHEMA",
    "VALUE_CAP",
    "WIDGET_CAP",
    "BindPlan",
    "Dashboard",
    "Display",
    "Grant",
    "Mutation",
    "Panel",
    "PanelView",
    "Policy",
    "Projection",
    "Reading",
    "Widget",
    "add_widget",
    "check_bind",
    "grant",
    "mutate",
    "panel",
    "panels",
    "policy",
    "read",
    "rebuild",
    "records",
    "reset",
    "screen",
    "widgets",
]
