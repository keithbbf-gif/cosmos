#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_dispatcher_daemon - auto-context, tag-routed agent creation.

COW drops a tiny file in the shared OUT BUCKET (agent/tag + assignment,
optional context_hint, optional out). This daemon:

  1. Parses the TAG -> G46/GW/SGH/GEM/OAi/CURSOR/SSA
  2. Pulls the CURRENT session transcript TAIL (native C:\\ tool)
  3. Auto-attaches the FULL text of docs/AGENT_BOUNDARIES.md
  4. Creates the agent of that type; sets OUTPUT folder = tag + timestamp
  5. Executes via the native rail (grok/cursor/claude) or worker-bucket handoff
  6. Files the record into DHx + live/state/assignments/<session>.jsonl
     and registers with the collector
  7. Heartbeats live/logs/dispatcher_heartbeat.json every tick
  8. Honors live/state/control/PAUSE.flag: --loop IDLEs while present
     (paused != dead; heartbeat state=PAUSED). --once is a commanded drain.

DEFAULT bucket topology: ONE shared box, tag-routed. Config option:
bucket_mode=per_agent (one folder per tag).

NO BTS. Does not modify kernel / ledger / sched / service.

    py -3.14 cosmos\\cosmos_dispatcher_daemon.py --root <live> --once
    py -3.14 cosmos\\cosmos_dispatcher_daemon.py --root <live> --loop
    py -3.14 cosmos\\cosmos_dispatcher_daemon.py --root <live> --standup
    py -3.14 cosmos\\cosmos_dispatcher_daemon.py --root <live> --status
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_clock import (  # noqa: E402
    acquire_lock, create_task, heartbeat_age_s, pid_alive, pythonw_exe,
    query_task, read_heartbeat, spawn_detached, tr_cmdline, wait_fresh,
    write_heartbeat,
)
from cosmos_context_pull import (  # noqa: E402
    DEFAULT_MAX_KB, DEFAULT_TURNS, pull_context,
)
from cosmos_dispatch import (  # noqa: E402
    DispatchError, WORKER_KINDS, append_session_assignment, bind_paths,
    compose_agent_prompt, dispatch, load_boundaries_text,
    parse_agent_tag, repo_docs_dir,
)
from cosmos_paths import CosmosPaths, CosmosPathError  # noqa: E402

WORKER = "cosmos-dispatcher"
TASK_NAME = "COSMOS Dispatcher"
TASK_NAME_LOGON = "COSMOS Dispatcher Logon"
HEARTBEAT_NAME = "dispatcher_heartbeat.json"
LOCK_NAME = "dispatcher.lock"
SCHEMA = "cosmos-dispatcher/1"
CONFIG_NAME = "dispatcher.json"
DEFAULT_INTERVAL_S = 5.0
FRESH_S = 90.0
DROP_SUFFIXES = {".json"}
SKIP_DIR_NAMES = {"processed", "out", "workers", "__pycache__", "_delme"}


def repo_tree() -> Path:
    return Path(__file__).resolve().parent.parent


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat()


def _stamp_folder(dt: datetime | None = None) -> str:
    now = dt or datetime.now().astimezone()
    return now.strftime("%Y-%m-%dT%H-%M-%S") + now.strftime("%z")


def _atomic_json(path: Path, obj) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1, default=str), encoding="utf-8")
    tmp.replace(path)


def default_config() -> dict:
    return {
        "schema": SCHEMA,
        "bucket_mode": "shared",          # shared | per_agent
        "tail_turns": DEFAULT_TURNS,
        "tail_kb": DEFAULT_MAX_KB,
        "interval_s": DEFAULT_INTERVAL_S,
        "sessions_roots": None,           # None -> cosmos_context_pull defaults
    }


