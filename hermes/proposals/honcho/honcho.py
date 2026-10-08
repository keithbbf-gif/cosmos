"""Dialectic notes as a projection. Not a handoff. Not a SEED. No network."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Sequence
from dataclasses import dataclass

from cosmos_hermes import Refuse, bound_int, bound_text, redact, secret_shape

SCHEMA = "cosmos-hermes-honcho/1"
POLICY_CAP = 32
STORE_CAP = 256
TEXT_CAP = 25_000
PRINCIPAL_CAP = 128
NOTE_BUDGET = 600
DEPTH_CAP = 3
GENESIS = "0" * 64
NOW_MAX = 2**63 - 1
_KINDS = frozenset({"observe", "contradict"})
_SHA = re.compile(r"^[0-9a-f]{64}$")


def _principal(value: object) -> str:
    text = bound_text(value, PRINCIPAL_CAP)
    if text.strip() == "":
        raise Refuse("EMPTY")
    if secret_shape(text):
        raise Refuse("SECRET")
    return text


def _body(value: object) -> str:
    text = bound_text(value, TEXT_CAP)
    if text.strip() == "":
        raise Refuse("EMPTY")
    if secret_shape(text):
        raise Refuse("SECRET")
    return text


def _stamp(value: object) -> int:
    return bound_int(value, 0, NOW_MAX)


def _kind(value: object) -> str:
    if not isinstance(value, str) or value not in _KINDS:
        raise Refuse("BAD_KIND")
    return value


def _pair_of(kind: str, pair: object) -> int:
    paired = bound_int(pair, 0, NOW_MAX)
    if kind == "observe":
        if paired != 0:
            raise Refuse("BAD_PAIR")
        return 0
    if paired < 1:
        raise Refuse("BAD_PAIR")
    return paired


def _identity(
    principal: object,
    text: object,
    now: object,
    seq: object,
    kind: object,
    pair: object,
) -> tuple[str, str, int, int, str, int]:
    who = _principal(principal)
    body = _body(text)
    stamp = _stamp(now)
    number = bound_int(seq, 1, NOW_MAX)
    label = _kind(kind)
    paired = _pair_of(label, pair)
    return who, body, stamp, number, label, paired


def _hash_hex(value: object) -> str:
    if not isinstance(value, str) or _SHA.fullmatch(value) is None:
        raise Refuse("BAD_HASH")
    return value


def _digest(
    prev: str,
    principal: str,
    text: str,
    now: int,
    seq: int,
    kind: str,
    pair: int,
) -> str:
    payload = f"{prev}\n{principal}\n{text}\n{now}\n{seq}\n{kind}\n{pair}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def evidence_sha(
    prev: object,
    principal: object,
    text: object,
    now: object,
    seq: object,
    kind: object,
    pair: object,
) -> str:
    """Hex digest of one evidence link."""
    who, body, stamp, number, label, paired = _identity(principal, text, now, seq, kind, pair)
    link = _hash_hex(prev)
    return _digest(link, who, body, stamp, number, label, paired)


def _authority(value: object) -> None:
    if value == "handoff":
        raise Refuse("NOT_HANDOFF")
    if value != "projection":
        raise Refuse("NOT_SEED")


def _schema(value: object) -> None:
    if value != SCHEMA:
        raise Refuse("BAD_SCHEMA")


def _exact_cap(value: object, expected: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("NOT_INT")
    if value != expected:
        raise Refuse("CAP")


def _clamp(value: object, ceiling: int) -> int:
    """Ignore a request above the policy ceiling. Do not raise it."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("NOT_INT")
    if value < 1:
        raise Refuse("OUT_OF_RANGE", f"1..{ceiling}")
    if value > ceiling:
        return ceiling
    return value


def _rank(claim: Claim) -> tuple[int, int]:
    return (claim.now, claim.seq)


def _seal_claim(
    who: str,
    body: str,
    stamp: int,
    seq: int,
    kind: str,
    pair: int,
    prev: str,
) -> Claim:
    digest = _digest(prev, who, body, stamp, seq, kind, pair)
    # Frozen slots reject assignment. Seal once so the write path hashes once.
    made = Claim.__new__(Claim)
    object.__setattr__(made, "principal", who)
    object.__setattr__(made, "text", body)
    object.__setattr__(made, "now", stamp)
    object.__setattr__(made, "seq", seq)
    object.__setattr__(made, "kind", kind)
    object.__setattr__(made, "pair", pair)
    object.__setattr__(made, "prev", prev)
    object.__setattr__(made, "sha", digest)
    return made


