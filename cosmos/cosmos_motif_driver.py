#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_motif_driver - mechanical Motif clock (no AI / no Cowork reasoning).

Reads docs/MOTIF_TRACKER.md + docs/COLLECTOR.md + the BTS runner_ledger.jsonl
(+ queued/running lane files). For each deliverable not at stage 6 and not
already advancing, DROPS the next-stage Grok Build job into a runner lane via
cosmos_dispatch (stage-5 critique / stage-6 build+gate, or the tracker's named
next stage). Dispatch auto-stamps DHx from datetime.now(). This module then
updates MOTIF_TRACKER.md and writes a heartbeat.

Windows clock (survives reboot; not the Claude scheduler):

    schtasks /create /tn "COSMOS Motif Driver" /sc minute /mo 15 ...

    py -3.14 cosmos\\cosmos_motif_driver.py --once
    py -3.14 cosmos\\cosmos_motif_driver.py --standup

Does not modify COSMOS core (kernel/ledger/sched/service).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone as dt_timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_dispatch import (  # noqa: E402
    LANE_ORDER,
    dispatch,
)
from cosmos_clock import pythonw_exe, tr_cmdline  # noqa: E402
from cosmos_inflight import Inflight  # noqa: E402

WORKER = "cosmos-motif-driver"
TASK_NAME = "COSMOS Motif Driver"
HEARTBEAT_NAME = "motif_driver_heartbeat.json"
SCHEMA = "cosmos-motif-driver/1"
AGENT = "G46"
CREATE_NO_WINDOW = 0x08000000  # windowless short-lived schtasks spawns

STAGE_RE = re.compile(r"(\d+)")
CELL_STRIP = re.compile(r"[*`]+")
NON_ALNUM = re.compile(r"[^a-z0-9]+")
TICK_START = "<!-- motif-driver-tick -->"
TICK_END = "<!-- /motif-driver-tick -->"

# Filename prefixes that mean these four apps are already moving through 5/6.
STAGE_BUNDLES = (
    ("cosmos_stage5_critiques", 5, frozenset({"cdeck", "cvm", "cdm", "gbridge"})),
    ("cosmos_stage6_improve", 6, frozenset({"cdeck", "cvm", "cdm", "gbridge"})),
)

# Longest folded key wins. Meta rows are skipped.
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
    ("gbridge", "gbridge"),
    ("cdeck", "cdeck"),
    ("cvm", "cvm"),
    ("cdm", "cdm"),
)

META_SLUGS = frozenset({"runtimeall"})

SKIP_DIR_NAMES = {
    "running", "done", "failed", "logs", "staged", "elevated",
    "_lanes", "_delme", "_hold", "_superseded", "__pycache__",
    "research", "findings", "returns", ".git", ".tmp",
}


def repo_tree() -> Path:
    return Path(__file__).resolve().parent.parent


def default_runtime_root() -> Path:
    return repo_tree() / "live"


def default_tracker() -> Path:
    return repo_tree() / "docs" / "MOTIF_TRACKER.md"


def default_collector_md() -> Path:
    return repo_tree() / "docs" / "COLLECTOR.md"


def default_dhx() -> Path:
    return repo_tree() / "docs" / "AGENT_BRIEF.md"


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat()


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


def _lane_dir(queue: Path, lane: str) -> Path:
    if lane == "root":
        return Path(queue)
    return Path(queue) / "_lanes" / lane


def plan_task_argv(root: str | None = None) -> list[str]:
    """schtasks /create plan. Current-user, no /rl highest. hush.py so
    pythonw does not flash a console (Task Scheduler Interactive scar)."""
    live = root or str(Path(__file__).resolve().parent.parent / "live")
    tr = tr_cmdline(Path(__file__).resolve(), live, "--once")
    return ["schtasks", "/create", "/tn", TASK_NAME, "/tr", tr,
            "/sc", "minute", "/mo", "15", "/f"]


def query_task(name: str = TASK_NAME) -> dict:
    argv = ["schtasks", "/query", "/tn", name, "/fo", "LIST", "/v"]
    try:
        p = subprocess.run(argv, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=30)
    except OSError as e:
        return {"ok": False, "rc": -1, "out": str(e), "argv": argv}
    out = ((p.stdout or "") + (p.stderr or "")).strip()
    return {"ok": p.returncode == 0, "rc": p.returncode, "out": out, "argv": argv}


def install_task() -> dict:
    argv = plan_task_argv()
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
        "note": ("registered: every 15 minutes" if p.returncode == 0 else
                 "FAILED - schtasks returned nonzero"),
    }
    if p.returncode == 0:
        r = subprocess.run(["schtasks", "/query", "/tn", TASK_NAME, "/fo", "LIST"],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=30,
                           creationflags=(CREATE_NO_WINDOW if os.name == "nt" else 0))
        rec["query_rc"] = r.returncode
        rec["query_out"] = ((r.stdout or "") + (r.stderr or "")).strip()
    return rec


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
        artifact = cells[2]
        next_stage = cells[3]
        rows.append({
            "name": name,
            "slug": canonical_slug(name),
            "current": current,
            "artifact": artifact,
            "next_stage": next_stage,
            "line": line,
        })
    return rows


