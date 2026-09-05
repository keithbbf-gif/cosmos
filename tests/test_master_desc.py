#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: F-68 master description re-render.

The repo-root incumbent (2026-08-25 23:36) does NOT carry the ITERATE
1→8 pin or the competency ratings table. The in-fence render at
docs/COSMOS_MASTER_DESCRIPTION.docx must.

Does not write kernel/ledger/sched/service. Does not touch repo-root
COSMOS_MASTER_DESCRIPTION.docx (outside fence).
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "cosmos"))

from cosmos_master_desc import (  # noqa: E402
    ITERATE_PIN, SCHEMA, default_out, extract_text, render,
)

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def main() -> int:
    incumbent = REPO / "COSMOS_MASTER_DESCRIPTION.docx"
    check("incumbent repo-root docx exists (the stale 2026-08-25 file)",
          lambda: incumbent.is_file())
    old = extract_text(incumbent) if incumbent.is_file() else ""
    check("incumbent lacks ITERATE 1→8 pin",
          lambda: ITERATE_PIN not in old and "not 5→8" not in old
          and "return to stage 1 RESEARCH" not in old)
    check("incumbent lacks COMPETENCY.toml / code-build table",
          lambda: "COMPETENCY.toml" not in old and "code-build" not in old)

    scratch = Path(tempfile.mkdtemp(prefix="cosmos_f68_")) / "out.docx"
    rec = render(scratch, repo=REPO)
    check("render ok", lambda: rec.get("ok") is True and rec.get("bytes", 0) > 1000)
    text = extract_text(scratch)
    check("rendered text carries ITERATE pin",
          lambda: ITERATE_PIN in text)
    check("rendered text names 1→8 not 5→8",
          lambda: "1→8" in text and "not 5→8" in text)
    check("rendered text folds COMPETENCY.toml",
          lambda: "COMPETENCY.toml" in text)
    check("rendered text has code-build and G46 and DOM",
          lambda: "code-build" in text and "G46" in text and "DOM" in text)
    check("rendered text has researched_at 2026-08-26",
          lambda: "2026-08-26" in text)
    check("schema is cosmos-master-desc/1", lambda: SCHEMA == "cosmos-master-desc/1")

    dest = default_out(REPO)
    check("default out is docs/COSMOS_MASTER_DESCRIPTION.docx",
          lambda: dest == REPO / "docs" / "COSMOS_MASTER_DESCRIPTION.docx")
    if dest.is_file():
        live = extract_text(dest)
        check("docs/ render on disk carries the ITERATE pin",
              lambda: ITERATE_PIN in live and "code-build" in live)
    else:
        check("docs/ render on disk carries the ITERATE pin", lambda: False)

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for l, ok, e in RESULTS:
        print(("  OK  " if ok else "  FAIL") + f" {l}" + (f"  {e}" if e else ""))
    live_value = {
        "checks": len(RESULTS),
        "incumbent_chars": len(old),
        "scratch_bytes": rec.get("bytes"),
        "iterate_pin": ITERATE_PIN,
        "docs_out": str(dest),
        "docs_present": dest.is_file(),
    }
    print("LIVE_VALUE", json.dumps(live_value))
    (REPO / "cosmos" / "_f68_master_desc.json").write_text(
        json.dumps({"ok": not bad, "schema": SCHEMA, "live_value": live_value},
                   indent=1) + "\n",
        encoding="utf-8")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
