#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_watchdog2_scan - WD2 markdown/route scanners (PHASE 4 seam).

Split out of `cosmos_watchdog2.py` (docs/CORE_RESTRUCTURE.md) along the
seam that already existed: `# scanners` at the former line 590. Text and
dicts in, dicts out -- no daemon state, no 15s loop, no schtasks. The
one filesystem touch (`cursor_key_exists`, `annotate_*`, `update_*_tick`)
takes paths as arguments; no path is assembled from a drive literal.

`cosmos_watchdog2` re-exports every name below, so every existing importer
(`tests/test_watchdog2.py`, `tests/test_askmine.py` parse_md_checkboxes,
`tests/test_competency.py` pick_agent) keeps working unchanged.

What lives here:
  * MD_ROUTE_SOURCES     - wishlist / backlog / askmine checkbox table
  * parse_md_checkboxes  - one parser for every markdown route source
  * pick_agent           - competency pick among dispatchable nodes
  * checkbox_skip_reason / name_hit / dhx_haystack
  * wishlist_task / backlog_task / route_drop_spec
  * annotate_checkbox / update_source_tick (path-in, path-out)

What deliberately did NOT move: `Watchdog2`, `scan_once`, standup/loop.
Those own the 15s clock, the queue drop, and the heartbeat.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_dispatch import LANE_ORDER  # noqa: E402
from cosmos_motif_driver import next_job_task  # noqa: E402
from cosmos_competency import (  # noqa: E402
    DISPATCHABLE,
    CompetencyError,
    agent_kind,
    classify_task_type,
    default_path,
    load as load_competency,
    pick as pick_node,
)

CURSOR_KEY_NAME = "cursor_cosmos_key.txt"
CURSOR_LOAD_OVERFLOW = 5

CHECK_RE = re.compile(r"^- \[([ xX])\]\s+(.*)$")
NON_ALNUM = re.compile(r"[^a-z0-9]+")
TICK_START = "<!-- watchdog2-tick -->"
TICK_END = "<!-- /watchdog2-tick -->"

# ONE parser, ONE skip/inflight guard, ONE drop cap. Wishlist survivors
# enter MOTIF at stage 1 (research). Order = drop priority after tracker
# rows: new wishes first (the self-build fuel), then leftover backlog.
MD_ROUTE_SOURCES = (
    {
        "name": "wishlist",
        "filename": "WISHLIST.md",
        "section": "Open wishes",
        "enter": "motif_s1",
    },
    {
        "name": "backlog",
        "filename": "BACKLOG.md",
        "section": None,
        "enter": "implement",
    },
    {
        "name": "askmine",
        "filename": "UNANSWERED.md",
        "loc": "state",
        "subdir": "askmine",
        "section": "Open",
        "enter": "implement",
    },
)

# This daemon IS the agent for these BACKLOG rows. Do not drop a second job.
SELF_SLUGS = frozenset({
    "watchdog2",
    "clock_cadence_rubric",
    "clock_cadence",
    "constant_session_backlog_agent",
    "session_backlog",
    "askmine",
    "session_transcript_mining",
})

KEITH_SECTION_HINTS = (
    "owed", "live core", "keith-only", "keith only", "not fire-and-forget",
)
SKIP_PHRASES = (
    "keith's call",
    "not fire-and-forget",
    "cow review",
    "cow's in-session",
)
STOPWORDS = frozenset({
    "from", "with", "that", "this", "each", "have", "open", "item", "into",
    "plus", "then", "live", "the", "and", "for", "own", "via", "its", "not",
    "all", "any", "but", "as", "of", "to", "on", "in", "or", "a", "an",
    "cosmos", "result", "json", "grok", "g46", "motif", "stage", "docs",
    "file", "files", "agent", "job", "python", "being",
})
CODING_HINTS = (
    "build", "code", "implement", "wire", "harden", "fix", "runner",
    "daemon", "clock", "dispatch",
)


def _fold(text: str) -> str:
    return NON_ALNUM.sub("", str(text or "").lower())


def _backlog_slug(title: str) -> str:
    s = NON_ALNUM.sub("_", str(title or "").lower()).strip("_")
    return (s[:40] or "item")


def _clip(s: str, n: int = 160) -> str:
    s = " ".join(str(s).split())
    if len(s) <= n:
        return s
    return s[: n - 1] + "…"


