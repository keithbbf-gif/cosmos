#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pin predecessor: cache hit claimed without measured cached_tokens.

    py -3.14 cosmos/_fail_p14_precache_against_old.py
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent / "cosmos"
OUT = HERE / "_fail_p14_precache_against_old.json"


def old_claim_hit(usage: dict) -> dict:
    """Pre-P14: green hit from intent, not vendor cached_tokens."""
    return {"cache_hit": True, "cached_tokens": usage.get("cached_tokens")}


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="p14_old_"))
    _ = td  # bite documents behavior, not disk layout
    usage_no_cached = {"prompt_tokens": 900, "completion_tokens": 50}
    rec = old_claim_hit(usage_no_cached)
    rec = {
        "old_claims_hit": rec["cache_hit"] is True,
        "old_cached_tokens_absent": rec.get("cached_tokens") is None,
        "no_naked_first_query_type": True,
        "no_fabricated_cache_hit_type": True,
    }
    rec["predecessor_precache_open"] = all(rec.values())
    OUT.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec["predecessor_precache_open"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
