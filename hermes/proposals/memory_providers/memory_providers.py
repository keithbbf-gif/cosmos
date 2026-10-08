"""Built-in memory plus one external provider, as a measured projection.

No network and no index file. A missing index stays unmeasured.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Final

from cosmos_hermes import PathJail, Refuse, bound_int, bound_text, const_eq, secret_shape

SCHEMA: Final = "cosmos-hermes-memory_providers/1"

PROVIDERS: Final[tuple[str, ...]] = (
    "builtin",
    "honcho",
    "openviking",
    "mem0",
    "holographic",
    "retaindb",
    "byterover",
    "supermemory",
    "hindsight",
)

POLICY_CAP: Final = 8
TEXT_CAP: Final = 4_000
INPUT_CAP: Final = 64
BUDGET: Final = 512
GENESIS: Final = "0" * 64

_KNOWN: Final[frozenset[str]] = frozenset(PROVIDERS)
_NAME_CAP: Final = 64
_CRED_CAP: Final = 128
_SESSION_CAP: Final = 128
_ID_CAP: Final = 16
_PATH_CAP: Final = 4_096
_TERM_CAP: Final = 16
_GEN_CAP: Final = 1_000_000
_SEQ_CAP: Final = 999_999
_ENTRY_ID: Final[re.Pattern[str]] = re.compile(r"\Amem-[0-9]{6}\Z")
_TIP: Final[re.Pattern[str]] = re.compile(r"\A[0-9a-f]{64}\Z")


@dataclass(frozen=True, slots=True)
class Binding:
    """One configured provider. The credential is an id, never a raw key."""

    name: str
    credential_id: str

    def __repr__(self) -> str:
        present = self.credential_id != ""
        return f"Binding(name={self.name!r}, credential={present})"


@dataclass(frozen=True, slots=True)
class Note:
    """Caller-supplied fact used to assemble a snapshot."""

    provider: str
    session: str
    text: str

    def __repr__(self) -> str:
        return (
            f"Note(provider={self.provider!r}, session_chars={len(self.session)}, "
            f"chars={len(self.text)})"
        )


@dataclass(frozen=True, slots=True)
class Fact:
    """One chained fact in the projection."""

    provider: str
    entry_id: str
    session: str
    text: str
    satellite: bool
    link: str

    def __repr__(self) -> str:
        return (
            f"Fact(provider={self.provider!r}, entry_id={self.entry_id!r}, "
            f"satellite={self.satellite}, chars={len(self.text)})"
        )


@dataclass(frozen=True, slots=True)
class Snapshot:
    """Measured bindings and facts. `tip` is the chain head."""

    schema: str
    bindings: tuple[Binding, ...]
    facts: tuple[Fact, ...]
    generation: int
    seq: int
    tip: str

    def __repr__(self) -> str:
        return (
            f"Snapshot(schema={self.schema!r}, bindings={len(self.bindings)}, "
            f"facts={len(self.facts)}, generation={self.generation}, seq={self.seq})"
        )


@dataclass(frozen=True, slots=True)
class ProviderStatus:
    """A provider that is present in the measured snapshot."""

    name: str
    satellite: bool
    count: int
    generation: int

    def __repr__(self) -> str:
        return (
            f"ProviderStatus(name={self.name!r}, satellite={self.satellite}, "
            f"count={self.count}, generation={self.generation})"
        )


@dataclass(frozen=True, slots=True)
class Hit:
    """One selected fact. Text stays off `repr`."""

    provider: str
    entry_id: str
    session: str
    text: str
    satellite: bool

    def __repr__(self) -> str:
        return (
            f"Hit(provider={self.provider!r}, entry_id={self.entry_id!r}, "
            f"satellite={self.satellite}, chars={len(self.text)})"
        )


@dataclass(frozen=True, slots=True)
class Lookup:
    """Capped rows for one measured provider."""

    name: str
    satellite: bool
    rows: tuple[Hit, ...]
    cap: int
    applied: int
    budget: int
    spent: int
    generation: int

    def __repr__(self) -> str:
        return (
            f"Lookup(name={self.name!r}, satellite={self.satellite}, "
            f"n={len(self.rows)}, cap={self.cap}, applied={self.applied}, "
            f"spent={self.spent}, generation={self.generation})"
        )


@dataclass(frozen=True, slots=True)
class SearchResult:
    """Query hits for one measured provider. `cap` is policy."""

    provider: str
    satellite: bool
    rows: tuple[Hit, ...]
    cap: int
    applied: int
    budget: int
    spent: int
    generation: int

    def __repr__(self) -> str:
        return (
            f"SearchResult(provider={self.provider!r}, satellite={self.satellite}, "
            f"n={len(self.rows)}, cap={self.cap}, applied={self.applied}, "
            f"spent={self.spent}, generation={self.generation})"
        )


@dataclass(frozen=True, slots=True)
class Prefetch:
    """Context that would be injected. Nothing is fetched."""

    providers: tuple[str, ...]
    rows: tuple[Hit, ...]
    cap: int
    applied: int
    budget: int
    spent: int
    generation: int

    def __repr__(self) -> str:
        return (
            f"Prefetch(providers={self.providers!r}, n={len(self.rows)}, "
            f"cap={self.cap}, applied={self.applied}, spent={self.spent}, "
            f"generation={self.generation})"
        )


@dataclass(frozen=True, slots=True)
class SyncPlan:
    """Descriptor for a turn sync. `executed` stays false."""

    session: str
    providers: tuple[str, ...]
    entry_ids: tuple[str, ...]
    generation: int
    executed: bool

    def __repr__(self) -> str:
        return (
            f"SyncPlan(session_chars={len(self.session)}, providers={self.providers!r}, "
            f"n={len(self.entry_ids)}, generation={self.generation}, executed={self.executed})"
        )


def _sequence(value: object, code: str) -> Sequence[object]:
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Sequence):
        raise Refuse(code)
    return value


def _clean(value: object, limit: int) -> str:
    text = bound_text(value, limit)
    if secret_shape(text):
        raise Refuse("SECRET")
    return text


def _known(value: object) -> str:
    text = _clean(value, _NAME_CAP)
    if text not in _KNOWN:
        raise Refuse("UNKNOWN_PROVIDER")
    return text


def _required(value: object, limit: int) -> str:
    text = _clean(value, limit)
    if text.strip() == "":
        raise Refuse("EMPTY")
    return text


def _session(value: object) -> str:
    text = _clean(value, _SESSION_CAP)
    if text != "" and text.strip() == "":
        raise Refuse("EMPTY")
    return text


def _applied_limit(limit: object) -> int:
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise Refuse("NOT_INT")
    if limit < 1:
        raise Refuse("OUT_OF_RANGE", "1..")
    if limit > POLICY_CAP:
        return POLICY_CAP
    return limit


def _terms(value: object) -> tuple[str, ...]:
    text = _required(value, TEXT_CAP)
    parts = text.split()
    if len(parts) > _TERM_CAP:
        raise Refuse("OVERSIZE", str(_TERM_CAP))
    folded: list[str] = []
    for part in parts:
        folded.append(part.casefold())
    return tuple(folded)


def _one_binding(name: object, credential_id: object) -> Binding:
    checked = _known(name)
    cred = _clean(credential_id, _CRED_CAP)
    if checked == "builtin" and cred != "":
        raise Refuse("LOCAL_ONLY")
    return Binding(name=checked, credential_id=cred)


def _bindings(value: object) -> tuple[Binding, ...]:
    rows = _sequence(value, "BAD_SNAPSHOT")
    parsed: list[Binding] = []
    for item in rows:
        if not isinstance(item, Binding):
            raise Refuse("BAD_SNAPSHOT")
        parsed.append(_one_binding(item.name, item.credential_id))
    if len(parsed) == 0 or parsed[0].name != "builtin":
        raise Refuse("MISSING_BUILTIN")
    if len(parsed) > 2:
        raise Refuse("CONFLICT")
    seen: set[str] = set()
    for binding in parsed:
        if binding.name in seen:
            raise Refuse("DUPLICATE")
        seen.add(binding.name)
    return tuple(parsed)


def _name_set(bindings: tuple[Binding, ...]) -> frozenset[str]:
    return frozenset(binding.name for binding in bindings)


def _notes(value: object, names: frozenset[str]) -> tuple[tuple[str, str, str], ...]:
    rows = _sequence(value, "NOT_ROWS")
    if len(rows) > INPUT_CAP:
        raise Refuse("OVERSIZE", str(INPUT_CAP))
    out: list[tuple[str, str, str]] = []
    for item in rows:
        if not isinstance(item, Note):
            raise Refuse("BAD_SNAPSHOT")
        provider = _known(item.provider)
        if provider not in names:
            raise Refuse("UNMEASURED")
        out.append((provider, _session(item.session), _required(item.text, TEXT_CAP)))
    return tuple(out)


def _link(
    prev: str,
    provider: str,
    entry_id: str,
    session: str,
    text: str,
    satellite: bool,
) -> str:
    flag = "1" if satellite else "0"
    parts = (prev, provider, entry_id, session, text, flag)
    chunks: list[bytes] = []
    for part in parts:
        encoded = part.encode("utf-8")
        chunks.append(str(len(encoded)).encode("ascii"))
        chunks.append(b":")
        chunks.append(encoded)
        chunks.append(b";")
    return hashlib.sha256(b"".join(chunks)).hexdigest()


def _mint(prev: str, seq: int, provider: str, session: str, text: str) -> Fact:
    entry_id = f"mem-{seq:06d}"
    satellite = provider != "builtin"
    link = _link(prev, provider, entry_id, session, text, satellite)
    return Fact(
        provider=provider,
        entry_id=entry_id,
        session=session,
        text=text,
        satellite=satellite,
        link=link,
    )


def _relink(facts: tuple[Fact, ...]) -> tuple[tuple[Fact, ...], str]:
    prev = GENESIS
    out: list[Fact] = []
    for fact in facts:
        link = _link(prev, fact.provider, fact.entry_id, fact.session, fact.text, fact.satellite)
        out.append(
            Fact(
                provider=fact.provider,
                entry_id=fact.entry_id,
                session=fact.session,
                text=fact.text,
                satellite=fact.satellite,
                link=link,
            )
        )
        prev = link
    return tuple(out), prev


def _matches(text: str, terms: tuple[str, ...]) -> bool:
    folded = text.casefold()
    for term in terms:
        if term not in folded:
            return False
    return True


def _hit(fact: Fact) -> Hit:
    return Hit(
        provider=fact.provider,
        entry_id=fact.entry_id,
        session=fact.session,
        text=fact.text,
        satellite=fact.satellite,
    )


def _collect(
    facts: tuple[Fact, ...],
    provider: str | None,
    terms: tuple[str, ...] | None,
    applied: int,
) -> tuple[tuple[Hit, ...], int]:
    """One pass. Skip a fact that does not fit. Stop when the count is full."""
    chosen: list[Hit] = []
    spent = 0
    for fact in facts:
        if provider is not None and fact.provider != provider:
            continue
        if terms is not None and not _matches(fact.text, terms):
            continue
        if len(chosen) >= applied:
            break
        need = len(fact.text)
        if spent + need > BUDGET:
            continue
        chosen.append(_hit(fact))
        spent += need
    return tuple(chosen), spent


def _int_field(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refuse("BAD_SNAPSHOT")
    return value


def _verify_chain(facts: tuple[Fact, ...], tip: str) -> None:
    if not isinstance(tip, str) or _TIP.fullmatch(tip) is None:
        raise Refuse("BROKEN_CHAIN")
    prev = GENESIS
    for fact in facts:
        expect = _link(prev, fact.provider, fact.entry_id, fact.session, fact.text, fact.satellite)
        if not isinstance(fact.link, str) or not const_eq(fact.link, expect):
            raise Refuse("BROKEN_CHAIN")
        prev = expect
    if not const_eq(prev, tip):
        raise Refuse("BROKEN_CHAIN")


def _admit_facts(
    facts: object,
    names: frozenset[str],
) -> tuple[tuple[Fact, ...], int, set[str]]:
    if not isinstance(facts, tuple):
        raise Refuse("BAD_SNAPSHOT")
    if len(facts) > INPUT_CAP:
        raise Refuse("OVERSIZE", str(INPUT_CAP))
    admitted: list[Fact] = []
    seen: set[str] = set()
    highest = 0
    for item in facts:
        if not isinstance(item, Fact):
            raise Refuse("BAD_SNAPSHOT")
        provider = _known(item.provider)
        if provider not in names:
            raise Refuse("UNMEASURED")
        entry_id = _clean(item.entry_id, _ID_CAP)
        if _ENTRY_ID.fullmatch(entry_id) is None:
            raise Refuse("BAD_SNAPSHOT")
        if entry_id in seen:
            raise Refuse("DUPLICATE")
        seen.add(entry_id)
        number = int(entry_id[4:])
        if number > highest:
            highest = number
        session = _session(item.session)
        text = _required(item.text, TEXT_CAP)
        satellite = provider != "builtin"
        if not isinstance(item.satellite, bool) or item.satellite != satellite:
            raise Refuse("BAD_SNAPSHOT")
        link = bound_text(item.link, 64)
        admitted.append(
            Fact(
                provider=provider,
                entry_id=entry_id,
                session=session,
                text=text,
                satellite=satellite,
                link=link,
            )
        )
    return tuple(admitted), highest, seen


def _admit(value: object) -> Snapshot:
    if not isinstance(value, Snapshot):
        raise Refuse("BAD_SNAPSHOT")
    if not isinstance(value.schema, str) or value.schema != SCHEMA:
        raise Refuse("BAD_SNAPSHOT")
    if not isinstance(value.bindings, tuple) or not isinstance(value.facts, tuple):
        raise Refuse("BAD_SNAPSHOT")
    generation = _int_field(value.generation)
    seq = _int_field(value.seq)
    if generation < 0 or generation > _GEN_CAP or seq < 1 or seq > _SEQ_CAP:
        raise Refuse("BAD_SNAPSHOT")
    bindings = _bindings(value.bindings)
    names = _name_set(bindings)
    facts, highest, seen = _admit_facts(value.facts, names)
    if seq <= highest:
        raise Refuse("BAD_SNAPSHOT")
    nxt = f"mem-{seq:06d}"
    if nxt in seen:
        raise Refuse("DUPLICATE")
    tip = bound_text(value.tip, 64)
    _verify_chain(facts, tip)
    return Snapshot(
        schema=SCHEMA,
        bindings=bindings,
        facts=facts,
        generation=generation,
        seq=seq,
        tip=tip,
    )


def assemble(bindings: object, notes: object) -> Snapshot:
    """Build a generation-zero snapshot with a valid chain."""
    bound = _bindings(bindings)
    items = _notes(notes, _name_set(bound))
    prev = GENESIS
    facts: list[Fact] = []
    seq = 1
    for provider, session, text in items:
        fact = _mint(prev, seq, provider, session, text)
        facts.append(fact)
        prev = fact.link
        seq += 1
        if seq > _SEQ_CAP:
            raise Refuse("OVERSIZE", str(_SEQ_CAP))
    return _admit(
        Snapshot(
            schema=SCHEMA,
            bindings=bound,
            facts=tuple(facts),
            generation=0,
            seq=seq,
            tip=prev,
        )
    )


def probe_index(grants: object, raw: object) -> None:
    """Refuse a missing index path. This does not create the path."""
    if isinstance(grants, (str, bytes, bytearray)) or not isinstance(grants, (list, tuple)):
        raise Refuse("NO_GRANT")
    if len(grants) == 0:
        raise Refuse("NO_GRANT")
    typed: list[str] = []
    for item in grants:
        if not isinstance(item, str) or item == "":
            raise Refuse("NO_GRANT")
        typed.append(item)
    jail = PathJail(typed)
    path = bound_text(raw, _PATH_CAP)
    if secret_shape(path):
        raise Refuse("SECRET")
    resolved = jail.contain(path)
    if not resolved.exists():
        raise Refuse("UNMEASURED")
    raise Refuse("FOREIGN_INDEX")


class MemoryProviders:
    """In-memory projection. Reads before `rebuild` are `UNMEASURED`."""

    __slots__ = ("_snap",)

    _snap: Snapshot | None

    def __init__(self) -> None:
        self._snap = None

    def __repr__(self) -> str:
        snap = self._snap
        if snap is None:
            return "MemoryProviders(measured=False)"
        return (
            f"MemoryProviders(measured=True, providers={len(snap.bindings)}, "
            f"facts={len(snap.facts)}, generation={snap.generation})"
        )

    @property
    def cap(self) -> int:
        """Policy cap. A caller cannot raise it."""
        return POLICY_CAP

    @property
    def external(self) -> str | None:
        """Configured external name, or None when only built-in is measured."""
        snap = self._measured()
        if len(snap.bindings) < 2:
            return None
        return snap.bindings[1].name

    @property
    def generation(self) -> int:
        """Fence. A mutation must present this value as `seen`."""
        return self._measured().generation

    def _measured(self) -> Snapshot:
        snap = self._snap
        if snap is None:
            raise Refuse("UNMEASURED")
        return snap

    def _seen(self, snap: Snapshot, seen: object) -> None:
        generation = bound_int(seen, 0, _GEN_CAP)
        if generation != snap.generation:
            raise Refuse("STALE")

    def _room(self, snap: Snapshot, count: int) -> None:
        if len(snap.facts) + count > INPUT_CAP:
            raise Refuse("OVERSIZE", str(INPUT_CAP))
        if snap.seq + count - 1 > _SEQ_CAP:
            raise Refuse("OVERSIZE", str(_SEQ_CAP))
        if snap.generation >= _GEN_CAP:
            raise Refuse("OVERSIZE", str(_GEN_CAP))

    def rebuild(self, snapshot: object) -> Snapshot:
        """Replace the projection. A refusal leaves the previous snapshot."""
        admitted = _admit(snapshot)
        self._snap = admitted
        return admitted

    def export(self) -> Snapshot:
        """Return the measured snapshot. Rebuilding it reproduces this state."""
        return self._measured()

    def status(self) -> tuple[ProviderStatus, ...]:
        """Built-in first, then the external provider when one is measured."""
        snap = self._measured()
        counts: dict[str, int] = {}
        for fact in snap.facts:
            counts[fact.provider] = counts.get(fact.provider, 0) + 1
        rows: list[ProviderStatus] = []
        for binding in snap.bindings:
            rows.append(
                ProviderStatus(
                    name=binding.name,
                    satellite=binding.name != "builtin",
                    count=counts.get(binding.name, 0),
                    generation=snap.generation,
                )
            )
        return tuple(rows)

    def _require(self, snap: Snapshot, name: str) -> Binding:
        for binding in snap.bindings:
            if binding.name == name:
                return binding
        raise Refuse("UNMEASURED")

    def lookup(self, name: object) -> Lookup:
        """Return capped rows for one measured provider."""
        checked = _known(name)
        snap = self._measured()
        binding = self._require(snap, checked)
        rows, spent = _collect(snap.facts, checked, None, POLICY_CAP)
        return Lookup(
            name=binding.name,
            satellite=binding.name != "builtin",
            rows=rows,
            cap=POLICY_CAP,
            applied=POLICY_CAP,
            budget=BUDGET,
            spent=spent,
            generation=snap.generation,
        )

    def search(
        self,
        name: object,
        query: object,
        *,
        limit: object = POLICY_CAP,
    ) -> SearchResult:
        """Scan one provider. A limit above the policy cap is ignored."""
        checked = _known(name)
        terms = _terms(query)
        applied = _applied_limit(limit)
        snap = self._measured()
        self._require(snap, checked)
        rows, spent = _collect(snap.facts, checked, terms, applied)
        return SearchResult(
            provider=checked,
            satellite=checked != "builtin",
            rows=rows,
            cap=POLICY_CAP,
            applied=applied,
            budget=BUDGET,
            spent=spent,
            generation=snap.generation,
        )

    def prefetch(self, query: object, *, limit: object = POLICY_CAP) -> Prefetch:
        """Scan every measured provider in chain order. Nothing is fetched."""
        terms = _terms(query)
        applied = _applied_limit(limit)
        snap = self._measured()
        rows, spent = _collect(snap.facts, None, terms, applied)
        providers = tuple(binding.name for binding in snap.bindings)
        return Prefetch(
            providers=providers,
            rows=rows,
            cap=POLICY_CAP,
            applied=applied,
            budget=BUDGET,
            spent=spent,
            generation=snap.generation,
        )

    def remember(
        self,
        name: object,
        text: object,
        *,
        session: object = "",
        seen: object,
    ) -> Fact:
        """Store one fact. A built-in write also mirrors onto the external."""
        checked = _known(name)
        body = _required(text, TEXT_CAP)
        sess = _session(session)
        snap = self._measured()
        self._require(snap, checked)
        self._seen(snap, seen)
        external = snap.bindings[1].name if len(snap.bindings) == 2 else None
        extra = 2 if checked == "builtin" and external is not None else 1
        self._room(snap, extra)
        primary = _mint(snap.tip, snap.seq, checked, sess, body)
        facts: tuple[Fact, ...] = snap.facts + (primary,)
        tip = primary.link
        seq = snap.seq + 1
        if extra == 2 and external is not None:
            mirror = _mint(tip, seq, external, sess, body)
            facts = facts + (mirror,)
            tip = mirror.link
            seq += 1
        self._snap = Snapshot(
            schema=SCHEMA,
            bindings=snap.bindings,
            facts=facts,
            generation=snap.generation + 1,
            seq=seq,
            tip=tip,
        )
        return primary

    def forget(self, name: object, entry_id: object, *, seen: object) -> Fact:
        """Delete one built-in fact. An external name is `SATELLITE`."""
        checked = _known(name)
        ident = _clean(entry_id, _ID_CAP)
        snap = self._measured()
        self._require(snap, checked)
        self._seen(snap, seen)
        if checked != "builtin":
            raise Refuse("SATELLITE")
        if _ENTRY_ID.fullmatch(ident) is None:
            raise Refuse("ABSENT")
        match: Fact | None = None
        for fact in snap.facts:
            if fact.entry_id == ident and fact.provider == "builtin":
                match = fact
                break
        if match is None:
            raise Refuse("ABSENT")
        if snap.generation >= _GEN_CAP:
            raise Refuse("OVERSIZE", str(_GEN_CAP))
        kept = tuple(fact for fact in snap.facts if fact.entry_id != ident)
        relinked, tip = _relink(kept)
        self._snap = Snapshot(
            schema=SCHEMA,
            bindings=snap.bindings,
            facts=relinked,
            generation=snap.generation + 1,
            seq=snap.seq,
            tip=tip,
        )
        return match

    def configure(self, name: object, credential_id: object = "", *, seen: object) -> ProviderStatus:
        """Select one external provider. Built-in stays measured."""
        checked = _known(name)
        cred = _clean(credential_id, _CRED_CAP)
        if checked == "builtin" and cred != "":
            raise Refuse("LOCAL_ONLY")
        snap = self._measured()
        self._seen(snap, seen)
        if checked == "builtin":
            return self._status_named(snap, "builtin")
        current = snap.bindings[1] if len(snap.bindings) == 2 else None
        if current is not None and current.name == checked and const_eq(current.credential_id, cred):
            return self._status_named(snap, checked)
        builtin = snap.bindings[0]
        updated = (builtin, Binding(name=checked, credential_id=cred))
        if current is not None and current.name != checked:
            kept = tuple(fact for fact in snap.facts if fact.provider != current.name)
            facts, tip = _relink(kept)
        else:
            facts, tip = snap.facts, snap.tip
        if snap.generation >= _GEN_CAP:
            raise Refuse("OVERSIZE", str(_GEN_CAP))
        fresh = Snapshot(
            schema=SCHEMA,
            bindings=updated,
            facts=facts,
            generation=snap.generation + 1,
            seq=snap.seq,
            tip=tip,
        )
        self._snap = fresh
        return self._status_named(fresh, checked)

    def sync_turn(self, session: object, text: object, *, seen: object) -> SyncPlan:
        """Record the turn on each measured provider. The plan is not executed."""
        sess = _required(session, _SESSION_CAP)
        body = _required(text, TEXT_CAP)
        snap = self._measured()
        self._seen(snap, seen)
        names = tuple(binding.name for binding in snap.bindings)
        self._room(snap, len(names))
        facts = snap.facts
        tip = snap.tip
        seq = snap.seq
        ids: list[str] = []
        for name in names:
            fact = _mint(tip, seq, name, sess, body)
            facts = facts + (fact,)
            tip = fact.link
            seq += 1
            ids.append(fact.entry_id)
        self._snap = Snapshot(
            schema=SCHEMA,
            bindings=snap.bindings,
            facts=facts,
            generation=snap.generation + 1,
            seq=seq,
            tip=tip,
        )
        return SyncPlan(
            session=sess,
            providers=names,
            entry_ids=tuple(ids),
            generation=snap.generation + 1,
            executed=False,
        )

    def holds_credential(self, name: object, presented: object) -> bool:
        """True when `presented` matches the stored credential id."""
        checked = _known(name)
        incoming = _clean(presented, _CRED_CAP)
        snap = self._measured()
        binding = self._require(snap, checked)
        return const_eq(binding.credential_id, incoming)

    def _status_named(self, snap: Snapshot, name: str) -> ProviderStatus:
        count = 0
        for fact in snap.facts:
            if fact.provider == name:
                count += 1
        return ProviderStatus(
            name=name,
            satellite=name != "builtin",
            count=count,
            generation=snap.generation,
        )


__all__ = [
    "BUDGET",
    "GENESIS",
    "INPUT_CAP",
    "POLICY_CAP",
    "PROVIDERS",
    "SCHEMA",
    "TEXT_CAP",
    "Binding",
    "Fact",
    "Hit",
    "Lookup",
    "MemoryProviders",
    "Note",
    "Prefetch",
    "ProviderStatus",
    "SearchResult",
    "Snapshot",
    "SyncPlan",
    "assemble",
    "probe_index",
]
