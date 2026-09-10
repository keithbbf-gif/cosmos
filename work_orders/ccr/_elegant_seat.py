#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kelly Vertex elegant-plan seat. pythonw. Not grok.exe. Not OpenRouter.

    py -3.14 work_orders\\ccr\\_elegant_seat.py --seat gf38 --out ...
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(r"V:\A\Ai\COSMOS")
LIVE = ROOT / "live"
IN = ROOT / "work_orders" / "ccr" / "CREW" / "IN"
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_paths import CosmosPaths  # noqa: E402
from cosmos_vertex_rail import load_coding_spec, rail_for_coding  # noqa: E402

SEATS = {
    "gf38": "gemini-3.8-flash",
    "gemini31pro": "gemini-3.1-pro-preview",
}
SEAT_TAG = {
    "gf38": "You are lane **Kelly A GF38** (`gemini-3.8-flash`). Not Joanna. Not OpenRouter Google.",
    "gemini31pro": "You are lane **Kelly B Gemini 3.1 Pro** (`gemini-3.1-pro-preview`). Not Joanna. Not OpenRouter Google.",
}


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--seat", required=True, choices=sorted(SEATS))
    p.add_argument("--out", required=True)
    p.add_argument("--timeout", type=int, default=900)
    p.add_argument("--max-tokens", type=int, default=8192)
    ns = p.parse_args(argv)
    model = SEATS[ns.seat]
    system = "\n\n".join(x for x in (
        _read(IN / "CACHE_RULE.md"),
        _read(IN / "CODING_GUIDELINES.md"),
        "PLAN mouth, not pane diffs. Do not start with unified diff. "
        "Do not write the live tree. P10 propose. CCr disposes.",
    ) if x.strip())
    patent = _read(IN / "CODER_PRELOAD_PATENT_IDEAS_CACHE.md")
    plan = _read(IN / "ELEGANT_PLAN.md")
    task = _read(IN / "ELEGANT_TASK.md")
    prompt = "\n\n".join((
        patent,
        "--- TASK ---",
        plan,
        task,
        SEAT_TAG[ns.seat],
    ))
    paths = CosmosPaths(str(LIVE))
    spec = load_coding_spec(paths)
    out = Path(ns.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    t0 = datetime.now().astimezone().isoformat(timespec="seconds")
    if spec.get("role") != "coding":
        rec = {
            "ok": False, "reason": "NO_CODING_SPEC",
            "detail": "vertex_coding.json missing — refusing Joanna",
        }
    else:
        rail = rail_for_coding(paths)
        rec = rail.ask(
            prompt, model=model, system=system,
            max_output_tokens=int(ns.max_tokens),
            timeout_s=int(ns.timeout),
        )
    tok = rec.get("tokens") if isinstance(rec.get("tokens"), dict) else {}
    body = {
        "schema": "cosmos-elegant-seat/1",
        "ok": bool(rec.get("ok")),
        "seat": ns.seat,
        "model": rec.get("model") or model,
        "via": rec.get("via") or "vertex",
        "reason": rec.get("reason"),
        "t0": t0,
        "t1": datetime.now().astimezone().isoformat(timespec="seconds"),
        "text": rec.get("text") or "",
        "detail": rec.get("detail") or "",
        "tokens": rec.get("tokens"),
        "usd": rec.get("cost_usd"),
        "cached_tokens": tok.get("cached"),
        "prompt_tokens": tok.get("in"),
        "account": spec.get("account"),
        "project": spec.get("project"),
        "prompt_chars": len(prompt),
        "system_chars": len(system),
        "note": "Kelly Vertex only. Patent preload not sent to OpenRouter.",
    }
    out.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": body["ok"], "seat": ns.seat, "model": body["model"],
        "reason": body["reason"], "out": str(out),
        "text_len": len(body["text"]),
        "prompt_chars": body["prompt_chars"],
    }))
    return 0 if body["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
