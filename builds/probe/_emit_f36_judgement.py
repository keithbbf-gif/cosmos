#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-measure F-36 live streak + derivation audit. Writes probe/, never cosmos/.

    py -3.14 builds/probe/_emit_f36_judgement.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
LIVE = REPO / "live"
OUT = HERE / "_f36_judgement.json"

sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "cosmos"))
import artifact_freshness as af                                          # noqa: E402
from cosmos_derivation_audit import audit                                # noqa: E402

SOURCES = (
    "cosmos/cosmos_motif_driver.py",
    "cosmos/cosmos_derivation_audit.py",
    "docs/CORE_RESTRUCTURE.md",
)
STALE_S = 20 * 60.0


def main() -> int:
    now = time.time()
    driver = (REPO / "cosmos" / "cosmos_motif_driver.py").read_text(encoding="utf-8")
    canon = (REPO / "docs" / "CORE_RESTRUCTURE.md").read_text(encoding="utf-8")
    ag_path = LIVE / "state" / "motif_agreement.json"
    tr_path = LIVE / "state" / "motif_tracker.json"
    hb_path = LIVE / "logs" / "motif_driver_heartbeat.json"
    ag = json.loads(ag_path.read_text(encoding="utf-8"))
    tr = json.loads(tr_path.read_text(encoding="utf-8"))
    hb = json.loads(hb_path.read_text(encoding="utf-8"))
    rec_audit = audit(REPO / "cosmos")
    age_s = now - float(hb["last_run_epoch"])
    streak = int(ag.get("consecutive_agreements") or 0)
    target = int(ag.get("flip_streak_target") or 0)
    flip_ready = bool(ag.get("flip_ready"))
    clock_alive = age_s <= STALE_S
    # Restraint is justified when the encoded threshold is not yet met AND
    # the clock that earns it is still ticking. A dead clock would turn the
    # 96-tick wait into a parking lot.
    justified = (
        streak < target
        and flip_ready is False
        and clock_alive
        and '"authority": "markdown"' in driver
    )
    rec = {
        "schema": "cosmos-f36-judgement/1",
        "ok": True,
        "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
        "tree_id": "KMesh-COSMOS-live",
        "consecutive_agreements": streak,
        "flip_streak_target": target,
        "ticks_remaining": max(target - streak, 0),
        "flip_ready": flip_ready,
        "agree": bool(ag.get("agree")),
        "ticks_total": ag.get("ticks_total"),
        "ticks_agreed": ag.get("ticks_agreed"),
        "authority": tr.get("authority"),
        "hb_last_run": hb.get("last_run"),
        "hb_last_run_epoch": hb.get("last_run_epoch"),
        "hb_age_s": round(age_s, 1),
        "clock_stale_20min": age_s > STALE_S,
        "clock_alive": clock_alive,
        "driver_hardcodes_markdown": '"authority": "markdown"' in driver,
        "driver_flip_streak_target_96": "FLIP_STREAK_TARGET = 96" in driver,
        "driver_flip_ready_is_advice": "flip_ready is ADVICE" in driver
        or "flip_ready is advice" in driver.lower(),
        "canon_has_21a": "Work order 2.1a" in canon,
        "canon_names_keith_or_cow": "Keith or COW" in canon,
        "audit_ok": rec_audit["ok"],
        "unreviewed_count": rec_audit["unreviewed_count"],
        "open_count": rec_audit["open_count"],
        "open": rec_audit["open"],
        "restraint_justified": justified,
        "restraint_is_excuse": (not justified) and (not flip_ready),
        "whose_judgement": (
            "Threshold: cosmos/cosmos_motif_driver.py FLIP_STREAK_TARGET=96 "
            "(2026-08-30 CC audit; scar 2026-08-26 claim-as-evidence). "
            "Flip actor: Keith or COW on the cosmos/ fence after flip_ready. "
            "This fence (docs/probe) cannot land write_tracker_json or 2.2."
        ),
        "cannot_flip_this_fence": True,
        "writes": 0,
        "live_paths": {
            "agreement": str(ag_path),
            "tracker": str(tr_path),
            "heartbeat": str(hb_path),
        },
    }
    rec["ok"] = (
        rec["driver_hardcodes_markdown"]
        and rec["canon_has_21a"]
        and rec["canon_names_keith_or_cow"]
        and rec["audit_ok"]
        and rec["unreviewed_count"] == 0
        and rec["authority"] == "markdown"
        and rec["flip_ready"] is False
    )
    af.write_stamped(OUT, rec, REPO, SOURCES)
    print(json.dumps({
        "ok": rec["ok"],
        "consecutive_agreements": rec["consecutive_agreements"],
        "flip_streak_target": rec["flip_streak_target"],
        "flip_ready": rec["flip_ready"],
        "restraint_justified": rec["restraint_justified"],
        "restraint_is_excuse": rec["restraint_is_excuse"],
        "hb_age_s": rec["hb_age_s"],
        "open_count": rec["open_count"],
        "artifact": str(OUT),
    }, indent=2))
    return 0 if rec["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
