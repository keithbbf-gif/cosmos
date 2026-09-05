#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Claim-artifact freshness — a recorded byte count of a vanished build is not evidence.

cDeck's FEATURE_PROBE.json pins ui/ file sizes. When ui/ changes the suite
FAILS STALE rather than passing on a number that describes different code.
builds/probe/ and builds/backup/ had the same hole: live evidence JSON with
no fingerprint of the source it describes. Measured this pass:

  builds/backup/cosmos_backup.py mtime 2026-08-31T12:49:31Z (F-43 leftover)
  builds/probe/_longpath_behaviour_20260831T0700Z.json measured 07:27:06Z
  builds/backup/_hmac_copyhash_live.json measured 12:07:18Z
  builds/backup/_stage_restore_live.json measured 12:39:00Z
  builds/backup/_f47_live_adapter.json measured 11:56:26Z

Those artifacts claimed things about a cosmos_backup.py that no longer
existed. FEATURE_MASTER cited them as current evidence.

This module fingerprints source files (bytes + sha256). Writers call
stamp() before writing. The clock-collected suite FAILS UNFINGERPRINTED
or STALE; MATCH is the only green. Re-measurement of a stale row is
remeasure_claims.py — this file is the detector, not the remesurer.

    py -3.14 builds/probe/artifact_freshness.py --check
    py -3.14 builds/probe/remeasure_claims.py
    py -3.14 builds/probe/test_artifact_freshness.py

Kinds: MATCH · STALE · UNFINGERPRINTED · ARTIFACT_ABSENT · SOURCE_ABSENT
Raised: BAD_RELS · BAD_REC · BAD_LIVE  (FreshnessError — a string of
paths was fingerprinted as characters; a list was stamped as a rec;
live fingerprint was not an object)
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


