#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_model_rater — catalog + seats + observed porosity for cDeck.

Pulls GET /api/v1/models (rates, modalities, Artificial Analysis indices)
into a local projection. Daily refresh or refresh-on-open. Does NOT call
the rotating openrouter/free router (H3). Seat assign is explicit.

Unique join (Keith 2026-09-09, Margie Irbe): vendor INT/COD/AGT are
guidelines. Occupancy is **observed** pair holes (GET /api/v1/porosity)
plus an audit stamp on every observation — agent_id key, action,
timestamp at the key point, authority source:class. A score without
stamps is not an audit trail. Canon: docs/AGENT_AUDIT.md.

Quality axes (vendor-measured, else UNMEASURED — never invented):
  intelligence, coding, agentic  (OpenRouter GET /benchmarks
  source=artificial-analysis, plus any indices already on GET /models).
  Q is the mean of the axes that exist. Sortable across INT / COD / AGT / Q.
Price: USD per 1M prompt/completion tokens (API is per-token).
Type: coding | reasoning | images | audio | video | chat

Seats (prestaged profiles): MOTIF dual-lane, Crucible roles, dispatch.
Cost estimate = tokens_in * prompt + tokens_out * completion (+ request).

    py -3.14 cosmos\\cosmos_model_rater.py --selftest
    py -3.14 cosmos\\cosmos_model_rater.py --root V:\\A\\Ai\\COSMOS\\live --refresh
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

SCHEMA = "cosmos-model-rater/3"
WORKER = "cosmos-model-rater"
TTL_S = 24 * 3600
CATALOG_NAME = "catalog.json"
SEATS_NAME = "seats.json"
POROSITY_NAME = "porosity.json"
BLEND_IN = 0.75
BLEND_OUT = 0.25
ROTATING = frozenset({
    "openrouter/free", "openrouter/auto", "openrouter/free:free",
    "openrouter/pareto-code",
})
# CCr initial for a MOTIF BUILD work-order: ~canon+files+brief in, patch out.
# Override on the Forge pane if the job is a one-file fix or a full-tree rewrite.
CCR_INITIAL_IN = 24000
CCR_INITIAL_OUT = 8000
JOB_EST_NAME = "job_estimate.json"
MAX_ADV = 24
# Occupancy: this TUI is Grok 4.6 CCr (Keith 2026-09-04). Not an OpenRouter
# pin — the rate card may be UNMEASURED. Empty model painted as "unassigned".
CCR_MODEL = "grok-4.6"
# How a seat is called. API link_ids match Kernel rails; cli:* is a binary;
# dom is the browser path. Occupancy: one CCr writer. Via is the hand, not a
# second Core.
VIA_OPTIONS = (
    {"id": "cli:grok", "label": "CLI · grok", "kind": "CLI"},
    {"id": "cli:gemini", "label": "CLI · gemini", "kind": "CLI"},
    {"id": "cli:codex", "label": "CLI · Codex", "kind": "CLI"},
    {"id": "cli:hermes", "label": "CLI · Hermes", "kind": "CLI"},
    {"id": "openrouter-api", "label": "API · OpenRouter (incl. :free)", "kind": "API"},
    {"id": "groq-api", "label": "API · GroqCloud", "kind": "API"},
    {"id": "gem-free", "label": "API · AI Studio Free", "kind": "API"},
    {"id": "gem-api", "label": "API · Vertex Joanna", "kind": "API"},
    {"id": "vertex-coding", "label": "API · Vertex $300", "kind": "API"},
    {"id": "oa-api", "label": "API · OpenAI", "kind": "API"},
    {"id": "sgh-api", "label": "API · xAI console", "kind": "API"},
    {"id": "cursor-api", "label": "API · Cursor", "kind": "API"},
    {"id": "dom", "label": "DOM · browser", "kind": "DOM"},
    {"id": "mcp", "label": "MCP · named server", "kind": "MCP"},
    {"id": "mcp:openwork", "label": "MCP · OpenWork", "kind": "MCP"},
    {"id": "mcp:github", "label": "MCP · GitHub", "kind": "MCP"},
    {"id": "mcp:bts", "label": "MCP · BTS", "kind": "MCP"},
)
VIA_IDS = frozenset(v["id"] for v in VIA_OPTIONS)
EFFORT_IDS = frozenset({"", "low", "medium", "high", "max"})
DEFAULT_SEATS = (
    {"profile": "openwork", "seat": "orc", "group": "OpenWork",
     "label": "OpenWork — ORC", "model": "", "via": "mcp:openwork",
     "locked": True},
    {"profile": "openwork", "seat": "gem_studio", "group": "OpenWork",
     "label": "OpenWork — AI Studio Free", "model": "gemini-2.5-flash",
     "via": "gem-free", "locked": True},
    {"profile": "forge", "seat": "ccr", "group": "Forge",
     "label": "CCr — Chief Coder", "model": CCR_MODEL, "via": "cli:grok",
     "locked": True},
    {"profile": "forge", "seat": "adv_1", "group": "Forge",
     "label": "Forge — Adversarial coder 1", "model": "", "via": "openrouter-api"},
    {"profile": "forge", "seat": "adv_2", "group": "Forge",
     "label": "Forge — Adversarial coder 2", "model": "", "via": "openrouter-api"},
    {"profile": "motif", "seat": "research_sgh", "group": "MOTIF RESEARCH",
     "label": "MOTIF RESEARCH — SGH (search)", "model": CCR_MODEL,
     "via": "cli:grok", "locked": True},
    {"profile": "motif", "seat": "research_gem", "group": "MOTIF RESEARCH",
     "label": "MOTIF RESEARCH — GEM (search)", "model": "gemini-2.5-flash",
     "via": "gem-api", "locked": True},
    {"profile": "motif", "seat": "research_pplx", "group": "MOTIF RESEARCH",
     "label": "MOTIF RESEARCH — Perplexity (search)", "model": "",
     "via": "dom", "locked": True},
    {"profile": "motif", "seat": "research_bing", "group": "MOTIF RESEARCH",
     "label": "MOTIF RESEARCH — Bing (search)", "model": "",
     "via": "dom", "locked": True},
    {"profile": "motif", "seat": "research_chatgpt", "group": "MOTIF RESEARCH",
     "label": "MOTIF RESEARCH — ChatGPT (search)", "model": "",
     "via": "dom", "locked": True},
    {"profile": "motif", "seat": "lane_a", "group": "MOTIF BUILD",
     "label": "MOTIF BUILD — Adversarial coder 1", "model": CCR_MODEL,
     "via": "cli:grok", "locked": True},
    {"profile": "motif", "seat": "lane_b", "group": "MOTIF BUILD",
     "label": "MOTIF BUILD — Adversarial coder 2", "model": "grok-4.6",
     "via": "cursor-api", "locked": True},
    {"profile": "motif", "seat": "build_3", "group": "MOTIF BUILD",
     "label": "MOTIF BUILD — Adversarial coder 3", "model": "",
     "via": "openrouter-api", "locked": True},
    {"profile": "motif", "seat": "build_4", "group": "MOTIF BUILD",
     "label": "MOTIF BUILD — Adversarial coder 4", "model": "",
     "via": "openrouter-api", "locked": True},
    {"profile": "motif", "seat": "build_5", "group": "MOTIF BUILD",
     "label": "MOTIF BUILD — Adversarial coder 5", "model": "",
     "via": "openrouter-api", "locked": True},
    {"profile": "motif", "seat": "critic_plaintiff", "group": "MOTIF CRITICS",
     "label": "MOTIF CRITICS — 1 Plaintiff", "model": "", "via": "openrouter-api",
     "locked": True},
    {"profile": "motif", "seat": "critic_defense", "group": "MOTIF CRITICS",
     "label": "MOTIF CRITICS — 2 Defense", "model": "", "via": "gem-api",
     "locked": True},
    {"profile": "motif", "seat": "critic_judge", "group": "MOTIF CRITICS",
     "label": "MOTIF CRITICS — 3 Judge", "model": CCR_MODEL, "via": "cli:grok",
     "locked": True},
    {"profile": "motif", "seat": "critic_4", "group": "MOTIF CRITICS",
     "label": "MOTIF CRITICS — 4", "model": "", "via": "openrouter-api",
     "locked": True},
    {"profile": "motif", "seat": "critic_5", "group": "MOTIF CRITICS",
     "label": "MOTIF CRITICS — 5", "model": "", "via": "openrouter-api",
     "locked": True},
    {"profile": "crucible", "seat": "plaintiff", "group": "Crucible",
     "label": "Crucible — Plaintiff's attorney", "model": "", "locked": True},
    {"profile": "crucible", "seat": "defense", "group": "Crucible",
     "label": "Crucible — Defendant's counsel", "model": "", "locked": True},
    {"profile": "crucible", "seat": "judge", "group": "Crucible",
     "label": "Crucible — Judge", "model": "", "locked": True},
    {"profile": "dispatch", "seat": "coding", "group": "Dispatch",
     "label": "Dispatch — coding", "model": "", "locked": True},
    {"profile": "dispatch", "seat": "ssa", "group": "Dispatch",
     "label": "Dispatch — cheap reasoning / SSA", "model": "", "locked": True},
)
LOCKED_SEATS = frozenset(
    (d["profile"], d["seat"]) for d in DEFAULT_SEATS if d.get("locked")
)
SORT_KEYS = frozenset({
    "price", "blended", "intelligence", "coding", "agentic", "quality", "q",
    "intelligence_per_cost", "coding_per_cost", "agentic_per_cost",
    "quality_per_cost", "porosity",
    "reasoning", "speed", "stability", "office", "file",
    "popularity", "recency", "created", "latency", "math",
    "gpqa", "hle", "ifbench", "tau2", "lcr", "gdpval", "critpt",
    "scicode", "terminal_bench", "omniscience", "omniscience_nh",
    "name", "context", "id",
})
QUALITY_AXES = ("intelligence", "coding", "agentic")
RATIO_AXES = ("intelligence", "coding", "agentic", "quality")
EXTRA_AXES = ("speed", "math", "office", "file", "stability",
              "popularity", "latency", "reasoning",
              "gpqa", "hle", "ifbench", "tau2", "lcr", "gdpval", "critpt",
              "scicode", "terminal_bench", "omniscience", "omniscience_nh")
