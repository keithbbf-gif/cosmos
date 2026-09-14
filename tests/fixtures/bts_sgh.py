#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contract stub for bts_sgh (xAI Console paid rail).

The live incumbent lives under COSMOS_BTS_ROOT (typically BTS_MESH). This
module exists only so COSMOS tests can prove the ask() contract without
spending: search=True is REFUSED unless spend_ok is true.
"""
from __future__ import annotations


def ask(prompt, search=False, spend_ok=False, **kwargs):
    if search and not spend_ok:
        return {
            "ok": False,
            "kind": "REFUSED",
            "reason": "search requires spend_ok",
            "text": "",
            "rc": 2,
            "node": "bts_sgh",
            "model": "grok-4.6",
        }
    if kwargs.get("force_fail"):
        return {"ok": False, "kind": "BROKE", "text": "", "rc": 2,
                "node": "bts_sgh", "model": "grok-4.6"}
    body = "PONG" if "PONG" in (prompt or "").upper() else f"ECHO: {prompt}"
    return {
        "ok": True,
        "kind": "API",
        "text": body,
        "model": "grok-4.6",
        "usd": 0.004,
        "node": "bts_sgh",
        "rc": 0,
    }
