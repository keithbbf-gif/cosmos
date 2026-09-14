#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_nodemap_panel — GET /api/v1/nodemap handler for cDeck."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "cosmos"))

from cosmos_paths import CosmosPaths  # noqa: E402

SCHEMA = "cdeck-nodemap/1"

# Agent-facing catalog (not a second registry). Rails prove via ledger;
# these rows carry role + independence notes for the deck only.
NODE_CATALOG = {
    "gem-api": {
        "agent": "GEM",
        "maker": "Gemini",
        "family": "gem-vertex",
        "role": (
            "numeric/verification/DOI; impossibility detector; "
            "take verdicts not digits"
        ),
        "independence": (
            "Different family from grok-sgh/gw (xAI). "
            "SGH+GBW are the same family — not independent checks of each other."
        ),
    },
    "sgh-api": {
        "agent": "SGH",
        "maker": "Grok",
        "family": "g46-grok",
        "independence": (
            "Same xAI family as gw-api / GBW — counts as one family for "
            "vendor-plural seating, not two independent votes."
        ),
    },
    "gw-api": {
        "agent": "GBW",
        "maker": "Grok Build",
        "family": "gw-grok-build",
        "independence": (
            "Same xAI family as sgh-api / SGH — not an independent check of SGH."
        ),
    },
}


def _load_registry(paths: CosmosPaths) -> dict | None:
    p = paths.role("registry", "rails.json")
    if not p.is_file():
        return None
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return obj if isinstance(obj, dict) else None


def _enrich_node(link_id: str, proof: dict | None) -> dict:
    cat = NODE_CATALOG.get(link_id) or {}
    row = {
        "id": link_id,
        "label": cat.get("agent") or link_id,
        "type": "rail",
        "link_id": link_id,
    }
    for key in ("agent", "maker", "family", "role", "independence"):
        if cat.get(key):
            row[key] = cat[key]
    if proof:
        for key in ("model", "verified", "age_s", "rc", "body_bytes",
                    "proof_state", "route", "rail_type"):
            if key in proof:
                row[key] = proof[key]
    return row


def handle_get(root: str, expected_tree_id: str | None = None,
               kernel_matrix: list | None = None) -> tuple[int, dict]:
    """kernel_matrix is injected by Core's _nodemap_overlay_kernel."""
    try:
        paths = CosmosPaths(root, expected_tree_id=expected_tree_id)
        tree_id = paths.sentinel.tree_id
    except Exception as e:  # noqa: BLE001
        return 503, {"ok": False, "error": "PATHS_ERROR", "detail": str(e)[:200]}

    reg = _load_registry(paths)

    nodes: list[dict] = []
    edges: list[dict] = []
    matrix: list[dict] = []
    stale: list[dict] = []
    source = "disk"

    if reg is not None:
        matrix = list(reg.get("matrix") or [])
        stale = list(reg.get("stale") or [])
        by_id = {r.get("link_id"): r for r in matrix + stale if r.get("link_id")}
        seen = set()
        for lid in reg.get("nodes") or []:
            nodes.append(_enrich_node(lid, by_id.get(lid)))
            seen.add(lid)
        for m in matrix + stale:
            lid = m.get("link_id") or m.get("id") or ""
            if lid and lid not in seen:
                nodes.append(_enrich_node(lid, m))
                seen.add(lid)
    elif kernel_matrix is not None:
        matrix = list(kernel_matrix)
        source = "kernel.projection_view"
        for m in matrix:
            lid = m.get("link_id") or m.get("id") or ""
            nodes.append(_enrich_node(lid, m))
    else:
        source = "empty"

    return 200, {
        "schema": SCHEMA,
        "ok": True,
        "tree_id": tree_id,
        "topology": {"nodes": nodes, "edges": edges},
        "registry": {
            "available": len(matrix) > 0 or len(stale) > 0,
            "source": source,
            "matrix": matrix,
            "stale": stale,
            "stale_count": len(stale),
            "proof_ttl_s": (reg or {}).get("proof_ttl_s"),
            "catalog": NODE_CATALOG,
        },
    }
