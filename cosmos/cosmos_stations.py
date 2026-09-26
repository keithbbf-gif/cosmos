#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wish queue and station seats.

ORC appends wishes. It does not rewrite the log. When the queue reaches
the floor, WOMBAT can be summoned in the harness already chosen on the
Model Rater — or the deck offers the rater link and the same dropdown.

One seat schema covers the prompt writer, WOMBAT, each CCrew coder, the
Judge, CCr, ORC, and the Cursor checker. CCrew is not called until the
board row has the shared prompt, the cache-tagged preload, and every
coder's scores. The Judge waits for 30 complete sets. The
axis is quality per cost. Quality rises along the pipe: a top-tier
prompt writer, a mixed CCrew, a top-tier Judge, a top-tier CCr.

The Judge rotates inside its pool. The Final is the other quality grade.
Those two stay different families. Auto-pick skips the other's family.
A pilot may seat the same family anyway, and that seats with a warning.
CCr is the pen and does not grade. The Cursor agent is a different
family from the coders when one is available: Composer, Grok, Opus, SOL,
Luna, Terra.

No model is executed here.

    py -3.14 cosmos\\cosmos_stations.py --selftest
"""
from __future__ import annotations

import json
from datetime import datetime

SCHEMA = "cosmos-stations/1"
WISH_FLOOR = 50
ORDER_FLOOR = 40
JUDGE_FLOOR = 30
# Judged KEEPs batched before the final checker is summoned. Ephemeral.
FINAL_FLOOR = 10
# Parallel coders on one work order. A Judge set still scores at 3 ready replies.
CREW_SIZE = 4
# Judge pool, best first. GLM 5.3 full is 74.8. Luna Flex is 71.4.
JUDGE_ORDER = ("glm53", "luna", "ds0731", "qwen27")
IDLE_MINUTES = 30
AXIS = "quality_per_cost"
SEAT_KEYS = (
    "station", "model", "family", "label", "via", "harness",
    "axis", "quality", "cost_per_m", "context", "source", "routing",
)
BOARD_FIELDS = ("order_id", "set_id", "prompt", "preload", "coders")
CODER_FIELDS = (
    "model", "family", "coding", "porosity", "ortho",
    "context", "latency", "scars", "needs", "duds",
)
# Roster order is the offline stand-in for a catalog score.
# A Model Rater row with coding + price replaces it.
CANDIDATES = (
    {"key": "luna", "label": "Luna 6", "model": "openai/gpt-5.6-luna",
     "family": "openai", "tier": "top", "rank": 6,
     "via": "openrouter-api", "harness": "codex exec",
     "note": "Flex $0.10/$0.60 per 1M. Page $0.20/$1.20."},
    {"key": "grok47", "label": "Grok 4.7", "model": "grok-4.7",
     "family": "xai", "tier": "top", "rank": 5,
     "via": "cli:grok", "harness": "cli:grok"},
    {"key": "gf38", "label": "Gemini 3.8 Flash", "model": "google/gemini-3.8-flash",
     "family": "google", "tier": "top", "rank": 4,
     "via": "gem-api", "harness": "vertex",
     "note": "Kelly promo $0.75/$3.75 per 1M. Dearer than Luna Flex."},
    {"key": "muse13", "label": "Muse Spark 1.3", "model": "meta/muse-spark-1.3-contributor",
     "family": "meta", "tier": "mid", "rank": 3,
     "via": "opencode", "harness": "opencode",
     "note": "ORC. Free on OpenCode, running on OpenWork."},
    {"key": "glm53", "label": "GLM 5.3", "model": "z-ai/glm-5.3",
     "family": "zai", "tier": "check", "rank": 8,
     "via": "openrouter-api", "harness": "cli:pi",
     "note": "Coding 74.8. $0.5625/$2.50. Not the Flash coder."},
    {"key": "glm", "label": "GLM 5.3 Flash", "model": "z-ai/glm-5.3-flash",
     "family": "zai", "tier": "mix", "rank": 2,
     "via": "openrouter-api", "harness": "cli:pi"},
    {"key": "ds0731", "label": "DSV0731", "model": "deepseek/deepseek-v4-flash-0731",
     "family": "deepseek", "tier": "mix", "rank": 1,
     "via": "openrouter-api", "harness": "cli:dsh"},
    {"key": "qwen27", "label": "Qwen3.8 27B", "model": "qwen/qwen3.8-27b:free",
     "family": "qwen", "tier": "check", "rank": 0,
     "via": "openrouter-api", "harness": "openrouter",
     "note": "Free. Coding 68.1. Context 262144."},
    {"key": "inkling", "label": "Inkling Small",
     "model": "thinkingmachines/inkling-small:free",
     "family": "thinkingmachines", "tier": "pen", "rank": 0,
     "via": "openrouter-api", "harness": "openrouter",
     "note": "Free pen. Coding 52.9. Context 1048576. Does not grade."},
    {"key": "sol6", "label": "SOL 6", "model": "openai/gpt-5.6-sol",
     "family": "openai", "tier": "check", "rank": 7,
     "via": "openrouter-api", "harness": "codex exec",
     "note": "Flex $1/$5, cache $0.10. Coding 77.4."},
)
CURSOR_OPTIONS = (
    {"key": "composer", "label": "Composer", "model": "composer-2.5",
     "family": "composer", "via": "cursor-api", "harness": "cursor"},
    {"key": "grok", "label": "Grok", "model": "grok-4.7",
     "family": "xai", "via": "cursor-api", "harness": "cursor"},
    {"key": "opus", "label": "Opus", "model": "claude-opus-5",
     "family": "anthropic", "via": "cursor-api", "harness": "cursor"},
    {"key": "sol", "label": "SOL", "model": "openai/gpt-5.6-sol",
     "family": "openai", "via": "cursor-api", "harness": "cursor"},
    {"key": "luna", "label": "Luna", "model": "openai/gpt-5.6-luna",
     "family": "openai", "via": "cursor-api", "harness": "cursor"},
    {"key": "terra", "label": "Terra", "model": "openai/gpt-5.6-terra",
     "family": "openai", "via": "cursor-api", "harness": "cursor"},
)
TOP_STATIONS = frozenset({"prompt_writer", "judge", "ccr"})
RATER_HREF = "/cdeck/#panel-model-rater"


class StationError(Exception):
    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _dir(paths):
    d = paths.role("state", "womb")
    d.mkdir(parents=True, exist_ok=True)
    return d


def _wish_path(paths):
    return _dir(paths) / "wishes.jsonl"


def _state_path(paths):
    return _dir(paths) / "stations.json"


def family_of(model: str) -> str:
    m = str(model or "").strip().lower()
    if not m:
        return ""
    if "composer" in m:
        return "composer"
    if "claude" in m or "opus" in m:
        return "anthropic"
    if "grok" in m or m.startswith("x-ai/"):
        return "xai"
    if "muse" in m or m.startswith("meta/"):
        return "meta"
    if "gemini" in m or m.startswith("google/"):
        return "google"
    if "glm" in m or m.startswith("z-ai/"):
        return "zai"
    if "deepseek" in m or m.startswith("ds"):
        return "deepseek"
    if "qwen" in m:
        return "qwen"
    if "inkling" in m or m.startswith("thinkingmachines/"):
        return "thinkingmachines"
    if "solar" in m or m.startswith("upstage/"):
        return "upstage"
    if any(tag in m for tag in ("luna", "terra", "sol", "gpt-5", "openai/")):
        return "openai"
    return ""


def _blank() -> dict:
    return {
        "schema": SCHEMA,
        "wish_floor": WISH_FLOOR,
        "order_floor": ORDER_FLOOR,
        "judge_floor": JUDGE_FLOOR,
        "final_floor": FINAL_FLOOR,
        "axis": AXIS,
        "seats": _default_seats(),
        "judge_history": [],
        "rotation": [],
    }


def load_state(paths) -> dict:
    path = _state_path(paths)
    if not path.is_file():
        return _blank()
    try:
        rec = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise StationError("UNREADABLE", str(e)) from e
    if not isinstance(rec, dict):
        raise StationError("UNPARSEABLE", "stations file is not an object")
    rec.setdefault("seats", {})
    rec.setdefault("judge_history", [])
    rec.setdefault("rotation", [])
    rec.setdefault("wish_floor", WISH_FLOOR)
    rec.setdefault("order_floor", ORDER_FLOOR)
    rec.setdefault("judge_floor", JUDGE_FLOOR)
    rec.setdefault("final_floor", FINAL_FLOOR)
    rec.setdefault("axis", AXIS)
    if "ccr" not in rec["seats"]:
        rec["seats"]["ccr"] = _seat("ccr", _by_key("inkling"), source="roster")
    defaults = _default_seats()
    for key, seat in defaults.items():
        if key not in rec["seats"]:
            rec["seats"][key] = seat
    return rec


def _named(row: dict, note: str) -> dict:
    return {
        "label": row["label"],
        "model": row["model"],
        "family": row["family"],
        "via": row.get("via") or "",
        "harness": row.get("harness") or "",
        "note": note,
    }


def _wombat_seat() -> dict:
    """Current try only. The pilot's rotation list is not a frozen roster."""
    return _seat("wombat", _by_key("sol6"), source="keith")


