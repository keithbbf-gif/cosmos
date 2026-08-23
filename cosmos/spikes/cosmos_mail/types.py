"""Typed absence, artifacts, and exit-code mapping for cosmos_mail.

NOT_FOUND is not EMPTY is not UNREADABLE is not STALE is not OUT_OF_CLOCK
is not NOT_IN_RECORD. Callers must match on AbsenceKind; None is not a
stand-in for any of these.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Generic, TypeVar

T = TypeVar("T")

SCHEMA_MESSAGE = "cosmos.mail.message.v1"
SCHEMA_IDENTITY = "cosmos.mail.identity.v1"
SCHEMA_HEARTBEAT = "cosmos.mail.heartbeat.v1"
SCHEMA_RECEIPT = "cosmos.mail.receipt.v1"
SCHEMA_PROBE = "cosmos.mail.probe.v1"


class AbsenceKind(str, Enum):
    FOUND = "FOUND"
    EMPTY = "EMPTY"
    NOT_FOUND = "NOT_FOUND"
    UNREADABLE = "UNREADABLE"
    UNPARSEABLE = "UNPARSEABLE"
    STALE = "STALE"
    OUT_OF_CLOCK = "OUT_OF_CLOCK"
    NOT_IN_RECORD = "NOT_IN_RECORD"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    HASH_MISMATCH = "HASH_MISMATCH"
    REFUSED = "REFUSED"
    COLLISION_REFUSED = "COLLISION_REFUSED"
    NATIVE_DEMO_REQUIRED = "NATIVE_DEMO_REQUIRED"


class ReceiptKind(str, Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"


# Machine-readable probe/CLI exits. 0 and 2 match incumbent runner/phone
# conventions (CLEAN / FINDINGS). 3 is the dead-phone signal: missing mailbox
# is never "no news".
EXIT_CLEAN = 0
EXIT_BROKE = 1
EXIT_FINDINGS = 2
EXIT_DEAD_PHONE = 3
EXIT_UNREADABLE = 4
EXIT_OUT_OF_CLOCK = 5
EXIT_NOT_IN_RECORD = 6
EXIT_IDENTITY = 7
EXIT_HASH = 8
EXIT_NATIVE_DEMO = 9

EXIT_BY_KIND: dict[AbsenceKind, int] = {
    AbsenceKind.FOUND: EXIT_CLEAN,
    AbsenceKind.EMPTY: EXIT_CLEAN,
    AbsenceKind.NOT_FOUND: EXIT_DEAD_PHONE,
    AbsenceKind.STALE: EXIT_FINDINGS,
    AbsenceKind.UNREADABLE: EXIT_UNREADABLE,
    AbsenceKind.UNPARSEABLE: EXIT_UNREADABLE,
    AbsenceKind.OUT_OF_CLOCK: EXIT_OUT_OF_CLOCK,
    AbsenceKind.NOT_IN_RECORD: EXIT_NOT_IN_RECORD,
    AbsenceKind.IDENTITY_MISMATCH: EXIT_IDENTITY,
    AbsenceKind.HASH_MISMATCH: EXIT_HASH,
    AbsenceKind.REFUSED: EXIT_BROKE,
    AbsenceKind.COLLISION_REFUSED: EXIT_BROKE,
    AbsenceKind.NATIVE_DEMO_REQUIRED: EXIT_NATIVE_DEMO,
}


def exit_code_for(kind: AbsenceKind) -> int:
    return EXIT_BY_KIND[kind]


def require_aware(instant: datetime) -> datetime:
    if instant.tzinfo is None:
        raise ValueError("naive timestamp refused: offset-aware clock is required")
    return instant


def format_aware(instant: datetime) -> str:
    return require_aware(instant).isoformat(timespec="microseconds")


def fs_safe_offset_timestamp(instant: datetime) -> str:
    """Windows-safe encoding of an offset-aware timestamp (no colon)."""
    aware = require_aware(instant)
    return (
        aware.strftime("%Y%m%dT%H%M%S")
        + f".{aware.microsecond:06d}"
        + aware.strftime("%z")
    )


def epoch_of(instant: datetime) -> float:
    return require_aware(instant).timestamp()


def utc_now_aware() -> datetime:
    return datetime.now(timezone.utc).astimezone()


@dataclass(frozen=True)
class Outcome(Generic[T]):
    kind: AbsenceKind
    value: T | None
    detail: str
    observed_at: str
    observed_epoch: float
    worker_id: str
    path: str | None = None

    def present(self) -> bool:
        return self.kind is AbsenceKind.FOUND

    def mailbox_exists(self) -> bool:
        """Mailbox surface is there. EMPTY is a live phone with no news."""
        return self.kind in (AbsenceKind.FOUND, AbsenceKind.EMPTY, AbsenceKind.STALE)


@dataclass(frozen=True)
class ArtifactStamp:
    worker_id: str
    instance_id: str
    observed_at: str
    observed_epoch: float
    tz_offset: str


@dataclass(frozen=True)
class Message:
    schema: str
    message_id: str
    sender_id: str
    sender_instance: str
    recipient_id: str
    created_at: str
    created_epoch: float
    tz_offset: str
    subject: str
    correlation_id: str
    payload: object
    payload_hash: str
    requires_ack: bool
    ack_deadline_epoch: float | None
    ttl_seconds: float | None

    def to_record(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "sender_instance": self.sender_instance,
            "recipient_id": self.recipient_id,
            "created_at": self.created_at,
            "created_epoch": self.created_epoch,
            "tz_offset": self.tz_offset,
            "subject": self.subject,
            "correlation_id": self.correlation_id,
            "payload": self.payload,
            "payload_hash": self.payload_hash,
            "requires_ack": self.requires_ack,
            "ack_deadline_epoch": self.ack_deadline_epoch,
            "ttl_seconds": self.ttl_seconds,
        }


@dataclass(frozen=True)
class Receipt:
    schema: str
    receipt_kind: ReceiptKind
    message_id: str
    worker_id: str
    instance_id: str
    observed_at: str
    observed_epoch: float
    tz_offset: str
    payload_hash: str

    def to_record(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "receipt_kind": self.receipt_kind.value,
            "message_id": self.message_id,
            "worker_id": self.worker_id,
            "instance_id": self.instance_id,
            "observed_at": self.observed_at,
            "observed_epoch": self.observed_epoch,
            "tz_offset": self.tz_offset,
            "payload_hash": self.payload_hash,
        }


@dataclass(frozen=True)
class InboxEntry:
    filename: str
    path: str
    parse: Outcome[Message]


@dataclass(frozen=True)
class ReceiveReport:
    messages: list[Message]
    defects: list[Outcome[None]]


@dataclass(frozen=True)
class ProbeFacets:
    root_sentinel: Outcome[None]
    identity: Outcome[dict[str, object]]
    heartbeat: Outcome[dict[str, object]]
    inbox: Outcome[None]
    unread_count: int
    oldest_unacked_required: Outcome[Message]
    last_read_receipt: Outcome[Receipt]
    defects: list[Outcome[None]] = field(default_factory=list)


@dataclass(frozen=True)
class ProbeReport:
    schema: str
    worker_id: str
    mailbox_state: AbsenceKind
    facets: ProbeFacets
    observed_at: str
    observed_epoch: float
    tz_offset: str
    probe_worker_id: str
    exit_code: int

    def to_record(self) -> dict[str, object]:
        def pack(outcome: Outcome[object]) -> dict[str, object]:
            record: dict[str, object] = {
                "kind": outcome.kind.value,
                "detail": outcome.detail,
                "observed_at": outcome.observed_at,
                "observed_epoch": outcome.observed_epoch,
                "worker_id": outcome.worker_id,
                "path": outcome.path,
            }
            if outcome.present() and outcome.value is not None:
                record["value"] = _jsonable(outcome.value)
            return record

        return {
            "schema": self.schema,
            "worker_id": self.worker_id,
            "mailbox_state": self.mailbox_state.value,
            "observed_at": self.observed_at,
            "observed_epoch": self.observed_epoch,
            "tz_offset": self.tz_offset,
            "probe_worker_id": self.probe_worker_id,
            "exit_code": self.exit_code,
            "facets": {
                "root_sentinel": pack(self.facets.root_sentinel),
                "identity": pack(self.facets.identity),
                "heartbeat": pack(self.facets.heartbeat),
                "inbox": pack(self.facets.inbox),
                "unread_count": self.facets.unread_count,
                "oldest_unacked_required": pack(self.facets.oldest_unacked_required),
                "last_read_receipt": pack(self.facets.last_read_receipt),
                "defects": [pack(item) for item in self.facets.defects],
            },
        }


def _jsonable(value: object) -> object:
    if isinstance(value, Message):
        return value.to_record()
    if isinstance(value, Receipt):
        return value.to_record()
    return value
