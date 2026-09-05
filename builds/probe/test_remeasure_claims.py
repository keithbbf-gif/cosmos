#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Claim-artifact remesure gate — a source edit cannot ship last week's numbers.

test_artifact_freshness.py FAILS STALE when a claim JSON no longer fingerprints
its source. That detector is RIGHT. After it shipped, _longpath_behaviour.json
and _f43_mutate_retire_live.json went STALE anyway because nothing re-ran the
measurement. This gate pins the recurrence fix — one catalog, one command,
freshness-suite auto-refresh — without relaxing a single STALE check.

Two halves:

  A. STATIC PINS on remeasure_claims.py / test_artifact_freshness.py.
  B. THE MEASUREMENT: --check against the staged incumbents MUST report
     longpath STALE (the detector can fail), and --check against the live
     tree MUST report FRESH. COSMOS_SKIP_CLAIM_REMEASURE=1 keeps this
     suite from auto-fixing the thing it is measuring.

Fail-against-old (run this BEFORE believing the remesure loop):

    py -3.14 builds/probe/_fail_remeasure_against_old.py

That path must be all_new_pins_failed:true against
builds/probe/_delme/predispose_stale_claims_20260831T152926Z.

Run:  py -3.14 builds/probe/test_remeasure_claims.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]

# This suite measures freshness. It must not auto-remeasure the tree it reads.
os.environ["COSMOS_SKIP_CLAIM_REMEASURE"] = "1"

sys.path.insert(0, str(HERE))
import artifact_freshness as af                                         # noqa: E402
from remeasure_claims import (  # noqa: E402
    BY_ARTIFACT, RECEIPT, SKIP_ENV, hint_argv, stale_in,
)

RESULTS: list[tuple[str, bool, str]] = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


SRC = (HERE / "remeasure_claims.py").read_text(encoding="utf-8")
FRESH_SRC = (HERE / "test_artifact_freshness.py").read_text(encoding="utf-8")
AF_SRC = (HERE / "artifact_freshness.py").read_text(encoding="utf-8")
STAGED = HERE / "_delme" / "predispose_stale_claims_20260831T152926Z"
FAIL_OLD = HERE / "_fail_remeasure_against_old.json"


# ==========================================================================
# A. STATIC PINS — the recurrence fix is in the tree, not a comment
# ==========================================================================

check("remeasure_claims.py catalogs builds/probe/_longpath_behaviour.json "
      "(the first artifact that went stale after the detector shipped)",
      lambda: "builds/probe/_longpath_behaviour.json" in BY_ARTIFACT)
check("…and builds/backup/_f43_mutate_retire_live.json (the second)",
      lambda: "builds/backup/_f43_mutate_retire_live.json" in BY_ARTIFACT)
check("the catalog is CLAIM_ARTIFACTS — one list, not a second copy",
      lambda: set(BY_ARTIFACT) == {art for art, _, _ in af.CLAIM_ARTIFACTS}
      and len(BY_ARTIFACT) == len(af.CLAIM_ARTIFACTS))
check("a --check flag exists and does not re-run measurements",
      lambda: '"--check"' in SRC and "do not re-run" in SRC)
check("COSMOS_SKIP_CLAIM_REMEASURE is the bite hatch, not a silent skip of the detector",
      lambda: SKIP_ENV == "COSMOS_SKIP_CLAIM_REMEASURE"
      and "COSMOS_SKIP_CLAIM_REMEASURE" in SRC)
check("test_artifact_freshness.py auto-remesures stale artifacts before the live gate",
      lambda: "refresh_stale" in FRESH_SRC
      and "remeasure_claims" in FRESH_SRC
      and "COSMOS_SKIP_CLAIM_REMEASURE" in FRESH_SRC)
check("test_artifact_freshness.py still refuses a stale artifact (not relaxed)",
      lambda: "wrong sha256 is STALE" in FRESH_SRC
      and 'r["kind"] == "MATCH"' in FRESH_SRC)
check("artifact_freshness.py --check still does not remesure (detector stays a detector)",
      lambda: "import remeasure_claims" not in AF_SRC
      and "refresh_stale" not in AF_SRC
      and "subprocess" not in AF_SRC)
check("refresh_if_stale is what the freshness suite calls",
      lambda: "def refresh_if_stale" in SRC and "def refresh_stale" in SRC)
