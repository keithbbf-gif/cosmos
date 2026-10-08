"""COSMOS CODE CLI — doctor / enclosure / scars."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from cosmos_code import __version__
from cosmos_code.safety.enclosure import detect_enclosure, refuse_unsandboxed_retry
from cosmos_code.safety.hooks import HookBus, install_defaults
from cosmos_code.safety.scars import detect_scar


def cmd_doctor() -> int:
    bus = install_defaults(HookBus())
    d_rm = bus.pre("shell", {"command": "rm -rf precious"})
    d_fmt = bus.pre("shell", {"command": "format C:"})
    print(f"cosmos-code {__version__}")
    print(f"delete hook: deny={d_rm.deny} rewrite={d_rm.rewrite_tool}")
    print(f"format hook: deny={d_fmt.deny} reason={d_fmt.reason}")
    enc = detect_enclosure()
    print(f"enclosure: {enc.reason} wipe_proof={enc.wipe_proof}")
    print("doctor: ok")
    return 0


def cmd_enclosure() -> int:
    enc = detect_enclosure()
    print(
        json.dumps(
            {
                "kind": enc.kind,
                "available": enc.available,
                "intended": enc.intended,
                "reason": enc.reason,
                "wipe_proof": enc.wipe_proof,
                "label": enc.label(),
            },
            indent=2,
        )
    )
    return 0


def cmd_scars(arg: str) -> int:
    hit = detect_scar(arg)
    if hit:
        print(f"SCAR {hit.name}")
        return 0
    print("clean")
    return 0


def cmd_refuse_retry() -> int:
    try:
        refuse_unsandboxed_retry()
    except Exception as e:
        print(type(e).__name__, str(e))
        return 0
    print("ERROR: refuse_unsandboxed_retry did not raise")
    return 1


def cmd_check(root: str) -> int:
    from cosmos_code.checks4 import check_package, package_blocked

    rows = check_package(Path(root))
    print(json.dumps(rows, indent=1))
    reason = package_blocked(rows)
    if reason:
        print(reason, file=sys.stderr)
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"):
        print("COSMOS CODE — propose-only worker (WOMBAT default)")
        print("usage: python -m cosmos_code [doctor|enclosure|scars <text>|refuse-retry|check <tree>]")
        return 0
    if argv[0] == "check":
        if len(argv) < 2:
            print("check needs a tree", file=sys.stderr)
            return 2
        return cmd_check(argv[1])
    cmd = argv[0]
    if cmd == "doctor":
        return cmd_doctor()
    if cmd == "enclosure":
        return cmd_enclosure()
    if cmd == "scars":
        return cmd_scars(argv[1] if len(argv) > 1 else "")
    if cmd == "refuse-retry":
        return cmd_refuse_retry()
    print(f"unknown command: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
