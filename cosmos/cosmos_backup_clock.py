#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""cosmos_backup_clock - 4x-daily verified backup satellite.

Cadence: Keith's backup hours 07/11/19/23 (ORCHESTRATION / BTS ruling).
Four daily schtasks, one script. Bounded snapshot of authority + identity
+ control + queue manifests — not the whole live tree (work/ logs/ collector
index rebuild). Uses cosmos_backup.Backup (hash-verify every file, ledger
BACKUP_VERIFIED). Does not modify Backup/Ledger source.

    py -3.14 cosmos\\cosmos_backup_clock.py --root V:\\A\\Ai\\COSMOS\\live --once
    py -3.14 cosmos\\cosmos_backup_clock.py --root ... --standup

Tasks: COSMOS Backup 07 / 11 / 19 / 23. No bts_*. Does not honor PAUSE
(backups keep moving so in-flight work is not the only surviving copy).

THE SNAPSHOT IS THE SCOPE, so a short snapshot is a short backup wearing a VERIFIED
label. Measured 2026-08-31 (docs/LONGPATH_FINDING.md, builds/backup/COVERAGE.md gap 2)
this module could shorten its own scope FOUR silent ways, and `poll_once` still wrote
state=VERIFIED over every one of them:

  * MAX_PATH   os.walk could not descend past 259 chars and `sp.stat()` failed
               winerror=3; `except OSError: continue` ate both. Against a real 3-file
               fixture: copied 1, reported 1, no error. (Both halves needed: the `\\?\`
               prefix on the ROOT so the files are SEEN, and no swallowed errors.)
  * the CAP    _copy_tree_files returned early at 400 files. A bare int cannot express
               "and there were more", so the truncation was invisible. Measured:
               queue/manifests holds 351 files against that 400 cap - 87% of the way
               to a silent truncation nobody would have seen.
  * unreadable a file that could not be stat'ed was skipped, not named.
  * oversize   a file over MAX_STAGE_BYTES was dropped from a BOUNDED scope in silence
               (authority.jsonl is in that scope and it only grows).

So `_copy_tree_files` now returns a RECORD of every way it covered less than it was
asked to, `_copy_file` refuses on unreadable while still tolerating genuinely absent
optional files, and `assemble_snapshot` raises SNAPSHOT_INCOMPLETE rather than handing
a truncated scope to a function whose next act is to append BACKUP_VERIFIED.

CONSEQUENCE, deliberate: a run that would previously have said VERIFIED over a hole now
FAILS. With queue/manifests at 351/400 that refusal is one Keith should expect - and the
remedy is to raise STAGE_LIMIT, not to restore the silence.
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

from cosmos_backup import Backup, BackupError, refuse_secrets  # noqa: E402
from cosmos_clock import (  # noqa: E402
    create_task, heartbeat_age_s, query_task, read_heartbeat, tr_cmdline,
    write_heartbeat,
)
from cosmos_ledger import Ledger, LedgerError  # noqa: E402
from cosmos_paths import CosmosPaths, CosmosPathError, extended as _x  # noqa: E402

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
SKIP_DIRS = frozenset({"__pycache__", "_delme", ".git", "collector"})
STAGE_LIMIT = 400              # per-subtree file cap; hitting it REFUSES, never truncates
MAX_STAGE_BYTES = 32 * 1024 * 1024


def _copy_file(src: Path, dest: Path) -> bool:
    r"""Copy one NAMED optional file. True if copied, False if genuinely absent.

    Absent and unreadable are two different facts and must never collapse into one
    False - that collapse is how an unreadable install_key or SEED left the snapshot
    without a word. Note the stat goes through the `\\?\` prefix FIRST: unprefixed, a
    path merely too long also raises FileNotFoundError (winerror 3), i.e. a length
    limit wearing a missing-file error's clothes (the C-60 scar in cosmos_paths).
    """
    try:
        return _stat.S_ISREG(os.stat(_x(src)).st_mode) and _do_copy(src, dest)
    except FileNotFoundError:
        return False
    except OSError as e:
        raise BackupError("SOURCE_UNREADABLE",
                          f"{src}: {type(e).__name__}: {e} - a file this backup "
                          f"cannot read is a HOLE, not a file to skip") from e


def _do_copy(src: Path, dest: Path) -> bool:
    os.makedirs(_x(Path(dest).parent), exist_ok=True)
    shutil.copy2(_x(src), _x(dest))
    return True


def _copy_tree_files(src: Path, dest: Path, limit: int | None = None) -> dict:
    r"""Copy files under src, skipping huge/rebuildable trees. Capped.

    Returns a RECORD, not a bare count: {copied, truncated, unreadable, skipped_large}.
    `truncated`, `unreadable` and `skipped_large` are the three ways this function can
    cover less than it was asked to, and a bare int could express none of them - so the
    caller reported VERIFIED over the shortfall. The hole is returned; assemble_snapshot
    refuses on it.

    The walk starts from the `\\?\`-prefixed root, so every descendant inherits the
    prefix and files past MAX_PATH are SEEN rather than filtered out by an
    error-swallowing test.
    """
    limit = STAGE_LIMIT if limit is None else limit
    rec: dict = {"copied": 0, "truncated": False, "unreadable": [], "skipped_large": []}
    if not os.path.isdir(_x(src)):
        return rec
    xsrc = _x(Path(src).resolve())
    cut = len(xsrc.rstrip("\\/")) + 1
    dest = Path(dest)

    def _note(err: OSError):
        # os.walk's default onerror=None EATS this; a directory the backup cannot list
        # is a hole in the backup, so it is recorded and the caller refuses.
        rec["unreadable"].append(f"{getattr(err, 'filename', '?')}: "
                                 f"{type(err).__name__}: {err}")

    for dirpath, dirnames, filenames in os.walk(xsrc, onerror=_note):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in sorted(filenames):
            if rec["copied"] >= limit:
                rec["truncated"] = True
                return rec
            sp = os.path.join(dirpath, fn)          # already extended, inherited
            try:
                if os.stat(sp).st_size > MAX_STAGE_BYTES:
                    rec["skipped_large"].append(sp[cut:])
                    continue
            except OSError as e:
                rec["unreadable"].append(f"{sp}: {type(e).__name__}: {e}")
                continue
            rel = sp[cut:]
            os.makedirs(_x((dest / rel).parent), exist_ok=True)
            shutil.copy2(sp, _x(dest / rel))
            rec["copied"] += 1
    return rec


def assemble_snapshot(paths: CosmosPaths, stage: Path) -> int:
    """Rebuild a bounded snapshot. Returns file count staged.

    REFUSES SNAPSHOT_INCOMPLETE if any subtree hit the cap, held a file it could not
    read, or dropped one for size. The snapshot IS the scope of the backup, so a short
    scope that still reports VERIFIED is the defect - the hole is raised here, not
    counted and forgotten.
    """
    stage = Path(stage)
    holes: list[str] = []

    def _stage(label: str, s: Path, d: Path) -> int:
        r = _copy_tree_files(s, d)
        if r["truncated"]:
            holes.append(f"{label}: hit the {STAGE_LIMIT}-file cap - scope TRUNCATED "
                         f"(raise STAGE_LIMIT; do not restore the silence)")
        if r["unreadable"]:
            holes.append(f"{label}: {len(r['unreadable'])} unreadable "
                         f"(first: {r['unreadable'][0][:160]})")
        if r["skipped_large"]:
            holes.append(f"{label}: {len(r['skipped_large'])} over "
                         f"{MAX_STAGE_BYTES} bytes (first: {r['skipped_large'][0][:160]})")
        return r["copied"]

    if os.path.exists(_x(stage)):
        shutil.rmtree(_x(stage), ignore_errors=True)
        if os.path.exists(_x(stage)) and os.listdir(_x(stage)):
            # leftovers from the previous snapshot would be hashed and shipped as if
            # they were current - a stale file inside a VERIFIED set is the same lie
            # from the other side.
            holes.append(f"stage: {stage} could not be cleared - a previous snapshot "
                         f"would be backed up as current")
    os.makedirs(_x(stage), exist_ok=True)
    n = 0
    n += _stage("ledger", paths.ledger(), stage / "ledger")
    n += int(_copy_file(paths.config("install_record.json"),
                        stage / "config" / "install_record.json"))
    # install_key.bin is READ in poll_once to open the ledger. It is NOT
    # copied into the snapshot: a local copy of the signing key is COVERAGE
    # gap 4 (SECRETS_IN_SCOPE). Restore uses the live config key, not a
    # duplicate sitting next to the backup set.
    n += int(_copy_file(paths.config("cursor_rail.json"),
                        stage / "config" / "cursor_rail.json"))
    state = paths.role("state")
    for name in ("SEED.json", "SEED.decl.json"):
        n += int(_copy_file(state / name, stage / "state" / name))
    control = state / "control"
    if os.path.isdir(_x(control)):
        n += _stage("state/control", control, stage / "state" / "control")
    q = paths.role("queue")
    n += int(_copy_file(q / "sched_ledger.jsonl",
                        stage / "queue" / "sched_ledger.jsonl"))
    n += _stage("queue/manifests", q / "manifests", stage / "queue" / "manifests")
    if holes:
        raise BackupError("SNAPSHOT_INCOMPLETE", "; ".join(holes))
    refuse_secrets(stage)
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
        bak = Backup(ledger, node=paths.sentinel.system)
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
