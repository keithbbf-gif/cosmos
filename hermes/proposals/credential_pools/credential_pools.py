"""Same-provider pool of credential ids.

A plain report of HTTP_429 or HTTP_401 cools that id until now + 60.
confirm=True on the first consecutive HTTP_429 is the one confirming retry.
The pool never stores a secret, never changes provider, and never reads a clock.
Committed adds, selections, and reports form a hash chain. rebuild replays it.
"""

from __future__ import annotations

import hashlib
import hmac
import re
from dataclasses import dataclass, replace
from typing import Final, Literal, NoReturn

from cosmos_hermes import Refuse, bound_int, bound_text, const_eq, redact, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-credential_pools/1"
POLICY_CAP: Final[int] = 8
COOLDOWN_S: Final[int] = 60
MAX_CONFIRMING_RETRIES: Final[int] = 1
RETRY_CLASS: Final[str] = "HTTP_429"

Strategy = Literal["fill_first", "round_robin", "least_used"]
Action = Literal["RETRY", "ROTATE", "HOLD"]

_NOW_HI: Final[int] = 4_000_000_000 - COOLDOWN_S
_TEXT_MAX: Final[int] = 64
_CODE_MAX: Final[int] = 32
_CAP_HI: Final[int] = 1_000_000_000
_BODY_MAX: Final[int] = 256
_GENESIS: Final[str] = "0" * 64
_STRATEGIES: Final[tuple[Strategy, ...]] = ("fill_first", "round_robin", "least_used")
_HOLD: Final[tuple[str, ...]] = ("HTTP_200", "OK", "HTTP_400", "HTTP_402", "HTTP_500")
_STRATEGY_SET: Final[frozenset[str]] = frozenset(_STRATEGIES)
_SUCCESS: Final[frozenset[str]] = frozenset(("HTTP_200", "OK"))
_CODES: Final[frozenset[str]] = frozenset((*_HOLD, RETRY_CLASS, "HTTP_401"))
_FLAGS: Final[frozenset[str]] = frozenset(("0", "1"))
_DIGITS: Final[frozenset[str]] = frozenset("0123456789")
_TOKEN: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$")
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class Cred:
    """One credential id and its rotation counters. No secret field."""

    cred_id: str
    cool_until: int | None
    request_count: int
    last_code: str
    retry_used: int


@dataclass(frozen=True, slots=True)
class Report:
    """Outcome of one status report. `cool_until` is absolute, or None."""

    cred_id: str
    code: str
    action: Action
    cool_until: int | None


@dataclass(frozen=True, slots=True)
class PoolStatus:
    """Peek at the pool. Reading it does not select or rotate."""

    schema: str
    provider: str
    strategy: Strategy
    cap: int
    requested_cap: int
    ids: tuple[str, ...]
    selected: str | None
    cooling: tuple[str, ...]
    counts: tuple[tuple[str, int], ...]
    retries: tuple[tuple[str, int], ...]


@dataclass(frozen=True, slots=True)
class PoolRecord:
    """One committed mutation. `digest` is sha256 of `prev` and `body`."""

    prev: str
    body: str
    digest: str

    def __post_init__(self) -> None:
        _check_record(self.prev, self.body, self.digest)

    def __repr__(self) -> str:
        return f"PoolRecord(digest={self.digest!r})"


def _plaintext() -> NoReturn:
    raise Refuse("PLAINTEXT")


def reveal() -> NoReturn:
    """Refuse to return secret material."""
    _plaintext()


def _chain(prev: str, body: str) -> str:
    return hashlib.sha256(f"{prev}\n{body}".encode("utf-8")).hexdigest()


def _note_record(prev: str, body: str) -> PoolRecord:
    digest = _chain(prev, body)
    record = PoolRecord.__new__(PoolRecord)
    object.__setattr__(record, "prev", prev)
    object.__setattr__(record, "body", body)
    object.__setattr__(record, "digest", digest)
    return record


