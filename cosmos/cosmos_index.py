#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_index - living projection of tools / features / implemented.

ONE rebuildable cache. Sources are truth; state/cosmos_index.json is NEVER
authority. Human view: state/cosmos_index.html (KDash panel fragment).

Scans:
  * cosmos/*.py modules
  * docs/WISHLIST.md open/checked items
  * docs/BACKLOG.md
  * docs/MOTIF_TRACKER.md table + cow-disposition blocks
  * live/state/*_result.json recent landings
  * live/logs/*heartbeat*.json (implemented/live daemons)

Clock 13 (reserved in cosmos_own_clocks.CLOCKS) — 1-min --once light clock:

    py -3.14 cosmos\\cosmos_index.py --root V:\\A\\Ai\\COSMOS\\live --once
    py -3.14 cosmos\\cosmos_index.py --root ... --standup
    py -3.14 cosmos\\cosmos_index.py --root ... --status

Does NOT modify COSMOS core (kernel/ledger/sched/service). No bts_* import.
Idempotent: atomic replace, never append. Collector may call rebuild() each
poll (best-effort); this module is also its own clock.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone as dt_timezone
from html import escape as _html_escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_clock import (  # noqa: E402
    create_task, heartbeat_age_s, plan_create, query_task, read_heartbeat,
    tr_cmdline, write_heartbeat, atomic_json,
)
from cosmos_paths import CosmosPaths, CosmosPathError  # noqa: E402

# Clock 13 — reserved in cosmos_own_clocks.CLOCKS. Do not renumber.
CLOCK_ID = 13
WORKER = "cosmos-index"
TASK_NAME = "COSMOS Index"
HEARTBEAT_NAME = "cosmos_index_heartbeat.json"
SCHEMA = "cosmos-index/2"
PROJECTION_NAME = "cosmos_index.json"
PANEL_NAME = "cosmos_index.html"
INDEX_NAME = PROJECTION_NAME  # compat: tests / collector hook
DEFAULT_INTERVAL_S = 60.0
FRESH_S = 180.0
GATE_STAGE = 6
LANDING_CAP = 40
DISP_CAP = 12

STAGE_RE = re.compile(r"(\d+)")
CELL_STRIP = re.compile(r"[*`]+")
NON_ALNUM = re.compile(r"[^a-z0-9]+")
AGENT_RE = re.compile(r"\b(G46|Grok|COW|Cursor|SSA|Sonnet|GBt|GrokBot)\b", re.I)
DHX_LINE = re.compile(
    r"^[-*]\s*(?P<ts>20\d{2}-\d{2}-\d{2}\S*)\s*[·\-]\s*(?P<agent>[^·\-|]+?)"
    r"\s*[·\-]\s*(?P<body>.+)$"
)
FEATURE_BULLET = re.compile(
    r"^[-*]\s+\*\*(?P<name>.+?)\*\*\s*[—:\-]*\s*(?P<rest>.*)$"
)
CHECK_RE = re.compile(
    r"^[-*]\s+\[(?P<mark>[ xX~])\]\s+(?P<body>.+)$"
)
DISP_RE = re.compile(
    r"<!--\s*cow-disposition\s+(?P<stamp>\S+)\s*-->(?P<body>.*?)"
    r"<!--\s*/cow-disposition\s*-->",
    re.S | re.I,
)
CLOCK_ID_RE = re.compile(r"^CLOCK_ID\s*=\s*(\d+)\s*$", re.M)
TASK_NAME_RE = re.compile(r'^TASK_NAME\s*=\s*["\']([^"\']+)', re.M)
DOC_RE = re.compile(r'\A(?:#![^\n]*\n)?(?:#\s*-\*-.*?-\*-\s*\n)?\s*("""|\'\'\')(.*?)\1',
                    re.S)

SLUG_KEYS = (
    ("cosmosandroid", "cvm"),
    ("t1synctool", "gbridge"),
    ("makerhandssweep", "makerhands"),
    ("meshadditions", "meshadditions"),
    ("cosmoscollector", "collector"),
    ("cosmosdispatch", "dispatch"),
    ("cosmosrunner", "runner"),
    ("cursorlane", "cursor"),
    ("runtimebinding", "runtimeall"),
    ("watchdog2", "watchdog2"),
    ("gbridge", "gbridge"),
    ("cdeck", "cdeck"),
    ("cvm", "cvm"),
    ("cdm", "cdm"),
)

SLUG_NEEDLES = {
    "cdeck": ("cdeck", "c-deck"),
    "cvm": ("cvm", "cosmos-android", "cosmosandroid"),
    "cdm": ("cdm",),
    "gbridge": ("gbridge", "t1"),
    "collector": ("collector", "cosmos_collector", "cosmos_build_collector"),
    "dispatch": ("dispatch", "cosmos_dispatch", "cosmos_build_dispatch"),
    "makerhands": ("makerhands", "maker-hands", "_hands", "hands.md"),
    "meshadditions": ("meshadditions", "mesh_additions", "mesh-additions"),
    "cursor": ("cursor", "cursor_verify", "cursor_prove", "cursor_lane"),
    "runner": ("runner", "cosmos_runner", "cosmos_standup_runner"),
    "runtimeall": ("runtime binding", "runtimeall", "stage6"),
    "watchdog2": ("watchdog2", "watchdog"),
}

