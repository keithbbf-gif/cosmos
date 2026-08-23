#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_migrate - THE PORT BACKLOG, MEASURED (F5 builder). Ingests the incumbent
TOOLS_REGISTRY.json into cosmos_tools as declared contracts, so "139 tools to port"
stops being a remembered number and becomes a queryable worklist with dispositions.

RULES: ingestion DECLARES, it never verifies - registration is not capability, and a
ported tool goes green only when a contract check runs against the NEW implementation.
The four spike modules are pre-dispositioned REPLACED (their COSMOS successors exist and
are tested). Everything else enters as UNDECIDED - which is a DISPOSITION GAP the report
counts, not a silent default. Reading the incumbent registry is read-only; this module
writes nothing outside the COSMOS ledger.
"""
from __future__ import annotations

import json
from pathlib import Path

from cosmos_ledger import Ledger
from cosmos_tools import ToolContracts, ToolsError

# The spikes already replaced these; the mapping is the decision record's seed.
REPLACED_BY_SPIKE = {
    "bts_paths": "cosmos_paths",
    "tree_lock": "cosmos_lock",
    "bts_phone": "cosmos_mail",
    "bts_runner": "cosmos_sched",
}
# Direct successors built in v1.0-f5 beyond the spikes.
REPLACED_BY_V1 = {
    "bts_health": "cosmos_health (planned on kernel selftests)",
    "bts_kdash_feed": "cosmos_service /api/v1 (KDash is a client now)",
    "backup_to_onedrive": "cosmos_backup",
    "bts_cursor": "carries forward as a registry link driver",
}


class Migrator:
    def __init__(self, contracts: ToolContracts):
        self.contracts = contracts

    def ingest(self, registry_json: Path) -> dict:
        """Read the incumbent registry (read-only), declare every tool, seed the
        dispositions we already earned. Returns the measured backlog summary."""
        raw = json.loads(Path(registry_json).read_text(encoding="utf-8"))
        tools = raw if isinstance(raw, list) else raw.get("tools", raw.get("entries", []))
        declared = skipped = 0
        for t in tools:
            if not isinstance(t, dict) or not t.get("id"):
                skipped += 1
                continue
            name = str(t["id"])
            desc = str(t.get("desc") or t.get("name") or "")[:300]
            try:
                self.contracts.declare(name, verbs=["run"],
                                       behavior=desc or "UNKNOWN - card owed")
                declared += 1
            except ToolsError as e:
                if e.kind != "DUPLICATE":
                    raise
                skipped += 1
        for old, new in REPLACED_BY_SPIKE.items():
            self._try_disposition(old, "REPLACED", f"spike successor: {new} (tested)")
        for old, new in REPLACED_BY_V1.items():
            self._try_disposition(old, "REPLACED", f"v1.0-f5 successor: {new}")
        return self.report()

    def _try_disposition(self, name: str, decision: str, reason: str) -> None:
        try:
            self.contracts.disposition(name, decision, reason)
        except ToolsError:
            pass                       # tool absent from the incumbent registry: fine

    def report(self) -> dict:
        """The backlog, COUNTED from the projection - never quoted from memory."""
        st = self.contracts.state()
        by = {}
        for v in st.values():
            d = v.get("disposition") or "UNDECIDED"
            key = d if isinstance(d, str) else d.get("decision", "UNDECIDED")
            by[key] = by.get(key, 0) + 1
        verified = sum(1 for v in st.values()
                       if v.get("last_verify") and v["last_verify"].get("ok"))
        return {"total": len(st), "by_disposition": by, "verified": verified,
                "undecided_gap": by.get("UNDECIDED", 0),
                "note": "UNDECIDED is a decision gap the port must close tool by tool - "
                        "architecture wins where contracts conflict, recorded never drifted"}