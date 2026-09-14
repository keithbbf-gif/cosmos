#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static pins for FEATURE_PROBE ui/ binding (subset gate when ui/ is vendored)."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
UI = HERE / "ui"
PROBE = HERE / "FEATURE_PROBE.json"

RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, fn) -> None:
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _probe_ui_files() -> dict:
    if not PROBE.is_file():
        raise FileNotFoundError(str(PROBE))
    rec = json.loads(PROBE.read_text(encoding="utf-8"))
    ui_files = rec.get("ui_files")
    if not isinstance(ui_files, dict) or not ui_files:
        raise ValueError("FEATURE_PROBE.json missing ui_files map")
    return ui_files


def main() -> int:
    check(
        "FEATURE_PROBE.json is present and matches the shipped ui/ byte for byte",
        lambda: _ui_matches_probe(),
    )
    bad = [r for r in RESULTS if not r[1]]
    for label, ok, err in RESULTS:
        print(f"  {'OK  ' if ok else 'FAIL'}  {label}{('  ' + err) if err else ''}")
    print(f"result: {'ok' if not bad else 'FAIL'}  "
          f"{len(RESULTS) - len(bad)}/{len(RESULTS)}")
    return 1 if bad else 0


def _ui_matches_probe() -> bool:
    ui_files = _probe_ui_files()
    if not UI.is_dir():
        raise FileNotFoundError(str(UI))
    live: dict[str, dict] = {}
    for path in sorted(UI.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(UI).as_posix()
        data = path.read_bytes()
        live[rel] = {
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
    if set(ui_files) != set(live):
        missing = sorted(set(ui_files) - set(live))
        extra = sorted(set(live) - set(ui_files))
        raise ValueError(f"ui_files keys drift probe-only={missing} disk-only={extra}")
    for rel, rec_fp in ui_files.items():
        disk_fp = live[rel]
        if not isinstance(rec_fp, dict):
            if rec_fp != disk_fp["bytes"]:
                raise ValueError(f"{rel}: probe bytes {rec_fp!r} != disk {disk_fp['bytes']}")
            continue
        if rec_fp.get("bytes") != disk_fp["bytes"]:
            raise ValueError(
                f"{rel}: bytes probe={rec_fp.get('bytes')} disk={disk_fp['bytes']}")
        if rec_fp.get("sha256") != disk_fp["sha256"]:
            raise ValueError(f"{rel}: sha256 mismatch")
    return True


if __name__ == "__main__":
    sys.exit(main())
