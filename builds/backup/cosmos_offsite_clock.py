#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""cosmos_offsite_clock - the SCHEDULED offsite push (F-47), and its refusal.

WHY THIS EXISTS. `docs/FEATURE_MASTER.md` ranks F-46 + F-47 + F-54 as the only route
to a backup whose failure is uncorrelated with this drive - the WISHLIST clause
"survives total tree DELETION". F-45 built and proved the R2 adapter; what was
measured MISSING was two things:

    F-46  the credential  -> Keith's door, and it is NOT opened here
    F-47  "none - nothing registers an R2 push with schtasks"

This module is F-47. Every local backup COSMOS takes today lands in
`live\backups\...` on `V:` - the same physical volume as the source it protects.
This one runs on the Windows clock, pushes to R2, reads every object back, re-hashes
it, and heartbeats the result where the health watchdog already looks.

WHAT IT DOES WITHOUT THE CREDENTIAL - which is the whole point of shipping it now:

    It REFUSES, typed and clean, and it heartbeats the refusal. `NO_CREDENTIALS` is a
    BackupRefusal from `cosmos_backup_r2.load_credentials`, not a traceback and not a
    silent skip. The scheduled task can therefore be armed TODAY: it will refuse
    every night, visibly, on the board, and the night the credential lands it starts
    working with no code change and no second decision. A blocked feature that is
    wired and refusing is worth more than an unblocked feature that is not wired.

