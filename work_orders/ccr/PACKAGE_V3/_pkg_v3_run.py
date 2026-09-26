#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Two-day package dispatcher. Propose-only. Does not write cosmos/ or builds/.

    py -3.14 work_orders\\ccr\\PACKAGE_V3\\_pkg_v3_run.py --query 1
    py -3.14 work_orders\\ccr\\PACKAGE_V3\\_pkg_v3_run.py --query 2 --model anthropic/claude-fable-5.1

Prefix = package Sections 1-2 + CSM_prompt.md (frozen after first write).
ITEM = query text + live slices. Mouth: REVIEW not CODING.
"""
from __future__ import annotations

import argparse
import json
import sys
from hashlib import sha256
from pathlib import Path

ROOT = Path(r"V:\A\Ai\COSMOS")
HERE = Path(__file__).resolve().parent
PKG = HERE / "COSMOS2_cDeck_TwoDay_Execution_Package_v3.md"
CSM_SRC = Path(r"C:\Users\Papa\OneDrive\Desktop\CSM_prompt.md")
CSM_FROZEN = HERE / "CSM_prompt.md"
PREFIX_PATH = HERE / "PREFIX.md"
FAT_PATH = HERE / "CACHE_FAT.md"
ITEM_DIR = HERE / "ITEMS"
OUT_DIR = HERE / "OUT"
LIVE = ROOT / "live"
# Fat system block (PREFIX + live slices). Next DS/Qwen/GLM/Luna call
# must hash this, not PREFIX.md alone, or the measured cache misses.
FAT_SEATS = frozenset({"luna", "glm", "dspro", "qwenmax"})

SOL = "openai/gpt-5.6-sol"
TERRA = "openai/gpt-5.6-terra"
FABLE = "anthropic/claude-fable-5.1"
Q1_MODEL = SOL
Q2_MODEL = FABLE

# Extra-pane + occupancy + Core fence files. Not index.html / app.js (NEEDS FILE).
SLICE_REL = [
    "builds/cdeck/ui/deck_tabs.js",
    "builds/cdeck/ui/header.js",
    "builds/cdeck/ui/header.css",
    "builds/cdeck/ui/deck_more.html",
    "builds/cdeck/ui/deck_more.css",
    "builds/cdeck/ui/deck_studio.js",
    "builds/cdeck/ui/deck_orders.js",
    "builds/cdeck/ui/deck_gitur.js",
    "builds/cdeck/ui/deck_backup.js",
    "builds/cdeck/ui/deck_forge.js",
    "builds/cdeck/ui/deck_profiles.js",
    "builds/cdeck/ui/deck_settings.js",
    "builds/cdeck/ui/deck_session_kit.js",
    "builds/cdeck/ui/model_rater.js",
    "builds/cdeck/ui/kdash_native.js",
    "builds/cdeck/test_kdash_working.py",
    "builds/cdeck/src-tauri/src/lib.rs",
    "cosmos/cosmos_pool.py",
    "cosmos/cosmos_run.py",
    "cosmos/cosmos_ledger.py",
    "cosmos/cosmos_pulse.py",
    "cosmos/cosmos_kernel.py",
    "cosmos/cosmos_service.py",
    "docs/CODER_BRIEF.md",
]

NEEDS_FILE = [
    "builds/cdeck/ui/index.html",
    "builds/cdeck/ui/app.js",
    "builds/cdeck/ui/app.css",
    "builds/cdeck/ui/sw.js",
    "builds/cdeck/src-tauri/src/main.rs",
]

FETCH_SCAN = """
FETCH() SCAN (CCr pre-scan of live bytes; reviewer still cites file/line):
- builds/cdeck/ui/header.js:135 fetch() inside apiGet/apiPost wrapper
- builds/cdeck/ui/header.js:674 fetch("deck_more.html") markup load, not Core
- builds/cdeck/ui/app.js:602 fetch()
- builds/cdeck/ui/sw.js:101,133 service-worker fetch
- builds/cdeck/ui/index.html:1023,1089,1127,1235,1266,1385,2016,2156,2441,2449,2595
  local json (mesh_state/chan/dash/TOOLS_REGISTRY/meters) plus
  /api/burn :2787 /api/bench :3049 /api/policy :3089
