"""Per-worker mailbox exchange: immutable messages, typed probe, split receipts.

Layout (explicit root, never walked from __file__):

    <root>/.cosmos_mail_root          sentinel content, not mere existence
    <root>/workers/<id>/identity.json
    <root>/workers/<id>/heartbeat.json
    <root>/workers/<id>/inbox/<message_id>.json
    <root>/workers/<id>/outbox/<message_id>.json
    <root>/messages/<message_id>.json
    <root>/receipts/<message_id>/{sent,delivered,read}-<worker>.json

Send succeeds only after read-back of the immutable bytes. Delivered and read
are separate recorded facts. A missing mailbox is a dead phone (NON-ZERO),
never "no news".
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from cosmos.spikes.cosmos_mail.clock import Clock, SystemClock
from cosmos.spikes.cosmos_mail.platform import PlatformAdapter, detect_platform_adapter
from cosmos.spikes.cosmos_mail.types import (
    SCHEMA_HEARTBEAT,
    SCHEMA_IDENTITY,
    SCHEMA_MESSAGE,
    SCHEMA_PROBE,
    SCHEMA_RECEIPT,
    AbsenceKind,
    InboxEntry,
    Message,
    Outcome,
    ProbeFacets,
    ProbeReport,
    Receipt,
    ReceiptKind,
    ReceiveReport,
    epoch_of,
    exit_code_for,
    format_aware,
    fs_safe_offset_timestamp,
    require_aware,
)

SPIKE_WORKER_ID = "cursor.cosmos_mail"
SPIKE_INSTANCE_ID = "bc-c18bfff9-6c25-43a4-b6fa-8e11af6caa32"
SENTINEL_NAME = ".cosmos_mail_root"
SENTINEL_BODY = "COSMOS_MAIL_ROOT\nv1\nidentity=exchange\n"
WORKER_ID_RE = re.compile(r"^[a-z][a-z0-9._-]{0,62}$")
REQUIRED_MESSAGE_FIELDS = (
    "schema",
    "message_id",
    "sender_id",
    "sender_instance",
    "recipient_id",
    "created_at",
    "created_epoch",
    "tz_offset",
    "payload",
    "payload_hash",
    "requires_ack",
)


@dataclass(frozen=True)
class StalenessPolicy:
    """Age threshold plus unanswered required-ack. Both can mark STALE."""

    heartbeat_stale_after_s: float = 86400.0
    clock_skew_future_s: float = 5.0


@dataclass(frozen=True)
class WorkerIdentity:
    worker_id: str
    instance_id: str


def canonical_payload_bytes(payload: object) -> bytes:
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def payload_hash(payload: object) -> str:
    return hashlib.sha256(canonical_payload_bytes(payload)).hexdigest()


def dump_json(record: dict[str, Any]) -> bytes:
    return (
        json.dumps(record, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def _validate_worker_id(worker_id: str) -> AbsenceKind | None:
    if not WORKER_ID_RE.match(worker_id):
        return AbsenceKind.REFUSED
    return None


class MailExchange:
    """Explicitly instantiated mailbox surface. Import does not construct one."""

    def __init__(
        self,
        root: Path,
        *,
        adapter: PlatformAdapter | None = None,
        clock: Clock | None = None,
        policy: StalenessPolicy | None = None,
        probe_worker_id: str = SPIKE_WORKER_ID,
        probe_instance_id: str = SPIKE_INSTANCE_ID,
    ) -> None:
        self.root = Path(root)
        self.clock = clock or SystemClock()
        self.adapter = adapter or detect_platform_adapter(clock=self.clock)
        self.policy = policy or StalenessPolicy()
        self.probe_worker_id = probe_worker_id
        self.probe_instance_id = probe_instance_id

    def _now(self) -> datetime:
        return require_aware(self.clock.now())

    def _outcome(
        self,
        kind: AbsenceKind,
        *,
        value: Any = None,
        detail: str = "",
        path: str | Path | None = None,
    ) -> Outcome[Any]:
        now = self._now()
        return Outcome(
            kind=kind,
            value=value,
            detail=detail,
            observed_at=format_aware(now),
            observed_epoch=epoch_of(now),
            worker_id=self.probe_worker_id,
            path=None if path is None else os.fspath(path),
        )

    def _stamp(self, worker_id: str, instance_id: str) -> dict[str, Any]:
        now = self._now()
        return {
            "worker_id": worker_id,
            "instance_id": instance_id,
            "observed_at": format_aware(now),
            "observed_epoch": epoch_of(now),
            "tz_offset": now.strftime("%z"),
        }

    def verify_surface(self) -> Outcome[Path]:
        """Refuse-not-guess. Existence of the directory is not identity."""
        if not self.root.exists():
            return self._outcome(
                AbsenceKind.NOT_FOUND,
                detail="mail root missing; refuse write (dead surface, not cwd)",
                path=self.root,
            )
        if not self.root.is_dir():
            return self._outcome(
                AbsenceKind.UNREADABLE,
                detail="mail root exists but is not a directory",
                path=self.root,
            )
        sentinel = self.root / SENTINEL_NAME
        if not sentinel.exists():
            return self._outcome(
                AbsenceKind.IDENTITY_MISMATCH,
                detail=(
                    "empty-dir sentinel trap: root exists but .cosmos_mail_root "
                    "is absent (mesh() lesson — existence is not identity)"
                ),
                path=sentinel,
            )
        try:
            body = sentinel.read_bytes()
        except OSError as exc:
            return self._outcome(
                AbsenceKind.UNREADABLE,
                detail=f"sentinel unreadable: {exc}",
                path=sentinel,
            )
        if body != SENTINEL_BODY.encode("ascii"):
            return self._outcome(
                AbsenceKind.IDENTITY_MISMATCH,
                detail="sentinel wrong-identity: content does not match COSMOS_MAIL_ROOT v1",
                path=sentinel,
            )
        return self._outcome(
            AbsenceKind.FOUND,
            value=self.root,
            detail="sentinel verified",
            path=self.root,
        )

    def _require_worker_id(self, worker_id: str) -> Outcome[str]:
        if _validate_worker_id(worker_id) is not None:
            return self._outcome(
                AbsenceKind.REFUSED,
                detail=(
                    "worker id must match ^[a-z][a-z0-9._-]{0,62}$ "
                    "(lowercase; Windows case-collision guard)"
                ),
                path=worker_id,
            )
        return self._outcome(
            AbsenceKind.FOUND, value=worker_id, detail="worker id canonical"
        )

    def _casefold_collision(self, worker_id: str) -> Outcome[str]:
        workers = self.root / "workers"
        if not workers.is_dir():
            return self._outcome(
                AbsenceKind.FOUND, value=worker_id, detail="no workers dir yet"
            )
        try:
            children = list(workers.iterdir())
        except OSError as exc:
            return self._outcome(
                AbsenceKind.UNREADABLE,
                detail=f"workers dir unreadable: {exc}",
                path=workers,
            )
        for child in children:
            if (
                child.name != worker_id
                and child.name.casefold() == worker_id.casefold()
            ):
                return self._outcome(
                    AbsenceKind.COLLISION_REFUSED,
                    detail=f"case-colliding worker id {child.name!r} vs {worker_id!r}",
                    path=child,
                )
        return self._outcome(
            AbsenceKind.FOUND, value=worker_id, detail="no casefold collision"
        )

    def worker_dir(self, worker_id: str) -> Path:
        return self.root / "workers" / worker_id

    def inbox_dir(self, worker_id: str) -> Path:
        return self.worker_dir(worker_id) / "inbox"

    def outbox_dir(self, worker_id: str) -> Path:
        return self.worker_dir(worker_id) / "outbox"

    def identity_path(self, worker_id: str) -> Path:
        return self.worker_dir(worker_id) / "identity.json"

    def heartbeat_path(self, worker_id: str) -> Path:
        return self.worker_dir(worker_id) / "heartbeat.json"

    def message_store_path(self, message_id: str) -> Path:
        return self.root / "messages" / f"{message_id}.json"

    def receipt_dir(self, message_id: str) -> Path:
        return self.root / "receipts" / message_id

    def receipt_path(self, message_id: str, kind: ReceiptKind, worker_id: str) -> Path:
        return self.receipt_dir(message_id) / f"{kind.value}-{worker_id}.json"

    def _write_exclusive(self, path: Path, payload: bytes) -> Outcome[Path]:
        parent = path.parent
        if not parent.is_dir():
            return self._outcome(
                AbsenceKind.NOT_FOUND,
                detail="parent directory missing; refuse-not-guess",
                path=parent,
            )
        created = self.adapter.exclusive_create(path)
        if created.kind is not AbsenceKind.FOUND or created.value is None:
            return Outcome(
                kind=created.kind,
                value=None,
                detail=created.detail,
                observed_at=created.observed_at,
                observed_epoch=created.observed_epoch,
                worker_id=created.worker_id,
                path=created.path,
            )
        written = self.adapter.write_fsync_close(created.value, payload)
        if written.kind is not AbsenceKind.FOUND:
            return Outcome(
                kind=written.kind,
                value=None,
                detail=written.detail,
                observed_at=written.observed_at,
                observed_epoch=written.observed_epoch,
                worker_id=written.worker_id,
                path=written.path,
            )
        try:
            back = path.read_bytes()
        except OSError as exc:
            return self._outcome(
                AbsenceKind.UNREADABLE,
                detail=f"read-back failed: {exc}",
                path=path,
            )
        if back != payload:
            return self._outcome(
                AbsenceKind.HASH_MISMATCH,
                detail="read-back bytes do not match written bytes",
                path=path,
            )
        return self._outcome(
            AbsenceKind.FOUND,
            value=path,
            detail="exclusive write read-back ok",
            path=path,
        )

    def _read_json(self, path: Path) -> Outcome[dict[str, Any]]:
        if not path.exists():
            return self._outcome(
                AbsenceKind.NOT_FOUND, detail="json artifact missing", path=path
            )
        try:
            raw = path.read_bytes()
        except OSError as exc:
            return self._outcome(
                AbsenceKind.UNREADABLE,
                detail=f"json artifact unreadable: {exc}",
                path=path,
            )
        try:
            parsed = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            return self._outcome(
                AbsenceKind.UNPARSEABLE,
                detail=f"torn/unparseable JSON refused: {exc}",
                path=path,
            )
        if not isinstance(parsed, dict):
            return self._outcome(
                AbsenceKind.UNPARSEABLE,
                detail="JSON root is not an object",
                path=path,
            )
        return self._outcome(
            AbsenceKind.FOUND, value=parsed, detail="json parsed", path=path
        )

    def _write_overwrite_json(
        self, path: Path, record: dict[str, Any]
    ) -> Outcome[Path]:
        """Heartbeat-style overwrite. Not used for messages or receipts."""
        payload = dump_json(record)
        tmp = path.with_name(f".{path.name}.tmp.{uuid.uuid4().hex[:8]}")
        try:
            tmp.write_bytes(payload)
            with tmp.open("rb") as handle:
                os.fsync(handle.fileno())
            os.replace(tmp, path)
        except OSError as exc:
            if tmp.exists():
                try:
                    tmp.unlink()
                except OSError:
                    pass
            return self._outcome(
                AbsenceKind.UNREADABLE,
                detail=f"overwrite failed: {exc}",
                path=path,
            )
        return self._outcome(
            AbsenceKind.FOUND, value=path, detail="overwrite read-back path", path=path
        )

    def register_worker(
        self, worker_id: str, *, instance_id: str = "i1"
    ) -> Outcome[Any]:
        surface = self.verify_surface()
        if surface.kind is not AbsenceKind.FOUND:
            return Outcome(
                kind=surface.kind,
                value=None,
                detail=surface.detail,
                observed_at=surface.observed_at,
                observed_epoch=surface.observed_epoch,
                worker_id=surface.worker_id,
                path=surface.path,
            )
        named = self._require_worker_id(worker_id)
        if named.kind is not AbsenceKind.FOUND:
            return named
        collision = self._casefold_collision(worker_id)
        if collision.kind is not AbsenceKind.FOUND:
            return collision
        wdir = self.worker_dir(worker_id)
        inbox = self.inbox_dir(worker_id)
        outbox = self.outbox_dir(worker_id)
        identity_path = self.identity_path(worker_id)
        if identity_path.exists():
            existing = self._read_json(identity_path)
            if existing.kind is not AbsenceKind.FOUND or existing.value is None:
                return existing
            if existing.value.get("worker_id") != worker_id:
                return self._outcome(
                    AbsenceKind.IDENTITY_MISMATCH,
                    detail="identity.json worker_id does not match directory",
                    path=identity_path,
                )
            return self._outcome(
                AbsenceKind.REFUSED,
                detail="worker already registered; refuse silent re-identity",
                path=identity_path,
            )
        try:
            wdir.mkdir(parents=True, exist_ok=True)
            inbox.mkdir(exist_ok=True)
            outbox.mkdir(exist_ok=True)
            (self.root / "messages").mkdir(exist_ok=True)
            (self.root / "receipts").mkdir(exist_ok=True)
        except OSError as exc:
            return self._outcome(
                AbsenceKind.UNREADABLE,
                detail=f"could not create worker dirs: {exc}",
                path=wdir,
            )
        stamp = self._stamp(worker_id, instance_id)
        identity = {
            "schema": SCHEMA_IDENTITY,
            "worker_id": worker_id,
            "instance_id": instance_id,
            "created_at": stamp["observed_at"],
            "created_epoch": stamp["observed_epoch"],
            "tz_offset": stamp["tz_offset"],
        }
        written = self._write_exclusive(identity_path, dump_json(identity))
        if written.kind is not AbsenceKind.FOUND:
            return written
        beat = self.touch_heartbeat(worker_id, instance_id=instance_id)
        if beat.kind is not AbsenceKind.FOUND:
            return beat
        return self._outcome(
            AbsenceKind.FOUND,
            value=WorkerIdentity(worker_id=worker_id, instance_id=instance_id),
            detail="worker registered",
            path=wdir,
        )

    def touch_heartbeat(
        self, worker_id: str, *, instance_id: str = "i1"
    ) -> Outcome[Any]:
        surface = self.verify_surface()
        if surface.kind is not AbsenceKind.FOUND:
            return surface
        named = self._require_worker_id(worker_id)
        if named.kind is not AbsenceKind.FOUND:
            return named
        if not self.worker_dir(worker_id).is_dir():
            return self._outcome(
                AbsenceKind.NOT_FOUND,
                detail="worker directory missing; heartbeat refused",
                path=self.worker_dir(worker_id),
            )
        stamp = self._stamp(worker_id, instance_id)
        record = {
            "schema": SCHEMA_HEARTBEAT,
            **stamp,
        }
        return self._write_overwrite_json(self.heartbeat_path(worker_id), record)

    def _read_identity(self, worker_id: str) -> Outcome[dict[str, Any]]:
        path = self.identity_path(worker_id)
        if not self.worker_dir(worker_id).exists():
            return self._outcome(
                AbsenceKind.NOT_FOUND,
                detail="worker directory missing (dead phone)",
                path=self.worker_dir(worker_id),
            )
        parsed = self._read_json(path)
        if parsed.kind is not AbsenceKind.FOUND or parsed.value is None:
            if parsed.kind is AbsenceKind.NOT_FOUND:
                return self._outcome(
                    AbsenceKind.NOT_FOUND,
                    detail="identity.json missing (dead phone)",
                    path=path,
                )
            return parsed
        if parsed.value.get("worker_id") != worker_id:
            return self._outcome(
                AbsenceKind.IDENTITY_MISMATCH,
                detail="identity worker_id does not match directory name",
                path=path,
            )
        if parsed.value.get("schema") != SCHEMA_IDENTITY:
            return self._outcome(
                AbsenceKind.UNPARSEABLE,
                detail="identity schema missing or unknown",
                path=path,
            )
        return parsed

    def _clock_check(
        self, created_epoch: float, *, path: Path | None = None
    ) -> Outcome[None]:
        now_epoch = epoch_of(self._now())
        if created_epoch - now_epoch > self.policy.clock_skew_future_s:
            return self._outcome(
                AbsenceKind.OUT_OF_CLOCK,
                detail=(
                    f"artifact epoch {created_epoch} is {created_epoch - now_epoch:.3f}s "
                    f"in the future (skew budget {self.policy.clock_skew_future_s}s)"
                ),
                path=path,
            )
        return self._outcome(AbsenceKind.FOUND, detail="clock within skew")

    def _parse_message(self, path: Path) -> Outcome[Any]:
        parsed = self._read_json(path)
        if parsed.kind is not AbsenceKind.FOUND or parsed.value is None:
            return parsed
        record = parsed.value
        missing = [key for key in REQUIRED_MESSAGE_FIELDS if key not in record]
        if missing:
            return self._outcome(
                AbsenceKind.UNPARSEABLE,
                detail=f"message missing required fields: {missing}",
                path=path,
            )
        if record.get("schema") != SCHEMA_MESSAGE:
            return self._outcome(
                AbsenceKind.UNPARSEABLE,
                detail="message schema missing or unknown",
                path=path,
            )
        declared = record["payload_hash"]
        if not isinstance(declared, str):
            return self._outcome(
                AbsenceKind.UNPARSEABLE,
                detail="payload_hash is not a string",
                path=path,
            )
        computed = payload_hash(record["payload"])
        if computed != declared:
            return self._outcome(
                AbsenceKind.HASH_MISMATCH,
                detail="half-written or torn payload: declared hash != sha256(canonical payload)",
                path=path,
            )
        try:
            created_epoch = float(record["created_epoch"])
        except (TypeError, ValueError):
            return self._outcome(
                AbsenceKind.OUT_OF_CLOCK,
                detail="created_epoch unparseable",
                path=path,
            )
        clocked = self._clock_check(created_epoch, path=path)
        if clocked.kind is not AbsenceKind.FOUND:
            return clocked
        ack_deadline = record.get("ack_deadline_epoch")
        if ack_deadline is not None:
            try:
                ack_deadline = float(ack_deadline)
            except (TypeError, ValueError):
                return self._outcome(
                    AbsenceKind.OUT_OF_CLOCK,
                    detail="ack_deadline_epoch unparseable",
                    path=path,
                )
        message = Message(
            schema=SCHEMA_MESSAGE,
            message_id=str(record["message_id"]),
            sender_id=str(record["sender_id"]),
            sender_instance=str(record["sender_instance"]),
            recipient_id=str(record["recipient_id"]),
            created_at=str(record["created_at"]),
            created_epoch=created_epoch,
            tz_offset=str(record["tz_offset"]),
            subject=str(record.get("subject") or ""),
            correlation_id=str(record.get("correlation_id") or ""),
            payload=record["payload"],
            payload_hash=declared,
            requires_ack=bool(record["requires_ack"]),
            ack_deadline_epoch=ack_deadline,
            ttl_seconds=(
                float(record["ttl_seconds"])
                if record.get("ttl_seconds") is not None
                else None
            ),
        )
        return self._outcome(
            AbsenceKind.FOUND, value=message, detail="message verified", path=path
        )

    def _list_inbox_files(self, worker_id: str) -> Outcome[list[Path]]:
        inbox = self.inbox_dir(worker_id)
        if not inbox.exists():
            return self._outcome(
                AbsenceKind.NOT_FOUND,
                detail="inbox directory missing (dead phone, never no-news)",
                path=inbox,
            )
        if not inbox.is_dir():
            return self._outcome(
                AbsenceKind.UNREADABLE,
                detail="inbox path exists but is not a directory",
                path=inbox,
            )
        try:
            names = list(inbox.iterdir())
        except OSError as exc:
            return self._outcome(
                AbsenceKind.UNREADABLE,
                detail=f"inbox unreadable: {exc}",
                path=inbox,
            )
        files = [
            item
            for item in names
            if item.is_file()
            and not item.name.startswith(".")
            and not item.name.startswith("_")
            and item.name.endswith(".json")
        ]
        files.sort(key=lambda item: item.name)
        return self._outcome(
            AbsenceKind.FOUND,
            value=files,
            detail=f"inbox files={len(files)}",
            path=inbox,
        )

    def list_inbox(self, worker_id: str) -> Outcome[Any]:
        named = self._require_worker_id(worker_id)
        if named.kind is not AbsenceKind.FOUND:
            return named
        files = self._list_inbox_files(worker_id)
        if files.kind is not AbsenceKind.FOUND or files.value is None:
            return files
        entries = [
            InboxEntry(
                filename=item.name,
                path=os.fspath(item),
                parse=self._parse_message(item),
            )
            for item in files.value
        ]
        return self._outcome(
            AbsenceKind.FOUND, value=entries, detail=f"entries={len(entries)}"
        )

    def get_message(self, message_id: str) -> Outcome[Any]:
        surface = self.verify_surface()
        if surface.kind is not AbsenceKind.FOUND:
            return surface
        path = self.message_store_path(message_id)
        if not path.exists():
            return self._outcome(
                AbsenceKind.NOT_IN_RECORD,
                detail="message_id is not in the message store",
                path=path,
            )
        return self._parse_message(path)

    def get_receipt(
        self, message_id: str, kind: ReceiptKind, worker_id: str
    ) -> Outcome[Any]:
        surface = self.verify_surface()
        if surface.kind is not AbsenceKind.FOUND:
            return surface
        path = self.receipt_path(message_id, kind, worker_id)
        parsed = self._read_json(path)
        if parsed.kind is AbsenceKind.NOT_FOUND:
            return self._outcome(
                AbsenceKind.NOT_IN_RECORD,
                detail=f"{kind.value} receipt not in record",
                path=path,
            )
        if parsed.kind is not AbsenceKind.FOUND or parsed.value is None:
            return parsed
        record = parsed.value
        try:
            receipt = Receipt(
                schema=str(record["schema"]),
                receipt_kind=ReceiptKind(str(record["receipt_kind"])),
                message_id=str(record["message_id"]),
                worker_id=str(record["worker_id"]),
                instance_id=str(record["instance_id"]),
                observed_at=str(record["observed_at"]),
                observed_epoch=float(record["observed_epoch"]),
                tz_offset=str(record["tz_offset"]),
                payload_hash=str(record["payload_hash"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            return self._outcome(
                AbsenceKind.UNPARSEABLE,
                detail=f"receipt fields refused: {exc}",
                path=path,
            )
        return self._outcome(
            AbsenceKind.FOUND, value=receipt, detail="receipt found", path=path
        )

    def _write_receipt(self, receipt: Receipt) -> Outcome[Path]:
        directory = self.receipt_dir(receipt.message_id)
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            return self._outcome(
                AbsenceKind.UNREADABLE,
                detail=f"receipt dir refused: {exc}",
                path=directory,
            )
        path = self.receipt_path(
            receipt.message_id, receipt.receipt_kind, receipt.worker_id
        )
        return self._write_exclusive(path, dump_json(receipt.to_record()))

    def send(
        self,
        sender_id: str,
        recipient_id: str,
        payload: object,
        *,
        subject: str = "",
        correlation_id: str = "",
        requires_ack: bool = False,
        ack_deadline_s: float | None = None,
        sender_instance: str = "i1",
        ttl_seconds: float | None = None,
    ) -> Outcome[Any]:
        surface = self.verify_surface()
        if surface.kind is not AbsenceKind.FOUND:
            return surface
        for identity in (sender_id, recipient_id):
            named = self._require_worker_id(identity)
            if named.kind is not AbsenceKind.FOUND:
                return named
        sender_ident = self._read_identity(sender_id)
        if sender_ident.kind is not AbsenceKind.FOUND:
            return sender_ident
        recipient_ident = self._read_identity(recipient_id)
        if recipient_ident.kind is not AbsenceKind.FOUND:
            if recipient_ident.kind is AbsenceKind.NOT_FOUND:
                return self._outcome(
                    AbsenceKind.NOT_FOUND,
                    detail="recipient mailbox missing (dead phone); send refused",
                    path=self.inbox_dir(recipient_id),
                )
            return recipient_ident
        inbox_state = self._list_inbox_files(recipient_id)
        if inbox_state.kind is not AbsenceKind.FOUND:
            return inbox_state
        now = self._now()
        digest = payload_hash(payload)
        nonce = uuid.uuid4().hex[:8]
        message_id = (
            f"{sender_id}__{fs_safe_offset_timestamp(now)}__{digest[:12]}__{nonce}"
        )
        ack_deadline_epoch = None
        if requires_ack:
            horizon = ack_deadline_s if ack_deadline_s is not None else 3600.0
            ack_deadline_epoch = epoch_of(now) + horizon
        message = Message(
            schema=SCHEMA_MESSAGE,
            message_id=message_id,
            sender_id=sender_id,
            sender_instance=sender_instance,
            recipient_id=recipient_id,
            created_at=format_aware(now),
            created_epoch=epoch_of(now),
            tz_offset=now.strftime("%z"),
            subject=subject,
            correlation_id=correlation_id,
            payload=payload,
            payload_hash=digest,
            requires_ack=requires_ack,
            ack_deadline_epoch=ack_deadline_epoch,
            ttl_seconds=ttl_seconds,
        )
        body = dump_json(message.to_record())
        stored = self._write_exclusive(self.message_store_path(message_id), body)
        if stored.kind is not AbsenceKind.FOUND:
            return stored
        inbox_path = self.inbox_dir(recipient_id) / f"{message_id}.json"
        placed = self._write_exclusive(inbox_path, body)
        if placed.kind is not AbsenceKind.FOUND:
            return placed
        verified = self._parse_message(inbox_path)
        if verified.kind is not AbsenceKind.FOUND:
            return verified
        outbox_path = self.outbox_dir(sender_id) / f"{message_id}.json"
        outbox_record = {
            "schema": "cosmos.mail.outbox.v1",
            "message_id": message_id,
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "payload_hash": digest,
            **self._stamp(sender_id, sender_instance),
        }
        outbox = self._write_exclusive(outbox_path, dump_json(outbox_record))
        if outbox.kind is not AbsenceKind.FOUND:
            return outbox
        sent = Receipt(
            schema=SCHEMA_RECEIPT,
            receipt_kind=ReceiptKind.SENT,
            message_id=message_id,
            worker_id=sender_id,
            instance_id=sender_instance,
            observed_at=format_aware(now),
            observed_epoch=epoch_of(now),
            tz_offset=now.strftime("%z"),
            payload_hash=digest,
        )
        sent_write = self._write_receipt(sent)
        if sent_write.kind is not AbsenceKind.FOUND:
            return sent_write
        delivered = Receipt(
            schema=SCHEMA_RECEIPT,
            receipt_kind=ReceiptKind.DELIVERED,
            message_id=message_id,
            worker_id=recipient_id,
            instance_id=str(
                recipient_ident.value.get("instance_id")
                if recipient_ident.value
                else "i1"
            ),
            observed_at=format_aware(self._now()),
            observed_epoch=epoch_of(self._now()),
            tz_offset=self._now().strftime("%z"),
            payload_hash=digest,
        )
        delivered_write = self._write_receipt(delivered)
        if delivered_write.kind is not AbsenceKind.FOUND:
            return delivered_write
        return self._outcome(
            AbsenceKind.FOUND,
            value=message,
            detail="send read-back verified; sent and delivered receipts recorded separately",
            path=inbox_path,
        )

    def receive(
        self,
        worker_id: str,
        *,
        write_read_receipt: bool = True,
        instance_id: str = "i1",
    ) -> Outcome[Any]:
        surface = self.verify_surface()
        if surface.kind is not AbsenceKind.FOUND:
            return surface
        named = self._require_worker_id(worker_id)
        if named.kind is not AbsenceKind.FOUND:
            return named
        identity = self._read_identity(worker_id)
        if identity.kind is not AbsenceKind.FOUND:
            return identity
        listed = self.list_inbox(worker_id)
        if listed.kind is not AbsenceKind.FOUND or listed.value is None:
            return listed
        messages: list[Message] = []
        defects: list[Outcome[None]] = []
        for entry in listed.value:
            if entry.parse.kind is AbsenceKind.FOUND and entry.parse.value is not None:
                message = entry.parse.value
                already = self.get_receipt(
                    message.message_id, ReceiptKind.READ, worker_id
                )
                if already.kind is AbsenceKind.FOUND:
                    continue
                if write_read_receipt:
                    now = self._now()
                    receipt = Receipt(
                        schema=SCHEMA_RECEIPT,
                        receipt_kind=ReceiptKind.READ,
                        message_id=message.message_id,
                        worker_id=worker_id,
                        instance_id=instance_id,
                        observed_at=format_aware(now),
                        observed_epoch=epoch_of(now),
                        tz_offset=now.strftime("%z"),
                        payload_hash=message.payload_hash,
                    )
                    written = self._write_receipt(receipt)
                    if written.kind is not AbsenceKind.FOUND:
                        defects.append(
                            self._outcome(
                                written.kind,
                                detail=written.detail,
                                path=written.path,
                            )
                        )
                        continue
                messages.append(message)
            else:
                defects.append(
                    self._outcome(
                        entry.parse.kind,
                        detail=entry.parse.detail,
                        path=entry.parse.path,
                    )
                )
        if not messages and defects:
            return self._outcome(
                defects[0].kind,
                value=ReceiveReport(messages=[], defects=defects),
                detail=defects[0].detail,
            )
        if not messages:
            return self._outcome(
                AbsenceKind.EMPTY,
                value=ReceiveReport(messages=[], defects=[]),
                detail="mailbox exists and is empty of unread verified messages",
                path=self.inbox_dir(worker_id),
            )
        return self._outcome(
            AbsenceKind.FOUND,
            value=ReceiveReport(messages=messages, defects=defects),
            detail=f"received {len(messages)} unread; defects={len(defects)}",
            path=self.inbox_dir(worker_id),
        )

    def _heartbeat_outcome(self, worker_id: str) -> Outcome[Any]:
        path = self.heartbeat_path(worker_id)
        parsed = self._read_json(path)
        if parsed.kind is not AbsenceKind.FOUND or parsed.value is None:
            if parsed.kind is AbsenceKind.NOT_FOUND:
                return self._outcome(
                    AbsenceKind.NOT_FOUND,
                    detail="heartbeat missing",
                    path=path,
                )
            return parsed
        record = parsed.value
        try:
            observed_epoch = float(record["observed_epoch"])
        except (KeyError, TypeError, ValueError):
            return self._outcome(
                AbsenceKind.OUT_OF_CLOCK,
                detail="heartbeat observed_epoch unparseable",
                path=path,
            )
        clocked = self._clock_check(observed_epoch, path=path)
        if clocked.kind is not AbsenceKind.FOUND:
            return clocked
        age = epoch_of(self._now()) - observed_epoch
        if age > self.policy.heartbeat_stale_after_s:
            return self._outcome(
                AbsenceKind.STALE,
                value=record,
                detail=f"heartbeat age {age:.3f}s exceeds {self.policy.heartbeat_stale_after_s}s",
                path=path,
            )
        return self._outcome(
            AbsenceKind.FOUND,
            value=record,
            detail=f"heartbeat age {age:.3f}s",
            path=path,
        )

    def _last_read_receipt(self, worker_id: str) -> Outcome[Any]:
        receipts_root = self.root / "receipts"
        if not receipts_root.is_dir():
            return self._outcome(
                AbsenceKind.NOT_IN_RECORD,
                detail="receipts store not in record",
                path=receipts_root,
            )
        newest: Receipt | None = None
        newest_epoch = -1.0
        try:
            children = list(receipts_root.iterdir())
        except OSError as exc:
            return self._outcome(
                AbsenceKind.UNREADABLE,
                detail=f"receipts unreadable: {exc}",
                path=receipts_root,
            )
        for directory in children:
            if not directory.is_dir():
                continue
            found = self.get_receipt(directory.name, ReceiptKind.READ, worker_id)
            if (
                found.kind is AbsenceKind.FOUND
                and found.value is not None
                and found.value.observed_epoch > newest_epoch
            ):
                newest = found.value
                newest_epoch = found.value.observed_epoch
        if newest is None:
            return self._outcome(
                AbsenceKind.NOT_IN_RECORD,
                detail="no read receipt in record for this worker",
            )
        return self._outcome(
            AbsenceKind.FOUND, value=newest, detail="last read receipt"
        )

    def probe(self, worker_id: str) -> ProbeReport:
        """Report missing, empty, unreadable, and stale as distinct facets."""
        now = self._now()
        named = self._require_worker_id(worker_id)
        if named.kind is not AbsenceKind.FOUND:
            empty_facet = self._outcome(named.kind, detail=named.detail)
            facets = ProbeFacets(
                root_sentinel=empty_facet,
                identity=empty_facet,
                heartbeat=empty_facet,
                inbox=empty_facet,
                unread_count=0,
                oldest_unacked_required=self._outcome(
                    AbsenceKind.NOT_IN_RECORD, detail="worker id refused"
                ),
                last_read_receipt=self._outcome(
                    AbsenceKind.NOT_IN_RECORD, detail="worker id refused"
                ),
            )
            return ProbeReport(
                schema=SCHEMA_PROBE,
                worker_id=worker_id,
                mailbox_state=named.kind,
                facets=facets,
                observed_at=format_aware(now),
                observed_epoch=epoch_of(now),
                tz_offset=now.strftime("%z"),
                probe_worker_id=self.probe_worker_id,
                exit_code=exit_code_for(named.kind),
            )

        root_sentinel = self.verify_surface()
        identity = (
            self._read_identity(worker_id)
            if root_sentinel.kind is AbsenceKind.FOUND
            else self._outcome(
                root_sentinel.kind, detail=root_sentinel.detail, path=root_sentinel.path
            )
        )
        heartbeat = (
            self._heartbeat_outcome(worker_id)
            if identity.kind is AbsenceKind.FOUND
            else self._outcome(
                identity.kind, detail=identity.detail, path=identity.path
            )
        )

        inbox_listed = (
            self.list_inbox(worker_id)
            if root_sentinel.kind is AbsenceKind.FOUND
            else None
        )
        if inbox_listed is None:
            inbox_facet = self._outcome(
                root_sentinel.kind, detail=root_sentinel.detail, path=root_sentinel.path
            )
            entries: list[InboxEntry] = []
        elif inbox_listed.kind is not AbsenceKind.FOUND or inbox_listed.value is None:
            inbox_facet = self._outcome(
                inbox_listed.kind, detail=inbox_listed.detail, path=inbox_listed.path
            )
            entries = []
        elif not inbox_listed.value:
            inbox_facet = self._outcome(
                AbsenceKind.EMPTY,
                detail="inbox exists and contains no message files",
                path=self.inbox_dir(worker_id),
            )
            entries = []
        else:
            inbox_facet = self._outcome(
                AbsenceKind.FOUND,
                detail=f"inbox files={len(inbox_listed.value)}",
                path=self.inbox_dir(worker_id),
            )
            entries = inbox_listed.value

        defects: list[Outcome[None]] = []
        unread: list[Message] = []
        stale_unacked: list[Message] = []
        for entry in entries:
            if entry.parse.kind is not AbsenceKind.FOUND or entry.parse.value is None:
                defects.append(
                    self._outcome(
                        entry.parse.kind,
                        detail=entry.parse.detail,
                        path=entry.parse.path,
                    )
                )
                continue
            message = entry.parse.value
            read = self.get_receipt(message.message_id, ReceiptKind.READ, worker_id)
            if read.kind is AbsenceKind.FOUND:
                continue
            unread.append(message)
            if (
                message.requires_ack
                and message.ack_deadline_epoch is not None
                and epoch_of(now) > message.ack_deadline_epoch
            ):
                stale_unacked.append(message)

        if stale_unacked:
            oldest_unacked = min(stale_unacked, key=lambda item: item.created_epoch)
            oldest_outcome = self._outcome(
                AbsenceKind.STALE,
                value=oldest_unacked,
                detail="required-ack unanswered past deadline",
                path=self.inbox_dir(worker_id) / f"{oldest_unacked.message_id}.json",
            )
        elif unread:
            required = [item for item in unread if item.requires_ack]
            if required:
                oldest_required = min(required, key=lambda item: item.created_epoch)
                oldest_outcome = self._outcome(
                    AbsenceKind.FOUND,
                    value=oldest_required,
                    detail="required-ack still inside deadline",
                )
            else:
                oldest_outcome = self._outcome(
                    AbsenceKind.NOT_IN_RECORD,
                    detail="no required-ack message in unread set",
                )
        else:
            oldest_outcome = self._outcome(
                AbsenceKind.NOT_IN_RECORD,
                detail="no unanswered required-ack in record",
            )

        last_read = (
            self._last_read_receipt(worker_id)
            if root_sentinel.kind is AbsenceKind.FOUND
            else self._outcome(root_sentinel.kind, detail=root_sentinel.detail)
        )

        state = _mailbox_state(
            root_sentinel=root_sentinel.kind,
            identity=identity.kind,
            heartbeat=heartbeat.kind,
            inbox=inbox_facet.kind,
            defects=defects,
            unread_count=len(unread),
            stale_unacked=bool(stale_unacked),
        )
        facets = ProbeFacets(
            root_sentinel=self._outcome(
                root_sentinel.kind, detail=root_sentinel.detail, path=root_sentinel.path
            ),
            identity=identity,
            heartbeat=heartbeat,
            inbox=inbox_facet,
            unread_count=len(unread),
            oldest_unacked_required=oldest_outcome,
            last_read_receipt=last_read,
            defects=defects,
        )
        return ProbeReport(
            schema=SCHEMA_PROBE,
            worker_id=worker_id,
            mailbox_state=state,
            facets=facets,
            observed_at=format_aware(now),
            observed_epoch=epoch_of(now),
            tz_offset=now.strftime("%z"),
            probe_worker_id=self.probe_worker_id,
            exit_code=exit_code_for(state),
        )


def _mailbox_state(
    *,
    root_sentinel: AbsenceKind,
    identity: AbsenceKind,
    heartbeat: AbsenceKind,
    inbox: AbsenceKind,
    defects: list[Outcome[None]],
    unread_count: int,
    stale_unacked: bool,
) -> AbsenceKind:
    """Dominant mailbox state. Priority is refusal > stale > empty/found."""
    for kind in (
        AbsenceKind.NOT_FOUND,
        AbsenceKind.UNREADABLE,
        AbsenceKind.UNPARSEABLE,
        AbsenceKind.IDENTITY_MISMATCH,
        AbsenceKind.OUT_OF_CLOCK,
        AbsenceKind.HASH_MISMATCH,
        AbsenceKind.REFUSED,
        AbsenceKind.COLLISION_REFUSED,
    ):
        if kind in (root_sentinel, identity, inbox):
            return kind
        if any(item.kind is kind for item in defects):
            return kind
    if heartbeat is AbsenceKind.OUT_OF_CLOCK:
        return AbsenceKind.OUT_OF_CLOCK
    if heartbeat is AbsenceKind.STALE or stale_unacked:
        return AbsenceKind.STALE
    if inbox is AbsenceKind.EMPTY or unread_count == 0:
        return AbsenceKind.EMPTY
    return AbsenceKind.FOUND


def prepare_surface(
    root: Path,
    *,
    adapter: PlatformAdapter | None = None,
    clock: Clock | None = None,
    worker_id: str = SPIKE_WORKER_ID,
) -> Outcome[Path]:
    """Explicit constructor for a new exchange. Never called at import."""
    exchange = MailExchange(
        root, adapter=adapter, clock=clock, probe_worker_id=worker_id
    )
    root = Path(root)
    try:
        root.mkdir(parents=True, exist_ok=True)
        (root / "workers").mkdir(exist_ok=True)
        (root / "messages").mkdir(exist_ok=True)
        (root / "receipts").mkdir(exist_ok=True)
    except OSError as exc:
        return exchange._outcome(
            AbsenceKind.UNREADABLE,
            detail=f"could not create mail root: {exc}",
            path=root,
        )
    sentinel = root / SENTINEL_NAME
    if sentinel.exists():
        try:
            body = sentinel.read_bytes()
        except OSError as exc:
            return exchange._outcome(
                AbsenceKind.UNREADABLE,
                detail=f"sentinel unreadable: {exc}",
                path=sentinel,
            )
        if body != SENTINEL_BODY.encode("ascii"):
            return exchange._outcome(
                AbsenceKind.IDENTITY_MISMATCH,
                detail="existing sentinel has the wrong identity",
                path=sentinel,
            )
        return exchange._outcome(
            AbsenceKind.FOUND, value=root, detail="surface already prepared", path=root
        )
    written = exchange._write_exclusive(sentinel, SENTINEL_BODY.encode("ascii"))
    if written.kind is not AbsenceKind.FOUND:
        return written
    return exchange._outcome(
        AbsenceKind.FOUND, value=root, detail="surface prepared", path=root
    )
