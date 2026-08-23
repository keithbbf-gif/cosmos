"""CLI. Unknown flags refuse with exit 2 — never swallow a typo."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from cosmos.spikes.cosmos_sched.absence import Absence
from cosmos.spikes.cosmos_sched.scheduler import Scheduler
from cosmos.spikes.cosmos_sched.stamp import WorkerIdentity


class RefuseParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        print(f"REFUSED unknown or invalid arguments: {message}", file=sys.stderr)
        raise SystemExit(2)


def build_parser() -> RefuseParser:
    parser = RefuseParser(prog="cosmos_sched")
    parser.add_argument("--root", required=True, help="scheduler root directory")
    parser.add_argument("--worker", default=None, help="worker id")
    parser.add_argument("--lane", default=None, help="lane name")
    parser.add_argument("--status", action="store_true", help="probe lanes and print helper skips")
    parser.add_argument("--drain", action="store_true", help="admit and run pending work")
    parser.add_argument("--probe-job", default=None, metavar="JOB_ID")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    identity = WorkerIdentity.mint(args.worker)
    sched = Scheduler(Path(args.root), identity)
    if args.status:
        result = sched.status(args.lane)
        print(f"{result.kind.value}: {result.detail}")
        return 0 if result.kind is Absence.FOUND else 2
    if args.probe_job:
        result = sched.probe_job(args.probe_job)
        print(f"{result.kind.value}: {result.detail}")
        if result.kind is Absence.NOT_FOUND:
            return 2
        if result.kind in (Absence.UNREADABLE, Absence.UNPARSEABLE, Absence.OUT_OF_CLOCK, Absence.NOT_IN_RECORD):
            return 2
        return 0
    if args.drain:
        results = sched.drain(args.lane)
        print(f"drained={len(results)}")
        return 0
    print("REFUSED: no action (--status | --drain | --probe-job)", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
