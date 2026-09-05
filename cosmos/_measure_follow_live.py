#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Measure FOLLOW_KEYS on the live authority ledger. Read-only. No secrets."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

FOLLOW_KEYS = ("job_id", "link_id", "rail", "node", "session_id", "sid", "rid")
LEDGER = Path(r"V:\A\Ai\COSMOS\live\ledger\authority.jsonl")
OUT = Path(__file__).resolve().parent / "_follow_live_measure.json"


def usable(payload: dict, k: str) -> bool:
    v = payload.get(k)
    if v is None:
        return False
    if isinstance(v, str):
        return bool(v.strip())
    if isinstance(v, (int, float)):
        return True
    return False


def main() -> int:
    if not LEDGER.is_file():
        print("NO_LEDGER", LEDGER)
        return 2
    rows = []
    bad = 0
    with LEDGER.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                bad += 1
                continue
            rows.append(rec)
    n = len(rows)
    by_event = Counter()
    by_event_with = Counter()
    key_counts = Counter()
    with_any = 0
    for r in rows:
        ev = r.get("event") or "?"
        by_event[ev] += 1
        p = r.get("payload") or {}
        if not isinstance(p, dict):
            p = {}
        hit = False
        for k in FOLLOW_KEYS:
            if usable(p, k):
                key_counts[k] += 1
                hit = True
        if hit:
            with_any += 1
            by_event_with[ev] += 1
    tail = rows[-100:] if n >= 100 else rows
    tail_with = 0
    tail_events = Counter()
    tail_events_with = Counter()
    tail_keys = Counter()
    tail_missing_types = Counter()
    for r in tail:
        ev = r.get("event") or "?"
        tail_events[ev] += 1
        p = r.get("payload") or {}
        if not isinstance(p, dict):
            p = {}
        hit = False
        present = []
        for k in FOLLOW_KEYS:
            if usable(p, k):
                tail_keys[k] += 1
                present.append(k)
                hit = True
        if hit:
            tail_with += 1
            tail_events_with[ev] += 1
        else:
            tail_missing_types[ev] += 1
    newest = rows[-1] if rows else {}
    newest_p = newest.get("payload") if isinstance(newest.get("payload"), dict) else {}
    newest_keys = [k for k in FOLLOW_KEYS if usable(newest_p, k)]
    evidence = {
        "ok": True,
        "ledger": str(LEDGER),
        "n_records": n,
        "bad_lines": bad,
        "head_seq": (rows[-1].get("seq") if rows else 0),
        "with_any_follow_key": with_any,
        "key_counts": dict(key_counts),
        "by_event": dict(by_event.most_common()),
        "by_event_with": dict(by_event_with.most_common()),
        "events_with_zero_ids": sorted(
            e for e, c in by_event.items() if by_event_with[e] == 0
        ),
        "tail_n": len(tail),
        "tail_with_any": tail_with,
        "tail_keys": dict(tail_keys),
        "tail_events": dict(tail_events.most_common()),
        "tail_events_with": dict(tail_events_with.most_common()),
        "tail_missing_types": dict(tail_missing_types.most_common()),
        "newest_seq": newest.get("seq"),
        "newest_event": newest.get("event"),
        "newest_follow_keys": newest_keys,
    }
    OUT.write_text(json.dumps(evidence, indent=1), encoding="utf-8")
    print("n=%s with_any=%s tail_with=%s/%s head_seq=%s"
          % (n, with_any, tail_with, len(tail), evidence["head_seq"]))
    print("key_counts", dict(key_counts))
    print("tail_keys", dict(tail_keys))
    print("tail_missing", dict(tail_missing_types))
    print("events_with_zero_ids", evidence["events_with_zero_ids"])
    print("newest", evidence["newest_event"], evidence["newest_seq"], newest_keys)
    print("EVIDENCE", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
