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
import re
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

# Portfolio Studio — seven canonical occupancy products (docs/PROFILES.md).
PORTFOLIO_SCHEMA = "cosmos-portfolio-studio/1"
PORTFOLIO_PRODUCT_IDS = tuple(p["id"] for p in PROFILES)
# Tracker slug hints; absent slug → tracker evidence stays NO_SOURCE for that product.
PRODUCT_TRACKER_SLUG = {
    "website": "cdeck",
}
SLUG_TO_PRODUCT = {v: k for k, v in PRODUCT_TRACKER_SLUG.items()}
_MOTIF_TOKEN_RE = re.compile(r"motif_([a-z0-9]+)_s(\d+)", re.I)
_STAGE_NINE_RE = re.compile(
    r"(?:\bstage[_\s-]?|motif[_\s-]?|s)(\d{1,2})\b", re.I)

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


def _stage_nine_meta(n: int | None) -> dict:
    if n is None or n < 1 or n > 9:
        return {"n": None, "id": None, "name": None}
    row = MOTIF_STAGES[n - 1]
    return {"n": row["n"], "id": row["id"], "name": row["name"]}


def _evidence_shell(source: str, *, kind: str = "NO_SOURCE",
                    seq: int | None = None, t: float | None = None,
                    stage_n: int | None = None,
                    detail: str | None = None) -> dict:
    return {
        "source": source,
        "kind": kind,
        "ledger_seq": seq,
        "ledger_t": t,
        "stage_n": stage_n,
        "detail": None if not detail else str(detail)[:240],
    }


def _fold_text_hits(text: str, product_id: str) -> bool:
    folded = re.sub(r"[^a-z0-9]+", "", str(text or "").lower())
    pid = re.sub(r"[^a-z0-9]+", "", product_id.lower())
    if not pid or pid not in folded:
        return False
    if product_id == "ups" and "upsjudge" in folded.replace("ups", "", 1):
        return True
    return pid in folded


