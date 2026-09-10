#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Poll Kelly elegant farm. Print only DONE/FAILED. Sidecar log for traces."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(r"V:\A\Ai\COSMOS")
sys.path.insert(0, str(ROOT / "cosmos"))
from cosmos_clock import pid_alive  # noqa: E402

OUT = ROOT / "work_orders" / "ccr" / "CREW" / "OUT" / "ELEGANT"
WATCH = OUT / "_watch.json"
SIDECAR = OUT / "_watch_poll.log"
SEATS = ("gf38", "gemini31pro")


def _log(msg: str) -> None:
    SIDECAR.parent.mkdir(parents=True, exist_ok=True)
    with SIDECAR.open("a", encoding="utf-8") as fh:
        fh.write(msg.rstrip() + "\n")


def _load(p: Path):
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _pid_map() -> dict:
    rec = _load(WATCH) or {}
    out = {}
    for row in rec.get("launched") or []:
        if isinstance(row, dict) and row.get("seat"):
            out[str(row["seat"])] = int(row.get("pid") or 0)
    return out


def _seat_state(seat: str, pid: int) -> str:
    rec = _load(OUT / f"{seat}.json")
    if isinstance(rec, dict):
        text = rec.get("text") or ""
        if rec.get("ok") and len(text) >= 200:
            return "ok"
        if rec.get("ok") is False or rec.get("reason") in (
            "EMPTY", "NO_CODING_SPEC", "UNREACHABLE",
        ) or str(rec.get("reason") or "").startswith("HTTP_"):
            return "fail"
        if rec.get("ok") and len(text) < 200:
            return "empty"
    if pid and pid_alive(pid):
        return "run"
    return "dead"


def main() -> int:
    while True:
        pids = _pid_map()
        states = {s: _seat_state(s, pids.get(s, 0)) for s in SEATS}
        _log(" ".join(f"{k}={v}" for k, v in states.items()))
        fails = [s for s, st in states.items() if st in ("fail", "empty", "dead")]
        oks = [s for s, st in states.items() if st == "ok"]
        if len(oks) == len(SEATS):
            print("DONE")
            return 0
        if fails and all(st != "run" for st in states.values()):
            print("FAILED: " + ",".join(f"{s}={states[s]}" for s in SEATS))
            return 1
        time.sleep(30)


if __name__ == "__main__":
    raise SystemExit(main())
