#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_node_bucket_worker - GROK + GEM Windows-native bucket daemons.

One helper, two daemons (same script, --node grok|gem). Each polls ITS OWN
bucket (live/buckets/<node>/), claims a drop under an O_EXCL fence, executes
via that node's COSMOS rail, and writes the result DIRECTLY to the designated
folder (V default/BEST, GDX/ODX configurable alternates).

This is the MOTIF iteration of cosmos_node_worker for grok/gem:
  * O_EXCL fence is the exactly-once token (rename is not exclusive)
  * unique worker-id on fence + heartbeat + result
  * HOLD vs RESUME-GATE (expired resume_gate drains; HOLD never self-clears)
  * heartbeat live/logs/<node>_heartbeat.json every poll (pass or idle)
    with last_run_epoch (cosmos_clock.write_heartbeat)
  * NO cosmos_dispatch import (results land on disk; collector scans them)
  * NO schtasks spawn (register_node_workers.py emits the /Create plan)

Grok -> sgh-api then gw-api (explicit audited fallback).
GEM  -> gem-api.

    py -3.14 cosmos\\cosmos_node_bucket_worker.py --root <live> --node grok --once
    py -3.14 cosmos\\cosmos_node_bucket_worker.py --root <live> --node gem --loop
    py -3.14 cosmos\\cosmos_node_bucket_worker.py --root <live> --node grok --status

NO BTS import. Does not modify kernel / ledger / sched / service.
Does not edit cosmos_dispatch.py / cosmos_collector.py / cosmos_index.py.
"""
from __future__ import annotations

import argparse
import errno
import json
import os
import sys
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_clock import (  # noqa: E402
    acquire_lock, atomic_json, heartbeat_age_s, pid_alive, query_task,
    read_heartbeat, write_heartbeat,
)
from cosmos_paths import CosmosPaths, CosmosPathError  # noqa: E402

SCHEMA = "cosmos-node-bucket-worker/1"
DEFAULT_INTERVAL_S = 15.0
FRESH_S = 90.0
DROP_SUFFIXES = {".json", ".txt"}
SKIP_DIR_NAMES = {
    "processed", "failed", "running", "claimed", "__pycache__", "_delme",
}
DEST_KEYS = ("V", "GDX", "ODX")
CONFIG_NAME = "node_bucket_worker.json"
_CLAIM_LOCK = threading.Lock()

# Named return folders, NOT resolver roles (resolver refuses absolute parts).
DEFAULT_EXT_DEST = {
    "GDX": Path(r"X:\My Drive\BTS_SGH_Handoff"),
    "ODX": Path(r"C:\Users\Papa\OneDrive"),
}

# Grok/GEM only. OA stays on cosmos_node_worker / cosmos_oa_worker.
# Lock names match the incumbent daemons so two pollers cannot both hold
# the OS lock during transition. Heartbeat names follow the assignment
# (live/logs/<name>_heartbeat.json).
NODES = {
    "grok": {
        "id": "grok",
        "worker": "cosmos-grok-bucket",
        "task_name": "COSMOS Grok Worker",
        "task_logon": "COSMOS Grok Worker Logon",
        "heartbeat": "grok_heartbeat.json",
        "lock": "grok_worker.lock",
        "agent": "GROK",
        "rails": (
            {"link_id": "sgh-api", "module": "bts_sgh",
             "metered_usd": 0.02, "budget": 10.0},
            {"link_id": "gw-api", "module": "bts_gw",
             "metered_usd": 0.001, "budget": 5.0},
        ),
    },
    "gem": {
        "id": "gem",
        "worker": "cosmos-gem-bucket",
        "task_name": "COSMOS GEM Worker",
        "task_logon": "COSMOS GEM Worker Logon",
        "heartbeat": "gem_heartbeat.json",
        "lock": "gem_worker.lock",
        "agent": "GEM",
        "rails": (
            {"link_id": "gem-api", "module": "bts_gem",
             "metered_usd": 0.03, "budget": 300.0},
        ),
    },
}


class WorkerError(RuntimeError):
    """kind in {BAD_NODE, BAD_OUT, BAD_TASK, NO_DEST, NO_KEY, NO_ROOT, REPLAY}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


NODE_ALIASES = {
    "grok": "grok", "g46": "grok", "sgh": "grok", "gw": "grok",
    "gem": "gem", "gemini": "gem",
}


