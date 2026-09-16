#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One live prove for gem-free via rails_prober map_wired_nodes (--live).

Requires live/config/google_api_key.txt (+ gem_free_rail.json from --gate).
No key → honest UNMEASURED in stdout JSON. Never fake GREEN.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_gem_free_rail import (  # noqa: E402
    BILLING_429_NOTE, KEY_NAME, SPEC_NAME, write_spec, spec_path_for,
)
from cosmos_paths import CosmosPaths  # noqa: E402
from cosmos_rails_prober import map_wired_nodes, open_registry  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", default="cosmos/_b29_gem_free_live.json")
    args = ap.parse_args()
    paths = CosmosPaths(args.root)
    rec = {
        "ok": False,
        "tree_id": paths.sentinel.tree_id,
        "link_id": "gem-free",
        "measured": "UNMEASURED",
        "billing_429_note": BILLING_429_NOTE,
    }
    key_ok = paths.config(KEY_NAME).exists() or paths.config("gemini_api_key.txt").exists()
    if not key_ok:
        rec["detail"] = f"NO_KEY: {KEY_NAME} absent at {paths.config(KEY_NAME)}"
        Path(args.out).write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(rec, indent=2))
        return 0
    if not paths.config(SPEC_NAME).exists():
        write_spec(spec_path_for(paths))
    reg = open_registry(paths)
    if reg is None:
        rec["detail"] = "NO install_key.bin — registry authority unavailable"
        Path(args.out).write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(rec, indent=2))
        return 0
    rows = map_wired_nodes(paths, reg, live=True)
    row = next((r for r in rows if r.get("link_id") == "gem-free"), {})
    rec.update({
        "measured": "LIVE" if row.get("registered") else "REFUSED",
        "registered": bool(row.get("registered")),
        "model": row.get("model") or "",
        "rc": row.get("rc"),
        "body_bytes": row.get("body_bytes"),
        "skipped": row.get("skipped"),
        "detail": row.get("detail"),
        "kind": row.get("kind"),
        "ok": bool(row.get("registered")),
    })
    if row.get("kind") == "QUOTA_DEAD" or (row.get("http") == 429):
        rec["billing_linked_dead"] = True
        rec["detail"] = BILLING_429_NOTE
    Path(args.out).write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rec, indent=2))
    return 0 if rec.get("registered") else 1


if __name__ == "__main__":
    raise SystemExit(main())
