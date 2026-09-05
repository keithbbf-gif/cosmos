#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P0 CVM timeout alignment parser (docs/CVM_ARCH.md section 9).

FAST GETs = 8s; VOICE POST = 70s =
OPUS_TIMEOUT_S + GROK_FALLBACK_S + VOICE_TURN_SLACK_S.
Client voice timeout >= OPUS_TIMEOUT_S (the 8s/30s inversion cannot return).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "cosmos"))

BRAIN = ROOT / "cosmos" / "cosmos_brain.py"
MOBILE = ROOT / "kdash" / "mobile.html"
INDEX = ROOT / "kdash" / "index.html"
KOTLIN = Path(r"V:\Ai\tmp\cosmos-android") / (
    "app/src/main/java/com/cosmos/voice/CosmosClient.kt"
)

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _ms_const(src: str, name: str) -> int:
    m = re.search(rf"{re.escape(name)}\s*=\s*([\d_]+)", src)
    if not m:
        raise AssertionError(f"{name} missing")
    return int(m.group(1).replace("_", ""))


def main() -> int:
    import cosmos_brain as cb

    check("brain file on disk", lambda: BRAIN.is_file())
    check("OPUS_TIMEOUT_S is 45.0 (unchanged)",
          lambda: cb.OPUS_TIMEOUT_S == 45.0)
    check("OPUS + GROK_FALLBACK + SLACK == 70",
          lambda: (cb.OPUS_TIMEOUT_S + cb.GROK_FALLBACK_S
                   + cb.VOICE_TURN_SLACK_S) == 70.0)
    check("voice_client_timeout_s() == 70.0",
          lambda: cb.voice_client_timeout_s() == 70.0)
    check("voice_client_timeout_s() >= OPUS_TIMEOUT_S",
          lambda: cb.voice_client_timeout_s() >= cb.OPUS_TIMEOUT_S)

    html = MOBILE.read_text(encoding="utf-8")
    check("mobile FETCH_TO_MS == 8000",
          lambda: _ms_const(html, "FETCH_TO_MS") == 8000)
    check("mobile VOICE_TO_MS == 70000",
          lambda: _ms_const(html, "VOICE_TO_MS") == 70000)
    check("mobile abort uses budget, not FETCH_TO_MS only",
          lambda: "timeout after \"+(budget/1000)" in html)

    idx = INDEX.read_text(encoding="utf-8")
    check("index FETCH_TO_MS == 8000",
          lambda: _ms_const(idx, "FETCH_TO_MS") == 8000)
    check("index VOICE_TO_MS == 70000",
          lambda: _ms_const(idx, "VOICE_TO_MS") == 70000)

    check("kotlin CosmosClient on disk", lambda: KOTLIN.is_file())
    if KOTLIN.is_file():
        kt = KOTLIN.read_text(encoding="utf-8")
        check("kotlin READ_TIMEOUT_FAST_MS == 8000",
              lambda: _ms_const(kt, "READ_TIMEOUT_FAST_MS") == 8000)
        check("kotlin READ_TIMEOUT_VOICE_MS == 70000",
              lambda: _ms_const(kt, "READ_TIMEOUT_VOICE_MS") == 70000)
        check("kotlin VOICE ms/1000 >= OPUS_TIMEOUT_S",
              lambda: (_ms_const(kt, "READ_TIMEOUT_VOICE_MS") / 1000)
              >= cb.OPUS_TIMEOUT_S)
        check("kotlin voice path selects VOICE timeout",
              lambda: "READ_TIMEOUT_VOICE_MS" in kt
              and "/api/v1/voice" in kt)

    ok = all(p for _, p, _ in RESULTS)
    for label, passed, err in RESULTS:
        print(("PASS" if passed else "FAIL") + "  " + label
              + (("  " + err) if err else ""))
    print("result: " + ("ok" if ok else "FAIL")
          + f"  {sum(1 for _, p, _ in RESULTS if p)}/{len(RESULTS)}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
