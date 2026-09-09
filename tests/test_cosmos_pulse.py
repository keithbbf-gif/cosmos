#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hermetic tests for cosmos_pulse Phase 1. No live tree, no OA, no schtasks."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "cosmos"))

from cosmos_clock import write_heartbeat  # noqa: E402
from cosmos_kernel import install  # noqa: E402
from cosmos_paths import CosmosPaths  # noqa: E402
from cosmos_pulse import (  # noqa: E402
    CLOCK_ID, DEFAULT_INTERVAL_S, HEARTBEAT_NAME, REQUIRED_CLOCKS,
    SHADOW_HEARTBEAT_NAME, WD2_SHIM_NAME, poll_once,
)

RESULTS: list[tuple[str, bool, str]] = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_pulse_"))
    root = install(td / "live", tree_id="spike-pulse")
    paths = CosmosPaths(root)

    qret = paths.queue() / "pulse_collect_proof_result.json"
    qret.parent.mkdir(parents=True, exist_ok=True)
    qret.write_text(json.dumps({
        "ok": True, "agent": "G46", "summary": "pulse-collect-pong",
    }), encoding="utf-8")

    rec = poll_once(str(root))
    check("RUNNING tick ok", lambda: rec.get("ok") is True)
    check("RUNNING not paused", lambda: rec.get("paused") is False)
    check("collect runs on the pulse",
          lambda: isinstance(rec.get("collect"), dict)
          and rec["collect"].get("ok") is True)
    check("pulse rewrites cdeck feed via existing poll_once",
          lambda: isinstance(rec.get("feed"), dict)
          and rec["feed"].get("ok") is True
          and rec["heartbeat"].get("claim") is False)
    check("pool is the claim_next; cosmos_run is double-claim",
          lambda: rec["heartbeat"].get("runner") == "pool"
          and rec["heartbeat"].get("cosmos_run") == "double-claim")
    check("new result landed this tick",
          lambda: int(rec["collect"].get("new_this_tick") or 0) >= 1)
    check("no claim / no dispatch",
          lambda: rec["heartbeat"].get("claim") is False
          and rec["heartbeat"].get("dispatch") is False)
    check("oa_api lane named PAUSED_LANE",
          lambda: rec["heartbeat"].get("oa_api") == "PAUSED_LANE")
    check("interval is 15s", lambda: DEFAULT_INTERVAL_S == 15.0)
    check("CLOCK_ID is 27", lambda: CLOCK_ID == 27)
    check("pulse heartbeat written",
          lambda: paths.logs(HEARTBEAT_NAME).is_file())
    check("default does not shim wd2",
          lambda: rec.get("shim_wd2") is None
          and not paths.logs(WD2_SHIM_NAME).is_file())
    check("P0 due-set is 26/26 resident.keep",
          lambda: rec.get("due_n") == REQUIRED_CLOCKS == 26
          and rec["heartbeat"].get("phase") == "P0"
          and rec["heartbeat"].get("shadow_n") == 26)
    check("P0 writes a distinct SHADOW heartbeat",
          lambda: rec.get("shadow") is not None
          and paths.logs(SHADOW_HEARTBEAT_NAME).is_file()
          and json.loads(paths.logs(SHADOW_HEARTBEAT_NAME).read_text(
              encoding="utf-8")).get("phase") == "P0")
    write_heartbeat(paths.role("logs", "collector_heartbeat.json"),
                    "cosmos-collector",
                    extra={"tick": "idle", "index_rows": 7}, polls=1,
                    interval_s=30.0)
    rec_r = poll_once(str(root))
    check("fresh collector heartbeat is reused (no second walk)",
          lambda: rec_r.get("collect", {}).get("tick") == "reuse"
          and rec_r["collect"].get("index_rows") == 7)

    flag = paths.role("state", "control", "PAUSE.flag")
    flag.parent.mkdir(parents=True, exist_ok=True)
    flag.write_text(json.dumps({
        "state": "PAUSED", "mode": "hold", "set_by": "Keith",
        "reason": "operator HOLD until review",
    }), encoding="utf-8")
    rec2 = poll_once(str(root), shim_wd2=True)
    check("HOLD tick state=PAUSED",
          lambda: rec2["heartbeat"].get("state") == "PAUSED"
          and rec2.get("pause_class") == "HOLD")
    check("HOLD still collects (in-flight returns)",
          lambda: rec2.get("collect", {}).get("ok") is True)
    check("HOLD still drops zero agents",
          lambda: rec2["heartbeat"].get("assigned_this_pass") == 0)
    check("HOLD does not clear the flag",
          lambda: flag.is_file())
    check("--shim-wd2 writes watchdog2 heartbeat",
          lambda: paths.logs(WD2_SHIM_NAME).is_file()
          and json.loads(paths.logs(WD2_SHIM_NAME).read_text(encoding="utf-8")
                         ).get("shim_from") == "pulse")

    bad = 0
    for label, ok, err in RESULTS:
        mark = "ok" if ok else "FAIL"
        print(f"  [{mark}] {label}" + (f" {err}" if err else ""))
        if not ok:
            bad += 1
    print(f"{len(RESULTS) - bad}/{len(RESULTS)} passed")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
