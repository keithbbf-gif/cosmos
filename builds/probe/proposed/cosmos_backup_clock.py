#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_backup_clock - 4x-daily verified backup satellite.

Cadence: Keith's backup hours 07/11/19/23 (ORCHESTRATION / BTS ruling).
Four daily schtasks, one script. Bounded snapshot of authority + identity
+ control + queue manifests — not the whole live tree (work/ logs/ collector
index rebuild). Uses cosmos_backup.Backup (hash-verify every file, ledger
BACKUP_VERIFIED). Does not modify Backup/Ledger source.

    py -3.14 cosmos\\cosmos_backup_clock.py --root V:\\A\\Ai\\COSMOS\\live --once
    py -3.14 cosmos\\cosmos_backup_clock.py --root ... --standup

Tasks: COSMOS Backup 07 / 11 / 19 / 23. No bts_*. Does not honor PAUSE
(backups keep moving so in-flight work is not the only surviving copy).
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import stat as _stat
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_backup import Backup, BackupError  # noqa: E402
from cosmos_clock import (  # noqa: E402
    create_task, heartbeat_age_s, query_task, read_heartbeat, tr_cmdline,
    write_heartbeat,
)
from cosmos_ledger import Ledger, LedgerError  # noqa: E402
from cosmos_paths import CosmosPaths, CosmosPathError  # noqa: E402

WORKER = "cosmos-backup-clock"
TASK_NAMES = (
    ("COSMOS Backup 07", "07:00"),
    ("COSMOS Backup 11", "11:00"),
    ("COSMOS Backup 19", "19:00"),
    ("COSMOS Backup 23", "23:00"),
)
HEARTBEAT_NAME = "backup_clock_heartbeat.json"
SCHEMA = "cosmos-backup-clock/1"
FRESH_S = 26 * 3600.0  # a missed 4x-daily window is stale after 26h
HOURS = {7, 11, 19, 23}
STAGE_LIMIT = 400

# MAX_PATH: Win32 caps a path at 260 chars (259 usable) unless it carries the
# `\\?\` extended-length prefix. Measured 2026-08-31, LongPathsEnabled = 0 on this
# machine. Without the prefix os.walk cannot descend past the limit and stat() fails
# winerror=3 — and the `except OSError: continue` below turned BOTH into a silent
# skip, after which poll_once still wrote state=VERIFIED. Measured against a real
# 262-char file: 2 files on disk, 1 copied, no error raised. Caveats: the prefix
# disables path normalization (abspath first), requires an absolute path, takes the
# \\?\UNC\ form for UNC, and is Windows-only — identity on POSIX.
_XP = "\\\\?\\"


def _x(p) -> str:
    r"""Extended-length form of a path. Identity on POSIX. Never double-prefixes."""
    s = str(p)
    if os.name != "nt" or s.startswith(_XP):
        return s
    if s.startswith("\\\\"):
        return _XP + "UNC" + s[1:]
    return _XP + os.path.abspath(s)


def _copy_file(src: Path, dest: Path) -> bool:
    try:
        if not _stat.S_ISREG(os.stat(_x(src)).st_mode):
            return False
    except OSError:
        return False
    os.makedirs(_x(dest.parent), exist_ok=True)
    shutil.copy2(_x(src), _x(dest))
    return True