def canon_node(node: str) -> str:
    key = str(node or "").strip().lower()
    if key not in NODE_ALIASES:
        raise WorkerError("BAD_NODE",
                          f"unknown node {node!r}; want grok|gem")
    return NODE_ALIASES[key]


def node_spec(node: str) -> dict:
    return NODES[canon_node(node)]


def make_worker_id(node: str) -> str:
    return f"{canon_node(node)}-{os.getpid()}-{uuid.uuid4().hex[:8]}"


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat()


def _stamp_file() -> str:
    now = datetime.now().astimezone()
    return now.strftime("%Y%m%dT%H%M%S") + now.strftime("%z").replace(":", "")


def _parse_iso(value) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def load_config(paths: CosmosPaths) -> dict:
    cfg = {"interval_s": DEFAULT_INTERVAL_S, "dest": {}}
    p = paths.config(CONFIG_NAME)
    if not p.exists():
        return cfg
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        cfg["_config_error"] = f"unreadable {p}"
        return cfg
    if not isinstance(raw, dict):
        return cfg
    if raw.get("interval_s") is not None:
        try:
            cfg["interval_s"] = float(raw["interval_s"])
        except (TypeError, ValueError):
            pass
    dest = raw.get("dest")
    if isinstance(dest, dict):
        cfg["dest"] = {str(k).upper(): str(v) for k, v in dest.items()}
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


def pause_decision(paused: dict | None, *, now: datetime | None = None) -> dict:
    """HOLD never self-clears. Expired RESUME-GATE drains (WD2 owns delete)."""
    if paused is None:
        return {"drain": True, "state": "RUNNING", "mode": None, "expired": False}
    state = str(paused.get("state") or "PAUSED").upper()
    if state == "RUNNING":
        return {"drain": True, "state": "RUNNING",
                "mode": paused.get("mode"), "expired": False}
    mode = str(paused.get("mode") or "hold").strip().lower().replace("-", "_")
    if mode == "resume_gate":
        auto = _parse_iso(paused.get("auto_resume_at"))
        if auto is None:
            return {"drain": False, "state": "PAUSED", "mode": "resume_gate",
                    "expired": False, "auto_resume_at": paused.get("auto_resume_at"),
                    "why": "resume_gate missing/unparseable auto_resume_at"}
        stamp = now or datetime.now().astimezone()
        if auto.tzinfo is None:
            auto = auto.replace(tzinfo=stamp.tzinfo)
        if stamp >= auto:
            return {"drain": True, "state": "RUNNING", "mode": "resume_gate",
                    "expired": True, "auto_resume_at": paused.get("auto_resume_at")}
        return {"drain": False, "state": "PAUSED", "mode": "resume_gate",
                "expired": False, "auto_resume_at": paused.get("auto_resume_at")}
    return {"drain": False, "state": "PAUSED", "mode": "hold", "expired": False}


def bucket_dir(paths: CosmosPaths, node: str) -> Path:
    d = paths.role("root", "buckets", canon_node(node))
    d.mkdir(parents=True, exist_ok=True)
    for sub in ("processed", "failed", "running", "claimed"):
        (d / sub).mkdir(parents=True, exist_ok=True)
    return d


def v_returns(paths: CosmosPaths, node: str) -> Path:
    d = paths.role("root", "returns", canon_node(node))
    d.mkdir(parents=True, exist_ok=True)
    return d


def canon_out(value: str | None, default: str = "V") -> str:
    raw = str(value or default or "V").strip().upper()
    raw = raw.replace(":", "").replace("/", "").replace("\\", "")
    if raw not in DEST_KEYS:
        raise WorkerError("BAD_OUT", f"out {value!r} is not V|GDX|ODX")
    return raw


def dest_dir(paths: CosmosPaths, node: str, dest_key: str,
             cfg: dict | None = None) -> Path:
    """Resolve the designated folder. V default is live/returns/<node> (on V:\\)."""
    key = canon_out(dest_key)
    node = canon_node(node)
    cfg = cfg or {}
    override = (cfg.get("dest") or {}).get(key)
    if key == "V" and not override:
        return v_returns(paths, node)
    if override:
        base = Path(override)
    elif key in DEFAULT_EXT_DEST:
        base = DEFAULT_EXT_DEST[key]
    else:
        raise WorkerError("NO_DEST", f"no dest configured for {key}")
    if not base.exists() or not base.is_dir():
        raise WorkerError("NO_DEST",
                          f"{key} dest is missing or not a directory: {base}")
    d = base / "COSMOS" / "returns" / node
    try:
        d.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise WorkerError("NO_DEST", f"{key} dest unwritable {d}: {e}") from e
    return d


