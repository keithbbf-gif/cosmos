#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_profiles — occupancy skins + per-profile MOTIF engine.

Each profile owns a MOTIF 9-stage skin. Stage 1 is PROBLEM STATEMENT /
STATED GOAL. Stage 8 is IMPLEMENT (was IMPROVE). Write dest depends on
the running profile. GET never mutates and never mkdir. POST does not
start MOTIF and does not publish.

POST /profiles may also apply an optimistic Keith-approved adjacent
stage transition (action=transition). That path emits ledger evidence
and never starts a job.

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
TRANSITION_SCHEMA = "cosmos-profiles-transition/1"
TRANSITION_EVENT = "PROFILE_STAGE_TRANSITION"
TRANSITION_EVENT_SCHEMA = "cosmos-profile-stage-transition/1"
ENGINE_NAME = "engine.json"
MAX_TEXT = 80_000
MAX_NOTE = 4_000
MAX_PATH = 400
UNMEASURED = "UNMEASURED"

# Ledger event payload contract for PROFILE_STAGE_TRANSITION (append-only).
TRANSITION_EVENT_FIELDS = (
    "schema", "profile", "edge_id", "from_stage", "to_stage", "version",
    "keith_decision", "gates", "starts_motif", "publishes", "job_started",
    "node",
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
STAGE_ORDER = tuple(s["id"] for s in MOTIF_STAGES)

# Gate names required on every legal adjacent transition (fail-closed).
TRANSITION_GATES = ("health", "tree", "spend", "product")

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
    """kind in {BAD_INPUT, REFUSED, BROKE, STALE, SKIPPED, RED, UNMEASURED, UNGATED}."""

    def __init__(self, kind: str, detail: str):
        self.kind = kind
        super().__init__(f"[{kind}] {detail}")


def _iso_now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def motif_transition_edges() -> list[dict]:
    """Frozen MOTIF advance edges. Only these are legal adjacent transitions."""
    edges: list[dict] = []
    for i, fr in enumerate(STAGE_ORDER):
        to = STAGE_ORDER[(i + 1) % len(STAGE_ORDER)]
        edges.append({
            "id": "%s_to_%s" % (fr, to),
            "from_stage": fr,
            "to_stage": to,
            "requires_keith": True,
        })
    edges[-1]["note"] = "ITERATE returns to PROBLEM STATEMENT / STATED GOAL"
    return edges


def _edge_map() -> dict[tuple[str, str], dict]:
    return {(e["from_stage"], e["to_stage"]): e for e in motif_transition_edges()}


def transition_contract() -> dict:
    """Schema freeze for Portfolio Studio stage transitions."""
    return {
        "schema": TRANSITION_SCHEMA,
        "event": TRANSITION_EVENT,
        "event_schema": TRANSITION_EVENT_SCHEMA,
        "event_fields": list(TRANSITION_EVENT_FIELDS),
        "allowed_edges": motif_transition_edges(),
        "gates": list(TRANSITION_GATES),
        "note": (
            "Legal adjacent transitions require an explicit Keith decision and "
            "emit ledger-bound evidence. SAVE does not advance. Transition does "
            "not start MOTIF and does not publish."
        ),
    }


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
        "current_stage": UNMEASURED,
        "version": None,
        "last_transition": None,
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
    cur_stage = rec.get("current_stage")
    if cur_stage in STAGE_IDS:
        current_stage = cur_stage
    elif cur_stage in (None, "", UNMEASURED):
        current_stage = UNMEASURED
    else:
        current_stage = UNMEASURED
    try:
        version = rec.get("version")
        if version is None:
            version = None
        else:
            version = int(version)
    except (TypeError, ValueError):
        version = None
    last = rec.get("last_transition")
    if not isinstance(last, dict):
        last = None
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
        "current_stage": current_stage,
        "version": version,
        "last_transition": last,
        "saved_at": rec.get("saved_at"),
        "kind": "OK",
        "note": base["note"],
    }


