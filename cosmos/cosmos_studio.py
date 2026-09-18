#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_studio — MOTIF Studio pack for cDeck.

GET never mutates and never mkdir. POST writes state/studio/pack.json.
Does not start MOTIF. Does not hold API keys (via names the rail).
BUILD: artifact json/toml/sql, simultaneous builders, audited input text
(same for every parallel coder), N agents. CRITICS: any number of seats
plus consensus/continuation. IMPLEMENT (was IMPROVE): CCr applies once continuation is met.
Target is a local file, GitHub, GitLab, or cloud drive. GitHub/GitLab
runs through Gitur before any live-tree write. ITERATE: rounds / timer /
budget / bar. Execution is a later pass.

    py -3.14 cosmos\\\\cosmos_studio.py --selftest
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cosmos_model_rater import (  # noqa: E402
    VIA_OPTIONS,
    ModelRaterError,
    normalize_via,
)

SCHEMA = "cosmos-studio/1"
STUDIO_HITL_WAIT = "STUDIO_HITL_WAIT"
PACK_NAME = "pack.json"
MAX_RESEARCH = 12
MAX_DEFINE = 80_000
MAX_URLS = 24
MAX_PROPOSALS = 12
MAX_NOTE = 4_000
MAX_AGENTS = 24

ARTIFACTS = (
    ("json", "JSON"),
    ("toml", "TOML"),
    ("sql", "SQL"),
)
ARTIFACT_IDS = frozenset(a[0] for a in ARTIFACTS)
CONTINUE_WHEN = (
    ("bar", "Continue when the consensus bar is met"),
    ("hitl", "HITL — CCr continues"),
)
CONTINUE_IDS = frozenset(c[0] for c in CONTINUE_WHEN)
ITERATE_UNTIL = (
    ("rounds", "Stop after N rounds"),
    ("bar", "Stop when the consensus bar is met"),
    ("runtime_bind", "Stop when runtime-binding emits"),
    ("timed", "Stop when the timer elapses"),
    ("budget", "Stop when spend hits the cap"),
    ("keith", "Stop only when Keith says stop"),
)
ITERATE_UNTIL_IDS = frozenset(u[0] for u in ITERATE_UNTIL)

# Write destination for BUILD/IMPLEMENT. Distinct from RESEARCH look-targets.
DEST_KINDS = (
    ("local", "Local file"),
    ("github", "GitHub — Gitur before the live tree"),
    ("gitlab", "GitLab — Gitur before the live tree"),
    ("gdrive", "Cloud drive — Google Drive"),
    ("onedrive", "Cloud drive — OneDrive"),
)
DEST_IDS = frozenset(d[0] for d in DEST_KINDS)
GITUR_DESTS = frozenset({"github", "gitlab"})
GRAPH_KINDS = frozenset({"stage", "lane", "seat", "custom"})
MAX_GRAPH_NODES = 24
MAX_GRAPH_LABEL = 80
MOTIF_GRAPH = (
    ("define", 1, "PROBLEM / GOAL"),
    ("research", 2, "RESEARCH"),
    ("arch", 3, "ARCH"),
    ("consensus1", 4, "CONSENSUS"),
    ("build", 5, "BUILD"),
    ("critics", 6, "CRITICS"),
    ("consensus2", 7, "CONSENSUS"),
    ("improve", 8, "IMPLEMENT"),
    ("iterate", 9, "ITERATE"),
)


def dest_via_gitur(kind: str) -> bool:
    """GitHub/GitLab: Gitur first, then CCr may write the live tree."""
    return str(kind or "").strip().lower() in GITUR_DESTS