def critique_exists(repo: Path, slug: str, name: str) -> bool:
    d = repo / "docs" / "critique"
    if not d.is_dir():
        return False
    keys = {_fold(slug), _fold(name)}
    keys.discard("")
    for p in d.iterdir():
        if not p.is_file():
            continue
        folded = _fold(p.stem)
        if any(k and k in folded for k in keys):
            return True
    return False


def effective_stage(row: dict, repo: Path) -> tuple[int, int]:
    """(current_stage, next_stage). Next defaults to current+1, capped at 6.

    Stage is the tracker row. A critique filename cannot lift current_stage —
    filenames are not a primitive (work order 2.3). critique_exists stays
    callable as an advisory count.
    """
    cur = _first_int(row.get("current") or "") or 0
    nxt = _first_int(row.get("next_stage") or "")
    if nxt is None:
        nxt = min(cur + 1, 6) if cur < 6 else 6
    if cur >= 5 and nxt <= 5:
        nxt = 6
    if nxt < 1:
        nxt = 1
    if nxt > 6:
        nxt = 6
    return cur, nxt


def motif_token(slug: str, stage: int) -> str:
    return f"motif_{slug}_s{int(stage)}"


# A finished job leaves its receipt beside the pending ones. A receipt is proof of
# COMPLETION, so counting it as inflight inverts its meaning and blocks the slug
# forever. Scar 2026-08-30: cdeck and gbridge were skipped by their own stage-6
# result files, and every later success would have wedged its own slug the same way.
RECEIPT_SUFFIXES = ("_result.json", "_result.json.stdout.txt")

# Manifests are historical dispatch records and are never pruned, so the set only
# grows. Honour them just long enough to cover the gap between a dispatch writing
# its manifest and its lane file appearing, then let them age out.
MANIFEST_WINDOW_S = 1800.0


def is_receipt(name: str) -> bool:
    """True when a filename is a completion receipt rather than an inflight job."""
    n = name.lower()
    return any(n.endswith(sfx) for sfx in RECEIPT_SUFFIXES)


def inflight_filenames(queue: Path, now: float | None = None) -> set[str]:
    """Lowercased names of queued + running jobs across root/lg/pb.

    Receipts are excluded and manifests are age-windowed, so a completed job can
    never permanently block its own slug.
    """
    names: set[str] = set()
    q = Path(queue)
    cutoff = (time.time() if now is None else now) - MANIFEST_WINDOW_S
    for lane in LANE_ORDER:
        base = _lane_dir(q, lane)
        if not base.exists():
            continue
        for p in base.iterdir():
            if p.name in SKIP_DIR_NAMES or p.name.startswith("."):
                continue
            if p.is_file() and not is_receipt(p.name):
                names.add(p.name.lower())
        running = base / "running"
        if running.is_dir():
            for p in running.iterdir():
                if (p.is_file() and not p.name.startswith(".")
                        and not is_receipt(p.name)):
                    names.add(p.name.lower())
    man = q / "manifests"
    if man.is_dir():
        try:
            for p in man.iterdir():
                if not (p.is_file() and p.suffix.lower() == ".json"):
                    continue
                try:
                    if p.stat().st_mtime < cutoff:
                        continue
                except OSError:
                    continue
                names.add(p.name.lower())
                names.add(p.stem.lower())
        except OSError:
            pass
    return names


def ledger_inflight(paths: list[Path], max_bytes: int = 512_000) -> set[str]:
    """Jobs with a start and no later end in the tail of each ledger."""
    live: set[str] = set()
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        try:
            data = path.read_bytes()
        except OSError:
            continue
        if len(data) > max_bytes:
            data = data[-max_bytes:]
        text = data.decode("utf-8", "replace")
        started: dict[str, None] = {}
        ended: set[str] = set()
        for ln in text.splitlines():
            ln = ln.strip()
            if not ln:
                continue
            try:
                row = json.loads(ln)
            except ValueError:
                continue
            if not isinstance(row, dict):
                continue
            job = str(row.get("job") or "").strip()
            payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
            if not job:
                job = str(payload.get("job_id") or "").strip()
            if not job:
                continue
            ev = row.get("event")
            key = job.lower()
            if ev in ("start", "JOB_CLAIMED", "JOB_SUBMITTED"):
                started[key] = None
                ended.discard(key)
            elif ev in ("end", "JOB_DONE", "JOB_STALE"):
                ended.add(key)
        live.update(k for k in started if k not in ended)
    return live


def ledger_paths(queue: Path) -> list[Path]:
    q = Path(queue)
    out = [q / "runner_ledger.jsonl", q / "sched_ledger.jsonl"]
    for lane in ("lg", "pb"):
        out.append(q / "_lanes" / lane / "runner_ledger.jsonl")
    return out


def _haystack(names: set[str]) -> str:
    return " ".join(sorted(names))