def _judge_seat() -> dict:
    """GLM 5.3 is the one in the pool above Luna. Luna, DS 0731, Qwen free follow."""
    seat = _seat("judge", _by_key("glm53"), source="roster")
    seat["also"] = [
        _named(_by_key("luna"), "Luna Flex. Coding 71.4."),
        _named(_by_key("ds0731"), "Also a coder. One session, so not while CCrew holds it."),
        _named(_by_key("qwen27"), "Free. Coding 68.1."),
    ]
    return seat


def _final_seat() -> dict:
    """Final Audit. Today's model is a seat, not a hardcoded ladder."""
    seat = _seat("final", _by_key("grok47"), source="roster")
    seat["role"] = "Final Audit"
    return seat


def _quality_family(rec, station: str) -> str:
    other = "final" if station == "judge" else "judge"
    seat = (rec.get("seats") or {}).get(other) or {}
    if not isinstance(seat, dict):
        return ""
    return str(seat.get("family") or family_of(seat.get("model")) or "")


def _quality_caution(rec, station: str, family: str) -> str:
    """Judge and Final. Same family warns. The pilot's pick still seats."""
    if station not in ("judge", "final"):
        return ""
    other = _quality_family(rec, station)
    if other and family and other == family:
        return f"WARN: Judge and Final Audit are both family {family}"
    return ""