def _claim(
    principal: object,
    text: object,
    now: object,
    seq: object,
    kind: object,
    pair: object,
    prev: object,
) -> Claim:
    who, body, stamp, number, label, paired = _identity(principal, text, now, seq, kind, pair)
    link = _hash_hex(prev)
    return _seal_claim(who, body, stamp, number, label, paired, link)


def _note(claim: Claim) -> Note:
    made = Note.__new__(Note)
    object.__setattr__(made, "principal", claim.principal)
    object.__setattr__(made, "text", claim.text)
    object.__setattr__(made, "now", claim.now)
    object.__setattr__(made, "seq", claim.seq)
    object.__setattr__(made, "kind", claim.kind)
    object.__setattr__(made, "pair", claim.pair)
    return made


@dataclass(frozen=True, slots=True)
class Claim:
    """One evidence line. A contradiction is two of these, and both stay."""

    principal: str
    text: str
    now: int
    seq: int
    kind: str
    pair: int
    prev: str
    sha: str

    def __post_init__(self) -> None:
        digest = evidence_sha(
            self.prev,
            self.principal,
            self.text,
            self.now,
            self.seq,
            self.kind,
            self.pair,
        )
        if self.sha != digest:
            raise Refuse("CHAIN")

    def __repr__(self) -> str:
        return (
            "Claim("
            f"principal={redact(self.principal)!r}, text={redact(self.text)!r}, "
            f"now={self.now}, seq={self.seq}, kind={self.kind!r}, pair={self.pair}, "
            f"prev={self.prev!r}, sha={self.sha!r})"
        )


@dataclass(frozen=True, slots=True)
class DataRecord:
    """Projection row. Authority is projection, never a SEED or a handoff."""

    schema: str
    authority: str
    principal: str
    text: str
    now: int
    seq: int
    kind: str
    pair: int
    cap: int
    prev: str
    sha: str

    def __post_init__(self) -> None:
        _authority(self.authority)
        _schema(self.schema)
        _exact_cap(self.cap, POLICY_CAP)
        digest = evidence_sha(
            self.prev,
            self.principal,
            self.text,
            self.now,
            self.seq,
            self.kind,
            self.pair,
        )
        if self.sha != digest:
            raise Refuse("CHAIN")

    def __repr__(self) -> str:
        return (
            "DataRecord("
            f"schema={self.schema!r}, authority={self.authority!r}, "
            f"principal={redact(self.principal)!r}, text={redact(self.text)!r}, "
            f"now={self.now}, seq={self.seq}, kind={self.kind!r}, pair={self.pair}, "
            f"cap={self.cap}, prev={self.prev!r}, sha={self.sha!r})"
        )


@dataclass(frozen=True, slots=True)
class Note:
    """One dialectic note. Derived from a claim. Not a handoff."""

    principal: str
    text: str
    now: int
    seq: int
    kind: str
    pair: int

    def __post_init__(self) -> None:
        _identity(self.principal, self.text, self.now, self.seq, self.kind, self.pair)

    def __repr__(self) -> str:
        return (
            "Note("
            f"principal={redact(self.principal)!r}, text={redact(self.text)!r}, "
            f"now={self.now}, seq={self.seq}, kind={self.kind!r}, pair={self.pair})"
        )


@dataclass(frozen=True, slots=True)
class Dialectic:
    """Notes for one peer. `authority` stays projection."""

    schema: str
    authority: str
    principal: str
    depth: int
    depth_cap: int
    budget: int
    budget_cap: int
    cap: int
    head: str
    used: int
    notes: tuple[Note, ...]

    def __post_init__(self) -> None:
        _authority(self.authority)
        _schema(self.schema)
        _exact_cap(self.depth_cap, DEPTH_CAP)
        _exact_cap(self.budget_cap, NOTE_BUDGET)
        _exact_cap(self.cap, POLICY_CAP)
        bound_int(self.depth, 1, DEPTH_CAP)
        bound_int(self.budget, 1, NOTE_BUDGET)
        _hash_hex(self.head)
        who = _principal(self.principal)
        if not isinstance(self.notes, tuple):
            raise Refuse("BAD_NOTE")
        used = 0
        for note in self.notes:
            if not isinstance(note, Note) or note.principal != who:
                raise Refuse("BAD_NOTE")
            used += len(note.text)
        if used != self.used:
            raise Refuse("BAD_NOTE")

    def __repr__(self) -> str:
        return (
            "Dialectic("
            f"schema={self.schema!r}, authority={self.authority!r}, "
            f"principal={redact(self.principal)!r}, depth={self.depth}, "
            f"depth_cap={self.depth_cap}, budget={self.budget}, "
            f"budget_cap={self.budget_cap}, cap={self.cap}, head={self.head!r}, "
            f"used={self.used}, notes={self.notes!r})"
        )


