"""cosmos-mail CLI. Unknown flags exit 2 (refuse, do not swallow)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from cosmos.spikes.cosmos_mail.demo import run_demo
from cosmos.spikes.cosmos_mail.mail import MailExchange, prepare_surface
from cosmos.spikes.cosmos_mail.types import EXIT_FINDINGS, AbsenceKind, exit_code_for


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cosmos-mail",
        description="COSMOS mailbox spike: per-worker IPC at N>2",
    )
    parser.add_argument(
        "--root", help="explicit mail exchange root (no import-time default)"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("prepare", help="create sentinel-verified exchange root")

    register = sub.add_parser("register", help="register a worker inbox")
    register.add_argument("--worker", required=True)

    heartbeat = sub.add_parser("heartbeat", help="refresh a worker heartbeat")
    heartbeat.add_argument("--worker", required=True)

    probe = sub.add_parser("probe", help="probe mailbox typed state")
    probe.add_argument("--worker", required=True)

    send = sub.add_parser("send", help="send an immutable message")
    send.add_argument("--from-worker", required=True)
    send.add_argument("--to-worker", required=True)
    send.add_argument("--payload", required=True, help="JSON payload or raw string")
    send.add_argument("--subject", default="")
    send.add_argument("--requires-ack", action="store_true")
    send.add_argument("--ack-deadline-s", type=float, default=None)

    receive = sub.add_parser(
        "receive", help="receive unread messages and write read receipts"
    )
    receive.add_argument("--worker", required=True)

    sub.add_parser("demo", help="print MEASURED numbers for the spike")
    sub.add_parser(
        "selftest", help="run the pytest selftest (positive and negative controls)"
    )
    return parser


def _exchange(root: str | None) -> MailExchange | int:
    if not root:
        print(
            "REFUSED: --root is required (no guessed default, no cwd write)",
            file=sys.stderr,
        )
        return EXIT_FINDINGS
    return MailExchange(Path(root))


def _payload_from_arg(raw: str) -> object:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        code = exc.code
        if code is None:
            return 0
        if isinstance(code, int):
            return code
        return EXIT_FINDINGS

    if args.cmd == "selftest":
        return _selftest()
    if args.cmd == "demo":
        return run_demo(Path(args.root) if args.root else None)

    opened = _exchange(args.root)
    if isinstance(opened, int):
        return opened

    if args.cmd == "prepare":
        prepared = prepare_surface(opened.root)
        print(f"PREPARE kind={prepared.kind.value} detail={prepared.detail}")
        return exit_code_for(prepared.kind)

    if args.cmd == "register":
        registered = opened.register_worker(args.worker)
        print(f"REGISTER kind={registered.kind.value} detail={registered.detail}")
        return exit_code_for(registered.kind)

    if args.cmd == "heartbeat":
        beat = opened.touch_heartbeat(args.worker)
        print(f"HEARTBEAT kind={beat.kind.value} detail={beat.detail}")
        return exit_code_for(beat.kind)

    if args.cmd == "probe":
        report = opened.probe(args.worker)
        print(json.dumps(report.to_record(), indent=2, ensure_ascii=False))
        print(f"MAILBOX_STATE={report.mailbox_state.value}")
        print(f"MEASURED probe_exit={report.exit_code}")
        return report.exit_code

    if args.cmd == "send":
        sent = opened.send(
            args.from_worker,
            args.to_worker,
            _payload_from_arg(args.payload),
            subject=args.subject,
            requires_ack=args.requires_ack,
            ack_deadline_s=args.ack_deadline_s,
        )
        print(f"SEND kind={sent.kind.value} detail={sent.detail}")
        if sent.kind is AbsenceKind.FOUND and sent.value is not None:
            print(f"MEASURED message_id={sent.value.message_id}")
            print(f"MEASURED payload_hash={sent.value.payload_hash}")
        return exit_code_for(sent.kind)

    if args.cmd == "receive":
        received = opened.receive(args.worker)
        print(f"RECEIVE kind={received.kind.value} detail={received.detail}")
        if received.value is not None:
            print(
                f"MEASURED received={len(received.value.messages)} defects={len(received.value.defects)}"
            )
        return exit_code_for(received.kind)

    print("REFUSED: unknown command", file=sys.stderr)
    return EXIT_FINDINGS


def _selftest() -> int:
    import pytest

    test_dir = Path(__file__).resolve().parent / "tests"
    return int(pytest.main(["-v", str(test_dir)]))