check("never-delete stages incumbents under _delme/predispose_stale_claims_",
      lambda: "predispose_stale_claims_" in SRC and "_delme" in SRC)
check("selftest clock glob builds/*/test_*.py includes this suite",
      lambda: any(p.resolve() == Path(__file__).resolve()
                  for p in (REPO / "builds").glob("*/test_*.py")))
check("hint_argv replaces py -3.14 with this interpreter",
      lambda: hint_argv(r"py -3.14 builds\probe\longpath_census.py behave")[0]
      == sys.executable)
check("hint_argv expands %TEMP% and does not leave a repo-relative literal",
      lambda: (
          argv := hint_argv(
              r"py -3.14 builds\probe\longpath_census.py behave "
              r"--scratch %TEMP%\lp_scratch --out builds\probe\_longpath_behaviour.json"
          ),
          "%TEMP%" not in " ".join(argv)
          and "--scratch" in argv
          and "COSMOS" not in Path(argv[argv.index("--scratch") + 1]).parts
      )[-1])


# ==========================================================================
# B. THE MEASUREMENT
# ==========================================================================

check("fail-against-old artifact exists", FAIL_OLD.is_file)
fod = json.loads(FAIL_OLD.read_text(encoding="utf-8")) if FAIL_OLD.is_file() else {}
check("fail-against-old is all_new_pins_failed true "
      "(old freshness test had no remesure; staged longpath is STALE)",
      lambda: fod.get("all_new_pins_failed") is True
      and fod.get("staged_longpath_kind") == "STALE")

check("BITE: staged incumbents dir exists", STAGED.is_dir)
if STAGED.is_dir():
    found = stale_in(STAGED, ["builds/probe/_longpath_behaviour.json"])
    check("BITE: --check / stale_in reports staged _longpath_behaviour.json STALE "
          "(this is the fail-against-old: last week's sha vs today's source)",
          lambda: "builds/probe/_longpath_behaviour.json" in found,
          )
    check("BITE: staged test_artifact_freshness.py does not call refresh_if_stale",
          lambda: "refresh_if_stale" not in (STAGED / "test_artifact_freshness.py")
          .read_text(encoding="utf-8"))
    check("BITE: staged dir has no remeasure_claims.py (the loop did not exist)",
          lambda: not (STAGED / "remeasure_claims.py").is_file())

live_longpath = REPO / "builds/probe/_longpath_behaviour.json"
mtime_before = live_longpath.stat().st_mtime_ns if live_longpath.is_file() else None
check_proc = subprocess.run(
    [sys.executable, str(HERE / "remeasure_claims.py"),
     "--check", "--artifacts-dir", str(STAGED)],
    cwd=str(REPO), capture_output=True, text=True,
    encoding="utf-8", errors="replace",
)
mtime_after = live_longpath.stat().st_mtime_ns if live_longpath.is_file() else None
check("--check against staged incumbents exits 1 (stale found) and does not rewrite live",
      lambda: check_proc.returncode == 1
      and mtime_before is not None
      and mtime_before == mtime_after)
try:
    check_doc = json.loads(check_proc.stdout or "{}")
except json.JSONDecodeError:
    check_doc = {}
check("--check report names builds/probe/_longpath_behaviour.json as stale",
      lambda: "builds/probe/_longpath_behaviour.json" in (check_doc.get("stale") or []))

live_stale = stale_in()
check("LIVE: every catalogued artifact MATCHES current sources "
      "(run remeasure_claims.py if this fails — a stale number is not evidence)",
      lambda: live_stale == [])
check("LIVE: artifact_freshness.check_all ok",
      lambda: af.check_all(REPO)["ok"] is True)


def main() -> int:
    bad = [r for r in RESULTS if not r[1]]
    for label, ok, err in RESULTS:
        print(f"  {'OK  ' if ok else 'FAIL'}  {label}{('  ' + err) if err else ''}")
    print("live_value: " + json.dumps({
        "checks": len(RESULTS),
        "passed": len(RESULTS) - len(bad),
        "live_stale": live_stale,
        "staged_check_rc": check_proc.returncode,
        "fail_against_old": fod.get("all_new_pins_failed"),
        "receipt_present": RECEIPT.is_file(),
    }, sort_keys=True))
    print(f"result: {'ok' if not bad else 'FAIL'}  "
          f"{len(RESULTS) - len(bad)}/{len(RESULTS)}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
