#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Summon a hero pack through the Copilot CLI door (GitHub agentic harness).

copilot.cmd -p "<prompt>" (non-interactive) in the pack worktree.
AGENTS.md auto-loads. Propose-only: no --auto-tier changes, no live tree.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(r"V:\A\Ai\COSMOS")
LOG = ROOT / "work_orders" / "ccr" / "BAKEOFF70.jsonl"
FIZZ = ["NONE"] + ["FizzBuzz" if i % 15 == 0 else "Buzz" if i % 5 == 0 else "Fizz" if i % 3 == 0 else str(i) for i in range(1, 16)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", required=True)
    ap.add_argument("--model", default="auto")
    ap.add_argument("--out", required=True)
    ap.add_argument("--task", default="ping", choices=["ping", "fizz"])
    ap.add_argument("--timeout", type=int, default=180)
    a = ap.parse_args()
    pack = Path(a.pack)
    pack.mkdir(parents=True, exist_ok=True)
    if a.task == "ping":
        msg = "Reply with exactly two lines and nothing else: NONE on line 1, HERO_OK copilot-seat on line 2."
        want = ["NONE", "HERO_OK copilot-seat"]
    else:
        msg = ("Print FizzBuzz for 1 to 15, one result per line: multiples of 3 print Fizz, "
               "of 5 print Buzz, of both print FizzBuzz, else the number. "
               "First line of your reply must be NONE, then the 15 result lines, nothing else.")
        want = FIZZ
    cmd = ["copilot.cmd", "-p", msg, "-s", "--allow-all-tools"]
    if a.model != "auto":
        cmd += ["--model", a.model]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=a.timeout, cwd=str(pack))
        lines = [t for t in p.stdout.splitlines() if t.strip()]
        ok_call = p.returncode == 0 and bool(lines)
        err = "" if ok_call else ((p.stderr.strip().splitlines() or ["rc!=0"])[0][:120])
    except subprocess.TimeoutExpired:
        lines, ok_call, err = [], False, "TIMEOUT"
    got = lines == want
    grade = "ACTIVE" if (ok_call and got) else ("HTTP" if not ok_call else "MOUTH")
    first = lines[0][:80] if lines else err
    Path(a.out).write_text("\n".join(lines) + ("\n" if lines else err), encoding="utf-8", newline="\n")
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"set": "COPILOT", "seat": f"copilot-{a.model}", "model": f"copilot/{a.model}",
                             "try": a.task, "label": "copilot-door", "args": ["copilot", a.model],
                             "rc": 0 if ok_call else 1, "served": a.model,
                             "first_line": first, "sku_bound": ok_call,
                             "grade": grade, "scar": "" if grade == "ACTIVE" else first}) + "\n")
    print(json.dumps({"ok": ok_call, "model": a.model, "first_line": first, "grade": grade}))
    return 0 if grade == "ACTIVE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