_MOTIF_STAGE_RE = re.compile(r"motif_([a-z0-9]+)_s(\d+)")


TRACKER_JSON_NAME = "motif_tracker.json"
TRACKER_JSON_SCHEMA = "cosmos-motif-tracker/1"


def write_tracker_json(runtime_root: Path, rows: list[dict], tracker_path: Path,
                       stamp: str, stage_map: dict | None = None) -> dict:
    """Publish the tracker's MACHINE state as JSON beside the markdown.

    PHASE 2, step one (docs/CORE_RESTRUCTURE.md). `MOTIF_TRACKER.md` is currently
    both a human document and a database: COW writes prose disposition blocks into
    it while the driver regex-parses stage rows out of it. A file that is both
    narrative and state will drift, and on 2026-08-26 that class of coupling --
    machine state read out of prose -- cost three days of silence.

    This step is deliberately ADDITIVE and changes no behaviour: the markdown is
    still the source, and this is a projection of what the parser actually saw.
    It buys three things immediately:

      * consumers (collector, index, cdeck) can read structured stage state
        instead of re-implementing the markdown parse;
      * `drift` below makes a disagreement between successive parses VISIBLE
        rather than silent;
      * when the source is eventually flipped (JSON authoritative, markdown
        rendered), the flip is verifiable because both have been agreeing for
        weeks.

    Returns the record written, including any drift against the previous tick.
    """
    dest = Path(runtime_root) / "state" / TRACKER_JSON_NAME
    prev_stages: dict = {}
    try:
        prev = json.loads(dest.read_text(encoding="utf-8"))
        prev_stages = {r["slug"]: r.get("current_stage")
                       for r in (prev.get("rows") or []) if r.get("slug")}
    except (OSError, ValueError, KeyError, TypeError):
        prev_stages = {}

    out_rows = []
    for r in rows:
        slug = r.get("slug")
        if not slug:
            continue
        # Stage must be the COMPUTED integer, not the markdown cell. The cell
        # is prose -- "5 critique: different-family review ... - DISPATCHED
        # motif_cdeck_s6 2026-08-25T23:27" -- which is exactly why stage state
        # cannot live in a document. effective_stage() reads the tracker row
        # (a critique filename cannot lift).
        cur, nxt = (stage_map or {}).get(slug, (None, None))
        out_rows.append({
            "slug": slug,
            "name": r.get("name"),
            "current_stage": cur,
            "next_stage": nxt,
            "artifact": r.get("artifact"),
            # parse_tracker names this cell `next_stage`; `next` is the older
            # fixture spelling. Reading only `next` silently dropped the
            # provenance on every real tick -- and provenance is what makes a
            # divergence diagnosable rather than merely visible.
            "raw_next_cell": r.get("next_stage") or r.get("next"),
            "meta": slug in META_SLUGS,
        })

    drift = []
    for r in out_rows:
        was = prev_stages.get(r["slug"])
        if was is not None and was != r["current_stage"]:
            drift.append({"slug": r["slug"], "was": was,
                          "now": r["current_stage"]})

    body = {
        "schema": TRACKER_JSON_SCHEMA,
        "generated": stamp,
        "generated_epoch": int(time.time()),
        "source": str(tracker_path),
        "authority": "markdown",   # flips to "json" at Phase 2 step two
        "rows": out_rows,
        "row_count": len(out_rows),
        "drift_since_last_tick": drift,
        "_readme": ("Projection of the stage rows the driver parsed out of "
                    "MOTIF_TRACKER.md this tick. `authority` names which side "
                    "is currently the source of truth -- do not write stage "
                    "state here while it reads 'markdown'."),
    }
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(".tmp")
        tmp.write_text(json.dumps(body, indent=1), encoding="utf-8")
        os.replace(tmp, dest)                                   # atomic
        body["path"] = str(dest)
    except OSError as e:
        body["error"] = f"{type(e).__name__}: {e}"
    return body


AGREEMENT_JSON_NAME = "motif_agreement.json"
AGREEMENT_SCHEMA = "cosmos-motif-agreement/1"

# 15-minute clock: 96 ticks is a full 24 hours, so the streak can only be
# reached by surviving a whole daily cycle of dispatches, COW disposition edits
# and lane traffic. Nothing here ever flips authority; the streak is evidence
# offered to a human, and `flip_ready` is advice.
FLIP_STREAK_TARGET = 96


def stage_map_for(rows: list[dict], repo: Path) -> dict[str, tuple]:
    """{slug: (current_stage, next_stage)} for parsed tracker rows.

    ONE definition, shared by the projection writer and the comparator below, so
    a disagreement between them can only come from the DATA -- never from two
    copies of this arithmetic drifting apart.
    """
    out: dict[str, tuple] = {}
    for r in rows:
        slug = r.get("slug")
        if not slug:
            continue
        if slug in META_SLUGS:
            out[slug] = (None, None)
            continue
        try:
            out[slug] = effective_stage(r, Path(repo))
        except Exception:                                            # noqa: BLE001
            out[slug] = (None, None)
    return out