def _check_record(prev: object, body: object, digest: object) -> None:
    prev_text = bound_text(prev, 64)
    body_text = bound_text(body, _BODY_MAX)
    digest_text = bound_text(digest, 64)
    if secret_shape(body_text):
        raise Refuse("SECRET")
    if _HEX.fullmatch(prev_text) is None or _HEX.fullmatch(digest_text) is None:
        raise Refuse("BAD_RECORD")
    if "\n" in body_text or "\r" in body_text:
        raise Refuse("BAD_RECORD")
    _shape(body_text)
    expected = _chain(prev_text, body_text)
    if not hmac.compare_digest(digest_text, expected):
        raise Refuse("CHAIN")


def _shape(body: str) -> None:
    parts = body.split("\t")
    kind = parts[0]
    if kind == "pool" and len(parts) == 5:
        return
    if kind == "add" and len(parts) == 2 and parts[1] != "":
        return
    if kind == "next" and len(parts) == 3 and parts[2] != "":
        return
    if kind == "report" and len(parts) == 5 and parts[4] in _FLAGS and parts[1] != "":
        return
    raise Refuse("BAD_RECORD")


def _decimal(text: str, lo: int, hi: int) -> int:
    if text == "0":
        return bound_int(0, lo, hi)
    if text == "" or len(text) > 10 or text[0] == "0":
        raise Refuse("BAD_RECORD")
    for ch in text:
        if ch not in _DIGITS:
            raise Refuse("BAD_RECORD")
    return bound_int(int(text), lo, hi)


def _token(value: object, *, missing: str, bad: str) -> str:
    text = bound_text(value, _TEXT_MAX)
    if text == "":
        raise Refuse(missing)
    if secret_shape(text):
        raise Refuse("SECRET")
    if _TOKEN.fullmatch(text) is None:
        raise Refuse(bad)
    return text


def _strategy_name(value: object) -> Strategy:
    text = bound_text(value, _CODE_MAX)
    if secret_shape(text):
        raise Refuse("SECRET")
    if text in _STRATEGY_SET:
        for name in _STRATEGIES:
            if text == name:
                return name
    if text == "random":
        raise Refuse("NONDETERMINISTIC")
    raise Refuse("UNKNOWN_STRATEGY")


def _clock(value: object) -> int:
    return bound_int(value, 0, _NOW_HI)


def _caps(requested: object) -> tuple[int, int]:
    if requested is None:
        return POLICY_CAP, POLICY_CAP
    raw = bound_int(requested, 1, _CAP_HI)
    applied = POLICY_CAP if raw > POLICY_CAP else raw
    return applied, raw


def _classify(code: object) -> str:
    text = bound_text(code, _CODE_MAX)
    if secret_shape(text):
        raise Refuse("SECRET")
    if text in _CODES:
        return text
    raise Refuse("UNCLASSIFIED")


def _flag(confirm: object) -> bool:
    if isinstance(confirm, bool):
        return confirm
    raise Refuse("UNCLASSIFIED")


def _cooling(row: Cred, now: int) -> bool:
    until = row.cool_until
    return until is not None and now < until


def _live_until(row: Cred, now: int) -> int | None:
    if _cooling(row, now):
        return row.cool_until
    return None


def _lowest_count(rows: list[Cred], eligible: list[int]) -> int:
    best = eligible[0]
    best_count = rows[best].request_count
    for index in eligible:
        count = rows[index].request_count
        if count < best_count:
            best = index
            best_count = count
    return best


def _link(prev: str, record: PoolRecord) -> None:
    if not hmac.compare_digest(record.prev, prev):
        raise Refuse("CHAIN")


def _records_of(records: object) -> tuple[PoolRecord, ...]:
    if not isinstance(records, tuple) or len(records) == 0:
        raise Refuse("BAD_RECORD")
    out: list[PoolRecord] = []
    for item in records:
        if not isinstance(item, PoolRecord):
            raise Refuse("BAD_RECORD")
        out.append(item)
    return tuple(out)