NEEDS FILE for full index.html and app.js bodies.
"""

Q1_ITEM = """ITEM
This call is REVIEW not CODING. Mouth rule (diff-first / NONE) does not apply.
Use the reporting contract in this ITEM. Do not emit a unified diff.

REVIEW 1 of 2 (independent — a second model will separately review the
same material; do not assume convergence, work from evidence only).

FULL REVIEW: COSMOS2 core + cDeck, tabs/feature completeness emphasis.

SCOPE:
- cosmos/ (modules in the prefix map; live slices attached below)
- builds/cdeck/ui/ (Files: list in prefix; live slices attached)
- builds/cdeck/src-tauri/ (lib.rs attached; main.rs = NEEDS FILE)

CSM_prompt-2.md was not on disk. Occupancy preload used is CSM_prompt.md
(frozen copy next to this package). Do not treat that rename as a finding.

FOR EACH cDeck TAB in this order: studio, runs, orders, review, gitur,
surfaces, recents, voice, system, models, backup, tools, clock, open,
settings, forge, crucible, diligence, docket, ups, differentiator,
website, Profiles popup —

Report exactly one of:
COMPLETE — cite the occupancy pin, test reference, or GET-body evidence
INCOMPLETE — cite what's missing, quote the relevant live slice
UNMEASURED — Core omits the field, say so, do not guess

Then, for the codebase as a whole, report:
1. BLOCKING findings (file, line, reason)
2. IMPORTANT findings
3. SUGGESTIONS
4. Any fetch() usage outside apiGet/apiPost — cite file/line
5. Any GET/POST referenced that is not in the documented surface
6. Merge decision: ship / ship-with-fixes / hold

If material needed isn't in this package, write NEEDS FILE: <name>
instead of guessing. Do not manufacture findings to fill a category.
"""

Q2_ITEM = """ITEM
This call is REVIEW not CODING. Mouth rule (diff-first / NONE) does not apply.
Use the reporting contract in this ITEM. Do not emit a unified diff.

REVIEW 2 of 2 (independent — this is a separate model from Review 1.
Do not reference or assume Review 1's conclusions. Work from the
material below only, as a fresh independent read.)

FULL REVIEW: COSMOS2 core + cDeck, tabs/feature completeness emphasis.

SCOPE:
- cosmos/ (modules in the prefix map; live slices attached below)
- builds/cdeck/ui/ (Files: list in prefix; live slices attached)
- builds/cdeck/src-tauri/ (lib.rs attached; main.rs = NEEDS FILE)

CSM_prompt-2.md was not on disk. Occupancy preload used is CSM_prompt.md
(frozen copy next to this package). Do not treat that rename as a finding.

FOR EACH cDeck TAB in this order: studio, runs, orders, review, gitur,
surfaces, recents, voice, system, models, backup, tools, clock, open,
settings, forge, crucible, diligence, docket, ups, differentiator,
website, Profiles popup —

Report exactly one of:
COMPLETE — cite the occupancy pin, test reference, or GET-body evidence
INCOMPLETE — cite what's missing, quote the relevant live slice
UNMEASURED — Core omits the field, say so, do not guess

Then, for the codebase as a whole, report:
1. BLOCKING findings (file, line, reason)
2. IMPORTANT findings
3. SUGGESTIONS
4. Any fetch() usage outside apiGet/apiPost — cite file/line
5. Any GET/POST referenced that is not in the documented surface
6. Merge decision: ship / ship-with-fixes / hold