def load_config(paths: CosmosPaths) -> dict:
    p = paths.config(CONFIG_NAME)
    cfg = default_config()
    if not p.exists():
        return cfg
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        cfg["_config_error"] = f"unreadable {p}"
        return cfg
    if isinstance(raw, dict):
        cfg.update({k: raw[k] for k in raw if k in cfg or k in (
            "bucket_mode", "tail_turns", "tail_kb", "interval_s",
            "sessions_roots")})
        mode = str(cfg.get("bucket_mode") or "shared").strip().lower()
        cfg["bucket_mode"] = "per_agent" if mode in (
            "per_agent", "per-agent", "one_per_agent") else "shared"
    return cfg


def pause_flag(paths: CosmosPaths) -> dict | None:
    """Presence of live/state/control/PAUSE.flag is the whole signal."""
    p = paths.state("control", "PAUSE.flag")
    if not p.exists() or not p.is_file():
        return None
    rec: dict = {"path": str(p), "state": "PAUSED"}
    try:
        raw = p.read_text(encoding="utf-8").strip()
    except OSError as e:
        rec["read_error"] = str(e)
        return rec
    if raw.startswith("{"):
        try:
            obj = json.loads(raw)
        except ValueError:
            obj = None
        if isinstance(obj, dict):
            rec.update(obj)
            rec.setdefault("state", "PAUSED")
            rec["path"] = str(p)
            return rec
    rec["reason"] = raw[:240] or "(empty flag file)"
    return rec


def bucket_root(paths: CosmosPaths) -> Path:
    d = paths.state("dispatch", "bucket")
    d.mkdir(parents=True, exist_ok=True)
    (d / "processed").mkdir(parents=True, exist_ok=True)
    return d


def per_agent_bucket(paths: CosmosPaths, tag: str) -> Path:
    d = bucket_root(paths) / str(tag).upper()
    d.mkdir(parents=True, exist_ok=True)
    return d


def list_drop_files(paths: CosmosPaths, cfg: dict) -> list[Path]:
    root = bucket_root(paths)
    files: list[Path] = []
    mode = cfg.get("bucket_mode") or "shared"

    def _collect(folder: Path) -> None:
        if not folder.exists():
            return
        for p in sorted(folder.iterdir(), key=lambda x: x.stat().st_mtime
                        if x.exists() else 0):
            if not p.is_file():
                continue
            if p.name.startswith("_") or p.name.startswith("."):
                continue
            if p.suffix.lower() not in DROP_SUFFIXES:
                continue
            files.append(p)

    if mode == "per_agent":
        for child in sorted(root.iterdir()):
            if child.is_dir() and child.name.lower() not in SKIP_DIR_NAMES:
                _collect(child)
    else:
        _collect(root)
    return files


def parse_drop(path: Path) -> dict:
    try:
        # utf-8-sig: PowerShell Set-Content -Encoding utf8 writes a BOM.
        raw = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as e:
        raise DispatchError("BAD_INPUT", f"drop unreadable {path}: {e}") from e
    if not isinstance(raw, dict):
        raise DispatchError("BAD_INPUT", f"drop is not a JSON object: {path}")
    agent = str(raw.get("agent") or raw.get("tag") or "").strip()
    assignment = str(raw.get("assignment") or raw.get("task") or "").strip()
    if not agent:
        raise DispatchError("BAD_INPUT", f"drop missing agent/tag: {path}")
    if not assignment:
        raise DispatchError("BAD_INPUT", f"drop missing assignment: {path}")
    return {
        "agent": agent,
        "assignment": assignment,
        "context_hint": str(raw.get("context_hint") or "").strip(),
        "out": str(raw.get("out") or "").strip(),
        "raw": raw,
        "path": str(path),
        "name": path.name,
    }


def stage_processed(bucket: Path, drop_path: Path, stamp: str) -> Path:
    """Move a handled drop into bucket/processed/. Never delete."""
    dest_dir = bucket / "processed"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{stamp}_{drop_path.name}"
    n = 1
    while dest.exists():
        n += 1
        dest = dest_dir / f"{stamp}_{n}_{drop_path.name}"
    try:
        drop_path.replace(dest)
        return dest
    except OSError:
        shutil.copy2(str(drop_path), str(dest))
        claimed = drop_path.with_name(drop_path.name + ".claimed")
        try:
            drop_path.replace(claimed)
        except OSError:
            pass
        return dest


