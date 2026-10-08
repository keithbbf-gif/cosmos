"""Bounded web search plans on the DOM and Firecrawl rails.

No HTTP. A later worker owns the fetch. Empty queries and missing
credential ids refuse. A plan is a hash-chained descriptor, not a call.
"""

from __future__ import annotations

import hashlib
import ipaddress
import json
import re
from dataclasses import dataclass
from typing import Final, cast

from cosmos_hermes import Refuse, bound_text, const_eq, redact, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-web_search/1"
QUERY_CAP: Final[int] = 400
TITLE_CAP: Final[int] = 200
SNIPPET_CAP: Final[int] = 500
URL_CAP: Final[int] = 2000
RESULT_CAP: Final[int] = 8
PAYLOAD_CAP: Final[int] = 2_000
ROW_CAP: Final[int] = 32
CRED_CAP: Final[int] = 64
TERM_CAP: Final[int] = 16
TERM_LEN: Final[int] = 64
RAIL: Final[str] = "dom"
RAILS: Final[tuple[str, ...]] = ("dom", "firecrawl")
RETRY_CLASS: Final[str] = "RATE_LIMIT"

_RAIL_SET: Final[frozenset[str]] = frozenset(RAILS)
_FIELDS: Final[frozenset[str]] = frozenset({"url", "title", "snippet"})
_SCHEMES: Final[frozenset[str]] = frozenset({"http", "https"})
_OPS: Final[frozenset[str]] = frozenset({"bind", "search", "retry"})
_OP_ORDER: Final[tuple[str, ...]] = ("bind", "search", "retry")
_RETRY_SET: Final[frozenset[str]] = frozenset({RETRY_CLASS})
_PRIVATE_LABELS: Final[frozenset[str]] = frozenset({"local", "localhost", "localdomain"})
_GENESIS: Final[str] = "0" * 64
_RECORD_LEN: Final[int] = 11

_WS: Final[re.Pattern[str]] = re.compile(r"\s+")
_ID: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$")
_HEX64: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")
_HOST_LABEL: Final[re.Pattern[str]] = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")


def _dump(parts: list[object]) -> str:
    return json.dumps(parts, separators=(",", ":"), ensure_ascii=True)


def _link(prev: str, body: str) -> str:
    return hashlib.sha256(f"{prev}\n{body}".encode("utf-8")).hexdigest()


def _normalize_query(value: object) -> str:
    raw = bound_text(value, QUERY_CAP)
    if secret_shape(raw):
        raise Refuse("SECRET")
    text = _WS.sub(" ", raw.strip())
    if text == "":
        raise Refuse("EMPTY_QUERY")
    return text