DAEMON_LABELS = {
    "cosmos_runner_heartbeat.json": "cosmos_runner",
    "collector_heartbeat.json": "collector",
    "mesh_discovery_heartbeat.json": "mesh_discovery",
    "watchdog2_heartbeat.json": "watchdog2",
    "motif_driver_heartbeat.json": "motif_driver",
    "cosmos_index_heartbeat.json": "cosmos_index",
    "health_clock_heartbeat.json": "health_clock",
    "rails_prober_heartbeat.json": "rails_prober",
    "spend_meter_heartbeat.json": "spend_meter",
    "drive_meter_heartbeat.json": "drive_meter",
    "cdeck_feed_heartbeat.json": "cdeck_feed",
    "backup_clock_heartbeat.json": "backup_clock",
    "ledger_verify_heartbeat.json": "ledger_verify",
    "dispatcher_heartbeat.json": "dispatcher",
}

REQUIRED_DAEMONS = ("cosmos_runner", "collector", "mesh_discovery")

LANDING_KEEP = (
    "job", "rc", "ok", "ts", "error", "summary", "elapsed_s", "state",
    "started", "agent", "status", "kind",
)


def repo_tree() -> Path:
    return Path(__file__).resolve().parent.parent


def plan_once_argv(root: str) -> list[str]:
    return ["py", "-3.14", str(Path(__file__).resolve()),
            "--root", str(Path(root).resolve()), "--once"]


def plan_task_argv(root: str) -> list[str]:
    """schtasks /create plan. 1-minute one-shot light clock. No /rl highest."""
    tr = tr_cmdline(Path(__file__).resolve(), root, "--once")
    return plan_create(TASK_NAME, tr, "minute", mo=1)


def _iso(ts: float | None = None) -> str:
    if ts is None:
        return datetime.now().astimezone().isoformat(timespec="seconds")
    try:
        return datetime.fromtimestamp(ts).astimezone().isoformat(timespec="seconds")
    except (OSError, OverflowError, ValueError):
        return datetime.fromtimestamp(0, tz=dt_timezone.utc).isoformat(
            timespec="seconds")


def _fold(text: str) -> str:
    return NON_ALNUM.sub("", str(text or "").lower())


def canonical_slug(name: str) -> str:
    folded = _fold(name)
    best = None
    best_n = -1
    for key, slug in SLUG_KEYS:
        if key in folded and len(key) > best_n:
            best, best_n = slug, len(key)
    if best:
        return best
    s = NON_ALNUM.sub("_", str(name or "").lower()).strip("_")
    return (s[:24] or "item")


def _first_int(text: str) -> int | None:
    m = STAGE_RE.search(str(text or ""))
    return int(m.group(1)) if m else None


def _clip(s: str, n: int = 72) -> str:
    s = " ".join(str(s).split())
    if len(s) <= n:
        return s
    return s[: n - 1] + "…"


def _cell(s: object) -> str:
    return _clip(str(s if s is not None else "—"), 160).replace("|", "/")


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _stat_mtime(path: Path) -> tuple[float | None, str]:
    try:
        mt = float(path.stat().st_mtime)
        return mt, _iso(mt)
    except OSError:
        return None, "—"


def _write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(body, encoding="utf-8")
    tmp.replace(path)


def parse_tracker(text: str) -> list[dict]:
    """Parse the MOTIF_TRACKER markdown table. Mechanical; no interpretation."""
    rows = []
    for raw in str(text or "").splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 4:
            continue
        head0 = CELL_STRIP.sub("", cells[0]).strip().lower()
        if head0 in ("deliverable", "") or set(head0) <= set("-: "):
            continue
        name = CELL_STRIP.sub("", cells[0]).strip()
        if not name:
            continue
        current = cells[1]
        stage_n = _first_int(current) or 0
        rows.append({
            "name": name,
            "slug": canonical_slug(name),
            "current": current,
            "artifact": cells[2],
            "next_stage": cells[3],
            "stage_n": stage_n,
            "past_gate": (
                stage_n >= GATE_STAGE
                and "unvetted" not in current.lower()
                and "passed" in current.lower()
            ),
        })
    return rows


def parse_dispositions(text: str) -> list[dict]:
    """COW check-in blocks from MOTIF_TRACKER (`<!-- cow-disposition -->`)."""
    out = []
    for m in DISP_RE.finditer(str(text or "")):
        body = (m.group("body") or "").strip()
        title = ""
        bullets: list[str] = []
        for raw in body.splitlines():
            s = raw.strip()
            if not title and s.startswith("## "):
                title = s[3:].strip()
                continue
            if s.startswith(("-", "*")):
                bullets.append(_clip(s.lstrip("-* ").strip(), 160))
            if len(bullets) >= 6:
                break
        out.append({
            "stamp": m.group("stamp"),
            "title": title or m.group("stamp"),
            "bullets": bullets,
            "bytes": len(body),
        })
    return out[:DISP_CAP]


