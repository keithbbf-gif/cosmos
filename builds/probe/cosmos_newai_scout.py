#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_newai_scout - open-ended NEW-AI discovery clock (F-26).

WHY THIS EXISTS. `cosmos/cosmos_discover.py` inventories KNOWN hands over a
closed probe table (PATH binaries + a few local HTTP endpoints). The wishlist
item is the missing *outward* scout: go OUT, find products that are not already
a COMPETENCY node / HANDS file / MESH_ADDITIONS row, and propose them for COW
to wire. A research note is not a clock; this file is the clock.

WHAT IT DOES
    1. Builds the known inventory from files on disk (never a closed name table):
       COMPETENCY.toml `[nodes.X]`, `docs/research/*_HANDS.md` stems,
       MESH_ADDITIONS.md / MESH_ADDITIONS_grok.md table names.
    2. Fetches a public feed (default: the awesome-coding-agents README the
       2026-08-27 research already cited). Transport is injected; production
       uses stdlib urllib. No model call, no spend, no key.
    3. Parses product names the FEED actually contains (markdown **bold** in
       tables/lists). Does not invent a name that was not in the bytes.
    4. Diffs: NEW = feed names whose normalised form is not in the inventory.
       Already-known names are counted, not proposed.
    5. Heartbeats every tick. --dry-run writes nothing. --plan-task emits
       `schtasks /create` and registers nothing.

REFUSALS (typed, heartbeated, rc=2)
    NO_ROOT_SENTINEL  --root has no .cosmos-root.json (existence of the dir
                      is not identity — the empty-dir scar)
    NO_ROOT     sentinel unreadable or CONTENT is not COSMOS
    NO_REPO     --repo is not a COSMOS repo tree (no docs/COMPETENCY.toml)
    NO_FEED     fetch failed, empty body, or zero parseable names
    HOLD        PAUSE.flag is not RUNNING (fail-closed; never self-clears)

States that are not refusals:
    MINED       at least one NEW candidate
    NEW_NONE    feed parsed; every name is already in the inventory
                (a silent empty list would look like "found nothing new"
                when it actually found nothing *unknown* — name it)

A candidate is evidence, not a ruling. COW files into COMPETENCY.toml / a
HANDS note / a rail, or not. This clock never writes those files.

    py -3.14 builds/probe/cosmos_newai_scout.py --root V:\\A\\Ai\\COSMOS\\live --dry-run
    py -3.14 builds/probe/cosmos_newai_scout.py --root ... --once
    py -3.14 builds/probe/cosmos_newai_scout.py --root ... --plan-task
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_DEFAULT = HERE.parents[1]

WORKER = "cosmos-newai-scout"
SCHEMA = "cosmos-newai-scout/1"
TASK_NAME = "COSMOS New-AI Scout"
HEARTBEAT_NAME = "newai_scout_heartbeat.json"
PROJECTION_REL = ("state", "discovery", "newai_scout.json")
PAUSE_REL = ("state", "control", "PAUSE.flag")
NO_WINDOW = 0x08000000 if os.name == "nt" else 0

# The 2026-08-27 research already named this feed. Fetching it is "going OUT";
# re-reading NEW_AI_SCOUT.md would be the closed-table failure this clock exists
# to end.
DEFAULT_FEEDS = (
    "https://raw.githubusercontent.com/tiennm99/awesome-coding-agents/main/README.md",
)

# Names that appear as **bold** in READMEs but are not products.
_STOP = frozenset({
    "name", "vendor", "reach", "cost", "cli", "mcp", "api", "dom", "free",
    "oss", "note", "todo", "readme", "license", "stars", "last", "update",
    "overview", "installation", "usage", "features", "docs", "documentation",
})

