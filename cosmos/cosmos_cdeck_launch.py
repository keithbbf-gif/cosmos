#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Launch native cDeck.exe as a DT process window (not a browser).

Keith 2026-09-04: the desktop app is cdeck.exe. Browser /cdeck/ is
mobile/remote. os.startfile goes through Explorer so the window lands on
the interactive desktop — a child of this agent session does not.

    py -3.14 cosmos\\cosmos.py deck
"""
from __future__ import annotations

import os
from pathlib import Path

EXE_REL = Path("builds") / "cdeck" / "src-tauri" / "target" / "release" / "cdeck.exe"


def repo_tree() -> Path:
    return Path(__file__).resolve().parent.parent


def cdeck_exe() -> Path:
    return repo_tree() / EXE_REL


def launch_cdeck() -> dict:
    exe = cdeck_exe()
    rec = {
        "ok": False,
        "exe": str(exe),
        "exists": exe.is_file(),
        "bytes": exe.stat().st_size if exe.is_file() else 0,
        "method": None,
    }
    if not exe.is_file():
        rec["error"] = "EXE_MISSING"
        return rec
    try:
        os.startfile(str(exe))  # type: ignore[attr-defined]
        rec["ok"] = True
        rec["method"] = "os.startfile"
    except AttributeError:
        rec["error"] = "NO_STARTFILE"
    except OSError as e:
        rec["error"] = f"{type(e).__name__}: {e}"
    return rec
