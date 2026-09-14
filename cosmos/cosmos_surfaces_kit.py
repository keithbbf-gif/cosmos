#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_surfaces_kit — GET fold: storage + channels + callable tools.

Storage is still GET /surfaces (five canon names). This fold adds:
  * channels — rails grouped by API / CLI / DOM / MCP / CHAT
  * local tools — DOI, PDF, OCR, UPS-JUDGE, ROLD, scar list
  * online tools — API/DOM rails that already exist (no vendor poll)

GET never mutates. Never mkdir. UPS-JUDGE is NAMED (needs Keith's July pack).

    py -3.14 cosmos\\\\cosmos_surfaces_kit.py --selftest
"""
from __future__ import annotations

import importlib.util
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

SCHEMA = "cosmos-surfaces-kit/1"
CHANNEL_TYPES = ("API", "CLI", "DOM", "MCP", "CHAT")


class SurfacesKitError(RuntimeError):
    """kind in {BAD_REQUEST, SURFACES_NOT_COMPOSED, UNKNOWN_SURFACE, UNQUALIFIED}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")
ROLD_ROOT = Path(r"V:\Ai\ROLD")
ROLD_FILES = ("GLOSSARY.md", "RULES.md", "SCARS.md")
SCARS_FILE = ROLD_ROOT / "SCARS.md"


def _which(name: str) -> dict:
    p = shutil.which(name)
    return {"bin": name, "path": p, "kind": "OK" if p else "NO_SOURCE"}


def _py_mod(name: str) -> dict:
    spec = importlib.util.find_spec(name)
    return {"module": name, "kind": "OK" if spec is not None else "NO_SOURCE"}


def _storage(kernel) -> dict:
    sf = getattr(kernel, "surfaces", None)
    if sf is None or not hasattr(sf, "report"):
        return {"kind": "NO_SOURCE", "rows": [],
                "note": "kernel.surfaces not composed"}
    try:
        rows = sf.report() or []
        return {"kind": "OK", "rows": rows if isinstance(rows, list) else []}
    except Exception as e:  # noqa: BLE001
        return {"kind": "BROKE", "detail": f"{type(e).__name__}: {e}"[:200], "rows": []}


def _channels(kernel) -> dict:
    reg = getattr(kernel, "registry", None)
    matrix = []
    kind = "NO_SOURCE"
    if reg is not None and hasattr(reg, "matrix"):
        try:
            matrix = list(reg.matrix() or [])
            kind = "OK"
        except Exception as e:  # noqa: BLE001
            return {"kind": "BROKE", "detail": f"{type(e).__name__}: {e}"[:200],
                    "types": [], "n": 0}
    by = {t: [] for t in CHANNEL_TYPES}
    other = []
    for row in matrix:
        if not isinstance(row, dict):
            continue
        rt = str(row.get("rail_type") or "OTHER").upper()
        rec = {
            "id": row.get("link_id"),
            "rail_type": rt,
            "route": row.get("route"),
            "verified": row.get("verified"),
            "age_s": row.get("age_s"),
        }
        if rt in by:
            by[rt].append(rec)
        else:
            other.append(rec)
    types = []
    for t in CHANNEL_TYPES:
        types.append({
            "type": t,
            "n": len(by[t]),
            "rows": by[t][:24],
        })
    if other:
        types.append({"type": "OTHER", "n": len(other), "rows": other[:24]})
    mcp_mod = Path(__file__).resolve().parent / "cosmos_mcp.py"
    mcp_client = Path(__file__).resolve().parent / "cosmos_mcp_client.py"
    return {
        "kind": kind,
        "n": len(matrix),
        "types": types,
        "mcp": {
            "server_module": mcp_mod.is_file(),
            "client_module": mcp_client.is_file(),
            "note": "MCP is a channel COSMOS speaks (server) and can call (client). "
                    "Registration is not a live MCP session.",
        },
        "note": "Channels are GET /rails grouped by rail_type. MCP is named even when n=0.",
    }


def _local_tools() -> list[dict]:
    doi = {
        "id": "doi",
        "label": "DOI",
        "lane": "local",
        "kind": "OK",
        "module": "cosmos_validate.v_doi_shape",
        "note": "Offline shape gate. Existence is UNMEASURED until Crossref runs.",
    }
    pdf_py = _py_mod("pypdf")
    if pdf_py["kind"] != "OK":
        pdf_py = _py_mod("PyPDF2")
    pdf_bins = [_which("pdftotext"), _which("pandoc"), _which("markitdown")]
    pdf_ok = pdf_py["kind"] == "OK" or any(b["kind"] == "OK" for b in pdf_bins)
    pdf = {
        "id": "pdf",
        "label": "PDF",
        "lane": "local",
        "kind": "OK" if pdf_ok else "NO_SOURCE",
        "python": pdf_py,
        "bins": pdf_bins,
        "note": "Local PDF read. Not a publisher.",
    }
    ocr_bins = [_which("tesseract"), _which("ocrmypdf")]
    ocr = {
        "id": "ocr",
        "label": "OCR",
        "lane": "local",
        "kind": "OK" if any(b["kind"] == "OK" for b in ocr_bins) else "NO_SOURCE",
        "bins": ocr_bins,
        "note": "tesseract / ocrmypdf on PATH. Presence is not a live OCR job.",
    }
    ups = {
        "id": "ups_judge",
        "label": "UPS-JUDGE",
        "lane": "local",
        "kind": "NAMED",
        "note": "GEM Vertex full-context judge. Needs Keith's July pack. "
                "Not invented. Not a callable until that rebuild.",
    }
    if ROLD_ROOT.is_dir():
        files = {n: (ROLD_ROOT / n).is_file() for n in ROLD_FILES}
        rold = {
            "id": "rold",
            "label": "ROLD",
            "lane": "local",
            "kind": "OK",
            "path": str(ROLD_ROOT),
            "files": files,
            "note": "Rule of Law Desk. Also a storage surface.",
        }
    else:
        rold = {
            "id": "rold",
            "label": "ROLD",
            "lane": "local",
            "kind": "NO_SOURCE",
            "path": str(ROLD_ROOT),
            "note": "V:\\Ai\\ROLD is not a directory on this host.",
        }
    if SCARS_FILE.is_file():
        try:
            n_lines = len(SCARS_FILE.read_text(encoding="utf-8", errors="replace").splitlines())
        except OSError:
            n_lines = None
        scars = {
            "id": "scars",
            "label": "scar list",
            "lane": "local",
            "kind": "OK",
            "path": str(SCARS_FILE),
            "lines": n_lines,
            "note": "SCARS.md on ROLD. Count is lines, not a classified index.",
        }
    else:
        scars = {
            "id": "scars",
            "label": "scar list",
            "lane": "local",
            "kind": "NO_SOURCE",
            "path": str(SCARS_FILE),
            "note": "SCARS.md unread.",
        }
    hermes_bin = _which("hermes")
    if hermes_bin["kind"] != "OK":
        hermes_bin = _which("hermes.exe")
    hermes = {
        "id": "hermes",
        "label": "Hermes Agent CLI",
        "lane": "local",
        "kind": hermes_bin["kind"],
        "bins": [hermes_bin],
        "note": "OpenRouter cookbook via. Keith sets OPENROUTER_API_KEY in "
                "~/.hermes/.env. COSMOS does not paste it. Presence is not a session.",
    }
    return [doi, pdf, ocr, ups, rold, scars, hermes]


def _online_tools(channels: dict) -> list[dict]:
    rows = []
    for t in channels.get("types") or []:
        if t.get("type") not in ("API", "DOM"):
            continue
        for r in t.get("rows") or []:
            rows.append({
                "id": r.get("id"),
                "label": r.get("id") or t.get("type"),
                "lane": "online",
                "channel": t.get("type"),
                "route": r.get("route"),
                "verified": r.get("verified"),
                "age_s": r.get("age_s"),
                "kind": ("OK" if r.get("verified") is True
                         else ("FAIL" if r.get("verified") is False else "UNKNOWN")),
            })
    return rows[:40]


def _contracts(kernel) -> dict:
    bound = getattr(kernel, "tools", None)
    if bound is None or not hasattr(bound, "report"):
        return {"kind": "NO_SOURCE", "rows": []}
    try:
        rows = bound.report() or []
        return {"kind": "OK", "rows": rows if isinstance(rows, list) else []}
    except Exception as e:  # noqa: BLE001
        return {"kind": "BROKE", "detail": f"{type(e).__name__}: {e}"[:200], "rows": []}


def save_surface(paths, body: dict, kernel=None) -> dict:
    """POST /api/v1/surfaces — measure surfaces; never mkdir; never invent reachability."""
    if not isinstance(body, dict):
        raise SurfacesKitError("BAD_REQUEST", "body must be a JSON object")
    sf = getattr(kernel, "surfaces", None) if kernel is not None else None
    if sf is None or not hasattr(sf, "measure"):
        raise SurfacesKitError(
            "SURFACES_NOT_COMPOSED",
            "kernel has no surfaces map — composition fault, not an empty catalog",
        )
    action = str(body.get("action") or "measure_canon").strip().lower()
    from cosmos_surfaces import CANON_SURFACE_IDS, measure_canon_surfaces

    if action in ("measure_canon", "check"):
        measured = measure_canon_surfaces(sf, paths)
        return {"action": action, "measured": measured, "surfaces": sf.report()}
    if action == "measure":
        sid = str(body.get("id") or "").strip()
        if not sid:
            raise SurfacesKitError("BAD_REQUEST", "measure requires id")
        try:
            rec = sf.measure(sid)
        except Exception as e:  # noqa: BLE001
            from cosmos_surfaces import SurfaceError

            if isinstance(e, SurfaceError):
                raise SurfacesKitError(e.kind, str(e)) from e
            raise
        return {"action": action, "measurement": rec, "surfaces": sf.report()}
    raise SurfacesKitError("BAD_REQUEST", f"unknown action {action!r}")


def snapshot(kernel) -> dict:
    channels = _channels(kernel)
    local = _local_tools()
    online = _online_tools(channels)
    return {
        "schema": SCHEMA,
        "measured_at": time.time(),
        "tree_id": kernel.paths.sentinel.tree_id,
        "storage": _storage(kernel),
        "channels": channels,
        "tools": {
            "local": local,
            "online": online,
            "contracts": _contracts(kernel),
            "note": (
                "Local catalog is named tools (DOI/PDF/OCR/UPS-JUDGE/ROLD/scars). "
                "Online is API/DOM rails already on GET /rails — does not poll vendors. "
                "UPS-JUDGE stays NAMED until Keith's July pack."
            ),
        },
        "note": (
            "Surfaces kit: storage + channels + callable tools. GET never mutates. "
            "Five canon storage names stay on GET /surfaces. MCP is a channel."
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

    td = Path(tempfile.mkdtemp(prefix="cosmos_surfkit_"))
    root = install(td / "live", tree_id="spike-surfkit")
    paths = CosmosPaths(root)
    kernel = SimpleNamespace(paths=paths, surfaces=None, registry=None, tools=None)
    rec = snapshot(kernel)
    ids = {t["id"] for t in rec["tools"]["local"]}
    types = {t["type"] for t in rec["channels"]["types"]}
    check("GET fold names storage channels tools without mkdir",
          lambda: rec.get("schema") == SCHEMA
          and "storage" in rec and "channels" in rec and "tools" in rec)
    check("channels always name API CLI DOM MCP",
          lambda: {"API", "CLI", "DOM", "MCP"} <= types)
    check("local catalog names DOI PDF OCR UPS-JUDGE ROLD scars Hermes",
          lambda: ids >= {"doi", "pdf", "ocr", "ups_judge", "rold", "scars", "hermes"})
    check("UPS-JUDGE stays NAMED, not a fake callable",
          lambda: any(t["id"] == "ups_judge" and t["kind"] == "NAMED"
                      for t in rec["tools"]["local"]))
    check("does not poll vendors",
          lambda: "does not poll vendors" in rec["tools"]["note"])

    failed = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (Surfaces kit)"
          % ("PASS" if not failed else "FAIL", len(results)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(_selftest())
