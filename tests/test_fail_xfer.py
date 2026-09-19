#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fail_xfer: JSONL attempt, wo_partner, board = bucket+picked."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_paths import CosmosPaths, write_sentinel  # noqa: E402
from cosmos_spawn import fail_xfer, wo_partner  # noqa: E402
from cosmos_work_order import drop_order, fold_work_orders  # noqa: E402

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_fail_xfer_"))
    live = td / "live"
    write_sentinel(live, tree_id="fail-xfer")
    (td / "docs").mkdir(parents=True, exist_ok=True)
    (td / "docs" / "WORK_ORDER_SPEC.md").write_text("# spec\n", encoding="utf-8")
    paths = CosmosPaths(live)

    a = {
        "Agent": "xAI | grok | prepaid-orch",
        "Context source": ["docs/WORK_ORDER_SPEC.md [read*]"],
        "Task": "Drive the MOTIF route from WISHLIST/BACKLOG. Drop work in the box.",
        "Target & scope": "queue drop only",
        "Timestamp": "2026-09-19T01:00:00-05:00",
        "Output": "prepaid | result.json",
        "pair_id": "pair-xfer-1",
    }
    b = dict(a)
    b["Task"] = "Drive the MOTIF route from WISHLIST/BACKLOG. partner B"
    drop_a = drop_order(paths, a, order_id="wo-xfer-a")
    drop_b = drop_order(paths, b, order_id="wo-xfer-b")
    rec_a = json.loads(drop_a.read_text(encoding="utf-8"))
    rec_b = json.loads(drop_b.read_text(encoding="utf-8"))

    partner_live = wo_partner(paths, rec_a)
    check("VERIFY 1 wo_partner MEASURED on pair_id",
          lambda: partner_live.get("kind") == "MEASURED"
          and partner_live.get("partner_id") == "wo-xfer-b")

    out = fail_xfer(paths, rec_a, "FAILED", "empty output")
    jsonl = live / "state" / "attempts" / "attempts.jsonl"
    line = json.loads(jsonl.read_text(encoding="utf-8").splitlines()[0])
    board = fold_work_orders(paths)
    failed = fold_work_orders(paths, state="FAILED")
    check("VERIFY 2 fail_xfer writes cosmos-score-attempt/1 and superseded MOTIF",
          lambda: out.get("xfer") == "superseded"
          and line.get("schema") == "cosmos-score-attempt/1"
          and line.get("job") == "wo-xfer-a"
          and jsonl.is_file())
    check("VERIFY 3 WOMB n_total is bucket+picked; failed is archive",
          lambda: board.get("n_total") == 1
          and board.get("n_board") == 1
          and board.get("counts", {}).get("failed") == 1
          and board.get("counts", {}).get("bucket") == 1
          and failed.get("n_shown") == 1
          and (failed.get("rows") or [{}])[0].get("order_id") == "wo-xfer-a")

    failed_n = 0
    for label, ok, err in RESULTS:
        mark = "ok" if ok else "FAIL"
        print(f"  [{mark}] {label}" + (f"  {err}" if err else ""))
        if not ok:
            failed_n += 1
    print(f"result: {'ok' if failed_n == 0 else 'FAILED'}  {len(RESULTS) - failed_n}/{len(RESULTS)}")
    return 0 if failed_n == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