def parse_dhx_assignments(text: str) -> list[dict]:
    """Assignment-log markers from AGENT_BRIEF.md (DHx)."""
    lines = str(text or "").splitlines()
    in_log = False
    out = []
    for raw in lines:
        s = raw.strip()
        if s.lower().startswith("## assignment log"):
            in_log = True
            continue
        if in_log and s.startswith("## ") and "assignment log" not in s.lower():
            in_log = False
        if not in_log:
            continue
        m = DHX_LINE.match(s)
        if not m:
            continue
        body = m.group("body").strip()
        out.append({
            "ts": m.group("ts"),
            "agent": m.group("agent").strip(),
            "body": body,
            "slug": canonical_slug(body),
        })
    return out


def _split_feature(body: str) -> tuple[str, str]:
    bold = FEATURE_BULLET.match("- " + body)
    if bold:
        return bold.group("name").strip(), (bold.group("rest") or "").strip()
    if " — " in body:
        name, rest = body.split(" — ", 1)
    elif " - " in body:
        name, rest = body.split(" - ", 1)
    else:
        name, rest = body, ""
    return name.strip(), rest.strip().lstrip(" —:-").strip()


def parse_checkboxes(text: str, source: str) -> list[dict]:
    """Open / checked / wip (`[~]`) markdown checkbox rows."""
    rows = []
    section = ""
    for raw in str(text or "").splitlines():
        s = raw.strip()
        if s.startswith("## "):
            section = s[3:].strip()
            continue
        m = CHECK_RE.match(s)
        if not m:
            continue
        mark = (m.group("mark") or " ").strip().lower()
        name, rest = _split_feature((m.group("body") or "").strip())
        if not name:
            continue
        rows.append({
            "feature": name,
            "detail": rest,
            "target": _backlog_target(name, rest),
            "source": ("docs/WISHLIST.md" if source == "wishlist"
                       else "docs/BACKLOG.md"),
            "kind": source,
            "section": section,
            "checked": mark == "x",
            "wip": mark == "~",
            "mark": mark if mark else " ",
        })
    return rows


def parse_backlog(text: str) -> list[dict]:
    return parse_checkboxes(text, "backlog")


def parse_wishlist(text: str) -> list[dict]:
    return parse_checkboxes(text, "wishlist")


def _backlog_target(name: str, detail: str = "") -> str:
    slug = canonical_slug(name)
    mapping = {
        "cdeck": "cDeck",
        "cvm": "CVM",
        "cdm": "CDM",
        "gbridge": "gbridge",
        "collector": "collector",
        "dispatch": "dispatch",
        "makerhands": "Maker-hands",
        "meshadditions": "Mesh additions",
        "cursor": "Cursor lane",
        "runner": "COSMOS runner",
        "watchdog2": "Watchdog2",
    }
    if slug in mapping:
        return mapping[slug]
    low = f"{name} {detail}".lower()
    if "cdeck" in low or "c-deck" in low:
        return "cDeck"
    if "clock" in low or "watchdog" in low:
        return "Watchdog2"
    if "index" in low:
        return "COSMOS_INDEX"
    if "resession" in low or "resume gate" in low:
        return "session"
    if "pause" in low:
        return "PAUSE"
    if "serve" in low:
        return "COSMOS Core"
    if "register_node_rails" in low or "kernel" in low:
        return "COSMOS Core"
    if "undecided" in low or "migration" in low or "tool" in low:
        return "migrate"
    return "COSMOS"


def scan_modules(repo: Path) -> list[dict]:
    """Every top-level cosmos/*.py. Count is the runtime-binding value."""
    cosmos_dir = repo / "cosmos"
    rows = []
    if not cosmos_dir.is_dir():
        return rows
    for p in sorted(cosmos_dir.glob("*.py")):
        text = _read_text(p)
        loc = text.count("\n") + (1 if text and not text.endswith("\n") else 0)
        doc = ""
        m = DOC_RE.search(text)
        if m:
            first = (m.group(2) or "").strip().splitlines()
            doc = _clip(first[0], 120) if first else ""
        cid = None
        cm = CLOCK_ID_RE.search(text)
        if cm:
            try:
                cid = int(cm.group(1))
            except ValueError:
                cid = None
        tm = TASK_NAME_RE.search(text)
        rows.append({
            "file": p.name,
            "name": p.stem,
            "summary": doc,
            "loc": loc,
            "clock_id": cid,
            "task_name": tm.group(1) if tm else None,
            "has_once": "--once" in text,
        })
    return rows


def scan_landings(state_dir: Path, cap: int = LANDING_CAP) -> list[dict]:
    """Top-level live/state/*_result.json, newest first. Never authority."""
    if not state_dir.is_dir():
        return []
    files = []
    for p in state_dir.glob("*_result.json"):
        if p.name.endswith(".tmp"):
            continue
        mt, iso = _stat_mtime(p)
        files.append((mt or 0.0, iso, p))
    files.sort(key=lambda x: x[0], reverse=True)
    out = []
    for mt, iso, p in files[:cap]:
        rec: dict = {}
        try:
            obj = json.loads(p.read_text(encoding="utf-8", errors="replace"))
            if isinstance(obj, dict):
                rec = {k: obj.get(k) for k in LANDING_KEEP if k in obj}
        except (OSError, ValueError):
            rec = {"unreadable": True}
        out.append({
            "file": p.name,
            "path": str(p),
            "mtime": mt,
            "mtime_iso": iso,
            **rec,
        })
    return out