def compare_projection(runtime_root: Path, tracker_path: Path,
                       repo: Path) -> dict:
    """Check the JSON projection ON DISK against a FRESH parse of the markdown.

    PHASE 2 step two (docs/CORE_RESTRUCTURE.md) PREPARES the authority flip; it
    does not take it. Flipping because the projection *ought* to match would be
    the same unevidenced leap that cost three days on 2026-08-26 -- a claim
    accepted as evidence. This is the evidence instead: every tick, re-open the
    JSON a consumer would read, re-parse the markdown the driver reads today,
    and record AGREEMENT or the exact divergence.

    Both sides are read from DISK and the stages recomputed independently.
    Comparing this tick's in-memory rows against themselves would compare a
    value with itself, and a checker that cannot fail is not a checker.

    Compared: the slug set and the two COMPUTED stages -- the only fields the
    driver acts on. `name`/`artifact`/`raw_next_cell` are provenance and are
    reported by the projection but not gated on.

    Typed verdict `kind`: agree | projection_missing | projection_unreadable |
    source_missing | row_set_differs | stage_differs.
    """
    dest = Path(runtime_root) / "state" / TRACKER_JSON_NAME
    tr = Path(tracker_path)
    verdict = {
        "schema": AGREEMENT_SCHEMA, "checked_at": _iso_now(),
        "projection": str(dest), "source": str(tr),
        "agree": False, "kind": "", "divergences": [], "checked_rows": 0,
    }
    try:
        body = json.loads(dest.read_text(encoding="utf-8"))
    except FileNotFoundError:
        verdict["kind"] = "projection_missing"
        return verdict
    except (OSError, ValueError) as e:
        verdict["kind"] = "projection_unreadable"
        verdict["detail"] = f"{type(e).__name__}: {e}"
        return verdict
    if not tr.is_file():
        verdict["kind"] = "source_missing"
        return verdict
    verdict["generated"] = body.get("generated")
    verdict["authority"] = body.get("authority")

    from_json = {r["slug"]: (r.get("current_stage"), r.get("next_stage"))
                 for r in (body.get("rows") or []) if r.get("slug")}
    from_md = stage_map_for(
        parse_tracker(tr.read_text(encoding="utf-8")), Path(repo))

    divs = []
    for slug in sorted(set(from_json) | set(from_md)):
        j, m = from_json.get(slug), from_md.get(slug)
        if j is None or m is None:
            divs.append({"slug": slug, "field": "row",
                         "json": "present" if j is not None else "absent",
                         "markdown": "present" if m is not None else "absent"})
            continue
        for i, field in enumerate(("current_stage", "next_stage")):
            if j[i] != m[i]:
                divs.append({"slug": slug, "field": field,
                             "json": j[i], "markdown": m[i]})
    verdict["checked_rows"] = len(set(from_json) | set(from_md))
    verdict["divergences"] = divs
    if not divs:
        verdict.update({"agree": True, "kind": "agree"})
    elif any(d["field"] == "row" for d in divs):
        verdict["kind"] = "row_set_differs"
    else:
        verdict["kind"] = "stage_differs"
    return verdict


def record_agreement(runtime_root: Path, verdict: dict) -> dict:
    """Bank the tick's verdict: consecutive agreeing ticks, last divergence.

    The streak is the artifact that would justify flipping authority, and the
    only thing that can raise it is a tick that actually agreed -- so it cannot
    be talked up, only earned. Any divergence resets it to zero, including one
    caused by a concurrent edit to the markdown: at flip time that same race
    LOSES the edit, so it is a finding, not noise.
    """
    dest = Path(runtime_root) / "state" / AGREEMENT_JSON_NAME
    try:
        prev = json.loads(dest.read_text(encoding="utf-8")) or {}
    except (OSError, ValueError):
        prev = {}
    agree = bool(verdict.get("agree"))
    streak = (int(prev.get("consecutive_agreements") or 0) + 1) if agree else 0
    rec = {
        "schema": AGREEMENT_SCHEMA,
        "checked_at": verdict.get("checked_at"),
        "agree": agree,
        "kind": verdict.get("kind"),
        "checked_rows": verdict.get("checked_rows"),
        "divergences": (verdict.get("divergences") or [])[:12],
        "consecutive_agreements": streak,
        "longest_streak": max(int(prev.get("longest_streak") or 0), streak),
        "ticks_total": int(prev.get("ticks_total") or 0) + 1,
        "ticks_agreed": int(prev.get("ticks_agreed") or 0) + (1 if agree else 0),
        "last_divergence": (
            {"at": verdict.get("checked_at"), "kind": verdict.get("kind"),
             "divergences": (verdict.get("divergences") or [])[:12]}
            if not agree else prev.get("last_divergence")),
        "flip_streak_target": FLIP_STREAK_TARGET,
        "flip_ready": streak >= FLIP_STREAK_TARGET,
        "authority": verdict.get("authority"),
        "_readme": (
            "Evidence for PHASE 2 step two: does the JSON projection say what a "
            "fresh markdown parse says, every tick? flip_ready is ADVICE, never "
            "an action -- authority flips only when a human lands the change, "
            f"and not before {FLIP_STREAK_TARGET} consecutive agreeing ticks "
            "(24h on the 15-minute clock)."),
    }
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(".tmp")
        tmp.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
        os.replace(tmp, dest)                                       # atomic
        rec["path"] = str(dest)
    except OSError as e:
        rec["error"] = f"{type(e).__name__}: {e}"
    return rec


