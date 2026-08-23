"""CLI for the cosmos_paths spike.

Unknown flags are refused with exit 2. COSMOS_ROOT is never consulted.
No filesystem work happens until instantiate or plant is explicitly asked.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .absence import TypedRefusal
from .plant import plant_installation
from .resolver import RootResolver
from .stamp import now_stamp


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cosmos_paths",
        description="COSMOS explicit-instantiation path resolver (spike).",
    )
    parser.add_argument(
        "--record",
        help="absolute path to the machine-local installation record (required; never guessed)",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="print the verified role map after instantiate",
    )
    parser.add_argument(
        "--plant",
        metavar="ROOT",
        help="plant a scratch install at ROOT and write --record (explicit demo helper)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    parser = _parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        code = exc.code
        if code is None:
            return 2
        return code if isinstance(code, int) else 2

    if args.plant:
        if not args.record:
            print("REFUSED: --plant requires --record; nothing is guessed", file=sys.stderr)
            return 2
        try:
            planted = plant_installation(Path(args.plant), Path(args.record))
        except TypedRefusal as exc:
            print(f"{exc.kind.value}: {exc.detail}", file=sys.stderr)
            return 1
        print(
            json.dumps(
                {
                    "planted": True,
                    "root": str(planted.root),
                    "record": str(planted.record_path),
                    "installation_id": planted.installation_id,
                    "sentinel_digest": planted.sentinel_digest,
                    **planted.stamp.as_dict(),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    if not args.record:
        print("REFUSED: --record is required; COSMOS_ROOT is not consulted", file=sys.stderr)
        return 2

    try:
        resolver = RootResolver.instantiate(Path(args.record))
    except TypedRefusal as exc:
        print(f"{exc.kind.value}: {exc.detail}", file=sys.stderr)
        return 1
    except ValueError:
        print("REFUSED: --record must be an absolute path", file=sys.stderr)
        return 2

    payload = resolver.report() if args.report else {
        "ready": resolver.ready,
        "installation_id": resolver.installation_id,
        "configured_root": str(resolver.root()),
        **now_stamp().as_dict(),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0
