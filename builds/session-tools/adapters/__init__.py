#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Family adapters. Slice-1 wires cowork (catalog wrap) and grok_tui."""
from __future__ import annotations

from . import cowork, grok_tui

WIRED = {
    "cowork": cowork,
    "grok_tui": grok_tui,
}

# Named, not first (ARCH §3.3). Scan emits UNMEASURED + path; n is null.
UNMEASURED = {
    "claude_desktop": r"%APPDATA%\Claude\local-agent-mode-sessions",
    "openwork_native": "opencode.db",
    "cursor": None,
    "codex_oa": None,
    "gemini_gf38": None,
}

OVERFLOW = {"claude_code_raw"}
REJECT = {"sgh_voice", "crash_sit"}


def get(family: str):
    return WIRED.get(family)
