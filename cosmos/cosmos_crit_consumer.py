#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_crit_consumer - vendor-plural critique packet consumer.

cosmos_dispatch already drops a handoff packet under
live/state/dispatch/workers/{gem,oa,ssa}/. That drop is ASSIGNMENT, not
the agent's return (kind_live=handoff, no body, a fake-DONE rc=0 was the
scar). This daemon is the missing half: claim each packet under a
lease/fence, run THAT node's rail, write a REAL critique body to the
packet's designated returns path.

  GEM  -> gem-api (cosmos_node_worker node_spec / execute_via_rail)
  OAi  -> oa-api  (same)
  SSA  -> claude -p --model sonnet

A handoff is NOT terminal until this consumer returns a nonempty body.
Empty rail text is FAILED, never accepted. Replay of a fenced packet is
ignored. --loop honors PAUSE.flag (claim NOTHING; heartbeat state=PAUSED).
--once is a commanded drain even while paused.

    py -3.14 cosmos\\cosmos_crit_consumer.py --root <live> --once
    py -3.14 cosmos\\cosmos_crit_consumer.py --root <live> --loop
    py -3.14 cosmos\\cosmos_crit_consumer.py --root <live> --standup
    py -3.14 cosmos\\cosmos_crit_consumer.py --root <live> --status

NO BTS import. Does not modify kernel / ledger / sched / service.
Does not edit cosmos_dispatch.py (one writer).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from cosmos_clock import (  # noqa: E402
    acquire_lock, atomic_json, create_task, heartbeat_age_s, pid_alive,
    plan_create, pythonw_exe, query_task, read_heartbeat, spawn_detached,
    tr_cmdline, wait_fresh, write_heartbeat,
)
# Sibling first: cosmos_dispatch inserts ITS own dir onto sys.path, which
# would otherwise bind the live (pre-OA) cosmos_node_worker.
from cosmos_node_worker import (  # noqa: E402
    WorkerError, execute_via_rail, is_paused, land_critique_return,
    node_spec, parse_task, pause_flag, stage_drop,
)
from cosmos_dispatch import append_dhx_marker, default_dhx  # noqa: E402
from cosmos_paths import CosmosPaths, CosmosPathError  # noqa: E402
sys.path.insert(0, str(_HERE))

SCHEMA = "cosmos-crit-consumer/1"
WORKER = "cosmos-crit-consumer"
CLOCK_ID = 20
TASK_NAME = "COSMOS CritConsumer"
TASK_NAME_LOGON = "COSMOS CritConsumer Logon"
HEARTBEAT_NAME = "crit_consumer_heartbeat.json"
LOCK_NAME = "crit_consumer.lock"
DEFAULT_INTERVAL_S = 10.0
FRESH_S = 90.0
CLAUDE_TIMEOUT_S = 1800
SSA_MODEL = "sonnet"
DROP_SUFFIXES = {".json", ".txt"}
CRIT_KINDS = ("gem", "oa", "ssa")
KIND_ALIASES = {
    "gem": "gem", "gemini": "gem",
    "oa": "oa", "oai": "oa", "openai": "oa",
    "ssa": "ssa", "subagent": "ssa", "sonnetsubagent": "ssa",
}
_CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0
_CLAIM_LOCK = threading.Lock()


class ConsumerError(WorkerError):
    """kind in {BAD_KIND, BAD_PACKET, FENCE_LOST, REPLAY, EMPTY_OUTPUT}."""


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat()


def _oneline(s: str, n: int = 140) -> str:
    s = " ".join(str(s or "").split())
    return s if len(s) <= n else s[: n - 1] + "…"


def canon_crit_kind(kind: str) -> str:
    key = str(kind or "").strip().lower()
    folded = "".join(ch for ch in key if ch.isalnum())
    if key in KIND_ALIASES:
        return KIND_ALIASES[key]
    if folded in KIND_ALIASES:
        return KIND_ALIASES[folded]
    raise ConsumerError("BAD_KIND",
                        f"unknown critique kind {kind!r}; want gem|oa|ssa")


