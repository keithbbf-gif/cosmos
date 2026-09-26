#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ingest_old_scars.py — merge the pre-wipe ROLD scars (bts-rold/scars.jsonl, 155)
into COSMOS_KB.json as scope=system scars, then rebuild the SQLite projection.

Source: V:\\OpenWork\\COSMOS_2\\ROLD\\pulled\\bts-rold\\scars.jsonl
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(r"V:\A\Ai\COSMOS")
KB = ROOT / "work_orders" / "ccr" / "COSMOS_KB.json"
SRC = Path(r"V:\OpenWork\COSMOS_2\ROLD\pulled\bts-rold\scars.jsonl")
SRC_NAME = "bts-rold/scars.jsonl (pre-wipe ROLD, recovered 2026-09-20)"


def extract_lesson(body: str) -> str | None:
    """Pull the 'Lesson:' line from an old scar body if present."""
    m = re.search(r"\*\*Lesson:\*\*\s*(.+)", body)
    if m:
        return m.group(1).strip()
    m = re.search(r"Lesson:\s*(.+)", body)
    return m.group(1).strip() if m else None


def main() -> None:
    kb = json.loads(KB.read_text(encoding="utf-8"))
    existing = {s["id"] for s in kb.get("scars", [])}

    raw = [json.loads(line) for line in SRC.read_text(encoding="utf-8").splitlines() if line.strip()]
    added = 0
    skipped = 0
    for r in raw:
        sid = r.get("id") or r.get("sid")
        if not sid:
            skipped += 1
            continue
        if sid in existing:
            skipped += 1
            continue
        body = r.get("body") or ""
        cls = r.get("class") or []
        if isinstance(cls, str):
            cls = [cls]
        kind = cls[0] if cls else "SYSTEM"
        kb["scars"].append({
            "id": sid,
            "scope": "system",
            "model_id": None,
            "kind": str(kind),
            "date": r.get("date"),
            "status": "RECOVERED",
            "symptom": (r.get("title") or "") + ("\n" + body if body else ""),
            "cause": None,
            "restricted_tree": None,
            "corrective": extract_lesson(body),
            "outcome": None,
            "derivation": SRC_NAME,
        })
        existing.add(sid)
        added += 1

    kb["scars"].sort(key=lambda s: s["id"])
    KB.write_text(json.dumps(kb, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Ingested {added} scars into {KB.name} ({skipped} skipped: dup/missing id)")
    print(f"Total scars now: {len(kb['scars'])}")


if __name__ == "__main__":
    main()