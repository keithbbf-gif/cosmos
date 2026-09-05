#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""cosmos_local_clock - scheduled vehicle for the F-43 P0 local daemon.

WHY THIS EXISTS. `builds/backup/cosmos_backup.py` is the HMAC / freeze /
SOURCE_MUTATED / SECRETS_IN_SCOPE daemon the wishlist named. Its docstring
mentions `schtasks /Create /TN COSMOS_Backup` but nothing emitted a
`schtasks /create` line (F-47/F-48/F-54 clocks push adapters or the F-54
whitelist; none schedule this daemon). The running 4x-daily clock is the
*other* module (`cosmos/cosmos_backup_clock.py`) and its dest is still
same-volume `live/backups`.

WITHOUT dest named — which is the deliverable today:

    tick() REFUSES typed `NO_CONFIG` / `NO_DEST` / `NO_SOURCE`, heartbeats
    the refusal, exits 2, and creates no backup set. `--plan-task` emits
    `COSMOS Bulletproof Backup` daily 04:00 and registers nothing, so the
    task can be armed today and refuse visibly until Keith names
    `targets.local.dest` (and `targets.local.source`) in
    `backup_targets.json`. A dest on the SAME volume as the source is
    `SAME_VOLUME` — that is the gap this clock exists to close.

A dest is NEVER invented. Existence of `live/backups` is not a dest.
`--install-task` exists and is Keith's elevated line.

    py -3.14 builds/backup/cosmos_local_clock.py --root V:\A\Ai\COSMOS\live --preflight
    py -3.14 builds/backup/cosmos_local_clock.py --root V:\A\Ai\COSMOS\live --selfcheck
    py -3.14 builds/backup/cosmos_local_clock.py --root V:\A\Ai\COSMOS\live --once
    py -3.14 builds/backup/cosmos_local_clock.py --root V:\A\Ai\COSMOS\live --plan-task
    py -3.14 builds/backup/cosmos_local_clock.py --root V:\A\Ai\COSMOS\live --install-task
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import cosmos_backup as cb                      # noqa: E402
import cosmos_backup_mounts as mounts           # noqa: E402
import cosmos_offsite_clock as oc               # noqa: E402
from cosmos_backup import BackupRefusal         # noqa: E402

CosmosPaths = oc.CosmosPaths
CosmosPathError = oc.CosmosPathError

SCHEMA = "cosmos-local-clock/1"
WORKER = "cosmos-local-clock"
HEARTBEAT_NAME = "local_clock_heartbeat.json"
CONFIG_NAME = mounts.CONFIG_NAME
KIND = "local"
TASK_NAME = "COSMOS Bulletproof Backup"
DEFAULT_AT = "04:00"
SELFCHECK_STAGE = "_delme_local_selfcheck"
NO_WINDOW = 0x08000000 if os.name == "nt" else 0
STALE_S = 26 * 3600.0

