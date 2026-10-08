"""Loopback subscription forward plan. No socket. The client bearer is not kept."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Final

from cosmos_hermes import Refuse, bound_bytes, bound_text, const_eq, redact, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-subscription_proxy/1"
BODY_CAP: Final[int] = 65536
HEADER_CAP: Final[int] = 32
ALLOW_CAP: Final[int] = 32
VALUE_CAP: Final[int] = 4096
LOOPBACK: Final[str] = "127.0.0.1"
PATHS: Final[tuple[str, ...]] = (
    "/v1/chat/completions",
    "/v1/completions",
    "/v1/embeddings",
    "/v1/models",
)
PROVIDERS: Final[tuple[str, ...]] = ("nous", "xai")

_NAME_CAP: Final[int] = 32
_CRED_CAP: Final[int] = 64
_HOST_CAP: Final[int] = 253
_TOKEN_MIN: Final[int] = 8
_RECORD_LEN: Final[int] = 11
_AUTH: Final[str] = "authorization"
_PATH_HEADER: Final[str] = "path"
_CRED_HEADER: Final[str] = "x-credential-id"
_PATH_SET: Final[frozenset[str]] = frozenset(PATHS)
_PROVIDER_SET: Final[frozenset[str]] = frozenset(PROVIDERS)
_SPECIAL: Final[frozenset[str]] = frozenset((_AUTH, _PATH_HEADER, _CRED_HEADER))
_NAME: Final[re.Pattern[str]] = re.compile(r"^[a-z][a-z0-9_-]{0,31}$")
_CRED: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_HEADER: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9-]{1,64}$")
_SHA: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")
# Colon form "Authorization: Bearer <token>" leaves the token after redact().
_LEAK: Final[re.Pattern[str]] = re.compile(r"\[redacted-assignment\][ \t]+\S")
_RAW_BEARER: Final[re.Pattern[str]] = re.compile(r"(?i)\bbearer[ \t]+\S")


def _dirty(text: str) -> bool:
    return bool(secret_shape(text) or _LEAK.search(text) or _RAW_BEARER.search(text))


def _sequence(value: object, code: str) -> Sequence[object]:
    if isinstance(value, (str, bytes, bytearray)):
        raise Refuse(code)
    if not isinstance(value, Sequence):
        raise Refuse(code)
    return value


def _upstream(value: object) -> str:
    text = bound_text(value, _NAME_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    if _NAME.fullmatch(text) is None:
        raise Refuse("BAD_UPSTREAM")
    return text


def _allow_name(value: object) -> str:
    text = bound_text(value, _NAME_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    if text not in _PROVIDER_SET:
        raise Refuse("BAD_ALLOW")
    return text


def _allow(value: object) -> frozenset[str]:
    rows = _sequence(value, "BAD_ALLOW")
    if len(rows) > ALLOW_CAP:
        raise Refuse("BAD_ALLOW")
    seen: set[str] = set()
    for item in rows:
        text = _allow_name(item)
        if text in seen:
            raise Refuse("DUPLICATE")
        seen.add(text)
    return frozenset(seen)


def _cap(value: object) -> tuple[int, bool]:
    if value is None:
        return BODY_CAP, False
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("NOT_INT")
    if value < 1:
        raise Refuse("BAD_LIMIT")
    if value > BODY_CAP:
        return BODY_CAP, True
    return value, False


def _host(value: object) -> str:
    text = bound_text(value, _HOST_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    if text != LOOPBACK:
        raise Refuse("PUBLIC_HOST")
    return text


def _header_name(value: object) -> str:
    text = bound_text(value, 64)
    if secret_shape(text):
        raise Refuse("SECRET")
    if _HEADER.fullmatch(text) is None:
        raise Refuse("BAD_HEADER")
    return text


def _header_value(value: object) -> str:
    text = bound_text(value, VALUE_CAP)
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in text):
        raise Refuse("BAD_HEADER")
    return text


def _pair(item: object) -> tuple[str, str]:
    seq = _sequence(item, "BAD_HEADER")
    if len(seq) != 2:
        raise Refuse("BAD_HEADER")
    return (_header_name(seq[0]), _header_value(seq[1]))


def _expand(key: object, value: object) -> tuple[tuple[str, str], ...]:
    name = _header_name(key)
    if isinstance(value, str):
        return ((name, _header_value(value)),)
    seq = _sequence(value, "BAD_HEADER")
    if len(seq) == 0:
        raise Refuse("BAD_HEADER")
    return tuple((name, _header_value(item)) for item in seq)


def _pairs(headers: object) -> tuple[tuple[str, str], ...]:
    rows: list[tuple[str, str]] = []
    if isinstance(headers, Mapping):
        for key, value in headers.items():
            for pair in _expand(key, value):
                if len(rows) >= HEADER_CAP:
                    raise Refuse("BAD_HEADERS")
                rows.append(pair)
    else:
        for entry in _sequence(headers, "BAD_HEADERS"):
            if len(rows) >= HEADER_CAP:
                raise Refuse("BAD_HEADERS")
            rows.append(_pair(entry))
    return tuple(rows)


def _path(text: str) -> str:
    if text not in _PATH_SET:
        raise Refuse("BAD_PATH")
    return text


def _cred(text: str) -> str:
    if text == "":
        raise Refuse("MISSING_CRED")
    narrowed = bound_text(text, _CRED_CAP)
    if _dirty(narrowed):
        raise Refuse("SECRET")
    if _CRED.fullmatch(narrowed) is None:
        raise Refuse("BAD_CRED")
    return narrowed


def _remember(found: list[str], text: str) -> None:
    if len(text) >= _TOKEN_MIN and text not in found:
        found.append(text)


def _auth_material(value: str) -> tuple[str, ...]:
    found: list[str] = []
    _remember(found, value)
    if not value.casefold().startswith("bearer"):
        _remember(found, f"Bearer {value}")
        return tuple(found)
    parts = value.split()
    if len(parts) < 2 or parts[0].casefold() != "bearer":
        return tuple(found)
    for part in parts[1:]:
        _remember(found, part)
    return tuple(found)


def _split(
    pairs: tuple[tuple[str, str], ...],
) -> tuple[str, str, tuple[tuple[str, str], ...], tuple[str, ...]]:
    paths: list[str] = []
    creds: list[str] = []
    outbound: list[tuple[str, str]] = []
    banned: list[str] = []
    auth_count = 0
    for name, value in pairs:
        folded = name.casefold()
        if folded == _AUTH:
            auth_count += 1
            if auth_count > 1:
                raise Refuse("DOUBLE_AUTH")
            banned.extend(_auth_material(value))
            continue
        if secret_shape(name) or _dirty(value):
            raise Refuse("SECRET")
        if folded == _PATH_HEADER:
            paths.append(value)
            continue
        if folded == _CRED_HEADER:
            creds.append(value)
            continue
        outbound.append((name, value))
    if len(paths) != 1:
        raise Refuse("BAD_PATH")
    if len(creds) == 0:
        raise Refuse("MISSING_CRED")
    if len(creds) > 1:
        raise Refuse("DUPLICATE")
    return (_path(paths[0]), _cred(creds[0]), tuple(outbound), tuple(banned))


def _log(pairs: tuple[tuple[str, str], ...], banned: tuple[str, ...]) -> str:
    """Store a redacted header line. Authorization never keeps the client bearer."""
    lines: list[str] = []
    for name, value in pairs:
        if name.casefold() == _AUTH:
            lines.append(f"{name} [redacted-bearer]")
            continue
        lines.append(f"{name}: {value}")
    logged = redact("\n".join(lines))
    if _dirty(logged):
        raise Refuse("SECRET")
    for secret in banned:
        if secret in logged:
            raise Refuse("SECRET")
    return logged


def _text_secret(raw: bytes) -> None:
    text = raw.decode("utf-8", errors="replace")
    if _dirty(text):
        raise Refuse("SECRET")


def _body(value: object, cap: int, banned: tuple[str, ...]) -> bytes:
    raw = bound_bytes(value, cap)
    for secret in banned:
        if secret.encode("utf-8") in raw:
            raise Refuse("SECRET")
    _text_secret(raw)
    return raw


def _as_str(value: object, code: str) -> str:
    if not isinstance(value, str):
        raise Refuse(code)
    return value


def _as_bytes(value: object) -> bytes:
    if not isinstance(value, bytes):
        raise Refuse("NOT_BYTES")
    return value


def _as_int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("NOT_INT")
    return value


def _as_bool(value: object) -> bool:
    if type(value) is not bool:
        raise Refuse("BAD_PLAN")
    return value


def _as_headers(value: object) -> tuple[tuple[str, str], ...]:
    if not isinstance(value, tuple) or type(value) is not tuple:
        raise Refuse("BAD_PLAN")
    checked: list[tuple[str, str]] = []
    for item in value:
        if not isinstance(item, tuple) or type(item) is not tuple or len(item) != 2:
            raise Refuse("BAD_PLAN")
        name, raw = item
        if not isinstance(name, str) or not isinstance(raw, str):
            raise Refuse("BAD_PLAN")
        checked.append((name, raw))
    return tuple(checked)


@dataclass(frozen=True, slots=True, kw_only=True)
class ForwardPlan:
    """Descriptor for a later host. `log_line` has no client bearer. `host` is loopback."""

    upstream: str
    host: str
    path: str
    credential_id: str
    headers: tuple[tuple[str, str], ...]
    body: bytes
    body_sha256: str
    cap: int
    clamped: bool
    log_line: str
    schema: str

    def __post_init__(self) -> None:
        name = _upstream(self.upstream)
        if name not in _PROVIDER_SET:
            raise Refuse("BAD_UPSTREAM")
        _host(self.host)
        if _dirty(self.path):
            raise Refuse("SECRET")
        _path(self.path)
        _cred(self.credential_id)
        if type(self.clamped) is not bool:
            raise Refuse("BAD_PLAN")
        if isinstance(self.cap, bool) or not isinstance(self.cap, int):
            raise Refuse("NOT_INT")
        if self.cap < 1 or self.cap > BODY_CAP:
            raise Refuse("BAD_LIMIT")
        if self.clamped and self.cap != BODY_CAP:
            raise Refuse("BAD_PLAN")
        if not isinstance(self.body, bytes):
            raise Refuse("NOT_BYTES")
        if len(self.body) > self.cap:
            raise Refuse("OVERSIZE", str(self.cap))
        _text_secret(self.body)
        if not isinstance(self.body_sha256, str) or _SHA.fullmatch(self.body_sha256) is None:
            raise Refuse("BAD_PLAN")
        digest = hashlib.sha256(self.body).hexdigest()
        if not const_eq(self.body_sha256, digest):
            raise Refuse("BAD_PLAN")
        if not isinstance(self.log_line, str) or not isinstance(self.schema, str):
            raise Refuse("BAD_PLAN")
        if _dirty(self.log_line):
            raise Refuse("SECRET")
        if not const_eq(self.schema, SCHEMA):
            raise Refuse("BAD_PLAN")
        if type(self.headers) is not tuple:
            raise Refuse("BAD_PLAN")
        for item in self.headers:
            if type(item) is not tuple or len(item) != 2:
                raise Refuse("BAD_PLAN")
            header_name, header_value = item
            if not isinstance(header_name, str) or not isinstance(header_value, str):
                raise Refuse("BAD_PLAN")
            if header_name.casefold() in _SPECIAL:
                raise Refuse("BAD_PLAN")
            if (
                _HEADER.fullmatch(header_name) is None
                or any(ord(ch) < 32 or ord(ch) == 127 for ch in header_value)
            ):
                raise Refuse("BAD_PLAN")
            if secret_shape(header_name) or _dirty(header_value):
                raise Refuse("SECRET")

    def __repr__(self) -> str:
        return (
            "ForwardPlan("
            f"upstream={self.upstream!r}, host={self.host!r}, path={self.path!r}, "
            f"credential_id={self.credential_id!r}, headers={self.headers!r}, "
            f"body_len={len(self.body)}, body_sha256={self.body_sha256!r}, "
            f"cap={self.cap}, clamped={self.clamped}, schema={self.schema!r}, "
            f"log_line={self.log_line!r})"
        )


def snapshot(plan: object) -> tuple[object, ...]:
    """Return plan fields in rebuild order. The body stays so the hash still matches."""
    if not isinstance(plan, ForwardPlan):
        raise Refuse("BAD_PLAN")
    return (
        plan.upstream,
        plan.host,
        plan.path,
        plan.credential_id,
        plan.headers,
        plan.body,
        plan.body_sha256,
        plan.cap,
        plan.clamped,
        plan.log_line,
        plan.schema,
    )


def _from_tuple(record: object) -> ForwardPlan:
    if not isinstance(record, tuple) or type(record) is not tuple or len(record) != _RECORD_LEN:
        raise Refuse("BAD_PLAN")
    row = record
    return ForwardPlan(
        upstream=_as_str(row[0], "BAD_PLAN"),
        host=_as_str(row[1], "BAD_PLAN"),
        path=_as_str(row[2], "BAD_PLAN"),
        credential_id=_as_str(row[3], "BAD_PLAN"),
        headers=_as_headers(row[4]),
        body=_as_bytes(row[5]),
        body_sha256=_as_str(row[6], "BAD_PLAN"),
        cap=_as_int(row[7]),
        clamped=_as_bool(row[8]),
        log_line=_as_str(row[9], "BAD_PLAN"),
        schema=_as_str(row[10], "BAD_PLAN"),
    )


def rebuild(record: object) -> ForwardPlan:
    """Rebuild a plan from `snapshot` output. The same record yields the same plan."""
    if isinstance(record, ForwardPlan):
        return _from_tuple(snapshot(record))
    return _from_tuple(record)


def adapters() -> tuple[str, ...]:
    """Shipped provider ids. The caller allowlist still has to name the one in use."""
    return PROVIDERS


def listen(*_args: object, **_kwargs: object) -> None:
    """Refuse to bind. A ForwardPlan is a descriptor for a later host."""
    raise Refuse("NO_SOCKET")


def connect(*_args: object, **_kwargs: object) -> None:
    """Refuse to connect. This module does not open an upstream socket."""
    raise Refuse("NO_SOCKET")


def forward(
    upstream: object,
    headers: object,
    body: object,
    allow: object,
    *,
    cap: object = None,
    host: object = LOOPBACK,
) -> ForwardPlan:
    """Return a loopback forward descriptor. `upstream` must be in `allow`. No socket."""
    applied, clamped = _cap(cap)
    client_host = _host(host)
    name = _upstream(upstream)
    allowed = _allow(allow)
    if name not in allowed:
        raise Refuse("UNKNOWN_UPSTREAM")
    pairs = _pairs(headers)
    path, credential_id, outbound, banned = _split(pairs)
    payload = _body(body, applied, banned)
    logged = _log(pairs, banned)
    return ForwardPlan(
        upstream=name,
        host=client_host,
        path=path,
        credential_id=credential_id,
        headers=outbound,
        body=payload,
        body_sha256=hashlib.sha256(payload).hexdigest(),
        cap=applied,
        clamped=clamped,
        log_line=logged,
        schema=SCHEMA,
    )


__all__ = [
    "ALLOW_CAP",
    "BODY_CAP",
    "HEADER_CAP",
    "LOOPBACK",
    "PATHS",
    "PROVIDERS",
    "SCHEMA",
    "VALUE_CAP",
    "ForwardPlan",
    "adapters",
    "connect",
    "forward",
    "listen",
    "rebuild",
    "snapshot",
]