def route_for(kind: str) -> dict:
    """What rail this kind binds to. No I/O. Test seam for routing."""
    k = canon_crit_kind(kind)
    if k == "ssa":
        return {
            "kind": "ssa",
            "rail": "claude-cli",
            "model": SSA_MODEL,
            "argv_head": ["claude", "-p", "--model", SSA_MODEL],
            "node": "ssa",
        }
    spec = node_spec(k)
    rail = spec["rails"][0]
    return {
        "kind": k,
        "rail": rail["link_id"],
        "module": rail["module"],
        "node": spec["id"],
        "agent": spec["agent"],
    }


def workers_dir(paths: CosmosPaths, kind: str) -> Path:
    """Identity inbox: live/state/dispatch/workers/<kind>."""
    k = canon_crit_kind(kind)
    d = paths.state("dispatch", "workers", k)
    d.mkdir(parents=True, exist_ok=True)
    (d / "processed").mkdir(parents=True, exist_ok=True)
    (d / "failed").mkdir(parents=True, exist_ok=True)
    (d / "running").mkdir(parents=True, exist_ok=True)
    (d / "_fence").mkdir(parents=True, exist_ok=True)
    return d


def fence_path(inbox: Path, name: str) -> Path:
    return inbox / "_fence" / (Path(name).stem + ".json")


def list_inbox_files(inbox: Path) -> list[Path]:
    files: list[Path] = []
    if not inbox.exists():
        return files
    try:
        kids = list(inbox.iterdir())
    except OSError:
        return files
    for p in sorted(kids, key=lambda x: x.stat().st_mtime if x.exists() else 0):
        if not p.is_file():
            continue
        if p.name.startswith("_") or p.name.startswith("."):
            continue
        if p.suffix.lower() not in DROP_SUFFIXES:
            continue
        files.append(p)
    return files


def list_packets(paths: CosmosPaths) -> list[tuple[str, Path]]:
    found: list[tuple[str, Path, float]] = []
    for kind in CRIT_KINDS:
        inbox = workers_dir(paths, kind)
        for p in list_inbox_files(inbox):
            try:
                mtime = p.stat().st_mtime
            except OSError:
                mtime = 0.0
            found.append((kind, p, mtime))
    found.sort(key=lambda x: x[2])
    return [(kind, p) for kind, p, _ in found]


