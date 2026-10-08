#!/usr/bin/env python3
"""HOLD / UNMEASURED families. n is JSON null, never 0. Store must be passed."""
from __future__ import annotations

from pathlib import Path

from refusals import SessionToolsRefusal


def _scan(family: str, store: Path) -> dict:
    if store is None:
        raise SessionToolsRefusal("GUESSED_ROOT", family)
    return {
        "family": family,
        "status": "UNMEASURED",
        "path": str(store),
        "n": None,
        "n_legal": 0,
        "bytes": None,
        "source_sha": None,
        "sample_ids": [],
        "note": "adapter not opened this slice — n is null not 0",
    }


def _load(family: str, store: Path, rec_id: str):
    raise SessionToolsRefusal("UNMEASURED", f"{family}:{rec_id}")


def _mod(family: str):
    class _M:
        pass
    m = _M()
    m.FAMILY = family
    m.scan = lambda store, _f=family: _scan(_f, store)
    m.load = lambda store, rec_id, _f=family: _load(_f, store, rec_id)
    return m


claude_desktop = _mod("claude_desktop")
cursor = _mod("cursor")
codex = _mod("codex")
gemini = _mod("gemini")
sgh_voice = _mod("sgh_voice")