def _tracker_evidence(paths, repo, product_id: str) -> dict:
    slug = PRODUCT_TRACKER_SLUG.get(product_id)
    if not slug:
        return _evidence_shell("tracker", kind="NO_SOURCE",
                             detail="no tracker slug for this product")
    dest = paths.state("motif_tracker.json")
    if not dest.is_file():
        return _evidence_shell("tracker", kind="NO_SOURCE",
                             detail="motif_tracker.json absent")
    try:
        body = json.loads(dest.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return _evidence_shell("tracker", kind="BROKE", detail=str(e)[:160])
    rows = body.get("rows") if isinstance(body, dict) else None
    if not isinstance(rows, list):
        return _evidence_shell("tracker", kind="BROKE", detail="rows missing")
    row = next((r for r in rows if isinstance(r, dict) and r.get("slug") == slug), None)
    if not row:
        return _evidence_shell("tracker", kind="NO_SOURCE",
                             detail=f"slug {slug!r} not in projection")
    cur = row.get("current_stage")
    try:
        n = int(cur) if cur is not None else None
    except (TypeError, ValueError):
        n = None
    if n is None or n < 1:
        return _evidence_shell(
            "tracker", kind="UNMEASURED",
            t=float(body.get("generated_epoch") or 0) or None,
            detail="current_stage not an integer",
        )
    meta = _stage_nine_meta(min(n, 9))
    gen = body.get("generated_epoch")
    return _evidence_shell(
        "tracker", kind="MEASURED",
        t=float(gen) if gen is not None else None,
        stage_n=meta["n"],
        detail="tracker current_stage=%s id=%s" % (meta["n"], meta["id"]),
    )


def _ledger_evidence(ledger, product_id: str) -> dict:
    if ledger is None:
        return _evidence_shell("ledger", kind="NO_SOURCE", detail="ledger not composed")
    best = None
    try:
        recs = list(ledger.verify())
    except Exception as e:  # noqa: BLE001
        return _evidence_shell("ledger", kind="BROKE", detail=str(e)[:160])
    for rec in recs:
        payload = rec.get("payload") if isinstance(rec, dict) else None
        if not isinstance(payload, dict):
            payload = {}
        blob = json.dumps(payload, sort_keys=True, default=str)
        prof = str(payload.get("profile") or payload.get("product") or "").strip().lower()
        attributed = prof == product_id or _fold_text_hits(blob, product_id)
        if not attributed:
            continue
        stage_n = payload.get("stage_n") or payload.get("motif_stage")
        stage_id = str(payload.get("stage") or payload.get("stage_id") or "").strip().lower()
        if stage_id in STAGE_IDS:
            stage_n = MOTIF_STAGES[[s["id"] for s in MOTIF_STAGES].index(stage_id)]["n"]
        if stage_n is None:
            m = _MOTIF_TOKEN_RE.search(blob)
            if m and SLUG_TO_PRODUCT.get(m.group(1).lower()) == product_id:
                stage_n = int(m.group(2))
            else:
                m2 = _STAGE_NINE_RE.search(blob)
                if m2:
                    stage_n = int(m2.group(1))
        try:
            stage_n = int(stage_n) if stage_n is not None else None
        except (TypeError, ValueError):
            stage_n = None
        if stage_n is None or stage_n < 1 or stage_n > 9:
            kind = "UNATTRIBUTED" if prof != product_id else "UNMEASURED"
            cand = {
                "kind": kind,
                "seq": rec.get("seq"),
                "t": rec.get("t"),
                "event": rec.get("event"),
                "stage_n": None,
            }
        else:
            cand = {
                "kind": "MEASURED",
                "seq": rec.get("seq"),
                "t": rec.get("t"),
                "event": rec.get("event"),
                "stage_n": stage_n,
            }
        if best is None or int(cand.get("seq") or 0) >= int(best.get("seq") or 0):
            best = cand
    if not best:
        return _evidence_shell("ledger", kind="NO_SOURCE",
                             detail="no ledger row names this product")
    meta = _stage_nine_meta(best.get("stage_n"))
    return _evidence_shell(
        "ledger", kind=best["kind"],
        seq=int(best["seq"]) if best.get("seq") is not None else None,
        t=float(best["t"]) if best.get("t") is not None else None,
        stage_n=meta["n"] if best["kind"] == "MEASURED" else None,
        detail=(
            None if best["kind"] != "MEASURED"
            else "event=%s stage n=%s id=%s" % (
                best.get("event"), meta["n"], meta["id"])
        ),
    )


def _work_order_evidence(paths, product_id: str) -> dict:
    try:
        from cosmos_work_order import fold_work_orders
        rec = fold_work_orders(paths, limit=64)
    except Exception as e:  # noqa: BLE001
        return _evidence_shell("work_order", kind="BROKE", detail=str(e)[:160])
    tagged = []
    untagged = 0
    for row in rec.get("rows") or []:
        if not isinstance(row, dict):
            continue
        blob = " ".join(str(row.get(k) or "") for k in (
            "order_id", "task", "agent", "product", "output_head"))
        if _fold_text_hits(blob, product_id):
            tagged.append(row)
        elif blob.strip():
            untagged += 1
    if not tagged:
        kind = "UNATTRIBUTED" if untagged else "NO_SOURCE"
        return _evidence_shell(
            "work_order", kind=kind,
            detail=(
                "no work order tags this product"
                if kind == "NO_SOURCE"
                else "work orders present but none tag this product"
            ),
        )
    last = sorted(tagged, key=lambda r: str(r.get("sort") or ""))[-1]
    blob = json.dumps(last, sort_keys=True, default=str)
    stage_n = None
    m = _MOTIF_TOKEN_RE.search(blob)
    if m and SLUG_TO_PRODUCT.get(m.group(1).lower()) == product_id:
        stage_n = int(m.group(2))
    else:
        m2 = _STAGE_NINE_RE.search(blob)
        if m2:
            stage_n = int(m2.group(1))
    if stage_n is None or stage_n < 1 or stage_n > 9:
        return _evidence_shell(
            "work_order", kind="UNATTRIBUTED",
            detail="order %s tags product but not stage"
            % (last.get("order_id") or last.get("id")),
        )
    meta = _stage_nine_meta(stage_n)
    ts = last.get("mtime") or last.get("timestamp")
    return _evidence_shell(
        "work_order", kind="MEASURED",
        stage_n=meta["n"],
        detail="order=%s stage n=%s id=%s at %s" % (
            last.get("order_id"), meta["n"], meta["id"], ts),
    )


def _lease_evidence(paths, product_id: str) -> dict:
    try:
        from cosmos_ccr import read_lease
        lease = read_lease(paths)
    except Exception as e:  # noqa: BLE001
        return _evidence_shell("lease", kind="BROKE", detail=str(e)[:160])
    if not lease:
        return _evidence_shell("lease", kind="NO_SOURCE", detail="CCR.lease absent")
    stream = str(lease.get("stream") or "").strip()
    if product_id == "forge":
        return _evidence_shell(
            "lease", kind="MEASURED",
            t=float(lease.get("taken_at") or 0) or None,
            detail="CCR held stream=%s sid=%s" % (stream, lease.get("sid")),
        )
    return _evidence_shell(
        "lease", kind="UNATTRIBUTED",
        t=float(lease.get("taken_at") or 0) or None,
        detail="lease names forge/CCr not %s" % product_id,
    )


def _scheduler_evidence(paths, product_id: str) -> dict:
    assigned_p = paths.state("watchdog2", "assigned.json")
    inflight_p = paths.state("inflight.jsonl")
    detail_parts = []
    stage_n = None
    source_t = None
    if assigned_p.is_file():
        try:
            assigned = json.loads(assigned_p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            assigned = None
        if isinstance(assigned, dict):
            blob = json.dumps(assigned, sort_keys=True, default=str)
            if _fold_text_hits(blob, product_id):
                detail_parts.append("assigned.json names product")
                m = _STAGE_NINE_RE.search(blob)
                if m:
                    stage_n = int(m.group(1))
            source_t = float(assigned.get("updated_at") or assigned.get("t") or 0) or source_t
    if inflight_p.is_file():
        try:
            from cosmos_inflight import Inflight
            active = Inflight(inflight_p).active()
        except Exception:  # noqa: BLE001
            active = {}
        for token, rec in active.items():
            m = _MOTIF_TOKEN_RE.match(str(token))
            if not m:
                continue
            slug = m.group(1).lower()
            if SLUG_TO_PRODUCT.get(slug) != product_id:
                continue
            stage_n = int(m.group(2))
            source_t = float(rec.get("at") or 0) or source_t
            detail_parts.append("inflight %s" % token)
    if not detail_parts:
        return _evidence_shell("scheduler", kind="NO_SOURCE",
                             detail="assigned/inflight silent for product")
    if stage_n is None or stage_n < 1 or stage_n > 9:
        return _evidence_shell(
            "scheduler", kind="UNATTRIBUTED", t=source_t,
            detail="; ".join(detail_parts),
        )
    meta = _stage_nine_meta(stage_n)
    return _evidence_shell(
        "scheduler", kind="MEASURED", t=source_t,
        stage_n=meta["n"],
        detail="; ".join(detail_parts) + " stage n=%s id=%s" % (meta["n"], meta["id"]),
    )


def _pick_stage_fold(evidence: list[dict]) -> dict:
    """Prefer measured stage evidence; never invent n=0."""
    order = ("ledger", "work_order", "scheduler", "tracker", "lease")
    for src in order:
        ev = next((e for e in evidence if e.get("source") == src), None)
        if not ev or ev.get("kind") != "MEASURED":
            continue
        try:
            n = int(ev.get("stage_n"))
        except (TypeError, ValueError):
            continue
        if n < 1 or n > 9:
            continue
        meta = _stage_nine_meta(n)
        return {
            "kind": "MEASURED",
            "contract": "motif-9",
            "n": meta["n"],
            "id": meta["id"],
            "name": meta["name"],
            "source": src,
            "ledger_seq": ev.get("ledger_seq"),
            "ledger_t": ev.get("ledger_t") or ev.get("t"),
        }
    # typed non-measurement
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
                "ledger_seq": ev.get("ledger_seq"),
                "ledger_t": ev.get("ledger_t") or ev.get("t"),
            }
    return {
        "kind": "UNMEASURED",
        "contract": "motif-9",
        "n": None,
        "id": None,
        "name": None,
        "source": None,
        "ledger_seq": None,
        "ledger_t": None,
    }


def _occupant_fold(paths, product_id: str, *, lease_ev: dict) -> dict:
    if lease_ev.get("source") == "lease" and lease_ev.get("kind") == "MEASURED":
        if product_id == "forge":
            return {
                "kind": "MEASURED",
                "profile": product_id,
                "source": "lease",
                "ledger_seq": lease_ev.get("ledger_seq"),
                "ledger_t": lease_ev.get("ledger_t") or lease_ev.get("t"),
                "detail": lease_ev.get("detail"),
            }
    return {
        "kind": "UNMEASURED",
        "profile": product_id,
        "source": None,
        "ledger_seq": None,
        "ledger_t": None,
        "detail": "one occupant per profile; only CCr lease names forge",
    }


def portfolio_projection(paths, *, ledger=None, repo=None) -> dict:
    """Seven-product live fold. GET never mkdir. No second store."""
    repo_p = repo if repo is not None else Path(__file__).resolve().parent.parent
    products = []
    for pid in PORTFOLIO_PRODUCT_IDS:
        row = next(p for p in PROFILES if p["id"] == pid)
        tracker_ev = _tracker_evidence(paths, repo_p, pid)
        ledger_ev = _ledger_evidence(ledger, pid)
        wo_ev = _work_order_evidence(paths, pid)
        lease_ev = _lease_evidence(paths, pid)
        sched_ev = _scheduler_evidence(paths, pid)
        evidence = [tracker_ev, ledger_ev, sched_ev, lease_ev, wo_ev]
        stage = _pick_stage_fold(evidence)
        occupant = _occupant_fold(paths, pid, lease_ev=lease_ev)
        refuse = {
            "ledger_seq": stage.get("ledger_seq"),
            "ledger_t": stage.get("ledger_t"),
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
        "schema": PORTFOLIO_SCHEMA,
        "stage_contract": "motif-9",
        "n_products": len(products),
        "products": products,
        "note": (
            "Portfolio Studio live projection from tracker, ledger, scheduler, "
            "lease, and work-order evidence only. Untagged orders are "
            "UNATTRIBUTED. Absent fields are UNMEASURED — never 0. Client "
            "must refuse inference past refuse_inference_after."
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
        "portfolio": portfolio,
        "portfolio_product": active,
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
    pf = snap.get("portfolio") or {}
    check("portfolio projection lists seven canonical products UNMEASURED",
          lambda: pf.get("n_products") == 7
          and pf.get("stage_contract") == "motif-9"
          and {p["id"] for p in (pf.get("products") or [])} == set(PORTFOLIO_PRODUCT_IDS)
          and all(p["stage"]["kind"] == "UNMEASURED" and p["stage"]["n"] is None
                  for p in (pf.get("products") or [])))
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
          and forge_row["refuse_inference_after"]["ledger_seq"] is not None
          and forge_row["refuse_inference_after"]["ledger_t"] is not None)

    failed = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (Website GC MOTIF skins; no auto-MOTIF)"
          % ("PASS" if not failed else "FAIL", len(results)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(_selftest())