If material needed isn't in this package, write NEEDS FILE: <name>
instead of guessing. Do not manufacture findings to fill a category.
"""


def extract_prefix(pkg_text: str) -> str:
    start = pkg_text.index("# SECTION 1 —")
    end = pkg_text.index("END SECTION 2.") + len("END SECTION 2.")
    return pkg_text[start:end].replace("\r\n", "\n")


def frozen_prefix() -> str:
    pkg = PKG.read_text(encoding="utf-8").replace("\r\n", "\n")
    sec = extract_prefix(pkg)
    if not CSM_FROZEN.is_file():
        CSM_FROZEN.write_text(
            CSM_SRC.read_text(encoding="utf-8").replace("\r\n", "\n"),
            encoding="utf-8", newline="\n")
    csm = CSM_FROZEN.read_text(encoding="utf-8").replace("\r\n", "\n")
    blob = sec.rstrip() + "\n\n" + csm.rstrip() + "\n"
    if PREFIX_PATH.is_file():
        old = PREFIX_PATH.read_text(encoding="utf-8").replace("\r\n", "\n")
        if old != blob:
            raise SystemExit("PREFIX.md bytes changed — P11 stop. Do not continue.")
        return old
    PREFIX_PATH.write_text(blob, encoding="utf-8", newline="\n")
    return blob


def frozen_fat() -> str:
    """P11: PREFIX + slices as one cached system block. Do not rebuild."""
    if not FAT_PATH.is_file():
        raise SystemExit(
            "CACHE_FAT.md missing — P11 stop. Run _pkg_v3_cache_prime.py first.")
    return FAT_PATH.read_text(encoding="utf-8").replace("\r\n", "\n")


COMPACT_SKIP = {
    "builds/cdeck/src-tauri/src/lib.rs",
    "cosmos/cosmos_service.py",
    "builds/cdeck/ui/header.css",
    "builds/cdeck/ui/deck_more.css",
}


def slice_block(compact: bool = False) -> str:
    parts = ["\n--- LIVE SLICES ---\n"]
    for rel in SLICE_REL:
        if compact and rel in COMPACT_SKIP:
            parts.append(f"\nNEEDS FILE (compact): {rel}\n")
            continue
        p = ROOT / rel.replace("/", "\\")
        if not p.is_file():
            parts.append(f"\nNEEDS FILE: {rel}\n")
            continue
        body = p.read_text(encoding="utf-8", errors="replace")
        parts.append(f"\n===== FILE: {rel} =====\n")
        parts.append(body)
        if not body.endswith("\n"):
            parts.append("\n")
    parts.append("\n--- NEEDS FILE (not attached; do not guess) ---\n")
    for rel in NEEDS_FILE:
        parts.append(f"NEEDS FILE: {rel}\n")
    parts.append(FETCH_SCAN)
    return "".join(parts)


def write_item(n: int) -> Path:
    ITEM_DIR.mkdir(parents=True, exist_ok=True)
    if n == 1:
        text = Q1_ITEM.rstrip() + "\n" + slice_block()
        dest = ITEM_DIR / "Q1.md"
    elif n == 2:
        text = Q2_ITEM.rstrip() + "\n" + slice_block()
        dest = ITEM_DIR / "Q2.md"
    else:
        raise SystemExit(f"ITEM builder ships Query 1 and 2 (got {n})")
    dest.write_text(text, encoding="utf-8", newline="\n")
    return dest


def dispatch_or(*, query, model: str, seat: str, prefix: str, item: str,
                out_path: Path, max_tokens: int, skip_pin: bool,
                flex: bool = False, reasoning_effort: str = "") -> dict:
    sys.path.insert(0, str(ROOT / "cosmos"))
    from cosmos_openrouter_rail import (
        CHAT_PATH, FLEX_MODELS, OPENAI_FLEX, OpenRouterRail, cache_family,
        fold_usage, key_path_for, load_spec, model_refused, spec_path_for,
        tag_preload, _message_text,
    )
    from cosmos_paths import CosmosPaths
    why = None if skip_pin else model_refused(model)
    if why:
        rec = {"ok": False, "reason": "REFUSED", "detail": why, "query": query,
               "pin": model}
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
        return rec
    paths = CosmosPaths(str(LIVE))
    spec = dict(load_spec(spec_path_for(paths)))
    spec["timeout_s"] = max(int(spec.get("timeout_s") or 120), 900)
    rail = OpenRouterRail(key_path_for(paths, spec), spec)
    pck = cache_family(model=model, prefix=prefix)
    use_flex = bool(flex or model in FLEX_MODELS)
    # Volatile ITEM is the tail. cache_control on the user block was the
    # DS/Qwen miss: slices sat after PREFIX, so the CACHE_FAT write never
    # matched. Static fat stays on system only. tag_preload always puts
    # cache_control on that system block (auto vendors ignore; picky hit).
    messages = tag_preload(
        [
            {"role": "system", "content": prefix},
            {"role": "user", "content": item},
        ],
        flex=use_flex,
    )
    prov = {"allow_fallbacks": False}
    if use_flex:
        prov["only"] = [OPENAI_FLEX]
        prov["order"] = [OPENAI_FLEX]
    body = {
        "model": model,
        "messages": messages,
        "max_tokens": int(max_tokens),
        "stream": False,
        "provider": prov,
        "prompt_cache_key": pck,
        "session_id": pck,
    }
    if use_flex:
        body["prompt_cache_options"] = {"mode": "explicit", "ttl": "30m"}
    if reasoning_effort:
        body["reasoning"] = {
            "effort": str(reasoning_effort),
            "exclude": True,
        }
    status, _hdrs, obj = rail._call("POST", CHAT_PATH, body)
    obj = obj if isinstance(obj, dict) else {}
    usage = fold_usage(obj)
    err = obj.get("error") if isinstance(obj.get("error"), dict) else None
    rec = {
        "schema": "cosmos-package-v3-query/1",
        "query": query,
        "seat": seat,
        "pin": model,
        "skip_pin": bool(skip_pin),
        "ok": status == 200 and bool(obj.get("model")),
        "http": status,
        "model": obj.get("model"),
        "model_requested": model,
        "via": "openrouter",
        "prompt_cache_key": pck,
        "prefix_sha12": sha256(prefix.encode("utf-8")).hexdigest()[:12],
        "prefix_bytes": len(prefix.encode("utf-8")),
        "item_bytes": len(item.encode("utf-8")),
        "text": _message_text(obj),
        "detail": (err or {}).get("message") if err else "",
        "error": err,
        "usage": usage,
        "csm_note": "CSM_prompt-2.md missing; used CSM_prompt.md frozen copy",
        "reasoning_effort": reasoning_effort or None,
        "max_tokens_req": int(max_tokens),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    return rec


Q2B_MODEL = "google/gemini-3.1-pro-preview"
Q2B_ITEM = """ITEM
This call is REVIEW not CODING. Mouth rule (diff-first / NONE) does not apply.
Use the reporting contract in this ITEM. Do not emit a unified diff.