def release_completed(inflight, queue: Path) -> list[str]:
    """Release every lease whose job has produced its result.

    A lease must close on COMPLETION, not merely age out. Without this the TTL
    does two jobs at once: crash-recovery backstop AND normal exit path, so a
    slug stays blocked for the full TTL after finishing and -- worse -- a job
    still running when the TTL lapses is dispatched a second time. On prepaid
    vendor rails a duplicate dispatch is real money. (Scar 2026-08-30: 20
    CLAIMs, 0 RELEASEs, two claims per slug.)

    Matching note: dispatch writes `<name>__t<timeout>.py` but the receipt is
    `<name>_result.json` -- the timeout suffix is DROPPED -- and receipts land
    under `returns/<lane>/`, not beside the job. Match on the base name and
    search the tree; anchoring on the job filename silently never matches.

    The TTL keeps its real job: a worker that dies without releasing still stops
    blocking on its own. Returns the tokens released.
    """
    released: list[str] = []
    try:
        active = inflight.active()
    except Exception:                                                # noqa: BLE001
        return released
    if not active:
        return released
    for token, rec in active.items():
        job_file = str(rec.get("job_file") or "")
        if not job_file:
            continue
        base = Path(job_file).stem.split("__t")[0]
        if not base:
            continue
        found = None
        try:
            for cand in queue.rglob(base + "_result.json"):
                if cand.is_file():
                    found = str(cand)
                    break
        except OSError:
            continue
        if found:
            try:
                inflight.release(token, outcome="done", detail=found)
                released.append(token)
            except Exception:                                        # noqa: BLE001
                pass
    return released


def is_advancing(slug: str, next_stage: int, names: set[str]) -> str | None:
    """Return the matching inflight token, or None.

    A same-slug Motif job at this stage or a later one counts as advancing
    (do not drop stage 5 while motif_{slug}_s6 is already running).
    """
    token = motif_token(slug, next_stage)
    hay = _haystack(names)
    for n in names:
        if token in n:
            return n
        m = _MOTIF_STAGE_RE.search(n)
        if m and m.group(1) == slug and int(m.group(2)) >= int(next_stage):
            return n
        if slug in n and (f"s{next_stage}" in n or f"stage{next_stage}" in n
                          or f"stage_{next_stage}" in n
                          or f"stage-{next_stage}" in n):
            return n
    for prefix, stage_n, slugs in STAGE_BUNDLES:
        if slug not in slugs:
            continue
        if next_stage > stage_n:
            continue
        if prefix in hay:
            for n in names:
                if prefix in n:
                    return n
    return None


def next_job_task(row: dict, next_n: int) -> str:
    """Deterministic prompt. Same deliverable+stage -> same dispatch filename."""
    name = row["name"]
    artifact = row["artifact"]
    next_text = row["next_stage"]
    slug = row["slug"]
    token = motif_token(slug, next_n)
    header = (
        f"{token} You are G46 (Grok Build), COSMOS Motif next-stage. "
        f"FIRST read docs/AGENT_BRIEF.md (DHx) and docs/MOTIF_TRACKER.md. "
        f"Deliverable: {name}. Artifact: {artifact}. "
        f"Tracker next-stage text: {next_text}. "
        f"Do NOT modify COSMOS core (kernel/ledger/sched/service). "
        f"Never delete; stage to _delme\\. No bats. "
        f"rc=0 is NOT complete — only stage 6 with a live-tree value is.\n\n"
    )
    if next_n == 5:
        body = (
            f"Motif STAGE-5 critique of '{name}'. Different-family review of the "
            f"build vs the spec (is this the thing that was decided). List DEFECTS "
            f"HIGH/MED/LOW with file/symbol. Write docs/critique/{slug}_CRITIQUE_g46.md."
        )
    elif next_n >= 6:
        body = (
            f"Motif STAGE-6 runtime-binding gate for '{name}'. Read any stage-5 "
            f"critique under docs/critique/. APPLY HIGH/MED fixes ADDITIVE (keep "
            f"every existing feature). BUILD and RUN it. Prove by a value only the "
            f"live tree can emit — never an exit code or a green log. Report the "
            f"proof artifact path and the emitted value. Edit only the deliverable "
            f"tree ({artifact})."
        )
    elif next_n == 4:
        body = (
            f"Motif STAGE-4 code for '{name}'. Implement: {next_text}. "
            f"Bind every done claim to a real artifact. Edit only the deliverable tree."
        )
    elif next_n == 3:
        body = (
            f"Motif STAGE-3 critique/rank for '{name}': {next_text}. "
            f"Concrete; UNKNOWN not guess. Write docs/critique/{slug}_STAGE3.md."
        )
    elif next_n == 2:
        body = (
            f"Motif STAGE-2 arch for '{name}': {next_text}. Decision rubric FIRST, "
            f"then a concrete design. Write docs/arch/{slug}_ARCH.md."
        )
    else:
        body = (
            f"Motif STAGE-1 research for '{name}': {next_text}. Vendor-plural, "
            f"UNKNOWN not guess. Write docs/research/{slug}/RESEARCH_1.md."
        )
    return header + body