def _split_title_body(rest: str) -> tuple[str, str]:
    rest = rest.strip()
    if rest.startswith("**"):
        end = rest.find("**", 2)
        if end > 2:
            title = rest[2:end].strip()
            body = rest[end + 2:].lstrip(" \t—-:").strip()
            return title, body
    return _clip(rest, 80), rest


def parse_md_checkboxes(text: str, source: str, *,
                        section: str | None = None) -> list[dict]:
    """Checkbox rows from one markdown route source.

    If *section* is set, only rows under that exact ``##`` heading are
    returned (WISHLIST 'Open wishes'). Keith/owed headings are tagged
    when the whole file is scanned — not dropped here.
    """
    items: list[dict] = []
    current = ""
    keith_section = False
    in_section = section is None
    for raw in str(text or "").splitlines():
        line = raw.rstrip()
        if line.startswith("## "):
            current = line[3:].strip()
            low = current.lower()
            keith_section = any(h in low for h in KEITH_SECTION_HINTS)
            if section is not None:
                in_section = current.lower() == section.lower()
            continue
        if not in_section:
            continue
        m = CHECK_RE.match(line.strip())
        if not m:
            continue
        checked = m.group(1).lower() == "x"
        title, body = _split_title_body(m.group(2))
        items.append({
            "source": source,
            "section": current,
            "checked": checked,
            "title": title,
            "body": body,
            "line": line,
            "slug": _backlog_slug(title),
            "keith_section": keith_section,
        })
    return items


def parse_backlog(text: str) -> list[dict]:
    """BACKLOG.md is one MD_ROUTE_SOURCES member."""
    return parse_md_checkboxes(text, "backlog")


def dhx_haystack(text: str) -> str:
    """Folded assignment-log + active-assignment lines (in-flight evidence)."""
    chunks: list[str] = []
    in_log = False
    in_active = False
    for raw in str(text or "").splitlines():
        if raw.startswith("## Assignment log"):
            in_log = True
            in_active = False
            continue
        if raw.startswith("## Active assignments"):
            in_active = True
            in_log = False
            continue
        if raw.startswith("## ") and (in_log or in_active):
            in_log = False
            in_active = False
            continue
        if (in_log or in_active) and raw.lstrip().startswith("-"):
            chunks.append(raw)
    return _fold(" ".join(chunks))


def cursor_key_exists(runtime_root: Path) -> bool:
    p = Path(runtime_root) / "config" / CURSOR_KEY_NAME
    try:
        return p.is_file() and p.stat().st_size > 8
    except OSError:
        return False


def pick_agent(item: dict, loads: dict, key_exists: bool,
               *, matrix=None, available=None) -> tuple[str, str]:
    """(agent, kind). Competency matrix among dispatchable nodes.

    Cursor named in the text still wins when the key exists (operator asked).
    Load overflow removes G46 from the available set so the next rated
    coding node (Cursor) is picked — same valve as before, expressed as
    availability. A torn matrix fails closed to G46 rather than halting
    the 15s clock.
    """
    folded = _fold(item.get("title", "") + " " + item.get("body", ""))
    if "cursor" in folded and key_exists:
        return "Cursor", "cursor"
    coding = any(h in folded for h in CODING_HINTS)
    grok_load = 0
    if loads:
        grok_load = min(int(loads[l]["load"]) for l in LANE_ORDER if l in loads)

    if matrix is None:
        try:
            matrix = load_competency(default_path())
        except CompetencyError:
            matrix = None
    if matrix is None:
        if coding and grok_load >= CURSOR_LOAD_OVERFLOW and key_exists:
            return "Cursor", "cursor"
        return "G46", "grok"

    if available is None:
        avail = set(DISPATCHABLE)
    else:
        avail = set(available)
    if key_exists:
        avail.add("Cursor")
    else:
        avail.discard("Cursor")
    if coding and grok_load >= CURSOR_LOAD_OVERFLOW and key_exists:
        avail.discard("G46")
    try:
        node = pick_node(matrix, classify_task_type(folded), avail)
        return agent_kind(node)
    except CompetencyError:
        if coding and grok_load >= CURSOR_LOAD_OVERFLOW and key_exists:
            return "Cursor", "cursor"
        return "G46", "grok"