def set_rotation(paths, models) -> dict:
    """Pilot's try-order. Not a frozen roster. New models do not need a code change."""
    if isinstance(models, str):
        models = [models]
    if not isinstance(models, list):
        raise StationError("BAD_ROTATION", "models is a list")
    order = []
    for model in models:
        mid = str(model or "").strip()
        if not mid:
            continue
        found = _find_model(mid)
        fam = (found or {}).get("family") or family_of(mid)
        if not fam:
            raise StationError("NO_FAMILY", mid)
        order.append({
            "model": (found or {}).get("model") or mid,
            "family": fam,
            "label": (found or {}).get("label") or mid,
        })
    rec = load_state(paths)
    rec["rotation"] = order
    save_state(paths, rec)
    return {"schema": SCHEMA, "rotation": order}


def pick_audit(paths) -> dict:
    """Final Audit. First rotation entry whose family is not the Judge's.

    A pilot list that is entirely the Judge's family still seats, and warns.
    An empty list does not invent a model.
    """
    rec = load_state(paths)
    judge = (rec.get("seats") or {}).get("judge") or {}
    avoid = str(judge.get("family") or family_of(judge.get("model")) or "")
    rotation = [row for row in (rec.get("rotation") or []) if isinstance(row, dict)]
    if not rotation:
        return {
            "schema": SCHEMA,
            "role": "Final Audit",
            "model": "",
            "family": "",
            "caution": "rotation empty",
            "exec": False,
        }
    chosen = next((row for row in rotation if row.get("family") != avoid), None)
    caution = ""
    if chosen is None:
        chosen = rotation[0]
        caution = f"WARN: Judge and Final Audit are both family {chosen.get('family')}"
    return {
        "schema": SCHEMA,
        "role": "Final Audit",
        "model": chosen.get("model") or "",
        "family": chosen.get("family") or "",
        "label": chosen.get("label") or "",
        "caution": caution,
        "exec": False,
    }


def _default_seats() -> dict:
    """Chairs from the six. One session per model, so the coders are the two left over."""
    orc = _seat("orc", _by_key("muse13"), source="keith")
    orc["alternate"] = {
        "label": "Solar Pro4",
        "model": "upstage/solar-pro4",
        "family": "upstage",
        "via": "hermes",
        "harness": "hermes",
        "note": "Also free. The other ORC, on Hermes.",
    }
    return {
        "orc": orc,
        "wombat": _wombat_seat(),
        "judge": _judge_seat(),
        "final": _final_seat(),
        "ccr": _seat("ccr", _by_key("inkling"), source="roster"),
        "ccrew": [
            _seat("ccrew", _by_key("glm"), source="mix"),
            _seat("ccrew", _by_key("ds0731"), source="mix"),
        ],
    }


def save_state(paths, rec: dict) -> dict:
    rec["schema"] = SCHEMA
    path = _state_path(paths)
    path.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    return rec


def _by_key(key: str) -> dict:
    for row in CANDIDATES:
        if row["key"] == key:
            return row
    raise StationError("BAD_CANDIDATE", key)


def _find_model(model: str) -> dict | None:
    want = str(model or "").strip()
    if not want:
        return None
    for row in CANDIDATES:
        if row["model"] == want or row["key"] == want:
            return row
    for row in CURSOR_OPTIONS:
        if row["model"] == want or row["key"] == want:
            return dict(row)
    return None


def _score(row: dict, scores: dict | None) -> tuple:
    """Higher is better. Catalog quality/cost outranks the roster rank."""
    scores = scores or {}
    hit = scores.get(row["model"]) or scores.get(row.get("key") or "") or {}
    quality = hit.get("coding", hit.get("quality"))
    price = hit.get("blended", hit.get("prompt_per_m"))
    try:
        if quality is not None and price not in (None, "", 0, 0.0):
            return (1, float(quality) / float(price), float(quality))
    except (TypeError, ValueError):
        pass
    q = float(quality) if isinstance(quality, (int, float)) else 0.0
    return (0, float(row.get("rank") or 0), q)


def _seat(station: str, row: dict, *, source: str, scores: dict | None = None,
          routing: str = "") -> dict:
    hit = (scores or {}).get(row["model"]) or {}
    return {
        "station": station,
        "model": row["model"],
        "family": row.get("family") or family_of(row["model"]),
        "label": row.get("label") or row["model"],
        "via": row.get("via") or "",
        "harness": row.get("harness") or row.get("via") or "",
        "axis": AXIS,
        "quality": hit.get("coding", hit.get("quality")),
        "cost_per_m": hit.get("blended", hit.get("prompt_per_m")),
        "context": hit.get("context"),
        "source": source,
        "routing": routing,
    }


def _ranked(rows, scores, *, tier=None, skip_families=()):
    pool = []
    for row in rows:
        if tier and row.get("tier") != tier:
            continue
        if row.get("family") in skip_families:
            continue
        pool.append(row)
    pool.sort(key=lambda r: _score(r, scores), reverse=True)
    return pool


