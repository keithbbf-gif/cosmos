#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_discover - permanent hourly mesh-hands discovery (rebuildable projection).

Mechanical inventory + PATH/local-HTTP probe of mesh hands. NO model call, NO
spend, NO COSMOS core (kernel/ledger/sched/service) writes. COW still verifies
before a candidate is promoted into docs/MESH_ADDITIONS.md.

Sources (ingress, not COSMOS roles):
  * Repo research: docs/research/**/*_HANDS.md  (scout returns)
  * Closed probe table of CLI binaries + a few local HTTP endpoints

Store:
  * live/state/discovery/hands.json            - rebuildable projection
  * live/logs/mesh_discovery_heartbeat.json    - written EVERY tick

Launch (survives reboot; hourly one-shot, not a daemon):

    py -3.14 cosmos\\cosmos_discover.py --root V:\\A\\Ai\\COSMOS\\live --once
    py -3.14 cosmos\\cosmos_discover.py --root ... --standup
    py -3.14 cosmos\\cosmos_discover.py --root ... --status

--standup registers Windows scheduled task "COSMOS Mesh Discovery" /sc HOURLY.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone as dt_timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_paths import CosmosPaths, CosmosPathError  # noqa: E402
from cosmos_clock import pythonw_exe  # noqa: E402

WORKER = "cosmos-discover"
TASK_NAME = "COSMOS Mesh Discovery"
HEARTBEAT_NAME = "mesh_discovery_heartbeat.json"
PROJECTION_NAME = "hands.json"
SCHEMA = "cosmos-discover/1"
FRESH_S = 3900.0  # hourly + 5 min slack
CREATE_NO_WINDOW = 0x08000000  # windowless short-lived schtasks spawns

# Closed probe table. A binary on PATH is evidence the hand EXISTS on this
# machine; absence is not a fault. HTTP probes are local-only (no vendor spend).
PROBE_CMDS = (
    ("py", "cli"),
    ("python", "cli"),
    ("git", "cli"),
    ("grok", "cli"),
    ("claude", "cli"),
    ("cursor", "cli"),
    ("gh", "cli"),
    ("glab", "cli"),
    ("ollama", "cli"),
    ("npx", "cli"),
    ("node", "cli"),
    ("uv", "cli"),
    ("ffmpeg", "cli"),
    ("rclone", "cli"),
    ("restic", "cli"),
    ("rg", "cli"),
    ("fd", "cli"),
    ("yt-dlp", "cli"),
    ("pandoc", "cli"),
    ("aider", "cli"),
    ("winget", "cli"),
    ("pwsh", "cli"),
    ("tesseract", "cli"),
    ("ocrmypdf", "cli"),
    ("markitdown", "cli"),
    ("opencode", "cli"),
    ("goose", "cli"),
    ("copilot", "cli"),
    ("tailscale", "cli"),
)

HTTP_PROBES = (
    ("ollama-http", "http://127.0.0.1:11434/api/version", 1.5),
)


def repo_tree() -> Path:
    return Path(__file__).resolve().parent.parent


def default_research_dir() -> Path:
    return repo_tree() / "docs" / "research"


def plan_once_argv(root: str) -> list[str]:
    return ["py", "-3.14", str(Path(__file__).resolve()),
            "--root", str(Path(root).resolve()), "--once"]


def plan_task_argv(root: str) -> list[str]:
    """schtasks /create plan. HOURLY one-shot. No /rl highest: current-user
    registration should not need elevation."""
    from cosmos_clock import tr_cmdline
    tr = tr_cmdline(Path(__file__).resolve(), root, "--once")
    return ["schtasks", "/create", "/tn", TASK_NAME, "/tr", tr,
            "/sc", "HOURLY", "/mo", "1", "/f"]


def _iso(ts: float | None = None) -> str:
    if ts is None:
        return datetime.now().astimezone().isoformat(timespec="seconds")
    return datetime.fromtimestamp(ts).astimezone().isoformat(timespec="seconds")


