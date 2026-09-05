#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""cosmos_state_offsite - F-54 payload through the F-47/F-48 adapters.

WHY THIS EXISTS. FEATURE_MASTER ranks F-46 + F-47 + F-54 as "get one copy off
this machine". The R2 clock (F-47) and the GDX/ODX/ES.3 clock (F-48) are built
and refuse typed when dest/credential are absent. What was still missing was
the *named payload*: the orchestrator carry-over that lets COSMOS resession
after total tree DELETION — SEED.json, SEED.decl.json, inflight.jsonl,
motif_tracker.json. Pushing `live/state/` wholesale would also ship mailboxes
and a pile of dispatch receipts; this module copies a whitelist into a staging
tree and then drives the EXISTING adapters.

WITHOUT dest AND without credential — which is the deliverable today:

    tick() REFUSES `NO_OFFSITE_ROUTE`, heartbeats the refusal, exits 2, and
    writes nothing to Drive / OneDrive / R2. Both blockers travel with it
    (`NO_CONFIG` and `NO_CREDENTIALS`). `--plan-task` emits
    `COSMOS State Offsite Push` daily 03:15 and registers nothing, so the
    task can be armed today and refuse visibly until dest/cred land. The
    night either route is named, the same tick starts pushing with no
    code change. F-47/F-48 clocks push *scopes*; this clock pushes the
    whitelist.

A dest is NEVER invented. `D:\R2Cloner` stays FORBIDDEN via the adapters.
The packed tree is secret-scanned; a planted install_key.bin is SECRETS_IN_SCOPE.
Never deletes: the pack lives under `work/_delme_state_offsite/<stamp>/`.

    py -3.14 builds/backup/cosmos_state_offsite.py --root V:\A\Ai\COSMOS\live --preflight
    py -3.14 builds/backup/cosmos_state_offsite.py --root V:\A\Ai\COSMOS\live --selfcheck
    py -3.14 builds/backup/cosmos_state_offsite.py --root V:\A\Ai\COSMOS\live --once
    py -3.14 builds/backup/cosmos_state_offsite.py --root V:\A\Ai\COSMOS\live --plan-task
    py -3.14 builds/backup/cosmos_state_offsite.py --root V:\A\Ai\COSMOS\live --install-task
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
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

CosmosPaths = oc.CosmosPaths
CosmosPathError = oc.CosmosPathError

SCHEMA = "cosmos-state-offsite/1"
WORKER = "cosmos-state-offsite"
HEARTBEAT_NAME = "state_offsite_heartbeat.json"
STAGE = "_delme_state_offsite"
PAYLOAD = ("SEED.json", "SEED.decl.json", "inflight.jsonl", "motif_tracker.json")
CONFIG_NAME = mounts.CONFIG_NAME
CREDENTIALS_NAME = oc.CREDENTIALS_NAME
TASK_NAME = "COSMOS State Offsite Push"
DEFAULT_AT = "03:15"
NO_WINDOW = 0x08000000 if os.name == "nt" else 0
STALE_S = 26 * 3600.0


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")


def inventory(paths: CosmosPaths) -> dict:
    """Presence and size of the F-54 payload. Reads no file body."""
    rows = {}
    present = 0
    bytes_ = 0
    for name in PAYLOAD:
        p = paths.role("state", name)
        try:
            st = p.stat()
            exists = p.is_file()
        except OSError:
            exists, st = False, None
        size = int(st.st_size) if exists and st is not None else None
        rows[name] = {"exists": bool(exists), "bytes": size, "path": str(p)}
        if exists:
            present += 1
            bytes_ += size or 0
    return {"files": rows, "present": present, "bytes": bytes_,
            "expected": len(PAYLOAD)}


