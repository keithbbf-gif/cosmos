#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P14 precache gate — NAKED_FIRST_QUERY / FABRICATED_CACHE_HIT (PLAN E2)."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_openrouter_rail import (  # noqa: E402
    PrecacheError,
    audit_cache_hit_claim,
    audit_precache_messages,
    cache_family,
    fold_usage,
    is_user_only_ping,
    tag_preload,
    OpenRouterRail,
    VALUE_CODER,
    default_spec,
    CHAT_PATH,
)


def test_user_ping_exempt_naked_agent_not():
    assert is_user_only_ping([{"role": "user", "content": "ping"}])
    assert not is_user_only_ping([{"role": "user", "content": "do the thing"}])
    audit_precache_messages([{"role": "user", "content": "ping"}])
    try:
        audit_precache_messages([{"role": "user", "content": "do the thing"}])
    except PrecacheError as e:
        assert e.kind == "NAKED_FIRST_QUERY"
    else:
        raise AssertionError("naked agent user query must refuse")


def test_untagged_system_is_naked():
    try:
        audit_precache_messages([
            {"role": "system", "content": "PREFIX"},
            {"role": "user", "content": "item"},
        ])
    except PrecacheError as e:
        assert e.kind == "NAKED_FIRST_QUERY"
    else:
        raise AssertionError("untagged preload must refuse")
    tagged = tag_preload([
        {"role": "system", "content": "PREFIX"},
        {"role": "user", "content": "item"},
    ])
    audit_precache_messages(tagged)


def test_fabricated_cache_hit():
    try:
        audit_cache_hit_claim(fold_usage({}), claim_cache_hit=True)
    except PrecacheError as e:
        assert e.kind == "FABRICATED_CACHE_HIT"
    else:
        raise AssertionError("claimed hit without cached_tokens must refuse")
    audit_cache_hit_claim(
        {"cached_tokens": 0, "kind": "MEASURED"},
        claim_cache_hit=True,
    )


def test_cache_family_reused_for_prefix():
    a = cache_family(model=VALUE_CODER, prefix="PREFIX+CACHE_RULE")
    b = cache_family(model=VALUE_CODER, prefix="PREFIX+CACHE_RULE")
    assert a == b
    assert a.startswith("cdeck-or-")


def test_dispatch_surfaces_cached_tokens():
    td = Path(tempfile.mkdtemp(prefix="p14_"))
    keyp = td / "key.txt"
    keyp.write_text("sk-or-test\n", encoding="utf-8")
    spec = default_spec()

    def fake_http(method, path, body=None):
        if method == "POST" and path == CHAT_PATH:
            return 200, {}, {
                "id": "gen-p14",
                "model": body.get("model"),
                "choices": [{"message": {"role": "assistant", "content": "ok"}}],
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 1,
                    "total_tokens": 101,
                    "prompt_tokens_details": {
                        "cached_tokens": 64,
                        "cache_write_tokens": 36,
                    },
                },
            }
        return 404, {}, {}

    rail = OpenRouterRail(keyp, spec, http=fake_http)
    rec = rail.dispatch({
        "model": VALUE_CODER,
        "messages": [
            {"role": "system", "content": "STABLE"},
            {"role": "user", "content": "tail"},
        ],
        "precache_prefix": "STABLE",
    })
    assert rec["ok"]
    assert rec["cached_tokens"] == 64
    assert rec["usage_fold"]["cached_tokens"] == 64


def test_dispatch_naked_user_refused():
    td = Path(tempfile.mkdtemp(prefix="p14n_"))
    keyp = td / "key.txt"
    keyp.write_text("sk-or-test\n", encoding="utf-8")
    rail = OpenRouterRail(keyp, default_spec(), http=lambda *a, **k: (404, {}, {}))
    rec = rail.dispatch({"model": VALUE_CODER, "text": "implement P14 now"})
    assert not rec["ok"]
    assert rec["kind"] == "NAKED_FIRST_QUERY"


def main() -> int:
    test_user_ping_exempt_naked_agent_not()
    test_untagged_system_is_naked()
    test_fabricated_cache_hit()
    test_cache_family_reused_for_prefix()
    test_dispatch_surfaces_cached_tokens()
    test_dispatch_naked_user_refused()
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