def list_drop_files(bucket: Path) -> list[Path]:
    files: list[Path] = []
    if not bucket.exists():
        return files
    try:
        kids = list(bucket.iterdir())
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


def parse_task(path: Path, default_out: str = "V") -> dict:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as e:
        raise WorkerError("BAD_TASK", f"drop unreadable {path}: {e}") from e
    suffix = path.suffix.lower()
    raw: dict = {}
    prompt = ""
    out = default_out
    task_id = path.stem
    if suffix == ".json":
        try:
            obj = json.loads(text) if text.strip() else {}
        except ValueError as e:
            raise WorkerError("BAD_TASK", f"drop is not JSON: {path}: {e}") from e
        if not isinstance(obj, dict):
            raise WorkerError("BAD_TASK", f"drop is not a JSON object: {path}")
        raw = obj
        prompt = str(obj.get("prompt") or obj.get("task")
                     or obj.get("assignment") or obj.get("text") or "").strip()
        if obj.get("out"):
            out = canon_out(obj.get("out"), default_out)
        if obj.get("id"):
            task_id = str(obj["id"]).strip() or task_id
    else:
        prompt = text.strip()
        raw = {"prompt": prompt, "source": "txt"}
    if not prompt:
        raise WorkerError("BAD_TASK", f"drop missing prompt: {path}")
    return {
        "prompt": prompt,
        "out": canon_out(out, default_out),
        "id": task_id,
        "raw": raw,
        "path": str(path),
        "name": path.name,
    }


def fence_path(bucket: Path, name: str) -> Path:
    d = bucket / "claimed"
    d.mkdir(parents=True, exist_ok=True)
    return d / (name + ".fence")


def _exists_error(exc: OSError) -> bool:
    if isinstance(exc, FileExistsError):
        return True
    if getattr(exc, "winerror", None) in (80, 183):
        return True
    return exc.errno in (errno.EEXIST,)