TWO CLOCKS IN ONE HEARTBEAT, because they answer different questions:

    last_run_epoch      is the CLOCK alive?     (the watchdog's staleness check)
    last_success_epoch  is the DATA protected?  (carried forward across ticks)

A clock that ticks nightly and refuses nightly is alive and protecting nothing. One
timestamp cannot say both, so the heartbeat carries both and `success_age_s` is the
number that means "how old is the newest copy that is not on this drive".

CREDENTIAL FENCE, inherited and re-stated: `D:\R2Cloner` holds key material in
plaintext. Nothing here reads, opens, lists or resolves into it -
`cosmos_backup_r2.guard_credential_path` refuses that prefix before touching the
filesystem. No key value is read, printed, logged or written to any artifact by this
module; the heartbeat and receipts carry a last-4 fingerprint of the PUBLIC access
key id and nothing else.

NEVER DELETES. The read-back scratch is born inside a staging directory
(`work/_delme_offsite_readback/<scope>-<stamp>`) rather than being cleaned up, so
Keith deletes at his leisure and the heartbeat reports the total staged bytes. R2
retention/lifecycle is a bucket policy Keith owns; this clock never issues a DELETE
and holds no credential scope to do so.

Canon honored: no hard-coded paths (the runtime root is a parameter, resolved by
`cosmos_paths` and verified by sentinel CONTENT); fail-closed (an unreadable PAUSE
flag means paused); the Windows clock carries the overhead, never Claude; rc reflects
the GATE, not the daemon.

    py -3.14 builds/backup/cosmos_offsite_clock.py --root V:\A\Ai\COSMOS\live --preflight
    py -3.14 builds/backup/cosmos_offsite_clock.py --root V:\A\Ai\COSMOS\live --selfcheck
    py -3.14 builds/backup/cosmos_offsite_clock.py --root V:\A\Ai\COSMOS\live --once
    py -3.14 builds/backup/cosmos_offsite_clock.py --root V:\A\Ai\COSMOS\live --plan-task
    py -3.14 builds/backup/cosmos_offsite_clock.py --root V:\A\Ai\COSMOS\live --install-task
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
import cosmos_backup_r2 as r2                   # noqa: E402
from cosmos_backup import BackupRefusal         # noqa: E402


def _load_cosmos_paths():
    r"""Load `cosmos/cosmos_paths.py` BY PATH, never by putting `cosmos/` on sys.path.

    THE COLLISION THIS AVOIDS, measured 2026-08-31 on the live root: `cosmos/` and
    `builds/backup/` BOTH contain a module named `cosmos_backup`, and they are
    different modules (the header of each says so). Adding `cosmos/` to sys.path made
    `import cosmos_backup` resolve to the core one and the clock died at import:

        ImportError: cannot import name 'BackupRefusal' from 'cosmos_backup'
                     (V:\A\Ai\COSMOS\cosmos\cosmos_backup.py)

    The suite did NOT catch it - a test process imports `cosmos_backup` first, so the
    right module is already in sys.modules and the shadow never fires. Only running
    the real command against the real root did. That is runtime binding, and it is
    why `test_offsite_clock` now runs the CLI in a SUBPROCESS.

    Importing one file is also the smaller claim: this module needs the resolver, not
    the whole of `cosmos/`.
    """
    import importlib.util
    p = _HERE.parents[1] / "cosmos" / "cosmos_paths.py"
    spec = importlib.util.spec_from_file_location("cosmos_paths_for_offsite", p)
    if spec is None or spec.loader is None:                       # pragma: no cover
        raise ImportError(f"cannot load the path resolver from {p}")
    mod = importlib.util.module_from_spec(spec)
    # Registered BEFORE exec: @dataclass resolves its own class's __module__ through
    # sys.modules, and a module absent from it raises AttributeError mid-decoration.
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


_paths_mod = _load_cosmos_paths()
CosmosPaths = _paths_mod.CosmosPaths
CosmosPathError = _paths_mod.CosmosPathError

SCHEMA = "cosmos-offsite-clock/1"
WORKER = "cosmos-offsite-clock"
HEARTBEAT_NAME = "offsite_clock_heartbeat.json"
SCOPES_NAME = "offsite_scopes.json"
CREDENTIALS_NAME = "r2_credentials.json"
RECEIPTS_DIR = "offsite"
READBACK_STAGE = "_delme_offsite_readback"
TASK_NAME = "COSMOS Offsite Push"
DEFAULT_AT = "02:30"

NO_WINDOW = 0x08000000 if os.name == "nt" else 0

# Scheduled daily, so anything past ~26h means the push stopped happening. Slack is
# deliberately generous: a 65 GiB first push is long, and a watchdog that cries wolf
# is how a real stall gets ignored (the discover_unwatched scar).
STALE_S = 26 * 3600.0


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")


# ---------------------------------------------------------------- scopes

def load_scopes(path: Path) -> list[dict]:
    r"""Read the scope list. A scope is {name, source, excludes?}.

    REFUSES rather than inventing a default source tree. "Back up something
    plausible" is how a backup ends up covering the wrong thing while reporting
    success - the scope is the operator's declaration, not this module's guess.
    """
    p = Path(path)
    if not p.is_file():
        raise BackupRefusal("NO_SCOPES", f"no scope declaration at {p} — write it "
                                         '{"scopes":[{"name":…,"source":…}]} '
                                         "(no source tree is ever guessed)")
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise BackupRefusal("BAD_SCOPES", f"{p} is not readable JSON: {type(e).__name__}") from e
    scopes = obj.get("scopes") if isinstance(obj, dict) else obj
    if not isinstance(scopes, list) or not scopes:
        raise BackupRefusal("BAD_SCOPES", f"{p} declares no scopes")
    out = []
    for i, s in enumerate(scopes):
        if not isinstance(s, dict) or not s.get("name") or not s.get("source"):
            raise BackupRefusal("BAD_SCOPES", f"{p} scope #{i} needs both 'name' and 'source'")
        extra = s.get("excludes")
        if extra is None:
            excludes = (".git", "__pycache__")
        elif (isinstance(extra, (str, bytes))
              or not isinstance(extra, (list, tuple))
              or not all(isinstance(x, str) and x.strip() for x in extra)):
            # A string iterates as characters (`excludes: "git"` → 'g','i','t')
            # — the green-log. Bite `_bite_unpinned_round8.json`.
            raise BackupRefusal(
                "BAD_SCOPES",
                f"{p} scope #{i} excludes must be a list of non-empty strings")
        else:
            excludes = tuple(extra)
        out.append({"name": r2.safe_rel(str(s["name"])),
                    "source": str(s["source"]),
                    "excludes": excludes})
    return out


def scopes_from_argv(sources: list[str] | None) -> list[dict]:
    """`--source <path>` repeated. The scheduled task uses the file; this is for
    a one-off push and for tests, and it is the SAME code path afterwards."""
    return [{"name": r2.safe_rel(Path(s).resolve().name), "source": s,
             "excludes": (".git", "__pycache__")} for s in (sources or [])]


# ---------------------------------------------------------------- control / heartbeat

def paused(paths: CosmosPaths) -> bool:
    """Unreadable control flag = fail-closed: treat as paused, do not push."""
    flag = paths.role("state", "control", "PAUSE.flag")
    try:
        raw = flag.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False
    except OSError:
        return True
    try:
        obj = json.loads(raw or "{}")
    except ValueError:
        return True
    # Valid JSON of the wrong shape (array/true/number/string/null) is
    # unreadable as a flag — fail-closed paused, never AttributeError.
    # Bite `_bite_unpinned_round8.json`.
    if not isinstance(obj, dict):
        return True
    return str(obj.get("state", "PAUSED")).upper() != "RUNNING"


def read_heartbeat(path: Path) -> dict:
    """A non-object heartbeat is the same as unreadable: empty dict.

    json.loads('[]') / 'true' / '1' succeed, then tick AttributeErrors
    on .get. Bite `_bite_unpinned_round8.json`.
    """
    try:
        obj = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return obj if isinstance(obj, dict) else {}


def write_heartbeat(path: Path, rec: dict) -> dict:
    """Written on EVERY tick — pass, refusal or pause. A tick that writes nothing
    is indistinguishable from a dead clock, which is the failure this file exists
    to make visible."""
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
                    "last_success_epoch = is the DATA protected off-machine. "
                    "state=REFUSED with kind=NO_CREDENTIALS means the push is wired "
                    "and waiting on the credential — see docs/OFFSITE_READY.md."),
    })
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(body, indent=1, default=str), encoding="utf-8")
    os.replace(tmp, path)
    return body


