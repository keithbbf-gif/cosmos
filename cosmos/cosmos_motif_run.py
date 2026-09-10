#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MOTIF BUILD / CRITICS run gate — DEFINE-first (P01). Not a MOTIF engine.

Refuses typed when PROBLEM STATEMENT / STATED GOAL is empty. Passing this
gate does not launch Gitur, invent PR traces, or write the live tree.

    py -3.14 cosmos\\cosmos_motif_run.py --selftest
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_motif_define import (  # noqa: E402
    MOTIF_STEP_1,
    MotifDefineError,
    assert_run_stage,
    frozen_statement,
    require_frozen_statement,
    stage_graph,
)

SCHEMA = "cosmos-motif-run/1"


def start(paths, stage: str, *, profile: str = "forge") -> dict:
    sid = assert_run_stage(stage)
    stmt = frozen_statement(paths, profile=profile)
    require_frozen_statement(sid, stmt)
    text = str(stmt.get("text") or "")
    return {
        "schema": SCHEMA,
        "ok": True,
        "stage": sid,
        "profile": str(profile or "forge"),
        "motif_step_1": MOTIF_STEP_1,
        "stages": stage_graph(),
        "define": {
            "text": text[:8000],
            "saved_at": stmt.get("saved_at"),
            "source": stmt.get("source"),
        },
        "does_not_invent_traces": True,
        "does_not_write_live_tree": True,
        "note": (
            "DEFINE-first gate passed. Gitur BUILD/CRITICS dispatch is "
            "separate; this record is not a PR or agent trace."
        ),
    }


def _selftest() -> int:
    import tempfile

    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths
    from cosmos_studio import save_pack

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    td = Path(tempfile.mkdtemp(prefix="cosmos_motif_run_"))
    root = install(td / "live", tree_id="spike-motif-run")
    paths = CosmosPaths(root)

    refused = False
    try:
        start(paths, "build")
    except MotifDefineError as e:
        refused = e.kind == "REFUSED"
    check("BUILD run REFUSED without define", lambda: refused)

    save_pack(paths, {"define": {"text": "WHAT: run. WHY: bite."}})
    rec = start(paths, "critics")
    check(
        "CRITICS run ok with frozen statement",
        lambda: rec["ok"] is True
        and rec["stage"] == "critics"
        and rec["define"]["text"].startswith("WHAT: run")
        and rec["does_not_invent_traces"] is True
        and len(rec["stages"]) == 9,
    )

    bad = False
    try:
        start(paths, "research")
    except MotifDefineError as e:
        bad = e.kind == "BAD_STAGE"
    check("research is not a BUILD/CRITICS run stage", lambda: bad)

    failed = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print(
            "  %s  %s%s"
            % ("OK  " if ok else "FAIL", label, ("  [" + err + "]") if err else "")
        )
    print(
        "SELFTEST %s - %d checks (MOTIF run gate; no Gitur traces)"
        % ("PASS" if not failed else "FAIL", len(results))
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(_selftest())
    raise SystemExit(2)
