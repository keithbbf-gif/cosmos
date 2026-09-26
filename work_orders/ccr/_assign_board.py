#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Assign ACTIVE HERO seats on Phase 2/3 board rows so WOMBAT writes prompts
to a named agent (window, MAX, first-line, pack). Mix paid-low vs :free.
No grok.exe. No unseated slugs.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

CCR = Path(r"V:\A\Ai\COSMOS\work_orders\ccr")
MASTER = CCR / "WOMB_MASTER.jsonl"
TZ = ZoneInfo("America/Chicago")

# ACTIVE only. window = catalog context. MAX = 0.8*window.
SEATS = [
    {
        "key": "north",
        "Agent": "OpenRouter | North | cohere/north-mini-code:free",
        "slug": "cohere/north-mini-code:free",
        "tier": "free",
        "family": "cohere",
        "context_window_tokens": 256000,
        "pack": "work_orders/ccr/hero_coders/09_northmini",
        "harness": "openrouter chat",
        "routing": "off",
        "first_line": "NONE | diff --git",
        "notes": "No essay. Named pin. Pair with paid-low, not free-vs-free only.",
    },
    {
        "key": "hy3p",
        "Agent": "OpenRouter | Hy3 | tencent/hy3-preview",
        "slug": "tencent/hy3-preview",
        "tier": "paid-low",
        "family": "tencent",
        "context_window_tokens": 262000,
        "pack": "work_orders/ccr/hero_coders/07_hy3preview",
        "harness": "openrouter chat",
        "routing": "off",
        "first_line": "NONE | diff --git",
        "notes": "Class-6 CoT prepends preamble. Task must make first line unambiguous. Prefill NONE on summon. Not tencent/hy3.",
    },
    {
        "key": "nex",
        "Agent": "OpenRouter | Nex | nex-agi/nex-n2.5-mini:free",
        "slug": "nex-agi/nex-n2.5-mini:free",
        "tier": "free",
        "family": "nex-agi",
        "context_window_tokens": 262000,
        "pack": "work_orders/ccr/hero_coders/13_nexmini",
        "harness": "openrouter chat",
        "routing": "off",
        "first_line": "NONE | diff --git",
        "notes": "No essay. Pair with paid-low.",
    },
    {
        "key": "qwen38",
        "Agent": "OpenRouter | Qwen | qwen/qwen3.8-flash",
        "slug": "qwen/qwen3.8-flash",
        "tier": "paid-low",
        "family": "qwen",
        "context_window_tokens": 1000000,
        "pack": "V:\\A\\Ai\\COSMOS\\live\\work\\openrouter\\hero-coder-ping",
        "harness": "openrouter chat",
        "routing": "off",
        "first_line": "NONE | diff --git",
        "notes": "1M ctx. Enable thinking in Task. Not qwen3.7-flash (429 this pass).",
    },
    {
        "key": "ds0731",
        "Agent": "OpenRouter | DeepSeek | deepseek/deepseek-v4-flash-0731",
        "slug": "deepseek/deepseek-v4-flash-0731",
        "tier": "paid-low",
        "family": "deepseek",
        "context_window_tokens": 1310000,
        "pack": "work_orders/ccr/hero_coders/3_ds",
        "harness": "openrouter chat",
        "routing": "off",
        "first_line": "NONE | diff --git",
        "notes": "dsh has no key this pass — OR rail. Thinking default.",
    },
    {
        "key": "nemo35",
        "Agent": "OpenRouter | Nemo | nvidia/nemotron-3.5-lightning:free",
        "slug": "nvidia/nemotron-3.5-lightning:free",
        "tier": "free",
        "family": "nvidia",
        "context_window_tokens": 262000,
        "pack": "work_orders/ccr/hero_coders/08_nemo35f",
        "harness": "openrouter chat",
        "routing": "off",
        "first_line": "NONE | diff --git",
        "notes": "Prefill NONE if CoT. No :floor on :free.",
    },
    {
        "key": "gf38",
        "Agent": "Google | Flash | google/gemini-3.8-flash",
        "slug": "google/gemini-3.8-flash",
        "tier": "paid-low",
        "family": "google",
        "context_window_tokens": 1000000,
        "pack": "work_orders/ccr/hero_coders/2_gf38",
        "harness": "openrouter chat",
        "routing": "off",
        "first_line": "NONE | diff --git",
        "notes": "Not gemini-2.5-flash. Kelly Vertex failover is same model, different via.",
    },
    {
        "key": "muse13",
        "Agent": "OpenRouter | Muse | meta/muse-spark-1.3-contributor",
        "slug": "meta/muse-spark-1.3-contributor",
        "tier": "paid-low",
        "family": "meta",
        "context_window_tokens": 1050000,
        "pack": "V:\\A\\Ai\\COSMOS\\live\\work\\openrouter\\hero-coder-ping",
        "harness": "openrouter chat",
        "routing": "off",
        "first_line": "NONE | diff --git",
        "notes": "Reasoning eats max_tokens — keep Task short; fat completion budget on summon.",
    },
]