def returns_already_done(returns_path: Path | None) -> bool:
    """True only when a REAL nonempty critique body already landed."""
    if returns_path is None or not returns_path.exists():
        return False
    try:
        rec = json.loads(returns_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    if not isinstance(rec, dict):
        return False
    text = str(
        rec.get("stdout_tail")
        or rec.get("text")
        or (rec.get("rail") or {}).get("text")
        or ""
    )
    return bool(rec.get("done") and text.strip())


def is_replay(inbox: Path, name: str, returns_path: Path | None = None) -> bool:
    if fence_path(inbox, name).exists():
        return True
    return returns_already_done(returns_path)


def write_fence(inbox: Path, name: str, rec: dict) -> dict:
    fp = fence_path(inbox, name)
    fp.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY
    try:
        fd = os.open(str(fp), flags, 0o644)
    except FileExistsError:
        raise ConsumerError("REPLAY", f"fence already held for {name}")
    try:
        os.write(fd, json.dumps(rec, indent=1, default=str).encode("utf-8"))
    finally:
        os.close(fd)
    rec["fence_path"] = str(fp)
    return rec


def claim_packet(inbox: Path, packet: Path, *, owner: str = WORKER,
                 fence_id: str | None = None,
                 returns_path: Path | None = None) -> Path | None:
    """Exclusive claim. Exactly one winner. Replay -> None.

    1. Fence file O_EXCL (durable exactly-once token).
    2. os.rename into running/ (Windows fails if dest exists).
    Lost races and replays return None — never double-invoke a rail.
    """
    with _CLAIM_LOCK:
        if not packet.exists() or not packet.is_file():
            return None
        if is_replay(inbox, packet.name, returns_path):
            return None
        running = inbox / "running"
        running.mkdir(parents=True, exist_ok=True)
        dest = running / packet.name
        try:
            os.rename(str(packet), str(dest))
        except OSError:
            return None
        fid = fence_id or uuid.uuid4().hex
        rec = {
            "schema": SCHEMA,
            "owner": owner,
            "pid": os.getpid(),
            "fence": fid,
            "claimed_at": _iso_now(),
            "packet": packet.name,
            "inbox": str(inbox),
            "claimed_path": str(dest),
        }
        try:
            write_fence(inbox, packet.name, rec)
        except ConsumerError:
            # rename won; fence lost the O_EXCL race. Still ours — dest moved.
            rec["fence_shared"] = True
            try:
                atomic_json(fence_path(inbox, packet.name), rec)
            except OSError:
                pass
        return dest


def parse_critique_packet(path: Path, folder_kind: str) -> dict:
    """Critique packet. Live packets have assignment+returns, no prompt."""
    task = parse_task(path, default_out="V")
    raw = task.get("raw") or {}
    kind_src = task.get("kind") or raw.get("kind") or folder_kind
    try:
        kind = canon_crit_kind(kind_src)
    except ConsumerError:
        kind = canon_crit_kind(folder_kind)
    returns = task.get("returns")
    if not returns:
        rp = raw.get("returns") or raw.get("result")
        returns = str(rp).strip() if rp else None
    task["kind"] = kind
    task["folder_kind"] = canon_crit_kind(folder_kind)
    task["returns"] = returns
    task["agent"] = task.get("agent") or raw.get("agent") or kind.upper()
    return task


def run_claude_sonnet(prompt: str, *, cwd, timeout_s: int = CLAUDE_TIMEOUT_S,
                      claude_call=None) -> dict:
    """SSA rail: claude -p --model sonnet (dispatch _claude_job flag set)."""
    cwd_s = str(Path(cwd))
    argv = ["claude", "-p", prompt, "--model", SSA_MODEL,
            "--permission-mode", "dontAsk", "--add-dir", cwd_s]
    if claude_call is not None:
        r = claude_call(argv)
        if not isinstance(r, dict):
            r = {"ok": True, "kind": "CLI", "text": str(r),
                 "model": SSA_MODEL, "link_id": "claude-cli"}
        r.setdefault("kind", "CLI")
        r.setdefault("model", SSA_MODEL)
        r.setdefault("link_id", "claude-cli")
        r.setdefault("argv", argv)
        return r
    t0 = time.time()
    try:
        p = subprocess.run(
            argv, capture_output=True, text=True, encoding="utf-8",
            errors="replace", cwd=cwd_s, timeout=int(timeout_s),
            shell=False, creationflags=_CREATE_NO_WINDOW)
        text = p.stdout or ""
        ok = p.returncode == 0 and bool(text.strip())
        return {
            "ok": ok, "kind": "CLI", "text": text,
            "model": SSA_MODEL, "link_id": "claude-cli",
            "argv": argv, "rc": p.returncode,
            "stderr_tail": (p.stderr or "")[-1500:],
            "elapsed_s": round(time.time() - t0, 3),
            "detail": None if ok else (
                "empty_stdout" if p.returncode == 0 else f"claude rc={p.returncode}"),
        }
    except FileNotFoundError as e:
        return {"ok": False, "kind": "UNREACHABLE", "text": "",
                "model": SSA_MODEL, "link_id": "claude-cli", "argv": argv,
                "detail": f"claude not on PATH: {e}"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "kind": "TIMEOUT", "text": "",
                "model": SSA_MODEL, "link_id": "claude-cli", "argv": argv,
                "detail": f"claude timed out after {timeout_s}s"}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "kind": "BROKE", "text": "",
                "model": SSA_MODEL, "link_id": "claude-cli", "argv": argv,
                "detail": f"{type(e).__name__}: {e}"}