# Whole-tree local backup (targets.local.source = the repo tree, dest on
# another volume, unencrypted). Per-target, not a second global: other
# adapters keep cosmos_backup.DEFAULT_EXCLUDES. Operator extras in
# targets.local.excludes are UNIONED with this set — they cannot drop
# live/config or *.lock from an unencrypted dest.
#
# CALL, written here so it is not just a changelog line:
#
# A file that is IN SCOPE and unreadable still REFUSES (SOURCE_UNREADABLE).
# That is the MAX_PATH defect: a hole must never look like coverage. The
# bug this clock hit at 16:50Z was that runtime lock files were IN SCOPE
# at all — tick() passed DEFAULT_EXCLUDES (".git", "__pycache__") and the
# walker opened live/logs/cdeck_feed.lock, held exclusive by the running
# daemon. The refusal was correct. The scope was wrong.
#
# NOT data (out of scope):
#   *.lock            writer-fence siblings, not the file they guard.
#                     live/ledger/authority.jsonl.lock sits NEXT TO the
#                     ledger; excluding live/logs alone would still refuse
#                     on the ledger lock. Same for queue/state jsonl.lock.
#   live/logs         runtime logs, heartbeats, .err/.out. Rebuildable.
#   live/work         attempt-private scratch.
#   live/backups      same-volume backup sets; copying them is recursive.
#   live/returns      agent IPC drop zone; the collector already harvested.
#   _delme            staged deletions, not live data.
#   .git, __pycache__ already default.
#
# IN scope (the point of a whole-tree local copy):
#   live/ledger       authority.jsonl — the signed hash chain. Valuable.
#                     Its .lock sibling is excluded by *.lock, not the dir.
#   live/state        SEED.json carry-over + control. Valuable.
#   live/registry, live/queue, live/publish, live/.cosmos-root.json
#   cosmos/, docs/, tests/, kdash/, builds/, governance
#
# NEVER copied to this dest:
#   live/config       credentials (install_key.bin, api_token.txt, …).
#                     Dest is unencrypted. SECRETS_IN_SCOPE would refuse
#                     the whole run if this dir stayed in scope; excluding
#                     it is the decision (do not copy secrets), not a
#                     bypass of the scanner. Other secret path-shapes
#                     still in scope still refuse.
#   trylive/config    measured 2026-08-31: a second runtime-config tree
#                     holding the same credential path-shapes. Same call.
#   install_key.bin, api_token.txt
#                     basename belt: a stray copy anywhere is still not
#                     copied. Scanner still refuses any other in-scope
#                     secret path-shape (PEM private, .pfx, …).
LOCAL_DEFAULT_EXCLUDES = (
    ".git",
    "__pycache__",
    "_delme",
    "*.lock",
    "live/logs",
    "live/work",
    "live/backups",
    "live/config",
    "live/returns",
    "trylive/config",
    "install_key.bin",
    "api_token.txt",
)


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")


def read_heartbeat(path: Path) -> dict:
    """A non-object heartbeat is the same as unreadable: empty dict.

    json.loads('[]') succeeds, then tick AttributeErrors on .get.
    Bite `_bite_unpinned_round8.json`.
    """
    try:
        obj = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return obj if isinstance(obj, dict) else {}


def write_heartbeat(path: Path, rec: dict) -> dict:
    """Written on EVERY tick — pass, refusal or pause."""
    if not isinstance(rec, dict):
        raise BackupRefusal(
            "BAD_HEARTBEAT",
            f"heartbeat rec is {type(rec).__name__}, not an object")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now().astimezone()
    body = dict(rec)
    body.update({
        "worker": WORKER, "pid": os.getpid(),
        "last_run": now.isoformat(timespec="seconds"),
        "last_run_epoch": int(now.timestamp()),
        "last_run_utc": _utcnow(),
        "_readme": ("Written on EVERY tick. last_run_epoch = is the CLOCK alive. "
                    "last_success_epoch = is the DATA on a different volume. "
                    "state=REFUSED with kind=NO_DEST means the daemon is wired "
                    "and waiting on targets.local.dest."),
    })
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(body, indent=1, default=str), encoding="utf-8")
    os.replace(tmp, path)
    return body


def parse_excludes(row: dict) -> tuple[str, ...]:
    """Union LOCAL_DEFAULT_EXCLUDES with optional targets.local.excludes.

    Absent / empty extras keep the defaults. A non-list is BAD_CONFIG.
    Safety patterns (*.lock, live/config, …) cannot be dropped: extras
    are added, never a replacement. That is the unencrypted-dest call.
    """
    if not isinstance(row, dict):
        raise BackupRefusal(
            "BAD_CONFIG",
            f"targets.{KIND} row is {type(row).__name__}, not an object")
    extra = row.get("excludes")
    if extra is None:
        return LOCAL_DEFAULT_EXCLUDES
    if not isinstance(extra, list) or not all(
            isinstance(x, str) and x.strip() for x in extra):
        raise BackupRefusal(
            "BAD_CONFIG",
            f"targets.{KIND}.excludes must be a list of non-empty strings")
    seen: list[str] = []
    for item in (*LOCAL_DEFAULT_EXCLUDES,
                 *(x.strip().replace("\\", "/") for x in extra)):
        if item not in seen:
            seen.append(item)
    return tuple(seen)


