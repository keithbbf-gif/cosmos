#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PS-06 deck feature smoke — attribution contract visible to Studio clients."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((label, bool(ok), str(detail)[:400]))


def main() -> int:
    sys.path.insert(0, str(REPO / "cosmos"))
    from cosmos_portfolio_attribution import (
        UNMEASURED,
        empty_product_spend_totals,
        optional_tags,
        read_tags,
    )

    tags = optional_tags(product="forge", stage="build")
    check("canonical product/stage tags validate",
          tags == {"product": "forge", "stage": "build"})
    check("untagged read is UNATTRIBUTED",
          read_tags({"command": "forge build"})["attribution"] == "UNATTRIBUTED",
          "no command-text classification")
    empty = empty_product_spend_totals()
    check("unavailable product totals are UNMEASURED not zero",
          all(r["settled_usd"] is None and r["kind"] == UNMEASURED for r in empty),
          "n=%d" % len(empty))
    # esc() discipline reminder for any future Studio paint of these fields
    check("attribution module does not emit HTML (esc() stays client-side)",
          "<" not in str(tags) and "&" not in str(tags))

    failed = [(l, d) for l, ok, d in RESULTS if not ok]
    for label, ok, detail in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + detail + "]") if detail else ""))
    print("SELFTEST %s - %d checks (PS-06 deck features smoke)"
          % ("PASS" if not failed else "FAIL", len(RESULTS)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
