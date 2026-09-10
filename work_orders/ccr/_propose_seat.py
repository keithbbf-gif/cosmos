#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One-shot propose seat. Does not write the live tree. Does not print keys.

    py -3.14 work_orders\\ccr\\_propose_seat.py --seat gf38 --prompt-file ... --out ...
    py -3.14 work_orders\\ccr\\_propose_seat.py --seat glm --prompt-file ... --out ...
    py -3.14 work_orders\\ccr\\_propose_seat.py --seat ds --prompt-file ... --out ...
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
CACHE_RULE = IN / "CACHE_RULE.md"
PREFIX_FILE = IN / "PREFIX.md"
GF38_MOUTH = IN / "GF38_MOUTH.md"
CODING_GUIDELINES = IN / "CODING_GUIDELINES.md"
VERTEX_PRELOAD = (
    PREFIX_FILE,
    CACHE_RULE,
    GF38_MOUTH,
    CODING_GUIDELINES,
    ROOT / "docs" / "PROMPT_CACHE.md",
    ROOT / "docs" / "AGENT_BOUNDARIES.md",
)


def _join_files(paths) -> str:
    parts = []
    for p in paths:
        if p.is_file():
            parts.append(p.read_text(encoding="utf-8").rstrip())
    return "\n\n".join(parts)
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_paths import CosmosPaths  # noqa: E402