def invoke_rail(paths: CosmosPaths, kind: str, prompt: str, *,
                invoke=None, rail_call=None, claude_call=None) -> dict:
    """Run the bound rail. `invoke(kind, prompt)` is the test seam."""
    k = canon_crit_kind(kind)
    if invoke is not None:
        r = invoke(k, prompt)
        if not isinstance(r, dict):
            r = {"ok": True, "kind": "API", "text": str(r),
                 "model": "injected", "link_id": "injected"}
        r.setdefault("kind", "CLI" if k == "ssa" else "API")
        r.setdefault("link_id", "claude-cli" if k == "ssa" else "injected")
        r.setdefault("model", SSA_MODEL if k == "ssa" else "injected")
        return r
    if k == "ssa":
        cwd = paths.root.parent if (paths.root.parent / "docs").exists() else paths.root
        return run_claude_sonnet(prompt, cwd=cwd, claude_call=claude_call)
    spec = node_spec(k)
    return execute_via_rail(paths, spec, prompt, rail_call=rail_call)


def _rail_view(rail: dict) -> dict:
    return {
        "ok": bool(rail.get("ok")),
        "kind": rail.get("kind"),
        "link_id": rail.get("link_id"),
        "model": rail.get("model") or rail.get("node"),
        "usd": rail.get("usd"),
        "text": rail.get("text") or "",
        "detail": rail.get("detail"),
        "node": rail.get("node"),
        "argv": rail.get("argv"),
    }


def process_packet(paths: CosmosPaths, folder_kind: str, drop_path: Path,
                   *, invoke=None, rail_call=None, claude_call=None,
                   dhx_path: Path | None = None) -> dict:
    """Claim under fence, invoke rail, land the designated returns path."""
    t0 = time.time()
    inbox = workers_dir(paths, folder_kind)
    if not drop_path.exists():
        return {"ok": True, "done": False, "replay": True, "picked": False,
                "kind": folder_kind, "drop_path": str(drop_path),
                "elapsed_s": round(time.time() - t0, 3)}
    try:
        task = parse_critique_packet(drop_path, folder_kind)
    except WorkerError as e:
        if not drop_path.exists():
            return {"ok": True, "done": False, "replay": True, "picked": False,
                    "kind": folder_kind, "drop_path": str(drop_path),
                    "error": str(e), "elapsed_s": round(time.time() - t0, 3)}
        failed = stage_drop(inbox, drop_path, _iso_now().replace(":", ""),
                            failed=True)
        return {"ok": False, "done": False, "kind": e.kind, "error": str(e),
                "drop_path": str(drop_path), "processed_drop": str(failed),
                "elapsed_s": round(time.time() - t0, 3), "replay": False}

    returns_path = Path(task["returns"]) if task.get("returns") else None
    if is_replay(inbox, drop_path.name, returns_path):
        return {"ok": True, "done": False, "replay": True,
                "kind": task["kind"], "task_id": task["id"],
                "drop_path": str(drop_path), "picked": False,
                "elapsed_s": round(time.time() - t0, 3)}

    fence_id = uuid.uuid4().hex
    claimed = claim_packet(inbox, drop_path, fence_id=fence_id,
                           returns_path=returns_path)
    if claimed is None:
        return {"ok": True, "done": False, "replay": True,
                "kind": task["kind"], "task_id": task["id"],
                "drop_path": str(drop_path), "picked": False,
                "fence_lost": True,
                "elapsed_s": round(time.time() - t0, 3)}

    route = route_for(task["kind"])
    spec_agent = route.get("agent") or str(task.get("agent") or task["kind"])
    rec = {
        "schema": SCHEMA,
        "ok": False,
        "done": False,
        "replay": False,
        "picked": True,
        "node": task["kind"],
        "kind": task["kind"],
        "worker": WORKER,
        "agent": spec_agent,
        "task_id": task["id"],
        "prompt": task["prompt"],
        "route": route,
        "drop_path": str(drop_path),
        "drop_name": drop_path.name,
        "processed_drop": str(claimed),
        "pickup_at": _iso_now(),
        "pickup_id": fence_id[:12],
        "fence": fence_id,
        "returns": str(returns_path) if returns_path else None,
    }
    rail = invoke_rail(paths, task["kind"], task["prompt"], invoke=invoke,
                       rail_call=rail_call, claude_call=claude_call)
    rec["rail"] = _rail_view(rail)
    rec["ok"] = bool(rail.get("ok")) and bool(str(rail.get("text") or "").strip())
    if not rec["ok"]:
        rec["error"] = (rail.get("detail") or rail.get("kind")
                        or ("EMPTY_OUTPUT" if not str(rail.get("text") or "").strip()
                            else "RAIL_FAILED"))
    rec["elapsed_s"] = round(time.time() - t0, 3)
    rec["model"] = rec["rail"].get("model")
    rec["link_id"] = rec["rail"].get("link_id")

    if returns_path is not None:
        rec = land_critique_return(rec, returns_path)
    else:
        text = rec["rail"].get("text") or ""
        rec["done"] = bool(text.strip()) and rec["ok"]
        rec["done_why"] = "nonempty_stdout" if rec["done"] else "empty_stdout"
        rec["rc"] = 0 if rec["done"] else 2
        rec["status"] = "returned" if rec["done"] else "failed"
        rec["stdout_tail"] = text[-4000:]

    failed = not rec.get("done")
    staged = stage_drop(
        inbox, claimed,
        datetime.now().astimezone().strftime("%Y%m%dT%H%M%S"),
        failed=failed)
    rec["processed_drop"] = str(staged)

    try:
        dhx = Path(dhx_path) if dhx_path is not None else default_dhx(paths)
        marker = (f"{rec.get('pickup_at') or _iso_now()} · "
                  f"{spec_agent} · "
                  f"critique {_oneline(task['prompt'])} · "
                  f"workers/{task['kind']}/{drop_path.name}")
        append_dhx_marker(dhx, marker)
        rec["dhx_marker"] = marker
    except Exception:  # noqa: BLE001
        pass
    return rec