def write_heartbeat(path: Path, extra: dict | None = None) -> dict:
    now = datetime.now().astimezone()
    rec = {
        "schema": SCHEMA,
        "last_run": now.isoformat(timespec="seconds"),
        "last_run_epoch": int(now.timestamp()),
        "last_run_utc": now.astimezone(dt_timezone.utc).isoformat(timespec="seconds"),
        "worker": WORKER,
        "pid": os.getpid(),
        "_readme": (
            "Written on EVERY tick, pass or idle. COMPARE USING last_run_epoch. "
            "If last_run_epoch is older than ~20 min the Motif Driver clock failed."
        ),
    }
    if extra:
        rec.update(extra)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    tmp.replace(path)
    return rec


def _replace_tick_block(text: str, block: str) -> str:
    body = block if block.endswith("\n") else block + "\n"
    start = text.find(TICK_START)
    end = text.find(TICK_END)
    if start >= 0 and end > start:
        end = end + len(TICK_END)
        after = text[end:]
        if after.startswith("\n"):
            after = after[1:]
        return text[:start] + body + after
    if not text.endswith("\n"):
        text += "\n"
    return text + "\n" + body


def update_tracker(path: Path, dispatched: list[dict], stamp: str,
                   skipped: list[dict]) -> dict:
    """Rewrite next-stage cells for dropped rows; refresh the tick footer."""
    original = path.read_text(encoding="utf-8") if path.exists() else ""
    lines = original.splitlines(keepends=True)
    by_slug = {d["slug"]: d for d in dispatched}
    new_lines = []
    changed = 0
    for line in lines:
        raw = line.strip()
        if not raw.startswith("|"):
            new_lines.append(line)
            continue
        cells = [c.strip() for c in raw.strip("|").split("|")]
        if len(cells) < 4:
            new_lines.append(line)
            continue
        slug = canonical_slug(CELL_STRIP.sub("", cells[0]))
        rec = by_slug.get(slug)
        if rec is None:
            new_lines.append(line)
            continue
        note = f"DISPATCHED {rec['token']} {stamp}"
        nxt = cells[3]
        if rec["token"] in nxt and "DISPATCHED" in nxt:
            new_lines.append(line)
            continue
        # drop a prior DISPATCHED clause, keep the human next-stage text
        nxt_core = re.sub(r"\s*·\s*DISPATCHED\s+\S+.*$", "", nxt).rstrip()
        cells[3] = f"{nxt_core} · {note}"
        nl = "\n" if line.endswith("\n") else ""
        if line.endswith("\r\n"):
            nl = "\r\n"
        new_lines.append("| " + " | ".join(cells) + " |" + nl)
        changed += 1
    text = "".join(new_lines)
    skip_s = ", ".join(
        f"{s['slug']}:{s.get('reason')}" for s in skipped[:12]) or "(none)"
    drop_s = ", ".join(
        f"{d['slug']}->s{d['next_stage']}@{d.get('lane', '?')}"
        for d in dispatched) or "(none)"
    footer = (
        f"{TICK_START}\n"
        f"Last mechanical tick: {stamp} · dispatched={len(dispatched)} "
        f"skipped={len(skipped)}\n"
        f"Dropped: {drop_s}\n"
        f"Skipped: {skip_s}\n"
        f"{TICK_END}\n"
    )
    text = _replace_tick_block(text, footer)
    if text != original:
        path.write_text(text, encoding="utf-8")
    return {"wrote": text != original, "rows_updated": changed,
            "path": str(path)}