def _fence_stale(fp: Path) -> bool:
    if not fp.exists():
        return False
    try:
        rec = json.loads(fp.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return True
    if not isinstance(rec, dict):
        return True
    try:
        pid = int(rec.get("pid") or 0)
    except (TypeError, ValueError):
        return True
    return not pid_alive(pid)


def write_fence(fp: Path, rec: dict) -> dict:
    """O_EXCL create. Exactly one winner. Existing live fence -> REPLAY."""
    fp.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY
    try:
        fd = os.open(str(fp), flags, 0o644)
    except OSError as e:
        if _exists_error(e):
            raise WorkerError("REPLAY", f"fence already held for {fp.name}") from e
        raise
    try:
        os.write(fd, json.dumps(rec, indent=1, default=str).encode("utf-8"))
    finally:
        os.close(fd)
    rec["fence_path"] = str(fp)
    return rec


def claim_drop(bucket: Path, drop: Path, worker_id: str) -> dict | None:
    """Exactly-once claim. O_EXCL fence first, then rename into running/.

    Lost races return None — never double-invoke a rail. A fence whose
    pid is dead AND whose drop is still in the inbox is released so a
    crash-after-fence cannot starve the bucket (anti-loss).
    """
    with _CLAIM_LOCK:
        if not drop.exists() or not drop.is_file():
            return None
        fp = fence_path(bucket, drop.name)
        if fp.exists():
            if drop.exists() and _fence_stale(fp):
                try:
                    fp.unlink()
                except OSError:
                    return None
            else:
                return None
        rec = {
            "schema": SCHEMA,
            "worker_id": worker_id,
            "pid": os.getpid(),
            "claimed_at": _iso_now(),
            "drop": drop.name,
            "bucket": str(bucket),
        }
        try:
            rec = write_fence(fp, rec)
        except WorkerError as e:
            if e.kind == "REPLAY":
                return None
            raise
        running = bucket / "running"
        running.mkdir(parents=True, exist_ok=True)
        dest = running / drop.name
        try:
            os.rename(str(drop), str(dest))
        except OSError:
            if drop.exists():
                try:
                    fp.unlink()
                except OSError:
                    pass
            return None
        rec["claimed_path"] = str(dest)
        try:
            atomic_json(fp, rec)
        except OSError:
            pass
        return rec


def stage_drop(bucket: Path, drop_path: Path, stamp: str,
               *, failed: bool = False) -> Path:
    """Move a handled drop into processed/ or failed/. Never delete."""
    dest_dir_ = bucket / ("failed" if failed else "processed")
    dest_dir_.mkdir(parents=True, exist_ok=True)
    dest = dest_dir_ / f"{stamp}_{drop_path.name}"
    n = 1
    while dest.exists():
        n += 1
        dest = dest_dir_ / f"{stamp}_{n}_{drop_path.name}"
    try:
        drop_path.replace(dest)
        return dest
    except OSError:
        try:
            dest.write_bytes(drop_path.read_bytes())
        except OSError:
            return dest
        parked = drop_path.with_name(drop_path.name + ".parked")
        try:
            drop_path.replace(parked)
        except OSError:
            pass
        return dest


def _open_spend(paths: CosmosPaths, writer: str):
    from cosmos_ledger import Ledger
    from cosmos_spend import SpendGate
    keyfile = paths.config("install_key.bin")
    if not keyfile.exists():
        raise WorkerError(
            "NO_KEY",
            f"no install key at {keyfile} - worker refuses rather than "
            f"inventing authentication material")
    key = keyfile.read_bytes()
    ledger = Ledger(paths.ledger("authority.jsonl"), key, writer)
    return ledger, SpendGate(ledger)


def execute_via_rail(paths: CosmosPaths, spec: dict, prompt: str,
                     *, rail_call=None) -> dict:
    """Spend-gated, ledgered dispatch through the node's COSMOS rails.

    `rail_call` is a test seam. Live path uses cosmos_node_rails.NodeRail.
    This module never imports bts_*.
    """
    if rail_call is not None:
        r = rail_call(prompt)
        if not isinstance(r, dict):
            r = {"ok": True, "kind": "API", "text": str(r),
                 "model": "injected", "usd": None, "link_id": "injected"}
        r.setdefault("kind", "API")
        r.setdefault("link_id", "injected")
        r.setdefault("model", r.get("node") or "injected")
        return r

    from cosmos_node_rails import NodeRail
    from cosmos_spend import SpendError

    ledger, spend = _open_spend(paths, spec["worker"])
    last: dict | None = None
    for rail in spec["rails"]:
        lid = rail["link_id"]
        if lid not in spend.audit()["rails"]:
            spend.set_budget(lid, rail["budget"])
        adapter = NodeRail(rail["module"], metered_usd=rail["metered_usd"])
        ledger.append("RAIL_DISPATCH", {
            "link_id": lid, "kind": "API",
            "src": spec["worker"], "dst": "models",
            "node": spec["id"],
        })
        try:
            result = spend.guarded_call(
                lid, rail["metered_usd"],
                lambda a=adapter: a.dispatch({"prompt": prompt}),
            )
        except SpendError as e:
            ledger.append("RAIL_RESULT", {
                "link_id": lid, "ok": False,
                "detail": f"spend-gated: {e}",
            })
            last = {"ok": False, "kind": "NOT_PERMITTED",
                    "detail": str(e), "link_id": lid, "model": rail["module"]}
            continue
        model = (result.get("model") or result.get("node")
                 or rail["module"])
        ledger.append("RAIL_RESULT", {
            "link_id": lid, "ok": result.get("ok"),
            "kind": result.get("kind"),
            "model": model, "usd": result.get("usd"),
        })
        bound = dict(result)
        bound["link_id"] = lid
        bound["model"] = model
        if bound.get("ok"):
            return bound
        if bound.get("kind") in ("UNREACHABLE", "SESSION_EXPIRED",
                                 "AUTH_REQUIRED"):
            ledger.append("RAIL_FALLBACK", {
                "from": lid, "reason": bound.get("kind"),
                "detail": "explicit audited fallback to next live link",
            })
            last = bound
            continue
        return bound
    return last or {
        "ok": False, "kind": "NO_LIVE_LINK",
        "detail": "all candidate rails failed or absent",
        "link_id": None, "model": None,
    }


def _result_name(task: dict, spec: dict, stamp: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "-"
                   for ch in str(task.get("id") or "task"))[:60] or "task"
    return f"{spec['id']}_{safe}_{stamp}_result.json"


def write_result_files(paths: CosmosPaths, spec: dict, rec: dict,
                       dest_key: str, cfg: dict) -> dict:
    """Write DIRECTLY to the designated folder. V is always landed too."""
    name = rec["result_name"]
    v_path = v_returns(paths, spec["id"]) / name
    atomic_json(v_path, rec)
    rec["v_path"] = str(v_path)
    rec["result_path"] = str(v_path)
    rec["out_landed"] = "V"
    if dest_key == "V":
        return rec
    try:
        d = dest_dir(paths, spec["id"], dest_key, cfg)
        p = d / name
        atomic_json(p, rec)
        rec["dest_path"] = str(p)
        rec["result_path"] = str(p)
        rec["out_landed"] = dest_key
        atomic_json(v_path, rec)
    except (WorkerError, OSError) as e:
        rec["dest_error"] = str(e)
        rec["out_landed"] = "V"
        atomic_json(v_path, rec)
    return rec


def process_drop(paths: CosmosPaths, spec: dict, drop_path: Path,
                 default_out: str = "V", cfg: dict | None = None,
                 *, rail_call=None, worker_id: str | None = None) -> dict | None:
    """Claim (O_EXCL), execute via the node's rail, write dest. None = lost race."""
    t0 = time.time()
    cfg = cfg if cfg is not None else load_config(paths)
    stamp = _stamp_file()
    pickup_at = _iso_now()
    bucket = bucket_dir(paths, spec["id"])
    wid = worker_id or make_worker_id(spec["id"])
    claimed = claim_drop(bucket, drop_path, wid)
    if claimed is None:
        return None

    claimed_path = Path(claimed["claimed_path"])
    try:
        task = parse_task(claimed_path, default_out=default_out)
    except WorkerError as e:
        failed = stage_drop(bucket, claimed_path, stamp, failed=True)
        return {"ok": False, "kind": e.kind, "error": str(e),
                "drop_path": str(drop_path), "processed_drop": str(failed),
                "worker_id": wid, "fence_path": claimed.get("fence_path"),
                "elapsed_s": round(time.time() - t0, 3)}

    dest_key = task["out"]
    result_name = _result_name(task, spec, stamp)
    rec = {
        "schema": SCHEMA,
        "ok": False,
        "node": spec["id"],
        "worker": spec["worker"],
        "worker_id": wid,
        "agent": spec["agent"],
        "task_id": task["id"],
        "prompt": task["prompt"],
        "out": dest_key,
        "result_name": result_name,
        "drop_path": str(drop_path),
        "drop_name": drop_path.name,
        "claimed_path": str(claimed_path),
        "fence_path": claimed.get("fence_path"),
        "pickup_at": pickup_at,
    }
    rail = execute_via_rail(paths, spec, task["prompt"], rail_call=rail_call)
    text = str(rail.get("text") or "")
    nonempty = bool(text.strip())
    rec["rail"] = {
        "ok": bool(rail.get("ok")),
        "kind": rail.get("kind"),
        "link_id": rail.get("link_id"),
        "model": rail.get("model") or rail.get("node"),
        "usd": rail.get("usd"),
        "text": text,
        "detail": rail.get("detail"),
        "node": rail.get("node"),
    }
    rec["ok"] = bool(rail.get("ok") and nonempty)
    if not rec["ok"]:
        rec["error"] = (
            rail.get("detail") or rail.get("kind") or "RAIL_FAILED"
            if not rail.get("ok") else "EMPTY_OUTPUT")
        rec["done_why"] = "empty_stdout" if not nonempty else "rail_failed"
    else:
        rec["done_why"] = "nonempty_stdout"
    rec["elapsed_s"] = round(time.time() - t0, 3)
    rec = write_result_files(paths, spec, rec, dest_key, cfg)
    rec["processed_drop"] = str(stage_drop(
        bucket, claimed_path, stamp, failed=not rec["ok"]))
    atomic_json(Path(rec["v_path"]), rec)
    if rec.get("dest_path") and rec.get("out_landed") != "V":
        try:
            atomic_json(Path(rec["dest_path"]), rec)
        except OSError:
            pass
    return rec


def _job_summary(j: dict) -> dict:
    return {
        "ok": j.get("ok"),
        "task_id": j.get("task_id"),
        "worker_id": j.get("worker_id"),
        "result_path": j.get("result_path"),
        "v_path": j.get("v_path"),
        "out": j.get("out"),
        "out_landed": j.get("out_landed"),
        "model": (j.get("rail") or {}).get("model"),
        "link_id": (j.get("rail") or {}).get("link_id"),
        "usd": (j.get("rail") or {}).get("usd"),
        "fence_path": j.get("fence_path"),
        "error": j.get("error"),
    }


def poll_once(root: str, node: str, polls: int = 0,
              interval_s: float | None = None, default_out: str = "V",
              *, drain: bool | None = None, rail_call=None,
              worker_id: str | None = None) -> dict:
    """One tick. Heartbeat always. HOLD / unexpired RESUME-GATE => pick up NOTHING."""
    spec = node_spec(node)
    try:
        paths = CosmosPaths(root)
    except CosmosPathError as e:
        raise WorkerError("NO_ROOT", str(e)) from e
    cfg = load_config(paths)
    interval = (interval_s if interval_s is not None
                else float(cfg.get("interval_s") or DEFAULT_INTERVAL_S))
    hb_path = paths.logs(spec["heartbeat"])
    bucket = bucket_dir(paths, spec["id"])
    wid = worker_id or make_worker_id(spec["id"])
    paused = pause_flag(paths)
    decision = pause_decision(paused)
    do_drain = decision["drain"] if drain is None else bool(drain)
    extra = {
        "schema": SCHEMA,
        "tick": "poll",
        "state": "RUNNING",
        "node": spec["id"],
        "worker_id": wid,
        "pause_present": paused is not None,
        "pause_mode": decision.get("mode"),
        "pause_expired": bool(decision.get("expired")),
        "bucket": str(bucket),
        "out_default": canon_out(default_out),
        "tree_id": paths.sentinel.tree_id,
        "no_bts": True,
    }
    if paused is not None:
        extra["auto_resume_at"] = paused.get("auto_resume_at")
        extra["pause"] = {
            "reason": paused.get("reason"),
            "set_by": paused.get("set_by"),
            "set_at": paused.get("set_at"),
            "path": paused.get("path"),
            "mode": decision.get("mode"),
        }
    if not do_drain:
        extra["state"] = "PAUSED"
        extra["tick"] = "paused"
        extra["picked_this_tick"] = 0
        extra["jobs"] = []
        extra["claimed_by"] = []
        hb = write_heartbeat(hb_path, spec["worker"], extra=extra,
                             polls=polls, interval_s=interval)
        extra["ok"] = True
        extra["heartbeat"] = hb
        extra["heartbeat_path"] = str(hb_path)
        return extra

    if decision.get("expired"):
        extra["tick"] = "resume_gate_expired"

    write_heartbeat(hb_path, spec["worker"], extra={**extra, "tick": "poll"},
                    polls=polls, interval_s=interval)

    jobs = []
    errors = []
    skipped = 0
    drops = list_drop_files(bucket)
    extra["drops_seen"] = len(drops)
    extra["drop_names"] = [p.name for p in drops]
    for dp in drops[:1]:
        extra["tick"] = "busy"
        extra["busy_drop"] = dp.name
        write_heartbeat(hb_path, spec["worker"], extra=extra,
                        polls=polls, interval_s=interval)
        try:
            rec = process_drop(
                paths, spec, dp, default_out=default_out, cfg=cfg,
                rail_call=rail_call, worker_id=wid)
            if rec is None:
                skipped += 1
            else:
                jobs.append(rec)
        except WorkerError as e:
            errors.append({"drop": str(dp), "kind": e.kind, "error": str(e)})
        except Exception as e:  # noqa: BLE001
            errors.append({"drop": str(dp),
                           "kind": type(e).__name__, "error": str(e)})
    extra["picked_this_tick"] = len(jobs)
    extra["skipped_this_tick"] = skipped
    extra["jobs"] = [_job_summary(j) for j in jobs]
    extra["claimed_by"] = [j.get("worker_id") for j in jobs]
    extra["errors"] = errors
    extra["tick"] = ("drained" if jobs else "idle")
    extra["ok"] = (not errors) and (all(j.get("ok") for j in jobs) if jobs else True)
    extra["state"] = "RUNNING"
    hb = write_heartbeat(hb_path, spec["worker"], extra=extra,
                         polls=polls, interval_s=interval)
    extra["heartbeat"] = hb
    extra["heartbeat_path"] = str(hb_path)
    return extra


def loop(root: str, node: str, interval_s: float,
         default_out: str = "V") -> int:
    spec = node_spec(node)
    paths = CosmosPaths(root)
    out_path = paths.logs(f"{spec['id']}_bucket.out")
    err_path = paths.logs(f"{spec['id']}_bucket.err")
    lock_path = paths.logs(spec["lock"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    log_fh = open(out_path, "a", encoding="utf-8", buffering=1)
    sys.stdout = log_fh
    sys.stderr = log_fh
    fd = acquire_lock(lock_path)
    if fd is None:
        rec = read_heartbeat(paths.logs(spec["heartbeat"]))
        age = heartbeat_age_s(rec)
        pid = (rec or {}).get("pid")
        if age is not None and age < FRESH_S and pid_alive(int(pid or 0)):
            print(json.dumps({"already_running": True, "pid": pid,
                              "age_s": round(age, 3),
                              "node": spec["id"]}), flush=True)
            return 0
        print(f"{spec['id']} worker lock held and heartbeat not fresh - refusing",
              flush=True)
        return 2
    polls = 0
    wid = make_worker_id(spec["id"])
    print(json.dumps({"loop": True, "pid": os.getpid(), "node": spec["id"],
                      "worker_id": wid, "interval_s": interval_s},
                     indent=1), flush=True)
    try:
        while True:
            polls += 1
            try:
                poll_once(root, spec["id"], polls=polls, interval_s=interval_s,
                          default_out=default_out, worker_id=wid)
            except Exception:
                import traceback
                tb = traceback.format_exc()
                try:
                    err_path.write_text(tb, encoding="utf-8")
                except OSError:
                    pass
                try:
                    write_heartbeat(
                        paths.logs(spec["heartbeat"]), spec["worker"],
                        extra={"tick": "error", "state": "ERROR",
                               "error": tb[-500:], "node": spec["id"],
                               "worker_id": wid},
                        polls=polls, interval_s=interval_s)
                except OSError:
                    pass
            time.sleep(interval_s)
    finally:
        os.close(fd)
    return 0


def status_probe(root: str, node: str) -> dict:
    spec = node_spec(node)
    paths = CosmosPaths(root)
    hb = paths.logs(spec["heartbeat"])
    rec = read_heartbeat(hb)
    age = heartbeat_age_s(rec)
    paused = pause_flag(paths)
    decision = pause_decision(paused)
    bucket = paths.role("root", "buckets", spec["id"])
    n = 0
    if bucket.exists():
        n = len(list_drop_files(bucket))
    return {
        "node": spec["id"],
        "path": str(hb),
        "age_s": age,
        "heartbeat": rec,
        "worker_id": (rec or {}).get("worker_id"),
        "pause_present": paused is not None,
        "pause_decision": decision,
        "pause": paused,
        "bucket": str(bucket),
        "drops_waiting": n,
        "task": query_task(spec["task_name"]),
        "fresh": age is not None and age < FRESH_S,
    }


def build_parser(prog: str | None = None) -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog=prog or "cosmos_node_bucket_worker")
    ap.add_argument("--root", required=True)
    ap.add_argument("--node", required=True, choices=sorted(NODES))
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--out", default="V", help="V (default, BEST) | GDX | ODX")
    ap.add_argument("--interval", type=float, default=DEFAULT_INTERVAL_S)
    return ap


def run_cli(argv: list[str] | None = None) -> int:
    ap = build_parser()
    a = ap.parse_args(argv)
    spec = node_spec(a.node)
    default_out = canon_out(a.out)
    if a.status:
        rec = status_probe(a.root, spec["id"])
        print(json.dumps(rec, indent=1, default=str))
        return 0 if rec.get("fresh") else 2
    if a.once:
        r = poll_once(a.root, spec["id"], interval_s=a.interval,
                      default_out=default_out, drain=True)
        out = {k: r[k] for k in r if k != "heartbeat"}
        print(json.dumps(out, indent=1, default=str))
        return 0 if r.get("ok") else 2
    return loop(a.root, spec["id"], a.interval, default_out=default_out)


def main() -> int:
    return run_cli()


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