def load_heartbeats(logs: Path) -> list[dict]:
    found: dict[str, dict] = {}
    if logs.is_dir():
        for p in sorted(logs.glob("*heartbeat*.json")):
            if p.name.endswith(".tmp"):
                continue
            rec = _heartbeat_row(p)
            found[rec["name"]] = rec
    for req in REQUIRED_DAEMONS:
        if req not in found:
            found[req] = {
                "name": req,
                "path": str(logs / _heartbeat_filename(req)),
                "exists": False,
                "mtime": None,
                "mtime_iso": "—",
                "last_run": "—",
                "last_run_epoch": None,
                "pid": None,
                "polls": None,
                "tick": None,
                "worker": None,
                "age_s": None,
                "fresh": False,
            }
    return [found[k] for k in sorted(found)]


def _heartbeat_filename(name: str) -> str:
    for fn, label in DAEMON_LABELS.items():
        if label == name:
            return fn
    return f"{name}_heartbeat.json"


def _heartbeat_row(path: Path) -> dict:
    label = DAEMON_LABELS.get(path.name, path.stem)
    mt, mt_iso = _stat_mtime(path)
    rec: dict = {}
    try:
        rec = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        if not isinstance(rec, dict):
            rec = {}
    except (OSError, ValueError):
        rec = {}
    last_epoch = rec.get("last_run_epoch")
    try:
        last_epoch = float(last_epoch) if last_epoch is not None else None
    except (TypeError, ValueError):
        last_epoch = None
    age = (time.time() - last_epoch) if last_epoch else None
    interval = rec.get("interval_s")
    try:
        interval = float(interval) if interval is not None else None
    except (TypeError, ValueError):
        interval = None
    if interval and interval > 0:
        stale_after = max(interval * 3.0, 90.0)
    elif label == "mesh_discovery":
        stale_after = 3900.0
    elif label == "motif_driver":
        stale_after = 20 * 60.0
    else:
        stale_after = 90.0
    fresh = age is not None and age < stale_after
    return {
        "name": label,
        "path": str(path),
        "exists": True,
        "mtime": mt,
        "mtime_iso": mt_iso,
        "last_run": rec.get("last_run") or "—",
        "last_run_epoch": last_epoch,
        "pid": rec.get("pid"),
        "polls": rec.get("polls"),
        "tick": rec.get("tick") or rec.get("state"),
        "worker": rec.get("worker"),
        "age_s": round(age, 1) if age is not None else None,
        "fresh": fresh,
    }


def _agent_for(row: dict, assignments: list[dict]) -> str:
    slug = row["slug"]
    name_l = row["name"].lower()
    needles = SLUG_NEEDLES.get(slug, (slug,))
    best = None
    for a in assignments:
        blob = (a.get("body") or "").lower()
        if slug in blob or name_l in blob or any(n in blob for n in needles):
            best = a
    if best:
        return best["agent"]
    m = AGENT_RE.search(row.get("current") or "")
    if m:
        return m.group(1)
    return "—"


def _last_update_for(row: dict, repo: Path, assignments: list[dict]) -> str:
    epochs: list[tuple[float, str]] = []
    art = str(row.get("artifact") or "").strip()
    if art and art not in ("—", "-", "(building)", "(owed)", "(standup ran)"):
        p = Path(art)
        if not p.is_absolute():
            p = repo / art
        mt, iso = _stat_mtime(p)
        if mt is not None:
            epochs.append((mt, iso))
    needles = SLUG_NEEDLES.get(row["slug"], (row["slug"], row["name"].lower()))
    for a in reversed(assignments):
        blob = (a.get("body") or "").lower()
        if row["slug"] in blob or any(n in blob for n in needles):
            epochs.append((0.0, a.get("ts") or "—"))
            break
    if not epochs:
        return "—"
    epochs.sort(key=lambda x: x[0])
    return epochs[-1][1]


def _pause_flag(paths: CosmosPaths) -> dict | None:
    p = paths.state("control", "PAUSE.flag")
    if not p.exists():
        return None
    mt, iso = _stat_mtime(p)
    rec: dict = {}
    try:
        rec = json.loads(p.read_text(encoding="utf-8", errors="replace"))
        if not isinstance(rec, dict):
            rec = {}
    except (OSError, ValueError):
        rec = {}
    return {
        "path": str(p),
        "mtime": mt,
        "mtime_iso": iso,
        "state": rec.get("state"),
        "mode": rec.get("mode"),
        "reason": rec.get("reason"),
        "set_at": rec.get("set_at"),
    }


def _in_build(feat: dict, building: list[dict]) -> bool:
    target = str(feat.get("target") or "")
    name = str(feat.get("feature") or "")
    blob = (target + " " + name).lower()
    for b in building:
        bname = (b.get("name") or "").lower()
        bslug = b.get("slug") or ""
        if bslug and (bslug in blob or bslug in canonical_slug(target)
                      or bslug in canonical_slug(name)):
            return True
        if bname and (bname in blob or target.lower() in bname):
            return True
    return False


