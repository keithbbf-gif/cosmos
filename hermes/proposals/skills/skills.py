"""In-memory skill proposals. A human flag activates. This module does not mint one."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Final, cast

from cosmos_hermes import Refuse, bound_bytes, bound_int, bound_text, const_eq, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-skills/1"
NAME_CAP: Final[int] = 64
DESCRIPTION_CAP: Final[int] = 1024
BODY_CAP: Final[int] = 65536
ALLOW_CAP: Final[int] = 32
LIST_BUDGET: Final[int] = 4096
PROPOSAL_CAP: Final[int] = 32
GENESIS_FENCE: Final[str] = "0" * 64
HARDLINE_MARKS: Final[tuple[str, ...]] = (
    "rm -rf",
    "git push --force",
    "Invoke-Expression",
    "curl | sh",
    "yolo",
)
HARDLINE_NAMES: Final[frozenset[str]] = frozenset(("godmode", "drug-discovery"))

_ASK_HI: Final[int] = 1_000_000_000
_AT_MAX: Final[int] = 4_000_000_000
_ROW_CAP: Final[int] = PROPOSAL_CAP * 2
_CCR: Final[str] = "ccr:"
_PROPOSE: Final[str] = "propose"
_ACTIVATE: Final[str] = "activate"
_WITNESS_NONE: Final[str] = "-"
_NAME_RE: Final[re.Pattern[str]] = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_KEY_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9_-]+$")
_SHA_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")
_HARDLINE_RE: Final[re.Pattern[str]] = re.compile("|".join(re.escape(mark) for mark in HARDLINE_MARKS))
_KINDS: Final[frozenset[str]] = frozenset((_PROPOSE, _ACTIVATE))


def _in_policy(value: object, policy: int) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and 1 <= value <= policy


def _requested_cap(value: object, policy: int) -> tuple[int, int]:
    """Return `(applied, requested)`. Applied never exceeds policy."""

    if value is None:
        return policy, policy
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("BAD_LIMIT")
    if value < 1 or value > _ASK_HI:
        raise Refuse("BAD_LIMIT")
    if value > policy:
        return policy, value
    return value, value


def _pair(applied: int, requested: int, policy: int) -> None:
    if not _in_policy(applied, policy):
        raise Refuse("BAD_LIMIT")
    if isinstance(requested, bool) or not isinstance(requested, int):
        raise Refuse("BAD_LIMIT")
    if requested < 1 or requested > _ASK_HI:
        raise Refuse("BAD_LIMIT")
    if requested > policy:
        if applied != policy:
            raise Refuse("BAD_LIMIT")
        return
    if applied != requested:
        raise Refuse("BAD_LIMIT")


@dataclass(frozen=True, slots=True)
class Caps:
    """Applied text caps and the numbers the caller asked for."""

    name: int
    description: int
    body: int
    requested_name: int
    requested_description: int
    requested_body: int

    def __post_init__(self) -> None:
        _pair(self.name, self.requested_name, NAME_CAP)
        _pair(self.description, self.requested_description, DESCRIPTION_CAP)
        _pair(self.body, self.requested_body, BODY_CAP)


def policy_caps(
    name: object = None,
    description: object = None,
    body: object = None,
) -> Caps:
    """Clamp requested caps to policy. A higher request is ignored and recorded."""

    applied_name, requested_name = _requested_cap(name, NAME_CAP)
    applied_description, requested_description = _requested_cap(description, DESCRIPTION_CAP)
    applied_body, requested_body = _requested_cap(body, BODY_CAP)
    return Caps(
        applied_name,
        applied_description,
        applied_body,
        requested_name,
        requested_description,
        requested_body,
    )


POLICY: Final[Caps] = policy_caps()


@dataclass(frozen=True, slots=True)
class SkillText:
    """Parsed skill. `body` is the text after the closing fence."""

    name: str
    description: str
    body: str
    meta: tuple[tuple[str, str], ...]


@dataclass(frozen=True, slots=True)
class Proposal:
    """Content-addressed proposal. `state` is PROPOSED, ACTIVE, or SUPERSEDED."""

    sha: str
    name: str
    description: str
    state: str


@dataclass(frozen=True, slots=True)
class ActiveSkill:
    """One installed skill. `principal` is the CCr id that presented the human flag."""

    name: str
    description: str
    sha: str
    version: int
    principal: str


@dataclass(frozen=True, slots=True)
class SkillCard:
    """Progressive-disclosure row. Name and description only."""

    name: str
    description: str


@dataclass(frozen=True, slots=True)
class Row:
    """One ledger row. `fence` is the previous digest. `witness` is not a flag."""

    seq: int
    kind: str
    sha: str
    fence: str
    digest: str
    at: int
    text: str
    principal: str
    witness: str

    def __post_init__(self) -> None:
        if self.kind not in _KINDS:
            raise Refuse("BAD_RECORD")
        bound_int(self.seq, 1, _ROW_CAP)
        bound_int(self.at, 0, _AT_MAX)
        if _SHA_RE.fullmatch(self.sha) is None:
            raise Refuse("BAD_SHA")
        if _SHA_RE.fullmatch(self.fence) is None or _SHA_RE.fullmatch(self.digest) is None:
            raise Refuse("BAD_SHA")
        text = bound_text(self.text, BODY_CAP)
        if secret_shape(self.principal):
            raise Refuse("HARDLINE", "secret shape")
        if self.kind == _PROPOSE:
            if self.principal != "" or self.witness != _WITNESS_NONE or text == "":
                raise Refuse("BAD_RECORD")
            return
        if text != "":
            raise Refuse("BAD_RECORD")
        if not _is_ccr(self.principal):
            raise Refuse("NOT_CCR", "principal is not ccr")
        if _SHA_RE.fullmatch(self.witness) is None:
            raise Refuse("BAD_RECORD")


def _utf8(text: str) -> bytes:
    try:
        return text.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise Refuse("NOT_TEXT") from exc


def _sha256(text: str) -> str:
    return hashlib.sha256(_utf8(text)).hexdigest()


def _witness(flag: str) -> str:
    return hashlib.sha256(_utf8(flag)).hexdigest()


def _row_digest(fence: str, kind: str, sha: str, at: int, principal: str, witness: str) -> str:
    payload = "\n".join((fence, kind, sha, str(at), principal, witness))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _matches(sha: str, text: str) -> bool:
    if len(text) > BODY_CAP:
        return False
    try:
        raw = _utf8(text)
    except Refuse as exc:
        if exc.code == "NOT_TEXT":
            return False
        raise
    if len(raw) > BODY_CAP:
        return False
    return const_eq(hashlib.sha256(raw).hexdigest(), sha)


def _is_ccr(principal: str) -> bool:
    if len(principal) < len(_CCR) or "\n" in principal or "\r" in principal:
        return False
    return const_eq(principal[: len(_CCR)], _CCR)


def _name_blocked(name: str) -> bool:
    if name in HARDLINE_NAMES:
        return True
    parts = name.split("-")
    if "godmode" in parts:
        return True
    for index in range(len(parts) - 1):
        if parts[index] == "drug" and parts[index + 1] == "discovery":
            return True
    return False


def _fit(value: str, limit: int, detail: str) -> str:
    try:
        return bound_text(value, limit)
    except Refuse as exc:
        if exc.code == "OVERSIZE":
            raise Refuse("BAD_SKILL", detail) from exc
        raise


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def _intake(text: object, caps: Caps) -> str:
    as_text = bound_text(text, caps.body)
    raw = _utf8(as_text)
    checked = bound_bytes(raw, caps.body)
    try:
        return checked.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise Refuse("NOT_TEXT") from exc


def _guard(text: str) -> None:
    if secret_shape(text):
        raise Refuse("HARDLINE", "secret shape")
    if _HARDLINE_RE.search(text) is not None:
        raise Refuse("HARDLINE", "hardline instruction")


def _opening_end(text: str) -> int:
    if not text.startswith("---"):
        raise Refuse("BAD_SKILL", "missing frontmatter")
    idx = 3
    length = len(text)
    while idx < length and text[idx] in " \t":
        idx += 1
    if idx < length and text[idx] == "\r":
        idx += 1
    if idx >= length or text[idx] != "\n":
        raise Refuse("BAD_SKILL", "opening fence is not a line")
    return idx + 1


def _split_document(text: str) -> tuple[str, str]:
    start = _opening_end(text)
    idx = start
    length = len(text)
    block: list[str] = []
    while idx < length:
        newline = text.find("\n", idx)
        if newline < 0:
            line = text[idx:]
            next_idx = length
        else:
            line = text[idx:newline]
            next_idx = newline + 1
        if line.endswith("\r"):
            line = line[:-1]
        if line.strip() == "---":
            return "\n".join(block), text[next_idx:]
        block.append(line)
        if newline < 0:
            break
        idx = next_idx
    raise Refuse("BAD_SKILL", "missing closing fence")


def _meta(block: str, caps: Caps) -> tuple[tuple[str, str], ...]:
    found: dict[str, str] = {}
    ordered: list[tuple[str, str]] = []
    for line in block.split("\n"):
        if line.strip() == "" or line.lstrip().startswith("#"):
            continue
        if line[:1] in " \t":
            raise Refuse("BAD_SKILL", "nested frontmatter is refused")
        key, sep, raw_value = line.partition(":")
        if sep != ":":
            raise Refuse("BAD_SKILL", "frontmatter line is not key: value")
        try:
            key = bound_text(key.strip(), NAME_CAP)
        except Refuse as exc:
            if exc.code == "OVERSIZE":
                raise Refuse("BAD_SKILL", "bad frontmatter key") from exc
            raise
        if _KEY_RE.fullmatch(key) is None:
            raise Refuse("BAD_SKILL", "bad frontmatter key")
        if key in found:
            raise Refuse("BAD_SKILL", "duplicate frontmatter key")
        value = _fit(_unquote(raw_value.strip()), caps.body, "frontmatter value exceeds cap")
        found[key] = value
        ordered.append((key, value))
    return tuple(ordered)


def _frontmatter(document: str, caps: Caps) -> SkillText:
    block, body = _split_document(document)
    meta = _meta(block, caps)
    found = dict(meta)
    if "name" not in found:
        raise Refuse("BAD_SKILL", "name is required")
    if "description" not in found:
        raise Refuse("BAD_SKILL", "description is required")
    name = _fit(found["name"], caps.name, "name exceeds cap")
    if _NAME_RE.fullmatch(name) is None:
        raise Refuse("BAD_SKILL", "bad name")
    if _name_blocked(name):
        raise Refuse("HARDLINE", "hardline skill name")
    description = found["description"]
    if description.strip() == "":
        raise Refuse("BAD_SKILL", "description is required")
    description = _fit(description, caps.description, "description exceeds cap")
    body = _fit(body, caps.body, "body exceeds cap")
    return SkillText(name=name, description=description, body=body, meta=meta)


def _caps_arg(caps: Caps | None) -> Caps:
    chosen = POLICY if caps is None else caps
    if not isinstance(chosen, Caps):
        raise Refuse("BAD_LIMIT")
    return chosen


def _parse_document(document: str, caps: Caps) -> SkillText:
    _guard(document)
    return _frontmatter(document, caps)


def parse_skill(text: object, caps: Caps | None = None) -> SkillText:
    """Parse agentskills frontmatter. No nested YAML. Hardline text is refused."""

    chosen = _caps_arg(caps)
    return _parse_document(_intake(text, chosen), chosen)


def _skill_name(value: object, limit: int) -> str:
    text = bound_text(value, limit)
    if _NAME_RE.fullmatch(text) is None:
        raise Refuse("BAD_SKILL", "bad name")
    if _name_blocked(text):
        raise Refuse("HARDLINE", "hardline skill name")
    return text


def _flag_id(value: object) -> str:
    text = bound_text(value, NAME_CAP)
    if secret_shape(text):
        raise Refuse("HARDLINE", "secret shape")
    if _NAME_RE.fullmatch(text) is None:
        raise Refuse("BAD_FLAG")
    if _name_blocked(text):
        raise Refuse("HARDLINE", "hardline skill name")
    return text


def _allowlist(value: object) -> tuple[str, ...] | None:
    if value is None:
        return None
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Sequence):
        raise Refuse("NOT_LIST")
    if len(value) > ALLOW_CAP:
        raise Refuse("OVERSIZE", str(ALLOW_CAP))
    names: list[str] = []
    seen: set[str] = set()
    for item in cast(Sequence[object], value):
        name = _skill_name(item, NAME_CAP)
        if name in seen:
            raise Refuse("DUPLICATE")
        seen.add(name)
        names.append(name)
    return tuple(names)


def _slug(summary: str, limit: int) -> str:
    chars: list[str] = []
    for char in summary.lower():
        if ("a" <= char <= "z") or ("0" <= char <= "9"):
            chars.append(char)
        elif chars and chars[-1] != "-":
            chars.append("-")
    while chars and chars[-1] == "-":
        chars.pop()
    slug = "".join(chars)
    if len(slug) > limit:
        slug = slug[:limit].rstrip("-")
    if _NAME_RE.fullmatch(slug) is None:
        raise Refuse("BAD_SKILL", "summary has no skill name")
    if _name_blocked(slug):
        raise Refuse("HARDLINE", "hardline skill name")
    return slug


def _by_name(item: ActiveSkill) -> str:
    return item.name


def _by_sha(item: Proposal) -> str:
    return item.sha


def _card_cost(name: str, description: str) -> int:
    return len(name) + len(description) + 1


def _rows(value: object) -> tuple[Row, ...]:
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Sequence):
        raise Refuse("BAD_RECORD")
    if len(value) > _ROW_CAP:
        raise Refuse("OVERSIZE", str(_ROW_CAP))
    parsed: list[Row] = []
    for item in cast(Sequence[object], value):
        if not isinstance(item, Row):
            raise Refuse("BAD_RECORD")
        parsed.append(item)
    return tuple(parsed)


def _check_chain(rows: tuple[Row, ...], flag: str | None) -> None:
    seen_seq: set[int] = set()
    seen_sha: set[str] = set()
    previous = GENESIS_FENCE
    last_at = -1
    witness = "" if flag is None else _witness(flag)
    for row in rows:
        if row.seq in seen_seq:
            raise Refuse("DUPLICATE")
        if row.seq != len(seen_seq) + 1:
            raise Refuse("BROKEN_CHAIN")
        seen_seq.add(row.seq)
        if row.kind == _PROPOSE:
            if row.sha in seen_sha:
                raise Refuse("DUPLICATE")
            seen_sha.add(row.sha)
            if not _matches(row.sha, row.text):
                raise Refuse("BROKEN_CHAIN")
        elif flag is None:
            raise Refuse("NO_FLAG")
        elif not const_eq(row.witness, witness):
            raise Refuse("FLAG_MISMATCH")
        if not const_eq(row.fence, previous):
            raise Refuse("STALE_FENCE")
        expected = _row_digest(row.fence, row.kind, row.sha, row.at, row.principal, row.witness)
        if not const_eq(expected, row.digest):
            raise Refuse("BROKEN_CHAIN")
        if row.at <= last_at:
            raise Refuse("CLOCK")
        last_at = row.at
        previous = row.digest


class SkillInbox:
    """Proposal inbox. Nothing is active until a human flag this module does not mint."""

    __slots__ = (
        "caps",
        "list_budget",
        "requested_list_budget",
        "_allow",
        "_allow_missing",
        "_flag",
        "_text",
        "_proposals",
        "_active",
        "_rows",
        "_at",
    )

    caps: Caps
    list_budget: int
    requested_list_budget: int
    _allow: frozenset[str]
    _allow_missing: bool
    _flag: str | None
    _text: dict[str, str]
    _proposals: dict[str, Proposal]
    _active: dict[str, ActiveSkill]
    _rows: list[Row]
    _at: int | None

    def __init__(
        self,
        *,
        name_cap: object = None,
        description_cap: object = None,
        body_cap: object = None,
        allow: object = None,
        human_flag: object = None,
        list_budget: object = None,
    ) -> None:
        self.caps = policy_caps(name_cap, description_cap, body_cap)
        applied_budget, requested_budget = _requested_cap(list_budget, LIST_BUDGET)
        self.list_budget = applied_budget
        self.requested_list_budget = requested_budget
        parsed_allow = _allowlist(allow)
        if parsed_allow is None:
            self._allow_missing = True
            self._allow = frozenset()
        else:
            self._allow_missing = False
            self._allow = frozenset(parsed_allow)
        self._flag = None if human_flag is None else _flag_id(human_flag)
        self._text = {}
        self._proposals = {}
        self._active = {}
        self._rows = []
        self._at = None

    def __repr__(self) -> str:
        return (
            f"SkillInbox(proposed={len(self._proposals)}, active={len(self._active)}, "
            f"allow={len(self._allow)})"
        )

    def _require_allow(self) -> None:
        if self._allow_missing or not self._allow:
            raise Refuse("EMPTY_ALLOW")

    def _budget(self, requested: object) -> int:
        ceiling = self.list_budget
        if requested is None:
            return ceiling
        if isinstance(requested, bool) or not isinstance(requested, int) or requested < 1:
            raise Refuse("BAD_LIMIT")
        if requested > _ASK_HI:
            raise Refuse("BAD_LIMIT")
        if requested > ceiling:
            return ceiling
        return requested

    def _verified_text(self, sha: str) -> str:
        stored = self._text.get(sha)
        if stored is None or not _matches(sha, stored):
            raise Refuse("TAMPER", "stored text does not match sha")
        return stored

    def _moment(self, value: object) -> int:
        return bound_int(value, 0, _AT_MAX)

    def _tick(self, moment: int) -> None:
        if self._at is not None and moment <= self._at:
            raise Refuse("CLOCK")

    def _make_row(self, kind: str, sha: str, at: int, text: str, principal: str, witness: str) -> Row:
        fence = GENESIS_FENCE if not self._rows else self._rows[-1].digest
        return Row(
            len(self._rows) + 1,
            kind,
            sha,
            fence,
            _row_digest(fence, kind, sha, at, principal, witness),
            at,
            text,
            principal,
            witness,
        )

    def propose(self, text: object, at: object) -> Proposal:
        """Store a SKILL.md under its sha256. Does not activate."""

        moment = self._moment(at)
        document = _intake(text, self.caps)
        parsed = _parse_document(document, self.caps)
        digest = _sha256(document)
        existing = self._proposals.get(digest)
        if existing is not None:
            self._verified_text(digest)
            return existing
        if len(self._proposals) >= PROPOSAL_CAP:
            raise Refuse("FULL")
        self._tick(moment)
        proposal = Proposal(digest, parsed.name, parsed.description, "PROPOSED")
        row = self._make_row(_PROPOSE, digest, moment, document, "", _WITNESS_NONE)
        self._text[digest] = document
        self._proposals[digest] = proposal
        self._rows.append(row)
        self._at = moment
        return proposal

    def activate(self, sha: object, principal: object, flag: object, at: object) -> ActiveSkill:
        """Install one proposal. The human flag must already exist outside this module."""

        principal_text = bound_text(principal, 256)
        if secret_shape(principal_text):
            raise Refuse("HARDLINE", "secret shape")
        if not _is_ccr(principal_text):
            raise Refuse("NOT_CCR", "principal is not ccr")
        sha_text = bound_text(sha, 256)
        if _SHA_RE.fullmatch(sha_text) is None:
            raise Refuse("BAD_SHA", "sha must be 64 lowercase hex")
        if self._flag is None:
            raise Refuse("NO_FLAG")
        presented = _flag_id(flag)
        if not const_eq(presented, self._flag):
            raise Refuse("FLAG_MISMATCH")
        moment = self._moment(at)
        self._require_allow()
        proposal = self._proposals.get(sha_text)
        if proposal is None:
            raise Refuse("NO_PROPOSAL", "unknown proposal")
        if proposal.state != "PROPOSED":
            raise Refuse("ALREADY_DECIDED", "proposal is already decided")
        if proposal.name not in self._allow:
            raise Refuse("NOT_ALLOWED")
        self._verified_text(sha_text)
        prior = self._active.get(proposal.name)
        previous: Proposal | None = None
        version = 1
        if prior is not None:
            self._verified_text(prior.sha)
            previous = self._proposals.get(prior.sha)
            if previous is None:
                raise Refuse("TAMPER", "active proposal is missing")
            version = prior.version + 1
        self._tick(moment)
        active = ActiveSkill(proposal.name, proposal.description, sha_text, version, principal_text)
        updated = Proposal(proposal.sha, proposal.name, proposal.description, "ACTIVE")
        superseded: Proposal | None = None
        if previous is not None:
            superseded = Proposal(previous.sha, previous.name, previous.description, "SUPERSEDED")
        row = self._make_row(_ACTIVATE, sha_text, moment, "", principal_text, _witness(self._flag))
        if superseded is not None:
            self._proposals[superseded.sha] = superseded
        self._proposals[sha_text] = updated
        self._active[proposal.name] = active
        self._rows.append(row)
        self._at = moment
        return active

    def list_skills(self, budget: object = None) -> tuple[SkillCard, ...]:
        """Active name and description only. Skip a card that does not fit."""

        self._require_allow()
        remaining = self._budget(budget)
        chosen: list[SkillCard] = []
        for item in sorted(self._active.values(), key=_by_name):
            if item.name not in self._allow:
                continue
            self._verified_text(item.sha)
            cost = _card_cost(item.name, item.description)
            if cost > remaining:
                continue
            remaining -= cost
            chosen.append(SkillCard(item.name, item.description))
        return tuple(chosen)

    def load(self, name: object) -> str:
        """Return active text when the stored sha still matches."""

        self._require_allow()
        name_text = _skill_name(name, self.caps.name)
        if name_text not in self._allow:
            raise Refuse("NOT_ALLOWED")
        active = self._active.get(name_text)
        if active is None:
            raise Refuse("NOT_FOUND", "no active skill")
        return self._verified_text(active.sha)

    def propose_from_task(self, summary: object, at: object) -> Proposal:
        """Store a one-line lesson as a proposal. Does not activate."""

        moment = self._moment(at)
        text = bound_text(summary, self.caps.description)
        if "\n" in text or "\r" in text or text.strip() == "":
            raise Refuse("BAD_SKILL", "summary must be one line")
        cleaned = bound_text(text.strip(), self.caps.description)
        name = _slug(cleaned, self.caps.name)
        document = f"---\nname: {name}\ndescription: {cleaned}\n---\n{cleaned}\n"
        return self.propose(document, moment)

    def ledger(self) -> tuple[Row, ...]:
        """Rows a later rebuild can replay. The human flag is not in the rows."""

        return tuple(self._rows)

    def proposals(self) -> tuple[Proposal, ...]:
        """Stored proposals in sha order. This does not enable a skill."""

        return tuple(sorted(self._proposals.values(), key=_by_sha))

    def actives(self) -> tuple[ActiveSkill, ...]:
        """Installed skills in name order. An empty allow enables none."""

        self._require_allow()
        ordered = sorted(self._active.values(), key=_by_name)
        for item in ordered:
            self._verified_text(item.sha)
        return tuple(ordered)


def rebuild(
    rows: object,
    *,
    allow: object = None,
    human_flag: object = None,
    name_cap: object = None,
    description_cap: object = None,
    body_cap: object = None,
    list_budget: object = None,
) -> SkillInbox:
    """Replay caller-supplied rows. The same flag and allow must be passed again."""

    parsed = _rows(rows)
    inbox = SkillInbox(
        allow=allow,
        human_flag=human_flag,
        name_cap=name_cap,
        description_cap=description_cap,
        body_cap=body_cap,
        list_budget=list_budget,
    )
    _check_chain(parsed, inbox._flag)
    for row in parsed:
        if row.kind == _PROPOSE:
            made = inbox.propose(row.text, row.at)
            if not const_eq(made.sha, row.sha):
                raise Refuse("BROKEN_CHAIN")
            continue
        if row.kind == _ACTIVATE:
            inbox.activate(row.sha, row.principal, human_flag, row.at)
            continue
        raise Refuse("BAD_RECORD")
    if inbox.ledger() != parsed:
        raise Refuse("BROKEN_CHAIN")
    return inbox


__all__ = [
    "ALLOW_CAP",
    "BODY_CAP",
    "DESCRIPTION_CAP",
    "GENESIS_FENCE",
    "HARDLINE_MARKS",
    "HARDLINE_NAMES",
    "LIST_BUDGET",
    "NAME_CAP",
    "POLICY",
    "PROPOSAL_CAP",
    "SCHEMA",
    "ActiveSkill",
    "Caps",
    "Proposal",
    "Row",
    "SkillCard",
    "SkillInbox",
    "SkillText",
    "parse_skill",
    "policy_caps",
    "rebuild",
]
