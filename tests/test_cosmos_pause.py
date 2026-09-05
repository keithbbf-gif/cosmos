#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hermetic tests for cosmos_pause. No live tree, no OA, no schtasks."""
from __future__ import annotations

import json
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_kernel import install  # noqa: E402
from cosmos_paths import CosmosPaths  # noqa: E402
from cosmos_pause import (  # noqa: E402
    classify_pause, is_paused, maybe_auto_resume, read_pause_flag,
)

RESULTS: list[tuple[str, bool, str]] = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def put_flag(paths: CosmosPaths, rec: dict) -> None:
    p = paths.role("state", "control", "PAUSE.flag")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rec), encoding="utf-8")


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_pause_"))
    root = install(td / "live", tree_id="spike-pause")
    paths = CosmosPaths(root)

    check("no flag is RUNNING",
          lambda: classify_pause(None)["class"] == "RUNNING")
    check("no flag is not paused",
          lambda: is_paused(None) is False)

    check("operator HOLD (Keith) is HOLD",
          lambda: classify_pause({
              "state": "PAUSED", "mode": "hold", "set_by": "Keith",
              "reason": "operator HOLD",
          })["class"] == "HOLD")
    check("COW operator HOLD (not tidyup) is HOLD",
          lambda: classify_pause({
              "state": "PAUSED", "mode": "hold", "set_by": "COW",
              "reason": "Keith said PAUSE. Operator HOLD.",
          })["class"] == "HOLD")
    check("TidyUP hold is ARM",
          lambda: classify_pause({
              "state": "PAUSED", "mode": "hold", "set_by": "COW",
              "reason": "TidyUP handoff",
          })["class"] == "ARM")
    check("resume_gate is GATE",
          lambda: classify_pause({
              "state": "PAUSED", "mode": "resume_gate",
              "auto_resume_at": "2099-01-01T00:00:00-05:00",
          })["class"] == "GATE")
    check("unknown mode is HOLD (fail-closed)",
          lambda: classify_pause({"state": "PAUSED", "mode": "weird"})["class"] == "HOLD")
    check("HOLD is paused for retask",
          lambda: is_paused({"state": "PAUSED", "mode": "hold", "set_by": "Keith"}))

    put_flag(paths, {
        "state": "PAUSED", "mode": "hold", "set_by": "Keith",
        "reason": "operator HOLD",
    })
    flag = read_pause_flag(paths)
    rec = maybe_auto_resume(paths, flag)
    check("HOLD maybe_auto_resume does not clear",
          lambda: rec.get("cleared") is False
          and paths.role("state", "control", "PAUSE.flag").is_file())

    past = (datetime.now().astimezone() - timedelta(seconds=5)).isoformat()
    put_flag(paths, {
        "state": "PAUSED", "mode": "resume_gate",
        "auto_resume_at": past,
    })
    rec2 = maybe_auto_resume(paths, read_pause_flag(paths))
    check("GATE past auto_resume_at unlinks",
          lambda: rec2.get("cleared") is True
          and not paths.role("state", "control", "PAUSE.flag").is_file())

    future = (datetime.now().astimezone() + timedelta(hours=1)).isoformat()
    put_flag(paths, {
        "state": "PAUSED", "mode": "resume_gate",
        "auto_resume_at": future,
    })
    rec3 = maybe_auto_resume(paths, read_pause_flag(paths))
    check("GATE future auto_resume_at stays",
          lambda: rec3.get("cleared") is False
          and paths.role("state", "control", "PAUSE.flag").is_file())

    bad = 0
    for label, ok, err in RESULTS:
        mark = "ok" if ok else "FAIL"
        print(f"  [{mark}] {label}" + (f"  {err}" if err else ""))
        if not ok:
            bad += 1
    print(f"{len(RESULTS) - bad}/{len(RESULTS)} passed")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