def poll_once(root: str, polls: int = 0, interval_s: float | None = None,
              *, drain: bool = True, invoke=None, rail_call=None,
              claude_call=None, dhx_path: Path | None = None) -> dict:
    """One tick. Heartbeat always. PAUSE + drain=False => claim NOTHING."""
    try:
        paths = CosmosPaths(root)
    except CosmosPathError as e:
        raise ConsumerError("NO_ROOT", str(e)) from e
    interval = (interval_s if interval_s is not None else DEFAULT_INTERVAL_S)
    hb_path = paths.logs(HEARTBEAT_NAME)
    paused = pause_flag(paths)
    extra = {
        "schema": SCHEMA,
        "tick": "poll",
        "state": "RUNNING",
        "worker": WORKER,
        "pause_present": paused is not None,
        "inboxes": {k: str(workers_dir(paths, k)) for k in CRIT_KINDS},
        "tree_id": paths.sentinel.tree_id,
        "no_bts": True,
        "interval_s": interval,
    }
    if is_paused(paused):
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
            extra["picked_this_tick"] = 0
            extra["jobs"] = []
            extra["claimed"] = 0
            hb = write_heartbeat(hb_path, WORKER, extra=extra,
                                 polls=polls, interval_s=interval)
            extra["ok"] = True
            extra["heartbeat"] = hb
            extra["heartbeat_path"] = str(hb_path)
            return extra
        extra["tick"] = "once_while_paused"

    jobs = []
    errors = []
    if drain:
        packets = list_packets(paths)
        extra["drops_seen"] = len(packets)
        extra["drop_names"] = [p.name for _, p in packets]
        # one packet per tick — a long rail call must not starve the heartbeat
        for folder_kind, dp in packets[:1]:
            try:
                rec = process_packet(
                    paths, folder_kind, dp, invoke=invoke,
                    rail_call=rail_call, claude_call=claude_call,
                    dhx_path=dhx_path)
                jobs.append(rec)
            except WorkerError as e:
                errors.append({"drop": str(dp), "kind": e.kind, "error": str(e)})
            except Exception as e:  # noqa: BLE001
                errors.append({"drop": str(dp),
                               "kind": type(e).__name__, "error": str(e)})
    extra["picked_this_tick"] = sum(1 for j in jobs if j.get("picked"))
    extra["claimed"] = extra["picked_this_tick"]
    extra["jobs"] = [{
        "ok": j.get("ok"),
        "done": j.get("done"),
        "replay": j.get("replay"),
        "picked": j.get("picked"),
        "task_id": j.get("task_id"),
        "kind": j.get("kind"),
        "returns_path": j.get("returns_path") or j.get("returns"),
        "model": j.get("model") or (j.get("rail") or {}).get("model"),
        "link_id": j.get("link_id") or (j.get("rail") or {}).get("link_id"),
        "stdout_tail": (j.get("stdout_tail") or "")[:200],
        "error": j.get("error"),
        "rc": j.get("rc"),
    } for j in jobs]
    extra["errors"] = errors
    extra["tick"] = extra.get("tick") if extra.get("tick") not in (
        "poll",) else ("drained" if extra["picked_this_tick"] else "idle")
    extra["ok"] = not errors
    hb = write_heartbeat(hb_path, WORKER, extra=extra,
                         polls=polls, interval_s=interval)
    extra["heartbeat"] = hb
    extra["heartbeat_path"] = str(hb_path)
    return extra


