#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Refresh FEATURE_PROBE.json ui_files from shipped builds/cdeck/ui/.

Full Chromium measurement against live Core is optional; ui/ fingerprint is
always re-emitted so static gates stay bound to the bytes on disk.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
UI = HERE / "ui"
OUT = HERE / "FEATURE_PROBE.json"
SCHEMA = "cosmos-cdeck-feature-probe/1"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fingerprint_ui(ui_dir: Path) -> dict[str, dict]:
    if not ui_dir.is_dir():
        raise FileNotFoundError(f"ui dir missing: {ui_dir}")
    out: dict[str, dict] = {}
    for path in sorted(ui_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ui_dir).as_posix()
        data = path.read_bytes()
        out[rel] = {
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
    return out


def refresh_ui_files(*, ui_dir: Path | None = None, out: Path | None = None) -> dict:
    ui_dir = UI if ui_dir is None else Path(ui_dir)
    out = OUT if out is None else Path(out)
    rec: dict = {}
    if out.is_file():
        rec = json.loads(out.read_text(encoding="utf-8"))
    rec["schema"] = rec.get("schema") or SCHEMA
    rec["label"] = rec.get("label") or f"FEATURE_PROBE-ui-refresh-{_now()}"
    rec["ui_files"] = fingerprint_ui(ui_dir)
    rec["ui_fingerprint_at"] = _now()
    out.write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n",
                   encoding="utf-8", newline="\n")
    return rec


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Emit / refresh FEATURE_PROBE.json")
    ap.add_argument("--ui-dir", default=str(UI), help="Shipped ui/ root")
    ap.add_argument("--out", default=str(OUT), help="Artifact path")
    ap.add_argument("--upstream", default="http://127.0.0.1:8770",
                    help="Live Core (runtime half; ui refresh always runs)")
    ns = ap.parse_args(argv)
    _ = ns.upstream  # reserved for full probe; ui gate must not depend on Core up
    refresh_ui_files(ui_dir=Path(ns.ui_dir), out=Path(ns.out))
    print(json.dumps({"ok": True, "out": ns.out, "ui_files": len(json.loads(
        Path(ns.out).read_text(encoding="utf-8"))["ui_files"])}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
