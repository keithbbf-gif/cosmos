#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: F-26 NEW-AI scout (open-ended, propose-only).

Isolated from the live COSMOS root. Does not register schtasks. Does not
hit the network (injected catalog). Proves:

  * known HANDS / probe-cmd names are excluded
  * an unknown name is PROPOSE
  * heartbeat + projection are written (unless --dry-run)
  * COMPETENCY.toml is never written
  * --plan-task emits HOURLY schtasks and registers nothing
  * CLOCKS id 23 is this satellite

Does not modify kernel/ledger/sched/service.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "cosmos"))

from cosmos_kernel import install  # noqa: E402
from cosmos_newai_scout import (  # noqa: E402
    CLOCK_ID, HEARTBEAT_NAME, PROJECTION_NAME, SCHEMA, TASK_NAME,
    fold_name, known_folds, parse_catalog, plan_task_argv, poll_once,
    propose,
)
from cosmos_own_clocks import CLOCKS  # noqa: E402

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


CATALOG = """# injected catalog
| # | name | vendor | reach |
|---|------|--------|-------|
| 1 | **Ollama** | Ollama | CLI |
| 2 | **BrandNewAI-XYZ** | Example | CLI |
| 3 | **Pipecat** | Daily | CLI |

name: AlsoFreshWidget
"""


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="cosmos_newai_scout_"))
    root = install(td / "live", tree_id="spike-newai-scout")
    research = REPO / "docs" / "research"
    makers = REPO / "cosmos" / "makers.toml"
    competency = REPO / "docs" / "COMPETENCY.toml"
    known = known_folds(research=research, makers=makers,
                        competency=competency)

    check("CLOCK_ID is 23", lambda: CLOCK_ID == 23)
    check("CLOCKS id 23 is COSMOS NEW-AI Scout",
          lambda: any(c.get("id") == 23 and c.get("task") == TASK_NAME
                      and c.get("script") == "cosmos_newai_scout.py"
                      and c.get("heartbeat") == HEARTBEAT_NAME
                      for c in CLOCKS))
    check("known set includes ollama (HANDS or probe)",
          lambda: "ollama" in known)
    check("fold_name strips junk",
          lambda: fold_name("BrandNewAI-XYZ") == "brandnewaixyz")

    parsed = parse_catalog(CATALOG, "injected")
    names = {r["fold"] for r in parsed}
    check("parser lifts table + name: lines",
          lambda: {"ollama", "brandnewaixyz", "pipecat",
                   "alsofreshwidget"} <= names)

    proposed = propose(parsed, known)
    pfolds = {r["fold"] for r in proposed}
    check("known Ollama is NOT proposed",
          lambda: "ollama" not in pfolds)
    check("unknown BrandNewAI-XYZ IS proposed",
          lambda: "brandnewaixyz" in pfolds)
    check("every proposed row is status=PROPOSE",
          lambda: proposed and all(r.get("status") == "PROPOSE"
                                   for r in proposed))

    before_comp = competency.stat().st_mtime if competency.is_file() else None
    rec = poll_once(str(root), catalog_text=CATALOG)
    hb = root / "logs" / HEARTBEAT_NAME
    proj = root / "state" / "discovery" / PROJECTION_NAME
    body = json.loads(proj.read_text(encoding="utf-8")) if proj.is_file() else {}
    hb_body = json.loads(hb.read_text(encoding="utf-8")) if hb.is_file() else {}
    pfolds_live = {r["fold"] for r in (body.get("proposed") or [])}

    check("poll_once ok state=SCOUTED",
          lambda: rec.get("ok") is True and rec.get("state") == "SCOUTED")
    check("projection schema + clock_id",
          lambda: body.get("schema") == SCHEMA and body.get("clock_id") == 23)
    check("heartbeat clock_id=23 worker=cosmos-newai-scout",
          lambda: hb_body.get("clock_id") == 23
          and hb_body.get("worker") == "cosmos-newai-scout")
    check("live projection excludes ollama",
          lambda: "ollama" not in pfolds_live)
    check("live projection proposes BrandNewAI-XYZ",
          lambda: "brandnewaixyz" in pfolds_live)
    check("COMPETENCY.toml mtime unchanged (never a writer)",
          lambda: competency.is_file()
          and competency.stat().st_mtime == before_comp)

    dry = poll_once(str(root), catalog_text=CATALOG, dry_run=True)
    dry_root = Path(tempfile.mkdtemp(prefix="cosmos_newai_dry_"))
    dry_live = install(dry_root / "live", tree_id="spike-newai-dry")
    dry2 = poll_once(str(dry_live), catalog_text=CATALOG, dry_run=True)
    check("dry_run writes nothing",
          lambda: dry2.get("dry_run") is True
          and not (dry_live / "logs" / HEARTBEAT_NAME).exists()
          and not (dry_live / "state" / "discovery" / PROJECTION_NAME).exists())
    check("dry_run still proposes the unknown name",
          lambda: any(r.get("fold") == "brandnewaixyz"
                      for r in (dry.get("proposed") or [])))

    argv = plan_task_argv(str(root))
    check("plan_task_argv is schtasks /create HOURLY, no /rl",
          lambda: argv[0] == "schtasks" and "/create" in argv
          and TASK_NAME in argv and "HOURLY" in argv and "/rl" not in argv)

    import cosmos_newai_scout as scout
    calls = []
    real = scout.subprocess.run
    scout.subprocess.run = lambda *a, **k: calls.append((a, k)) or type(
        "P", (), {"returncode": 0, "stdout": "", "stderr": ""})()
    try:
        rc = scout.main(["--root", str(root), "--plan-task"])
    finally:
        scout.subprocess.run = real
    check("--plan-task registers nothing (subprocess.run never called)",
          lambda: rc == 0 and calls == [])

    empty = poll_once(str(root), catalog_text="# empty\nno names here\n")
    check("empty catalog is still SCOUTED with proposed_count=0",
          lambda: empty.get("state") == "SCOUTED"
          and empty.get("proposed_count") == 0
          and empty.get("ok") is True)

    junk = parse_catalog(
        "- **Cost:** billed\n- **(A)** discovery\n| 9 | **Ok** | x |\n",
        "junk")
    check("bold field labels and 2-letter names are not candidates",
          lambda: junk == [])

    gh_body = (
        "| 1 | [anomalyco/opencode](https://github.com/anomalyco/opencode) "
        "| 202.6k | +1958 |\n"
        "| 2 | [Aider-AI/aider](https://github.com/Aider-AI/aider) "
        "| 48.6k | +180 |\n"
        "| 3 | [cline/cline](https://github.com/cline/cline) "
        "| 67.2k | +468 |\n"
        "Inclusion criteria and **Last updated** 2026-08-31.\n"
    )
    gh = parse_catalog(gh_body, "gh-readme")
    gh_folds = {r["fold"] for r in gh}
    check("GH-link parser lifts opencode/aider/cline from org/repo links",
          lambda: {"opencode", "aider", "cline"} <= gh_folds)
    check("GH-link parser does not harvest Inclusion criteria",
          lambda: "inclusioncriteria" not in gh_folds
          and "lastupdated" not in gh_folds)

    gh_remote = poll_once(
        str(root), catalog_text=None, live_remote=True,
        transport=lambda url: {"http": 200, "body": gh_body, "rc": 0},
        dry_run=True)
    remote_src = next((s for s in (gh_remote.get("sources") or [])
                       if s.get("id") == "remote"), {})
    check("injected live_remote GH body reports names>0 not names=0",
          lambda: int(remote_src.get("names") or 0) >= 3
          and gh_remote.get("ok") is True)

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for l, ok, e in RESULTS:
        print(("  OK  " if ok else "  FAIL") + f" {l}" + (f"  {e}" if e else ""))
    print(f"{len(RESULTS) - len(bad)}/{len(RESULTS)} passed")
    live_value = {
        "checks": len(RESULTS),
        "clock_id": CLOCK_ID,
        "proposed_count": rec.get("proposed_count"),
        "known_count": rec.get("known_count"),
        "state": rec.get("state"),
        "heartbeat": HEARTBEAT_NAME,
    }
    print("LIVE_VALUE", json.dumps(live_value))
    (REPO / "cosmos" / "_f26_newai_scout.json").write_text(
        json.dumps({"ok": not bad, "live_value": live_value,
                    "proposed_folds": sorted(pfolds_live)}, indent=1) + "\n",
        encoding="utf-8")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
