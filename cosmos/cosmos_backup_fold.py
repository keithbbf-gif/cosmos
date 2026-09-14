#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_backup_fold — backup clock fold for cDeck.

GET never runs a backup. Never mkdir. Heartbeat + verified dir if they exist.
POST suite verbs refuse a silent full-tree backup: no sources is BACKUP_REFUSED.

    py -3.14 cosmos\\\\cosmos_backup_fold.py --selftest
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

HOURS = (7, 11, 19, 23)
HB_NAME = "backup_clock_heartbeat.json"


class BackupFoldError(RuntimeError):
    """kind in {BACKUP_REFUSED}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        self.detail = detail
        super().__init__(f"[{kind}] {detail}")


def _source_list(body: dict) -> list:
    raw = body.get("sources")
    if raw is None:
        return []
    if isinstance(raw, str):
        return [raw] if raw.strip() else []
    if isinstance(raw, (list, tuple)):
        out = []
        for item in raw:
            if item is None:
                continue
            s = str(item).strip()
            if s:
                out.append(s)
        return out
    return []


def run_action(paths, body, kernel=None) -> dict:
    """POST suite. Never a silent full-tree backup. HTTP never copies files."""
    if not isinstance(body, dict):
        raise BackupFoldError("BACKUP_REFUSED", "body must be a JSON object")
    action = str(body.get("action") or "").strip().lower()
    if action in ("restore", "generate"):
        bak = body.get("bak") or body.get("backup")
        dest = body.get("dest") or body.get("target")
        if not bak or not dest:
            raise BackupFoldError(
                "BACKUP_REFUSED",
                "restore/generate refuse without bak/dest",
            )
    sources = _source_list(body)
    if not sources:
        raise BackupFoldError(
            "BACKUP_REFUSED",
            "no sources - never a silent full-tree backup",
        )
    # A 200 that copied nothing (or everything) on the HTTP thread is the
    # green-log class this fold exists to stop. Clock + scheduled job run.
    raise BackupFoldError(
        "BACKUP_REFUSED",
        "POST /backup does not run a backup on the HTTP thread",
    )


def snapshot(paths) -> dict:
    """GET. Missing heartbeat is NO_SOURCE, not an empty backup."""
    hb_path = paths.logs(HB_NAME)
    rec = {
        "schema": "cosmos-backup-fold/1",
        "hours": list(HOURS),
        "heartbeat": None,
        "verified": None,
        "available": False,
        "kind": "NO_SOURCE",
        "note": (
            "GET never runs a backup. Hours 07/11/19/23. "
            "Header Backup key opens this pane. Does not paste secrets."
        ),
        "measured_at": time.time(),
    }
    if hb_path.is_file():
        try:
            hb = json.loads(hb_path.read_text(encoding="utf-8"))
            if isinstance(hb, dict):
                rec["heartbeat"] = hb
                rec["available"] = True
                rec["kind"] = "OK"
        except (OSError, ValueError, UnicodeDecodeError):
            rec["kind"] = "BROKE"
    try:
        verified = paths.backups("verified")
    except Exception:  # noqa: BLE001
        verified = None
    if verified is not None and verified.is_dir():
        names = []
        try:
            for p in sorted(verified.iterdir(), key=lambda x: x.name, reverse=True):
                if p.is_dir() or p.is_file():
                    names.append(p.name)
                if len(names) >= 8:
                    break
        except OSError:
            names = []
        rec["verified"] = {"dir": True, "recent": names}
        if rec["kind"] == "NO_SOURCE":
            rec["kind"] = "OK"
            rec["available"] = True
    rec["tree_id"] = paths.sentinel.tree_id
    rec["iso"] = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
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

    td = Path(tempfile.mkdtemp(prefix="cosmos_bakfold_"))
    root = install(td / "live", tree_id="spike-backup")
    paths = CosmosPaths(root)
    rec = snapshot(paths)
    check("GET missing heartbeat is NO_SOURCE and does not mkdir",
          lambda: rec.get("kind") == "NO_SOURCE"
          and rec.get("hours") == [7, 11, 19, 23]
          and not paths.logs(HB_NAME).exists())
    check("GET does not claim a backup ran",
          lambda: "never runs a backup" in (rec.get("note") or ""))

    no_src = None
    try:
        run_action(paths, {})
    except BackupFoldError as e:
        no_src = e
    check("POST no sources is BACKUP_REFUSED (not an exception escape)",
          lambda: no_src is not None
          and no_src.kind == "BACKUP_REFUSED"
          and "no sources" in (no_src.detail or ""))
    empty_list = None
    try:
        run_action(paths, {"sources": []})
    except BackupFoldError as e:
        empty_list = e
    check("POST empty sources list is BACKUP_REFUSED",
          lambda: empty_list is not None
          and empty_list.kind == "BACKUP_REFUSED")

    bad = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (backup fold)"
          % ("PASS" if not bad else "FAIL", len(results)))
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(_selftest())
