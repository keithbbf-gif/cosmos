#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Loopback DT auto-connect vs Tailscale bearer. No live Core required."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_service import _is_loopback_peer, _request_authed  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def main() -> int:
    check("127.0.0.1 is loopback", lambda: _is_loopback_peer("127.0.0.1"))
    check("::1 is loopback", lambda: _is_loopback_peer("::1"))
    check("localhost is loopback", lambda: _is_loopback_peer("localhost"))
    check("IPv4-mapped ::ffff:127.0.0.1 is loopback",
          lambda: _is_loopback_peer("::ffff:127.0.0.1"))
    check("Tailscale CGNAT is NOT loopback",
          lambda: _is_loopback_peer("100.64.1.2") is False)
    check("LAN is NOT loopback",
          lambda: _is_loopback_peer("192.168.1.50") is False)
    check("empty is NOT loopback", lambda: _is_loopback_peer("") is False)
    tok = "secret-for-unit"
    check("loopback + no Authorization is authed (DT auto-connect)",
          lambda: _request_authed("127.0.0.1", "", tok) is True)
    check("loopback + wrong Bearer is still authed (peer is this machine)",
          lambda: _request_authed("127.0.0.1", "Bearer nope", tok) is True)
    check("Tailscale + no Authorization is NOT authed",
          lambda: _request_authed("100.64.1.2", "", tok) is False)
    check("Tailscale + matching Bearer is authed",
          lambda: _request_authed("100.64.1.2", "Bearer " + tok, tok) is True)
    check("Tailscale + wrong Bearer is NOT authed",
          lambda: _request_authed("100.64.1.2", "Bearer nope", tok) is False)
    check("LAN + empty Authorization is NOT authed",
          lambda: _request_authed("192.168.1.50", "", tok) is False)
    bad = 0
    for label, ok, err in RESULTS:
        print(("  [ok] " if ok else "  [FAIL] ") + label + ((" " + err) if err else ""))
        if not ok:
            bad += 1
    print(f"{len(RESULTS) - bad}/{len(RESULTS)} passed")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
