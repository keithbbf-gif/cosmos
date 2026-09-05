#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Live evidence: Registry.prove() for codex-cli + claude-cli via default_live_call.

This IS the normal prove() path map_wired_nodes uses. It does not call
poll_once(--live), which would spend every other wired rail. Key material is
never printed; the rail reads config/openai_api_key.txt itself.

    py -3.14 cosmos\\_emit_codex_wired_live.py --root V:\\A\\Ai\\COSMOS\\live
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "cosmos"))

from cosmos_paths import CosmosPaths  # noqa: E402
from cosmos_rails_prober import (  # noqa: E402
    WIRED_NODES, default_live_call, open_registry,
)

OUT = REPO / "cosmos" / "_codex_wired_live.json"
WANT = ("codex-cli", "claude-cli")
KEEP = ("ok", "rc", "model", "model_source", "body", "body_bytes",
        "registered", "detail", "kind", "link_id")


def _slim(rec: dict) -> dict:
    out = {k: rec.get(k) for k in KEEP}
    body = str(out.get("body") or "")
    if len(body) > 240:
        out["body"] = body[:240] + "…"
    dumped = json.dumps(out)
    if "sk-" in dumped.lower():
        out["body"] = "<redacted: key-shaped token in body>"
        out["detail"] = str(out.get("detail") or "")[:80]
    return out


def main() -> int:
    root = Path(sys.argv[sys.argv.index("--root") + 1]) if "--root" in sys.argv else (
        REPO / "live")
    paths = CosmosPaths(root)
    spec_by = {s["link_id"]: s for s in WIRED_NODES}
    missing = [lid for lid in WANT if lid not in spec_by]
    if missing:
        rec = {"ok": False, "error": f"not in WIRED_NODES: {missing}"}
        OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(rec, indent=1))
        return 2
    key_path = paths.config("openai_api_key.txt")
    reg = open_registry(paths)
    if reg is None:
        rec = {"ok": False, "error": "NO_KEY: install_key.bin absent"}
        OUT.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(rec, indent=1))
        return 2
    proofs = {}
    for lid in WANT:
        spec = spec_by[lid]
        rec = reg.prove(
            lid, spec["rail_type"], spec["src"], spec["dst"],
            default_live_call(paths, spec))
        proofs[lid] = _slim(rec)
    runtime = reg.file_runtime(paths.role("registry"))
    live = list(runtime.get("nodes") or [])
    stale = [r.get("link_id") for r in (runtime.get("stale") or [])]
    out = {
        "schema": "cosmos-codex-wired-live/1",
        "tree_id": paths.sentinel.tree_id,
        "key_present": key_path.exists(),
        "key_bytes": key_path.stat().st_size if key_path.exists() else 0,
        "wired": {lid: {
            "rail_type": spec_by[lid]["rail_type"],
            "src": spec_by[lid]["src"],
            "dst": spec_by[lid]["dst"],
            "module": spec_by[lid].get("module"),
            "satellite": spec_by[lid].get("satellite"),
            "family": spec_by[lid].get("family"),
        } for lid in WANT},
        "proofs": proofs,
        "runtime": {
            "count": runtime.get("count"),
            "nodes": live,
            "stale": stale,
            "codex_in_nodes": "codex-cli" in live,
            "claude_in_nodes": "claude-cli" in live,
        },
        "ok": bool(proofs.get("codex-cli", {}).get("ok")
                   and proofs.get("codex-cli", {}).get("registered")),
    }
    OUT.write_text(json.dumps(out, indent=1, default=str) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=1, default=str))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
