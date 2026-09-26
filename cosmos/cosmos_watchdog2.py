#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_watchdog2 - a 15s check that prevents a 30s idle ceiling: route scanner + assigner.

Keith: the 15-second check PREVENTS a 30-second idle ceiling — COSMOS must
never idle longer than that. A CONSTANT agent finds, flags, and ASSIGNS
route items as they surface. COSMOS self-builds from docs/WISHLIST.md.

This is a DETACHED Python daemon on a 15s loop — a 15-second check that
prevents a 30-second idle ceiling. Windows Task Scheduler's repeating floor
is 1 minute, so the 15s cadence CANNOT be a schtasks entry — the schtask
(1-min self-heal + onlogon relaunch) only restarts the daemon.

Each pass (a 15s check that prevents a 30-second idle ceiling — Keith
2026-08-25; schtasks floor is 1 min so this is a detached process):
  0. If live\\state\\control\\PAUSE.flag exists, drop NOTHING (heartbeat
     still writes state=PAUSED — a paused clock must not look dead)
     hold => never self-clears; resume_gate => auto_resume_at
  1. Scan markdown checkbox sources via ONE helper (docs/WISHLIST.md
     'Open wishes' + docs/BACKLOG.md). A wish enters MOTIF at stage 1.
  2. Scan docs/MOTIF_TRACKER.md (rows not at stage 6)
  3. Read the DHx assignment log + this install's runner_ledger.jsonl
     (and the lg/pb lane ledgers) for in-flight evidence
  4. For any open item with NO in-flight agent: DROP the right Grok/Cursor
     job via cosmos_dispatch (DHx recipe) and flag it. Wishlist lines
     already in BACKLOG / MOTIF_TRACKER / DHx / queue are not re-dropped.
  5. Append live\\logs\\WATCHDOG2.log; rewrite live\\logs\\watchdog2_heartbeat.json
     Runtime-binding: jobs[] with source=wishlist + job_file + wishlist_line.