def _status_for_feature(feat: dict, building: list[dict], live_names: set[str]) -> str:
    """requested / in-build / shipped.

    Open BACKLOG/WISHLIST checkboxes are never shipped — the box is the claim
    that work remains. Checked items become shipped only when a C-row name is a
    real token in the feature (not a substring of another word).
    """
    target = str(feat.get("target") or "")
    name = str(feat.get("feature") or "")
    blob = f"{target} {name}".lower()
    bound = False
    for live in live_names:
        token = (live or "").strip().lower()
        if not token:
            continue
        if re.search(r"(?<![a-z0-9])" + re.escape(token) + r"(?![a-z0-9])", blob):
            bound = True
            break
    open_box = feat.get("kind") in ("backlog", "wishlist") and not feat.get("checked")
    if open_box:
        if _in_build(feat, building) or bound or feat.get("wip"):
            return "in-build"
        return "requested"
    if bound:
        return "shipped"
    if _in_build(feat, building):
        return "in-build"
    return "requested"


def gather(root: str, repo: Path | None = None) -> dict:
    """Read every source. Never writes. Never opens the Ledger writer."""
    paths = CosmosPaths(root)
    repo = Path(repo) if repo is not None else repo_tree()
    tracker_p = repo / "docs" / "MOTIF_TRACKER.md"
    backlog_p = repo / "docs" / "BACKLOG.md"
    wish_p = repo / "docs" / "WISHLIST.md"
    dhx_p = repo / "docs" / "AGENT_BRIEF.md"
    logs = paths.logs()
    tracker_text = _read_text(tracker_p)

    tracker = parse_tracker(tracker_text)
    dispositions = parse_dispositions(tracker_text)
    assignments = parse_dhx_assignments(_read_text(dhx_p))
    backlog = parse_backlog(_read_text(backlog_p))
    wishlist = parse_wishlist(_read_text(wish_p))
    modules = scan_modules(repo)
    landings = scan_landings(paths.state())
    heartbeats = load_heartbeats(logs)
    pause = _pause_flag(paths)

    building = []
    gated = []
    for row in tracker:
        packed = {
            **row,
            "builder": _agent_for(row, assignments),
            "last_update": _last_update_for(row, repo, assignments),
        }
        if row["past_gate"]:
            gated.append(packed)
        else:
            building.append(packed)

    live_rows = []
    live_names: set[str] = set()

    for hb in heartbeats:
        if not hb.get("exists"):
            continue
        proof = (
            f"heartbeat last_run={hb['last_run']} file_mtime={hb['mtime_iso']} "
            f"pid={hb.get('pid')} polls={hb.get('polls')} tick={hb.get('tick')}"
        )
        if hb.get("fresh"):
            proof = "LIVE · " + proof
        else:
            proof = f"STALE age_s={hb.get('age_s')} · " + proof
        live_rows.append({
            "item": hb["name"],
            "kind": "daemon",
            "proof": proof,
            "last_update": hb.get("last_run") or hb.get("mtime_iso"),
            "path": hb["path"],
        })
        live_names.add(hb["name"])

    for g in gated:
        live_rows.append({
            "item": g["name"],
            "kind": "gate",
            "proof": f"MOTIF stage {GATE_STAGE}: {g['current']}",
            "last_update": g["last_update"],
            "path": g.get("artifact"),
        })
        live_names.add(g["name"])

    if pause:
        live_rows.append({
            "item": "PAUSE protocol",
            "kind": "protocol",
            "proof": (
                f"flag {pause['path']} state={pause.get('state')} "
                f"mode={pause.get('mode')} file_mtime={pause['mtime_iso']}"
            ),
            "last_update": pause.get("set_at") or pause["mtime_iso"],
            "path": pause["path"],
        })
        live_names.add("pause")
        live_names.add("PAUSE protocol")

    feat_rows = []
    seen_feat: set[tuple[str, str]] = set()
    for feat in wishlist + backlog:
        key = (feat["feature"].lower(), str(feat.get("target") or "").lower())
        if key in seen_feat:
            continue
        seen_feat.add(key)
        feat_rows.append({
            "feature": feat["feature"],
            "target": feat.get("target") or "—",
            "status": _status_for_feature(feat, building, live_names),
            "source": feat.get("source") or "",
            "kind": feat.get("kind"),
            "checked": bool(feat.get("checked")),
            "wip": bool(feat.get("wip")),
        })

    return {
        "paths_root": str(paths.root),
        "repo": str(repo),
        "clock_id": CLOCK_ID,
        "tracker": tracker,
        "building": building,
        "gated": gated,
        "features": feat_rows,
        "live": live_rows,
        "heartbeats": heartbeats,
        "modules": modules,
        "wishlist": wishlist,
        "backlog": backlog,
        "dispositions": dispositions,
        "landings": landings,
        "assignments": len(assignments),
        "pause": pause,
        "tracker_path": str(tracker_p),
        "backlog_path": str(backlog_p),
        "wishlist_path": str(wish_p),
        "dhx_path": str(dhx_p),
        "logs": str(logs),
    }


