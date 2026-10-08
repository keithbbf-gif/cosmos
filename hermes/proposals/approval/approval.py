"""Fail-closed action approval. The live cosmos_approval module stays the authority.

Classification, request, grant, and consume only. The returned descriptor does not run.
There is no off mode and no yolo mode. Silence past the deadline is a deny.
"""

from __future__ import annotations

import hashlib
import json
import re
import secrets
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from fnmatch import fnmatchcase

from cosmos_hermes import PathJail, Refuse, bound_bytes, bound_int, bound_text, const_eq, secret_shape

SCHEMA = "cosmos-hermes-approval/1"
HARDLINE = "HARDLINE"
CONFIRM = "CONFIRM"
ALLOW = "ALLOW"
MODE = "enforce"
REQUEST_TTL_CAP = 900
GRANT_TTL_CAP = 120
FIELD_CAP = 4_000
ACTOR_CAP = 80
PATTERN_CAP = 200
RETRY_FAILURE = "ACTION_MISMATCH"
_NOW_MAX = 4_000_000_000
_CRED_KINDS = frozenset({"http", "publish", "spend", "install"})
_ALWAYS_CONFIRM = frozenset({"http", "publish", "spend", "install"})
_KINDS = frozenset(
    {
        "shell",
        "git",
        "file_write",
        "file_delete",
        "file_read",
        "http",
        "publish",
        "spend",
        "install",
        "other",
    }
)
_ID_CHARS = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._:-")
_CONFIRM_MARKERS = (
    "git push",
    "gh pr merge",
    "pip install",
    "npm install",
    "winget install",
    "schtasks",
    "--live",
)
_KNOWN = frozenset(
    {
        "APPROVAL_REQUESTED",
        "APPROVAL_GRANTED",
        "APPROVAL_DENIED",
        "APPROVAL_CONSUMED",
        "APPROVAL_REFUSED",
        "APPROVAL_ALLOWLISTED",
        "APPROVAL_RETRY",
        "APPROVAL_CAPPED",
    }
)
_ACTION_KEYS = ("kind", "command", "path", "url", "detail", "credential_id")
_PATH_SEGS = re.compile(r"[/\\]+")
_HIDDEN_RE = re.compile("[\u200b\u200c\u200d\u2060\ufeff\u202a\u202b\u202d\u202e\u2066\u2067\u2068]")
_DESTRUCTIVE_RE = re.compile(
    r"rm -rf|rm -fr|rmdir /s|remove-item -recurse|del /s|format |diskpart|mkfs|dd if=",
    re.IGNORECASE,
)
_PIPE_RE = re.compile(r"invoke-expression|curl.*\|", re.IGNORECASE | re.DOTALL)
_SENSITIVE_RE = re.compile(r"ledger|api_token", re.IGNORECASE)
_FORCE_FLAT = re.compile(r"git push --force|git push -f", re.IGNORECASE)
_CONFIRM_RES = tuple(
    (marker, re.compile(re.escape(marker), re.IGNORECASE)) for marker in _CONFIRM_MARKERS
)

__all__ = [
    "ALLOW",
    "CONFIRM",
    "FIELD_CAP",
    "GRANT_TTL_CAP",
    "HARDLINE",
    "MODE",
    "REQUEST_TTL_CAP",
    "RETRY_FAILURE",
    "SCHEMA",
    "Admit",
    "ApprovalGate",
    "LedgerEvent",
    "Policy",
    "Ticket",
    "Verdict",
    "action_sha",
    "canonical_json",
]


@dataclass(frozen=True, slots=True)
class Policy:
    """TTL ceiling. A higher ask is ignored and kept on the asked fields."""

    request_ttl_s: int
    grant_ttl_s: int
    asked_request_ttl_s: int
    asked_grant_ttl_s: int
    request_capped: bool
    grant_capped: bool


@dataclass(frozen=True, slots=True)
class Verdict:
    """Classification of one normalized action."""

    cls: str
    rules: tuple[str, ...]
    action_sha: str


@dataclass(frozen=True, slots=True)
class Ticket:
    """Pending confirm, or an allow that needs no nonce."""

    cls: str
    request_id: str
    action_sha: str
    exp: int
    applied_ttl_s: int
    capped: bool


