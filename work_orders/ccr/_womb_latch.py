#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Latch WOMB rows only if every cell matches STANDARD_FORM_WO.json types.
Gold Task text comes from docs/WISHLIST.md (verbatim). Mouth is
WOMBAT_LUNA_last.txt. One ITEM bite → latch that order_id only. Do not
gold-fill the rest of the wishlist. Missing top-level Agent is filled from
crew[0]. Shorter-than-gold Task is replaced by gold, not a description.
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

CCR = Path(r"V:\A\Ai\COSMOS\work_orders\ccr")
DROP = Path(r"V:\A\Ai\COSMOS\work_orders\drop")
WISHLIST = Path(r"V:\A\Ai\COSMOS\docs\WISHLIST.md")
EXAMPLE = CCR / "STANDARD_FORM_WO.json"
LAST = CCR / "WOMBAT_LUNA_last.txt"
TZ = ZoneInfo("America/Chicago")

AGENT_RE = re.compile(r"^[^|]+ \| [^|]+ \| \S+")
READ_RE = re.compile(r". \[read\*\]$")  # label form — refuse; want abs path
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$")
OUT_RE = re.compile(r"^[^\\/|]+ \| [^\\/|]+\.[A-Za-z0-9]+$")
BAD_SCOPE = re.compile(r"(?i)read the complete matching wish|truncated excerpt")
POINTER_CELL = re.compile(
    r"(?i)<pointer>|see docs/|see file:|\[read\*\]\s*$|^docs/\S+$"
)
TASK_HEAD = "FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md."


def _open_wishes(text: str) -> list[str]:
    chunks = re.split(r"\n(?=- \[[ xX]\])", text)
    out = []
    for c in chunks:
        c = c.strip()
        if c.startswith("- [ ]"):
            body = c[len("- [ ]"):].strip()
            body = re.sub(r"^(\*\*)(.+?)(\*\*)", r"\2", body, count=1)
            out.append(body)
    return out


CREW3 = [
    {
        "seat": 1,
        "Agent": "OpenRouter | Nex | nex-agi/nex-n2.5-mini:free",
        "tier": "free",
        "context_window_tokens": 262000,
        "cache_floor_tokens": 1024,
        "cache_ttl": "30m",
        "cache_prefix": "legend+WRAP+STYLE+SKILL",
        "timeout_s": 900,
        "tps": 49,
        "pack": "work_orders/ccr/hero_coders/13_nexmini",
        "output_what": "python",
        "OPTIMUM_tokens": "float",
        "MAX_tokens": 209600,
    },
    {
        "seat": 2,
        "Agent": "OpenRouter | North | cohere/north-mini-code:free",
        "tier": "free",
        "context_window_tokens": 256000,
        "cache_floor_tokens": 1024,
        "cache_ttl": "30m",
        "cache_prefix": "legend+WRAP+STYLE+SKILL",
        "timeout_s": 900,
        "tps": 58,
        "pack": "work_orders/ccr/hero_coders/09_northmini",
        "output_what": "python",
        "OPTIMUM_tokens": "float",
        "MAX_tokens": 204800,
    },
    {
        "seat": 3,
        "Agent": "OpenRouter | Hy3 | tencent/hy3-preview",
        "tier": "paid-low",
        "context_window_tokens": 262000,
        "cache_floor_tokens": 1024,
        "cache_ttl": "30m",
        "cache_prefix": "legend+WRAP+STYLE+SKILL",
        "timeout_s": 900,
        "tps": 69,
        "pack": "work_orders/ccr/hero_coders/07_hy3preview",
        "output_what": "python",
        "OPTIMUM_tokens": "float",
        "MAX_tokens": 209600,
    },
]


def gold_rows(n: int | None = None) -> list[dict]:
    wishes = _open_wishes(WISHLIST.read_text(encoding="utf-8"))
    if n is None:
        n = len(wishes)
    ts = datetime.now(TZ).replace(microsecond=0).isoformat()
    rows = []
    for i, body in enumerate(wishes[:n], 1):
        rows.append({
            "order_id": f"wish-{i:02d}-womb",
            "Agent": CREW3[0]["Agent"],
            "Context source": [
                r"V:\A\Ai\COSMOS\docs\AGENT_BRIEF.md",
                r"V:\A\Ai\COSMOS\docs\AGENT_BOUNDARIES.md",
                r"V:\A\Ai\COSMOS\docs\WISHLIST.md",
            ],
            "Task": TASK_HEAD + " P10: PROPOSE only. Never write the live tree. WISH: " + body,
            "Target & scope": (
                "proposals under Output only; never kernel/ledger/sched/service; "
                "never LiT; never grok.exe"
            ),
            "Timestamp": ts,
            "Output": "proposals | out.json",
            "output_what": "python",
            "OPTIMUM_tokens": "float",
            "MAX_tokens": 209600,
            "crew": [dict(x) for x in CREW3],
        })
    return rows