GROK = {
    "key": "grok",
    "Agent": "xAI | Grok | grok-4.6",
    "slug": "grok-4.6",
    "tier": "paid",
    "family": "xai",
    "context_window_tokens": 131072,
    "pack": "work_orders/ccr/hero_coders/6_grok_gitur",
    "harness": "Cursor Gitur BUILD",
    "routing": None,
    "first_line": "NONE | diff --git",
    "notes": "NOT grok.exe. PREFIX+ITEM under 200k (2x surcharge above). Cursor credits Gitur-only.",
}

NORTH = SEATS[0]
HY3 = SEATS[1]


def _cell(seat: dict) -> dict:
    w = int(seat["context_window_tokens"])
    return {
        "Agent": seat["Agent"],
        "slug": seat["slug"],
        "tier": seat["tier"],
        "family": seat["family"],
        "context_window_tokens": w,
        "cache_floor_tokens": 1024,
        "cache_ttl": "30m",
        "cache_prefix": "legend+WRAP+STYLE+SKILL",
        "pack": seat["pack"],
        "harness": seat["harness"],
        "routing": seat.get("routing"),
        "first_line": seat["first_line"],
        "prompt_notes": seat["notes"],
        "MAX_tokens": int(w * 0.8),
        "OPTIMUM_tokens": "float",
    }


def _pair_for(primary: dict) -> dict:
    alt = HY3 if primary["tier"] == "free" else NORTH
    return {"primary": _cell(primary), "alt": _cell(alt)}


def assign_row(d: dict, i: int) -> dict:
    d = dict(d)
    ag = str(d.get("agent_field") or "")
    kind = str(d.get("kind") or "")
    if "Grok" in ag or "grok-4.6" in ag:
        pair = {"primary": _cell(GROK), "alt": _cell(NORTH)}
    elif "gemini-2.5" in ag.lower() or "Google | Flash" in ag:
        pair = {"primary": _cell(SEATS[6]), "alt": _cell(NORTH)}  # GF38 not 2.5
    else:
        primary = SEATS[i % len(SEATS)]
        pair = _pair_for(primary)
    d["agent_field"] = pair["primary"]["Agent"]
    d["model"] = pair["primary"]["slug"]
    d["hero_pack"] = pair["primary"]["pack"]
    d["harness"] = pair["primary"]["harness"]
    d["assigned"] = pair
    d["assigned_at"] = datetime.now(TZ).replace(microsecond=0).isoformat()
    d["first_line"] = pair["primary"]["first_line"]
    if kind == "wish" or str(d.get("order_id") or "").startswith("wish-"):
        # standing WOMBAT crew of 3 on wish rows
        d["crew"] = [_cell(SEATS[2]), _cell(NORTH), _cell(HY3)]
        d["agent_field"] = SEATS[2]["Agent"]
        d["assigned"] = {
            "primary": _cell(SEATS[2]),
            "alt": _cell(HY3),
            "crew3": True,
        }
    return d


def patch_jsonl(path: Path, start_i: int = 0) -> int:
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    out = []
    for i, r in enumerate(rows):
        out.append(assign_row(r, start_i + i))
    path.write_text("".join(json.dumps(r, ensure_ascii=True) + "\n" for r in out), encoding="utf-8")
    return len(out)


def patch_master(lo: int, hi: int) -> int:
    rows = [json.loads(l) for l in MASTER.read_text(encoding="utf-8").splitlines() if l.strip()]
    n = 0
    by_n = {}
    for p in (CCR / "PHASE2_100.jsonl", CCR / "PHASE3_100.jsonl"):
        for l in p.read_text(encoding="utf-8").splitlines():
            d = json.loads(l)
            by_n[int(d["n"])] = d
    out = []
    for r in rows:
        nn = int(r.get("n") or 0)
        if lo <= nn <= hi and nn in by_n:
            src = by_n[nn]
            r = dict(r)
            for k in ("agent_field", "model", "hero_pack", "harness", "assigned",
                      "assigned_at", "first_line", "crew"):
                if k in src:
                    r[k] = src[k]
            n += 1
        out.append(r)
    MASTER.write_text("".join(json.dumps(r, ensure_ascii=True) + "\n" for r in out), encoding="utf-8")
    return n


def main() -> int:
    a = patch_jsonl(CCR / "PHASE2_100.jsonl", 0)
    b = patch_jsonl(CCR / "PHASE3_100.jsonl", 100)
    m = patch_master(501, 700)
    print(json.dumps({"phase2": a, "phase3": b, "master_patched": m}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