def _copy_tree_files(src: Path, dest: Path, limit: int = STAGE_LIMIT) -> dict:
    """Copy files under src, skipping huge/rebuildable trees. Capped.

    Returns a RECORD, not a bare count. `truncated` and `unreadable` are the two ways
    this function can cover less than it was asked to, and both used to be invisible:
    the cap returned early and `except OSError: continue` ate the rest, while the
    caller still reported VERIFIED. A backup that drops files and says VERIFIED is
    the green-log defect the canon names; a bare int cannot express the hole, so the
    hole is returned and assemble_snapshot refuses on it.
    """
    rec = {"copied": 0, "truncated": False, "unreadable": [], "skipped_large": 0}
    if not os.path.isdir(_x(src)):
        return rec
    skip_dir = {"__pycache__", "_delme", ".git", "collector"}
    xsrc = _x(Path(src).resolve())
    cut = len(xsrc.rstrip("\\/")) + 1

    def _note(err: OSError):
        rec["unreadable"].append(f"{getattr(err, 'filename', '?')}: {err}")

    for dirpath, dirnames, filenames in os.walk(xsrc, onerror=_note):
        dirnames[:] = [d for d in dirnames if d not in skip_dir]
        for fn in filenames:
            if rec["copied"] >= limit:
                rec["truncated"] = True
                return rec
            sp = os.path.join(dirpath, fn)
            try:
                if os.stat(sp).st_size > 32 * 1024 * 1024:
                    rec["skipped_large"] += 1
                    continue
            except OSError as e:
                rec["unreadable"].append(f"{sp}: {type(e).__name__}: {e}")
                continue
            rel = sp[cut:]
            os.makedirs(_x(Path(dest) / os.path.dirname(rel)) if os.path.dirname(rel)
                        else _x(dest), exist_ok=True)
            shutil.copy2(sp, _x(Path(dest) / rel))
            rec["copied"] += 1
    return rec


def assemble_snapshot(paths: CosmosPaths, stage: Path) -> int:
    """Rebuild a bounded snapshot. Returns file count staged.

    REFUSES SNAPSHOT_INCOMPLETE if any subtree hit the cap or held an unreadable
    file. The snapshot IS the scope of the backup, so a short scope that still
    reports VERIFIED is the defect — the hole is raised here, not counted and
    forgotten. Measured 2026-08-31: queue/manifests holds 351 files against a
    400 cap, i.e. 87% of the way to a silent truncation nobody would have seen.
    """
    holes: list[str] = []

    def _stage(label: str, s: Path, d: Path) -> int:
        r = _copy_tree_files(s, d)
        if r["truncated"]:
            holes.append(f"{label}: hit the {STAGE_LIMIT}-file cap — scope TRUNCATED")
        if r["unreadable"]:
            holes.append(f"{label}: {len(r['unreadable'])} unreadable "
                         f"(first: {r['unreadable'][0][:160]})")
        return r["copied"]

    if stage.exists():
        shutil.rmtree(_x(stage), ignore_errors=True)
    os.makedirs(_x(stage), exist_ok=True)
    n = 0
    n += _stage("ledger", paths.ledger(), stage / "ledger")
    n += int(_copy_file(paths.config("install_record.json"),
                        stage / "config" / "install_record.json"))
    n += int(_copy_file(paths.config("install_key.bin"),
                        stage / "config" / "install_key.bin"))
    n += int(_copy_file(paths.config("cursor_rail.json"),
                        stage / "config" / "cursor_rail.json"))
    state = paths.role("state")
    for name in ("SEED.json", "SEED.decl.json"):
        n += int(_copy_file(state / name, stage / "state" / name))
    control = state / "control"
    if control.is_dir():
        n += _stage("state/control", control, stage / "state" / "control")
    q = paths.role("queue")
    n += int(_copy_file(q / "sched_ledger.jsonl",
                        stage / "queue" / "sched_ledger.jsonl"))
    n += _stage("queue/manifests", q / "manifests", stage / "queue" / "manifests")
    if holes:
        raise BackupError("SNAPSHOT_INCOMPLETE", "; ".join(holes))
    return n