def save_engine(paths, body: dict, *, kernel=None) -> dict:
    """Persist skin setup. Does not start MOTIF. Does not advance stages.

    When body.action == 'transition' (or a transition object is present),
    delegates to apply_stage_transition instead.
    """
    if not isinstance(body, dict):
        raise ProfileError("BAD_INPUT", "body must be a JSON object")
    action = str(body.get("action") or "").strip().lower()
    tr = body.get("transition")
    if action == "transition" or (
        isinstance(tr, dict)
        and (tr.get("from_stage") is not None or tr.get("to_stage") is not None
             or tr.get("from") is not None or tr.get("to") is not None)
    ):
        return apply_stage_transition(paths, body, kernel=kernel)
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
    # First SAVE lands the occupant at DEFINE without walking a transition.
    if cur.get("current_stage") in (None, UNMEASURED):
        cur["current_stage"] = "define"
    try:
        ver = int(cur["version"]) if cur.get("version") is not None else 0
    except (TypeError, ValueError):
        ver = 0
    cur["version"] = ver + 1
    cur["saved_at"] = _iso_now()
    cur["kind"] = "OK"
    d = dir_for(paths, row["id"])
    d.mkdir(parents=True, exist_ok=True)
    out = _engine_disk_record(cur, row)
    engine_path(paths, row["id"]).write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out["kind"] = "OK"
    return snapshot(paths, profile=row["id"], rec=out)


def _engine_disk_record(cur: dict, row: dict) -> dict:
    return {
        "schema": SCHEMA,
        "profile": row["id"],
        "label": row["label"],
        "define": cur["define"],
        "stages": cur["stages"],
        "step_setup": cur.get("step_setup") or default_step_setup(),
        "dest": cur["dest"],
        "current_stage": cur.get("current_stage") if cur.get("current_stage") in STAGE_IDS
        else UNMEASURED,
        "version": cur.get("version"),
        "last_transition": cur.get("last_transition"),
        "saved_at": cur["saved_at"],
        "note": cur["note"],
    }


def _public_keith_decision(raw) -> dict:
    if not isinstance(raw, dict):
        raise ProfileError(
            "UNGATED",
            "legal adjacent transition requires an explicit Keith decision object",
        )
    approved = raw.get("approved")
    if approved is not True and str(approved).strip().lower() not in ("true", "yes", "1"):
        # Explicit reject or missing approval is ungated / refused — no queue.
        if approved in (False, None, "", 0, "0", "false", "no"):
            raise ProfileError(
                "UNGATED",
                "Keith decision.approved must be true for a legal adjacent transition",
            )
        raise ProfileError("UNGATED", "Keith decision.approved must be true")
    by = str(raw.get("decided_by") or raw.get("by") or "").strip().lower()
    if by not in ("keith", "kb", "owner"):
        raise ProfileError(
            "UNGATED",
            "Keith decision.decided_by must name Keith (got %r)" % (by or ""),
        )
    note = str(raw.get("note") or "")[:MAX_NOTE]
    at = str(raw.get("at") or raw.get("decided_at") or _iso_now())[:80]
    return {
        "approved": True,
        "decided_by": "keith",
        "at": at,
        "note": note,
        "decision_id": str(raw.get("decision_id") or raw.get("id") or "")[:120] or None,
    }


