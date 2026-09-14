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
PS_SCHEMA = "cosmos-portfolio-studio/1"
PS_ROUTE = "/api/v1/profiles"
ENGINE_NAME = "engine.json"
MAX_TEXT = 80_000
MAX_NOTE = 4_000
MAX_PATH = 400
UNMEASURED = "UNMEASURED"
EMPTY = "EMPTY"

# Legacy GET/POST envelope. Additive Portfolio Studio keys live under
# portfolio_studio so existing clients keep byte/meaning of these fields.
LEGACY_SNAPSHOT_KEYS = (
    "schema", "ok", "profile", "label", "kind", "profiles", "stages",
    "dest_catalog", "skin_tabs", "motif_top", "bar_catalog", "bg",
    "engine", "motif_step_1", "implement_was", "does_not_start_motif",
    "does_not_publish", "note",
)
LEGACY_ENGINE_KEYS = (
    "schema", "profile", "label", "define", "stages", "step_setup",
    "dest", "saved_at", "kind", "note",
)
LEGACY_PROFILE_ROW_KEYS = (
    "id", "label", "kind", "status", "note", "dest_catalog",
    "skin_tabs", "motif_top",
)
LEGACY_STAGE_KEYS = ("id", "n", "name", "hint")

# Typed-state vocab. Empty is explicit. UNMEASURED is not 0.
TYPED_STATES = (
    UNMEASURED,
    "NO_SOURCE",
    "OK",
    "BROKE",
    EMPTY,
)

# Allowed transitions on the existing profiles route. Catalog, not a cursor.
# SAVE is not a MOTIF start. GET does not mutate.
TRANSITION_CATALOG = (
    {
        "id": "get_snapshot",
        "via": "GET /api/v1/profiles",
        "mutates": False,
        "starts_motif": False,
        "publishes": False,
    },
    {
        "id": "save_engine",
        "via": "POST /api/v1/profiles",
        "mutates": True,
        "starts_motif": False,
        "publishes": False,
        "from_kinds": ["NO_SOURCE", "OK", "BROKE"],
        "to_kind": "OK",
    },
)

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


def _bg_fold(paths, profile_id: str) -> dict:
    if profile_id != "forge":
        return {"kind": "SKIP"}
    try:
        from cosmos_forge_bg import status
        return status(paths)
    except Exception as e:  # noqa: BLE001
        return {"kind": "BROKE", "detail": f"{type(e).__name__}: {e}"[:200]}


def _unmeasured_stage_cursor() -> dict:
    return {"kind": UNMEASURED, "id": None, "n": None}


def _unmeasured_scalar() -> dict:
    return {"kind": UNMEASURED, "value": None}


def _unmeasured_transition() -> dict:
    return {
        "kind": UNMEASURED,
        "id": None,
        "at": None,
        "from_kind": None,
        "to_kind": None,
    }


def _transition_catalog() -> list[dict]:
    rows = []
    for t in TRANSITION_CATALOG:
        row = dict(t)
        if "from_kinds" in row:
            row["from_kinds"] = list(row["from_kinds"])
        rows.append(row)
    return rows


def stage_projection(engine) -> list[dict]:
    """Nine MOTIF rows. Catalog fields match stages[]. Live run fields
    stay UNMEASURED until Core observes a MOTIF tick. Empty note is EMPTY,
    never 0 and never a guessed status."""
    notes = engine.get("stages") if isinstance((engine or {}).get("stages"), dict) else {}
    rows = []
    for s in MOTIF_STAGES:
        note = str(notes.get(s["id"]) or "")
        rows.append({
            "id": s["id"],
            "n": s["n"],
            "name": s["name"],
            "hint": s["hint"],
            "note": note,
            "note_kind": "OK" if note else EMPTY,
            "status": UNMEASURED,
            "outcome": UNMEASURED,
            "current": None,
            "elapsed_s": None,
            "tokens": None,
            "spend_usd": None,
        })
    return rows


def portfolio_studio_fold(engine) -> dict:
    """Additive Portfolio Studio contract. Does not infer a live stage."""
    en = engine if isinstance(engine, dict) else {}
    define = en.get("define") if isinstance(en.get("define"), dict) else {}
    text = str(define.get("text") or "")
    return {
        "schema": PS_SCHEMA,
        "route": PS_ROUTE,
        "does_not_start_motif": True,
        "does_not_publish": True,
        "response": {
            "schema": SCHEMA,
            "legacy_keys": list(LEGACY_SNAPSHOT_KEYS),
            "additive": "portfolio_studio",
        },
        "typed_states": {
            "vocab": list(TYPED_STATES),
            "engine": en.get("kind") or "NO_SOURCE",
            "define": "OK" if text else EMPTY,
            "live": {
                "current_stage": UNMEASURED,
                "motif_running": UNMEASURED,
                "last_transition": UNMEASURED,
                "next_live": UNMEASURED,
                "spend": UNMEASURED,
                "occupancy_n": UNMEASURED,
            },
        },
        "stage_projection": stage_projection(en),
        "transitions": {
            "schema": PS_SCHEMA + "-transitions",
            "catalog": _transition_catalog(),
            "last": _unmeasured_transition(),
            "next_live": {"kind": UNMEASURED, "id": None},
        },
        "current_stage": _unmeasured_stage_cursor(),
        "motif_running": _unmeasured_scalar(),
        "spend": {"kind": UNMEASURED, "usd": None, "tokens": None},
        "occupancy": {"kind": UNMEASURED, "n": None},
    }