def loop(root: str, interval_s: float) -> int:
    paths = CosmosPaths(root)
    out_path = paths.logs("crit_consumer.out")
    err_path = paths.logs("crit_consumer.err")
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
        print("crit consumer lock held and heartbeat not fresh - refusing",
              flush=True)
        return 2
    polls = 0
    print(json.dumps({"loop": True, "pid": os.getpid(),
                      "interval_s": interval_s}, indent=1), flush=True)
    try:
        while True:
            polls += 1
            paused = pause_flag(paths)
            drain = not is_paused(paused)
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
                    write_heartbeat(
                        paths.logs(HEARTBEAT_NAME), WORKER,
                        extra={"tick": "error", "state": "ERROR",
                               "error": tb[-500:]},
                        polls=polls, interval_s=interval_s)
                except OSError:
                    pass
            time.sleep(interval_s)
    finally:
        os.close(fd)
    return 0


def plan_task_argv(root: str) -> list[str]:
    """schtasks /create plan. 1-min self-heal of --loop. Registers nothing."""
    tr = tr_cmdline(Path(__file__).resolve(), str(root), "--loop")
    return plan_create(TASK_NAME, tr, "minute", mo=1)


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
        argv = [pythonw_exe(), str(script), "--root",
                str(Path(root).resolve()), "--loop"]
        detach = spawn_detached(argv, str(script.parent),
                                paths.logs("crit_consumer.out"))
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
    waiting = {}
    n = 0
    for kind in CRIT_KINDS:
        inbox = paths.state("dispatch", "workers", kind)
        c = 0
        if inbox.exists():
            c = sum(1 for p in inbox.iterdir()
                    if p.is_file() and p.suffix.lower() in DROP_SUFFIXES
                    and not p.name.startswith("_") and not p.name.startswith("."))
        waiting[kind] = c
        n += c
    return {
        "path": str(hb),
        "age_s": age,
        "heartbeat": rec,
        "pause_present": paused is not None,
        "pause": paused,
        "inboxes": {k: str(paths.state("dispatch", "workers", k))
                    for k in CRIT_KINDS},
        "drops_waiting": n,
        "waiting": waiting,
        "task": query_task(TASK_NAME),
        "fresh": age is not None and age < FRESH_S,
    }


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_crit_consumer")
    ap.add_argument("--root", required=True)
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--standup", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--plan-task", action="store_true",
                    help="print the schtasks argv, register nothing")
    ap.add_argument("--interval", type=float, default=DEFAULT_INTERVAL_S)
    a = ap.parse_args()
    if a.plan_task:
        rec = {"task": TASK_NAME, "argv": plan_task_argv(a.root),
               "heartbeat": HEARTBEAT_NAME, "clock_id": CLOCK_ID}
        print(json.dumps(rec, indent=1))
        return 0
    if a.status:
        rec = status_probe(a.root)
        print(json.dumps(rec, indent=1, default=str))
        return 0 if rec.get("fresh") else 2
    if a.standup:
        r = standup(a.root, a.interval)
        print(json.dumps(r, indent=1, default=str))
        return 0 if (r.get("proof") or {}).get("ok") else 2
    if a.once:
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
    except WorkerError as e:
        print(json.dumps({"ok": False, "kind": e.kind, "error": str(e)},
                         indent=1))
        raise SystemExit(2)