def _counts(bundle: dict) -> dict:
    wish = bundle.get("wishlist") or []
    back = bundle.get("backlog") or []
    return {
        "modules": len(bundle.get("modules") or []),
        "wishlist_open": sum(1 for x in wish if not x.get("checked")),
        "wishlist_checked": sum(1 for x in wish if x.get("checked")),
        "backlog_open": sum(1 for x in back if not x.get("checked")),
        "backlog_checked": sum(1 for x in back if x.get("checked")),
        "tracker": len(bundle.get("tracker") or []),
        "building": len(bundle.get("building") or []),
        "gated": len(bundle.get("gated") or []),
        "features": len(bundle.get("features") or []),
        "live": len(bundle.get("live") or []),
        "dispositions": len(bundle.get("dispositions") or []),
        "landings": len(bundle.get("landings") or []),
        "heartbeats_fresh": sum(
            1 for h in (bundle.get("heartbeats") or [])
            if h.get("exists") and h.get("fresh")
        ),
        "assignments": bundle.get("assignments") or 0,
    }


def projection(bundle: dict, generated_at: str, generated_epoch: float) -> dict:
    """The one rebuildable JSON cache. Never authority."""
    counts = _counts(bundle)
    return {
        "schema": SCHEMA,
        "authority": False,
        "clock_id": CLOCK_ID,
        "worker": WORKER,
        "generated_at": generated_at,
        "generated_epoch": int(generated_epoch),
        "root": bundle["paths_root"],
        "repo": bundle["repo"],
        "counts": counts,
        "modules": bundle["modules"],
        "wishlist": [
            {"feature": w["feature"], "checked": w["checked"], "wip": w.get("wip"),
             "section": w.get("section"), "mark": w.get("mark")}
            for w in bundle["wishlist"]
        ],
        "backlog": [
            {"feature": b["feature"], "checked": b["checked"], "wip": b.get("wip"),
             "mark": b.get("mark"), "target": b.get("target")}
            for b in bundle["backlog"]
        ],
        "building": [
            {"name": r["name"], "slug": r["slug"], "current": r["current"],
             "builder": r["builder"], "artifact": r["artifact"],
             "last_update": r["last_update"]}
            for r in bundle["building"]
        ],
        "gated": [
            {"name": r["name"], "slug": r["slug"], "current": r["current"]}
            for r in bundle["gated"]
        ],
        "features": bundle["features"],
        "live": bundle["live"],
        "dispositions": bundle["dispositions"],
        "landings": bundle["landings"],
        "pause": bundle.get("pause"),
        "sources": {
            "modules": "cosmos/*.py",
            "wishlist": bundle["wishlist_path"],
            "backlog": bundle["backlog_path"],
            "tracker": bundle["tracker_path"],
            "dhx": bundle["dhx_path"],
            "landings": "state/*_result.json",
            "heartbeats": str(Path(bundle["logs"]) / "*heartbeat*.json"),
        },
    }


def _table(headers: list[str], rows: list[list[object]]) -> str:
    th = "".join(f"<th>{_html_escape(h)}</th>" for h in headers)
    body = []
    if not rows:
        body.append(
            "<tr>" + "".join("<td>—</td>" for _ in headers) + "</tr>"
        )
    else:
        for r in rows:
            tds = "".join(f"<td>{_html_escape(_cell(c))}</td>" for c in r)
            body.append(f"<tr>{tds}</tr>")
    return (
        '<div class="twrap"><table>'
        f"<thead><tr>{th}</tr></thead>"
        f"<tbody>{''.join(body)}</tbody></table></div>"
    )