def _select(claims: list[Claim], budget: int) -> tuple[tuple[Note, ...], int]:
    ranked = sorted(claims, key=_rank, reverse=True)
    kept: list[Note] = []
    used = 0
    for claim in ranked:
        if len(kept) >= POLICY_CAP:
            break
        size = len(claim.text)
        if used + size > budget:
            continue
        kept.append(_note(claim))
        used += size
    return tuple(kept), used


def _rows(records: object) -> tuple[DataRecord, ...]:
    if isinstance(records, (str, bytes, bytearray)) or not isinstance(records, Sequence):
        raise Refuse("BAD_RECORD")
    rows: list[DataRecord] = []
    for item in records:
        if not isinstance(item, DataRecord):
            raise Refuse("BAD_RECORD")
        rows.append(item)
    return tuple(rows)


def _replay(
    rows: tuple[DataRecord, ...],
) -> tuple[list[Claim], dict[str, list[Claim]], int, int, str]:
    claims: list[Claim] = []
    by: dict[str, list[Claim]] = {}
    seen_seq: set[int] = set()
    seen_sha: set[str] = set()
    seen_prev: set[str] = {GENESIS}
    running = GENESIS
    expect_seq = 1
    expect_pair = 1
    pending_who: str | None = None
    pending_now: int | None = None
    for row in rows:
        if row.seq in seen_seq:
            raise Refuse("DUP_ID")
        if row.seq != expect_seq:
            raise Refuse("BAD_SEQ")
        if row.prev != running and row.prev in seen_prev:
            raise Refuse("STALE")
        if row.prev != running:
            raise Refuse("CHAIN")
        claim = _claim(row.principal, row.text, row.now, row.seq, row.kind, row.pair, row.prev)
        if claim.sha != row.sha or claim.sha in seen_sha:
            raise Refuse("CHAIN") if claim.sha != row.sha else Refuse("DUP_ID")
        if claim.kind == "observe":
            if pending_who is not None:
                raise Refuse("BAD_PAIR")
        elif pending_who is None:
            if claim.pair != expect_pair:
                raise Refuse("BAD_PAIR")
            pending_who = claim.principal
            pending_now = claim.now
        elif claim.pair != expect_pair or claim.principal != pending_who or claim.now != pending_now:
            raise Refuse("BAD_PAIR")
        else:
            pending_who = None
            pending_now = None
            expect_pair += 1
        bucket = by.get(claim.principal)
        held = 0 if bucket is None else len(bucket)
        if held + 1 > STORE_CAP:
            raise Refuse("FULL")
        if bucket is None:
            bucket = []
            by[claim.principal] = bucket
        bucket.append(claim)
        claims.append(claim)
        seen_seq.add(claim.seq)
        seen_sha.add(claim.sha)
        seen_prev.add(claim.sha)
        running = claim.sha
        expect_seq += 1
    if pending_who is not None:
        raise Refuse("BAD_PAIR")
    return claims, by, expect_seq - 1, expect_pair - 1, running


