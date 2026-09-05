#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_pause - one PAUSE.flag reader (HOLD vs resume_gate).

HOLD never self-clears. resume_gate unlinks at auto_resume_at (WD2/Pulse).
Fail-closed: unrecognised mode is HOLD. No OA, no dispatch, no schtasks.

    from cosmos_pause import classify_pause, read_pause_flag, maybe_auto_resume
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from cosmos_paths import CosmosPaths

PAUSE_NAME = "PAUSE.flag"
SCHEMA = "cosmos-pause/1"


def pause_path(paths: CosmosPaths) -> Path:
    return paths.role("state", "control", PAUSE_NAME)


def read_pause_flag(paths: CosmosPaths) -> dict | None:
    """Presence of live/state/control/PAUSE.flag is the whole signal."""
    p = pause_path(paths)
    if not p.exists() or not p.is_file():
        return None
    rec: dict = {"path": str(p), "state": "PAUSED"}
    try:
        raw = p.read_text(encoding="utf-8").strip()
    except OSError as e:
        rec["read_error"] = str(e)
        return rec
    if raw.startswith("{"):
        try:
            obj = json.loads(raw)
        except ValueError:
            obj = None
        if isinstance(obj, dict):
            rec.update(obj)
            rec.setdefault("state", "PAUSED")
            rec["path"] = str(p)
            return rec
    rec["reason"] = raw[:240] or "(empty flag file)"
    return rec


def classify_pause(flag: dict | None) -> dict:
    """HOLD is sacred. Unrecognised mode is HOLD. GATE is WD2/Pulse-owned."""
    if flag is None:
        return {"class": "RUNNING", "why": "no PAUSE.flag"}
    if str(flag.get("state", "PAUSED")).upper() == "RUNNING":
        return {"class": "RUNNING", "why": "flag present but state=RUNNING"}
    mode = str(flag.get("mode") or "").strip().lower()
    if mode == "resume_gate":
        return {"class": "GATE", "why": "resume_gate already armed; clock owns it"}
    if mode != "hold":
        return {"class": "HOLD",
                "why": f"unrecognised mode={mode!r} - fail-closed to HOLD"}
    set_by = str(flag.get("set_by") or "").strip().lower()
    reason = str(flag.get("reason") or "").lower()
    if set_by in ("cow", "cosmos", "tidyup") and "tidyup" in reason:
        return {"class": "ARM",
                "why": "TidyUP handoff hold (set_by=%s) - P3 arming case" % set_by}
    return {"class": "HOLD",
            "why": "operator hold (set_by=%s) - never rewritten" % (set_by or "?")}


def is_paused(flag: dict | None) -> bool:
    """True iff retask must drop no NEW agents. HOLD/GATE/ARM all pause retask."""
    cls = classify_pause(flag).get("class")
    return cls in ("HOLD", "GATE", "ARM")


def maybe_auto_resume(paths: CosmosPaths, flag: dict | None) -> dict:
    """Unlink resume_gate at auto_resume_at. HOLD never. Fail toward staying paused."""
    out = {"cleared": False, "why": "not a resume_gate"}
    if flag is None:
        out["why"] = "no flag"
        return out
    classified = classify_pause(flag)
    if classified.get("class") != "GATE":
        out["why"] = classified.get("why") or "not GATE"
        out["class"] = classified.get("class")
        return out
    ara = flag.get("auto_resume_at")
    if not ara:
        out["why"] = "resume_gate missing auto_resume_at — staying PAUSED"
        return out
    try:
        due = datetime.fromisoformat(str(ara).replace("Z", "+00:00"))
    except ValueError:
        out["why"] = "unparseable auto_resume_at=%r — staying PAUSED" % (ara,)
        return out
    if due.tzinfo is None:
        due = due.astimezone()
    if datetime.now().astimezone() < due:
        out["why"] = "auto_resume_at not reached"
        return out
    p = pause_path(paths)
    try:
        p.unlink()
    except FileNotFoundError:
        pass
    except OSError as e:
        out["why"] = "could not remove PAUSE.flag: %r" % (e,)
        return out
    out["cleared"] = True
    out["why"] = "AUTO-RESUME resume_gate auto_resume_at=%s" % (ara,)
    return out
