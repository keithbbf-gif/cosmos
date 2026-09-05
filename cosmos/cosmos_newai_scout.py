#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_newai_scout - open-ended NEW-AI discovery satellite (CLOCKS id 23).

F-26 (docs/FEATURE_MASTER.md). cosmos_discover.py inventories KNOWN hands
(closed PROBE_CMDS + docs/research/*_HANDS.md). This satellite goes OUT:
it reads spend-free catalogs (local NEW_AI_SCOUT.md plus an optional
injected/remote list) and PROPOSES candidates that are NOT in the known
set. A closed probe table is not a scout; this is the missing daemon.

PROPOSE-ONLY. Never writes COMPETENCY.toml, makers.toml, or rails.
COW wires, or not. A candidate is evidence, not a rating.

Does not modify kernel / ledger / sched / service. --plan-task /
--standup never register a task from a test; --install-task is Keith's
elevated line.

    py -3.14 cosmos\\cosmos_newai_scout.py --root <live> --once
    py -3.14 cosmos\\cosmos_newai_scout.py --root <live> --once --dry-run
    py -3.14 cosmos\\cosmos_newai_scout.py --root <live> --plan-task
    py -3.14 cosmos\\cosmos_newai_scout.py --root <live> --standup

Ingress (union, then subtract known):
  * local research: docs/research/NEW_AI_SCOUT.md (and NEW_AI_DISCOVERY.md)
  * injected catalog_text (tests; no network)
  * optional remote catalog via injected transport (default off in tests)

Known set (exclusion, never proposed):
  * *_HANDS.md stems under docs/research/
  * cosmos_discover.PROBE_CMDS ids
  * cosmos/makers.toml maker ids
  * docs/COMPETENCY.toml [nodes.*] ids when the file is readable
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
import urllib.error
import urllib.request
from datetime import datetime, timezone as dt_timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_clock import (  # noqa: E402
    create_task, plan_create, pythonw_exe, query_task, tr_cmdline,
    write_heartbeat,
)
from cosmos_discover import PROBE_CMDS  # noqa: E402
from cosmos_paths import CosmosPathError, CosmosPaths  # noqa: E402

WORKER = "cosmos-newai-scout"
SCHEMA = "cosmos-newai-scout/1"
CLOCK_ID = 23
TASK_NAME = "COSMOS NEW-AI Scout"
HEARTBEAT_NAME = "newai_scout_heartbeat.json"
PROJECTION_NAME = "newai_scout.json"
NO_WINDOW = 0x08000000 if os.name == "nt" else 0
DEFAULT_REMOTE = (
    "https://raw.githubusercontent.com/tiennm99/awesome-coding-agents/"
    "main/README.md"
)

# Numbered markdown table: `| 1 | **Pipecat** | Daily | CLI |`
# Test seam: `name: BrandNewAI-XYZ`. Bullets are NOT names — NEW_AI_DISCOVERY.md
# bold-labels (`**Cost:**`) would otherwise become candidates.
_TABLE_NAME = re.compile(
    r"^\|\s*\d+\s*\|\s*\*\*([^*]+)\*\*", re.M)
_NAME_LINE = re.compile(
    r"^name:\s*(.+)$", re.M | re.I)
# The 2026-08-31 awesome-coding-agents README names products as
# [org/repo](https://github.com/org/repo), not **bold**. Bold-only
# parsing harvested zero names on a live http=200 body (F-26 leftover).
_GH_LINK = re.compile(
    r"\[([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)\]"
    r"\(https://github\.com/\1/\2/?(?:\)|\s)")
_MIN_FOLD = 4


class ScoutError(RuntimeError):
    """kind in {NO_ROOT, BAD_CATALOG, UNREACHABLE}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def repo_tree() -> Path:
    return Path(__file__).resolve().parent.parent


def _iso(ts: float | None = None) -> str:
    if ts is None:
        return datetime.now().astimezone().isoformat(timespec="seconds")
    return datetime.fromtimestamp(ts).astimezone().isoformat(timespec="seconds")


def fold_name(s: str) -> str:
    return "".join(ch for ch in str(s or "").lower() if ch.isalnum())


def _parts(stem: str) -> list[str]:
    """HANDS stem XAI_GROK -> xaigrok, xai, grok."""
    raw = str(stem or "").strip()
    if not raw:
        return []
    bits = re.split(r"[\s_\-/]+", raw)
    out = [fold_name(raw)]
    for b in bits:
        f = fold_name(b)
        if f and f not in out:
            out.append(f)
    return [x for x in out if x]


def known_folds(*, research: Path | None, makers: Path | None,
                competency: Path | None) -> dict[str, str]:
    """fold -> source tag. Presence in this map is exclusion, not a rating."""
    known: dict[str, str] = {}

    def add(name: str, src: str) -> None:
        for f in _parts(name):
            known.setdefault(f, src)

    for cmd, _kind in PROBE_CMDS:
        add(cmd, "probe_cmds")
    if research is not None and research.is_dir():
        for p in research.rglob("*_HANDS.md"):
            stem = p.stem
            if stem.upper().endswith("_HANDS"):
                stem = stem[: -len("_HANDS")]
            add(stem, f"hands:{p.name}")
    if makers is not None and makers.is_file():
        try:
            data = tomllib.loads(makers.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError, UnicodeDecodeError):
            data = {}
        for row in data.get("makers") or []:
            if isinstance(row, dict) and row.get("id"):
                add(str(row["id"]), "makers.toml")
    if competency is not None and competency.is_file():
        try:
            raw = competency.read_text(encoding="utf-8")
        except OSError:
            raw = ""
        for m in re.finditer(r"^\[nodes\.([^\]]+)\]", raw, re.M):
            add(m.group(1), "competency.toml")
    return known


def _clean_name(name: str) -> str | None:
    name = (name or "").strip().strip("*").strip()
    if not name or name.endswith(":"):
        return None
    if name.startswith("(") and name.endswith(")"):
        return None
    folded = fold_name(name)
    if len(folded) < _MIN_FOLD:
        return None
    return name


def parse_catalog(text: str, source: str) -> list[dict]:
    """Lift candidate names from a markdown catalog. No ratings invented.

    GitHub org/repo markdown links first (the live awesome-coding-agents
    shape). Then numbered-table **bold**. Loose **bold** is not harvested
    — it is how 'Inclusion criteria' / 'Last updated' became candidates.
    """
    if not isinstance(text, str):
        raise ScoutError("BAD_CATALOG", f"catalog is {type(text).__name__}")
    seen: set[str] = set()
    rows: list[dict] = []

    def add(raw: str) -> None:
        name = _clean_name(raw)
        if name is None:
            return
        folded = fold_name(name)
        if folded in seen:
            return
        seen.add(folded)
        rows.append({
            "name": name,
            "fold": folded,
            "source": source,
        })

    for m in _GH_LINK.finditer(text):
        add(m.group(2))
    for rx in (_TABLE_NAME, _NAME_LINE):
        for m in rx.finditer(text):
            add(m.group(1) or "")
    return rows


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def default_http(url: str, timeout: int = 25) -> dict:
    """One GET. Never raises — a failure is evidence. No key is sent."""
    req = urllib.request.Request(url, method="GET", headers={
        "User-Agent": "cosmos-newai-scout/1",
        "Accept": "text/plain, text/markdown, */*",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return {"http": r.status,
                    "body": r.read(120_000).decode("utf-8", "replace"),
                    "rc": 0}
    except urllib.error.HTTPError as e:
        return {"http": e.code,
                "body": e.read(1200).decode("utf-8", "replace"),
                "rc": 1}
    except (urllib.error.URLError, OSError, ValueError) as e:
        return {"http": None, "body": f"{type(e).__name__}: {e}", "rc": None}


