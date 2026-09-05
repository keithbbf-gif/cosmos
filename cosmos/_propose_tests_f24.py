#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_propose_tests_f24 - the two tests/ edits F-24 requires, PROVEN without
touching tests/.

This slice's fence is cosmos/. Wiring four more rails invalidates exactly two
checks under tests/, both of which spell "the four" as a literal. Rather than
write outside the fence, this builds a throwaway tree, applies the proposed
patches there, runs both suites against the REAL cosmos/ modules, and prints
the unified diffs for COW to apply.

    py -3.14 cosmos\\_propose_tests_f24.py            # run the proof
    py -3.14 cosmos\\_propose_tests_f24.py --diff     # print the diffs only
"""
from __future__ import annotations

import argparse
import difflib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# (suite, [(old, new), ...]) - every replacement is asserted to match exactly once.
PATCHES = {
    "tests/test_rails_prober.py": [(
        '''        check("WIRED_NODES is the four named hands, not a static dump",
              lambda: [s["link_id"] for s in WIRED_NODES]
              == ["sgh-api", "gem-api", "oa-api", "claude-cli"])''',
        '''        check("WIRED_NODES is the named hands, not a static dump",
              lambda: [s["link_id"] for s in WIRED_NODES]
              == ["sgh-api", "gem-api", "gw-api", "oa-api", "claude-cli",
                  "cursor-api", "firecrawl-web", "playwright-dom"])''')],
    "tests/test_boot_attach.py": [
        ('''    "claude-cli": _fake("claude-cli", "claude-haiku-4-5"),
}''',
         '''    "claude-cli": _fake("claude-cli", "claude-haiku-4-5"),
    # F-24: the four rails that answered their own probes and were never asked.
    # Each carries the responder its VENDOR emits, not a name invented here.
    "gw-api": _fake("gw-api", "grok-build-0.1"),
    "cursor-api": _fake("cursor-api", "Cursor COSMOS 2"),
    "firecrawl-web": _fake("firecrawl-web", "firecrawl/v2-research-papers"),
    "playwright-dom": _fake("playwright-dom",
                            "Playwright/1.63.0-alpha-2026-08-05"),
}'''),
        ('''        check("projection is non-empty and lists the four wired nodes",
              lambda: d.get("count") == 4''',
         '''        check("projection is non-empty and lists every wired node",
              lambda: d.get("count") == len(WIRED_IDS)'''),
        ('''        check("injected live_calls ran once per wired node (no default rail)",
              lambda: spent["n"] == 4)''',
         '''        check("injected live_calls ran once per wired node (no default rail)",
              lambda: spent["n"] == len(WIRED_IDS))'''),
    ],
}


def _patched(rel: str) -> tuple[str, str]:
    src = (REPO / rel).read_text(encoding="utf-8")
    out = src
    for old, new in PATCHES[rel]:
        if out.count(old) != 1:
            raise SystemExit(
                f"{rel}: anchor matched {out.count(old)} times, expected 1 -- "
                f"the file moved under this proposal; re-derive it")
        out = out.replace(old, new)
    return src, out


def diffs() -> str:
    parts = []
    for rel in PATCHES:
        src, out = _patched(rel)
        parts.append(f"### PROPOSAL: {rel}")
        parts.extend(difflib.unified_diff(
            src.splitlines(), out.splitlines(),
            fromfile=f"a/{rel}", tofile=f"b/{rel}", lineterm=""))
        parts.append("")
    return "\n".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(prog="_propose_tests_f24")
    ap.add_argument("--diff", action="store_true", help="print the diffs only")
    a = ap.parse_args()
    if a.diff:
        print(diffs())
        return 0

    td = Path(tempfile.mkdtemp(prefix="cosmos_propose_tests_"))
    (td / "cosmos").mkdir()
    (td / "tests").mkdir()
    for p in (REPO / "cosmos").iterdir():
        if p.is_file() and p.suffix in (".py", ".toml"):
            shutil.copy2(p, td / "cosmos" / p.name)
    for p in (REPO / "tests").iterdir():
        if p.is_file() and p.suffix == ".py":
            shutil.copy2(p, td / "tests" / p.name)
    for rel in PATCHES:
        (td / rel).write_text(_patched(rel)[1], encoding="utf-8")

    print(f"PATCHED TREE {td}")
    ok = True
    for rel in PATCHES:
        r = subprocess.run([sys.executable, str(td / rel)],
                           capture_output=True, text=True, timeout=900)
        lines = [ln for ln in (r.stdout or "").splitlines() if ln.strip()]
        bad = [ln for ln in lines if ln.strip().startswith("FAIL")]
        print(f"  {'PASS' if r.returncode == 0 else 'FAIL'}  rc={r.returncode}  {rel}")
        print(f"        {lines[-1] if lines else (r.stderr or '')[-300:]}")
        for ln in bad:
            print(f"        {ln}")
        ok = ok and r.returncode == 0
    print(f"PROPOSED PATCHES {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
