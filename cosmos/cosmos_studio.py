#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_studio — MOTIF DEFINE + RESEARCH pack for cDeck Studio.

GET never mutates and never mkdir. POST writes state/studio/pack.json.
Does not start MOTIF. Does not hold API keys (via names the rail).
Fallback is config for RESEARCH: if the first model call fails, try the
fallback via/model. Execution is a later RESEARCH pass.

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
PACK_NAME = "pack.json"
MAX_RESEARCH = 12
MAX_DEFINE = 80_000
MAX_URLS = 24

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
    """kind in {BAD_INPUT, REFUSED, BROKE}."""

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


def default_research_models() -> list[dict]:
    """MOTIF RESEARCH: SGH + GEM first, both, in parallel. Fallbacks named."""
    return [
        {
            "id": "r_1",
            "label": "SGH",
            "model": "grok-4.6",
            "via": "cli:grok",
            "fallback_model": "grok-4.6",
            "fallback_via": "sgh-api",
        },
        {
            "id": "r_2",
            "label": "GEM",
            "model": "gemini-2.5-flash",
            "via": "gem-api",
            "fallback_model": "google/gemma-4-26b-a4b-it:free",
            "fallback_via": "openrouter-api",
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
        "updated_at": None,
        "available": False,
        "kind": "NO_SOURCE",
        "via_options": [dict(v) for v in VIA_OPTIONS],
        "target_catalog": [{"id": i, "label": lab} for i, lab in TARGETS],
    }


def _norm_via(raw) -> str:
    try:
        return normalize_via(raw)
    except ModelRaterError as e:
        raise StudioError(e.kind, str(e)[:300]) from e


def _public_model(raw: dict, idx: int) -> dict:
    n = idx + 1
    via = _norm_via(raw.get("via"))
    fb_via = _norm_via(raw.get("fallback_via"))
    oid = str(raw.get("id") or f"r_{n}").strip() or f"r_{n}"
    return {
        "id": oid[:32],
        "label": str(raw.get("label") or f"Research {n}").strip()[:80],
        "model": str(raw.get("model") or "").strip()[:160],
        "via": via,
        "fallback_model": str(raw.get("fallback_model") or "").strip()[:160],
        "fallback_via": fb_via,
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
    return {
        "schema": SCHEMA,
        "define": {
            "text": str(define.get("text") or "")[:MAX_DEFINE],
            "saved_at": define.get("saved_at"),
        },
        "research": {"models": models, "targets": targets, "extra_urls": urls},
        "updated_at": rec.get("updated_at"),
        "available": True,
        "kind": "OK",
        "via_options": [dict(v) for v in VIA_OPTIONS],
        "target_catalog": [{"id": i, "label": lab} for i, lab in TARGETS],
    }


def save_pack(paths, body: dict) -> dict:
    """POST. Merges onto current pack. Does not start MOTIF."""
    if not isinstance(body, dict):
        raise StudioError("BAD_INPUT", "body must be an object")
    cur = load_pack(paths)
    define = dict(cur["define"])
    research = {
        "models": list(cur["research"]["models"]),
        "targets": dict(cur["research"]["targets"]),
        "extra_urls": list(cur["research"]["extra_urls"]),
    }
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
    rec = {
        "schema": SCHEMA,
        "define": define,
        "research": research,
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
    return out


def snapshot(paths) -> dict:
    rec = load_pack(paths)
    rec["measured_at"] = time.time()
    rec.setdefault("via_options", [dict(v) for v in VIA_OPTIONS])
    rec.setdefault("target_catalog", [{"id": i, "label": lab} for i, lab in TARGETS])
    rec["note"] = (
        "DEFINE is the frozen prompt. RESEARCH models/targets are config. "
        "This POST does not start MOTIF. Keys stay on the named via, never in this pack."
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

    bad_out = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (Studio DEFINE+RESEARCH pack)"
          % ("PASS" if not bad_out else "FAIL", len(results)))
    return 0 if not bad_out else 1


if __name__ == "__main__":
    raise SystemExit(_selftest())
