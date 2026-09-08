#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_model_rater — OpenRouter catalog + seat assignments for cDeck.

Pulls GET /api/v1/models (rates, modalities, Artificial Analysis indices)
into a local projection. Daily refresh or refresh-on-open. Does NOT call
the rotating openrouter/free router (H3). Seat assign is explicit.

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
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

SCHEMA = "cosmos-model-rater/1"
WORKER = "cosmos-model-rater"
TTL_S = 24 * 3600
CATALOG_NAME = "catalog.json"
SEATS_NAME = "seats.json"
ROTATING = frozenset({
    "openrouter/free", "openrouter/auto", "openrouter/free:free",
})
# CCr initial for a MOTIF BUILD work-order: ~canon+files+brief in, patch out.
# Override on the Forge pane if the job is a one-file fix or a full-tree rewrite.
CCR_INITIAL_IN = 24000
CCR_INITIAL_OUT = 8000
JOB_EST_NAME = "job_estimate.json"
MAX_ADV = 24
LOCKED_SEATS = frozenset({
    ("forge", "ccr"),
    ("motif", "lane_a"), ("motif", "lane_b"),
    ("motif", "research_sgh"), ("motif", "research_gem"),
    ("motif", "critic_plaintiff"), ("motif", "critic_defense"),
    ("motif", "critic_judge"),
    ("crucible", "plaintiff"), ("crucible", "defense"), ("crucible", "judge"),
    ("dispatch", "coding"), ("dispatch", "ssa"),
})
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
    {"id": "openrouter-api", "label": "API · OpenRouter (incl. :free)", "kind": "API"},
    {"id": "groq-api", "label": "API · GroqCloud", "kind": "API"},
    {"id": "gem-api", "label": "API · Vertex Joanna", "kind": "API"},
    {"id": "vertex-coding", "label": "API · Vertex $300", "kind": "API"},
    {"id": "oa-api", "label": "API · OpenAI", "kind": "API"},
    {"id": "sgh-api", "label": "API · xAI console", "kind": "API"},
    {"id": "cursor-api", "label": "API · Cursor", "kind": "API"},
    {"id": "dom", "label": "DOM · browser", "kind": "DOM"},
)
VIA_IDS = frozenset(v["id"] for v in VIA_OPTIONS)
DEFAULT_SEATS = (
    {"profile": "forge", "seat": "ccr", "group": "Forge",
     "label": "CCr — Chief Coder", "model": CCR_MODEL, "via": "cli:grok",
     "locked": True},
    {"profile": "forge", "seat": "adv_1", "group": "Forge",
     "label": "Forge — Adversarial coder 1", "model": "", "via": "openrouter-api"},
    {"profile": "forge", "seat": "adv_2", "group": "Forge",
     "label": "Forge — Adversarial coder 2", "model": "", "via": "openrouter-api"},
    {"profile": "motif", "seat": "research_sgh", "group": "MOTIF RESEARCH",
     "label": "MOTIF RESEARCH — SGH", "model": CCR_MODEL, "via": "cli:grok",
     "locked": True},
    {"profile": "motif", "seat": "research_gem", "group": "MOTIF RESEARCH",
     "label": "MOTIF RESEARCH — GEM", "model": "gemini-2.5-flash",
     "via": "gem-api", "locked": True},
    {"profile": "motif", "seat": "lane_a", "group": "MOTIF BUILD",
     "label": "MOTIF BUILD — Adversarial coder 1", "model": CCR_MODEL,
     "via": "cli:grok", "locked": True},
    {"profile": "motif", "seat": "lane_b", "group": "MOTIF BUILD",
     "label": "MOTIF BUILD — Adversarial coder 2", "model": "composer-2.5",
     "via": "cursor-api", "locked": True},
    {"profile": "motif", "seat": "build_3", "group": "MOTIF BUILD",
     "label": "MOTIF BUILD — Adversarial coder 3", "model": "",
     "via": "openrouter-api"},
    {"profile": "motif", "seat": "critic_plaintiff", "group": "MOTIF CRITICS",
     "label": "MOTIF CRITICS — Plaintiff", "model": "", "via": "openrouter-api",
     "locked": True},
    {"profile": "motif", "seat": "critic_defense", "group": "MOTIF CRITICS",
     "label": "MOTIF CRITICS — Defense", "model": "", "via": "gem-api",
     "locked": True},
    {"profile": "motif", "seat": "critic_judge", "group": "MOTIF CRITICS",
     "label": "MOTIF CRITICS — Judge", "model": CCR_MODEL, "via": "cli:grok",
     "locked": True},
    {"profile": "crucible", "seat": "plaintiff", "group": "Crucible",
     "label": "Crucible — Plaintiff's attorney", "model": "", "locked": True},
    {"profile": "crucible", "seat": "defense", "group": "Crucible",
     "label": "Crucible — Defense attorney", "model": "", "locked": True},
    {"profile": "crucible", "seat": "judge", "group": "Crucible",
     "label": "Crucible — Judge", "model": "", "locked": True},
    {"profile": "dispatch", "seat": "coding", "group": "Dispatch",
     "label": "Dispatch — coding", "model": "", "locked": True},
    {"profile": "dispatch", "seat": "ssa", "group": "Dispatch",
     "label": "Dispatch — cheap reasoning / SSA", "model": "", "locked": True},
)
SORT_KEYS = frozenset({
    "price", "intelligence", "coding", "agentic", "quality", "q",
    "name", "context", "id",
})
QUALITY_AXES = ("intelligence", "coding", "agentic")
TYPE_KEYS = frozenset({
    "coding", "reasoning", "images", "audio", "video", "chat", "free",
})


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