def path_present(name: str) -> dict:
    """PATH presence is evidence the binary exists, not that it is wired."""
    ticks = re.findall(r"`([^`]+)`", name)
    token = ticks[-1] if ticks else re.split(r"[\s/]+", name.strip())[0]
    token = re.sub(r"[^A-Za-z0-9._+-]+", "", token)
    if not token:
        return {"id": name, "present": False}
    found = shutil.which(token)
    rec = {"id": token, "kind": "cli", "present": bool(found)}
    if found:
        rec["path"] = found
    return rec


def propose(candidates: list[dict], known: dict[str, str]) -> list[dict]:
    """Subtract the known set. Remaining rows are PROPOSE, never a wiring."""
    out = []
    for c in candidates:
        folded = c.get("fold") or fold_name(c.get("name"))
        hit = known.get(folded)
        if hit:
            continue
        probe = path_present(c["name"])
        out.append({
            "name": c["name"],
            "fold": folded,
            "source": c.get("source"),
            "status": "PROPOSE",
            "path_probe": probe,
            "credential": "unknown",
            "reach": "unknown",
        })
    return out


def bind(root: str) -> dict:
    paths = CosmosPaths(root)
    logs = paths.logs()
    logs.mkdir(parents=True, exist_ok=True)
    state = paths.state("discovery")
    state.mkdir(parents=True, exist_ok=True)
    return {
        "paths": paths,
        "heartbeat": logs / HEARTBEAT_NAME,
        "projection": state / PROJECTION_NAME,
        "repo": repo_tree(),
    }