class CredentialPool:
    """Rotation ledger for one provider. Methods never return secret material."""

    __slots__ = (
        "_provider",
        "_strategy",
        "_cap",
        "_requested_cap",
        "_rows",
        "_ids",
        "_cursor",
        "_selected",
        "_seen",
        "_records",
    )

    _provider: str
    _strategy: Strategy
    _cap: int
    _requested_cap: int
    _rows: list[Cred]
    _ids: dict[str, int]
    _cursor: int
    _selected: str | None
    _seen: int | None
    _records: list[PoolRecord]

    def __init__(
        self,
        provider: object,
        *,
        strategy: object = "fill_first",
        cap: object = None,
    ) -> None:
        """Bind one provider. A cap above policy is recorded and not applied."""
        self._rows = []
        self._ids = {}
        self._cursor = -1
        self._selected = None
        self._seen = None
        self._records = []
        self._provider = _token(provider, missing="MISSING_PROVIDER", bad="BAD_PROVIDER")
        self._strategy = _strategy_name(strategy)
        self._cap, self._requested_cap = _caps(cap)
        self._note(
            f"pool\t{self._provider}\t{self._strategy}\t{self._cap}\t{self._requested_cap}"
        )

    def add(self, cred_id: object) -> Cred:
        """Store a credential id. A secret-shaped id is refused."""
        row = self._add(cred_id)
        self._note(f"add\t{row.cred_id}")
        return row

    def next_id(self, now: object) -> str:
        """Return the next id that is not cooling."""
        stamp = _clock(now)
        chosen = self._pick(stamp)
        self._commit_select(chosen, stamp)
        cred_id = self._rows[chosen].cred_id
        self._note(f"next\t{stamp}\t{cred_id}")
        return cred_id

    def report(
        self,
        cred_id: object,
        code: object,
        now: object,
        *,
        confirm: object = False,
    ) -> Report:
        """Record a status. HTTP_429 and HTTP_401 cool the id until now + 60."""
        token = _token(cred_id, missing="MISSING_ID", bad="BAD_ID")
        kind = _classify(code)
        stamp = _clock(now)
        retry = _flag(confirm)
        outcome = self._apply_report(token, kind, stamp, confirm=retry)
        flag = "1" if retry else "0"
        self._note(f"report\t{outcome.cred_id}\t{kind}\t{stamp}\t{flag}")
        return outcome

    def status(self, now: object) -> PoolStatus:
        """Return a peek. This does not select or rotate."""
        stamp = _clock(now)
        ids: list[str] = []
        cooling: list[str] = []
        counts: list[tuple[str, int]] = []
        retries: list[tuple[str, int]] = []
        want = self._selected
        visible: str | None = None
        for row in self._rows:
            ids.append(row.cred_id)
            counts.append((row.cred_id, row.request_count))
            retries.append((row.cred_id, row.retry_used))
            cooling_row = _cooling(row, stamp)
            if cooling_row:
                cooling.append(row.cred_id)
            if want is not None and const_eq(row.cred_id, want):
                if not cooling_row:
                    visible = row.cred_id
                want = None
        return PoolStatus(
            schema=SCHEMA,
            provider=self._provider,
            strategy=self._strategy,
            cap=self._cap,
            requested_cap=self._requested_cap,
            ids=tuple(ids),
            selected=visible,
            cooling=tuple(cooling),
            counts=tuple(counts),
            retries=tuple(retries),
        )

    def records(self) -> tuple[PoolRecord, ...]:
        """Return the chain. `rebuild` of this tuple reproduces the public status."""
        return tuple(self._records)

    def change_provider(self, provider: object) -> None:
        """Refuse. The pool's provider is fixed."""
        _token(provider, missing="MISSING_PROVIDER", bad="BAD_PROVIDER")
        raise Refuse("PROVIDER_FIXED")

    def reveal(self) -> NoReturn:
        """Refuse to return secret material."""
        _plaintext()

    def __repr__(self) -> str:
        provider = redact(self._provider)
        return (
            f"CredentialPool(provider={provider!r}, strategy={self._strategy!r}, "
            f"n={len(self._rows)}, cap={self._cap})"
        )

    def _note(self, body: str) -> PoolRecord:
        prev = _GENESIS if not self._records else self._records[-1].digest
        record = _note_record(prev, body)
        self._records.append(record)
        return record

    def _add(self, cred_id: object) -> Cred:
        token = _token(cred_id, missing="MISSING_ID", bad="BAD_ID")
        if self._known(token):
            raise Refuse("DUPLICATE")
        if len(self._rows) >= self._cap:
            raise Refuse("CAP", str(self._cap))
        row = Cred(
            cred_id=token,
            cool_until=None,
            request_count=0,
            last_code="",
            retry_used=0,
        )
        self._ids[token] = len(self._rows)
        self._rows.append(row)
        return row

    def _known(self, cred_id: str) -> bool:
        index = self._ids.get(cred_id)
        if index is None:
            return False
        return const_eq(self._rows[index].cred_id, cred_id)

    def _find(self, cred_id: str) -> int:
        index = self._ids.get(cred_id)
        if index is None or not const_eq(self._rows[index].cred_id, cred_id):
            raise Refuse("UNKNOWN_ID")
        return index

    def _ensure_fresh(self, now: int) -> None:
        seen = self._seen
        if seen is not None and now < seen:
            raise Refuse("STALE")

    def _eligible(self, now: int) -> list[int]:
        found: list[int] = []
        rows = self._rows
        for index in range(len(rows)):
            if not _cooling(rows[index], now):
                found.append(index)
        return found

    def _pick(self, stamp: int) -> int:
        if not self._rows:
            raise Refuse("EMPTY")
        self._ensure_fresh(stamp)
        eligible = self._eligible(stamp)
        if not eligible:
            raise Refuse("POOL_EXHAUSTED")
        return self._choose(eligible)

    def _choose(self, eligible: list[int]) -> int:
        if not eligible:
            raise Refuse("POOL_EXHAUSTED")
        strategy = self._strategy
        if strategy == "fill_first":
            return eligible[0]
        if strategy == "least_used":
            return _lowest_count(self._rows, eligible)
        return self._round_robin(eligible)

    def _round_robin(self, eligible: list[int]) -> int:
        total = len(self._rows)
        if total == 0:
            raise Refuse("POOL_EXHAUSTED")
        cursor = self._cursor
        if cursor < 0 or cursor >= total:
            start = 0
        else:
            start = (cursor + 1) % total
        allowed = set(eligible)
        for step in range(total):
            index = (start + step) % total
            if index in allowed:
                return index
        raise Refuse("POOL_EXHAUSTED")

    def _commit_select(self, chosen: int, stamp: int) -> None:
        current = self._rows[chosen]
        updated = replace(current, request_count=current.request_count + 1)
        self._rows[chosen] = updated
        self._cursor = chosen
        self._selected = updated.cred_id
        self._seen = stamp

    def _apply_report(self, token: str, kind: str, stamp: int, *, confirm: bool) -> Report:
        index = self._find(token)
        self._ensure_fresh(stamp)
        row = self._rows[index]
        if kind == RETRY_CLASS:
            outcome = self._on_429(index, row, stamp, confirm=confirm)
        elif kind == "HTTP_401":
            outcome = self._bench(index, row, "HTTP_401", stamp)
        else:
            outcome = self._hold(index, row, kind, stamp)
        self._seen = stamp
        return outcome

    def _bench(self, index: int, row: Cred, code: str, now: int) -> Report:
        until = now + COOLDOWN_S
        self._rows[index] = replace(
            row,
            cool_until=until,
            last_code=code,
            retry_used=0,
        )
        if self._selected is not None and const_eq(self._selected, row.cred_id):
            self._selected = None
            self._cursor = index
        return Report(cred_id=row.cred_id, code=code, action="ROTATE", cool_until=until)

    def _on_429(self, index: int, row: Cred, now: int, *, confirm: bool) -> Report:
        """Confirm HTTP_429 once. The next one, or any plain report, benches it."""
        if confirm and row.retry_used < MAX_CONFIRMING_RETRIES and not _cooling(row, now):
            until = _live_until(row, now)
            self._rows[index] = replace(
                row,
                cool_until=until,
                last_code=RETRY_CLASS,
                retry_used=row.retry_used + 1,
            )
            return Report(
                cred_id=row.cred_id,
                code=RETRY_CLASS,
                action="RETRY",
                cool_until=until,
            )
        return self._bench(index, row, RETRY_CLASS, now)

    def _hold(self, index: int, row: Cred, code: str, now: int) -> Report:
        until = _live_until(row, now)
        self._rows[index] = replace(
            row,
            cool_until=until,
            last_code=code,
            retry_used=0 if code in _SUCCESS else row.retry_used,
        )
        return Report(cred_id=row.cred_id, code=code, action="HOLD", cool_until=until)

    def _replay(self, record: PoolRecord) -> None:
        parts = record.body.split("\t")
        kind = parts[0]
        if kind == "add":
            if len(parts) != 2:
                raise Refuse("BAD_RECORD")
            self._add(parts[1])
            return
        if kind == "next":
            if len(parts) != 3:
                raise Refuse("BAD_RECORD")
            stamp = _decimal(parts[1], 0, _NOW_HI)
            chosen = self._pick(stamp)
            cred_id = self._rows[chosen].cred_id
            if f"next\t{stamp}\t{cred_id}" != record.body:
                raise Refuse("CHAIN")
            self._commit_select(chosen, stamp)
            return
        if kind == "report":
            if len(parts) != 5:
                raise Refuse("BAD_RECORD")
            stamp = _decimal(parts[3], 0, _NOW_HI)
            if parts[4] not in _FLAGS:
                raise Refuse("BAD_RECORD")
            self._apply_report(parts[1], _classify(parts[2]), stamp, confirm=parts[4] == "1")
            return
        raise Refuse("BAD_RECORD")


