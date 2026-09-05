#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-run every claim-backing measurement whose artifact no longer describes shipped bytes.

THE SCAR. The freshness detector (artifact_freshness.py) correctly refuses a
stale number. After it shipped, builds/probe/_longpath_behaviour.json and
builds/backup/_f43_mutate_retire_live.json went STALE anyway: the sources
changed and nothing re-ran the measurement. Forgetting was the defect, not
the refusal.

THIS FILE is the recurrence fix. It does not relax the detector. It makes
the artifact stop being stale:

    py -3.14 builds/probe/remeasure_claims.py            # re-run only stale
    py -3.14 builds/probe/remeasure_claims.py --force    # re-run the whole catalog
    py -3.14 builds/probe/remeasure_claims.py --check    # rc=1 if any stale; no run
    py -3.14 builds/probe/remeasure_claims.py --only builds/probe/_longpath_behaviour.json

test_artifact_freshness.py calls refresh_stale before the live MATCH gate,
so a source edit cannot ship last week's measurements. COSMOS_SKIP_CLAIM_REMEASURE=1
is the bite hatch that must observe STALE.

Catalog is CLAIM_ARTIFACTS in artifact_freshness.py — one list, not a second.

Exit: 0 = every selected artifact now MATCHES (or --check found none stale).
1 = --check found stale, or a remesure ran and the artifact is still not MATCH.
2 = a remesure command could not be parsed.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

import artifact_freshness as af                                         # noqa: E402

RECEIPT = HERE / "REMEASURE_CLAIMS.json"
SKIP_ENV = "COSMOS_SKIP_CLAIM_REMEASURE"
BY_ARTIFACT = {art: (srcs, hint) for art, srcs, hint in af.CLAIM_ARTIFACTS}

_STAGE: Path | None = None


def hint_argv(hint: str) -> list[str]:
    """Turn a CLAIM_ARTIFACTS remesure hint into argv for this interpreter.

    Expands %TEMP% / $VAR. Replaces `py -3.14` with sys.executable so a
    literal `%TEMP%` cannot land under the repo (SCRATCH_UNSAFE). A --scratch
    value is made unique so two remesures cannot collide.
    """
    expanded = os.path.expandvars(hint)
    parts = expanded.split()
    if not parts:
        return []
    argv: list[str] = []
    i = 0
    if parts[0] in ("py", "python", "python3"):
        i = 1
        if i < len(parts) and parts[i].startswith("-"):
            i += 1
        argv.append(sys.executable)
    argv.extend(parts[i:])
    if "--scratch" in argv:
        idx = argv.index("--scratch")
        if idx + 1 < len(argv):
            argv[idx + 1] = tempfile.mkdtemp(prefix="cosmos_claim_scratch_")
    return argv


def stage_incumbent(path: Path) -> Path | None:
    """Never-delete: copy the file about to be overwritten into _delme."""
    global _STAGE
    if not path.is_file():
        return None
    if _STAGE is None:
        stamp = time.strftime("%Y%m%dT%H%M%S")
        _STAGE = HERE / "_delme" / f"predispose_stale_claims_{stamp}"
        _STAGE.mkdir(parents=True, exist_ok=True)
    dest_dir = _STAGE / path.parent.name
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / path.name
    if not dest.exists():
        shutil.copy2(path, dest)
    return dest


def check_one(art: str, srcs: tuple[str, ...], hint: str, *,
              repo: Path | None = None,
              artifacts_dir: Path | None = None) -> dict:
    repo = Path(repo) if repo is not None else REPO
    if artifacts_dir is None:
        return af.check_artifact(repo, art, srcs, hint)
    path = Path(artifacts_dir) / Path(art).name
    live = af.fingerprint(repo, srcs)
    if not path.is_file():
        return {
            "kind": "ARTIFACT_ABSENT", "ok": False, "artifact": art,
            "drift": list(srcs), "remeasure": hint, "live": live,
            "detail": f"{path} missing",
        }
    try:
        rec = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:                                            # noqa: BLE001
        return {
            "kind": "ARTIFACT_ABSENT", "ok": False, "artifact": art,
            "drift": list(srcs), "remeasure": hint, "live": live,
            "detail": f"{path} unreadable: {type(e).__name__}: {e}",
        }
    out = af.compare(rec.get(af.DESCRIBES_KEY), live)
    out["artifact"] = art
    out["remeasure"] = hint
    out["live"] = live
    return out


def stale_in(artifacts_dir: Path | None = None,
             names: list[str] | None = None,
             repo: Path | None = None) -> list[str]:
    want = names or [art for art, _, _ in af.CLAIM_ARTIFACTS]
    out: list[str] = []
    for art in want:
        srcs, hint = BY_ARTIFACT[art]
        row = check_one(art, srcs, hint, repo=repo, artifacts_dir=artifacts_dir)
        if not row.get("ok"):
            out.append(art)
    return out


def _persist_stdout(art: str, srcs: tuple[str, ...], stdout: str) -> None:
    """If the remesure printed a stamped (or stampable) record, write it.

    mcp_docs --live and cosmos_state_offsite --preflight stamp in memory and
    print; they do not write the claim artifact. Persisting that stdout is
    still a remesure, not a fingerprint stamp of an un-run measurement.
    """
    try:
        rec = json.loads(stdout)
    except json.JSONDecodeError:
        return
    if not isinstance(rec, dict):
        return
    path = REPO / art
    if not rec.get(af.DESCRIBES_KEY):
        af.stamp(rec, REPO, srcs)
    path.write_text(json.dumps(rec, indent=1, default=str) + "\n",
                    encoding="utf-8", newline="\n")


