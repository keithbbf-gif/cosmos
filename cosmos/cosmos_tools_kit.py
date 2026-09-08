#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_tools_kit — GET catalog for the Tools extra pane.

1. COSMOS components (named Core modules)
2. Local callable tools (DOI, PDF-to-text, OCR, UPS-JUDGE, ROLD, scars)
3. Everything else we can name without inventing: makers seed, discover
   binaries, rails, tool contracts.

GET never mutates. Never mkdir. UPS-JUDGE is NAMED (Physics Profile later).

    py -3.14 cosmos\\\\cosmos_tools_kit.py --selftest
"""
from __future__ import annotations

import importlib.util
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_discover import PROBE_CMDS  # noqa: E402
from cosmos_surfaces_kit import _local_tools, _which  # noqa: E402

SCHEMA = "cosmos-tools-kit/1"
HERE = Path(__file__).resolve().parent
MAKERS_TOML = HERE / "makers.toml"

COMPONENTS = (
    ("kernel", "COSMOS Kernel", "cosmos_kernel"),
    ("ledger", "append-only ledger", "cosmos_ledger"),
    ("spend", "spend gate", "cosmos_spend"),
    ("registry", "rails registry", "cosmos_registry"),
    ("rails", "dispatcher / rails", "cosmos_rails"),
    ("surfaces", "storage surfaces", "cosmos_surfaces"),
    ("tools_contracts", "tool contracts", "cosmos_tools"),
    ("dispatch", "dispatch harness", "cosmos_dispatch"),
    ("studio", "MOTIF Studio pack", "cosmos_studio"),
    ("gitur", "GitHub + GitLab + Cursor", "cosmos_gitur"),
    ("mcp_server", "MCP server (COSMOS spoken as MCP)", "cosmos_mcp"),
    ("mcp_client", "MCP client", "cosmos_mcp_client"),
    ("work_order", "work orders", "cosmos_work_order"),
    ("validate", "DOI / quote / path gate", "cosmos_validate"),
    ("model_rater", "Model Rater", "cosmos_model_rater"),
    ("backup", "backup clock", "cosmos_backup"),
    ("session_kit", "session kit", "cosmos_session_kit"),
    ("review", "Review fold", "cosmos_review"),
    ("runs_ops", "Runs ops fold", "cosmos_runs_ops"),
    ("health", "health board", "cosmos_health"),
    ("cvm", "voice CVM", "cosmos_cvm_clock"),
    ("discover", "mesh discovery / hands", "cosmos_discover"),
    ("makers", "maker map", "cosmos_makers"),
    ("watchdog2", "Activity Clock", "cosmos_watchdog2"),
    ("crucible", "Crucible", "cosmos_crucible"),
    ("dom", "DOM worker", "cosmos_dom"),
    ("browser", "browser / dump-dom", "cosmos_browser"),
)


def _mod_ok(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _components() -> list[dict]:
    rows = []
    for cid, label, mod in COMPONENTS:
        rows.append({
            "id": cid,
            "label": label,
            "module": mod,
            "kind": "OK" if _mod_ok(mod) else "NO_SOURCE",
            "lane": "cosmos",
        })
    return rows


def _makers() -> dict:
    if not MAKERS_TOML.is_file():
        return {"kind": "NO_SOURCE", "rows": []}
    try:
        import tomllib
        rec = tomllib.loads(MAKERS_TOML.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return {"kind": "BROKE", "detail": f"{type(e).__name__}: {e}"[:160], "rows": []}
    rows = []
    for m in rec.get("makers") or []:
        if not isinstance(m, dict):
            continue
        rows.append({
            "id": m.get("id"),
            "label": m.get("id"),
            "kind": "SEED",
            "maker_kind": m.get("kind"),
            "location": m.get("location"),
            "function": m.get("function"),
            "lane": "custom",
            "note": "makers.toml seed — a place, not a live capability.",
        })
    return {"kind": "OK", "rows": rows}


def _hands() -> list[dict]:
    rows = []
    for name, lane in PROBE_CMDS:
        rec = _which(name)
        rec["id"] = name
        rec["label"] = name
        rec["lane"] = "other"
        rec["channel"] = lane
        rec["note"] = "PATH binary. Absence is not a fault."
        rows.append(rec)
    return rows


def _contracts(kernel) -> dict:
    bound = getattr(kernel, "tools", None)
    if bound is None or not hasattr(bound, "report"):
        return {"kind": "NO_SOURCE", "rows": []}
    try:
        rows = bound.report() or []
        return {"kind": "OK", "rows": rows if isinstance(rows, list) else []}
    except Exception as e:  # noqa: BLE001
        return {"kind": "BROKE", "detail": f"{type(e).__name__}: {e}"[:160], "rows": []}


def _rails(kernel) -> list[dict]:
    reg = getattr(kernel, "registry", None)
    if reg is None or not hasattr(reg, "matrix"):
        return []
    try:
        matrix = list(reg.matrix() or [])
    except Exception:  # noqa: BLE001
        return []
    out = []
    for row in matrix:
        if not isinstance(row, dict):
            continue
        out.append({
            "id": row.get("link_id"),
            "label": row.get("link_id"),
            "lane": "other",
            "channel": row.get("rail_type"),
            "route": row.get("route"),
            "verified": row.get("verified"),
            "kind": ("OK" if row.get("verified") is True
                     else ("FAIL" if row.get("verified") is False else "UNKNOWN")),
        })
    return out[:80]


def snapshot(kernel) -> dict:
    local = _local_tools()
    for row in local:
        if row.get("id") == "ups_judge":
            row["note"] = (
                "UPS-JUDGE — GEM Vertex full-context judge. Lives here until "
                "the Physics Profile has a home. Needs Keith's July pack. "
                "NAMED, not callable, not invented."
            )
        if row.get("id") == "pdf":
            row["label"] = "PDF to text"
    return {
        "schema": SCHEMA,
        "measured_at": time.time(),
        "tree_id": kernel.paths.sentinel.tree_id,
        "cosmos": _components(),
        "custom": _makers(),
        "local": local,
        "other": {
            "hands": _hands(),
            "rails": _rails(kernel),
            "contracts": _contracts(kernel),
        },
        "note": (
            "Tools catalog: COSMOS components, makers seed, local callables "
            "(DOI / PDF-to-text / OCR / UPS-JUDGE / ROLD / scars), PATH hands, "
            "rails, contracts. GET never mutates. Does not poll vendors. "
            "UPS-JUDGE stays NAMED until Physics Profile."
        ),
    }


def _selftest() -> int:
    import tempfile
    from types import SimpleNamespace

    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    td = Path(tempfile.mkdtemp(prefix="cosmos_toolskit_"))
    root = install(td / "live", tree_id="spike-toolskit")
    kernel = SimpleNamespace(paths=CosmosPaths(root), tools=None, registry=None)
    rec = snapshot(kernel)
    cids = {r["id"] for r in rec["cosmos"]}
    lids = {r["id"] for r in rec["local"]}
    check("GET fold names cosmos custom local other without mkdir",
          lambda: rec.get("schema") == SCHEMA
          and "cosmos" in rec and "custom" in rec
          and "local" in rec and "other" in rec)
    check("COSMOS components include kernel ledger mcp validate",
          lambda: {"kernel", "ledger", "mcp_server", "validate"} <= cids)
    check("local catalog still names DOI PDF OCR UPS-JUDGE",
          lambda: lids >= {"doi", "pdf", "ocr", "ups_judge"})
    check("UPS-JUDGE stays NAMED until Physics Profile",
          lambda: any(r["id"] == "ups_judge" and r["kind"] == "NAMED"
                      for r in rec["local"])
          and "Physics Profile" in rec["note"])
    check("does not poll vendors",
          lambda: "Does not poll vendors" in rec["note"])

    failed = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (Tools kit)"
          % ("PASS" if not failed else "FAIL", len(results)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(_selftest())
