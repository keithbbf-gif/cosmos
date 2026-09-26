#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OpenRouter CODE-propose seat. Same cached prefix. Tail = CODE_PROPOSE.

    py -3.14 work_orders\\ccr\\_code_or_seat.py --seat glm --out ...
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(r"V:\A\Ai\COSMOS")
LIVE = ROOT / "live"
IN = ROOT / "work_orders" / "ccr" / "CREW" / "IN"
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_paths import CosmosPaths  # noqa: E402
from cosmos_openrouter_rail import (  # noqa: E402
    CHAT_PATH, FLEX_MODELS, OPENAI_FLEX, OpenRouterRail, cache_family,
    fold_usage, key_path_for, load_spec, model_refused, spec_path_for,
    _message_text,
)

# Fat CACHE_FAT seats. Keith 2026-09-10: GLM + DS V4 Flash are **1.4M**.
# Luna family 1.1M. Ling + Solar stay cut (window + low COD).
# Two DS V4 Flash slugs = two OR provider queues (Keith 2026-09-10).
# ds = 0731 GA (1.3M, $0.05/$0.16). ds0423 = 0423 (1.0M). Not Pro. Not v4.1.
# Keith 2026-09-10 try: Qwen3.8 Flash, Nemotron 3.5 Lightning (paid), Codestral.
SEATS = {
    "luna": "openai/gpt-5.6-luna",
    "luna-pro": "openai/gpt-5.6-luna-pro",
    "sol": "openai/gpt-5.6-sol",
    "terra": "openai/gpt-5.6-terra",
    "glm": "z-ai/glm-5.3-flash",
    "ds": "deepseek/deepseek-v4-flash-0731",
    "ds0423": "deepseek/deepseek-v4-flash",
    "qwen": "qwen/qwen3.8-flash",
    "nemo": "nvidia/nemotron-3.5-lightning",
    "mistral": "mistralai/codestral-2508",
    "llama": "meta-llama/llama-4-maverick",
    "muse": "meta/muse-spark-1.2-contributor",
    "oss": "openai/gpt-oss-120b",
    "hy3preview": "tencent/hy3-preview",
    "nemo35f": "nvidia/nemotron-3.5-lightning:free",
    "northmini": "cohere/north-mini-code:free",
    "lagunaxs": "poolside/laguna-xs-2.1:free",
    "dots3": "dots-studio/dots3-note-preview:free",
    "luna6": "openai/gpt-6-luna",
    "nexmini": "nex-agi/nex-n2.5-mini",
    "lingvl": "inclusionai/ling-3.0-flash-vl:free",
    "qwen37": "qwen/qwen3.7-flash",
    "nanoomni": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "qwen3635b": "qwen/qwen3.6-35b-a3b",
    "gemma426b": "google/gemma-4-26b-a4b:free",
    "qwen27f": "qwen/qwen3.8-27b:free",
    "lagunas": "poolside/laguna-s-2.1:free",
    "hy3": "tencent/hy3",
    "qwenomni": "qwen/qwen3.8-omni-flash",
    "solarpro4": "upstage/solar-pro-4",
    "inklingf": "thinkingmachines/inkling:free",
    "mimo25": "xiaomi/mimo-v2.5",
    "gemma431b": "google/gemma-4-31b",
}
SEAT_TAG = {
    "luna": "You are lane **Luna Flex** (`openai/gpt-5.6-luna`, 1.1M). Full patent-ideas preload. Not Ling. Not Solar.",
    "luna-pro": "You are lane **Luna Pro Flex** (`openai/gpt-5.6-luna-pro`, 1.1M). Full patent-ideas preload. Not a swap of luna.",
    "sol": "You are lane **Sol** (`openai/gpt-5.6-sol`). Major review. Full patent-ideas preload. The five-part plan MUST appear in message content. Empty content is failure.",
    "terra": "You are lane **Terra Flex** (`openai/gpt-5.6-terra`, 1.1M). Full patent-ideas preload. Escalate seat.",
    "glm": "You are lane **GLM** (`z-ai/glm-5.3-flash`, 1.4M). Full patent-ideas preload. Not sliced. Not Ling. Not Solar.",
    "ds": "You are lane **DS V4 Flash 0731 GA** (`deepseek/deepseek-v4-flash-0731`, 1.3M). Full patent-ideas preload. Not sliced. Not Ling. Not Solar.",
    "ds0423": "You are lane **DS V4 Flash 0423** (`deepseek/deepseek-v4-flash`, 1.0M). Distinct OR slug from 0731 GA. Full patent-ideas preload. Not sliced. Not Ling. Not Solar.",
    "qwen": "You are lane **Qwen3.8 Flash** (`qwen/qwen3.8-flash`, 1.0M). Distinct family from GLM/DS. Full patent-ideas preload. Not Qwen Max. Not Ling. Not Solar.",
    "nemo": "You are lane **Nemotron 3.5 Lightning** (`nvidia/nemotron-3.5-lightning`, 1.0M). Paid pin, not :free. Full patent-ideas preload. Not Ling. Not Solar.",
    "mistral": "You are lane **Codestral 2508** (`mistralai/codestral-2508`, 256K). Mistral coding. Full patent-ideas preload. Not Devstral. Not Ling. Not Solar.",
    "llama": "You are lane **Llama 4 Maverick** (`meta-llama/llama-4-maverick`, 1.0M). Meta Llama paid pin, not :free Scout. Full patent-ideas preload. Not Ling. Not Solar.",
    "muse": "You are lane **Muse Spark 1.2 Contributor** (`meta/muse-spark-1.2-contributor`, 1.0M). Meta contributor tier $0.10/$0.20. Full patent-ideas preload. Not Ling. Not Solar.",
    "oss": "You are lane **GPT OSS 120B** (`openai/gpt-oss-120b`, 131K). OpenAI open-weight MoE. Not Luna. Not Sol. Not Flex. Full patent-ideas preload. Not Ling. Not Solar.",
}