REVIEW 2b of 3 (independent — two other models, OpenAI and Anthropic
family, are separately reviewing the same material. Do not reference or
assume their conclusions. Work from the material below only, as a fresh
independent read.)

FULL REVIEW: COSMOS2 core + cDeck, tabs/feature completeness emphasis.

SCOPE:
- cosmos/ (modules in the prefix map; live slices attached below)
- builds/cdeck/ui/ (Files: list in prefix; live slices attached)
- builds/cdeck/src-tauri/ (lib.rs attached; main.rs = NEEDS FILE)

CSM_prompt-2.md was not on disk. Occupancy preload used is CSM_prompt.md
(frozen copy next to this package). Do not treat that rename as a finding.

FOR EACH cDeck TAB in this order: studio, runs, orders, review, gitur,
surfaces, recents, voice, system, models, backup, tools, clock, open,
settings, forge, crucible, diligence, docket, ups, differentiator,
website, Profiles popup —

Report exactly one of:
COMPLETE — cite the occupancy pin, test reference, or GET-body evidence
INCOMPLETE — cite what's missing, quote the relevant live slice
UNMEASURED — Core omits the field, say so, do not guess

Then, for the codebase as a whole, report:
1. BLOCKING findings (file, line, reason)
2. IMPORTANT findings
3. SUGGESTIONS
4. Any fetch() usage outside apiGet/apiPost — cite file/line
5. Any GET/POST referenced that is not in the documented surface
6. Merge decision: ship / ship-with-fixes / hold

If material needed isn't in this package, write NEEDS FILE: <name>
instead of guessing. Do not manufacture findings to fill a category.
"""

Q3_ITEM = """ITEM
This call is REVIEW not CODING. Mouth rule (diff-first / NONE) does not apply.
Use the reporting contract in this ITEM. Do not emit a unified diff.

DEEP DIVE: cDeck tabs and features only. This goes beyond COMPLETE/
INCOMPLETE labeling — for EACH tab, produce:

1. What the tab currently does, based on the live slice provided
   (walk through the actual code path, not just presence/absence).
2. What UI rules it satisfies or violates (IIFE-only, no fetch(),
   apiGet/apiPost only, no invented GET/POST, tab-order position).
3. What functionality appears MISSING relative to the tab's evident
   purpose (e.g. if "forge" has a stub handler but no real logic,
   say exactly what's stubbed and what a working version would need
   to do).