def _types(row: dict) -> list[str]:
    arch = row.get("architecture") if isinstance(row.get("architecture"), dict) else {}
    ins = [str(x).lower() for x in (arch.get("input_modalities") or [])]
    outs = [str(x).lower() for x in (arch.get("output_modalities") or [])]
    params = [str(x).lower() for x in (row.get("supported_parameters") or [])]
    aa = ((row.get("benchmarks") or {}) if isinstance(row.get("benchmarks"), dict) else {}
          ).get("artificial_analysis") or {}
    kinds = []
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
    return {
        "id": mid,
        "name": str(raw.get("name") or mid),
        "context": int(raw.get("context_length") or 0),
        "prompt_per_m": round(prompt * 1_000_000, 6),
        "completion_per_m": round(completion * 1_000_000, 6),
        "request_usd": request,
        "intelligence": _f(aa.get("intelligence_index")),
        "coding": _f(aa.get("coding_index")),
        "agentic": _f(aa.get("agentic_index")),
        "quality": None,
        "quality_n": 0,
        "quality_from": None,
        "types": _types(raw),
        "reasoning": bool(isinstance(raw.get("reasoning"), dict)
                          and raw["reasoning"].get("default_enabled")),
        "rotator": mid.lower() in ROTATING,
    }


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
        hit = False
        for src, dst in (("intelligence_index", "intelligence"),
                         ("coding_index", "coding"),
                         ("agentic_index", "agentic")):
            v = _f(raw.get(src))
            if v is not None and m.get(dst) is None:
                m[dst] = v
                hit = True
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
        for k in QUALITY_AXES:
            if m.get(k) is None and src.get(k) is not None:
                m[k] = src[k]
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
            "via": str(src.get("via") or ""),
            "cap_usd": src.get("cap_usd"),
            "assigned_at": src.get("assigned_at"),
        })
    rec["seats"] = merged
    rec["schema"] = SCHEMA
    rec.setdefault("model_caps", {})
    if not isinstance(rec.get("model_caps"), dict):
        rec["model_caps"] = {}
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
    rec = {
        "schema": SCHEMA,
        "fetched_at": _iso_now(),
        "fetched_at_unix": time.time(),
        "http": status,
        "benchmarks_http": b_status,
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


def _sort_key(row: dict, sort: str):
    if sort == "price":
        return (row.get("prompt_per_m") or 0) + (row.get("completion_per_m") or 0)
    if sort in ("intelligence", "coding", "agentic", "quality", "q"):
        key = "quality" if sort in ("quality", "q") else sort
        v = row.get(key)
        return -1.0 if v is None else float(v)
    if sort == "context":
        return int(row.get("context") or 0)
    if sort == "name":
        return str(row.get("name") or "").lower()
    return str(row.get("id") or "")


def query_models(catalog: dict, *, sort="price", desc=False, type_name="",
                 q="", limit=400) -> list[dict]:
    sort = sort if sort in SORT_KEYS else "price"
    rows = list(catalog.get("models") or [])
    ql = str(q or "").strip().lower()
    tn = str(type_name or "").strip().lower()
    out = []
    for r in rows:
        if r.get("rotator"):
            continue
        if tn and tn not in (r.get("types") or []):
            continue
        if ql:
            blob = (str(r.get("id") or "") + " " + str(r.get("name") or "")).lower()
            if ql not in blob:
                continue
        out.append(r)
    if sort in ("intelligence", "coding", "agentic", "quality", "q"):
        axis = "quality" if sort in ("quality", "q") else sort
        out.sort(key=lambda r, a=axis: (
            r.get(a) is None,
            (-(r.get(a) or 0.0)) if not desc else (r.get(a) or 0.0),
        ))
    elif sort == "price":
        out.sort(key=lambda r: _sort_key(r, "price"), reverse=bool(desc))
    elif sort == "context":
        out.sort(key=lambda r: int(r.get("context") or 0), reverse=not bool(desc))
    else:
        out.sort(key=lambda r: str(r.get("name") or r.get("id") or "").lower(),
                 reverse=bool(desc))
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


def assign_seat(paths, profile: str, seat: str, model: str, via: str = "",
                cap_usd=None) -> dict:
    profile = str(profile or "").strip().lower()
    seat = str(seat or "").strip().lower()
    model = str(model or "").strip()
    if not profile or not seat:
        raise ModelRaterError("BAD_INPUT", "profile and seat are required")
    if (profile, seat) == ("forge", "ccr") and not model:
        raise ModelRaterError("REFUSED", "forge.ccr occupancy is grok-4.6 — cannot unassign")
    if model.lower() in ROTATING:
        raise ModelRaterError("REFUSED", f"rotator id {model!r} is not assignable")
    via_n = normalize_via(via) if via else ""
    rec = load_seats(paths)
    found = False
    for row in rec["seats"]:
        if row["profile"] == profile and row["seat"] == seat:
            row["model"] = model
            row["assigned_at"] = _iso_now() if model else None
            if via_n:
                row["via"] = via_n
            if cap_usd is not None and cap_usd != "":
                n = _clamp_usd(cap_usd, 0.0)
                if n == 0:
                    row.pop("cap_usd", None)
                else:
                    row["cap_usd"] = n
            found = True
            break
    if not found:
        raise ModelRaterError("BAD_INPUT", f"unknown seat {profile}.{seat}")
    occupancy = {CCR_MODEL, "composer-2.5", "claude-opus-5"}
    via_now = via_n or next(
        (str(s.get("via") or "") for s in rec["seats"]
         if s.get("profile") == profile and s.get("seat") == seat),
        "")
    cli_or_dom = via_now.startswith("cli:") or via_now == "dom"
    if model and model not in occupancy and not cli_or_dom:
        cat = load_catalog(paths)
        ids = {m.get("id") for m in cat.get("models") or []}
        if cat.get("n") and model not in ids:
            raise ModelRaterError("BAD_INPUT", f"model {model!r} not in local catalog")
    return save_seats(paths, rec)


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
             limit=400, refresh_if_stale=False, http=None) -> dict:
    cat = load_catalog(paths)
    refreshed = False
    if refresh_if_stale and (cat.get("stale") or not cat.get("n")):
        cat = refresh(paths, http=http)
        refreshed = True
    seats = load_seats(paths)
    models = query_models(cat, sort=sort, desc=desc, type_name=type_name,
                          q=q, limit=limit)
    job = load_job_estimate(paths)
    costs = job_costs(cat, seats.get("seats") or [],
                      job["tokens_in"], job["tokens_out"])
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
        "models": models,
        "seats": seats.get("seats") or default_seats(),
        "model_caps": seats.get("model_caps") or {},
        "job_estimate": job,
        "job_costs": costs,
        "ccr_initial": {"tokens_in": CCR_INITIAL_IN, "tokens_out": CCR_INITIAL_OUT},
        "axes": ["quality", "intelligence", "coding", "agentic", "price"],
        "n_quality": cat.get("n_quality") or sum(
            1 for m in (cat.get("models") or []) if m.get("quality") is not None),
        "ttl_s": TTL_S,
        "max_adv": MAX_ADV,
        "via_options": [dict(v) for v in VIA_OPTIONS],
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
                 "agentic_index": 85.0},
                {"source": "artificial-analysis",
                 "model_permaslug": DEFAULT_MODEL.split(":")[0],
                 "intelligence_index": 40.0, "coding_index": 55.0,
                 "agentic_index": 30.0},
            ], "meta": {"source": "artificial-analysis"}}
        if method == "GET" and str(path).endswith("/models"):
            return 200, {}, {"data": [
                {"id": DEFAULT_MODEL, "name": "Gemma 4 26B A4B (free)",
                 "context_length": 262144,
                 "architecture": {"input_modalities": ["text", "image"],
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
    check("roles enumerate BUILD adversarial 1-3, RESEARCH, CRITICS, Crucible plaintiff",
          lambda: {(s["profile"], s["seat"]) for s in default_seats()}
          >= {("motif", "lane_a"), ("motif", "lane_b"), ("motif", "build_3"),
              ("motif", "research_sgh"), ("motif", "critic_plaintiff"),
              ("forge", "adv_1"), ("forge", "adv_2"),
              ("crucible", "plaintiff")})
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
