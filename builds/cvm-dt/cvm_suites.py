#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run every cvm-dt suite in a fresh interpreter and record what it emitted.

Each suite is its own process (they mutate module-level voice state and
sys.modules), so a shared interpreter would let one suite's fake `vosk`
decide another suite's verdict. rc is recorded but is NOT the verdict — the
per-suite PASS/FAIL line counts read off stdout are, and a suite that prints
neither is reported as `NO_SIGNAL` rather than counted as green.

    py -3.14 builds\\cvm-dt\\cvm_suites.py            # -> SUITES.json

Writes `SUITES.json` beside this file. No Core, no network, no credential.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
_LINE = re.compile(r"^(PASS|FAIL)\b", re.M)


def suites() -> list[Path]:
    return sorted(p for p in HERE.glob("test_*.py") if p.is_file())


def run_one(path: Path, timeout_s: float = 600.0) -> dict:
    t0 = time.perf_counter()
    try:
        cp = subprocess.run([sys.executable, str(path)], capture_output=True,
                            text=True, timeout=timeout_s, cwd=str(HERE))
        rc, out, err = cp.returncode, cp.stdout, cp.stderr
    except subprocess.TimeoutExpired:
        return {"suite": path.name, "verdict": "TIMEOUT", "rc": None,
                "ms": round((time.perf_counter() - t0) * 1000.0, 1)}
    hits = _LINE.findall(out)
    npass, nfail = hits.count("PASS"), hits.count("FAIL")
    if not hits:
        verdict = "NO_SIGNAL"
    elif nfail == 0 and rc == 0:
        verdict = "PASS"
    else:
        verdict = "FAIL"
    rec = {"suite": path.name, "verdict": verdict, "rc": rc,
           "passed": npass, "failed": nfail,
           "ms": round((time.perf_counter() - t0) * 1000.0, 1)}
    if verdict != "PASS":
        rec["failing"] = [ln for ln in out.splitlines()
                          if ln.startswith("FAIL")][:8]
        tail = (err or out).strip().splitlines()[-6:]
        rec["tail"] = tail
    return rec


def main() -> int:
    recs = [run_one(p) for p in suites()]
    tot_p = sum(int(r.get("passed") or 0) for r in recs)
    tot_f = sum(int(r.get("failed") or 0) for r in recs)
    ok = all(r["verdict"] == "PASS" for r in recs)
    out = {
        "ok": ok, "wire": "cvm-dt-suites/1",
        "ran_at_epoch": time.time(),
        "python": sys.version.split()[0], "executable": sys.executable,
        "suites": len(recs), "checks_passed": tot_p, "checks_failed": tot_f,
        "results": recs,
        "note": ("rc is recorded, not trusted. A suite printing no PASS/FAIL "
                 "line is NO_SIGNAL, never green."),
    }
    p = HERE / "SUITES.json"
    p.write_text(json.dumps(out, indent=1), encoding="utf-8")
    out["proof_path"] = str(p)
    print(json.dumps(out, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