def drive_once(*, repo=None, queue=None, runtime_root=None, tracker=None,
               collector_md=None, dhx=None, dry_run: bool = False) -> dict:
    """One mechanical tick. Never claims a deliverable is complete."""
    repo_p = Path(repo) if repo is not None else repo_tree()
    rt = Path(runtime_root) if runtime_root is not None else default_runtime_root()
    q = Path(queue) if queue is not None else (rt / "queue")
    tr_path = Path(tracker) if tracker is not None else (repo_p / "docs" / "MOTIF_TRACKER.md")
    col_path = (Path(collector_md) if collector_md is not None
                else (repo_p / "docs" / "COLLECTOR.md"))
    dhx_path = Path(dhx) if dhx is not None else (repo_p / "docs" / "AGENT_BRIEF.md")
    stamp = _iso_now()
    t0 = time.time()

    tracker_text = tr_path.read_text(encoding="utf-8") if tr_path.exists() else ""
    collector_text = col_path.read_text(encoding="utf-8") if col_path.exists() else ""
    rows = parse_tracker(tracker_text)

    # PAUSE guard (P2/P10): a HOLD stops NEW motif submissions. The runner and any
    # in-flight jobs keep moving (that is cosmos_run's job, correctly pause-agnostic).
    # Without this, the 15-min driver refills the runner against a hold — the grok
    # saturation scar, 2026-08-26. A resume_gate flag self-clears elsewhere (WD2);
    # a hold stays paused until Keith deletes the flag. A human --dry-run still runs.
    pause_flag = rt / "state" / "control" / "PAUSE.flag"
    if not dry_run and pause_flag.is_file():
        try:
            _pf = json.loads(pause_flag.read_text(encoding="utf-8") or "{}")
        except (OSError, ValueError):
            _pf = {}
        if str(_pf.get("state", "PAUSED")).upper() != "RUNNING":
            return {"ok": True, "schema": SCHEMA, "stamp": stamp, "tick": "paused",
                    "mode": _pf.get("mode", "hold"), "dispatched": [],
                    "skipped": [{"slug": r["slug"], "reason": "paused"} for r in rows],
                    "queue": str(q), "rows": len(rows), "elapsed_s": 0.0}

    # Queue filenames + mtime-windowed manifests are a rolling scrape of
    # artifacts that outlive the work they describe, so they cannot decide
    # a skip — inflight leases and the ledger are the authority. Scar
    # 2026-08-30: cdeck/gbridge blocked themselves with their own receipts.
    # Kept as an advisory count so the signal stays visible.
    file_names = inflight_filenames(q)
    names = ledger_inflight(ledger_paths(q))
    # COLLECTOR.md is a rolling SUMMARY of recent work carrying no completion
    # signal, so it cannot decide a skip — the queue and the ledger are the
    # authority, as this call site always said. Scar 2026-08-30: collector and
    # dispatch were skipped against their own finished summary lines. Kept as an
    # advisory count so the signal stays visible without gaining authority.
    soft_names = {
        m.group(1).strip().lower()
        for m in re.finditer(r"· \*\*([^*]+)\*\*", collector_text[:8000])
    }
    critique_hits = [
        row["slug"] for row in rows
        if critique_exists(repo_p, row["slug"], row["name"])
    ]

    # OWNED in-flight state. Leases are explicit and they EXPIRE, so a worker
    # that dies without releasing stops blocking on its own. The ledger is
    # the other primitive (belt-and-braces with owned leases). Scar 2026-08-30.
    inflight = Inflight(rt / "state" / "inflight.jsonl")
    lease_unreadable = False
    try:
        # Close finished leases BEFORE reading the active set, so a slug that
        # completed since the last tick is free to advance immediately instead
        # of waiting out its TTL.
        released_now = release_completed(inflight, q)
        lease_tokens = inflight.tokens()
        lease_expired = [r["token"] for r in inflight.expired()]
    except Exception:  # noqa: BLE001
        # An unreadable lease store must not read as 'nothing is running'.
        # Fail closed: skip every row this tick rather than dispatching blind.
        lease_tokens, lease_expired = set(), ["LEASE_STORE_UNREADABLE"]
        released_now = []
        lease_unreadable = True
    names |= lease_tokens

    dispatched: list[dict] = []
    skipped: list[dict] = []
    for row in rows:
        slug = row["slug"]
        if slug in META_SLUGS:
            skipped.append({"slug": slug, "name": row["name"],
                            "reason": "meta"})
            continue
        if lease_unreadable:
            skipped.append({"slug": slug, "name": row["name"],
                            "reason": "lease_unreadable"})
            continue
        cur, nxt = effective_stage(row, repo_p)
        if cur >= 6:
            skipped.append({"slug": slug, "name": row["name"],
                            "reason": "stage6"})
            continue
        hit = is_advancing(slug, nxt, names)
        if hit:
            skipped.append({"slug": slug, "name": row["name"],
                            "reason": "inflight", "hit": hit,
                            "next_stage": nxt})
            continue
        token = motif_token(slug, nxt)
        task = next_job_task(row, nxt)
        rec = {
            "slug": slug, "name": row["name"], "current_stage": cur,
            "next_stage": nxt, "token": token, "artifact": row["artifact"],
        }
        if dry_run:
            rec["dry_run"] = True
            dispatched.append(rec)
            names.add(token)
            continue
        try:
            out = dispatch(
                AGENT, task, str(repo_p), kind="grok",
                queue=q, runtime_root=rt, dhx=dhx_path,
            )
        except Exception as e:  # noqa: BLE001
            rec["ok"] = False
            rec["error"] = f"{type(e).__name__}: {e}"
            skipped.append({**rec, "reason": "dispatch_error"})
            continue
        rec.update({
            "ok": bool(out.get("ok")),
            "created": out.get("created"),
            "lane": out.get("lane"),
            "job_file": out.get("job_file"),
            "job_path": out.get("job_path"),
            "marker": out.get("marker"),
            "stamp": out.get("stamp"),
        })
        dispatched.append(rec)
        if rec.get("ok"):
            try:
                inflight.claim(token, slug=slug, stage=nxt, worker=AGENT,
                               lane=rec.get("lane") or "",
                               job_file=rec.get("job_file") or "")
                rec["leased"] = True
            except Exception as e:  # noqa: BLE001
                # A lease we could not write is reported, never assumed.
                rec["leased"] = False
                rec["lease_error"] = f"{type(e).__name__}: {e}"
        if rec.get("job_file"):
            names.add(str(rec["job_file"]).lower())
        names.add(token)

    tracker_rec = {"wrote": False, "rows_updated": 0, "path": str(tr_path)}
    if not dry_run:
        tracker_rec = update_tracker(tr_path, dispatched, stamp, skipped)

    # Phase 2 step one: publish machine state as JSON beside the markdown.
    # Additive -- markdown remains authority until the flip is verified.
    stage_map = stage_map_for(rows, repo_p)
    tracker_json = write_tracker_json(rt, rows, tr_path, stamp, stage_map)

    # Phase 2 step two: PREPARE the flip -- measure it, never take it. Compare
    # what a consumer would read out of the JSON against a fresh parse of the
    # markdown, and bank the agreement streak as the evidence for flipping.
    projection = compare_projection(rt, tr_path, repo_p)
    agreement = {} if dry_run else record_agreement(rt, projection)

    hb_path = rt / "logs" / HEARTBEAT_NAME
    extra = {
        "tick": "dry_run" if dry_run else "once",
        "dispatched": len(dispatched),
        "skipped": len(skipped),
        "rows": len(rows),
        "elapsed_s": round(time.time() - t0, 3),
        "tracker": str(tr_path),
        "tracker_json": tracker_json.get("path"),
        "tracker_rows": tracker_json.get("row_count"),
        "tracker_drift": tracker_json.get("drift_since_last_tick"),
        "tracker_authority": tracker_json.get("authority"),
        "projection_agree": projection.get("agree"),
        "projection_kind": projection.get("kind"),
        "projection_divergences": (projection.get("divergences") or [])[:12],
        "projection_streak": agreement.get("consecutive_agreements"),
        "projection_flip_ready": agreement.get("flip_ready"),
        "queue": str(q),
        "soft_inflight": len(soft_names),
        "soft_filenames": len(file_names),
        "soft_critiques": critique_hits,
        "leases_active": len(lease_tokens),
        "leases_expired": lease_expired,
        "leases_released": released_now,
        "jobs": [
            {"slug": d["slug"], "next_stage": d["next_stage"],
             "lane": d.get("lane"), "job_file": d.get("job_file"),
             "token": d["token"]}
            for d in dispatched
        ],
    }
    if not dry_run:
        write_heartbeat(hb_path, extra)
    return {
        "ok": True,
        "schema": SCHEMA,
        "stamp": stamp,
        "dry_run": dry_run,
        "dispatched": dispatched,
        "skipped": skipped,
        "tracker": tracker_rec,
        "projection": projection,
        "agreement": agreement,
        "heartbeat": str(hb_path),
        "queue": str(q),
        "rows": len(rows),
        "elapsed_s": extra["elapsed_s"],
    }