class Honcho:
    """Per-peer evidence log. Starts disabled. There is no off switch."""

    __slots__ = (
        "_on",
        "_seq",
        "_pair",
        "_head",
        "_claims",
        "_by",
        "_recorded_cap",
        "_recorded_budget",
        "_recorded_depth",
    )

    def __init__(self) -> None:
        self._on = False
        self._seq = 0
        self._pair = 0
        self._head = GENESIS
        self._claims: list[Claim] = []
        self._by: dict[str, list[Claim]] = {}
        self._recorded_cap = POLICY_CAP
        self._recorded_budget = NOTE_BUDGET
        self._recorded_depth = DEPTH_CAP

    @property
    def recorded_cap(self) -> int:
        return self._recorded_cap

    @property
    def recorded_budget(self) -> int:
        return self._recorded_budget

    @property
    def recorded_depth(self) -> int:
        return self._recorded_depth

    def __repr__(self) -> str:
        state = "enabled" if self._on else "disabled"
        return f"Honcho({state}, claims={len(self._claims)}, cap={self._recorded_cap})"

    def enable(self) -> None:
        self._on = True

    def _gate(self) -> None:
        if not self._on:
            raise Refuse("DISABLED")

    def _peer(self, principal: object) -> tuple[str, list[Claim]]:
        who = _principal(principal)
        found = self._by.get(who)
        if not found:
            raise Refuse("UNKNOWN_PEER")
        return who, found

    def _hold(self, principal: str) -> list[Claim]:
        bucket = self._by.get(principal)
        if bucket is None:
            bucket = []
            self._by[principal] = bucket
        return bucket

    def observe(self, principal: object, text: object, now: object) -> Claim:
        self._gate()
        who = _principal(principal)
        body = _body(text)
        stamp = _stamp(now)
        bucket = self._by.get(who)
        held = 0 if bucket is None else len(bucket)
        if held + 1 > STORE_CAP:
            raise Refuse("FULL")
        claim = _seal_claim(who, body, stamp, self._seq + 1, "observe", 0, self._head)
        self._seq = claim.seq
        self._head = claim.sha
        self._claims.append(claim)
        self._hold(who).append(claim)
        return claim

    def contradict(
        self,
        principal: object,
        claim_a: object,
        claim_b: object,
        now: object,
    ) -> tuple[Claim, Claim]:
        """Store both claims. Neither side replaces the other."""
        self._gate()
        who = _principal(principal)
        left = _body(claim_a)
        right = _body(claim_b)
        stamp = _stamp(now)
        bucket = self._by.get(who)
        held = 0 if bucket is None else len(bucket)
        if held + 2 > STORE_CAP:
            raise Refuse("FULL")
        pair = self._pair + 1
        first = _seal_claim(who, left, stamp, self._seq + 1, "contradict", pair, self._head)
        second = _seal_claim(who, right, stamp, self._seq + 2, "contradict", pair, first.sha)
        self._seq = second.seq
        self._pair = pair
        self._head = second.sha
        self._claims.append(first)
        self._claims.append(second)
        held_bucket = self._hold(who)
        held_bucket.append(first)
        held_bucket.append(second)
        return (first, second)

    def profile(self, principal: object, cap: object = POLICY_CAP) -> tuple[Claim, ...]:
        self._gate()
        applied = _clamp(cap, POLICY_CAP)
        self._recorded_cap = POLICY_CAP
        _who, found = self._peer(principal)
        ranked = sorted(found, key=_rank, reverse=True)
        return tuple(ranked[:applied])

    def dialectic(
        self,
        principal: object,
        budget: object = NOTE_BUDGET,
        depth: object = 1,
    ) -> Dialectic:
        """Project notes from this peer's claims. Skip text that does not fit."""
        self._gate()
        applied_budget = _clamp(budget, NOTE_BUDGET)
        applied_depth = _clamp(depth, DEPTH_CAP)
        self._recorded_budget = NOTE_BUDGET
        self._recorded_depth = DEPTH_CAP
        who, found = self._peer(principal)
        notes, used = _select(found, applied_budget)
        return Dialectic(
            schema=SCHEMA,
            authority="projection",
            principal=who,
            depth=applied_depth,
            depth_cap=DEPTH_CAP,
            budget=applied_budget,
            budget_cap=NOTE_BUDGET,
            cap=POLICY_CAP,
            head=self._head,
            used=used,
            notes=notes,
        )

    def export_projection(self) -> tuple[DataRecord, ...]:
        self._gate()
        return tuple(
            DataRecord(
                schema=SCHEMA,
                authority="projection",
                principal=claim.principal,
                text=claim.text,
                now=claim.now,
                seq=claim.seq,
                kind=claim.kind,
                pair=claim.pair,
                cap=POLICY_CAP,
                prev=claim.prev,
                sha=claim.sha,
            )
            for claim in self._claims
        )


def rebuild(records: object) -> Honcho:
    """Replay projection rows. Notes come from the same claims. No network."""
    claims, by, seq, pair, head = _replay(_rows(records))
    model = Honcho()
    model._on = True
    model._claims = claims
    model._by = by
    model._seq = seq
    model._pair = pair
    model._head = head
    return model


__all__ = [
    "DEPTH_CAP",
    "GENESIS",
    "NOTE_BUDGET",
    "POLICY_CAP",
    "PRINCIPAL_CAP",
    "SCHEMA",
    "STORE_CAP",
    "TEXT_CAP",
    "Claim",
    "DataRecord",
    "Dialectic",
    "Honcho",
    "Note",
    "evidence_sha",
    "rebuild",
]
