#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_makers - the MAKER MAP (where agents/tools/connectors/skills can be made).

A maker is a PLACE, not a capability claim: Cursor Cloud Agent, Claude Agent tool,
GrokBot team, mcp-registry, save_skill, scheduled task. Registration answers WHERE
something can be made and HOW to invoke that place. It does not claim the place is
reachable today - that is a probe, and this module does not pretend to be one.

The same authority pattern as cosmos_tools: every add() is a ledger event (MAKER_ADDED);
current state is a projection. makers.toml is the known starting catalog and is loaded
by writing those entries through add() so the ledger is the sole authority. A second
declaration of the same id is a drift, not an update. There is no delete.

Kinds are a closed set: AGENT | TOOL | CONNECTOR | SKILL. An unknown kind REFUSES.
"""
from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Iterable, Optional

from cosmos_ledger import Ledger

MAKER_KINDS = ("AGENT", "TOOL", "CONNECTOR", "SKILL")
REQUIRED_FIELDS = ("id", "kind", "location", "function", "access",
                   "potential_sources", "tags")
DEFAULT_TOML = Path(__file__).resolve().with_name("makers.toml")


class MakerError(RuntimeError):
    """kind in {UNKNOWN_KIND, BAD_ENTRY, DUPLICATE, UNREADABLE}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _as_str_list(value, field: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(x, str) for x in value):
        raise MakerError("BAD_ENTRY",
                         f"{field} must be a list of strings, got {type(value).__name__}")
    return [x for x in value]


def _validate(entry: dict) -> dict:
    """Normalize one maker entry or REFUSE. Unknown kind is UNKNOWN_KIND; anything
    else structurally wrong is BAD_ENTRY. The catalog is a contract, not a suggestion."""
    if not isinstance(entry, dict):
        raise MakerError("BAD_ENTRY", f"entry is not a table, got {type(entry).__name__}")
    missing = [f for f in REQUIRED_FIELDS if f not in entry]
    if missing:
        raise MakerError("BAD_ENTRY", f"missing field(s): {', '.join(missing)}")
    out = {}
    for field in ("id", "kind", "location", "function", "access"):
        val = entry[field]
        if not isinstance(val, str) or not val.strip():
            raise MakerError("BAD_ENTRY",
                             f"{field} must be a non-empty string, got {val!r}")
        out[field] = val.strip()
    if out["kind"] not in MAKER_KINDS:
        raise MakerError("UNKNOWN_KIND",
                         f"{out['kind']!r} not in {list(MAKER_KINDS)}")
    out["potential_sources"] = _as_str_list(entry["potential_sources"], "potential_sources")
    out["tags"] = _as_str_list(entry["tags"], "tags")
    return out


def _read_toml(path: Path) -> list[dict]:
    try:
        raw = path.read_bytes()
    except OSError as e:
        raise MakerError("UNREADABLE", f"{path}: {e}") from e
    try:
        data = tomllib.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as e:
        raise MakerError("UNREADABLE", f"{path}: does not parse ({e})") from e
    rows = data.get("makers")
    if rows is None:
        raise MakerError("BAD_ENTRY", f"{path}: no [[makers]] array")
    if not isinstance(rows, list):
        raise MakerError("BAD_ENTRY", f"{path}: makers is not an array")
    return [_validate(r) for r in rows]


class MakerMap:
    """Backed by the SAME authority pattern as ToolContracts: every add is a ledger
    event; current state is a projection. The TOML catalog is seeded through add()
    so a reload reconstructs the map from the ledger alone."""

    def __init__(self, ledger: Ledger, toml_path: Optional[str | Path] = DEFAULT_TOML,
                 clock=None, seed: bool = True):
        self.ledger = ledger
        self._clock = clock
        self.toml_path = Path(toml_path) if toml_path is not None else None
        if seed:
            if self.toml_path is None:
                raise MakerError("UNREADABLE",
                                 "seed=True requires a toml_path - an empty catalog "
                                 "must be asked for (seed=False), never implied")
            self.load(self.toml_path)

    # ---------------- mutations ----------------
    def add(self, entry: dict) -> dict:
        """Record one maker. Unknown kind REFUSES. A second add of the same id is a
        drift (DUPLICATE), not an update - there is no delete and no silent replace."""
        rec = _validate(entry)
        if rec["id"] in self.state():
            raise MakerError("DUPLICATE",
                             f"{rec['id']!r} already declared - a second add is a "
                             f"drift, not an update")
        self.ledger.append("MAKER_ADDED", rec)
        return dict(rec)

    def load(self, path: str | Path) -> dict:
        """Read a makers.toml. Every entry is validated first (a half-applied catalog
        is a lie); ids already in the projection are skipped so a restart does not
        re-declare. Returns {loaded, added, already}."""
        rows = _read_toml(Path(path))
        existing = self.state()
        added = []
        for rec in rows:
            if rec["id"] in existing:
                continue
            added.append(self.add(rec))
        return {"loaded": len(rows), "added": len(added),
                "already": len(rows) - len(added)}

    # ---------------- projection ----------------
    def state(self) -> dict:
        def fold(s, rec):
            if rec["event"] == "MAKER_ADDED":
                p = rec["payload"]
                mid = p.get("id")
                if mid:
                    s[mid] = {"id": mid,
                              "kind": p.get("kind"),
                              "location": p.get("location"),
                              "function": p.get("function"),
                              "access": p.get("access"),
                              "potential_sources": list(p.get("potential_sources") or []),
                              "tags": list(p.get("tags") or []),
                              "t": rec["t"]}
            return s
        return self.ledger.project(fold, {})

    def list(self, kind: Optional[str] = None) -> list[dict]:
        """All makers, optionally filtered by kind. An unknown kind REFUSES rather
        than returning empty - empty would hide a typo as 'none of those exist'."""
        if kind is not None and kind not in MAKER_KINDS:
            raise MakerError("UNKNOWN_KIND", f"{kind!r} not in {list(MAKER_KINDS)}")
        rows = [dict(v) for _, v in sorted(self.state().items())]
        if kind is None:
            return rows
        return [r for r in rows if r["kind"] == kind]

    def find(self, tag: Optional[str] = None, kind: Optional[str] = None,
             text: Optional[str] = None) -> list[dict]:
        """AND of optional filters. kind is the closed set (unknown REFUSES). tag is
        an exact tag match. text is a case-insensitive substring over id/location/
        function/access/sources/tags. No criteria returns the full list."""
        rows = self.list(kind=kind)
        if tag is not None:
            rows = [r for r in rows if tag in r["tags"]]
        if text:
            needle = text.lower()
            keep = []
            for r in rows:
                hay: Iterable[str] = (
                    [r["id"], r["kind"], r["location"], r["function"], r["access"]]
                    + list(r["potential_sources"]) + list(r["tags"])
                )
                if any(needle in (s or "").lower() for s in hay):
                    keep.append(r)
            rows = keep
        return rows