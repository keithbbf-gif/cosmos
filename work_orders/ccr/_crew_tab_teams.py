#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One 2x2 (or 2-seat) propose team per cDeck tab. Cheap+quota. Not Sol.

    py -3.14 work_orders\\ccr\\_crew_tab_teams.py
Luna = 30m frozen keep-alive. Sol = Keith+CCr together only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(r"V:\A\Ai\COSMOS")
sys.path.insert(0, str(ROOT / "cosmos"))
sys.path.insert(0, str(ROOT / "work_orders" / "ccr"))
from cosmos_clock import pythonw_exe, spawn_detached  # noqa: E402
from cosmos_paths import CosmosPaths  # noqa: E402
from cosmos_session import require_bootup  # noqa: E402
from _iter_out import next_pair  # noqa: E402
from _pair_pack import OR_WINDOW, VX_WINDOW, seat_pack  # noqa: E402

PYW = pythonw_exe()
VX = ROOT / "work_orders" / "ccr" / "_cdeck_code_seat.py"
OR = ROOT / "work_orders" / "ccr" / "_code_or_seat.py"
ITEMS = ROOT / "work_orders" / "ccr" / "CREW" / "IN" / "TABS"
OUT = ROOT / "work_orders" / "ccr" / "CREW" / "OUT" / "TEAM_TABS"

# Keith 2026-09-10: many OR×OR pairs on the same ITEMs (porosity variety).
# GEM only on harder jobs (tools, gitur). One DS0731 per list. DS/Muse house no patent.
TABS = (
    ("tools", "gemini31pro", "ds"),
    ("gitur", "gf38", "muse"),
    ("skins", "glm", "qwen"),
    ("skins", "mistral", "ds0423"),
    ("recents", "glm", "mistral"),
    ("recents", "qwen", "llama"),
    ("jobs", "qwen", "nemo"),
    ("jobs", "ds0423", "oss"),
    ("spend", "mistral", "oss"),
    ("spend", "glm", "nemo"),
    ("voice", "nemo", "llama"),
    ("voice", "qwen", "mistral"),
    ("surfaces", "oss", "llama"),
    ("surfaces", "glm", "llama"),
    ("gitur", "glm", "muse"),
    ("tools", "glm", "oss"),
)


def _py(seat: str) -> Path:
    return VX if seat in VX_WINDOW else OR


def _spawn(py: Path, extra: list[str], dest: Path, log: Path) -> dict:
    cmd = [PYW, str(py), *extra, "--out", str(dest),
           "--timeout", "900", "--max-tokens", "8192"]
    rec = spawn_detached(cmd, str(ROOT), log)
    return {"pid": rec.get("pid"), "ok": rec.get("ok"),
            "spawn": rec.get("method"), "out": str(dest)}


def main() -> int:
    require_bootup(CosmosPaths(str(ROOT / "live")))
    try:
        raw = json.loads((ROOT / "live" / "state" / "control" / "PAUSE.flag").read_text(encoding="utf-8"))
        if raw.get("state") == "PAUSED" and raw.get("mode") == "hold":
            print("PAUSED hold - no seats spawned", flush=True)
            return 0
    except (OSError, ValueError):
        pass
    launched = []
    for tab, a, b in TABS:
        item = ITEMS / f"{tab}.md"
        folder = OUT / tab
        adest, alog = next_pair(folder, a)
        bdest, blog = next_pair(folder, b)
        ka, kb = seat_pack(a), seat_pack(b)
        launched.append({
            "tab": tab,
            "pack_a": ka,
            "pack_b": kb,
            "a": _spawn(_py(a), ["--seat", a, "--pack", ka, "--item", str(item)],
                        adest, alog),
            "b": _spawn(_py(b), ["--seat", b, "--pack", kb, "--item", str(item)],
                        bdest, blog),
        })
    watch = OUT / "_watch.json"
    watch.parent.mkdir(parents=True, exist_ok=True)
    watch.write_text(json.dumps({
        "schema": "cosmos-crew-tab-teams/1",
        "n_tabs": len(TABS),
        "luna": "30m frozen keep-alive only",
        "sol": "Keith+CCr together — not launched",
        "launched": launched,
    }, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "n_tabs": len(TABS),
        "n_seats": len(TABS) * 2,
        "tabs": [t[0] for t in TABS],
        "watch": str(watch),
    }, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
