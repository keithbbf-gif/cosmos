"""Loopback route descriptors and an OpenAI chat check. Does not listen."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Final

from cosmos_hermes import Refuse, bound_int, bound_text, const_eq, secret_shape

SCHEMA: Final = "cosmos-hermes-api_server/1"
BODY_TEXT_CAP: Final = 256_000
POLICY_RUN_CAP: Final = 10
LOOPBACK_HOST: Final = "127.0.0.1"
DEFAULT_PORT: Final = 8642
FENCE_CAP: Final = 1_000_000
_MAX_DEPTH: Final = 32
_HOST_CAP: Final = 253
_REQUEST_CAP: Final = 128
_BEARER_CAP: Final = 64
_ROLES: Final = frozenset({"system", "user", "assistant", "tool"})
_METHODS: Final = frozenset({"GET", "POST", "PATCH", "DELETE"})
_AUTHS: Final = frozenset({"none", "bearer"})
_SCALARS: Final = (bool, int, float)
_KIND: Final = "descriptor"

_IPV4: Final = re.compile(
    r"^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.){3}"
    r"(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])$"
)
_PATH: Final = re.compile(r"^/(?:[a-z0-9._~-]+)(?:/(?:[a-z0-9._~-]+))*$")
_CRED: Final = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$")

# method, path, auth, starts_run. Policy catalog. Callers cannot add a row.
_SPECS: Final[tuple[tuple[str, str, str, bool], ...]] = (
    ("GET", "/health", "none", False),
    ("GET", "/v1/health", "none", False),
    ("GET", "/health/detailed", "bearer", False),
    ("GET", "/v1/models", "bearer", False),
    ("GET", "/v1/capabilities", "bearer", False),
    ("POST", "/v1/chat/completions", "bearer", True),
    ("POST", "/v1/responses", "bearer", True),
    ("POST", "/v1/runs", "bearer", True),
    ("POST", "/session", "bearer", True),
    ("GET", "/v1/skills", "bearer", False),
    ("GET", "/v1/toolsets", "bearer", False),
)
_INDEX: Final[dict[str, tuple[str, str, str, bool]]] = {
    f"{method} {path}": (method, path, auth, starts) for method, path, auth, starts in _SPECS
}


def _cost(method: str, path: str) -> int:
    return len(method) + 1 + len(path)


POLICY_TEXT_BUDGET: Final[int] = sum(_cost(item[0], item[1]) for item in _SPECS)


def _keep(text: str, total: list[int]) -> None:
    total[0] += len(text)
    if total[0] > BODY_TEXT_CAP:
        raise Refuse("OVERSIZE", str(BODY_TEXT_CAP))
    if secret_shape(text):
        raise Refuse("SECRET")


def _walk(node: object, total: list[int], depth: int) -> None:
    if depth > _MAX_DEPTH:
        raise Refuse("BAD_BODY")
    if isinstance(node, str):
        _keep(bound_text(node, BODY_TEXT_CAP), total)
        return
    if isinstance(node, dict):
        for key, value in node.items():
            if not isinstance(key, str):
                raise Refuse("BAD_BODY")
            _keep(bound_text(key, BODY_TEXT_CAP), total)
            _walk(value, total, depth + 1)
        return
    if isinstance(node, list):
        for item in node:
            _walk(item, total, depth + 1)
        return
    if node is None or isinstance(node, _SCALARS):
        return
    raise Refuse("BAD_BODY")


def _recorded_cap(requested: object, ceiling: int = POLICY_RUN_CAP) -> int:
    if isinstance(requested, bool) or not isinstance(requested, int):
        raise Refuse("NOT_INT")
    if requested < 1:
        raise Refuse("BAD_LIMIT")
    if requested > ceiling:
        return ceiling
    return requested


def _bearer_id(value: object) -> str:
    if value is None:
        raise Refuse("NO_BEARER")
    text = bound_text(value, _BEARER_CAP)
    if text == "" or text.strip() == "":
        raise Refuse("NO_BEARER")
    if secret_shape(text):
        raise Refuse("SECRET")
    if _CRED.fullmatch(text) is None:
        raise Refuse("BAD_BEARER")
    return text


def _presented(value: object, required: bool) -> str | None:
    if value is None:
        if required:
            raise Refuse("NO_BEARER")
        return None
    text = bound_text(value, _BEARER_CAP)
    if text == "" or text.strip() == "":
        if required:
            raise Refuse("NO_BEARER")
        return None
    if secret_shape(text):
        raise Refuse("SECRET")
    return text


def _loopback_host(value: object) -> str:
    text = bound_text(value, _HOST_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    if text != LOOPBACK_HOST:
        raise Refuse("NOT_LOOPBACK")
    return LOOPBACK_HOST


def _parse_target(value: object) -> tuple[str, str]:
    text = bound_text(value, _REQUEST_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    parts = text.split(" ")
    if len(parts) != 2:
        raise Refuse("BAD_TARGET")
    method, path = parts
    if method not in _METHODS:
        raise Refuse("BAD_METHOD")
    if _PATH.fullmatch(path) is None:
        raise Refuse("BAD_PATH")
    return method, path


def _digest(
    host: str,
    port: int,
    bearer_id: str,
    run_cap: int,
    budget: int,
    fence: int,
    routes: tuple[Route, ...],
) -> str:
    lines = [SCHEMA, host, str(port), bearer_id, str(run_cap), str(budget), str(fence)]
    for row in routes:
        lines.append(row.method)
        lines.append(row.path)
        lines.append(row.auth)
        lines.append("1" if row.starts_run else "0")
        lines.append(str(row.cost))
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def _fit(rows: tuple[Route, ...], budget: int) -> tuple[Route, ...]:
    kept: list[Route] = []
    left = budget
    for row in rows:
        if row.cost <= left:
            kept.append(row)
            left -= row.cost
    if not kept:
        raise Refuse("EMPTY_ROUTES")
    return tuple(kept)


def _assert_fits(rows: tuple[Route, ...], budget: int) -> None:
    left = budget
    for row in rows:
        if row.cost > left:
            raise Refuse("BROKEN_CHAIN")
        left -= row.cost


@dataclass(frozen=True, slots=True)
class ChatMessage:
    """One text turn. Image and file parts are not accepted."""

    role: str
    content: str

    def __post_init__(self) -> None:
        role = bound_text(self.role, BODY_TEXT_CAP)
        content = bound_text(self.content, BODY_TEXT_CAP)
        if secret_shape(role) or secret_shape(content):
            raise Refuse("SECRET")
        if role not in _ROLES:
            raise Refuse("BAD_BODY")
        object.__setattr__(self, "role", role)
        object.__setattr__(self, "content", content)


def _fresh_message(role: str, content: str) -> ChatMessage:
    made = object.__new__(ChatMessage)
    object.__setattr__(made, "role", role)
    object.__setattr__(made, "content", content)
    return made


@dataclass(frozen=True, slots=True)
class ChatRequest:
    """A chat a later service could run. `cap` is the recorded run cap."""

    schema: str
    model: str
    messages: tuple[ChatMessage, ...]
    stream: bool
    cap: int

    def __post_init__(self) -> None:
        model = bound_text(self.model, BODY_TEXT_CAP)
        if model.strip() == "":
            raise Refuse("BAD_BODY")
        if secret_shape(model):
            raise Refuse("SECRET")
        if not isinstance(self.messages, tuple) or len(self.messages) == 0:
            raise Refuse("BAD_BODY")
        if any(not isinstance(item, ChatMessage) for item in self.messages):
            raise Refuse("BAD_BODY")
        if not isinstance(self.stream, bool):
            raise Refuse("BAD_BODY")
        object.__setattr__(self, "schema", SCHEMA)
        object.__setattr__(self, "model", model)
        object.__setattr__(self, "cap", _recorded_cap(self.cap))


def _fresh_request(
    model: str,
    messages: tuple[ChatMessage, ...],
    stream: bool,
    cap: int,
) -> ChatRequest:
    made = object.__new__(ChatRequest)
    object.__setattr__(made, "schema", SCHEMA)
    object.__setattr__(made, "model", model)
    object.__setattr__(made, "messages", messages)
    object.__setattr__(made, "stream", stream)
    object.__setattr__(made, "cap", cap)
    return made


@dataclass(frozen=True, slots=True)
class BindCheck:
    """Host decision. Nothing is bound."""

    schema: str
    host: str
    loopback: bool
    public_grant: bool

    def __post_init__(self) -> None:
        host = bound_text(self.host, _HOST_CAP)
        if secret_shape(host):
            raise Refuse("SECRET")
        if not isinstance(self.loopback, bool) or not isinstance(self.public_grant, bool):
            raise Refuse("BAD_GRANT")
        object.__setattr__(self, "schema", SCHEMA)
        object.__setattr__(self, "host", host)


@dataclass(frozen=True, slots=True)
class BearerCheck:
    """A matched credential id. The id is not stored."""

    schema: str
    accepted: bool

    def __post_init__(self) -> None:
        if self.accepted is not True:
            raise Refuse("BAD_BEARER")
        object.__setattr__(self, "schema", SCHEMA)


@dataclass(frozen=True, slots=True)
class Route:
    """One mounted path. `executes` stays false. `kind` stays `descriptor`."""

    schema: str
    method: str
    path: str
    auth: str
    starts_run: bool
    cost: int
    executes: bool
    kind: str = _KIND

    def __post_init__(self) -> None:
        if not isinstance(self.starts_run, bool) or not isinstance(self.executes, bool):
            raise Refuse("NOT_BOOL")
        if not isinstance(self.kind, str):
            raise Refuse("NOT_TEXT")
        method = bound_text(self.method, 16)
        path = bound_text(self.path, _REQUEST_CAP)
        if secret_shape(method) or secret_shape(path):
            raise Refuse("SECRET")
        if method not in _METHODS:
            raise Refuse("BAD_METHOD")
        if _PATH.fullmatch(path) is None:
            raise Refuse("BAD_PATH")
        if not isinstance(self.auth, str) or self.auth not in _AUTHS:
            raise Refuse("BAD_AUTH")
        spec = _INDEX.get(f"{method} {path}")
        if spec is None:
            raise Refuse("UNKNOWN_ROUTE")
        auth = spec[2]
        starts = spec[3]
        if isinstance(self.cost, bool) or not isinstance(self.cost, int):
            raise Refuse("NOT_INT")
        real_cost = _cost(method, path)
        if self.cost != real_cost:
            raise Refuse("BROKEN_CHAIN")
        object.__setattr__(self, "schema", SCHEMA)
        object.__setattr__(self, "method", method)
        object.__setattr__(self, "path", path)
        object.__setattr__(self, "auth", auth)
        object.__setattr__(self, "starts_run", starts)
        object.__setattr__(self, "cost", real_cost)
        object.__setattr__(self, "executes", False)
        object.__setattr__(self, "kind", _KIND)


def _catalog_routes() -> tuple[Route, ...]:
    built: list[Route] = []
    for method, path, auth, starts in _SPECS:
        built.append(
            Route(
                schema=SCHEMA,
                method=method,
                path=path,
                auth=auth,
                starts_run=starts,
                cost=_cost(method, path),
                executes=False,
            )
        )
    return tuple(built)


_CATALOG: Final[tuple[Route, ...]] = _catalog_routes()
_BY_KEY: Final[dict[str, Route]] = {f"{row.method} {row.path}": row for row in _CATALOG}


def _select(routes: object) -> tuple[Route, ...]:
    if routes is None:
        return _CATALOG
    if isinstance(routes, (str, bytes)) or not isinstance(routes, (list, tuple)):
        raise Refuse("BAD_BODY")
    if len(routes) == 0:
        raise Refuse("EMPTY_ROUTES")
    seen: set[str] = set()
    picked: list[Route] = []
    for item in routes:
        method, path = _parse_target(item)
        key = f"{method} {path}"
        if key in seen:
            raise Refuse("DUPLICATE")
        seen.add(key)
        row = _BY_KEY.get(key)
        if row is None:
            raise Refuse("UNKNOWN_ROUTE")
        picked.append(row)
    return tuple(picked)


def _safe_cost(method: object, path: object) -> int:
    if not isinstance(method, str) or not isinstance(path, str):
        return 0
    return _cost(method, path)


@dataclass(frozen=True, slots=True)
class RouteTable:
    """Loopback routes a later listener could mount. `listens` stays false."""

    schema: str
    host: str
    port: int
    bearer_id: str
    run_cap: int
    budget: int
    fence: int
    public_grant: bool
    listens: bool
    routes: tuple[Route, ...]
    names: frozenset[str] = frozenset()
    chain: str = ""
    kind: str = _KIND

    def __post_init__(self) -> None:
        host = _loopback_host(self.host)
        bearer = _bearer_id(self.bearer_id)
        port = bound_int(self.port, 1, 65535)
        fence = bound_int(self.fence, 0, FENCE_CAP)
        if not isinstance(self.public_grant, bool):
            raise Refuse("BAD_GRANT")
        if not isinstance(self.listens, bool):
            raise Refuse("NOT_BOOL")
        if not isinstance(self.kind, str):
            raise Refuse("NOT_TEXT")
        if not isinstance(self.chain, str):
            raise Refuse("NOT_TEXT")
        run_cap = _recorded_cap(self.run_cap, POLICY_RUN_CAP)
        budget = _recorded_cap(self.budget, POLICY_TEXT_BUDGET)
        if not isinstance(self.routes, tuple):
            raise Refuse("BAD_BODY")
        seen: set[str] = set()
        rows: list[Route] = []
        for row in self.routes:
            if not isinstance(row, Route):
                raise Refuse("BAD_BODY")
            key = f"{row.method} {row.path}"
            if key in seen:
                raise Refuse("DUPLICATE")
            seen.add(key)
            rows.append(row)
        if not rows:
            raise Refuse("EMPTY_ROUTES")
        sealed = tuple(rows)
        _assert_fits(sealed, budget)
        digest = _digest(host, port, bearer, run_cap, budget, fence, sealed)
        chain = digest
        if self.chain != "":
            token = bound_text(self.chain, 64)
            if secret_shape(token):
                raise Refuse("SECRET")
            if not const_eq(token, digest):
                raise Refuse("BROKEN_CHAIN")
            chain = digest
        object.__setattr__(self, "schema", SCHEMA)
        object.__setattr__(self, "host", host)
        object.__setattr__(self, "port", port)
        object.__setattr__(self, "bearer_id", bearer)
        object.__setattr__(self, "run_cap", run_cap)
        object.__setattr__(self, "budget", budget)
        object.__setattr__(self, "fence", fence)
        object.__setattr__(self, "public_grant", False)
        object.__setattr__(self, "listens", False)
        object.__setattr__(self, "routes", sealed)
        object.__setattr__(self, "names", frozenset(seen))
        object.__setattr__(self, "chain", chain)
        object.__setattr__(self, "kind", _KIND)


@dataclass(frozen=True, slots=True)
class Resolution:
    """The route a later service would run. This value does not run it."""

    schema: str
    method: str
    path: str
    auth: str
    starts_run: bool
    run_cap: int
    fence: int
    listens: bool
    executes: bool
    kind: str = _KIND

    def __post_init__(self) -> None:
        if (
            not isinstance(self.listens, bool)
            or not isinstance(self.executes, bool)
            or not isinstance(self.starts_run, bool)
        ):
            raise Refuse("NOT_BOOL")
        if not isinstance(self.kind, str):
            raise Refuse("NOT_TEXT")
        row = Route(
            schema=SCHEMA,
            method=self.method,
            path=self.path,
            auth=self.auth,
            starts_run=self.starts_run,
            cost=_safe_cost(self.method, self.path),
            executes=False,
        )
        object.__setattr__(self, "schema", SCHEMA)
        object.__setattr__(self, "method", row.method)
        object.__setattr__(self, "path", row.path)
        object.__setattr__(self, "auth", row.auth)
        object.__setattr__(self, "starts_run", row.starts_run)
        object.__setattr__(self, "run_cap", _recorded_cap(self.run_cap))
        object.__setattr__(self, "fence", bound_int(self.fence, 0, FENCE_CAP))
        object.__setattr__(self, "listens", False)
        object.__setattr__(self, "executes", False)
        object.__setattr__(self, "kind", _KIND)


def _message(item: object) -> ChatMessage:
    if not isinstance(item, dict):
        raise Refuse("BAD_BODY")
    role = item.get("role")
    content = item.get("content")
    if not isinstance(role, str) or not isinstance(content, str):
        raise Refuse("BAD_BODY")
    if role not in _ROLES:
        raise Refuse("BAD_BODY")
    return _fresh_message(role, content)


def parse_chat(
    body: dict[object, object],
    *,
    requested_cap: object = POLICY_RUN_CAP,
) -> ChatRequest:
    """Require a string model and a message list. Record the run cap."""
    if not isinstance(body, dict):
        raise Refuse("BAD_BODY")
    _walk(body, [0], 0)
    model = body.get("model")
    messages = body.get("messages")
    if not isinstance(model, str) or not isinstance(messages, list):
        raise Refuse("BAD_BODY")
    if model.strip() == "" or len(messages) == 0:
        raise Refuse("BAD_BODY")
    parsed = tuple(_message(item) for item in messages)
    stream = body.get("stream", False)
    if not isinstance(stream, bool):
        raise Refuse("BAD_BODY")
    return _fresh_request(model, parsed, stream, _recorded_cap(requested_cap))


def check_bind(host: object, public_grant: bool) -> BindCheck:
    """Allow 127.0.0.1. A granted host must be a dotted IPv4 address. Does not listen."""
    if not isinstance(public_grant, bool):
        raise Refuse("BAD_GRANT")
    bound = bound_text(host, _HOST_CAP)
    if secret_shape(bound):
        raise Refuse("SECRET")
    if bound == LOOPBACK_HOST:
        return BindCheck(schema=SCHEMA, host=bound, loopback=True, public_grant=public_grant)
    if bound.strip() == "" or not public_grant:
        raise Refuse("PUBLIC_BIND")
    if _IPV4.fullmatch(bound) is None:
        raise Refuse("BAD_HOST")
    return BindCheck(schema=SCHEMA, host=bound, loopback=False, public_grant=True)


def check_bearer(presented: object, expected: object) -> BearerCheck:
    """Compare credential ids with const_eq. An empty expected id is refused."""
    got = bound_text(presented, BODY_TEXT_CAP)
    want = bound_text(expected, BODY_TEXT_CAP)
    if want.strip() == "":
        raise Refuse("NO_BEARER")
    if secret_shape(got) or secret_shape(want):
        raise Refuse("SECRET")
    if not const_eq(got, want):
        raise Refuse("BAD_BEARER")
    return BearerCheck(schema=SCHEMA, accepted=True)


def describe_loopback(
    host: object,
    bearer_id: object,
    *,
    port: object = DEFAULT_PORT,
    requested_cap: object = POLICY_RUN_CAP,
    routes: object = None,
    text_budget: object = None,
    public_grant: object = False,
    fence: object = 0,
) -> RouteTable:
    """Describe the loopback route table. A non-loopback host is refused. Nothing listens."""
    if not isinstance(public_grant, bool):
        raise Refuse("BAD_GRANT")
    budget = POLICY_TEXT_BUDGET if text_budget is None else _recorded_cap(text_budget, POLICY_TEXT_BUDGET)
    selected = _fit(_select(routes), budget)
    return RouteTable(
        schema=SCHEMA,
        host=_loopback_host(host),
        port=bound_int(port, 1, 65535),
        bearer_id=_bearer_id(bearer_id),
        run_cap=_recorded_cap(requested_cap),
        budget=budget,
        fence=bound_int(fence, 0, FENCE_CAP),
        public_grant=False,
        listens=False,
        routes=selected,
    )


def resolve(
    table: object,
    target: object,
    presented: object = None,
    *,
    fence: object = None,
) -> Resolution:
    """Name the descriptor for one request line. Does not call the route."""
    if not isinstance(table, RouteTable):
        raise Refuse("BAD_TABLE")
    if fence is None:
        raise Refuse("STALE")
    seen = bound_int(fence, 0, FENCE_CAP)
    if seen != table.fence:
        raise Refuse("STALE")
    method, path = _parse_target(target)
    key = f"{method} {path}"
    if key not in table.names:
        raise Refuse("UNKNOWN_ROUTE")
    row = _BY_KEY.get(key)
    if row is None:
        raise Refuse("UNKNOWN_ROUTE")
    presented_id = _presented(presented, row.auth == "bearer")
    if presented_id is not None and not const_eq(presented_id, table.bearer_id):
        raise Refuse("BAD_BEARER")
    return Resolution(
        schema=SCHEMA,
        method=row.method,
        path=row.path,
        auth=row.auth,
        starts_run=row.starts_run,
        run_cap=table.run_cap,
        fence=table.fence,
        listens=False,
        executes=False,
    )


def rebuild(table: object) -> RouteTable:
    """Rebuild the public table from its records. A bad chain is refused."""
    if not isinstance(table, RouteTable):
        raise Refuse("BAD_TABLE")
    fresh = describe_loopback(
        table.host,
        table.bearer_id,
        port=table.port,
        requested_cap=table.run_cap,
        routes=tuple(f"{row.method} {row.path}" for row in table.routes),
        text_budget=table.budget,
        public_grant=False,
        fence=table.fence,
    )
    if not const_eq(fresh.chain, table.chain) or fresh != table:
        raise Refuse("BROKEN_CHAIN")
    return fresh


__all__ = [
    "BODY_TEXT_CAP",
    "DEFAULT_PORT",
    "FENCE_CAP",
    "LOOPBACK_HOST",
    "POLICY_RUN_CAP",
    "POLICY_TEXT_BUDGET",
    "SCHEMA",
    "BearerCheck",
    "BindCheck",
    "ChatMessage",
    "ChatRequest",
    "Resolution",
    "Route",
    "RouteTable",
    "check_bearer",
    "check_bind",
    "describe_loopback",
    "parse_chat",
    "rebuild",
    "resolve",
]
