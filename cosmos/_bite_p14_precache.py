#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bite: P14 precache gate. NAKED first query + fabricated hit refuse.

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
    OpenRouterRail, cache_family, fold_usage, tag_preload,
)
from cosmos_precache import (  # noqa: E402
    PrecacheError, assert_cache_hit_measured, assert_not_naked_first_query,
    has_preload_tag, is_user_only_ping, measure_cached,
)

OUT = HERE / "_bite_p14_precache.json"


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_bite_p14_"))
    keyp = td / "key.txt"
    keyp.write_text("sk-test\n", encoding="utf-8")
    spec = {"base": "https://openrouter.ai/api/v1", "timeout_s": 5}

    naked = None
    try:
        assert_not_naked_first_query(
            [{"role": "user", "content": "implement P14 precache gate"}],
            first_in_family=True,
        )
    except PrecacheError as e:
        naked = e.kind

    ping_ok = is_user_only_ping([{"role": "user", "content": "ping"}])
    try:
        assert_not_naked_first_query(
            [{"role": "user", "content": "ping"}], first_in_family=True)
        ping_allowed = True
    except PrecacheError:
        ping_allowed = False

    tagged = tag_preload([
        {"role": "system", "content": "PREFIX"},
        {"role": "user", "content": "ITEM"},
    ])
    preload_ok = has_preload_tag(tagged)
    try:
        assert_not_naked_first_query(tagged, first_in_family=True)
        tagged_allowed = True
    except PrecacheError:
        tagged_allowed = False

    fab = None
    try:
        assert_cache_hit_measured(
            claimed_hit=True,
            usage_fold=fold_usage({"usage": {"prompt_tokens": 100}}),
        )
    except PrecacheError as e:
        fab = e.kind

    hit_ok = None
    try:
        assert_cache_hit_measured(
            claimed_hit=True,
            usage_fold={"cached_tokens": 512, "kind": "MEASURED"},
        )
        hit_ok = True
    except PrecacheError:
        hit_ok = False

    measured = measure_cached(fold_usage({
        "usage": {
            "prompt_tokens": 10,
            "prompt_tokens_details": {"cached_tokens": 8},
        },
    }))

    calls = []

    def fake_http(method, path, body=None):
        calls.append(body)
        return 200, {}, {
            "id": "gen-p14",
            "model": body.get("model"),
            "choices": [{"message": {"role": "assistant", "content": "OK"}}],
            "usage": {
                "prompt_tokens": 4,
                "completion_tokens": 1,
                "total_tokens": 5,
                "prompt_tokens_details": {"cached_tokens": 3},
            },
        }

    rail = OpenRouterRail(keyp, spec, http=fake_http)
    family = cache_family(model="openai/gpt-5.6-luna", prefix="PREFIX")
    ok_dispatch = rail.dispatch({
        "model": "openai/gpt-5.6-luna",
        "messages": tagged,
        "prompt_cache_key": family,
        "first_in_cache_family": True,
    })
    refused = rail.dispatch({
        "model": "openai/gpt-5.6-luna",
        "messages": [{"role": "user", "content": "naked task"}],
        "prompt_cache_key": family,
        "first_in_cache_family": True,
    })
    def fake_no_cache(method, path, body=None):
        return 200, {}, {
            "id": "gen-p14-nc",
            "model": body.get("model"),
            "choices": [{"message": {"role": "assistant", "content": "OK"}}],
            "usage": {"prompt_tokens": 4, "completion_tokens": 1},
        }

    rail_nc = OpenRouterRail(keyp, spec, http=fake_no_cache)
    fab_dispatch = rail_nc.dispatch({
        "model": "openai/gpt-5.6-luna",
        "messages": tagged,
        "prompt_cache_key": family,
        "first_in_cache_family": False,
        "cache_hit_claim": True,
    })

    rec = {
        "naked_first_query_kind": naked,
        "user_ping_allowed": ping_ok and ping_allowed,
        "tagged_preload_ok": preload_ok and tagged_allowed,
        "fabricated_hit_kind": fab,
        "measured_hit_allowed": hit_ok is True,
        "measure_cached_tokens": measured.get("cached_tokens"),
        "dispatch_precache_measured": (ok_dispatch.get("precache") or {}).get(
            "cached_tokens"),
        "dispatch_naked_kind": refused.get("kind"),
        "dispatch_fabricated_kind": fab_dispatch.get("kind"),
        "cache_family_reused": family.startswith("cdeck-luna-"),
    }
    rec["all_bite"] = (
        rec["naked_first_query_kind"] == "NAKED_FIRST_QUERY"
        and rec["user_ping_allowed"] is True
        and rec["tagged_preload_ok"] is True
        and rec["fabricated_hit_kind"] == "FABRICATED_CACHE_HIT"
        and rec["measured_hit_allowed"] is True
        and rec["measure_cached_tokens"] == 8
        and rec["dispatch_precache_measured"] == 3
        and rec["dispatch_naked_kind"] == "NAKED_FIRST_QUERY"
        and rec["dispatch_fabricated_kind"] == "FABRICATED_CACHE_HIT"
        and rec["cache_family_reused"] is True
    )
    OUT.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["all_bite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