4. Cross-references to Review 1 and Review 2 findings for this tab,
   noting agreement or disagreement between the two reviews.

Tabs to cover, in this order: studio, runs, orders, review, gitur,
surfaces, recents, voice, system, models, backup, tools, clock, open,
settings, forge, crucible, diligence, docket, ups, differentiator,
website, Profiles popup.

Live slices are the cached system block (CACHE_FAT). Review 1 and
Review 2 excerpts follow in this ITEM. Do not assume later merges
unless the attached slice shows them. If material needed isn't in
this package, write NEEDS FILE: <name>.
"""

Q5_ITEM = """ITEM
This call is REVIEW not CODING. Mouth rule (diff-first / NONE) does not apply.
Do not emit a unified diff.

BLUEPRINT DRAFT — EXPLICITLY NON-AUTHORITATIVE. This is a planning
roadmap for Keith and the crew to evaluate, NOT a mergeable diff and
NOT a CCr disposal candidate. Do not format as a unified diff. Do not
apply the Mouth rule's diff-first requirement here — prose, pseudocode,
and structured checklists are all acceptable.

For each tab confirmed INCOMPLETE by the deep dive above, produce:

1. GOAL — one sentence, what "complete" means for this tab.
2. CURRENT STATE — summary of what exists today (from the deep dive).
3. GAP — specific missing pieces: functions, UI elements, GET/POST
   wiring, test coverage.
4. PROPOSED APPROACH — a plain-language implementation plan: what
   files would change, what new functions/handlers are needed, how it
   would wire into apiGet/apiPost and the existing GET surface (do not
   invent new GET/POST — flag if a new endpoint seems genuinely needed
   as a separate, explicitly-flagged recommendation).
5. RISK NOTES — anything that looks like it could conflict with
   existing occupancy rules, tab order, or other tabs' behavior.
6. SUGGESTED JOB BREAKDOWN — how this would split into discrete
   CREW/OUT jobs if approved (job count, rough sizing, suggested seat:
   Luna / GLM+Ling / GF38).

This is a map, not a commitment. Do not claim test coverage, occupancy
pins, or GET-body evidence for anything not already confirmed in the
deep dive — mark unverified assumptions clearly as ASSUMPTION.

Live slices are the cached system block. Deep-dive findings follow.
"""

Q5B_ITEM = """ITEM
This call is REVIEW not CODING. Mouth rule (diff-first / NONE) does not apply.
Do not emit a unified diff.

CRITIQUE the blueprint draft below. You did not write it — review it
independently. For each tab's proposed approach, answer:

1. Does the proposed approach actually fit existing conventions
   (IIFE-only, apiGet/apiPost, documented GET/POST surface, tab order)?
2. Does it invent anything — a GET/POST, a file not in the Files: list,
   an assumption not grounded in the live slices provided?
3. Is the suggested job breakdown realistic for the assigned seat
   (Luna / GLM+Ling / GF38), or does it actually need GF38/escalation
   when it was assigned to a cheaper seat?
4. Flag ANY point where you would revise the approach before it becomes
   a real job — be specific, cite the exact blueprint section.

If the blueprint is sound as written, say so explicitly per tab. Do not
invent a critique to fill space.