def choose_station(paths, station: str, *, model=None, scores=None,
                   source: str = "axis", routing: str = "") -> dict:
    """Pick or accept one seat. Pilot/rater model wins when it passes the rules."""
    station = str(station or "").strip().lower()
    if station not in ("prompt_writer", "wombat", "judge", "final", "ccr", "orc", "cursor"):
        raise StationError("BAD_STATION", station)
    rec = load_state(paths)
    if model:
        found = _find_model(model)
        if found is None:
            found = {
                "model": str(model).strip(),
                "family": family_of(model),
                "label": str(model).strip(),
                "via": "",
                "harness": "",
                "rank": 0,
                "tier": "top",
            }
        if not found.get("family"):
            raise StationError("NO_FAMILY", str(model))
        caution = ""
        if station == "cursor":
            used = _coder_families(rec)
            if found["family"] in used and _cursor_other(used):
                raise StationError(
                    "CURSOR_FAMILY",
                    f"Cursor family {found['family']} matches a coder",
                )
        seat = _seat(station, found, source=source or "model_rater",
                     scores=scores, routing=routing)
        if not caution:
            caution = _quality_caution(rec, station, seat.get("family") or "")
    else:
        seat = _auto(station, rec, scores, routing)
        caution = _quality_caution(rec, station, seat.get("family") or "")
    rec["seats"][station] = seat
    if station == "judge":
        hist = list(rec.get("judge_history") or [])
        hist.append(seat["model"])
        rec["judge_history"] = hist[-24:]
    save_state(paths, rec)
    seat = dict(seat)
    if caution:
        seat["caution"] = caution
    seat["href"] = RATER_HREF
    seat["dropdown"] = _dropdown(station)
    return seat


def _auto(station, rec, scores, routing) -> dict:
    ccr = rec["seats"].get("ccr") or {}
    if station == "judge":
        busy = (rec.get("seats") or {}).get("wombat") or {}
        busy_model = str(busy.get("model") or "")
        pen = str(ccr.get("model") or "")
        last = (rec.get("judge_history") or [None])[-1]
        final_model = str((rec.get("seats") or {}).get("final", {}).get("model") or "")
        taken = {m for m in (busy_model, pen, final_model) if m}
        final_fam = _quality_family(rec, "judge")
        pool = [_by_key(key) for key in JUDGE_ORDER if _by_key(key)["model"] not in taken]
        other = [r for r in pool if r.get("family") != final_fam]
        if other:
            pool = other
        if last and len(pool) > 1:
            pool = [r for r in pool if r["model"] != last] or pool
        if not pool:
            raise StationError("NO_JUDGE", "no judge left in the pool")
        return _seat("judge", pool[0], source="rotate", scores=scores, routing=routing)
    if station == "cursor":
        used = _coder_families(rec)
        pick = _cursor_other(used) or CURSOR_OPTIONS[0]
        return _seat("cursor", pick, source="axis", scores=scores, routing=routing)
    if station == "final":
        return _final_seat()
    if station == "orc":
        return _seat("orc", _by_key("muse13"), source="axis",
                     scores=scores, routing=routing)
    if station in TOP_STATIONS:
        pool = _ranked(CANDIDATES, scores, tier="top")
        return _seat(station, pool[0], source="axis", scores=scores, routing=routing)
    pool = _ranked(CANDIDATES, scores)
    return _seat(station, pool[0], source="axis", scores=scores, routing=routing)


def _coder_families(rec) -> set:
    crew = rec.get("seats", {}).get("ccrew") or []
    if isinstance(crew, dict):
        crew = [crew]
    return {str(row.get("family") or "") for row in crew if isinstance(row, dict)}


def _cursor_other(used: set) -> dict | None:
    for row in CURSOR_OPTIONS:
        if row["family"] not in used:
            return row
    return None


def choose_ccrew(paths, *, models=None, scores=None, n: int = CREW_SIZE,
                 routing: str = "") -> dict:
    """Mixed families. A rater pick replaces that family inside the mix."""
    rec = load_state(paths)
    named = [m for m in (models or []) if str(m or "").strip()]
    if len(named) >= CREW_SIZE:
        order = []
        seen = set()
        for model in named:
            found = _known_or_rater(model)
            if found["family"] in seen:
                raise StationError("SAME_FAMILY", f"CCrew already has {found['family']}")
            seen.add(found["family"])
            order.append(_seat("ccrew", found, source="model_rater",
                               scores=scores, routing=routing))
    else:
        order = _mix_coders(rec, scores, routing, n)
        by_fam = {row["family"]: i for i, row in enumerate(order)}
        for model in named:
            found = _known_or_rater(model)
            seat = _seat("ccrew", found, source="model_rater",
                         scores=scores, routing=routing)
            if found["family"] in by_fam:
                order[by_fam[found["family"]]] = seat
            else:
                order.append(seat)
                by_fam[found["family"]] = len(order) - 1
    if len(order) < CREW_SIZE:
        raise StationError("SET_SHORT", f"CCrew set has {len(order)}")
    families = [row["family"] for row in order]
    if len(families) != len(set(families)):
        raise StationError("SAME_FAMILY", "CCrew coders share a family")
    rec["seats"]["ccrew"] = order
    save_state(paths, rec)
    return {
        "schema": SCHEMA,
        "station": "ccrew",
        "axis": AXIS,
        "href": RATER_HREF,
        "dropdown": _dropdown("ccrew"),
        "coders": order,
    }