# ---------------------------------------------------------------- the tick

def tick(paths: CosmosPaths, scopes: list[dict], credentials: Path,
         transport_factory=None, credentials_override=None, force: bool = False) -> dict:
    """One offsite cycle. Returns the heartbeat record; NEVER raises for a refusal.

    `transport_factory` and `credentials_override` are injection seams, not test
    conveniences: `--selfcheck` drives THIS function with a MemoryTransport, so the
    scheduled path is what gets proven offline rather than a parallel imitation of it.
    """
    t0 = time.time()
    prev = read_heartbeat(paths.logs(HEARTBEAT_NAME))
    rec: dict = {"schema": SCHEMA, "ts": _utcnow(), "tick": "once",
                 "scopes_declared": [s["name"] for s in scopes],
                 "credentials_path": str(credentials)}
    # Carry the protection clock forward: a refusal must not erase the memory of
    # the last real success, and it must not fake one either.
    for k in ("last_success_epoch", "last_success_utc", "last_success_scopes"):
        if prev.get(k) is not None:
            rec[k] = prev[k]

    if not force and paused(paths):
        rec.update({"ok": True, "state": "PAUSED",
                    "detail": "state/control/PAUSE.flag is not RUNNING"})
        return _finish(paths, rec, t0)

    try:
        creds = (credentials_override if credentials_override is not None
                 else r2.load_credentials(Path(credentials)))
        if not scopes:
            raise BackupRefusal("NO_SCOPES", "no scope declared and none given on the "
                                             "command line — nothing to push")
    except BackupRefusal as e:
        # THE refusal this module ships for. Typed, quiet, heartbeated, rc=2.
        rec.update({"ok": False, "state": "REFUSED", "kind": e.kind, "detail": e.detail,
                    "unblocks": ("place the credential, then this same task pushes "
                                 "with no code change — docs/OFFSITE_READY.md")
                                if e.kind in ("NO_CREDENTIALS", "BAD_CREDENTIALS") else None})
        return _finish(paths, rec, t0)

    stamp = _stamp()
    made = transport_factory or (lambda: r2.UrllibTransport())
    results, pushed_bytes, staged_bytes, failures = [], 0, 0, 0
    for scope in scopes:
        prefix = f"{scope['name']}/{stamp}"
        scratch = paths.role("work", READBACK_STAGE, f"{scope['name']}-{stamp}")
        row = {"scope": scope["name"], "source": scope["source"], "prefix": prefix,
               "readback_scratch": str(scratch)}
        try:
            target = r2.R2Target(creds, prefix, made())
            receipt = r2.push(Path(scope["source"]), target,
                              excludes=tuple(scope["excludes"]), scratch=scratch)
            row.update({"ok": True, "state": "PUSHED",
                        "files_pushed": receipt["files_pushed"],
                        "bytes_pushed": receipt["bytes_pushed"],
                        "readback_verified": receipt["readback_verified"],
                        "manifest_seal_sha256": receipt["manifest_seal_sha256"],
                        "receipt": str(write_receipt(paths, scope["name"], stamp, receipt))})
            pushed_bytes += int(receipt["bytes_pushed"])
            staged_bytes += int(receipt["bytes_pushed"])
        except BackupRefusal as e:
            # One scope refusing must not silently cancel the others, and must not
            # be summarised away: the kind and the scope both reach the board.
            row.update({"ok": False, "state": "REFUSED", "kind": e.kind, "detail": e.detail})
            failures += 1
        except Exception as e:                                        # noqa: BLE001
            row.update({"ok": False, "state": "CRASHED",
                        "kind": type(e).__name__, "detail": str(e)[:400]})
            failures += 1
        results.append(row)

    ok = failures == 0
    rec.update({"ok": ok, "state": "PUSHED" if ok else "PARTIAL" if pushed_bytes else "FAILED",
                "credential": creds.asdict(), "prefix_stamp": stamp,
                "scopes": results, "bytes_pushed": pushed_bytes,
                "readback_staged_bytes": staged_bytes, "failures": failures})
    if ok:
        rec.update({"last_success_epoch": int(time.time()), "last_success_utc": _utcnow(),
                    "last_success_scopes": [s["name"] for s in scopes]})
    return _finish(paths, rec, t0)


