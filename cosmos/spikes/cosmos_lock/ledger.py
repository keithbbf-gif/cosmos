"""Append-only, hash-chained, HMAC-authenticated JSONL ledger.

Authority for leases and commits lives here. A torn, hash-mismatched, or
HMAC-invalid record is UNPARSEABLE / LEDGER_INTEGRITY — never skipped,
never repaired in place, never read as free.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from cosmos.spikes.cosmos_lock.absence import AbsenceKind, Outcome, RefusalCode
from cosmos.spikes.cosmos_lock.identity import Stamp, WorkerIdentity

SCHEMA_VERSION = 1
ZERO_HASH = "0" * 64


def _canonical(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class LedgerEvent:
    schema_version: int
    event_id: str
    event_type: str
    installation_id: str
    prev_hash: str
    payload_len: int
    payload_sha256: str
    record_hash: str
    hmac_hex: str
    writer: WorkerIdentity
    stamp: Stamp
    payload: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "event_id": self.event_id,
            "event_type": self.event_type,
            "installation_id": self.installation_id,
            "prev_hash": self.prev_hash,
            "payload_len": self.payload_len,
            "payload_sha256": self.payload_sha256,
            "record_hash": self.record_hash,
            "hmac": self.hmac_hex,
            "writer": self.writer.as_dict(),
            "stamp": self.stamp.as_dict(),
            "payload": self.payload,
        }


class Ledger:
    """Single-writer JSONL store. Instantiate with an explicit path."""

    def __init__(
        self,
        path: Path,
        *,
        service_key: bytes,
        installation_id: str,
        writer: WorkerIdentity,
    ) -> None:
        self.path = path
        self.service_key = service_key
        self.installation_id = installation_id
        self.writer = writer
        self._events: list[LedgerEvent] = []
        self._by_id: dict[str, LedgerEvent] = {}
        self._head_hash = ZERO_HASH
        self._integrity: Outcome[str] | None = None

    @property
    def head_hash(self) -> str:
        return self._head_hash

    @property
    def integrity(self) -> Outcome[str] | None:
        return self._integrity

    def events(self) -> tuple[LedgerEvent, ...]:
        return tuple(self._events)

    def event_types(self) -> list[str]:
        return [event.event_type for event in self._events]

    def get(self, event_id: str) -> Outcome[LedgerEvent]:
        found = self._by_id.get(event_id)
        if found is None:
            return Outcome.absent(
                AbsenceKind.NOT_IN_RECORD,
                reason=f"event_id {event_id} is not in the ledger",
            )
        return Outcome.found(found)

    def of_type(self, event_type: str) -> list[LedgerEvent]:
        return [event for event in self._events if event.event_type == event_type]

    def append(
        self,
        event_type: str,
        payload: dict[str, Any],
        *,
        stamp: Stamp,
    ) -> Outcome[LedgerEvent]:
        if self._integrity is not None and not self._integrity.ok:
            return Outcome(
                self._integrity.kind,
                value=None,
                code=self._integrity.code,
                reason=f"ledger refuses append: {self._integrity.reason}",
                details=self._integrity.details,
            )
        payload_bytes = _canonical(payload)
        body = {
            "schema_version": SCHEMA_VERSION,
            "event_id": str(uuid4()),
            "event_type": event_type,
            "installation_id": self.installation_id,
            "prev_hash": self._head_hash,
            "payload_len": len(payload_bytes),
            "payload_sha256": sha256_hex(payload_bytes),
            "writer": self.writer.as_dict(),
            "stamp": stamp.as_dict(),
            "payload": payload,
        }
        record_hash = sha256_hex(_canonical(body))
        mac = hmac.new(self.service_key, record_hash.encode("ascii"), hashlib.sha256).hexdigest()
        event = LedgerEvent(
            schema_version=SCHEMA_VERSION,
            event_id=str(body["event_id"]),
            event_type=event_type,
            installation_id=self.installation_id,
            prev_hash=self._head_hash,
            payload_len=int(body["payload_len"]) if isinstance(body["payload_len"], int) else int(str(body["payload_len"])),
            payload_sha256=str(body["payload_sha256"]),
            record_hash=record_hash,
            hmac_hex=mac,
            writer=self.writer,
            stamp=stamp,
            payload=payload,
        )
        line = _canonical(event.as_dict()) + b"\n"
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("ab") as handle:
                handle.write(line)
                handle.flush()
                try:
                    import os

                    os.fsync(handle.fileno())
                except OSError:
                    pass
        except OSError as exc:
            return Outcome.absent(AbsenceKind.UNREADABLE, reason=str(exc))
        self._events.append(event)
        self._by_id[event.event_id] = event
        self._head_hash = record_hash
        return Outcome.found(event)

    def load(self) -> Outcome[int]:
        """Replay the file. Torn / bad chain / bad HMAC → refuse, keep nothing as authority."""
        self._events.clear()
        self._by_id.clear()
        self._head_hash = ZERO_HASH
        self._integrity = None
        if not self.path.exists():
            return Outcome.absent(
                AbsenceKind.NOT_FOUND,
                reason=f"ledger file missing: {self.path}",
            )
        try:
            raw = self.path.read_bytes()
        except OSError as exc:
            self._integrity = Outcome.absent(AbsenceKind.UNREADABLE, reason=str(exc))
            return self._integrity  # type: ignore[return-value]

        if raw == b"":
            self._integrity = Outcome.found("empty")
            return Outcome.found(0)

        if not raw.endswith(b"\n"):
            self._integrity = Outcome.absent(
                AbsenceKind.UNPARSEABLE,
                code=RefusalCode.TORN_STATE,
                reason="ledger ends without a newline (torn final record)",
            )
            return self._integrity  # type: ignore[return-value]

        expected_prev = ZERO_HASH
        count = 0
        for index, line in enumerate(raw.splitlines()):
            parsed = self._parse_line(line, expected_prev=expected_prev, index=index)
            if not parsed.ok:
                self._events.clear()
                self._by_id.clear()
                self._head_hash = ZERO_HASH
                self._integrity = Outcome(
                    parsed.kind,
                    value=None,
                    code=parsed.code,
                    reason=parsed.reason,
                    details=parsed.details,
                )
                return self._integrity  # type: ignore[return-value]
            event = parsed.unwrap()
            self._events.append(event)
            self._by_id[event.event_id] = event
            expected_prev = event.record_hash
            count += 1
        self._head_hash = expected_prev
        self._integrity = Outcome.found("ok")
        return Outcome.found(count)

    def _parse_line(
        self,
        line: bytes,
        *,
        expected_prev: str,
        index: int,
    ) -> Outcome[LedgerEvent]:
        try:
            text = line.decode("utf-8")
            obj = json.loads(text)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            return Outcome.absent(
                AbsenceKind.UNPARSEABLE,
                code=RefusalCode.TORN_STATE,
                reason=f"torn ledger line {index}: {exc}",
            )
        if not isinstance(obj, dict):
            return Outcome.absent(
                AbsenceKind.UNPARSEABLE,
                code=RefusalCode.TORN_STATE,
                reason=f"ledger line {index} is not an object",
            )
        try:
            payload = obj["payload"]
            payload_bytes = _canonical(payload)
            if int(obj["payload_len"]) != len(payload_bytes):
                return Outcome.refused(
                    RefusalCode.LEDGER_INTEGRITY,
                    reason=f"payload_len mismatch at line {index}",
                )
            if obj["payload_sha256"] != sha256_hex(payload_bytes):
                return Outcome.refused(
                    RefusalCode.LEDGER_INTEGRITY,
                    reason=f"payload_sha256 mismatch at line {index}",
                )
            if obj["prev_hash"] != expected_prev:
                return Outcome.refused(
                    RefusalCode.LEDGER_INTEGRITY,
                    reason=f"chain break at line {index}",
                )
            writer_d = obj["writer"]
            stamp_d = obj["stamp"]
            writer = WorkerIdentity(
                worker_id=writer_d["worker_id"],
                instance_id=writer_d["instance_id"],
                lane=writer_d["lane"],
                attempt_id=writer_d.get("attempt_id"),
            )
            stamp = Stamp(
                worker=WorkerIdentity(
                    worker_id=stamp_d["worker"]["worker_id"],
                    instance_id=stamp_d["worker"]["instance_id"],
                    lane=stamp_d["worker"]["lane"],
                    attempt_id=stamp_d["worker"].get("attempt_id"),
                ),
                aware_iso=stamp_d["aware_iso"],
                epoch_seconds=float(stamp_d["epoch_seconds"]),
                tz_offset=stamp_d["tz_offset"],
                time_source=stamp_d["time_source"],
            )
            body = {
                "schema_version": obj["schema_version"],
                "event_id": obj["event_id"],
                "event_type": obj["event_type"],
                "installation_id": obj["installation_id"],
                "prev_hash": obj["prev_hash"],
                "payload_len": obj["payload_len"],
                "payload_sha256": obj["payload_sha256"],
                "writer": obj["writer"],
                "stamp": obj["stamp"],
                "payload": obj["payload"],
            }
            record_hash = sha256_hex(_canonical(body))
            if record_hash != obj["record_hash"]:
                return Outcome.refused(
                    RefusalCode.LEDGER_INTEGRITY,
                    reason=f"record_hash mismatch at line {index}",
                )
            expected_mac = hmac.new(
                self.service_key, record_hash.encode("ascii"), hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(expected_mac, obj["hmac"]):
                return Outcome.refused(
                    RefusalCode.LEDGER_INTEGRITY,
                    reason=f"HMAC mismatch at line {index}",
                )
            event = LedgerEvent(
                schema_version=int(obj["schema_version"]),
                event_id=obj["event_id"],
                event_type=obj["event_type"],
                installation_id=obj["installation_id"],
                prev_hash=obj["prev_hash"],
                payload_len=int(obj["payload_len"]),
                payload_sha256=obj["payload_sha256"],
                record_hash=record_hash,
                hmac_hex=obj["hmac"],
                writer=writer,
                stamp=stamp,
                payload=payload,
            )
        except (KeyError, TypeError, ValueError) as exc:
            return Outcome.absent(
                AbsenceKind.UNPARSEABLE,
                code=RefusalCode.TORN_STATE,
                reason=f"incomplete ledger record at line {index}: {exc}",
            )
        return Outcome.found(event)

    def chain_for(self, resource_id: str, types: Iterable[str] | None = None) -> list[str]:
        wanted = set(types) if types is not None else None
        out: list[str] = []
        for event in self._events:
            if event.payload.get("resource_id") != resource_id:
                continue
            if wanted is not None and event.event_type not in wanted:
                continue
            out.append(event.event_type)
        return out
