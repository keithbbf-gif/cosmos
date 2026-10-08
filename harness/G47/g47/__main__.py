"""python -m g47 plan|grade|doctor

plan writes JSON to stdout and does not start a model.
"""

from __future__ import annotations

import argparse
import json
import sys

from g47.contracts import Legend, OutputContract
from g47.doctor import report
from g47.grade import grade
from g47.locate import write_local
from g47.refuse import Refuse
from g47.seat import seat
from g47.summon import plan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="g47")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("plan")
    p.add_argument("--door", required=True)
    p.add_argument("--role", required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--what", default="text", choices=("text", "python", "no_prose"))
    p.add_argument("--task", default="")
    p.add_argument("--wrap", default="")
    p.add_argument("--style", default="")
    p.add_argument("--where", default="")
    p.add_argument("--window", type=int)
    p.add_argument("--optimum", default="float")
    p.add_argument("--ping", action="store_true")
    p.add_argument("--write", action="store_true")
    p.add_argument("--context", action="append", default=[])

    g = sub.add_parser("grade")
    g.add_argument("--role", required=True)
    g.add_argument("--what", default="text")
    g.add_argument("--ping", action="store_true")
    g.add_argument("--door-grade", default="filed_text", choices=("filed_text", "worktree"))
    g.add_argument("--worktree-obeyed", action="store_true")
    g.add_argument("--mouth", required=True)

    sub.add_parser("doctor")
    sub.add_parser("locate")

    s = sub.add_parser("seat")
    s.add_argument("--agent", required=True)
    s.add_argument("--via", required=True, choices=("native", "cosmos-code"))
    s.add_argument("--task", required=True)
    s.add_argument("--where", required=True)
    s.add_argument("--wrap", default="")
    s.add_argument("--style", default="")

    args = parser.parse_args(argv)

    if args.cmd == "seat":
        built = seat(args.agent, via=args.via, task=args.task, where=args.where, wrap=args.wrap, style=args.style)
        json.dump(built.to_public(), sys.stdout, indent=1)
        sys.stdout.write("\n")
        return 0
    if args.cmd == "doctor":
        try:
            rows = report()
        except Refuse as exc:
            print(f"{exc.reason}: {exc.detail}", file=sys.stderr)
            return 2
        json.dump(rows, sys.stdout, indent=1)
        sys.stdout.write("\n")
        return 0
    if args.cmd == "locate":
        try:
            dest = write_local()
        except Refuse as exc:
            print(f"{exc.reason}: {exc.detail}", file=sys.stderr)
            return 2
        sys.stdout.write(str(dest) + "\n")
        return 0
    if args.cmd == "grade":
        text = args.mouth if args.mouth != "-" else sys.stdin.read()
        result = grade(
            text,
            OutputContract(args.role, args.what, args.ping),
            door_grade=args.door_grade,
            worktree_obeyed=True if args.worktree_obeyed else None,
        )
        json.dump({
            "mouth_ok": result.mouth_ok,
            "applied": result.applied,
            "reason": result.reason,
            "task_pass": result.task_pass,
        }, sys.stdout)
        sys.stdout.write("\n")
        return 0 if result.mouth_ok else 2

    optimum: int | str
    optimum = int(args.optimum) if args.optimum.isdigit() else args.optimum
    legend = Legend(
        role=args.role,
        model=args.model,
        what=args.what,
        ping=args.ping,
        wrap=args.wrap,
        style=args.style,
        task=args.task,
        context=tuple(args.context),
        where=args.where,
        optimum=optimum,
        window=args.window,
    )
    planned = plan(legend, args.door, write=args.write)
    sys.stdout.write(planned.to_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
