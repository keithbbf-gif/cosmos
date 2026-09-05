#!/usr/bin/env python3
"""Measure what sys.stdout is under pythonw.exe (GUI subsystem, no console).

Evidence for CLOCK_POSTMORTEM.md: cvm_dt_voice.loop() calls bare print() every
tick with no redirect, unlike cvm_dt_clock.loop() which reassigns sys.stdout to
logs/cvm_dt_clock.out first. If stdout is None under pythonw, a windowless
--loop of the voice worker dies on its first tick.

    pythonw.exe builds/cvm-dt/_disposal/pythonw_stdout_probe.py <out.json>
"""
import json
import pathlib
import sys

rec = {
    "argv0": sys.argv[0],
    "executable": sys.executable,
    "stdout_is_none": sys.stdout is None,
    "stderr_is_none": sys.stderr is None,
}
try:
    print("tick")
    rec["print_ok"] = True
except BaseException as exc:                                      # noqa: BLE001
    rec["print_ok"] = False
    rec["print_exc"] = "%s: %s" % (type(exc).__name__, exc)

pathlib.Path(sys.argv[1]).write_text(json.dumps(rec, indent=1), encoding="utf-8")