TYPE_KEYS = frozenset({
    "coding", "reasoning", "images", "audio", "video", "chat", "free", "docs",
})
# OpenRouter models page cut Keith named 2026-09-07:
# text out, text+file+image in (cards). Not a rotator.
DOCS_CUT = {
    "id": "docs",
    "label": "text out · text/file/image in",
    "url": (
        "https://openrouter.ai/models?fmt=cards"
        "&output_modalities=text&input_modalities=text,file,image"
    ),
    "fmt": "cards",
    "output_modalities": ("text",),
    "input_modalities": ("text", "file", "image"),
}
# OpenRouter models TABLE (Keith screenshot): Programming + Text, Newest.
# Columns: Weekly Tokens, Input, Output, Context, Latency, Throughput, Released.
OR_CATEGORIES = (
    "programming", "roleplay", "marketing", "marketing/seo", "technology",
    "science", "translation", "legal", "finance", "health", "trivia",
    "academia",
)
TABLE_CUT = {
    "id": "table",
    "label": "table · programming · text out · newest",
    "url": (
        "https://openrouter.ai/models?fmt=table"
        "&output_modalities=text&category=programming"
    ),
    "fmt": "table",
    "output_modalities": ("text",),
    "category": "programming",
    "sort": "newest",
}
# Vendor field → column. Copy only when present. Never invent a number.
AA_FIELD_MAP = (
    ("intelligence_index", "intelligence"),
    ("coding_index", "coding"),
    ("agentic_index", "agentic"),
    ("math_index", "math"),
    ("reasoning_index", "reasoning"),
    ("output_speed", "speed"),
    ("speed_index", "speed"),
    ("tokens_per_second", "speed"),
    ("latency", "latency"),
    ("time_to_first_token", "latency"),
    ("office_index", "office"),
    ("file_index", "file"),
    ("pdf_index", "file"),
    ("stability_index", "stability"),
    ("endpoint_accuracy", "stability"),
    ("gpqa_diamond", "gpqa"),
    ("gpqa", "gpqa"),
    ("hle", "hle"),
    ("humanity_last_exam", "hle"),
    ("ifbench", "ifbench"),
    ("tau2_bench_telecom", "tau2"),
    ("tau2_telecom", "tau2"),
    ("aa_lcr", "lcr"),
    ("lcr", "lcr"),
    ("gdpval_aa", "gdpval"),
    ("gdpval", "gdpval"),
    ("critpt", "critpt"),
    ("scicode", "scicode"),
    ("terminal_bench_hard", "terminal_bench"),
    ("terminal_bench", "terminal_bench"),
    ("omniscience_accuracy", "omniscience"),
    ("omniscience_non_hallucination", "omniscience_nh"),
)
AXES_META = (
    {"id": "intelligence", "label": "INT / reasoning composite",
     "source": "Artificial Analysis Intelligence Index via OpenRouter GET /benchmarks"},
    {"id": "coding", "label": "coding",
     "source": "Artificial Analysis Coding Index via OpenRouter GET /benchmarks"},
    {"id": "agentic", "label": "agentic",
     "source": "Artificial Analysis Agentic Index via OpenRouter GET /benchmarks"},
    {"id": "reasoning", "label": "reasoning (dedicated)",
     "source": "AA reasoning_index when OpenRouter sends it; else UNMEASURED (INT is the composite)"},
    {"id": "speed", "label": "speed",
     "source": "AA output tokens/s when OpenRouter sends it; else UNMEASURED"},
    {"id": "math", "label": "math",
     "source": "AA math_index when OpenRouter sends it; else UNMEASURED"},
    {"id": "office", "label": "office work",
     "source": "UNMEASURED unless a vendor office index exists. GDPval-AA is its own column."},
    {"id": "gpqa", "label": "GPQA Diamond",
     "group": "Reasoning",
     "def": "Graduate-level scientific reasoning (biology, chemistry, physics). Google-proof. Higher % is better.",
     "source": "Artificial Analysis via OpenRouter model Benchmarks tab"},
    {"id": "hle", "label": "HLE",
     "group": "Reasoning",
     "def": "Humanity's Last Exam — expert-level questions. Higher % is better.",
     "source": "Artificial Analysis via OpenRouter model Benchmarks tab"},
    {"id": "ifbench", "label": "IFBench",
     "group": "Reasoning",
     "def": "Instruction-following benchmark. Higher % is better.",
     "source": "Artificial Analysis via OpenRouter model Benchmarks tab"},
    {"id": "tau2", "label": "τ²-Bench Telecom",
     "group": "Reasoning",
     "def": "Conversational AI agents in dual-control scenarios. Higher % is better.",
     "source": "Artificial Analysis via OpenRouter model Benchmarks tab"},
    {"id": "lcr", "label": "AA-LCR",
     "group": "Reasoning",
     "def": "Long context reasoning evaluation. Higher % is better.",
     "source": "Artificial Analysis via OpenRouter model Benchmarks tab"},
    {"id": "gdpval", "label": "GDPval-AA",
     "group": "Reasoning",
     "def": "Economically valuable tasks. Higher % is better.",
     "source": "Artificial Analysis via OpenRouter model Benchmarks tab"},
    {"id": "critpt", "label": "CritPt",
     "group": "Reasoning",
     "def": "Research-level physics reasoning. Higher % is better.",
     "source": "Artificial Analysis via OpenRouter model Benchmarks tab"},
    {"id": "scicode", "label": "SciCode",
     "group": "Coding",
     "def": "Python programming for scientific computing. Higher % is better.",
     "source": "Artificial Analysis via OpenRouter model Benchmarks tab"},
    {"id": "terminal_bench", "label": "Terminal-Bench Hard",
     "group": "Coding",
     "def": "Agentic coding and terminal use. Higher % is better.",
     "source": "Artificial Analysis via OpenRouter model Benchmarks tab"},
    {"id": "omniscience", "label": "AA-Omniscience Accuracy",
     "group": "Knowledge",
     "def": "Proportion of correctly answered questions. Higher % is better.",
     "source": "Artificial Analysis via OpenRouter model Benchmarks tab"},
    {"id": "omniscience_nh", "label": "AA-Omniscience Non-Hallucination",
     "group": "Knowledge",
     "def": "Rate of avoiding hallucination among non-correct responses. Higher % is better.",
     "source": "Artificial Analysis via OpenRouter model Benchmarks tab"},
    {"id": "file", "label": "file work",
     "source": "UNMEASURED — no vendor file-work index on this fold"},
    {"id": "stability", "label": "stability",
     "source": "UNMEASURED — AA Endpoint Accuracy Index is not on the OpenRouter fold"},
    {"id": "popularity", "label": "weekly tokens / popularity",
     "source": "OpenRouter weekly volume (table: Weekly Tokens) when the models row carries it; else UNMEASURED"},
    {"id": "throughput", "label": "throughput",
     "source": "OpenRouter table Throughput = vendor output tokens/s (AA output_speed). UNMEASURED if missing."},
    {"id": "latency", "label": "latency",
     "source": "OpenRouter table Latency = vendor time-to-first-token / latency when sent. UNMEASURED if missing."},
    {"id": "recency", "label": "most recent",
     "source": "OpenRouter models.created (unix). Newest first."},
    {"id": "price", "label": "price",
     "source": "OpenRouter pricing.prompt + pricing.completion, USD per 1M tokens"},
    {"id": "blended", "label": "blended $/M (75% in / 25% out)",
     "source": "0.75 * prompt_per_m + 0.25 * completion_per_m. Not invented."},
    {"id": "porosity", "label": "porosity",
     "source": "Scalar fold: errors per 100 LOC × severity 1–10 (hole SIZE only). Pair tensor + orthogonality is GET /api/v1/porosity. Audit stamps (agent_id, action, t, source:class) required for occupancy. UNMEASURED until observed. Does not invent."},
)
SEAT_COPY_KEYS = (
    "model", "model_2", "model_3", "via", "via_2", "via_3",
    "cap_usd", "effort", "label", "group", "assigned_at",
)


