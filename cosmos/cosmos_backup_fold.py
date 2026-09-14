#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_backup_fold — GET-only backup clock fold for cDeck.

Never runs a backup. Never mkdir. Heartbeat + verified dir if they exist.

    py -3.14 cosmos\\\\cosmos_backup_fold.py --selftest
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

HOURS = (7, 11, 19, 23)
HB_NAME = "backup_clock_heartbeat.json"


class BackupFoldError(Exception):
    def __init__(self, kind: str, detail: str = ""):
        self.kind = kind
        super().__init__(detail)


def _profiles_for_backup(paths) -> list[dict]:
    """Per-profile dest hints for cDeck chips — GET only, no MOTIF start."""
    try:
        from cosmos_profiles import catalog, engine_path
        import json as _json
    except Exception:  # noqa: BLE001
        return []
    out = []
    for p in catalog():
        pid = p.get("id") or ""
        dest = {"kind": "", "path": ""}
        ep = engine_path(paths, pid)
        if ep.is_file():
            try:
                eng = _json.loads(ep.read_text(encoding="utf-8"))
                if isinstance(eng, dict) and isinstance(eng.get("dest"), dict):
                    dest = {
                        "kind": eng["dest"].get("kind") or "",
                        "path": eng["dest"].get("path") or "",
                    }
            except (OSError, ValueError, UnicodeDecodeError):
                pass
        out.append({
            "id": pid,
            "label": p.get("label") or pid,
            "dest": dest,
            "dest_catalog": p.get("dest") or [],
        })
    return out


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
    rec["profiles"] = _profiles_for_backup(paths)
    rec["tree_id"] = paths.sentinel.tree_id
    rec["iso"] = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    return rec


def run_action(paths, body, *, kernel=None) -> dict:
    """POST verbs for the backup suite. Never a silent full-tree backup."""
    if not isinstance(body, dict):
        raise BackupFoldError("BAD_REQUEST", "body must be a JSON object")
    action = str(body.get("action") or "").strip().lower()
    if not action:
        raise BackupFoldError("BAD_ACTION", "action required")

    rec = {
        "schema": "cosmos-backup-fold/1",
        "action": action,
        "ok": True,
        "measured_at": time.time(),
        "tree_id": paths.sentinel.tree_id,
        "note": "POST only — GET never runs a backup.",
    }

    if action == "surface_test":
        rec["kind"] = "SURFACE_TEST"
        rec["measure_all"] = bool(body.get("measure_all"))
        rec["surfaces"] = {"kind": "NO_SOURCE", "rows": []}
        sf = getattr(kernel, "surfaces", None) if kernel is not None else None
        if sf is not None and hasattr(sf, "report"):
            try:
                rows = sf.report() or []
                rec["surfaces"] = {
                    "kind": "OK",
                    "rows": rows if isinstance(rows, list) else [],
                    "n": len(rows) if isinstance(rows, list) else 0,
                }
            except Exception as e:  # noqa: BLE001
                rec["surfaces"] = {
                    "kind": "BROKE",
                    "detail": f"{type(e).__name__}: {e}"[:200],
                    "rows": [],
                }
        rec["note"] = (
            "surface_test (measure_all) qualifies targets; "
            "does not run a full-tree backup."
        )
        return rec

    if action == "search":
        rec["kind"] = "SEARCH"
        candidates = []
        sf = getattr(kernel, "surfaces", None) if kernel is not None else None
        if sf is not None and hasattr(sf, "report"):
            try:
                for row in sf.report() or []:
                    if not isinstance(row, dict):
                        continue
                    candidates.append({
                        "id": row.get("id") or row.get("name"),
                        "role": row.get("role"),
                        "path": row.get("path"),
                    })
            except Exception:  # noqa: BLE001
                candidates = []
        rec["candidates"] = candidates[:32]
        rec["note"] = "search returns dest candidates; Keith picks dest."
        return rec

    if action == "restore":
        bak = str(body.get("bak") or body.get("bak_name") or "").strip()
        if not bak:
            raise BackupFoldError(
                "BAK_REQUIRED",
                "restore refuses without a verified bak name",
            )
        rec["kind"] = "REFUSED"
        rec["bak"] = bak
        rec["error"] = "RESTORE_NOT_RUN_FROM_PANEL"
        rec["note"] = (
            "restore is POST-only with explicit bak; "
            "Core does not silent-restore from the fold."
        )
        return rec

    if action == "generate":
        dest = str(body.get("dest") or body.get("dest_id") or "").strip()
        if not dest:
            raise BackupFoldError(
                "DEST_REQUIRED",
                "generate refuses without explicit dest",
            )
        rec["kind"] = "REFUSED"
        rec["dest"] = dest
        rec["error"] = "GENERATE_NOT_RUN_FROM_PANEL"
        rec["note"] = "Never a silent full-tree backup."
        return rec

    raise BackupFoldError("BAD_ACTION", f"unknown action {action!r}")


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
    check("GET lists profile dest hints for backup chips",
          lambda: isinstance(rec.get("profiles"), list))

    post = run_action(paths, {"action": "surface_test", "measure_all": True})
    check("POST surface_test accepts measure_all",
          lambda: post.get("kind") == "SURFACE_TEST"
          and post.get("measure_all") is True)
    refused = False
    try:
        run_action(paths, {"action": "restore"})
    except BackupFoldError as e:
        refused = e.kind == "BAK_REQUIRED"
    check("POST restore refuses without bak name", lambda: refused)
    refused_gen = False
    try:
        run_action(paths, {"action": "generate"})
    except BackupFoldError as e:
        refused_gen = e.kind == "DEST_REQUIRED"
    check("POST generate refuses without dest", lambda: refused_gen)

    bad = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (backup fold)"
          % ("PASS" if not bad else "FAIL", len(results)))
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(_selftest())
