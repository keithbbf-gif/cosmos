#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: P14 precache gate — naked first query and fabricated cache hit.

    py -3.14 cosmos/_bite_p14_precache.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from cosmos_openrouter_rail import (  # noqa: E402
    PrecacheError,
    audit_cache_hit_claim,
    audit_precache_messages,
    tag_preload,
    OpenRouterRail,
    VALUE_CODER,
    default_spec,
    CHAT_PATH,
)

OUT = HERE / "_bite_p14_precache.json"


def main() -> int:
    naked_system = False
    naked_user = False
    ping_ok = False
    fabricated = False
    measured = False

    try:
        audit_precache_messages([
            {"role": "system", "content": "x"},
            {"role": "user", "content": "y"},
        ])
    except PrecacheError as e:
        naked_system = e.kind == "NAKED_FIRST_QUERY"

    try:
        audit_precache_messages([{"role": "user", "content": "run the farm"}])
    except PrecacheError as e:
        naked_user = e.kind == "NAKED_FIRST_QUERY"

    try:
        audit_precache_messages([{"role": "user", "content": "ping"}])
        ping_ok = True
    except PrecacheError:
        ping_ok = False

    try:
        audit_cache_hit_claim({"kind": "MEASURED"}, claim_cache_hit=True)
    except PrecacheError as e:
        fabricated = e.kind == "FABRICATED_CACHE_HIT"

    tagged = tag_preload([
        {"role": "system", "content": "PREFIX"},
        {"role": "user", "content": "ITEM"},
    ])
    audit_precache_messages(tagged)

    td = Path(tempfile.mkdtemp(prefix="bite_p14_"))
    keyp = td / "key.txt"
    keyp.write_text("sk-or-bite\n", encoding="utf-8")

    def fake_http(method, path, body=None):
        if method == "POST" and path == CHAT_PATH:
            return 200, {}, {
                "model": body.get("model"),
                "choices": [{"message": {"role": "assistant", "content": "ok"}}],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 1,
                    "prompt_tokens_details": {"cached_tokens": 8},
                },
            }
        return 404, {}, {}

    rail = OpenRouterRail(keyp, default_spec(), http=fake_http)
    rec = rail.dispatch({
        "model": VALUE_CODER,
        "messages": tagged,
        "precache_prefix": "PREFIX",
    })
    measured = rec.get("ok") and rec.get("cached_tokens") == 8

    payload = {
        "naked_untagged_system": naked_system,
        "naked_user_agent_query": naked_user,
        "user_ping_exempt": ping_ok,
        "fabricated_cache_hit_refused": fabricated,
        "dispatch_cached_tokens_measured": measured,
    }
    payload["all_bite"] = all(payload.values())
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if payload["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
