"""One messaging gateway. Idempotent ingest, drain, and delivery descriptors.

No thread, no watcher, and no socket. A later service would send ``Delivery``.
The signature is an HMAC keyed by a credential id, not by raw key material.
"""

from __future__ import annotations

import hashlib
import hmac
import re
from dataclasses import dataclass
from typing import Final, Literal

from cosmos_hermes import Refuse, bound_int, bound_text, const_eq, secret_shape

SCHEMA: Final[str] = "cosmos-hermes-gateway/1"
MESSAGE_CAP: Final[int] = 8_000
QUEUE_CAP: Final[int] = 128
PLATFORM_CAP: Final[int] = 32
FENCE_WINDOW: Final[int] = 300
_NOW_MAX: Final[int] = 4_000_000_000
_NAME_CAP: Final[int] = 32
_ID_CAP: Final[int] = 128
_SIGNER_CAP: Final[int] = 64
_GENESIS: Final[str] = "0" * 64

_NAME_RE: Final[re.Pattern[str]] = re.compile(r"\A[a-z][a-z0-9_-]{0,31}\Z")
_ID_RE: Final[re.Pattern[str]] = re.compile(r"\A[A-Za-z0-9][A-Za-z0-9._:-]{0,127}\Z")
_SIGNER_RE: Final[re.Pattern[str]] = re.compile(r"\A[a-z][a-z0-9._:-]{0,63}\Z")
_HEX_RE: Final[re.Pattern[str]] = re.compile(r"\A[0-9a-f]{64}\Z")
_STATES: Final[frozenset[str]] = frozenset(("running", "draining"))

__all__ = [
    "FENCE_WINDOW",
    "MESSAGE_CAP",
    "PLATFORM_CAP",
    "QUEUE_CAP",
    "SCHEMA",
    "Delivery",
    "Gateway",
    "IngestResult",
    "Platform",
    "Policy",
    "Receipt",
    "Shutdown",
    "Snapshot",
    "Status",
    "rebuild",
    "sign",
]


def _span(applied: int, asked: int, capped: bool, ceiling: int) -> None:
    if type(applied) is not int or type(asked) is not int or type(capped) is not bool:
        raise Refuse("BAD_POLICY")
    if applied < 1 or applied > ceiling or asked < applied:
        raise Refuse("BAD_POLICY")
    if capped:
        if applied != ceiling or asked <= ceiling:
            raise Refuse("BAD_POLICY")
        return
    if applied != asked:
        raise Refuse("BAD_POLICY")


@dataclass(frozen=True, slots=True)
class Policy:
    """Caps for one gateway. A higher ask is stored and is not applied."""

    message_cap: int
    queue_cap: int
    platform_cap: int
    asked_message_cap: int
    asked_queue_cap: int
    asked_platform_cap: int
    message_capped: bool
    queue_capped: bool
    platform_capped: bool

    def __post_init__(self) -> None:
        _span(self.message_cap, self.asked_message_cap, self.message_capped, MESSAGE_CAP)
        _span(self.queue_cap, self.asked_queue_cap, self.queue_capped, QUEUE_CAP)
        _span(self.platform_cap, self.asked_platform_cap, self.platform_capped, PLATFORM_CAP)


@dataclass(frozen=True, slots=True)
class Platform:
    """One registered platform and the credential id that signs its events."""

    schema: str
    name: str
    signer: str

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_RECORD")
        _name(self.name)
        _signer(self.signer)


@dataclass(frozen=True, slots=True)
class Receipt:
    """One applied message. A replay returns this object and does not copy it."""

    schema: str
    platform: str
    message_id: str
    message: str
    fence: int
    signature: str
    index: int
    prev: str
    sha: str

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_RECORD")
        _name(self.platform)
        _message_id(self.message_id)
        _body(self.message, MESSAGE_CAP)
        _fence(self.fence)
        _signature(self.signature)
        if type(self.index) is not int or self.index < 0 or self.index >= QUEUE_CAP:
            raise Refuse("BAD_RECORD")
        _hex(self.prev, "BAD_RECORD")
        _hex(self.sha, "BAD_RECORD")

    def __repr__(self) -> str:
        return (
            f"Receipt(platform={self.platform!r}, message_id={self.message_id!r}, "
            f"index={self.index})"
        )


@dataclass(frozen=True, slots=True)
class IngestResult:
    """The stored receipt plus the replay mark. ``replay`` is true only on a repeat."""

    schema: str
    receipt: Receipt
    replay: bool

    def __post_init__(self) -> None:
        if self.schema != SCHEMA or type(self.receipt) is not Receipt or type(self.replay) is not bool:
            raise Refuse("BAD_RECORD")

    def __repr__(self) -> str:
        return f"IngestResult(message_id={self.receipt.message_id!r}, replay={self.replay})"


