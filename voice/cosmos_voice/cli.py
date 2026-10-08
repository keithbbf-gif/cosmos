"""Command line for the COSMOS voice client.

``doctor`` prints the plugin manifest and does not build a client.
The bearer is never written to stdout or stderr.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from cosmos_voice.doors import CoreMouth
from cosmos_voice.errors import VoiceError
from cosmos_voice.plugin import manifest
from cosmos_voice.road import RoadQueue
from cosmos_voice.session import VoiceSession
from cosmos_voice.transport import CoreClient


def main(argv: list[str] | None = None, client: CoreClient | None = None) -> int:
    """Run one subcommand. Return 0 on a dict result and 2 on ``VoiceError``."""
    parser = _parser()
    args = parser.parse_args(argv)
    command = args.command
    if command == "doctor":
        return _doctor()
    if command == "say":
        return _say(args, client)
    if command == "status":
        return _status(args, client)
    if command == "kill":
        return _kill(args, client)
    if command == "queue":
        return _queue(args)
    print("unknown command", file=sys.stderr)
    return 2


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cosmos-voice")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor", help="print the plugin manifest as JSON")

    say = sub.add_parser("say", help="speak one transcript through Core")
    _add_http(say, base_required=False)
    say.add_argument("--transcript", required=True)
    say.add_argument("--client-id", default="cosmos-voice")
    say.add_argument("--mode", default="ptt")

    status = sub.add_parser("status", help="read Core status")
    _add_http(status, base_required=True)

    kill = sub.add_parser("kill", help="turn the mic off for one client")
    _add_http(kill, base_required=True)
    kill.add_argument("--client-id", required=True)

    queue = sub.add_parser("queue", help="print the pending road count")
    queue.add_argument("--root", required=True)
    return parser


def _add_http(parser: argparse.ArgumentParser, *, base_required: bool) -> None:
    parser.add_argument("--base", default="", required=base_required)
    parser.add_argument("--bearer", default="")
    parser.add_argument("--allow-http-bearer", action="store_true")


def _doctor() -> int:
    print(json.dumps(manifest(), indent=2, sort_keys=True))
    return 0


def _say(args: argparse.Namespace, client: CoreClient | None) -> int:
    active, code = _client_from(args, client)
    if active is None:
        return code
    client_id = _text(args.client_id, "cosmos-voice")
    mode = _text(args.mode, "ptt")
    transcript = _text(args.transcript, "")
    session = VoiceSession(client_id=client_id)
    mouth = CoreMouth(active)
    try:
        result = mouth.speak_turn(transcript, session, mode=mode)
    except VoiceError as exc:
        _refuse(exc)
        return 2
    if not isinstance(result, dict):
        return 2
    _print_spoken(result)
    return 0


def _status(args: argparse.Namespace, client: CoreClient | None) -> int:
    active, code = _client_from(args, client)
    if active is None:
        return code
    try:
        result = active.get_status()
    except VoiceError as exc:
        _refuse(exc)
        return 2
    if not isinstance(result, dict):
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


def _kill(args: argparse.Namespace, client: CoreClient | None) -> int:
    active, code = _client_from(args, client)
    if active is None:
        return code
    client_id = _text(args.client_id, "")
    if client_id == "":
        print("kill requires --client-id", file=sys.stderr)
        return 2
    try:
        result = active.post_kill(client_id)
    except VoiceError as exc:
        _refuse(exc)
        return 2
    if not isinstance(result, dict):
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


def _queue(args: argparse.Namespace) -> int:
    root = _text(args.root, "")
    if root == "":
        print("queue requires --root", file=sys.stderr)
        return 2
    try:
        pending = RoadQueue(Path(root)).list_pending()
    except VoiceError as exc:
        _refuse(exc)
        return 2
    print(len(pending))
    return 0


def _client_from(
    args: argparse.Namespace,
    client: CoreClient | None,
) -> tuple[CoreClient | None, int]:
    if client is not None:
        return client, 0
    base = _text(args.base, "")
    if base == "":
        print("base URL is required", file=sys.stderr)
        return None, 2
    try:
        built = CoreClient(
            base,
            bearer=_text(args.bearer, ""),
            allow_bearer_over_http=bool(args.allow_http_bearer),
        )
    except VoiceError as exc:
        _refuse(exc)
        return None, 2
    return built, 0


def _print_spoken(result: dict[str, object]) -> None:
    spoken = result.get("spoken")
    if isinstance(spoken, str):
        print(spoken)
        return
    reply = result.get("reply")
    print(reply if isinstance(reply, str) else "")


def _refuse(exc: VoiceError) -> None:
    # Kind only. A detail may repeat the bearer or the base URL.
    print(exc.kind)


def _text(value: object, default: str) -> str:
    if isinstance(value, str):
        return value
    return default


if __name__ == "__main__":
    raise SystemExit(main())
