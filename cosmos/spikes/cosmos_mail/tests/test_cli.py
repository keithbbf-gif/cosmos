"""CLI: refuse unknown flags (exit 2); dead-phone probe is non-zero."""

from __future__ import annotations

from pathlib import Path

from cosmos.spikes.cosmos_mail.cli import main
from cosmos.spikes.cosmos_mail.mail import MailExchange, prepare_surface
from cosmos.spikes.cosmos_mail.types import EXIT_DEAD_PHONE, EXIT_FINDINGS


def test_unknown_flag_exits_2() -> None:
    assert main(["--typo"]) == EXIT_FINDINGS


def test_unknown_flag_after_command_exits_2(tmp_path: Path) -> None:
    assert (
        main(["--root", str(tmp_path), "probe", "--worker", "bob", "--weird"])
        == EXIT_FINDINGS
    )


def test_probe_without_root_refuses() -> None:
    assert main(["probe", "--worker", "bob"]) == EXIT_FINDINGS


def test_probe_missing_mailbox_nonzero(tmp_path: Path) -> None:
    assert prepare_surface(tmp_path).kind.value == "FOUND"
    assert (
        main(["--root", str(tmp_path), "probe", "--worker", "zoe"]) == EXIT_DEAD_PHONE
    )


def test_probe_empty_mailbox_zero(tmp_path: Path) -> None:
    assert prepare_surface(tmp_path).kind.value == "FOUND"
    assert main(["--root", str(tmp_path), "register", "--worker", "bob"]) == 0
    assert main(["--root", str(tmp_path), "probe", "--worker", "bob"]) == 0


def test_send_receive_cli_round_trip(tmp_path: Path) -> None:
    assert main(["--root", str(tmp_path), "prepare"]) == 0
    assert main(["--root", str(tmp_path), "register", "--worker", "alice"]) == 0
    assert main(["--root", str(tmp_path), "register", "--worker", "bob"]) == 0
    assert (
        main(
            [
                "--root",
                str(tmp_path),
                "send",
                "--from-worker",
                "alice",
                "--to-worker",
                "bob",
                "--payload",
                '{"ok":true}',
            ]
        )
        == 0
    )
    exchange = MailExchange(tmp_path)
    listed = exchange.list_inbox("bob")
    assert listed.value is not None
    assert len(listed.value) == 1
    assert main(["--root", str(tmp_path), "receive", "--worker", "bob"]) == 0
    assert main(["--root", str(tmp_path), "probe", "--worker", "bob"]) == 0