def poll_once(root: str, *, catalog_text: str | None = None,
              transport=None, live_remote: bool = False,
              dry_run: bool = False) -> dict:
    """One scout tick. Always heartbeats unless dry_run.

    catalog_text is the test seam (no network). live_remote is opt-in.
    Missing catalogs are an empty ingress, not a crash: the tick still
    writes candidates=[] so a reader can see the scout ran.
    """
    bound = bind(root)
    repo = bound["repo"]
    research = repo / "docs" / "research"
    known = known_folds(
        research=research if research.is_dir() else None,
        makers=repo / "cosmos" / "makers.toml",
        competency=repo / "docs" / "COMPETENCY.toml",
    )
    ingress: list[dict] = []
    sources: list[dict] = []

    local_files = [
        research / "NEW_AI_SCOUT.md",
        research / "NEW_AI_DISCOVERY.md",
    ]
    if catalog_text is not None:
        rows = parse_catalog(catalog_text, "injected")
        ingress.extend(rows)
        sources.append({"id": "injected", "names": len(rows), "ok": True})
    else:
        for p in local_files:
            text = _read_text(p) if p.is_file() else ""
            rows = parse_catalog(text, str(p)) if text else []
            ingress.extend(rows)
            sources.append({
                "id": p.name, "path": str(p),
                "present": p.is_file(), "names": len(rows), "ok": p.is_file(),
            })
        if live_remote:
            fetch = (transport or default_http)(DEFAULT_REMOTE)
            rc = fetch.get("rc")
            body = fetch.get("body") or ""
            if rc == 0 and body:
                rows = parse_catalog(body, DEFAULT_REMOTE)
                ingress.extend(rows)
                sources.append({
                    "id": "remote", "url": DEFAULT_REMOTE,
                    "http": fetch.get("http"), "names": len(rows), "ok": True,
                })
            else:
                sources.append({
                    "id": "remote", "url": DEFAULT_REMOTE,
                    "http": fetch.get("http"), "ok": False,
                    "kind": "UNREACHABLE",
                    "detail": body[:200],
                })

    proposed = propose(ingress, known)
    rec = {
        "schema": SCHEMA,
        "clock_id": CLOCK_ID,
        "ok": True,
        "state": "SCOUTED",
        "dry_run": bool(dry_run),
        "known_count": len(known),
        "ingress_count": len(ingress),
        "proposed_count": len(proposed),
        "proposed": proposed,
        "sources": sources,
        "tree_id": bound["paths"].sentinel.tree_id,
        "writes": 0 if dry_run else 2,
        "_readme": (
            "PROPOSE-ONLY. Candidates are not COMPETENCY rows and not rails. "
            "COW wires, or not. cosmos_discover.py still inventories known hands."
        ),
    }
    if dry_run:
        rec["heartbeat"] = HEARTBEAT_NAME
        rec["projection"] = str(bound["projection"])
        return rec

    bound["projection"].parent.mkdir(parents=True, exist_ok=True)
    tmp = bound["projection"].with_suffix(".tmp")
    tmp.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    os.replace(tmp, bound["projection"])
    extra = {
        "schema": SCHEMA,
        "tick": "done",
        "ok": True,
        "state": "SCOUTED",
        "clock_id": CLOCK_ID,
        "proposed_count": len(proposed),
        "known_count": len(known),
        "ingress_count": len(ingress),
        "projection": str(bound["projection"]),
        "tree_id": rec["tree_id"],
    }
    write_heartbeat(bound["heartbeat"], WORKER, extra=extra)
    rec["heartbeat"] = HEARTBEAT_NAME
    rec["path"] = str(bound["heartbeat"])
    rec["projection_path"] = str(bound["projection"])
    return rec


