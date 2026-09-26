#!/usr/bin/env python3
"""GLM Flash Judge #587. Do not run until Keith says test."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(r"V:\A\Ai\COSMOS")
sys.path.insert(0, str(ROOT / "cosmos"))
from cosmos_openrouter_rail import (  # noqa: E402
    CHAT_PATH,
    VALUE_CODER,
    OpenRouterRail,
    _message_text,
    cache_family,
    fold_usage,
    tag_preload,
)

PREFIX = (ROOT / "work_orders" / "ccr" / "hero_glm" / "L4_WRAPPER.md").read_text(encoding="utf-8")
ITEM = (ROOT / "docs" / "CANON_PEN.md").read_text(encoding="utf-8")
TAIL = (
    "JUDGE. First line KEEP or DROP or HOLD then one sentence. "
    "Then findings or NONE. Do not merge.\n\n" + ITEM
)


def main() -> int:
    rail = OpenRouterRail(ROOT / "live" / "config" / "openrouter_api_key.txt", {"timeout_s": 180})
    messages = [
        {"role": "system", "content": PREFIX},
        {"role": "user", "content": TAIL},
    ]
    body = {
        "model": VALUE_CODER,
        "messages": tag_preload(messages, flex=False),
        "max_tokens": 4096,
        "stream": False,
        "provider": {"allow_fallbacks": False},
    }
    pck = cache_family(model=VALUE_CODER, prefix=PREFIX)
    body["prompt_cache_key"] = pck
    status, _h, obj = rail._call("POST", CHAT_PATH, body)  # noqa: SLF001
    text = _message_text(obj if isinstance(obj, dict) else {})
    rec = {
        "http": status,
        "model": obj.get("model") if isinstance(obj, dict) else None,
        "usage_fold": fold_usage(obj if isinstance(obj, dict) else {}),
        "text": text,
        "err": (obj.get("error") if isinstance(obj, dict) else None),
    }
    out = ROOT / "work_orders" / "ccr"
    (out / "JUDGE_GLM_PR587.json").write_text(json.dumps(rec, indent=1), encoding="utf-8")
    (out / "JUDGE_GLM_PR587_last.txt").write_text(text, encoding="utf-8")
    print(json.dumps({k: rec.get(k) for k in ("http", "model", "usage_fold", "err")}, default=str))
    print(text[:1500])
    return 0 if status == 200 and text else 2


if __name__ == "__main__":
    raise SystemExit(main())