def _known_or_rater(model: str) -> dict:
    found = _find_model(model)
    if found is not None:
        return found
    fam = family_of(model)
    if not fam:
        raise StationError("NO_FAMILY", str(model))
    return {
        "model": str(model).strip(),
        "family": fam,
        "label": str(model).strip(),
        "via": "openrouter-api",
        "harness": "openrouter-api",
        "rank": 0,
        "tier": "mix",
    }


def _mix_coders(rec, scores, routing, n: int) -> list:
    picked = []
    seen = set()
    for row in (_by_key("glm"), _by_key("ds0731")):
        picked.append(_seat("ccrew", row, source="mix",
                            scores=scores, routing=routing))
        seen.add(row["family"])
    ccr_fam = (rec["seats"].get("ccr") or {}).get("family")
    busy = str((rec.get("seats") or {}).get("wombat", {}).get("model") or "")
    final_model = str((rec.get("seats") or {}).get("final", {}).get("model") or "")
    tops = _ranked(CANDIDATES, scores, tier="top",
                   skip_families={ccr_fam} if ccr_fam else ())
    held = {m for m in (busy, final_model) if m}
    if held:
        free = [r for r in tops if r["model"] not in held]
        if free:
            tops = free
    for row in tops:
        if len(picked) >= max(3, int(n)):
            break
        if row["family"] in seen:
            continue
        picked.append(_seat("ccrew", row, source="mix",
                            scores=scores, routing=routing))
        seen.add(row["family"])
    return picked


def _dropdown(station: str) -> list:
    if station == "cursor":
        rows = CURSOR_OPTIONS
    elif station == "ccrew":
        rows = CANDIDATES
    else:
        rows = CANDIDATES
    return [
        {"model": r["model"], "label": r.get("label") or r["model"],
         "family": r.get("family"), "harness": r.get("harness") or r.get("via")}
        for r in rows
    ]


def append_wish(paths, text: str, *, source: str = "orc") -> dict:
    """One new line. The file is never rewritten."""
    if str(source or "").strip().lower() != "orc":
        raise StationError("ORC_WRITES", "ORC appends the wish queue")
    wish = str(text or "").strip()
    if not wish:
        raise StationError("EMPTY_WISH", "wish text is required")
    line = {
        "schema": SCHEMA,
        "at": _iso_now(),
        "source": "orc",
        "wish": wish,
    }
    path = _wish_path(paths)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(line, ensure_ascii=False) + "\n")
    depth = wish_depth(paths)
    rec = load_state(paths)
    floor = int(rec.get("wish_floor") or WISH_FLOOR)
    due = depth >= floor
    wombat = rec.get("seats", {}).get("wombat")
    if due and not (isinstance(wombat, dict) and wombat.get("model")):
        wombat = choose_station(paths, "wombat", source="axis")
    return {
        "schema": SCHEMA,
        "depth": depth,
        "wish_floor": floor,
        "summon_wombat": due,
        "seat": wombat if due else None,
        "href": RATER_HREF,
        "dropdown": _dropdown("wombat"),
    }


def wish_depth(paths) -> int:
    path = _wish_path(paths)
    if not path.is_file():
        return 0
    n = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            n += 1
    return n


def set_wish_floor(paths, n: int) -> dict:
    try:
        n = int(n)
    except (TypeError, ValueError) as e:
        raise StationError("BAD_FLOOR", "wish floor must be an int") from e
    if n < 1:
        raise StationError("BAD_FLOOR", "wish floor is at least 1")
    rec = load_state(paths)
    rec["wish_floor"] = n
    return save_state(paths, rec)


def board_missing(row: dict) -> list:
    row = row if isinstance(row, dict) else {}
    missing = []
    for key in BOARD_FIELDS:
        if key == "coders":
            continue
        if not str(row.get(key) or "").strip():
            missing.append(key)
    coders = row.get("coders")
    if not isinstance(coders, list) or len(coders) < CREW_SIZE:
        missing.append("coders")
        return missing
    prompts = []
    for i, coder in enumerate(coders):
        if not isinstance(coder, dict):
            missing.append(f"coders[{i}]")
            continue
        for key in CODER_FIELDS:
            val = coder.get(key)
            if val is None or str(val).strip() == "":
                missing.append(f"coders[{i}].{key}")
        stated = str(coder.get("family") or "").strip().lower()
        got = family_of(coder.get("model"))
        if got and stated and got != stated:
            missing.append(f"coders[{i}].family")
        duds = str(coder.get("duds") or "").strip().lower()
        if duds in ("tbd", "unseated", "todo", "placeholder", "filled per gitur wo"):
            missing.append(f"coders[{i}].duds")
        prompts.append(coder.get("prompt") or row.get("prompt"))
    if len(set(prompts)) > 1:
        missing.append("prompt_bytes")
    prompt = str(row.get("prompt") or "").strip().lower()
    if prompt in ("tbd", "unseated", "todo", "placeholder"):
        missing.append("prompt")
    return missing


