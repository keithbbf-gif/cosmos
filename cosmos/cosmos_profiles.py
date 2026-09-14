#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_profiles — occupancy skins + per-profile MOTIF engine.

Each profile owns a MOTIF 9-stage skin. Stage 1 is PROBLEM STATEMENT /
STATED GOAL. Stage 8 is IMPLEMENT (was IMPROVE). Write dest depends on
the running profile. GET never mutates and never mkdir. POST does not
start MOTIF and does not publish.

    py -3.14 cosmos\\\\cosmos_profiles.py --selftest
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

SCHEMA = "cosmos-profiles/1"
ENGINE_NAME = "engine.json"
MAX_TEXT = 80_000
MAX_NOTE = 4_000
MAX_PATH = 400

# Pack key `define` is on-disk. Display is PROBLEM STATEMENT / STATED GOAL.
MOTIF_STAGES = (
    {"id": "define", "n": 1, "name": "PROBLEM / GOAL",
     "hint": "PROBLEM STATEMENT / STATED GOAL. Freeze WHAT / WHY / acceptance. Verbatim. RESEARCH does not start without it."},
    {"id": "research", "n": 2, "name": "RESEARCH",
     "hint": "DOM rails. SGH + GEM first, both, in parallel. Returns on disk before BUILD."},
    {"id": "arch", "n": 3, "name": "ARCH",
     "hint": "Decision rubric first. Independent designs. No peeking."},
    {"id": "consensus1", "n": 4, "name": "CONSENSUS",
     "hint": "Bar: plurality / majority / complete. HITL or AUTO. No third model resolves."},
    {"id": "build", "n": 5, "name": "BUILD",
     "hint": "N adversarial builders. GitHub/GitLab through Gitur before the live tree."},
    {"id": "critics", "n": 6, "name": "CRITICS",
     "hint": "Different-family review vs the frozen statement."},
    {"id": "consensus2", "n": 7, "name": "CONSENSUS",
     "hint": "Adjudication. Same bar as stage 4."},
    {"id": "improve", "n": 8, "name": "IMPLEMENT",
     "hint": "Was IMPROVE. CCr applies once continuation is met. Dest is profile-specific."},
    {"id": "iterate", "n": 9, "name": "ITERATE",
     "hint": "Return to PROBLEM STATEMENT / STATED GOAL. Runtime-binding, not a green log."},
)
STAGE_IDS = frozenset(s["id"] for s in MOTIF_STAGES)
STAGE_BY_ID = {s["id"]: s for s in MOTIF_STAGES}
STAGE_BY_N = {s["n"]: s for s in MOTIF_STAGES}

# Portfolio Studio — frozen contract (PS-01) + seven-product live fold (PS-04).
PORTFOLIO_STUDIO_SCHEMA = "cosmos-portfolio-studio/1"
STAGE_PROJECTION_SCHEMA = "cosmos-profiles-stage-projection/1"
TYPED_STATE_SCHEMA = "cosmos-profiles-typed-state/1"
TRANSITION_SCHEMA = "cosmos-profiles-transition/1"
PORTFOLIO_PRODUCTS_SCHEMA = "cosmos-portfolio-products/1"

JUKEBOX_QUEUE_WORDS = frozenset({"QUEUED", "RUNNING", "BROKE", "CLEAN", "FINDINGS"})
STAGE_PROJECTION_LIVE_FIELDS = ("queue_word", "job_id", "heat_class")
TYPED_STATE_LIVE_VALUES = frozenset({
    "UNMEASURED",
    "QUEUED",
    "RUNNING",
    "STALE_RUNNING",
    "CLEAN",
    "BROKE",
    "FINDINGS",
})

# docs/PROFILES.md numbered order — seven canonical occupancy products.
PORTFOLIO_PRODUCT_IDS = (
    "ups",
    "forge",
    "crucible",
    "differentiator",
    "diligence",
    "docket",
    "website",
)

FORGE_DEST = (
    ("local", "Local file"),
    ("github", "GitHub — Gitur before the live tree"),
    ("gitlab", "GitLab — Gitur before the live tree"),
    ("gdrive", "Cloud drive — Google Drive"),
    ("onedrive", "Cloud drive — OneDrive"),
)
WEBSITE_DEST = (
    ("staged", "Staged site — preview, not live"),
    ("sandbox", "Sandbox"),
    ("publish", "Publish online — Keith click; this TUI does not publish"),
    ("github", "GitHub — Gitur before the live tree"),
    ("gitlab", "GitLab — Gitur before the live tree"),
)
LEGAL_DEST = (
    ("local", "Local file on this profile's tree"),
    ("github", "GitHub — Gitur before the live tree"),
    ("gdrive", "Cloud drive — Google Drive"),
)
GITUR_DESTS = frozenset({"github", "gitlab"})

PROFILES = (
    {"id": "forge", "label": "Forge — Coding", "kind": "coding",
     "dest": FORGE_DEST, "status": "cooking",
     "note": "Coding profile. MOTIF sequence on top. Left tabs: Session, Seats, Estimate, TidyUP, then a tab per MOTIF step for setup. Background free CLI for RESEARCH→CONSENSUS."},
    {"id": "crucible", "label": "Crucible", "kind": "legal",
     "dest": LEGAL_DEST, "status": "named",
     "note": "Plaintiff / defense / judge. Own Legal tree."},
    {"id": "diligence", "label": "Diligence", "kind": "deal",
     "dest": LEGAL_DEST, "status": "named",
     "note": "Bull / bear / independent risk. Not Legal. Not Medical."},
    {"id": "docket", "label": "Docket", "kind": "ip",
     "dest": LEGAL_DEST, "status": "named",
     "note": "Patents / trademarks / copyrights. Filing is Legal + Keith."},
    {"id": "ups", "label": "UPS", "kind": "physics",
     "dest": FORGE_DEST, "status": "needs_keith",
     "note": "Spectra / UPS-JUDGE. Do not invent the July app."},
    {"id": "differentiator", "label": "Differentiator", "kind": "medical",
     "dest": LEGAL_DEST, "status": "named",
     "note": "Anonymized casefiles. Anonymize is a gate."},
    {"id": "website", "label": "Website GC", "kind": "site",
     "dest": WEBSITE_DEST, "status": "cooking",
     "note": "Site MOTIF. IMPLEMENT dest: staged site, sandbox, publish online, or Gitur."},
)
PROFILE_IDS = frozenset(p["id"] for p in PROFILES)
DEFAULT_PROFILE = "website"