def pack(paths: CosmosPaths, dest: Path) -> dict:
    """Copy the whitelist into dest. Never deletes. Never copies config/."""
    dest = Path(dest)
    if dest.exists() and not dest.is_dir():
        raise BackupRefusal("DEST_NOT_DIR",
                            f"pack dest is not a directory: {dest}")
    dest.mkdir(parents=True, exist_ok=True)
    copied, missing = [], []
    for name in PAYLOAD:
        src = paths.role("state", name)
        if not src.is_file():
            missing.append(name)
            continue
        shutil.copy2(src, dest / name)
        copied.append(name)
    if not copied:
        raise BackupRefusal("EMPTY_PAYLOAD",
                            "none of the F-54 payload files exist under the state role "
                            f"({', '.join(PAYLOAD)})")
    manifest = cb.build_manifest(dest)
    offenders = r2.scan_secrets(manifest)
    if offenders:
        raise BackupRefusal(
            "SECRETS_IN_SCOPE",
            f"{len(offenders)} packed file(s) hold key material: "
            f"{', '.join(offenders[:5])} — the F-54 payload is a whitelist; "
            "do not add secrets to it")
    return {
        "packed_dir": str(dest.resolve()),
        "copied": copied,
        "missing": missing,
        "files": manifest["file_count"],
        "bytes": manifest["total_bytes"],
        "secrets_in_scope": [],
    }


def _blockers(paths: CosmosPaths, config_path: Path, creds_path: Path) -> list[dict]:
    """Typed reasons neither offsite route can run. Reads no credential value
    when the file is absent (the live case)."""
    out = []
    try:
        mounts.load_config(config_path)
        out.append({"route": "mount", "kind": "CONFIG_PRESENT",
                    "detail": f"{config_path} is present"})
    except BackupRefusal as e:
        out.append({"route": "mount", "kind": e.kind, "detail": e.detail})
    try:
        r2.load_credentials(creds_path)
        # asdict redacts the secret. We still do not want a live preflight to
        # surface even the last-4 if we can avoid it — CONFIG_PRESENT is enough.
        out.append({"route": "r2", "kind": "CREDENTIAL_PRESENT",
                    "detail": f"{creds_path} is present (value not copied here)"})
    except BackupRefusal as e:
        out.append({"route": "r2", "kind": e.kind, "detail": e.detail})
    return out


def preflight(paths: CosmosPaths) -> dict:
    """Configured vs missing. Creates nothing. Writes no heartbeat."""
    inv = inventory(paths)
    cfg = paths.config(CONFIG_NAME)
    creds = paths.config(CREDENTIALS_NAME)
    blockers = _blockers(paths, cfg, creds)
    blocked = [b for b in blockers if b["kind"] not in ("CONFIG_PRESENT", "CREDENTIAL_PRESENT")]
    status = "READY" if (inv["present"] and not blocked) else "BLOCKED"
    kind = None
    if blocked and all(b["kind"] in ("NO_CONFIG", "NO_CREDENTIALS") for b in blocked):
        kind = "NO_OFFSITE_ROUTE"
    elif blocked:
        kind = blocked[0]["kind"]
    if inv["present"] == 0:
        kind = "EMPTY_PAYLOAD"
        status = "BLOCKED"
    rec = {
        "schema": SCHEMA, "ts": _utcnow(), "status": status, "kind": kind,
        "payload": inv,
        "routes": blockers,
        "adapter_implemented": {"mount": True, "r2": True},
        "config_present": cfg.is_file(),
        "credentials_present": creds.is_file(),
        "heartbeat_written": False,
        "unblocks": ("place backup_targets.json dests (F-48) and/or "
                     "r2_credentials.json (F-46); this same tick then pushes "
                     "the packed SEED/inflight/tracker with no code change"),
    }
    probe = Path(__file__).resolve().parents[1] / "probe"
    if str(probe) not in sys.path:
        sys.path.insert(0, str(probe))
    import artifact_freshness as af                                    # noqa: WPS433
    af.stamp(rec, Path(__file__).resolve().parents[2],
             ["builds/backup/cosmos_state_offsite.py"])
    return rec


