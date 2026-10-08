"""Defensive labeler. It names operator intent and does not run it.

Content that matches secret_shape is labeled SECRET. The span stays numeric so
repr stays free of the raw shape.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final

from cosmos_hermes import Refuse, bound_int, bound_text, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-threat_scan/1"
TEXT_CAP: Final[int] = 8000
ASK_MAX: Final[int] = 1_000_000_000
CLEAN: Final[str] = "CLEAN"
HARDLINE: Final[str] = "HARDLINE"
SECRET: Final[str] = "SECRET"
FORCE_PUBLISH: Final[str] = "force-publish"
APPROVAL_BYPASS: Final[str] = "approval-bypass"
PIPE_TO_INTERPRETER: Final[str] = "pipe-to-interpreter"
DESTRUCTIVE_WIPE: Final[str] = "destructive-wipe"
SECRET_SHAPED: Final[str] = "secret-shaped"
_SECRET_LABEL: Final[str] = "secret-shaped"
_CODES: Final[frozenset[str]] = frozenset({CLEAN, HARDLINE, SECRET})

# Longer `--force-with-lease` is listed before `--force` so the span is not a prefix.
_RULES: Final[tuple[tuple[str, str, str, str], ...]] = (
    (
        "force_lease",
        FORCE_PUBLISH,
        "git push --force-with-lease",
        r"\bgit\s+push\s+--force-with-lease(?![\w-])",
    ),
    (
        "force_long",
        FORCE_PUBLISH,
        "git push --force",
        r"\bgit\s+push\s+--force(?![\w-])",
    ),
    (
        "force_short",
        FORCE_PUBLISH,
        "git push -f",
        r"\bgit\s+push\s+-f(?![\w-])",
    ),
    (
        "disable",
        APPROVAL_BYPASS,
        "disable approval",
        r"\bdisable\s+approval(?![\w-])",
    ),
    (
        "yolo_flag",
        APPROVAL_BYPASS,
        "--yolo",
        r"(?<![\w-])--yolo(?![\w-])",
    ),
    (
        "yolo_slash",
        APPROVAL_BYPASS,
        "/yolo",
        r"(?<!\S)/yolo(?![\w-])",
    ),
    (
        "yolo_env",
        APPROVAL_BYPASS,
        "HERMES_YOLO_MODE",
        r"\bHERMES_YOLO_MODE(?![\w-])",
    ),
    (
        "iex",
        PIPE_TO_INTERPRETER,
        "invoke-expression",
        r"\binvoke-expression(?![\w-])",
    ),
    (
        "curl",
        PIPE_TO_INTERPRETER,
        "curl |",
        r"\bcurl\s+\|",
    ),
    (
        "rm_rf",
        DESTRUCTIVE_WIPE,
        "rm -rf",
        r"\brm\s+-rf(?![\w-])",
    ),
    (
        "rm_fr",
        DESTRUCTIVE_WIPE,
        "rm -fr",
        r"\brm\s+-fr(?![\w-])",
    ),
)

_OPS: Final[re.Pattern[str]] = re.compile(
    "|".join(f"(?P<{group}>{pattern})" for group, _, _, pattern in _RULES),
    re.IGNORECASE,
)
_GROUP_META: Final[Mapping[str, tuple[str, str]]] = {
    group: (category, label) for group, category, label, _ in _RULES
}
_SECRET_RE: Final[re.Pattern[str]] = re.compile(
    r"sk-[A-Za-z0-9_\-]{8,}"
    r"|(?i:\bBearer\s+[A-Za-z0-9._\-]{8,})"
    r"|(?i:\b(?:api_key|apikey|token|secret|password|authorization)\b\s*[:=]\s*\S+)"
)


def _label_table() -> dict[str, frozenset[str]]:
    buckets: dict[str, set[str]] = {}
    for _, category, label, _ in _RULES:
        found = buckets.get(category)
        if found is None:
            buckets[category] = {label}
        else:
            found.add(label)
    buckets[SECRET_SHAPED] = {_SECRET_LABEL}
    return {key: frozenset(value) for key, value in buckets.items()}


_LABELS: Final[Mapping[str, frozenset[str]]] = _label_table()
CATEGORIES: Final[frozenset[str]] = frozenset(_LABELS)
LABELS: Final[frozenset[str]] = frozenset(label for names in _LABELS.values() for label in names)


def _offset(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("NOT_INT")
    return value


def _hit_key(hit: Finding) -> tuple[int, int, str, str]:
    return (hit.start, hit.end, hit.category, hit.label)


def _primary(hits: tuple[Finding, ...]) -> Finding:
    for hit in hits:
        if hit.category != SECRET_SHAPED:
            return hit
    return hits[0]


@dataclass(frozen=True, slots=True)
class Policy:
    """Applied text cap and the cap the caller asked for."""

    cap: int
    asked: int

    def __post_init__(self) -> None:
        cap = _offset(self.cap)
        asked = _offset(self.asked)
        if cap < 1 or cap > TEXT_CAP or asked < 1 or asked > ASK_MAX:
            raise Refuse("OUT_OF_RANGE")
        if asked > TEXT_CAP:
            if cap != TEXT_CAP:
                raise Refuse("BAD_POLICY")
            return
        if cap != asked:
            raise Refuse("BAD_POLICY")


@dataclass(frozen=True, slots=True)
class Finding:
    """One labeled span. The label is a fixed operator phrase, not a slice of the text."""

    category: str
    label: str
    start: int
    end: int

    def __post_init__(self) -> None:
        allowed = _LABELS.get(self.category)
        if allowed is None or self.label not in allowed:
            raise Refuse("BAD_HIT")
        start = _offset(self.start)
        end = _offset(self.end)
        if start < 0 or end <= start or end > TEXT_CAP:
            raise Refuse("OUT_OF_RANGE")


@dataclass(frozen=True, slots=True)
class Scan:
    """Frozen classification. `start` and `end` are offsets into the bounded text."""

    code: str
    category: str
    start: int
    end: int
    label: str
    policy: Policy
    hits: tuple[Finding, ...]

    def __post_init__(self) -> None:
        if self.code not in _CODES:
            raise Refuse("BAD_CODE")
        if not isinstance(self.policy, Policy):
            raise Refuse("BAD_POLICY")
        if not isinstance(self.hits, tuple):
            raise Refuse("BAD_HIT")
        previous: tuple[int, int, str, str] | None = None
        for hit in self.hits:
            if not isinstance(hit, Finding):
                raise Refuse("BAD_HIT")
            if hit.end > self.policy.cap:
                raise Refuse("OUT_OF_RANGE")
            key = _hit_key(hit)
            if previous is not None and previous >= key:
                raise Refuse("BAD_SCAN")
            previous = key
        if self.code == CLEAN:
            if (
                self.category != ""
                or self.label != ""
                or self.hits != ()
                or self.start != -1
                or self.end != -1
            ):
                raise Refuse("BAD_SCAN")
            return
        if not self.hits:
            raise Refuse("BAD_SCAN")
        primary = _primary(self.hits)
        if (
            self.category != primary.category
            or self.label != primary.label
            or self.start != primary.start
            or self.end != primary.end
        ):
            raise Refuse("BAD_SCAN")
        if self.code == SECRET:
            if any(hit.category != SECRET_SHAPED for hit in self.hits):
                raise Refuse("BAD_SCAN")
            return
        if self.category == SECRET_SHAPED or not any(
            hit.category != SECRET_SHAPED for hit in self.hits
        ):
            raise Refuse("BAD_SCAN")


def resolve_cap(asked: object = None) -> Policy:
    """Return the applied cap. A higher ask is ignored and recorded."""

    if asked is None:
        return Policy(TEXT_CAP, TEXT_CAP)
    value = bound_int(asked, 1, ASK_MAX)
    if value > TEXT_CAP:
        return Policy(TEXT_CAP, value)
    return Policy(value, value)


def _operator_hits(text: str) -> list[Finding]:
    found: list[Finding] = []
    for match in _OPS.finditer(text):
        name = match.lastgroup
        if name is None:
            raise Refuse("BAD_SCAN")
        meta = _GROUP_META.get(name)
        if meta is None:
            raise Refuse("BAD_SCAN")
        category, label = meta
        found.append(Finding(category, label, match.start(), match.end()))
    return found


def _secret_hits(text: str) -> list[Finding]:
    found: list[Finding] = []
    for match in _SECRET_RE.finditer(text):
        found.append(Finding(SECRET_SHAPED, _SECRET_LABEL, match.start(), match.end()))
    return found


def scan(text: object, text_cap: object = None) -> Scan:
    """Label one bounded text. Empty text refuses. The same text returns the same scan."""

    policy = resolve_cap(text_cap)
    body = bound_text(text, policy.cap)
    if body.strip() == "":
        raise Refuse("EMPTY")
    # secret_shape is the authority. A match without a local span still covers the text.
    hidden = secret_shape(body)
    found = _operator_hits(body)
    if hidden:
        secret_hits = _secret_hits(body)
        if not secret_hits:
            secret_hits = [Finding(SECRET_SHAPED, _SECRET_LABEL, 0, len(body))]
        found.extend(secret_hits)
    found.sort(key=_hit_key)
    hits = tuple(found)
    if not hits:
        return Scan(CLEAN, "", -1, -1, "", policy, ())
    primary = _primary(hits)
    code = HARDLINE if any(hit.category != SECRET_SHAPED for hit in hits) else SECRET
    return Scan(code, primary.category, primary.start, primary.end, primary.label, policy, hits)


__all__ = [
    "APPROVAL_BYPASS",
    "ASK_MAX",
    "CATEGORIES",
    "CLEAN",
    "DESTRUCTIVE_WIPE",
    "FORCE_PUBLISH",
    "Finding",
    "HARDLINE",
    "LABELS",
    "PIPE_TO_INTERPRETER",
    "Policy",
    "SECRET",
    "SECRET_SHAPED",
    "SCHEMA",
    "Scan",
    "TEXT_CAP",
    "resolve_cap",
    "scan",
]
