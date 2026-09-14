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


def _load_registry(paths: CosmosPaths) -> dict | None:
    p = paths.role("registry", "rails.json")
    if not p.is_file():
        return None
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return obj if isinstance(obj, dict) else None


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
    source = "disk"

    if reg is not None:
        matrix = reg.get("matrix") or []
        reg_nodes = reg.get("nodes") or []
        for nid in reg_nodes:
            nodes.append({"id": nid, "label": nid, "type": "rail"})
        for m in matrix:
            lid = m.get("link_id") or m.get("id") or ""
            if lid not in {n["id"] for n in nodes}:
                nodes.append({"id": lid, "label": lid, "type": "rail"})
    elif kernel_matrix is not None:
        matrix = kernel_matrix
        source = "kernel.matrix"
        for m in matrix:
            lid = m.get("link_id") or m.get("id") or ""
            nodes.append({"id": lid, "label": lid, "type": "rail"})
    else:
        source = "empty"

    return 200, {
        "schema": SCHEMA,
        "ok": True,
        "tree_id": tree_id,
        "topology": {"nodes": nodes, "edges": edges},
        "registry": {
            "available": len(matrix) > 0,
            "source": source,
            "matrix": matrix,
        },
    }
