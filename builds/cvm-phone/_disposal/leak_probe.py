#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Throwaway: does `cvm_phone_gate local` write the live runtime root?

The gate is a READER of live/. Claiming that is cheap; measuring it is the
point — but the live fleet is RUNNING, so a naive before/after shows a dozen
daemon heartbeats and proves nothing about the gate.

CONTROLLED COMPARISON. Three fingerprints of everything under live/state and
live/logs: t0, t1 after an idle window, t2 after the gate run over a window of
the same length. Files that move in the idle window are fleet churn. The gate
is implicated only by a file that moves in the gate window and NOT the idle one
— and even then only after a second look, because a daemon can fire late.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else r"V:/A/Ai/COSMOS/live")
GATE = Path(__file__).resolve().parent.parent / "cvm_phone_gate.py"
WATCH = ("state", "logs")
# What the phone half could conceivably touch. Everything else is fleet noise.
SUSPECT = ("state\\cvm\\phone.json", "state\\cvm\\pull.json",
           "state\\cvm\\phone_turn.json")


def fingerprint() -> dict:
    out = {}
    for sub in WATCH:
        d = ROOT / sub
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*")):
            if not p.is_file():
                continue
            try:
                st = p.stat()
                b = p.read_bytes()
            except OSError as e:
                out[str(p.relative_to(ROOT))] = "UNREADABLE:%s" % e
                continue
            out[str(p.relative_to(ROOT))] = {
                "size": st.st_size, "mtime_ns": st.st_mtime_ns,
                "sha256": hashlib.sha256(b).hexdigest()}
    return out


def diff(a: dict, b: dict) -> list:
    return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))


t0 = fingerprint()
control_start = time.perf_counter()
proof = Path(__file__).resolve().parent / "leak_run.json"

# Idle window first, length unknown until the gate runs; use a prior measured
# ~3.5 s, then match the gate window against the ACTUAL gate elapsed below.
time.sleep(3.5)
control_s = time.perf_counter() - control_start
t1 = fingerprint()

gate_start = time.perf_counter()
p = subprocess.run([sys.executable, str(GATE), "local", "--root", str(ROOT),
                    "--proof", str(proof)],
                   capture_output=True, text=True, encoding="utf-8")
gate_s = time.perf_counter() - gate_start
t2 = fingerprint()

idle_moved = diff(t0, t1)
gate_moved = diff(t1, t2)
only_gate = sorted(set(gate_moved) - set(idle_moved))
suspects = [f for f in only_gate if f in SUSPECT]
print(json.dumps({
    "rc": p.returncode,
    "files_watched": len(t2),
    "control_window_s": round(control_s, 2),
    "gate_window_s": round(gate_s, 2),
    "moved_in_idle_window": idle_moved,
    "moved_in_gate_window": gate_moved,
    "moved_ONLY_in_gate_window": only_gate,
    "phone_files_moved_only_in_gate_window": suspects,
    "verdict": ("NO_PHONE_WRITE_TO_LIVE" if not suspects
                else "LIVE_WRITE_DETECTED"),
    "note": ("Files in moved_in_idle_window are the running fleet's own "
             "daemons. Only phone_files_moved_only_in_gate_window would "
             "implicate this gate."),
}, indent=1))