def out_dir_for(paths: CosmosPaths, tag: str, stamp_folder: str,
                out_tag: str | None = None) -> Path:
    folder_tag = (out_tag or tag or "out").strip() or "out"
    # role() refuses '..' and absolute parts; stamp/tag are sanitised.
    safe_tag = "".join(ch if ch.isalnum() or ch in "-_" else "-"
                       for ch in folder_tag)[:40] or "out"
    safe_stamp = "".join(ch if ch.isalnum() or ch in "-_" else "-"
                         for ch in stamp_folder)[:40] or "t"
    d = paths.state("dispatch", "out", safe_tag, safe_stamp)
    d.mkdir(parents=True, exist_ok=True)
    return d


def assignments_path(paths: CosmosPaths, session_id: str | None) -> Path:
    sid = str(session_id or "no-session").strip() or "no-session"
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in sid)[:80]
    d = paths.state("assignments")
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{safe}.jsonl"


def process_drop(paths: CosmosPaths, drop_path: Path, cfg: dict,
                 *, execute: bool = True) -> dict:
    """One drop: parse, pull context, attach boundaries, create agent, file."""
    t0 = time.time()
    created_at = datetime.now().astimezone()
    stamp = created_at.isoformat()
    stamp_folder = _stamp_folder(created_at)
    drop = parse_drop(drop_path)
    parsed = parse_agent_tag(drop["agent"])
    tag = parsed["tag"]
    kind = parsed["kind"]
    out_tag = drop["out"] or tag

    sessions_roots = None
    if cfg.get("sessions_roots"):
        sessions_roots = [Path(p) for p in cfg["sessions_roots"]]
    ctx = pull_context(
        sessions_roots=sessions_roots,
        max_turns=int(cfg.get("tail_turns") or DEFAULT_TURNS),
        max_kb=int(cfg.get("tail_kb") or DEFAULT_MAX_KB),
    )
    boundaries = load_boundaries_text()
    if not boundaries.strip():
        raise DispatchError(
            "NO_DIR",
            f"docs/AGENT_BOUNDARIES.md missing at {repo_docs_dir() / 'AGENT_BOUNDARIES.md'} "
            f"— refusing to send an assignment without the addendum")

    prompt = compose_agent_prompt(
        drop["assignment"],
        context_blob=ctx.get("blob") or "",
        context_hint=drop.get("context_hint") or "",
        boundaries=boundaries,
        provenance=ctx.get("provenance") or {},
    )
    out_dir = out_dir_for(paths, tag, stamp_folder, out_tag=out_tag)
    packet = {
        "schema": SCHEMA,
        "created_at": stamp,
        "timestamp": stamp,
        "tag": tag,
        "agent": drop["agent"],
        "kind": kind,
        "assignment": drop["assignment"],
        "out": out_tag,
        "out_dir": str(out_dir),
        "drop_path": str(drop_path),
        "drop_name": drop["name"],
        "context_hint": drop.get("context_hint") or "",
        "context": {
            "ok": bool(ctx.get("ok")),
            "session_id": ctx.get("session_id"),
            "path": ctx.get("path"),
            "byte_start": ctx.get("byte_start"),
            "byte_end": ctx.get("byte_end"),
            "file_size": ctx.get("file_size"),
            "turns": ctx.get("turns"),
            "blob_chars": ctx.get("blob_chars"),
            "error": ctx.get("error"),
        },
        "boundaries_chars": len(boundaries),
        "boundaries_path": str(repo_docs_dir() / "AGENT_BOUNDARIES.md"),
        "prompt_chars": len(prompt),
    }
    _atomic_json(out_dir / "assignment.json", packet)
    (out_dir / "context.txt").write_text(ctx.get("blob") or "", encoding="utf-8")
    (out_dir / "drop.json").write_text(
        json.dumps(drop.get("raw") or drop, indent=1, default=str),
        encoding="utf-8")
    (out_dir / "prompt.txt").write_text(prompt, encoding="utf-8")

    disp = None
    if execute:
        disp = dispatch(
            drop["agent"], prompt,
            target_dir=str(out_dir),
            runtime_root=paths.root,
            label=drop["assignment"],
        )
        _atomic_json(out_dir / "dispatch.json", disp)

    session_id = ctx.get("session_id") or "no-session"
    assign_path = assignments_path(paths, session_id)
    row = {
        "schema": SCHEMA,
        "source": "dispatcher_assignment",
        "created_at": stamp,
        "timestamp": stamp,
        "tag": tag,
        "agent": drop["agent"],
        "kind": kind,
        "assignment": drop["assignment"],
        "assignment_oneline": " ".join(drop["assignment"].split())[:140],
        "out": out_tag,
        "out_dir": str(out_dir),
        "drop_path": str(drop_path),
        "drop_name": drop["name"],
        "session_id": session_id,
        "context_path": ctx.get("path"),
        "context_bytes": [ctx.get("byte_start"), ctx.get("byte_end")],
        "context_ok": bool(ctx.get("ok")),
        "job_file": (disp or {}).get("job_file"),
        "job_path": (disp or {}).get("job_path"),
        "native_job_id": (disp or {}).get("native_job_id"),
        "returns_path": (disp or {}).get("returns_path"),
        "dhx_marker": (disp or {}).get("marker"),
        "collector": (disp or {}).get("collector"),
        "execute": bool(execute),
        "elapsed_s": round(time.time() - t0, 3),
    }
    sess = append_session_assignment(assign_path, row)
    processed = stage_processed(bucket_root(paths), drop_path, stamp_folder)
    rec = {
        "ok": True,
        "created_at": stamp,
        "tag": tag,
        "agent": drop["agent"],
        "kind": kind,
        "assignment": drop["assignment"],
        "out_dir": str(out_dir),
        "timestamp": stamp,
        "session_id": session_id,
        "assignments_path": sess["path"],
        "processed_drop": str(processed),
        "context": packet["context"],
        "dispatch": {
            "ok": (disp or {}).get("ok"),
            "created": (disp or {}).get("created"),
            "job_file": (disp or {}).get("job_file"),
            "job_path": (disp or {}).get("job_path"),
            "native_job_id": (disp or {}).get("native_job_id"),
            "returns_path": (disp or {}).get("returns_path"),
            "marker": (disp or {}).get("marker"),
            "dhx": (disp or {}).get("dhx"),
            "collector": (disp or {}).get("collector"),
            "kind_live": (disp or {}).get("kind_live"),
            "queue_identity": (disp or {}).get("queue_identity"),
        } if disp else None,
        "elapsed_s": round(time.time() - t0, 3),
        "worker_kind": kind in WORKER_KINDS,
    }
    _atomic_json(out_dir / "result.json", rec)
    return rec


