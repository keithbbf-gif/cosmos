"""Lease arbiter, fencing tokens, and fenced commit gateway.

The arbiter is the sole authority. Advisory file locks, sandbox lock
files, and client clocks do not grant, expire, or publish. Takeover is
LEASE_EXPIRED then LEASE_GRANTED — never a silent clear. A dying holder
is recovered by arbiter-clock expiry with zero cleanup calls.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from uuid import uuid4

from cosmos.spikes.cosmos_lock.absence import AbsenceKind, Outcome, RefusalCode
from cosmos.spikes.cosmos_lock.clock import ArbiterClock
from cosmos.spikes.cosmos_lock.identity import Stamp, WorkerIdentity
from cosmos.spikes.cosmos_lock.ingress import IngressEnvelope, read_envelope
from cosmos.spikes.cosmos_lock.ledger import Ledger, sha256_hex
from cosmos.spikes.cosmos_lock.platform import PlatformAdapter

DEFAULT_TTL_SECONDS = 90 * 60  # incumbent STALE_MINUTES
DEFAULT_MAX_SKEW_SECONDS = 5 * 60
ByteReader = Callable[[Path], Outcome[bytes]]


def filesystem_read(path: Path) -> Outcome[bytes]:
    try:
        return Outcome.found(path.read_bytes())
    except FileNotFoundError:
        return Outcome.absent(AbsenceKind.NOT_FOUND, reason=str(path))
    except OSError as exc:
        return Outcome.absent(AbsenceKind.UNREADABLE, reason=str(exc))


@dataclass(frozen=True)
class LeaseCapability:
    """In-process token possession. Lost on process death. Not a file."""

    lease_id: str
    resource_id: str
    fencing_token: int
    expires_at_epoch: float
    holder: WorkerIdentity


@dataclass(frozen=True)
class LeaseRecord:
    lease_id: str
    resource_id: str
    holder: WorkerIdentity
    fencing_token: int
    granted_at_epoch: float
    expires_at_epoch: float
    purpose: str
    fingerprints: dict[str, str]
    expected_inputs: dict[str, str]
    active: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "lease_id": self.lease_id,
            "resource_id": self.resource_id,
            "holder": self.holder.as_dict(),
            "fencing_token": self.fencing_token,
            "granted_at_epoch": self.granted_at_epoch,
            "expires_at_epoch": self.expires_at_epoch,
            "purpose": self.purpose,
            "fingerprints": self.fingerprints,
            "expected_inputs": self.expected_inputs,
            "active": self.active,
        }


@dataclass(frozen=True)
class FingerprintCheck:
    path: str
    state: str
    expected: str | None
    observed: str | None


@dataclass(frozen=True)
class CommitReceipt:
    event_id: str
    artifact_sha256: str
    cas_name: str
    fencing_token: int
    resource_id: str


@dataclass
class _Projection:
    current: dict[str, LeaseRecord] = field(default_factory=dict)
    last_token: dict[str, int] = field(default_factory=dict)
    by_lease_id: dict[str, LeaseRecord] = field(default_factory=dict)
    highest_token: int = 0


class Arbiter:
    """In-process COSMOS Core lock module. Explicitly instantiated."""

    def __init__(
        self,
        *,
        root: Path,
        clock: ArbiterClock,
        service_key: bytes,
        installation_id: str,
        adapter: PlatformAdapter,
        service_identity: WorkerIdentity,
        ttl_seconds: float = DEFAULT_TTL_SECONDS,
        max_skew_seconds: float = DEFAULT_MAX_SKEW_SECONDS,
        byte_reader: ByteReader = filesystem_read,
    ) -> None:
        self.root = root
        self.clock = clock
        self.adapter = adapter
        self.ttl_seconds = ttl_seconds
        self.max_skew_seconds = max_skew_seconds
        self.byte_reader = byte_reader
        self.service_identity = service_identity
        self.installation_id = installation_id
        self.ledger = Ledger(
            root / "ledger" / "events.jsonl",
            service_key=service_key,
            installation_id=installation_id,
            writer=service_identity,
        )
        self.ingress_dir = root / "ingress"
        self.cas_dir = root / "cas"
        self.mirror_dir = root / "mirrors"
        self._workers: dict[str, WorkerIdentity] = {}
        self._proj = _Projection()
        self.release_calls = 0

    @classmethod
    def instantiate(
        cls,
        *,
        root: Path,
        clock: ArbiterClock,
        service_key: bytes,
        installation_id: str,
        adapter: PlatformAdapter | None = None,
        ttl_seconds: float = DEFAULT_TTL_SECONDS,
        max_skew_seconds: float = DEFAULT_MAX_SKEW_SECONDS,
        byte_reader: ByteReader = filesystem_read,
        service_identity: WorkerIdentity | None = None,
    ) -> Outcome[Arbiter]:
        native = (adapter or PlatformAdapter()).native_authoritative_path(str(root))
        if not native.ok:
            return Outcome(
                native.kind,
                value=None,
                code=native.code,
                reason=native.reason,
                details=native.details,
            )
        service = service_identity or WorkerIdentity.mint("cosmos-core", lane="arbiter")
        arbiter = cls(
            root=root,
            clock=clock,
            service_key=service_key,
            installation_id=installation_id,
            adapter=adapter or PlatformAdapter(),
            service_identity=service,
            ttl_seconds=ttl_seconds,
            max_skew_seconds=max_skew_seconds,
            byte_reader=byte_reader,
        )
        root.mkdir(parents=True, exist_ok=True)
        arbiter.ingress_dir.mkdir(parents=True, exist_ok=True)
        arbiter.cas_dir.mkdir(parents=True, exist_ok=True)
        arbiter.mirror_dir.mkdir(parents=True, exist_ok=True)
        arbiter.ledger.path.parent.mkdir(parents=True, exist_ok=True)
        if arbiter.ledger.path.exists():
            loaded = arbiter.ledger.load()
            if not loaded.ok:
                return Outcome(
                    loaded.kind,
                    value=None,
                    code=loaded.code,
                    reason=loaded.reason,
                    details=loaded.details,
                )
            arbiter._rebuild()
        else:
            arbiter.ledger.path.touch()
            arbiter.ledger.load()
        return Outcome.found(arbiter)

    def register_worker(self, worker: WorkerIdentity) -> None:
        self._workers[worker.worker_id] = worker

    def stamp(self, worker: WorkerIdentity | None = None) -> Stamp:
        return Stamp.from_clock(
            worker or self.service_identity,
            self.clock,
            time_source=self.clock.source_name,
        )

    def probe_client_clock(self, client_epoch: float) -> Outcome[float]:
        arbiter_epoch = self.clock.epoch()
        skew = abs(client_epoch - arbiter_epoch)
        if skew > self.max_skew_seconds:
            return Outcome.absent(
                AbsenceKind.OUT_OF_CLOCK,
                code=RefusalCode.CLOCK_SKEW,
                reason=f"client clock skew {skew:.3f}s exceeds {self.max_skew_seconds}s",
                details={"client_epoch": client_epoch, "arbiter_epoch": arbiter_epoch},
            )
        return Outcome.found(arbiter_epoch)

    def inspect_lease(self, lease_id: str) -> Outcome[LeaseRecord]:
        record = self._proj.by_lease_id.get(lease_id)
        if record is None:
            return Outcome.absent(
                AbsenceKind.NOT_IN_RECORD,
                reason=f"lease_id {lease_id} was never granted",
            )
        return Outcome.found(record)

    def current_holder(self, resource_id: str) -> Outcome[LeaseRecord | None]:
        """FOUND(None) means no active holder. That is not NOT_FOUND."""
        if self._ledger_closed():
            return self._closed()
        record = self._proj.current.get(resource_id)
        if record is None or not record.active:
            return Outcome.found(None, reason="no active holder")
        if self.clock.epoch() >= record.expires_at_epoch:
            return Outcome.found(None, reason="holder expired on arbiter clock (not yet reaped)")
        return Outcome.found(record)

    def grant(
        self,
        worker: WorkerIdentity,
        resource_id: str,
        *,
        purpose: str = "protected-write",
        ttl_seconds: float | None = None,
        client_expires_at_epoch: float | None = None,
        watched: Mapping[str, Path] | None = None,
        expected_inputs: Mapping[str, str] | None = None,
    ) -> Outcome[LeaseCapability]:
        if self._ledger_closed():
            return self._closed()
        unknown = self._require_worker(worker)
        if unknown is not None:
            return unknown
        if client_expires_at_epoch is not None:
            # Arbiter clock is the only expiry source. The value is ignored.
            _ = client_expires_at_epoch
        self._reap_if_expired(resource_id)
        current = self._proj.current.get(resource_id)
        if current is not None and current.active:
            return Outcome.refused(
                RefusalCode.RESOURCE_HELD,
                reason=f"{resource_id} held by {current.holder.worker_id} token={current.fencing_token}",
                details={"holder": current.holder.as_dict(), "token": current.fencing_token},
            )
        fingerprints = self._snapshot_fingerprints(watched or {})
        if fingerprints.kind is AbsenceKind.UNREADABLE:
            return Outcome(
                AbsenceKind.UNREADABLE,
                value=None,
                code=fingerprints.code,
                reason=fingerprints.reason,
                details=fingerprints.details,
            )
        fps = fingerprints.value or {}
        ttl = self.ttl_seconds if ttl_seconds is None else ttl_seconds
        now = self.clock.epoch()
        token = self._proj.last_token.get(resource_id, 0) + 1
        record = LeaseRecord(
            lease_id=str(uuid4()),
            resource_id=resource_id,
            holder=worker,
            fencing_token=token,
            granted_at_epoch=now,
            expires_at_epoch=now + ttl,
            purpose=purpose,
            fingerprints=fps,
            expected_inputs=dict(expected_inputs or {}),
            active=True,
        )
        prior = None
        for event in reversed(self.ledger.events()):
            if (
                event.event_type == "LEASE_EXPIRED"
                and event.payload.get("resource_id") == resource_id
            ):
                prior = event.payload.get("lease_id")
                break
        appended = self.ledger.append(
            "LEASE_GRANTED",
            {
                **record.as_dict(),
                "supersedes_lease_id": prior,
                "takeover": prior is not None,
            },
            stamp=self.stamp(),
        )
        if not appended.ok:
            return Outcome(
                appended.kind,
                value=None,
                code=appended.code,
                reason=appended.reason,
                details=appended.details,
            )
        self._remember(record)
        self._write_mirror(record)
        return Outcome.found(
            LeaseCapability(
                lease_id=record.lease_id,
                resource_id=resource_id,
                fencing_token=token,
                expires_at_epoch=record.expires_at_epoch,
                holder=worker,
            )
        )

    def release(self, capability: LeaseCapability, worker: WorkerIdentity) -> Outcome[str]:
        if self._ledger_closed():
            return self._closed()
        unknown = self._require_worker(worker)
        if unknown is not None:
            return unknown
        current = self._proj.current.get(capability.resource_id)
        if current is None or not current.active:
            return Outcome.refused(
                RefusalCode.LEASE_NOT_ACTIVE,
                reason="no active lease to release",
            )
        if (
            current.lease_id != capability.lease_id
            or current.fencing_token != capability.fencing_token
            or current.holder.worker_id != worker.worker_id
        ):
            return Outcome.refused(
                RefusalCode.STALE_TOKEN,
                reason="release presented a token that is not current",
            )
        self.release_calls += 1
        released = current
        appended = self.ledger.append(
            "LEASE_RELEASED",
            {
                "lease_id": released.lease_id,
                "resource_id": released.resource_id,
                "fencing_token": released.fencing_token,
                "holder": worker.as_dict(),
            },
            stamp=self.stamp(),
        )
        if not appended.ok:
            return Outcome(
                appended.kind,
                value=None,
                code=appended.code,
                reason=appended.reason,
                details=appended.details,
            )
        self._deactivate(released)
        return Outcome.found(released.lease_id)

    def commit(
        self,
        *,
        worker: WorkerIdentity,
        resource_id: str,
        fencing_token: int,
        artifact_bytes: bytes,
        expected_inputs: Mapping[str, str] | None = None,
        via_ingress: bool = False,
    ) -> Outcome[CommitReceipt]:
        if via_ingress:
            return Outcome.refused(
                RefusalCode.INGRESS_CANNOT_COMMIT,
                reason=(
                    "sandbox ingress cannot publish; only the native fenced "
                    "commit gateway holding a current token may commit"
                ),
            )
        if self._ledger_closed():
            return self._closed()
        unknown = self._require_worker(worker)
        if unknown is not None:
            return unknown
        current = self._proj.current.get(resource_id)
        last = self._proj.last_token.get(resource_id, 0)
        expired_this_token = False
        if (
            current is not None
            and current.active
            and self.clock.epoch() >= current.expires_at_epoch
        ):
            expired_this_token = fencing_token == current.fencing_token
            self._reap_if_expired(resource_id)
            current = self._proj.current.get(resource_id)
        if last == 0:
            return Outcome.absent(
                AbsenceKind.NOT_IN_RECORD,
                reason="no fencing token has been granted for this resource",
            )
        if fencing_token < last:
            return self._ledger_refuse_commit(
                worker,
                resource_id,
                fencing_token,
                RefusalCode.STALE_TOKEN,
                "fencing token is lower than the most recently granted token",
            )
        if fencing_token > last:
            return Outcome.absent(
                AbsenceKind.NOT_IN_RECORD,
                reason=f"fencing token {fencing_token} was never granted",
            )
        if expired_this_token:
            return self._ledger_refuse_commit(
                worker,
                resource_id,
                fencing_token,
                RefusalCode.EXPIRED_HOLDER,
                "lease expired on the arbiter clock; holder cannot publish",
            )
        if current is None or not current.active:
            return self._ledger_refuse_commit(
                worker,
                resource_id,
                fencing_token,
                RefusalCode.LEASE_NOT_ACTIVE,
                "lease is not active; token cannot publish",
            )
        if current.holder.worker_id != worker.worker_id:
            return self._ledger_refuse_commit(
                worker,
                resource_id,
                fencing_token,
                RefusalCode.STALE_TOKEN,
                "token holder is not this worker",
            )
        expected = dict(expected_inputs) if expected_inputs is not None else current.expected_inputs
        if current.expected_inputs and expected != current.expected_inputs:
            return self._ledger_refuse_commit(
                worker,
                resource_id,
                fencing_token,
                RefusalCode.INPUT_HASH_MISMATCH,
                "expected input hashes do not match the hashes recorded at grant",
                extra={"expected": current.expected_inputs, "presented": expected},
            )
        digest = sha256_hex(artifact_bytes)
        cas_path = self.cas_dir / digest
        try:
            if not cas_path.exists():
                cas_path.write_bytes(artifact_bytes)
        except OSError as exc:
            return Outcome.absent(AbsenceKind.UNREADABLE, reason=str(exc))
        appended = self.ledger.append(
            "COMMIT_ACCEPTED",
            {
                "resource_id": resource_id,
                "lease_id": current.lease_id,
                "fencing_token": fencing_token,
                "holder": worker.as_dict(),
                "artifact_sha256": digest,
                "cas_name": digest,
            },
            stamp=self.stamp(),
        )
        if not appended.ok:
            return Outcome(
                appended.kind,
                value=None,
                code=appended.code,
                reason=appended.reason,
                details=appended.details,
            )
        receipt = CommitReceipt(
            event_id=appended.unwrap().event_id,
            artifact_sha256=digest,
            cas_name=digest,
            fencing_token=fencing_token,
            resource_id=resource_id,
        )
        return Outcome.found(receipt)

    def ingest_ingress(self, path: Path) -> Outcome[IngressEnvelope]:
        if self._ledger_closed():
            return self._closed()
        loaded = read_envelope(path)
        if not loaded.ok:
            return loaded
        envelope = loaded.unwrap()
        unknown = self._require_worker(envelope.sender)
        if unknown is not None:
            return unknown
        appended = self.ledger.append(
            "INGRESS_ACCEPTED",
            {
                "envelope_id": envelope.envelope_id,
                "sender": envelope.sender.as_dict(),
                "payload_sha256": envelope.payload_sha256,
                "declared_len": envelope.declared_len,
                "cannot_commit": True,
            },
            stamp=self.stamp(),
        )
        if not appended.ok:
            return Outcome(
                appended.kind,
                value=None,
                code=appended.code,
                reason=appended.reason,
                details=appended.details,
            )
        return Outcome.found(envelope)

    def commit_from_ingress(
        self,
        envelope: IngressEnvelope,
        *,
        resource_id: str,
        fencing_token: int,
        artifact_bytes: bytes,
    ) -> Outcome[CommitReceipt]:
        return self.commit(
            worker=envelope.sender,
            resource_id=resource_id,
            fencing_token=fencing_token,
            artifact_bytes=artifact_bytes,
            via_ingress=True,
        )

    def read_lease_mirror(self, path: Path) -> Outcome[dict[str, Any]]:
        """Diagnostic only. Missing is NOT_FOUND, never FREE. Torn REFUSES."""
        if not path.exists():
            return Outcome.absent(
                AbsenceKind.NOT_FOUND,
                reason=f"lease mirror missing: {path} (not free; ask the arbiter)",
            )
        try:
            raw = path.read_bytes()
        except OSError as exc:
            return Outcome.absent(AbsenceKind.UNREADABLE, reason=str(exc))
        try:
            obj = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            return Outcome.absent(
                AbsenceKind.UNPARSEABLE,
                code=RefusalCode.TORN_STATE,
                reason=f"torn lease file refuses rather than reading as free: {exc}",
            )
        if not isinstance(obj, dict) or "lease_id" not in obj or "fencing_token" not in obj:
            return Outcome.absent(
                AbsenceKind.UNPARSEABLE,
                code=RefusalCode.TORN_STATE,
                reason="lease mirror JSON is not a lease record",
            )
        return Outcome.found(obj, reason="diagnostic mirror; not authority")

    def verify(self, resource_id: str, watched: Mapping[str, Path]) -> Outcome[list[FingerprintCheck]]:
        current = self._proj.current.get(resource_id)
        if current is None:
            return Outcome.absent(
                AbsenceKind.NOT_IN_RECORD,
                reason=f"no lease record for {resource_id}",
            )
        checks: list[FingerprintCheck] = []
        for name, path in watched.items():
            expected = current.fingerprints.get(name)
            read = self.byte_reader(path)
            if read.kind is AbsenceKind.NOT_FOUND:
                checks.append(FingerprintCheck(name, "NOT_FOUND", expected, None))
                continue
            if read.kind is AbsenceKind.UNREADABLE:
                checks.append(FingerprintCheck(name, "UNREADABLE", expected, None))
                continue
            if not read.ok:
                return Outcome(
                    read.kind,
                    value=None,
                    code=read.code,
                    reason=read.reason,
                    details=read.details,
                )
            observed = sha256_hex(read.unwrap())
            if expected is None:
                checks.append(FingerprintCheck(name, "NOT_IN_RECORD", None, observed))
            elif observed == expected:
                checks.append(FingerprintCheck(name, "UNCHANGED", expected, observed))
            else:
                checks.append(FingerprintCheck(name, "CHANGED", expected, observed))
        return Outcome.found(checks)

    def takeover_chain(self, resource_id: str) -> list[str]:
        return self.ledger.chain_for(
            resource_id,
            types=("LEASE_EXPIRED", "LEASE_GRANTED", "LEASE_RELEASED"),
        )

    def _require_worker(self, worker: WorkerIdentity) -> Outcome[Any] | None:
        known = self._workers.get(worker.worker_id)
        if known is None:
            return Outcome.refused(
                RefusalCode.UNKNOWN_WORKER,
                reason=f"worker {worker.worker_id!r} is not registered",
            )
        if known.instance_id != worker.instance_id:
            return Outcome.absent(
                AbsenceKind.IDENTITY_MISMATCH,
                code=RefusalCode.UNKNOWN_WORKER,
                reason="worker instance_id does not match the registered identity",
            )
        return None

    def _snapshot_fingerprints(self, watched: Mapping[str, Path]) -> Outcome[dict[str, str]]:
        out: dict[str, str] = {}
        for name, path in watched.items():
            read = self.byte_reader(path)
            if read.kind is AbsenceKind.NOT_FOUND:
                continue
            if not read.ok:
                return Outcome(
                    read.kind,
                    value=None,
                    code=read.code,
                    reason=read.reason,
                    details=read.details,
                )
            out[name] = sha256_hex(read.unwrap())
        return Outcome.found(out)

    def _reap_if_expired(self, resource_id: str) -> None:
        current = self._proj.current.get(resource_id)
        if current is None or not current.active:
            return
        if self.clock.epoch() < current.expires_at_epoch:
            return
        self.ledger.append(
            "LEASE_EXPIRED",
            {
                "lease_id": current.lease_id,
                "resource_id": current.resource_id,
                "fencing_token": current.fencing_token,
                "holder": current.holder.as_dict(),
                "reason": "ARBITER_CLOCK",
                "cleanup_calls": 0,
            },
            stamp=self.stamp(),
        )
        self._deactivate(current)

    def _ledger_refuse_commit(
        self,
        worker: WorkerIdentity,
        resource_id: str,
        fencing_token: int,
        code: RefusalCode,
        reason: str,
        extra: dict[str, Any] | None = None,
    ) -> Outcome[CommitReceipt]:
        payload = {
            "resource_id": resource_id,
            "fencing_token": fencing_token,
            "holder": worker.as_dict(),
            "code": code.value,
            "reason": reason,
        }
        if extra:
            payload["extra"] = extra
        self.ledger.append("COMMIT_REFUSED", payload, stamp=self.stamp())
        return Outcome.refused(code, reason=reason, details=payload)

    def _deactivate(self, record: LeaseRecord) -> None:
        self._remember(
            LeaseRecord(
                lease_id=record.lease_id,
                resource_id=record.resource_id,
                holder=record.holder,
                fencing_token=record.fencing_token,
                granted_at_epoch=record.granted_at_epoch,
                expires_at_epoch=record.expires_at_epoch,
                purpose=record.purpose,
                fingerprints=record.fingerprints,
                expected_inputs=record.expected_inputs,
                active=False,
            )
        )

    def _remember(self, record: LeaseRecord) -> None:
        self._proj.by_lease_id[record.lease_id] = record
        self._proj.last_token[record.resource_id] = max(
            self._proj.last_token.get(record.resource_id, 0), record.fencing_token
        )
        self._proj.highest_token = max(self._proj.highest_token, record.fencing_token)
        if record.active:
            self._proj.current[record.resource_id] = record
        else:
            self._proj.current[record.resource_id] = record

    def _write_mirror(self, record: LeaseRecord) -> None:
        path = self.mirror_dir / f"{record.resource_id}.lease.json"
        try:
            path.write_bytes(
                json.dumps(record.as_dict(), sort_keys=True, indent=2).encode("utf-8") + b"\n"
            )
        except OSError:
            # Mirror is diagnostic. A write failure does not roll back the lease.
            return

    def _rebuild(self) -> None:
        self._proj = _Projection()
        registered: dict[str, WorkerIdentity] = {}
        for event in self.ledger.events():
            payload = event.payload
            if event.event_type == "LEASE_GRANTED":
                holder_d = payload["holder"]
                holder = WorkerIdentity(
                    worker_id=holder_d["worker_id"],
                    instance_id=holder_d["instance_id"],
                    lane=holder_d["lane"],
                    attempt_id=holder_d.get("attempt_id"),
                )
                registered[holder.worker_id] = holder
                record = LeaseRecord(
                    lease_id=payload["lease_id"],
                    resource_id=payload["resource_id"],
                    holder=holder,
                    fencing_token=int(payload["fencing_token"]),
                    granted_at_epoch=float(payload["granted_at_epoch"]),
                    expires_at_epoch=float(payload["expires_at_epoch"]),
                    purpose=payload.get("purpose", ""),
                    fingerprints=dict(payload.get("fingerprints") or {}),
                    expected_inputs=dict(payload.get("expected_inputs") or {}),
                    active=True,
                )
                self._remember(record)
            elif event.event_type in {"LEASE_EXPIRED", "LEASE_RELEASED"}:
                current = self._proj.current.get(payload["resource_id"])
                if current is not None:
                    self._deactivate(current)
        self._workers.update(registered)

    def _ledger_closed(self) -> bool:
        integrity = self.ledger.integrity
        return integrity is not None and not integrity.ok

    def _closed(self) -> Outcome[Any]:
        integrity = self.ledger.integrity
        assert integrity is not None
        return Outcome(
            integrity.kind,
            value=None,
            code=integrity.code or RefusalCode.LEDGER_INTEGRITY.value,
            reason=f"torn or corrupt ledger refuses: {integrity.reason}",
            details=integrity.details,
        )