SEATS = {
    "gf38": {"kind": "vertex", "model": "gemini-3.8-flash", "role": "quality"},
    "glm": {"kind": "or", "model": "z-ai/glm-5.3-flash", "role": "cheap"},
    "ds": {"kind": "or", "model": "deepseek/deepseek-v4-flash-0731", "role": "cheap"},
    "ling": {"kind": "or", "model": "inclusionai/ling-3.0-flash", "role": "cheap"},
    "solar": {"kind": "or", "model": "upstage/solar-pro4", "role": "cheap"},
    # Named this turn: cheaper than G46 $2/$6 (catalog 0.2/1.2, COD 71.4).
    # Not :batch. Not Sol ($2/$10 — more than G46). Not grok-4.6.
    # Keith 2026-09-08: pin flex. Catalog Flex $0.10/$0.60 (page $0.20/$1.20).
    # Not :batch. Not Sol ($2/$10 — more than G46). Not grok-4.6.
    "luna": {"kind": "or", "model": "openai/gpt-5.6-luna", "role": "credit",
             "flex": True},
    # Keith 2026-09-10: Luna Pro is ½ off on Flex. Same underlying Luna,
    # reasoning max. Page $0.20/$1.75 → Flex $0.10/$0.875. Not a swap of luna.
    # Catalog COD UNMEASURED. Not Sol.
    "luna-pro": {"kind": "or", "model": "openai/gpt-5.6-luna-pro",
                 "role": "credit", "flex": True},
    # Hard Python / repo escalate. Flex pin already in cosmos_openrouter_rail.
    # Vendor DeepSWE lead is a guideline, not a seat lock vs G46/GF38.
    "terra": {"kind": "or", "model": "openai/gpt-5.6-terra", "role": "escalate",
              "flex": True},
    # Keith 2026-09-09 later: Luna mostly. Sol = major full-code reviews only.
    # oa-api stays paused (rails-prober scar). Not Flex unless named.
    "sol": {"kind": "or", "model": "openai/gpt-5.6-sol", "role": "major_review"},
}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--seat", required=True, choices=sorted(SEATS))
    p.add_argument("--prompt-file", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--system-file", default="")
    p.add_argument("--max-tokens", type=int, default=4000)
    ns = p.parse_args(argv)
    seat = SEATS[ns.seat]
    prompt = Path(ns.prompt_file).read_text(encoding="utf-8")
    system = ""
    if ns.system_file:
        system = Path(ns.system_file).read_text(encoding="utf-8")
    elif (ROOT / "work_orders" / "ccr" / "CREW" / "IN" / "PREFIX.md").is_file():
        # SOP: preload PREFIX even if the caller omitted --system-file.
        system = (ROOT / "work_orders" / "ccr" / "CREW" / "IN" / "PREFIX.md").read_text(
            encoding="utf-8")
    paths = CosmosPaths(str(LIVE))
    t0 = datetime.now().astimezone().isoformat(timespec="seconds")
    if seat["kind"] == "vertex":
        from cosmos_vertex_rail import (  # noqa: E402
            load_coding_spec, rail_for_coding,
        )
        spec = load_coding_spec(paths)
        if spec.get("role") != "coding":
            rec = {
                "ok": False, "reason": "NO_CODING_SPEC",
                "detail": "vertex_coding.json missing — refusing Joanna",
            }
        else:
            rail = rail_for_coding(paths)
            rail.spec["timeout_s"] = max(int(rail.spec.get("timeout_s") or 120), 180)
            # Gemini 3.x implicit cache floor 4096. systemInstruction = canon
            # stack (PREFIX+CACHE_RULE+PROMPT_CACHE+BOUNDARIES); item is tail.
            prefix = _join_files(VERTEX_PRELOAD) or system
            from cosmos_vertex_rail import CACHE_TTL, cache_display_name
            rules = _join_files((
                CACHE_RULE, GF38_MOUTH, CODING_GUIDELINES,
                ROOT / "docs" / "PROMPT_CACHE.md"))
            repo = _join_files((
                PREFIX_FILE, ROOT / "docs" / "AGENT_BOUNDARIES.md"))
            item = prompt
            if system and system.strip() and system.strip() != prefix.strip():
                item = system.rstrip() + "\n\n--- ITEM ---\n" + prompt
            disp = cache_display_name(model=seat["model"], prefix=prefix)
            ptr = ROOT / "work_orders" / "ccr" / "CREW" / "OUT" / "FARM" / "gf38_explicit_cache.json"
            created = {}
            if ptr.is_file():
                try:
                    old = json.loads(ptr.read_text(encoding="utf-8"))
                except ValueError:
                    old = {}
                if (old.get("display_name") == disp and old.get("name")
                        and old.get("ok")):
                    created = old
            if not created.get("name"):
                created = rail.ensure_cache(
                    model=seat["model"], contents_text=repo,
                    system_instruction=rules, ttl=CACHE_TTL,
                    display_name=disp)
                if created.get("ok") and created.get("name"):
                    ptr.parent.mkdir(parents=True, exist_ok=True)
                    ptr.write_text(json.dumps(created, indent=1) + "\n",
                                   encoding="utf-8")
            if created.get("ok") and created.get("name"):
                rec = rail.ask(item, model=seat["model"],
                               cached_content=created["name"])
                rec["cache_name"] = created.get("name")
                rec["cache_expire"] = created.get("expire_time")
                rec["cache_display"] = created.get("display_name")
            else:
                rec = rail.ask(item, model=seat["model"], system=prefix)
                rec["cache_create"] = created
            tok = rec.get("tokens") if isinstance(rec.get("tokens"), dict) else {}
            rec = {
                "ok": bool(rec.get("ok")),
                "reason": rec.get("reason"),
                "model": rec.get("model"),
                "via": rec.get("via"),
                "text": rec.get("text") or "",
                "detail": rec.get("detail") or "",
                "tokens": rec.get("tokens"),
                "usd": rec.get("cost_usd"),
                "account": spec.get("account"),
                "project": spec.get("project"),
                "cached_tokens": tok.get("cached"),
                "prompt_tokens": tok.get("in"),
                "cache_name": rec.get("cache_name") or rec.get("cached_content"),
                "cache_expire": rec.get("cache_expire"),
                "cache_display": rec.get("cache_display"),
                "cache_create": rec.get("cache_create"),
            }
    else:
        from cosmos_openrouter_rail import (  # noqa: E402
            CHAT_PATH, FLEX_MODELS, OPENAI_FLEX, OpenRouterRail, cache_family,
            fold_usage, key_path_for, load_spec, model_refused, spec_path_for,
            tag_preload, _message_text,
        )
        why = None if seat.get("skip_pin") else model_refused(seat["model"])
        if why:
            rec = {"ok": False, "reason": "REFUSED", "detail": why}
        else:
            spec = load_spec(spec_path_for(paths))
            spec["timeout_s"] = max(int(spec.get("timeout_s") or 120), 180)
            rail = OpenRouterRail(key_path_for(paths, spec), spec)
            prefix = system
            if system and CACHE_RULE.is_file():
                prefix = system.rstrip() + "\n\n" + CACHE_RULE.read_text(
                    encoding="utf-8")
            if prefix and CODING_GUIDELINES.is_file():
                prefix = prefix.rstrip() + "\n\n" + CODING_GUIDELINES.read_text(
                    encoding="utf-8")
            flex = bool(seat.get("flex") or seat["model"] in FLEX_MODELS)
            if prefix:
                messages = [
                    {"role": "system", "content": prefix},
                    {"role": "user", "content": prompt},
                ]
            else:
                messages = [{"role": "user", "content": prompt}]
            messages = tag_preload(messages, flex=flex)
            prov = {"allow_fallbacks": False}
            if flex:
                prov["only"] = [OPENAI_FLEX]
                prov["order"] = [OPENAI_FLEX]
            body = {
                "model": seat["model"],
                "messages": messages,
                "max_tokens": int(ns.max_tokens),
                "stream": False,
                "provider": prov,
            }
            if prefix:
                body["prompt_cache_key"] = cache_family(
                    model=seat["model"], prefix=prefix)
                body["session_id"] = body["prompt_cache_key"]
                if flex:
                    body["prompt_cache_options"] = {
                        "mode": "explicit", "ttl": "30m",
                    }
            # Same OpenRouter key for every named pin. 429/502 are provider
            # limits (GLM Z.AI), not AUTH. Retry with backoff; do not
            # allow_fallbacks (H3 silent swap).
            status, obj = 0, {}
            last_err = ""
            for attempt in range(4):
                status, _hdrs, obj = rail._call("POST", CHAT_PATH, body)
                obj = obj if isinstance(obj, dict) else {}
                err = obj.get("error") if isinstance(obj.get("error"), dict) else None
                last_err = (err or {}).get("message") if err else ""
                if status == 200 and obj.get("model"):
                    break
                if status not in (429, 502) or attempt == 3:
                    break
                import time
                time.sleep((5, 15, 30, 45)[attempt])
            bound = obj.get("model")
            usage = fold_usage(obj)
            text = _message_text(obj)
            choices = obj.get("choices") if isinstance(obj.get("choices"), list) else []
            msg = (choices[0] or {}).get("message") if choices and isinstance(choices[0], dict) else {}
            err = obj.get("error") if isinstance(obj.get("error"), dict) else None
            rec = {
                "ok": status == 200 and bool(bound),
                "reason": None if status == 200 else f"HTTP_{status}",
                "model": bound,
                "model_requested": seat["model"],
                "via": "openrouter",
                "http": status,
                "provider": (body.get("provider") or {}).get("only"),
                "prompt_cache_key": body.get("prompt_cache_key"),
                "text": text,
                "detail": (err or {}).get("message") if err else "",
                "usage": usage,
                "msg_keys": sorted(msg.keys()) if isinstance(msg, dict) else [],
                "content_type": type((msg or {}).get("content")).__name__ if isinstance(msg, dict) else "",
            }
    out = {
        "schema": "cosmos-propose-seat/1",
        "seat": ns.seat,
        "role": seat["role"],
        "pin": seat["model"],
        "t": t0,
        "prompt_file": str(ns.prompt_file),
        **rec,
    }
    dest = Path(ns.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    usage = out.get("usage") or {}
    print(json.dumps({
        "ok": out.get("ok"), "seat": ns.seat, "model": out.get("model") or seat["model"],
        "via": out.get("via"), "reason": out.get("reason"), "out": str(dest),
        "text_n": len(out.get("text") or ""),
        "usd": out.get("usd") or usage.get("cost"),
        "prompt_tokens": usage.get("prompt_tokens"),
        "cached_tokens": out.get("cached_tokens") if out.get("cached_tokens") is not None
        else usage.get("cached_tokens"),
        "cache_write_tokens": usage.get("cache_write_tokens"),
        "provider": out.get("provider"),
    }))
    return 0 if out.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
