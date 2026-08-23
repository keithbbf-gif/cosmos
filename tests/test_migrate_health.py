#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: cosmos_migrate (measured backlog) + cosmos_health (the board).
The migrate test runs against the REAL incumbent TOOLS_REGISTRY.json when present
(native run) and a synthetic registry otherwise - the native run is the measurement."""
from __future__ import annotations
import json, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cosmos_ledger import Ledger
from cosmos_tools import ToolContracts
from cosmos_migrate import Migrator
from cosmos_kernel import Kernel, install
from cosmos_health import HealthBoard

RESULTS = []

def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_mh_"))

    # ================= MIGRATE =================
    led = Ledger(td / "tools.jsonl", b"k", "F5")
    tc = ToolContracts(led)
    mig = Migrator(tc)

    real = Path(r"V:\Ai\BTS_MESH\TOOLS_REGISTRY.json")
    if real.exists():
        rep = mig.ingest(real)
        check("REAL incumbent registry ingested [MEASURED: %d tools]" % rep["total"],
              lambda: rep["total"] > 100)
        check("spike replacements pre-dispositioned REPLACED",
              lambda: rep["by_disposition"].get("REPLACED", 0) >= 4)
        check("UNDECIDED gap is COUNTED, not defaulted silently",
              lambda: rep["undecided_gap"] == rep["total"] - rep["by_disposition"].get("REPLACED", 0))
        check("nothing verified yet (registration is not capability)",
              lambda: rep["verified"] == 0)
        check("re-ingest is idempotent (duplicates skipped, count stable)",
              lambda: mig.ingest(real)["total"] == rep["total"])
    else:
        synth = td / "reg.json"
        synth.write_text(json.dumps([{"id": "bts_paths", "desc": "resolver"},
                                     {"id": "bts_x", "desc": "thing"}]), encoding="utf-8")
        rep = mig.ingest(synth)
        check("synthetic ingest declares + dispositions [SANDBOX - native is the measurement]",
              lambda: rep["total"] == 2 and rep["by_disposition"].get("REPLACED") == 1)

    # ================= HEALTH =================
    root = td / "Cosmos"
    install(root, tree_id="health-test")
    k = Kernel(root, worker="core")
    hb = HealthBoard(k)
    b = hb.run()
    check("board runs GREEN on a healthy kernel", lambda: b["verdict"] == "GREEN")
    check("THE PLANTED FAILURE IS RED (the board can see failure)",
          lambda: b["negative_control_red"] is True)
    check("board run is ledgered", lambda: any(r["event"] == "HEALTH_BOARD"
                                              for r in k.ledger.verify()))
    check("every row carries a detail", lambda: all(r["detail"] for r in b["rows"].values()))

    # a raising row lands RED, does not kill the board
    hb.add_row("bomb", lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    b2 = hb.run()
    check("a RAISING row is a RED row, not a dead board",
          lambda: b2["rows"]["bomb"]["ok"] is False and "RAISED" in b2["rows"]["bomb"]["detail"])
    check("verdict counts the red", lambda: b2["verdict"].startswith("RED"))

    # shared-cause diagnosis: make every row fail the same way
    hb2 = HealthBoard(k)
    for name in list(hb2._rows):
        if "negative control" not in name:
            hb2._rows[name] = lambda: (False, "SANDBOX-DEAD: mount gone")
    b3 = hb2.run()
    check("all-red-one-reason -> SHARED-CAUSE diagnosis (C-46)",
          lambda: b3["diagnosis"] is not None and "SHARED-CAUSE" in b3["diagnosis"])

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label, ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (the backlog is measured; the board can see failure)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_migrate_health():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
