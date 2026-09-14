#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_nodemap_panel — GET /api/v1/nodemap handler for cDeck.

Logical routing nodes (COMPETENCY-aligned) bind to live registry rows.
`model` is never synthesized: it is quoted only from a proven live rail
measurement on disk (live/registry/rails.json) or from kernel overlay rows
that carry the vendor-emitted name. UNMEASURED is explicit; stale proofs
are listed with proof_state=STALE (UI renders RED).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "cosmos"))

from cosmos_paths import CosmosPaths  # noqa: E402
from cosmos_registry import PROOF_TTL_S  # noqa: E402

SCHEMA = "cdeck-nodemap/2"

# Context ceilings are vendor-documented rails, not live measurements.
# Live `model` on each row comes only from registry proof rows.
_OA_CODEX_CTX = 272_000
_OA_API_CTX = 1_050_000

ROUTING_NODES = (
    {
        "id": "DOM",
        "label": "DOM · Playwright MCP",
        "family": "dom",
        "rails": ({"link_id": "playwright-dom", "context_tokens": 0},),
        "independence_note": "",
    },
    {
        "id": "G46",
        "label": "G46 · Grok Build (GBW)",
        "family": "xai",
        "rails": ({"link_id": "gw-api", "context_tokens": 500_000},),
        "independence_note": (
            "SGH and GBW (G46) share the xai family — they are not "
            "independent checks of each other."
        ),
    },
    {
        "id": "Cursor",
        "label": "Cursor · Cloud Agents",
        "family": "cursor",
        "rails": ({"link_id": "cursor-api", "context_tokens": 0},),
        "independence_note": "",
    },
    {
        "id": "SGH",
        "label": "SGH · Grok research",
        "family": "xai",
        "rails": ({"link_id": "sgh-api", "context_tokens": 500_000},),
        "independence_note": (
            "SGH and GBW (G46) share the xai family — they are not "
            "independent checks of each other."
        ),
    },
    {
        "id": "GEM",
        "label": "GEM · Gemini API",
        "family": "google",
        "rails": ({"link_id": "gem-api", "context_tokens": 1_048_576},),
        "independence_note": "",
    },
    {
        "id": "OA",
        "label": "OA · OpenAI gpt-5.6",
        "family": "openai",
        "hands": "whole-corpus read",
        "rails": (
            {
                "link_id": "codex-cli",
                "context_tokens": _OA_CODEX_CTX,
                "ceiling_label": "Codex CLI",
            },
            {
                "link_id": "oa-api",
                "context_tokens": _OA_API_CTX,
                "ceiling_label": "Responses API",
            },
        ),
        "independence_note": "",
    },
)


def _load_registry(paths: CosmosPaths) -> dict | None:
    p = paths.role("registry", "rails.json")
    if not p.is_file():
        return None
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return obj if isinstance(obj, dict) else None


def _merge_matrix(reg: dict | None, kernel_matrix: list | None) -> tuple[list[dict], str]:
    """Live + stale rows with proof_state. Never invent model names."""
    if reg is not None:
        live = [dict(r) for r in (reg.get("matrix") or [])]
        stale = [dict(r) for r in (reg.get("stale") or [])]
        for r in live:
            r.setdefault("proof_state", "LIVE" if r.get("verified") else "UNMEASURED")
        for r in stale:
            r["verified"] = False
            r.setdefault("proof_state", "STALE")
        return live + stale, "disk"
    if kernel_matrix is not None:
        out = []
        for r in kernel_matrix:
            row = dict(r)
            if row.get("proof_state"):
                out.append(row)
            elif row.get("verified") is True:
                row["proof_state"] = "LIVE"
                out.append(row)
            elif row.get("verified") is False:
                row["proof_state"] = "STALE"
                out.append(row)
            else:
                row["proof_state"] = "UNMEASURED"
                out.append(row)
        return out, "kernel.matrix"
    return [], "empty"


def _index_links(matrix: list[dict]) -> dict[str, dict]:
    idx: dict[str, dict] = {}
    for row in matrix:
        lid = str(row.get("link_id") or row.get("id") or "")
        if lid:
            idx[lid] = row
    return idx


def _compose_routing_nodes(link_idx: dict[str, dict]) -> list[dict]:
    nodes: list[dict] = []
    edges: list[dict] = []
    for spec in ROUTING_NODES:
        rail_rows = []
        for bind in spec["rails"]:
            lid = bind["link_id"]
            live = link_idx.get(lid)
            model = ""
            proof_state = "UNMEASURED"
            age_s = None
            if live:
                model = str(live.get("model") or "").strip()
                proof_state = str(live.get("proof_state") or "UNMEASURED")
                age_s = live.get("age_s")
                if proof_state == "UNMEASURED" and live.get("verified") is True:
                    proof_state = "LIVE"
                elif proof_state == "UNMEASURED" and live.get("verified") is False:
                    proof_state = "STALE"
            rail_rows.append({
                **bind,
                "model": model,
                "proof_state": proof_state,
                "age_s": age_s,
                "verified": live.get("verified") if live else None,
            })
            edges.append({"from": spec["id"], "to": lid, "kind": "rail"})
        nodes.append({
            "id": spec["id"],
            "label": spec["label"],
            "type": "routing",
            "family": spec.get("family"),
            "hands": spec.get("hands") or "",
            "rails": rail_rows,
            "independence_note": spec.get("independence_note") or "",
        })
    return nodes, edges


def handle_get(root: str, expected_tree_id: str | None = None,
               kernel_matrix: list | None = None) -> tuple[int, dict]:
    """kernel_matrix is injected by Core's _nodemap_overlay_kernel when disk is empty."""
    try:
        paths = CosmosPaths(root, expected_tree_id=expected_tree_id)
        tree_id = paths.sentinel.tree_id
    except Exception as e:  # noqa: BLE001
        return 503, {"ok": False, "error": "PATHS_ERROR", "detail": str(e)[:200]}

    reg = _load_registry(paths)
    matrix, source = _merge_matrix(reg, kernel_matrix)
    link_idx = _index_links(matrix)
    nodes, edges = _compose_routing_nodes(link_idx)

    proof_ttl = None
    if reg is not None:
        proof_ttl = reg.get("proof_ttl_s")
    if proof_ttl is None:
        proof_ttl = PROOF_TTL_S

    stale_count = sum(1 for r in matrix if r.get("proof_state") == "STALE")
    live_count = sum(1 for r in matrix if r.get("proof_state") == "LIVE")

    return 200, {
        "schema": SCHEMA,
        "ok": True,
        "tree_id": tree_id,
        "topology": {"nodes": nodes, "edges": edges},
        "registry": {
            "available": bool(matrix),
            "source": source,
            "schema": (reg or {}).get("schema") or "cosmos-registry/1",
            "proof_ttl_s": proof_ttl,
            "count": live_count,
            "stale_count": stale_count,
            "matrix": matrix,
        },
    }