def tick(paths: CosmosPaths, *, probe=None, dests: dict | None = None,
         credentials_override=None, transport_factory=None,
         force: bool = False) -> dict:
    """Pack then push, or REFUSE typed. Never raises for a refusal."""
    t0 = time.time()
    rec: dict = {"schema": SCHEMA, "ts": _utcnow(), "tick": "once",
                 "payload_names": list(PAYLOAD)}
    if not force and oc.paused(paths):
        rec.update({"ok": True, "state": "PAUSED",
                    "detail": "state/control/PAUSE.flag is not RUNNING"})
        return _finish(paths, rec, t0)

    cfg = paths.config(CONFIG_NAME)
    creds_path = paths.config(CREDENTIALS_NAME)
    injected = dests is not None or credentials_override is not None

    if not injected:
        blockers = _blockers(paths, cfg, creds_path)
        blocked = [b for b in blockers
                   if b["kind"] not in ("CONFIG_PRESENT", "CREDENTIAL_PRESENT")]
        # Both routes blocked → the waiting-state refusal this module ships.
        if len(blocked) == len(blockers) and blockers:
            rec.update({"ok": False, "state": "REFUSED", "kind": "NO_OFFSITE_ROUTE",
                        "detail": "neither mount dests nor R2 credentials are in place",
                        "routes": blockers, "unblocks": preflight(paths)["unblocks"],
                        "offsite_copy_exists": False})
            return _finish(paths, rec, t0)

    stamp = _stamp()
    packed_dir = paths.role("work", STAGE, stamp, "payload")
    try:
        packed = pack(paths, packed_dir)
    except BackupRefusal as e:
        rec.update({"ok": False, "state": "REFUSED", "kind": e.kind, "detail": e.detail})
        return _finish(paths, rec, t0)
    rec["packed"] = packed
    src = Path(packed["packed_dir"])

    results, pushed_bytes, failures = [], 0, 0

    def _mount_push(kind: str, *, dest=None, config_path=None) -> None:
        nonlocal pushed_bytes, failures
        row = {"route": "mount", "target_kind": kind, "source": str(src)}
        try:
            receipt = mounts.push(src, kind, dest=dest, config_path=config_path,
                                  probe=probe)
            row.update({"ok": True, "state": "PUSHED",
                        "files_pushed": receipt["files_pushed"],
                        "bytes_pushed": receipt["bytes_pushed"],
                        "set_dir": receipt.get("set_dir")})
            pushed_bytes += int(receipt["bytes_pushed"])
        except BackupRefusal as e:
            row.update({"ok": False, "state": "REFUSED", "kind": e.kind,
                        "detail": e.detail})
            failures += 1
        results.append(row)

    if dests is not None:
        for kind, dest in dests.items():
            _mount_push(kind, dest=Path(dest))
    else:
        try:
            mounts.load_config(cfg)
            for kind in mounts.KINDS:
                _mount_push(kind, config_path=cfg)
        except BackupRefusal:
            pass

    def _r2_push(creds) -> None:
        nonlocal pushed_bytes, failures
        row = {"route": "r2", "source": str(src)}
        try:
            made = transport_factory or (lambda: r2.UrllibTransport())
            prefix = f"orchestrator-state/{stamp}"
            scratch = paths.role("work", STAGE, stamp, "r2-readback")
            scratch.mkdir(parents=True, exist_ok=True)
            target = r2.R2Target(creds, prefix, made())
            receipt = r2.push(src, target, scratch=scratch)
            row.update({"ok": True, "state": "PUSHED",
                        "files_pushed": receipt["files_pushed"],
                        "bytes_pushed": receipt["bytes_pushed"],
                        "readback_verified": receipt["readback_verified"]})
            pushed_bytes += int(receipt["bytes_pushed"])
        except BackupRefusal as e:
            row.update({"ok": False, "state": "REFUSED", "kind": e.kind,
                        "detail": e.detail})
            failures += 1
        results.append(row)

    if credentials_override is not None:
        _r2_push(credentials_override)
    else:
        try:
            _r2_push(r2.load_credentials(creds_path))
        except BackupRefusal:
            pass

    ok = failures == 0 and bool(results)
    rec.update({"ok": ok, "targets": results, "bytes_pushed": pushed_bytes,
                "failures": failures,
                "state": "PUSHED" if ok else ("PARTIAL" if pushed_bytes else "FAILED")})
    if ok:
        rec.update({"last_success_epoch": int(time.time()), "last_success_utc": _utcnow(),
                    "offsite_copy_exists": True})
    else:
        rec.setdefault("offsite_copy_exists", False)
    return _finish(paths, rec, t0)