def legacy_view(snap: dict) -> dict:
    """Legacy envelope only — existing clients ignore portfolio_studio."""
    return {k: snap[k] for k in LEGACY_SNAPSHOT_KEYS}


def iter_unbound_live(ps: dict):
    """Every unbound live slot: (path, value). Numbers must be None, not 0."""
    if not isinstance(ps, dict):
        raise AssertionError("portfolio_studio is not an object")
    yield "current_stage.kind", (ps.get("current_stage") or {}).get("kind")
    yield "current_stage.id", (ps.get("current_stage") or {}).get("id")
    yield "current_stage.n", (ps.get("current_stage") or {}).get("n")
    yield "motif_running.kind", (ps.get("motif_running") or {}).get("kind")
    yield "motif_running.value", (ps.get("motif_running") or {}).get("value")
    yield "spend.kind", (ps.get("spend") or {}).get("kind")
    yield "spend.usd", (ps.get("spend") or {}).get("usd")
    yield "spend.tokens", (ps.get("spend") or {}).get("tokens")
    yield "occupancy.kind", (ps.get("occupancy") or {}).get("kind")
    yield "occupancy.n", (ps.get("occupancy") or {}).get("n")
    last = (ps.get("transitions") or {}).get("last") or {}
    yield "transitions.last.kind", last.get("kind")
    yield "transitions.last.id", last.get("id")
    yield "transitions.last.at", last.get("at")
    yield "transitions.last.from_kind", last.get("from_kind")
    yield "transitions.last.to_kind", last.get("to_kind")
    nxt = (ps.get("transitions") or {}).get("next_live") or {}
    yield "transitions.next_live.kind", nxt.get("kind")
    yield "transitions.next_live.id", nxt.get("id")
    live = ((ps.get("typed_states") or {}).get("live") or {})
    for key in ("current_stage", "motif_running", "last_transition",
                "next_live", "spend", "occupancy_n"):
        yield "typed_states.live.%s" % key, live.get(key)
    for i, row in enumerate(ps.get("stage_projection") or []):
        prefix = "stage_projection[%d]" % i
        yield prefix + ".status", row.get("status")
        yield prefix + ".outcome", row.get("outcome")
        yield prefix + ".current", row.get("current")
        yield prefix + ".elapsed_s", row.get("elapsed_s")
        yield prefix + ".tokens", row.get("tokens")
        yield prefix + ".spend_usd", row.get("spend_usd")


def assert_legacy_compatible(snap: dict) -> bool:
    """Executable response-schema freeze. Raises on legacy drift."""
    if not isinstance(snap, dict):
        raise AssertionError("snapshot is not an object")
    missing = [k for k in LEGACY_SNAPSHOT_KEYS if k not in snap]
    if missing:
        raise AssertionError("legacy keys missing: %s" % (missing,))
    if snap.get("schema") != SCHEMA:
        raise AssertionError("schema drifted: %r" % (snap.get("schema"),))
    if snap.get("does_not_start_motif") is not True:
        raise AssertionError("does_not_start_motif drifted")
    if snap.get("does_not_publish") is not True:
        raise AssertionError("does_not_publish drifted")
    if not isinstance(snap.get("profiles"), list) or not snap["profiles"]:
        raise AssertionError("profiles[] missing")
    ids = [p.get("id") for p in snap["profiles"]]
    for need in ("website", "forge", "crucible", "ups",
                 "diligence", "docket", "differentiator"):
        if need not in ids:
            raise AssertionError("profiles[] lost %s" % need)
    for row in snap["profiles"]:
        lost = [k for k in LEGACY_PROFILE_ROW_KEYS if k not in row]
        if lost:
            raise AssertionError("profiles[] row keys missing: %s" % (lost,))
    stages = snap.get("stages") or []
    if [s.get("n") for s in stages] != list(range(1, 10)):
        raise AssertionError("stages[] is not nine MOTIF steps")
    if [s.get("id") for s in stages] != [s["id"] for s in MOTIF_STAGES]:
        raise AssertionError("stages[] ids drifted")
    for s in stages:
        lost = [k for k in LEGACY_STAGE_KEYS if k not in s]
        if lost:
            raise AssertionError("stages[] keys missing: %s" % (lost,))
    engine = snap.get("engine")
    if not isinstance(engine, dict):
        raise AssertionError("engine missing")
    lost_en = [k for k in LEGACY_ENGINE_KEYS if k not in engine]
    if lost_en:
        raise AssertionError("engine keys missing: %s" % (lost_en,))
    return True