def local_row(config: dict) -> dict:
    """targets.local dest+source+excludes. Empty is NO_DEST / NO_SOURCE, never guessed."""
    if not isinstance(config, dict):
        raise BackupRefusal(
            "BAD_CONFIG",
            f"{CONFIG_NAME} is {type(config).__name__}, not an object")
    row = (config.get("targets") or {}).get(KIND)
    if not isinstance(row, dict):
        raise BackupRefusal("NO_DEST",
                            f"{CONFIG_NAME} has no targets.{KIND} row — "
                            "Keith names dest; COSMOS never invents live/backups")
    raw_dest = row.get("dest")
    if not isinstance(raw_dest, str) or not raw_dest.strip():
        raise BackupRefusal("NO_DEST",
                            f"targets.{KIND}.dest is empty — Keith names it")
    dest = Path(raw_dest.strip())
    if not dest.is_absolute():
        raise BackupRefusal("BAD_CONFIG",
                            f"targets.{KIND}.dest must be absolute, got {raw_dest!r}")
    raw_src = row.get("source")
    src = None
    if isinstance(raw_src, str) and raw_src.strip():
        src = Path(raw_src.strip())
        if not src.is_absolute():
            raise BackupRefusal("BAD_CONFIG",
                                f"targets.{KIND}.source must be absolute, got {raw_src!r}")
    ident = row.get("identity")
    if ident is not None and not isinstance(ident, dict):
        raise BackupRefusal("BAD_CONFIG",
                            f"targets.{KIND}.identity is not an object")
    return {"dest": dest, "source": src, "identity": ident,
            "excludes": parse_excludes(row)}


def bind_local(dest: Path, source: Path, probe=None, identity=None) -> Path:
    """Dest must exist as a directory on a DIFFERENT volume from source.

    Drive letter is not identity (empty-dir scar). Optional `identity` is
    CONTENT — volume_serial / volume_label / sentinel / model — checked
    by the same `_check_identity` F-48 mounts already run. A swapped
    disk at the same letter is IDENTITY_MISMATCH, never a silent copy.
    """
    probe = probe or mounts.MountProbe()
    dest_p = Path(dest)
    if not dest_p.is_absolute():
        raise BackupRefusal("BAD_CONFIG", "dest must be an absolute path")
    dest_p = mounts.guard_dest(dest_p)
    if not probe.is_dir(dest_p):
        raise BackupRefusal("DRIVE_NOT_MOUNTED",
                            f"local dest is not a directory: {dest_p}")
    src_vol = probe.volume_id(Path(source))
    dst_vol = probe.volume_id(dest_p)
    if src_vol == dst_vol:
        raise BackupRefusal(
            "SAME_VOLUME",
            f"local dest {dest_p} is volume {dst_vol}, the same as source "
            f"{source} — a drive failure takes both")
    if identity is not None and not isinstance(identity, dict):
        raise BackupRefusal("BAD_CONFIG",
                            f"targets.{KIND}.identity is not an object")
    mounts._check_identity({"kind": KIND, "dest": dest_p, "identity": identity},
                           probe)
    return dest_p


