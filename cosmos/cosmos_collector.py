#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_collector - permanent results-collector (rebuildable projection).

Polls every ~30s and COLLECTS, ORGANIZES, and STORES agent/subagent results from
every AI into a central append-only index. The index is a CACHE; source files
are truth. Idempotent, restart-safe, never a second COSMOS authority writer.

Decided function (DHx): read the assignment log and correlate each marker to
its result. The human summary is the aggregated state of all *agents*. Anti-loss
DIFF (assigned vs collected) is why this daemon exists.

Sources:
  * Resolver queue role (`live/queue`) — identity, always scanned
  * Optional bootstrap ingress (`--queue` / COSMOS_COLLECTOR_QUEUE / config) —
    the BTS runner `V:\\Ai\\_queue` is named bootstrap, never default identity
  * Queue buckets: *_result.json, done/, failed/, logs/, returns/
  * runner_ledger.jsonl (precise start/end)
  * DHx assignment log (`docs/AGENT_BRIEF.md`) — marker ↔ result
  * Repo research outputs: docs/research/**/*.md
  * COSMOS authority ledger: result-bearing events only

Store:
  * live/state/collector/index.jsonl  - append-only projection
  * docs/COLLECTOR.md                 - human summary, grouped by agent
  * live/state/collector/dhx.json     - current DHx correlation snapshot
  * live/logs/collector_heartbeat.json - written EVERY poll (liveness is a file)

