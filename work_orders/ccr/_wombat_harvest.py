#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Host write for WOMBAT. Codex 0.147 on Windows stamps sandbox_policy
read-only even with --sandbox workspace-write. The mouth is the product;
this process is the kind-gated writer (board, not coding).

    py -3.14 work_orders\\ccr\\_wombat_harvest.py --probe
    py -3.14 work_orders\\ccr\\_wombat_harvest.py --drops
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

CCR = Path(r"V:\A\Ai\COSMOS\work_orders\ccr")
DROP = Path(r"V:\A\Ai\COSMOS\work_orders\drop")
PROBE_LAST = CCR / "WOMBAT_LAYER_PROBE_last.txt"
PROBE_OUT = CCR / "WOMBAT_LAYER_PROBE.json"
DROPS_LAST = CCR / "WOMBAT_LUNA_last.txt"

PROBE_KEYS = (
    "role", "model", "effort", "harness", "wrapper_role", "skill",
    "tools_allow", "cwd", "wrap_first_line", "style_model",
)


class HarvestError(RuntimeError):
    pass


def _extract_json(text: str):
    if not text or not str(text).strip():
        raise HarvestError("empty last-message")
    s = text.strip()
    m = re.search(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", s, re.S)
    if m:
        return json.loads(m.group(1))
    start = s.find("{")
    start_a = s.find("[")
    if start_a >= 0 and (start < 0 or start_a < start):
        return json.loads(s[start_a:s.rfind("]") + 1])
    if start >= 0:
        return json.loads(s[start:s.rfind("}") + 1])
    raise HarvestError("no JSON object/array in last-message")


def harvest_probe(last: Path = PROBE_LAST, dest: Path = PROBE_OUT) -> dict:
    obj = _extract_json(last.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise HarvestError("probe last-message is not a JSON object")
    missing = [k for k in PROBE_KEYS if k not in obj]
    if missing:
        raise HarvestError("probe missing keys: " + ",".join(missing))
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8", newline="\n")
    return {"ok": True, "path": str(dest), "bytes": dest.stat().st_size}


def harvest_drops(last: Path = DROPS_LAST, dest_dir: Path = DROP) -> dict:
    obj = _extract_json(last.read_text(encoding="utf-8"))
    rows = obj if isinstance(obj, list) else [obj]
    dest_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for i, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise HarvestError(f"drop {i} is not an object")
        name = row.get("file") or row.get("path")
        if not name:
            oid = str(row.get("order_id") or f"n{i:02d}")
            name = f"wo-harvest-wombat-{i:02d}.json"
            row = dict(row)
            row.setdefault("order_id", oid)
        path = Path(name)
        if path.is_absolute():
            out = path
        else:
            out = dest_dir / path.name
        if out.parent.resolve() not in (dest_dir.resolve(), CCR.resolve()):
            raise HarvestError(f"refuse write outside drop/ccr: {out}")
        if "wombat" not in out.name.lower() and out.parent.resolve() == dest_dir.resolve():
            raise HarvestError(f"drop name must contain wombat: {out.name}")
        out.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8", newline="\n")
        written.append(str(out))
    return {"ok": True, "n": len(written), "paths": written}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--probe", action="store_true")
    g.add_argument("--drops", action="store_true")
    a = ap.parse_args(argv)
    try:
        out = harvest_probe() if a.probe else harvest_drops()
    except (HarvestError, json.JSONDecodeError, OSError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
