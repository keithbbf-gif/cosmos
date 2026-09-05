#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""cosmos_mount_clock - the SCHEDULED GDX/ODX/ES.3 + R2 push (F-48 clock).

WHY THIS EXISTS. F-47 scheduled the R2 adapter as a sibling clock
(`cosmos_offsite_clock.py`, 02:30). F-48 built the path-mount adapters
(`cosmos_backup_mounts.py`) and this 03:00 vehicle. The nightly
"COSMOS Mount Offsite Push" now ALSO pushes to R2: one scheduled task,
four targets. R2 is a separate adapter (`cosmos_backup_r2.py`); a missing
credential is typed `NO_CREDENTIALS` on the r2 target row, never a silent
skip and never a traceback. GDX/ODX/ES.3 still come from backup_targets.json.

WHAT IT DOES WITHOUT DESTS NAMED — which is the whole point of shipping it now:

    It REFUSES, typed and clean, and it heartbeats the refusal. `NO_CONFIG` is a
    BackupRefusal from `cosmos_backup_mounts.load_config`, not a traceback and
    not a silent skip. The scheduled task can be armed TODAY: it will refuse
    every night, visibly, on the board, and the night Keith copies
    `backup_targets.example.json` to the config role and fills each `dest`, it
    starts working with no code change and no second decision.

TWO CLOCKS IN ONE HEARTBEAT (same split as the R2 sibling):

    last_run_epoch      is the CLOCK alive?
    last_success_epoch  is the DATA protected off this volume?

