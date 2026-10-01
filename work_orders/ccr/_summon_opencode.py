#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Summon a hero pack through the OpenCode door (agentic harness, OR provider).

Shape per harness_cheats/opencode.md + hero_unify.BIND['opencode']:
  binary opencode.cmd run --dir WORKTREE -m openrouter/<slug>
  wrapper AGENTS.md native-loaded (copy WRAP.md only if absent)
  skills SKILL.md by name; built-in tools are the pool; grade reads the tree.

Propose-only: never passes --auto. No grok.exe. No live tree.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"V:\A\Ai\COSMOS")
LOG = ROOT / "work_orders" / "ccr" / "BAKEOFF70.jsonl"
FIZZ = ["NONE"] + ["FizzBuzz" if i % 15 == 0 else "Buzz" if i % 5 == 0 else "Fizz" if i % 3 == 0 else str(i) for i in range(1, 16)]


def key() -> str:
    return (ROOT / "live" / "config" / "openrouter_api_key.txt").read_text(encoding="utf-8").strip()


def bind(pack: Path) -> dict:
    """AGENTS.md native load; WRAP.md fallback copy. Returns bind record."""
    pack.mkdir(parents=True, exist_ok=True)
    agents = pack / "AGENTS.md"
    wrap = pack / "WRAP.md"
    if not agents.is_file() and not wrap.is_file():
        raise SystemExit(f"REFUSED no pack: {pack} has neither AGENTS.md nor WRAP.md")
    copied = False
    if not agents.is_file() and wrap.is_file():
        agents.write_text(wrap.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
        copied = True
    return {"door": "opencode", "agents": agents.is_file(), "wrap_copied": copied,
            "task": (pack / "TASK.md").is_file()}


def clean(text: str) -> list[str]:
    lines = []
    for raw in text.splitlines():
        t = raw.strip()
        if not t:
            continue
        if t.startswith("> ") and "·" in t:
            continue
        lines.append(t)
    return lines


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", required=True)
    ap.add_argument("--model", required=True, help="full OR slug, e.g. thinkingmachines/inkling:free")
    ap.add_argument("--out", required=True)
    ap.add_argument("--task", default="ping", choices=["ping", "fizz"])
    ap.add_argument("--timeout", type=int, default=150)
    a = ap.parse_args()
    pack = Path(a.pack)
    rec = bind(pack)
    slug = a.model
    short = slug.split("/")[-1]
    if a.task == "ping":
        msg = f"Reply with exactly two lines and nothing else: NONE on line 1, HERO_OK {short} on line 2."
        want = ["NONE", f"HERO_OK {short}"]
    else:
        msg = ("Print FizzBuzz for the numbers 1 to 15, one result per line: print Fizz for multiples of 3, "
               "Buzz for multiples of 5, FizzBuzz for multiples of both, else the number itself. "
               "First line of your reply must be NONE, then the 15 result lines, nothing else.")
        want = FIZZ
    env = dict(os.environ)
    env["OPENROUTER_API_KEY"] = key()
    cmd = ["opencode.cmd", "run", "--dir", str(pack), "-m", f"openrouter/{slug}", msg]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=a.timeout, env=env, cwd=str(ROOT))
        lines = clean(p.stdout)
        ok_call = p.returncode == 0
        err = "" if ok_call else (p.stderr.strip().splitlines() or ["rc!=0"])[0][:120]
    except subprocess.TimeoutExpired:
        lines, ok_call, err = [], False, "TIMEOUT"
    got = lines == want
    grade = "ACTIVE" if (ok_call and got) else ("HTTP" if not ok_call else "MOUTH")
    first = lines[0][:80] if lines else err
    Path(a.out).write_text("\n".join(lines) + ("\n" if lines else err), encoding="utf-8", newline="\n")
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"set": "DOOR2", "seat": short, "model": slug, "try": a.task,
                             "label": "opencode-door", "args": ["opencode", f"openrouter/{slug}"],
                             "rc": 0 if ok_call else 1, "served": slug if ok_call else "",
                             "first_line": first, "sku_bound": ok_call,
                             "grade": grade, "scar": "" if grade == "ACTIVE" else first}) + "\n")
    print(json.dumps({"ok": ok_call, "model": slug if ok_call else "", "first_line": first,
                      "out": a.out, "bind": rec, "grade": grade}))
    return 0 if grade == "ACTIVE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
