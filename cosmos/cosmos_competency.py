#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_competency — COMPETENCY.toml is ROUTING input, not a document.

docs/COMPETENCY.toml declares the gate `skills.<task_type>.<node>.rating`.
Until this module, no cosmos/ code read the file (two comments in
cosmos_dispatch.py named it; FEATURE_MASTER F-27). Availability is HANDED
IN (registry/prober, or a dispatchable subset) — the file does not get to
claim a node is live.

Algorithm (from the file's own header): among nodes with
skills.<task_type>.<node>.possessed==true AND currently AVAILABLE, pick
max(rating). Ties: prefer nodes.<id>.family=="dom". Remaining ties:
router.nodes_order.

    pick(matrix, "web-research", {"G46", "SGH", "GEM"}) -> "SGH"

Typed refusals, never a guessed node: UNREADABLE, BAD_SCHEMA, UNKNOWN_TASK,
NO_CANDIDATE, NO_DISPATCH.
"""
from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Iterable


class CompetencyError(RuntimeError):
    """kind in {UNREADABLE, BAD_SCHEMA, UNKNOWN_TASK, NO_CANDIDATE, NO_DISPATCH}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


SCHEMA = "competency/1"

# Nodes WD2 can actually dispatch today without an unwatched bucket or a
# missing kind. GEM/OA are kind=gem/oa handoffs (F-65 workers never
# started); DOM has no dispatch kind. Callers pass a wider `available`
# when those paths are live. Cursor is added by the caller when the key
# exists — it is not implied by the matrix.
DISPATCHABLE = frozenset({"G46", "SGH"})

NODE_AGENT_KIND = {
    "G46": ("G46", "grok"),
    "SGH": ("SGH", "grok"),
    "GEM": ("GEM", "gem"),
    "OA": ("OA", "oa"),
    "Cursor": ("Cursor", "cursor"),
}

# Specific-first. code-build vs web-research: coding wins (dispatch rule).
_TASK_HINTS = (
    ("vendor-plural-critique", (
        "vendor-plural", "different-family", "different family",
        "gem/oa", "oa critique", "gem critique",
    )),
    ("DOM-automation", (
        "playwright", "dom-automation", "dom automation",
        "computer-use", "computer use", "browser automation",
    )),
    ("bulk-structured-extraction", (
        "structured extraction", "bulk extract", "extract structured",
    )),
    ("long-context-reasoning", (
        "long-context", "long context",
    )),
    ("code-review-critique", (
        "code-review", "code review", "critique", "vetting", "vetter",
    )),
    ("docs-authoring", (
        "docs-author", "documentation", "authoring",
    )),
    ("web-research", (
        "research", "scout", "survey", "web-search", "web search",
    )),
    ("code-build", (
        "implement", "code", "build", "wire", "harden", "fix",
        "daemon", "clock", "dispatch", "runner", "patch",
    )),
)


def default_path(repo: Path | str | None = None) -> Path:
    """Canon lives in the repo tree, not the live root. No drive literal."""
    root = Path(repo) if repo is not None else Path(__file__).resolve().parent.parent
    return root / "docs" / "COMPETENCY.toml"


def load(path: Path | str) -> dict:
    """Parse and validate. A missing or torn file is UNREADABLE, never {}."""
    p = Path(path)
    try:
        raw = p.read_bytes()
    except OSError as e:
        raise CompetencyError("UNREADABLE", f"{p}: {e}") from e
    try:
        data = tomllib.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as e:
        raise CompetencyError("UNREADABLE", f"{p}: does not parse ({e})") from e
    if not isinstance(data, dict):
        raise CompetencyError("BAD_SCHEMA", f"{p}: root is not a table")
    schema = data.get("schema")
    if schema != SCHEMA:
        raise CompetencyError("BAD_SCHEMA",
                              f"{p}: schema {schema!r} != {SCHEMA!r}")
    nodes = data.get("nodes")
    skills = data.get("skills")
    router = data.get("router")
    if not isinstance(nodes, dict) or not nodes:
        raise CompetencyError("BAD_SCHEMA", f"{p}: [nodes.*] missing")
    if not isinstance(skills, dict) or not skills:
        raise CompetencyError("BAD_SCHEMA", f"{p}: [skills.*] missing")
    if not isinstance(router, dict):
        raise CompetencyError("BAD_SCHEMA", f"{p}: [router] missing")
    task_types = router.get("task_types")
    nodes_order = router.get("nodes_order")
    if not isinstance(task_types, list) or not task_types:
        raise CompetencyError("BAD_SCHEMA", f"{p}: router.task_types missing")
    if not isinstance(nodes_order, list) or not nodes_order:
        raise CompetencyError("BAD_SCHEMA", f"{p}: router.nodes_order missing")
    return data


def pick(matrix: dict, task_type: str, available: Iterable[str]) -> str:
    """Highest possessed+available rating. Never invents a node."""
    skills = matrix.get("skills") or {}
    if task_type not in skills:
        raise CompetencyError("UNKNOWN_TASK", task_type)
    rows = skills[task_type]
    if not isinstance(rows, dict):
        raise CompetencyError("BAD_SCHEMA",
                              f"skills.{task_type} is not a table")
    avail = {str(x) for x in available}
    nodes = matrix.get("nodes") or {}
    order = list((matrix.get("router") or {}).get("nodes_order") or [])
    cands: list[tuple[str, int, bool]] = []
    for node_id, rec in rows.items():
        if node_id not in avail:
            continue
        if not isinstance(rec, dict):
            continue
        if rec.get("possessed") is not True:
            continue
        try:
            rating = int(rec["rating"])
        except (KeyError, TypeError, ValueError):
            continue
        if rating <= 0:
            continue
        family = str((nodes.get(node_id) or {}).get("family") or "")
        cands.append((node_id, rating, family == "dom"))
    if not cands:
        raise CompetencyError(
            "NO_CANDIDATE",
            f"{task_type}: no possessed+available node in {sorted(avail)}")
    best = max(c[1] for c in cands)
    top = [c for c in cands if c[1] == best]
    dom = [c for c in top if c[2]]
    pool = dom if dom else top
    if len(pool) == 1:
        return pool[0][0]
    rank = {n: i for i, n in enumerate(order)}
    pool.sort(key=lambda c: rank.get(c[0], 10 ** 9))
    return pool[0][0]


def classify_task_type(text: str) -> str:
    """Map a title/body onto router.task_types. Default is code-build."""
    folded = " ".join(str(text or "").lower().split())
    hits: list[str] = []
    for task, hints in _TASK_HINTS:
        if any(h in folded for h in hints):
            hits.append(task)
    if "code-build" in hits and "web-research" in hits:
        return "code-build"
    if hits:
        return hits[0]
    return "code-build"


def agent_kind(node_id: str) -> tuple[str, str]:
    """Map a COMPETENCY node id onto dispatch (agent, kind)."""
    rec = NODE_AGENT_KIND.get(node_id)
    if rec is None:
        raise CompetencyError("NO_DISPATCH",
                              f"{node_id!r} has no dispatch kind")
    return rec
