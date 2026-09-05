#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pin F-36 whose-judgement: 2.1a in canon, flip_ready is advice, 96 not yet met.

Bite: staged CORE_RESTRUCTURE.md has no 2.1a. Fail-against-old: 5/5 new pins
FAIL on that incumbent. This suite then pins the live files.

Does not flip write_tracker_json. Does not write cosmos/.

    py -3.14 builds/probe/test_f36_judgement.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "cosmos"))
from cosmos_derivation_audit import audit                                # noqa: E402

STAGE = (REPO / "docs" / "_delme" /
         "predispose_core_restructure_f36_20260831T155400Z" /
         "CORE_RESTRUCTURE.md")
CANON = REPO / "docs" / "CORE_RESTRUCTURE.md"
DRIVER = REPO / "cosmos" / "cosmos_motif_driver.py"
BITE = HERE / "_bite_f36_judgement.json"
FAIL_OLD = HERE / "_fail_f36_against_old.json"
JUDGE = HERE / "_f36_judgement.json"
AG = REPO / "live" / "state" / "motif_agreement.json"

RESULTS: list[tuple[str, bool, str]] = []
LIVE_VALUE: dict = {}


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def main() -> int:
    old = STAGE.read_text(encoding="utf-8")
    live_canon = CANON.read_text(encoding="utf-8")
    driver = DRIVER.read_text(encoding="utf-8")
    bite = json.loads(BITE.read_text(encoding="utf-8")) if BITE.is_file() else {}
    fail = json.loads(FAIL_OLD.read_text(encoding="utf-8")) if FAIL_OLD.is_file() else {}
    judge = json.loads(JUDGE.read_text(encoding="utf-8")) if JUDGE.is_file() else {}
    ag = json.loads(AG.read_text(encoding="utf-8"))
    rec_audit = audit(REPO / "cosmos")

    check("staged incumbent exists (never-delete)", STAGE.is_file)
    check("bite all_bite:true (incumbent had no 2.1a)",
          lambda: bite.get("all_bite") is True
          and bite.get("has_work_order_21a") is False)
    check("fail-against-old all_new_pins_failed:true",
          lambda: fail.get("all_new_pins_failed") is True
          and len(fail.get("failed_pins") or []) == 5)
    check("staged CORE_RESTRUCTURE has no Work order 2.1a",
          lambda: "Work order 2.1a" not in old)
    check("live CORE_RESTRUCTURE has Work order 2.1a",
          lambda: "Work order 2.1a" in live_canon)
    check("2.1a names Keith or COW as the flip actor",
          lambda: "Keith or COW" in live_canon)
    check("2.1a names FLIP_STREAK_TARGET 96",
          lambda: "FLIP_STREAK_TARGET" in live_canon and "96" in live_canon)
    check("2.1a says flip_ready is advice, never an action",
          lambda: "advice, never an action" in live_canon.lower())
    check("2.3 names parse_tracker_markdown as the remaining OPEN site",
          lambda: "parse_tracker_markdown" in live_canon
          and "OPEN remaining" in live_canon)
    check("runtime-binding gate cannot pass while authority is markdown",
          lambda: "cannot pass" in live_canon.lower()
          and '"markdown"' in live_canon)
    check("driver still hard-codes authority markdown",
          lambda: '"authority": "markdown"' in driver)
    check("driver FLIP_STREAK_TARGET is 96",
          lambda: "FLIP_STREAK_TARGET = 96" in driver)
    check("driver never auto-flips (flip_ready is advice)",
          lambda: "Nothing here ever flips authority" in driver
          or "flip_ready is ADVICE" in driver)
    check("live agreement flip_ready is false",
          lambda: ag.get("flip_ready") is False)
    check("live streak is below 96 (threshold not met)",
          lambda: int(ag.get("consecutive_agreements") or 0) < 96)
    check("live tracker authority is still markdown",
          lambda: ag.get("authority") == "markdown")
    check("derivation audit unreviewed_count is 0",
          lambda: rec_audit["unreviewed_count"] == 0 and rec_audit["ok"] is True)
    check("parse_tracker_markdown remains OPEN until the JSON flip (2.2)",
          lambda: rec_audit["open"] == ["parse_tracker_markdown"])
    check("four filename/prose skip sites are advisory, not unreviewed",
          lambda: rec_audit["unreviewed_count"] == 0
          and {"critique_filename_stage", "inflight_filenames_mtime",
               "wd2_dhx_haystack", "wd2_uses_inflight_filenames"}
          <= set(rec_audit["advisory"]))
    check("judgement artifact restraint_justified is true",
          lambda: judge.get("restraint_justified") is True
          and judge.get("restraint_is_excuse") is False)
    check("judgement artifact cannot_flip_this_fence",
          lambda: judge.get("cannot_flip_this_fence") is True
          and judge.get("writes") == 0)
    check("judgement artifact names whose_judgement",
          lambda: "Keith or COW" in (judge.get("whose_judgement") or "")
          and "FLIP_STREAK_TARGET=96" in (judge.get("whose_judgement") or ""))
    check("judgement artifact is fingerprinted (describes)",
          lambda: isinstance(judge.get("describes"), dict)
          and judge["describes"].get("docs/CORE_RESTRUCTURE.md", {}).get("exists") is True)

    LIVE_VALUE.update({
        "checks": len(RESULTS),
        "streak": ag.get("consecutive_agreements"),
        "target": ag.get("flip_streak_target"),
        "flip_ready": ag.get("flip_ready"),
        "open_count": rec_audit["open_count"],
        "restraint_justified": judge.get("restraint_justified"),
        "whose": "Keith or COW on cosmos/ after flip_ready; threshold=96",
    })
    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % (
            "OK  " if ok else "FAIL", label,
            ("  [" + err + "]") if err else ""))
    print("live_value: " + json.dumps(LIVE_VALUE, sort_keys=True))
    print("%d/%d" % (len(RESULTS) - len(bad), len(RESULTS)))
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