def rebuild(records: object) -> CredentialPool:
    """Replay a chain. The same records produce the same public status."""
    chain = _records_of(records)
    first = chain[0]
    _check_record(first.prev, first.body, first.digest)
    if not hmac.compare_digest(first.prev, _GENESIS):
        raise Refuse("CHAIN")
    header = first.body.split("\t")
    if len(header) != 5 or header[0] != "pool":
        raise Refuse("BAD_RECORD")
    provider = _token(header[1], missing="MISSING_PROVIDER", bad="BAD_PROVIDER")
    strategy = _strategy_name(header[2])
    applied = _decimal(header[3], 1, POLICY_CAP)
    requested = _decimal(header[4], 1, _CAP_HI)
    expect = POLICY_CAP if requested > POLICY_CAP else requested
    if applied != expect:
        raise Refuse("BAD_RECORD")
    pool = CredentialPool.__new__(CredentialPool)
    pool._provider = provider
    pool._strategy = strategy
    pool._cap = applied
    pool._requested_cap = requested
    pool._rows = []
    pool._ids = {}
    pool._cursor = -1
    pool._selected = None
    pool._seen = None
    pool._records = [first]
    prev = first.digest
    for record in chain[1:]:
        _check_record(record.prev, record.body, record.digest)
        _link(prev, record)
        kind = record.body.split("\t", 1)[0]
        if kind == "pool":
            raise Refuse("BAD_RECORD")
        pool._replay(record)
        pool._records.append(record)
        prev = record.digest
    return pool


__all__ = [
    "SCHEMA",
    "POLICY_CAP",
    "COOLDOWN_S",
    "MAX_CONFIRMING_RETRIES",
    "RETRY_CLASS",
    "Action",
    "Strategy",
    "Cred",
    "PoolRecord",
    "PoolStatus",
    "Report",
    "CredentialPool",
    "rebuild",
    "reveal",
]