_REDACT = [
    ("slack-webhook", re.compile(r"https://hooks\.slack\.com/services/\S+")),
    ("anthropic-key", re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{12,}")),
    ("openai-key", re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}")),
    ("xai-key", re.compile(r"\bxai-[A-Za-z0-9_\-]{16,}")),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{16,}")),
    ("google-key", re.compile(r"\bAIza[0-9A-Za-z_\-]{30,}")),
]

_NODES = re.compile(r"^\[nodes\.([A-Za-z0-9_-]+)\]\s*$", re.M)
_TABLE_NAME = re.compile(
    r"^\|\s*(?:\d+\s*\|)?\s*\*\*([^*]{2,60})\*\*", re.M)
# The 2026-08-31 awesome-coding-agents README names products as
# [org/repo](https://github.com/org/repo), not **bold**. Bold-only
# parsing harvested "Inclusion criteria" / dates — that is inventing.
_GH_LINK = re.compile(
    r"\[([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)\]\(https://github\.com/\1/\2/?(?:\)|\s)")


class ScoutRefusal(RuntimeError):
    """kind in {NO_ROOT, NO_REPO, NO_FEED, HOLD, NO_ROOT_SENTINEL}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        self.detail = detail
        super().__init__(f"[{kind}] {detail}")


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def redact(text: str) -> tuple[str, int]:
    """Every string that leaves this module. Count is reported so a clean run
    says so out loud rather than being assumed."""
    n = 0
    out = text or ""
    for label, rx in _REDACT:
        out, c = rx.subn(f"[{label}]", out)
        n += c
    return out, n


def norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (name or "").lower())


def verify_root(root: Path) -> dict:
    """Sentinel CONTENT is identity. Existence is not identity."""
    sentinel = Path(root) / ".cosmos-root.json"
    if not sentinel.is_file():
        raise ScoutRefusal("NO_ROOT_SENTINEL", f"no sentinel at {sentinel}")
    try:
        doc = json.loads(sentinel.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError) as e:
        raise ScoutRefusal("NO_ROOT", f"unreadable sentinel: {type(e).__name__}: {e}") from e
    if (not isinstance(doc, dict)
            or doc.get("system") != "COSMOS" or not doc.get("tree_id")):
        raise ScoutRefusal("NO_ROOT", f"sentinel CONTENT is not COSMOS: {doc!r}")
    return doc


def verify_repo(repo: Path) -> Path:
    repo = Path(repo)
    toml = repo / "docs" / "COMPETENCY.toml"
    if not toml.is_file():
        raise ScoutRefusal("NO_REPO", f"no docs/COMPETENCY.toml under {repo}")
    return repo


# ------------------------------------------------------------------ inventory (from files, not a table)

def inventory_from_competency(text: str) -> set[str]:
    return {m.group(1) for m in _NODES.finditer(text or "")}


def inventory_from_hands(repo: Path) -> set[str]:
    names: set[str] = set()
    research = repo / "docs" / "research"
    if not research.is_dir():
        return names
    for p in research.glob("*_HANDS.md"):
        stem = p.stem[: -len("_HANDS")] if p.stem.endswith("_HANDS") else p.stem
        names.add(stem.replace("_", " "))
        names.add(stem.replace("_", "-"))
        names.add(stem)
    return names


def inventory_from_mesh_md(text: str) -> set[str]:
    names: set[str] = set()
    for m in _TABLE_NAME.finditer(text or ""):
        raw = m.group(1).strip()
        # "Playwright MCP (Microsoft, official)" -> "Playwright MCP"
        raw = re.split(r"\s*[—(]", raw, maxsplit=1)[0].strip()
        if raw:
            names.add(raw)
    return names


def build_inventory(repo: Path) -> dict:
    """Known products, bound to files that exist. A closed probe table is
    not consulted — that is cosmos_discover.py, a different row."""
    repo = verify_repo(repo)
    toml_path = repo / "docs" / "COMPETENCY.toml"
    toml_text = toml_path.read_text(encoding="utf-8")
    nodes = inventory_from_competency(toml_text)
    hands = inventory_from_hands(repo)
    mesh: set[str] = set()
    mesh_files = []
    for rel in ("docs/MESH_ADDITIONS.md", "docs/MESH_ADDITIONS_grok.md"):
        p = repo / rel
        if p.is_file():
            mesh_files.append(rel)
            mesh |= inventory_from_mesh_md(p.read_text(encoding="utf-8"))
    names = set(nodes) | set(hands) | set(mesh)
    keyed = {norm(n): n for n in names if norm(n)}
    return {
        "repo": str(repo),
        "competency_nodes": sorted(nodes),
        "hands": sorted(hands),
        "mesh": sorted(mesh),
        "mesh_files": mesh_files,
        "known_count": len(keyed),
        "known": keyed,
        "toml_bytes": len(toml_text.encode("utf-8")),
    }


# ------------------------------------------------------------------ feed

def default_fetch(url: str, timeout: int = 25) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": "cosmos-newai-scout/1"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(400_000).decode("utf-8", "replace")


def _ok_product_name(name: str) -> bool:
    """A product, not a date / sentence / table heading."""
    name = (name or "").strip()
    if len(name) < 2 or len(name) > 48:
        return False
    if re.search(r"\d{4}-\d{2}-\d{2}", name):
        return False
    if re.match(r"^[\d.kKmM+]+$", name):
        return False
    words = name.split()
    if len(words) > 4:
        return False
    if not re.search(r"[A-Za-z]", name):
        return False
    key = norm(name)
    if not key or key in _STOP:
        return False
    if name.lower() in _STOP:
        return False
    return True


def parse_feed_names(text: str) -> list[str]:
    """Names the feed actually contains.

    GitHub org/repo markdown links first (the live awesome-coding-agents
    shape). Then **bold** in a table column. Loose **bold** is not harvested
    — it is how 'Inclusion criteria' / 'Last updated' became candidates.
    """
    seen: set[str] = set()
    out: list[str] = []

    def add(raw: str) -> None:
        name = re.split(r"\s*[—(,]", (raw or "").strip(), maxsplit=1)[0].strip()
        name = name.strip("`[]:")
        if not _ok_product_name(name):
            return
        key = norm(name)
        if key in seen:
            return
        seen.add(key)
        out.append(name)

    for m in _GH_LINK.finditer(text or ""):
        add(m.group(2))
    for m in _TABLE_NAME.finditer(text or ""):
        add(m.group(1))
    return out


def fetch_feeds(urls: tuple[str, ...] | list[str], fetch) -> dict:
    bodies = []
    errors = []
    for url in urls:
        try:
            body = fetch(url)
        except (urllib.error.URLError, urllib.error.HTTPError,
                TimeoutError, OSError, ValueError) as e:
            errors.append({"url": url, "kind": type(e).__name__,
                           "detail": str(e)[:240]})
            continue
        if not (body or "").strip():
            errors.append({"url": url, "kind": "EMPTY", "detail": "empty body"})
            continue
        redacted, nred = redact(body)
        bodies.append({"url": url, "chars": len(body), "redacted": nred,
                       "text": redacted})
    if not bodies:
        raise ScoutRefusal(
            "NO_FEED",
            "no feed body: " + "; ".join(
                f"{e['url']} {e['kind']}" for e in errors) or "no urls")
    names: list[str] = []
    seen: set[str] = set()
    for b in bodies:
        for n in parse_feed_names(b["text"]):
            k = norm(n)
            if k in seen:
                continue
            seen.add(k)
            names.append(n)
    if not names:
        raise ScoutRefusal("NO_FEED", "feed had no parseable product names")
    return {
        "feeds": [{"url": b["url"], "chars": b["chars"], "redacted": b["redacted"]}
                  for b in bodies],
        "errors": errors,
        "feed_names": names,
        "feed_count": len(names),
        "bodies": bodies,  # dropped before heartbeat
    }


def diff_new(feed_names: list[str], known: dict[str, str]) -> list[dict]:
    new = []
    known_hits = 0
    for n in feed_names:
        k = norm(n)
        if k in known:
            known_hits += 1
            continue
        new.append({"name": n, "norm": k, "status": "NEW"})
    return new, known_hits


# ------------------------------------------------------------------ tick

def _pause_class(root: Path) -> str:
    flag = Path(root).joinpath(*PAUSE_REL)
    if not flag.is_file():
        return "RUNNING"
    try:
        raw = flag.read_text(encoding="utf-8").strip()
    except OSError:
        return "HOLD"
    if not raw:
        return "HOLD"
    try:
        doc = json.loads(raw)
    except ValueError:
        return "HOLD"
    if str(doc.get("state", "PAUSED")).upper() == "RUNNING":
        return "RUNNING"
    return "HOLD"


def write_json_atomic(path: Path, obj: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1, sort_keys=True) + "\n",
                   encoding="utf-8")
    os.replace(tmp, path)


def scout(repo: Path, fetch, feeds: tuple[str, ...] | list[str] = DEFAULT_FEEDS) -> dict:
    """Pure-enough: inventory + fetch + diff. No heartbeat, no root required."""
    inv = build_inventory(repo)
    got = fetch_feeds(feeds, fetch)
    new, known_hits = diff_new(got["feed_names"], inv["known"])
    kind = "MINED" if new else "NEW_NONE"
    rec = {
        "schema": SCHEMA,
        "worker": WORKER,
        "ok": True,
        "state": kind,
        "kind": kind,
        "ts": _utcnow(),
        "feeds": got["feeds"],
        "feed_errors": got["errors"],
        "feed_count": got["feed_count"],
        "known_count": inv["known_count"],
        "competency_nodes": inv["competency_nodes"],
        "hands_count": len(inv["hands"]),
        "mesh_files": inv["mesh_files"],
        "already_known_in_feed": known_hits,
        "new_count": len(new),
        "candidates": new,
        "redacted_total": sum(b["redacted"] for b in got["bodies"]),
    }
    return rec


def tick(root: Path, repo: Path, *, fetch=None, feeds=DEFAULT_FEEDS,
         dry_run: bool = False, force: bool = False) -> dict:
    t0 = time.time()
    doc = verify_root(root)
    rec: dict = {"schema": SCHEMA, "worker": WORKER, "tree_id": doc.get("tree_id"),
                 "root": str(Path(root)), "dry_run": bool(dry_run)}
    if not force and _pause_class(root) == "HOLD":
        rec.update(ok=False, state="REFUSED", kind="HOLD",
                   detail="PAUSE.flag is not RUNNING")
        rec["elapsed_s"] = round(time.time() - t0, 3)
        rec["writes"] = 0
        if not dry_run:
            _finish(root, rec)
        return rec
    try:
        out = scout(repo, fetch or default_fetch, feeds)
    except ScoutRefusal as e:
        rec.update(ok=False, state="REFUSED", kind=e.kind, detail=e.detail,
                   writes=0, elapsed_s=round(time.time() - t0, 3))
        if not dry_run:
            _finish(root, rec)
        return rec
    rec.update(out)
    rec["elapsed_s"] = round(time.time() - t0, 3)
    rec["tree_id"] = doc.get("tree_id")
    if dry_run:
        rec["writes"] = 0
        rec["dry_run"] = True
        return rec
    rec["writes"] = 2
    _finish(root, rec)
    proj = Path(root).joinpath(*PROJECTION_REL)
    write_json_atomic(proj, rec)
    return rec


def _finish(root: Path, rec: dict) -> dict:
    hb = Path(root) / "logs" / HEARTBEAT_NAME
    write_json_atomic(hb, rec)
    rec["heartbeat"] = str(hb)
    return rec


# ------------------------------------------------------------------ clock vehicle

def _pythonw() -> str:
    exe = sys.executable
    if os.name == "nt":
        cand = Path(exe).with_name("pythonw.exe")
        if cand.is_file():
            return str(cand)
    return exe


def plan_task_argv(root: Path) -> list[str]:
    tr = subprocess.list2cmdline([
        _pythonw(), str(Path(__file__).resolve()),
        "--root", str(root), "--once",
    ])
    return ["schtasks", "/create", "/tn", TASK_NAME, "/tr", tr,
            "/sc", "HOURLY", "/f"]


def install_task(root: Path) -> dict:
    argv = plan_task_argv(root)
    try:
        p = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=60,
                           creationflags=NO_WINDOW)
    except OSError as e:
        return {"ok": False, "rc": -1, "argv": argv, "out": str(e)}
    return {"ok": p.returncode == 0, "rc": p.returncode, "argv": argv,
            "out": ((p.stdout or "") + (p.stderr or "")).strip()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", help="COSMOS runtime root (sentinel CONTENT)")
    ap.add_argument("--repo", default=str(REPO_DEFAULT),
                    help="repo tree holding docs/COMPETENCY.toml")
    ap.add_argument("--feed", action="append", dest="feeds",
                    help="override default feed URL (repeatable)")
    ap.add_argument("--force", action="store_true")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--once", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--plan-task", action="store_true")
    g.add_argument("--install-task", action="store_true")
    a = ap.parse_args(argv)

    if a.plan_task:
        if not a.root:
            print(json.dumps({"ok": False, "kind": "NO_ROOT",
                              "detail": "--root is required"}), file=sys.stderr)
            return 2
        print(json.dumps({"task": TASK_NAME, "argv": plan_task_argv(Path(a.root)),
                          "heartbeat": HEARTBEAT_NAME}, indent=1))
        return 0
    if a.install_task:
        if not a.root:
            print(json.dumps({"ok": False, "kind": "NO_ROOT"}), file=sys.stderr)
            return 2
        rec = install_task(Path(a.root))
        print(json.dumps(rec, indent=1))
        return 0 if rec["ok"] else 1
    if not a.root:
        print(json.dumps({"ok": False, "kind": "NO_ROOT",
                          "detail": "--root is required"}), file=sys.stderr)
        return 2
    rec = tick(Path(a.root), Path(a.repo),
               feeds=tuple(a.feeds) if a.feeds else DEFAULT_FEEDS,
               dry_run=bool(a.dry_run), force=bool(a.force))
    print(json.dumps({k: v for k, v in rec.items() if k != "bodies"},
                     indent=1, default=str))
    if rec.get("state") == "REFUSED":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
