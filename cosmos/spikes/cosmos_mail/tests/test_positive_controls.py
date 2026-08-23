"""POSITIVE controls — the gates that must open when the channel is healthy."""

from __future__ import annotations

import importlib
import json
import threading
import time
from pathlib import Path

import pytest

from cosmos.spikes.cosmos_mail import mail as mail_mod
from cosmos.spikes.cosmos_mail.mail import MailExchange, payload_hash, prepare_surface
from cosmos.spikes.cosmos_mail.types import (
    AbsenceKind,
    Outcome,
    ReceiptKind,
    exit_code_for,
)


def test_import_has_no_filesystem_side_effect(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    importlib.reload(mail_mod)
    assert list(tmp_path.iterdir()) == []


def test_prepare_and_register_empty_mailbox_is_empty_not_missing(
    exchange: MailExchange,
) -> None:
    registered = exchange.register_worker("bob")
    assert registered.kind is AbsenceKind.FOUND
    report = exchange.probe("bob")
    assert report.mailbox_state is AbsenceKind.EMPTY
    assert report.exit_code == 0
    assert report.facets.inbox.kind is AbsenceKind.EMPTY
    assert report.facets.identity.kind is AbsenceKind.FOUND
    assert report.facets.unread_count == 0
    assert report.facets.oldest_unacked_required.kind is AbsenceKind.NOT_IN_RECORD
    assert report.facets.last_read_receipt.kind is AbsenceKind.NOT_IN_RECORD


def test_send_readback_hash_and_unique_name(exchange: MailExchange) -> None:
    exchange.register_worker("alice")
    exchange.register_worker("bob")
    payload = {"text": "hello", "emoji": "📬"}
    sent = exchange.send("alice", "bob", payload, subject="ping")
    assert sent.kind is AbsenceKind.FOUND
    assert sent.value is not None
    assert sent.value.payload_hash == payload_hash(payload)
    assert sent.value.sender_id == "alice"
    assert sent.value.tz_offset != ""
    assert sent.value.created_epoch > 0
    name = sent.value.message_id
    assert name.startswith("alice__")
    assert sent.value.payload_hash[:12] in name
    inbox_file = exchange.inbox_dir("bob") / f"{name}.json"
    assert inbox_file.is_file()
    body = json.loads(inbox_file.read_text(encoding="utf-8"))
    assert body["payload_hash"] == sent.value.payload_hash
    assert body["created_at"].count(":") >= 2  # offset-aware ISO in the payload


def test_two_senders_two_files_zero_collisions(exchange: MailExchange) -> None:
    exchange.register_worker("alice")
    exchange.register_worker("bob")
    exchange.register_worker("carol")
    first = exchange.send("alice", "bob", {"n": 1})
    second = exchange.send("carol", "bob", {"n": 2})
    assert first.kind is AbsenceKind.FOUND
    assert second.kind is AbsenceKind.FOUND
    listed = exchange.list_inbox("bob")
    assert listed.kind is AbsenceKind.FOUND
    assert listed.value is not None
    names = [entry.filename for entry in listed.value]
    assert len(names) == 2
    assert len(set(names)) == 2
    senders = {
        entry.parse.value.sender_id for entry in listed.value if entry.parse.value
    }
    assert senders == {"alice", "carol"}


def test_send_and_receive_are_separate_receipts(exchange: MailExchange) -> None:
    exchange.register_worker("alice")
    exchange.register_worker("bob")
    sent = exchange.send("alice", "bob", {"k": "v"})
    assert sent.value is not None
    mid = sent.value.message_id
    assert (
        exchange.get_receipt(mid, ReceiptKind.SENT, "alice").kind is AbsenceKind.FOUND
    )
    assert (
        exchange.get_receipt(mid, ReceiptKind.DELIVERED, "bob").kind
        is AbsenceKind.FOUND
    )
    assert (
        exchange.get_receipt(mid, ReceiptKind.READ, "bob").kind
        is AbsenceKind.NOT_IN_RECORD
    )
    received = exchange.receive("bob")
    assert received.kind is AbsenceKind.FOUND
    assert received.value is not None
    assert len(received.value.messages) == 1
    assert exchange.get_receipt(mid, ReceiptKind.READ, "bob").kind is AbsenceKind.FOUND
    again = exchange.receive("bob")
    assert again.kind is AbsenceKind.EMPTY


def test_probe_reports_all_facets_on_a_live_mailbox(exchange: MailExchange) -> None:
    exchange.register_worker("alice")
    exchange.register_worker("bob")
    exchange.send("alice", "bob", {"q": True}, requires_ack=True, ack_deadline_s=3600)
    report = exchange.probe("bob")
    assert report.mailbox_state is AbsenceKind.FOUND
    assert report.facets.root_sentinel.kind is AbsenceKind.FOUND
    assert report.facets.identity.kind is AbsenceKind.FOUND
    assert report.facets.heartbeat.kind is AbsenceKind.FOUND
    assert report.facets.inbox.kind is AbsenceKind.FOUND
    assert report.facets.unread_count == 1
    assert report.facets.oldest_unacked_required.kind is AbsenceKind.FOUND
    assert report.facets.last_read_receipt.kind is AbsenceKind.NOT_IN_RECORD
    assert report.probe_worker_id == "cursor.cosmos_mail"
    assert report.tz_offset != ""


def test_required_ack_receive_clears_unanswered(exchange: MailExchange) -> None:
    exchange.register_worker("alice")
    exchange.register_worker("bob")
    exchange.send(
        "alice", "bob", {"need": "ack"}, requires_ack=True, ack_deadline_s=3600
    )
    before = exchange.probe("bob")
    assert before.facets.oldest_unacked_required.kind is AbsenceKind.FOUND
    exchange.receive("bob")
    after = exchange.probe("bob")
    assert after.mailbox_state is AbsenceKind.EMPTY
    assert after.facets.oldest_unacked_required.kind is AbsenceKind.NOT_IN_RECORD
    assert after.facets.last_read_receipt.kind is AbsenceKind.FOUND


def test_posix_inotify_wakes_on_create(exchange: MailExchange) -> None:
    exchange.register_worker("bob")
    inbox = exchange.inbox_dir("bob")
    holder: list[Outcome[object]] = []

    def watch() -> None:
        holder.append(exchange.adapter.watch_directory(inbox, 2.0))

    thread = threading.Thread(target=watch)
    thread.start()
    time.sleep(0.15)
    (inbox / "wake.json").write_text("{}", encoding="utf-8")
    thread.join(timeout=3.0)
    assert not thread.is_alive()
    assert holder
    outcome = holder[0]
    assert outcome.kind is AbsenceKind.FOUND
    events = list(outcome.value or [])
    names = [event.name for event in events]
    assert "wake.json" in names


def test_utf8_emoji_survives_round_trip(exchange: MailExchange) -> None:
    exchange.register_worker("alice")
    exchange.register_worker("bob")
    sent = exchange.send("alice", "bob", {"note": "red 🔴 not broken"})
    assert sent.kind is AbsenceKind.FOUND
    received = exchange.receive("bob")
    assert received.value is not None
    assert received.value.messages[0].payload == {"note": "red 🔴 not broken"}


def test_helper_underscore_file_is_untouched(exchange: MailExchange) -> None:
    exchange.register_worker("bob")
    helper = exchange.inbox_dir("bob") / "_helper.json"
    helper.write_text('{"not":"a-message"}', encoding="utf-8")
    listed = exchange.list_inbox("bob")
    assert listed.value is not None
    assert listed.value == []
    assert helper.is_file()


def test_get_message_found_after_send(exchange: MailExchange) -> None:
    exchange.register_worker("alice")
    exchange.register_worker("bob")
    sent = exchange.send("alice", "bob", {"x": 1})
    assert sent.value is not None
    found = exchange.get_message(sent.value.message_id)
    assert found.kind is AbsenceKind.FOUND
    assert found.value is not None
    assert found.value.payload_hash == sent.value.payload_hash


def test_exit_codes_distinguish_empty_from_found() -> None:
    assert exit_code_for(AbsenceKind.EMPTY) == 0
    assert exit_code_for(AbsenceKind.FOUND) == 0
    assert exit_code_for(AbsenceKind.NOT_FOUND) != 0
    assert exit_code_for(AbsenceKind.EMPTY) != exit_code_for(AbsenceKind.NOT_FOUND)


def test_prepare_is_explicit_not_import(tmp_path: Path) -> None:
    assert not (tmp_path / ".cosmos_mail_root").exists()
    result = prepare_surface(tmp_path)
    assert result.kind is AbsenceKind.FOUND
    assert (tmp_path / ".cosmos_mail_root").read_text(encoding="ascii") == (
        "COSMOS_MAIL_ROOT\nv1\nidentity=exchange\n"
    )
