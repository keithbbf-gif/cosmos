#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_build_audit_batches.py — Final Auditor Batch Builder & Aggregator.

Enforces:
1. Bucket-full-only rule: Only builds when catch bin has >= 30 judged keeps.
2. Sub-batch slicing: 5–9 pairs/call (default 6) to keep input well under grok-4.7's
   131,072 context window (30 large pairs can exceed 3MB).
3. Schema compliance: Generates prompts following hero_final_auditor/LAYERS.md
   and aggregates returned JSON into schema cosmos-final-audit/1.
"""
from __future__ import annotations

import glob
import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"V:\A\Ai\COSMOS")
CCR = ROOT / "work_orders" / "ccr"
AUDITOR_DIR = CCR / "hero_final_auditor"
LIVE = ROOT / "live"
QUEUE_KEEPS = LIVE / "queue" / "gitur_keeps"
QUEUE_BINS = LIVE / "queue" / "audit_bins" / "final"
VERDICTS_DIR = LIVE / "queue" / "audit_verdicts"
WORK_AUDIT = LIVE / "work" / "audit"
DB_PATH = LIVE / "state" / "code_checks.db"

BATCH_SIZE = 30
SUB_BATCH_MIN = 5
SUB_BATCH_MAX = 9
SUB_BATCH_DEFAULT = 6


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def ensure_dirs() -> None:
    for d in (QUEUE_KEEPS, QUEUE_BINS, VERDICTS_DIR, WORK_AUDIT):
        d.mkdir(parents=True, exist_ok=True)


def load_receipts(order_ids: list[str]) -> dict[str, list[dict]]:
    """Fetch 4Cs check receipts from code_checks.db for the given orders."""
    if not DB_PATH.exists():
        return {}
    con = sqlite3.connect(str(DB_PATH))
    con.row_factory = sqlite3.Row
    res: dict[str, list[dict]] = {oid: [] for oid in order_ids}
    placeholders = ",".join("?" for _ in order_ids)
    if not placeholders:
        con.close()
        return {}
    rows = con.execute(
        f"SELECT order_id, tool, status, returncode, target, source_sha, stdout, stderr "
        f"FROM code_checks WHERE order_id IN ({placeholders})",
        order_ids,
    ).fetchall()
    for r in rows:
        oid = r["order_id"]
        res.setdefault(oid, []).append(
            {
                "tool": r["tool"],
                "status": r["status"],
                "returncode": r["returncode"],
                "target": r["target"],
                "sha": r["source_sha"][:16] if r["source_sha"] else "",
            }
        )
    con.close()
    return res


def scan_judged_keeps() -> list[dict]:
    """Scan queue dirs for judged keep items waiting for Final Audit."""
    ensure_dirs()
    items = []
    seen = set()

    # 1. Check QUEUE_BINS / final
    for f in sorted(QUEUE_BINS.glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            oid = d.get("order_id") or d.get("wo") or f.stem
            if oid not in seen:
                seen.add(oid)
                items.append({"source_file": str(f), "order_id": oid, "data": d})
        except Exception:
            continue

    # 2. Check QUEUE_KEEPS
    for f in sorted(QUEUE_KEEPS.glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            oid = d.get("order_id") or d.get("wo") or f.stem
            if oid not in seen:
                seen.add(oid)
                items.append({"source_file": str(f), "order_id": oid, "data": d})
        except Exception:
            continue

    return items


def make_prefix() -> str:
    """Compose the stable prompt prefix for the Final Auditor."""
    role = (AUDITOR_DIR / "L1_ROLE.md").read_text(encoding="utf-8", errors="replace") if (AUDITOR_DIR / "L1_ROLE.md").exists() else ""
    wrapper = (AUDITOR_DIR / "L4_WRAPPER.md").read_text(encoding="utf-8", errors="replace") if (AUDITOR_DIR / "L4_WRAPPER.md").exists() else ""
    mission = (AUDITOR_DIR / "L8_MISSION.md").read_text(encoding="utf-8", errors="replace") if (AUDITOR_DIR / "L8_MISSION.md").exists() else ""
    return (
        "# COSMOS HERO Final Auditor — Quality & Security Gate\n\n"
        f"## System Role\n{role}\n\n"
        f"## Wrapper Rules\n{wrapper}\n\n"
        f"## Output Contract\n{mission}\n\n"
        "---\n\n"
    )


def build_batches(items: list[dict], sub_size: int = SUB_BATCH_DEFAULT) -> list[dict]:
    """Group items into batches of 30, slicing each into sub-batches."""
    if len(items) < BATCH_SIZE:
        print(f"[AUDITOR_BATCH] WAITING: {len(items)}/{BATCH_SIZE} judged keeps. Bucket-full gate held.")
        return []

    ensure_dirs()
    prefix = make_prefix()
    order_ids = [it["order_id"] for it in items[:BATCH_SIZE]]
    receipts = load_receipts(order_ids)

    batches_created = []
    # Take first BATCH_SIZE items
    batch_items = items[:BATCH_SIZE]
    batch_id = f"audit-{_iso_now()}"
    batch_dir = WORK_AUDIT / batch_id
    batch_dir.mkdir(parents=True, exist_ok=True)

    # Slice into sub-batches of 5–9
    sub_batches = []
    for i in range(0, len(batch_items), sub_size):
        sub_items = batch_items[i : i + sub_size]
        sub_idx = i // sub_size + 1
        prompt_path = batch_dir / f"{batch_id}-sub{sub_idx:02d}.md"

        # Build prompt content
        body_lines = [
            f"# Batch {batch_id} Sub-batch {sub_idx} ({len(sub_items)} items)\n\n",
            "Audit each of the following candidate items against 4Cs checks, diff validity, ",
            "and boundary safety. Emit JSON matching schema `cosmos-final-audit/1`.\n\n",
        ]

        for item in sub_items:
            oid = item["order_id"]
            d = item["data"]
            rec_list = receipts.get(oid, [])
            rec_summary = ", ".join(f"{r['tool']}={r['status']}" for r in rec_list) or "NO_RECEIPTS_IN_DB"
            diff_text = d.get("diff") or d.get("patch") or ""
            if not diff_text and "diff_path" in d:
                dp = Path(d["diff_path"])
                if dp.exists():
                    diff_text = dp.read_text(encoding="utf-8", errors="replace")[:8000]

            body_lines.append(f"### Item: {oid}\n")
            body_lines.append(f"- **Title / Task**: {d.get('title') or d.get('task', '')[:200]}\n")
            body_lines.append(f"- **Judge verdict**: {d.get('verdict') or d.get('judge_verdict') or 'KEEP'}\n")
            body_lines.append(f"- **4Cs summary**: {rec_summary}\n")
            if diff_text:
                body_lines.append(f"```diff\n{diff_text[:12000]}\n```\n\n")
            else:
                body_lines.append("(Diff body attached via reference or omitted)\n\n")

        full_prompt = prefix + "".join(body_lines)
        prompt_path.write_text(full_prompt, encoding="utf-8")

        sub_batches.append(
            {
                "sub_idx": sub_idx,
                "item_count": len(sub_items),
                "prompt_path": str(prompt_path),
                "expected_verdict_path": str(VERDICTS_DIR / f"{batch_id}-sub{sub_idx:02d}.json"),
            }
        )

    meta = {
        "batch_id": batch_id,
        "created_at": _iso_now(),
        "total_items": len(batch_items),
        "sub_batches": sub_batches,
    }
    meta_path = batch_dir / "batch_manifest.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[AUDITOR_BATCH] Built {batch_id}: {len(batch_items)} items across {len(sub_batches)} sub-batches.")
    batches_created.append(meta)
    return batches_created


def aggregate_verdicts(batch_id: str) -> dict | None:
    """Merge sub-batch verdict JSONs into one master cosmos-final-audit/1 artifact."""
    batch_dir = WORK_AUDIT / batch_id
    meta_path = batch_dir / "batch_manifest.json"
    if not meta_path.exists():
        print(f"[AGGREGATE] No manifest found for {batch_id}")
        return None

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    all_verdicts = []

    for sub in meta["sub_batches"]:
        vp = Path(sub["expected_verdict_path"])
        if not vp.exists():
            print(f"[AGGREGATE] Incomplete: {vp.name} missing.")
            return None
        try:
            vd = json.loads(vp.read_text(encoding="utf-8"))
            if isinstance(vd, dict) and "verdicts" in vd:
                all_verdicts.extend(vd["verdicts"])
            elif isinstance(vd, list):
                all_verdicts.extend(vd)
        except Exception as e:
            print(f"[AGGREGATE] Error reading {vp.name}: {e}")
            return None

    master_verdict = {
        "schema": "cosmos-final-audit/1",
        "audit_batch_id": batch_id,
        "auditor_model": "grok-4.7",
        "auditor_family": "xai",
        "batch_count": len(all_verdicts),
        "created_at": _iso_now(),
        "verdicts": all_verdicts,
    }

    out_path = VERDICTS_DIR / f"{batch_id}.json"
    out_path.write_text(json.dumps(master_verdict, indent=2), encoding="utf-8")
    print(f"[AGGREGATE] SUCCESS: {out_path} created with {len(all_verdicts)} verdicts.")
    return master_verdict


if __name__ == "__main__":
    items = scan_judged_keeps()
    print(f"[SCAN] Found {len(items)} judged keep items in queue.")
    if len(sys.argv) > 1 and sys.argv[1] == "--aggregate":
        if len(sys.argv) > 2:
            aggregate_verdicts(sys.argv[2])
        else:
            print("Specify batch_id to aggregate")
    else:
        build_batches(items)