def _require_gates(raw_gates, *, paths, profile_row: dict, kernel=None) -> dict:
    """Fail-closed health/tree/spend/product gates. Never queues work."""
    if not isinstance(raw_gates, dict):
        raise ProfileError(
            "UNGATED",
            "transition requires gates {%s}" % ", ".join(TRANSITION_GATES),
        )
    missing = [g for g in TRANSITION_GATES if g not in raw_gates]
    if missing:
        raise ProfileError("UNGATED", "missing gate(s): %s" % ", ".join(missing))

    health = raw_gates.get("health")
    if not isinstance(health, dict):
        raise ProfileError("UNGATED", "gates.health must be an object")
    verdict = str(health.get("verdict") or "")
    try:
        reds = int(health.get("reds") if health.get("reds") is not None else -1)
    except (TypeError, ValueError):
        reds = -1
    nc = health.get("negative_control_red")
    if nc is not True and str(nc).lower() not in ("true", "1"):
        # Absent / false negative-control means the board is untrustworthy.
        raise ProfileError(
            "RED",
            "health gate refused: negative_control_red is not true (board untrusted)",
        )
    if reds < 0:
        raise ProfileError("UNGATED", "gates.health.reds must be a measured integer")
    if reds > 0 or verdict.upper().startswith("RED") or verdict.upper().startswith("BOARD-BROKEN"):
        raise ProfileError(
            "RED",
            "health gate refused: verdict=%r reds=%s" % (verdict, reds),
        )
    if not verdict:
        raise ProfileError("UNGATED", "gates.health.verdict is empty")

    tree = raw_gates.get("tree")
    if not isinstance(tree, dict):
        raise ProfileError("UNGATED", "gates.tree must be an object")
    want = str(tree.get("tree_id") or "").strip()
    if not want:
        raise ProfileError("UNGATED", "gates.tree.tree_id is required")
    have = paths.sentinel.tree_id
    if want != have:
        raise ProfileError(
            "STALE",
            "tree gate fencing mismatch: request %r != live %r" % (want, have),
        )

    spend = raw_gates.get("spend")
    if not isinstance(spend, dict):
        raise ProfileError("UNGATED", "gates.spend must be an object")
    spend_kind = str(spend.get("kind") or "").strip().upper()
    if not spend_kind:
        raise ProfileError("UNGATED", "gates.spend.kind is required")
    if spend_kind == UNMEASURED:
        raise ProfileError("UNMEASURED", "spend gate is UNMEASURED — refuse, never invent 0")
    if spend_kind in ("DENIED", "REFUSED", "NOT_PERMITTED", "RED"):
        raise ProfileError("REFUSED", "spend gate kind=%s" % spend_kind)

    product = raw_gates.get("product")
    if not isinstance(product, dict):
        raise ProfileError("UNGATED", "gates.product must be an object")
    prod_kind = str(product.get("kind") or "").strip().upper()
    if not prod_kind:
        raise ProfileError("UNGATED", "gates.product.kind is required")
    if prod_kind == UNMEASURED:
        raise ProfileError(
            "UNMEASURED",
            "product gate is UNMEASURED — refuse without queueing work",
        )
    prod_id = str(product.get("id") or product.get("profile") or "").strip().lower()
    if prod_id and prod_id != profile_row["id"]:
        raise ProfileError(
            "REFUSED",
            "product gate id %r does not match profile %r" % (prod_id, profile_row["id"]),
        )

    # Optional kernel cross-check when composed — still no job start.
    if kernel is not None:
        live_tree = getattr(getattr(kernel, "paths", None), "sentinel", None)
        if live_tree is not None and getattr(live_tree, "tree_id", None) not in (None, want):
            if live_tree.tree_id != want:
                raise ProfileError(
                    "STALE",
                    "kernel tree_id %r != gate tree_id %r"
                    % (live_tree.tree_id, want),
                )

    return {
        "health": {
            "verdict": verdict,
            "reds": reds,
            "negative_control_red": True,
        },
        "tree": {"tree_id": want},
        "spend": {"kind": spend_kind, "detail": str(spend.get("detail") or "")[:200]},
        "product": {
            "id": profile_row["id"],
            "kind": prod_kind,
            "detail": str(product.get("detail") or "")[:200],
        },
    }


