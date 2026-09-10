#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P14 precache gate: NAKED_FIRST_QUERY and FABRICATED_CACHE_HIT."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_openrouter_rail import OpenRouterRail, cache_family, tag_preload  # noqa: E402
from cosmos_precache import (  # noqa: E402
    PrecacheError, assert_cache_hit_measured, assert_not_naked_first_query,
    measure_cached,
)


def test_naked_first_query_refused():
    try:
        assert_not_naked_first_query(
            [{"role": "user", "content": "build the gate"}],
            first_in_family=True,
        )
    except PrecacheError as e:
        assert e.kind == "NAKED_FIRST_QUERY"
    else:
        raise AssertionError("untagged first query must NAKED_FIRST_QUERY")


def test_user_ping_exempt():
    assert_not_naked_first_query(
        [{"role": "user", "content": "ping"}], first_in_family=True)


def test_fabricated_cache_hit_refused():
    try:
        assert_cache_hit_measured(claimed_hit=True, usage_fold={"prompt_tokens": 1})
    except PrecacheError as e:
        assert e.kind == "FABRICATED_CACHE_HIT"
    else:
        raise AssertionError("hit claim without cached_tokens must refuse")


def test_dispatch_measures_cached_tokens():
    td = Path(tempfile.mkdtemp(prefix="p14t_"))
    keyp = td / "key.txt"
    keyp.write_text("sk-test\n", encoding="utf-8")
    spec = {"base": "https://openrouter.ai/api/v1", "timeout_s": 5}
    tagged = tag_preload([
        {"role": "system", "content": "STABLE"},
        {"role": "user", "content": "tail"},
    ])

    def fake_http(method, path, body=None):
        return 200, {}, {
            "model": body.get("model"),
            "choices": [{"message": {"role": "assistant", "content": "x"}}],
            "usage": {
                "prompt_tokens": 2,
                "completion_tokens": 1,
                "prompt_tokens_details": {"cached_tokens": 99},
            },
        }

    rail = OpenRouterRail(keyp, spec, http=fake_http)
    rec = rail.dispatch({
        "model": "z-ai/glm-5.3-flash",
        "messages": tagged,
        "prompt_cache_key": cache_family(model="z-ai/glm-5.3-flash", prefix="STABLE"),
    })
    assert rec["ok"] is True
    assert rec["precache"]["cached_tokens"] == 99


def main() -> int:
    test_naked_first_query_refused()
    test_user_ping_exempt()
    test_fabricated_cache_hit_refused()
    test_dispatch_measures_cached_tokens()
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
