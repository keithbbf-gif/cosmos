#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Suite wrapper for cosmos_contracts.

Two gates, deliberately:
  1. the auditor's own selftest -- it must be able to DETECT a contradiction,
     because a checker that cannot fail is not a checker;
  2. the LIVE tree audit -- the contracts in docs/contracts must actually hold.

(2) is the one that would have caught the stale `register_node_rails` docstring
before it cost a regression on 2026-08-30.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_contracts import audit, selftest  # noqa: E402

_REPO = Path(__file__).resolve().parent.parent


def main() -> int:
    rc = selftest()
    if rc != 0:
        print("result: FAIL  auditor selftest failed")
        return rc
    rec = audit(_REPO)
    for r in rec["rows"]:
        print(f"  {'OK  ' if r['ok'] else 'FAIL'}  [{r['severity']}] {r['id']}")
        for e in r["evidence"]:
            if not e["ok"]:
                print(f"          {e['detail']}: {e['file']}")
    print(f"live_value: {rec['verified']}/{rec['contracts']} verified, "
          f"{rec['contradictions']} contradiction(s)")
    print(f"result: {'ok' if rec['ok'] else 'FAIL'}  live tree contracts")
    return 0 if rec["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
