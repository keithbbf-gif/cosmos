#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pins for GET /api/v1/nodemap OA node wiring (registry + routing catalog)."""
from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "cosmos"))
sys.path.insert(0, str(REPO / "builds" / "cdeck"))

from cosmos_kernel import install  # noqa: E402
from cosmos_nodemap_panel import (  # noqa: E402
    ROUTING_NODES,
    _OA_API_CTX,
    _OA_CODEX_CTX,
    handle_get,
)

RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((label, bool(ok), detail[:400]))


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="nodemap_oa_"))
    root = install(td / "live", tree_id="nodemap-oa")
    now = time.time()

    reg = root / "registry" / "rails.json"
    reg.parent.mkdir(parents=True, exist_ok=True)
    reg.write_text(
        json.dumps({
            "schema": "cosmos-registry/1",
            "measured_at": now,
            "proof_ttl_s": 3600.0,
            "count": 2,
            "nodes": ["oa-api", "codex-cli"],
            "matrix": [
                {
                    "link_id": "oa-api",
                    "rail_type": "API",
                    "route": "core->models",
                    "verified": True,
                    "model": "gpt-5.6-terra",
                    "rc": 0,
                    "body_bytes": 4,
                    "age_s": 12.0,
                    "proof_state": "LIVE",
                },
                {
                    "link_id": "codex-cli",
                    "rail_type": "CLI",
                    "route": "core->code",
                    "verified": True,
                    "model": "gpt-5.4-codex",
                    "rc": 0,
                    "body_bytes": 4,
                    "age_s": 8.0,
                    "proof_state": "LIVE",
                },
            ],
            "stale": [
                {
                    "link_id": "sgh-api",
                    "verified": False,
                    "proof_state": "STALE",
                    "model": "grok-4.6",
                    "age_s": 7200.0,
                },
            ],
            "stale_count": 1,
        }),
        encoding="utf-8",
    )

    code, body = handle_get(str(root))
    check("handle_get returns 200", code == 200 and body.get("ok") is True)
    oa = next(n for n in body["topology"]["nodes"] if n["id"] == "OA")
    check("OA node declares whole-corpus read hands",
          oa.get("hands") == "whole-corpus read")
    rails = {r["link_id"]: r for r in oa["rails"]}
    check("OA codex-cli ceiling is 272k",
          rails["codex-cli"]["context_tokens"] == _OA_CODEX_CTX)
    check("OA oa-api ceiling is 1.05M",
          rails["oa-api"]["context_tokens"] == _OA_API_CTX)
    check("OA oa-api model is vendor-emitted from registry only",
          rails["oa-api"]["model"] == "gpt-5.6-terra")
    check("OA codex-cli model is vendor-emitted from registry only",
          rails["codex-cli"]["model"] == "gpt-5.4-codex")
    sgh = next(n for n in body["topology"]["nodes"] if n["id"] == "SGH")
    g46 = next(n for n in body["topology"]["nodes"] if n["id"] == "G46")
    check("SGH+GBW independence note is present on both xai nodes",
          "not independent" in (sgh.get("independence_note") or "")
          and "not independent" in (g46.get("independence_note") or ""))
    mx = body["registry"]["matrix"]
    check("registry matrix includes stale rows for RED rendering",
          any(r.get("link_id") == "sgh-api" and r.get("proof_state") == "STALE"
              for r in mx))
    check("ROUTING_NODES includes OA with two rails",
          any(n["id"] == "OA" and len(n["rails"]) == 2 for n in ROUTING_NODES))

    failed = [r for r in RESULTS if not r[1]]
    for label, ok, detail in RESULTS:
        mark = "OK  " if ok else "FAIL"
        print("  %s  %s%s" % (mark, label, ("  [" + detail + "]") if detail and not ok else ""))
    print("SELFTEST %s %d/%d" % (
        "PASS" if not failed else "FAIL", len(RESULTS) - len(failed), len(RESULTS)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