def inventory_hands(research: Path) -> list[dict]:
    """Scout returns on disk. Rebuildable; files are truth."""
    rows = []
    if not research.is_dir():
        return rows
    for p in sorted(research.rglob("*_HANDS.md")):
        try:
            st = p.stat()
        except OSError:
            continue
        maker = p.stem[: -len("_HANDS")] if p.stem.upper().endswith("_HANDS") else p.stem
        rows.append({
            "maker": maker,
            "path": str(p),
            "bytes": int(st.st_size),
            "mtime": float(st.st_mtime),
            "mtime_iso": _iso(st.st_mtime),
        })
    return rows


def probe_cmds() -> list[dict]:
    out = []
    for name, kind in PROBE_CMDS:
        found = shutil.which(name)
        rec = {"id": name, "kind": kind, "present": bool(found)}
        if found:
            rec["path"] = found
        out.append(rec)
    return out


def probe_http() -> list[dict]:
    out = []
    for hid, url, timeout_s in HTTP_PROBES:
        rec = {"id": hid, "kind": "http", "url": url, "present": False}
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                body = resp.read(256)
                rec["present"] = 200 <= int(resp.status) < 300
                rec["status"] = int(resp.status)
                rec["body_head"] = body.decode("utf-8", errors="replace")[:120]
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
            rec["error"] = f"{type(e).__name__}: {e}"[:200]
        out.append(rec)
    return out


def bind(root: str, research=None) -> dict:
    paths = CosmosPaths(root)
    logs = paths.logs()
    logs.mkdir(parents=True, exist_ok=True)
    state = paths.state("discovery")
    state.mkdir(parents=True, exist_ok=True)
    research_dir = Path(research) if research else default_research_dir()
    return {
        "paths": paths,
        "heartbeat": logs / HEARTBEAT_NAME,
        "projection": state / PROJECTION_NAME,
        "research": research_dir,
    }