def order_count(paths) -> int:
    """Fully written work orders. A file with a missing field does not count."""
    dest = _dir(paths) / "board"
    if not dest.is_dir():
        return 0
    n = 0
    for path in dest.glob("*.json"):
        try:
            row = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(row, dict) and not board_missing(row):
            n += 1
    return n


def set_floors(paths, floors: dict) -> dict:
    """Pilot sets how big each pile is before that role is spawned."""
    if not isinstance(floors, dict):
        raise StationError("BAD_FLOOR", "floors is an object")
    rec = load_state(paths)
    keys = ("wish_floor", "order_floor", "judge_floor", "final_floor")
    for key in keys:
        if key not in floors or floors.get(key) in (None, ""):
            continue
        try:
            n = int(floors[key])
        except (TypeError, ValueError) as e:
            raise StationError("BAD_FLOOR", key) from e
        if n < 1:
            raise StationError("BAD_FLOOR", f"{key} is at least 1")
        rec[key] = n
    save_state(paths, rec)
    return pile_audit(paths)


def file_board(paths, row: dict) -> dict:
    """WOMBAT writes the row only when every field the coders need is present."""
    missing = board_missing(row)
    if missing:
        raise StationError("BOARD_INCOMPLETE", ", ".join(missing))
    set_id = str(row.get("set_id") or "").strip()
    dest = _dir(paths) / "board"
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / f"{set_id}.json"
    body = dict(row)
    body["schema"] = SCHEMA
    body["at"] = _iso_now()
    body["ccrew_called"] = False
    path.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    n = order_count(paths)
    floor = int(load_state(paths).get("order_floor") or ORDER_FLOOR)
    out = {"ok": True, "path": str(path), "set_id": set_id,
           "ccrew_called": False, "orders": n, "order_floor": floor}
    if n >= floor:
        from cosmos_duds import note_ccrew_summon
        out["summon_ccrew"] = True
        out["ccrew"] = note_ccrew_summon(paths)
    else:
        out["summon_ccrew"] = False
    return out


def release_ccrew(paths, set_id: str) -> dict:
    """CCrew is called only after the board file exists and is complete."""
    path = _dir(paths) / "board" / f"{set_id}.json"
    if not path.is_file():
        raise StationError("BOARD_INCOMPLETE", set_id)
    try:
        row = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise StationError("UNREADABLE", str(e)) from e
    missing = board_missing(row)
    if missing:
        raise StationError("BOARD_INCOMPLETE", ", ".join(missing))
    row["ccrew_called"] = True
    row["ccrew_at"] = _iso_now()
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    rec = load_state(paths)
    return {
        "ok": True,
        "set_id": set_id,
        "coders": rec.get("seats", {}).get("ccrew") or row.get("coders"),
        "prompt": row.get("prompt"),
        "preload": row.get("preload"),
    }


def judge_family_ok(paths, model: str) -> tuple:
    """CCr does not grade, so the pen's family does not constrain the Judge."""
    del paths
    fam = family_of(model)
    if not fam:
        return False, f"no family for {model}"
    return True, ""


def family_caution(paths, model: str) -> str:
    """No family warning. The pen does not check the code."""
    del paths, model
    return ""


def note_judge_seated(paths, model: str) -> None:
    rec = load_state(paths)
    hist = list(rec.get("judge_history") or [])
    if not hist or hist[-1] != model:
        hist.append(str(model))
    rec["judge_history"] = hist[-24:]
    save_state(paths, rec)


def judge_due(paths, pile_n: int) -> dict:
    rec = load_state(paths)
    floor = int(rec.get("judge_floor") or JUDGE_FLOOR)
    if int(pile_n) < floor:
        return {
            "due": False,
            "pile": int(pile_n),
            "judge_floor": floor,
            "href": RATER_HREF,
            "dropdown": _dropdown("judge"),
        }
    seat = rec.get("seats", {}).get("judge")
    if not (isinstance(seat, dict) and seat.get("model")):
        seat = choose_station(paths, "judge", source="rotate")
    return {
        "due": True,
        "pile": int(pile_n),
        "judge_floor": floor,
        "seat": seat,
        "href": RATER_HREF,
        "dropdown": _dropdown("judge"),
    }


def _audit_wishes(paths) -> dict:
    path = _wish_path(paths)
    ready = 0
    rejected = []
    if path.is_file():
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except ValueError:
                rejected.append({"line": i, "problems": ["json"]})
                continue
            if isinstance(row, dict) and str(row.get("wish") or "").strip():
                ready += 1
            else:
                rejected.append({"line": i, "problems": ["wish"]})
    return {"ready": ready, "rejected": rejected[:12]}


def _audit_board(paths) -> dict:
    dest = _dir(paths) / "board"
    files = 0
    ready = 0
    rejected = []
    if dest.is_dir():
        for path in sorted(dest.glob("*.json")):
            files += 1
            try:
                row = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                rejected.append({"file": path.name, "problems": ["json"]})
                continue
            missing = board_missing(row if isinstance(row, dict) else {})
            if missing:
                rejected.append({"file": path.name, "problems": missing[:8]})
            else:
                ready += 1
    return {"files": files, "ready": ready, "rejected": rejected[:12]}


