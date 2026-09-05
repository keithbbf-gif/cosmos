#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_collector_dhx - DHx assignment-log parsing and marker <-> result join.

Split out of `cosmos_collector.py` (PHASE 4, `docs/CORE_RESTRUCTURE.md`) along a
seam that already existed: this is the whole of the collector's *pure* DHx layer.
Text and dicts in, dicts out -- no runtime root, no resolver, no daemon state, no
writes. `cosmos_collector` re-exports every name below, so every existing importer
keeps working unchanged; nothing outside the collector imported these directly.

What lives here, and why it is one piece:
  * the LANE vocabulary   - the routing folders DHx markers are written in
  * the marker grammar    - DHX_LINE / DHX_LANE_FILE / JOB_TOKEN / HEX8
  * `task_of`             - the job-stem normalizer both the grammar and the join
                            depend on (strip `_result.json`, `__t1800`, `__<ts>`)
  * `parse_dhx_markers`   - assignment log -> markers
  * `marker_stems`        - marker -> the stems it may be joined on
  * `correlate_marker`    - marker + catalog rows -> the newest matching result
  * `resolve_marker_artifact` - marker -> a deliverable that is not a queue result

What deliberately did NOT move: `Collector._collect_dhx`. It reads `self.catalog`,
writes `self.dhx_snap` and appends through `self._row`/`self._consider` -- pulling
it out would mean passing the collector into a free function, which is coupling
wearing a module's clothes, not a seam. The seam is exactly here, at the boundary
where the DHx logic stops needing the daemon.

