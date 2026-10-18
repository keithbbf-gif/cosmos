#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_models_from_catalog — regenerate the gateway registry (models.json)
from the TokenCenter catalog, verified against OpenRouter's public model list.

Source of truth for WHICH models are sold: the paid lane of lanes.json joined
with models.json pricing from the catalog base (default https://tokenctr.com/data,
the local copy refreshed from the mdata.mdrater.com hub). OpenRouter's public
GET /api/v1/models (no key) is the check that a model is live and what it costs
right now: if the catalog price disagrees, the live OpenRouter price is used so
zero markup stays true, and the disagreement is reported.

Skipped: missing pricing, negative/variable pricing (-1 routers), not on
OpenRouter. Non-OpenRouter entries already in the target file are kept.

Usage:
  python3 build_models_from_catalog.py [--base URL] [--out PATH] [--public-out PATH] [--dry-run]

--public-out also writes a public price list (ids, names, split prices only; no
secrets) for the site estimator, e.g. ~/tokenctr.com/data/prices.json.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

OR_MODELS = "https://openrouter.ai/api/v1/models"


def _get(url: str):
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "tokencenter-registry/1"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def _num(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if f == f else None


def build(base: str, existing: dict) -> tuple[dict, dict]:
    base = base.rstrip("/")
    lanes = _get(base + "/lanes.json")
    catalog = {m["id"]: m for m in _get(base + "/models.json") if isinstance(m, dict) and m.get("id")}
    live = {m["id"]: m for m in _get(OR_MODELS).get("data", [])}
    out = {k: v for k, v in existing.items() if isinstance(v, dict) and v.get("rail") != "openrouter"}
    report = {"paid_ids": len(lanes.get("paid", [])), "added": 0, "skipped_missing_price": [],
              "skipped_negative_or_variable": [], "skipped_not_on_openrouter": [], "price_from_openrouter_live": []}
    for mid in lanes.get("paid", []):
        p = (catalog.get(mid) or {}).get("pricing") or {}
        a, b = _num(p.get("prompt")), _num(p.get("completion"))
        if a is None or b is None:
            report["skipped_missing_price"].append(mid); continue
        if a < 0 or b < 0:
            report["skipped_negative_or_variable"].append(mid); continue
        lv = live.get(mid)
        if not lv:
            report["skipped_not_on_openrouter"].append(mid); continue
        la, lb = _num((lv.get("pricing") or {}).get("prompt")), _num((lv.get("pricing") or {}).get("completion"))
        if la is None or lb is None or la < 0 or lb < 0:
            report["skipped_negative_or_variable"].append(mid); continue
        if abs(la - a) > 1e-15 or abs(lb - b) > 1e-15:
            report["price_from_openrouter_live"].append(mid)
            a, b = la, lb
        extras = sorted(k for k, v in (lv.get("pricing") or {}).items()
                        if k not in ("prompt", "completion") and _num(v) not in (None, 0.0))
        out[mid] = {
            "rail": "openrouter", "endpoint": "openrouter", "lane": "A",
            "price_rule": "passthrough (zero markup)",
            "prompt_per_m_usd": round(a * 1e6, 9), "completion_per_m_usd": round(b * 1e6, 9),
            "context_length": lv.get("context_length") or (catalog.get(mid) or {}).get("context_length"),
            "name": (catalog.get(mid) or {}).get("name") or lv.get("name"),
            "vendor_extra_pricing": extras,
        }
        report["added"] += 1
    return out, report


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=os.environ.get("TOKENCTR_CATALOG_BASE", "https://tokenctr.com/data"))
    ap.add_argument("--out", default=str(Path(os.environ.get("COSMOS_PAY_ROOT", str(Path.home() / ".cosmos_pay"))) / "models.json"))
    ap.add_argument("--public-out", default="")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    out_path = Path(a.out)
    existing = json.loads(out_path.read_text(encoding="utf-8")) if out_path.exists() else {}
    models, report = build(a.base, existing)
    summary = {k: (len(v) if isinstance(v, list) else v) for k, v in report.items()}
    print(json.dumps({"summary": summary, "skipped_negative_or_variable": report["skipped_negative_or_variable"],
                      "skipped_not_on_openrouter": report["skipped_not_on_openrouter"],
                      "skipped_missing_price": report["skipped_missing_price"],
                      "price_from_openrouter_live": report["price_from_openrouter_live"]}, indent=1))
    if a.dry_run:
        return
    tmp = out_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(models, indent=1, sort_keys=True), encoding="utf-8")
    os.chmod(tmp, 0o600)
    os.replace(tmp, out_path)  # atomic; the gateway hot-reloads on mtime
    print(f"wrote {out_path} ({len(models)} entries)")
    if a.public_out:
        write_public(models, Path(a.public_out))


def write_public(models: dict, path: Path) -> None:
    import time
    rows = [{"id": k, "name": v.get("name") or k,
             "prompt_per_m_usd": v["prompt_per_m_usd"], "completion_per_m_usd": v["completion_per_m_usd"],
             "context_length": v.get("context_length")}
            for k, v in sorted(models.items())
            if v.get("rail") == "openrouter" and "prompt_per_m_usd" in v and "completion_per_m_usd" in v]
    doc = {"generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "unit": "USD per 1M tokens", "markup": 0, "source": "gateway registry (models.json)", "models": rows}
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(doc, separators=(",", ":")), encoding="utf-8")
    os.chmod(tmp, 0o644)
    os.replace(tmp, path)
    print(f"wrote public price list {path} ({len(rows)} models)")


if __name__ == "__main__":
    sys.exit(main())