def _tokens(slug: str, title: str) -> list[str]:
    raw = (slug + " " + title).lower()
    words = re.findall(r"[a-z0-9]{4,}", raw)
    out = []
    for w in words:
        if w in STOPWORDS:
            continue
        if w not in out:
            out.append(w)
    return out


def name_hit(slug: str, title: str, names: set[str], dhx_fold: str) -> str | None:
    """Return the matching in-flight token, or None.

    'cosmos' is in almost every job name — it is a stopword. A hit needs the
    backlog_* token, the compact slug, two distinctive tokens on ONE filename,
    or one token of length >= 8.
    """
    compact = _fold(slug)
    hay = " ".join(sorted(names))
    hay_fold = _fold(hay)
    token = f"backlog_{slug}"
    token_fold = _fold(token)
    if token_fold and token_fold in hay_fold:
        for n in names:
            if token_fold in _fold(n) or token.lower() in n:
                return n
    core_slug = slug
    if core_slug.startswith("cosmos_"):
        core_slug = core_slug[7:]
    parts = [p for p in core_slug.split("_") if p not in STOPWORDS and len(p) >= 4]
    needle = "".join(parts[:2])
    if needle and len(needle) >= 5:
        for n in names:
            if needle in _fold(n):
                return n
    core = compact[6:] if compact.startswith("cosmos") else compact
    if core and len(core) >= 8 and core in hay_fold:
        for n in names:
            if core in _fold(n):
                return n
    toks = [t for t in _tokens(slug, title) if len(t) >= 5]
    for n in names:
        nf = n.lower()
        hits = [t for t in toks if t in nf]
        if len(hits) >= 2:
            return n
        if any(len(t) >= 8 and t in nf for t in toks):
            return n
    # dhx_fold is accepted for signature compatibility. Assignment-log
    # prose cannot decide a skip (COLLECTOR.md scar 2026-08-30).
    _ = dhx_fold
    return None


def _tracked_hit(item: dict, tracked_names: set[str]) -> str | None:
    """Wish already represented in MOTIF_TRACKER or another checkbox source."""
    title_fold = _fold(item.get("title", "") + " " + item.get("body", ""))
    slug_fold = _fold(item.get("slug", ""))
    parts = set(re.findall(r"[a-z0-9]+", (item.get("title") or "").lower()))
    parts.update(str(item.get("slug") or "").lower().split("_"))
    for n in tracked_names:
        nf = _fold(n)
        if not nf:
            continue
        if slug_fold and slug_fold == nf:
            return n
        if len(nf) >= 5 and (nf in title_fold or nf in slug_fold
                             or (slug_fold and slug_fold in nf)):
            return n
        if 3 <= len(nf) <= 4 and nf in parts:
            return n
    return name_hit(item.get("slug", ""), item.get("title", ""),
                    tracked_names, "")


def checkbox_skip_reason(item: dict, names: set[str], dhx_fold: str,
                         assigned: dict, orch_text: str,
                         tracked_names: set[str] | None = None) -> str | None:
    if item.get("checked"):
        return "checked"
    if item.get("keith_section"):
        return "keith_section"
    blob = (item.get("title", "") + " " + item.get("body", "")).lower()
    for phrase in SKIP_PHRASES:
        if phrase in blob:
            return "cow_or_keith"
    slug = item["slug"]
    folded = _fold(slug)
    if folded in {_fold(s) for s in SELF_SLUGS} or slug in SELF_SLUGS:
        # This daemon is the agent. Clock-cadence is done once ORCHESTRATION
        # carries the rubric heading.
        if "clock" in folded and "cadence" in folded:
            if "clock cadence rubric" in orch_text.lower():
                return "self_encoded"
            return "self"
        return "self"
    if slug in assigned:
        rec = assigned.get(slug) or {}
        job = str(rec.get("job_file") or "").lower()
        if job and job in names:
            return "assigned_inflight"
        return "already_assigned"
    hit = name_hit(slug, item.get("title", ""), names, dhx_fold)
    if hit:
        return f"inflight:{hit[:80]}"
    if tracked_names:
        th = _tracked_hit(item, tracked_names)
        if th:
            return f"tracked:{th[:80]}"
    return None


