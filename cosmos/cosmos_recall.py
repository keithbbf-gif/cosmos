#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_recall — rebuildable carry-over fold for GET /api/v1/recall.

The 15-minute native clock (`cosmos_recall_clock.py`) writes the projection.
Core GET reads it only. GET never mkdir. GET never invents facts. Empty
store → kind=UNMEASURED.

Does not modify kernel / ledger / sched / service.

    py -3.14 cosmos\\cosmos_recall.py --selftest
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_clock import atomic_json  # noqa: E402

SCHEMA = "cosmos-recall/1"
PACK_NAME = "pack.json"
COLLECTOR_TAIL = 8
INDEX_TAIL = 5


def store_dir(paths) -> Path:
    return paths.role("state", "recall")


def pack_path(paths) -> Path:
    return store_dir(paths) / PACK_NAME


def empty_snapshot() -> dict:
    return {
        "schema": SCHEMA,
        "kind": "UNMEASURED",
        "n_sources": 0,
        "seed": None,
        "collector_tail": [],
        "index_hint": None,
        "askmine_open": None,
        "refreshed_at": None,
        "note": "Projection absent or never refreshed. GET never mkdir.",
    }


def _read_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        return None
    return obj if isinstance(obj, dict) else None


def _seed_fold(state: Path) -> dict | None:
    for name in ("SEED.json", "seed.json"):
        raw = _read_json(state / name)
        if not raw:
            continue
        facts = raw.get("facts")
        n_facts = len(facts) if isinstance(facts, list) else 0
        return {
            "session_id": raw.get("session_id") or raw.get("sid"),
            "schema": raw.get("schema"),
            "tree_id": raw.get("tree_id"),
            "n_facts": n_facts,
            "thin": n_facts == 0,
            "path": name,
        }
    return None


def _collector_tail(state: Path) -> list[dict]:
    idx = state / "collector" / "index.jsonl"
    if not idx.is_file():
        return []
    lines = []
    try:
        text = idx.read_text(encoding="utf-8")
    except OSError:
        return []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if isinstance(rec, dict):
            lines.append(rec)
    slim = []
    for rec in lines[-COLLECTOR_TAIL:]:
        slim.append({
            k: rec.get(k)
            for k in ("ts", "agent", "status", "task", "lane", "summary")
            if k in rec
        })
    return slim


def _index_hint(state: Path) -> dict | None:
    p = state / "cosmos_index.json"
    raw = _read_json(p)
    if not raw:
        return None
    return {
        "path": "state/cosmos_index.json",
        "module_count": raw.get("module_count"),
        "section_a": raw.get("section_a"),
        "section_b": raw.get("section_b"),
        "generated_at": raw.get("generated_at"),
    }


def _askmine_open(state: Path) -> int | None:
    p = state / "askmine" / "result.json"
    raw = _read_json(p)
    if not raw:
        return None
    try:
        return int(raw.get("outstanding") or raw.get("findings") or 0)
    except (TypeError, ValueError):
        return None


def refresh(paths) -> dict:
    """Write the recall projection. May mkdir under state/recall only."""
    state = paths.role("state")
    seed = _seed_fold(state)
    tail = _collector_tail(state)
    index_hint = _index_hint(state)
    askmine_open = _askmine_open(state)
    n_sources = (
        (1 if seed else 0)
        + (1 if tail else 0)
        + (1 if index_hint else 0)
        + (1 if askmine_open is not None else 0)
    )
    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    pack = {
        "schema": SCHEMA,
        "kind": "MEASURED" if n_sources else "UNMEASURED",
        "n_sources": n_sources,
        "seed": seed,
        "collector_tail": tail,
        "index_hint": index_hint,
        "askmine_open": askmine_open,
        "refreshed_at": now,
    }
    dest = pack_path(paths)
    atomic_json(dest, pack)
    return {"ok": True, "dest": str(dest), "kind": pack["kind"],
            "n_sources": n_sources, "bytes": dest.stat().st_size}


def snapshot(paths) -> dict:
    """GET fold. Never mkdir. Never invents."""
    p = pack_path(paths)
    if not p.is_file():
        return empty_snapshot()
    raw = _read_json(p)
    if not raw:
        out = empty_snapshot()
        out["kind"] = "STALE"
        out["note"] = "pack.json present but unreadable"
        return out
    raw.setdefault("schema", SCHEMA)
    return raw


def selftest() -> int:
    import tempfile
    from cosmos_kernel import install  # noqa: E402
    from cosmos_paths import CosmosPaths  # noqa: E402

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, str(e)))

    td = Path(tempfile.mkdtemp(prefix="cosmos_recall_"))
    root = install(td / "live", tree_id="recall-selftest")
    paths = CosmosPaths(str(root), expected_tree_id="recall-selftest")
    store_before = store_dir(paths).exists()

    snap0 = snapshot(paths)
    store_after_get = store_dir(paths).exists()

    check("GET never mkdir when absent",
          lambda: (snap0["kind"] == "UNMEASURED" and not store_before
                   and not store_after_get))

    state = paths.role("state")
    state.mkdir(parents=True, exist_ok=True)
    (state / "SEED.json").write_text(json.dumps({
        "schema": "cosmos-seed/1", "session_id": "abc", "facts": [{"k": "v"}],
    }), encoding="utf-8")

    rec = refresh(paths)
    snap1 = snapshot(paths)

    check("refresh writes pack",
          lambda: rec.get("ok") and rec.get("kind") == "MEASURED"
          and pack_path(paths).is_file())
    check("GET reads refreshed pack",
          lambda: snap1.get("kind") == "MEASURED"
          and snap1.get("seed", {}).get("session_id") == "abc")

    bad = [r for r in results if not r[1]]
    for label, ok, err in results:
        print(f"  {'OK  ' if ok else 'FAIL'}  {label}{('  ' + err) if err else ''}")
    print(f"result: {'ok' if not bad else 'FAIL'}  "
          f"{len(results) - len(bad)}/{len(results)}")
    return 1 if bad else 0


def main() -> int:
    ap = __import__("argparse").ArgumentParser(prog="cosmos_recall")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    print(json.dumps({"error": "use cosmos_recall_clock --once or --selftest"},
                     indent=1))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