def _finish(paths: CosmosPaths, rec: dict, t0: float) -> dict:
    rec["elapsed_s"] = round(time.time() - t0, 3)
    rec.setdefault("offsite_copy_exists", False)
    hb_path = paths.logs(HEARTBEAT_NAME)
    path = Path(hb_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now().astimezone()
    body = dict(rec)
    body.update({
        "worker": WORKER, "pid": os.getpid(),
        "last_run": now.isoformat(timespec="seconds"),
        "last_run_epoch": int(now.timestamp()),
        "last_run_utc": _utcnow(),
        "_readme": ("Written on EVERY tick. state=REFUSED kind=NO_OFFSITE_ROUTE "
                    "means the F-54 packer is wired and waiting on dests (F-48) "
                    "or the R2 credential (F-46)."),
    })
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(body, indent=1, default=str), encoding="utf-8")
    os.replace(tmp, path)
    body["heartbeat_path"] = str(path)
    return body


def selfcheck(paths: CosmosPaths) -> dict:
    """Drive the REAL tick against FakeProbe + MemoryTransport. Zero network."""
    stamp = _stamp()
    # Dest is a SIBLING of the pack stage so FakeProbe prefix-match cannot
    # assign the source volume to the dest (SAME_VOLUME would fire).
    dest = paths.role("work", "_delme_state_offsite_gdx", stamp)
    dest.mkdir(parents=True, exist_ok=True)
    packed_hint = paths.role("work", STAGE)
    probe = mounts.FakeProbe(volumes={
        str(dest): "vol:SELFCHECK-GDX",
        str(dest.resolve()): "vol:SELFCHECK-GDX",
        str(packed_hint): "vol:SELFCHECK-SRC",
        str(packed_hint.resolve()): "vol:SELFCHECK-SRC",
    })
    creds = r2.R2Credentials("selfcheckaccount", r2.SELFCHECK_ID, r2.SELFCHECK_ID,
                             "selfcheck-bucket")
    return tick(paths, probe=probe, dests={"gdx": dest},
                credentials_override=creds,
                transport_factory=r2.MemoryTransport, force=True)


def _pythonw() -> str:
    cand = Path(sys.executable).with_name("pythonw.exe")
    return str(cand) if cand.exists() else sys.executable


def plan_task_argv(root: Path, at: str = DEFAULT_AT) -> list[str]:
    """schtasks /create plan. Current user, no /rl highest. Registers nothing.

    Daily 03:15 — after the R2 clock (02:30) and the mount clock (03:00) so
    three dest-waiting refusals do not collide on the same minute. The
    payload is the F-54 whitelist, not a scope tree (F-47/F-48 clocks).
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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", required=True)
    ap.add_argument("--at", default=DEFAULT_AT, help="schtasks daily start time")
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
        print(json.dumps({"refused": True, "kind": e.kind, "detail": str(e)}), file=sys.stderr)
        return 2

    if a.plan_task:
        print(json.dumps({"task": TASK_NAME, "argv": plan_task_argv(Path(a.root), a.at),
                          "stale_s": STALE_S, "heartbeat": HEARTBEAT_NAME,
                          "payload": list(PAYLOAD), "registers": False}, indent=1))
        return 0
    if a.install_task:
        rec = install_task(Path(a.root), a.at)
        print(json.dumps(rec, indent=1))
        return 0 if rec["ok"] else 1

    if a.preflight:
        out = preflight(paths)
        print(json.dumps(out, indent=2, sort_keys=True))
        return 0 if out["status"] == "READY" else 2

    rec = selfcheck(paths) if a.selfcheck else tick(paths)
    print(json.dumps(rec, indent=1, default=str))
    if rec.get("ok"):
        return 0
    return 2 if rec.get("state") == "REFUSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