def backlog_skip_reason(item: dict, names: set[str], dhx_fold: str,
                        assigned: dict, orch_text: str) -> str | None:
    """Compat wrapper — BACKLOG.md uses the shared checkbox skip."""
    return checkbox_skip_reason(item, names, dhx_fold, assigned, orch_text)


def backlog_task(item: dict) -> str:
    slug = item["slug"]
    title = item["title"]
    body = item["body"]
    return (
        f"backlog_{slug} You are G46 (Grok Build) / Cursor, COSMOS backlog. "
        f"FIRST read docs/AGENT_BRIEF.md (DHx) and docs/BACKLOG.md. "
        f"Open item: {title}. {body} "
        f"Do NOT modify COSMOS core (kernel/ledger/sched/service). "
        f"Never delete; stage to _delme\\. No bats. "
        f"Bind every done claim to a real artifact (ledger event, file, API "
        f"response) — no fabricated compliance."
    )


def wishlist_task(item: dict) -> str:
    """A wish enters MOTIF at stage-1 research. Same prompt as motif_driver."""
    slug = item["slug"]
    line = item.get("line") or item["title"]
    row = {
        "name": item["title"],
        "slug": slug,
        "artifact": f"docs/research/{slug}/RESEARCH_1.md",
        "next_stage": "1 research (from docs/WISHLIST.md: %s)" % line,
        "current": "0",
    }
    return next_job_task(row, 1)


def route_drop_spec(rec: dict, rows: list[dict], loads: dict,
                    key_ok: bool) -> tuple[str, str, str]:
    """(task, agent, kind) for one flagged route item. Shared drop recipe."""
    enter = rec.get("enter")
    if rec.get("source") == "motif" or enter == "motif_s1":
        if rec.get("source") == "motif":
            tracker_row = next(r for r in rows if r["slug"] == rec["slug"])
            task = next_job_task(tracker_row, rec["next_stage"])
        else:
            task = wishlist_task(rec["item"])
        return task, "G46", "grok"
    item = rec["item"]
    agent, kind = pick_agent(item, loads, key_ok)
    return backlog_task(item), agent, kind


def annotate_checkbox(path: Path, item: dict, rec: dict, stamp: str) -> bool:
    """Once: append a WATCHDOG2 ASSIGNED marker on the checkbox line."""
    if not path.exists():
        return False
    original = path.read_text(encoding="utf-8")
    target = item.get("line") or ""
    if not target or target not in original:
        return False
    job = rec.get("job_file") or ""
    lane = rec.get("lane") or ""
    marker = f" · WATCHDOG2 ASSIGNED {stamp} {lane}/{job}"
    if "WATCHDOG2 ASSIGNED" in target:
        return False
    new_line = target.rstrip() + marker
    text = original.replace(target, new_line, 1)
    if text == original:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def annotate_backlog(path: Path, item: dict, rec: dict, stamp: str) -> bool:
    """Compat wrapper — BACKLOG.md uses the shared checkbox annotator."""
    return annotate_checkbox(path, item, rec, stamp)


def update_source_tick(path: Path, _stamp: str, _assigned: list[dict],
                       _flagged: list[dict], _skipped: list[dict]) -> None:
    """Strip a legacy tick footer from a route markdown.

    The pass record is the heartbeat: stamp, counts, jobs. Writing that
    footer into WISHLIST.md / BACKLOG.md dirties canon every 15s (BUCm
    not-list: do not commit Watchdog2 ticks). Checkbox ASSIGNED markers
    stay; those are annotate_checkbox, not this footer. The arguments
    are kept so the scan_once call site does not change.
    """
    if not path.exists():
        return
    original = path.read_text(encoding="utf-8")
    start = original.find(TICK_START)
    end = original.find(TICK_END)
    if start < 0 or end < start:
        return
    end = end + len(TICK_END)
    prefix = original[:start].rstrip("\n")
    suffix = original[end:].lstrip("\n")
    text = prefix + "\n"
    if suffix:
        text += "\n" + suffix
        if not text.endswith("\n"):
            text += "\n"
    if text != original:
        path.write_text(text, encoding="utf-8")


def update_backlog_tick(path: Path, stamp: str, assigned: list[dict],
                        flagged: list[dict], skipped: list[dict]) -> None:
    """Compat wrapper — BACKLOG.md uses the shared tick footer."""
    return update_source_tick(path, stamp, assigned, flagged, skipped)
