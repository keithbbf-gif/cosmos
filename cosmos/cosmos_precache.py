#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P14 precache gate — prompt-cache SOP, not engine KV-cache.

First query in a ``cache_family`` must carry a preload tag (P11 ``tag_preload``).
User-only pings stay untagged. A claimed cache hit without measured
``cached_tokens`` is fabricated compliance.

Reuses ``cache_family`` from ``cosmos_openrouter_rail``; does not touch Core.
"""
from __future__ import annotations

# Same roles as tag_preload — do not import the rail here (dispatch imports us).
_PRELOAD_ROLES = frozenset({"system", "developer"})


class PrecacheError(RuntimeError):
    """kind in {NAKED_FIRST_QUERY, FABRICATED_CACHE_HIT}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _block_has_cache_control(block) -> bool:
    if isinstance(block, dict) and block.get("cache_control"):
        return True
    if isinstance(block, list):
        for part in block:
            if isinstance(part, dict) and part.get("cache_control"):
                return True
    return False


def has_preload_tag(messages) -> bool:
    """True when the first system/developer block carries cache_control."""
    if not isinstance(messages, list):
        return False
    for msg in messages:
        if not isinstance(msg, dict):
            continue
        role = str(msg.get("role") or "").strip().lower()
        if role not in _PRELOAD_ROLES:
            continue
        content = msg.get("content")
        if isinstance(content, str) and content.strip():
            return _block_has_cache_control(content)
        if isinstance(content, list) and content:
            return _block_has_cache_control(content)
        return False
    return False


def _message_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                parts.append(str(part.get("text") or ""))
            elif isinstance(part, str):
                parts.append(part)
        return "".join(parts)
    return ""


def is_user_only_ping(messages) -> bool:
    """Occupancy: the ping, not every user-only message (PROMPT_CACHE)."""
    if not isinstance(messages, list) or len(messages) != 1:
        return False
    msg = messages[0]
    if not isinstance(msg, dict) or str(msg.get("role") or "").lower() != "user":
        return False
    text = _message_text(msg.get("content")).strip().lower()
    if text in ("ping", "pong"):
        return True
    return len(text) <= 8 and text in ("hi", "hello", "ok", "thanks")


def has_stable_prefix(messages) -> bool:
    """True when a non-empty system/developer block is present (preload seat)."""
    if not isinstance(messages, list):
        return False
    for msg in messages:
        if not isinstance(msg, dict):
            continue
        role = str(msg.get("role") or "").strip().lower()
        if role not in _PRELOAD_ROLES:
            continue
        return bool(_message_text(msg.get("content")).strip())
    return False


def assert_not_naked_first_query(messages, *, first_in_family: bool = True) -> None:
    """Refuse an untagged first query when a cache family expects preload."""
    if not first_in_family:
        return
    if is_user_only_ping(messages):
        return
    if has_preload_tag(messages):
        return
    raise PrecacheError(
        "NAKED_FIRST_QUERY",
        "first query in cache family lacks preload tag (PREFIX + CACHE_RULE SOP)",
    )


def measure_cached(usage_fold: dict | None) -> dict:
    """Vendor ``cached_tokens`` only — never invented."""
    fold = usage_fold if isinstance(usage_fold, dict) else {}
    cached = fold.get("cached_tokens")
    measured = isinstance(cached, int) and cached >= 0
    return {
        "cached_tokens": cached if measured else None,
        "cache_write_tokens": fold.get("cache_write_tokens"),
        "kind": "MEASURED" if measured else "UNMEASURED",
    }


def assert_cache_hit_measured(*, claimed_hit: bool,
                              usage_fold: dict | None) -> None:
    """Refuse a hit claim without positive measured ``cached_tokens``."""
    if not claimed_hit:
        return
    m = measure_cached(usage_fold)
    cached = m.get("cached_tokens")
    if not isinstance(cached, int) or cached <= 0:
        raise PrecacheError(
            "FABRICATED_CACHE_HIT",
            "cache hit claimed without measured cached_tokens",
        )