def apply_stage_transition(paths, body: dict, *, kernel=None) -> dict:
    """Optimistic Keith-approved adjacent stage transition on POST /profiles.

    Emits PROFILE_STAGE_TRANSITION ledger evidence when a kernel ledger is
    present. Never starts a job, never starts MOTIF, never publishes.
    """
    if not isinstance(body, dict):
        raise ProfileError("BAD_INPUT", "body must be a JSON object")
    row = _profile(body.get("profile") or DEFAULT_PROFILE)
    tr = body.get("transition") if isinstance(body.get("transition"), dict) else body
    fr = str(tr.get("from_stage") or tr.get("from") or "").strip().lower()
    to = str(tr.get("to_stage") or tr.get("to") or "").strip().lower()
    if fr not in STAGE_IDS or to not in STAGE_IDS:
        raise ProfileError("BAD_INPUT", "from_stage/to_stage must be MOTIF stage ids")

    edge = _edge_map().get((fr, to))
    if edge is None:
        raise ProfileError(
            "SKIPPED",
            "transition %s -> %s is not a legal adjacent edge (skipped/non-adjacent)"
            % (fr, to),
        )

    # Legal adjacent transitions always require an explicit Keith decision.
    keith = _public_keith_decision(
        body.get("keith_decision") or tr.get("keith_decision") or body.get("decision")
    )
    gates = _require_gates(
        body.get("gates") or tr.get("gates"),
        paths=paths,
        profile_row=row,
        kernel=kernel,
    )

    cur = load_engine(paths, row["id"])
    if cur.get("kind") == "NO_SOURCE":
        raise ProfileError(
            "UNMEASURED",
            "engine is NO_SOURCE / UNMEASURED — SAVE first; refuse without queueing",
        )
    if cur.get("kind") == "BROKE":
        raise ProfileError("BROKE", "engine is BROKE — refuse without queueing")

    have_stage = cur.get("current_stage")
    if have_stage in (None, UNMEASURED):
        raise ProfileError(
            "UNMEASURED",
            "current_stage is UNMEASURED — refuse without inventing a stage",
        )
    if have_stage != fr:
        raise ProfileError(
            "STALE",
            "from_stage %r does not match engine current_stage %r" % (fr, have_stage),
        )

    try:
        expect = tr.get("expect_version", body.get("expect_version"))
        if expect is None:
            raise ProfileError("UNGATED", "expect_version is required (fencing)")
        expect_i = int(expect)
    except ProfileError:
        raise
    except (TypeError, ValueError):
        raise ProfileError("BAD_INPUT", "expect_version must be an integer")
    have_ver = cur.get("version")
    if have_ver is None:
        raise ProfileError(
            "UNMEASURED",
            "engine version is UNMEASURED — refuse fencing without a measured version",
        )
    try:
        have_i = int(have_ver)
    except (TypeError, ValueError):
        raise ProfileError("BROKE", "engine version is unreadable")
    if expect_i != have_i:
        raise ProfileError(
            "STALE",
            "version fencing: expect_version %s != engine version %s"
            % (expect_i, have_i),
        )

    # Website no-publish: transitioning into IMPLEMENT never publishes.
    if to == "improve" and (cur.get("dest") or {}).get("kind") == "publish":
        # Allowed as a stage cursor move; still does not publish.
        pass

    new_ver = have_i + 1
    at = _iso_now()
    last = {
        "schema": TRANSITION_EVENT_SCHEMA,
        "edge_id": edge["id"],
        "from_stage": fr,
        "to_stage": to,
        "at": at,
        "version": new_ver,
        "keith_decision": keith,
        "gates": gates,
        "starts_motif": False,
        "publishes": False,
        "job_started": False,
    }

    ledger_seq = None
    if kernel is not None and getattr(kernel, "ledger", None) is not None:
        payload = {
            "schema": TRANSITION_EVENT_SCHEMA,
            "profile": row["id"],
            "edge_id": edge["id"],
            "from_stage": fr,
            "to_stage": to,
            "version": new_ver,
            "keith_decision": keith,
            "gates": gates,
            "starts_motif": False,
            "publishes": False,
            "job_started": False,
            "node": row["id"],
        }
        try:
            expect_head = body.get("expect_head_seq", tr.get("expect_head_seq"))
            if expect_head is not None:
                rec = kernel.ledger.append(
                    TRANSITION_EVENT, payload, expect_head_seq=int(expect_head))
            else:
                rec = kernel.ledger.append(TRANSITION_EVENT, payload)
            ledger_seq = rec.get("seq")
            last["ledger_seq"] = ledger_seq
            last["ledger_event"] = TRANSITION_EVENT
        except Exception as e:  # noqa: BLE001
            # Ledger refusal must not partially advance the engine.
            kind = getattr(e, "kind", None) or type(e).__name__
            if kind == "STALE_HEAD":
                raise ProfileError("STALE", "ledger head moved: %s" % e) from e
            raise ProfileError("BROKE", "ledger append failed: %s" % e) from e
    else:
        # Core-only writer: without a ledger there is no evidence — refuse.
        raise ProfileError(
            "UNGATED",
            "transition requires Core ledger (kernel) for ledger-bound evidence",
        )

    cur["current_stage"] = to
    cur["version"] = new_ver
    cur["last_transition"] = last
    cur["saved_at"] = at
    cur["kind"] = "OK"
    d = dir_for(paths, row["id"])
    d.mkdir(parents=True, exist_ok=True)
    out = _engine_disk_record(cur, row)
    engine_path(paths, row["id"]).write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out["kind"] = "OK"
    snap = snapshot(paths, profile=row["id"], rec=out)
    snap["transition"] = {
        "ok": True,
        "edge_id": edge["id"],
        "from_stage": fr,
        "to_stage": to,
        "version": new_ver,
        "ledger_seq": ledger_seq,
        "ledger_event": TRANSITION_EVENT,
        "starts_motif": False,
        "publishes": False,
        "job_started": False,
        "keith_decision": keith,
        "gates": gates,
    }
    return snap