@dataclass(frozen=True, slots=True)
class Delivery:
    """Outbound descriptor. Recording it does not send."""

    schema: str
    target: str
    message: str
    index: int

    def __post_init__(self) -> None:
        if self.schema != SCHEMA:
            raise Refuse("BAD_RECORD")
        _name(self.target)
        _body(self.message, MESSAGE_CAP)
        if type(self.index) is not int or self.index < 0 or self.index >= QUEUE_CAP:
            raise Refuse("BAD_RECORD")

    def __repr__(self) -> str:
        return f"Delivery(target={self.target!r}, index={self.index})"


@dataclass(frozen=True, slots=True)
class Shutdown:
    """Drain marker. The message ledger stays."""

    schema: str
    state: Literal["draining"]
    accepted: int


@dataclass(frozen=True, slots=True)
class Status:
    """Point-in-time counts. Not a watcher."""

    schema: str
    state: Literal["running", "draining"]
    platforms: tuple[str, ...]
    accepted: int
    deliveries: int


@dataclass(frozen=True, slots=True)
class Snapshot:
    """Public ledger. ``rebuild`` replays these records back to an equal value."""

    schema: str
    state: Literal["running", "draining"]
    policy: Policy
    platforms: tuple[Platform, ...]
    receipts: tuple[Receipt, ...]
    deliveries: tuple[Delivery, ...]
    accepted: int

    def __post_init__(self) -> None:
        _audit(self)


def _cap(asked: object, ceiling: int) -> tuple[int, int, bool]:
    if type(asked) is not int:
        raise Refuse("NOT_INT")
    if asked < 1:
        raise Refuse("OUT_OF_RANGE", f"1..{ceiling}")
    if asked > ceiling:
        return ceiling, asked, True
    return asked, asked, False