def tick(paths: CosmosPaths, config_path: Path, *,
         source: Path | None = None, dest: Path | None = None,
         probe=None, force: bool = False, freeze=None) -> dict:
    """One local-backup cycle. Returns the heartbeat; NEVER raises for a refusal.

    `probe` and `dest` are injection seams: `--selfcheck` drives THIS function
    with FakeProbe + a scratch dest so the scheduled path is what gets proven.
    """
    t0 = time.time()
    prev = read_heartbeat(paths.logs(HEARTBEAT_NAME))
    rec: dict = {"schema": SCHEMA, "ts": _utcnow(), "tick": "once",
                 "config_path": str(config_path)}
    for k in ("last_success_epoch", "last_success_utc"):
        if prev.get(k) is not None:
            rec[k] = prev[k]

    if not force and oc.paused(paths):
        rec.update({"ok": True, "state": "PAUSED",
                    "detail": "state/control/PAUSE.flag is not RUNNING"})
        return _finish(paths, rec, t0)

    try:
        src = Path(source) if source is not None else None
        dest_p = Path(dest) if dest is not None else None
        identity = None
        excludes = LOCAL_DEFAULT_EXCLUDES
        if dest_p is None:
            cfg = mounts.load_config(Path(config_path))
            spec = local_row(cfg)
            dest_p = spec["dest"]
            identity = spec["identity"]
            excludes = spec["excludes"]
            if src is None:
                src = spec["source"]
        if src is None:
            raise BackupRefusal("NO_SOURCE",
                                "targets.local.source is empty and --source was "
                                "not given — no tree is ever guessed")
        dest_p = bind_local(dest_p, src, probe=probe, identity=identity)
        rec["excludes"] = list(excludes)
        completed = cb.run_once([src], dest_p, excludes, None, freeze=freeze)
    except BackupRefusal as e:
        rec.update({"ok": False, "state": "REFUSED", "kind": e.kind,
                    "detail": e.detail,
                    "unblocks": ("name targets.local.dest (and .source) in "
                                 "backup_targets.json on a different volume")
                                if e.kind in ("NO_CONFIG", "NO_DEST", "NO_SOURCE",
                                              "SAME_VOLUME", "BAD_CONFIG") else None})
        return _finish(paths, rec, t0)
    except Exception as e:                                            # noqa: BLE001
        rec.update({"ok": False, "state": "CRASHED",
                    "kind": type(e).__name__, "detail": str(e)[:400]})
        return _finish(paths, rec, t0)

    stats = _set_stats(completed)
    rec.update({"ok": True, "state": "VERIFIED",
                "source": str(src), "dest": str(dest_p),
                "files": stats["files"], "bytes": stats["bytes"],
                "sets": stats["sets"],
                "last_success_epoch": int(time.time()),
                "last_success_utc": _utcnow()})
    return _finish(paths, rec, t0)


def _set_stats(completed: list | None) -> dict:
    """file_count / total_bytes from each sealed MANIFEST. rc=0 is not the proof."""
    out = {"files": 0, "bytes": 0, "sets": []}
    for row in completed or ():
        set_dir = Path(row["set"])
        out["sets"].append(str(set_dir))
        mp = set_dir / cb.MANIFEST_NAME
        try:
            m = json.loads(mp.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        out["files"] += int(m.get("file_count") or 0)
        out["bytes"] += int(m.get("total_bytes") or 0)
    return out


def _finish(paths: CosmosPaths, rec: dict, t0: float) -> dict:
    rec["elapsed_s"] = round(time.time() - t0, 3)
    now = time.time()
    if rec.get("last_success_epoch"):
        rec["success_age_s"] = round(now - float(rec["last_success_epoch"]), 1)
        rec["off_volume_copy_exists"] = True
    else:
        rec["success_age_s"] = None
        rec["off_volume_copy_exists"] = False
    hb_path = paths.logs(HEARTBEAT_NAME)
    out = write_heartbeat(hb_path, rec)
    out["heartbeat_path"] = str(hb_path)
    return out


def preflight(paths: CosmosPaths, config_path: Path,
              source: Path | None = None) -> dict:
    """Configured vs missing. Creates nothing, writes no heartbeat."""
    out: dict = {
        "schema": SCHEMA, "status": "BLOCKED", "kind": None,
        "config_present": Path(config_path).is_file(),
        "dest_named": False, "source_named": False,
        "adapter_implemented": True,
        "task_registered": _task_registered(),
        "heartbeat_written": False,
        "task": TASK_NAME, "heartbeat": HEARTBEAT_NAME,
    }
    try:
        cfg = mounts.load_config(Path(config_path))
        spec = local_row(cfg)
        out["dest_named"] = True
        src = source if source is not None else spec["source"]
        if src is None:
            raise BackupRefusal("NO_SOURCE", "targets.local.source is empty")
        out["source_named"] = True
        out["status"] = "READY"
        out["kind"] = "READY"
        out["dest"] = str(spec["dest"])
        out["source"] = str(src)
    except BackupRefusal as e:
        out["kind"] = e.kind
        out["detail"] = e.detail
        out["status"] = "BLOCKED"
    return out


def selfcheck(paths: CosmosPaths) -> dict:
    """Drive the REAL tick against FakeProbe + a scratch dest. Zero mounts."""
    stamp = _stamp()
    dest = paths.role("work", SELFCHECK_STAGE, stamp, "dest")
    src = paths.role("work", SELFCHECK_STAGE, stamp, "src")
    dest.mkdir(parents=True, exist_ok=True)
    src.mkdir(parents=True, exist_ok=True)
    (src / "hello.txt").write_text("selfcheck\n", encoding="utf-8", newline="\n")
    probe = mounts.FakeProbe(volumes={
        str(src): "vol:SELFCHECK-SRC",
        str(src.resolve()): "vol:SELFCHECK-SRC",
        str(dest): "vol:SELFCHECK-DST",
        str(dest.resolve()): "vol:SELFCHECK-DST",
    })
    return tick(paths, Path("<selfcheck — no config read>"),
                source=src, dest=dest, probe=probe, force=True)


def _pythonw() -> str:
    cand = Path(sys.executable).with_name("pythonw.exe")
    return str(cand) if cand.exists() else sys.executable


def plan_task_argv(root: Path, at: str = DEFAULT_AT) -> list[str]:
    """schtasks /create plan. Current user, no /rl highest. Registers nothing.

    Daily 04:00 — after R2 02:30, mount 03:00, state 03:15 so four dest-waiting
    refusals do not collide on the same minute.
    """
    tr = subprocess.list2cmdline([_pythonw(), str(Path(__file__).resolve()),
                                  "--root", str(root), "--once"])
    return ["schtasks", "/create", "/tn", TASK_NAME, "/tr", tr,
            "/sc", "daily", "/st", at, "/f"]


def install_task(root: Path, at: str = DEFAULT_AT) -> dict:
    """Register the clock. A nonzero rc is REPORTED, never swallowed."""
    argv = plan_task_argv(root, at)
    try:
        p = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=60, creationflags=NO_WINDOW)
    except OSError as e:
        return {"ok": False, "rc": -1, "argv": argv, "out": str(e)}
    return {"ok": p.returncode == 0, "rc": p.returncode, "argv": argv,
            "out": ((p.stdout or "") + (p.stderr or "")).strip()}