# Stable preloads — each part gets cache_control. Order is the cache family.
SYSTEM_PRELOADS = (
    IN / "CACHE_RULE.md",
    IN / "ELEGANT_OR_SYSTEM.md",
    IN / "CODING_GUIDELINES.md",
)
USER_PRELOADS = (
    IN / "CODER_PRELOAD_PATENT_IDEAS_CACHE.md",
    IN / "ELEGANT_PLAN.md",
)
CACHE_EPHEMERAL = {"type": "ephemeral"}
CACHE_BREAKPOINT = {"mode": "explicit"}


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def _cached_part(text: str, *, flex: bool, breakpoint: bool = False) -> dict:
    part = {
        "type": "text",
        "text": text,
        "cache_control": dict(CACHE_EPHEMERAL),
    }
    if flex and breakpoint:
        part["prompt_cache_breakpoint"] = dict(CACHE_BREAKPOINT)
    return part


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--seat", required=True, choices=sorted(SEATS))
    p.add_argument("--out", required=True)
    p.add_argument("--timeout", type=int, default=900)
    p.add_argument("--max-tokens", type=int, default=16384)
    p.add_argument("--item", default="", help="Replace CODE_PROPOSE tail with this ITEM.")
    p.add_argument("--thin", action="store_true",
                   help="legacy: house pack without patent (prefer --pack).")
    p.add_argument("--pack", choices=("fat", "house"), default="",
                   help="Pair pack. fat=patent 407k. house=no patent, still >thin.")
    ns = p.parse_args(argv)
    model = SEATS[ns.seat]
    from _pair_pack import (  # noqa: E402
        FAT_MIN_CTX, NO_PATENT_SEATS, OR_WINDOW, system_texts, user_cached_texts,
    )
    kind = ns.pack or ("house" if ns.thin else "fat")
    win = OR_WINDOW.get(ns.seat, 1_000_000)
    if ns.seat in NO_PATENT_SEATS:
        kind = "house"
    if kind == "fat" and win < FAT_MIN_CTX:
        raise SystemExit(
            f"REFUSED: seat {ns.seat} ctx {win} cannot hold fat patent pack; use --pack house"
        )
    flex = model in FLEX_MODELS
    sys_parts = []
    sys_blob = []
    for t in system_texts():
        sys_parts.append(_cached_part(t, flex=flex))
        sys_blob.append(t)
    tab = Path(ns.item).stem if ns.item else ""
    user_cached = user_cached_texts(kind, tab)
    user_blob = list(user_cached)
    pack = user_cached[0] if kind == "fat" else ""
    item = _read(Path(ns.item)).rstrip() if ns.item else _read(IN / "CODE_PROPOSE.md").rstrip()
    tail = "\n\n".join((
        "--- TASK ---",
        item,
        SEAT_TAG.get(ns.seat, f"You are lane **{ns.seat}** (`{model}`). Full patent-ideas preload. Not Ling. Not Solar."),
        "PROPOSE only. Unified diff first. Do not write the live tree.",
    ))
    # Last cached user part gets the Flex breakpoint (P11: static then tail).
    user_parts = []
    for i, t in enumerate(user_cached):
        last = i == len(user_cached) - 1
        user_parts.append(_cached_part(t, flex=flex, breakpoint=last))
    user_parts.append({"type": "text", "text": tail})
    fat_key_src = "\n\n".join(sys_blob + user_blob)
    paths = CosmosPaths(str(LIVE))
    t0 = datetime.now().astimezone().isoformat(timespec="seconds")
    why = model_refused(model)
    out = Path(ns.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if why:
        rec = {"ok": False, "reason": "REFUSED", "detail": why, "text": ""}
    else:
        spec = load_spec(spec_path_for(paths))
        spec["timeout_s"] = max(int(spec.get("timeout_s") or 120), int(ns.timeout))
        rail = OpenRouterRail(key_path_for(paths, spec), spec)
        messages = [
            {"role": "system", "content": sys_parts},
            {"role": "user", "content": user_parts},
        ]
        prov = {"allow_fallbacks": False}
        if flex:
            prov["only"] = [OPENAI_FLEX]
            prov["order"] = [OPENAI_FLEX]
        key = cache_family(model=model, prefix=fat_key_src)
        body = {
            "model": model,
            "messages": messages,
            "max_tokens": int(ns.max_tokens),
            "stream": False,
            "provider": prov,
            "prompt_cache_key": key,
            "session_id": key,
        }
        if flex:
            body["prompt_cache_options"] = {"mode": "explicit", "ttl": "30m"}
        if ns.seat == "sol":
            body["reasoning"] = {"max_tokens": 2048}
        status, obj, last_err = 0, {}, ""
        for attempt in range(6):
            status, _hdrs, obj = rail._call("POST", CHAT_PATH, body)
            obj = obj if isinstance(obj, dict) else {}
            err = obj.get("error") if isinstance(obj.get("error"), dict) else None
            last_err = (err or {}).get("message") if err else ""
            if status == 200 and obj.get("model"):
                break
            if status not in (429, 502) or attempt == 5:
                break
            time.sleep((10, 25, 45, 70, 100, 120)[attempt])
        bound = obj.get("model")
        text = _message_text(obj)
        rec = {
            "ok": status == 200 and bool(bound) and bool(text),
            "reason": (
                "EMPTY" if status == 200 and bound and not text
                else (None if status == 200 else f"HTTP_{status}")
            ),
            "model": bound,
            "model_requested": model,
            "via": "openrouter",
            "http": status,
            "text": text or "",
            "detail": last_err or "",
            "usage": fold_usage(obj),
            "prompt_cache_key": key,
        }
    usage = rec.get("usage") if isinstance(rec.get("usage"), dict) else {}
    prompt_chars = sum(len(x) for x in sys_blob + user_blob) + len(tail)
    body_out = {
        "schema": "cosmos-code-or-seat/1",
        "ok": bool(rec.get("ok")),
        "seat": ns.seat,
        "model": rec.get("model") or model,
        "via": rec.get("via") or "openrouter",
        "reason": rec.get("reason"),
        "http": rec.get("http"),
        "t0": t0,
        "t1": datetime.now().astimezone().isoformat(timespec="seconds"),
        "text": rec.get("text") or "",
        "detail": rec.get("detail") or "",
        "usage": usage,
        "usd": usage.get("cost"),
        "cached_tokens": usage.get("cached_tokens"),
        "cache_write_tokens": usage.get("cache_write_tokens"),
        "prompt_tokens": usage.get("prompt_tokens"),
        "prompt_chars": prompt_chars,
        "pack_chars": len(pack),
        "n_cached_parts": len(sys_parts) + len(user_parts) - 1,
        "flex": flex,
        "prompt_cache_key": rec.get("prompt_cache_key"),
        "note": (
            "Error review. Same cached prefix as elegant. "
            "Tail ERROR_TASK untagged. Not Luna Pro. Not Ling. Not Solar."
        ),
    }
    out.write_text(json.dumps(body_out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": body_out["ok"], "seat": ns.seat, "model": body_out["model"],
        "reason": body_out["reason"], "out": str(out),
        "text_len": len(body_out["text"]),
        "prompt_chars": body_out["prompt_chars"],
        "cached_tokens": body_out["cached_tokens"],
        "cache_write_tokens": body_out["cache_write_tokens"],
        "usd": body_out["usd"],
        "n_cached_parts": body_out["n_cached_parts"],
    }))
    return 0 if body_out["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