def _name(value: object) -> str:
    text = bound_text(value, _NAME_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    if _NAME_RE.fullmatch(text) is None:
        raise Refuse("BAD_NAME")
    return text


def _message_id(value: object) -> str:
    text = bound_text(value, _ID_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    if _ID_RE.fullmatch(text) is None:
        raise Refuse("BAD_ID")
    return text


def _signer(value: object) -> str:
    text = bound_text(value, _SIGNER_CAP)
    if text == "":
        raise Refuse("MISSING")
    if secret_shape(text):
        raise Refuse("SECRET")
    if _SIGNER_RE.fullmatch(text) is None:
        raise Refuse("BAD_NAME")
    return text


def _body(value: object, limit: int) -> str:
    text = bound_text(value, limit)
    if secret_shape(text):
        raise Refuse("SECRET")
    if text.strip() == "":
        raise Refuse("EMPTY_MESSAGE")
    return text


def _hex(value: object, code: str) -> str:
    if type(value) is not str or _HEX_RE.fullmatch(value) is None:
        raise Refuse(code)
    return value


def _signature(value: object) -> str:
    if type(value) is not str:
        raise Refuse("BAD_SIGNATURE")
    if "\x00" in value:
        raise Refuse("NULL_BYTE")
    if _HEX_RE.fullmatch(value) is None:
        raise Refuse("BAD_SIGNATURE")
    return value


def _fence(value: object) -> int:
    if type(value) is not int:
        raise Refuse("BAD_FENCE")
    if value < 0 or value > _NOW_MAX:
        raise Refuse("BAD_FENCE")
    return value


def _canon(platform: str, message_id: str, message: str, fence: int) -> bytes:
    parts = (platform, message_id, message, str(fence))
    return "\n".join(f"{len(part)}\n{part}" for part in parts).encode("utf-8")


def _digest(signer: str, platform: str, message_id: str, message: str, fence: int) -> str:
    payload = _canon(platform, message_id, message, fence)
    return hmac.new(signer.encode("utf-8"), payload, hashlib.sha256).hexdigest()


def _link(prev: str, platform: str, message_id: str, fence: int, signature: str) -> str:
    raw = f"{prev}\n{platform}\n{message_id}\n{fence}\n{signature}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _phase(draining: bool) -> Literal["running", "draining"]:
    if draining:
        return "draining"
    return "running"


def sign(
    signer: object,
    platform: object,
    message_id: object,
    message: object,
    fence: object,
) -> str:
    """HMAC-SHA256 hex of the canonical message, keyed by the credential id."""
    return _digest(
        _signer(signer),
        _name(platform),
        _message_id(message_id),
        _body(message, MESSAGE_CAP),
        _fence(fence),
    )


def _audit(snapshot: Snapshot) -> None:
    if snapshot.schema != SCHEMA or snapshot.state not in _STATES:
        raise Refuse("BAD_RECORD")
    if type(snapshot.policy) is not Policy:
        raise Refuse("BAD_RECORD")
    if (
        type(snapshot.platforms) is not tuple
        or type(snapshot.receipts) is not tuple
        or type(snapshot.deliveries) is not tuple
    ):
        raise Refuse("BAD_RECORD")
    if type(snapshot.accepted) is not int or snapshot.accepted != len(snapshot.receipts):
        raise Refuse("BAD_RECORD")
    if len(snapshot.platforms) > snapshot.policy.platform_cap:
        raise Refuse("PLATFORM_CAP", str(snapshot.policy.platform_cap))
    if len(snapshot.receipts) > snapshot.policy.queue_cap:
        raise Refuse("QUEUE_CAP", str(snapshot.policy.queue_cap))
    if len(snapshot.deliveries) > snapshot.policy.queue_cap:
        raise Refuse("DELIVERY_CAP", str(snapshot.policy.queue_cap))
    signers: dict[str, str] = {}
    for platform in snapshot.platforms:
        if type(platform) is not Platform:
            raise Refuse("BAD_RECORD")
        if platform.name in signers:
            raise Refuse("DUPLICATE")
        signers[platform.name] = platform.signer
    seen: set[str] = set()
    last_fence: dict[str, int] = {}
    prev = _GENESIS
    for index, receipt in enumerate(snapshot.receipts):
        if type(receipt) is not Receipt or receipt.index != index:
            raise Refuse("BAD_RECORD")
        if len(receipt.message) > snapshot.policy.message_cap:
            raise Refuse("OVERSIZE", str(snapshot.policy.message_cap))
        signer = signers.get(receipt.platform)
        if signer is None:
            raise Refuse("UNKNOWN_PLATFORM")
        if receipt.message_id in seen:
            raise Refuse("DUPLICATE")
        seen.add(receipt.message_id)
        expected = _digest(signer, receipt.platform, receipt.message_id, receipt.message, receipt.fence)
        if not const_eq(expected, receipt.signature):
            raise Refuse("BAD_SIGNATURE")
        link = _link(prev, receipt.platform, receipt.message_id, receipt.fence, receipt.signature)
        if not const_eq(receipt.prev, prev) or not const_eq(link, receipt.sha):
            raise Refuse("CHAIN")
        prior_fence = last_fence.get(receipt.platform)
        if prior_fence is not None and receipt.fence < prior_fence:
            raise Refuse("STALE", "order")
        last_fence[receipt.platform] = receipt.fence
        prev = receipt.sha
    for index, delivery in enumerate(snapshot.deliveries):
        if type(delivery) is not Delivery or delivery.index != index:
            raise Refuse("BAD_RECORD")
        if delivery.target not in signers:
            raise Refuse("UNKNOWN_PLATFORM")
        if len(delivery.message) > snapshot.policy.message_cap:
            raise Refuse("OVERSIZE", str(snapshot.policy.message_cap))


def rebuild(snapshot: object) -> Snapshot:
    """Replay a snapshot. A broken chain, stale fence, or duplicate id refuses."""
    if type(snapshot) is not Snapshot:
        raise Refuse("BAD_RECORD")
    _audit(snapshot)
    return snapshot


class Gateway:
    """In-memory registry, ingest ledger, and delivery ledger for one gateway."""

    __slots__ = (
        "_policy",
        "_platforms",
        "_by_name",
        "_messages",
        "_by_id",
        "_last_fence",
        "_deliveries",
        "_draining",
    )

    def __init__(
        self,
        *,
        message_cap: object = MESSAGE_CAP,
        queue_cap: object = QUEUE_CAP,
        platform_cap: object = PLATFORM_CAP,
    ) -> None:
        message_applied, message_asked, message_capped = _cap(message_cap, MESSAGE_CAP)
        queue_applied, queue_asked, queue_capped = _cap(queue_cap, QUEUE_CAP)
        platform_applied, platform_asked, platform_capped = _cap(platform_cap, PLATFORM_CAP)
        self._policy = Policy(
            message_cap=message_applied,
            queue_cap=queue_applied,
            platform_cap=platform_applied,
            asked_message_cap=message_asked,
            asked_queue_cap=queue_asked,
            asked_platform_cap=platform_asked,
            message_capped=message_capped,
            queue_capped=queue_capped,
            platform_capped=platform_capped,
        )
        self._platforms: list[Platform] = []
        self._by_name: dict[str, Platform] = {}
        self._messages: list[Receipt] = []
        self._by_id: dict[str, Receipt] = {}
        self._last_fence: dict[str, int] = {}
        self._deliveries: list[Delivery] = []
        self._draining = False

    def __repr__(self) -> str:
        state = "draining" if self._draining else "running"
        return (
            f"Gateway(state={state!r}, platforms={len(self._platforms)}, "
            f"accepted={len(self._messages)}, deliveries={len(self._deliveries)})"
        )

    @property
    def policy(self) -> Policy:
        return self._policy

    @property
    def draining(self) -> bool:
        return self._draining

    @property
    def platforms(self) -> tuple[str, ...]:
        return tuple(item.name for item in self._platforms)

    @property
    def messages(self) -> tuple[Receipt, ...]:
        return tuple(self._messages)

    @property
    def deliveries(self) -> tuple[Delivery, ...]:
        return tuple(self._deliveries)

    def register_platform(self, name: object, signer: object) -> Platform:
        """Register one platform. The same name and signer returns the existing row."""
        self._require_open()
        platform_name = _name(name)
        signer_id = _signer(signer)
        found = self._by_name.get(platform_name)
        if found is not None:
            if not const_eq(found.signer, signer_id):
                raise Refuse("MISMATCH")
            return found
        if len(self._platforms) >= self._policy.platform_cap:
            raise Refuse("PLATFORM_CAP", str(self._policy.platform_cap))
        item = Platform(schema=SCHEMA, name=platform_name, signer=signer_id)
        self._platforms.append(item)
        self._by_name[platform_name] = item
        return item

    def ingest(
        self,
        platform: object,
        message_id: object,
        message: object,
        signature: object,
        fence: object,
        now: object,
    ) -> IngestResult:
        """Apply one message. The same id returns that receipt and does not apply again.

        An exact retry still returns the stored receipt after the fence window has
        moved. A new id with a bad signature, a bad fence, or a stale fence refuses.
        """
        self._require_open()
        platform_name = _name(platform)
        identifier = _message_id(message_id)
        body = _body(message, self._policy.message_cap)
        digest = _signature(signature)
        now_i = bound_int(now, 0, _NOW_MAX)
        fence_i = _fence(fence)
        registered = self._by_name.get(platform_name)
        if registered is None:
            raise Refuse("UNKNOWN_PLATFORM")
        expected = _digest(registered.signer, platform_name, identifier, body, fence_i)
        if not const_eq(expected, digest):
            raise Refuse("BAD_SIGNATURE")
        prior = self._by_id.get(identifier)
        if prior is not None:
            if not const_eq(prior.message_id, identifier) or not const_eq(prior.signature, digest):
                raise Refuse("MISMATCH")
            return IngestResult(schema=SCHEMA, receipt=prior, replay=True)
        if fence_i < now_i - FENCE_WINDOW or fence_i > now_i + FENCE_WINDOW:
            raise Refuse("STALE", "window")
        last = self._last_fence.get(platform_name)
        if last is not None and fence_i < last:
            raise Refuse("STALE", "order")
        if len(self._messages) >= self._policy.queue_cap:
            raise Refuse("QUEUE_CAP", str(self._policy.queue_cap))
        prev = self._messages[-1].sha if self._messages else _GENESIS
        row = Receipt(
            schema=SCHEMA,
            platform=platform_name,
            message_id=identifier,
            message=body,
            fence=fence_i,
            signature=digest,
            index=len(self._messages),
            prev=prev,
            sha=_link(prev, platform_name, identifier, fence_i, digest),
        )
        self._messages.append(row)
        self._by_id[identifier] = row
        self._last_fence[platform_name] = fence_i
        return IngestResult(schema=SCHEMA, receipt=row, replay=False)

    def deliver(self, target: object, message: object) -> Delivery:
        """Record a descriptor for a registered target. The queue cap bounds the log."""
        target_name = _name(target)
        body = _body(message, self._policy.message_cap)
        if target_name not in self._by_name:
            raise Refuse("UNKNOWN_PLATFORM")
        if len(self._deliveries) >= self._policy.queue_cap:
            raise Refuse("DELIVERY_CAP", str(self._policy.queue_cap))
        row = Delivery(
            schema=SCHEMA,
            target=target_name,
            message=body,
            index=len(self._deliveries),
        )
        self._deliveries.append(row)
        return row

    def shutdown(self) -> Shutdown:
        """Mark this gateway draining. Later ingest and register refuse."""
        self._draining = True
        return Shutdown(schema=SCHEMA, state="draining", accepted=len(self._messages))

    def status(self) -> Status:
        """Return counts and registered names. This starts no watcher."""
        return Status(
            schema=SCHEMA,
            state=_phase(self._draining),
            platforms=self.platforms,
            accepted=len(self._messages),
            deliveries=len(self._deliveries),
        )

    def snapshot(self) -> Snapshot:
        """Freeze the public ledger. ``rebuild`` of this value matches it."""
        return Snapshot(
            schema=SCHEMA,
            state=_phase(self._draining),
            policy=self._policy,
            platforms=tuple(self._platforms),
            receipts=tuple(self._messages),
            deliveries=tuple(self._deliveries),
            accepted=len(self._messages),
        )

    def _require_open(self) -> None:
        if self._draining:
            raise Refuse("DRAINING")
