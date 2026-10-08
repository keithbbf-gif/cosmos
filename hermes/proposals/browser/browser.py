"""DOM descriptors for the Hermes browser toolset.

A descriptor is a record for cosmos_dom to run later. Nothing here launches a
browser, attaches to CDP, or opens a socket. The snapshot policy cap is 15000
characters. A line that does not fit that budget is skipped.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass, replace

from cosmos_hermes import Refuse, bound_int, bound_text, const_eq, secret_shape

SCHEMA = "cosmos-hermes-browser/1"
SNAPSHOT_CAP = 15_000
MIN_SNAPSHOT = 1_000
URL_CAP = 2_048
SELECTOR_CAP = 256
TEXT_CAP = 8_000
PAGE_CAP = 64_000
PROMPT_CAP = 500
PLAN_CAP = 32
MAX_ATTEMPT = 2
_ID_CAP = 64

_OPS = frozenset(
    {"navigate", "click", "snapshot", "type_text", "scroll", "press", "back", "dialog"}
)
_CODES = frozenset({"READY", "CONFIRM"})
_DIRECTIONS = frozenset({"up", "down"})
_DIALOGS = frozenset({"accept", "dismiss"})
_KEYS = frozenset(
    {
        "Enter",
        "Tab",
        "Escape",
        "ArrowDown",
        "ArrowUp",
        "ArrowLeft",
        "ArrowRight",
        "Backspace",
        "Space",
        "Home",
        "End",
        "PageUp",
        "PageDown",
    }
)
_SCHEMES = frozenset({"http", "https"})
_RETRYABLE = "UNREACHABLE"
_HOST_CHARS = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-")
_V6_CHARS = frozenset("0123456789abcdefABCDEF:.")
_ID_START = frozenset("abcdefghijklmnopqrstuvwxyz")
_ID_CHARS = frozenset("abcdefghijklmnopqrstuvwxyz0123456789-")
_DIGITS = frozenset("0123456789")
_HEX = frozenset("0123456789abcdefABCDEF")
_ENCODED_DOTDOT = re.compile(r"%2e%2e", re.IGNORECASE)


def _flag(value: object) -> bool:
    if not isinstance(value, bool):
        raise Refuse("NOT_BOOL")
    return value


def _ident(value: object) -> str:
    raw = bound_text(value, _ID_CAP)
    if secret_shape(raw):
        raise Refuse("SECRET")
    if raw == "" or raw[0] not in _ID_START or any(ch not in _ID_CHARS for ch in raw):
        raise Refuse("BAD_ID")
    return raw


def _blank(value: object, limit: int) -> None:
    if bound_text(value, limit) != "":
        raise Refuse("BAD_JOB")


def _snapshot_cap(threshold: object) -> int:
    """Record the policy cap when the caller asks for more. Never raise it."""
    if threshold is None:
        return SNAPSHOT_CAP
    if isinstance(threshold, bool) or not isinstance(threshold, int):
        raise Refuse("NOT_INT")
    if threshold > SNAPSHOT_CAP:
        return SNAPSHOT_CAP
    return bound_int(threshold, MIN_SNAPSHOT, SNAPSHOT_CAP)


def _bad_url_char(ch: str) -> bool:
    code = ord(ch)
    return ch.isspace() or code < 32 or code == 127 or ch == "\\"


def _unquote_once(text: str) -> str:
    out: list[str] = []
    index = 0
    size = len(text)
    while index < size:
        if text[index] == "%" and index + 2 < size:
            pair = text[index + 1 : index + 3]
            if pair[0] in _HEX and pair[1] in _HEX:
                out.append(chr(int(pair, 16)))
                index += 3
                continue
        out.append(text[index])
        index += 1
    return "".join(out)


def _has_dotdot(text: str) -> bool:
    return ".." in text or _ENCODED_DOTDOT.search(text) is not None


def _port(value: str) -> None:
    if value == "" or any(ch not in _DIGITS for ch in value):
        raise Refuse("BAD_URL")
    number = int(value)
    if number < 1 or number > 65535:
        raise Refuse("BAD_URL")


def _dns_host(host: str) -> None:
    if host == "" or len(host) > 253 or host.startswith(".") or host.startswith("-"):
        raise Refuse("BAD_URL")
    body = host[:-1] if host.endswith(".") else host
    if body == "" or ".." in body:
        raise Refuse("BAD_URL")
    for label in body.split("."):
        if label == "" or len(label) > 63 or label[0] == "-" or label[-1] == "-":
            raise Refuse("BAD_URL")
        if any(ch not in _HOST_CHARS for ch in label):
            raise Refuse("BAD_URL")


def _v6_host(host: str) -> None:
    if host == "" or len(host) > 64 or ":" not in host or host.count("::") > 1:
        raise Refuse("BAD_URL")
    if any(ch not in _V6_CHARS for ch in host):
        raise Refuse("BAD_URL")


def _host_port(authority: str) -> None:
    if authority.startswith("["):
        end = authority.find("]")
        if end < 2 or "[" in authority[1:end]:
            raise Refuse("BAD_URL")
        host = authority[1:end]
        tail = authority[end + 1 :]
        _v6_host(host)
        if tail == "":
            return
        if not tail.startswith(":"):
            raise Refuse("BAD_URL")
        _port(tail[1:])
        return
    host, sep, port = authority.partition(":")
    if sep == "":
        _dns_host(authority)
        return
    _dns_host(host)
    _port(port)


def _check_path(tail: str) -> None:
    path = tail
    for index, ch in enumerate(tail):
        if ch in "?#":
            path = tail[:index]
            break
    if path == "":
        return
    if not path.startswith("/"):
        raise Refuse("BAD_URL")
    for segment in path.split("/"):
        if segment == "" or segment == ".":
            continue
        if _has_dotdot(segment):
            raise Refuse("DOTDOT")
        decoded = _unquote_once(segment)
        if _has_dotdot(decoded):
            raise Refuse("DOTDOT")
        folded = decoded.lower()
        if "%2f" in folded or "%5c" in folded or "%00" in folded:
            raise Refuse("BAD_URL")
        if any(ch in "/\\" or ord(ch) < 32 or ord(ch) == 127 for ch in decoded):
            raise Refuse("BAD_URL")


def _structure(raw: str) -> None:
    scheme, sep, rest = raw.partition("://")
    if sep != "://" or rest == "":
        raise Refuse("BAD_URL")
    if scheme.lower() not in _SCHEMES:
        raise Refuse("BAD_URL")
    cut = len(rest)
    for index, ch in enumerate(rest):
        if ch in "/?#":
            cut = index
            break
    authority = rest[:cut]
    tail = rest[cut:]
    if authority == "" or "@" in authority:
        raise Refuse("BAD_URL")
    _host_port(authority)
    _check_path(tail)


def _http_url(value: object) -> str:
    """Accept only http or https. file: and dot-dot forms refuse."""
    raw = bound_text(value, URL_CAP)
    if secret_shape(raw):
        raise Refuse("SECRET")
    # file: wins over dot-dot so file:///C:/a/../b stays FILE_URL.
    if raw.lower().startswith("file:"):
        raise Refuse("FILE_URL")
    if _has_dotdot(raw):
        raise Refuse("DOTDOT")
    decoded = _unquote_once(raw)
    if _has_dotdot(decoded) or "\x00" in decoded:
        raise Refuse("DOTDOT" if _has_dotdot(decoded) else "BAD_URL")
    if "%00" in raw.lower() or any(_bad_url_char(ch) for ch in raw):
        raise Refuse("BAD_URL")
    _structure(raw)
    return raw


def _selector(value: object) -> str:
    raw = bound_text(value, SELECTOR_CAP)
    if secret_shape(raw):
        raise Refuse("SECRET")
    if raw == "" or raw.strip() != raw or any(ord(ch) < 32 or ord(ch) == 127 for ch in raw):
        raise Refuse("BAD_SELECTOR")
    folded = raw.lower()
    if folded.startswith("javascript:") or folded.startswith("file:") or _has_dotdot(raw):
        raise Refuse("BAD_SELECTOR")
    return raw


def _plain_text(value: object, limit: int) -> str:
    raw = bound_text(value, limit)
    if secret_shape(raw):
        raise Refuse("SECRET")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in raw):
        raise Refuse("BAD_TEXT")
    return raw


def _member(value: object, limit: int, allowed: frozenset[str], code: str) -> str:
    raw = bound_text(value, limit)
    if raw not in allowed:
        raise Refuse(code)
    return raw


@dataclass(frozen=True, slots=True)
class DomDescriptor:
    """One DOM action. Frozen. code is READY, or CONFIRM for a credential type."""

    schema: str
    session: str
    step_id: str
    op: str
    code: str
    url: str
    selector: str
    text: str
    full: bool
    snapshot_cap: int
    direction: str
    key: str
    dialog: str
    prompt: str
    credential_id: str
    require_session: bool
    password: bool
    attempt: int

    def __post_init__(self) -> None:
        _audit(self)

    def __repr__(self) -> str:
        # Field name `password` would match the assignment secret shape.
        return (
            "DomDescriptor("
            f"schema={self.schema!r}, session={self.session!r}, step_id={self.step_id!r}, "
            f"op={self.op!r}, code={self.code!r}, url={self.url!r}, "
            f"selector={self.selector!r}, text={self.text!r}, full={self.full!r}, "
            f"snapshot_cap={self.snapshot_cap!r}, direction={self.direction!r}, "
            f"key={self.key!r}, dialog={self.dialog!r}, prompt={self.prompt!r}, "
            f"credential_id={self.credential_id!r}, require_session={self.require_session!r}, "
            f"hidden={self.password!r}, attempt={self.attempt!r})"
        )


@dataclass(frozen=True, slots=True)
class SnapshotView:
    """Lines kept under the snapshot cap. Oversized lines are counted, not stored."""

    schema: str
    text: str
    cap: int
    kept: int
    skipped: int
    truncated: bool

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_JOB")
        body = bound_text(self.text, SNAPSHOT_CAP)
        if secret_shape(body):
            raise Refuse("SECRET")
        if isinstance(self.cap, bool) or not isinstance(self.cap, int):
            raise Refuse("NOT_INT")
        if self.cap < MIN_SNAPSHOT or self.cap > SNAPSHOT_CAP:
            raise Refuse("BAD_CAP")
        if isinstance(self.kept, bool) or not isinstance(self.kept, int):
            raise Refuse("NOT_INT")
        if isinstance(self.skipped, bool) or not isinstance(self.skipped, int):
            raise Refuse("NOT_INT")
        if self.kept < 0 or self.skipped < 0:
            raise Refuse("OUT_OF_RANGE")
        if not isinstance(self.truncated, bool):
            raise Refuse("NOT_BOOL")
        if self.truncated != (self.skipped > 0):
            raise Refuse("BAD_CAP")
        if len(body) > self.cap:
            raise Refuse("BAD_CAP")
        if body == "":
            if self.kept not in (0, 1):
                raise Refuse("BAD_CAP")
        elif self.kept != len(body.split("\n")):
            raise Refuse("BAD_CAP")


@dataclass(frozen=True, slots=True)
class BrowserPlan:
    """Ordered descriptors for one session. Rebuilding the steps reproduces it."""

    schema: str
    session: str
    steps: tuple[DomDescriptor, ...]
    snapshot_cap: int

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_JOB")
        if _ident(self.session) != self.session:
            raise Refuse("BAD_ID")
        if isinstance(self.snapshot_cap, bool) or not isinstance(self.snapshot_cap, int):
            raise Refuse("NOT_INT")
        if not MIN_SNAPSHOT <= self.snapshot_cap <= SNAPSHOT_CAP:
            raise Refuse("BAD_CAP")
        if type(self.steps) is not tuple or len(self.steps) == 0:
            raise Refuse("BAD_PLAN")
        if len(self.steps) > PLAN_CAP:
            raise Refuse("OVERSIZE")
        seen: set[str] = set()
        for step in self.steps:
            if type(step) is not DomDescriptor:
                raise Refuse("BAD_JOB")
            if step.session != self.session:
                raise Refuse("BAD_JOB")
            if step.step_id in seen:
                raise Refuse("DUPLICATE")
            seen.add(step.step_id)


def _reject_extra(
    desc: DomDescriptor,
    *,
    url: bool = False,
    selector: bool = False,
    text: bool = False,
    full: bool = False,
    cap: bool = False,
    direction: bool = False,
    key: bool = False,
    dialog: bool = False,
    prompt: bool = False,
    credential: bool = False,
    session_flag: bool = False,
) -> None:
    if not url:
        _blank(desc.url, URL_CAP)
    if not selector:
        _blank(desc.selector, SELECTOR_CAP)
    if not text:
        _blank(desc.text, TEXT_CAP)
    if not full and desc.full:
        raise Refuse("BAD_JOB")
    if not isinstance(desc.full, bool):
        raise Refuse("NOT_BOOL")
    if cap:
        if not MIN_SNAPSHOT <= desc.snapshot_cap <= SNAPSHOT_CAP:
            raise Refuse("BAD_CAP")
    elif desc.snapshot_cap != 0:
        raise Refuse("BAD_JOB")
    if not direction:
        _blank(desc.direction, 16)
    if not key:
        _blank(desc.key, 32)
    if not dialog:
        _blank(desc.dialog, 16)
    if not prompt:
        _blank(desc.prompt, PROMPT_CAP)
    if not credential:
        _blank(desc.credential_id, _ID_CAP)
    if not session_flag and desc.require_session:
        raise Refuse("BAD_JOB")


def _audit(desc: DomDescriptor) -> None:
    if desc.schema != SCHEMA or desc.op not in _OPS:
        raise Refuse("BAD_JOB")
    if _ident(desc.session) != desc.session or _ident(desc.step_id) != desc.step_id:
        raise Refuse("BAD_ID")
    if desc.code not in _CODES:
        raise Refuse("BAD_CODE")
    if not isinstance(desc.password, bool) or not isinstance(desc.require_session, bool):
        raise Refuse("NOT_BOOL")
    if isinstance(desc.attempt, bool) or not isinstance(desc.attempt, int):
        raise Refuse("NOT_INT")
    if desc.attempt not in (1, MAX_ATTEMPT):
        raise Refuse("BAD_ATTEMPT")
    if isinstance(desc.snapshot_cap, bool) or not isinstance(desc.snapshot_cap, int):
        raise Refuse("NOT_INT")
    if (desc.code == "CONFIRM") != desc.password or (desc.password and desc.op != "type_text"):
        raise Refuse("BAD_CODE")
    if desc.op == "navigate":
        if _http_url(desc.url) != desc.url:
            raise Refuse("BAD_URL")
        _reject_extra(desc, url=True, session_flag=True)
        return
    if desc.op == "click":
        if _selector(desc.selector) != desc.selector:
            raise Refuse("BAD_SELECTOR")
        _reject_extra(desc, selector=True)
        return
    if desc.op == "snapshot":
        _reject_extra(desc, full=True, cap=True)
        return
    if desc.op == "type_text":
        if _selector(desc.selector) != desc.selector:
            raise Refuse("BAD_SELECTOR")
        if desc.password:
            if desc.text != "":
                raise Refuse("BAD_TEXT")
            if _ident(desc.credential_id) != desc.credential_id:
                raise Refuse("BAD_ID")
            _reject_extra(desc, selector=True, credential=True)
            return
        if _plain_text(desc.text, TEXT_CAP) != desc.text:
            raise Refuse("BAD_TEXT")
        _reject_extra(desc, selector=True, text=True)
        return
    if desc.op == "scroll":
        if desc.direction not in _DIRECTIONS:
            raise Refuse("BAD_DIRECTION")
        _reject_extra(desc, direction=True)
        return
    if desc.op == "press":
        if desc.key not in _KEYS:
            raise Refuse("BAD_KEY")
        _reject_extra(desc, key=True)
        return
    if desc.op == "back":
        _reject_extra(desc)
        return
    if desc.dialog not in _DIALOGS:
        raise Refuse("BAD_DIALOG")
    if desc.dialog == "dismiss" and desc.prompt != "":
        raise Refuse("BAD_DIALOG")
    if desc.prompt != "" and _plain_text(desc.prompt, PROMPT_CAP) != desc.prompt:
        raise Refuse("BAD_TEXT")
    _reject_extra(desc, dialog=True, prompt=True)


def _base(
    session: str,
    step_id: str,
    op: str,
    *,
    code: str = "READY",
    url: str = "",
    selector: str = "",
    text: str = "",
    full: bool = False,
    snapshot_cap: int = 0,
    direction: str = "",
    key: str = "",
    dialog: str = "",
    prompt: str = "",
    credential_id: str = "",
    require_session: bool = False,
    password: bool = False,
    attempt: int = 1,
) -> DomDescriptor:
    return DomDescriptor(
        schema=SCHEMA,
        session=session,
        step_id=step_id,
        op=op,
        code=code,
        url=url,
        selector=selector,
        text=text,
        full=full,
        snapshot_cap=snapshot_cap,
        direction=direction,
        key=key,
        dialog=dialog,
        prompt=prompt,
        credential_id=credential_id,
        require_session=require_session,
        password=password,
        attempt=attempt,
    )


def open_page(
    url: object,
    session: object,
    step_id: object,
    *,
    require_session: object = False,
) -> DomDescriptor:
    """Return a navigate descriptor for cosmos_dom. Does not launch a browser."""
    return _base(
        _ident(session),
        _ident(step_id),
        "navigate",
        url=_http_url(url),
        require_session=_flag(require_session),
    )


def click(selector: object, session: object, step_id: object) -> DomDescriptor:
    """Return a click descriptor for a selector or a snapshot ref."""
    return _base(_ident(session), _ident(step_id), "click", selector=_selector(selector))


def snapshot(
    session: object,
    step_id: object,
    *,
    full: object = False,
    threshold: object = None,
) -> DomDescriptor:
    """Return a snapshot descriptor. Thresholds above the policy cap are ignored."""
    return _base(
        _ident(session),
        _ident(step_id),
        "snapshot",
        full=_flag(full),
        snapshot_cap=_snapshot_cap(threshold),
    )


def type_text(
    selector: object,
    text: object,
    session: object,
    step_id: object,
    *,
    password: object = False,
    credential_id: object = "",
) -> DomDescriptor:
    """Return a type descriptor. password=True stores a credential id and CONFIRM."""
    chosen = _selector(selector)
    hidden = _flag(password)
    if hidden:
        raw = bound_text(text, TEXT_CAP)
        if secret_shape(raw):
            raise Refuse("SECRET")
        if raw != "":
            raise Refuse("BAD_TEXT")
        if not isinstance(credential_id, str):
            raise Refuse("NOT_TEXT")
        return _base(
            _ident(session),
            _ident(step_id),
            "type_text",
            code="CONFIRM",
            selector=chosen,
            credential_id=_ident(credential_id),
            password=True,
        )
    if credential_id != "":
        raise Refuse("BAD_JOB")
    return _base(
        _ident(session),
        _ident(step_id),
        "type_text",
        selector=chosen,
        text=_plain_text(text, TEXT_CAP),
    )


def scroll(direction: object, session: object, step_id: object) -> DomDescriptor:
    """Return a scroll descriptor. Direction is up or down."""
    return _base(
        _ident(session),
        _ident(step_id),
        "scroll",
        direction=_member(direction, 16, _DIRECTIONS, "BAD_DIRECTION"),
    )


def press(key: object, session: object, step_id: object) -> DomDescriptor:
    """Return a key descriptor. The key must be on the policy allowlist."""
    return _base(
        _ident(session),
        _ident(step_id),
        "press",
        key=_member(key, 32, _KEYS, "BAD_KEY"),
    )


def back(session: object, step_id: object) -> DomDescriptor:
    """Return a history-back descriptor. Does not move a live page."""
    return _base(_ident(session), _ident(step_id), "back")


def dialog(
    action: object,
    session: object,
    step_id: object,
    prompt: object = "",
) -> DomDescriptor:
    """Return a dialog descriptor. dismiss ignores no prompt text."""
    kind = _member(action, 16, _DIALOGS, "BAD_DIALOG")
    note = _plain_text(prompt, PROMPT_CAP)
    if kind == "dismiss" and note != "":
        raise Refuse("BAD_DIALOG")
    return _base(
        _ident(session),
        _ident(step_id),
        "dialog",
        dialog=kind,
        prompt=note,
    )


def pack_snapshot(text: object, threshold: object = None) -> SnapshotView:
    """Keep lines that fit. Skip a line that does not fit, then keep later lines."""
    raw = bound_text(text, PAGE_CAP)
    if secret_shape(raw):
        raise Refuse("SECRET")
    cap = _snapshot_cap(threshold)
    if raw == "":
        return SnapshotView(schema=SCHEMA, text="", cap=cap, kept=0, skipped=0, truncated=False)
    kept_lines: list[str] = []
    skipped = 0
    used = 0
    for line in raw.split("\n"):
        if line.endswith("\r"):
            line = line[:-1]
        extra = 1 if kept_lines else 0
        need = len(line) + extra
        if need > cap - used:
            skipped += 1
            continue
        kept_lines.append(line)
        used += need
    body = "\n".join(kept_lines)
    return SnapshotView(
        schema=SCHEMA,
        text=body,
        cap=cap,
        kept=len(kept_lines),
        skipped=skipped,
        truncated=skipped > 0,
    )


def plan(session: object, steps: object, threshold: object = None) -> BrowserPlan:
    """Freeze descriptors for one session. More than PLAN_CAP steps refuse."""
    ident = _ident(session)
    cap = _snapshot_cap(threshold)
    if isinstance(steps, (str, bytes, bytearray)) or not isinstance(steps, Sequence):
        raise Refuse("BAD_PLAN")
    if len(steps) == 0:
        raise Refuse("BAD_PLAN")
    if len(steps) > PLAN_CAP:
        raise Refuse("OVERSIZE")
    kept: list[DomDescriptor] = []
    seen: set[str] = set()
    for step in steps:
        item = _as_desc(step)
        if item.session != ident:
            raise Refuse("BAD_JOB")
        if item.step_id in seen:
            raise Refuse("DUPLICATE")
        seen.add(item.step_id)
        kept.append(item)
    return BrowserPlan(schema=SCHEMA, session=ident, steps=tuple(kept), snapshot_cap=cap)


def rebuild(steps: object, session: object, threshold: object = None) -> BrowserPlan:
    """Reproduce a plan from the descriptors it emitted."""
    return plan(session, steps, threshold)


def _as_desc(step: object) -> DomDescriptor:
    if type(step) is not DomDescriptor:
        raise Refuse("BAD_JOB")
    return step


def retry(desc: object, failure: object) -> DomDescriptor:
    """One confirming retry, and only when failure is UNREACHABLE."""
    item = _as_desc(desc)
    kind = bound_text(failure, 40)
    if secret_shape(kind):
        raise Refuse("SECRET")
    if not const_eq(kind, _RETRYABLE) or item.password or item.code == "CONFIRM":
        raise Refuse("NO_RETRY")
    if item.attempt >= MAX_ATTEMPT:
        raise Refuse("RETRY_CAP")
    return replace(item, attempt=item.attempt + 1)


def run(_desc: object = None) -> None:
    """Refuse. A DOM descriptor is not a launch."""
    raise Refuse("NO_LAUNCH")


__all__ = [
    "MAX_ATTEMPT",
    "MIN_SNAPSHOT",
    "PAGE_CAP",
    "PLAN_CAP",
    "PROMPT_CAP",
    "SCHEMA",
    "SELECTOR_CAP",
    "SNAPSHOT_CAP",
    "TEXT_CAP",
    "URL_CAP",
    "BrowserPlan",
    "DomDescriptor",
    "SnapshotView",
    "back",
    "click",
    "dialog",
    "open_page",
    "pack_snapshot",
    "plan",
    "press",
    "rebuild",
    "retry",
    "run",
    "scroll",
    "snapshot",
    "type_text",
]