def plan_task_argv(root: str | Path) -> list[str]:
    """schtasks /create plan. HOURLY one-shot. Registers nothing."""
    tr = tr_cmdline(Path(__file__).resolve(), str(root), "--once")
    return plan_create(TASK_NAME, tr, "HOURLY")


def install_task(root: str | Path) -> dict:
    argv = plan_task_argv(root)
    try:
        p = subprocess.run(
            argv, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=60,
            creationflags=NO_WINDOW)
    except OSError as e:
        return {"ok": False, "rc": -1, "argv": argv, "out": str(e)}
    return {"ok": p.returncode == 0, "rc": p.returncode, "argv": argv,
            "out": ((p.stdout or "") + (p.stderr or "")).strip()}


def standup(root: str) -> dict:
    """Register the HOURLY --once task if missing. Never called by tests."""
    existing = query_task(TASK_NAME)
    script = Path(__file__).resolve()
    tr = tr_cmdline(script, root, "--once")
    if existing.get("ok"):
        tick_rec = poll_once(root)
        return {"started": "already", "task": existing, "tick": tick_rec,
                "keith_cmd": None, "task_name": TASK_NAME}
    task = create_task(TASK_NAME, tr, "HOURLY", run_now=False)
    return {
        "started": "schtasks" if task.get("ok") else "planned",
        "task": task,
        "keith_cmd": task.get("keith_cmd") if (
            task.get("needs_elevation") or not task.get("ok")) else None,
        "task_name": TASK_NAME,
        "proof": {"ok": True, "heartbeat": HEARTBEAT_NAME},
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="cosmos_newai_scout",
                                 description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", help="runtime root (live/)")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--live-remote", action="store_true",
                    help="GET the public catalog (spend-free). Off by default.")
    ap.add_argument("--catalog", default=None,
                    help="injected catalog file (tests; no network)")
    ap.add_argument("--plan-task", action="store_true",
                    help="print the schtasks argv, register nothing")
    ap.add_argument("--install-task", action="store_true")
    ap.add_argument("--standup", action="store_true")
    a = ap.parse_args(argv)

    if a.plan_task:
        if not a.root:
            print(json.dumps({"ok": False, "kind": "NO_ROOT",
                              "detail": "--root is required"}))
            return 2
        print(json.dumps({"task": TASK_NAME, "argv": plan_task_argv(a.root),
                          "heartbeat": HEARTBEAT_NAME, "clock_id": CLOCK_ID},
                         indent=1))
        return 0
    if a.install_task:
        if not a.root:
            print(json.dumps({"ok": False, "kind": "NO_ROOT",
                              "detail": "--root is required"}))
            return 2
        rec = install_task(a.root)
        print(json.dumps(rec, indent=1))
        return 0 if rec["ok"] else 1
    if a.standup:
        if not a.root:
            print(json.dumps({"ok": False, "kind": "NO_ROOT",
                              "detail": "--root is required"}))
            return 2
        rec = standup(a.root)
        print(json.dumps(rec, indent=1, default=str))
        return 0
    if a.once:
        if not a.root:
            print(json.dumps({"ok": False, "kind": "NO_ROOT",
                              "detail": "--root is required"}))
            return 2
        text = None
        if a.catalog:
            text = Path(a.catalog).read_text(encoding="utf-8")
        rec = poll_once(a.root, catalog_text=text, live_remote=a.live_remote,
                        dry_run=a.dry_run)
        print(json.dumps(rec, indent=1, default=str))
        return 0 if rec.get("ok") else 2
    ap.print_help()
    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CosmosPathError as e:
        print(json.dumps({"ok": False, "kind": "NO_ROOT", "error": str(e)}),
              file=sys.stderr)
        raise SystemExit(2)
    except ScoutError as e:
        print(json.dumps({"ok": False, "kind": e.kind, "error": str(e)}))
        raise SystemExit(2)