def default_graph() -> dict:
    """9 MOTIF stages on a 3-column board. Not a linear dump."""
    nodes = []
    for i, (sid, n, name) in enumerate(MOTIF_GRAPH):
        nodes.append({
            "id": sid,
            "kind": "stage",
            "n": n,
            "label": name,
            "x": (i % 3) * 200,
            "y": (i // 3) * 140,
        })
    return {"nodes": nodes, "saved_at": None}


def _public_graph(raw) -> dict:
    src = raw if isinstance(raw, dict) else {}
    nodes = []
    seen = set()
    incoming = src.get("nodes") if isinstance(src.get("nodes"), list) else []
    for i, row in enumerate(incoming):
        if not isinstance(row, dict):
            continue
        nid = str(row.get("id") or "").strip()[:40]
        kind = str(row.get("kind") or "custom").strip().lower()
        if kind not in GRAPH_KINDS:
            kind = "custom"
        if not nid:
            nid = "%s_%s" % (kind, i)
        if nid in seen:
            continue
        seen.add(nid)
        try:
            x = int(row.get("x") if row.get("x") not in (None, "") else 0)
        except (TypeError, ValueError):
            x = 0
        try:
            y = int(row.get("y") if row.get("y") not in (None, "") else 0)
        except (TypeError, ValueError):
            y = 0
        try:
            n = int(row["n"]) if row.get("n") not in (None, "") else None
        except (TypeError, ValueError):
            n = None
        nodes.append({
            "id": nid,
            "kind": kind,
            "n": n,
            "label": str(row.get("label") or nid)[:MAX_GRAPH_LABEL],
            "x": max(0, min(x, 4000)),
            "y": max(0, min(y, 4000)),
        })
        if len(nodes) >= MAX_GRAPH_NODES:
            break
    if not nodes:
        return default_graph()
    return {"nodes": nodes, "saved_at": src.get("saved_at")}

BARS = (
    ("plurality", "Plurality — the most votes wins"),
    ("majority", "Majority — more than half of the seats"),
    ("complete", "Complete — every seat agrees"),
)
BAR_IDS = frozenset(b[0] for b in BARS)
ARCH_CHOICES = (
    ("auto", "AUTO — pick by the consensus bar (default)"),
    ("hitl", "HITL — human chooses the architecture"),
)
ARCH_CHOICE_IDS = frozenset(c[0] for c in ARCH_CHOICES)

TARGETS = (
    ("github", "GitHub repos / libraries"),
    ("docs", "Company / product documentation sites"),
    ("reddit", "Forums (Reddit and similar)"),
    ("social", "Social media search"),
    ("uspto", "Patents / USPTO"),
    ("legal", "Legal (case law, statutes, filings)"),
    ("corporate", "Corporate (SEC, filings, investor)"),
    ("gov_federal", "Government — federal"),
    ("gov_state", "Government — state"),
    ("gov_local", "Government — local"),
)
TARGET_IDS = frozenset(t[0] for t in TARGETS)


class StudioError(RuntimeError):
    """kind in {BAD_INPUT, REFUSED, BROKE, HITL_BIND_FAILED}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _iso_now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def pack_path(paths) -> Path:
    return paths.state("studio", PACK_NAME)


def default_targets() -> dict:
    on = {"github", "docs", "reddit"}
    return {tid: (tid in on) for tid, _lab in TARGETS}


def default_consensus() -> dict:
    """AUTO by the bar is the default. HITL is the override to choose ARCH."""
    return {
        "bar": "majority",
        "arch_choice": "auto",
        "chosen_id": None,
        "note": "",
        "saved_at": None,
    }


def default_arch() -> dict:
    return {"proposals": []}


def default_build_agents() -> list[dict]:
    """MOTIF BUILD adversarial 1–5. Operator may add more."""
    return [
        {
            "id": "b_1",
            "label": "Adversarial coder 1",
            "model": "grok-4.6",
            "via": "cli:grok",
            "fallback_model": "grok-4.6",
            "fallback_via": "sgh-api",
            "fallback_model_2": "",
            "fallback_via_2": "",
        },
        {
            "id": "b_2",
            "label": "Adversarial coder 2",
            "model": "composer-2.5",
            "via": "cursor-api",
            "fallback_model": "grok-4.6",
            "fallback_via": "sgh-api",
            "fallback_model_2": "",
            "fallback_via_2": "",
        },
        {
            "id": "b_3",
            "label": "Adversarial coder 3",
            "model": "",
            "via": "openrouter-api",
            "fallback_model": "",
            "fallback_via": "openrouter-api",
            "fallback_model_2": "",
            "fallback_via_2": "",
        },
        {
            "id": "b_4",
            "label": "Adversarial coder 4",
            "model": "",
            "via": "openrouter-api",
            "fallback_model": "",
            "fallback_via": "openrouter-api",
            "fallback_model_2": "",
            "fallback_via_2": "",
        },
        {
            "id": "b_5",
            "label": "Adversarial coder 5",
            "model": "",
            "via": "openrouter-api",
            "fallback_model": "",
            "fallback_via": "openrouter-api",
            "fallback_model_2": "",
            "fallback_via_2": "",
        },
    ]


def default_critic_agents() -> list[dict]:
    return [
        {
            "id": "c_1",
            "label": "1 Plaintiff",
            "model": "",
            "via": "openrouter-api",
            "fallback_model": "",
            "fallback_via": "openrouter-api",
            "fallback_model_2": "",
            "fallback_via_2": "",
        },
        {
            "id": "c_2",
            "label": "2 Defense",
            "model": "",
            "via": "gem-api",
            "fallback_model": "",
            "fallback_via": "openrouter-api",
            "fallback_model_2": "",
            "fallback_via_2": "",
        },
        {
            "id": "c_3",
            "label": "3 Judge",
            "model": "",
            "via": "cli:grok",
            "fallback_model": "grok-4.6",
            "fallback_via": "sgh-api",
            "fallback_model_2": "",
            "fallback_via_2": "",
        },
        {
            "id": "c_4",
            "label": "4",
            "model": "",
            "via": "openrouter-api",
            "fallback_model": "",
            "fallback_via": "openrouter-api",
            "fallback_model_2": "",
            "fallback_via_2": "",
        },
        {
            "id": "c_5",
            "label": "5",
            "model": "",
            "via": "openrouter-api",
            "fallback_model": "",
            "fallback_via": "openrouter-api",
            "fallback_model_2": "",
            "fallback_via_2": "",
        },
    ]


def default_build() -> dict:
    return {
        "artifact": "json",
        "simultaneous": 2,
        "input_text": "",
        "agents": default_build_agents(),
        "saved_at": None,
    }


def default_critics() -> dict:
    return {
        "bar": "majority",
        "continue_when": "bar",
        "agents": default_critic_agents(),
        "saved_at": None,
    }


def default_dest() -> dict:
    """Default write target is GitHub, so Gitur runs before the live tree."""
    return {
        "kind": "github",
        "path": "",
        "via_gitur": True,
        "saved_at": None,
    }


def default_implement() -> dict:
    """IMPROVE, called IMPLEMENT for now. Gitur only when the target is GitHub/GitLab."""
    return {
        "via_gitur": True,
        "note": "",
        "saved_at": None,
    }


def default_iterate() -> dict:
    return {
        "max_rounds": 1,
        "timed_s": 0,
        "budget_usd": 0,
        "until": "rounds",
        "saved_at": None,
    }


def _clamp_int(raw, lo: int, hi: int, default: int) -> int:
    try:
        n = int(raw)
    except (TypeError, ValueError):
        return default
    if n < lo:
        return lo
    if n > hi:
        return hi
    return n


def _clamp_usd(raw) -> float:
    try:
        n = float(raw)
    except (TypeError, ValueError):
        return 0.0
    if n < 0:
        return 0.0
    if n > 1_000_000:
        return 1_000_000.0
    return n


def bar_met(winner: int, n: int, bar: str, second: int = 0) -> bool:
    """Whether a winning tally meets the named bar. A tie fails plurality.

    Does not pick an architecture. CONSENSUS later uses this; AUTO only
    fires when this is True, else CONTESTED (HITL).
    """
    b = str(bar or "").strip().lower()
    if b not in BAR_IDS:
        raise StudioError("BAD_INPUT", f"unknown consensus bar {bar!r}")
    try:
        win = int(winner)
        seats = int(n)
        nxt = int(second)
    except (TypeError, ValueError) as e:
        raise StudioError("BAD_INPUT", "vote counts must be integers") from e
    if seats <= 0 or win <= 0:
        return False
    if b == "complete":
        return win == seats
    if b == "majority":
        return win * 2 > seats
    return win > nxt


def default_research_models() -> list[dict]:
    """MOTIF RESEARCH search agents. SGH + GEM first.
    Perplexity is the optional search seat (step 2): GPT-5.6-Luna on DOM,
    OpenRouter API fallback. Vendor DeepSearchQA 2026-08-18 named that pair
    as the cheap search config — not a COSMOS-invented score."""
    return [
        {
            "id": "r_1",
            "label": "SGH",
            "model": "grok-4.6",
            "via": "cli:grok",
            "fallback_model": "grok-4.6",
            "fallback_via": "sgh-api",
            "fallback_model_2": "",
            "fallback_via_2": "",
        },
        {
            "id": "r_2",
            "label": "GEM",
            "model": "gemini-2.5-flash",
            "via": "gem-api",
            "fallback_model": "google/gemma-4-26b-a4b-it:free",
            "fallback_via": "openrouter-api",
            "fallback_model_2": "",
            "fallback_via_2": "",
        },
        {
            "id": "r_3",
            "label": "Perplexity (search, optional)",
            "model": "openai/gpt-5.6-luna",
            "via": "dom",
            "fallback_model": "openai/gpt-5.6-luna",
            "fallback_via": "openrouter-api",
            "fallback_model_2": "",
            "fallback_via_2": "",
            "optional": True,
            "note": (
                "Optional MOTIF RESEARCH search. OpenRouter DeepSearchQA "
                "(vendor page, last benchmark 2026-08-18): Perplexity + "
                "GPT-5.6-Luna 25-turn high ~73.2% / ~$0.03 per question. "
                "Not a COSMOS score. Winning vendor config was Parallel + "
                "Claude Opus 5 High 77% / $0.10 — not the COSMOS coding path "
                "(ANTHROPIC_OFF). DOM first; OpenRouter API fallback. Keith "
                "does credentials. Core does not fetch."
            ),
        },
        {
            "id": "r_4",
            "label": "Bing",
            "model": "",
            "via": "dom",
            "fallback_model": "",
            "fallback_via": "openrouter-api",
            "fallback_model_2": "",
            "fallback_via_2": "",
        },
        {
            "id": "r_5",
            "label": "ChatGPT",
            "model": "",
            "via": "dom",
            "fallback_model": "",
            "fallback_via": "openrouter-api",
            "fallback_model_2": "",
            "fallback_via_2": "",
        },
    ]


def empty_pack() -> dict:
    return {
        "schema": SCHEMA,
        "define": {"text": "", "saved_at": None},
        "research": {
            "models": default_research_models(),
            "targets": default_targets(),
            "extra_urls": [],
        },
        "arch": default_arch(),
        "consensus": default_consensus(),
        "build": default_build(),
        "critics": default_critics(),
        "dest": default_dest(),
        "implement": default_implement(),
        "iterate": default_iterate(),
        "graph": default_graph(),
        "updated_at": None,
        "available": False,
        "kind": "NO_SOURCE",
        "via_options": [dict(v) for v in VIA_OPTIONS],
        "target_catalog": [{"id": i, "label": lab} for i, lab in TARGETS],
        "bar_catalog": [{"id": i, "label": lab} for i, lab in BARS],
        "arch_choice_catalog": [{"id": i, "label": lab} for i, lab in ARCH_CHOICES],
        "artifact_catalog": [{"id": i, "label": lab} for i, lab in ARTIFACTS],
        "continue_catalog": [{"id": i, "label": lab} for i, lab in CONTINUE_WHEN],
        "iterate_until_catalog": [{"id": i, "label": lab} for i, lab in ITERATE_UNTIL],
        "dest_catalog": [{"id": i, "label": lab} for i, lab in DEST_KINDS],
    }


def _norm_via(raw) -> str:
    try:
        return normalize_via(raw)
    except ModelRaterError as e:
        raise StudioError(e.kind, str(e)[:300]) from e


def _public_model(raw: dict, idx: int, prefix: str = "r") -> dict:
    n = idx + 1
    via = _norm_via(raw.get("via"))
    fb_via = _norm_via(raw.get("fallback_via"))
    fb_via_2 = _norm_via(raw.get("fallback_via_2")) if raw.get("fallback_via_2") else ""
    oid = str(raw.get("id") or f"{prefix}_{n}").strip() or f"{prefix}_{n}"
    kind = {"r": "Research", "b": "Builder", "c": "Critic"}.get(prefix, "Seat")
    effort = str(raw.get("effort") or "").strip().lower()
    if effort not in ("", "low", "medium", "high", "max"):
        effort = ""
    cap = raw.get("budget_usd", raw.get("cap_usd"))
    try:
        cap_n = float(cap) if cap not in (None, "") else None
    except (TypeError, ValueError):
        cap_n = None
    if cap_n is not None and cap_n <= 0:
        cap_n = None
    return {
        "id": oid[:32],
        "label": str(raw.get("label") or f"{kind} {n}").strip()[:80],
        "model": str(raw.get("model") or "").strip()[:160],
        "via": via,
        "fallback_model": str(raw.get("fallback_model") or "").strip()[:160],
        "fallback_via": fb_via,
        "fallback_model_2": str(raw.get("fallback_model_2") or "").strip()[:160],
        "fallback_via_2": fb_via_2,
        "effort": effort,
        "budget_usd": cap_n,
        "optional": bool(raw.get("optional")),
        "note": str(raw.get("note") or "")[:400],
    }


def _public_agents(raw_list, prefix: str, defaults_fn, cap: int) -> list[dict]:
    rows = []
    for i, row in enumerate(raw_list or []):
        if not isinstance(row, dict):
            continue
        try:
            rows.append(_public_model(row, i, prefix))
        except StudioError:
            continue
        if len(rows) >= cap:
            break
    return rows or list(defaults_fn())


def _public_build(raw) -> dict:
    src = raw if isinstance(raw, dict) else {}
    base = default_build()
    art = str(src.get("artifact") or base["artifact"]).strip().lower().lstrip(".")
    if art not in ARTIFACT_IDS:
        raise StudioError("BAD_INPUT", f"unknown BUILD artifact {art!r}")
    agents = _public_agents(src.get("agents"), "b", default_build_agents, MAX_AGENTS)
    sim = _clamp_int(src.get("simultaneous"), 1, MAX_AGENTS, base["simultaneous"])
    if sim > len(agents):
        sim = len(agents) or 1
    text = str(src.get("input_text") or "")[:MAX_DEFINE]
    return {
        "artifact": art,
        "simultaneous": sim,
        "input_text": text,
        "agents": agents,
        "saved_at": src.get("saved_at"),
    }


def _public_critics(raw) -> dict:
    src = raw if isinstance(raw, dict) else {}
    base = default_critics()
    bar = str(src.get("bar") or base["bar"]).strip().lower()
    if bar not in BAR_IDS:
        raise StudioError("BAD_INPUT", f"unknown critics bar {bar!r}")
    cont = str(src.get("continue_when") or base["continue_when"]).strip().lower()
    if cont not in CONTINUE_IDS:
        raise StudioError("BAD_INPUT", f"unknown continue_when {cont!r}")
    return {
        "bar": bar,
        "continue_when": cont,
        "agents": _public_agents(src.get("agents"), "c",
                                 default_critic_agents, MAX_AGENTS),
        "saved_at": src.get("saved_at"),
    }


def _public_dest(raw) -> dict:
    src = raw if isinstance(raw, dict) else {}
    kind = str(src.get("kind") or "github").strip().lower()
    if kind not in DEST_IDS:
        raise StudioError("BAD_INPUT", f"unknown write target {kind!r}")
    return {
        "kind": kind,
        "path": str(src.get("path") or "").strip()[:400],
        "via_gitur": dest_via_gitur(kind),
        "saved_at": src.get("saved_at"),
    }


def _public_implement(raw, dest=None) -> dict:
    src = raw if isinstance(raw, dict) else {}
    kind = (dest or {}).get("kind") or "github"
    return {
        "via_gitur": dest_via_gitur(kind),
        "note": str(src.get("note") or "")[:MAX_NOTE],
        "saved_at": src.get("saved_at"),
    }


def _public_iterate(raw) -> dict:
    src = raw if isinstance(raw, dict) else {}
    base = default_iterate()
    until = str(src.get("until") or base["until"]).strip().lower()
    if until not in ITERATE_UNTIL_IDS:
        raise StudioError("BAD_INPUT", f"unknown iterate until {until!r}")
    return {
        "max_rounds": _clamp_int(src.get("max_rounds"), 0, 99, base["max_rounds"]),
        "timed_s": _clamp_int(src.get("timed_s"), 0, 86400, 0),
        "budget_usd": _clamp_usd(src.get("budget_usd")),
        "until": until,
        "saved_at": src.get("saved_at"),
    }


def _public_proposal(raw: dict, idx: int) -> dict:
    n = idx + 1
    oid = str(raw.get("id") or f"a_{n}").strip() or f"a_{n}"
    return {
        "id": oid[:32],
        "label": str(raw.get("label") or f"Architecture {n}").strip()[:120],
        "path": str(raw.get("path") or "").strip()[:400],
        "by": str(raw.get("by") or "").strip()[:80],
    }


def _public_arch(raw) -> dict:
    src = raw if isinstance(raw, dict) else {}
    proposals = []
    for i, row in enumerate(src.get("proposals") or []):
        if not isinstance(row, dict):
            continue
        proposals.append(_public_proposal(row, i))
        if len(proposals) >= MAX_PROPOSALS:
            break
    return {"proposals": proposals}


def _public_consensus(raw) -> dict:
    src = raw if isinstance(raw, dict) else {}
    base = default_consensus()
    bar = str(src.get("bar") or base["bar"]).strip().lower()
    if bar not in BAR_IDS:
        raise StudioError("BAD_INPUT", f"unknown consensus bar {bar!r}")
    choice = str(src.get("arch_choice") or base["arch_choice"]).strip().lower()
    if choice not in ARCH_CHOICE_IDS:
        raise StudioError("BAD_INPUT", f"unknown arch_choice {choice!r}")
    chosen = src.get("chosen_id")
    if chosen is None or chosen == "":
        chosen_id = None
    else:
        chosen_id = str(chosen).strip()[:32] or None
    if choice == "auto":
        chosen_id = None
    note = str(src.get("note") or "")[:MAX_NOTE]
    return {
        "bar": bar,
        "arch_choice": choice,
        "chosen_id": chosen_id,
        "note": note,
        "saved_at": src.get("saved_at"),
    }


def load_pack(paths) -> dict:
    """GET. Missing file is empty defaults, not a write."""
    p = pack_path(paths)
    base = empty_pack()
    if not p.is_file():
        return base
    try:
        rec = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        base["kind"] = "BROKE"
        return base
    if not isinstance(rec, dict):
        base["kind"] = "BROKE"
        return base
    define = rec.get("define") if isinstance(rec.get("define"), dict) else {}
    research = rec.get("research") if isinstance(rec.get("research"), dict) else {}
    models = []
    for i, row in enumerate(research.get("models") or []):
        if not isinstance(row, dict):
            continue
        try:
            models.append(_public_model(row, i))
        except StudioError:
            continue
        if len(models) >= MAX_RESEARCH:
            break
    if not models:
        models = default_research_models()
    else:
        # GET view only: empty Perplexity seat inherits the optional Luna pin.
        # Does not rewrite pack.json until SAVE RESEARCH.
        pin = {m["id"]: m for m in default_research_models()}.get("r_3") or {}
        for m in models:
            if m.get("id") == "r_3" and not m.get("model"):
                m["model"] = pin.get("model") or m.get("model")
                m["fallback_model"] = pin.get("fallback_model") or m.get("fallback_model")
                m["optional"] = True
                if not m.get("note"):
                    m["note"] = pin.get("note") or ""
    targets = default_targets()
    incoming = research.get("targets") if isinstance(research.get("targets"), dict) else {}
    for tid in TARGET_IDS:
        if tid in incoming:
            targets[tid] = bool(incoming[tid])
    urls = []
    for u in research.get("extra_urls") or []:
        s = str(u or "").strip()
        if s and s not in urls:
            urls.append(s[:400])
        if len(urls) >= MAX_URLS:
            break
    try:
        consensus = _public_consensus(rec.get("consensus"))
    except StudioError:
        consensus = default_consensus()
    arch = _public_arch(rec.get("arch"))
    try:
        build = _public_build(rec.get("build"))
    except StudioError:
        build = default_build()
    try:
        critics = _public_critics(rec.get("critics"))
    except StudioError:
        critics = default_critics()
    try:
        dest = _public_dest(rec.get("dest"))
    except StudioError:
        dest = default_dest()
    implement = _public_implement(rec.get("implement"), dest)
    try:
        iterate = _public_iterate(rec.get("iterate"))
    except StudioError:
        iterate = default_iterate()
    graph = _public_graph(rec.get("graph"))
    return {
        "schema": SCHEMA,
        "define": {
            "text": str(define.get("text") or "")[:MAX_DEFINE],
            "saved_at": define.get("saved_at"),
        },
        "research": {"models": models, "targets": targets, "extra_urls": urls},
        "arch": arch,
        "consensus": consensus,
        "build": build,
        "critics": critics,
        "dest": dest,
        "implement": implement,
        "iterate": iterate,
        "graph": graph,
        "updated_at": rec.get("updated_at"),
        "available": True,
        "kind": "OK",
        "via_options": [dict(v) for v in VIA_OPTIONS],
        "target_catalog": [{"id": i, "label": lab} for i, lab in TARGETS],
        "bar_catalog": [{"id": i, "label": lab} for i, lab in BARS],
        "arch_choice_catalog": [{"id": i, "label": lab} for i, lab in ARCH_CHOICES],
        "artifact_catalog": [{"id": i, "label": lab} for i, lab in ARTIFACTS],
        "continue_catalog": [{"id": i, "label": lab} for i, lab in CONTINUE_WHEN],
        "iterate_until_catalog": [{"id": i, "label": lab} for i, lab in ITERATE_UNTIL],
        "dest_catalog": [{"id": i, "label": lab} for i, lab in DEST_KINDS],
    }


def save_pack(paths, body: dict, ledger=None) -> dict:
    """POST. Merges onto current pack. Does not start MOTIF.

    An optional ``ledger`` (the service passes ``kernel.ledger``) appends
    one STUDIO_HITL_WAIT event per active HITL wait so the Review fold
    can bind the wait to a ledger seq (docs/arch/OSS_BORROW_ARCH.md
    ADAPT 1). Without a ledger the save stays hermetic — pack.json only,
    no ledger write, no event.
    """
    if not isinstance(body, dict):
        raise StudioError("BAD_INPUT", "body must be an object")
    cur = load_pack(paths)
    define = dict(cur["define"])
    research = {
        "models": list(cur["research"]["models"]),
        "targets": dict(cur["research"]["targets"]),
        "extra_urls": list(cur["research"]["extra_urls"]),
    }
    arch = _public_arch(cur.get("arch"))
    try:
        consensus = _public_consensus(cur.get("consensus"))
    except StudioError:
        consensus = default_consensus()
    try:
        build = _public_build(cur.get("build"))
    except StudioError:
        build = default_build()
    try:
        critics = _public_critics(cur.get("critics"))
    except StudioError:
        critics = default_critics()
    try:
        dest = _public_dest(cur.get("dest"))
    except StudioError:
        dest = default_dest()
    implement = _public_implement(cur.get("implement"), dest)
    try:
        iterate = _public_iterate(cur.get("iterate"))
    except StudioError:
        iterate = default_iterate()
    if "define" in body:
        d = body["define"]
        if isinstance(d, str):
            d = {"text": d}
        if not isinstance(d, dict):
            raise StudioError("BAD_INPUT", "define must be an object or string")
        text = str(d.get("text") if "text" in d else define.get("text") or "")
        if len(text) > MAX_DEFINE:
            raise StudioError("REFUSED", f"DEFINE longer than {MAX_DEFINE} chars")
        define["text"] = text
        define["saved_at"] = _iso_now()
    if "research" in body:
        r = body["research"]
        if not isinstance(r, dict):
            raise StudioError("BAD_INPUT", "research must be an object")
        if "models" in r:
            if not isinstance(r["models"], list):
                raise StudioError("BAD_INPUT", "research.models must be a list")
            if len(r["models"]) > MAX_RESEARCH:
                raise StudioError("REFUSED", f"at most {MAX_RESEARCH} research models")
            models = []
            for i, row in enumerate(r["models"]):
                if not isinstance(row, dict):
                    raise StudioError("BAD_INPUT", f"research.models[{i}] is not an object")
                models.append(_public_model(row, i))
            research["models"] = models or default_research_models()
        if "targets" in r:
            if not isinstance(r["targets"], dict):
                raise StudioError("BAD_INPUT", "research.targets must be an object")
            for tid, val in r["targets"].items():
                if tid not in TARGET_IDS:
                    raise StudioError("BAD_INPUT", f"unknown research target {tid!r}")
                research["targets"][tid] = bool(val)
        if "extra_urls" in r:
            if not isinstance(r["extra_urls"], list):
                raise StudioError("BAD_INPUT", "research.extra_urls must be a list")
            urls = []
            for u in r["extra_urls"]:
                s = str(u or "").strip()
                if s and s not in urls:
                    urls.append(s[:400])
                if len(urls) >= MAX_URLS:
                    break
            research["extra_urls"] = urls
    if "arch" in body:
        a = body["arch"]
        if not isinstance(a, dict):
            raise StudioError("BAD_INPUT", "arch must be an object")
        if "proposals" in a:
            if not isinstance(a["proposals"], list):
                raise StudioError("BAD_INPUT", "arch.proposals must be a list")
            if len(a["proposals"]) > MAX_PROPOSALS:
                raise StudioError("REFUSED", f"at most {MAX_PROPOSALS} architectures")
            props = []
            for i, row in enumerate(a["proposals"]):
                if not isinstance(row, dict):
                    raise StudioError("BAD_INPUT", f"arch.proposals[{i}] is not an object")
                props.append(_public_proposal(row, i))
            arch["proposals"] = props
    if "consensus" in body:
        c = body["consensus"]
        if not isinstance(c, dict):
            raise StudioError("BAD_INPUT", "consensus must be an object")
        merged = dict(consensus)
        merged.update(c)
        consensus = _public_consensus(merged)
        consensus["saved_at"] = _iso_now()
    if "build" in body:
        b = body["build"]
        if not isinstance(b, dict):
            raise StudioError("BAD_INPUT", "build must be an object")
        merged = dict(build)
        merged.update(b)
        if "agents" in b:
            if not isinstance(b["agents"], list):
                raise StudioError("BAD_INPUT", "build.agents must be a list")
            if len(b["agents"]) > MAX_AGENTS:
                raise StudioError("REFUSED", f"at most {MAX_AGENTS} builders")
            agents = []
            for i, row in enumerate(b["agents"]):
                if not isinstance(row, dict):
                    raise StudioError("BAD_INPUT", f"build.agents[{i}] is not an object")
                agents.append(_public_model(row, i, "b"))
            merged["agents"] = agents or default_build_agents()
        build = _public_build(merged)
        build["saved_at"] = _iso_now()
    if "critics" in body:
        k = body["critics"]
        if not isinstance(k, dict):
            raise StudioError("BAD_INPUT", "critics must be an object")
        merged = dict(critics)
        merged.update(k)
        if "agents" in k:
            if not isinstance(k["agents"], list):
                raise StudioError("BAD_INPUT", "critics.agents must be a list")
            if len(k["agents"]) > MAX_AGENTS:
                raise StudioError("REFUSED", f"at most {MAX_AGENTS} critics")
            agents = []
            for i, row in enumerate(k["agents"]):
                if not isinstance(row, dict):
                    raise StudioError("BAD_INPUT", f"critics.agents[{i}] is not an object")
                agents.append(_public_model(row, i, "c"))
            merged["agents"] = agents or default_critic_agents()
        critics = _public_critics(merged)
        critics["saved_at"] = _iso_now()
    if "dest" in body:
        d = body["dest"]
        if not isinstance(d, dict):
            raise StudioError("BAD_INPUT", "dest must be an object")
        merged = dict(dest)
        merged.update(d)
        dest = _public_dest(merged)
        dest["saved_at"] = _iso_now()
    if "implement" in body:
        im = body["implement"]
        if not isinstance(im, dict):
            raise StudioError("BAD_INPUT", "implement must be an object")
        merged = dict(implement)
        merged.update(im)
        implement = _public_implement(merged, dest)
        implement["saved_at"] = _iso_now()
    else:
        implement = _public_implement(implement, dest)
    if "iterate" in body:
        it = body["iterate"]
        if not isinstance(it, dict):
            raise StudioError("BAD_INPUT", "iterate must be an object")
        merged = dict(iterate)
        merged.update(it)
        iterate = _public_iterate(merged)
        iterate["saved_at"] = _iso_now()
    graph = _public_graph(cur.get("graph"))
    if "graph" in body:
        g = body["graph"]
        if not isinstance(g, dict):
            raise StudioError("BAD_INPUT", "graph must be an object")
        graph = _public_graph(g)
        graph["saved_at"] = _iso_now()
    rec = {
        "schema": SCHEMA,
        "define": define,
        "research": research,
        "arch": arch,
        "consensus": consensus,
        "build": build,
        "critics": critics,
        "dest": dest,
        "implement": implement,
        "iterate": iterate,
        "graph": graph,
        "updated_at": _iso_now(),
        "available": True,
        "kind": "OK",
    }
    p = pack_path(paths)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    tmp.replace(p)
    out = load_pack(paths)
    out["measured_at"] = time.time()
    # Wait is not done until the ledger names it. Pack has already landed
    # (a failed save never gets an event). POST only; GET never appends.
    if ledger is not None:
        try:
            for wait in hitl_waits(out):
                ledger.append(STUDIO_HITL_WAIT, {
                    "schema": SCHEMA,
                    "id": wait["id"],
                    "why": wait["why"],
                    "saved_at": rec.get("updated_at"),
                })
        except Exception as e:  # noqa: BLE001
            raise StudioError(
                "HITL_BIND_FAILED",
                f"pack saved but the ledger did not name the HITL wait "
                f"({type(e).__name__}: {e}) — re-save to bind; the wait "
                f"refuses in Review until then") from e
    return out


def hitl_waits(pack: dict) -> list[dict]:
    """Active HITL waits in a studio pack (OSS_BORROW ADAPT 1).

    One definition shared by the writer (save_pack appends one
    STUDIO_HITL_WAIT per wait) and the Review fold (bind or refuse). A
    wait is studio config that parks the MOTIF route on a human; Review
    must not paint it green until a ledger event names it (P04).
    """
    src = pack if isinstance(pack, dict) else {}
    cons = src.get("consensus") if isinstance(src.get("consensus"), dict) else {}
    critics = src.get("critics") if isinstance(src.get("critics"), dict) else {}
    waits = []
    if cons.get("arch_choice") == "hitl" and not cons.get("chosen_id"):
        waits.append({"id": "consensus.arch",
                     "why": "CONSENSUS HITL — architecture not chosen"})
    if critics.get("continue_when") == "hitl":
        waits.append({"id": "critics.continue",
                     "why": "CRITICS continuation is HITL — CCr continues"})
    return waits


def snapshot(paths) -> dict:
    rec = load_pack(paths)
    rec["measured_at"] = time.time()
    rec.setdefault("via_options", [dict(v) for v in VIA_OPTIONS])
    rec.setdefault("target_catalog", [{"id": i, "label": lab} for i, lab in TARGETS])
    rec.setdefault("bar_catalog", [{"id": i, "label": lab} for i, lab in BARS])
    rec.setdefault("arch_choice_catalog",
                   [{"id": i, "label": lab} for i, lab in ARCH_CHOICES])
    rec.setdefault("artifact_catalog", [{"id": i, "label": lab} for i, lab in ARTIFACTS])
    rec.setdefault("continue_catalog", [{"id": i, "label": lab} for i, lab in CONTINUE_WHEN])
    rec.setdefault("iterate_until_catalog",
                   [{"id": i, "label": lab} for i, lab in ITERATE_UNTIL])
    rec.setdefault("dest_catalog", [{"id": i, "label": lab} for i, lab in DEST_KINDS])
    rec["note"] = (
        "DEFINE is the frozen prompt. RESEARCH / BUILD / CRITICS are config. "
        "Write target is a local file, GitHub, GitLab, or cloud drive. "
        "GitHub/GitLab runs through Gitur before any live-tree write. "
        "IMPLEMENT is CCr apply once continuation is met. "
        "This POST does not start MOTIF. Keys stay on the named via. "
        "graph is the Profile Studio board (drag/drop MOTIF nodes). "
        "Does not invent an occupancy profile id."
    )
    return rec


def _selftest() -> int:
    import tempfile

    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    td = Path(tempfile.mkdtemp(prefix="cosmos_studio_"))
    root = install(td / "live", tree_id="spike-studio")
    paths = CosmosPaths(root)
    empty = load_pack(paths)
    check("GET missing pack is NO_SOURCE and does not mkdir",
          lambda: empty.get("kind") == "NO_SOURCE"
          and not pack_path(paths).exists())
    check("GET missing pack still names vias and research targets",
          lambda: any(v.get("id") == "cli:grok" for v in (empty.get("via_options") or []))
          and any(t.get("id") == "uspto" for t in (empty.get("target_catalog") or []))
          and any(t.get("id") == "gov_local" for t in (empty.get("target_catalog") or [])))
    ppl = [m for m in (empty.get("research") or {}).get("models") or []
           if m.get("id") == "r_3"]
    check("Perplexity RESEARCH seat is optional search + GPT-5.6-Luna",
          lambda: ppl and ppl[0].get("optional") is True
          and ppl[0].get("model") == "openai/gpt-5.6-luna"
          and ppl[0].get("via") == "dom"
          and ppl[0].get("fallback_via") == "openrouter-api")
    saved = save_pack(paths, {"define": {"text": "WHAT: pane. WHY: live."}})
    check("POST DEFINE persists verbatim",
          lambda: saved["define"]["text"] == "WHAT: pane. WHY: live."
          and saved["define"]["saved_at"]
          and pack_path(paths).is_file())
    again = load_pack(paths)
    check("GET after POST returns the same DEFINE",
          lambda: again["define"]["text"] == "WHAT: pane. WHY: live.")
    res = save_pack(paths, {"research": {
        "models": [{
            "label": "OpenRouter free",
            "model": "google/gemma-4-26b-a4b-it:free",
            "via": "openrouter-api",
            "fallback_model": "grok-4.6",
            "fallback_via": "cli:grok",
        }],
        "targets": {"uspto": True, "github": False},
        "extra_urls": ["https://docs.example"],
    }})
    m = (res["research"]["models"] or [None])[0]
    check("research model stores via + fallback, not a key",
          lambda: m and m["via"] == "openrouter-api"
          and m["fallback_via"] == "cli:grok"
          and m["fallback_model"] == "grok-4.6"
          and m.get("fallback_model_2") == ""
          and "api_key" not in m)
    check("targets accept USPTO and GitHub off",
          lambda: res["research"]["targets"].get("uspto") is True
          and res["research"]["targets"].get("github") is False
          and res["research"]["extra_urls"] == ["https://docs.example"])
    bad = False
    try:
        save_pack(paths, {"research": {"targets": {"mars": True}}})
    except StudioError as e:
        bad = e.kind == "BAD_INPUT"
    check("unknown research target is BAD_INPUT", lambda: bad)
    rotator = False
    try:
        save_pack(paths, {"research": {"models": [{"via": "openrouter/free"}]}})
    except StudioError as e:
        rotator = e.kind == "BAD_INPUT"
    check("rotator is not a research via", lambda: rotator)
    check("AUTO + majority is the default consensus",
          lambda: empty["consensus"]["bar"] == "majority"
          and empty["consensus"]["arch_choice"] == "auto"
          and empty["consensus"]["chosen_id"] is None)
    check("plurality 2>1 meets the bar; 1=1 does not",
          lambda: bar_met(2, 3, "plurality", 1) is True
          and bar_met(1, 2, "plurality", 1) is False)
    check("majority needs more than half; complete needs all",
          lambda: bar_met(2, 3, "majority") is True
          and bar_met(1, 3, "majority") is False
          and bar_met(2, 3, "complete") is False
          and bar_met(3, 3, "complete") is True)
    hitl = save_pack(paths, {
        "arch": {"proposals": [
            {"id": "a_sgh", "label": "DOM-first rails", "by": "SGH"},
            {"id": "a_gem", "label": "API-first", "by": "GEM"},
        ]},
        "consensus": {
            "bar": "plurality",
            "arch_choice": "hitl",
            "chosen_id": "a_sgh",
            "note": "Keith picks the DOM-first arch.",
        },
    })
    check("HITL chooses architecture; bar is plurality",
          lambda: hitl["consensus"]["bar"] == "plurality"
          and hitl["consensus"]["arch_choice"] == "hitl"
          and hitl["consensus"]["chosen_id"] == "a_sgh"
          and hitl["arch"]["proposals"][0]["id"] == "a_sgh")
    auto = save_pack(paths, {"consensus": {"arch_choice": "auto", "chosen_id": "a_sgh"}})
    check("AUTO clears a HITL pick — the bar decides later",
          lambda: auto["consensus"]["arch_choice"] == "auto"
          and auto["consensus"]["chosen_id"] is None)
    keep = save_pack(paths, {"define": {"text": "still the same DEFINE"}})
    check("DEFINE save preserves consensus bar",
          lambda: keep["consensus"]["bar"] == "plurality"
          and keep["define"]["text"] == "still the same DEFINE")
    bad_bar = False
    try:
        save_pack(paths, {"consensus": {"bar": "unanimous"}})
    except StudioError as e:
        bad_bar = e.kind == "BAD_INPUT"
    check("unknown consensus bar is BAD_INPUT (complete, not unanimous)",
          lambda: bad_bar)
    bld = save_pack(paths, {"build": {
        "artifact": "toml",
        "simultaneous": 3,
        "input_text": "WHAT: pane. audited.",
        "agents": [
            {"label": "A", "model": "grok-4.6", "via": "cli:grok"},
            {"label": "B", "model": "claude-opus-5", "via": "cursor-api"},
            {"label": "C", "model": "gemini-2.5-flash", "via": "gem-api"},
        ],
    }})
    check("BUILD artifact toml, 3 simultaneous, audited input shared",
          lambda: bld["build"]["artifact"] == "toml"
          and bld["build"]["simultaneous"] == 3
          and bld["build"]["input_text"] == "WHAT: pane. audited."
          and len(bld["build"]["agents"]) == 3
          and "api_key" not in bld["build"]["agents"][0])
    bad_art = False
    try:
        save_pack(paths, {"build": {"artifact": "xml"}})
    except StudioError as e:
        bad_art = e.kind == "BAD_INPUT"
    check("unknown BUILD artifact is BAD_INPUT (json/toml/sql)", lambda: bad_art)
    dotted = save_pack(paths, {"build": {"artifact": ".json"}})
    check(".json normalizes to json",
          lambda: dotted["build"]["artifact"] == "json")
    cri = save_pack(paths, {"critics": {
        "bar": "complete",
        "continue_when": "hitl",
        "agents": [
            {"label": "Opus", "model": "claude-opus-5", "via": "cursor-api"},
        ],
    }})
    check("CRITICS any number + HITL continuation",
          lambda: cri["critics"]["bar"] == "complete"
          and cri["critics"]["continue_when"] == "hitl"
          and len(cri["critics"]["agents"]) == 1)
    gh = save_pack(paths, {"dest": {
        "kind": "github", "path": "keithbbf-gif/cdeck",
    }})
    check("GitHub target runs Gitur before the live tree",
          lambda: gh["dest"]["kind"] == "github"
          and gh["dest"]["via_gitur"] is True
          and gh["implement"]["via_gitur"] is True
          and gh["dest"]["path"] == "keithbbf-gif/cdeck")
    loc = save_pack(paths, {"dest": {
        "kind": "local", "path": "docs/arch/FOO.md",
    }})
    check("local file target does not go through Gitur",
          lambda: loc["dest"]["kind"] == "local"
          and loc["dest"]["via_gitur"] is False
          and loc["implement"]["via_gitur"] is False)
    cloud = save_pack(paths, {"dest": {"kind": "gdrive", "path": "GDX/studio"}})
    check("cloud drive target does not go through Gitur",
          lambda: cloud["dest"]["kind"] == "gdrive"
          and cloud["dest"]["via_gitur"] is False)
    forced = save_pack(paths, {
        "dest": {"kind": "local"},
        "implement": {"via_gitur": True, "note": "cannot force Gitur"},
    })
    check("via_gitur is derived from dest, not a free checkbox",
          lambda: forced["implement"]["via_gitur"] is False
          and forced["implement"]["note"] == "cannot force Gitur")
    bad_dest = False
    try:
        save_pack(paths, {"dest": {"kind": "s3"}})
    except StudioError as e:
        bad_dest = e.kind == "BAD_INPUT"
    check("unknown write target is BAD_INPUT", lambda: bad_dest)
    imp = save_pack(paths, {"dest": {"kind": "github"}, "implement": {
        "note": "apply via Gitur",
    }})
    check("IMPLEMENT on GitHub is Gitur then live tree, not auto-MOTIF",
          lambda: imp["implement"]["via_gitur"] is True
          and imp["implement"]["note"] == "apply via Gitur")
    it = save_pack(paths, {"iterate": {
        "max_rounds": 4, "timed_s": 3600, "budget_usd": 12.5,
        "until": "budget",
    }})
    check("ITERATE rounds / timer / budget",
          lambda: it["iterate"]["max_rounds"] == 4
          and it["iterate"]["timed_s"] == 3600
          and it["iterate"]["budget_usd"] == 12.5
          and it["iterate"]["until"] == "budget")
    check("defaults: BUILD json dual-lane, GitHub dest via Gitur, ITERATE 1 round",
          lambda: empty["build"]["artifact"] == "json"
          and empty["build"]["simultaneous"] == 2
          and empty["dest"]["kind"] == "github"
          and empty["dest"]["via_gitur"] is True
          and empty["iterate"]["until"] == "rounds"
          and empty["iterate"]["max_rounds"] == 1)
    check("GET missing pack still names a 9-node MOTIF graph",
          lambda: len((empty.get("graph") or {}).get("nodes") or []) == 9
          and (empty["graph"]["nodes"][0]["id"] == "define"))
    g = save_pack(paths, {"graph": {"nodes": [
        {"id": "define", "kind": "stage", "n": 1, "label": "PROBLEM / GOAL",
         "x": 16, "y": 32},
        {"id": "lane_a", "kind": "lane", "label": "Lane A", "x": 216, "y": 32},
    ]}})
    check("POST graph persists positions; does not start MOTIF",
          lambda: g["graph"]["nodes"][0]["x"] == 16
          and g["graph"]["nodes"][1]["kind"] == "lane"
          and g["graph"]["saved_at"])
    again_g = load_pack(paths)
    check("GET after POST graph returns the same board",
          lambda: again_g["graph"]["nodes"][0]["x"] == 16
          and again_g["graph"]["nodes"][1]["id"] == "lane_a")

    from cosmos_ledger import Ledger
    led = Ledger(paths.ledger("authority.jsonl"),
                 (root / "config" / "install_key.bin").read_bytes(),
                 "studio-selftest")
    save_pack(paths, {"consensus": {"arch_choice": "hitl"},
                      "critics": {"continue_when": "hitl"}}, ledger=led)
    waits_ev = [r for r in led.verify()
                if r.get("event") == STUDIO_HITL_WAIT]
    check("save_pack with a ledger appends one STUDIO_HITL_WAIT per active wait",
          lambda: [r["payload"].get("id") for r in waits_ev]
          == ["consensus.arch", "critics.continue"]
          and all(isinstance(r.get("seq"), int) for r in waits_ev))
    cleared = save_pack(paths, {"consensus": {"arch_choice": "auto"},
                                "critics": {"continue_when": "bar"}},
                        ledger=led)
    waits_after = [r for r in led.verify()
                   if r.get("event") == STUDIO_HITL_WAIT]
    check("a save with no active wait appends no STUDIO_HITL_WAIT",
          lambda: hitl_waits(cleared) == [] and len(waits_after) == 2)

    bad_out = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (Studio BUILD/CRITICS/IMPLEMENT/ITERATE pack)"
          % ("PASS" if not bad_out else "FAIL", len(results)))
    return 0 if not bad_out else 1


if __name__ == "__main__":
    raise SystemExit(_selftest())