def poll_once(root: str, polls: int = 0, interval_s: float | None = None,
              *, drain: bool = True) -> dict:
    """One tick. Heartbeat always. If PAUSE present and drain is False, idle.

    --loop passes drain=False when paused. --once always drains (commanded).
    """
    paths = bind_paths(root)
    cfg = load_config(paths)
    interval = (interval_s if interval_s is not None
                else float(cfg.get("interval_s") or DEFAULT_INTERVAL_S))
    hb_path = paths.logs(HEARTBEAT_NAME)
    paused = pause_flag(paths)
    extra = {
        "schema": SCHEMA,
        "tick": "poll",
        "state": "RUNNING",
        "pause_present": paused is not None,
        "bucket": str(bucket_root(paths)),
        "bucket_mode": cfg.get("bucket_mode"),
        "tree_id": paths.sentinel.tree_id,
    }
    if paused is not None and str(paused.get("state", "PAUSED")).upper() != "RUNNING":
        extra["state"] = "PAUSED"
        extra["tick"] = "paused"
        extra["mode"] = str(paused.get("mode") or "hold")
        extra["auto_resume_at"] = paused.get("auto_resume_at")
        extra["pause"] = {
            "reason": paused.get("reason"),
            "set_by": paused.get("set_by"),
            "set_at": paused.get("set_at"),
            "path": paused.get("path"),
        }
        if not drain:
            extra["dropped_this_tick"] = 0
            extra["jobs"] = []
            hb = write_heartbeat(hb_path, WORKER, extra=extra, polls=polls,
                                 interval_s=interval)
            extra["ok"] = True
            extra["heartbeat"] = hb
            extra["heartbeat_path"] = str(hb_path)
            return extra
        extra["tick"] = "once_while_paused"

    jobs = []
    errors = []
    if drain:
        drops = list_drop_files(paths, cfg)
        extra["drops_seen"] = len(drops)
        extra["drop_names"] = [p.name for p in drops]
        for dp in drops:
            try:
                rec = process_drop(paths, dp, cfg, execute=True)
                jobs.append({
                    "ok": rec.get("ok"),
                    "tag": rec.get("tag"),
                    "out_dir": rec.get("out_dir"),
                    "job_file": (rec.get("dispatch") or {}).get("job_file"),
                    "native_job_id": (rec.get("dispatch") or {}).get("native_job_id"),
                    "assignments_path": rec.get("assignments_path"),
                    "session_id": rec.get("session_id"),
                    "context_ok": (rec.get("context") or {}).get("ok"),
                    "timestamp": rec.get("timestamp"),
                })
            except DispatchError as e:
                errors.append({"drop": str(dp), "kind": e.kind, "error": str(e)})
            except Exception as e:  # noqa: BLE001
                errors.append({"drop": str(dp),
                               "kind": type(e).__name__, "error": str(e)})
    extra["dropped_this_tick"] = len(jobs)
    extra["jobs"] = jobs
    extra["errors"] = errors
    extra["tick"] = extra.get("tick") if extra.get("tick") != "poll" else (
        "drained" if jobs else "idle")
    extra["ok"] = not errors
    hb = write_heartbeat(hb_path, WORKER, extra=extra, polls=polls,
                         interval_s=interval)
    extra["heartbeat"] = hb
    extra["heartbeat_path"] = str(hb_path)
    return extra


