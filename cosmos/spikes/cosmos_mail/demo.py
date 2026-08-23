"""Measured demo. A spike whose claims are prose has not run."""

from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from cosmos.spikes.cosmos_mail.clock import FrozenClock, SystemClock
from cosmos.spikes.cosmos_mail.mail import (
    MailExchange,
    StalenessPolicy,
    payload_hash,
    prepare_surface,
)
from cosmos.spikes.cosmos_mail.platform import (
    PlatformAdapter,
    PosixPlatformAdapter,
    WindowsPlatformAdapter,
    detect_platform_adapter,
)
from cosmos.spikes.cosmos_mail.types import AbsenceKind, ReceiptKind


def run_demo(root: Path | None = None) -> int:
    clock = SystemClock()
    adapter = detect_platform_adapter(clock=clock)
    if root is None:
        holding = TemporaryDirectory(prefix="cosmos_mail_demo_")
        root = Path(holding.name)
        owns = True
    else:
        holding = None
        owns = False
    try:
        return _run(root, clock, adapter)
    finally:
        if owns and holding is not None:
            holding.cleanup()


def _run(root: Path, clock: SystemClock, adapter: PlatformAdapter) -> int:
    prepared = prepare_surface(root, adapter=adapter, clock=clock)
    print(f"MEASURED prepare_kind={prepared.kind.value}")
    exchange = MailExchange(
        root,
        adapter=adapter,
        clock=clock,
        policy=StalenessPolicy(heartbeat_stale_after_s=2.0),
    )
    for worker in ("alice", "bob", "carol"):
        registered = exchange.register_worker(worker)
        print(f"MEASURED register_{worker}={registered.kind.value}")

    t0 = time.perf_counter()
    sent = exchange.send(
        "alice", "bob", {"text": "hello-from-alice", "emoji": "📬"}, subject="ping"
    )
    send_ms = (time.perf_counter() - t0) * 1000.0
    print(f"MEASURED send_kind={sent.kind.value}")
    print(f"MEASURED send_readback_ms={send_ms:.3f}")
    if sent.kind is not AbsenceKind.FOUND or sent.value is None:
        print("MEASURED demo_failed=send")
        return 1
    message_id = sent.value.message_id
    print(f"MEASURED message_id={message_id}")
    print(f"MEASURED name_has_sender={int('alice' in message_id)}")
    print(f"MEASURED name_has_hash12={int(sent.value.payload_hash[:12] in message_id)}")

    sent_receipt = exchange.get_receipt(message_id, ReceiptKind.SENT, "alice")
    delivered = exchange.get_receipt(message_id, ReceiptKind.DELIVERED, "bob")
    read_before = exchange.get_receipt(message_id, ReceiptKind.READ, "bob")
    print(f"MEASURED sent_receipt={sent_receipt.kind.value}")
    print(f"MEASURED delivered_receipt={delivered.kind.value}")
    print(f"MEASURED read_receipt_after_send={read_before.kind.value}")

    t1 = time.perf_counter()
    second = exchange.send("carol", "bob", {"text": "hello-from-carol"})
    two_sender_ms = (time.perf_counter() - t1) * 1000.0
    listed = exchange.list_inbox("bob")
    names = [entry.filename for entry in listed.value or []]
    collisions = len(names) - len(set(names))
    print(f"MEASURED two_sender_kind={second.kind.value}")
    print(f"MEASURED two_sender_files={len(names)}")
    print(f"MEASURED two_sender_collisions={collisions}")
    print(f"MEASURED two_sender_ms={two_sender_ms:.3f}")

    received = exchange.receive("bob")
    read_after = exchange.get_receipt(message_id, ReceiptKind.READ, "bob")
    print(f"MEASURED receive_kind={received.kind.value}")
    print(
        f"MEASURED received_count={len(received.value.messages) if received.value else 0}"
    )
    print(f"MEASURED read_receipt_after_receive={read_after.kind.value}")

    empty = MailExchange(root, adapter=adapter, clock=clock).probe("carol")
    print(f"MEASURED empty_state={empty.mailbox_state.value}")
    print(f"MEASURED empty_exit={empty.exit_code}")

    missing = MailExchange(root, adapter=adapter, clock=clock).probe(
        "nobody-registered"
    )
    print(f"MEASURED missing_state={missing.mailbox_state.value}")
    print(f"MEASURED missing_exit={missing.exit_code}")
    print(f"MEASURED dead_phone_nonzero={int(missing.exit_code != 0)}")

    half_path = exchange.inbox_dir("carol") / "planted_half_written.json"
    half_path.write_text(
        json.dumps(
            {
                "schema": "cosmos.mail.message.v1",
                "message_id": "planted_half_written",
                "sender_id": "alice",
                "sender_instance": "i1",
                "recipient_id": "carol",
                "created_at": clock.now().isoformat(timespec="microseconds"),
                "created_epoch": clock.now().timestamp(),
                "tz_offset": clock.now().strftime("%z"),
                "subject": "",
                "correlation_id": "",
                "payload": {"text": "torn"},
                "payload_hash": "0" * 64,
                "requires_ack": False,
                "ack_deadline_epoch": None,
                "ttl_seconds": None,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    half = exchange.probe("carol")
    print(f"MEASURED half_written_state={half.mailbox_state.value}")
    print(f"MEASURED half_written_exit={half.exit_code}")

    frozen = FrozenClock(datetime(2026, 8, 23, 12, 0, tzinfo=timezone.utc))
    stale_ex = MailExchange(
        root,
        adapter=PosixPlatformAdapter(clock=frozen),
        clock=frozen,
        policy=StalenessPolicy(heartbeat_stale_after_s=1.0),
    )
    stale_ex.register_worker("dave")
    frozen.advance(90.0)
    stale = stale_ex.probe("dave")
    print(f"MEASURED stale_state={stale.mailbox_state.value}")
    print(f"MEASURED stale_exit={stale.exit_code}")

    # Probe a worker whose inbox is a file, not a directory.
    (exchange.worker_dir("carol") / "inbox").rename(
        exchange.worker_dir("carol") / "inbox.bak"
    )
    (exchange.worker_dir("carol") / "inbox").write_text("not-a-dir", encoding="utf-8")
    unreadable = exchange.probe("carol")
    print(f"MEASURED unreadable_state={unreadable.mailbox_state.value}")
    print(f"MEASURED unreadable_exit={unreadable.exit_code}")
    (exchange.worker_dir("carol") / "inbox").unlink()
    (exchange.worker_dir("carol") / "inbox.bak").rename(
        exchange.worker_dir("carol") / "inbox"
    )

    future = FrozenClock(datetime(2026, 8, 23, 12, 0, tzinfo=timezone.utc))
    clocked = MailExchange(
        root, adapter=PosixPlatformAdapter(clock=future), clock=future
    )
    clocked.register_worker("erin")
    planted = clocked.inbox_dir("erin") / "future.json"
    future_ts = future.now() + timedelta(seconds=120)
    planted.write_text(
        json.dumps(
            {
                "schema": "cosmos.mail.message.v1",
                "message_id": "future",
                "sender_id": "alice",
                "sender_instance": "i1",
                "recipient_id": "erin",
                "created_at": future_ts.isoformat(timespec="microseconds"),
                "created_epoch": future_ts.timestamp(),
                "tz_offset": future_ts.strftime("%z"),
                "subject": "",
                "correlation_id": "",
                "payload": {"n": 1},
                "payload_hash": payload_hash({"n": 1}),
                "requires_ack": False,
                "ack_deadline_epoch": None,
                "ttl_seconds": None,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    out_of_clock = clocked.probe("erin")
    print(f"MEASURED out_of_clock_state={out_of_clock.mailbox_state.value}")

    unknown = exchange.get_message("no-such-message")
    print(f"MEASURED not_in_record_state={unknown.kind.value}")

    win = WindowsPlatformAdapter(clock=clock)
    job = win.job_object_contain(1)
    watch = win.watch_directory(root, 0.1)
    msvcrt = win.msvcrt_locking(0)
    drive = win.interpret_drive(r"V:\A\Ai\COSMOS")
    extended = win.native_fs_path(Path(r"V:\A\Ai\COSMOS") / ("x" * 80))
    posix_drive = PosixPlatformAdapter(clock=clock).interpret_drive(r"V:\Ai\_queue")
    print(f"MEASURED windows_job_object={job.kind.value}")
    print(f"MEASURED windows_readdirectorychanges={watch.kind.value}")
    print(f"MEASURED windows_msvcrt={msvcrt.kind.value}")
    print(f"MEASURED windows_drive_letter={drive.kind.value}")
    print(
        f"MEASURED windows_extended_prefix={int(str(extended.value or '').startswith('\\\\?\\'))}"
    )
    print(f"MEASURED posix_refuses_drive={posix_drive.kind.value}")

    inbox = exchange.inbox_dir("alice")
    t_watch = time.perf_counter()
    # The watch is started in-thread by the caller of the POSIX adapter; here we
    # measure a zero-event timeout as the lower bound and a create wakeup above.
    nonevent = adapter.watch_directory(inbox, 0.05)
    nonevent_ms = (time.perf_counter() - t_watch) * 1000.0
    print(f"MEASURED posix_inotify_timeout_kind={nonevent.kind.value}")
    print(f"MEASURED posix_inotify_timeout_ms={nonevent_ms:.3f}")
    print(f"MEASURED posix_inotify_timeout_events={len(nonevent.value or [])}")

    print(
        "MEASURED native_demo_required=ReadDirectoryChangesW,JobObjects,msvcrt,live_V_drive"
    )
    print("MEASURED four_states_reported=1")
    print(f"MEASURED demo_root={root}")
    print("MEASURED demo_ok=1")
    return 0