def poll_once(root: str, *, force: bool = False) -> dict:
    paths = CosmosPaths(root)
    logs = paths.logs()
    logs.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    hour = time.localtime(t0).tm_hour
    extra: dict = {"schema": SCHEMA, "tick": "once", "hour": hour}

    if not force and hour not in HOURS:
        extra.update({"ok": True, "state": "SKIP",
                      "reason": "not a backup hour (07/11/19/23)",
                      "elapsed_s": round(time.time() - t0, 3)})
        hb = write_heartbeat(logs / HEARTBEAT_NAME, WORKER, extra=extra)
        return {"ok": True, "skipped": True, "heartbeat": hb}

    keyfile = paths.config("install_key.bin")
    try:
        if not keyfile.exists():
            raise FileNotFoundError("no install_key.bin")
        key = keyfile.read_bytes()
        ledger = Ledger(paths.ledger("authority.jsonl"), key, WORKER)
        stage = paths.backups("_snapshot")
        n = assemble_snapshot(paths, stage)
        if n <= 0:
            raise BackupError("EMPTY_SCOPE", "snapshot staged 0 files")
        bak = Backup(ledger)
        result = bak.run(stage, paths.backups("verified"))
        extra.update({
            "ok": True, "state": "VERIFIED",
            "files": result.get("files"),
            "dest": str(result.get("dest")),
            "staged": n,
        })
    except (BackupError, LedgerError, OSError, FileNotFoundError) as e:
        kind = getattr(e, "kind", type(e).__name__)
        extra.update({"ok": False, "state": "FAILED", "kind": kind,
                      "detail": str(e)[:400]})
    extra["elapsed_s"] = round(time.time() - t0, 3)
    hb = write_heartbeat(logs / HEARTBEAT_NAME, WORKER, extra=extra)
    extra["heartbeat"] = hb
    extra["heartbeat_path"] = str(logs / HEARTBEAT_NAME)
    return extra


def standup(root: str) -> dict:
    script = Path(__file__).resolve()
    tr = tr_cmdline(script, root, "--once", "--force")
    tasks = []
    keith = []
    for name, st in TASK_NAMES:
        existing = query_task(name)
        if existing.get("ok"):
            tasks.append({"name": name, "started": "already",
                          "ok": True, "query": existing.get("ok")})
            continue
        rec = create_task(name, tr, "DAILY", st=st, run_now=False)
        rec["name"] = name
        rec["st"] = st
        tasks.append(rec)
        if rec.get("keith_cmd") and (rec.get("needs_elevation") or not rec.get("ok")):
            keith.append(rec["keith_cmd"])
    tick = poll_once(root, force=True)
    return {
        "started": "schtasks",
        "tasks": [{"name": t.get("name"), "ok": t.get("ok"),
                   "st": t.get("st"), "out": (t.get("out") or "")[:200]}
                  for t in tasks],
        "tick": {"ok": tick.get("ok"), "state": tick.get("state"),
                 "files": tick.get("files")},
        "proof": {"ok": bool(tick.get("ok")), "heartbeat": tick.get("heartbeat")},
        "keith_cmd": " & ".join(keith) if keith else None,
        "keith_cmds": keith,
        "task_names": [n for n, _ in TASK_NAMES],
    }


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_backup_clock")
    ap.add_argument("--root", required=True)
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--force", action="store_true",
                    help="run the backup even off-hour (standup / manual)")
    ap.add_argument("--standup", action="store_true")
    ap.add_argument("--status", action="store_true")
    a = ap.parse_args()
    if a.status:
        paths = CosmosPaths(a.root)
        rec = read_heartbeat(paths.logs(HEARTBEAT_NAME))
        age = heartbeat_age_s(rec)
        print(json.dumps({"path": str(paths.logs(HEARTBEAT_NAME)),
                          "age_s": age, "heartbeat": rec}, indent=1,
                         default=str))
        return 0 if age is not None and age < FRESH_S else 2
    if a.standup:
        r = standup(a.root)
        print(json.dumps(r, indent=1, default=str))
        return 0 if (r.get("proof") or {}).get("ok") else 2
    r = poll_once(a.root, force=a.force)
    print(json.dumps({k: r[k] for k in r if k != "heartbeat"},
                     indent=1, default=str))
    return 0 if r.get("ok") else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CosmosPathError as e:
        print(e, file=sys.stderr)
        raise SystemExit(2)
