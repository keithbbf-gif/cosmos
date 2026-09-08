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
    {"id": "forge", "label": "Forge", "kind": "coding",
     "dest": FORGE_DEST, "status": "cooking",
     "note": "CCr + N adversarial coders. IMPLEMENT writes code via Gitur or local."},
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


def default_engine(profile_id: str = DEFAULT_PROFILE) -> dict:
    row = _profile(profile_id)
    notes = {s["id"]: "" for s in MOTIF_STAGES}
    return {
        "schema": SCHEMA,
        "profile": row["id"],
        "label": row["label"],
        "define": {"text": "", "saved_at": None},
        "stages": notes,
        "dest": default_dest(row),
        "saved_at": None,
        "kind": "NO_SOURCE",
        "note": (
            "MOTIF engine skin for this profile. SAVE does not start MOTIF. "
            "IMPLEMENT dest is profile-specific. Publish is Keith's click."
        ),
    }


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
        "dest": cur["dest"],
        "saved_at": cur["saved_at"],
        "note": cur["note"],
    }
    engine_path(paths, row["id"]).write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out["kind"] = "OK"
    return snapshot(paths, profile=row["id"], rec=out)


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

    failed = [(l, e) for l, ok, e in results if not ok]
    for label, ok, err in results:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (Website GC MOTIF skins; no auto-MOTIF)"
          % ("PASS" if not failed else "FAIL", len(results)))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(_selftest())
