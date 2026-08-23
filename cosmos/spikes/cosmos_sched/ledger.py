"""Append-only hash-chained JSONL ledger. Authority for job lifecycle.

A torn/unparseable tail REFUSES. Never skip, never repair-in-place.
fsync after every append. Import has no filesystem side effect.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

from cosmos.spikes.cosmos_sched.absence import Absence, TypedResult
from cosmos.spikes.cosmos_sched.stamp import ArtifactStamp, WorkerIdentity, now_stamp


SCHEMA = "cosmos_sched.ledger.v1"
GENESIS = "0" * 64


@dataclass(frozen=True)
class LedgerEvent:
    event_id: str
    event_type: str
    prev_hash: str
    payload_sha256: str
    record_hash: str
    stamp: dict[str, Any]
    payload: dict[str, Any]
    schema_version: str = SCHEMA

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "event_id": self.event_id,
            "event_type": self.event_type,
            "prev_hash": self.prev_hash,
            "payload_sha256": self.payload_sha256,
            "record_hash": self.record_hash,
            "stamp": self.stamp,
            "payload": self.payload,
        }


def _canonical(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Ledger:
    def __init__(self, path: Path, identity: WorkerIdentity) -> None:
        self.path = path
        self.identity = identity
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.touch()

    def _tail_hash(self) -> TypedResult[str]:
        if not self.path.exists():
            return TypedResult(Absence.NOT_FOUND, f"ledger missing: {self.path}")
        try:
            text = self.path.read_text(encoding="utf-8")
        except OSError as exc:
            return TypedResult(Absence.UNREADABLE, f"ledger unreadable: {exc}")
        lines = [ln for ln in text.splitlines() if ln.strip()]
        if not lines:
            return TypedResult(Absence.EMPTY, "ledger empty", GENESIS)
        try:
            last = json.loads(lines[-1])
        except json.JSONDecodeError as exc:
            return TypedResult(Absence.UNPARSEABLE, f"torn ledger tail: {exc}")
        record_hash = last.get("record_hash")
        if not isinstance(record_hash, str) or len(record_hash) != 64:
            return TypedResult(Absence.UNPARSEABLE, "ledger tail missing record_hash")
        return TypedResult(Absence.FOUND, "tail", record_hash)

    def append(self, event_type: str, payload: dict[str, Any]) -> TypedResult[LedgerEvent]:
        tail = self._tail_hash()
        if tail.kind is Absence.UNPARSEABLE:
            return TypedResult(tail.kind, tail.detail)
        if tail.kind is Absence.UNREADABLE:
            return TypedResult(tail.kind, tail.detail)
        if tail.kind is Absence.NOT_FOUND:
            return TypedResult(tail.kind, tail.detail)
        prev = tail.value if tail.value is not None else GENESIS
        stamp: ArtifactStamp = now_stamp(self.identity)
        payload_hash = _sha256(_canonical(payload))
        event_id = _sha256(f"{stamp.epoch}:{event_type}:{payload_hash}".encode("utf-8"))
        body = {
            "schema_version": SCHEMA,
            "event_id": event_id,
            "event_type": event_type,
            "prev_hash": prev,
            "payload_sha256": payload_hash,
            "stamp": stamp.to_dict(),
            "payload": payload,
        }
        record_hash = _sha256(_canonical(body))
        body["record_hash"] = record_hash
        event = LedgerEvent(
            event_id=event_id,
            event_type=event_type,
            prev_hash=prev,
            payload_sha256=payload_hash,
            record_hash=record_hash,
            stamp=stamp.to_dict(),
            payload=payload,
        )
        line = json.dumps(body, sort_keys=True, separators=(",", ":")) + "\n"
        try:
            fd = os.open(str(self.path), os.O_APPEND | os.O_WRONLY | os.O_CREAT, 0o644)
            try:
                os.write(fd, line.encode("utf-8"))
                os.fsync(fd)
            finally:
                os.close(fd)
        except OSError as exc:
            return TypedResult(Absence.UNREADABLE, f"ledger append failed: {exc}")
        return TypedResult(Absence.FOUND, event_type, event)

    def iter_events(self) -> TypedResult[list[dict[str, Any]]]:
        if not self.path.exists():
            return TypedResult(Absence.NOT_FOUND, f"ledger missing: {self.path}")
        try:
            text = self.path.read_text(encoding="utf-8")
        except OSError as exc:
            return TypedResult(Absence.UNREADABLE, f"ledger unreadable: {exc}")
        events: list[dict[str, Any]] = []
        for index, raw in enumerate(text.splitlines(), start=1):
            if not raw.strip():
                continue
            try:
                events.append(json.loads(raw))
            except json.JSONDecodeError as exc:
                return TypedResult(Absence.UNPARSEABLE, f"torn ledger line {index}: {exc}")
        if not events:
            return TypedResult(Absence.EMPTY, "ledger empty", [])
        return TypedResult(Absence.FOUND, f"n={len(events)}", events)

    def types_for_job(self, job_id: str) -> TypedResult[list[str]]:
        scanned = self.iter_events()
        if scanned.kind is not Absence.FOUND or scanned.value is None:
            if scanned.kind is Absence.EMPTY:
                return TypedResult(Absence.NOT_IN_RECORD, f"no events for job {job_id}", [])
            return TypedResult(scanned.kind, scanned.detail)
        found = [
            ev["event_type"]
            for ev in scanned.value
            if ev.get("payload", {}).get("job_id") == job_id
        ]
        if not found:
            return TypedResult(Absence.NOT_IN_RECORD, f"job {job_id} not in ledger", [])
        return TypedResult(Absence.FOUND, job_id, found)

    def __iter__(self) -> Iterator[dict[str, Any]]:
        scanned = self.iter_events()
        if scanned.kind is Absence.FOUND and scanned.value is not None:
            yield from scanned.value
