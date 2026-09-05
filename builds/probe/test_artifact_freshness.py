#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_artifact_freshness - claim-backing artifacts must fingerprint their source.

cDeck test_deck_features.py FAILS STALE when FEATURE_PROBE.json's ui_files
no longer match ui/. Probe and backup evidence JSON had no equivalent, so a
code change left FEATURE_MASTER citing byte counts of a vanished build.

Hermetic pins first (planted fixtures). Then the live registry: every
CLAIM_ARTIFACTS row MATCHES the files it names, or this suite is red.

Bite: `_bite_artifact_freshness.json` all_bite:true against the pre-stamp
artifacts (UNFINGERPRINTED + source newer than measurement). Fail-against-old:
`_fail_freshness_against_old.py` on the staged incumbents.

Recurrence: `remeasure_claims.py` re-runs a stale row's measurement before the
live MATCH gate. COSMOS_SKIP_CLAIM_REMEASURE=1 observes STALE (the bite path).
The STALE refusal itself is not relaxed.

    py -3.14 builds/probe/test_artifact_freshness.py
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

import artifact_freshness as af                                         # noqa: E402

BITE = HERE / "_bite_artifact_freshness.json"
RESULTS: list[tuple[str, bool, str]] = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_fresh_"))
    try:
        src_rel = "builds/backup/cosmos_backup.py"
        (td / "builds/backup").mkdir(parents=True)
        (td / "builds/probe").mkdir(parents=True)
        body = b"alpha-module-bytes\n"
        (td / src_rel).write_bytes(body)
        live = af.fingerprint(td, [src_rel])

        check("fingerprint records bytes of the real file",
              lambda: live[src_rel]["bytes"] == len(body) and live[src_rel]["exists"] is True)
        check("fingerprint sha256 is of the real bytes",
              lambda: live[src_rel]["sha256"] == __import__("hashlib").sha256(body).hexdigest())
        missing = af.fingerprint(td, ["builds/backup/no_such.py"])
        check("a missing source is exists:false, not a guessed hash",
              lambda: missing["builds/backup/no_such.py"]["exists"] is False
              and missing["builds/backup/no_such.py"]["sha256"] is None)

        def _fp_str():
            try:
                af.fingerprint(td, "one/file.py")
            except af.FreshnessError as e:
                return e.kind == "BAD_RELS"
            return False

        def _fp_none():
            try:
                af.fingerprint(td, None)
            except af.FreshnessError as e:
                return e.kind == "BAD_RELS"
            return False

        check("fingerprint of a string is BAD_RELS not character keys", _fp_str)
        check("fingerprint of None is BAD_RELS not TypeError", _fp_none)
        check("compare of a string recorded is UNFINGERPRINTED not AttributeError",
              lambda: af.compare("stale", live)["kind"] == "UNFINGERPRINTED"
              and af.compare("stale", live)["ok"] is False)

        def _stamp_list():
            try:
                af.stamp([], td, [src_rel])
            except af.FreshnessError as e:
                return e.kind == "BAD_REC"
            return False

        check("stamp of a list rec is BAD_REC not TypeError", _stamp_list)

        def _live_list():
            try:
                af.compare({src_rel: live[src_rel]}, [])
            except af.FreshnessError as e:
                return e.kind == "BAD_LIVE"
            return False

        def _live_none():
            try:
                af.compare({src_rel: live[src_rel]}, None)
            except af.FreshnessError as e:
                return e.kind == "BAD_LIVE"
            return False

        check("compare of a list live is BAD_LIVE not AttributeError (round-8)",
              _live_list)
        check("compare of None live is BAD_LIVE not AttributeError",
              _live_none)

        check("no describes map is UNFINGERPRINTED",
              lambda: af.compare(None, live)["kind"] == "UNFINGERPRINTED"
              and af.compare(None, live)["ok"] is False)
        check("empty describes map is UNFINGERPRINTED",
              lambda: af.compare({}, live)["kind"] == "UNFINGERPRINTED")

        wrong = {src_rel: {"exists": True, "bytes": 1, "sha256": "0" * 64}}
        check("wrong sha256 is STALE",
              lambda: af.compare(wrong, live)["kind"] == "STALE"
              and af.compare(wrong, live)["ok"] is False
              and src_rel in af.compare(wrong, live)["drift"])
        check("matching fingerprint is MATCH",
              lambda: af.compare(live, live)["kind"] == "MATCH"
              and af.compare(live, live)["ok"] is True)

        gone_live = af.fingerprint(td, ["builds/backup/no_such.py"])
        gone_rec = {"builds/backup/no_such.py": {
            "exists": True, "bytes": 4, "sha256": "abcd"}}
        check("fingerprinted file that is gone is SOURCE_ABSENT",
              lambda: af.compare(gone_rec, gone_live)["kind"] == "SOURCE_ABSENT")

        art = td / "builds/probe/_live.json"
        rec = {"schema": "x", "verdict": "COVERS_LONG_PATHS"}
        af.write_stamped(art, rec, td, [src_rel])
        got = json.loads(art.read_text(encoding="utf-8"))
        check("write_stamped stores describes_schema and describes",
              lambda: got.get("describes_schema") == af.SCHEMA
              and got["describes"][src_rel]["bytes"] == len(body))
        row = af.check_artifact(td, "builds/probe/_live.json", (src_rel,))
        check("stamped artifact checks MATCH against its source",
              lambda: row["kind"] == "MATCH" and row["ok"] is True)

        (td / "builds/probe/_stale.json").write_text(
            json.dumps({"describes": wrong}), encoding="utf-8")
        stale_row = af.check_artifact(td, "builds/probe/_stale.json", (src_rel,))
        check("stamped-wrong artifact is STALE not MATCH",
              lambda: stale_row["kind"] == "STALE")

        (td / "builds/probe/_bare.json").write_text(
            json.dumps({"verdict": "COVERS_LONG_PATHS"}), encoding="utf-8")
        bare = af.check_artifact(td, "builds/probe/_bare.json", (src_rel,))
        check("bare evidence JSON is UNFINGERPRINTED",
              lambda: bare["kind"] == "UNFINGERPRINTED")
        check("absent artifact is ARTIFACT_ABSENT",
              lambda: af.check_artifact(td, "builds/probe/_nope.json", (src_rel,))["kind"]
              == "ARTIFACT_ABSENT")
    finally:
        shutil.rmtree(td, ignore_errors=True)

    bite7 = HERE / "_bite_unpinned_round7.json"
    check("round7 bite artifact exists", bite7.is_file)
    rec7 = json.loads(bite7.read_text(encoding="utf-8")) if bite7.is_file() else {}
    check("round7 bite records silent character fingerprint + untyped crashes",
          lambda: rec7.get("all_bite") is True
          and rec7.get("fp_rels_str", {}).get("returned") == "dict"
          and rec7.get("fp_rels_none", {}).get("crash") == "TypeError"
          and rec7.get("compare_recorded_str", {}).get("crash") == "AttributeError"
          and rec7.get("stamp_rec_list", {}).get("crash") == "TypeError")

    check("bite artifact exists", BITE.is_file)
    bite = json.loads(BITE.read_text(encoding="utf-8")) if BITE.is_file() else {}
    check("bite records all_bite true (pre-stamp UNFINGERPRINTED + STALE plant)",
          lambda: bite.get("all_bite") is True)
    check("bite records source newer than the dated longpath measurement",
          lambda: bite.get("backup_src_newer_than_dated_longpath") is True)
    fail_old = HERE / "_fail_freshness_against_old.json"
    check("fail-against-old artifact exists", fail_old.is_file)
    fod = json.loads(fail_old.read_text(encoding="utf-8")) if fail_old.is_file() else {}
    check("fail-against-old is 10/10 UNFINGERPRINTED on staged incumbents",
          lambda: fod.get("all_new_pins_failed") is True
          and fod.get("unfingerprinted") == 10)

    collected = list((REPO / "builds").glob("*/test_*.py"))
    check("selftest clock glob builds/*/test_*.py includes this suite",
          lambda: any(p.resolve() == Path(__file__).resolve() for p in collected))

    if os.environ.get("COSMOS_SKIP_CLAIM_REMEASURE") != "1":
        import remeasure_claims as rc                                   # noqa: WPS433
        rc.refresh_stale(reason="test_artifact_freshness.live_gate")
    live_gate = af.check_all(REPO)
    for row in live_gate["rows"]:
        check(f"live {row['artifact']} is {row['kind']}",
              lambda r=row: r["ok"] is True and r["kind"] == "MATCH")
    check("live check_all ok", lambda: live_gate["ok"] is True)

    bad = [r for r in RESULTS if not r[1]]
    for label, ok, err in RESULTS:
        print(f"  {'OK  ' if ok else 'FAIL'}  {label}{('  ' + err) if err else ''}")
    print("live_value: " + json.dumps({
        "checks": len(RESULTS),
        "passed": len(RESULTS) - len(bad),
        "live_checked": live_gate["checked"],
        "live_matched": live_gate["matched"],
        "live_ok": live_gate["ok"],
        "refusal_kinds": ["UNFINGERPRINTED", "STALE", "ARTIFACT_ABSENT",
                          "SOURCE_ABSENT"],
    }, sort_keys=True))
    print(f"result: {'ok' if not bad else 'FAIL'}  "
          f"{len(RESULTS) - len(bad)}/{len(RESULTS)}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