A dest is NEVER invented. Existence of `X:\` or OneDrive is not a dest (the
empty-dir scar). Tests and `--selfcheck` inject FakeProbe + a scratch dest so
nothing in this module can write to DriveFS or OneDrive by accident.

NEVER DELETES. Selfcheck dests are born under `work/_delme_mount_selfcheck/`.
Keith deletes at his leisure.

Canon honored: no hard-coded dest paths; fail-closed (unreadable PAUSE = paused);
the Windows clock carries the overhead; rc reflects the GATE.

    py -3.14 builds/backup/cosmos_mount_clock.py --root V:\A\Ai\COSMOS\live --preflight
    py -3.14 builds/backup/cosmos_mount_clock.py --root V:\A\Ai\COSMOS\live --selfcheck --source <tree>
    py -3.14 builds/backup/cosmos_mount_clock.py --root V:\A\Ai\COSMOS\live --once
    py -3.14 builds/backup/cosmos_mount_clock.py --root V:\A\Ai\COSMOS\live --plan-task
    py -3.14 builds/backup/cosmos_mount_clock.py --root V:\A\Ai\COSMOS\live --install-task
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
import cosmos_backup_r2 as r2                   # noqa: E402
import cosmos_offsite_clock as oc               # noqa: E402
from cosmos_backup import BackupRefusal         # noqa: E402

# Resolver comes from the R2 sibling so `cosmos/` never lands on sys.path
# (the two-module-named-cosmos_backup collision, measured 2026-08-31).
CosmosPaths = oc.CosmosPaths
CosmosPathError = oc.CosmosPathError

SCHEMA = "cosmos-mount-clock/1"
WORKER = "cosmos-mount-clock"
HEARTBEAT_NAME = "mount_clock_heartbeat.json"
CONFIG_NAME = mounts.CONFIG_NAME
SCOPES_NAME = oc.SCOPES_NAME
CREDENTIALS_NAME = oc.CREDENTIALS_NAME
RECEIPTS_DIR = "mount"
SELFCHECK_STAGE = "_delme_mount_selfcheck"
R2_READBACK_STAGE = "_delme_mount_r2_readback"
TASK_NAME = "COSMOS Mount Offsite Push"
DEFAULT_AT = "03:00"
KINDS = mounts.KINDS

NO_WINDOW = 0x08000000 if os.name == "nt" else 0
STALE_S = 26 * 3600.0


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
                    "last_success_epoch = is the DATA protected off this volume. "
                    "state=REFUSED with kind=NO_CONFIG means the push is wired "
                    "and waiting on backup_targets.json dests. "
                    "target_kind=r2 state=REFUSED kind=NO_CREDENTIALS means "
                    "the R2 leg is wired and waiting on r2_credentials.json."),
    })
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(body, indent=1, default=str), encoding="utf-8")
    os.replace(tmp, path)
    return body


def write_receipt(paths: CosmosPaths, kind: str, scope: str, stamp: str,
                  receipt: dict) -> Path:
    d = paths.logs(RECEIPTS_DIR)
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{kind}-{scope}-{stamp}.json"
    p.write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")
    return p


def tick(paths: CosmosPaths, scopes: list[dict], config_path: Path,
         *, probe=None, dests: dict | None = None, kinds: tuple[str, ...] | None = None,
         force: bool = False,
         r2_credentials: Path | None = None,
         r2_transport_factory=None,
         r2_credentials_override=None) -> dict:
    """One mount-offsite cycle. Returns the heartbeat record; NEVER raises for a refusal.

    `probe` and `dests` are injection seams, not test conveniences: `--selfcheck`
    drives THIS function with FakeProbe + a scratch dest, so the scheduled path
    is what gets proven offline rather than a parallel imitation of it.

    A dest is never invented. `dests is None` means read `backup_targets.json`.
    Missing file is NO_CONFIG. Empty dest rows are NO_DEST per kind.

    R2 is a separate adapter. The scheduled path (`dests is None`) ALWAYS
    appends an r2 target row per scope: PUSHED on a live credential, or
    REFUSED typed `NO_CREDENTIALS` if the file is absent. Injected dests
    (selfcheck / hermetic mount tests) skip R2 unless
    `r2_transport_factory` / `r2_credentials_override` is passed, so a
    fixture that only names a GDX scratch dest cannot reach the wire.
    No credential value is copied into the heartbeat; the receipt uses
    `R2Credentials.asdict()` (secret redacted).
    """
    t0 = time.time()
    prev = read_heartbeat(paths.logs(HEARTBEAT_NAME))
    want = (tuple(kinds) if kinds is not None
            else (tuple(dests) if dests is not None else KINDS))
    rec: dict = {"schema": SCHEMA, "ts": _utcnow(), "tick": "once",
                 "scopes_declared": [s["name"] for s in scopes],
                 "config_path": str(config_path),
                 "kinds": list(want)}
    for k in ("last_success_epoch", "last_success_utc", "last_success_scopes"):
        if prev.get(k) is not None:
            rec[k] = prev[k]

    if not force and oc.paused(paths):
        rec.update({"ok": True, "state": "PAUSED",
                    "detail": "state/control/PAUSE.flag is not RUNNING"})
        return _finish(paths, rec, t0)

    try:
        if dests is None:
            mounts.load_config(Path(config_path))
        if not scopes:
            raise BackupRefusal("NO_SCOPES", "no scope declared and none given on the "
                                             "command line — nothing to push")
    except BackupRefusal as e:
        rec.update({"ok": False, "state": "REFUSED", "kind": e.kind, "detail": e.detail,
                    "unblocks": ("place backup_targets.json with absolute dests, "
                                 "then this same task pushes with no code change")
                                if e.kind in ("NO_CONFIG", "NO_DEST", "BAD_CONFIG") else None})
        return _finish(paths, rec, t0)

    stamp = _stamp()
    results, pushed_bytes, failures = [], 0, 0
    for kind in want:
        dest_arg = Path(dests[kind]) if dests is not None and kind in dests else None
        if dests is not None and dest_arg is None:
            continue
        for scope in scopes:
            row = {"target_kind": kind, "scope": scope["name"],
                   "source": scope["source"]}
            try:
                receipt = mounts.push(
                    Path(scope["source"]), kind,
                    dest=dest_arg,
                    config_path=None if dests is not None else Path(config_path),
                    probe=probe,
                    excludes=tuple(scope.get("excludes") or cb.DEFAULT_EXCLUDES),
                )
                row.update({"ok": True, "state": "PUSHED",
                            "dest": receipt.get("dest"),
                            "files_pushed": receipt["files_pushed"],
                            "bytes_pushed": receipt["bytes_pushed"],
                            "set_dir": receipt.get("set_dir"),
                            "receipt": str(write_receipt(
                                paths, kind, scope["name"], stamp, receipt))})
                pushed_bytes += int(receipt["bytes_pushed"])
            except BackupRefusal as e:
                row.update({"ok": False, "state": "REFUSED", "kind": e.kind,
                            "detail": e.detail})
                failures += 1
            except Exception as e:                                    # noqa: BLE001
                row.update({"ok": False, "state": "CRASHED",
                            "kind": type(e).__name__, "detail": str(e)[:400]})
                failures += 1
            results.append(row)

    r2_wanted = (
        r2_transport_factory is not None
        or r2_credentials_override is not None
        or r2_credentials is not None
        or dests is None
    )
    if r2_wanted and scopes:
        creds_obj = None
        creds_err = None
        try:
            if r2_credentials_override is not None:
                creds_obj = r2_credentials_override
            else:
                cred_path = (Path(r2_credentials) if r2_credentials is not None
                             else paths.config(CREDENTIALS_NAME))
                creds_obj = r2.load_credentials(cred_path)
        except BackupRefusal as e:
            creds_err = e
        made = r2_transport_factory or (lambda: r2.UrllibTransport())
        for scope in scopes:
            row = {"target_kind": "r2", "scope": scope["name"],
                   "source": scope["source"]}
            if creds_err is not None:
                row.update({"ok": False, "state": "REFUSED",
                            "kind": creds_err.kind, "detail": creds_err.detail,
                            "unblocks": ("place r2_credentials.json; this same "
                                         "nightly task then pushes with no "
                                         "code change")
                            if creds_err.kind in ("NO_CREDENTIALS",
                                                  "BAD_CREDENTIALS") else None})
                failures += 1
                results.append(row)
                continue
            prefix = f"{scope['name']}/{stamp}"
            scratch = paths.role("work", R2_READBACK_STAGE,
                                 f"{scope['name']}-{stamp}")
            row["readback_scratch"] = str(scratch)
            try:
                target = r2.R2Target(creds_obj, prefix, made())
                receipt = r2.push(
                    Path(scope["source"]), target,
                    excludes=tuple(scope.get("excludes") or cb.DEFAULT_EXCLUDES),
                    scratch=scratch)
                row.update({"ok": True, "state": "PUSHED",
                            "files_pushed": receipt["files_pushed"],
                            "bytes_pushed": receipt["bytes_pushed"],
                            "readback_verified": receipt["readback_verified"],
                            "prefix": prefix,
                            "bucket": creds_obj.bucket,
                            "receipt": str(write_receipt(
                                paths, "r2", scope["name"], stamp, receipt))})
                pushed_bytes += int(receipt["bytes_pushed"])
            except BackupRefusal as e:
                row.update({"ok": False, "state": "REFUSED",
                            "kind": e.kind, "detail": e.detail})
                failures += 1
            except Exception as e:                                    # noqa: BLE001
                row.update({"ok": False, "state": "CRASHED",
                            "kind": type(e).__name__, "detail": str(e)[:400]})
                failures += 1
            results.append(row)

    ok = failures == 0 and bool(results)
    if not results:
        rec.update({"ok": False, "state": "REFUSED", "kind": "NO_DEST",
                    "detail": "no kind had a dest (injected dests empty and no config rows)",
                    "unblocks": "name dests in backup_targets.json"})
        return _finish(paths, rec, t0)
    rec.update({"ok": ok,
                "state": "PUSHED" if ok else ("PARTIAL" if pushed_bytes else "FAILED"),
                "prefix_stamp": stamp, "targets": results,
                "bytes_pushed": pushed_bytes, "failures": failures})
    # last_success answers "did any copy leave this volume?", not "did every
    # named kind succeed". ODX is SKIPPED and ES.3 waits on hardware, so a
    # nightly tick is PARTIAL forever; refusing to stamp last_success while
    # gdx/r2 actually PUSHED would make the heartbeat look unprotected.
    if any(r.get("state") == "PUSHED" for r in results):
        rec.update({"last_success_epoch": int(time.time()), "last_success_utc": _utcnow(),
                    "last_success_scopes": [s["name"] for s in scopes
                                            if any(r.get("scope") == s["name"]
                                                   and r.get("state") == "PUSHED"
                                                   for r in results)]})
    # If every row refused with the same kind, surface it at the top so the
    # board names the operator action (NO_DEST / DRIVE_NOT_MOUNTED / SAME_VOLUME).
    if not ok and not pushed_bytes:
        kinds_seen = {r.get("kind") for r in results if r.get("state") == "REFUSED"}
        if len(kinds_seen) == 1:
            rec["kind"] = next(iter(kinds_seen))
            rec["state"] = "REFUSED"
    return _finish(paths, rec, t0)


def _finish(paths: CosmosPaths, rec: dict, t0: float) -> dict:
    rec["elapsed_s"] = round(time.time() - t0, 3)
    now = time.time()
    if rec.get("last_success_epoch"):
        rec["success_age_s"] = round(now - float(rec["last_success_epoch"]), 1)
        rec["offsite_copy_exists"] = True
    else:
        rec["success_age_s"] = None
        rec["offsite_copy_exists"] = False
    hb_path = paths.logs(HEARTBEAT_NAME)
    out = write_heartbeat(hb_path, rec)
    out["heartbeat_path"] = str(hb_path)
    return out


def selfcheck(paths: CosmosPaths, scopes: list[dict]) -> dict:
    """Drive the REAL tick against FakeProbe + a scratch dest.

    Dest is born under work/_delme_mount_selfcheck (never deleted). FakeProbe
    *declares* it a different volume so SAME_VOLUME does not fire. Nothing
    reaches a real DriveFS / OneDrive / ES.3 mount.
    """
    stamp = _stamp()
    dest = paths.role("work", SELFCHECK_STAGE, stamp, "dest")
    dest.mkdir(parents=True, exist_ok=True)
    volumes: dict[str, str] = {
        str(dest): "vol:SELFCHECK-GDX",
        str(dest.resolve()): "vol:SELFCHECK-GDX",
    }
    for s in scopes:
        src = Path(s["source"])
        volumes[str(src)] = "vol:SELFCHECK-SRC"
        try:
            volumes[str(src.resolve())] = "vol:SELFCHECK-SRC"
        except OSError:
            pass
    probe = mounts.FakeProbe(volumes=volumes)
    creds = r2.R2Credentials("selfcheckaccount", r2.SELFCHECK_ID, r2.SELFCHECK_ID,
                             "selfcheck-bucket")
    return tick(paths, scopes, Path("<selfcheck — no config read>"),
                probe=probe, dests={"gdx": dest}, force=True,
                r2_transport_factory=r2.MemoryTransport,
                r2_credentials_override=creds)


def _pythonw() -> str:
    cand = Path(sys.executable).with_name("pythonw.exe")
    return str(cand) if cand.exists() else sys.executable


def plan_task_argv(root: Path, at: str = DEFAULT_AT) -> list[str]:
    """schtasks /create plan. Current user, no /rl highest. Registers nothing."""
    tr = subprocess.list2cmdline([_pythonw(), str(Path(__file__).resolve()),
                                  "--root", str(root), "--once"])
    return ["schtasks", "/create", "/tn", TASK_NAME, "/tr", tr,
            "/sc", "daily", "/st", at, "/f"]


def install_task(root: Path, at: str = DEFAULT_AT) -> dict:
    argv = plan_task_argv(root, at)
    try:
        p = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=60, creationflags=NO_WINDOW)
    except OSError as e:
        return {"ok": False, "rc": -1, "argv": argv, "out": str(e)}
    return {"ok": p.returncode == 0, "rc": p.returncode, "argv": argv,
            "out": ((p.stdout or "") + (p.stderr or "")).strip()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", required=True,
                    help="COSMOS runtime root (holds .cosmos-root.json)")
    ap.add_argument("--scopes", help=f"scope declaration (default: <config>/{SCOPES_NAME})")
    ap.add_argument("--source", action="append",
                    help="push this tree instead of the scope file")
    ap.add_argument("--config", help=f"targets file (default: <config>/{CONFIG_NAME})")
    ap.add_argument("--at", default=DEFAULT_AT, help="schtasks daily start time")
    ap.add_argument("--force", action="store_true", help="run even when PAUSEd")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--once", action="store_true")
    g.add_argument("--preflight", action="store_true",
                   help="configured vs missing; no dest invented, no write")
    g.add_argument("--selfcheck", action="store_true",
                   help="prove the path offline against FakeProbe")
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

    config_path = Path(a.config) if a.config else paths.config(CONFIG_NAME)
    scopes_path = Path(a.scopes) if a.scopes else paths.config(SCOPES_NAME)

    if a.plan_task:
        print(json.dumps({"task": TASK_NAME, "argv": plan_task_argv(Path(a.root), a.at),
                          "stale_s": STALE_S, "heartbeat": HEARTBEAT_NAME}, indent=1))
        return 0
    if a.install_task:
        rec = install_task(Path(a.root), a.at)
        print(json.dumps(rec, indent=1))
        return 0 if rec["ok"] else 1

    def _scopes() -> list[dict]:
        return oc.scopes_from_argv(a.source) if a.source else oc.load_scopes(scopes_path)

    if a.preflight:
        try:
            scopes = _scopes()
        except BackupRefusal as e:
            scopes = []
            print(json.dumps({"scopes_refused": {"kind": e.kind, "detail": e.detail}}),
                  file=sys.stderr)
        adapter = mounts.preflight(config_path if config_path.is_file() else None,
                                   Path(scopes[0]["source"]) if scopes else None)
        cred_path = paths.config(CREDENTIALS_NAME)
        r2_state, r2_kind = "ABSENT", None
        if cred_path.is_file():
            try:
                r2.load_credentials(cred_path)
                r2_state, r2_kind = "PRESENT", "CREDENTIAL_PRESENT"
            except BackupRefusal as e:
                r2_state, r2_kind = e.kind, e.kind
        else:
            r2_kind = "NO_CREDENTIALS"
        out = {"schema": SCHEMA, "task": TASK_NAME,
               "task_registered": _task_registered(),
               "config_path": str(config_path),
               "config_present": config_path.is_file(),
               "scopes_path": str(scopes_path),
               "scopes": [s["name"] for s in scopes],
               "heartbeat": str(paths.logs(HEARTBEAT_NAME)),
               "adapter": adapter,
               "adapter_implemented": True,
               "r2_credentials_path": str(cred_path),
               "r2_credentials_present": cred_path.is_file(),
               "r2_state": r2_state,
               "r2_kind": r2_kind}
        out["status"] = "READY" if (scopes and adapter.get("status") == "READY") else "BLOCKED"
        print(json.dumps(out, indent=2, sort_keys=True))
        return 0 if out["status"] == "READY" else 2

    try:
        scopes = _scopes()
    except BackupRefusal as e:
        rec = _finish(paths, {"schema": SCHEMA, "ts": _utcnow(), "ok": False,
                              "state": "REFUSED", "kind": e.kind, "detail": e.detail},
                      time.time())
        print(json.dumps(rec, indent=1, default=str))
        return 2

    rec = selfcheck(paths, scopes) if a.selfcheck else tick(
        paths, scopes, config_path, force=a.force)
    print(json.dumps(rec, indent=1, default=str))
    if rec.get("ok"):
        return 0
    return 2 if rec.get("state") == "REFUSED" else 1


def _task_registered() -> bool | None:
    """None means UNMEASURED — schtasks may be denied. Never guessed as False."""
    try:
        p = subprocess.run(["schtasks", "/query", "/tn", TASK_NAME], capture_output=True,
                           text=True, timeout=30, creationflags=NO_WINDOW)
    except OSError:
        return None
    return p.returncode == 0


if __name__ == "__main__":
    raise SystemExit(main())