def pile_audit(paths) -> dict:
    """Ready counts, not file counts. A hollow row does not spawn anyone."""
    rec = load_state(paths)
    wishes = _audit_wishes(paths)
    board = _audit_board(paths)
    try:
        from cosmos_duds import judge_audit
        judged = judge_audit(paths)
    except Exception as e:  # noqa: BLE001
        judged = {"rows": 0, "ready_sets": 0, "error": type(e).__name__}
    floors = {
        "wish_floor": int(rec.get("wish_floor") or WISH_FLOOR),
        "order_floor": int(rec.get("order_floor") or ORDER_FLOOR),
        "judge_floor": int(rec.get("judge_floor") or JUDGE_FLOOR),
        "final_floor": int(rec.get("final_floor") or FINAL_FLOOR),
    }
    return {
        "floors": floors,
        "wishes": wishes,
        "board": board,
        "judge": judged,
        "spawn": {
            "wombat": wishes["ready"] >= floors["wish_floor"],
            "ccrew": board["ready"] >= floors["order_floor"],
            "judge": int(judged.get("ready_sets") or 0) >= floors["judge_floor"],
        },
    }


def snapshot(paths) -> dict:
    rec = load_state(paths)
    routing = ""
    try:
        from cosmos_route_variant import load_routing
        routing = str(load_routing(paths).get("priority") or "")
    except Exception:  # noqa: BLE001
        routing = ""
    return {
        "schema": SCHEMA,
        "wish_depth": wish_depth(paths),
        "wish_floor": rec.get("wish_floor"),
        "order_floor": rec.get("order_floor") or ORDER_FLOOR,
        "judge_floor": rec.get("judge_floor"),
        "axis": rec.get("axis"),
        "routing": routing,
        "audit": pile_audit(paths),
        "seats": rec.get("seats") or {},
        "judge_history": rec.get("judge_history") or [],
        "href": RATER_HREF,
        "candidates": [
            {"key": r["key"], "label": r["label"], "model": r["model"],
             "family": r["family"], "tier": r["tier"], "harness": r["harness"]}
            for r in CANDIDATES
        ],
        "cursor": [
            {"key": r["key"], "label": r["label"], "model": r["model"],
             "family": r["family"]}
            for r in CURSOR_OPTIONS
        ],
    }


def _coder(model, family):
    return {
        "model": model, "family": family, "coding": "UNMEASURED",
        "porosity": "UNMEASURED", "ortho": "UNMEASURED",
        "context": "UNMEASURED", "latency": "UNMEASURED",
        "scars": "none", "needs": "none", "duds": "complete",
    }


