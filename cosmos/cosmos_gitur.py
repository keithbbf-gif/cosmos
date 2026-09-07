#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gitur projection — GitHub + GitLab + Cursor as one BUILD triad.

GET /api/v1/gitur folds rails matrix + Cursor probe/launch files + jukebox
rows that already name the triad. Does not poll GitHub/GitLab APIs. Does not
call Cursor GET /v1/repositories (1/min). Does not invent PR lists.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from cosmos_ccr import read_lease
from cosmos_cursor_rail import LAUNCH_NAME, PROBE_NAME

SCHEMA = "cosmos-gitur/1"
LEGS = (
    ("cursor-api", "Cursor",
     "Lane B BUILD. Cloud Agents. Probe is GET /v1/me."),
    ("github-forge", "GitHub",
     "origin, PRs, Copilot review. Not the live-tree writer."),
    ("gitlab-forge", "GitLab",
     "CI is the execute-the-gate. Duo proposes."),
)
JOB_NEEDLES = ("gitur", "github", "gitlab", "cursor", "glab", "copilot")


class GiturError(RuntimeError):
    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _read_json(p: Path) -> dict | None:
    if not p.is_file():
        return None
    try:
        rec = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"kind": "BROKE"}
    return rec if isinstance(rec, dict) else {"kind": "BROKE"}


def _public_probe(rec: dict | None) -> dict | None:
    if not rec:
        return None
    if rec.get("kind") == "BROKE":
        return rec
    live = rec.get("live_value") if isinstance(rec.get("live_value"), dict) else {}
    return {
        "gate": rec.get("gate"),
        "gated_at": rec.get("gated_at"),
        "identity_ok": rec.get("identity_ok"),
        "kernel_attached": rec.get("kernel_attached"),
        "key_ok": rec.get("key_ok"),
        "key_last4": rec.get("key_last4"),
        "link_id": rec.get("link_id"),
        "http": live.get("http") or rec.get("http"),
        "apiKeyName": live.get("apiKeyName"),
        "attach_refused": bool((rec.get("attach_refusal") or {}).get("refused")),
    }


def _public_launch(rec: dict | None) -> dict | None:
    if not rec:
        return None
    if rec.get("kind") == "BROKE":
        return rec
    keep = {}
    for k in ("ok", "kind", "agent_id", "run_id", "pr_url", "branch",
              "http", "detail", "node", "status"):
        if rec.get(k) is not None:
            keep[k] = rec.get(k)
    return keep or None


def _gitur_job(row: dict) -> bool:
    blob = " ".join(str(row.get(k) or "") for k in
                    ("command", "job_id", "lane", "node", "detail")).lower()
    return any(n in blob for n in JOB_NEEDLES)


def snapshot(kernel) -> dict:
    """Projection. kernel.registry / paths / jukebox only — no vendor poll."""
    paths = kernel.paths
    matrix = []
    rails_err = None
    try:
        reg = getattr(kernel, "registry", None)
        if reg is None:
            rails_err = "REGISTRY_NOT_COMPOSED"
        else:
            matrix = list(reg.matrix() or [])
    except Exception as e:  # noqa: BLE001
        rails_err = f"{type(e).__name__}: {e}"[:200]
        matrix = []
    by_id = {r.get("link_id"): r for r in matrix if isinstance(r, dict)}
    legs = []
    for lid, name, role in LEGS:
        row = by_id.get(lid)
        legs.append({
            "id": lid,
            "name": name,
            "role": role,
            "present": row is not None,
            "verified": None if row is None else row.get("verified"),
            "age_s": None if row is None else row.get("age_s"),
            "route": None if row is None else row.get("route"),
            "rail_type": None if row is None else row.get("rail_type"),
        })
    lease = None
    try:
        lease = read_lease(paths)
    except Exception as e:  # noqa: BLE001
        lease = {"kind": "BROKE", "detail": f"{type(e).__name__}: {e}"[:200]}
    ccr = {"held": False}
    if isinstance(lease, dict) and lease.get("schema"):
        ccr = {
            "held": True,
            "sid": lease.get("sid"),
            "stream": lease.get("stream"),
            "tree_id": lease.get("tree_id"),
            "taken_at": lease.get("taken_at"),
        }
    elif isinstance(lease, dict) and lease.get("kind"):
        ccr = {"held": False, "kind": lease.get("kind"),
               "detail": lease.get("detail")}

    jobs = []
    jobs_kind = "UNMEASURED"
    try:
        import sys
        from pathlib import Path as _P
        _cdeck = str((_P(__file__).resolve().parent.parent / "builds" / "cdeck").resolve())
        if _cdeck not in sys.path:
            sys.path.insert(0, _cdeck)
        from cosmos_jukebox_panel import handle_get
        code, body = handle_get(str(paths.root),
                                expected_tree_id=paths.sentinel.tree_id)
        if code != 200:
            jobs_kind = (body or {}).get("error") or f"HTTP_{code}"
        else:
            q = (body or {}).get("queue") or {}
            raw = q.get("jobs") if isinstance(q, dict) else None
            if not q.get("available"):
                jobs_kind = (q.get("kind") if isinstance(q, dict) else None) or "QUEUE_UNAVAILABLE"
            else:
                jobs_kind = "jukebox"
                for row in (raw or []):
                    if isinstance(row, dict) and _gitur_job(row):
                        jobs.append({
                            "job_id": row.get("job_id"),
                            "st": row.get("st"),
                            "command": row.get("command"),
                            "priority": row.get("priority"),
                            "age_s": row.get("age_s"),
                            "lane": row.get("lane"),
                            "stale_flag": row.get("stale_flag"),
                        })
    except Exception as e:  # noqa: BLE001
        jobs_kind = f"{type(e).__name__}: {e}"[:200]

    return {
        "schema": SCHEMA,
        "measured_at": time.time(),
        "gitur": "GitHub + GitLab + Cursor",
        "note": ("Projection of rails + Cursor probe/launch files + jukebox "
                 "rows that already name the triad. Does not poll GitHub, "
                 "GitLab, or Cursor /v1/repositories."),
        "rails_err": rails_err,
        "ccr": ccr,
        "legs": legs,
        "cursor": _public_probe(_read_json(paths.config(PROBE_NAME))),
        "launch": _public_launch(_read_json(paths.config(LAUNCH_NAME))),
        "jobs": jobs[:80],
        "jobs_n": len(jobs),
        "jobs_kind": jobs_kind,
    }
