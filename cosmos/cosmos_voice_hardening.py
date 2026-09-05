#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cosmos_voice_hardening - voice constants + read-only BootUP helpers.

PHASE 4, docs/CORE_RESTRUCTURE.md. `cosmos_service.py` was 1,581 lines. This
module is ONE cut along a seam the file already named for itself:

    # ---------------- voice hardening constants (2026-08-25) ----------------

Everything between that banner and `class ServiceError` (the bind/token
refusals, not voice) is here, byte-for-byte in behaviour. POST /api/v1/voice
still lives on the service: control -> dedupe -> spend -> telemetry ->
bootup short-circuit. The handler only *calls* these helpers.

Why this seam and not another. The block has no Kernel / ledger / HTTP
coupling — string work plus one read of the stream handoff. It does not
touch make_handler, bearer auth, the static/cDeck shell, or CVM
projection. The other named leftover (`cosmos_codex_rail.py`) has no
existing `# seam` banner, so it is not this cut.

The move is ADDITIVE. `cosmos_service` re-exports every name below, so
make_handler and tests keep:

    from cosmos_service import (
        DEDUPE_WINDOW_S, STREAM_ROOTS, _bootup_summary,
    )

Does not modify kernel / ledger / sched. BU_MD_PATH and STREAM_ROOTS are
the incumbent module attributes (a test can repoint them); this cut does
not invent a resolver and does not rewrite the literals.
"""
from __future__ import annotations

# ---------------- voice hardening constants (2026-08-25) ----------------
DEDUPE_WINDOW_S = 15.0    # identical (client_id, utterance) inside this = drop

# BOOTUP (read-only): the stream handoff lives in BU.MD; a stream scopes the
# orchestrator's file roots. Module attributes on purpose - a test (or a
# future resolver) can repoint them without editing the handler.
BU_MD_PATH = r"V:\Ai\BU.MD"
STREAM_ROOTS = {
    "legal":    [r"V:\Ai\Legal"],
    "plumbing": [r"V:\A\Ai\COSMOS", r"V:\Ai\ROLD"],
    "physics":  [r"V:\Research4"],
    "chapter":  [r"V:\Research4"],
}
_BOOTUP_REPLY_CAP = 1500  # chars of BU.MD quoted back in a bootup reply
_SPOKEN_CAP = 320         # TTS trim, cosmos_voice's figure


def _flat_trim(text: str, cap: int = _SPOKEN_CAP) -> str:
    """cosmos_voice._spoken's rule: whitespace-collapsed, cut at a word
    boundary with an audible ellipsis - never mid-word."""
    flat = " ".join(str(text).split())
    if len(flat) <= cap:
        return flat
    cut = flat[:cap]
    if " " in cut:
        cut = cut[:cut.rfind(" ")]
    return cut + " ..."


def _stream_section(raw: str, stream: str) -> str:
    """The stream's slice of the handoff: the first heading line naming the
    stream through to the next heading; else the first plain line naming it
    plus a short window; else the head of the file with an honest note.
    Read-only string work - nothing here touches disk."""
    lines = raw.splitlines()
    if stream:
        s = stream.lower()
        start = next((i for i, ln in enumerate(lines)
                      if ln.lstrip().startswith("#") and s in ln.lower()), None)
        if start is not None:
            out = [lines[start]]
            for ln in lines[start + 1:]:
                if ln.lstrip().startswith("#"):
                    break
                out.append(ln)
            return "\n".join(out).strip()[:_BOOTUP_REPLY_CAP]
        start = next((i for i, ln in enumerate(lines) if s in ln.lower()), None)
        if start is not None:
            return "\n".join(lines[start:start + 20]).strip()[:_BOOTUP_REPLY_CAP]
        return (f"(no section for stream {stream!r} in the handoff - "
                f"head follows)\n" + raw[:_BOOTUP_REPLY_CAP])
    return raw[:_BOOTUP_REPLY_CAP]


def _bootup_summary(stream: str, session_id=None, bu_path=None) -> dict:
    """READ-ONLY BootUP for the voice seam: read the handoff (BU.MD), slice
    the stream's section, name the stream's file roots. Nothing is written,
    nothing is executed, nothing is spent - this is a spoken summary, not the
    ROLD checklist."""
    path = bu_path or BU_MD_PATH
    stream = (stream or "").strip().lower()
    base = {"ok": False, "session_id": session_id, "kind": "bootup",
            "reply": "", "spoken": "", "needs_confirm": False,
            "confirm_id": None, "action": "bootup", "sources": [],
            "refused": False, "stream": stream or None,
            "roots": list(STREAM_ROOTS.get(stream, []))}
    from pathlib import Path as _P
    try:
        raw = _P(path).read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        base.update(refused=True,
                    reply=f"[BU_MD_UNREADABLE] handoff not readable at "
                          f"{path}: {type(e).__name__}: {e}",
                    spoken="Boot up failed: the handoff file is not "
                           "readable here.")
        base["error"] = "BU_MD_UNREADABLE"
        return base
    section = _stream_section(raw, stream)
    base.update(ok=True, reply=section, sources=[f"file:{path}"])
    prefix = (f"Boot up for the {stream} stream. " if stream else "Boot up. ")
    base["spoken"] = prefix + _flat_trim(section)
    return base
