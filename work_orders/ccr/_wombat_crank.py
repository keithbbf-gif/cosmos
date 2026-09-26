#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Keep WOMBAT one-bite busy until every open WISHLIST line has a mouth ITEM.

Board full = 44 mouth-latched drops (not gold 08:15:55). Then she may close.
Never gold-fill. Never grok.exe. Isolated CODEX_HOME via CALL_WOMBAT_LUNA.cmd.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

CCR = Path(r"V:\A\Ai\COSMOS\work_orders\ccr")
DROP = Path(r"V:\A\Ai\COSMOS\work_orders\drop")
WISHLIST = Path(r"V:\A\Ai\COSMOS\docs\WISHLIST.md")
TASK = Path(r"V:\A\Ai\COSMOS\live\work\codex\hero-wombat-luna\TASK.md")
CALL = CCR / "CALL_WOMBAT_LUNA.cmd"
GOLD_TS = "2026-09-24T08:15:55-05:00"
ROOTS = (
    Path(r"V:\A\Ai\COSMOS\docs"),
    Path(r"V:\A\Ai\COSMOS\work_orders\ccr"),
    Path(r"V:\A\Ai\COSMOS"),
)

sys.path.insert(0, str(CCR))
from _womb_latch import _open_wishes  # noqa: E402


def _mouth_n() -> int:
    n = 0
    for p in DROP.glob("wo-luna-wombat-*.json"):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if str(d.get("Timestamp") or "") != GOLD_TS:
            n += 1
    return n


def _ctx_paths(wish: str) -> list[str]:
    found = [
        r"V:\A\Ai\COSMOS\docs\AGENT_BRIEF.md",
        r"V:\A\Ai\COSMOS\docs\AGENT_BOUNDARIES.md",
        r"V:\A\Ai\COSMOS\docs\WISHLIST.md",
    ]
    ticks = re.findall(r"`([^`]+)`", wish)
    for raw in ticks:
        name = raw.strip().replace("/", "\\")
        if name.lower().endswith((".md", ".json", ".toml", ".py")):
            hit = None
            p = Path(name)
            if p.is_file():
                hit = p
            else:
                base = Path(name.replace("\\", "/")).name
                for root in ROOTS:
                    cand = root / name
                    if cand.is_file():
                        hit = cand
                        break
                    cand2 = root / base
                    if cand2.is_file():
                        hit = cand2
                        break
            if hit is not None:
                s = str(hit)
                if s not in found:
                    found.append(s)
    return found


def _write_task(n: int, wish: str) -> None:
    ctx = _ctx_paths(wish)
    ctx_txt = ", ".join(f"`{p}`" for p in ctx)
    prior = ", ".join(f"wish-{i:02d}" for i in range(1, n))
    TASK.write_text(
        f"""# Mission — one bite: wish-{n:02d}-womb. Volatile.

PREFIX has no dates and no WO ids.
Product JSON MUST have order_id and Timestamp.

One mouth. One row. Not 20. Not 44. Not WOMB_MASTER.
Host gold drops do **not** count as your ITEM. Emit ITEM for this bite.
Do not re-emit {prior or "any earlier wish"}.

Open wish (verbatim, no checkbox):

{wish}

1. STANDARD_FORM_WO.json is the MIN STANDARD. Crew of 3, mix paid-low vs :free.
2. First line ITEM.
3. One JSON object, order_id `wish-{n:02d}-womb`.
   - top-level Agent = crew[0] three-part
   - Context source = abs existing paths: {ctx_txt}
   - Task = FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. WISH: <the wish above verbatim>
   - Timestamp ISO with offset (no fractional seconds); Output `proposals | out.json`
   - MAX_tokens = crew[0] window * 0.8 (never 880000)
4. Do not emit other order_ids. Do not summon CCrew.
5. Do not dump AGENT_BRIEF or AGENT_BOUNDARIES into the mouth.

Do not merge. Do not push. Do not grok.exe.
""",
        encoding="utf-8",
        newline="\n",
    )


def crank_one(n: int, wish: str) -> dict:
    _write_task(n, wish)
    r = subprocess.run(
        ["cmd", "/c", str(CALL)],
        cwd=str(CCR),
        capture_output=True,
        text=True,
        timeout=900,
    )
    tail = (r.stdout or "")[-800:]
    rec = {"n": n, "rc": r.returncode, "tail": tail[-400:]}
    gate = CCR / "WOMBAT_LUNA_pack.json"
    if gate.is_file():
        try:
            rec["pack"] = json.loads(gate.read_text(encoding="utf-8"))
        except ValueError:
            rec["pack"] = None
    return rec


def main() -> int:
    wishes = _open_wishes(WISHLIST.read_text(encoding="utf-8"))
    total = len(wishes)
    done = _mouth_n()
    print(json.dumps({"open": total, "mouth": done, "gold_left": total - done}))
    if done >= total:
        print(json.dumps({"ok": True, "kind": "BOARD_FULL", "close": True}))
        return 0
    start = done + 1
    count = 3
    if len(sys.argv) > 1:
        count = int(sys.argv[1])
    for n in range(start, min(start + count, total + 1)):
        print("CRANK", n, flush=True)
        rec = crank_one(n, wishes[n - 1])
        print(json.dumps({
            "n": n,
            "rc": rec["rc"],
            "first_line": (rec.get("pack") or {}).get("first_line"),
            "sku": (rec.get("pack") or {}).get("sku"),
        }), flush=True)
        if rec["rc"] != 0 or (rec.get("pack") or {}).get("first_line") != "ITEM":
            return 2
    print(json.dumps({"mouth": _mouth_n(), "open": total}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