def render_panel(proj: dict) -> str:
    """Self-contained KDash panel fragment (same tokens as kdash/index.html)."""
    c = proj.get("counts") or {}
    chips = "".join(
        f'<span class="chip">{_html_escape(k.replace("_", " "))} '
        f'<b>{_html_escape(str(v))}</b></span>'
        for k, v in (
            ("modules", c.get("modules", 0)),
            ("building", c.get("building", 0)),
            ("wishlist open", c.get("wishlist_open", 0)),
            ("backlog open", c.get("backlog_open", 0)),
            ("live", c.get("live", 0)),
            ("landings", c.get("landings", 0)),
            ("dispositions", c.get("dispositions", 0)),
        )
    )
    a_rows = [
        [r["name"], r["current"], r["builder"], r["artifact"], r["last_update"]]
        for r in (proj.get("building") or [])
    ]
    b_rows = [
        [r["feature"], r["target"], r["status"], r["source"]]
        for r in (proj.get("features") or [])
    ]
    c_rows = [
        [r["item"], r["kind"], r["proof"], r["last_update"]]
        for r in (proj.get("live") or [])
    ]
    m_rows = [
        [r["file"], r.get("loc"), r.get("clock_id") or "—",
         r.get("task_name") or "—", r.get("summary") or "—"]
        for r in (proj.get("modules") or [])
    ]
    d_rows = [
        [r["stamp"], r["title"], "; ".join(r.get("bullets") or [])]
        for r in (proj.get("dispositions") or [])
    ]
    l_rows = [
        [r["file"], r.get("mtime_iso"), r.get("rc") if "rc" in r else "—",
         r.get("job") or r.get("status") or r.get("state") or "—"]
        for r in (proj.get("landings") or [])
    ]
    gen = _html_escape(str(proj.get("generated_at") or "—"))
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>COSMOS INDEX</title>
<style>
:root{{--bg:#0b0e12;--panel:#12161c;--panel-edge:#1f2630;--ink:#c8d2dc;--ink-dim:#7a8694;--ink-faint:#4a545f;--green:#3fd68f;--cyan:#56b6c2;--head:#e2e8ee;--mono:"Consolas","Cascadia Mono","Courier New",monospace}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{background:var(--bg);color:var(--ink);font-family:var(--mono);font-size:13px;line-height:1.45}}
body{{padding:10px 14px 20px}}
.panel{{background:var(--panel);border:1px solid var(--panel-edge);border-radius:4px}}
.panel-hd{{display:flex;align-items:baseline;justify-content:space-between;padding:7px 10px 6px;border-bottom:1px solid var(--panel-edge);margin-bottom:8px}}
.panel-hd h2{{font-size:12px;letter-spacing:2px;color:var(--head);font-weight:700}}
.age{{font-size:11px;color:var(--green)}} .panel-bd{{padding:0 10px 8px}}
h3{{font-size:11px;letter-spacing:1px;color:var(--cyan);margin:12px 0 6px}}
.chips{{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px}}
.chip{{border:1px solid var(--panel-edge);border-radius:3px;padding:2px 8px;font-size:11px;color:var(--ink-dim)}}
.chip b{{color:var(--head)}} .twrap{{overflow:auto;max-height:280px}}
table{{border-collapse:collapse;width:100%;font-size:12px}}
th{{color:var(--ink-dim);text-align:left;font-weight:400;letter-spacing:1px;border-bottom:1px solid var(--panel-edge);padding:2px 10px 4px 0}}
td{{padding:2px 10px 2px 0;border-bottom:1px solid #171d25;vertical-align:top;word-break:break-word}}
.dim{{color:var(--ink-faint);font-size:11px;margin-top:8px}}
</style>
</head>
<body>
<section class="panel" id="panel-index">
  <div class="panel-hd"><h2>INDEX</h2><span class="age">{gen}</span></div>
  <div class="panel-bd">
    <div class="chips">{chips}</div>
    <h3>A. BUILDING</h3>
    {_table(["name", "motif stage", "builder", "artifact", "last update"], a_rows)}
    <h3>B. FEATURES / WISHES</h3>
    {_table(["feature", "target", "status", "source"], b_rows)}
    <h3>C. IMPLEMENTED / LIVE</h3>
    {_table(["item", "kind", "proof", "last update"], c_rows)}
    <h3>MODULES cosmos/*.py</h3>
    {_table(["file", "loc", "clock_id", "task", "summary"], m_rows)}
    <h3>DISPOSITIONS</h3>
    {_table(["stamp", "title", "bullets"], d_rows)}
    <h3>RECENT LANDINGS state/*_result.json</h3>
    {_table(["file", "mtime", "rc", "job"], l_rows)}
    <p class="dim">Rebuildable projection. Never authority. schema={_html_escape(SCHEMA)}
    clock_id={CLOCK_ID} · {WORKER} · py -3.14 cosmos\\cosmos_index.py --once</p>
  </div>
</section>
</body>
</html>
"""


def rebuild(root: str, *, repo: str | Path | None = None,
            dest: str | Path | None = None,
            write_hb: bool = True) -> dict:
    """Rebuild state/cosmos_index.json + the KDash panel fragment."""
    t0 = time.time()
    paths = CosmosPaths(root)
    repo_p = Path(repo) if repo is not None else repo_tree()
    dest_p = Path(dest) if dest is not None else paths.state(PROJECTION_NAME)
    panel_p = paths.state(PANEL_NAME)
    hb_path = paths.logs(HEARTBEAT_NAME)
    generated_at = _iso()
    if write_hb:
        write_heartbeat(hb_path, WORKER, extra={
            "schema": SCHEMA, "tick": "rebuild", "clock_id": CLOCK_ID,
            "interval_s": DEFAULT_INTERVAL_S,
        }, interval_s=DEFAULT_INTERVAL_S)
    bundle = gather(root, repo=repo_p)
    proj = projection(bundle, generated_at, t0)
    atomic_json(dest_p, proj)
    html = render_panel(proj)
    try:
        _write_text(panel_p, html)
        panel_ok = True
        panel_err = None
    except OSError as e:
        panel_ok = False
        panel_err = str(e)
    elapsed = round(time.time() - t0, 3)
    counts = proj["counts"]
    extra = {
        "schema": SCHEMA,
        "tick": "done",
        "clock_id": CLOCK_ID,
        "dest": str(dest_p),
        "panel": str(panel_p),
        "panel_ok": panel_ok,
        "bytes": dest_p.stat().st_size if dest_p.exists() else 0,
        "section_a": counts["building"],
        "section_b": counts["features"],
        "section_c": counts["live"],
        "module_count": counts["modules"],
        "landing_count": counts["landings"],
        "elapsed_s": elapsed,
        "interval_s": DEFAULT_INTERVAL_S,
    }
    if panel_err:
        extra["panel_error"] = panel_err
    hb = (write_heartbeat(hb_path, WORKER, extra=extra,
                          interval_s=DEFAULT_INTERVAL_S)
          if write_hb else extra)
    return {
        "ok": True,
        "schema": SCHEMA,
        "clock_id": CLOCK_ID,
        "dest": str(dest_p),
        "panel": str(panel_p),
        "heartbeat": str(hb_path),
        "bytes": extra["bytes"],
        "section_a": extra["section_a"],
        "section_b": extra["section_b"],
        "section_c": extra["section_c"],
        "module_count": extra["module_count"],
        "landing_count": extra["landing_count"],
        "elapsed_s": elapsed,
        "generated_at": generated_at,
        "proof": hb,
        "bundle": bundle,
        "projection": proj,
    }


def standup(root: str) -> dict:
    t0 = time.time()
    existing = query_task(TASK_NAME)
    script = Path(__file__).resolve()
    tr = tr_cmdline(script, root, "--once")
    tick = rebuild(root)
    rec = read_heartbeat(Path(tick["heartbeat"]))
    age = heartbeat_age_s(rec)
    proof_ok = (rec is not None and age is not None and age < 60
                and float(rec.get("last_run_epoch") or 0) >= t0 - 5)
    if existing.get("ok"):
        return {
            "started": "already",
            "task": existing,
            "tick": {k: tick.get(k) for k in (
                "ok", "dest", "bytes", "section_a", "section_b", "section_c",
                "module_count")},
            "proof": {"ok": proof_ok, "heartbeat": rec, "age_s": age,
                      "path": tick["heartbeat"]},
            "heartbeat_path": tick["heartbeat"],
            "dest": tick["dest"],
            "keith_cmd": None,
            "task_name": TASK_NAME,
            "clock_id": CLOCK_ID,
        }
    task = create_task(TASK_NAME, tr, "minute", mo=1, run_now=False)
    return {
        "started": "schtasks" if task.get("ok") else "in-process-tick",
        "task": task,
        "tick": {k: tick.get(k) for k in (
            "ok", "dest", "bytes", "section_a", "section_b", "section_c",
            "module_count")},
        "proof": {"ok": proof_ok, "heartbeat": rec, "age_s": age,
                  "path": tick["heartbeat"]},
        "heartbeat_path": tick["heartbeat"],
        "dest": tick["dest"],
        "keith_cmd": task.get("keith_cmd") if (
            task.get("needs_elevation") or not task.get("ok")) else None,
        "task_name": TASK_NAME,
        "clock_id": CLOCK_ID,
    }


def loop(root: str, interval_s: float = DEFAULT_INTERVAL_S) -> int:
    interval = float(interval_s)
    while True:
        try:
            rebuild(root)
        except Exception:
            import traceback
            tb = traceback.format_exc()
            try:
                CosmosPaths(root).logs("cosmos_index.err").write_text(
                    tb, encoding="utf-8")
            except (OSError, CosmosPathError):
                pass
        time.sleep(interval)


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_index")
    ap.add_argument("--root", required=True,
                    help="COSMOS runtime root (sentinel-verified)")
    ap.add_argument("--repo", default=None,
                    help="repo tree (default: parent of this module)")
    ap.add_argument("--dest", default=None,
                    help="JSON dest (default: <root>/state/cosmos_index.json)")
    ap.add_argument("--once", action="store_true",
                    help="rebuild the index once and exit")
    ap.add_argument("--loop", action="store_true",
                    help="rebuild on an interval (fallback daemon)")
    ap.add_argument("--standup", action="store_true",
                    help="register 1-min schtasks light clock and rebuild once")
    ap.add_argument("--status", action="store_true",
                    help="print heartbeat age; exit 0 if fresh")
    ap.add_argument("--interval", type=float, default=DEFAULT_INTERVAL_S)
    a = ap.parse_args()

    if a.status:
        paths = CosmosPaths(a.root)
        rec = read_heartbeat(paths.logs(HEARTBEAT_NAME))
        age = heartbeat_age_s(rec)
        print(json.dumps({"path": str(paths.logs(HEARTBEAT_NAME)),
                          "age_s": age, "clock_id": CLOCK_ID,
                          "heartbeat": rec}, indent=1, default=str))
        return 0 if age is not None and age < FRESH_S else 2

    if a.standup:
        r = standup(a.root)
        print(json.dumps(r, indent=1, default=str))
        return 0 if (r.get("proof") or {}).get("ok") else 2

    if a.loop:
        return loop(a.root, a.interval)

    r = rebuild(a.root, repo=a.repo, dest=a.dest)
    out = {k: r[k] for k in r if k not in ("bundle", "projection")}
    print(json.dumps(out, indent=1, default=str))
    return 0 if r.get("ok") else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CosmosPathError as e:
        print(e, file=sys.stderr)
        raise SystemExit(2)