def run_claim(art: str, srcs: tuple[str, ...], hint: str) -> dict:
    path = REPO / art
    staged = stage_incumbent(path)
    argv = hint_argv(hint)
    if not argv:
        return {"artifact": art, "rc": 2, "argv": argv, "detail": "empty argv"}
    print(f"[remeasure] RUN {art} <- {argv[1:] if len(argv) > 1 else argv}")
    proc = subprocess.run(
        argv, cwd=str(REPO), capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=120,
    )
    row = af.check_artifact(REPO, art, srcs, hint)
    if not row.get("ok"):
        _persist_stdout(art, srcs, proc.stdout or "")
        row = af.check_artifact(REPO, art, srcs, hint)
    return {
        "artifact": art,
        "rc": int(proc.returncode),
        "argv": argv,
        "staged": str(staged) if staged else None,
        "kind_after": row.get("kind"),
        "ok_after": bool(row.get("ok")),
        "stderr_tail": (proc.stderr or "")[-400:],
    }


def _skip() -> bool:
    return os.environ.get(SKIP_ENV) == "1"


def refresh_if_stale(names: list[str] | None = None, *,
                     force: bool = False,
                     label: str | None = None) -> dict:
    """Re-run every named (or catalogued) claim whose artifact is not MATCH.

    No-op when COSMOS_SKIP_CLAIM_REMEASURE=1 (the bite path that must
    observe stale). Returns a receipt dict.
    """
    if _skip():
        return {"skipped": True, "reason": SKIP_ENV}
    label = label or ("AFTER-REMEASURE-" + time.strftime("%Y-%m-%dT%H%M"))
    selected = list(names) if names else [art for art, _, _ in af.CLAIM_ARTIFACTS]
    unknown = [n for n in selected if n not in BY_ARTIFACT]
    if unknown:
        raise SystemExit(f"unknown claim artifact(s): {unknown}")
    ran: list[str] = []
    skipped_fresh: list[str] = []
    failed: list[dict] = []
    stale_before = {n: check_one(n, *BY_ARTIFACT[n]) for n in selected
                    if not check_one(n, *BY_ARTIFACT[n]).get("ok")}
    for name in selected:
        srcs, hint = BY_ARTIFACT[name]
        if not force and check_one(name, srcs, hint).get("ok"):
            skipped_fresh.append(name)
            continue
        info = run_claim(name, srcs, hint)
        ran.append(name)
        if not info.get("ok_after"):
            failed.append(info)
    stale_after = {n: check_one(n, *BY_ARTIFACT[n]) for n in selected
                   if not check_one(n, *BY_ARTIFACT[n]).get("ok")}
    receipt = {
        "kind": "REMEASURE_CLAIMS",
        "label": label,
        "probed_at_epoch": time.time(),
        "ran": ran,
        "skipped_fresh": skipped_fresh,
        "stale_before": {k: {"kind": v.get("kind"), "drift": v.get("drift") or []}
                         for k, v in stale_before.items()},
        "stale_after": {k: {"kind": v.get("kind"), "drift": v.get("drift") or []}
                        for k, v in stale_after.items()},
        "failed": failed,
        "stage": str(_STAGE) if _STAGE else None,
        "skip_env": SKIP_ENV,
    }
    if ran or stale_before:
        RECEIPT.write_text(json.dumps(receipt, indent=1, default=str) + "\n",
                           encoding="utf-8", newline="\n")
    return receipt


def refresh_stale(*, reason: str = "refresh_stale") -> dict:
    """test_artifact_freshness entry: re-run whatever is currently not MATCH."""
    names = stale_in()
    if not names:
        return {"ran": [], "skipped_fresh": [art for art, _, _ in af.CLAIM_ARTIFACTS],
                "reason": reason}
    print(f"[remeasure] {reason}: stale {names}")
    return refresh_if_stale(names, label="AFTER-REMEASURE-" + time.strftime("%Y-%m-%dT%H%M"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="report stale artifacts and exit 1 if any; do not re-run")
    ap.add_argument("--force", action="store_true",
                    help="re-run the whole catalog even if currently matching")
    ap.add_argument("--only", default=None,
                    help="comma-separated artifact rels to consider")
    ap.add_argument("--artifacts-dir", default=None,
                    help="read artifacts from this dir (bite against staged copies)")
    ap.add_argument("--label", default=None)
    args = ap.parse_args(argv)

    names = ([x.strip() for x in args.only.split(",") if x.strip()]
             if args.only else None)
    art_dir = Path(args.artifacts_dir).resolve() if args.artifacts_dir else None

    if args.check or art_dir is not None:
        stale = stale_in(art_dir, names)
        rows = []
        want = names or [art for art, _, _ in af.CLAIM_ARTIFACTS]
        for art in want:
            srcs, hint = BY_ARTIFACT[art]
            row = check_one(art, srcs, hint, artifacts_dir=art_dir)
            rows.append({"artifact": art, "kind": row.get("kind"),
                         "ok": row.get("ok"), "drift": row.get("drift") or []})
        report = {
            "kind": "REMEASURE_CHECK",
            "artifacts_dir": str(art_dir or REPO),
            "stale": stale,
            "rows": rows,
        }
        print(json.dumps(report, indent=1))
        if art_dir is not None and not args.check:
            return 0 if stale else 1
        return 1 if stale else 0

    receipt = refresh_if_stale(names, force=args.force, label=args.label)
    print(json.dumps({
        "kind": receipt.get("kind"),
        "ran": receipt.get("ran"),
        "skipped_fresh": receipt.get("skipped_fresh"),
        "stale_after": receipt.get("stale_after"),
        "failed": receipt.get("failed"),
        "stage": receipt.get("stage"),
        "artifact": str(RECEIPT) if RECEIPT.is_file() else None,
    }, indent=1, default=str))
    if receipt.get("skipped"):
        return 0
    if receipt.get("stale_after") or receipt.get("failed"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
