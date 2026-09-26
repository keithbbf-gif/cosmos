#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_scout — inventory NEW_AI_SCOUT candidates vs MESH (no invented web).

cosmos_discover inventories KNOWN hands. This scout diffs the standing
research artifact against MESH_ADDITIONS*.md. It does not fetch the web
(that would invent a live ranking). Kind=UNMEASURED for "went out".

    py -3.14 cosmos\\cosmos_scout.py --root V:\\A\\Ai\\COSMOS\\live --once
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_clock import atomic_json, write_heartbeat  # noqa: E402
from cosmos_paths import CosmosPaths  # noqa: E402

SCHEMA = "cosmos-scout/1"
WORKER = "cosmos-scout"
SCOUT_MD = Path(__file__).resolve().parent.parent / "docs" / "research" / "NEW_AI_SCOUT.md"
MESH_FILES = (
    Path(__file__).resolve().parent.parent / "docs" / "MESH_ADDITIONS.md",
    Path(__file__).resolve().parent.parent / "docs" / "MESH_ADDITIONS_grok.md",
)


def _names_from_scout(text: str) -> list[str]:
    names = []
    for line in text.splitlines():
        m = re.match(r"^\|\s*\d+\s*\|\s*\*\*([^*]+)\*\*", line)
        if m:
            names.append(m.group(1).strip())
    return names


def poll_once(root: str) -> dict:
    paths = CosmosPaths(root)
    logs = paths.logs()
    logs.mkdir(parents=True, exist_ok=True)
    dest_dir = paths.state("discovery")
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "scout.json"
    t0 = time.time()
    scout_txt = SCOUT_MD.read_text(encoding="utf-8") if SCOUT_MD.is_file() else ""
    mesh_txt = ""
    for p in MESH_FILES:
        if p.is_file():
            mesh_txt += "\n" + p.read_text(encoding="utf-8")
    names = _names_from_scout(scout_txt)
    still, inventoried = [], []
    blob = mesh_txt.lower()
    for n in names:
        if n.lower() in blob:
            inventoried.append(n)
        else:
            still.append(n)
    rec = {
        "schema": SCHEMA,
        "ok": bool(names),
        "kind": "INVENTORY",
        "went_out": "UNMEASURED",
        "n_scout": len(names),
        "n_still_new": len(still),
        "n_inventoried": len(inventoried),
        "still_new": still,
        "inventoried": inventoried,
        "source": str(SCOUT_MD) if SCOUT_MD.is_file() else None,
        "elapsed_s": round(time.time() - t0, 3),
    }
    extra = {"ok": rec["ok"], "n_still_new": rec["n_still_new"], "state": rec["kind"]}
    hb = write_heartbeat(logs / "scout_heartbeat.json", WORKER, extra=extra)
    rec["measured_at"] = hb.get("last_run")
    atomic_json(dest, rec)
    return rec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="cosmos_scout")
    ap.add_argument("--root", required=True)
    ap.add_argument("--once", action="store_true")
    a = ap.parse_args(argv)
    if not a.once:
        print("usage: --root LIVE --once")
        return 2
    rec = poll_once(a.root)
    print(json.dumps({
        "ok": rec["ok"], "n_scout": rec["n_scout"],
        "n_still_new": rec["n_still_new"], "still_new": rec["still_new"][:8],
    }, indent=2))
    return 0 if rec["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
