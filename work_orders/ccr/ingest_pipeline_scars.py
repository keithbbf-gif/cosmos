#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ingest_pipeline_scars.py — merge the WOMB pipeline battle ledger (SCAR_TABLE.md
S1-S24) and the September occupancy scars (SCARS_2026-09.md, 12 rows) into
COSMOS_KB.json, then rebuild the SQLite projection.

Follows the ingest_old_scars.py pattern: ID dedup, append-only, sort by id.

Usage:
    py -3.14 work_orders\\ccr\\ingest_pipeline_scars.py [--dry-run]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(r"V:\A\Ai\COSMOS")
KB = ROOT / "work_orders" / "ccr" / "COSMOS_KB.json"
ST = Path(r"V:\OpenWork\COSMOS_2\ROLD\living\SCAR_TABLE.md")

SEPT_ROWS = [
    ("SEPT-01", "TWO_HEADS",
     "Two heads: 37 occupancy commits vs 189 Gitur main. CCr wrote LiT and Gitur wrote GitHub.",
     "Two writers on one tree with no arbiter.",
     "LiT is origin/main. origin/main..HEAD != 0 -> WARN x3. Gitur only. CANON_ONE_HEAD.md"),
    ("SEPT-02", "TWO_PENS",
     "Two pens: 716fbaea wrote cosmos/ after pen passed to f47bad79. Lease in the TUI != disk ACL.",
     "Lease held in TUI memory is not a filesystem ACL; agents wrote past the handoff.",
     "CAM holds write key. Agents never get S: R/W. Fencing on the resource. DEFINE_CAM_SAFE.md"),
    ("SEPT-03", "ZOMBIE_SPAWN",
     "Zombie grok.exe: 112x grok --single MOTIF clones. Empty Output. Token leak.",
     "Background loops spawned uncapped single-shot CLI workers with no reaper.",
     "Runner: WARN x3 then do not spawn. WD2 drives MOTIF. #578"),
    ("SEPT-04", "CONCAT_CTX",
     "Concat CTX: 35 orders NEVER RAN (cdot-concatenated string / missing SOP.md).",
     "Context passed as a dot-joined string instead of a path list; missing SOP not gated.",
     "CTX is a list. Spawn refuse."),
    ("SEPT-05", "FAIL_CORPSE",
     "FAIL terminal: 157 corpses. No partner, no judge, no attempt 2. n_total looked like work.",
     "Failed orders left on the board with no partner retry and no judge verdict.",
     "JSONL attempts. wo_partner. Board = bucket+picked. File away, don't throw away."),
    ("SEPT-06", "JUDGE_EMPTY",
     "Judge on empty WOMB: Qwen Max 907k write, 5 min TTL, $2.31, then gone. New judge prefixes.",
     "Judge seated against an empty board with a dead cache; verdicts evaporated.",
     "One Judge/run. If cache dead and n_board < 20, leave."),
    ("SEPT-07", "ASIS_RETRY",
     "As-is retry: retrying empty WOs would re-fire grok.",
     "Blind retry of failed orders re-triggers the same expensive failure.",
     "(1) prove full or (2) restate + two GAC + new prompt."),
    ("SEPT-08", "SQUASH_CLOBBER",
     "Squash clobber: #570/#577 delete working main files (1127-del stagehand).",
     "Squash-merges deleted more live code than they added.",
     "WARN x3 if PR deletes more than it adds on a live file. Grade dups. Don't squash."),
    ("SEPT-09", "CD_POWERSHELL",
     "cd /d in PowerShell: reset never ran; git not in repo.",
     "cmd-style cd /d silently fails under PowerShell; subsequent git ran in the wrong dir.",
     "WARN: cd V:\\A\\Ai\\COSMOS."),
    ("SEPT-10", "PLACATION",
     "Placation: claims of completion without verifiable runtime evidence.",
     "Status asserted from prose instead of measured artifacts.",
     "Claim != evidence. Runtime binding. docs/SCAR_PLACATION.md"),
    ("SEPT-11", "MUSE_CHAMBER",
     "Muse chamber: duplicate POST, truncated diff, invented occupancy.",
     "High token pressure caused duplicated submits and fabricated state.",
     "STYLES/muse.md append."),
    ("SEPT-12", "DS_ESSAY",
     "DS :free essay: fat cache hit, first line not NONE.",
     "Chatty model emitted reasoning prose instead of the contract first line.",
     "STYLES/deepseek-v4-flash.md."),
]

ERA_DATE = {"era1": "2026-09-12", "era2": "2026-09-13", "era0": "2026-08"}


def era_of(n: int) -> str:
    if 1 <= n <= 8:
        return "era1"
    if 9 <= n <= 15:
        return "era2"
    return "era0"


def parse_table() -> list[dict]:
    text = ST.read_text(encoding="utf-8")
    rows = re.findall(r"\|\s*(S\d+)\s*\|(.*?)\|([^*|]*?)\|([^*|]*?)\|(.*?)\|\s*\*\*(.*?)\*\*",
                      text)
    out = []
    for sid, scar, cost, cause, fix, status in rows:
        n = int(sid[1:])
        st = status.strip().upper()
        norm_status = "HEALING" if st.startswith("HEALING") else "HEALED"
        out.append({
            "id": sid,
            "scope": "pipeline",
            "model_id": None,
            "kind": "PIPELINE",
            "date": ERA_DATE[era_of(n)],
            "status": norm_status,
            "symptom": scar.strip(),
            "cause": cause.strip(),
            "restricted_tree": None,
            "corrective": fix.strip(),
            "outcome": f"Status: {status.strip()}. Cost: {cost.strip()}.",
            "derivation": "ROLD/living/SCAR_TABLE.md (WOMB pipeline battle ledger)",
        })
    return out


def sept_rows() -> list[dict]:
    out = []
    for sid, kind, symptom, cause, corrective in SEPT_ROWS:
        out.append({
            "id": sid,
            "scope": "system",
            "model_id": None,
            "kind": kind,
            "date": "2026-09",
            "status": "ACTIVE",
            "symptom": symptom,
            "cause": cause,
            "restricted_tree": None,
            "corrective": corrective,
            "outcome": None,
            "derivation": "docs/SCARS_2026-09.md (September occupancy)",
        })
    return out


def main() -> int:
    dry = "--dry-run" in sys.argv
    kb = json.loads(KB.read_text(encoding="utf-8"))
    existing = {s["id"] for s in kb.get("scars", [])}
    new_rows = parse_table() + sept_rows()
    print(f"Parsed {len(new_rows)} candidate rows (24 pipeline + 12 september)")
    added, skipped = 0, []
    for r in new_rows:
        if r["id"] in existing:
            skipped.append(r["id"])
            continue
        if not dry:
            kb["scars"].append(r)
        existing.add(r["id"])
        added += 1
    print(f"Would add: {added}, skipped (dup id): {skipped}")
    if dry:
        print("dry-run: KB untouched")
        return 0
    kb["scars"].sort(key=lambda s: s["id"])
    KB.write_text(json.dumps(kb, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {KB} — total scars now: {len(kb['scars'])}")
    # Rebuild the SQLite projection in the same pass (edit -> rebuild rule)
    sys.path.insert(0, str(ROOT / "work_orders" / "ccr"))
    from cosmos_kb import build, DEFAULT_DB
    build(KB, DEFAULT_DB)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