class ModelRaterError(RuntimeError):
    """kind in {NO_KEY, UNREACHABLE, AUTH_REQUIRED, BROKE, REFUSED, BAD_ROOT, BAD_INPUT}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _iso_now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def dir_for(paths) -> Path:
    return paths.role("state", "model_rater")


def catalog_path(paths) -> Path:
    return dir_for(paths) / CATALOG_NAME


def porosity_path(paths) -> Path:
    return dir_for(paths) / POROSITY_NAME


def seats_path(paths) -> Path:
    return dir_for(paths) / SEATS_NAME


def job_est_path(paths) -> Path:
    return dir_for(paths) / JOB_EST_NAME


def _f(v, default=None):
    if v is None or v == "":
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _mod_list(raw) -> tuple[str, ...]:
    if isinstance(raw, (list, tuple)):
        parts = raw
    else:
        parts = str(raw or "").replace(" ", "").split(",")
    out = []
    for p in parts:
        p = str(p or "").strip().lower()
        if p and p not in out:
            out.append(p)
    return tuple(out)


def _has_mods(have, need) -> bool:
    if not need:
        return True
    h = {str(x).lower() for x in (have or [])}
    return set(need) <= h


def _arch_mods(row: dict) -> tuple[list[str], list[str]]:
    arch = row.get("architecture") if isinstance(row.get("architecture"), dict) else {}
    ins = [str(x).lower() for x in (arch.get("input_modalities") or row.get("input_modalities") or [])]
    outs = [str(x).lower() for x in (arch.get("output_modalities") or row.get("output_modalities") or [])]
    return ins, outs


def _types(row: dict) -> list[str]:
    ins, outs = _arch_mods(row)
    params = [str(x).lower() for x in (row.get("supported_parameters") or [])]
    aa = ((row.get("benchmarks") or {}) if isinstance(row.get("benchmarks"), dict) else {}
          ).get("artificial_analysis") or {}
    kinds = []
    if "text" in outs and _has_mods(ins, DOCS_CUT["input_modalities"]):
        kinds.append("docs")
    if "image" in ins or "image" in outs:
        kinds.append("images")
    if "audio" in ins or "audio" in outs:
        kinds.append("audio")
    if "video" in ins or "video" in outs:
        kinds.append("video")
    if "reasoning" in params or (isinstance(row.get("reasoning"), dict)
                                 and row["reasoning"].get("default_enabled")):
        kinds.append("reasoning")
    if _f(aa.get("coding_index")) is not None:
        kinds.append("coding")
    if not kinds:
        kinds.append("chat")
    elif "text" in ins and "chat" not in kinds:
        kinds.append("chat")
    pricing = row.get("pricing") if isinstance(row.get("pricing"), dict) else {}
    if _f(pricing.get("prompt"), 1) == 0 and _f(pricing.get("completion"), 1) == 0:
        kinds.append("free")
    # unique, stable order
    seen = []
    for k in kinds:
        if k not in seen:
            seen.append(k)
    return seen


def family_of(model_id: str) -> str:
    """Family slug from a model id. Empty id → empty family."""
    mid = str(model_id or "").strip().lower()
    if not mid:
        return ""
    name = mid.split("/", 1)[-1]
    if mid.startswith("x-ai/") or name.startswith("grok"):
        return "grok"
    if "composer" in name:
        return "composer"
    if mid.startswith("anthropic/") or name.startswith("claude"):
        return "anthropic"
    if mid.startswith("google/") or name.startswith("gemini") or name.startswith("gemma"):
        return "google"
    if mid.startswith("openai/") or name.startswith("gpt"):
        return "openai"
    if "/" in mid:
        return mid.split("/", 1)[0]
    return name.split("-", 1)[0]


def default_policy() -> dict:
    return {
        "favored_models": [],
        "favored_families": [],
        "banned_models": [],
        "banned_families": [],
    }


def _str_list(raw) -> list[str]:
    out = []
    seen = set()
    for x in raw or []:
        s = str(x or "").strip()
        if not s:
            continue
        key = s.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(s)
    return out


def normalize_policy(raw) -> dict:
    src = raw if isinstance(raw, dict) else {}
    pol = default_policy()
    for k in pol:
        pol[k] = _str_list(src.get(k))
    return pol


def is_banned(model_id: str, policy: dict) -> bool:
    mid = str(model_id or "").strip()
    if not mid:
        return False
    pol = normalize_policy(policy)
    low = mid.lower()
    if any(low == str(x).lower() for x in pol["banned_models"]):
        return True
    fam = family_of(mid)
    return bool(fam) and any(fam == str(x).lower() for x in pol["banned_families"])


def is_favored(model_id: str, policy: dict) -> bool:
    mid = str(model_id or "").strip()
    if not mid:
        return False
    pol = normalize_policy(policy)
    low = mid.lower()
    if any(low == str(x).lower() for x in pol["favored_models"]):
        return True
    fam = family_of(mid)
    return bool(fam) and any(fam == str(x).lower() for x in pol["favored_families"])


def _copy_aa(dst: dict, aa: dict) -> bool:
    hit = False
    if not isinstance(aa, dict):
        return False
    for src, col in AA_FIELD_MAP:
        if dst.get(col) is not None:
            continue
        v = _f(aa.get(src))
        if v is not None:
            dst[col] = v
            hit = True
    return hit


def _popularity(raw: dict):
    stats = raw.get("stats") if isinstance(raw.get("stats"), dict) else {}
    for k in ("weekly_volume", "top_weekly", "popularity", "volume"):
        v = _f(stats.get(k) if k in stats else raw.get(k))
        if v is not None:
            return v
    return None


def normalize_row(raw: dict) -> dict:
    pricing = raw.get("pricing") if isinstance(raw.get("pricing"), dict) else {}
    aa = {}
    bench = raw.get("benchmarks") if isinstance(raw.get("benchmarks"), dict) else {}
    if isinstance(bench.get("artificial_analysis"), dict):
        aa = bench["artificial_analysis"]
    prompt = _f(pricing.get("prompt"), 0.0) or 0.0
    completion = _f(pricing.get("completion"), 0.0) or 0.0
    request = _f(pricing.get("request"), 0.0) or 0.0
    mid = str(raw.get("id") or "").strip()
    created = raw.get("created")
    try:
        created = int(created) if created not in (None, "") else None
    except (TypeError, ValueError):
        created = None
    row = {
        "id": mid,
        "name": str(raw.get("name") or mid),
        "family": family_of(mid),
        "context": int(raw.get("context_length") or 0),
        "prompt_per_m": round(prompt * 1_000_000, 6),
        "completion_per_m": round(completion * 1_000_000, 6),
        "request_usd": request,
        "intelligence": _f(aa.get("intelligence_index")),
        "coding": _f(aa.get("coding_index")),
        "agentic": _f(aa.get("agentic_index")),
        "reasoning": _f(aa.get("reasoning_index")),
        "speed": None,
        "math": _f(aa.get("math_index")),
        "office": None,
        "file": None,
        "stability": None,
        "gpqa": None,
        "hle": None,
        "ifbench": None,
        "tau2": None,
        "lcr": None,
        "gdpval": None,
        "critpt": None,
        "scicode": None,
        "terminal_bench": None,
        "omniscience": None,
        "omniscience_nh": None,
        "popularity": _popularity(raw),
        "weekly_tokens": _popularity(raw),
        "latency": None,
        "throughput": None,
        "categories": [],
        "created": created,
        "quality": None,
        "quality_n": 0,
        "quality_from": None,
        "types": _types(raw),
        "input_modalities": _arch_mods(raw)[0],
        "output_modalities": _arch_mods(raw)[1],
        "reasoning_enabled": bool(isinstance(raw.get("reasoning"), dict)
                                  and raw["reasoning"].get("default_enabled")),
        "rotator": mid.lower() in ROTATING,
        "favored": False,
        "banned": False,
    }
    _copy_aa(row, aa)
    row["throughput"] = row.get("speed")
    return row


def quality_score(row: dict) -> float | None:
    """Q = mean of vendor axes that exist. None = UNMEASURED, never invented."""
    vals = []
    for k in QUALITY_AXES:
        v = _f(row.get(k))
        if v is not None:
            vals.append(v)
    if not vals:
        return None
    return round(sum(vals) / len(vals), 1)


def _stamp_quality(row: dict) -> dict:
    q = quality_score(row)
    row["quality"] = q
    row["quality_n"] = sum(1 for k in QUALITY_AXES if row.get(k) is not None)
    _stamp_blend(row)
    return row


def blended_per_m(row: dict) -> float:
    """USD per 1M tokens at 75% input / 25% output."""
    pin = float(row.get("prompt_per_m") or 0)
    pout = float(row.get("completion_per_m") or 0)
    return round(BLEND_IN * pin + BLEND_OUT * pout, 6)


def _per_cost(quality, blend):
    """quality / blended $/M. None if either is UNMEASURED or blend is 0 (free)."""
    q = _f(quality)
    b = _f(blend)
    if q is None or b is None or b <= 0:
        return None
    return round(q / b, 4)


def _stamp_blend(row: dict) -> dict:
    blend = blended_per_m(row)
    row["blended_per_m"] = blend
    for axis in RATIO_AXES:
        row[f"{axis}_per_cost"] = _per_cost(row.get(axis), blend)
    return row


def apply_aa_benchmarks(models: list[dict], bench_rows) -> int:
    """Join Artificial Analysis indices from GET /benchmarks onto catalog rows.

    Match model_permaslug to id, then to the :variant-stripped base. Does not
    invent a number: only copies vendor indices that exist.
    """
    by_slug: dict[str, dict] = {}
    for raw in bench_rows or []:
        if not isinstance(raw, dict):
            continue
        slug = str(raw.get("model_permaslug") or raw.get("id") or "").strip()
        if not slug:
            continue
        by_slug[slug.lower()] = raw
    n = 0
    for m in models:
        mid = str(m.get("id") or "")
        base = mid.split(":", 1)[0]
        raw = by_slug.get(mid.lower()) or by_slug.get(base.lower())
        if not raw:
            continue
        hit = _copy_aa(m, raw)
        if hit:
            n += 1
            m["quality_from"] = "openrouter/benchmarks"
    return n


def inherit_variant_quality(models: list[dict]) -> int:
    """:batch / :free / :nitro share weights with the base id. Copy axes only."""
    by_base: dict[str, dict] = {}
    for m in models:
        if m.get("intelligence") is None and m.get("coding") is None:
            continue
        base = str(m.get("id") or "").split(":", 1)[0]
        if base and base not in by_base:
            by_base[base] = m
    n = 0
    for m in models:
        if m.get("intelligence") is not None or m.get("coding") is not None:
            continue
        base = str(m.get("id") or "").split(":", 1)[0]
        src = by_base.get(base)
        if not src or src is m:
            continue
        for k in QUALITY_AXES + EXTRA_AXES:
            if m.get(k) is None and src.get(k) is not None:
                m[k] = src[k]
        if m.get("created") is None and src.get("created") is not None:
            m["created"] = src.get("created")
        m["quality_from"] = src.get("id")
        n += 1
    return n


def load_catalog(paths) -> dict:
    p = catalog_path(paths)
    if not p.is_file():
        return {
            "schema": SCHEMA, "fetched_at": None, "n": 0, "models": [],
            "stale": True, "age_s": None, "http": None,
        }
    try:
        rec = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {
            "schema": SCHEMA, "fetched_at": None, "n": 0, "models": [],
            "stale": True, "age_s": None, "http": None, "kind": "BROKE",
        }
    fetched = rec.get("fetched_at_unix")
    age = None if not fetched else max(0.0, time.time() - float(fetched))
    rec["age_s"] = None if age is None else round(age, 1)
    rec["stale"] = age is None or age > TTL_S
    rec.setdefault("schema", SCHEMA)
    rec.setdefault("models", [])
    rec["n"] = len(rec["models"])
    for m in rec["models"]:
        if isinstance(m, dict) and m.get("quality") is None:
            _stamp_quality(m)
    rec["n_quality"] = sum(1 for m in rec["models"]
                           if isinstance(m, dict) and m.get("quality") is not None)
    for m in rec["models"]:
        if isinstance(m, dict):
            _stamp_blend(m)
    return rec


def default_seats() -> list[dict]:
    return [dict(s) for s in DEFAULT_SEATS]


def load_seats(paths) -> dict:
    p = seats_path(paths)
    base = default_seats()
    locked_keys = {(d["profile"], d["seat"]) for d in base
                   if (d["profile"], d["seat"]) in LOCKED_SEATS}
    if not p.is_file():
        return {"schema": SCHEMA, "seats": base, "updated_at": None}
    try:
        rec = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"schema": SCHEMA, "seats": base, "updated_at": None, "kind": "BROKE"}
    have = {(s.get("profile"), s.get("seat")): s for s in rec.get("seats") or []
            if isinstance(s, dict) and s.get("profile") and s.get("seat")}
    merged = []
    seen = set()
    for d in base:
        key = (d["profile"], d["seat"])
        if key not in locked_keys and key not in have:
            continue
        row = dict(d)
        if key in have:
            incoming = str(have[key].get("model") or "")
            if incoming or key not in LOCKED_SEATS:
                row["model"] = incoming
            row["assigned_at"] = have[key].get("assigned_at")
            if have[key].get("label"):
                row["label"] = have[key]["label"]
            if have[key].get("via"):
                row["via"] = str(have[key]["via"])
            if have[key].get("cap_usd") is not None:
                row["cap_usd"] = have[key].get("cap_usd")
            if have[key].get("group"):
                row["group"] = have[key].get("group")
            for k in ("model_2", "model_3", "via_2", "via_3", "effort"):
                if have[key].get(k) not in (None,):
                    row[k] = have[key].get(k)
        merged.append(row)
        seen.add(key)
    for key, src in have.items():
        if key in seen:
            continue
        merged.append({
            "profile": str(src.get("profile")),
            "seat": str(src.get("seat")),
            "group": str(src.get("group") or src.get("profile") or ""),
            "label": str(src.get("label") or f"{src.get('profile')}.{src.get('seat')}"),
            "model": str(src.get("model") or ""),
            "model_2": str(src.get("model_2") or ""),
            "model_3": str(src.get("model_3") or ""),
            "via": str(src.get("via") or ""),
            "via_2": str(src.get("via_2") or ""),
            "via_3": str(src.get("via_3") or ""),
            "cap_usd": src.get("cap_usd"),
            "effort": str(src.get("effort") or ""),
            "assigned_at": src.get("assigned_at"),
        })
    rec["seats"] = merged
    rec["schema"] = SCHEMA
    rec.setdefault("model_caps", {})
    if not isinstance(rec.get("model_caps"), dict):
        rec["model_caps"] = {}
    rec["policy"] = normalize_policy(rec.get("policy"))
    return rec


def save_seats(paths, rec: dict) -> dict:
    d = dir_for(paths)
    d.mkdir(parents=True, exist_ok=True)
    rec = dict(rec)
    rec["schema"] = SCHEMA
    rec["updated_at"] = _iso_now()
    seats_path(paths).write_text(
        json.dumps(rec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return rec


def save_catalog(paths, rec: dict) -> dict:
    d = dir_for(paths)
    d.mkdir(parents=True, exist_ok=True)
    catalog_path(paths).write_text(
        json.dumps(rec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return rec


def refresh(paths, *, http=None) -> dict:
    from cosmos_openrouter_rail import (
        BENCHMARKS_PATH, OpenRouterRail, key_path_for, load_spec,
        spec_path_for, MODELS_PATH, read_key,
    )
    spec = load_spec(spec_path_for(paths) if spec_path_for(paths).exists() else None)
    keyp = key_path_for(paths, spec)
    if http is None and not read_key(keyp):
        raise ModelRaterError("NO_KEY", f"OpenRouter key missing at {keyp.name}")
    rail = OpenRouterRail(keyp, spec, http=http)
    status, _hdrs, body = rail._call("GET", MODELS_PATH)
    if status in (401, 403):
        raise ModelRaterError("AUTH_REQUIRED", f"OpenRouter GET /models http={status}")
    if status in (-1,):
        raise ModelRaterError("UNREACHABLE", "OpenRouter GET /models unreachable")
    if status != 200 or not isinstance(body, dict):
        raise ModelRaterError("BROKE", f"OpenRouter GET /models http={status}")
    rows = []
    for raw in body.get("data") or []:
        if not isinstance(raw, dict) or not raw.get("id"):
            continue
        rows.append(normalize_row(raw))
    b_status, _bh, b_body = rail._call("GET", BENCHMARKS_PATH)
    n_bench = 0
    if b_status == 200 and isinstance(b_body, dict):
        n_bench = apply_aa_benchmarks(rows, b_body.get("data") or [])
    n_inherit = inherit_variant_quality(rows)
    for m in rows:
        _stamp_quality(m)
        if m.get("throughput") is None:
            m["throughput"] = m.get("speed")
        if m.get("weekly_tokens") is None:
            m["weekly_tokens"] = m.get("popularity")
    prog_ids = set()
    p_status, _ph, p_body = rail._call(
        "GET", MODELS_PATH + "?category=programming")
    if p_status == 200 and isinstance(p_body, dict):
        for raw in p_body.get("data") or []:
            if isinstance(raw, dict) and raw.get("id"):
                prog_ids.add(str(raw["id"]))
    for m in rows:
        cats = list(m.get("categories") or [])
        if m.get("id") in prog_ids and "programming" not in cats:
            cats.append("programming")
        m["categories"] = cats
    rec = {
        "schema": SCHEMA,
        "fetched_at": _iso_now(),
        "fetched_at_unix": time.time(),
        "http": status,
        "benchmarks_http": b_status,
        "programming_http": p_status,
        "n_programming": len(prog_ids),
        "n": len(rows),
        "n_quality": sum(1 for m in rows if m.get("quality") is not None),
        "n_benchmarks_joined": n_bench,
        "n_variant_inherited": n_inherit,
        "models": rows,
        "stale": False,
        "age_s": 0,
        "source": "openrouter GET /api/v1/models",
        "quality_source": "openrouter GET /api/v1/benchmarks?source=artificial-analysis",
    }
    save_catalog(paths, rec)
    return rec


_AXIS_SORT = frozenset({
    "intelligence", "coding", "agentic", "quality", "q", "reasoning",
    "speed", "stability", "office", "file", "math", "popularity", "latency",
    "intelligence_per_cost", "coding_per_cost", "agentic_per_cost",
    "quality_per_cost", "porosity",
    "gpqa", "hle", "ifbench", "tau2", "lcr", "gdpval", "critpt",
    "scicode", "terminal_bench", "omniscience", "omniscience_nh",
})


def _sort_key(row: dict, sort: str):
    if sort == "price":
        return (row.get("prompt_per_m") or 0) + (row.get("completion_per_m") or 0)
    if sort == "blended":
        return float(row.get("blended_per_m") or 0)
    if sort in _AXIS_SORT:
        key = "quality" if sort in ("quality", "q") else sort
        v = row.get(key)
        return -1.0 if v is None else float(v)
    if sort in ("recency", "created"):
        return int(row.get("created") or 0)
    if sort == "context":
        return int(row.get("context") or 0)
    if sort == "name":
        return str(row.get("name") or "").lower()
    return str(row.get("id") or "")


def query_models(catalog: dict, *, sort="price", desc=False, type_name="",
                 q="", limit=400, policy=None, show_banned=False,
                 favored_first=True, porosity=None,
                 input_modalities="", output_modalities="",
                 category="") -> list[dict]:
    sort = sort if sort in SORT_KEYS else "price"
    rows = list(catalog.get("models") or [])
    ql = str(q or "").strip().lower()
    tn = str(type_name or "").strip().lower()
    catn = str(category or "").strip().lower()
    if tn == "docs":
        need_in = DOCS_CUT["input_modalities"]
        need_out = DOCS_CUT["output_modalities"]
    else:
        need_in = _mod_list(input_modalities)
        need_out = _mod_list(output_modalities)
    pol = normalize_policy(policy)
    out = []
    for r in rows:
        if r.get("rotator"):
            continue
        row = dict(r)
        row["family"] = row.get("family") or family_of(row.get("id"))
        row["banned"] = is_banned(row.get("id"), pol)
        row["favored"] = is_favored(row.get("id"), pol)
        _stamp_blend(row)
        if row["banned"] and not show_banned:
            continue
        ins, outs = _arch_mods(row)
        if tn == "docs":
            if not (_has_mods(ins, need_in) and _has_mods(outs, need_out)):
                continue
        elif tn and tn not in (row.get("types") or []):
            continue
        elif need_in and not _has_mods(ins, need_in):
            continue
        elif need_out and not _has_mods(outs, need_out):
            continue
        if catn and catn not in [str(x).lower() for x in (row.get("categories") or [])]:
            continue
        if ql:
            blob = (str(row.get("id") or "") + " " + str(row.get("name") or "")
                    + " " + str(row.get("family") or "")).lower()
            if ql not in blob:
                continue
        out.append(row)
    if porosity:
        apply_porosity(out, porosity)
    if sort == "porosity":
        # Lower porosity is better. Default ascending. None = UNMEASURED last.
        out.sort(key=lambda r: (
            r.get("porosity") is None,
            (r.get("porosity") or 0.0) if not desc else -(r.get("porosity") or 0.0),
        ))
    elif sort in _AXIS_SORT:
        axis = "quality" if sort in ("quality", "q") else sort
        out.sort(key=lambda r, a=axis: (
            r.get(a) is None,
            (-(r.get(a) or 0.0)) if not desc else (r.get(a) or 0.0),
        ))
    elif sort in ("price", "blended"):
        out.sort(key=lambda r: _sort_key(r, sort), reverse=bool(desc))
    elif sort in ("recency", "created"):
        out.sort(key=lambda r: int(r.get("created") or 0), reverse=not bool(desc))
    elif sort == "context":
        out.sort(key=lambda r: int(r.get("context") or 0), reverse=not bool(desc))
    else:
        out.sort(key=lambda r: str(r.get("name") or r.get("id") or "").lower(),
                 reverse=bool(desc))
    if favored_first:
        out.sort(key=lambda r: (0 if r.get("favored") else 1))
    try:
        lim = int(limit)
    except (TypeError, ValueError):
        lim = 400
    return out[: max(1, min(lim, 800))]


def normalize_via(via) -> str:
    v = str(via or "").strip().lower()
    if not v:
        return ""
    if v not in VIA_IDS:
        raise ModelRaterError("BAD_INPUT", f"unknown via {via!r}")
    return v


def _clamp_usd(raw, default=None):
    if raw is None or raw == "":
        return default
    try:
        n = float(raw)
    except (TypeError, ValueError):
        return default
    if n < 0:
        return 0.0
    if n > 1_000_000:
        return 1_000_000.0
    return n


def set_model_cap(paths, model: str, cap_usd) -> dict:
    """Per-model spend limit on the rater. 0 = off. Not the Core spend gate."""
    model = str(model or "").strip()
    if not model:
        raise ModelRaterError("BAD_INPUT", "model is required")
    if model.lower() in ROTATING:
        raise ModelRaterError("REFUSED", f"rotator id {model!r} is not assignable")
    rec = load_seats(paths)
    caps = rec.get("model_caps") if isinstance(rec.get("model_caps"), dict) else {}
    n = _clamp_usd(cap_usd, None)
    if n is None:
        raise ModelRaterError("BAD_INPUT", "cap_usd is required")
    if n == 0:
        caps.pop(model, None)
    else:
        caps[model] = n
    rec["model_caps"] = caps
    return save_seats(paths, rec)


def default_porosity() -> dict:
    return {
        "schema": SCHEMA,
        "models": {},
        "federation": {
            "kind": "NO_HOST",
            "n_local": 0,
            "n_federated": 0,
            "note": (
                "Scalar fold: (errors per 100 LOC) × (severity 1–10) = hole SIZE. "
                "1 = incidental, 10 = security/data/system hazard. "
                "Distribution and pair orthogonality: GET /api/v1/porosity. "
                "Each observation needs Irbe stamps: agent_id, action, t, "
                "authority source:class. Federation aggregates peer rows when "
                "a host is named — NO_HOST until then. Does not invent scores."
            ),
        },
    }


def load_porosity(paths) -> dict:
    base = default_porosity()
    p = porosity_path(paths)
    if not p.is_file():
        return base
    try:
        rec = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        base["kind"] = "BROKE"
        return base
    if not isinstance(rec, dict):
        base["kind"] = "BROKE"
        return base
    models = rec.get("models") if isinstance(rec.get("models"), dict) else {}
    clean = {}
    n_local = 0
    n_fed = 0
    for mid, rows in models.items():
        if not isinstance(rows, list):
            continue
        kept = []
        for o in rows:
            if not isinstance(o, dict):
                continue
            kept.append(o)
            if str(o.get("source") or "local").lower() == "federation":
                n_fed += 1
            else:
                n_local += 1
        if kept:
            clean[str(mid)] = kept
    fed = dict(base["federation"])
    if isinstance(rec.get("federation"), dict):
        fed.update({k: rec["federation"].get(k, fed.get(k)) for k in fed})
    fed["n_local"] = n_local
    fed["n_federated"] = n_fed
    if n_fed and fed.get("kind") == "NO_HOST":
        fed["kind"] = "AGGREGATED"
    return {"schema": SCHEMA, "models": clean, "federation": fed}


def save_porosity(paths, rec: dict) -> dict:
    d = dir_for(paths)
    d.mkdir(parents=True, exist_ok=True)
    rec = dict(rec)
    rec["schema"] = SCHEMA
    rec["updated_at"] = _iso_now()
    porosity_path(paths).write_text(
        json.dumps(rec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return rec


def _fold_obs(rows: list) -> dict:
    vals = []
    n_local = 0
    n_fed = 0
    for o in rows or []:
        if not isinstance(o, dict):
            continue
        v = _f(o.get("porosity"))
        if v is not None:
            vals.append(v)
        if str(o.get("source") or "local").lower() == "federation":
            n_fed += 1
        else:
            n_local += 1
    return {
        "porosity": None if not vals else round(sum(vals) / len(vals), 4),
        "n": len(vals),
        "n_local": n_local,
        "n_federated": n_fed,
    }


def apply_porosity(models: list[dict], rec: dict) -> None:
    by = rec.get("models") if isinstance(rec.get("models"), dict) else {}
    for m in models:
        if not isinstance(m, dict):
            continue
        mid = str(m.get("id") or "")
        fold = _fold_obs(by.get(mid) or [])
        m["porosity"] = fold["porosity"]
        m["porosity_n"] = fold["n"]
        m["porosity_n_local"] = fold["n_local"]
        m["porosity_n_federated"] = fold["n_federated"]


def _unmeasured_complement() -> dict:
    """Compact pack when pair obs.jsonl is absent. Does not mkdir."""
    from cosmos_porosity import SCHEMA as poro_schema
    return {
        "schema": poro_schema,
        "kind": "UNMEASURED",
        "n_obs": 0,
        "n_pairs": 0,
        "tensors_shape": "tensors[agent][vs][axis]",
        "last_obs": {},
        "complement_kind": "UNMEASURED",
    }


def complement_pack(paths) -> dict:
    """Pointer pack for pair-tensor T + complement C. GET never mkdir.

    Catalog occupancy is not scalar-only. The pane GETs /api/v1/porosity
    for the grid; this pack is schema/kind/counts only — never the tensors.
    """
    from cosmos_porosity import obs_path, snapshot as porosity_snapshot
    if not obs_path(paths).is_file():
        return _unmeasured_complement()
    snap = porosity_snapshot(paths)
    base = _unmeasured_complement()
    last = snap.get("last_obs")
    n_obs = snap.get("n_obs")
    n_pairs = snap.get("n_pairs")
    return {
        "schema": snap.get("schema") or base["schema"],
        "kind": snap.get("kind") or "UNMEASURED",
        "n_obs": n_obs if isinstance(n_obs, int) else base["n_obs"],
        "n_pairs": n_pairs if isinstance(n_pairs, int) else base["n_pairs"],
        "tensors_shape": snap.get("tensors_shape") or base["tensors_shape"],
        "last_obs": last if isinstance(last, dict) else {},
        "complement_kind": snap.get("complement_kind") or "UNMEASURED",
    }


def record_porosity(paths, model: str, loc_per_100, severity, *,
                    source="local", loc_n=None, note="",
                    agent_id="", action="", authority="") -> dict:
    """Record one porosity observation. Does not invent a score.

    Optional Irbe stamps: agent_id (named-pin key), action, authority
    as source:class. Missing stamps stay empty — the fold is still
    size-only UNMEASURED as an audit event.
    """
    model = str(model or "").strip()
    if not model:
        raise ModelRaterError("BAD_INPUT", "model is required")
    if model.lower() in ROTATING:
        raise ModelRaterError("REFUSED", f"rotator id {model!r} is not assignable")
    loc = _f(loc_per_100)
    sev = _f(severity)
    if loc is None or loc < 0:
        raise ModelRaterError("BAD_INPUT", "loc_per_100 must be >= 0")
    if sev is None or sev < 1 or sev > 10:
        raise ModelRaterError("BAD_INPUT", "severity must be 1–10")
    src = str(source or "local").strip().lower()
    if src not in ("local", "federation"):
        raise ModelRaterError("BAD_INPUT", f"unknown porosity source {source!r}")
    score = round(loc * sev, 4)
    rec = load_porosity(paths)
    rows = list(rec["models"].get(model) or [])
    rows.append({
        "porosity": score,
        "loc_per_100": loc,
        "severity": sev,
        "loc_n": loc_n,
        "source": src,
        "agent_id": str(agent_id or model)[:80],
        "action": str(action or "observe")[:40],
        "authority": str(authority or "")[:80],
        "note": str(note or "")[:240],
        "at": _iso_now(),
    })
    rec["models"][model] = rows[-200:]
    rec = save_porosity(paths, rec)
    rec["last"] = {
        "model": model, "porosity": score, "source": src,
        "agent_id": str(agent_id or model)[:80],
        "action": str(action or "observe")[:40],
        "authority": str(authority or "")[:80],
    }
    rec["fold"] = _fold_obs(rec["models"][model])
    return rec


def normalize_effort(effort) -> str:
    e = str(effort or "").strip().lower()
    if e not in EFFORT_IDS:
        raise ModelRaterError("BAD_INPUT", f"unknown effort {effort!r}")
    return e


def _check_model_id(model: str, paths, via_now: str, rec: dict):
    model = str(model or "").strip()
    if not model:
        return
    if model.lower() in ROTATING:
        raise ModelRaterError("REFUSED", f"rotator id {model!r} is not assignable")
    if is_banned(model, rec.get("policy")):
        raise ModelRaterError("REFUSED", f"model {model!r} is banned on the rater")
    occupancy = {CCR_MODEL, "composer-2.5", "claude-opus-5"}
    cli_or_dom = via_now.startswith("cli:") or via_now == "dom" or via_now.startswith("mcp")
    if model not in occupancy and not cli_or_dom:
        cat = load_catalog(paths)
        ids = {m.get("id") for m in cat.get("models") or []}
        if cat.get("n") and model not in ids:
            raise ModelRaterError("BAD_INPUT", f"model {model!r} not in local catalog")


def assign_seat(paths, profile: str, seat: str, model=None, via: str = "",
                cap_usd=None, model_2=None, model_3=None,
                via_2=None, via_3=None, effort=None) -> dict:
    profile = str(profile or "").strip().lower()
    seat = str(seat or "").strip().lower()
    model_in = None if model is None else str(model).strip()
    if not profile or not seat:
        raise ModelRaterError("BAD_INPUT", "profile and seat are required")
    if (profile, seat) == ("forge", "ccr") and model_in == "":
        raise ModelRaterError("REFUSED", "forge.ccr occupancy is grok-4.6 — cannot unassign")
    if model_in and model_in.lower() in ROTATING:
        raise ModelRaterError("REFUSED", f"rotator id {model_in!r} is not assignable")
    via_n = normalize_via(via) if via else ""
    rec = load_seats(paths)
    found = False
    for row in rec["seats"]:
        if row["profile"] == profile and row["seat"] == seat:
            if model_in is not None:
                row["model"] = model_in
                row["assigned_at"] = _iso_now() if model_in else None
            if via_n:
                row["via"] = via_n
            if cap_usd is not None and cap_usd != "":
                n = _clamp_usd(cap_usd, 0.0)
                if n == 0:
                    row.pop("cap_usd", None)
                else:
                    row["cap_usd"] = n
            if model_2 is not None:
                row["model_2"] = str(model_2 or "").strip()
            if model_3 is not None:
                row["model_3"] = str(model_3 or "").strip()
            if via_2 is not None:
                row["via_2"] = normalize_via(via_2) if via_2 else ""
            if via_3 is not None:
                row["via_3"] = normalize_via(via_3) if via_3 else ""
            if effort is not None:
                row["effort"] = normalize_effort(effort)
            found = True
            break
    if not found:
        raise ModelRaterError("BAD_INPUT", f"unknown seat {profile}.{seat}")
    via_now = via_n or next(
        (str(s.get("via") or "") for s in rec["seats"]
         if s.get("profile") == profile and s.get("seat") == seat),
        "")
    if model_in:
        _check_model_id(model_in, paths, via_now, rec)
    for extra in (model_2, model_3):
        if extra not in (None, ""):
            _check_model_id(str(extra), paths, via_now, rec)
    return save_seats(paths, rec)


def set_policy(paths, *, favored_models=None, favored_families=None,
               banned_models=None, banned_families=None) -> dict:
    rec = load_seats(paths)
    pol = normalize_policy(rec.get("policy"))
    if favored_models is not None:
        pol["favored_models"] = _str_list(favored_models)
    if favored_families is not None:
        pol["favored_families"] = _str_list(
            str(x).lower() for x in (favored_families or []))
    if banned_models is not None:
        pol["banned_models"] = _str_list(banned_models)
    if banned_families is not None:
        pol["banned_families"] = _str_list(
            str(x).lower() for x in (banned_families or []))
    rec["policy"] = pol
    return save_seats(paths, rec)


def _stage_for(seat_row: dict) -> str:
    g = str(seat_row.get("group") or "")
    p = str(seat_row.get("profile") or "")
    s = str(seat_row.get("seat") or "")
    if "RESEARCH" in g or s.startswith("research_"):
        return "research"
    if "BUILD" in g or s in ("lane_a", "lane_b") or s.startswith("build_"):
        return "build"
    if "CRITICS" in g or s.startswith("critic_"):
        return "critics"
    if p == "openwork" or s == "orc":
        return "openwork"
    if p == "crucible":
        return "crucible"
    if p == "forge":
        return "forge"
    if p == "dispatch":
        return "dispatch"
    return p or "role"


def scan_roles(paths=None, *, q="") -> dict:
    """Named COSMOS roles. This catalog, not a live grep of the tree."""
    seats = (load_seats(paths).get("seats") if paths else None) or default_seats()
    ql = str(q or "").strip().lower()
    roles = []
    for s in seats:
        if not isinstance(s, dict):
            continue
        rec = {
            "element": s.get("group") or s.get("profile"),
            "profile": s.get("profile"),
            "seat": s.get("seat"),
            "label": s.get("label"),
            "stage": _stage_for(s),
            "model": s.get("model") or "",
            "model_2": s.get("model_2") or "",
            "model_3": s.get("model_3") or "",
            "via": s.get("via") or "",
            "via_2": s.get("via_2") or "",
            "via_3": s.get("via_3") or "",
            "effort": s.get("effort") or "",
            "cap_usd": s.get("cap_usd"),
            "locked": bool(s.get("locked") or
                           (s.get("profile"), s.get("seat")) in LOCKED_SEATS),
        }
        if ql:
            blob = " ".join(str(rec.get(k) or "") for k in
                            ("element", "profile", "seat", "label", "stage",
                             "model")).lower()
            if ql not in blob:
                continue
        roles.append(rec)
    return {
        "schema": SCHEMA,
        "ok": True,
        "n": len(roles),
        "q": q or "",
        "roles": roles,
        "note": (
            "Search is the named COSMOS role catalog (OpenWork ORC, Forge CCr, "
            "MOTIF RESEARCH/BUILD/CRITICS, Crucible, Dispatch), plus extra "
            "seats already stored. Not a live grep of the tree."
        ),
    }


def _next_adv_seat(seats: list[dict]) -> str:
    taken = {s.get("seat") for s in seats
             if s.get("profile") == "forge" and str(s.get("seat") or "").startswith("adv_")}
    n = 1
    while f"adv_{n}" in taken:
        n += 1
        if n > MAX_ADV:
            raise ModelRaterError("REFUSED", f"at most {MAX_ADV} adversarial coders")
    return f"adv_{n}"


def add_adversary(paths, model: str = "", label: str = "", via: str = "") -> dict:
    rec = load_seats(paths)
    n_adv = sum(1 for s in rec["seats"]
                if s.get("profile") == "forge"
                and str(s.get("seat") or "").startswith("adv_"))
    if n_adv >= MAX_ADV:
        raise ModelRaterError("REFUSED", f"at most {MAX_ADV} adversarial coders")
    seat = _next_adv_seat(rec["seats"])
    num = seat.split("_", 1)[-1]
    via_n = normalize_via(via) if via else "openrouter-api"
    row = {
        "profile": "forge",
        "seat": seat,
        "label": str(label or f"Adversarial coder {num}").strip()
                 or f"Adversarial coder {num}",
        "model": "",
        "via": via_n,
        "assigned_at": None,
    }
    rec["seats"].append(row)
    rec = save_seats(paths, rec)
    model = str(model or "").strip()
    if model:
        rec = assign_seat(paths, "forge", seat, model)
    return rec


def remove_adversary(paths, seat: str) -> dict:
    seat = str(seat or "").strip().lower()
    if not seat:
        raise ModelRaterError("BAD_INPUT", "seat is required")
    if ("forge", seat) in LOCKED_SEATS:
        raise ModelRaterError("REFUSED", f"seat forge.{seat} is locked")
    rec = load_seats(paths)
    keep = []
    found = False
    for row in rec["seats"]:
        if row.get("profile") == "forge" and row.get("seat") == seat:
            found = True
            continue
        keep.append(row)
    if not found:
        raise ModelRaterError("BAD_INPUT", f"unknown seat forge.{seat}")
    rec["seats"] = keep
    return save_seats(paths, rec)


def default_job_estimate() -> dict:
    return {
        "schema": SCHEMA,
        "tokens_in": CCR_INITIAL_IN,
        "tokens_out": CCR_INITIAL_OUT,
        "source": "ccr_initial",
        "override": False,
        "note": ("CCr initial for a MOTIF BUILD work-order "
                 f"({CCR_INITIAL_IN} in / {CCR_INITIAL_OUT} out). Override if the job is smaller or larger."),
    }


def load_job_estimate(paths) -> dict:
    p = job_est_path(paths)
    base = default_job_estimate()
    if not p.is_file():
        return base
    try:
        rec = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return dict(base, kind="BROKE")
    if not isinstance(rec, dict):
        return base
    try:
        tin = max(0, int(rec.get("tokens_in")))
        tout = max(0, int(rec.get("tokens_out")))
    except (TypeError, ValueError):
        return base
    out = dict(base)
    out["tokens_in"] = tin
    out["tokens_out"] = tout
    out["override"] = bool(rec.get("override"))
    out["source"] = "override" if out["override"] else "ccr_initial"
    out["updated_at"] = rec.get("updated_at")
    return out


def save_job_estimate(paths, tokens_in, tokens_out, *, override=True) -> dict:
    try:
        tin = max(0, int(tokens_in))
        tout = max(0, int(tokens_out))
    except (TypeError, ValueError) as e:
        raise ModelRaterError("BAD_INPUT", "tokens_in/tokens_out must be integers") from e
    rec = {
        "schema": SCHEMA,
        "tokens_in": tin,
        "tokens_out": tout,
        "override": bool(override),
        "source": "override" if override else "ccr_initial",
        "updated_at": _iso_now(),
        "note": default_job_estimate()["note"],
    }
    d = dir_for(paths)
    d.mkdir(parents=True, exist_ok=True)
    job_est_path(paths).write_text(
        json.dumps(rec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return rec


def reset_job_estimate(paths) -> dict:
    rec = default_job_estimate()
    rec["updated_at"] = _iso_now()
    d = dir_for(paths)
    d.mkdir(parents=True, exist_ok=True)
    job_est_path(paths).write_text(
        json.dumps(rec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return rec


def job_costs(catalog: dict, seats: list[dict], tokens_in: int, tokens_out: int) -> dict:
    lines = []
    total = 0.0
    unassigned = 0
    for s in seats:
        if s.get("profile") != "forge":
            continue
        model = str(s.get("model") or "").strip()
        line = {
            "profile": s.get("profile"),
            "seat": s.get("seat"),
            "label": s.get("label"),
            "model": model or None,
            "usd": None,
            "free": None,
        }
        if not model:
            unassigned += 1
            lines.append(line)
            continue
        try:
            est = estimate(catalog, model, tokens_in, tokens_out)
        except ModelRaterError:
            lines.append(line)
            continue
        line["usd"] = est["usd"]
        line["free"] = est["free"]
        line["name"] = est.get("name")
        total += float(est["usd"] or 0)
        lines.append(line)
    return {
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "n": len(lines),
        "unassigned": unassigned,
        "total_usd": round(total, 6),
        "lines": lines,
    }


def estimate(catalog: dict, model: str, tokens_in: int, tokens_out: int) -> dict:
    model = str(model or "").strip()
    if not model:
        raise ModelRaterError("BAD_INPUT", "model is required")
    if model.lower() in ROTATING:
        raise ModelRaterError("REFUSED", f"rotator id {model!r}")
    try:
        tin = max(0, int(tokens_in))
        tout = max(0, int(tokens_out))
    except (TypeError, ValueError) as e:
        raise ModelRaterError("BAD_INPUT", "tokens_in/tokens_out must be integers") from e
    row = None
    for m in catalog.get("models") or []:
        if m.get("id") == model:
            row = m
            break
    if row is None:
        raise ModelRaterError("BAD_INPUT", f"model {model!r} not in local catalog")
    usd = (tin / 1_000_000.0) * float(row.get("prompt_per_m") or 0)
    usd += (tout / 1_000_000.0) * float(row.get("completion_per_m") or 0)
    usd += float(row.get("request_usd") or 0)
    return {
        "model": model,
        "name": row.get("name"),
        "tokens_in": tin,
        "tokens_out": tout,
        "prompt_per_m": row.get("prompt_per_m"),
        "completion_per_m": row.get("completion_per_m"),
        "usd": round(usd, 6),
        "free": "free" in (row.get("types") or []),
    }


def snapshot(paths, *, sort="price", desc=False, type_name="", q="",
             limit=400, refresh_if_stale=False, http=None,
             show_banned=False, role_q="",
             input_modalities="", output_modalities="",
             category="") -> dict:
    cat = load_catalog(paths)
    refreshed = False
    if refresh_if_stale and (cat.get("stale") or not cat.get("n")):
        cat = refresh(paths, http=http)
        refreshed = True
    seats = load_seats(paths)
    pol = normalize_policy(seats.get("policy"))
    poro = load_porosity(paths)
    models = query_models(cat, sort=sort, desc=desc, type_name=type_name,
                          q=q, limit=limit, policy=pol,
                          show_banned=bool(show_banned), porosity=poro,
                          input_modalities=input_modalities,
                          output_modalities=output_modalities,
                          category=category)
    job = load_job_estimate(paths)
    costs = job_costs(cat, seats.get("seats") or [],
                      job["tokens_in"], job["tokens_out"])
    roles = scan_roles(paths, q=role_q)
    return {
        "schema": SCHEMA,
        "ok": True,
        "fetched_at": cat.get("fetched_at"),
        "age_s": cat.get("age_s"),
        "stale": bool(cat.get("stale")),
        "http": cat.get("http"),
        "quality_source": cat.get("quality_source"),
        "n_catalog": cat.get("n") or 0,
        "n": len(models),
        "refreshed": refreshed,
        "sort": sort,
        "type": type_name or "",
        "q": q or "",
        "input_modalities": list(_mod_list(input_modalities)
                                 or (DOCS_CUT["input_modalities"]
                                     if str(type_name or "").strip().lower() == "docs"
                                     else ())),
        "output_modalities": list(_mod_list(output_modalities)
                                  or (DOCS_CUT["output_modalities"]
                                      if str(type_name or "").strip().lower() == "docs"
                                      else ())),
        "category": str(category or ""),
        "categories": list(OR_CATEGORIES),
        "catalog_cut": dict(DOCS_CUT),
        "table_cut": dict(TABLE_CUT),
        "models": models,
        "seats": seats.get("seats") or default_seats(),
        "roles": roles.get("roles") or [],
        "n_roles": roles.get("n") or 0,
        "role_q": role_q or "",
        "policy": pol,
        "model_caps": seats.get("model_caps") or {},
        "job_estimate": job,
        "job_costs": costs,
        "ccr_initial": {"tokens_in": CCR_INITIAL_IN, "tokens_out": CCR_INITIAL_OUT},
        "axes": [a["id"] for a in AXES_META],
        "axes_meta": [dict(a) for a in AXES_META],
        "n_quality": cat.get("n_quality") or sum(
            1 for m in (cat.get("models") or []) if m.get("quality") is not None),
        "ttl_s": TTL_S,
        "max_adv": MAX_ADV,
        "via_options": [dict(v) for v in VIA_OPTIONS],
        "effort_options": ["low", "medium", "high", "max"],
        "motif_step_1": "PROBLEM STATEMENT / STATED GOAL",
        "blend": {"in": BLEND_IN, "out": BLEND_OUT},
        "porosity": poro.get("federation") or default_porosity()["federation"],
        "complement": complement_pack(paths),
        "bench_defs": [dict(a) for a in AXES_META if a.get("def")],
        "bench_cite": "openrouter.ai model Benchmarks tab · Artificial Analysis",
        "usage_cookbook": (
            "https://openrouter.ai/docs/cookbook/administration/usage-accounting"
        ),
        "mcp_cookbook": (
            "https://openrouter.ai/docs/cookbook/coding-agents/mcp-servers"
        ),
        "hermes": hermes_probe(),
        "agents": _agents_fold(),
    }


def _agents_fold() -> dict:
    try:
        from cosmos_cred_kit import agents_snapshot
        return agents_snapshot()
    except Exception as e:  # noqa: BLE001
        return {"kind": "BROKE", "detail": f"{type(e).__name__}: {e}"[:200]}


def hermes_probe() -> dict:
    """OpenRouter cookbook: hermes as a CLI hand. Does not read the key."""
    bin_path = shutil.which("hermes") or shutil.which("hermes.exe")
    home = Path.home() / ".hermes"
    env = home / ".env"
    cfg = home / "config.yaml"
    return {
        "bin": bin_path,
        "kind": "OK" if bin_path else "NO_SOURCE",
        "env_present": env.is_file(),
        "config_present": cfg.is_file(),
        "cookbook": "https://openrouter.ai/docs/cookbook/coding-agents/hermes-integration",
        "note": "Keith sets OPENROUTER_API_KEY in ~/.hermes/.env (hermes config set). "
                "COSMOS does not paste it. Fallback seats are Model Rater DEFAULT+2, "
                "not Hermes swapping mid-session. Rotator and pareto-code cannot sit.",
    }


def _selftest() -> int:
    import tempfile
    from cosmos_kernel import install
    from cosmos_paths import CosmosPaths
    from cosmos_openrouter_rail import DEFAULT_MODEL, GEMMA_31B

    results = []

    def check(label, fn):
        try:
            results.append((label, bool(fn()), ""))
        except Exception as e:  # noqa: BLE001
            results.append((label, False, f"{type(e).__name__}: {e}"))

    td = Path(tempfile.mkdtemp(prefix="cosmos_model_rater_"))
    root = install(td / "live", tree_id="spike-model-rater")
    paths = CosmosPaths(root)

    def fake_http(method, path, body=None):
        if method == "GET" and "benchmarks" in str(path):
            return 200, {}, {"data": [
                {"source": "artificial-analysis",
                 "model_permaslug": "anthropic/claude-opus-5",
                 "intelligence_index": 90.0, "coding_index": 88.0,
                 "agentic_index": 85.0, "output_speed": 42.0,
                 "gpqa_diamond": 86.7, "hle": 28.4, "ifbench": 81.4,
                 "scicode": 40.3, "terminal_bench_hard": 36.4},
                {"source": "artificial-analysis",
                 "model_permaslug": DEFAULT_MODEL.split(":")[0],
                 "intelligence_index": 40.0, "coding_index": 55.0,
                 "agentic_index": 30.0},
            ], "meta": {"source": "artificial-analysis"}}
        if method == "GET" and "category=programming" in str(path):
            return 200, {}, {"data": [
                {"id": "anthropic/claude-opus-5", "name": "Claude Opus 5"},
            ]}
        if method == "GET" and str(path).endswith("/models"):
            return 200, {}, {"data": [
                {"id": DEFAULT_MODEL, "name": "Gemma 4 26B A4B (free)",
                 "context_length": 262144,
                 "architecture": {"input_modalities": ["text", "file", "image"],
                                  "output_modalities": ["text"]},
                 "pricing": {"prompt": "0", "completion": "0", "request": "0"},
                 "benchmarks": {"artificial_analysis": {
                     "intelligence_index": 40.0, "coding_index": 55.0,
                     "agentic_index": 30.0}},
                 "supported_parameters": ["temperature"],
                 "reasoning": {"default_enabled": False}},
                {"id": GEMMA_31B, "name": "Gemma 4 31B (free)",
                 "context_length": 262144,
                 "architecture": {"input_modalities": ["text"],
                                  "output_modalities": ["text"]},
                 "pricing": {"prompt": "0", "completion": "0"},
                 "benchmarks": {"artificial_analysis": {
                     "intelligence_index": 50.0, "coding_index": 60.0,
                     "agentic_index": 40.0}},
                 "supported_parameters": ["reasoning"],
                 "reasoning": {"default_enabled": True}},
                {"id": "anthropic/claude-opus-5", "name": "Claude Opus 5",
                 "created": 1_800_000_000,
                 "context_length": 1000000,
                 "architecture": {"input_modalities": ["text"],
                                  "output_modalities": ["text"]},
                 "pricing": {"prompt": "0.000015", "completion": "0.000075"},
                 "benchmarks": {"artificial_analysis": {
                     "intelligence_index": 90.0, "coding_index": 88.0,
                     "agentic_index": 85.0}},
                 "supported_parameters": ["tools", "reasoning"]},
                {"id": "openrouter/free", "name": "Free rotator",
                 "context_length": 200000,
                 "architecture": {"input_modalities": ["text"],
                                  "output_modalities": ["text"]},
                 "pricing": {"prompt": "0", "completion": "0"}},
            ]}
        return 404, {}, {"error": path}

    rec = refresh(paths, http=fake_http)
    check("refresh stores 4 vendor rows including rotator",
          lambda: rec["n"] == 4 and rec["http"] == 200)
    check("Q is the mean of vendor INT/COD/AGT, never invented",
          lambda: any(m["id"] == "anthropic/claude-opus-5"
                      and m.get("quality") == round((90+88+85)/3, 1)
                      and m.get("quality_n") == 3
                      for m in rec["models"]))
    check("sort=quality puts highest Q first",
          lambda: snapshot(paths, sort="quality")["models"][0]["id"]
          == "anthropic/claude-opus-5")
    gem_free = next((m for m in rec["models"] if m["id"] == DEFAULT_MODEL), {})
    check(":free variant inherits AA indices from the base slug",
          lambda: gem_free.get("intelligence") == 40.0
          and gem_free.get("quality") is not None)
    snap = snapshot(paths, sort="intelligence")
    check("query drops rotator from assignable list",
          lambda: all(m["id"] != "openrouter/free" for m in snap["models"])
          and snap["n_catalog"] == 4)
    check("intelligence sort puts Opus first (vendor AA index)",
          lambda: snap["models"][0]["id"] == "anthropic/claude-opus-5"
          and snap["models"][0]["intelligence"] == 90.0)
    check("Gemma 26B types include images and free",
          lambda: "images" in rec["models"][0]["types"]
          and "free" in rec["models"][0]["types"])
    docs = snapshot(paths, type_name="docs")
    check("docs cut is text out + text/file/image in (OpenRouter cards filter)",
          lambda: docs["catalog_cut"]["url"].endswith("input_modalities=text,file,image")
          and all("docs" in (m.get("types") or []) for m in docs["models"])
          and any(m["id"] == DEFAULT_MODEL for m in docs["models"])
          and all(m["id"] != "anthropic/claude-opus-5" for m in docs["models"]))
    prog = snapshot(paths, category="programming", sort="recency")
    check("table cut tags programming from vendor category GET, does not invent weekly tokens",
          lambda: prog["table_cut"]["fmt"] == "table"
          and prog["table_cut"]["category"] == "programming"
          and all("programming" in (m.get("categories") or []) for m in prog["models"])
          and any(m["id"] == "anthropic/claude-opus-5" for m in prog["models"])
          and all(m["id"] != DEFAULT_MODEL for m in prog["models"]))
    est = estimate(rec, "anthropic/claude-opus-5", 1000, 500)
    check("cost estimate uses per-token * 1e6 card",
          lambda: abs(est["usd"] - (1000 * 15 / 1e6 + 500 * 75 / 1e6)) < 1e-9)
    seats = assign_seat(paths, "crucible", "plaintiff", DEFAULT_MODEL)
    check("Crucible plaintiff seat stores named Gemma 4",
          lambda: any(s["seat"] == "plaintiff" and s["model"] == DEFAULT_MODEL
                      for s in seats["seats"]))
    refused = False
    try:
        assign_seat(paths, "motif", "lane_a", "openrouter/free")
    except ModelRaterError as e:
        refused = e.kind == "REFUSED"
    check("rotator cannot sit a MOTIF lane", lambda: refused)
    check("default seats include MOTIF lanes and Crucible roles",
          lambda: { (s["profile"], s["seat"]) for s in default_seats() }
          >= {("motif", "lane_a"), ("motif", "lane_b"),
              ("crucible", "plaintiff"), ("crucible", "judge")})
    check("roles enumerate BUILD 1-5, RESEARCH search agents, CRITICS 1-5, ORC, Crucible",
          lambda: {(s["profile"], s["seat"]) for s in default_seats()}
          >= {("motif", "lane_a"), ("motif", "lane_b"), ("motif", "build_3"),
              ("motif", "build_4"), ("motif", "build_5"),
              ("motif", "research_sgh"), ("motif", "research_gem"),
              ("motif", "research_pplx"), ("motif", "research_bing"),
              ("motif", "research_chatgpt"),
              ("motif", "critic_plaintiff"), ("motif", "critic_4"),
              ("motif", "critic_5"),
              ("forge", "adv_1"), ("forge", "adv_2"), ("forge", "ccr"),
              ("openwork", "orc"),
              ("crucible", "plaintiff")})
    found = scan_roles(paths, q="ORC")
    check("role search finds OpenWork ORC",
          lambda: found["n"] >= 1
          and any(r["seat"] == "orc" and r["profile"] == "openwork"
                  for r in found["roles"]))
    fb = assign_seat(paths, "motif", "lane_a", CCR_MODEL, via="cli:grok",
                     model_2="composer-2.5", via_2="cursor-api",
                     model_3="anthropic/claude-opus-5", via_3="cursor-api",
                     effort="high", cap_usd=8)
    check("DEFAULT + secondary + tertiary fallback, via, effort, budget persist",
          lambda: any(s["seat"] == "lane_a"
                      and s.get("model") == CCR_MODEL
                      and s.get("model_2") == "composer-2.5"
                      and s.get("model_3") == "anthropic/claude-opus-5"
                      and s.get("via") == "cli:grok"
                      and s.get("via_2") == "cursor-api"
                      and s.get("via_3") == "cursor-api"
                      and s.get("effort") == "high"
                      and s.get("cap_usd") == 8
                      for s in fb["seats"]))
    mcp = assign_seat(paths, "openwork", "orc", CCR_MODEL, via="mcp:openwork")
    check("ORC can sit MCP · OpenWork",
          lambda: any(s["seat"] == "orc" and s.get("via") == "mcp:openwork"
                      for s in mcp["seats"]))
    pol = set_policy(paths, favored_families=["grok"],
                     banned_models=["anthropic/claude-opus-5"])
    check("favored family grok / banned model persist",
          lambda: "grok" in (pol.get("policy") or {}).get("favored_families", [])
          and "anthropic/claude-opus-5" in (pol.get("policy") or {}).get(
              "banned_models", []))
    banned = False
    try:
        assign_seat(paths, "crucible", "defense", "anthropic/claude-opus-5")
    except ModelRaterError as e:
        banned = e.kind == "REFUSED"
    check("banned model cannot sit a role", lambda: banned)
    set_policy(paths, banned_models=[])
    office = next((m for m in rec["models"] if m["id"] == "anthropic/claude-opus-5"), {})
    check("office / file / stability are UNMEASURED, never invented",
          lambda: office.get("office") is None
          and office.get("file") is None
          and office.get("stability") is None)
    check("speed copies vendor output_speed, recency copies created",
          lambda: office.get("speed") == 42.0
          and office.get("created") == 1_800_000_000)
    check("OpenRouter AA benches copy GPQA/HLE/IFBench/SciCode/Terminal-Bench when sent",
          lambda: office.get("gpqa") == 86.7
          and office.get("hle") == 28.4
          and office.get("ifbench") == 81.4
          and office.get("scicode") == 40.3
          and office.get("terminal_bench") == 36.4
          and office.get("omniscience") is None)
    check("snapshot carries metric definitions, never invents missing benches",
          lambda: any(d.get("id") == "gpqa" and "Graduate-level" in (d.get("def") or "")
                      for d in snapshot(paths, limit=1).get("bench_defs") or [])
          and "Artificial Analysis" in (snapshot(paths, limit=1).get("bench_cite") or "")
          and len(snapshot(paths, limit=1).get("bench_defs") or []) >= 11)
    blend = blended_per_m(office)
    check("blended cost is 75% in / 25% out per M",
          lambda: abs(blend - (0.75 * 15 + 0.25 * 75)) < 1e-9
          and office.get("blended_per_m") == blend)
    check("INT/$ COD/$ AGT/$ Q/$ are quality / blended; free is UNMEASURED",
          lambda: office.get("quality_per_cost") == _per_cost(office.get("quality"), blend)
          and office.get("intelligence_per_cost") == _per_cost(90.0, blend)
          and gem_free.get("blended_per_m") == 0
          and gem_free.get("quality_per_cost") is None)
    check("porosity is UNMEASURED until an observation is recorded",
          lambda: snapshot(paths, limit=80)["models"][0].get("porosity") is None
          and snapshot(paths, limit=1)["porosity"]["kind"] == "NO_HOST")
    def _empty_complement_ok():
        from cosmos_porosity import SCHEMA as poro_schema
        from cosmos_porosity import obs_path as poro_obs, store_dir as poro_dir
        rec = snapshot(paths, limit=1)
        c = rec.get("complement") or {}
        return (
            c.get("kind") == "UNMEASURED"
            and c.get("complement_kind") == "UNMEASURED"
            and c.get("n_obs") == 0
            and c.get("n_pairs") == 0
            and c.get("schema") == poro_schema
            and c.get("tensors_shape") == "tensors[agent][vs][axis]"
            and c.get("last_obs") == {}
            and set(c) == {
                "schema", "kind", "n_obs", "n_pairs",
                "tensors_shape", "last_obs", "complement_kind",
            }
            and not poro_obs(paths).exists()
            and not poro_dir(paths).exists()
        )
    check("empty pair store is UNMEASURED and catalog GET does not mkdir",
          _empty_complement_ok)
    por = record_porosity(paths, "anthropic/claude-opus-5", 2.0, 10)
    check("porosity = loc_per_100 * severity; federation does not invent",
          lambda: por["last"]["porosity"] == 20.0
          and por["fold"]["n_local"] == 1
          and por["fold"]["n_federated"] == 0
          and any(m.get("id") == "anthropic/claude-opus-5"
                  and m.get("porosity") == 20.0
                  for m in snapshot(paths, limit=80)["models"]))
    por_stamped = record_porosity(
        paths, "anthropic/claude-opus-5", 1.0, 5,
        agent_id="anthropic/claude-opus-5", action="observe",
        authority="ccr:g46",
    )
    check("scalar porosity carries Irbe agent_id / action / authority",
          lambda: por_stamped["last"]["agent_id"] == "anthropic/claude-opus-5"
          and por_stamped["last"]["action"] == "observe"
          and por_stamped["last"]["authority"] == "ccr:g46")
    check("MCP is a via kind",
          lambda: any(v["id"] == "mcp:openwork" and v["kind"] == "MCP"
                      for v in VIA_OPTIONS))
    check("snapshot names MOTIF step 1 PROBLEM STATEMENT / STATED GOAL",
          lambda: snapshot(paths, limit=1).get("motif_step_1")
          == "PROBLEM STATEMENT / STATED GOAL")
    caps = set_model_cap(paths, "anthropic/claude-opus-5", 12.5)
    check("per-model cap stores USD; 0 clears it (not the Core spend gate)",
          lambda: caps.get("model_caps", {}).get("anthropic/claude-opus-5") == 12.5
          and set_model_cap(paths, "anthropic/claude-opus-5", 0
                            ).get("model_caps", {}).get("anthropic/claude-opus-5") is None)
    check("Forge CCr seat is locked in defaults",
          lambda: any(s["profile"] == "forge" and s["seat"] == "ccr"
                      for s in default_seats()))
    check("forge.ccr occupancy defaults to grok-4.6",
          lambda: any(s["profile"] == "forge" and s["seat"] == "ccr"
                      and s["model"] == CCR_MODEL
                      for s in load_seats(paths)["seats"]))
    ccr_blank = False
    try:
        assign_seat(paths, "forge", "ccr", "")
    except ModelRaterError as e:
        ccr_blank = e.kind == "REFUSED"
    check("forge.ccr cannot be unassigned", lambda: ccr_blank)
    added = add_adversary(paths, model="anthropic/claude-opus-5")
    check("add_adversary creates forge.adv_3 with named model",
          lambda: any(s["profile"] == "forge" and s["seat"] == "adv_3"
                      and s["model"] == "anthropic/claude-opus-5"
                      for s in added["seats"]))
    groq = add_adversary(paths, via="groq-api")
    check("add_adversary via=groq-api stores the rail, not a silent OpenRouter default",
          lambda: any(s["profile"] == "forge" and s.get("via") == "groq-api"
                      for s in groq["seats"]))
    bad_via = False
    try:
        add_adversary(paths, via="openrouter/free")
    except ModelRaterError as e:
        bad_via = e.kind == "BAD_INPUT"
    check("rotator is not a via", lambda: bad_via)
    ccr_via = assign_seat(paths, "forge", "ccr", CCR_MODEL, via="cli:grok")
    check("forge.ccr can sit cli:grok with grok-4.6 (not an OpenRouter card)",
          lambda: any(s["seat"] == "ccr" and s.get("via") == "cli:grok"
                      and s.get("model") == CCR_MODEL
                      for s in ccr_via["seats"]))
    locked = False
    try:
        remove_adversary(paths, "ccr")
    except ModelRaterError as e:
        locked = e.kind == "REFUSED"
    check("CCr seat cannot be removed", lambda: locked)
    gone = remove_adversary(paths, "adv_3")
    check("remove_adversary drops extra coder and does not resurrect it",
          lambda: not any(s.get("seat") == "adv_3" for s in gone["seats"])
          and not any(s.get("seat") == "adv_3" for s in load_seats(paths)["seats"]))
    je = save_job_estimate(paths, 1000, 500, override=True)
    snap2 = snapshot(paths)
    check("job estimate override autocalcs cost per assigned Forge seat",
          lambda: je["override"] is True
          and snap2["job_estimate"]["tokens_in"] == 1000
          and any(L.get("seat") == "ccr" for L in snap2["job_costs"]["lines"]))
    reset = reset_job_estimate(paths)
    check("reset restores CCr initial 24000/8000",
          lambda: reset["tokens_in"] == CCR_INITIAL_IN
          and reset["tokens_out"] == CCR_INITIAL_OUT
          and reset["override"] is False)
    stale = load_catalog(paths)
    check("fresh catalog is not stale", lambda: stale["stale"] is False)
    check("cli:hermes is a CLI via; OpenRouter cookbook; not a second Core",
          lambda: any(v["id"] == "cli:hermes" and v["kind"] == "CLI"
                      for v in VIA_OPTIONS)
          and "cookbook" in (snapshot(paths, limit=1).get("hermes") or {})
          and snapshot(paths, limit=1)["hermes"]["kind"] in ("OK", "NO_SOURCE"))
    hermes_ok = False
    try:
        assign_seat(paths, "forge", "adv_1", CCR_MODEL, via="cli:hermes")
        hermes_ok = True
    except ModelRaterError:
        hermes_ok = False
    check("a Forge seat can sit cli:hermes", lambda: hermes_ok)
    pareto = False
    try:
        assign_seat(paths, "forge", "adv_2", "openrouter/pareto-code")
    except ModelRaterError as e:
        pareto = e.kind == "REFUSED"
    check("OpenRouter pareto-code rotator cannot sit a seat", lambda: pareto)

    bad = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (catalog+seats+estimate; rotator REFUSED)"
          % ("PASS" if not bad else "FAIL", len(results)))
    return 0 if not bad else 1


def main() -> int:
    ap = argparse.ArgumentParser(prog="cosmos_model_rater")
    ap.add_argument("--root", default=None)
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.root:
        print(json.dumps({"ok": False, "kind": "BAD_ROOT",
                          "error": "--root is required"}, indent=1))
        return 2
    from cosmos_paths import CosmosPaths
    paths = CosmosPaths(a.root)
    if a.refresh:
        rec = refresh(paths)
        print(json.dumps({
            "ok": True, "n": rec["n"], "fetched_at": rec["fetched_at"],
            "http": rec["http"],
        }, indent=1))
        return 0
    snap = snapshot(paths)
    print(json.dumps({
        "ok": True, "n": snap["n"], "n_catalog": snap["n_catalog"],
        "stale": snap["stale"], "fetched_at": snap["fetched_at"],
        "seats": snap["seats"],
    }, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
