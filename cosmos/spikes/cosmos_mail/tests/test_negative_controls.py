"""NEGATIVE controls — the gates that must close. A one-sided test is not a gate."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from cosmos.spikes.cosmos_mail.clock import FrozenClock
from cosmos.spikes.cosmos_mail.mail import (
    SENTINEL_BODY,
    SENTINEL_NAME,
    MailExchange,
    StalenessPolicy,
    payload_hash,
    prepare_surface,
)
from cosmos.spikes.cosmos_mail.platform import PosixPlatformAdapter
from cosmos.spikes.cosmos_mail.types import AbsenceKind, ReceiptKind


def _plant_message(
    path: Path,
    *,
    payload: object,
    digest: str,
    created: datetime,
    requires_ack: bool = False,
    ack_deadline_epoch: float | None = None,
    message_id: str = "planted",
) -> None:
    record = {
        "schema": "cosmos.mail.message.v1",
        "message_id": message_id,
        "sender_id": "alice",
        "sender_instance": "i1",
        "recipient_id": "bob",
        "created_at": created.isoformat(timespec="microseconds"),
        "created_epoch": created.timestamp(),
        "tz_offset": created.strftime("%z"),
        "subject": "",
        "correlation_id": "",
        "payload": payload,
        "payload_hash": digest,
        "requires_ack": requires_ack,
        "ack_deadline_epoch": ack_deadline_epoch,
        "ttl_seconds": None,
    }
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")


def test_missing_mailbox_is_dead_phone_nonzero(exchange: MailExchange) -> None:
    report = exchange.probe("zoe")
    assert report.mailbox_state is AbsenceKind.NOT_FOUND
    assert report.exit_code != 0
    assert report.exit_code == 3
    assert report.facets.identity.kind is AbsenceKind.NOT_FOUND


def test_send_to_missing_mailbox_refuses_and_does_not_write_cwd(
    exchange: MailExchange, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    exchange.register_worker("alice")
    monkeypatch.chdir(tmp_path)
    before = {item.name for item in tmp_path.iterdir()}
    result = exchange.send("alice", "zoe", {"no": "recipient"})
    assert result.kind is AbsenceKind.NOT_FOUND
    after = {item.name for item in tmp_path.iterdir()}
    assert after == before
    assert not (tmp_path / "COW_TO_QA_ENGINEER.md").exists()
    assert not exchange.inbox_dir("zoe").exists()


def test_missing_root_refuses_send_and_does_not_create_cwd_letter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    missing = tmp_path / "no-such-root"
    exchange = MailExchange(missing)
    result = exchange.send("alice", "bob", {"x": 1})
    assert result.kind is AbsenceKind.NOT_FOUND
    assert list(tmp_path.iterdir()) == []


def test_empty_dir_sentinel_trap(tmp_path: Path) -> None:
    empty = tmp_path / "empty-root"
    empty.mkdir()
    exchange = MailExchange(empty)
    result = exchange.verify_surface()
    assert result.kind is AbsenceKind.IDENTITY_MISMATCH
    report = exchange.probe("bob")
    assert report.mailbox_state is AbsenceKind.IDENTITY_MISMATCH


def test_wrong_sentinel_identity_refuses(tmp_path: Path) -> None:
    root = tmp_path / "wrong"
    root.mkdir()
    (root / SENTINEL_NAME).write_text("NOT THE SENTINEL\n", encoding="ascii")
    exchange = MailExchange(root)
    assert exchange.verify_surface().kind is AbsenceKind.IDENTITY_MISMATCH


def test_half_written_message_detected_by_hash(exchange: MailExchange) -> None:
    exchange.register_worker("bob")
    now = exchange.clock.now()
    planted = exchange.inbox_dir("bob") / "half.json"
    _plant_message(planted, payload={"text": "torn"}, digest="0" * 64, created=now)
    report = exchange.probe("bob")
    assert report.mailbox_state is AbsenceKind.HASH_MISMATCH
    assert any(item.kind is AbsenceKind.HASH_MISMATCH for item in report.facets.defects)
    received = exchange.receive("bob")
    assert received.kind is AbsenceKind.HASH_MISMATCH


def test_torn_json_is_unparseable_not_empty(exchange: MailExchange) -> None:
    exchange.register_worker("bob")
    torn = exchange.inbox_dir("bob") / "torn.json"
    torn.write_bytes(b"{")
    report = exchange.probe("bob")
    assert report.mailbox_state is AbsenceKind.UNPARSEABLE
    assert report.mailbox_state != AbsenceKind.EMPTY
    assert report.mailbox_state != AbsenceKind.NOT_FOUND


def test_inbox_as_file_is_unreadable_not_missing(exchange: MailExchange) -> None:
    exchange.register_worker("bob")
    inbox = exchange.inbox_dir("bob")
    for child in inbox.iterdir():
        child.unlink()
    inbox.rmdir()
    inbox.write_text("not-a-directory", encoding="utf-8")
    report = exchange.probe("bob")
    assert report.mailbox_state is AbsenceKind.UNREADABLE
    assert report.facets.inbox.kind is AbsenceKind.UNREADABLE
    assert report.exit_code != 0
    assert report.exit_code != 3


def test_stale_heartbeat_is_stale_not_empty(tmp_path: Path) -> None:
    frozen = FrozenClock(datetime(2026, 8, 23, 12, 0, tzinfo=timezone.utc))
    adapter = PosixPlatformAdapter(clock=frozen)
    prepare_surface(tmp_path, adapter=adapter, clock=frozen)
    exchange = MailExchange(
        tmp_path,
        adapter=adapter,
        clock=frozen,
        policy=StalenessPolicy(heartbeat_stale_after_s=1.0),
    )
    assert exchange.register_worker("bob").kind is AbsenceKind.FOUND
    frozen.advance(90.0)
    report = exchange.probe("bob")
    assert report.mailbox_state is AbsenceKind.STALE
    assert report.facets.heartbeat.kind is AbsenceKind.STALE
    assert report.facets.inbox.kind is AbsenceKind.EMPTY
    assert report.exit_code == 2


def test_unanswered_required_ack_is_stale(tmp_path: Path) -> None:
    frozen = FrozenClock(datetime(2026, 8, 23, 12, 0, tzinfo=timezone.utc))
    adapter = PosixPlatformAdapter(clock=frozen)
    prepare_surface(tmp_path, adapter=adapter, clock=frozen)
    exchange = MailExchange(
        tmp_path,
        adapter=adapter,
        clock=frozen,
        policy=StalenessPolicy(heartbeat_stale_after_s=10_000.0),
    )
    exchange.register_worker("alice")
    exchange.register_worker("bob")
    sent = exchange.send(
        "alice", "bob", {"q": 1}, requires_ack=True, ack_deadline_s=10.0
    )
    assert sent.kind is AbsenceKind.FOUND
    frozen.advance(20.0)
    # Keep the heartbeat fresh so STALE is the unanswered ack, not the beat.
    exchange.touch_heartbeat("bob")
    report = exchange.probe("bob")
    assert report.mailbox_state is AbsenceKind.STALE
    assert report.facets.oldest_unacked_required.kind is AbsenceKind.STALE
    assert report.facets.unread_count == 1


def test_future_timestamp_is_out_of_clock(exchange: MailExchange) -> None:
    exchange.register_worker("bob")
    future = exchange.clock.now() + timedelta(seconds=120)
    planted = exchange.inbox_dir("bob") / "future.json"
    payload = {"n": 1}
    _plant_message(
        planted, payload=payload, digest=payload_hash(payload), created=future
    )
    report = exchange.probe("bob")
    assert report.mailbox_state is AbsenceKind.OUT_OF_CLOCK


def test_unknown_message_is_not_in_record(exchange: MailExchange) -> None:
    found = exchange.get_message("no-such-id")
    assert found.kind is AbsenceKind.NOT_IN_RECORD
    receipt = exchange.get_receipt("no-such-id", ReceiptKind.READ, "bob")
    assert receipt.kind is AbsenceKind.NOT_IN_RECORD


def test_uppercase_worker_id_refused(exchange: MailExchange) -> None:
    result = exchange.register_worker("Bob")
    assert result.kind is AbsenceKind.REFUSED
    report = exchange.probe("Bob")
    assert report.mailbox_state is AbsenceKind.REFUSED


def test_casefold_collision_refused(exchange: MailExchange) -> None:
    planted = exchange.root / "workers" / "Bob"
    planted.mkdir(parents=True)
    result = exchange.register_worker("bob")
    assert result.kind is AbsenceKind.COLLISION_REFUSED


def test_identity_mismatch(exchange: MailExchange) -> None:
    exchange.register_worker("bob")
    identity = json.loads(exchange.identity_path("bob").read_text(encoding="utf-8"))
    identity["worker_id"] = "alice"
    exchange.identity_path("bob").write_text(
        json.dumps(identity, indent=2) + "\n", encoding="utf-8"
    )
    report = exchange.probe("bob")
    assert report.mailbox_state is AbsenceKind.IDENTITY_MISMATCH


def test_exclusive_create_collision(exchange: MailExchange) -> None:
    exchange.register_worker("bob")
    target = exchange.inbox_dir("bob") / "same-name.json"
    first = exchange.adapter.exclusive_create(target)
    assert first.kind is AbsenceKind.FOUND
    assert first.value is not None
    exchange.adapter.write_fsync_close(first.value, b"{}\n")
    second = exchange.adapter.exclusive_create(target)
    assert second.kind is AbsenceKind.COLLISION_REFUSED


def test_typed_absences_are_not_collapsed() -> None:
    kinds = {
        AbsenceKind.NOT_FOUND,
        AbsenceKind.EMPTY,
        AbsenceKind.UNREADABLE,
        AbsenceKind.STALE,
        AbsenceKind.OUT_OF_CLOCK,
        AbsenceKind.NOT_IN_RECORD,
        AbsenceKind.HASH_MISMATCH,
        AbsenceKind.UNPARSEABLE,
        AbsenceKind.IDENTITY_MISMATCH,
    }
    assert len(kinds) == 9
    assert AbsenceKind.NOT_FOUND != AbsenceKind.EMPTY
    assert AbsenceKind.UNREADABLE != AbsenceKind.NOT_FOUND
    assert AbsenceKind.STALE != AbsenceKind.EMPTY


def test_re_register_refuses_silent_reidentity(exchange: MailExchange) -> None:
    assert exchange.register_worker("bob").kind is AbsenceKind.FOUND
    again = exchange.register_worker("bob")
    assert again.kind is AbsenceKind.REFUSED


def test_prepare_does_not_overwrite_wrong_sentinel(tmp_path: Path) -> None:
    root = tmp_path / "x"
    root.mkdir()
    (root / SENTINEL_NAME).write_bytes(b"wrong")
    result = prepare_surface(root)
    assert result.kind is AbsenceKind.IDENTITY_MISMATCH
    assert (root / SENTINEL_NAME).read_bytes() == b"wrong"
    assert SENTINEL_BODY.encode("ascii") != b"wrong"
