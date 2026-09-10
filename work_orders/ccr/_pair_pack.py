#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Identical pair packs. Both mouths on a tab get the same cached prefix.

    fat   — patent 407k + plan + features + CODE_CDECK. Use when min(pair ctx) >= 250k.
    house — no patent; still fatter than --thin. Use for oss 131k / llama routed 128k.

Tail (item + seat tag) is the only per-mouth difference. P11: prefix identical, identity last.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(r"V:\A\Ai\COSMOS")
IN = ROOT / "work_orders" / "ccr" / "CREW" / "IN"

UI = ROOT / "builds" / "cdeck" / "ui"
SYSTEM_FILES = (
    IN / "CACHE_RULE.md",
    IN / "DEEP_CONTEXT.md",
    IN / "ELEGANT_OR_SYSTEM.md",
    IN / "CODING_GUIDELINES.md",
)
FAT_USER_FILES = (
    IN / "CODER_PRELOAD_PATENT_IDEAS_CACHE.md",
    IN / "ELEGANT_PLAN.md",
    ROOT / "builds" / "cdeck" / "FEATURES_KEITH.md",
    IN / "CODE_CDECK.md",
)
HOUSE_USER_FILES = (
    IN / "ELEGANT_PLAN.md",
    ROOT / "builds" / "cdeck" / "FEATURES_KEITH.md",
    IN / "CODE_CDECK.md",
    ROOT / "builds" / "cdeck" / "ORCH_HOME_SPEC.md",
)
# Live files for the ITEM tab — same bytes for both mouths. Cap keeps oss/llama under window.
TAB_CONTEXT = {
    "skins": (UI / "deck_profiles.js", UI / "deck_sfx.js", UI / "header.css"),
    "gitur": (UI / "deck_gitur.js",),
    "tools": (UI / "app.js",),
    "recents": (UI / "app.js",),
    "jobs": (UI / "app.js",),
    "spend": (UI / "app.js",),
    "voice": (UI / "header.js",),
    "surfaces": (UI / "deck_more.html",),
}
TAB_CONTEXT_CAP = 80_000

# Routed ctx (OpenRouter catalog 2026-09-10). Vertex GEM brothers = 1M.
OR_WINDOW = {
    "oss": 131072,
    "llama": 128000,
    "mistral": 256000,
    "nemo": 262144,
    "qwen": 1000000,
    "muse": 1048576,
    "ds0423": 1048576,
    "ds": 1310720,
    "glm": 1310720,
}
VX_WINDOW = {
    "gf38": 1_000_000,
    "gemini31pro": 1_000_000,
}
FAT_MIN_CTX = 250_000
# Keith 2026-09-10: no patent preload to DS or Muse. Discrete coding jobs only.
NO_PATENT_SEATS = frozenset({"ds", "ds0423", "muse"})


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def seat_window(seat: str) -> int:
    if seat in VX_WINDOW:
        return VX_WINDOW[seat]
    return OR_WINDOW.get(seat, 1_000_000)


def seat_pack(seat: str) -> str:
    """Per-mouth pack. DS/Muse never get patent. Small ctx never get patent."""
    if seat in NO_PATENT_SEATS:
        return "house"
    return "fat" if seat_window(seat) >= FAT_MIN_CTX else "house"


def pack_kind(a: str, b: str) -> str:
    """Legacy pair-min. Prefer seat_pack per mouth."""
    if a in NO_PATENT_SEATS or b in NO_PATENT_SEATS:
        return "house"
    lo = min(seat_window(a), seat_window(b))
    return "fat" if lo >= FAT_MIN_CTX else "house"


def system_texts() -> list[str]:
    return [t.rstrip() for t in (_read(p) for p in SYSTEM_FILES) if t.strip()]


def tab_context_texts(tab: str) -> list[str]:
    out = []
    used = 0
    for p in TAB_CONTEXT.get(tab or "", ()):
        t = _read(p).rstrip()
        if not t:
            continue
        chunk = "--- FILE %s ---\n%s" % (p.name, t)
        if used + len(chunk) > TAB_CONTEXT_CAP:
            break
        out.append(chunk)
        used += len(chunk)
    return out


def user_cached_texts(kind: str, tab: str = "") -> list[str]:
    if kind == "fat":
        pack = _read(IN / "CODER_PRELOAD_PATENT_IDEAS_CACHE.md")
        if len(pack) < 400000:
            raise SystemExit("REFUSED: patent preload missing or truncated")
        files = FAT_USER_FILES
    elif kind == "house":
        files = HOUSE_USER_FILES
    else:
        raise SystemExit(f"REFUSED: pack kind {kind!r}")
    texts = [t.rstrip() for t in (_read(p) for p in files) if t.strip()]
    texts.extend(tab_context_texts(tab))
    return texts