def read_heartbeat(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return None


def heartbeat_age_s(rec: dict | None, now: float | None = None) -> float | None:
    if not rec or "last_run_epoch" not in rec:
        return None
    return (now if now is not None else time.time()) - float(rec["last_run_epoch"])


def write_heartbeat(path: Path, extra: dict | None = None) -> dict:
    now = datetime.now().astimezone()
    rec = {
        "last_run": now.isoformat(timespec="seconds"),
        "last_run_epoch": int(now.timestamp()),
        "last_run_utc": now.astimezone(dt_timezone.utc).isoformat(timespec="seconds"),
        "worker": WORKER,
        "pid": os.getpid(),
        "_readme": (
            "Written on EVERY tick. If last_run_epoch is older than ~3900s "
            "this COSMOS mesh-discovery scheduled task is what failed. "
            "COMPARE USING last_run_epoch."
        ),
    }
    if extra:
        rec.update(extra)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    tmp.replace(path)
    return rec


def poll_once(root: str, research=None) -> dict:
    """One inventory+probe tick. Always writes heartbeat + projection."""
    bound = bind(root, research=research)
    t0 = time.time()
    write_heartbeat(bound["heartbeat"], extra={"tick": "poll"})
    hands = inventory_hands(bound["research"])
    cmds = probe_cmds()
    http = probe_http()
    present = [x["id"] for x in cmds + http if x.get("present")]
    absent = [x["id"] for x in cmds + http if not x.get("present")]
    projection = {
        "schema": SCHEMA,
        "written_at": _iso(),
        "written_epoch": int(time.time()),
        "research_dir": str(bound["research"]),
        "hands_md_count": len(hands),
        "hands_md": hands,
        "probes": cmds + http,
        "present": present,
        "absent": absent,
        "_readme": (
            "Rebuildable projection. Scout files in docs/research/*_HANDS.md "
            "and PATH/local-HTTP probes are truth. COW promotes candidates; "
            "this file does not."
        ),
    }
    bound["projection"].write_text(
        json.dumps(projection, indent=1, default=str), encoding="utf-8")
    hb = write_heartbeat(bound["heartbeat"], extra={
        "tick": "done",
        "hands_md_count": len(hands),
        "present_count": len(present),
        "absent_count": len(absent),
        "projection": str(bound["projection"]),
        "research_dir": str(bound["research"]),
        "elapsed_s": round(time.time() - t0, 3),
        "present": present,
    })
    return {"heartbeat": hb, "projection": projection,
            "path": str(bound["heartbeat"])}


def install_task(root: str) -> dict:
    argv = plan_task_argv(root)
    try:
        p = subprocess.run(argv, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=60)
    except OSError as e:
        return {"argv": argv, "rc": -1, "ok": False, "out": str(e),
                "note": "schtasks could not run at all",
                "keith_cmd": subprocess.list2cmdline(argv),
                "needs_elevation": False}
    out = ((p.stdout or "") + (p.stderr or "")).strip()
    low = out.lower()
    denied = p.returncode != 0 and ("access is denied" in low
                                    or "access denied" in low
                                    or "elevat" in low
                                    or "denied" in low)
    rec = {
        "argv": argv, "rc": p.returncode, "ok": p.returncode == 0, "out": out,
        "needs_elevation": denied,
        "keith_cmd": subprocess.list2cmdline(argv) if p.returncode != 0 else None,
        "note": ("registered: runs every hour" if p.returncode == 0 else
                 "FAILED - schtasks returned nonzero"),
    }
    if p.returncode == 0:
        r = subprocess.run(["schtasks", "/run", "/tn", TASK_NAME],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=30,
                           creationflags=(CREATE_NO_WINDOW if os.name == "nt" else 0))
        rec["run_rc"] = r.returncode
        rec["run_out"] = ((r.stdout or "") + (r.stderr or "")).strip()
        rec["run_ok"] = r.returncode == 0
    return rec


def standup(root: str) -> dict:
    """Register the hourly task and prove a tick landed a heartbeat."""
    bound = bind(root)
    t0 = time.time()
    task = install_task(root)
    # Always do one in-process tick so proof does not depend on Task Scheduler
    # actually launching the child before we look (hourly /run can be slow).
    tick = poll_once(root)
    rec = read_heartbeat(bound["heartbeat"])
    age = heartbeat_age_s(rec)
    proof_ok = (rec is not None and age is not None and age < 60
                and float(rec.get("last_run_epoch") or 0) >= t0 - 5)
    return {
        "started": "schtasks" if task.get("ok") else "in-process-tick",
        "task": task,
        "tick": {"hands_md_count": tick["heartbeat"].get("hands_md_count"),
                 "present_count": tick["heartbeat"].get("present_count"),
                 "projection": tick["heartbeat"].get("projection")},
        "proof": {"ok": proof_ok, "heartbeat": rec, "age_s": age,
                  "path": str(bound["heartbeat"])},
        "heartbeat_path": str(bound["heartbeat"]),
        "keith_cmd": task.get("keith_cmd") if (
            task.get("needs_elevation") or not task.get("ok")) else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_discover")
    ap.add_argument("--root", required=True,
                    help="COSMOS runtime root (sentinel-verified)")
    ap.add_argument("--research", default=None,
                    help="research dir (default <repo>/docs/research)")
    ap.add_argument("--once", action="store_true",
                    help="one inventory+probe tick then exit")
    ap.add_argument("--standup", action="store_true",
                    help="register hourly schtasks and run one tick")
    ap.add_argument("--status", action="store_true",
                    help="print heartbeat age; exit 0 if fresh (<3900s)")
    a = ap.parse_args()

    if a.status:
        bound = bind(a.root, research=a.research)
        rec = read_heartbeat(bound["heartbeat"])
        age = heartbeat_age_s(rec)
        print(json.dumps({"path": str(bound["heartbeat"]), "age_s": age,
                          "heartbeat": rec,
                          "projection": str(bound["projection"])}, indent=1))
        return 0 if age is not None and age < FRESH_S else 2

    if a.standup:
        r = standup(a.root)
        print(json.dumps(r, indent=1, default=str))
        return 0 if (r.get("proof") or {}).get("ok") and (
            r.get("task") or {}).get("ok") else 2

    # --once, or a bare --root: what the hourly task invokes
    r = poll_once(a.root, research=a.research)
    print(json.dumps({"ok": True,
                      "heartbeat": str(r["path"]),
                      "hands_md_count": r["heartbeat"].get("hands_md_count"),
                      "present": r["heartbeat"].get("present"),
                      "projection": r["heartbeat"].get("projection")},
                     indent=1, default=str))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CosmosPathError as e:
        print(e, file=sys.stderr)
        raise SystemExit(2)