Launch (survives this job's exit and process-tree kill):

    py -3.14 cosmos\\cosmos_collector.py --root V:\\A\\Ai\\COSMOS\\live --standup
    py -3.14 cosmos\\cosmos_collector.py --root ... --loop
    py -3.14 cosmos\\cosmos_collector.py --root ... --once
    py -3.14 cosmos\\cosmos_collector.py --root ... --status

--standup registers a 1-minute self-heal schtask (plus ONLOGON relaunch) and/or
spawns a DETACHED pythonw child via WMI. Proof is a FRESH heartbeat from a
still-alive pid, not an exit code.

This module does NOT modify COSMOS core (kernel/ledger/sched/service). It
reads sources and writes only its own projection + heartbeat under the
resolver-verified runtime root.

Modules: the pure DHx layer lives in `cosmos_collector_dhx`; the pure walk
layer (queue / research / ledger iterators) lives in `cosmos_collector_scan`.
Both are re-exported here (PHASE 4, `docs/CORE_RESTRUCTURE.md`). What remains
here is the daemon: catalog, collection, summary rendering, poll loop, standup.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone as dt_timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_paths import CosmosPaths, CosmosPathError  # noqa: E402
# The DHx layer was split out here (PHASE 4, docs/CORE_RESTRUCTURE.md) and is
# re-exported verbatim, so every existing importer of these names off
# cosmos_collector keeps working unchanged. Underscore aliases preserve the
# private spellings this module already used.
from cosmos_collector_dhx import (  # noqa: E402,F401
    DHX_LANE_FILE, DHX_LINE, HEX8, JOB_TOKEN, KNOWN_LANES, LANE_NAMES,
    correlate_marker, parse_dhx_markers, resolve_marker_artifact,
    marker_stems as _marker_stems,
    path_hit_score as _path_hit_score,
    pick_lane_job as _pick_lane_job,
    task_of as _task_of,
)
# PHASE 4 seam (docs/CORE_RESTRUCTURE.md): queue/research/ledger walkers live
# in cosmos_collector_scan and are re-exported here -- same objects, not copies
# -- so Collector._collect_* and tests/test_collector.py keep working unchanged.
from cosmos_collector_scan import (  # noqa: E402,F401
    LEDGER_DROP, LEDGER_KEEP, LEDGER_KEEP_SUBSTR, SKIP_DIR_NAMES,
    _is_result_name, _walk_files,
    iter_jsonl_objs, iter_ledger_events, iter_queue_files,
    iter_research_files, iter_runner_ledger, ledger_event_kept,
)

WORKER = "cosmos-collector"
TASK_NAME = "COSMOS Collector"
TASK_NAME_LOGON = "COSMOS Collector Logon"
HEARTBEAT_NAME = "collector_heartbeat.json"
LOCK_NAME = "collector.lock"
INDEX_LOCK_NAME = "index.jsonl.lock"
INDEX_NAME = "index.jsonl"
SUMMARY_NAME = "COLLECTOR.md"
DHX_SNAP_NAME = "dhx.json"
DEFAULT_INTERVAL_S = 30.0
SCHEMA = "cosmos-collector/1"

# Optional named bootstrap (BTS runner). Never default identity — the resolver
# queue role is identity. Override / configure with --queue, COSMOS_COLLECTOR_QUEUE,
# or live/config/collector.json `bootstrap_queue`.
WELL_KNOWN_BOOTSTRAP = Path(r"V:\Ai\_queue")
DEFAULT_QUEUE = Path(os.environ["COSMOS_COLLECTOR_QUEUE"]) if os.environ.get(
    "COSMOS_COLLECTOR_QUEUE") else WELL_KNOWN_BOOTSTRAP

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200
CREATE_NO_WINDOW = 0x08000000
CREATE_BREAKAWAY_FROM_JOB = 0x01000000

# SKIP_DIR_NAMES / LEDGER_KEEP / LEDGER_DROP / LEDGER_KEEP_SUBSTR live in
# cosmos_collector_scan (imported above and re-exported unchanged).

TEXT_SUFFIXES = {
    ".json", ".md", ".txt", ".log", ".py", ".ps1", ".csv", ".toml",
    ".jsonl", ".out", ".err", ".rst", ".yml", ".yaml",
}

SUMMARY_CAP_PER_GROUP = 40
SUMMARY_LINE = 180
READ_HEAD = 8192
READ_TAIL = 4096
MAX_READ_BYTES = 5 * 1024 * 1024

# Filename prefixes -> (agent, maker/app). Longest prefix wins.
# Lanes (lg/pb) are NOT agents — H2: identity never comes from _lanes/<lane>.
_AGENT_PREFIXES = (
    ("g46", "G46", "Grok"),
    ("grok", "Grok", "Grok"),
    ("cursor", "Cursor", "Cursor"),
    ("claude", "Claude", "Claude"),
    ("cowork", "Cowork", "Claude"),
    ("gemini", "Gemini", "Gemini"),
    ("openai", "OpenAI", "OpenAI"),
    ("cdeck", "cDeck", "cDeck"),
    ("cosmos", "COSMOS", "COSMOS"),
    ("motif", "Motif", "Motif"),
    ("cdm", "CDM", "CDM"),
    ("cvm", "CVM", "CVM"),
    ("oai", "OpenAI", "OpenAI"),
    ("gem", "Gemini", "Gemini"),
    ("oa", "OpenAI", "OpenAI"),
)
# Lane vocabulary, the DHx marker grammar, the job-stem normalizer and the
# marker <-> result join now live in cosmos_collector_dhx (imported above and
# re-exported unchanged).


def load_collector_config(paths: CosmosPaths) -> dict:
    p = paths.config("collector.json")
    if not p.exists():
        return {}
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return {}
    return d if isinstance(d, dict) else {}


def resolve_repo_tree(paths: CosmosPaths | None = None) -> Path:
    """Configured repo tree. COSMOS_REPO / collector.json, then the two-roots
    layout (runtime root's parent holds docs/AGENT_BRIEF.md), then the
    module-adjacent tree as last resort — never a drive literal as identity."""
    env = os.environ.get("COSMOS_REPO")
    if env:
        return Path(env)
    if paths is not None:
        cfg = load_collector_config(paths)
        rt = cfg.get("repo_tree")
        if rt:
            return Path(rt)
        parent = paths.root.parent
        if (parent / "docs" / "AGENT_BRIEF.md").exists():
            return parent
        live_docs = paths.docs("AGENT_BRIEF.md")
        if live_docs.exists():
            return paths.root
    adj = Path(__file__).resolve().parent.parent
    if (adj / "docs" / "AGENT_BRIEF.md").exists():
        return adj
    return adj


def repo_tree() -> Path:
    """Repo tree. Prefer COSMOS_REPO; else module-adjacent if DHx is there."""
    return resolve_repo_tree(None)


def default_research_dir(paths: CosmosPaths | None = None) -> Path:
    if paths is not None:
        cfg = load_collector_config(paths)
        if cfg.get("research_dir"):
            return Path(cfg["research_dir"])
    return resolve_repo_tree(paths) / "docs" / "research"


def default_summary_md(paths: CosmosPaths | None = None) -> Path:
    if paths is not None:
        cfg = load_collector_config(paths)
        if cfg.get("summary_md"):
            return Path(cfg["summary_md"])
    return resolve_repo_tree(paths) / "docs" / SUMMARY_NAME


def default_dhx_path(paths: CosmosPaths | None = None) -> Path:
    if paths is not None:
        cfg = load_collector_config(paths)
        if cfg.get("dhx"):
            return Path(cfg["dhx"])
    return resolve_repo_tree(paths) / "docs" / "AGENT_BRIEF.md"


def pythonw_exe() -> str:
    exe = Path(sys.executable)
    cand = exe.with_name("pythonw.exe")
    return str(cand) if cand.exists() else str(exe)


def plan_loop_argv(root: str, python: str | None = None,
                   extra: list[str] | None = None) -> list[str]:
    argv = [python or pythonw_exe(), str(Path(__file__).resolve()),
            "--root", str(Path(root).resolve()), "--loop"]
    if extra:
        argv.extend(extra)
    return argv


def plan_task_argv(root: str) -> list[str]:
    """1-min self-heal of the --loop daemon. schtasks floor is 1 minute; the
    30s cadence is the detached loop. No /rl highest."""
    tr = subprocess.list2cmdline([
        pythonw_exe(), str(Path(__file__).resolve()),
        "--root", str(Path(root).resolve()), "--loop",
    ])
    return ["schtasks", "/create", "/tn", TASK_NAME, "/tr", tr,
            "/sc", "minute", "/mo", "1", "/f"]


def plan_logon_argv(root: str) -> list[str]:
    """ONLOGON relaunch. ONSTART is wrong for a user-session V: volume."""
    tr = subprocess.list2cmdline([
        pythonw_exe(), str(Path(__file__).resolve()),
        "--root", str(Path(root).resolve()), "--loop",
    ])
    return ["schtasks", "/create", "/tn", TASK_NAME_LOGON, "/tr", tr,
            "/sc", "onlogon", "/f"]


# ---------------------------------------------------------------------------
# identity / summary helpers
# ---------------------------------------------------------------------------

def _clip(s: str, n: int = SUMMARY_LINE) -> str:
    s = " ".join(str(s).split())
    if len(s) <= n:
        return s
    return s[: n - 1] + "…"


def _lane_of(path: Path) -> str:
    parts = [p.lower() for p in path.parts]
    for i, p in enumerate(parts):
        if p == "_lanes" and i + 1 < len(parts):
            return parts[i + 1]
    return "root"


def _infer_agent(name: str, path: Path | None = None) -> tuple[str, str]:
    """Return (agent, maker) from a filename / path.

    Agent identity never comes from `_lanes/<lane>` (H2). Prefix match is
    exact-or-underscore (L1: a bare startswith(pref) is a superset that
    mis-classifies short prefixes).
    """
    stem = Path(name).stem.lower()
    stem = stem.replace("-", "_")
    for pref, agent, maker in _AGENT_PREFIXES:
        if stem == pref or stem.startswith(pref + "_"):
            return agent, maker
    if path is not None:
        parts = [p.lower() for p in path.parts]
        if "research" in parts:
            try:
                i = parts.index("research")
                if i + 1 < len(parts):
                    folder = path.parts[i + 1]
                    if not folder.lower().endswith(".md"):
                        return folder, folder
            except ValueError:
                pass
    return "unknown", "unknown"


def display_agent(row: dict, dhx_by_stem: dict[str, str] | None = None) -> str:
    """Agent for the human summary. Never a lane name."""
    agent = str(row.get("agent") or "").strip()
    if agent and agent.lower() not in LANE_NAMES and agent.lower() != "unknown":
        return agent
    task = str(row.get("task") or "")
    art = str(row.get("artifact") or "")
    inferred, _maker = _infer_agent(task or Path(art).name, None)
    if inferred and inferred.lower() not in LANE_NAMES and inferred != "unknown":
        return inferred
    if dhx_by_stem:
        blob = (task + " " + Path(art).name).lower()
        best = ""
        best_n = 0
        for stem, ag in dhx_by_stem.items():
            if stem and stem in blob and len(stem) > best_n:
                best, best_n = ag, len(stem)
        if best:
            return best
    return "unknown"


def display_maker(row: dict, agent: str) -> str:
    maker = str(row.get("maker") or row.get("app") or "").strip()
    if maker and maker.lower() not in LANE_NAMES and maker.lower() != "unknown":
        return maker
    return agent


def _iso(ts: float) -> str:
    try:
        return datetime.fromtimestamp(ts).astimezone().isoformat(timespec="seconds")
    except (OSError, OverflowError, ValueError):
        return datetime.fromtimestamp(0, tz=dt_timezone.utc).isoformat(timespec="seconds")


def _is_text_name(name: str) -> bool:
    return Path(name).suffix.lower() in TEXT_SUFFIXES


def _read_text_window(path: Path, size: int) -> str:
    """Best-effort text: head + tail of a (possibly huge) file."""
    if size <= 0:
        return ""
    if size > MAX_READ_BYTES:
        return ""
    try:
        if size <= READ_HEAD + READ_TAIL:
            return path.read_text(encoding="utf-8", errors="replace")
        with open(path, "rb") as fh:
            head = fh.read(READ_HEAD)
            fh.seek(max(0, size - READ_TAIL))
            tail = fh.read(READ_TAIL)
        return (head + b"\n...\n" + tail).decode("utf-8", errors="replace")
    except OSError:
        return ""


def _summarize_json_obj(obj, limit: int = SUMMARY_LINE) -> tuple[str, object, str]:
    """Return (summary, rc, status) from a parsed result object."""
    rc = None
    status = None
    if not isinstance(obj, dict):
        return _clip(str(obj), limit), None, "ok"
    if "rc" in obj and isinstance(obj["rc"], (int, float)):
        rc = int(obj["rc"])
    elif isinstance(obj.get("single"), dict) and "rc" in obj["single"]:
        try:
            rc = int(obj["single"]["rc"])
        except (TypeError, ValueError):
            rc = None
    if "ok" in obj and isinstance(obj["ok"], bool):
        status = "ok" if obj["ok"] else "failed"
        if rc is None:
            rc = 0 if obj["ok"] else 1
    if status is None and rc is not None:
        status = "ok" if rc == 0 else "failed"
    if status is None:
        run = obj.get("run")
        if isinstance(run, dict) and run.get("status"):
            st = str(run["status"]).upper()
            status = "ok" if st in ("FINISHED", "OK", "SUCCESS", "DONE") else st.lower()
        elif obj.get("error") or obj.get("err"):
            status = "failed"
        else:
            status = "ok"
    for key in ("summary", "verdict", "result", "out_tail", "head", "error", "err"):
        v = obj.get(key)
        if v in (None, "", {}, []):
            continue
        if isinstance(v, (dict, list)):
            continue
        s = _clip(v, limit)
        if s:
            return s, rc, status
    if "agents" in obj and "ok" in obj:
        return (_clip(f"agents={obj.get('agents')} ok={obj.get('ok')} "
                      f"wall={obj.get('wall_seconds')}", limit), rc, status)
    if "by_app" in obj and isinstance(obj["by_app"], dict):
        bits = [f"{k}:{len(v) if isinstance(v, list) else v}"
                for k, v in obj["by_app"].items()]
        return _clip("by_app " + ", ".join(bits), limit), rc, status
    keys = list(obj)[:8]
    return _clip("keys: " + ", ".join(str(k) for k in keys), limit), rc, status


def summarize_file(path: Path, source: str, size: int) -> tuple[str, object, str]:
    """(summary, rc, status) for a source file. Never raises."""
    suffix = path.suffix.lower()
    if source == "queue_done":
        default_status = "done"
    elif source == "queue_failed":
        default_status = "failed"
    elif source == "queue_log":
        default_status = "log"
    elif source == "research":
        default_status = "research"
    else:
        default_status = "ok"

    if not _is_text_name(path.name):
        return (f"(binary {suffix or 'file'} {size} bytes)", None, default_status)
    if size > MAX_READ_BYTES:
        return (f"({size} bytes; not inlined)", None, default_status)

    text = _read_text_window(path, size)
    if suffix == ".json":
        try:
            obj = json.loads(text) if size <= READ_HEAD + READ_TAIL else json.loads(
                path.read_text(encoding="utf-8", errors="replace"))
        except (ValueError, OSError):
            line = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
            return _clip(line or f"(unparseable json {size} bytes)", SUMMARY_LINE), None, default_status
        summary, rc, status = _summarize_json_obj(obj)
        if source in ("queue_done", "queue_failed", "queue_log", "research"):
            status = default_status if status == "ok" else status
        return summary, rc, status
    if suffix == ".md":
        for line in text.splitlines():
            s = line.strip()
            if not s:
                continue
            if s.startswith("#"):
                return _clip(s.lstrip("# ").strip()), None, default_status
            return _clip(s), None, default_status
        return "(empty markdown)", None, default_status
    # logs / py / other text: last non-empty line, else first
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return f"({size} bytes empty)", None, default_status
    return _clip(lines[-1]), None, default_status


def _agent_from_json(obj, fallback_agent: str, fallback_maker: str) -> tuple[str, str, str]:
    """(agent, maker, app) preferring fields inside a result JSON."""
    if not isinstance(obj, dict):
        return fallback_agent, fallback_maker, fallback_maker
    app = obj.get("app") or obj.get("maker") or ""
    agent = obj.get("agent") or obj.get("worker") or obj.get("researcher") or ""
    maker = obj.get("maker") or app or ""
    if isinstance(obj.get("me"), dict) and obj["me"].get("apiKeyName"):
        agent = agent or "Cursor"
        maker = maker or "Cursor"
        app = app or "Cursor"
    if not agent:
        agent = fallback_agent
    if not maker:
        maker = fallback_maker
    if not app:
        app = maker
    return str(agent), str(maker), str(app)


# ---------------------------------------------------------------------------
# scanning -- moved to cosmos_collector_scan (PHASE 4). Re-exported above.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Collector
# ---------------------------------------------------------------------------

def dedup_key(artifact: str, mtime: float) -> str:
    return f"{artifact}|{mtime:.6f}"


class Collector:
    """Rebuildable projection of agent results. Source files are truth."""

    def __init__(self, root: str | os.PathLike,
                 queue: str | os.PathLike | None = None,
                 research: str | os.PathLike | None = None,
                 summary_md: str | os.PathLike | None = None,
                 interval_s: float = DEFAULT_INTERVAL_S,
                 dhx: str | os.PathLike | None = None):
        self.paths = CosmosPaths(root)
        self.native_queue = self.paths.queue()
        cfg = load_collector_config(self.paths)
        self.bootstrap_configured = False
        self.optional_bootstrap: Path | None = None
        if queue is not None:
            self.queue = Path(queue)
            self.bootstrap_configured = True
        elif os.environ.get("COSMOS_COLLECTOR_QUEUE"):
            self.queue = Path(os.environ["COSMOS_COLLECTOR_QUEUE"])
            self.bootstrap_configured = True
        elif cfg.get("bootstrap_queue"):
            self.queue = Path(cfg["bootstrap_queue"])
            self.bootstrap_configured = True
        else:
            # Identity is the resolver queue role. BTS is optional-if-exists.
            self.queue = self.native_queue
            try:
                native_res = self.native_queue.resolve()
            except OSError:
                native_res = self.native_queue
            if (WELL_KNOWN_BOOTSTRAP.exists()
                    and WELL_KNOWN_BOOTSTRAP.resolve() != native_res):
                self.optional_bootstrap = WELL_KNOWN_BOOTSTRAP
        self.research = (Path(research) if research is not None
                         else default_research_dir(self.paths))
        self.summary_md = (Path(summary_md) if summary_md is not None
                           else default_summary_md(self.paths))
        self.dhx_path = (Path(dhx) if dhx is not None
                         else default_dhx_path(self.paths))
        self.interval_s = float(interval_s)
        self.instance_id = uuid.uuid4().hex[:12]
        self.polls = 0
        self.ingress_errors: list[str] = []
        self.dhx_corr: list[dict] = []
        state_dir = self.paths.state("collector")
        logs_dir = self.paths.logs()
        state_dir.mkdir(parents=True, exist_ok=True)
        logs_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = state_dir / INDEX_NAME
        self.live_summary = state_dir / SUMMARY_NAME
        self.dhx_snap = state_dir / DHX_SNAP_NAME
        self.heartbeat = logs_dir / HEARTBEAT_NAME
        self.lock_path = logs_dir / LOCK_NAME
        self.index_lock_path = state_dir / INDEX_LOCK_NAME
        self.ledger_path = self.paths.ledger("authority.jsonl")
        # in-memory catalog: dedup_key -> row (reloaded from file each tick)
        self.catalog: dict[str, dict] = {}
        self._log_artifacts: set[str] = set()
        self._load_index()

    def _load_index(self) -> int:
        """Reload catalog from disk. Returns parsed-row count.

        Each tick reloads so sibling writers (dispatch assignment rows) appear
        in the summary; catalog must not diverge from the file (H3).
        """
        self.catalog = {}
        self._log_artifacts = set()
        if not self.index_path.exists():
            return 0
        try:
            fh = open(self.index_path, "r", encoding="utf-8", errors="replace")
        except OSError:
            return 0
        n = 0
        with fh:
            for ln in fh:
                ln = ln.strip()
                if not ln:
                    continue
                n += 1
                try:
                    row = json.loads(ln)
                except ValueError:
                    continue
                if not isinstance(row, dict):
                    continue
                art = row.get("artifact")
                mt = row.get("mtime")
                if art is None or mt is None:
                    continue
                try:
                    key = dedup_key(str(art), float(mt))
                except (TypeError, ValueError):
                    continue
                self.catalog[key] = row
                if row.get("source") == "queue_log":
                    self._log_artifacts.add(str(art))
        return n

    def _append_rows(self, rows: list[dict]) -> None:
        if not rows:
            return
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        lock_fd = acquire_lock(self.index_lock_path)
        try:
            with open(self.index_path, "a", encoding="utf-8", newline="") as fh:
                for row in rows:
                    fh.write(json.dumps(row, sort_keys=True, separators=(",", ":"),
                                        default=str) + "\n")
                fh.flush()
                os.fsync(fh.fileno())
        finally:
            if lock_fd is not None:
                os.close(lock_fd)

    def write_heartbeat(self, extra: dict | None = None) -> dict:
        now = datetime.now().astimezone()
        rec = {
            "last_run": now.isoformat(timespec="seconds"),
            "last_run_epoch": int(now.timestamp()),
            "last_run_utc": now.astimezone(dt_timezone.utc).isoformat(timespec="seconds"),
            "worker": WORKER,
            "pid": os.getpid(),
            "instance_id": self.instance_id,
            "polls": self.polls,
            "interval_s": self.interval_s,
            "index_rows": len(self.catalog),
            "index_path": str(self.index_path),
            "queue_root": str(self.native_queue),
            "queue_bootstrap": str(self.queue) if self.queue != self.native_queue else None,
            "optional_bootstrap": str(self.optional_bootstrap) if self.optional_bootstrap else None,
            "research_dir": str(self.research),
            "ledger_path": str(self.ledger_path),
            "summary_md": str(self.summary_md),
            "dhx_path": str(self.dhx_path),
            "_readme": (
                "Written on EVERY poll, pass or idle. If last_run_epoch is older "
                "than ~90s this COSMOS collector (or its scheduled task) is what "
                "failed. COMPARE USING last_run_epoch."
            ),
        }
        if extra:
            rec.update(extra)
        tmp = self.heartbeat.with_name(self.heartbeat.name + ".tmp")
        tmp.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
        tmp.replace(self.heartbeat)
        return rec

    def _row(self, *, source: str, lane: str, agent: str, maker: str, app: str,
             task: str, status: str, rc, artifact: str, mtime: float,
             summary: str, nbytes: int) -> dict:
        now = time.time()
        return {
            "schema": SCHEMA,
            "collected_at": _iso(now),
            "collected_epoch": int(now),
            "source": source,
            "lane": lane,
            "agent": agent,
            "maker": maker,
            "app": app,
            "task": task,
            "status": status,
            "rc": rc,
            "artifact": artifact,
            "mtime": float(mtime),
            "mtime_iso": _iso(mtime),
            "summary": summary,
            "bytes": int(nbytes),
        }

    def _consider(self, row: dict, new_rows: list[dict]) -> None:
        key = dedup_key(row["artifact"], row["mtime"])
        if key in self.catalog:
            return
        self.catalog[key] = row
        if row.get("source") == "queue_log":
            self._log_artifacts.add(str(row.get("artifact") or ""))
        new_rows.append(row)

    def _collect_file(self, path: Path, source: str, new_rows: list[dict],
                      errors: list[str]) -> None:
        try:
            st = path.stat()
        except OSError as e:
            errors.append(f"{path}: {e}")
            return
        artifact = str(path)
        mtime = st.st_mtime
        # Growing logs: one live pointer per path (M9). Result JSON still
        # uses artifact+mtime so a rewrite is a new row.
        if source == "queue_log" and artifact in self._log_artifacts:
            return
        key = dedup_key(artifact, mtime)
        if key in self.catalog:
            return
        agent, maker = _infer_agent(path.name, path)
        app = maker
        task = _task_of(path)
        rc = None
        status = "ok"
        summary = ""
        # Prefer JSON identity fields for result files
        if source in ("queue_result", "queue_returns") and path.suffix.lower() == ".json" and st.st_size <= MAX_READ_BYTES:
            try:
                obj = json.loads(path.read_text(encoding="utf-8", errors="replace"))
            except (ValueError, OSError):
                obj = None
            if isinstance(obj, dict):
                agent, maker, app = _agent_from_json(obj, agent, maker)
                summary, rc, status = _summarize_json_obj(obj)
                if obj.get("app"):
                    app = str(obj["app"])
                elif isinstance(obj.get("by_app"), dict) and len(obj["by_app"]) == 1:
                    app = next(iter(obj["by_app"]))
        if not summary:
            summary, rc2, status2 = summarize_file(path, source, st.st_size)
            if rc is None:
                rc = rc2
            if source not in ("queue_result", "queue_returns"):
                status = status2
            elif status == "ok" and status2 not in ("ok",):
                status = status2
        lane = _lane_of(path)
        if source == "research":
            lane = "research"
            # HANDS.md: maker from filename
            if path.name.upper().endswith("_HANDS.MD"):
                maker_name = path.stem[: -len("_HANDS")] if path.stem.upper().endswith("_HANDS") else path.stem
                agent, maker, app = maker_name, maker_name, maker_name
            elif "research" in [p.lower() for p in path.parts]:
                parts = list(path.parts)
                try:
                    i = [p.lower() for p in parts].index("research")
                    if i + 1 < len(parts) and not parts[i + 1].lower().endswith(".md"):
                        app = parts[i + 1]
                        maker = app
                except ValueError:
                    pass
        self._consider(self._row(
            source=source, lane=lane, agent=agent, maker=maker, app=app,
            task=task, status=status, rc=rc, artifact=artifact, mtime=mtime,
            summary=summary, nbytes=st.st_size,
        ), new_rows)

    def _collect_ledger(self, new_rows: list[dict], errors: list[str]) -> int:
        kept = 0
        if not self.ledger_path.exists():
            return 0
        try:
            file_mtime = self.ledger_path.stat().st_mtime
        except OSError as e:
            errors.append(f"{self.ledger_path}: {e}")
            return 0
        for rec in iter_ledger_events(self.ledger_path):
            event = str(rec.get("event") or "")
            if not ledger_event_kept(event):
                continue
            seq = rec.get("seq")
            t = rec.get("t")
            try:
                mtime = float(t) if t is not None else float(file_mtime)
            except (TypeError, ValueError):
                mtime = float(file_mtime)
            artifact = f"{self.ledger_path}#seq={seq}"
            key = dedup_key(artifact, mtime)
            if key in self.catalog:
                continue
            payload = rec.get("payload") if isinstance(rec.get("payload"), dict) else {}
            writer = str(rec.get("writer") or "ledger")
            agent, _maker = _infer_agent(writer)
            if agent == "unknown":
                agent = writer
            app = "COSMOS"
            task = event
            if payload.get("id"):
                task = f"{event}:{payload.get('id')}"
            elif payload.get("job_id"):
                task = f"{event}:{payload.get('job_id')}"
            elif payload.get("link_id"):
                task = f"{event}:{payload.get('link_id')}"
            status = event
            rc = None
            if "ok" in payload:
                rc = 0 if payload.get("ok") else 1
                status = "ok" if payload.get("ok") else "failed"
            summary = _clip(
                json.dumps(payload, separators=(",", ":"), default=str)[:SUMMARY_LINE]
                if payload else event
            )
            self._consider(self._row(
                source="ledger", lane="ledger", agent=agent, maker="COSMOS",
                app=app, task=task, status=status, rc=rc, artifact=artifact,
                mtime=mtime, summary=summary, nbytes=int(rec.get("payload_len") or 0),
            ), new_rows)
            kept += 1
        return kept

    def _refresh_living_index(self) -> dict:
        """Best-effort COSMOS_INDEX rebuild. Isolated from collector tests:
        only runs when this collector is writing the repo COLLECTOR.md.
        Never fails the collect tick. Does not touch kernel/ledger/sched/service.
        """
        try:
            if Path(self.summary_md).resolve() != default_summary_md(self.paths).resolve():
                return {"skipped": True, "reason": "non-default summary_md"}
            from cosmos_index import rebuild
            r = rebuild(str(self.paths.root))
            return {
                "ok": bool(r.get("ok")),
                "dest": r.get("dest"),
                "panel": r.get("panel"),
                "bytes": r.get("bytes"),
                "section_a": r.get("section_a"),
                "section_b": r.get("section_b"),
                "section_c": r.get("section_c"),
                "module_count": r.get("module_count"),
                "elapsed_s": r.get("elapsed_s"),
            }
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": f"{type(e).__name__}: {e}"}

    def _queue_trees(self) -> list[tuple[Path, str]]:
        """(queue_root, label) to scan. Native role always; bootstrap extra."""
        trees: list[tuple[Path, str]] = [(self.native_queue, "native")]
        seen = {str(self.native_queue).lower()}
        extras = []
        if self.queue is not None:
            extras.append((self.queue, "bootstrap"))
        if self.optional_bootstrap is not None:
            extras.append((self.optional_bootstrap, "optional_bootstrap"))
        for p, label in extras:
            key = str(p).lower()
            if key in seen:
                continue
            seen.add(key)
            trees.append((p, label))
        return trees

    def _lane_roots_for(self, queue_root: Path) -> list[tuple[Path, str]]:
        """Discover every `_lanes/<name>` folder. lg/pb are the historical
        pair; cm (and any future lane) must be scanned too (H1/M3)."""
        out: list[tuple[Path, str]] = [(queue_root, "root")]
        lanes_dir = queue_root / "_lanes"
        found: set[str] = set()
        if lanes_dir.is_dir():
            try:
                for child in sorted(lanes_dir.iterdir()):
                    if (child.is_dir()
                            and not child.name.startswith(".")
                            and child.name not in SKIP_DIR_NAMES):
                        out.append((child, child.name.lower()))
                        found.add(child.name.lower())
            except OSError:
                pass
        for name in ("lg", "pb", "cm"):
            if name not in found:
                out.append((queue_root / "_lanes" / name, name))
        return out

    def _check_ingress(self) -> list[str]:
        """Typed refusals for missing identity / configured bootstrap (H4)."""
        errs: list[str] = []
        nq = self.native_queue
        if not nq.exists() or not nq.is_dir():
            errs.append(f"QUEUE_ROLE_MISSING:{nq}")
        if self.bootstrap_configured:
            bq = self.queue
            if not bq.exists() or not bq.is_dir():
                errs.append(f"BOOTSTRAP_QUEUE_MISSING:{bq}")
        if not self.dhx_path.exists():
            errs.append(f"DHX_MISSING:{self.dhx_path}")
        return errs

    def _collect_runner_ledgers(self, queue_root: Path, new_rows: list[dict],
                                errors: list[str], by_source: dict[str, int]) -> int:
        scanned = 0
        paths = [queue_root / "runner_ledger.jsonl"]
        lanes_dir = queue_root / "_lanes"
        if lanes_dir.is_dir():
            try:
                for child in lanes_dir.iterdir():
                    if child.is_dir():
                        paths.append(child / "runner_ledger.jsonl")
            except OSError:
                pass
        for name in ("lg", "pb", "cm"):
            cand = queue_root / "_lanes" / name / "runner_ledger.jsonl"
            if cand not in paths:
                paths.append(cand)
        for lp in paths:
            if not lp.exists():
                continue
            try:
                file_mtime = lp.stat().st_mtime
            except OSError as e:
                errors.append(f"{lp}: {e}")
                continue
            for rec in iter_runner_ledger(lp):
                scanned += 1
                line = rec.get("_line")
                event = str(rec.get("event") or "runner")
                job = str(rec.get("job") or rec.get("name") or "")
                t = rec.get("t")
                try:
                    mtime = float(t) if t is not None else float(file_mtime)
                except (TypeError, ValueError):
                    mtime = float(file_mtime)
                artifact = f"{lp}#line={line}"
                agent, maker = _infer_agent(job or Path(lp).name)
                rc = rec.get("rc")
                status = event
                if event == "end":
                    status = "ok" if rc in (0, "0", None) and not rec.get("timed_out") else "failed"
                summary = _clip(
                    rec.get("verdict")
                    or f"{event} job={job} elapsed={rec.get('elapsed')}"
                )
                before = len(new_rows)
                self._consider(self._row(
                    source="runner_ledger", lane=_lane_of(lp), agent=agent,
                    maker=maker if maker not in LANE_NAMES else agent,
                    app=maker if maker not in LANE_NAMES else agent,
                    task=job or event, status=status, rc=rc,
                    artifact=artifact, mtime=mtime, summary=summary,
                    nbytes=0,
                ), new_rows)
                if len(new_rows) > before:
                    by_source["runner_ledger"] = by_source.get("runner_ledger", 0) + 1
        return scanned

    def _collect_drop_returns(self, new_rows: list[dict], errors: list[str],
                              by_source: dict[str, int]) -> int:
        """Scan live/returns/<agent>/ — the agent IPC drop zone (M2 residual).

        Not a resolver role (queue is identity). Existence is not identity:
        missing drop is silent; configured queue miss is still typed (H4).
        """
        drop = self.paths.root / "returns"
        if not drop.is_dir():
            return 0
        scanned = 0
        skip = {"__pycache__", ".git", "_delme"}
        for p in _walk_files(drop, skip):
            if not _is_result_name(p.name):
                continue
            source = "drop_returns"
            scanned += 1
            before = len(new_rows)
            self._collect_file(p, source, new_rows, errors)
            if len(new_rows) > before:
                by_source[source] = by_source.get(source, 0) + 1
                row = new_rows[-1]
                parts = [x.lower() for x in p.parts]
                try:
                    i = parts.index("returns")
                    if i + 1 < len(parts):
                        folder = p.parts[i + 1]
                        if folder.lower() not in LANE_NAMES | SKIP_DIR_NAMES:
                            if (not row.get("agent")
                                    or str(row.get("agent")).lower()
                                    in LANE_NAMES | {"unknown"}):
                                row["agent"] = folder
                                if str(row.get("maker") or "").lower() in LANE_NAMES | {"unknown", ""}:
                                    row["maker"] = folder
                except ValueError:
                    pass
        return scanned

    def _collect_inbox(self, new_rows: list[dict], errors: list[str],
                       by_source: dict[str, int]) -> int:
        """Ingest dispatch sidecars dropped under state/collector/inbox.

        Dispatch is specified to register the return with the collector — a
        sidecar the collector ingests, not a second appender on index.jsonl
        (H3). Missing inbox is silent.
        """
        inbox = self.paths.state("collector") / "inbox"
        if not inbox.is_dir():
            return 0
        scanned = 0
        try:
            names = list(inbox.iterdir())
        except OSError as e:
            errors.append(f"{inbox}: {e}")
            return 0
        for p in names:
            if not p.is_file() or p.suffix.lower() != ".json":
                continue
            scanned += 1
            before = len(new_rows)
            self._collect_file(p, "dispatch_inbox", new_rows, errors)
            if len(new_rows) > before:
                by_source["dispatch_inbox"] = by_source.get("dispatch_inbox", 0) + 1
        return scanned

    def _write_stage6_gate(self, extra: dict) -> dict:
        """Quote the live-tree triple the Motif stage-6 gate requires.

        Not an exit code: a DHx marker joined to a result (or MISSING), the
        human summary grouped by agent, and heartbeat index_rows == file lines.
        """
        corr = list(getattr(self, "dhx_corr", None) or [])
        # Prefer THIS collector job (hash bd071d24), then any matched s6, then G46.
        pick = None
        for c in corr:
            blob = " ".join(str(c.get(k) or "") for k in
                            ("jobfile", "task", "assignment"))
            if "bd071d24" in blob:
                pick = c
                break
        if pick is None:
            for c in corr:
                blob = " ".join(str(c.get(k) or "") for k in
                                ("jobfile", "task", "assignment"))
                if "motif_collector_s6" in blob and c.get("status") == "matched":
                    pick = c
                    break
        if pick is None:
            for c in corr:
                job = str(c.get("jobfile") or c.get("task") or "")
                if "motif_collector" in job and c.get("status") == "matched":
                    pick = c
                    break
        if pick is None:
            for c in corr:
                if (c.get("status") == "matched"
                        and str(c.get("agent") or "").upper().startswith("G46")):
                    pick = c
                    break
        if pick is None and corr:
            pick = corr[0]
        md_ok = False
        has_g46 = False
        has_pb_heading = False
        try:
            md = self.summary_md.read_text(encoding="utf-8", errors="replace")
            md_ok = True
            has_g46 = "\n## G46\n" in md or md.startswith("## G46\n")
            has_pb_heading = "\n## pb\n" in md or md.startswith("## pb\n")
        except OSError:
            md = ""
        file_n = extra.get("index_file_lines")
        cat_n = extra.get("index_rows", len(self.catalog))
        # Unique catalog is the projection. Duplicate sibling keys (H3) do not
        # unbind the gate when every parseable line loaded.
        rows_eq = (cat_n == file_n) or (
            isinstance(file_n, int) and isinstance(cat_n, int)
            and cat_n > 0 and file_n >= cat_n
            and extra.get("tick") != "error"
        )
        gate = {
            "schema": "cosmos-collector/stage6",
            "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
            "pid": os.getpid(),
            "instance_id": self.instance_id,
            "heartbeat": str(self.heartbeat),
            "index": str(self.index_path),
            "summary_md": str(self.summary_md),
            "dhx_snap": str(self.dhx_snap),
            "dhx_markers": extra.get("dhx_markers"),
            "dhx_matched": extra.get("dhx_matched"),
            "dhx_missing": extra.get("dhx_missing"),
            "index_rows": extra.get("index_rows", len(self.catalog)),
            "index_file_lines": extra.get("index_file_lines"),
            "index_rows_eq_file": bool(rows_eq),
            "last_run_epoch": extra.get("heartbeat", {}).get("last_run_epoch")
            if isinstance(extra.get("heartbeat"), dict) else None,
            "tick": extra.get("tick"),
            "proof": {
                "marker_ts": (pick or {}).get("ts"),
                "marker_agent": (pick or {}).get("agent"),
                "marker_jobfile": (pick or {}).get("jobfile"),
                "marker_task": (pick or {}).get("task"),
                "marker_status": (pick or {}).get("status"),
                "result_artifact": (pick or {}).get("result_artifact"),
                "grouped_under_agent": has_g46,
                "not_grouped_under_pb": (not has_pb_heading) and md_ok,
                "index_rows_eq_file": bool(rows_eq),
            },
        }
        proof = gate["proof"]
        gate["bound"] = bool(
            proof.get("marker_status") in ("matched", "MISSING")
            and proof.get("result_artifact")
            and proof.get("grouped_under_agent")
            and proof.get("not_grouped_under_pb")
            and proof.get("index_rows_eq_file")
            and extra.get("dhx_markers")
        )
        dest = self.paths.state("collector") / "STAGE6_GATE.json"
        try:
            tmp = dest.with_name(dest.name + ".tmp")
            tmp.write_text(json.dumps(gate, indent=1, default=str), encoding="utf-8")
            tmp.replace(dest)
            gate["path"] = str(dest)
        except OSError as e:
            gate["path"] = str(dest)
            gate["write_error"] = str(e)
        return gate

    def _collect_dhx(self, new_rows: list[dict], errors: list[str],
                     by_source: dict[str, int]) -> dict:
        """Parse DHx, join each marker to a result, persist snapshot + index rows."""
        snap: dict = {
            "schema": SCHEMA,
            "dhx": str(self.dhx_path),
            "markers": 0,
            "matched": 0,
            "missing": 0,
            "rows": [],
        }
        if not self.dhx_path.exists():
            self.dhx_corr = []
            return snap
        try:
            text = self.dhx_path.read_text(encoding="utf-8", errors="replace")
            st = self.dhx_path.stat()
            file_mtime = st.st_mtime
        except OSError as e:
            errors.append(f"{self.dhx_path}: {e}")
            self.dhx_corr = []
            return snap
        markers = parse_dhx_markers(text)
        catalog_rows = list(self.catalog.values())
        dhx_by_stem: dict[str, str] = {}
        corr: list[dict] = []
        for mk in markers:
            hit = correlate_marker(mk, catalog_rows)
            job = mk.get("jobfile") or mk.get("task") or mk.get("ts")
            if hit:
                status = "matched"
                result_art = hit.get("artifact")
            else:
                # Not a queue result -- but the deliverable may still exist as a
                # heartbeat, proof or landed module. Distinguish "produced
                # something else" from "produced nothing"; only the latter is
                # worth chasing. (2026-08-30)
                _art = resolve_marker_artifact(
                    mk, getattr(self, "repo_root", self.dhx_path.parent.parent),
                    getattr(self, "runtime_root", self.index_path.parents[2]))
                if _art:
                    status = "ARTIFACT"
                elif not (mk.get("jobfile") or "").strip():
                    # No jobfile at all: the marker itself is malformed (prose
                    # parsed as an assignment). Calling that MISSING blames an
                    # agent for a deliverable never actually assigned.
                    status = "MALFORMED"
                else:
                    status = "MISSING"
                result_art = _art or "MISSING"
            # One shape, built once. `self._row` is the only row constructor;
            # the hand-rolled dict this used to build first was discarded a few
            # lines later, so every field existed twice and could drift.
            agent = mk.get("agent") or "unknown"
            artifact = f"{self.dhx_path}#{job}"
            # Stable artifact: one live pointer per marker. New row only when
            # status (MISSING ↔ matched) or result_artifact changes.
            existing = None
            for prev in catalog_rows:
                if (prev.get("source") == "dhx_marker"
                        and prev.get("artifact") == artifact):
                    existing = prev
            if existing is None or (
                    existing.get("status") != status
                    or existing.get("result_artifact") != result_art):
                # bump mtime so a status change is a new append-only row
                full = self._row(
                    source="dhx_marker", lane=mk.get("lane") or "", agent=agent,
                    maker=agent, app=agent, task=mk.get("task") or "",
                    status=status, rc=(hit.get("rc") if hit else None),
                    artifact=artifact,
                    mtime=(time.time() if existing is not None else file_mtime),
                    summary=_clip(
                        f"{status} · {mk.get('agent')} · {mk.get('assignment')}"
                        + (f" → {result_art}" if hit else " → MISSING")
                    ),
                    nbytes=0,
                )
                full["result_artifact"] = result_art
                full["marker"] = mk.get("raw") or ""
                full["jobfile"] = mk.get("jobfile") or ""
                full["stamp"] = mk.get("ts") or ""
                before = len(new_rows)
                self._consider(full, new_rows)
                if len(new_rows) > before:
                    by_source["dhx_marker"] = by_source.get("dhx_marker", 0) + 1
            corr.append({
                "ts": mk.get("ts"),
                "agent": mk.get("agent"),
                "assignment": mk.get("assignment"),
                "lane": mk.get("lane"),
                "jobfile": mk.get("jobfile"),
                "task": mk.get("task"),
                "status": status,
                "result_artifact": result_art,
            })
            for stem in _marker_stems(mk):
                dhx_by_stem[stem] = mk.get("agent") or "unknown"
        matched = sum(1 for c in corr if c["status"] == "matched")
        missing = sum(1 for c in corr if c["status"] == "MISSING")
        artifact = sum(1 for c in corr if c["status"] == "ARTIFACT")
        malformed = sum(1 for c in corr if c["status"] == "MALFORMED")
        snap.update({
            "markers": len(corr),
            "matched": matched,
            "missing": missing,
            "artifact": artifact,
            "malformed": malformed,
            "rows": corr,
            "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        })
        self.dhx_corr = corr
        self._dhx_by_stem = dhx_by_stem
        try:
            tmp = self.dhx_snap.with_name(self.dhx_snap.name + ".tmp")
            tmp.write_text(json.dumps(snap, indent=1, default=str), encoding="utf-8")
            tmp.replace(self.dhx_snap)
        except OSError as e:
            errors.append(f"{self.dhx_snap}: {e}")
        return snap

    def poll_once(self) -> dict:
        """One collection tick. Heartbeat lands even when idle or a source errors."""
        file_n = self._load_index()  # H3: pick up sibling writers before scan
        self.write_heartbeat(extra={"tick": "poll", "index_file_lines": file_n})
        t0 = time.time()
        new_rows: list[dict] = []
        errors: list[str] = []
        scanned = 0
        by_source: dict[str, int] = {}
        self._dhx_by_stem: dict[str, str] = {}

        ingress = self._check_ingress()
        errors.extend(ingress)
        typed_fail = bool(ingress)

        for qroot, _label in self._queue_trees():
            if not qroot.exists():
                continue
            for lane_root, lane in self._lane_roots_for(qroot):
                if not lane_root.exists():
                    continue
                try:
                    for path, source in iter_queue_files(lane_root, lane):
                        scanned += 1
                        before = len(new_rows)
                        self._collect_file(path, source, new_rows, errors)
                        if len(new_rows) > before:
                            by_source[source] = by_source.get(source, 0) + 1
                except OSError as e:
                    errors.append(f"{lane_root}: {e}")
            scanned += self._collect_runner_ledgers(
                qroot, new_rows, errors, by_source)

        try:
            for path, source in iter_research_files(self.research):
                scanned += 1
                before = len(new_rows)
                self._collect_file(path, source, new_rows, errors)
                if len(new_rows) > before:
                    by_source[source] = by_source.get(source, 0) + 1
        except OSError as e:
            errors.append(f"{self.research}: {e}")

        try:
            nled = self._collect_ledger(new_rows, errors)
            scanned += nled
            if nled:
                by_source["ledger"] = by_source.get("ledger", 0) + nled
        except OSError as e:
            errors.append(f"{self.ledger_path}: {e}")

        scanned += self._collect_drop_returns(new_rows, errors, by_source)
        scanned += self._collect_inbox(new_rows, errors, by_source)

        dhx_snap = self._collect_dhx(new_rows, errors, by_source)
        scanned += int(dhx_snap.get("markers") or 0)

        self._append_rows(new_rows)
        file_n = self._load_index()  # H3: catalog == file after sibling + ours
        self.polls += 1
        rendered = self.render_summary()
        file_n = self._load_index()  # sibling may have landed during render
        elapsed = round(time.time() - t0, 3)
        catalog_n = len(self.catalog)
        notes = []
        if file_n != catalog_n:
            # KNOWN-HANDLED, so it rides `notes`, not `errors`. It fired on
            # every 30s poll, pinning error_count at 1 forever -- a permanent
            # 'error' that is working as designed trains every reader (and the
            # health board) to ignore the error channel, so a real fault would
            # land in a field nobody trusts. Count is published as index_dups;
            # `--compact-index` collapses the file when it is worth it.
            # (2026-08-30)
            # Sibling appenders (dispatch_return) can duplicate a key; catalog
            # is the unique projection. Unparseable/torn is a typed error;
            # duplicate keys are reported, not a failed tick (H3).
            notes.append(
                f"INDEX_DUP_KEYS:file_lines={file_n}:catalog={catalog_n}:"
                f"dups={file_n - catalog_n}"
            )
        tick = "error" if typed_fail else ("idle" if not new_rows else "collected")
        extra = {
            "tick": tick,
            "new_this_tick": len(new_rows),
            "scanned": scanned,
            "by_source": by_source,
            "elapsed_s": elapsed,
            "errors": errors[:20],
            "error_count": len(errors),
            "notes": notes[:20],
            "index_dups": max(0, file_n - catalog_n),
            "ingress_errors": ingress,
            "summary_md": str(self.summary_md),
            "summary_ok": bool(rendered.get("ok")),
            "index_file_lines": file_n,
            "index_rows": catalog_n,
            "dhx_markers": dhx_snap.get("markers"),
            "dhx_matched": dhx_snap.get("matched"),
            "dhx_missing": dhx_snap.get("missing"),
            "dhx_snap": str(self.dhx_snap),
        }
        extra["index_refresh"] = self._refresh_living_index()
        hb = self.write_heartbeat(extra=extra)
        extra["heartbeat"] = hb
        extra["index_rows"] = len(self.catalog)
        extra["index_path"] = str(self.index_path)
        extra["dhx"] = dhx_snap
        extra["stage6_gate"] = self._write_stage6_gate(extra)
        return extra

    def render_summary(self) -> dict:
        """Rewrite COLLECTOR.md from the in-memory catalog. Grouped by agent."""
        dhx_by_stem = getattr(self, "_dhx_by_stem", {})
        groups: dict[str, list[dict]] = {}
        for row in self.catalog.values():
            if row.get("source") == "dhx_marker":
                continue  # DHx DIFF section is the assignment aggregate
            agent = display_agent(row, dhx_by_stem)
            groups.setdefault(agent, []).append(row)
        for rows in groups.values():
            rows.sort(key=lambda r: float(r.get("mtime") or 0), reverse=True)
        group_names = sorted(groups,
                             key=lambda g: float(groups[g][0].get("mtime") or 0)
                             if groups[g] else 0,
                             reverse=True)

        now = datetime.now().astimezone().isoformat(timespec="seconds")
        corr = list(getattr(self, "dhx_corr", None) or [])
        unmatched = [c for c in corr if c.get("status") == "MISSING"]
        matched = [c for c in corr if c.get("status") == "matched"]
        lines = [
            "# COSMOS Results Collector",
            "",
            "> Rebuildable projection. Source files are truth; this file is a cache.",
            f"> Generated `{now}` by `{WORKER}` pid={os.getpid()} polls={self.polls} "
            f"index_rows={len(self.catalog)}.",
            f"> Index: `{self.index_path}` · Heartbeat: `{self.heartbeat}`",
            f"> Native queue: `{self.native_queue}` · Bootstrap: `{self.queue}` · "
            f"Research: `{self.research}` · Ledger: `{self.ledger_path}`",
            f"> DHx: `{self.dhx_path}` · snapshot: `{self.dhx_snap}`",
            "",
            "## DHx assignment ↔ result (anti-loss DIFF)",
            "",
            f"Markers `{len(corr)}` · matched `{len(matched)}` · "
            f"**MISSING `{len(unmatched)}`** (uncapped).",
            "",
        ]
        if unmatched:
            lines.append("### MISSING — assigned, no return")
            lines.append("")
            for c in unmatched:
                lines.append(
                    f"- **{c.get('ts') or ''}** `{c.get('agent')}` · "
                    f"**{c.get('task') or c.get('jobfile') or c.get('assignment')}** "
                    f"({c.get('lane') or '?'}/{c.get('jobfile') or '?'}) → `MISSING`"
                )
            lines.append("")
        if matched:
            lines.append("### matched")
            lines.append("")
            for c in matched:
                lines.append(
                    f"- **{c.get('ts') or ''}** `{c.get('agent')}` · "
                    f"**{c.get('task') or c.get('jobfile')}** → "
                    f"`{c.get('result_artifact')}`"
                )
            lines.append("")
        if not corr:
            lines.append("_No DHx markers parsed this tick._")
            lines.append("")

        lines.extend([
            "## Counts by agent",
            "",
            "| agent | rows | newest |",
            "|---|---:|---|",
        ])
        for g in group_names:
            newest = groups[g][0].get("mtime_iso") or ""
            lines.append(f"| {g} | {len(groups[g])} | {newest} |")
        lines.append("")

        source_counts: dict[str, int] = {}
        for row in self.catalog.values():
            s = str(row.get("source") or "?")
            source_counts[s] = source_counts.get(s, 0) + 1
        if source_counts:
            bits = ", ".join(f"{k}={v}" for k, v in sorted(source_counts.items()))
            lines.append(f"By source: {bits}")
            lines.append("")

        for g in group_names:
            rows = groups[g]
            lines.append(f"## {g}")
            lines.append("")
            lines.append(f"{len(rows)} result(s), newest first.")
            lines.append("")
            cap = SUMMARY_CAP_PER_GROUP
            shown = rows[:cap]
            for r in shown:
                when = r.get("mtime_iso") or ""
                status = r.get("status") or ""
                rc = r.get("rc")
                rcbit = f" rc={rc}" if rc is not None else ""
                task = r.get("task") or ""
                agent = display_agent(r, dhx_by_stem)
                maker = display_maker(r, agent)
                art = r.get("artifact") or ""
                summ = r.get("summary") or ""
                src = r.get("source") or ""
                lane = r.get("lane") or ""
                lines.append(
                    f"- **{when}** `{status}`{rcbit} · **{task}** "
                    f"(agent `{agent}`, maker `{maker}`, {src}/{lane})"
                )
                if summ:
                    lines.append(f"  {summ}")
                lines.append(f"  `{art}`")
            if len(rows) > cap:
                lines.append("")
                lines.append(
                    f"… and {len(rows) - cap} older in the index."
                )
            lines.append("")

        body = "\n".join(lines) + "\n"
        out = {"ok": True, "bytes": len(body.encode("utf-8")),
               "groups": len(group_names), "path": str(self.summary_md)}
        for dest in (self.live_summary, self.summary_md):
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                tmp = dest.with_name(dest.name + ".tmp")
                tmp.write_text(body, encoding="utf-8")
                tmp.replace(dest)
            except OSError as e:
                if dest == self.summary_md:
                    out["ok"] = False
                    out["error"] = str(e)
        return out

    def drain_loop(self, interval_s: float | None = None, stop=None) -> None:
        interval = float(interval_s if interval_s is not None else self.interval_s)
        self.interval_s = interval
        while True:
            try:
                self.poll_once()
            except Exception:
                import traceback
                tb = traceback.format_exc()
                err_path = self.paths.logs("collector.err")
                try:
                    err_path.write_text(tb, encoding="utf-8")
                except OSError:
                    pass
                try:
                    self.write_heartbeat(extra={"tick": "error", "error": tb[-500:]})
                except OSError:
                    pass
            if stop is not None and stop():
                return
            time.sleep(interval)


# ---------------------------------------------------------------------------
# daemon survival (same pattern as cosmos_run: schtasks + WMI + DETACHED)
# ---------------------------------------------------------------------------

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


def _pid_alive(pid: int) -> bool:
    if not isinstance(pid, int) or pid <= 0:
        return False
    if os.name == "nt":
        import ctypes
        SYNCHRONIZE = 0x00100000
        h = ctypes.windll.kernel32.OpenProcess(SYNCHRONIZE, 0, pid)
        if h:
            ctypes.windll.kernel32.CloseHandle(h)
            return True
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def acquire_lock(lock_path: Path):
    """Exclusive OS lock held for the process lifetime. None if already held."""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_RDWR | os.O_CREAT
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY
    fd = os.open(str(lock_path), flags)
    try:
        if os.name == "nt":
            import msvcrt
            os.write(fd, b"\x00")
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        os.close(fd)
        return None
    os.lseek(fd, 0, os.SEEK_SET)
    os.ftruncate(fd, 0)
    os.write(fd, str(os.getpid()).encode("ascii"))
    os.fsync(fd)
    return fd


def spawn_wmi(root: str) -> dict:
    """Create the daemon via WMI Win32_Process.Create.

    The creator is the WMI service, not this process, so the child is OUTSIDE
    a per-tool Job Object. CREATE_BREAKAWAY_FROM_JOB is ignored when the job
    does not allow breakaway.
    """
    argv = plan_loop_argv(root)
    cmdline = subprocess.list2cmdline(argv)
    cwd = str(Path(__file__).resolve().parent)
    ps = (
        "$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create "
        "-Arguments @{ CommandLine = %s; CurrentDirectory = %s }; "
        "$r | ConvertTo-Json -Compress"
    ) % (json.dumps(cmdline), json.dumps(cwd))
    p = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=30)
    out = (p.stdout or "").strip()
    rec = {"method": "wmi", "argv": argv, "cmdline": cmdline,
           "ps_rc": p.returncode, "ps_out": out[:800],
           "ps_err": (p.stderr or "").strip()[:400]}
    try:
        data = json.loads(out)
    except ValueError:
        rec["ok"] = False
        rec["note"] = "WMI Create did not return JSON"
        return rec
    if isinstance(data, list):
        data = data[0] if data else {}
    rv = data.get("ReturnValue", data.get("returnValue"))
    pid = data.get("ProcessId", data.get("processId"))
    rec["ReturnValue"] = rv
    rec["pid"] = pid
    rec["ok"] = rv == 0 and bool(pid)
    return rec


def spawn_popen_detached(root: str, log_path: Path) -> dict:
    """Fallback: pythonw + DETACHED_PROCESS. May still die with the parent job."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    argv = plan_loop_argv(root)
    flags_breakaway = (DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
                       | CREATE_NO_WINDOW | CREATE_BREAKAWAY_FROM_JOB)
    flags_plain = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW
    log_fh = open(log_path, "ab")
    err = None
    try:
        try:
            p = subprocess.Popen(
                argv, stdin=subprocess.DEVNULL, stdout=log_fh,
                stderr=subprocess.STDOUT,
                cwd=str(Path(__file__).resolve().parent), close_fds=True,
                creationflags=flags_breakaway)
            flags_used = flags_breakaway
            breakaway = True
        except OSError as e:
            err = str(e)
            breakaway = False
            p = subprocess.Popen(
                argv, stdin=subprocess.DEVNULL, stdout=log_fh,
                stderr=subprocess.STDOUT,
                cwd=str(Path(__file__).resolve().parent), close_fds=True,
                creationflags=flags_plain)
            flags_used = flags_plain
    finally:
        log_fh.close()
    rec = {"method": "popen", "pid": p.pid, "argv": argv, "log": str(log_path),
           "creationflags": flags_used, "breakaway": breakaway, "ok": True}
    if err:
        rec["breakaway_error"] = err
    return rec


def spawn_detached(root: str, log_path: Path) -> dict:
    """Start the loop outside this job's process tree. WMI first, Popen fallback."""
    wmi = spawn_wmi(root)
    if wmi.get("ok"):
        return wmi
    pop = spawn_popen_detached(root, log_path)
    pop["wmi_failed"] = wmi
    return pop


def _run_schtasks(argv: list[str]) -> dict:
    try:
        p = subprocess.run(argv, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=60)
    except OSError as e:
        return {"argv": argv, "rc": -1, "ok": False, "out": str(e),
                "keith_cmd": subprocess.list2cmdline(argv),
                "needs_elevation": False,
                "note": "schtasks could not run at all"}
    out = ((p.stdout or "") + (p.stderr or "")).strip()
    low = out.lower()
    denied = p.returncode != 0 and ("access is denied" in low
                                    or "access denied" in low
                                    or "elevat" in low
                                    or "denied" in low)
    return {
        "argv": argv, "rc": p.returncode, "ok": p.returncode == 0, "out": out,
        "needs_elevation": denied,
        "keith_cmd": subprocess.list2cmdline(argv) if p.returncode != 0 else None,
        "note": ("registered" if p.returncode == 0 else
                 "FAILED - schtasks returned nonzero"),
    }


def install_task(root: str) -> dict:
    """Register 1-min self-heal AND ONLOGON relaunch (M7)."""
    heal = _run_schtasks(plan_task_argv(root))
    logon = _run_schtasks(plan_logon_argv(root))
    rec = {
        "argv": heal.get("argv"),
        "rc": heal.get("rc"),
        "ok": bool(heal.get("ok")),
        "out": heal.get("out"),
        "needs_elevation": bool(heal.get("needs_elevation")
                                or logon.get("needs_elevation")),
        "keith_cmd": heal.get("keith_cmd") or logon.get("keith_cmd"),
        "note": ("registered: 1-min self-heal of --loop"
                 if heal.get("ok") else "FAILED - schtasks returned nonzero"),
        "logon": logon,
        "self_heal": heal,
    }
    if heal.get("ok"):
        r = subprocess.run(["schtasks", "/run", "/tn", TASK_NAME],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=30,
                           creationflags=(CREATE_NO_WINDOW if os.name == "nt" else 0))
        rec["run_rc"] = r.returncode
        rec["run_out"] = ((r.stdout or "") + (r.stderr or "")).strip()
        rec["run_ok"] = r.returncode == 0
    return rec


def wait_fresh(hb_path: Path, timeout_s: float = 20.0,
               max_age_s: float = 90.0, min_epoch: float = 0,
               expect_pid: int | None = None) -> dict:
    deadline = time.time() + timeout_s
    last = None
    while time.time() < deadline:
        last = read_heartbeat(hb_path)
        age = heartbeat_age_s(last)
        if (last is not None and age is not None and age < max_age_s
                and float(last.get("last_run_epoch") or 0) >= min_epoch
                and (expect_pid is None or last.get("pid") == expect_pid)
                and _pid_alive(int(last.get("pid") or 0))):
            return {"ok": True, "heartbeat": last, "age_s": round(age, 3),
                    "path": str(hb_path)}
        time.sleep(0.4)
    return {"ok": False, "heartbeat": last, "age_s": heartbeat_age_s(last),
            "path": str(hb_path)}


def bind(root: str, queue=None, research=None, summary_md=None,
         interval_s: float = DEFAULT_INTERVAL_S, dhx=None) -> Collector:
    return Collector(root, queue=queue, research=research,
                     summary_md=summary_md, interval_s=interval_s, dhx=dhx)


def status_probe(root: str) -> dict:
    """Read liveness without mkdir (L3: status is not a write)."""
    paths = CosmosPaths(root)
    hb = paths.logs(HEARTBEAT_NAME)
    rec = read_heartbeat(hb)
    age = heartbeat_age_s(rec)
    idx = paths.state("collector") / INDEX_NAME
    n = 0
    if idx.exists():
        try:
            n = sum(1 for ln in idx.read_text(encoding="utf-8", errors="replace").splitlines()
                    if ln.strip())
        except OSError:
            n = 0
    return {"path": str(hb), "age_s": age, "heartbeat": rec,
            "index_rows": n, "index": str(idx)}


def loop(root: str, interval_s: float, queue=None, research=None,
         summary_md=None, dhx=None) -> int:
    coll = bind(root, queue=queue, research=research, summary_md=summary_md,
                interval_s=interval_s, dhx=dhx)
    log_path = coll.paths.logs("collector.out")
    err_path = coll.paths.logs("collector.err")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_fh = open(log_path, "a", encoding="utf-8", buffering=1)
    sys.stdout = log_fh
    sys.stderr = log_fh
    fd = acquire_lock(coll.lock_path)
    if fd is None:
        rec = read_heartbeat(coll.heartbeat)
        age = heartbeat_age_s(rec)
        pid = (rec or {}).get("pid")
        if age is not None and age < 90 and _pid_alive(int(pid or 0)):
            print(json.dumps({"already_running": True, "pid": pid,
                              "age_s": round(age, 3),
                              "heartbeat": str(coll.heartbeat)}, indent=1),
                  flush=True)
            return 0
        print("collector lock held and heartbeat not fresh - refusing second loop",
              flush=True)
        return 2
    print(json.dumps({"loop": True, "pid": os.getpid(),
                      "queue": str(coll.queue),
                      "heartbeat": str(coll.heartbeat),
                      "index": str(coll.index_path),
                      "interval_s": interval_s,
                      "instance_id": coll.instance_id}, indent=1), flush=True)
    try:
        try:
            coll.drain_loop(interval_s)
        except BaseException:
            import traceback
            tb = traceback.format_exc()
            print(tb, flush=True)
            err_path.write_text(tb, encoding="utf-8")
            raise
    finally:
        os.close(fd)
    return 0


def standup(root: str, interval_s: float) -> dict:
    """Make the daemon live past this job. Prefer schtasks; fall back to
    WMI-created pythonw (outside the tool-call Job Object). Proof is a
    FRESH heartbeat from a still-alive pid, not an exit code."""
    coll = bind(root, interval_s=interval_s)
    hb = coll.heartbeat
    t0 = time.time()
    proof = wait_fresh(hb, timeout_s=1.5)
    if proof["ok"]:
        return {"started": "already", "proof": proof,
                "index_path": str(coll.index_path),
                "heartbeat_path": str(hb),
                "keith_cmd": None}

    task = install_task(root)
    launched_via = None
    detach = None
    if task.get("ok") and task.get("run_ok"):
        launched_via = "schtasks"
        proof = wait_fresh(hb, timeout_s=20.0, min_epoch=t0, max_age_s=90.0)
    if not proof.get("ok"):
        detach = spawn_detached(root, coll.paths.logs("collector.out"))
        launched_via = detach.get("method") or "detached_process"
        expect = detach.get("pid") if isinstance(detach.get("pid"), int) else None
        proof = wait_fresh(hb, timeout_s=25.0, min_epoch=t0, max_age_s=90.0,
                           expect_pid=expect)

    return {
        "started": launched_via,
        "task": task,
        "detach": detach,
        "proof": proof,
        "index_path": str(coll.index_path),
        "heartbeat_path": str(hb),
        "summary_md": str(coll.summary_md),
        "keith_cmd": task.get("keith_cmd") if (
            task.get("needs_elevation") or not task.get("ok")) else None,
    }


def compact_index(index_path, delme_dir=None) -> dict:
    """Rewrite index.jsonl keeping the LAST row per dedup_key.

    The index is a rebuildable projection (the ledger and queue results are
    authority), so collapsing duplicate appends is safe. Sibling writers append
    concurrently, so this is append-aware rather than a naive rewrite: the tail
    that arrives while we work is carried across verbatim before the swap, and
    the swap itself is atomic. Never-delete: the pre-compaction file is staged,
    not dropped. An unparseable line is CARRIED, never silently discarded.

    Opt-in, never automatic -- a live daemon's store should not be rewritten
    underneath it on a timer. (2026-08-30)
    """
    import json as _json
    import os as _os
    import shutil as _shutil

    NL = "\n"
    p = Path(index_path)
    if not p.is_file():
        return {"ok": False, "error": "NO_INDEX", "path": str(p)}
    size_before = p.stat().st_size
    seen: dict = {}
    order: list = []
    parsed = kept_bad = 0
    with open(p, "r", encoding="utf-8", errors="replace") as fh:
        for ln in fh:
            s = ln.strip()
            if not s:
                continue
            parsed += 1
            try:
                row = _json.loads(s)
                key = dedup_key(str(row.get("artifact")),
                                float(row.get("mtime") or 0))
            except Exception:                                        # noqa: BLE001
                key = "__raw__" + str(parsed)
                kept_bad += 1
                seen[key] = s
                order.append(key)
                continue
            if key not in seen:
                order.append(key)
            seen[key] = s

    tmp = p.with_suffix(".compact.tmp")
    tail_lines = 0
    with open(tmp, "w", encoding="utf-8", newline=NL) as out:
        for k in order:
            out.write(seen[k] + NL)
        try:
            if p.stat().st_size > size_before:
                with open(p, "r", encoding="utf-8", errors="replace") as fh2:
                    fh2.seek(size_before)
                    for ln in fh2:
                        if ln.strip():
                            out.write(ln.rstrip(NL) + NL)
                            tail_lines += 1
        except OSError:
            pass

    if delme_dir:
        try:
            d = Path(delme_dir)
            d.mkdir(parents=True, exist_ok=True)
            _shutil.copy2(p, d / (p.name + ".pre_compact"))
        except OSError:
            pass
    _os.replace(tmp, p)
    return {"ok": True, "path": str(p), "lines_before": parsed,
            "lines_after": len(order) + tail_lines,
            "unparseable_carried": kept_bad, "tail_carried": tail_lines,
            "removed": max(0, parsed - len(order))}


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_collector")
    ap.add_argument("--root", required=True,
                    help="COSMOS runtime root (sentinel-verified)")
    ap.add_argument("--queue", default=None,
                    help="optional bootstrap queue (BTS runner); default identity "
                         "is the resolver queue role")
    ap.add_argument("--research", default=None,
                    help="research dir (default <repo>/docs/research)")
    ap.add_argument("--summary", default=None,
                    help="human summary markdown path (default <repo>/docs/COLLECTOR.md)")
    ap.add_argument("--dhx", default=None,
                    help="DHx assignment log (default <repo>/docs/AGENT_BRIEF.md)")
    ap.add_argument("--loop", action="store_true",
                    help="persistent collect loop (what the daemon runs)")
    ap.add_argument("--once", action="store_true",
                    help="one poll then exit (heartbeat still written)")
    ap.add_argument("--standup", action="store_true",
                    help="register schtasks and/or spawn a surviving daemon")
    ap.add_argument("--status", action="store_true",
                    help="print heartbeat age; exit 0 if fresh")
    ap.add_argument("--interval", type=float, default=DEFAULT_INTERVAL_S)
    ap.add_argument("--compact-index", action="store_true",
                    help="collapse duplicate index rows (opt-in maintenance)")
    a = ap.parse_args()

    if a.status:
        rec = status_probe(a.root)
        print(json.dumps(rec, indent=1, default=str))
        age = rec.get("age_s")
        return 0 if age is not None and age < 90 else 2

    if a.compact_index:
        coll = bind(a.root, queue=a.queue, research=a.research,
                    summary_md=a.summary, interval_s=a.interval, dhx=a.dhx)
        import time as _t
        stage = Path(a.root) / "_delme" / ("compact_index_" + str(int(_t.time())))
        rec = compact_index(coll.index_path, delme_dir=stage)
        print(json.dumps(rec, indent=1, default=str))
        return 0 if rec.get("ok") else 1

    if a.standup:
        r = standup(a.root, a.interval)
        print(json.dumps(r, indent=1, default=str))
        return 0 if (r.get("proof") or {}).get("ok") else 2

    if a.once:
        coll = bind(a.root, queue=a.queue, research=a.research,
                    summary_md=a.summary, interval_s=a.interval, dhx=a.dhx)
        result = coll.poll_once()
        print(json.dumps({
            "new_this_tick": result.get("new_this_tick"),
            "index_rows": result.get("index_rows"),
            "index_file_lines": result.get("index_file_lines"),
            "scanned": result.get("scanned"),
            "by_source": result.get("by_source"),
            "elapsed_s": result.get("elapsed_s"),
            "error_count": result.get("error_count"),
            "errors": result.get("errors"),
            "tick": result.get("tick"),
            "dhx_markers": result.get("dhx_markers"),
            "dhx_matched": result.get("dhx_matched"),
            "dhx_missing": result.get("dhx_missing"),
            "dhx_snap": result.get("dhx_snap"),
            "heartbeat": str(coll.heartbeat),
            "index": str(coll.index_path),
            "summary_md": str(coll.summary_md),
            "heartbeat_rec": read_heartbeat(coll.heartbeat),
            "stage6_gate": result.get("stage6_gate"),
        }, indent=1, default=str))
        return 0 if result.get("tick") != "error" else 2

    return loop(a.root, a.interval, queue=a.queue, research=a.research,
                summary_md=a.summary, dhx=a.dhx)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CosmosPathError as e:
        print(e, file=sys.stderr)
        raise SystemExit(2)