# Per-profile left-tab skin. MOTIF 9 is the default; Coding keeps tools on
# the left and the 9-stage sequence on top, each step its own setup pane.
FORGE_SKIN_TABS = (
    {"id": "session", "label": "Session", "kind": "mount",
     "mount": ["home-code"],
     "hint": "CCr/GBW is background grok CLI unless called forward. This left pane is the live interface when forwarded. Does not spawn a grok TUI."},
    {"id": "seats", "label": "Seats", "kind": "mount",
     "mount": ["panel-forge-ccr", "panel-forge-adv"],
     "hint": "CCr model/via. Add adversarial coders and pick a model for each seat."},
    {"id": "estimate", "label": "Estimate", "kind": "mount",
     "mount": ["panel-forge-job"],
     "hint": "Job token estimate × rate card. Not the Core spend gate."},
    {"id": "tidyup", "label": "TidyUP / BOOTUP", "kind": "mount",
     "mount": ["panel-session-kit"],
     "hint": "TidyUP, TU2, BU/BOOTUP pointer, autosave, auto-resession. SAVE does not fire a resession."},
)


def motif_skin_tabs() -> list[dict]:
    return [
        {"id": s["id"], "label": "%d %s" % (s["n"], s["name"]), "kind": "motif",
         "hint": s["hint"]}
        for s in MOTIF_STAGES
    ]


def skin_tabs_for(profile_id: str) -> list[dict]:
    if profile_id == "forge":
        return [dict(t) for t in FORGE_SKIN_TABS] + motif_skin_tabs()
    return motif_skin_tabs()