def loop(root: str, interval_s: float) -> int:
    paths = CosmosPaths(root)
    out_path = paths.logs("dispatcher.out")
    err_path = paths.logs("dispatcher.err")
    lock_path = paths.logs(LOCK_NAME)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    log_fh = open(out_path, "a", encoding="utf-8", buffering=1)
    sys.stdout = log_fh
    sys.stderr = log_fh
    fd = acquire_lock(lock_path)
    if fd is None:
        rec = read_heartbeat(paths.logs(HEARTBEAT_NAME))
        age = heartbeat_age_s(rec)
        pid = (rec or {}).get("pid")
        if age is not None and age < FRESH_S and pid_alive(int(pid or 0)):
            print(json.dumps({"already_running": True, "pid": pid,
                              "age_s": round(age, 3)}), flush=True)
            return 0
        print("dispatcher lock held and heartbeat not fresh - refusing",
              flush=True)
        return 2
    polls = 0
    print(json.dumps({"loop": True, "pid": os.getpid(),
                      "interval_s": interval_s}, indent=1), flush=True)
    try:
        while True:
            polls += 1
            paused = pause_flag(paths)
            drain = not (paused is not None
                         and str(paused.get("state", "PAUSED")).upper()
                         != "RUNNING")
            try:
                poll_once(root, polls=polls, interval_s=interval_s,
                          drain=drain)
            except Exception:
                import traceback
                tb = traceback.format_exc()
                try:
                    err_path.write_text(tb, encoding="utf-8")
                except OSError:
                    pass
                try:
                    write_heartbeat(paths.logs(HEARTBEAT_NAME), WORKER,
                                    extra={"tick": "error", "error": tb[-500:]},
                                    polls=polls, interval_s=interval_s)
                except OSError:
                    pass
            time.sleep(interval_s)
    finally:
        os.close(fd)
    return 0