def _selftest() -> int:
    import tempfile
    from pathlib import Path

    from cosmos_paths import CosmosPaths, write_sentinel

    ok = True

    def check(label, cond):
        nonlocal ok
        print(("  OK  " if cond else "  FAIL") + " " + label)
        if not cond:
            ok = False

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        write_sentinel(root, tree_id="stations-test")
        (root / "state").mkdir()
        paths = CosmosPaths(root)
        refused = False
        try:
            append_wish(paths, "a wish", source="pilot")
        except StationError as e:
            refused = e.kind == "ORC_WRITES"
        check("only ORC appends wishes", refused)
        first = append_wish(paths, "wish one")
        check("one wish does not summon", first["summon_wombat"] is False)
        for n in range(2, WISH_FLOOR):
            append_wish(paths, f"wish {n}")
        held = wish_depth(paths)
        last = append_wish(paths, "wish fifty")
        text = _wish_path(paths).read_text(encoding="utf-8")
        check("fifty wishes summon WOMBAT",
              held == WISH_FLOOR - 1 and last["summon_wombat"] is True
              and last["seat"]["model"] and text.count("\n") == WISH_FLOOR
              and "wish one" in text.splitlines()[0])
        chairs = load_state(paths)["seats"]
        check("SOL 6 is WOMBAT, GLM 5.3 is Judge, Inkling is the pen, Grok 4.7 checks",
              chairs["orc"]["model"] == "meta/muse-spark-1.3-contributor"
              and chairs["wombat"]["model"] == "openai/gpt-5.6-sol"
              and chairs["final"]["role"] == "Final Audit"
              and load_state(paths)["rotation"] == []
              and chairs["judge"]["model"] == "z-ai/glm-5.3"
              and [a["model"] for a in chairs["judge"]["also"]] == [
                  "openai/gpt-5.6-luna",
                  "deepseek/deepseek-v4-flash-0731",
                  "qwen/qwen3.8-27b:free",
              ]
              and chairs["final"]["model"] == "grok-4.7"
              and chairs["ccr"]["model"] == "thinkingmachines/inkling-small:free"
              and {c["model"] for c in chairs["ccrew"]} == {
                  "z-ai/glm-5.3-flash", "deepseek/deepseek-v4-flash-0731",
              })
        writer = choose_station(paths, "prompt_writer")
        check("prompt writer is top tier",
              writer["model"] == "openai/gpt-5.6-luna" and writer["family"] == "openai")
        crew = choose_ccrew(paths)
        families = {c["family"] for c in crew["coders"]}
        models = {c["model"] for c in crew["coders"]}
        check("CCrew mixes families and keeps GLM and DSV0731",
              families >= {"zai", "deepseek"} and len(families) == len(crew["coders"])
              and "z-ai/glm-5.3-flash" in models
              and "deepseek/deepseek-v4-flash-0731" in models
              and "thinkingmachines/inkling-small:free" not in models
              and "openai/gpt-5.6-sol" not in models
              and "z-ai/glm-5.3" not in models
              and "grok-4.7" not in models)
        same = choose_station(paths, "judge", model="grok-4.7", source="model_rater")
        check("a pilot may seat Judge in Final's family, and it warns",
              same["model"] == "grok-4.7"
              and "WARN:" in str(same.get("caution") or "")
              and "xai" in str(same.get("caution") or ""))
        j1 = choose_station(paths, "judge")
        j2 = choose_station(paths, "judge")
        judge_pool = {
            "z-ai/glm-5.3", "openai/gpt-5.6-luna",
            "deepseek/deepseek-v4-flash-0731", "qwen/qwen3.8-27b:free",
        }
        check("Judge rotates inside its pool and stays off Final's family",
              j1["model"] in judge_pool and j2["model"] in judge_pool
              and j1["family"] != "xai" and j2["family"] != "xai"
              and not j1.get("caution") and not j2.get("caution"))
        cur = choose_station(paths, "cursor")
        check("Cursor is a different family from the coders",
              cur["family"] not in families)
        thin = {"order_id": "wo", "set_id": "s1", "prompt": "same", "preload": "cache"}
        incomplete = False
        try:
            file_board(paths, thin)
        except StationError as e:
            incomplete = e.kind == "BOARD_INCOMPLETE"
        check("CCrew waits until the board is full", incomplete)
        full = dict(thin, coders=[
            _coder("z-ai/glm-5.3-flash", "zai"),
            _coder("deepseek/deepseek-v4-flash-0731", "deepseek"),
            _coder("google/gemini-3.8-flash", "google"),
        ])
        filed = file_board(paths, full)
        released = release_ccrew(paths, "s1")
        check("a full board releases CCrew on the shared prompt",
              filed["ok"] and filed["summon_ccrew"] is False
              and released["prompt"] == "same"
              and released["preload"] == "cache")
        got = None
        for i in range(2, ORDER_FLOOR + 1):
            got = file_board(paths, dict(full, set_id=f"s{i}", order_id=f"wo-{i}"))
        hollow = dict(full, set_id="hollow", order_id="hollow",
                      coders=[dict(c, duds="tbd") for c in full["coders"]])
        refused_board = False
        try:
            file_board(paths, hollow)
        except StationError as e:
            refused_board = e.kind == "BOARD_INCOMPLETE"
        check("a placeholder board is not executable", refused_board)
        check("forty written orders make WOMBAT summon the CCrew",
              got is not None and got["summon_ccrew"] is True
              and got["orders"] == ORDER_FLOOR
              and got["ccrew"]["by"] == "WOMBAT"
              and got["ccrew"]["mode"] == "HERO"
              and got["ccrew"]["exec"] is False)
        early = judge_due(paths, JUDGE_FLOOR - 1)
        ready = judge_due(paths, JUDGE_FLOOR)
        bare = pick_audit(paths)
        check("an empty rotation does not invent a Final Audit model",
              bare["model"] == "" and bare["role"] == "Final Audit"
              and bare["caution"] == "rotation empty")
        set_rotation(paths, [
            "google/gemini-3.8-flash", "grok-4.7", "openai/gpt-5.6-sol",
        ])
        first_pick = pick_audit(paths)
        check("rotation uses the pilot list, not a hardcoded ladder",
              first_pick["model"] == "google/gemini-3.8-flash"
              and not first_pick["caution"])
        choose_station(paths, "judge", model="google/gemini-3.8-flash",
                       source="pilot")
        skipped = pick_audit(paths)
        check("Final Audit skips the seated Judge's family",
              skipped["model"] == "grok-4.7" and not skipped["caution"])
        set_rotation(paths, ["google/gemini-3.8-flash"])
        forced = pick_audit(paths)
        check("a one-family list still seats and warns",
              forced["model"] == "google/gemini-3.8-flash"
              and "WARN:" in str(forced.get("caution") or ""))
        check("Judge waits for 30 complete sets",
              early["due"] is False and ready["due"] is True
              and ready["seat"]["model"])
        sized = set_floors(paths, {
            "wish_floor": 3, "order_floor": 4, "judge_floor": 5, "final_floor": 6,
        })
        check("cDeck can set each pile size",
              sized["floors"]["wish_floor"] == 3
              and sized["floors"]["order_floor"] == 4
              and sized["floors"]["judge_floor"] == 5
              and sized["floors"]["final_floor"] == 6
              and sized["board"]["ready"] >= 1
              and sized["spawn"]["ccrew"] is True)
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print("cosmos_stations: --selftest", file=sys.stderr)
    raise SystemExit(2)