def assert_unbound_unmeasured(ps: dict) -> bool:
    """New live fields emit UNMEASURED / None. Never inferred. Never 0."""
    kind_suffixes = (".kind", ".status", ".outcome")
    for path, val in iter_unbound_live(ps):
        if val == 0:
            raise AssertionError("%s is 0 (UNMEASURED is never 0)" % path)
        if path.startswith("typed_states.live.") or path.endswith(kind_suffixes):
            if val != UNMEASURED:
                raise AssertionError("%s=%r not UNMEASURED" % (path, val))
            continue
        if val is not None:
            raise AssertionError("%s=%r inferred (want None)" % (path, val))
    return True


def assert_portfolio_studio_contract(snap: dict) -> bool:
    """Response + stage-projection + typed-state + transition freeze."""
    assert_legacy_compatible(snap)
    ps = snap.get("portfolio_studio")
    if not isinstance(ps, dict):
        raise AssertionError("portfolio_studio missing")
    if ps.get("schema") != PS_SCHEMA:
        raise AssertionError("portfolio_studio.schema drifted")
    if ps.get("route") != PS_ROUTE:
        raise AssertionError("portfolio_studio.route drifted (no new route)")
    if ps.get("does_not_start_motif") is not True:
        raise AssertionError("portfolio_studio.does_not_start_motif drifted")
    if ps.get("does_not_publish") is not True:
        raise AssertionError("portfolio_studio.does_not_publish drifted")
    proj = ps.get("stage_projection") or []
    if len(proj) != 9:
        raise AssertionError("stage_projection is not nine rows")
    catalog = [{k: s[k] for k in LEGACY_STAGE_KEYS} for s in snap["stages"]]
    proj_cat = [{k: r[k] for k in LEGACY_STAGE_KEYS} for r in proj]
    if catalog != proj_cat:
        raise AssertionError("stage_projection catalog fields drifted from stages[]")
    for row in proj:
        if row.get("note_kind") not in (EMPTY, "OK"):
            raise AssertionError("note_kind must be EMPTY or OK, got %r" % row.get("note_kind"))
        if row.get("note_kind") == EMPTY and row.get("note") != "":
            raise AssertionError("EMPTY note is not explicit empty string")
        if row.get("elapsed_s") == 0 or row.get("tokens") == 0 or row.get("spend_usd") == 0:
            raise AssertionError("UNMEASURED numeric slot is 0")
    vocab = (ps.get("typed_states") or {}).get("vocab") or []
    if list(vocab) != list(TYPED_STATES):
        raise AssertionError("typed_states.vocab drifted")
    trans = (ps.get("transitions") or {}).get("catalog") or []
    if [t.get("id") for t in trans] != ["get_snapshot", "save_engine"]:
        raise AssertionError("transition catalog drifted")
    for t in trans:
        if t.get("starts_motif") is not False or t.get("publishes") is not False:
            raise AssertionError("transition %s starts MOTIF or publishes" % t.get("id"))
    assert_unbound_unmeasured(ps)
    return True


def snapshot(paths, *, profile: str = "", rec=None) -> dict:
    pid = str(profile or "").strip().lower() or DEFAULT_PROFILE
    row = _profile(pid)
    engine = rec if rec is not None else load_engine(paths, row["id"])
    out = {
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
        "note": (
            "Per-profile MOTIF skins. Website GC IMPLEMENT dest is staged / "
            "sandbox / publish / Gitur. SAVE does not start MOTIF and does "
            "not publish."
        ),
    }
    out["portfolio_studio"] = portfolio_studio_fold(engine)
    return out


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
    check("Portfolio Studio contract on GET NO_SOURCE (legacy + UNMEASURED live)",
          lambda: assert_portfolio_studio_contract(snap)
          and snap["portfolio_studio"]["typed_states"]["engine"] == "NO_SOURCE"
          and snap["portfolio_studio"]["typed_states"]["define"] == EMPTY
          and "portfolio_studio" not in legacy_view(snap))
    check("SAVE is not a MOTIF transition; unbound live stays UNMEASURED",
          lambda: assert_portfolio_studio_contract(saved)
          and saved["portfolio_studio"]["typed_states"]["define"] == "OK"
          and saved["portfolio_studio"]["typed_states"]["engine"] == "OK"
          and saved["portfolio_studio"]["current_stage"]["id"] is None
          and saved["portfolio_studio"]["current_stage"]["kind"] == UNMEASURED
          and saved["does_not_start_motif"] is True)
    check("stage_projection notes: empty=EMPTY, written=OK, never inferred current",
          lambda: (
              next(r for r in saved["portfolio_studio"]["stage_projection"]
                   if r["id"] == "improve")["note_kind"] == "OK"
              and next(r for r in saved["portfolio_studio"]["stage_projection"]
                       if r["id"] == "define")["note_kind"] == EMPTY
              and all(r["current"] is None
                      for r in saved["portfolio_studio"]["stage_projection"])
          ))
    check("unbound live fields never emit 0",
          lambda: all(v != 0 for _p, v in iter_unbound_live(
              saved["portfolio_studio"])))

    failed = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (Website GC MOTIF skins; no auto-MOTIF)"
          % ("PASS" if not failed else "FAIL", len(results)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(_selftest())