@dataclass(frozen=True, slots=True)
class Admit:
    """Descriptor for a later executor. This package does not run it."""

    cls: str
    request_id: str
    action_sha: str
    nonce_sha: str


@dataclass(frozen=True, slots=True)
class LedgerEvent:
    """One ledger row. Action and nonce appear only as sha256 hex."""

    schema: str
    event: str
    request_id: str
    principal_sha: str
    action_sha: str
    nonce_sha: str
    exp: int
    at: int
    cls: str
    kind: str
    pattern: str
    retries: int


@dataclass(frozen=True, slots=True)
class _Request:
    request_id: str
    principal_sha: str
    action_sha: str
    cls: str
    request_exp: int
    grant_exp: int
    state: str
    nonce_sha: str
    retries: int

    def __repr__(self) -> str:
        return f"_Request(request_id={self.request_id!r}, state={self.state!r})"


@dataclass(frozen=True, slots=True)
class _Rule:
    principal_sha: str
    kind: str
    pattern: str
    exp: int

    def __repr__(self) -> str:
        return f"_Rule(kind={self.kind!r}, exp={self.exp!r})"


def _sha256_text(text: str) -> str:
    raw = bound_bytes(text.encode("utf-8"))
    return hashlib.sha256(raw).hexdigest()


def _hash_eq(left_sha: str, right_sha: str) -> bool:
    return const_eq(left_sha, right_sha)


def canonical_json(action: Mapping[str, str]) -> str:
    """Canonical action JSON. Key order does not change the bytes."""
    body: dict[str, str] = {}
    for key in _ACTION_KEYS:
        if key not in action:
            raise Refuse("BAD_ACTION")
        value = action[key]
        if not isinstance(value, str):
            raise Refuse("BAD_ACTION")
        body[key] = value
    return json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def action_sha(action: Mapping[str, str]) -> str:
    """sha256 of `canonical_json`."""
    return _sha256_text(canonical_json(action))


def _cap(asked: int, ceiling: int) -> tuple[int, bool]:
    if isinstance(asked, bool) or not isinstance(asked, int):
        raise Refuse("NOT_INT")
    if asked < 1:
        raise Refuse("OUT_OF_RANGE", "1..cap")
    if asked > ceiling:
        return ceiling, True
    return asked, False


def _now(now: object) -> int:
    return bound_int(now, 0, _NOW_MAX)


def _actor(value: object) -> str:
    text = bound_text(value, ACTOR_CAP)
    if text == "":
        raise Refuse("BAD_ACTOR")
    if secret_shape(text):
        raise Refuse("SECRET")
    return text


def _mode(mode: object) -> str:
    text = bound_text(mode, 32).casefold()
    if text in {"off", "yolo"} or text != MODE:
        raise Refuse("BAD_MODE")
    return MODE