Live slices are the cached system block. Blueprint draft follows.
This seat is GPT-5.6 Terra (Rule B substitute). Do not call Claude.
"""


def review_excerpts() -> str:
    q1 = (OUT_DIR / "Q1_sol.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    q2p = OUT_DIR / "Q2_fable.md"
    q2 = q2p.read_text(encoding="utf-8").replace("\r\n", "\n") if q2p.is_file() else ""
    return (
        "\n--- REVIEW 1 (Sol) ---\n" + q1.rstrip()
        + "\n\n--- REVIEW 2 (Fable, truncated; ANTHROPIC_OFF, do not retry) ---\n"
        + q2.rstrip()
        + "\n\nCCr volatile note: after Review 1/2, cDeck PR #106 merged the "
          "studio parse fix. CACHE_FAT may still be pre-fix bytes. Walk the "
          "attached slices. Query 2a Fable cache was 0. Do not call Claude.\n"
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--query", required=True)
    p.add_argument("--max-tokens", type=int, default=16000)
    ns = p.parse_args(argv)
    q = str(ns.query)
    prefix = frozen_prefix()
    out_name = ""
    if q == "1":
        item_path = write_item(1)
        rec = dispatch_or(
            query=1, model=Q1_MODEL, seat="sol", prefix=prefix,
            item=item_path.read_text(encoding="utf-8"),
            out_path=OUT_DIR / "Q1_sol.json",
            max_tokens=ns.max_tokens, skip_pin=False)
        out_name = "Q1_sol.json"
    elif q == "2":
        item_path = write_item(2)
        rec = dispatch_or(
            query=2, model=Q2_MODEL, seat="fable", prefix=prefix,
            item=item_path.read_text(encoding="utf-8"),
            out_path=OUT_DIR / "Q2_fable.json",
            max_tokens=ns.max_tokens, skip_pin=True)
        out_name = "Q2_fable.json"
    elif q in ("2a", "21"):
        item_path = ITEM_DIR / "Q2.md"
        if not item_path.is_file():
            item_path = write_item(2)
        rec = dispatch_or(
            query="2a", model=Q2_MODEL, seat="fable", prefix=prefix,
            item=item_path.read_text(encoding="utf-8"),
            out_path=OUT_DIR / "Q2a_fable.json",
            max_tokens=max(ns.max_tokens, 24000), skip_pin=True,
            reasoning_effort="medium")
        out_name = "Q2a_fable.json"
    elif q in ("2b", "22"):
        ITEM_DIR.mkdir(parents=True, exist_ok=True)
        item_path = ITEM_DIR / "Q2b.md"
        item_path.write_text(
            Q2B_ITEM.rstrip() + "\n" + slice_block(),
            encoding="utf-8", newline="\n")
        rec = dispatch_or(
            query="2b", model=Q2B_MODEL, seat="gemini3pro", prefix=prefix,
            item=item_path.read_text(encoding="utf-8"),
            out_path=OUT_DIR / "Q2b_gemini.json",
            max_tokens=max(ns.max_tokens, 24000), skip_pin=True)
        out_name = "Q2b_gemini.json"
    elif q in ("luna", "glm", "ling", "dspro", "qwenmax"):
        ITEM_DIR.mkdir(parents=True, exist_ok=True)
        q2 = ITEM_DIR / "Q2.md"
        if not q2.is_file():
            write_item(2)
        seats = {
            "luna": ("openai/gpt-5.6-luna", True, False, False),
            "glm": ("z-ai/glm-5.3-flash", False, False, False),
            "ling": ("inclusionai/ling-3.0-flash", False, False, True),
            "dspro": ("deepseek/deepseek-v4-pro-0813", False, True, False),
            "qwenmax": ("qwen/qwen3.8-max-0902", False, True, False),
        }
        model, flex, skip, compact = seats[q]
        if q in FAT_SEATS:
            sys_text = frozen_fat()
            text = Q2_ITEM.rstrip() + "\n"
            text = text.replace(
                "REVIEW 2 of 2", "INDEPENDENT REVIEW (" + q + ")", 1)
            item_path = ITEM_DIR / ("Q_" + q + "_tail.md")
        elif compact:
            sys_text = prefix
            text = Q2_ITEM.rstrip() + "\n" + slice_block(compact=True)
            text = text.replace(
                "REVIEW 2 of 2",
                "INDEPENDENT REVIEW (" + q + ", compact slices)", 1)
            item_path = ITEM_DIR / ("Q_" + q + ".md")
        else:
            sys_text = prefix
            text = q2.read_text(encoding="utf-8")
            text = text.replace(
                "REVIEW 2 of 2", "INDEPENDENT REVIEW (" + q + ")", 1)
            item_path = ITEM_DIR / ("Q_" + q + ".md")
        item_path.write_text(text, encoding="utf-8", newline="\n")
        rec = dispatch_or(
            query=q, model=model, seat=q, prefix=sys_text,
            item=item_path.read_text(encoding="utf-8"),
            out_path=OUT_DIR / ("Q_" + q + ".json"),
            max_tokens=ns.max_tokens, skip_pin=skip, flex=flex)
        out_name = "Q_" + q + ".json"
    elif q == "3":
        ITEM_DIR.mkdir(parents=True, exist_ok=True)
        fat = frozen_fat()
        text = Q3_ITEM.rstrip() + "\n" + review_excerpts()
        item_path = ITEM_DIR / "Q3.md"
        item_path.write_text(text, encoding="utf-8", newline="\n")
        rec = dispatch_or(
            query=3, model=SOL, seat="sol", prefix=fat,
            item=text, out_path=OUT_DIR / "Q3_sol.json",
            max_tokens=max(ns.max_tokens, 16000), skip_pin=False)
        out_name = "Q3_sol.json"
    elif q == "5":
        fat = frozen_fat()
        dive = OUT_DIR / "Q3_sol.json"
        if not dive.is_file():
            raise SystemExit("Q3_sol.json missing — run --query 3 first")
        obj = json.loads(dive.read_text(encoding="utf-8"))
        text = (Q5_ITEM.rstrip() + "\n\n--- DEEP DIVE (Query 3) ---\n"
                + str(obj.get("text") or ""))
        item_path = ITEM_DIR / "Q5.md"
        item_path.write_text(text, encoding="utf-8", newline="\n")
        rec = dispatch_or(
            query=5, model=SOL, seat="sol", prefix=fat,
            item=text, out_path=OUT_DIR / "Q5_sol.json",
            max_tokens=max(ns.max_tokens, 16000), skip_pin=False)
        out_name = "Q5_sol.json"
    elif q in ("5b", "5B"):
        fat = frozen_fat()
        bp = OUT_DIR / "Q5_sol.json"
        if not bp.is_file():
            raise SystemExit("Q5_sol.json missing — run --query 5 first")
        obj = json.loads(bp.read_text(encoding="utf-8"))
        text = (Q5B_ITEM.rstrip() + "\n\n--- BLUEPRINT (Query 5) ---\n"
                + str(obj.get("text") or ""))
        item_path = ITEM_DIR / "Q5b.md"
        item_path.write_text(text, encoding="utf-8", newline="\n")
        rec = dispatch_or(
            query="5b", model=TERRA, seat="terra", prefix=fat,
            item=text, out_path=OUT_DIR / "Q5b_terra.json",
            max_tokens=max(ns.max_tokens, 16000), skip_pin=False, flex=True)
        out_name = "Q5b_terra.json"
    elif q in ("5bds", "5b-ds"):
        # Different family from Sol (Rule B). Do not replace Terra artifact.
        ITEM_DIR.mkdir(parents=True, exist_ok=True)
        fat = frozen_fat()
        bp = OUT_DIR / "Q5_sol.json"
        if not bp.is_file():
            raise SystemExit("Q5_sol.json missing — run --query 5 first")
        obj = json.loads(bp.read_text(encoding="utf-8"))
        text = (Q5B_ITEM.rstrip()
                + "\nThis seat is deepseek/deepseek-v4-pro-0813 (different "
                  "family from Sol). Terra already ran; do not treat Terra as "
                  "the independent critic.\n"
                + "\n--- BLUEPRINT (Query 5) ---\n"
                + str(obj.get("text") or ""))
        item_path = ITEM_DIR / "Q5b_ds.md"
        item_path.write_text(text, encoding="utf-8", newline="\n")
        rec = dispatch_or(
            query="5bds", model="deepseek/deepseek-v4-pro-0813",
            seat="dspro", prefix=fat, item=text,
            out_path=OUT_DIR / "Q5b_dspro.json",
            max_tokens=max(ns.max_tokens, 16000), skip_pin=True)
        out_name = "Q5b_dspro.json"
    else:
        print("this runner: 1, 2, 2a, 2b, 3, 5, 5b, luna, glm, ling, dspro, qwenmax",
              file=sys.stderr)
        return 2
    usage = rec.get("usage") or {}
    print(json.dumps({
        "ok": rec.get("ok"),
        "query": rec.get("query"),
        "model": rec.get("model"),
        "http": rec.get("http"),
        "reason": rec.get("reason"),
        "out": str(OUT_DIR / out_name),
        "text_n": len(rec.get("text") or ""),
        "usd": usage.get("cost"),
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "cached_tokens": usage.get("cached_tokens"),
        "cache_write_tokens": usage.get("cache_write_tokens"),
        "prefix_bytes": rec.get("prefix_bytes"),
        "item_bytes": rec.get("item_bytes"),
        "reasoning_effort": rec.get("reasoning_effort"),
        "detail": (rec.get("detail") or "")[:240],
    }))
    return 0 if rec.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
