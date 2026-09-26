#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P11: put PREFIX+slices in one cached system block, then a second call to measure hit.

    py -3.14 work_orders\\ccr\\PACKAGE_V3\\_pkg_v3_cache_prime.py --model deepseek/deepseek-v4-pro-0813 --seat dspro
"""
from __future__ import annotations

import argparse
import json
import sys
from hashlib import sha256
from pathlib import Path

ROOT = Path(r"V:\A\Ai\COSMOS")
HERE = Path(__file__).resolve().parent
LIVE = ROOT / "live"
FAT_PATH = HERE / "CACHE_FAT.md"
OUT_DIR = HERE / "OUT"


def fat_bytes() -> str:
    prefix = (HERE / "PREFIX.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    q2 = (HERE / "ITEMS" / "Q2.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    marker = "--- LIVE SLICES ---"
    slices = q2.split(marker, 1)[1] if marker in q2 else q2
    blob = prefix.rstrip() + "\n\n" + marker + "\n" + slices.lstrip()
    if FAT_PATH.is_file():
        old = FAT_PATH.read_text(encoding="utf-8").replace("\r\n", "\n")
        if old != blob:
            raise SystemExit("CACHE_FAT.md bytes changed — P11 stop")
        return old
    FAT_PATH.write_text(blob, encoding="utf-8", newline="\n")
    return blob


def call(model: str, fat: str, user: str, max_tokens: int) -> dict:
    sys.path.insert(0, str(ROOT / "cosmos"))
    from cosmos_openrouter_rail import (
        CHAT_PATH, OpenRouterRail, cache_family, fold_usage, key_path_for,
        load_spec, spec_path_for, _message_text,
    )
    from cosmos_paths import CosmosPaths
    paths = CosmosPaths(str(LIVE))
    spec = dict(load_spec(spec_path_for(paths)))
    spec["timeout_s"] = max(int(spec.get("timeout_s") or 120), 300)
    rail = OpenRouterRail(key_path_for(paths, spec), spec)
    pck = cache_family(model=model, prefix=fat)
    body = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": [{
                    "type": "text",
                    "text": fat,
                    "cache_control": {"type": "ephemeral"},
                }],
            },
            {"role": "user", "content": user},
        ],
        "max_tokens": int(max_tokens),
        "stream": False,
        "provider": {"allow_fallbacks": False},
        "prompt_cache_key": pck,
        "session_id": pck,
    }
    status, _hdrs, obj = rail._call("POST", CHAT_PATH, body)
    obj = obj if isinstance(obj, dict) else {}
    err = obj.get("error") if isinstance(obj.get("error"), dict) else None
    usage = fold_usage(obj)
    return {
        "ok": status == 200 and bool(obj.get("model")),
        "http": status,
        "model": obj.get("model"),
        "model_requested": model,
        "prompt_cache_key": pck,
        "fat_sha12": sha256(fat.encode("utf-8")).hexdigest()[:12],
        "fat_bytes": len(fat.encode("utf-8")),
        "text": (_message_text(obj) or "")[:200],
        "detail": (err or {}).get("message") if err else "",
        "error": err,
        "usage": usage,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--seat", required=True)
    ns = p.parse_args()
    fat = fat_bytes()
    write = call(ns.model, fat, "P11 cache write. Reply with the single word PONG.", 16)
    hit = None
    if write.get("ok"):
        hit = call(ns.model, fat, "P11 cache hit check. Reply with the single word PONG.", 16)
    rec = {"schema": "cosmos-package-v3-cache/1", "seat": ns.seat,
           "write": write, "hit": hit}
    dest = OUT_DIR / ("CACHE_" + ns.seat + ".json")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    wu = (write.get("usage") or {})
    hu = (hit or {}).get("usage") or {}
    print(json.dumps({
        "seat": ns.seat,
        "write_ok": write.get("ok"),
        "write_http": write.get("http"),
        "write_usd": wu.get("cost"),
        "write_cached": wu.get("cached_tokens"),
        "write_cache_write": wu.get("cache_write_tokens"),
        "write_prompt": wu.get("prompt_tokens"),
        "hit_ok": (hit or {}).get("ok"),
        "hit_http": (hit or {}).get("http"),
        "hit_usd": hu.get("cost"),
        "hit_cached": hu.get("cached_tokens"),
        "hit_cache_write": hu.get("cache_write_tokens"),
        "hit_prompt": hu.get("prompt_tokens"),
        "detail": ((hit or write).get("detail") or "")[:200],
        "out": str(dest),
    }))
    return 0 if write.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
