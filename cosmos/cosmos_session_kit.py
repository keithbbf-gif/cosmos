#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_session_kit — COS panes + autosave + auto-resession config.

GET never mutates and never mkdir. POST writes state/session_kit/pack.json.
Does not fire TidyUP, BU, or a resession. Autosave minutes in {5,10,20,30}.

    py -3.14 cosmos\\\\cosmos_session_kit.py --selftest
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "cosmos-session-kit/1"
PACK_NAME = "pack.json"
AUTOSAVE_MIN = (5, 10, 20, 30)
COS_PANES = (
    ("rold", "ROLD — Rule of Law Desk"),
    ("tidyup", "TidyUP"),
    ("tu2", "TU2"),
    ("bu", "BU — BootUP pointer"),
)
COS_IDS = frozenset(c[0] for c in COS_PANES)


class SessionKitError(RuntimeError):
    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _iso_now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def pack_path(paths) -> Path:
    return paths.state("session_kit", PACK_NAME)


def default_kit() -> dict:
    return {
        "schema": SCHEMA,
        "cos": {cid: True for cid, _lab in COS_PANES},
        "autosave_min": 10,
        "resession": {
            "time_s": 0,
            "context_tokens": 0,
            "on_compaction": True,
            "on_token_count": True,
        },
        "updated_at": None,
        "available": False,
        "kind": "NO_SOURCE",
        "cos_catalog": [{"id": i, "label": lab} for i, lab in COS_PANES],
        "autosave_catalog": list(AUTOSAVE_MIN),
    }


def _clamp_int(raw, lo: int, hi: int, default: int) -> int:
    try:
        n = int(raw)
    except (TypeError, ValueError):
        return default
    return max(lo, min(hi, n))


def _public(rec: dict) -> dict:
    base = default_kit()
    cos = dict(base["cos"])
    incoming = rec.get("cos") if isinstance(rec.get("cos"), dict) else {}
    for cid in COS_IDS:
        if cid in incoming:
            cos[cid] = bool(incoming[cid])
    mins = rec.get("autosave_min", base["autosave_min"])
    try:
        mins = int(mins)
    except (TypeError, ValueError):
        mins = 10
    if mins not in AUTOSAVE_MIN:
        raise SessionKitError("BAD_INPUT", f"autosave_min must be one of {AUTOSAVE_MIN}")
    rs = rec.get("resession") if isinstance(rec.get("resession"), dict) else {}
    resession = {
        "time_s": _clamp_int(rs.get("time_s"), 0, 86400, 0),
        "context_tokens": _clamp_int(rs.get("context_tokens"), 0, 2_000_000, 0),
        "on_compaction": bool(rs["on_compaction"]) if "on_compaction" in rs else True,
        "on_token_count": bool(rs["on_token_count"]) if "on_token_count" in rs else True,
    }
    return {
        "schema": SCHEMA,
        "cos": cos,
        "autosave_min": mins,
        "resession": resession,
        "updated_at": rec.get("updated_at"),
        "available": rec.get("available", False),
        "kind": rec.get("kind") or "OK",
        "cos_catalog": [{"id": i, "label": lab} for i, lab in COS_PANES],
        "autosave_catalog": list(AUTOSAVE_MIN),
    }


def load_kit(paths) -> dict:
    p = pack_path(paths)
    base = default_kit()
    if not p.is_file():
        return base
    try:
        rec = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        base["kind"] = "BROKE"
        return base
    if not isinstance(rec, dict):
        base["kind"] = "BROKE"
        return base
    try:
        out = _public(rec)
    except SessionKitError:
        base["kind"] = "BROKE"
        return base
    out["available"] = True
    out["kind"] = "OK"
    return out


def save_kit(paths, body: dict) -> dict:
    if not isinstance(body, dict):
        raise SessionKitError("BAD_INPUT", "body must be an object")
    cur = load_kit(paths)
    merged = {
        "cos": dict(cur["cos"]),
        "autosave_min": cur["autosave_min"],
        "resession": dict(cur["resession"]),
        "updated_at": _iso_now(),
        "available": True,
        "kind": "OK",
    }
    if "cos" in body:
        if not isinstance(body["cos"], dict):
            raise SessionKitError("BAD_INPUT", "cos must be an object")
        for cid, val in body["cos"].items():
            if cid not in COS_IDS:
                raise SessionKitError("BAD_INPUT", f"unknown COS pane {cid!r}")
            merged["cos"][cid] = bool(val)
    if "autosave_min" in body:
        merged["autosave_min"] = body["autosave_min"]
    if "resession" in body:
        if not isinstance(body["resession"], dict):
            raise SessionKitError("BAD_INPUT", "resession must be an object")
        merged["resession"].update(body["resession"])
    out = _public(merged)
    out["updated_at"] = merged["updated_at"]
    out["available"] = True
    out["kind"] = "OK"
    p = pack_path(paths)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(json.dumps({
        "schema": SCHEMA,
        "cos": out["cos"],
        "autosave_min": out["autosave_min"],
        "resession": out["resession"],
        "updated_at": out["updated_at"],
        "available": True,
        "kind": "OK",
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(p)
    got = load_kit(paths)
    got["measured_at"] = time.time()
    got["note"] = (
        "COS panes are ROLD / TidyUP / TU2 / BU. Autosave is 5/10/20/30 min. "
        "Auto-resession triggers are config. This POST does not fire a resession."
    )
    return got


def snapshot(paths) -> dict:
    rec = load_kit(paths)
    rec["measured_at"] = time.time()
    rec["note"] = (
        "COS panes are ROLD / TidyUP / TU2 / BU. Autosave is 5/10/20/30 min. "
        "This GET does not fire a resession. Resume is grok -c / -r <id>."
    )
    return rec


def _selftest() -> int:
    import tempfile
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    td = Path(tempfile.mkdtemp(prefix="cosmos_skit_"))
    root = install(td / "live", tree_id="spike-skit")
    paths = CosmosPaths(root)
    empty = load_kit(paths)
    check("GET missing kit is NO_SOURCE and does not mkdir",
          lambda: empty.get("kind") == "NO_SOURCE"
          and not pack_path(paths).exists())
    saved = save_kit(paths, {
        "autosave_min": 20,
        "cos": {"tu2": False},
        "resession": {"time_s": 900, "context_tokens": 100000},
    })
    check("POST autosave 20 min + resession triggers",
          lambda: saved["autosave_min"] == 20
          and saved["cos"]["tu2"] is False
          and saved["cos"]["rold"] is True
          and saved["resession"]["time_s"] == 900
          and saved["resession"]["context_tokens"] == 100000)
    bad = False
    try:
        save_kit(paths, {"autosave_min": 7})
    except SessionKitError as e:
        bad = e.kind == "BAD_INPUT"
    check("autosave 7 min is BAD_INPUT", lambda: bad)

    failed = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (session kit)"
          % ("PASS" if not failed else "FAIL", len(results)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(_selftest())
