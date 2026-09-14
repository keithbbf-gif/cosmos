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

# Competency routing nodes (link_id is the live rail; model comes from proof only).
ROUTING_NODES = (
    {
        "id": "SGH",
        "link_id": "sgh-api",
        "label": "SGH · Grok research",
        "role": "web-research",
        "family": "g46-grok",
        "note": (
            "Paid rail (sgh-api): web + GitHub research. "
            "Search is refused without spend_ok."
        ),
    },
    {
        "id": "GBW",
        "link_id": "gw-api",
        "label": "GBW · Grok Build",
        "role": "code-build",
        "family": "gw-grok-build",
        "note": "Grok Build TUI (grok CLI); same xAI vendor as SGH.",
    },
)

INDEPENDENCE_NOTES = (
    {
        "nodes": ["SGH", "GBW"],
        "link_ids": ["sgh-api", "gw-api"],
        "note": (
            "SGH (sgh-api) and GBW (gw-api) are one xAI vendor family — "
            "not independent checks of each other."
        ),
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


def _index_matrix(matrix: list, stale: list) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for row in matrix or []:
        if not isinstance(row, dict):
            continue
        lid = str(row.get("link_id") or row.get("id") or "")
        if lid:
            out[lid] = dict(row)
    for row in stale or []:
        if not isinstance(row, dict):
            continue
        lid = str(row.get("link_id") or row.get("id") or "")
        if lid:
            tagged = dict(row)
            tagged.setdefault("proof_state", "STALE")
            tagged["verified"] = False
            out[lid] = tagged
    return out


def _merge_routing_nodes(by_link: dict[str, dict]) -> list[dict]:
    nodes: list[dict] = []
    for spec in ROUTING_NODES:
        lid = spec["link_id"]
        proof = by_link.get(lid) or {}
        model = str(proof.get("model") or "")
        proof_state = proof.get("proof_state")
        if not proof_state:
            if proof.get("verified") is True:
                proof_state = "FRESH"
            elif proof:
                proof_state = "STALE" if proof.get("verified") is False else "UNMEASURED"
            else:
                proof_state = "UNMEASURED"
        nodes.append({
            **spec,
            "type": "routing",
            "model": model,
            "model_source": "vendor live_call" if model else "",
            "verified": proof.get("verified"),
            "proof_state": proof_state,
            "age_s": proof.get("age_s"),
            "rc": proof.get("rc"),
            "body_bytes": proof.get("body_bytes"),
        })
    return nodes


def handle_get(root: str, expected_tree_id: str | None = None,
               kernel_matrix: list | None = None,
               kernel_stale: list | None = None) -> tuple[int, dict]:
    """kernel_matrix / kernel_stale injected by Core's nodemap overlay."""
    try:
        paths = CosmosPaths(root, expected_tree_id=expected_tree_id)
        tree_id = paths.sentinel.tree_id
    except Exception as e:  # noqa: BLE001
        return 503, {"ok": False, "error": "PATHS_ERROR", "detail": str(e)[:200]}

    reg = _load_registry(paths)

    edges: list[dict] = []
    matrix: list[dict] = []
    stale: list[dict] = []
    source = "empty"

    if reg is not None:
        matrix = reg.get("matrix") or []
        stale = reg.get("stale") or []
        source = "disk"
    elif kernel_matrix is not None:
        matrix = kernel_matrix
        stale = kernel_stale or []
        source = "kernel.matrix"

    by_link = _index_matrix(matrix, stale)
    routing = _merge_routing_nodes(by_link)

    # Topology: routing nodes first, then any other proven link_ids.
    seen = {n["id"] for n in routing}
    nodes = list(routing)
    for lid, row in sorted(by_link.items()):
        if lid in {s["link_id"] for s in ROUTING_NODES}:
            continue
        nid = lid
        if nid not in seen:
            nodes.append({
                "id": nid,
                "label": nid,
                "type": "rail",
                "link_id": lid,
                "model": str(row.get("model") or ""),
                "verified": row.get("verified"),
                "proof_state": row.get("proof_state"),
                "age_s": row.get("age_s"),
            })
            seen.add(nid)

    proof_ttl = None
    if reg is not None:
        proof_ttl = reg.get("proof_ttl_s")

    return 200, {
        "schema": SCHEMA,
        "ok": True,
        "tree_id": tree_id,
        "topology": {"nodes": nodes, "edges": edges},
        "registry": {
            "available": len(matrix) > 0 or len(stale) > 0,
            "source": source,
            "proof_ttl_s": proof_ttl,
            "matrix": matrix,
            "stale": stale,
        },
        "independence_notes": list(INDEPENDENCE_NOTES),
    }