def standup() -> dict:
    """Register the 15-minute clock. Report the one Keith command if denied."""
    existing = query_task()
    if existing.get("ok"):
        return {"started": "already", "task": existing,
                "keith_cmd": None, "task_name": TASK_NAME}
    task = install_task()
    return {
        "started": "schtasks" if task.get("ok") else "failed",
        "task": task,
        "keith_cmd": task.get("keith_cmd") if (
            task.get("needs_elevation") or not task.get("ok")) else None,
        "task_name": TASK_NAME,
    }


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_motif_driver")
    ap.add_argument("--once", action="store_true",
                    help="one mechanical tick then exit")
    ap.add_argument("--standup", action="store_true",
                    help="register the 15-minute Windows scheduled task")
    ap.add_argument("--dry-run", action="store_true",
                    help="parse + decide; do not drop jobs or edit the tracker")
    ap.add_argument("--root", default=None,
                    help="COSMOS runtime root (default <repo>/live)")
    ap.add_argument("--queue", default=None)
    ap.add_argument("--tracker", default=None)
    ap.add_argument("--collector-md", default=None)
    ap.add_argument("--dhx", default=None)
    ap.add_argument("--repo", default=None)
    a = ap.parse_args()
    if not (a.once or a.standup or a.dry_run):
        a.once = True
    rec: dict = {"ok": True}
    if a.standup:
        rec["standup"] = standup()
    if a.once or a.dry_run:
        rec["tick"] = drive_once(
            repo=a.repo, queue=a.queue, runtime_root=a.root,
            tracker=a.tracker, collector_md=a.collector_md, dhx=a.dhx,
            dry_run=a.dry_run,
        )
    print(json.dumps(rec, indent=1, default=str))
    if a.standup and rec.get("standup", {}).get("keith_cmd"):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