def _finish(paths: CosmosPaths, rec: dict, t0: float) -> dict:
    rec["elapsed_s"] = round(time.time() - t0, 3)
    now = time.time()
    if rec.get("last_success_epoch"):
        rec["success_age_s"] = round(now - float(rec["last_success_epoch"]), 1)
        rec["offsite_copy_exists"] = True
    else:
        # Never guessed, never rendered as fresh. No push has ever succeeded.
        rec["success_age_s"] = None
        rec["offsite_copy_exists"] = False
    hb_path = paths.logs(HEARTBEAT_NAME)
    out = write_heartbeat(hb_path, rec)
    out["heartbeat_path"] = str(hb_path)
    return out


def write_receipt(paths: CosmosPaths, scope: str, stamp: str, receipt: dict) -> Path:
    """The sealed R2_PUSH_OK receipt, kept on THIS machine too.

    The receipt in the bucket proves the push to anyone holding the bucket; the copy
    here proves it to the operator who has just lost the bucket's contents and needs
    to know what should be in it.
    """
    d = paths.logs(RECEIPTS_DIR)
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{scope}-{stamp}.json"
    p.write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")
    return p


# ---------------------------------------------------------------- selfcheck

def selfcheck(paths: CosmosPaths, scopes: list[dict]) -> dict:
    """Drive the REAL tick against an in-memory bucket with an obviously-fake
    credential. Proves the whole scheduled path — scope load, push, read-back,
    re-hash, receipt, heartbeat — with zero credentials and zero network."""
    creds = r2.R2Credentials("selfcheckaccount", r2.SELFCHECK_ID, r2.SELFCHECK_ID,
                             "selfcheck-bucket")
    return tick(paths, scopes, Path("<selfcheck — no credential read>"),
                transport_factory=r2.MemoryTransport,
                credentials_override=creds, force=True)


# ---------------------------------------------------------------- schtasks

def _pythonw() -> str:
    cand = Path(sys.executable).with_name("pythonw.exe")
    return str(cand) if cand.exists() else sys.executable


def plan_task_argv(root: Path, at: str = DEFAULT_AT) -> list[str]:
    """schtasks /create plan. Current user, no /rl highest — pushing a backup needs
    no elevation, and asking for it would be capability this does not need."""
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


# ---------------------------------------------------------------- CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", required=True, help="COSMOS runtime root (holds .cosmos-root.json)")
    ap.add_argument("--scopes", help=f"scope declaration (default: <config>/{SCOPES_NAME})")
    ap.add_argument("--source", action="append", help="push this tree instead of the scope file")
    ap.add_argument("--credentials", help=f"credential file (default: <config>/{CREDENTIALS_NAME})")
    ap.add_argument("--at", default=DEFAULT_AT, help="schtasks daily start time")
    ap.add_argument("--force", action="store_true", help="run even when PAUSEd")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--once", action="store_true")
    g.add_argument("--preflight", action="store_true", help="configured vs missing; no network")
    g.add_argument("--selfcheck", action="store_true", help="prove the path offline")
    g.add_argument("--plan-task", action="store_true", help="print the schtasks argv, register nothing")
    g.add_argument("--install-task", action="store_true")
    a = ap.parse_args(argv)

    try:
        paths = CosmosPaths(a.root)
    except CosmosPathError as e:
        print(json.dumps({"refused": True, "kind": e.kind, "detail": str(e)}), file=sys.stderr)
        return 2

    creds_path = Path(a.credentials) if a.credentials else paths.config(CREDENTIALS_NAME)
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
        return scopes_from_argv(a.source) if a.source else load_scopes(scopes_path)

    if a.preflight:
        try:
            scopes = _scopes()
        except BackupRefusal as e:
            scopes = []
            print(json.dumps({"scopes_refused": {"kind": e.kind, "detail": e.detail}}),
                  file=sys.stderr)
        out = {"schema": SCHEMA, "task": TASK_NAME,
               "task_registered": _task_registered(),
               "scopes_path": str(scopes_path), "scopes": [s["name"] for s in scopes],
               "heartbeat": str(paths.logs(HEARTBEAT_NAME)),
               "adapter": r2.preflight(Path(scopes[0]["source"]) if scopes else None,
                                       creds_path)}
        out["status"] = "READY" if (scopes and out["adapter"]["status"] == "READY") else "BLOCKED"
        print(json.dumps(out, indent=2, sort_keys=True))
        return 0 if out["status"] == "READY" else 2

    try:
        scopes = _scopes()
    except BackupRefusal as e:
        rec = _finish(paths, {"schema": SCHEMA, "ts": _utcnow(), "ok": False,
                              "state": "REFUSED", "kind": e.kind, "detail": e.detail}, time.time())
        print(json.dumps(rec, indent=1, default=str))
        return 2

    rec = selfcheck(paths, scopes) if a.selfcheck else tick(
        paths, scopes, creds_path, force=a.force)
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