Does NOT modify COSMOS core (kernel/ledger/sched/service). Cadence rubric:
docs/ORCHESTRATION.md (Keith's tiers, encoded 2026-08-25).

PHASE 4 seam (docs/CORE_RESTRUCTURE.md): markdown/route scanners live in
`cosmos_watchdog2_scan` and are re-exported here — same objects, not copies
— so tests/test_askmine.py (`parse_md_checkboxes`) and
tests/test_competency.py (`pick_agent`) keep working unchanged.

    py -3.14 cosmos\\cosmos_watchdog2.py --root V:\\A\\Ai\\COSMOS\\live --loop
    py -3.14 cosmos\\cosmos_watchdog2.py --root ... --once
    py -3.14 cosmos\\cosmos_watchdog2.py --root ... --standup
    py -3.14 cosmos\\cosmos_watchdog2.py --root ... --status
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone as dt_timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_paths import CosmosPaths, CosmosPathError  # noqa: E402
from cosmos_dispatch import (  # noqa: E402
    dispatch,
    measure_lanes,
)
from cosmos_inflight import Inflight, InflightError  # noqa: E402
from cosmos_motif_driver import (  # noqa: E402
    META_SLUGS,
    effective_stage,
    inflight_filenames,
    is_advancing,
    ledger_inflight,
    ledger_paths,
    motif_token,
    parse_tracker,
)
# PHASE 4 seam: scanners live in cosmos_watchdog2_scan. Re-exported here --
# and they are the SAME objects, not copies -- so every importer
# (test_askmine parse_md_checkboxes, test_competency pick_agent,
# test_watchdog2) works unchanged. Additive.
from cosmos_watchdog2_scan import (  # noqa: E402,F401
    CHECK_RE, CODING_HINTS, CURSOR_KEY_NAME, CURSOR_LOAD_OVERFLOW,
    KEITH_SECTION_HINTS, MD_ROUTE_SOURCES, NON_ALNUM, SELF_SLUGS,
    SKIP_PHRASES, STOPWORDS, TICK_END, TICK_START,
    _backlog_slug, _clip, _fold, _split_title_body, _tokens, _tracked_hit,
    annotate_backlog, annotate_checkbox, backlog_skip_reason, backlog_task,
    checkbox_skip_reason, cursor_key_exists, dhx_haystack, name_hit,
    parse_backlog, parse_md_checkboxes, pick_agent, route_drop_spec,
    update_backlog_tick, update_source_tick, wishlist_task,
)

WORKER = "cosmos-watchdog2"
TASK_NAME = "COSMOS Watchdog2"
TASK_NAME_LOGON = "COSMOS Watchdog2 Logon"
HEARTBEAT_NAME = "watchdog2_heartbeat.json"
LOCK_NAME = "watchdog2.lock"
LOG_NAME = "WATCHDOG2.log"
ASSIGNED_NAME = "assigned.json"
SCHEMA = "cosmos-watchdog2/1"
# BACKLOG 2026-08-25: a 15-second check that prevents a 30-second idle ceiling
# (schtasks floor is 1 min, so this cadence must be a detached daemon).
DEFAULT_INTERVAL_S = 15.0
MAX_DROPS_PER_PASS = 3
FRESH_S = 45.0
# CURSOR_KEY_NAME / CURSOR_LOAD_OVERFLOW / MD_ROUTE_SOURCES / checkbox
# grammar live in cosmos_watchdog2_scan (imported above and re-exported).

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200
CREATE_NO_WINDOW = 0x08000000
CREATE_BREAKAWAY_FROM_JOB = 0x01000000

SKIP_DIR_NAMES = {
    "running", "done", "failed", "logs", "staged", "elevated",
    "_lanes", "_delme", "_hold", "_superseded", "__pycache__",
    "research", "findings", "returns", ".git", ".tmp",
}


def repo_tree() -> Path:
    return Path(__file__).resolve().parent.parent


def default_runtime_root() -> Path:
    return repo_tree() / "live"


def pythonw_exe() -> str:
    exe = Path(sys.executable)
    cand = exe.with_name("pythonw.exe")
    return str(cand) if cand.exists() else str(exe)


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat()


def _lane_dir(queue: Path, lane: str) -> Path:
    if lane == "root":
        return Path(queue)
    return Path(queue) / "_lanes" / lane


# ---------------------------------------------------------------------------
# Windows survival (same pattern as cosmos_run / cosmos_collector)
# ---------------------------------------------------------------------------

def plan_loop_argv(root: str, python: str | None = None,
                   extra: list[str] | None = None) -> list[str]:
    argv = [python or pythonw_exe(), str(Path(__file__).resolve()),
            "--root", str(Path(root).resolve()), "--loop"]
    if extra:
        argv.extend(extra)
    return argv


def plan_task_argv(root: str) -> list[str]:
    """1-min self-heal. The daemon runs a 15s check that prevents a 30s idle
    ceiling; this only relaunches it."""
    tr = subprocess.list2cmdline([
        pythonw_exe(), str(Path(__file__).resolve()),
        "--root", str(Path(root).resolve()), "--loop",
    ])
    return ["schtasks", "/create", "/tn", TASK_NAME, "/tr", tr,
            "/sc", "minute", "/mo", "1", "/f"]


def plan_logon_argv(root: str) -> list[str]:
    tr = subprocess.list2cmdline([
        pythonw_exe(), str(Path(__file__).resolve()),
        "--root", str(Path(root).resolve()), "--loop",
    ])
    return ["schtasks", "/create", "/tn", TASK_NAME_LOGON, "/tr", tr,
            "/sc", "onlogon", "/f"]


def _run_schtasks(argv: list[str]) -> dict:
    try:
        p = subprocess.run(argv, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=60,
                           creationflags=(CREATE_NO_WINDOW if os.name == "nt" else 0))
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
    rec = {
        "argv": argv, "rc": p.returncode, "ok": p.returncode == 0, "out": out,
        "needs_elevation": denied,
        "keith_cmd": subprocess.list2cmdline(argv) if p.returncode != 0 else None,
    }
    return rec


def query_task(name: str) -> dict:
    argv = ["schtasks", "/query", "/tn", name, "/fo", "LIST", "/v"]
    try:
        p = subprocess.run(argv, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=30)
    except OSError as e:
        return {"ok": False, "rc": -1, "out": str(e), "argv": argv, "name": name}
    out = ((p.stdout or "") + (p.stderr or "")).strip()
    return {"ok": p.returncode == 0, "rc": p.returncode, "out": out,
            "argv": argv, "name": name}


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
    wmi = spawn_wmi(root)
    if wmi.get("ok"):
        return wmi
    pop = spawn_popen_detached(root, log_path)
    pop["wmi_failed"] = wmi
    return pop


def wait_fresh(hb_path: Path, timeout_s: float = 20.0,
               max_age_s: float = FRESH_S, min_epoch: float = 0,
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


# ---------------------------------------------------------------------------
# bind / log / heartbeat / assigned memory
# ---------------------------------------------------------------------------

class Watchdog2:
    def __init__(self, root: str, queue=None, interval_s: float = DEFAULT_INTERVAL_S):
        self.paths = CosmosPaths(root)
        logs = self.paths.logs()
        logs.mkdir(parents=True, exist_ok=True)
        state = self.paths.role("state")
        wd = state / "watchdog2"
        wd.mkdir(parents=True, exist_ok=True)
        self.heartbeat = logs / HEARTBEAT_NAME
        self.lock_path = logs / LOCK_NAME
        self.log_path = logs / LOG_NAME
        self.assigned_path = wd / ASSIGNED_NAME
        # COSMOS-own queue (resolver role). BTS V:\Ai\_queue is not identity.
        self.queue = (Path(queue) if queue is not None
                      else self.paths.role("queue"))
        self.repo = repo_tree()
        self.sources = {}
        for spec in MD_ROUTE_SOURCES:
            if spec.get("loc") == "state":
                sub = spec.get("subdir") or spec["name"]
                self.sources[spec["name"]] = (
                    self.paths.state(sub) / spec["filename"])
            else:
                self.sources[spec["name"]] = (
                    self.repo / "docs" / spec["filename"])
        self.backlog = self.sources["backlog"]
        self.wishlist = self.sources["wishlist"]
        self.askmine = self.sources["askmine"]
        self.tracker = self.repo / "docs" / "MOTIF_TRACKER.md"
        self.dhx = self.repo / "docs" / "AGENT_BRIEF.md"
        self.runtime_root = Path(root)
        self.interval_s = float(interval_s)
        self.polls = 0
        self.instance_id = os.getpid()
        self.pause_path = self.paths.role("state") / "control" / "PAUSE.flag"
        self._pause_logged = False

    def pause_flag(self) -> dict | None:
        """Presence of live/state/control/PAUSE.flag is the whole signal."""
        p = self.pause_path
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

    def maybe_auto_resume(self, paused: dict, stamp: str) -> bool:
        """Resume gate (Keith 2026-08-25, permanent, all streams).

        A mode='resume_gate' flag self-clears at its auto_resume_at time — the
        auto-resession default: no affirmative selection at BootUP => the route
        resumes on this 15s clock with no human turn. A mode='hold' flag (TidyUP
        or a deliberate stop) NEVER self-clears. Returns True iff the flag was
        cleared this pass and the route may resume. Fails toward STAYING PAUSED
        on any bad/missing timestamp — a visible pause beats a wrong resume.
        """
        mode = str(paused.get("mode") or "hold").lower()
        if mode != "resume_gate":
            return False
        ara = paused.get("auto_resume_at")
        if not ara:
            return False
        try:
            due = datetime.fromisoformat(str(ara).replace("Z", "+00:00"))
        except ValueError:
            self.log("resume-gate: unparseable auto_resume_at=%r — staying PAUSED"
                     % (ara,))
            return False
        if due.tzinfo is None:
            due = due.astimezone()
        if datetime.now().astimezone() < due:
            return False
        try:
            self.pause_path.unlink()
        except FileNotFoundError:
            pass
        except OSError as e:
            self.log("resume-gate: could not remove PAUSE.flag: %r" % (e,))
            return False
        self.log("AUTO-RESUME (resume_gate) %s — auto_resume_at=%s reached" % (
            stamp, ara))
        self._pause_logged = False
        return True

    def log(self, msg: str) -> None:
        line = "[%s] %s" % (
            datetime.now().astimezone().isoformat(timespec="seconds"), msg)
        print(line, flush=True)
        try:
            with open(self.log_path, "a", encoding="utf-8") as fh:
                fh.write(line + "\n")
        except OSError:
            pass

    def write_heartbeat(self, extra: dict | None = None) -> dict:
        now = datetime.now().astimezone()
        rec = {
            "schema": SCHEMA,
            "last_run": now.isoformat(timespec="seconds"),
            "last_run_epoch": int(now.timestamp()),
            "last_run_utc": now.astimezone(dt_timezone.utc).isoformat(
                timespec="seconds"),
            "worker": WORKER,
            "pid": os.getpid(),
            "polls": self.polls,
            "interval_s": self.interval_s,
            "queue": str(self.queue),
            "log": str(self.log_path),
            "_readme": (
                "Written on EVERY tick, pass or idle. COMPARE USING "
                "last_run_epoch. If last_run_epoch is older than ~90s "
                "Watchdog2 failed (never-idle-15s is broken)."
            ),
        }
        if extra:
            rec.update(extra)
        tmp = self.heartbeat.with_name(self.heartbeat.name + ".tmp")
        tmp.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
        tmp.replace(self.heartbeat)
        return rec

    def load_assigned(self) -> dict:
        if not self.assigned_path.exists():
            return {}
        try:
            obj = json.loads(self.assigned_path.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            return {}
        return obj if isinstance(obj, dict) else {}

    def save_assigned(self, obj: dict) -> None:
        tmp = self.assigned_path.with_name(self.assigned_path.name + ".tmp")
        tmp.write_text(json.dumps(obj, indent=1, default=str), encoding="utf-8")
        tmp.replace(self.assigned_path)


# ---------------------------------------------------------------------------
# scanners -- moved to cosmos_watchdog2_scan (PHASE 4). Re-exported above.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# one pass
# ---------------------------------------------------------------------------

def _close_idle_sessions(wd: Watchdog2) -> int:
    """30 minutes idle closes WOMBAT, Judge, and the final checker.

    ORC and CCr stay. This is not a new drop, so a hold still runs it.
    """
    try:
        from cosmos_duds import sweep_idle
        return len(sweep_idle(wd.paths))
    except Exception as e:  # noqa: BLE001
        wd.log("sweep_idle: %s" % (e,))
        return 0


def scan_once(wd: Watchdog2, *, dry_run: bool = False) -> dict:
    t0 = time.time()
    stamp = _iso_now()
    idle_closed = _close_idle_sessions(wd)
    paused = wd.pause_flag()
    if paused is not None and str(paused.get("state", "PAUSED")).upper() != "RUNNING":
        # RESUME GATE: a mode='resume_gate' flag self-clears at auto_resume_at
        # (the auto-resession default); a mode='hold' flag waits until removed.
        if wd.maybe_auto_resume(paused, stamp):
            paused = None
    if paused is not None and str(paused.get("state", "PAUSED")).upper() != "RUNNING":
        wd.polls += 1
        extra = {
            "tick": "paused",
            "state": "PAUSED",
            "stamp": stamp,
            "mode": str(paused.get("mode") or "hold"),
            "auto_resume_at": paused.get("auto_resume_at"),
            "pause": {
                "reason": paused.get("reason"),
                "set_by": paused.get("set_by"),
                "set_at": paused.get("set_at"),
                "path": paused.get("path"),
            },
            "assigned_this_pass": 0,
            "idle_closed": idle_closed,
            "open_flagged": 0,
            "skipped": 0,
            "elapsed_s": round(time.time() - t0, 3),
            "jobs": [],
        }
        hb = wd.write_heartbeat(extra=extra)
        if not wd._pause_logged:
            wd.log("PAUSED  mode=%s reason=%s set_by=%s auto_resume_at=%s" % (
                paused.get("mode") or "hold", paused.get("reason"),
                paused.get("set_by"), paused.get("auto_resume_at")))
            wd._pause_logged = True
        extra["heartbeat"] = hb
        extra["assigned"] = []
        extra["ok"] = True
        extra["dry_run"] = dry_run
        extra["log"] = str(wd.log_path)
        extra["heartbeat_path"] = str(wd.heartbeat)
        return extra
    if wd._pause_logged:
        wd.log("RESUMED")
        wd._pause_logged = False
    wd.write_heartbeat(extra={"tick": "scan", "idle_closed": idle_closed})

    tracker_text = wd.tracker.read_text(encoding="utf-8") if wd.tracker.exists() else ""
    dhx_text = wd.dhx.read_text(encoding="utf-8") if wd.dhx.exists() else ""
    orch = wd.repo / "docs" / "ORCHESTRATION.md"
    orch_text = orch.read_text(encoding="utf-8") if orch.exists() else ""
    md_texts: dict[str, str] = {}
    for spec in MD_ROUTE_SOURCES:
        path = getattr(wd, spec["name"])
        md_texts[spec["name"]] = (
            path.read_text(encoding="utf-8") if path.exists() else "")

    # Queue filenames cannot decide a skip — inflight leases + ledger are
    # the authority (work order 2.3). Scraped as an advisory count.
    file_names = inflight_filenames(wd.queue)
    names = ledger_inflight(ledger_paths(wd.queue))
    dhx_fold = dhx_haystack(dhx_text)  # advisory; cannot decide a skip
    lease_unreadable = False
    try:
        names |= Inflight(wd.runtime_root / "state" / "inflight.jsonl").tokens()
    except InflightError:
        lease_unreadable = True
    assigned_mem = wd.load_assigned()
    loads = measure_lanes(wd.queue)
    key_ok = cursor_key_exists(wd.runtime_root)

    flagged: list[dict] = []
    skipped: list[dict] = []
    dropped: list[dict] = []

    # --- MOTIF incomplete rows (same drop recipe as motif_driver, idempotent)
    rows = parse_tracker(tracker_text)
    for row in rows:
        slug = row["slug"]
        if slug in META_SLUGS:
            skipped.append({"source": "motif", "slug": slug, "reason": "meta"})
            continue
        if lease_unreadable:
            skipped.append({"source": "motif", "slug": slug,
                            "reason": "lease_unreadable"})
            continue
        cur, nxt = effective_stage(row, wd.repo)
        if cur >= 6:
            skipped.append({"source": "motif", "slug": slug, "reason": "stage6"})
            continue
        hit = is_advancing(slug, nxt, names)
        if hit:
            skipped.append({"source": "motif", "slug": slug,
                            "reason": "inflight", "hit": hit})
            continue
        rec = {
            "source": "motif", "slug": slug, "name": row["name"],
            "current_stage": cur, "next_stage": nxt,
            "token": motif_token(slug, nxt),
            "title": row["name"],
        }
        flagged.append(rec)

    # --- Markdown checkbox sources (WISHLIST + BACKLOG) — one helper
    parsed_md: dict[str, list[dict]] = {}
    tracked_names: set[str] = set()
    for row in rows:
        tracked_names.add(row["slug"])
        tracked_names.add(row["name"])
    for spec in MD_ROUTE_SOURCES:
        items = parse_md_checkboxes(
            md_texts.get(spec["name"], ""), spec["name"],
            section=spec["section"])
        parsed_md[spec["name"]] = items
        if spec["enter"] != "motif_s1":
            for it in items:
                tracked_names.add(it["slug"])
                tracked_names.add(it["title"])

    for spec in MD_ROUTE_SOURCES:
        extra_tracked = tracked_names if spec["enter"] == "motif_s1" else None
        for item in parsed_md[spec["name"]]:
            reason = checkbox_skip_reason(
                item, names, dhx_fold, assigned_mem, orch_text,
                tracked_names=extra_tracked)
            if not reason and spec["enter"] == "motif_s1":
                hit = is_advancing(item["slug"], 1, names)
                if hit:
                    reason = f"inflight:{hit[:80]}"
            if reason:
                skipped.append({"source": spec["name"], "slug": item["slug"],
                                "title": item["title"], "reason": reason})
                continue
            rec = {
                "source": spec["name"], "slug": item["slug"],
                "title": item["title"], "body": item["body"], "item": item,
                "enter": spec["enter"],
            }
            if spec["enter"] == "motif_s1":
                rec["next_stage"] = 1
                rec["token"] = motif_token(item["slug"], 1)
            flagged.append(rec)

    # Drop up to MAX_DROPS_PER_PASS. Motif first (mechanical next-stage),
    # then MD_ROUTE_SOURCES order (wishlist, then leftover backlog).
    remaining = [f for f in flagged]
    for rec in remaining:
        if len(dropped) >= MAX_DROPS_PER_PASS:
            rec["reason"] = "cap"
            continue
        if dry_run:
            rec["dry_run"] = True
            dropped.append(rec)
            continue
        try:
            task, agent, kind = route_drop_spec(rec, rows, loads, key_ok)
            out = dispatch(
                agent, task, str(wd.repo), kind=kind,
                queue=wd.queue, runtime_root=wd.runtime_root, dhx=wd.dhx,
            )
        except Exception as e:  # noqa: BLE001
            rec["ok"] = False
            rec["error"] = f"{type(e).__name__}: {e}"
            rec["reason"] = "dispatch_error"
            skipped.append(rec)
            wd.log("DISPATCH FAIL %s %s: %r" % (
                rec.get("source"), rec.get("slug"), e))
            continue
        rec.update({
            "ok": bool(out.get("ok")),
            "created": out.get("created"),
            "idempotent": out.get("idempotent"),
            "lane": out.get("lane"),
            "job_file": out.get("job_file"),
            "job_path": out.get("job_path"),
            "agent": out.get("agent"),
            "kind": out.get("kind"),
            "marker": out.get("marker"),
            "stamp": out.get("stamp"),
        })
        dropped.append(rec)
        wd.log("ASSIGN  %s/%s  %s -> %s/%s" % (
            rec.get("source"), rec.get("slug"), rec.get("agent"),
            rec.get("lane"), rec.get("job_file")))
        if rec.get("job_file"):
            names.add(str(rec["job_file"]).lower())
        if rec.get("token"):
            names.add(str(rec["token"]).lower())
        if rec["source"] in ("backlog", "wishlist"):
            assigned_mem[rec["slug"]] = {
                "stamp": rec.get("stamp") or stamp,
                "job_file": rec.get("job_file"),
                "lane": rec.get("lane"),
                "agent": rec.get("agent"),
                "kind": rec.get("kind"),
                "source": rec["source"],
                "token": rec.get("token"),
            }
            try:
                annotate_checkbox(getattr(wd, rec["source"]), rec["item"],
                                 rec, stamp)
            except OSError as e:
                wd.log("WARN annotate %s: %r" % (rec["source"], e))

    if not dry_run:
        wd.save_assigned(assigned_mem)
        for src in (spec["name"] for spec in MD_ROUTE_SOURCES):
            try:
                update_source_tick(getattr(wd, src), stamp, dropped,
                                   flagged, skipped)
            except OSError as e:
                wd.log("WARN %s tick: %r" % (src, e))

    wd.polls += 1
    elapsed = round(time.time() - t0, 3)
    extra = {
        "tick": "idle" if not dropped else "assigned",
        "stamp": stamp,
        "open_flagged": len(flagged),
        "assigned_this_pass": len(dropped),
        "skipped": len(skipped),
        "elapsed_s": elapsed,
        "lane_loads": {k: {"queued": v["queued"], "running": v["running"],
                           "load": v["load"]} for k, v in loads.items()},
        "md_sources": [s["name"] for s in MD_ROUTE_SOURCES],
        "soft_filenames": len(file_names),
        "soft_dhx_chars": len(dhx_fold),
        "leases_unreadable": lease_unreadable,
        "jobs": [
            {"source": d.get("source"), "slug": d.get("slug"),
             "agent": d.get("agent"), "kind": d.get("kind"),
             "lane": d.get("lane"), "job_file": d.get("job_file"),
             "created": d.get("created"),
             "token": d.get("token"),
             "enter": d.get("enter"),
             "wishlist_line": ((d.get("item") or {}).get("line")
                               if d.get("source") == "wishlist" else None)}
            for d in dropped
        ],
        "flagged": [
            {"source": f.get("source"), "slug": f.get("slug"),
             "title": f.get("title") or f.get("name")}
            for f in flagged[:30]
        ],
        "skipped_sample": [
            {"source": s.get("source"), "slug": s.get("slug"),
             "reason": s.get("reason")}
            for s in skipped[:24]
        ],
    }
    hb = wd.write_heartbeat(extra=extra)
    wd.log("cycle polls=%d flagged=%d assigned=%d skipped=%d elapsed=%ss" % (
        wd.polls, len(flagged), len(dropped), len(skipped), elapsed))
    extra["heartbeat"] = hb
    extra["assigned"] = dropped
    extra["skipped_full"] = skipped
    extra["ok"] = True
    extra["dry_run"] = dry_run
    extra["log"] = str(wd.log_path)
    extra["heartbeat_path"] = str(wd.heartbeat)
    return extra


def loop(root: str, interval_s: float, queue=None) -> int:
    wd = Watchdog2(root, queue=queue, interval_s=interval_s)
    out_path = wd.paths.logs("watchdog2.out")
    err_path = wd.paths.logs("watchdog2.err")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    log_fh = open(out_path, "a", encoding="utf-8", buffering=1)
    sys.stdout = log_fh
    sys.stderr = log_fh
    fd = acquire_lock(wd.lock_path)
    if fd is None:
        rec = read_heartbeat(wd.heartbeat)
        age = heartbeat_age_s(rec)
        pid = (rec or {}).get("pid")
        if age is not None and age < FRESH_S and _pid_alive(int(pid or 0)):
            print(json.dumps({"already_running": True, "pid": pid,
                              "age_s": round(age, 3),
                              "heartbeat": str(wd.heartbeat)}, indent=1),
                  flush=True)
            return 0
        print("watchdog2 lock held and heartbeat not fresh - refusing second loop",
              flush=True)
        return 2
    print(json.dumps({"loop": True, "pid": os.getpid(),
                      "queue": str(wd.queue),
                      "heartbeat": str(wd.heartbeat),
                      "log": str(wd.log_path),
                      "interval_s": interval_s}, indent=1), flush=True)
    wd.log("watchdog2 UP. interval=%.0fs. pid=%d" % (interval_s, os.getpid()))
    try:
        while True:
            try:
                scan_once(wd)
            except Exception:
                import traceback
                tb = traceback.format_exc()
                try:
                    err_path.write_text(tb, encoding="utf-8")
                except OSError:
                    pass
                wd.log("CYCLE ERROR:\n" + tb)
                try:
                    wd.write_heartbeat(extra={"tick": "error", "error": tb[-500:]})
                except OSError:
                    pass
            time.sleep(interval_s)
    finally:
        os.close(fd)
    return 0


def install_minute_task(root: str) -> dict:
    rec = _run_schtasks(plan_task_argv(root))
    rec["note"] = ("registered: 1-min self-heal of the 15s daemon"
                   if rec.get("ok") else "FAILED - schtasks returned nonzero")
    if rec.get("ok"):
        r = subprocess.run(["schtasks", "/run", "/tn", TASK_NAME],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=30,
                           creationflags=(CREATE_NO_WINDOW if os.name == "nt" else 0))
        rec["run_rc"] = r.returncode
        rec["run_out"] = ((r.stdout or "") + (r.stderr or "")).strip()
        rec["run_ok"] = r.returncode == 0
        q = query_task(TASK_NAME)
        rec["query_ok"] = q.get("ok")
        rec["query_out"] = (q.get("out") or "")[:1200]
    return rec


def install_logon_task(root: str) -> dict:
    rec = _run_schtasks(plan_logon_argv(root))
    rec["note"] = ("registered: onlogon relaunch"
                   if rec.get("ok") else
                   "FAILED - onlogon typically needs elevation")
    if rec.get("ok"):
        q = query_task(TASK_NAME_LOGON)
        rec["query_ok"] = q.get("ok")
        rec["query_out"] = (q.get("out") or "")[:800]
    return rec


def standup(root: str, interval_s: float) -> dict:
    """Make the daemon live past this job. Proof = fresh heartbeat + live pid."""
    wd = Watchdog2(root, interval_s=interval_s)
    hb = wd.heartbeat
    t0 = time.time()
    proof = wait_fresh(hb, timeout_s=1.5)
    if proof["ok"]:
        return {"started": "already", "proof": proof,
                "heartbeat_path": str(hb),
                "log": str(wd.log_path),
                "keith_cmd": None}

    minute = install_minute_task(root)
    logon = install_logon_task(root)
    launched_via = None
    detach = None
    if minute.get("ok") and minute.get("run_ok"):
        launched_via = "schtasks"
        proof = wait_fresh(hb, timeout_s=20.0, min_epoch=t0, max_age_s=FRESH_S)
    if not proof.get("ok"):
        detach = spawn_detached(root, wd.paths.logs("watchdog2.out"))
        launched_via = detach.get("method") or "detached_process"
        expect = detach.get("pid") if isinstance(detach.get("pid"), int) else None
        proof = wait_fresh(hb, timeout_s=25.0, min_epoch=t0, max_age_s=FRESH_S,
                           expect_pid=expect)

    keith_cmds = []
    if minute.get("needs_elevation") or not minute.get("ok"):
        if minute.get("keith_cmd"):
            keith_cmds.append(minute["keith_cmd"])
    if logon.get("needs_elevation") or not logon.get("ok"):
        if logon.get("keith_cmd"):
            keith_cmds.append(logon["keith_cmd"])

    return {
        "started": launched_via,
        "task_minute": minute,
        "task_logon": logon,
        "detach": detach,
        "proof": proof,
        "heartbeat_path": str(hb),
        "log": str(wd.log_path),
        "keith_cmd": " & ".join(keith_cmds) if keith_cmds else None,
        "keith_cmds": keith_cmds,
    }


def bind(root: str, queue=None, interval_s: float = DEFAULT_INTERVAL_S) -> Watchdog2:
    return Watchdog2(root, queue=queue, interval_s=interval_s)


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_watchdog2")
    ap.add_argument("--root", required=True,
                    help="COSMOS runtime root (sentinel-verified)")
    ap.add_argument("--queue", default=None,
                    help="runner queue (default: this install's queue role)")
    ap.add_argument("--loop", action="store_true",
                    help="persistent 15s assigner (what the daemon runs)")
    ap.add_argument("--once", action="store_true",
                    help="one scan then exit (heartbeat still written)")
    ap.add_argument("--standup", action="store_true",
                    help="register schtasks and/or spawn a surviving daemon")
    ap.add_argument("--status", action="store_true",
                    help="print heartbeat age; exit 0 if fresh")
    ap.add_argument("--dry-run", action="store_true",
                    help="scan + decide; do not drop jobs")
    ap.add_argument("--interval", type=float, default=DEFAULT_INTERVAL_S)
    a = ap.parse_args()

    if a.status:
        wd = bind(a.root, queue=a.queue, interval_s=a.interval)
        rec = read_heartbeat(wd.heartbeat)
        age = heartbeat_age_s(rec)
        print(json.dumps({"path": str(wd.heartbeat), "age_s": age,
                          "heartbeat": rec, "log": str(wd.log_path)},
                         indent=1, default=str))
        return 0 if age is not None and age < FRESH_S else 2

    if a.standup:
        r = standup(a.root, a.interval)
        print(json.dumps(r, indent=1, default=str))
        return 0 if (r.get("proof") or {}).get("ok") else 2

    if a.once or a.dry_run:
        wd = bind(a.root, queue=a.queue, interval_s=a.interval)
        result = scan_once(wd, dry_run=a.dry_run)
        print(json.dumps({
            "ok": result.get("ok"),
            "stamp": result.get("stamp"),
            "assigned_this_pass": result.get("assigned_this_pass"),
            "open_flagged": result.get("open_flagged"),
            "skipped": result.get("skipped"),
            "jobs": result.get("jobs"),
            "flagged": result.get("flagged"),
            "skipped_sample": result.get("skipped_sample"),
            "elapsed_s": result.get("elapsed_s"),
            "heartbeat_path": result.get("heartbeat_path"),
            "log": result.get("log"),
            "dry_run": result.get("dry_run"),
        }, indent=1, default=str))
        return 0

    return loop(a.root, a.interval, queue=a.queue)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CosmosPathError as e:
        print(e, file=sys.stderr)
        raise SystemExit(2)