def _cred(value: object) -> str:
    if value is None:
        raise Refuse("NO_CRED")
    text = bound_text(value, CRED_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    if text.strip() == "":
        raise Refuse("NO_CRED")
    if _ID.fullmatch(text) is None:
        raise Refuse("BAD_CRED")
    return text


def _rail(value: object) -> str:
    if value is None:
        return RAIL
    text = bound_text(value, 16)
    if secret_shape(text):
        raise Refuse("SECRET")
    if text not in _RAIL_SET:
        raise Refuse("BAD_RAIL")
    return text


def _fence(value: object) -> str:
    text = bound_text(value, CRED_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    if text == "":
        return ""
    if _ID.fullmatch(text) is None:
        raise Refuse("BAD_FENCE")
    return text


def _applied_limit(value: object) -> tuple[int, bool]:
    """Ignore a limit above the policy cap. Record the cap, not the request."""
    if value is None:
        return RESULT_CAP, False
    if type(value) is not int:
        raise Refuse("NOT_INT")
    if value < 1:
        raise Refuse("OUT_OF_RANGE", f"1..{RESULT_CAP}")
    if value > RESULT_CAP:
        return RESULT_CAP, True
    return value, False


def _applied_budget(value: object) -> int:
    if value is None:
        return PAYLOAD_CAP
    if type(value) is not int:
        raise Refuse("NOT_INT")
    if value < 0:
        raise Refuse("OUT_OF_RANGE", f"0..{PAYLOAD_CAP}")
    if value > PAYLOAD_CAP:
        return PAYLOAD_CAP
    return value


def _plain(value: object, limit: int) -> str:
    text = bound_text(value, limit)
    if secret_shape(text):
        raise Refuse("SECRET")
    return text


def _reject_url_text(text: str) -> None:
    if ".." in text or "@" in text or "\\" in text:
        raise Refuse("BAD_URL")
    for ch in text:
        code = ord(ch)
        if code < 32 or code == 127:
            raise Refuse("BAD_URL")
    lowered = text.lower()
    if (
        "%00" in lowered
        or "%0a" in lowered
        or "%0d" in lowered
        or "%5c" in lowered
        or "%40" in lowered
    ):
        raise Refuse("BAD_URL")


def _authority(rest: str) -> str:
    for index, ch in enumerate(rest):
        if ch in "/?#":
            if index == 0:
                raise Refuse("BAD_URL")
            return rest[:index]
    return rest


def _host_port(authority: str) -> tuple[str, str | None]:
    if authority.startswith("["):
        end = authority.find("]")
        if end < 2:
            raise Refuse("BAD_URL")
        host = authority[1:end]
        tail = authority[end + 1 :]
        if tail == "":
            return host, None
        if len(tail) < 2 or not tail.startswith(":"):
            raise Refuse("BAD_URL")
        return host, tail[1:]
    if ":" in authority:
        host, port = authority.rsplit(":", 1)
        if host == "" or port == "":
            raise Refuse("BAD_URL")
        return host, port
    return authority, None


def _port(text: str) -> None:
    if text == "" or not text.isdigit() or len(text) > 5 or (len(text) > 1 and text.startswith("0")):
        raise Refuse("BAD_URL")
    number = int(text)
    if number < 1 or number > 65535:
        raise Refuse("BAD_URL")


def _ip(host: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    if ":" in host:
        try:
            return ipaddress.ip_address(host)
        except ValueError:
            raise Refuse("BAD_URL") from None
    if host.replace(".", "").isdigit():
        try:
            return ipaddress.ip_address(host)
        except ValueError:
            raise Refuse("BAD_URL") from None
    return None


def _public_ip(parsed: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return bool(
        parsed.is_global
        and not parsed.is_multicast
        and not parsed.is_reserved
        and not parsed.is_loopback
        and not parsed.is_link_local
        and not parsed.is_unspecified
        and not parsed.is_private
    )


def _check_host(host: str) -> None:
    if host == "" or host.startswith(".") or host.endswith(".") or ".." in host:
        raise Refuse("BAD_URL")
    parsed = _ip(host)
    if parsed is not None:
        if not _public_ip(parsed):
            raise Refuse("PRIVATE_URL")
        return
    labels = host.split(".")
    if len(labels) < 2:
        raise Refuse("PRIVATE_URL")
    for label in labels:
        folded = label.casefold()
        if folded in _PRIVATE_LABELS:
            raise Refuse("PRIVATE_URL")
        if _HOST_LABEL.fullmatch(folded) is None:
            raise Refuse("BAD_URL")


def _check_authority(authority: str) -> None:
    if authority == "":
        raise Refuse("BAD_URL")
    host, port = _host_port(authority)
    if port is not None:
        _port(port)
    _check_host(host)


def _http_url(value: object) -> str:
    """Accept a public http or https URL. Refuse userinfo, private hosts, and other schemes."""
    text = bound_text(value, URL_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    _reject_url_text(text)
    lowered = text.lower()
    scheme, sep, _rest = lowered.partition("://")
    if sep != "://" or scheme not in _SCHEMES:
        raise Refuse("BAD_URL")
    rest = text[len(scheme) + 3 :]
    if rest == "" or rest[0] in "/?#":
        raise Refuse("BAD_URL")
    _check_authority(_authority(rest))
    return text


def _cache_key(text: str, cred_id: str, rail: str, limit: int) -> str:
    folded = text.casefold()
    raw = f"{SCHEMA}\n{cred_id}\n{rail}\n{limit}\n{folded}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _plan_digest(
    text: str,
    cred_id: str,
    rail: str,
    limit: int,
    clamped: bool,
    fence: str,
    retry_used: int,
    terms: tuple[Term, ...],
    steps: tuple[PlanStep, ...],
    cache_key: str,
) -> str:
    body: dict[str, object] = {
        "cache_key": cache_key,
        "clamped": clamped,
        "cred_id": cred_id,
        "fence": fence,
        "limit": limit,
        "rail": rail,
        "retry_used": retry_used,
        "schema": SCHEMA,
        "steps": [step.sha for step in steps],
        "terms": [term.text for term in terms],
        "text": text,
    }
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _terms(text: str) -> tuple[Term, ...]:
    parts = text.split(" ")
    if len(parts) > TERM_CAP:
        raise Refuse("TOO_MANY")
    built: list[Term] = []
    for part in parts:
        if part == "" or len(part) > TERM_LEN or "://" in part:
            raise Refuse("BAD_TERM")
        built.append(Term(text=part, fold=part.casefold()))
    return tuple(built)


def _steps(
    cred_id: str,
    rail: str,
    fence: str,
    text: str,
    limit: int,
    retry_used: int,
) -> tuple[PlanStep, ...]:
    if type(retry_used) is not int or retry_used not in (0, 1):
        raise Refuse("BAD_PLAN")
    bodies: list[str] = [
        _dump(["bind", cred_id, rail, fence]),
        _dump(["search", text, limit]),
    ]
    if retry_used == 1:
        bodies.append(_dump(["retry", RETRY_CLASS]))
    prev = _GENESIS
    built: list[PlanStep] = []
    for ordinal, body in enumerate(bodies):
        sha = _link(prev, body)
        built.append(PlanStep(ordinal=ordinal, op=_OP_ORDER[ordinal], prev_sha=prev, sha=sha))
        prev = sha
    return tuple(built)


def _steps_match(left: tuple[PlanStep, ...], right: tuple[PlanStep, ...]) -> bool:
    if len(left) != len(right):
        return False
    for one, two in zip(left, right, strict=True):
        if type(one) is not PlanStep or type(two) is not PlanStep:
            return False
        if one.ordinal != two.ordinal or one.op != two.op:
            return False
        if not const_eq(one.prev_sha, two.prev_sha) or not const_eq(one.sha, two.sha):
            return False
    return True


@dataclass(frozen=True, slots=True)
class Term:
    """One query term and its casefold."""

    text: str
    fold: str

    def __post_init__(self) -> None:
        if type(self.text) is not str or type(self.fold) is not str:
            raise Refuse("BAD_TERM")
        if (
            self.text == ""
            or len(self.text) > TERM_LEN
            or "://" in self.text
            or any(ch.isspace() for ch in self.text)
        ):
            raise Refuse("BAD_TERM")
        if secret_shape(self.text):
            raise Refuse("SECRET")
        if self.fold != self.text.casefold():
            raise Refuse("BAD_TERM")

    def __repr__(self) -> str:
        return redact(f"Term(text={self.text!r})")


@dataclass(frozen=True, slots=True)
class PlanStep:
    """One link in the plan chain. `prev_sha` is the previous link, or the genesis hash."""

    ordinal: int
    op: str
    prev_sha: str
    sha: str

    def __post_init__(self) -> None:
        if type(self.ordinal) is not int or self.ordinal < 0 or self.ordinal > 2:
            raise Refuse("BAD_PLAN")
        if type(self.op) is not str or self.op not in _OPS:
            raise Refuse("BAD_PLAN")
        if type(self.prev_sha) is not str or type(self.sha) is not str:
            raise Refuse("CHAIN")
        if _HEX64.fullmatch(self.prev_sha) is None or _HEX64.fullmatch(self.sha) is None:
            raise Refuse("CHAIN")

    def __repr__(self) -> str:
        return f"PlanStep(ordinal={self.ordinal}, op={self.op!r})"


@dataclass(frozen=True, slots=True)
class QueryPlan:
    """Bounded search plan. This object does not fetch."""

    schema: str
    text: str
    cred_id: str
    rail: str
    limit: int
    clamped: bool
    fence: str
    retry_used: int
    terms: tuple[Term, ...]
    steps: tuple[PlanStep, ...]
    cache_key: str
    digest: str

    def __post_init__(self) -> None:
        if type(self.schema) is not str or not const_eq(self.schema, SCHEMA):
            raise Refuse("BAD_SCHEMA")
        if type(self.clamped) is not bool:
            raise Refuse("NOT_BOOL")
        if type(self.limit) is not int:
            raise Refuse("NOT_INT")
        if self.limit < 1 or self.limit > RESULT_CAP:
            raise Refuse("BAD_LIMIT")
        if self.clamped and self.limit != RESULT_CAP:
            raise Refuse("BAD_LIMIT")
        text = _normalize_query(self.text)
        if not const_eq(text, self.text):
            raise Refuse("BAD_PLAN")
        cred = _cred(self.cred_id)
        if not const_eq(cred, self.cred_id):
            raise Refuse("BAD_CRED")
        if type(self.rail) is not str or self.rail not in _RAIL_SET:
            raise Refuse("BAD_RAIL")
        fence = _fence(self.fence)
        if not const_eq(fence, self.fence):
            raise Refuse("BAD_FENCE")
        if type(self.retry_used) is not int or self.retry_used not in (0, 1):
            raise Refuse("BAD_PLAN")
        if type(self.terms) is not tuple or type(self.steps) is not tuple:
            raise Refuse("BAD_PLAN")
        expected_terms = _terms(text)
        if len(self.terms) != len(expected_terms):
            raise Refuse("BAD_TERM")
        for got, exp in zip(self.terms, expected_terms, strict=True):
            if type(got) is not Term or got != exp:
                raise Refuse("BAD_TERM")
        for step in self.steps:
            if type(step) is not PlanStep:
                raise Refuse("BAD_PLAN")
        expected_steps = _steps(cred, self.rail, fence, text, self.limit, self.retry_used)
        if not _steps_match(self.steps, expected_steps):
            raise Refuse("CHAIN")
        key = _cache_key(text, cred, self.rail, self.limit)
        if (
            type(self.cache_key) is not str
            or _HEX64.fullmatch(self.cache_key) is None
            or not const_eq(key, self.cache_key)
        ):
            raise Refuse("BAD_PLAN")
        digest = _plan_digest(
            text,
            cred,
            self.rail,
            self.limit,
            self.clamped,
            fence,
            self.retry_used,
            expected_terms,
            expected_steps,
            key,
        )
        if (
            type(self.digest) is not str
            or _HEX64.fullmatch(self.digest) is None
            or not const_eq(digest, self.digest)
        ):
            raise Refuse("BAD_DIGEST")

    def __repr__(self) -> str:
        return redact(
            f"QueryPlan(text={self.text!r}, cred_id={self.cred_id!r}, rail={self.rail!r}, "
            f"limit={self.limit}, clamped={self.clamped}, retry_used={self.retry_used})"
        )


@dataclass(frozen=True, slots=True)
class SearchHit:
    """One http(s) hit. Title and snippet are inside the field caps."""

    url: str
    title: str
    snippet: str

    def __post_init__(self) -> None:
        url = _http_url(self.url)
        title = _plain(self.title, TITLE_CAP)
        snippet = _plain(self.snippet, SNIPPET_CAP)
        if url is not self.url or title is not self.title or snippet is not self.snippet:
            raise Refuse("BAD_ROW")

    def __repr__(self) -> str:
        return redact(f"SearchHit(url={self.url!r}, title={self.title!r}, snippet={self.snippet!r})")


@dataclass(frozen=True, slots=True)
class IngestResult:
    """Hits kept under the count and the snippet budget, plus how many rows were dropped."""

    schema: str
    hits: tuple[SearchHit, ...]
    dropped: int
    limit: int
    budget: int

    def __post_init__(self) -> None:
        if type(self.schema) is not str or not const_eq(self.schema, SCHEMA):
            raise Refuse("BAD_SCHEMA")
        if type(self.hits) is not tuple:
            raise Refuse("BAD_ROWS")
        if type(self.limit) is not int:
            raise Refuse("NOT_INT")
        if self.limit < 1 or self.limit > RESULT_CAP:
            raise Refuse("BAD_LIMIT")
        if len(self.hits) > RESULT_CAP or len(self.hits) > self.limit:
            raise Refuse("BAD_ROWS")
        if type(self.budget) is not int:
            raise Refuse("NOT_INT")
        if self.budget < 0 or self.budget > PAYLOAD_CAP:
            raise Refuse("BAD_BUDGET")
        if type(self.dropped) is not int:
            raise Refuse("NOT_INT")
        if self.dropped < 0 or self.dropped > ROW_CAP or len(self.hits) + self.dropped > ROW_CAP:
            raise Refuse("BAD_COUNT")
        used = 0
        for hit in self.hits:
            if type(hit) is not SearchHit:
                raise Refuse("BAD_ROW")
            used += len(hit.snippet)
            if used > self.budget:
                raise Refuse("BAD_BUDGET")

    def __repr__(self) -> str:
        return redact(
            f"IngestResult(hits={len(self.hits)}, dropped={self.dropped}, "
            f"limit={self.limit}, budget={self.budget})"
        )


def _assemble(
    text: str,
    cred_id: str,
    rail: str,
    limit: int,
    clamped: bool,
    fence: str,
    retry_used: int,
) -> QueryPlan:
    terms = _terms(text)
    steps = _steps(cred_id, rail, fence, text, limit, retry_used)
    cache_key = _cache_key(text, cred_id, rail, limit)
    digest = _plan_digest(
        text,
        cred_id,
        rail,
        limit,
        clamped,
        fence,
        retry_used,
        terms,
        steps,
        cache_key,
    )
    return QueryPlan(
        schema=SCHEMA,
        text=text,
        cred_id=cred_id,
        rail=rail,
        limit=limit,
        clamped=clamped,
        fence=fence,
        retry_used=retry_used,
        terms=terms,
        steps=steps,
        cache_key=cache_key,
        digest=digest,
    )


def query(
    text: object,
    cred_id: object = None,
    limit: object = None,
    rail: object = None,
    fence: object = "",
) -> QueryPlan:
    """Return a bounded search plan for `text` and `cred_id`. No network."""
    body = _normalize_query(text)
    cred = _cred(cred_id)
    chosen = _rail(rail)
    applied, clamped = _applied_limit(limit)
    token = _fence(fence)
    return _assemble(body, cred, chosen, applied, clamped, token, 0)


def confirm_retry(plan: object, failure: object) -> QueryPlan:
    """Record one confirming retry after RATE_LIMIT. The plan does not fetch."""
    if type(plan) is not QueryPlan:
        raise Refuse("BAD_PLAN")
    name = bound_text(failure, 32)
    if secret_shape(name):
        raise Refuse("SECRET")
    if name not in _RETRY_SET:
        raise Refuse("NO_RETRY")
    if plan.retry_used != 0:
        raise Refuse("RETRY_CAP")
    return _assemble(
        plan.text,
        plan.cred_id,
        plan.rail,
        plan.limit,
        plan.clamped,
        plan.fence,
        1,
    )


def accept(plan: object, fence: object) -> QueryPlan:
    """Return `plan` when `fence` matches. A missing or different fence is STALE."""
    if type(plan) is not QueryPlan:
        raise Refuse("BAD_PLAN")
    token = _fence(fence)
    if token == "" or plan.fence == "" or not const_eq(plan.fence, token):
        raise Refuse("STALE")
    return plan


def _as_str(value: object, code: str) -> str:
    if type(value) is not str:
        raise Refuse(code)
    return value


def _as_int(value: object) -> int:
    if type(value) is not int:
        raise Refuse("NOT_INT")
    return value


def _as_bool(value: object) -> bool:
    if type(value) is not bool:
        raise Refuse("NOT_BOOL")
    return value


def _parse_term_names(value: object) -> tuple[str, ...]:
    if type(value) is not tuple:
        raise Refuse("BAD_RECORD")
    raw = cast(tuple[object, ...], value)
    names: list[str] = []
    for item in raw:
        if type(item) is not str:
            raise Refuse("BAD_TERM")
        names.append(item)
    return tuple(names)


def _parse_step_tuples(value: object) -> tuple[tuple[int, str, str, str], ...]:
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
            raise Refuse("BAD_PLAN")
        if type(op) is not str or op not in _OPS:
            raise Refuse("BAD_PLAN")
        if type(prev) is not str or type(sha) is not str:
            raise Refuse("CHAIN")
        if _HEX64.fullmatch(prev) is None or _HEX64.fullmatch(sha) is None:
            raise Refuse("CHAIN")
        if ordinal in seen:
            raise Refuse("DUPLICATE")
        seen.add(ordinal)
        parsed.append((ordinal, op, prev, sha))
    return tuple(parsed)


def _record_steps_match(
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
    if type(plan) is not QueryPlan:
        raise Refuse("BAD_PLAN")
    return (
        plan.schema,
        plan.text,
        plan.cred_id,
        plan.rail,
        plan.limit,
        plan.clamped,
        plan.fence,
        plan.retry_used,
        tuple(term.text for term in plan.terms),
        tuple((step.ordinal, step.op, step.prev_sha, step.sha) for step in plan.steps),
        plan.digest,
    )


def rebuild(record: object) -> QueryPlan:
    """Reproduce a plan from `emit` records. A broken link or digest refuses."""
    if type(record) is not tuple:
        raise Refuse("BAD_RECORD")
    row = cast(tuple[object, ...], record)
    if len(row) != _RECORD_LEN:
        raise Refuse("BAD_RECORD")
    schema = row[0]
    if type(schema) is not str or not const_eq(schema, SCHEMA):
        raise Refuse("BAD_SCHEMA")
    text = _as_str(row[1], "BAD_RECORD")
    cred_id = _as_str(row[2], "BAD_RECORD")
    rail = _as_str(row[3], "BAD_RECORD")
    limit = _as_int(row[4])
    clamped = _as_bool(row[5])
    fence = _as_str(row[6], "BAD_RECORD")
    retry_used = _as_int(row[7])
    parsed_terms = _parse_term_names(row[8])
    parsed_steps = _parse_step_tuples(row[9])
    digest = _as_str(row[10], "BAD_DIGEST")
    built = _assemble(text, cred_id, rail, limit, clamped, fence, retry_used)
    if tuple(term.text for term in built.terms) != parsed_terms:
        raise Refuse("BAD_TERM")
    if not _record_steps_match(built.steps, parsed_steps):
        raise Refuse("CHAIN")
    if not const_eq(built.digest, digest):
        raise Refuse("BAD_DIGEST")
    return built


def _field(row: dict[object, object], name: str) -> object:
    if name not in row:
        raise Refuse("BAD_ROW")
    return row[name]


def _rows(value: object) -> list[object] | tuple[object, ...]:
    if type(value) is list:
        return cast(list[object], value)
    if type(value) is tuple:
        return cast(tuple[object, ...], value)
    raise Refuse("BAD_ROWS")


def _hit(row: object) -> SearchHit:
    if type(row) is not dict:
        raise Refuse("BAD_ROW")
    found: dict[object, object] = cast(dict[object, object], row)
    shaped: dict[str, object] = {}
    for key in found:
        if type(key) is not str or key not in _FIELDS:
            raise Refuse("BAD_ROW")
        shaped[key] = found[key]
    if len(shaped) != len(_FIELDS):
        raise Refuse("BAD_ROW")
    return SearchHit(
        url=cast(str, _field(found, "url")),
        title=cast(str, _field(found, "title")),
        snippet=cast(str, _field(found, "snippet")),
    )


def ingest(rows: object, limit: object = None, budget: object = None) -> IngestResult:
    """Keep hits that fit the count and the remaining snippet budget.

    A valid hit that does not fit is skipped. Later hits that fit are kept.
    A malformed row refuses, including a row past the count cap.
    """
    items = _rows(rows)
    if len(items) > ROW_CAP:
        raise Refuse("TOO_MANY")
    keep, _clamped = _applied_limit(limit)
    budget_cap = _applied_budget(budget)
    hits: list[SearchHit] = []
    dropped = 0
    room = budget_cap
    seen = 0
    for row in items:
        seen += 1
        if seen > ROW_CAP:
            raise Refuse("TOO_MANY")
        hit = _hit(row)
        size = len(hit.snippet)
        if len(hits) >= keep or size > room:
            dropped += 1
            continue
        hits.append(hit)
        room -= size
    return IngestResult(
        schema=SCHEMA,
        hits=tuple(hits),
        dropped=dropped,
        limit=keep,
        budget=budget_cap,
    )


__all__ = [
    "CRED_CAP",
    "PAYLOAD_CAP",
    "QUERY_CAP",
    "RAIL",
    "RAILS",
    "RESULT_CAP",
    "RETRY_CLASS",
    "ROW_CAP",
    "SCHEMA",
    "SNIPPET_CAP",
    "TERM_CAP",
    "TERM_LEN",
    "TITLE_CAP",
    "URL_CAP",
    "IngestResult",
    "PlanStep",
    "QueryPlan",
    "SearchHit",
    "Term",
    "accept",
    "confirm_retry",
    "emit",
    "ingest",
    "query",
    "rebuild",
]