class FreshnessError(RuntimeError):
    """kind in {BAD_RELS, BAD_REC, BAD_LIVE}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        self.detail = detail
        super().__init__(f"[{kind}] {detail}")

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SCHEMA = "cosmos-claim-artifact-freshness/1"
DESCRIBES_KEY = "describes"

# Artifacts FEATURE_MASTER / COVERAGE cite as current-code evidence.
# Live-state snapshots (ledger size, inflight.jsonl bytes) are NOT here:
# those files mutate by design. Source .py files are the cdeck analog.
CLAIM_ARTIFACTS: tuple[tuple[str, tuple[str, ...], str], ...] = (
    (
        "builds/probe/_longpath_behaviour.json",
        (
            "cosmos/cosmos_backup.py",
            "cosmos/cosmos_backup_clock.py",
            "builds/backup/cosmos_backup.py",
        ),
        r"py -3.14 builds\probe\longpath_census.py behave --scratch %TEMP%\lp_scratch --out builds\probe\_longpath_behaviour.json",
    ),
    (
        "builds/probe/_tools_surface_live.json",
        (
            "builds/probe/tools/mcp_docs.py",
            "builds/probe/tools/surface.py",
        ),
        r"py -3.14 builds\probe\tools\mcp_docs.py --live",
    ),
    (
        "builds/probe/_blockers_freshness.json",
        ("builds/probe/mesh_blockers.py",),
        r"py -3.14 builds\probe\mesh_blockers.py --root V:\A\Ai\COSMOS\live --json builds\probe\_blockers_freshness.json --write-md",
    ),
    (
        "builds/probe/MESH_STATUS.json",
        ("builds/probe/mesh_blockers.py",),
        r"py -3.14 builds\probe\mesh_blockers.py --root V:\A\Ai\COSMOS\live --json builds\probe\MESH_STATUS.json --write-md",
    ),
    (
        "builds/backup/_f43_mutate_retire_live.json",
        ("builds/backup/cosmos_backup.py",),
        r"py -3.14 builds\backup\_emit_f43_live.py",
    ),
    (
        "builds/backup/_f43_freeze_live.json",
        (
            "builds/backup/cosmos_backup.py",
            "builds/backup/cosmos_backup_freeze.py",
        ),
        r"py -3.14 builds\backup\_emit_f43_freeze_live.py",
    ),
    (
        "builds/backup/_f47_live_adapter.json",
        ("builds/backup/cosmos_backup.py",),
        r"py -3.14 builds\backup\_emit_f47_live.py",
    ),
    (
        "builds/backup/_hmac_copyhash_live.json",
        ("builds/backup/cosmos_backup.py",),
        r"py -3.14 builds\backup\_emit_hmac_copyhash_live.py",
    ),
    (
        "builds/backup/_stage_restore_live.json",
        ("builds/backup/cosmos_backup.py",),
        r"py -3.14 builds\backup\_emit_stage_restore_live.py",
    ),
    (
        "builds/backup/_f54_live_preflight.json",
        ("builds/backup/cosmos_state_offsite.py",),
        r"py -3.14 builds\backup\cosmos_state_offsite.py --root V:\A\Ai\COSMOS\live --preflight",
    ),
    (
        "builds/probe/_f41_live_apply_refused.json",
        ("builds/probe/tool_disposition.py",),
        r"py -3.14 builds\probe\_emit_f41_live_apply.py",
    ),
    (
        "builds/probe/_f36_judgement.json",
        (
            "cosmos/cosmos_motif_driver.py",
            "cosmos/cosmos_derivation_audit.py",
            "docs/CORE_RESTRUCTURE.md",
        ),
        r"py -3.14 builds\probe\_emit_f36_judgement.py",
    ),
    (
        "builds/backup/_f43_clock_live_preflight.json",
        ("builds/backup/cosmos_local_clock.py",),
        r"py -3.14 builds\backup\cosmos_local_clock.py --root V:\A\Ai\COSMOS\live --preflight",
    ),
)


def fingerprint(repo: Path, rels: list[str] | tuple[str, ...]) -> dict:
    """bytes + sha256 of each repo-relative source. Existence is not identity.

    rels must be a list/tuple of path strings. A string iterates as
    characters (`fingerprint(repo, "one/file.py")` returned keys o,n,e,…)
    — the green-log. None/int TypeError. Bite `_bite_unpinned_round7.json`.
    """
    if isinstance(rels, (str, bytes)) or not isinstance(rels, (list, tuple)):
        raise FreshnessError(
            "BAD_RELS",
            f"rels is {type(rels).__name__}, not a list of paths")
    out: dict[str, dict] = {}
    for rel in rels:
        rel_n = str(rel).replace("\\", "/")
        p = Path(repo) / rel_n
        if not p.is_file():
            out[rel_n] = {"exists": False, "bytes": None, "sha256": None}
            continue
        data = p.read_bytes()
        out[rel_n] = {
            "exists": True,
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
    return out


def compare(recorded: dict | None, live: dict) -> dict:
    """MATCH only when every live source is fingerprinted and the hashes agree.

    A non-object recorded (string, list) is UNFINGERPRINTED, never
    AttributeError on .items() (bite `_bite_unpinned_round7.json`).
    """
    if not recorded or not isinstance(recorded, dict):
        return {
            "kind": "UNFINGERPRINTED",
            "ok": False,
            "drift": sorted(live) if isinstance(live, dict) else [],
            "detail": "artifact has no describes map; a number with no source "
                      "identity cannot prove the build it claims",
        }
    if not isinstance(live, dict):
        # live.items() AttributeError on a list/string/None (bite
        # `_bite_unpinned_round8.json`). fingerprint() always returns a
        # dict; a non-object live is a caller bug, not UNFINGERPRINTED.
        raise FreshnessError(
            "BAD_LIVE",
            f"live is {type(live).__name__}, not a fingerprint object")
    rec_n = {str(k).replace("\\", "/"): v for k, v in recorded.items()}
    drift: list[str] = []
    missing_source: list[str] = []
    for rel, live_fp in live.items():
        if not live_fp.get("exists"):
            missing_source.append(rel)
            continue
        rec_fp = rec_n.get(rel) or {}
        if rec_fp.get("sha256") != live_fp.get("sha256") or rec_fp.get("bytes") != live_fp.get("bytes"):
            drift.append(rel)
    if missing_source:
        return {
            "kind": "SOURCE_ABSENT",
            "ok": False,
            "drift": missing_source,
            "detail": "required source file is gone; the artifact describes a "
                      "build that no longer exists",
        }
    if drift:
        return {
            "kind": "STALE",
            "ok": False,
            "drift": drift,
            "detail": "Re-measure; a stale number is not evidence.",
        }
    return {"kind": "MATCH", "ok": True, "drift": []}


def stamp(rec: dict, repo: Path, rels: list[str] | tuple[str, ...]) -> dict:
    """Attach describes. Mutates rec and returns it.

    rec must be an object. A list TypeError'd on rec[DESCRIBES_KEY]
    (bite `_bite_unpinned_round7.json`).
    """
    if not isinstance(rec, dict):
        raise FreshnessError(
            "BAD_REC",
            f"rec is {type(rec).__name__}, not an object")
    rec[DESCRIBES_KEY] = fingerprint(repo, rels)
    rec["describes_schema"] = SCHEMA
    return rec


def write_stamped(path: Path, rec: dict, repo: Path,
                  rels: list[str] | tuple[str, ...]) -> dict:
    stamp(rec, repo, rels)
    path = Path(path)
    path.write_text(json.dumps(rec, indent=1, default=str) + "\n",
                    encoding="utf-8", newline="\n")
    return rec


def check_artifact(repo: Path, artifact_rel: str, source_rels: tuple[str, ...],
                   remeasure: str = "") -> dict:
    path = Path(repo) / artifact_rel
    live = fingerprint(repo, source_rels)
    if not path.is_file():
        return {
            "kind": "ARTIFACT_ABSENT",
            "ok": False,
            "artifact": artifact_rel,
            "drift": list(source_rels),
            "detail": f"{artifact_rel} missing — claims it backed are UNMEASURED",
            "remeasure": remeasure,
            "live": live,
        }
    try:
        rec = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:                                            # noqa: BLE001
        return {
            "kind": "ARTIFACT_ABSENT",
            "ok": False,
            "artifact": artifact_rel,
            "drift": list(source_rels),
            "detail": f"{artifact_rel} unreadable: {type(e).__name__}: {e}",
            "remeasure": remeasure,
            "live": live,
        }
    out = compare(rec.get(DESCRIBES_KEY), live)
    out["artifact"] = artifact_rel
    out["remeasure"] = remeasure
    out["live"] = live
    return out


def check_all(repo: Path | None = None) -> dict:
    repo = Path(repo) if repo is not None else REPO
    rows = [check_artifact(repo, art, srcs, hint)
            for art, srcs, hint in CLAIM_ARTIFACTS]
    bad = [r for r in rows if not r["ok"]]
    return {
        "schema": SCHEMA,
        "ok": not bad,
        "checked": len(rows),
        "matched": sum(1 for r in rows if r["kind"] == "MATCH"),
        "rows": [{"artifact": r["artifact"], "kind": r["kind"],
                  "ok": r["ok"], "drift": r.get("drift") or [],
                  "remeasure": r.get("remeasure") or ""}
                 for r in rows],
    }


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "--check":
        rec = check_all()
        print(json.dumps(rec, indent=2, sort_keys=True))
        return 0 if rec["ok"] else 2
    print("usage: artifact_freshness.py --check", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