def _transition_fold(engine: dict) -> dict:
    """Live transition cursor for GET — UNMEASURED until a ledgered advance."""
    last = engine.get("last_transition") if isinstance(engine.get("last_transition"), dict) else None
    cur_stage = engine.get("current_stage")
    if last and last.get("edge_id") and cur_stage in STAGE_IDS:
        return {
            "schema": TRANSITION_SCHEMA,
            "contract": transition_contract(),
            "current": {
                "kind": "OK",
                "edge_id": last.get("edge_id"),
                "from_stage": last.get("from_stage"),
                "to_stage": last.get("to_stage") or cur_stage,
                "at": last.get("at"),
                "version": engine.get("version"),
                "ledger_seq": last.get("ledger_seq"),
            },
        }
    return {
        "schema": TRANSITION_SCHEMA,
        "contract": transition_contract(),
        "current": {
            "kind": UNMEASURED,
            "edge_id": None,
            "from_stage": None,
            "to_stage": None if cur_stage in (None, UNMEASURED) else cur_stage,
            "at": None,
            "version": engine.get("version"),
            "ledger_seq": None,
        },
    }


def _bg_fold(paths, profile_id: str) -> dict:
    if profile_id != "forge":
        return {"kind": "SKIP"}
    try:
        from cosmos_forge_bg import status
        return status(paths)
    except Exception as e:  # noqa: BLE001
        return {"kind": "BROKE", "detail": f"{type(e).__name__}: {e}"[:200]}