def check_row(row: dict, gold: dict) -> list[str]:
    bad = []
    if not isinstance(row, dict):
        return ["not an object"]
    for k in EXAMPLE_KEYS:
        if k not in row:
            bad.append(f"missing {k}")
    if bad:
        return bad
    if not re.match(r"^wish-\d{2}-womb$", str(row.get("order_id") or "")):
        bad.append("order_id")
    if not AGENT_RE.match(str(row.get("Agent") or "").strip()):
        bad.append("Agent")
    ctx = row.get("Context source")
    if not isinstance(ctx, list) or not ctx:
        bad.append("Context source")
    else:
        for x in ctx:
            if not isinstance(x, str) or READ_RE.search(x) or POINTER_CELL.search(x):
                bad.append("Context source.label")
                break
            p = Path(x)
            if not p.is_absolute() or not p.is_file():
                bad.append("Context source.missing")
                break
    task = str(row.get("Task") or "")
    if POINTER_CELL.search(task.strip()) or task.strip().startswith("<pointer"):
        bad.append("Task.pointer")
    if not task.startswith("FIRST read docs/AGENT_BRIEF.md"):
        bad.append("Task.head")
    if len(task) < len(gold.get("Task") or "") - 5:
        bad.append("Task.short")
    scope = str(row.get("Target & scope") or "")
    if BAD_SCOPE.search(scope) or len(scope) < 20:
        bad.append("Target & scope")
    if not ISO_RE.match(str(row.get("Timestamp") or "")):
        bad.append("Timestamp")
    if not OUT_RE.match(str(row.get("Output") or "").strip()):
        bad.append("Output")
    if str(row.get("output_what") or "") not in ("text", "python", "no_prose"):
        bad.append("output_what")
    opt = row.get("OPTIMUM_tokens")
    if opt != "float" and not (isinstance(opt, int) and opt > 0):
        bad.append("OPTIMUM_tokens")
    mx = row.get("MAX_tokens")
    if not (isinstance(mx, int) and mx > 0):
        bad.append("MAX_tokens")
    crew = row.get("crew")
    if not isinstance(crew, list) or len(crew) != 3:
        bad.append("crew.len")
    else:
        tiers = {str(c.get("tier") or "") for c in crew if isinstance(c, dict)}
        if "paid-low" not in tiers or "free" not in tiers:
            bad.append("crew.mix")
        need = ("seat", "Agent", "tier", "context_window_tokens",
                "cache_floor_tokens", "cache_ttl", "cache_prefix",
                "timeout_s", "tps", "pack", "output_what",
                "OPTIMUM_tokens", "MAX_tokens")
        for i, c in enumerate(crew):
            if not isinstance(c, dict) or any(k not in c for k in need):
                bad.append(f"crew[{i}]")
            elif not AGENT_RE.match(str(c.get("Agent") or "")):
                bad.append(f"crew[{i}].Agent")
    return bad


EXAMPLE_KEYS = (
    "order_id", "Agent", "Context source", "Task",
    "Target & scope", "Timestamp", "Output", "output_what",
    "OPTIMUM_tokens", "MAX_tokens", "crew",
)


def load_mouth(path: Path = LAST) -> list:
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    start_a = text.find("[")
    start_o = text.find("{")
    if start_a >= 0 and (start_o < 0 or start_a < start_o):
        obj = json.loads(text[start_a:text.rfind("]") + 1])
        return obj if isinstance(obj, list) else [obj]
    if start_o >= 0:
        obj = json.loads(text[start_o:text.rfind("}") + 1])
        return [obj] if isinstance(obj, dict) else []
    return []


def _prepare(cand: dict, gold: dict) -> dict:
    cand = dict(cand)
    if not cand.get("Agent"):
        crew = cand.get("crew")
        if isinstance(crew, list) and crew and isinstance(crew[0], dict):
            cand["Agent"] = crew[0].get("Agent") or gold["Agent"]
        else:
            cand["Agent"] = gold["Agent"]
    task = str(cand.get("Task") or "")
    task = re.sub(r"WISH:\s*- \[[ xX]\]\s*", "WISH: ", task, count=1)
    cand["Task"] = task
    if len(task) < len(gold.get("Task") or "") - 5:
        cand["Task"] = gold["Task"]
    for k in EXAMPLE_KEYS:
        if k not in cand or cand[k] in ("", None):
            cand[k] = gold[k]
    if str(cand.get("Agent") or "").startswith("UNASSIGNED"):
        cand["Agent"] = gold["Agent"]
    if BAD_SCOPE.search(str(cand.get("Target & scope") or "")):
        cand["Target & scope"] = gold["Target & scope"]
    if not ISO_RE.match(str(cand.get("Timestamp") or "")):
        cand["Timestamp"] = gold["Timestamp"]
    if not OUT_RE.match(str(cand.get("Output") or "").strip()):
        cand["Output"] = gold["Output"]
    return cand


def latch(mouth: list | None = None) -> dict:
    gold = gold_rows()
    gold_by = {g["order_id"]: g for g in gold}
    if mouth is None:
        mouth = load_mouth()
    by_id = {}
    for r in mouth or []:
        if isinstance(r, dict) and r.get("order_id"):
            by_id[str(r["order_id"])] = r
    latched, rejected = [], []
    DROP.mkdir(parents=True, exist_ok=True)
    # One ITEM bite: only latch mouth order_ids. Empty/NONE mouth must not
    # gold-fill the wishlist (that scar wrote 44 drops at one timestamp).
    if not by_id:
        return {"ok": True, "latched": 0, "rejected": [], "mouth_n": 0,
                "detail": "NONE or empty mouth — no gold-fill"}
    targets = list(by_id)
    for oid in targets:
        g = gold_by.get(oid)
        if g is None:
            rejected.append({"order_id": oid, "errs": ["unknown_order_id"]})
            continue
        cand = _prepare(by_id.get(oid, g), g)
        errs = check_row(cand, g)
        nn = oid.split("-")[1]
        dest = DROP / f"wo-luna-wombat-{nn}.json"
        if errs:
            rejected.append({"order_id": oid, "errs": errs})
            continue
        dest.write_text(json.dumps(cand, indent=2) + "\n", encoding="utf-8", newline="\n")
        latched.append(str(dest))
    return {"ok": not rejected, "latched": len(latched), "rejected": rejected,
            "mouth_n": len(by_id)}


def main() -> int:
    rec = latch()
    print(json.dumps(rec, indent=1))
    return 0 if rec["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
