#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fire Kelly Vertex dual-lane elegant plan. pythonw. Not grok.exe. Not OR."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(r"V:\A\Ai\COSMOS")
sys.path.insert(0, str(ROOT / "cosmos"))
from cosmos_clock import pythonw_exe, spawn_detached  # noqa: E402

OUT = ROOT / "work_orders" / "ccr" / "CREW" / "OUT" / "ELEGANT"
SEAT = ROOT / "work_orders" / "ccr" / "_elegant_seat.py"
PYW = pythonw_exe()
JOBS = ("gf38", "gemini31pro")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    launched = []
    for seat in JOBS:
        dest = OUT / f"{seat}.json"
        log = OUT / f"{seat}.log"
        cmd = [PYW, str(SEAT), "--seat", seat, "--out", str(dest),
               "--timeout", "900", "--max-tokens", "8192"]
        rec = spawn_detached(cmd, str(ROOT), log)
        launched.append({
            "seat": seat, "pid": rec.get("pid"), "out": str(dest),
            "log": str(log), "exe": PYW, "spawn": rec.get("method"),
            "ok": rec.get("ok"),
        })
    watch = {
        "schema": "cosmos-crew-elegant/1",
        "n": len(launched),
        "launched": launched,
        "note": (
            "WMI/pythonw spawn_detached. Kelly Vertex only. "
            "No OpenRouter. No grok.exe. P02 no peeking."
        ),
    }
    (OUT / "_watch.json").write_text(
        json.dumps(watch, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": True, "n": len(launched),
        "watch": str(OUT / "_watch.json"),
        "seats": [x["seat"] for x in launched],
        "pids": [x["pid"] for x in launched],
    }, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
