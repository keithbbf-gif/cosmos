"""Bounded X search plans. Disabled until a credential id is present. No HTTP."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Final, cast

from cosmos_hermes import Refuse, bound_text, const_eq, redact, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-x_search/1"
QUERY_CAP: Final[int] = 400
INGEST_CAP: Final[int] = 10
CRED_CAP: Final[int] = 64
URL_CAP: Final[int] = 2000
TEXT_CAP: Final[int] = 2000
HANDLE_CAP: Final[int] = 15
ROW_CAP: Final[int] = 32
BUDGET_CAP: Final[int] = 4_000
KIND: Final[str] = "posts"
KINDS: Final[tuple[str, ...]] = ("posts", "profiles", "threads")
RETRY_CLASS: Final[str] = "UPSTREAM"

_KIND_CAP: Final[int] = 16
_HANDLE_INPUT_CAP: Final[int] = HANDLE_CAP + 1
_RECORD_LEN: Final[int] = 11
_GENESIS: Final[str] = "0" * 64
_FIELDS: Final[frozenset[str]] = frozenset({"url", "handle", "text"})
_KINDS: Final[frozenset[str]] = frozenset(KINDS)
_OPS: Final[frozenset[str]] = frozenset({"arm", "ask", "again"})
_BANNED_CREDS: Final[frozenset[str]] = frozenset({"off", "yolo"})
_HOSTS: Final[frozenset[str]] = frozenset(
    {
        "x.com",
        "www.x.com",
        "twitter.com",
        "www.twitter.com",
        "mobile.twitter.com",
    }
)
_BAD_ESC: Final[tuple[str, ...]] = ("%00", "%0a", "%0d", "%5c")

_WS: Final[re.Pattern[str]] = re.compile(r"\s+")
_CRED_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$")
_HANDLE_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9_]{1,15}$")
_HEX_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")


def _as_text(value: object) -> str:
    if type(value) is not str:
        raise Refuse("NOT_TEXT")
    return value


def _reject_secret(text: str) -> None:
    if secret_shape(text):
        raise Refuse("SECRET")


def _cred(value: object) -> str:
    text = bound_text(_as_text(value), CRED_CAP)
    _reject_secret(text)
    if text.strip() == "":
        raise Refuse("NO_CRED")
    if text.casefold() in _BANNED_CREDS or _CRED_RE.fullmatch(text) is None:
        raise Refuse("BAD_CRED")
    return text


def _normalize_query(value: object) -> str:
    raw = bound_text(_as_text(value), QUERY_CAP)
    text = _WS.sub(" ", raw.strip())
    if text == "":
        raise Refuse("EMPTY_QUERY")
    _reject_secret(text)
    return text


def _kind(value: object) -> str:
    if value is None:
        return KIND
    text = bound_text(_as_text(value), _KIND_CAP)
    _reject_secret(text)
    if text not in _KINDS:
        raise Refuse("BAD_KIND")
    return text


def _fence(value: object) -> str:
    if value is None:
        return ""
    text = bound_text(_as_text(value), CRED_CAP)
    _reject_secret(text)
    if text == "":
        return ""
    if _CRED_RE.fullmatch(text) is None:
        raise Refuse("BAD_FENCE")
    return text


def _applied_limit(value: object) -> tuple[int, bool]:
    """Ignore a result limit above the policy cap. Record that cap, not the request."""
    if value is None:
        return INGEST_CAP, False
    if type(value) is not int:
        raise Refuse("NOT_INT")
    if value < 1:
        raise Refuse("OUT_OF_RANGE", f"1..{INGEST_CAP}")
    if value > INGEST_CAP:
        return INGEST_CAP, True
    return value, False


def _applied_budget(value: object) -> int:
    if value is None:
        return BUDGET_CAP
    if type(value) is not int:
        raise Refuse("NOT_INT")
    if value < 0:
        raise Refuse("OUT_OF_RANGE", f"0..{BUDGET_CAP}")
    if value > BUDGET_CAP:
        return BUDGET_CAP
    return value


def _dump(parts: tuple[str | int | bool, ...]) -> str:
    return json.dumps(list(parts), separators=(",", ":"), ensure_ascii=True)


def _link(prev: str, body: str) -> str:
    return hashlib.sha256(f"{prev}\n{body}".encode("utf-8")).hexdigest()


def _https_x(value: object) -> str:
    """Accept an https X or Twitter URL. Refuse userinfo, ports, and other hosts."""
    text = bound_text(_as_text(value), URL_CAP)
    _reject_secret(text)
    for ch in text:
        code = ord(ch)
        if ch in "@\\" or code <= 32 or code == 127:
            raise Refuse("BAD_URL")
    lowered = text.casefold()
    for token in _BAD_ESC:
        if token in lowered:
            raise Refuse("BAD_URL")
    scheme, sep, rest = text.partition("://")
    if sep != "://" or scheme.casefold() != "https" or rest == "":
        raise Refuse("BAD_URL")
    host_end = len(rest)
    for index, ch in enumerate(rest):
        if ch in "/?#":
            host_end = index
            break
    if host_end == 0:
        raise Refuse("BAD_URL")
    host = rest[:host_end]
    if ":" in host or host.casefold() not in _HOSTS:
        raise Refuse("BAD_URL")
    return text


def _handle(value: object) -> str:
    text = bound_text(_as_text(value), _HANDLE_INPUT_CAP)
    _reject_secret(text)
    if text.startswith("@") and not text.startswith("@@"):
        text = text[1:]
    if _HANDLE_RE.fullmatch(text) is None:
        raise Refuse("BAD_HANDLE")
    return text


def _post_text(value: object) -> str:
    text = bound_text(_as_text(value), TEXT_CAP)
    _reject_secret(text)
    if text.strip() == "":
        raise Refuse("BAD_ROW")
    return text


def _url_key(url: str) -> str:
    """Post identity ignores scheme case, host case, query, and fragment."""
    _scheme, sep, rest = url.partition("://")
    if sep != "://":
        raise Refuse("BAD_URL")
    host_end = len(rest)
    for index, ch in enumerate(rest):
        if ch in "/?#":
            host_end = index
            break
    path_end = len(rest)
    for index in range(host_end, len(rest)):
        if rest[index] in "?#":
            path_end = index
            break
    path = rest[host_end:path_end]
    if path == "":
        path = "/"
    return f"https://{rest[:host_end].casefold()}{path}"


def _chain(
    cred: str,
    kind: str,
    fence: str,
    text: str,
    limit: int,
    cap: int,
    clamped: bool,
    retry_used: int,
) -> tuple[PlanStep, ...]:
    records: list[tuple[str, str]] = [
        ("arm", _dump(("arm", SCHEMA, cred, kind, fence))),
        ("ask", _dump(("ask", text, limit, cap, clamped))),
    ]
    if retry_used == 1:
        records.append(("again", _dump(("again", RETRY_CLASS))))
    prev = _GENESIS
    built: list[PlanStep] = []
    for ordinal, (op, body) in enumerate(records):
        sha = _link(prev, body)
        built.append(PlanStep(ordinal, op, prev, sha))
        prev = sha
    return tuple(built)


@dataclass(frozen=True, slots=True)
class Enabled:
    """Proof that one credential id armed X search. Not a key."""

    cred_id: str
    cap: int

    def __post_init__(self) -> None:
        if type(self.cap) is not int or self.cap != QUERY_CAP:
            raise Refuse("BAD_CAP")
        checked = _cred(self.cred_id)
        if checked != self.cred_id:
            raise Refuse("BAD_CRED")

    def __repr__(self) -> str:
        return redact(f"Enabled(cred_id={self.cred_id!r}, cap={self.cap})")


@dataclass(frozen=True, slots=True)
class PlanStep:
    """One link in the plan chain. `prev_sha` is the previous link, or genesis."""

    ordinal: int
    op: str
    prev_sha: str
    sha: str

    def __post_init__(self) -> None:
        if type(self.ordinal) is not int:
            raise Refuse("NOT_INT")
        if self.ordinal < 0 or self.ordinal > 2:
            raise Refuse("BAD_PLAN")
        if type(self.op) is not str or self.op not in _OPS:
            raise Refuse("BAD_PLAN")
        if type(self.prev_sha) is not str or type(self.sha) is not str:
            raise Refuse("CHAIN")
        if _HEX_RE.fullmatch(self.prev_sha) is None or _HEX_RE.fullmatch(self.sha) is None:
            raise Refuse("CHAIN")

    def __repr__(self) -> str:
        return f"PlanStep(ordinal={self.ordinal}, op={self.op!r})"


@dataclass(frozen=True, slots=True)
class SearchPlan:
    """Bounded X search plan. This object does not fetch."""

    schema: str
    text: str
    cred_id: str
    kind: str
    limit: int
    cap: int
    clamped: bool
    fence: str
    retry_used: int
    steps: tuple[PlanStep, ...] = field(init=False)
    digest: str = field(init=False)

    def __post_init__(self) -> None:
        if type(self.schema) is not str or self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        if type(self.clamped) is not bool:
            raise Refuse("NOT_BOOL")
        if type(self.limit) is not int or type(self.cap) is not int or type(self.retry_used) is not int:
            raise Refuse("NOT_INT")
        if self.cap != INGEST_CAP:
            raise Refuse("BAD_CAP")
        if self.limit < 1 or self.limit > INGEST_CAP:
            raise Refuse("BAD_LIMIT")
        if self.clamped and self.limit != INGEST_CAP:
            raise Refuse("BAD_LIMIT")
        if self.retry_used not in (0, 1):
            raise Refuse("BAD_PLAN")
        cred = _cred(self.cred_id)
        if cred != self.cred_id:
            raise Refuse("BAD_CRED")
        if type(self.kind) is not str or self.kind not in _KINDS:
            raise Refuse("BAD_KIND")
        token = _fence(self.fence)
        if token != self.fence:
            raise Refuse("BAD_FENCE")
        body = _normalize_query(self.text)
        if body != self.text:
            raise Refuse("BAD_PLAN")
        steps = _chain(cred, self.kind, token, body, self.limit, self.cap, self.clamped, self.retry_used)
        if len(steps) != (3 if self.retry_used == 1 else 2):
            raise Refuse("BAD_PLAN")
        object.__setattr__(self, "steps", steps)
        object.__setattr__(self, "digest", steps[len(steps) - 1].sha)

    def __repr__(self) -> str:
        return redact(
            f"SearchPlan(text={self.text!r}, cred_id={self.cred_id!r}, kind={self.kind!r}, "
            f"limit={self.limit}, cap={self.cap}, clamped={self.clamped}, retry_used={self.retry_used})"
        )


@dataclass(frozen=True, slots=True)
class Hit:
    """One public X post the caller already holds."""

    url: str
    handle: str
    text: str

    def __post_init__(self) -> None:
        url = _https_x(self.url)
        handle = _handle(self.handle)
        text = _post_text(self.text)
        if url != self.url or handle != self.handle or text != self.text:
            raise Refuse("BAD_ROW")

    def __repr__(self) -> str:
        return redact(f"Hit(url={self.url!r}, handle={self.handle!r}, text={self.text!r})")


@dataclass(frozen=True, slots=True)
class IngestResult:
    """Hits kept under the count and the text budget, plus how many rows were dropped."""

    schema: str
    hits: tuple[Hit, ...]
    dropped: int
    limit: int
    cap: int
    budget: int

    def __post_init__(self) -> None:
        if type(self.schema) is not str or self.schema != SCHEMA:
            raise Refuse("BAD_SCHEMA")
        if type(self.hits) is not tuple:
            raise Refuse("BAD_ROWS")
        if type(self.limit) is not int or type(self.cap) is not int or type(self.budget) is not int:
            raise Refuse("NOT_INT")
        if type(self.dropped) is not int:
            raise Refuse("NOT_INT")
        if self.cap != INGEST_CAP:
            raise Refuse("BAD_CAP")
        if self.limit < 1 or self.limit > INGEST_CAP:
            raise Refuse("BAD_LIMIT")
        if self.budget < 0 or self.budget > BUDGET_CAP:
            raise Refuse("BAD_BUDGET")
        if len(self.hits) > INGEST_CAP or len(self.hits) > self.limit:
            raise Refuse("BAD_ROWS")
        if self.dropped < 0 or self.dropped > ROW_CAP or len(self.hits) + self.dropped > ROW_CAP:
            raise Refuse("BAD_COUNT")
        used = 0
        seen: set[str] = set()
        for hit in self.hits:
            if type(hit) is not Hit:
                raise Refuse("BAD_ROW")
            key = _url_key(hit.url)
            if key in seen:
                raise Refuse("DUPLICATE")
            seen.add(key)
            used += len(hit.text)
            if used > self.budget:
                raise Refuse("BAD_BUDGET")

    def __repr__(self) -> str:
        return redact(
            f"IngestResult(hits={len(self.hits)}, dropped={self.dropped}, "
            f"limit={self.limit}, cap={self.cap}, budget={self.budget})"
        )


def _unwrap_cred(cred_id: object) -> str:
    if type(cred_id) is Enabled:
        return cred_id.cred_id
    return _cred(cred_id)


def _plan(
    text: object,
    cred_id: object,
    limit: int,
    clamped: bool,
    kind: object,
    fence: object,
    retry_used: int,
) -> SearchPlan:
    if type(retry_used) is not int or retry_used not in (0, 1):
        raise Refuse("BAD_PLAN")
    if type(limit) is not int or type(clamped) is not bool:
        raise Refuse("BAD_PLAN")
    cred = _unwrap_cred(cred_id)
    chosen = _kind(kind)
    token = _fence(fence)
    body = _normalize_query(text)
    return SearchPlan(
        schema=SCHEMA,
        text=body,
        cred_id=cred,
        kind=chosen,
        limit=limit,
        cap=INGEST_CAP,
        clamped=clamped,
        fence=token,
        retry_used=retry_used,
    )


def enable(cred_id: object) -> Enabled:
    """Arm X search with a credential id. An empty id is NO_CRED."""
    return Enabled(_cred(cred_id), QUERY_CAP)


def query(
    text: object = None,
    cred_id: object = None,
    limit: object = None,
    kind: object = None,
    fence: object = None,
) -> SearchPlan:
    """Return a bounded plan when a credential id is present. Otherwise DISABLED.

    A missing id does not read `text`. The plan does not fetch.
    """
    if cred_id is None:
        raise Refuse("DISABLED")
    cred = _unwrap_cred(cred_id)
    applied, clamped = _applied_limit(limit)
    return _plan(text, cred, applied, clamped, kind, fence, 0)


def confirm_retry(plan: object, failure: object) -> SearchPlan:
    """Record one confirming retry after UPSTREAM. The plan does not fetch."""
    if type(plan) is not SearchPlan:
        raise Refuse("BAD_PLAN")
    name = bound_text(_as_text(failure), 32)
    _reject_secret(name)
    if name != RETRY_CLASS:
        raise Refuse("NO_RETRY")
    if plan.retry_used != 0:
        raise Refuse("RETRY_CAP")
    return _plan(plan.text, plan.cred_id, plan.limit, plan.clamped, plan.kind, plan.fence, 1)


def accept(plan: object, fence: object) -> SearchPlan:
    """Return `plan` when `fence` matches. A missing or different fence is STALE."""
    if type(plan) is not SearchPlan:
        raise Refuse("BAD_PLAN")
    token = _fence(fence)
    if token == "" or plan.fence == "" or not const_eq(plan.fence, token):
        raise Refuse("STALE")
    return plan


def _parse_steps(value: object) -> tuple[tuple[int, str, str, str], ...]:
    if type(value) is not tuple:
        raise Refuse("BAD_RECORD")
    raw = cast(tuple[object, ...], value)
    seen: set[int] = set()
    parsed: list[tuple[int, str, str, str]] = []
    for item in raw:
        if type(item) is not tuple:
            raise Refuse("BAD_RECORD")
        step = cast(tuple[object, ...], item)
        if len(step) != 4:
            raise Refuse("BAD_RECORD")
        ordinal = step[0]
        op = step[1]
        prev = step[2]
        sha = step[3]
        if type(ordinal) is not int:
            raise Refuse("NOT_INT")
        if type(op) is not str or op not in _OPS:
            raise Refuse("BAD_PLAN")
        if type(prev) is not str or type(sha) is not str:
            raise Refuse("CHAIN")
        if _HEX_RE.fullmatch(prev) is None or _HEX_RE.fullmatch(sha) is None:
            raise Refuse("CHAIN")
        if ordinal in seen:
            raise Refuse("DUPLICATE")
        seen.add(ordinal)
        parsed.append((ordinal, op, prev, sha))
    return tuple(parsed)


def _steps_match(
    expected: tuple[PlanStep, ...],
    got: tuple[tuple[int, str, str, str], ...],
) -> bool:
    if len(expected) != len(got):
        return False
    for step, item in zip(expected, got, strict=True):
        ordinal, op, prev, sha = item
        if step.ordinal != ordinal or step.op != op:
            return False
        if not const_eq(step.prev_sha, prev) or not const_eq(step.sha, sha):
            return False
    return True


def emit(plan: object) -> tuple[object, ...]:
    """Return the plan as records. `rebuild` accepts this exact shape."""
    if type(plan) is not SearchPlan:
        raise Refuse("BAD_PLAN")
    return (
        plan.schema,
        plan.text,
        plan.cred_id,
        plan.kind,
        plan.limit,
        plan.cap,
        plan.clamped,
        plan.fence,
        plan.retry_used,
        tuple((step.ordinal, step.op, step.prev_sha, step.sha) for step in plan.steps),
        plan.digest,
    )


def rebuild(record: object) -> SearchPlan:
    """Reproduce a plan from `emit` records. A broken link or digest refuses."""
    if type(record) is not tuple:
        raise Refuse("BAD_RECORD")
    row = cast(tuple[object, ...], record)
    if len(row) != _RECORD_LEN:
        raise Refuse("BAD_RECORD")
    schema = row[0]
    if type(schema) is not str or schema != SCHEMA:
        raise Refuse("BAD_SCHEMA")
    text = row[1]
    cred_id = row[2]
    kind = row[3]
    limit = row[4]
    cap = row[5]
    clamped = row[6]
    fence = row[7]
    retry_used = row[8]
    parsed = _parse_steps(row[9])
    digest = row[10]
    if type(text) is not str or type(cred_id) is not str or type(kind) is not str or type(fence) is not str:
        raise Refuse("BAD_RECORD")
    if type(limit) is not int or type(cap) is not int or type(retry_used) is not int:
        raise Refuse("NOT_INT")
    if type(clamped) is not bool:
        raise Refuse("NOT_BOOL")
    if type(digest) is not str or _HEX_RE.fullmatch(digest) is None:
        raise Refuse("BAD_DIGEST")
    if retry_used not in (0, 1):
        raise Refuse("BAD_PLAN")
    built = SearchPlan(
        schema=schema,
        text=text,
        cred_id=cred_id,
        kind=kind,
        limit=limit,
        cap=cap,
        clamped=clamped,
        fence=fence,
        retry_used=retry_used,
    )
    if not _steps_match(built.steps, parsed):
        raise Refuse("CHAIN")
    if not const_eq(built.digest, digest):
        raise Refuse("BAD_DIGEST")
    return built


def _rows(value: object) -> list[object] | tuple[object, ...]:
    if type(value) is list:
        return cast(list[object], value)
    if type(value) is tuple:
        return cast(tuple[object, ...], value)
    raise Refuse("BAD_ROWS")


def _hit(row: object) -> Hit:
    if type(row) is not dict:
        raise Refuse("BAD_ROW")
    found = cast(dict[object, object], row)
    if len(found) != len(_FIELDS):
        raise Refuse("BAD_ROW")
    shaped: dict[str, object] = {}
    for key, item in found.items():
        if type(key) is not str or key not in _FIELDS:
            raise Refuse("BAD_ROW")
        shaped[key] = item
    handle = shaped["handle"]
    if type(handle) is str and handle.startswith("@") and not handle.startswith("@@"):
        handle = handle[1:]
    return Hit(_https_x(shaped["url"]), _handle(handle), _post_text(shaped["text"]))


def ingest(rows: object, limit: object = None, budget: object = None) -> IngestResult:
    """Keep hits that fit the count and the remaining text budget.

    A valid hit that does not fit is skipped. Later hits that fit are kept.
    A malformed row or a duplicate post id refuses, including past the count cap.
    """
    items = _rows(rows)
    if len(items) > ROW_CAP:
        raise Refuse("TOO_MANY")
    keep, _clamped = _applied_limit(limit)
    room_cap = _applied_budget(budget)
    hits: list[Hit] = []
    dropped = 0
    room = room_cap
    seen: set[str] = set()
    for row in items:
        hit = _hit(row)
        key = _url_key(hit.url)
        if key in seen:
            raise Refuse("DUPLICATE")
        seen.add(key)
        size = len(hit.text)
        if len(hits) >= keep or size > room:
            dropped += 1
            continue
        hits.append(hit)
        room -= size
    return IngestResult(SCHEMA, tuple(hits), dropped, keep, INGEST_CAP, room_cap)


__all__ = [
    "BUDGET_CAP",
    "CRED_CAP",
    "HANDLE_CAP",
    "INGEST_CAP",
    "KIND",
    "KINDS",
    "QUERY_CAP",
    "RETRY_CLASS",
    "ROW_CAP",
    "SCHEMA",
    "TEXT_CAP",
    "URL_CAP",
    "Enabled",
    "Hit",
    "IngestResult",
    "PlanStep",
    "SearchPlan",
    "accept",
    "confirm_retry",
    "emit",
    "enable",
    "ingest",
    "query",
    "rebuild",
]