def snapshot(paths, *, profile: str = "", rec=None) -> dict:
    pid = str(profile or "").strip().lower() or DEFAULT_PROFILE
    row = _profile(pid)
    engine = rec if rec is not None else load_engine(paths, row["id"])
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
        "stage_transition": _transition_fold(engine),
        "motif_step_1": "PROBLEM STATEMENT / STATED GOAL",
        "implement_was": "IMPROVE",
        "does_not_start_motif": True,
        "does_not_publish": True,
        "note": (
            "Per-profile MOTIF skins. Website GC IMPLEMENT dest is staged / "
            "sandbox / publish / Gitur. SAVE does not start MOTIF and does "
            "not publish. Legal adjacent transitions require Keith decision "
            "and ledger evidence."
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

    edges = motif_transition_edges()
    check("legal adjacent transition catalog has 9 MOTIF edges",
          lambda: len(edges) == 9
          and edges[0]["from_stage"] == "define"
          and edges[0]["to_stage"] == "research"
          and edges[0]["requires_keith"] is True
          and edges[-1]["from_stage"] == "iterate"
          and edges[-1]["to_stage"] == "define")
    check("SAVE lands current_stage=define with a measured version; no MOTIF start",
          lambda: saved["engine"]["current_stage"] == "define"
          and isinstance(saved["engine"]["version"], int)
          and saved["engine"]["version"] >= 1
          and saved["does_not_start_motif"] is True
          and (saved.get("stage_transition") or {}).get("current", {}).get("kind")
          == UNMEASURED)

    from cosmos_kernel import Kernel

    kroot = install(td / "live-tr", tree_id="spike-profiles-tr")
    kern = Kernel(kroot)
    kpaths = kern.paths
    save_engine(kpaths, {
        "profile": "website",
        "define": {"text": "WHAT: transition pin. WHY: PS-05."},
        "dest": {"kind": "staged"},
    })
    eng = load_engine(kpaths, "website")
    ok_tr = apply_stage_transition(kpaths, {
        "profile": "website",
        "action": "transition",
        "transition": {
            "from_stage": "define",
            "to_stage": "research",
            "expect_version": eng["version"],
        },
        "keith_decision": {"approved": True, "decided_by": "keith",
                           "note": "PS-05 selftest"},
        "gates": {
            "health": {"verdict": "GREEN", "reds": 0,
                       "negative_control_red": True},
            "tree": {"tree_id": kpaths.sentinel.tree_id},
            "spend": {"kind": "OK"},
            "product": {"id": "website", "kind": "OK"},
        },
    }, kernel=kern)
    check("Keith-approved adjacent transition emits ledger evidence; no job start",
          lambda: ok_tr["engine"]["current_stage"] == "research"
          and ok_tr["transition"]["ledger_event"] == TRANSITION_EVENT
          and isinstance(ok_tr["transition"]["ledger_seq"], int)
          and ok_tr["transition"]["job_started"] is False
          and ok_tr["transition"]["starts_motif"] is False
          and ok_tr["does_not_publish"] is True)

    def _refuse(kind, body):
        try:
            apply_stage_transition(kpaths, body, kernel=kern)
            return False
        except ProfileError as e:
            return e.kind == kind

    eng2 = load_engine(kpaths, "website")
    base_gates = {
        "health": {"verdict": "GREEN", "reds": 0, "negative_control_red": True},
        "tree": {"tree_id": kpaths.sentinel.tree_id},
        "spend": {"kind": "OK"},
        "product": {"id": "website", "kind": "OK"},
    }
    check("SKIPPED non-adjacent transition refuses without queueing",
          lambda: _refuse("SKIPPED", {
              "profile": "website",
              "transition": {"from_stage": "define", "to_stage": "build",
                             "expect_version": eng2["version"]},
              "keith_decision": {"approved": True, "decided_by": "keith"},
              "gates": base_gates,
          }))
    check("STALE version fencing refuses without queueing",
          lambda: _refuse("STALE", {
              "profile": "website",
              "transition": {"from_stage": "research", "to_stage": "arch",
                             "expect_version": (eng2["version"] or 0) + 99},
              "keith_decision": {"approved": True, "decided_by": "keith"},
              "gates": base_gates,
          }))
    check("RED health gate refuses without queueing",
          lambda: _refuse("RED", {
              "profile": "website",
              "transition": {"from_stage": "research", "to_stage": "arch",
                             "expect_version": eng2["version"]},
              "keith_decision": {"approved": True, "decided_by": "keith"},
              "gates": {**base_gates, "health": {
                  "verdict": "RED x1", "reds": 1, "negative_control_red": True}},
          }))
    check("UNMEASURED product gate refuses without queueing",
          lambda: _refuse("UNMEASURED", {
              "profile": "website",
              "transition": {"from_stage": "research", "to_stage": "arch",
                             "expect_version": eng2["version"]},
              "keith_decision": {"approved": True, "decided_by": "keith"},
              "gates": {**base_gates, "product": {
                  "id": "website", "kind": UNMEASURED}},
          }))
    check("UNGATED missing Keith decision refuses without queueing",
          lambda: _refuse("UNGATED", {
              "profile": "website",
              "transition": {"from_stage": "research", "to_stage": "arch",
                             "expect_version": eng2["version"]},
              "gates": base_gates,
          }))

    failed = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (Website GC MOTIF skins; no auto-MOTIF)"
          % ("PASS" if not failed else "FAIL", len(results)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(_selftest())