def _field(action: Mapping[str, object], key: str) -> str:
    if key not in action or action[key] is None:
        return ""
    text = bound_text(action[key], FIELD_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    return text


def _credential(kind: str, raw: str) -> str:
    if raw == "":
        if kind in _CRED_KINDS:
            raise Refuse("MISSING_CREDENTIAL")
        return ""
    if len(raw) > ACTOR_CAP or any(ch not in _ID_CHARS for ch in raw):
        raise Refuse("BAD_CREDENTIAL")
    return raw


def _normalize(action: Mapping[str, object]) -> dict[str, str]:
    kind = _field(action, "kind").casefold()
    if kind not in _KINDS:
        raise Refuse("UNCLASSIFIED")
    command = _field(action, "command")
    path = _field(action, "path")
    url = _field(action, "url")
    detail = _field(action, "detail")
    credential_id = _credential(kind, _field(action, "credential_id"))
    if kind == "file_read" and path == "":
        raise Refuse("BAD_ACTION")
    return {
        "kind": kind,
        "command": command,
        "path": path,
        "url": url,
        "detail": detail,
        "credential_id": credential_id,
    }


def _under_delme(path: str) -> bool:
    """True when a path segment is `_delme`. A substring such as `not_delme` is not."""
    return any(part.casefold() == "_delme" for part in _PATH_SEGS.split(path))


def _force_push(command: str) -> bool:
    if _FORCE_FLAT.search(command):
        return True
    folded = command.casefold()
    tokens = [tok for tok in folded.replace("\t", " ").split(" ") if tok]
    for index, tok in enumerate(tokens[:-1]):
        if tok != "git" or tokens[index + 1] != "push":
            continue
        for item in tokens[index + 2 :]:
            if item in {"-f", "--force", "--force-with-lease"} or item.startswith("--force"):
                return True
            if item.startswith("+") and len(item) > 1:
                return True
        return False
    return False


def _pipe_remote(command: str) -> bool:
    return _PIPE_RE.search(command) is not None


def _sensitive(text: str) -> bool:
    return _SENSITIVE_RE.search(text) is not None


def _destructive(command: str) -> bool:
    return _DESTRUCTIVE_RE.search(command) is not None


def _hidden(text: str) -> bool:
    return _HIDDEN_RE.search(text) is not None


def _confirm_marker(command: str) -> str:
    for marker, pattern in _CONFIRM_RES:
        if pattern.search(command):
            return marker
    return ""


def _event(
    event: str,
    *,
    request_id: str = "",
    principal_sha: str = "",
    action_sha_hex: str = "",
    nonce_sha: str = "",
    exp: int = 0,
    at: int = 0,
    cls: str = "",
    kind: str = "",
    pattern: str = "",
    retries: int = 0,
) -> LedgerEvent:
    return LedgerEvent(
        schema=SCHEMA,
        event=event,
        request_id=request_id,
        principal_sha=principal_sha,
        action_sha=action_sha_hex,
        nonce_sha=nonce_sha,
        exp=exp,
        at=at,
        cls=cls,
        kind=kind,
        pattern=pattern,
        retries=retries,
    )


class ApprovalGate:
    """Project approval events. Hardline stays hardline after a captain grant."""

    __slots__ = (
        "_by_kind",
        "_events",
        "_jail",
        "_requests",
        "_rules",
        "mode",
        "policy",
    )

    def __init__(
        self,
        roots: Sequence[str],
        *,
        mode: str = MODE,
        request_ttl_s: int = REQUEST_TTL_CAP,
        grant_ttl_s: int = GRANT_TTL_CAP,
    ) -> None:
        self.mode = _mode(mode)
        request_applied, request_capped = _cap(request_ttl_s, REQUEST_TTL_CAP)
        grant_applied, grant_capped = _cap(grant_ttl_s, GRANT_TTL_CAP)
        self.policy = Policy(
            request_ttl_s=request_applied,
            grant_ttl_s=grant_applied,
            asked_request_ttl_s=request_ttl_s,
            asked_grant_ttl_s=grant_ttl_s,
            request_capped=request_capped,
            grant_capped=grant_capped,
        )
        cleaned = [bound_text(root, FIELD_CAP) for root in roots]
        self._jail = PathJail(cleaned)
        self._events: list[LedgerEvent] = []
        self._requests: dict[str, _Request] = {}
        self._rules: list[_Rule] = []
        self._by_kind: dict[str, list[_Rule]] = {}

    def __repr__(self) -> str:
        return f"ApprovalGate(mode={self.mode!r}, events={len(self._events)})"

    @property
    def ledger(self) -> tuple[LedgerEvent, ...]:
        return tuple(self._events)

    def rebuild(self, events: Sequence[LedgerEvent]) -> None:
        """Replace the projection. Caller-supplied rows are the authority."""
        fresh: list[LedgerEvent] = []
        for event in events:
            if not isinstance(event, LedgerEvent) or event.event not in _KNOWN or event.schema != SCHEMA:
                raise Refuse("BAD_EVENT")
            fresh.append(event)
        saved_events = self._events
        saved_requests = self._requests
        saved_rules = self._rules
        saved_kinds = self._by_kind
        try:
            self._events = []
            self._requests = {}
            self._rules = []
            self._by_kind = {}
            for event in fresh:
                self._events.append(event)
                self._apply(event)
        except Refuse:
            self._events = saved_events
            self._requests = saved_requests
            self._rules = saved_rules
            self._by_kind = saved_kinds
            raise

    def classify(
        self,
        action: Mapping[str, object],
        principal: str = "",
        *,
        now: int = 0,
    ) -> Verdict:
        """Return HARDLINE, CONFIRM, or ALLOW. An unknown kind refuses."""
        if not isinstance(action, Mapping):
            raise Refuse("BAD_ACTION")
        now_i = _now(now)
        actor = "" if principal == "" else _actor(principal)
        return self._verdict(_normalize(action), actor, now_i)

    def request(
        self,
        principal: str,
        action: Mapping[str, object],
        *,
        now: int,
        deadline: int | None = None,
    ) -> Ticket:
        """Open a confirm ticket, or return ALLOW. Hardline refuses.

        `deadline` is a caller clock. A value past the policy ceiling is ignored.
        """
        if not isinstance(action, Mapping):
            raise Refuse("BAD_ACTION")
        now_i = _now(now)
        actor = _actor(principal)
        norm = _normalize(action)
        verdict = self._verdict(norm, actor, now_i)
        if verdict.cls == HARDLINE:
            self._append(
                _event(
                    "APPROVAL_REFUSED",
                    principal_sha=_sha256_text(actor),
                    action_sha_hex=verdict.action_sha,
                    at=now_i,
                    cls=HARDLINE,
                    kind=norm["kind"],
                )
            )
            raise Refuse("HARDLINE")
        self._accept_norm_path(norm["path"])
        exp, exp_capped = self._exp(now_i, deadline)
        if verdict.cls == ALLOW:
            return Ticket(
                cls=ALLOW,
                request_id="",
                action_sha=verdict.action_sha,
                exp=0,
                applied_ttl_s=self.policy.request_ttl_s,
                capped=self.policy.request_capped,
            )
        request_id = "ap-" + secrets.token_hex(8)
        self._append(
            _event(
                "APPROVAL_REQUESTED",
                request_id=request_id,
                principal_sha=_sha256_text(actor),
                action_sha_hex=verdict.action_sha,
                exp=exp,
                at=now_i,
                cls=CONFIRM,
                kind=norm["kind"],
            )
        )
        return Ticket(
            cls=CONFIRM,
            request_id=request_id,
            action_sha=verdict.action_sha,
            exp=exp,
            applied_ttl_s=exp - now_i,
            capped=exp_capped,
        )

    def grant(
        self,
        request_id: str,
        approver: str,
        action: Mapping[str, object],
        *,
        now: int,
    ) -> str:
        """Return a hex nonce. Hardline raises even when a captain asks."""
        if not isinstance(action, Mapping):
            raise Refuse("BAD_ACTION")
        now_i = _now(now)
        norm = _normalize(action)
        verdict = self._verdict(norm, "", now_i)
        if verdict.cls == HARDLINE:
            raise Refuse("HARDLINE")
        ident = bound_text(request_id, ACTOR_CAP)
        rec = self._requests.get(ident)
        if rec is None:
            raise Refuse("UNGRANTED")
        if rec.state == "CAPPED":
            raise Refuse("RETRY_CAP")
        if rec.state != "PENDING":
            raise Refuse("ALREADY")
        approver_text = _actor(approver)
        approver_sha = _sha256_text(approver_text)
        if _hash_eq(approver_sha, rec.principal_sha):
            raise Refuse("SELF")
        if not approver_text.startswith("captain:") or approver_text == "captain:":
            raise Refuse("NOT_APPROVER")
        if now_i > rec.request_exp:
            raise Refuse("EXPIRED")
        if not _hash_eq(verdict.action_sha, rec.action_sha):
            self._mismatch(rec, verdict.action_sha, now_i)
        self._accept_norm_path(norm["path"])
        nonce = secrets.token_hex(16)
        nonce_sha = _sha256_text(nonce)
        exp = now_i + self.policy.grant_ttl_s
        self._append(
            _event(
                "APPROVAL_GRANTED",
                request_id=ident,
                principal_sha=approver_sha,
                action_sha_hex=rec.action_sha,
                nonce_sha=nonce_sha,
                exp=exp,
                at=now_i,
                cls=CONFIRM,
            )
        )
        return nonce

    def deny(self, request_id: str, approver: str, *, now: int) -> None:
        """Captain deny. A later consume raises DENIED."""
        now_i = _now(now)
        ident = bound_text(request_id, ACTOR_CAP)
        rec = self._requests.get(ident)
        if rec is None or rec.state != "PENDING":
            raise Refuse("UNGRANTED")
        approver_text = _actor(approver)
        approver_sha = _sha256_text(approver_text)
        if _hash_eq(approver_sha, rec.principal_sha):
            raise Refuse("SELF")
        if not approver_text.startswith("captain:") or approver_text == "captain:":
            raise Refuse("NOT_APPROVER")
        if now_i > rec.request_exp:
            raise Refuse("EXPIRED")
        self._append(
            _event(
                "APPROVAL_DENIED",
                request_id=ident,
                principal_sha=approver_sha,
                action_sha_hex=rec.action_sha,
                at=now_i,
                cls=rec.cls,
            )
        )

    def consume(
        self,
        request_id: str,
        nonce: str,
        principal: str,
        action: Mapping[str, object],
        *,
        now: int,
    ) -> Admit:
        """Check hashes with const_eq and burn the nonce once."""
        if not isinstance(action, Mapping):
            raise Refuse("BAD_ACTION")
        now_i = _now(now)
        actor = _actor(principal)
        norm = _normalize(action)
        verdict = self._verdict(norm, actor, now_i)
        if verdict.cls == HARDLINE:
            raise Refuse("HARDLINE")
        ident = bound_text(request_id, ACTOR_CAP)
        rec = self._requests.get(ident)
        if rec is None:
            raise Refuse("UNGRANTED")
        if rec.state == "PENDING":
            if now_i > rec.request_exp:
                self._timeout(rec, now_i)
                raise Refuse("DENIED")
            raise Refuse("UNGRANTED")
        if rec.state == "DENIED":
            raise Refuse("DENIED")
        if rec.state == "CONSUMED":
            raise Refuse("REPLAY")
        if rec.state == "CAPPED":
            raise Refuse("RETRY_CAP")
        if rec.state != "GRANTED":
            raise Refuse("UNGRANTED")
        if not _hash_eq(_sha256_text(actor), rec.principal_sha):
            raise Refuse("NOT_OWNER")
        if now_i > rec.grant_exp:
            raise Refuse("EXPIRED")
        if not _hash_eq(verdict.action_sha, rec.action_sha):
            self._mismatch(rec, verdict.action_sha, now_i)
        nonce_text = bound_text(nonce, 128)
        if secret_shape(nonce_text):
            raise Refuse("SECRET")
        nonce_sha = _sha256_text(nonce_text)
        if not _hash_eq(nonce_sha, rec.nonce_sha):
            raise Refuse("BAD_NONCE")
        self._accept_norm_path(norm["path"])
        self._append(
            _event(
                "APPROVAL_CONSUMED",
                request_id=ident,
                principal_sha=rec.principal_sha,
                action_sha_hex=rec.action_sha,
                nonce_sha=rec.nonce_sha,
                exp=rec.grant_exp,
                at=now_i,
                cls=rec.cls,
            )
        )
        return Admit(cls=rec.cls, request_id=ident, action_sha=rec.action_sha, nonce_sha=rec.nonce_sha)

    def allow_rule(
        self,
        principal: str,
        kind: str,
        pattern: str,
        approver: str,
        *,
        now: int,
        ttl_s: int,
    ) -> None:
        """Standing allow for one non-hardline shape. Empty patterns refuse."""
        now_i = _now(now)
        actor = _actor(principal)
        approver_text = _actor(approver)
        actor_sha = _sha256_text(actor)
        approver_sha = _sha256_text(approver_text)
        if _hash_eq(approver_sha, actor_sha):
            raise Refuse("SELF")
        if not approver_text.startswith("captain:") or approver_text == "captain:":
            raise Refuse("NOT_APPROVER")
        kind_text = bound_text(kind, 32).casefold()
        if kind_text not in _KINDS:
            raise Refuse("UNCLASSIFIED")
        pattern_text = bound_text(pattern, PATTERN_CAP)
        if pattern_text == "":
            raise Refuse("BAD_PATTERN")
        if secret_shape(pattern_text):
            raise Refuse("SECRET")
        applied, _capped = _cap(ttl_s, self.policy.request_ttl_s)
        exp = now_i + applied
        self._append(
            _event(
                "APPROVAL_ALLOWLISTED",
                principal_sha=actor_sha,
                exp=exp,
                at=now_i,
                cls=ALLOW,
                kind=kind_text,
                pattern=pattern_text,
            )
        )

    def authorize(self, principal: str, action: Mapping[str, object], *, now: int) -> Verdict:
        """ALLOW only from a live rule. An empty or expired list refuses.

        Hardline is reported as itself, even when the allow list is empty.
        """
        if not isinstance(action, Mapping):
            raise Refuse("BAD_ACTION")
        now_i = _now(now)
        actor = "" if principal == "" else _actor(principal)
        norm = _normalize(action)
        verdict = self._verdict(norm, actor, now_i)
        if verdict.cls == HARDLINE:
            raise Refuse("HARDLINE")
        if not self._live(now_i):
            raise Refuse("EMPTY_ALLOW")
        if verdict.cls != ALLOW:
            raise Refuse("NOT_LISTED")
        self._accept_norm_path(norm["path"])
        return verdict

    def unanswered(self, request_id: str, *, now: int) -> None:
        """Silence is not consent. Pending past the deadline becomes DENIED."""
        now_i = _now(now)
        ident = bound_text(request_id, ACTOR_CAP)
        rec = self._requests.get(ident)
        if rec is None:
            raise Refuse("UNGRANTED")
        if rec.state == "DENIED":
            raise Refuse("DENIED")
        if rec.state == "CAPPED":
            raise Refuse("RETRY_CAP")
        if rec.state != "PENDING":
            raise Refuse("ALREADY")
        if now_i <= rec.request_exp:
            raise Refuse("NOT_DUE")
        self._timeout(rec, now_i)
        raise Refuse("DENIED")

    def _mismatch(self, rec: _Request, presented: str, now_i: int) -> None:
        if rec.retries >= 1:
            self._append(
                _event(
                    "APPROVAL_CAPPED",
                    request_id=rec.request_id,
                    principal_sha=rec.principal_sha,
                    action_sha_hex=presented,
                    nonce_sha=rec.nonce_sha,
                    exp=rec.grant_exp,
                    at=now_i,
                    cls=rec.cls,
                    retries=rec.retries + 1,
                )
            )
            raise Refuse("RETRY_CAP")
        self._append(
            _event(
                "APPROVAL_RETRY",
                request_id=rec.request_id,
                principal_sha=rec.principal_sha,
                action_sha_hex=presented,
                nonce_sha=rec.nonce_sha,
                exp=rec.grant_exp,
                at=now_i,
                cls=rec.cls,
                retries=rec.retries + 1,
            )
        )
        raise Refuse(RETRY_FAILURE)

    def _append(self, event: LedgerEvent) -> None:
        self._events.append(event)
        self._apply(event)

    def _apply(self, event: LedgerEvent) -> None:
        if event.event == "APPROVAL_REQUESTED":
            if event.request_id in self._requests:
                raise Refuse("BAD_EVENT")
            self._requests[event.request_id] = _Request(
                request_id=event.request_id,
                principal_sha=event.principal_sha,
                action_sha=event.action_sha,
                cls=event.cls,
                request_exp=event.exp,
                grant_exp=0,
                state="PENDING",
                nonce_sha="",
                retries=0,
            )
            return
        if event.event == "APPROVAL_ALLOWLISTED":
            rule = _Rule(
                principal_sha=event.principal_sha,
                kind=event.kind,
                pattern=event.pattern,
                exp=event.exp,
            )
            self._rules.append(rule)
            bucket = self._by_kind.get(rule.kind)
            if bucket is None:
                self._by_kind[rule.kind] = [rule]
            else:
                bucket.append(rule)
            return
        if event.event == "APPROVAL_REFUSED":
            return
        rec = self._requests.get(event.request_id)
        if rec is None:
            raise Refuse("BAD_EVENT")
        if event.event == "APPROVAL_GRANTED":
            self._requests[event.request_id] = replace(
                rec,
                state="GRANTED",
                nonce_sha=event.nonce_sha,
                grant_exp=event.exp,
            )
            return
        if event.event == "APPROVAL_DENIED":
            self._requests[event.request_id] = replace(rec, state="DENIED")
            return
        if event.event == "APPROVAL_CONSUMED":
            self._requests[event.request_id] = replace(rec, state="CONSUMED")
            return
        if event.event == "APPROVAL_RETRY":
            self._requests[event.request_id] = replace(rec, retries=event.retries)
            return
        if event.event == "APPROVAL_CAPPED":
            self._requests[event.request_id] = replace(rec, state="CAPPED", retries=event.retries)
            return
        raise Refuse("BAD_EVENT")

    def _verdict(self, norm: Mapping[str, str], actor: str, now_i: int) -> Verdict:
        digest = action_sha(norm)
        rules = self._rules_for(norm)
        if rules:
            return Verdict(cls=HARDLINE, rules=tuple(rules), action_sha=digest)
        confirm: list[str] = []
        if norm["kind"] in _ALWAYS_CONFIRM:
            confirm.append(norm["kind"])
        marker = _confirm_marker(norm["command"])
        if marker:
            confirm.append(marker)
        if _hidden(norm["command"] + norm["path"] + norm["url"] + norm["detail"]):
            confirm.append("hidden-text")
        if confirm:
            return Verdict(cls=CONFIRM, rules=tuple(confirm), action_sha=digest)
        if actor and self._listed(actor, norm, now_i):
            return Verdict(cls=ALLOW, rules=(), action_sha=digest)
        return Verdict(cls=CONFIRM, rules=("unlisted",), action_sha=digest)

    def _exp(self, now_i: int, deadline: int | None) -> tuple[int, bool]:
        ceiling = now_i + self.policy.request_ttl_s
        if deadline is None:
            return ceiling, self.policy.request_capped
        asked = bound_int(deadline, 0, _NOW_MAX)
        if asked <= now_i:
            raise Refuse("OUT_OF_RANGE", "deadline")
        if asked > ceiling:
            return ceiling, True
        return asked, self.policy.request_capped

    def _timeout(self, rec: _Request, now_i: int) -> None:
        self._append(
            _event(
                "APPROVAL_DENIED",
                request_id=rec.request_id,
                action_sha_hex=rec.action_sha,
                at=now_i,
                cls=rec.cls,
                pattern="timeout",
            )
        )

    def _live(self, now_i: int) -> bool:
        for rule in self._rules:
            if now_i <= rule.exp:
                return True
        return False

    def _rules_for(self, norm: Mapping[str, str]) -> list[str]:
        hits: list[str] = []
        command = norm["command"]
        path = norm["path"]
        if norm["kind"] == "file_delete" and not _under_delme(path):
            hits.append("delete-outside-delme")
        if _force_push(command):
            hits.append("force-push")
        if _pipe_remote(command):
            hits.append("pipe-shell")
        if any(_sensitive(norm[key]) for key in ("command", "path", "url", "detail")):
            hits.append("ledger-or-token")
        if norm["kind"] in {"shell", "git"} and _destructive(command):
            hits.append("destructive-shell")
        return hits

    def _listed(self, principal: str, norm: Mapping[str, str], now_i: int) -> bool:
        bucket = self._by_kind.get(norm["kind"])
        if not bucket:
            return False
        principal_sha = _sha256_text(principal)
        hay = " ".join(part for part in (norm["kind"], norm["command"], norm["path"]) if part)
        for rule in bucket:
            if now_i > rule.exp:
                continue
            if not _hash_eq(rule.principal_sha, principal_sha):
                continue
            if fnmatchcase(hay, rule.pattern):
                return True
        return False

    def _accept_norm_path(self, path: str) -> None:
        if path == "":
            return
        self._jail.contain(path)
