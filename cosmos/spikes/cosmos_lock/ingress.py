"""Sandbox ingress envelopes.

A mount-visible write is not a hold and not a commit. The native service
reads the envelope, checks declared bytes against consumed bytes, verifies
hash, schema, and sender, and ledgers INGRESS_ACCEPTED. Only then is the
content known. The envelope still cannot publish — publication is a
fenced native commit presenting a fencing token.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from cosmos.spikes.cosmos_lock.absence import AbsenceKind, Outcome, RefusalCode
from cosmos.spikes.cosmos_lock.identity import Stamp, WorkerIdentity
from cosmos.spikes.cosmos_lock.ledger import sha256_hex

ENVELOPE_SCHEMA = 1


@dataclass(frozen=True)
class IngressEnvelope:
    envelope_id: str
    schema_version: int
    sender: WorkerIdentity
    stamp: Stamp
    declared_len: int
    payload_sha256: str
    payload: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "envelope_id": self.envelope_id,
            "schema_version": self.schema_version,
            "sender": self.sender.as_dict(),
            "stamp": self.stamp.as_dict(),
            "declared_len": self.declared_len,
            "payload_sha256": self.payload_sha256,
            "payload": self.payload,
        }

    @staticmethod
    def build(
        sender: WorkerIdentity,
        stamp: Stamp,
        payload: dict[str, Any],
    ) -> IngressEnvelope:
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return IngressEnvelope(
            envelope_id=str(uuid4()),
            schema_version=ENVELOPE_SCHEMA,
            sender=sender,
            stamp=stamp,
            declared_len=len(raw),
            payload_sha256=sha256_hex(raw),
            payload=payload,
        )


def write_envelope(directory: Path, envelope: IngressEnvelope) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{envelope.envelope_id}.ingress.json"
    path.write_bytes(
        json.dumps(envelope.as_dict(), sort_keys=True, indent=2).encode("utf-8") + b"\n"
    )
    return path


def read_envelope(path: Path) -> Outcome[IngressEnvelope]:
    if not path.exists():
        return Outcome.absent(AbsenceKind.NOT_FOUND, reason=str(path))
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
            reason=f"torn ingress envelope: {exc}",
        )
    try:
        payload = obj["payload"]
        payload_raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        if int(obj["declared_len"]) != len(payload_raw):
            return Outcome.refused(
                RefusalCode.LEDGER_INTEGRITY,
                reason="ingress declared_len does not match consumed bytes",
            )
        if obj["payload_sha256"] != sha256_hex(payload_raw):
            return Outcome.refused(
                RefusalCode.LEDGER_INTEGRITY,
                reason="ingress payload hash mismatch",
            )
        if int(obj["schema_version"]) != ENVELOPE_SCHEMA:
            return Outcome.refused(
                RefusalCode.LEDGER_INTEGRITY,
                reason=f"unsupported ingress schema {obj['schema_version']}",
            )
        sender_d = obj["sender"]
        stamp_d = obj["stamp"]
        sender = WorkerIdentity(
            worker_id=sender_d["worker_id"],
            instance_id=sender_d["instance_id"],
            lane=sender_d["lane"],
            attempt_id=sender_d.get("attempt_id"),
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
        envelope = IngressEnvelope(
            envelope_id=obj["envelope_id"],
            schema_version=int(obj["schema_version"]),
            sender=sender,
            stamp=stamp,
            declared_len=int(obj["declared_len"]),
            payload_sha256=obj["payload_sha256"],
            payload=payload,
        )
    except (KeyError, TypeError, ValueError) as exc:
        return Outcome.absent(
            AbsenceKind.UNPARSEABLE,
            code=RefusalCode.TORN_STATE,
            reason=f"incomplete ingress envelope: {exc}",
        )
    return Outcome.found(envelope)