class ProfileError(RuntimeError):
    """kind in {BAD_INPUT, REFUSED, BROKE}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _iso_now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def dir_for(paths, profile: str) -> Path:
    return paths.role("state", "profiles", profile)


def engine_path(paths, profile: str) -> Path:
    return dir_for(paths, profile) / ENGINE_NAME


def dest_via_gitur(kind: str) -> bool:
    return str(kind or "").strip().lower() in GITUR_DESTS


def catalog() -> list[dict]:
    rows = []
    for p in PROFILES:
        rows.append({
            "id": p["id"],
            "label": p["label"],
            "kind": p["kind"],
            "status": p["status"],
            "note": p["note"],
            "dest_catalog": [{"id": i, "label": lab} for i, lab in p["dest"]],
            "skin_tabs": skin_tabs_for(p["id"]),
            "motif_top": p["id"] == "forge",
        })
    return rows


def _profile(pid: str) -> dict:
    pid = str(pid or "").strip().lower()
    if pid not in PROFILE_IDS:
        raise ProfileError("BAD_INPUT", f"unknown profile {pid!r}")
    return next(p for p in PROFILES if p["id"] == pid)


def _dest_ids(profile_row: dict) -> set[str]:
    return {d[0] for d in profile_row["dest"]}


def default_dest(profile_row: dict) -> dict:
    first = profile_row["dest"][0][0]
    return {
        "kind": first,
        "path": "",
        "via_gitur": dest_via_gitur(first),
    }


def default_step_setup() -> dict:
    """Per-step setup for every MOTIF stage. Folders / files / prompt / roles
    are occupancy setup, not invented scores. Background free CLI is
    RESEARCH→CONSENSUS only."""
    bars = frozenset(("research", "arch", "consensus1", "critics", "consensus2"))
    out = {}
    for s in MOTIF_STAGES:
        sid = s["id"]
        out[sid] = {
            "bar": "majority" if sid in bars else "",
            "arch_choice": "auto" if sid == "arch" else "",
            "n_free": 3 if sid in bars else 0,
            "via": "cli",
            "folders": "",
            "files": "",
            "prompt": "",
            "roles": "",
        }
    return out


def default_engine(profile_id: str = DEFAULT_PROFILE) -> dict:
    row = _profile(profile_id)
    notes = {s["id"]: "" for s in MOTIF_STAGES}
    return {
        "schema": SCHEMA,
        "profile": row["id"],
        "label": row["label"],
        "define": {"text": "", "saved_at": None},
        "stages": notes,
        "step_setup": default_step_setup(),
        "dest": default_dest(row),
        "saved_at": None,
        "kind": "NO_SOURCE",
        "note": (
            "MOTIF engine skin for this profile. SAVE does not start MOTIF. "
            "IMPLEMENT dest is profile-specific. Publish is Keith's click."
        ),
    }


def _public_step_setup(raw) -> dict:
    base = default_step_setup()
    src = raw if isinstance(raw, dict) else {}
    out = {}
    for sid, dflt in base.items():
        got = src.get(sid) if isinstance(src.get(sid), dict) else {}
        bar = str(got.get("bar") or dflt["bar"]).strip().lower()
        if bar and bar not in ("plurality", "majority", "complete"):
            bar = dflt["bar"]
        choice = str(got.get("arch_choice") or dflt["arch_choice"]).strip().lower()
        if choice and choice not in ("auto", "hitl"):
            choice = dflt["arch_choice"]
        try:
            n_free = int(got.get("n_free") if got.get("n_free") not in (None, "") else dflt["n_free"])
        except (TypeError, ValueError):
            n_free = dflt["n_free"]
        n_cap = 5 if dflt["n_free"] else 0
        out[sid] = {
            "bar": bar,
            "arch_choice": choice,
            "n_free": max(0, min(n_free, n_cap or 5)) if n_cap else 0,
            "via": "cli",
            "folders": str(got.get("folders") or dflt["folders"] or "")[:MAX_PATH],
            "files": str(got.get("files") or dflt["files"] or "")[:MAX_NOTE],
            "prompt": str(got.get("prompt") or dflt["prompt"] or "")[:MAX_NOTE],
            "roles": str(got.get("roles") or dflt["roles"] or "")[:MAX_NOTE],
        }
    return out


def _public_dest(raw, profile_row: dict) -> dict:
    src = raw if isinstance(raw, dict) else {}
    kind = str(src.get("kind") or "").strip().lower()
    allowed = _dest_ids(profile_row)
    if not kind:
        kind = profile_row["dest"][0][0]
    if kind not in allowed:
        raise ProfileError("BAD_INPUT", f"unknown dest {kind!r} for {profile_row['id']}")
    path = str(src.get("path") or "").strip()[:MAX_PATH]
    return {
        "kind": kind,
        "path": path,
        "via_gitur": dest_via_gitur(kind),
    }


def load_engine(paths, profile_id: str) -> dict:
    row = _profile(profile_id)
    base = default_engine(row["id"])
    p = engine_path(paths, row["id"])
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
    text = str((rec.get("define") or {}).get("text") or "")[:MAX_TEXT]
    stages = dict(base["stages"])
    incoming = rec.get("stages") if isinstance(rec.get("stages"), dict) else {}
    for sid in STAGE_IDS:
        stages[sid] = str(incoming.get(sid) or "")[:MAX_NOTE]
    try:
        dest = _public_dest(rec.get("dest"), row)
    except ProfileError:
        dest = default_dest(row)
    return {
        "schema": SCHEMA,
        "profile": row["id"],
        "label": row["label"],
        "define": {
            "text": text,
            "saved_at": (rec.get("define") or {}).get("saved_at"),
        },
        "stages": stages,
        "step_setup": _public_step_setup(rec.get("step_setup")),
        "dest": dest,
        "saved_at": rec.get("saved_at"),
        "kind": "OK",
        "note": base["note"],
    }


def save_engine(paths, body: dict) -> dict:
    if not isinstance(body, dict):
        raise ProfileError("BAD_INPUT", "body must be a JSON object")
    row = _profile(body.get("profile") or DEFAULT_PROFILE)
    cur = load_engine(paths, row["id"])
    if "define" in body:
        d = body["define"]
        if isinstance(d, str):
            text = d
        elif isinstance(d, dict):
            text = str(d.get("text") or "")
        else:
            raise ProfileError("BAD_INPUT", "define must be text or {text}")
        if len(text) > MAX_TEXT:
            raise ProfileError("REFUSED", f"statement longer than {MAX_TEXT} chars")
        cur["define"] = {"text": text, "saved_at": _iso_now()}
    if "stages" in body:
        src = body["stages"]
        if not isinstance(src, dict):
            raise ProfileError("BAD_INPUT", "stages must be an object")
        for sid, note in src.items():
            if sid not in STAGE_IDS:
                raise ProfileError("BAD_INPUT", f"unknown MOTIF stage {sid!r}")
            cur["stages"][sid] = str(note or "")[:MAX_NOTE]
    if "dest" in body:
        cur["dest"] = _public_dest(body["dest"], row)
    if "step_setup" in body:
        cur["step_setup"] = _public_step_setup(body["step_setup"])
    cur["saved_at"] = _iso_now()
    cur["kind"] = "OK"
    d = dir_for(paths, row["id"])
    d.mkdir(parents=True, exist_ok=True)
    out = {
        "schema": SCHEMA,
        "profile": row["id"],
        "label": row["label"],
        "define": cur["define"],
        "stages": cur["stages"],
        "step_setup": cur.get("step_setup") or default_step_setup(),
        "dest": cur["dest"],
        "saved_at": cur["saved_at"],
        "note": cur["note"],
    }
    engine_path(paths, row["id"]).write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out["kind"] = "OK"
    return snapshot(paths, profile=row["id"], rec=out)


def _unmeasured_live_slot(field: str) -> dict:
    """Explicit empty live slot — never 0, never inferred."""
    return {"field": field, "kind": "UNMEASURED", "value": None}


def motif_transition_edges() -> list[dict]:
    """Frozen MOTIF advance edges (SAVE does not walk these)."""
    order = [s["id"] for s in MOTIF_STAGES]
    edges: list[dict] = []
    for i, fr in enumerate(order):
        to = order[(i + 1) % len(order)]
        edges.append({"id": "%s_to_%s" % (fr, to), "from_stage": fr, "to_stage": to})
    edges[-1]["note"] = "ITERATE returns to PROBLEM STATEMENT / STATED GOAL"
    return edges


def portfolio_studio_contract() -> dict:
    """Frozen Portfolio Studio schemas (contract only until live-bound)."""
    return {
        "stage_projection": {
            "schema": STAGE_PROJECTION_SCHEMA,
            "live_fields": list(STAGE_PROJECTION_LIVE_FIELDS),
            "queue_words": sorted(JUKEBOX_QUEUE_WORDS),
            "stage_ids": [s["id"] for s in MOTIF_STAGES],
        },
        "typed_state": {
            "schema": TYPED_STATE_SCHEMA,
            "live_values": sorted(TYPED_STATE_LIVE_VALUES),
            "note": "Live jukebox/MOTIF fold only. Persisted notes live in engine.stages.",
        },
        "transition": {
            "schema": TRANSITION_SCHEMA,
            "allowed_edges": motif_transition_edges(),
            "note": "WD2/driver when bound. GET /api/v1/profiles SAVE does not advance.",
        },
    }


def _portfolio_stage_projection_live() -> list[dict]:
    rows = []
    for s in MOTIF_STAGES:
        row = {"stage_id": s["id"], "n": s["n"]}
        for field in STAGE_PROJECTION_LIVE_FIELDS:
            row[field] = _unmeasured_live_slot(field)
        rows.append(row)
    return rows


def _portfolio_typed_state_live() -> list[dict]:
    return [
        {"stage_id": s["id"], "n": s["n"], "state": "UNMEASURED", "since": None}
        for s in MOTIF_STAGES
    ]


def portfolio_studio_fold(profile_id: str) -> dict:
    """Per-occupant Portfolio Studio contract + unbound live slots (PS-01)."""
    return {
        "schema": PORTFOLIO_STUDIO_SCHEMA,
        "profile": profile_id,
        "contract": portfolio_studio_contract(),
        "live": {
            "kind": "UNMEASURED",
            "source": "UNMEASURED",
            "stage_projection": _portfolio_stage_projection_live(),
            "typed_state": _portfolio_typed_state_live(),
            "transition": {
                "current": {
                    "kind": "UNMEASURED",
                    "edge_id": None,
                    "from_stage": None,
                    "to_stage": None,
                    "at": None,
                },
            },
        },
        "note": (
            "Live Core jukebox heat and MOTIF driver are not bound on this route "
            "yet. Every live slot stays UNMEASURED — never inferred."
        ),
    }


def portfolio_studio_live_is_honest(live: dict) -> bool:
    """True when every unbound live field is explicitly UNMEASURED (not 0)."""
    if not isinstance(live, dict):
        return False
    if live.get("kind") != "UNMEASURED" or live.get("source") != "UNMEASURED":
        return False
    cur = (live.get("transition") or {}).get("current") or {}
    if cur.get("kind") != "UNMEASURED":
        return False
    for n in (cur.get("edge_id"), cur.get("from_stage"), cur.get("to_stage"), cur.get("at")):
        if n == 0:
            return False
    for row in live.get("stage_projection") or []:
        if not isinstance(row, dict):
            return False
        for field in STAGE_PROJECTION_LIVE_FIELDS:
            slot = row.get(field) or {}
            if slot.get("kind") != "UNMEASURED" or slot.get("value") is not None:
                return False
            if slot.get("value") == 0:
                return False
    for row in live.get("typed_state") or []:
        if not isinstance(row, dict):
            return False
        if row.get("state") != "UNMEASURED" or row.get("since") is not None:
            return False
        if row.get("since") == 0:
            return False
    return True


def _stage_meta(n: int | None) -> dict:
    if n is None or n not in STAGE_BY_N:
        return {"n": None, "id": None, "name": None}
    row = STAGE_BY_N[n]
    return {"n": row["n"], "id": row["id"], "name": row["name"]}


def _parse_stage_n(raw) -> int | None:
    """Integer stage 1..9, or stage id → n. Never invents 0."""
    if raw is None or raw == "":
        return None
    if isinstance(raw, bool):
        return None
    if isinstance(raw, (int, float)):
        n = int(raw)
        return n if 1 <= n <= 9 else None
    text = str(raw).strip().lower()
    if text in STAGE_BY_ID:
        return STAGE_BY_ID[text]["n"]
    try:
        n = int(text)
    except (TypeError, ValueError):
        return None
    return n if 1 <= n <= 9 else None


def _explicit_product_tag(obj) -> str | None:
    """Return a canonical product id only when a field explicitly names it."""
    if not isinstance(obj, dict):
        return None
    for key in ("profile", "product_id", "occupancy", "Portfolio", "portfolio"):
        v = str(obj.get(key) or "").strip().lower()
        if v in PROFILE_IDS:
            return v
    # `product` on work-order public rows is an output filename — only trust
    # it when the value itself is a canonical occupancy id.
    prod = str(obj.get("product") or "").strip().lower()
    if prod in PROFILE_IDS:
        return prod
    return None


def _evidence(source: str, *, kind: str, seq=None, t=None,
              stage_n: int | None = None, detail: str | None = None) -> dict:
    meta = _stage_meta(stage_n) if kind in ("MEASURED", "BOUND") else _stage_meta(None)
    return {
        "source": source,
        "kind": kind,
        "seq": None if seq is None else int(seq),
        "t": None if t is None else float(t),
        "stage_n": meta["n"],
        "stage_id": meta["id"],
        "detail": None if not detail else str(detail)[:240],
    }


def _tracker_evidence(paths, product_id: str) -> dict:
    dest = paths.state("motif_tracker.json")
    if not dest.is_file():
        return _evidence("tracker", kind="NO_SOURCE",
                         detail="motif_tracker.json absent")
    try:
        body = json.loads(dest.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return _evidence("tracker", kind="BROKE", detail=str(e)[:160])
    rows = body.get("rows") if isinstance(body, dict) else None
    if not isinstance(rows, list):
        return _evidence("tracker", kind="BROKE", detail="rows missing")
    gen = body.get("generated_epoch")
    t = float(gen) if isinstance(gen, (int, float)) else None
    tagged = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        tag = _explicit_product_tag(row)
        if tag is None and str(row.get("slug") or "").strip().lower() == product_id:
            tag = product_id
        if tag == product_id:
            tagged.append(row)
    if not tagged:
        if rows:
            return _evidence(
                "tracker", kind="UNATTRIBUTED", t=t,
                detail="tracker present; no row tags this product",
            )
        return _evidence("tracker", kind="NO_SOURCE", detail="tracker empty")
    row = tagged[-1]
    n = _parse_stage_n(row.get("current_stage"))
    if n is None:
        return _evidence(
            "tracker", kind="UNMEASURED", t=t,
            detail="tagged row has no motif-9 current_stage",
        )
    meta = _stage_meta(n)
    return _evidence(
        "tracker", kind="MEASURED", t=t, stage_n=meta["n"],
        detail="slug=%s current_stage=%s id=%s" % (
            row.get("slug"), meta["n"], meta["id"]),
    )


def _ledger_evidence(ledger, product_id: str) -> dict:
    if ledger is None:
        return _evidence("ledger", kind="NO_SOURCE", detail="ledger not composed")
    try:
        recs = list(ledger.verify())
    except Exception as e:  # noqa: BLE001
        return _evidence("ledger", kind="BROKE", detail=str(e)[:160])
    if not recs:
        return _evidence("ledger", kind="NO_SOURCE", detail="ledger empty")
    best = None
    saw_any = False
    for rec in recs:
        if not isinstance(rec, dict):
            continue
        payload = rec.get("payload") if isinstance(rec.get("payload"), dict) else {}
        tag = _explicit_product_tag(payload)
        if tag != product_id:
            continue
        saw_any = True
        n = _parse_stage_n(
            payload.get("stage_n")
            if payload.get("stage_n") is not None
            else payload.get("motif_stage")
            if payload.get("motif_stage") is not None
            else payload.get("stage")
            if payload.get("stage") is not None
            else payload.get("stage_id")
        )
        cand = {
            "kind": "MEASURED" if n is not None else "UNMEASURED",
            "seq": rec.get("seq"),
            "t": rec.get("t"),
            "stage_n": n,
            "event": rec.get("event"),
        }
        if best is None or int(cand.get("seq") or 0) >= int(best.get("seq") or 0):
            best = cand
    if not best:
        return _evidence(
            "ledger", kind="UNATTRIBUTED" if saw_any or recs else "NO_SOURCE",
            detail=("ledger present; no payload tags this product"
                    if recs else "ledger empty"),
        )
    if best["kind"] != "MEASURED":
        return _evidence(
            "ledger", kind="UNMEASURED",
            seq=best.get("seq"), t=best.get("t"),
            detail="tagged payload without motif-9 stage",
        )
    meta = _stage_meta(best["stage_n"])
    return _evidence(
        "ledger", kind="MEASURED",
        seq=best.get("seq"), t=best.get("t"), stage_n=meta["n"],
        detail="event=%s stage n=%s id=%s" % (
            best.get("event"), meta["n"], meta["id"]),
    )


def _work_order_evidence(paths, product_id: str) -> dict:
    try:
        from cosmos_work_order import fold_work_orders, work_order_dirs_ro
    except Exception as e:  # noqa: BLE001
        return _evidence("work_order", kind="BROKE", detail=str(e)[:160])
    try:
        fold = fold_work_orders(paths, limit=64)
    except Exception as e:  # noqa: BLE001
        return _evidence("work_order", kind="BROKE", detail=str(e)[:160])
    n_total = int(fold.get("n_total") or 0)
    # Prefer explicit profile tags on the live folder JSON (six-field SOP has
    # no profile; additive profile/product_id is the only honest tag).
    tagged = []
    try:
        dirs = work_order_dirs_ro(paths)
    except Exception:  # noqa: BLE001
        dirs = {}
    for folder, d in (dirs.items() if isinstance(dirs, dict) else []):
        if not hasattr(d, "is_dir") or not d.is_dir():
            continue
        try:
            names = list(d.iterdir())
        except OSError:
            continue
        for p in names:
            if not p.is_file() or p.suffix.lower() != ".json":
                continue
            if p.name.startswith("_") or p.name.endswith(".tmp"):
                continue
            try:
                raw = json.loads(p.read_text(encoding="utf-8"))
            except (OSError, ValueError, UnicodeDecodeError):
                continue
            if not isinstance(raw, dict):
                continue
            if _explicit_product_tag(raw) != product_id:
                continue
            tagged.append(raw)
    if not tagged:
        if n_total > 0:
            return _evidence(
                "work_order", kind="UNATTRIBUTED",
                detail="work orders present; none tag this product",
            )
        return _evidence("work_order", kind="NO_SOURCE",
                         detail="no work orders")
    last = sorted(
        tagged,
        key=lambda r: str(
            r.get("picked_at") or r.get("filed_at")
            or r.get("dropped_at") or r.get("Timestamp") or ""
        ),
    )[-1]
    n = _parse_stage_n(
        last.get("stage_n")
        if last.get("stage_n") is not None
        else last.get("stage")
        if last.get("stage") is not None
        else last.get("stage_id")
    )
    ts = last.get("picked_at") or last.get("filed_at") or last.get("Timestamp")
    t = None
    if isinstance(ts, (int, float)):
        t = float(ts)
    if n is None:
        return _evidence(
            "work_order", kind="UNMEASURED", t=t,
            detail="order %s tags product but not motif-9 stage"
            % (last.get("order_id") or last.get("id")),
        )
    meta = _stage_meta(n)
    return _evidence(
        "work_order", kind="MEASURED", t=t, stage_n=meta["n"],
        detail="order=%s stage n=%s id=%s" % (
            last.get("order_id"), meta["n"], meta["id"]),
    )


def _lease_evidence(paths, product_id: str) -> dict:
    try:
        from cosmos_ccr import read_lease
        lease = read_lease(paths)
    except Exception as e:  # noqa: BLE001
        return _evidence("lease", kind="BROKE", detail=str(e)[:160])
    if not lease:
        return _evidence("lease", kind="NO_SOURCE", detail="CCR.lease absent")
    t = float(lease.get("taken_at") or 0) or None
    # One occupant / one CCr pen: lease names the coding (forge) writer only.
    tag = _explicit_product_tag(lease)
    if tag is None and product_id == "forge":
        tag = "forge"
    if tag != product_id:
        return _evidence(
            "lease", kind="UNATTRIBUTED", t=t,
            detail="lease does not tag product %s" % product_id,
        )
    n = _parse_stage_n(
        lease.get("stage_n")
        if lease.get("stage_n") is not None
        else lease.get("stage")
    )
    if n is None:
        return _evidence(
            "lease", kind="UNMEASURED", t=t,
            detail="CCR held sid=%s stream=%s; no motif-9 stage"
            % (lease.get("sid"), lease.get("stream")),
        )
    meta = _stage_meta(n)
    return _evidence(
        "lease", kind="MEASURED", t=t, stage_n=meta["n"],
        detail="CCR held stage n=%s id=%s" % (meta["n"], meta["id"]),
    )


def _scheduler_evidence(paths, product_id: str) -> dict:
    assigned_p = paths.state("watchdog2", "assigned.json")
    inflight_p = paths.state("inflight.jsonl")
    detail_parts = []
    stage_n = None
    source_t = None
    tagged = False
    if assigned_p.is_file():
        try:
            assigned = json.loads(assigned_p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            assigned = None
        if isinstance(assigned, dict):
            source_t = float(
                assigned.get("updated_at") or assigned.get("t") or 0
            ) or source_t
            if _explicit_product_tag(assigned) == product_id:
                tagged = True
                detail_parts.append("assigned.json tags product")
                stage_n = _parse_stage_n(
                    assigned.get("stage_n")
                    if assigned.get("stage_n") is not None
                    else assigned.get("stage")
                    if assigned.get("stage") is not None
                    else assigned.get("current_stage")
                )
            jobs = assigned.get("jobs") if isinstance(assigned.get("jobs"), list) else []
            for job in jobs:
                if not isinstance(job, dict):
                    continue
                if _explicit_product_tag(job) != product_id:
                    continue
                tagged = True
                detail_parts.append("assigned job tags product")
                stage_n = _parse_stage_n(
                    job.get("stage_n")
                    if job.get("stage_n") is not None
                    else job.get("stage")
                ) or stage_n
    if inflight_p.is_file():
        try:
            from cosmos_inflight import Inflight
            active = Inflight(inflight_p).active()
        except Exception:  # noqa: BLE001
            active = {}
        for token, rec in (active.items() if isinstance(active, dict) else []):
            if not isinstance(rec, dict):
                continue
            tag = _explicit_product_tag(rec)
            slug = str(rec.get("slug") or "").strip().lower()
            if tag is None and slug == product_id:
                tag = product_id
            if tag != product_id:
                continue
            tagged = True
            detail_parts.append("inflight %s" % token)
            source_t = float(rec.get("at") or 0) or source_t
            stage_n = _parse_stage_n(
                rec.get("stage") if rec.get("stage") is not None else rec.get("stage_n")
            ) or stage_n
    if not tagged:
        present = assigned_p.is_file() or inflight_p.is_file()
        return _evidence(
            "scheduler",
            kind="UNATTRIBUTED" if present else "NO_SOURCE",
            detail=("scheduler present; no row tags this product"
                    if present else "assigned/inflight absent"),
        )
    if stage_n is None:
        return _evidence(
            "scheduler", kind="UNMEASURED", t=source_t,
            detail="; ".join(detail_parts) or "tagged without stage",
        )
    meta = _stage_meta(stage_n)
    return _evidence(
        "scheduler", kind="MEASURED", t=source_t, stage_n=meta["n"],
        detail="; ".join(detail_parts) + " stage n=%s id=%s" % (meta["n"], meta["id"]),
    )


def _pick_stage_fold(evidence: list[dict]) -> dict:
    """Measured/bound motif-9 fold, or typed non-measurement. Never n=0."""
    measured = [
        e for e in evidence
        if e.get("kind") == "MEASURED" and e.get("stage_n") in STAGE_BY_N
    ]
    if measured:
        # Prefer ledger > work_order > scheduler > tracker > lease.
        rank = {"ledger": 0, "work_order": 1, "scheduler": 2, "tracker": 3, "lease": 4}
        measured.sort(key=lambda e: (
            rank.get(e.get("source"), 99),
            -(e.get("seq") or -1),
            -(e.get("t") or -1.0),
        ))
        primary = measured[0]
        agree = [e for e in measured if e.get("stage_n") == primary.get("stage_n")]
        kind = "BOUND" if len({e.get("source") for e in agree}) >= 2 else "MEASURED"
        meta = _stage_meta(primary.get("stage_n"))
        # Prefer ledger seq/t for refuse watermark when present among agreers.
        watermark = primary
        for e in agree:
            if e.get("source") == "ledger" and e.get("seq") is not None:
                watermark = e
                break
        return {
            "kind": kind,
            "contract": "motif-9",
            "n": meta["n"],
            "id": meta["id"],
            "name": meta["name"],
            "source": primary.get("source"),
            "sources": sorted({e.get("source") for e in agree}),
            "seq": watermark.get("seq"),
            "t": watermark.get("t"),
        }
    order = ("ledger", "work_order", "scheduler", "tracker", "lease")
    for src in order:
        ev = next((e for e in evidence if e.get("source") == src), None)
        if ev and ev.get("kind") in ("UNATTRIBUTED", "UNMEASURED", "BROKE"):
            return {
                "kind": ev["kind"],
                "contract": "motif-9",
                "n": None,
                "id": None,
                "name": None,
                "source": src,
                "sources": [src],
                "seq": ev.get("seq"),
                "t": ev.get("t"),
            }
    return {
        "kind": "UNMEASURED",
        "contract": "motif-9",
        "n": None,
        "id": None,
        "name": None,
        "source": None,
        "sources": [],
        "seq": None,
        "t": None,
    }


def _occupant_fold(product_id: str, lease_ev: dict) -> dict:
    """One occupant per profile. Lease only binds forge unless tagged."""
    if (lease_ev.get("kind") in ("MEASURED", "UNMEASURED")
            and lease_ev.get("source") == "lease"):
        # Tagged/held lease for this product — occupancy measured; stage may not be.
        return {
            "kind": "MEASURED",
            "profile": product_id,
            "source": "lease",
            "seq": lease_ev.get("seq"),
            "t": lease_ev.get("t"),
            "detail": lease_ev.get("detail"),
        }
    if lease_ev.get("kind") == "UNATTRIBUTED":
        return {
            "kind": "UNATTRIBUTED",
            "profile": product_id,
            "source": "lease",
            "seq": lease_ev.get("seq"),
            "t": lease_ev.get("t"),
            "detail": lease_ev.get("detail"),
        }
    return {
        "kind": "UNMEASURED",
        "profile": product_id,
        "source": None,
        "seq": None,
        "t": None,
        "detail": "one occupant per profile; no lease tags this product",
    }


def portfolio_projection(paths, *, ledger=None) -> dict:
    """Seven-product live fold from tracker/ledger/scheduler/lease/WO only.

    GET never mkdir. No second store. Untagged → UNATTRIBUTED. Absent →
    UNMEASURED (never 0). refuse_inference_after carries source seq/time.
    """
    products = []
    for pid in PORTFOLIO_PRODUCT_IDS:
        row = next(p for p in PROFILES if p["id"] == pid)
        tracker_ev = _tracker_evidence(paths, pid)
        ledger_ev = _ledger_evidence(ledger, pid)
        wo_ev = _work_order_evidence(paths, pid)
        lease_ev = _lease_evidence(paths, pid)
        sched_ev = _scheduler_evidence(paths, pid)
        evidence = [tracker_ev, ledger_ev, sched_ev, lease_ev, wo_ev]
        stage = _pick_stage_fold(evidence)
        occupant = _occupant_fold(pid, lease_ev)
        refuse = {
            "seq": stage.get("seq"),
            "t": stage.get("t"),
            "source": stage.get("source"),
            "stage_kind": stage.get("kind"),
        }
        products.append({
            "id": pid,
            "label": row["label"],
            "profile": pid,
            "stage": stage,
            "occupant": occupant,
            "evidence": evidence,
            "refuse_inference_after": refuse,
        })
    return {
        "schema": PORTFOLIO_PRODUCTS_SCHEMA,
        "stage_contract": "motif-9",
        "n_products": len(products),
        "product_ids": list(PORTFOLIO_PRODUCT_IDS),
        "products": products,
        "note": (
            "Portfolio Studio seven-product live projection. Joins tracker, "
            "ledger, scheduler, lease, and work-order evidence only. Untagged "
            "is UNATTRIBUTED. Absent is UNMEASURED — never 0. Client must "
            "refuse inference past refuse_inference_after seq/time."
        ),
    }


def _bg_fold(paths, profile_id: str) -> dict:
    if profile_id != "forge":
        return {"kind": "SKIP"}
    try:
        from cosmos_forge_bg import status
        return status(paths)
    except Exception as e:  # noqa: BLE001
        return {"kind": "BROKE", "detail": f"{type(e).__name__}: {e}"[:200]}


def snapshot(paths, *, profile: str = "", rec=None, ledger=None) -> dict:
    pid = str(profile or "").strip().lower() or DEFAULT_PROFILE
    row = _profile(pid)
    engine = rec if rec is not None else load_engine(paths, row["id"])
    portfolio = portfolio_projection(paths, ledger=ledger)
    active = next((p for p in portfolio["products"] if p["id"] == row["id"]), None)
    return {
        "schema": SCHEMA,
        "ok": True,
        "profile": row["id"],
        "label": row["label"],
        "kind": engine.get("kind") or "NO_SOURCE",
        "profiles": catalog(),
        "stages": [dict(s) for s in MOTIF_STAGES],
        "dest_catalog": [{"id": i, "label": lab} for i, lab in row["dest"]],
        "skin_tabs": skin_tabs_for(row["id"]),
        "motif_top": row["id"] == "forge",
        "bar_catalog": [
            {"id": "plurality", "label": "Plurality — the most votes wins"},
            {"id": "majority", "label": "Majority — more than half of the seats"},
            {"id": "complete", "label": "Complete — every seat agrees"},
        ],
        "bg": _bg_fold(paths, row["id"]),
        "engine": engine,
        "motif_step_1": "PROBLEM STATEMENT / STATED GOAL",
        "implement_was": "IMPROVE",
        "does_not_start_motif": True,
        "does_not_publish": True,
        "portfolio_studio": portfolio_studio_fold(row["id"]),
        "portfolio": portfolio,
        "portfolio_product": active,
        "note": (
            "Per-profile MOTIF skins. Website GC IMPLEMENT dest is staged / "
            "sandbox / publish / Gitur. SAVE does not start MOTIF and does "
            "not publish. portfolio is the seven-product live projection."
        ),
    }


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

    td = Path(tempfile.mkdtemp(prefix="cosmos_profiles_"))
    root = install(td / "live", tree_id="spike-profiles")
    paths = CosmosPaths(root)

    ids = {p["id"] for p in catalog()}
    check("catalog names Website GC plus occupancy profiles",
          lambda: ids >= {"website", "forge", "crucible", "ups",
                          "diligence", "docket", "differentiator"}
          and any(p["label"] == "Website GC" for p in catalog()))
    snap = snapshot(paths, profile="website")
    check("GET missing engine is NO_SOURCE and does not mkdir",
          lambda: snap["kind"] == "NO_SOURCE"
          and not engine_path(paths, "website").exists())
    check("MOTIF is 9 stages; step 1 PROBLEM; step 8 IMPLEMENT not IMPROVE",
          lambda: [s["n"] for s in snap["stages"]] == list(range(1, 10))
          and snap["stages"][0]["name"] == "PROBLEM / GOAL"
          and snap["stages"][0]["id"] == "define"
          and snap["stages"][7]["name"] == "IMPLEMENT"
          and snap["stages"][7]["id"] == "improve"
          and snap["motif_step_1"] == "PROBLEM STATEMENT / STATED GOAL"
          and snap["implement_was"] == "IMPROVE")
    dest_ids = {d["id"] for d in snap["dest_catalog"]}
    check("Website GC IMPLEMENT dest is staged/sandbox/publish/Gitur",
          lambda: dest_ids == {"staged", "sandbox", "publish", "github", "gitlab"}
          and dest_via_gitur("github") is True
          and dest_via_gitur("staged") is False
          and dest_via_gitur("publish") is False)
    saved = save_engine(paths, {
        "profile": "website",
        "define": {"text": "WHAT: a staged site. WHY: GC profile."},
        "dest": {"kind": "staged", "path": "preview/index.html"},
        "stages": {"improve": "write the staged preview, do not publish"},
    })
    check("POST statement + staged dest persist; does not start MOTIF",
          lambda: saved["engine"]["define"]["text"].startswith("WHAT:")
          and saved["engine"]["dest"]["kind"] == "staged"
          and saved["engine"]["dest"]["via_gitur"] is False
          and saved["does_not_start_motif"] is True
          and saved["does_not_publish"] is True)
    pub = save_engine(paths, {"profile": "website",
                              "dest": {"kind": "publish"}})
    check("publish dest is named and via_gitur false (Keith click)",
          lambda: pub["engine"]["dest"]["kind"] == "publish"
          and pub["engine"]["dest"]["via_gitur"] is False)
    gh = save_engine(paths, {"profile": "website",
                             "dest": {"kind": "github",
                                      "path": "keithbbf-gif/cdeck"}})
    check("Gitur dest sets via_gitur",
          lambda: gh["engine"]["dest"]["via_gitur"] is True)
    bad = False
    try:
        save_engine(paths, {"profile": "website", "dest": {"kind": "s3"}})
    except ProfileError as e:
        bad = e.kind == "BAD_INPUT"
    check("unknown dest for Website GC is BAD_INPUT", lambda: bad)
    unk = False
    try:
        snapshot(paths, profile="chatbot")
    except ProfileError as e:
        unk = e.kind == "BAD_INPUT"
    check("ChatBot is not an occupancy profile", lambda: unk)
    forge = snapshot(paths, profile="forge")
    check("Forge dest still includes local + Gitur, not website publish",
          lambda: {d["id"] for d in forge["dest_catalog"]}
          >= {"local", "github", "gitlab"}
          and "publish" not in {d["id"] for d in forge["dest_catalog"]})
    forge_tabs = [t["id"] for t in (forge.get("skin_tabs") or [])]
    check("Coding profile: MOTIF on top; left tabs tools + a tab per MOTIF step",
          lambda: forge_tabs[:4] == ["session", "seats", "estimate", "tidyup"]
          and forge_tabs[-1] == "iterate"
          and "research" in forge_tabs
          and "consensus1" in forge_tabs
          and forge.get("motif_top") is True
          and [s["id"] for s in forge["stages"]][0] == "define"
          and forge["label"] == "Forge — Coding")
    check("Website GC does not pin MOTIF on top (left tabs ARE the 9 stages)",
          lambda: snap.get("motif_top") is False)
    setup = save_engine(paths, {
        "profile": "forge",
        "step_setup": {
            "research": {
                "folders": r"V:\A\Ai\COSMOS\docs",
                "files": "MOTIF.md",
                "prompt": "SGH + GEM first",
                "roles": "SGH · GEM",
                "bar": "majority",
                "n_free": 3,
            }
        },
    })
    rs = ((setup.get("engine") or {}).get("step_setup") or {}).get("research") or {}
    check("step setup persists folders/files/prompt/roles",
          lambda: rs.get("folders", "").endswith("docs")
          and rs.get("files") == "MOTIF.md"
          and "SGH" in (rs.get("roles") or "")
          and rs.get("prompt") == "SGH + GEM first")
    web_tabs = [t["id"] for t in (snap.get("skin_tabs") or [])]
    check("Website GC skin left tabs are the 9 MOTIF stages",
          lambda: web_tabs[0] == "define" and web_tabs[-1] == "iterate"
          and len(web_tabs) == 9)
    ps = snap.get("portfolio_studio") or {}
    check("Portfolio Studio contract frozen on profiles GET",
          lambda: ps.get("schema") == PORTFOLIO_STUDIO_SCHEMA
          and len((ps.get("contract") or {}).get("transition", {}).get("allowed_edges") or []) == 9
          and (ps.get("contract") or {}).get("stage_projection", {}).get("stage_ids")
          == [s["id"] for s in MOTIF_STAGES])
    check("Portfolio Studio live fold is UNMEASURED (never inferred, never 0)",
          lambda: portfolio_studio_live_is_honest(ps.get("live") or {}))
    pf = snap.get("portfolio") or {}
    check("portfolio projection lists seven canonical products UNMEASURED",
          lambda: pf.get("n_products") == 7
          and pf.get("stage_contract") == "motif-9"
          and pf.get("schema") == PORTFOLIO_PRODUCTS_SCHEMA
          and list(pf.get("product_ids") or []) == list(PORTFOLIO_PRODUCT_IDS)
          and {p["id"] for p in (pf.get("products") or [])} == set(PORTFOLIO_PRODUCT_IDS)
          and all(p["stage"]["kind"] == "UNMEASURED" and p["stage"]["n"] is None
                  for p in (pf.get("products") or []))
          and all(p["refuse_inference_after"]["stage_kind"] == "UNMEASURED"
                  for p in (pf.get("products") or [])))
    check("legacy profiles[] + engine + does_not_* unchanged with portfolio",
          lambda: isinstance(snap.get("profiles"), list)
          and isinstance(snap.get("engine"), dict)
          and snap.get("does_not_start_motif") is True
          and snap.get("does_not_publish") is True
          and snap.get("portfolio_product", {}).get("id") == "website")
    from cosmos_kernel import Kernel
    k = Kernel(root, worker="profiles-selftest")
    k.ledger.append("MOTIF_STAGE", {
        "profile": "forge", "stage": "research", "stage_n": 2,
    })
    pf2 = portfolio_projection(paths, ledger=k.ledger)
    forge_row = next(p for p in pf2["products"] if p["id"] == "forge")
    check("ledger-bound stage fold is measured with seq/time for client refuse",
          lambda: forge_row["stage"]["kind"] == "MEASURED"
          and forge_row["stage"]["n"] == 2
          and forge_row["stage"]["id"] == "research"
          and forge_row["refuse_inference_after"]["seq"] is not None
          and forge_row["refuse_inference_after"]["t"] is not None
          and forge_row["refuse_inference_after"]["seq"] != 0)
    # Tracker slug==product id is explicit identity; inventing website→cdeck is not.
    paths.state("motif_tracker.json").write_text(json.dumps({
        "schema": "cosmos-motif-tracker/1",
        "generated_epoch": 1_700_000_000,
        "rows": [
            {"slug": "website", "current_stage": 3, "profile": "website"},
            {"slug": "cdeck", "current_stage": 5},
        ],
    }), encoding="utf-8")
    pf3 = portfolio_projection(paths, ledger=None)
    web_row = next(p for p in pf3["products"] if p["id"] == "website")
    check("tracker binds only when slug/profile tags the product (no invented map)",
          lambda: web_row["stage"]["kind"] == "MEASURED"
          and web_row["stage"]["n"] == 3
          and web_row["stage"]["id"] == "arch"
          and web_row["refuse_inference_after"]["t"] == 1_700_000_000.0)

    failed = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (Website GC MOTIF skins; no auto-MOTIF)"
          % ("PASS" if not failed else "FAIL", len(results)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(_selftest())