def _task_registered() -> bool | None:
    """None means UNMEASURED — schtasks may be denied. Never guessed as False."""
    try:
        p = subprocess.run(["schtasks", "/query", "/tn", TASK_NAME], capture_output=True,
                           text=True, timeout=30, creationflags=NO_WINDOW)
    except OSError:
        return None
    return p.returncode == 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", required=True)
    ap.add_argument("--source", help="override targets.local.source (absolute)")
    ap.add_argument("--at", default=DEFAULT_AT, help="schtasks daily start time")
    ap.add_argument("--force", action="store_true", help="run even when PAUSEd")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--preflight", action="store_true",
                   help="configured vs missing; creates nothing, no heartbeat")
    g.add_argument("--selfcheck", action="store_true")
    g.add_argument("--once", action="store_true")
    g.add_argument("--plan-task", action="store_true",
                   help="print the schtasks argv, register nothing")
    g.add_argument("--install-task", action="store_true")
    a = ap.parse_args(argv)

    try:
        paths = CosmosPaths(a.root)
    except CosmosPathError as e:
        print(json.dumps({"refused": True, "kind": e.kind, "detail": str(e)}),
              file=sys.stderr)
        return 2

    if a.plan_task:
        print(json.dumps({"task": TASK_NAME, "argv": plan_task_argv(Path(a.root), a.at),
                          "stale_s": STALE_S, "heartbeat": HEARTBEAT_NAME,
                          "registers": False}, indent=1))
        return 0
    if a.install_task:
        rec = install_task(Path(a.root), a.at)
        print(json.dumps(rec, indent=1))
        return 0 if rec["ok"] else 1

    cfg = paths.config(CONFIG_NAME)
    src = Path(a.source) if a.source else None

    if a.preflight:
        out = preflight(paths, cfg, source=src)
        print(json.dumps(out, indent=2, sort_keys=True, default=str))
        return 0 if out["status"] == "READY" else 2

    rec = selfcheck(paths) if a.selfcheck else tick(
        paths, cfg, source=src, force=a.force)
    print(json.dumps(rec, indent=1, default=str))
    if rec.get("ok"):
        return 0
    return 2 if rec.get("state") == "REFUSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
