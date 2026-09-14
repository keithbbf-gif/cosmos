#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_jukebox_panel — GET /api/v1/jukebox handler for cDeck."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "cosmos"))

from cosmos_paths import CosmosPaths  # noqa: E402

SCHEMA = "cdeck-jukebox/1"
LANE_DIRS = ("_lanes/lg", "_lanes/pb")


def _scan_jobs(q: Path) -> list[dict]:
    jobs = []
    lanes = [q] + [q / lane for lane in LANE_DIRS]
    for lane_dir in lanes:
        if not lane_dir.is_dir():
            continue
        try:
            for p in sorted(lane_dir.iterdir()):
                if p.is_file() and p.suffix.lower() == ".py" and not p.name.startswith("_"):
                    mtime = p.stat().st_mtime
                    jobs.append({
                        "file": p.name,
                        "lane": lane_dir.name if lane_dir != q else "root",
                        "mtime": mtime,
                        "state": "QUEUED",
                    })
        except OSError:
            continue
    return jobs


def _load_manifest_jobs(q: Path) -> list[dict]:
    mdir = q / "manifests"
    jobs = []
    if not mdir.is_dir():
        return jobs
    try:
        for p in sorted(mdir.iterdir()):
            if p.is_file() and p.suffix.lower() == ".json":
                try:
                    obj = json.loads(p.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    obj = {}
                jobs.append({
                    "file": p.name,
                    "state": obj.get("state", "QUEUED"),
                    "task": obj.get("task") or obj.get("name"),
                    "lane": obj.get("lane") or "manifests",
                    "mtime": p.stat().st_mtime,
                })
    except OSError:
        pass
    return jobs


def handle_get(root: str, expected_tree_id: str | None = None) -> tuple[int, dict]:
    try:
        paths = CosmosPaths(root, expected_tree_id=expected_tree_id)
        tree_id = paths.sentinel.tree_id
    except Exception as e:  # noqa: BLE001
        return 503, {"ok": False, "error": "PATHS_ERROR", "detail": str(e)[:200]}

    q = paths.role("queue")
    py_jobs = _scan_jobs(q)
    manifest_jobs = _load_manifest_jobs(q)
    all_jobs = manifest_jobs + py_jobs

    in_flight = [j for j in all_jobs if j.get("state") in ("RUNNING", "QUEUED")]
    done = [j for j in all_jobs if j.get("state") in ("CLEAN", "FINDINGS")]
    broke = [j for j in all_jobs if j.get("state") == "BROKE"]

    return 200, {
        "schema": SCHEMA,
        "ok": True,
        "tree_id": tree_id,
        "jobs_n": len(all_jobs),
        "in_flight_n": len(in_flight),
        "broke_n": len(broke),
        "done_n": len(done),
        "jobs": all_jobs[:50],
    }
