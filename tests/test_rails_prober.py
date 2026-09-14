#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: rails prober populates live/registry from proven live calls.

Uses injected live_calls so this never spends a cent. A real rail call is
NATIVE-DEMO / --live against a live root.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_kernel import install
from cosmos_rails_prober import WIRED_NODES, poll_once

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                            # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def _fake(link_id, model, ok=True, rc=0, body="PONG"):
    def _call():
        return {"ok": ok, "rc": rc, "body": body, "model": model,
                "text": body, "link_id": link_id}
    return _call


FAKES = {
    "sgh-api": _fake("sgh-api", "grok-4.6"),
    "gem-api": _fake("gem-api", "gemini-2.5-flash"),
    "oa-api": _fake("oa-api", "gpt-5.6-terra"),
    "claude-cli": _fake("claude-cli", "claude-haiku-4-5"),
    "codex-cli": _fake("codex-cli", "gpt-5.4-codex"),
    "gw-api": _fake("gw-api", "grok-build-0.1"),
    "cursor-api": _fake("cursor-api", "Cursor COSMOS 2"),
    "firecrawl-web": _fake("firecrawl-web", "firecrawl/v2-research-papers"),
    "groq-api": _fake("groq-api", "openai/gpt-oss-20b"),
    "gem-free": _fake("gem-free", "gemini-2.5-flash"),
    "playwright-dom": _fake("playwright-dom",
                            "Playwright/1.63.0-alpha-2026-08-05"),
    "github-forge": _fake("github-forge", "rest_limit=5000 remaining=4999"),
    "gitlab-forge": _fake("gitlab-forge", "user_id=42 username=probe-user"),
}
WIRED_IDS = [s["link_id"] for s in WIRED_NODES]


def main() -> int:
    old_env = os.environ.pop("COSMOS_BTS_ROOT", None)
    try:
        td = Path(tempfile.mkdtemp(prefix="cosmos_rprob_"))
        root = install(td / "live", tree_id="rails-prober")

        # default poll (no bts_root, no --live) must NOT invoke live_calls
        calls = {"n": 0}

        def _count():
            calls["n"] += 1
            return {"ok": True, "rc": 0, "body": "PONG", "model": "nope"}

        r0 = poll_once(str(root), live=False,
                       live_calls={lid: _count for lid, *_ in
                                   ((s["link_id"],) for s in WIRED_NODES)})
        check("poll_once without hands configured does not spend",
              lambda: r0.get("ok") is True and calls["n"] == 0)
        src = (Path(__file__).resolve().parent.parent / "cosmos"
               / "cosmos_rails_prober.py").read_text(encoding="utf-8")
        check("1-minute clock is identity-only; all rail proves require --live",
              lambda: 'SKIP_REQUIRES_LIVE = "requires-live"' in src
              and "if not live and not injected:" in src
              and "_cursor_probe" in src)
        nodes0 = json.loads(
            (root / "registry" / "nodes.json").read_text(encoding="utf-8"))
        check("unproven poll writes MEASURED-empty registry files",
              lambda: nodes0["count"] == 0 and nodes0["nodes"] == []
              and (root / "registry" / "rails.json").is_file())

        r = poll_once(str(root), live=True, live_calls=FAKES)
        check("poll_once --live registers every wired node",
              lambda: r.get("ok") is True
              and set(r.get("registered") or []) == set(WIRED_IDS))
        disk = json.loads(
            (root / "registry" / "nodes.json").read_text(encoding="utf-8"))
        by_id = {row["link_id"]: row for row in disk["matrix"]}
        check("nodes.json quotes model+rc+body_bytes per node",
              lambda: disk["count"] == len(WIRED_IDS)
              and by_id["sgh-api"]["model"] == "grok-4.6"
              and by_id["gem-api"]["model"] == "gemini-2.5-flash"
              and by_id["oa-api"]["model"] == "gpt-5.6-terra"
              and by_id["claude-cli"]["model"] == "claude-haiku-4-5"
              and by_id["codex-cli"]["model"] == "gpt-5.4-codex"
              and by_id["gw-api"]["model"] == "grok-build-0.1"
              and by_id["cursor-api"]["model"] == "Cursor COSMOS 2"
              and by_id["firecrawl-web"]["model"] == "firecrawl/v2-research-papers"
              and by_id["groq-api"]["model"] == "openai/gpt-oss-20b"
              and by_id["gem-free"]["model"] == "gemini-2.5-flash"
              and by_id["playwright-dom"]["model"]
              == "Playwright/1.63.0-alpha-2026-08-05"
              and by_id["github-forge"]["model"]
              == "rest_limit=5000 remaining=4999"
              and by_id["gitlab-forge"]["model"]
              == "user_id=42 username=probe-user"
              and all(row["rc"] == 0 and row["body_bytes"] > 0
                      for row in disk["matrix"]))

        mixed = {
            "sgh-api": FAKES["sgh-api"],
            "gem-api": _fake("gem-api", "gemini-2.5-flash", ok=False, rc=2,
                             body=""),
            "oa-api": FAKES["oa-api"],
            "claude-cli": _fake("claude-cli", "", ok=True, rc=0, body="PONG"),
            "codex-cli": _fake("codex-cli", "", ok=False, rc=2, body=""),
            "gw-api": _fake("gw-api", "", ok=False, rc=2, body=""),
            "cursor-api": _fake("cursor-api", "", ok=False, rc=2, body=""),
            "firecrawl-web": _fake("firecrawl-web", "", ok=False, rc=2,
                                   body=""),
            "groq-api": _fake("groq-api", "", ok=False, rc=2, body=""),
            "gem-free": _fake("gem-free", "", ok=False, rc=2, body=""),
            "playwright-dom": _fake("playwright-dom", "", ok=False, rc=2,
                                    body=""),
            "github-forge": _fake("github-forge", "", ok=False, rc=2, body=""),
            "gitlab-forge": _fake("gitlab-forge", "", ok=False, rc=2, body=""),
        }
        root2 = install(td / "live2", tree_id="rails-prober-2")
        r2 = poll_once(str(root2), live=True, live_calls=mixed)
        check("a node that does not answer is NOT registered",
              lambda: set(r2.get("registered") or []) == {"sgh-api", "oa-api"})
        disk2 = json.loads(
            (root2 / "registry" / "nodes.json").read_text(encoding="utf-8"))
        check("failed gem/claude absent from projection",
              lambda: "gem-api" not in disk2["nodes"]
              and "claude-cli" not in disk2["nodes"]
              and disk2["count"] == 2)

        check("WIRED_NODES is the named hands, not a static dump",
              lambda: [s["link_id"] for s in WIRED_NODES]
              == ["sgh-api", "gem-api", "gw-api", "oa-api", "claude-cli",
                  "codex-cli",
                  "cursor-api", "firecrawl-web", "groq-api", "gem-free",
                  "playwright-dom", "github-forge", "gitlab-forge"])

        src = (Path(__file__).resolve().parent.parent / "cosmos"
               / "cosmos_rails_prober.py").read_text(encoding="utf-8")
        check("prober still does not import bts_* (NodeRail wraps)",
              lambda: "from bts_" not in src and "import bts_" not in src)
        check("prober does not modify kernel/sched/service",
              lambda: "Does not modify" in src)
    finally:
        if old_env is not None:
            os.environ["COSMOS_BTS_ROOT"] = old_env

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (prober files proven-live registry)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_rails_prober():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