def standup(root: str, interval_s: float = DEFAULT_INTERVAL_S) -> dict:
    paths = CosmosPaths(root)
    hb = paths.logs(HEARTBEAT_NAME)
    t0 = time.time()
    proof = wait_fresh(hb, timeout_s=1.2, max_age_s=FRESH_S)
    if proof["ok"]:
        return {"started": "already", "proof": proof, "keith_cmd": None,
                "task_name": TASK_NAME}

    script = Path(__file__).resolve()
    tr = tr_cmdline(script, root, "--loop")
    minute = create_task(TASK_NAME, tr, "minute", mo=1, run_now=True)
    logon = create_task(TASK_NAME_LOGON, tr, "onlogon")
    launched_via = None
    detach = None
    if minute.get("ok") and minute.get("run_ok"):
        launched_via = "schtasks"
        proof = wait_fresh(hb, timeout_s=12.0, min_epoch=t0, max_age_s=FRESH_S)
    if not proof.get("ok"):
        argv = [pythonw_exe(), str(script), "--root", str(Path(root).resolve()),
                "--loop"]
        detach = spawn_detached(argv, str(script.parent),
                                paths.logs("dispatcher.out"))
        launched_via = detach.get("method") or "detached"
        expect = detach.get("pid") if isinstance(detach.get("pid"), int) else None
        proof = wait_fresh(hb, timeout_s=15.0, min_epoch=t0, max_age_s=FRESH_S,
                           expect_pid=expect)

    keith = []
    for rec in (minute, logon):
        if rec.get("keith_cmd") and (rec.get("needs_elevation") or not rec.get("ok")):
            keith.append(rec["keith_cmd"])
        h = rec.get("harden") or {}
        if h.get("keith_cmd") and not h.get("ok"):
            keith.append(h["keith_cmd"])
    return {
        "started": launched_via,
        "task_minute": minute,
        "task_logon": logon,
        "detach": detach,
        "proof": proof,
        "heartbeat_path": str(hb),
        "keith_cmd": " & ".join(keith) if keith else None,
        "keith_cmds": keith,
        "task_name": TASK_NAME,
    }


def status_probe(root: str) -> dict:
    paths = CosmosPaths(root)
    hb = paths.logs(HEARTBEAT_NAME)
    rec = read_heartbeat(hb)
    age = heartbeat_age_s(rec)
    paused = pause_flag(paths)
    bucket = paths.state("dispatch", "bucket")
    n = 0
    if bucket.exists():
        n = sum(1 for p in bucket.iterdir()
                if p.is_file() and p.suffix.lower() == ".json"
                and not p.name.startswith("_"))
    return {
        "path": str(hb),
        "age_s": age,
        "heartbeat": rec,
        "pause_present": paused is not None,
        "pause": paused,
        "bucket": str(bucket),
        "drops_waiting": n,
        "task": query_task(TASK_NAME),
    }


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_dispatcher_daemon")
    ap.add_argument("--root", required=True)
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--standup", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--interval", type=float, default=DEFAULT_INTERVAL_S)
    a = ap.parse_args()
    if a.status:
        rec = status_probe(a.root)
        print(json.dumps(rec, indent=1, default=str))
        age = rec.get("age_s")
        return 0 if age is not None and age < FRESH_S else 2
    if a.standup:
        r = standup(a.root, a.interval)
        print(json.dumps(r, indent=1, default=str))
        return 0 if (r.get("proof") or {}).get("ok") else 2
    if a.once:
        # Commanded drain: process waiting drops even if PAUSE is up
        # (Keith/COW explicit --once). The --loop vehicle idles on PAUSE.
        r = poll_once(a.root, interval_s=a.interval, drain=True)
        out = {k: r[k] for k in r if k != "heartbeat"}
        print(json.dumps(out, indent=1, default=str))
        return 0 if r.get("ok") else 2
    return loop(a.root, a.interval)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CosmosPathError as e:
        print(e, file=sys.stderr)
        raise SystemExit(2)
    except DispatchError as e:
        print(json.dumps({"ok": False, "kind": e.kind, "error": str(e)},
                         indent=1))
        raise SystemExit(2)