The one filesystem touch, `resolve_marker_artifact`, is read-only, best effort, and
takes both roots as arguments -- no path is assembled from a literal (canon: no
hard-coded paths).
"""
from __future__ import annotations

import re
from pathlib import Path

# Lane names are routing folders, never agents (H2). cm is the COSMOS
# dispatch lane; buckets/ is the node-worker drop. root/lg/pb are BTS.
LANE_NAMES = {"lg", "pb", "root", "cm", "buckets"}
KNOWN_LANES = LANE_NAMES | {"returns", "inbox"}
DHX_LINE = re.compile(
    r"^[-*]\s*(?P<ts>20\d{2}-\d{2}-\d{2}\S*)\s*[·\-]\s*(?P<agent>[^·\-|]+?)"
    r"\s*[·\-]\s*(?P<body>.+)$"
)
# Any lane[/sub]/job token — cm/, buckets/grok/, lg/, pb/, root/. Last
# high-score hit wins so docs/AGENT_BRIEF.md in the assignment text does
# not steal the jobfile (H1 residual: stage-5 parser only matched root|lg|pb).
DHX_LANE_FILE = re.compile(
    r"(?P<full>(?P<lane>[A-Za-z][A-Za-z0-9_.-]{0,24})"
    r"(?:/[A-Za-z0-9_.-]{1,64})*/"
    r"(?P<job>[A-Za-z0-9][A-Za-z0-9_.-]{3,200}))"
)
JOB_TOKEN = re.compile(
    r"\b((?:g46|grok|gem|oai|oa|sgh|cursor|claude|cowork|motif|cdeck|cvm|cdm)"
    r"_[A-Za-z0-9_.-]{6,})",
    re.I,
)
HEX8 = re.compile(r"_([0-9a-f]{8})(?:_|$|\.)", re.I)

# Sources that are themselves markers/assignments, never a result to join to.
SKIP_SOURCES = {"dhx_marker", "dispatch_assignment"}

# How strongly a catalog source counts as "the deliverable came back".
# A result JSON beats an inbox copy beats a log line beats a runner ledger row.
SOURCE_RANK = {
    "queue_result": 3.0e12,
    "queue_returns": 3.0e12,
    "drop_returns": 2.5e12,
    "queue_done": 2.0e12,
    "queue_failed": 2.0e12,
    "dispatch_inbox": 1.5e12,
    "queue_log": 1.0e12,
    "runner_ledger": 0.5e12,
}

# Where a non-queue deliverable plausibly lands, relative to a root. "" is the
# root itself. Ordered cheapest/most-likely first.
ARTIFACT_SUBDIRS = ("logs", "state", "proof", "cosmos", "builds", "docs", "")


def task_of(path: Path) -> str:
    """Job stem: strip the result/hands suffix, the runner timeout, the stamp."""
    name = path.name
    lower = name.lower()
    if lower.endswith("_result.json"):
        name = name[: -len("_result.json")]
    elif lower.endswith(".result.json"):
        name = name[: -len(".result.json")]
    elif lower.endswith("_hands.md"):
        name = name[: -len(".md")]
    stem = Path(name).stem
    # strip runner timeout suffix: foo__t1800
    if "__t" in stem:
        head, tail = stem.rsplit("__t", 1)
        if tail.isdigit():
            stem = head
    # strip timestamp suffix on logs: foo__2026-08-25T21-14-04
    if "__20" in stem:
        head, tail = stem.rsplit("__", 1)
        if tail[:4].isdigit():
            stem = head
    return stem


def path_hit_score(m: re.Match) -> int:
    """Prefer real job paths over docs/ mentioned in the assignment text."""
    lane = (m.group("lane") or "").lower()
    job = (m.group("job") or "").lower()
    score = 0
    if lane in KNOWN_LANES:
        score += 12
    if job.endswith(".py") or job.endswith("_result.json") or job.endswith(".json"):
        score += 8
    if "__t" in job:
        score += 4
    if job.startswith(("g46_", "grok_", "gem_", "oa_", "oai_", "sgh_",
                       "cursor_", "claude_", "cowork_", "motif_")):
        score += 6
    if job.endswith(".md"):
        score -= 6
    if lane in {"docs", "live", "cosmos", "tests", "builds"}:
        score -= 8
    return score


def pick_lane_job(body: str) -> tuple[str, str, int]:
    """Return (lane, jobfile, match_start) from a DHx marker body."""
    blob = str(body or "").replace("\\", "/")
    hits = list(DHX_LANE_FILE.finditer(blob))
    if not hits:
        return "", "", -1
    best = hits[-1]
    best_score = path_hit_score(best)
    for h in hits:
        sc = path_hit_score(h)
        if sc >= best_score:
            best, best_score = h, sc
    if best_score < 0:
        return "", "", -1
    return (best.group("lane") or "").lower(), best.group("job") or "", best.start()


def parse_dhx_markers(text: str) -> list[dict]:
    """Parse DHx assignment-log markers.

    Protocol: `ISO-timestamp · agent · assignment · lane/file`.
    Also accepts ` - ` as the separator (dispatch stamps that form).
    lane/file is any routing folder (cm/, lg/, pb/, root/, buckets/…),
    not just the historical BTS pair.
    """
    lines = str(text or "").splitlines()
    in_log = False
    out: list[dict] = []
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
        agent = m.group("agent").strip()
        lane, jobfile, cut = pick_lane_job(body)
        if cut >= 0 and jobfile:
            assignment = body[:cut].strip(" ·-|")
        else:
            assignment = body
        out.append({
            "ts": m.group("ts"),
            "agent": agent,
            "assignment": assignment,
            "body": body,
            "lane": lane,
            "jobfile": jobfile,
            "task": task_of(Path(jobfile)) if jobfile else assignment[:80],
            "raw": s,
        })
    return out


def marker_stems(marker: dict) -> list[str]:
    """Every stem a marker may legitimately be joined on, longest first."""
    stems: list[str] = []
    job = str(marker.get("jobfile") or "")
    task = str(marker.get("task") or "")
    body = str(marker.get("body") or "")
    if job:
        stems.append(Path(job).name)
        stems.append(Path(job).stem)
        stems.append(task_of(Path(job)))
    if task:
        stems.append(task)
    for tok in JOB_TOKEN.findall(f"{job} {task} {body}"):
        stems.append(tok)
        stems.append(task_of(Path(tok)))
    for blob in (job, task):
        for hx in HEX8.findall(blob):
            stems.append(hx)
    out: list[str] = []
    seen: set[str] = set()
    for s in stems:
        sl = s.strip().lower()
        if sl and sl not in seen and len(sl) >= 4:
            seen.add(sl)
            out.append(sl)
    # longest first so a full job stem beats a short hash collision
    out.sort(key=len, reverse=True)
    return out


def resolve_marker_artifact(mk, repo_root, runtime_root):
    """Locate a marker's deliverable when it is not a QUEUE RESULT.

    Not every assignment lands as a job result. Some produce a heartbeat, a
    proof file, or a landed source module. `correlate_marker` only searches the
    collector catalog (queue results), so those deliverables came back MISSING
    even though they exist on disk -- which conflated three very different
    situations under one alarming word:

      matched  -> a queue result exists           (unchanged)
      ARTIFACT -> the named deliverable exists, just not as a queue result
      MISSING  -> nothing was produced; this is the one worth chasing

    Returns the resolved path as a string, or None. Read-only, best effort; a
    root that is None or not a directory is skipped, never a TypeError.
    (2026-08-30: of 6 reported MISSING, 3 were present as heartbeat/source and
    only 2 were genuinely absent, with 1 malformed marker.)
    """
    name = (mk.get("jobfile") or "").strip()
    if not name or name in {"-", "--"}:
        return None
    stem = name.rsplit(".", 1)[0]
    roots = [Path(r) for r in (runtime_root, repo_root) if r and Path(r).is_dir()]
    for root in roots:
        for sub in ARTIFACT_SUBDIRS:
            base = (root / sub) if sub else root
            if not base.is_dir():
                continue
            for cand in (name, stem + ".json", stem + ".py", stem + ".md"):
                p = base / cand
                try:
                    if p.is_file():
                        return str(p)
                except OSError:
                    continue
    return None


def correlate_marker(marker: dict, rows: list[dict]) -> dict | None:
    """Join a DHx marker to the newest matching result row (not the marker itself)."""
    stems = marker_stems(marker)
    if not stems:
        return None
    best = None
    best_rank = -1.0
    for row in rows:
        src = str(row.get("source") or "")
        if src in SKIP_SOURCES:
            continue
        art = str(row.get("artifact") or "").replace("\\", "/").lower()
        task = str(row.get("task") or "").lower()
        name = Path(str(row.get("artifact") or "")).name.lower()
        blob = f"{art} {task} {name}"
        matched_stem = next((s for s in stems if s in blob), "")
        if not matched_stem:
            continue
        try:
            mt = float(row.get("mtime") or 0)
        except (TypeError, ValueError):
            mt = 0.0
        # Result JSON beats inbox/logs. Stem length is a tie-breaker only
        # (a `__t1800` suffix must not beat a *_result.json).
        rank = SOURCE_RANK.get(src, 0.0) + (len(matched_stem) * 1e6) + mt
        if rank >= best_rank:
            best_rank = rank
            best = row
    return best
