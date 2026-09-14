#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: writing Kernel boot attaches Dispatcher + proves node rails.

Wishlist #64 second half. Isolated tmp root. Injected live_calls so this
never spends a cent. After boot the live/registry projection is non-empty
and lists ONLY proven nodes (rc==0 + body + model). A node that does not
answer is NOT registered; boot still READY.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

from cosmos_kernel import Kernel, install
from cosmos_rails_prober import WIRED_NODES

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
    # F-24: the four rails that answered their own probes and were never asked.
    # Each carries the responder its VENDOR emits, not a name invented here.
    "gw-api": _fake("gw-api", "grok-build-0.1"),
    "cursor-api": _fake("cursor-api", "Cursor COSMOS 2"),
    "firecrawl-web": _fake("firecrawl-web", "firecrawl/v2-research-papers"),
    "playwright-dom": _fake("playwright-dom",
                            "Playwright/1.63.0-alpha-2026-08-05"),
    "github-forge": _fake("github-forge", "rest_limit=5000 remaining=4999"),
    "gitlab-forge": _fake("gitlab-forge", "user_id=42 username=probe-user"),
    "groq-api": _fake("groq-api", "openai/gpt-oss-20b"),
    "cop-chat": _fake("cop-chat", "gpt-5.6"),
}

WIRED_IDS = [s["link_id"] for s in WIRED_NODES]


def _disk(root):
    p = Path(root) / "registry" / "nodes.json"
    r = Path(root) / "registry" / "rails.json"
    nodes = json.loads(p.read_text(encoding="utf-8"))
    rails = json.loads(r.read_text(encoding="utf-8"))
    return nodes, rails


def main() -> int:
    old_env = os.environ.pop("COSMOS_BTS_ROOT", None)
    try:
        td = Path(tempfile.mkdtemp(prefix="cosmos_boot_attach_"))

        # --- no live_calls, no hands: MUST NOT spend; measured-empty ---
        calls = {"n": 0}

        def _count():
            calls["n"] += 1
            return {"ok": True, "rc": 0, "body": "PONG", "model": "nope"}

        root0 = install(td / "live0", tree_id="boot-attach-0")
        k0 = Kernel(root0, worker="core")
        check("boot without live_calls is READY", lambda: k0.ready is True)
        check("Dispatcher is composed on normal boot",
              lambda: k0.dispatcher is not None)
        check("node-rail adapters are attached (built, even if unproven)",
              lambda: {"sgh-api", "gem-api", "oa-api"} <= set(k0.adapters))
        d0, r0 = _disk(root0)
        check("unproven boot writes MEASURED-empty registry projection",
              lambda: d0.get("schema") == "cosmos-registry/1"
              and d0.get("count") == 0 and d0.get("nodes") == []
              and r0 == d0)
        check("unproven boot does not invent LINK_REGISTERED for model rails",
              lambda: not ({"sgh-api", "gem-api", "oa-api"}
                           & set(k0.registry.state())))
        k0b = Kernel(root0, worker="core", live_calls={
            lid: _count for lid in WIRED_IDS})
        check("injected live_calls ARE invoked when passed (force-prove)",
              lambda: k0b.ready and calls["n"] == len(WIRED_IDS))

        # --- live_calls: projection non-empty, only proven nodes ---
        root = install(td / "live", tree_id="boot-attach")
        spent = {"n": 0}

        def _wrap(lid, model):
            inner = FAKES[lid]

            def _call():
                spent["n"] += 1
                return inner()
            return _call

        wrapped = {lid: _wrap(lid, FAKES[lid]) for lid in FAKES}
        k = Kernel(root, worker="core", live_calls=wrapped)
        rec = k.rails_compose or {}
        d, rails = _disk(root)
        by_id = {row["link_id"]: row for row in d.get("matrix") or []}
        check("boot with injected live_calls is READY",
              lambda: k.ready is True)
        check("Dispatcher composed", lambda: k.dispatcher is not None)
        check("projection schema is the registry authority (not a dump)",
              lambda: d.get("schema") == "cosmos-registry/1"
              and rails == d
              and d.get("measured_at") is not None)
        check("projection is non-empty and lists every wired node",
              lambda: d.get("count") == len(WIRED_IDS)
              and set(d.get("nodes") or []) == set(WIRED_IDS)
              and set(rec.get("registered") or []) == set(WIRED_IDS))
        check("projection quotes model+rc+body_bytes per proven node",
              lambda: by_id["sgh-api"]["model"] == "grok-4.6"
              and by_id["gem-api"]["model"] == "gemini-2.5-flash"
              and by_id["oa-api"]["model"] == "gpt-5.6-terra"
              and by_id["claude-cli"]["model"] == "claude-haiku-4-5"
              and by_id["codex-cli"]["model"] == "gpt-5.4-codex"
              and by_id["gw-api"]["model"] == "grok-build-0.1"
              and by_id["cursor-api"]["model"] == "Cursor COSMOS 2"
              and by_id["firecrawl-web"]["model"] == "firecrawl/v2-research-papers"
              and by_id["playwright-dom"]["model"]
              == "Playwright/1.63.0-alpha-2026-08-05"
              and by_id["github-forge"]["model"]
              == "rest_limit=5000 remaining=4999"
              and by_id["gitlab-forge"]["model"]
              == "user_id=42 username=probe-user"
              and by_id["groq-api"]["model"] == "openai/gpt-oss-20b"
              and by_id["cop-chat"]["model"] == "gpt-5.6"
              and all(row["rc"] == 0 and row["body_bytes"] > 0
                      and row.get("verified") is True
                      for row in d["matrix"]))
        check("live_nodes matches the disk projection",
              lambda: set(k.registry.live_nodes()) == set(d["nodes"]))
        check("injected live_calls ran once per wired node (no default rail)",
              lambda: spent["n"] == len(WIRED_IDS))

        # --- mixed: a node that does not answer is NOT registered ---
        mixed = {
            "sgh-api": FAKES["sgh-api"],
            "gem-api": _fake("gem-api", "gemini-2.5-flash", ok=False, rc=2,
                             body=""),
            "oa-api": FAKES["oa-api"],
            "claude-cli": _fake("claude-cli", "", ok=True, rc=0, body="PONG"),
            "codex-cli": _fake("codex-cli", "", ok=False, rc=2, body=""),
            # Extra F-24 rails stay injected so live=True never falls through
            # to default_live_call (gw-api is a module rail, not a satellite).
            "gw-api": _fake("gw-api", "", ok=False, rc=2, body=""),
            "cursor-api": _fake("cursor-api", "", ok=False, rc=2, body=""),
            "firecrawl-web": _fake("firecrawl-web", "", ok=False, rc=2,
                                   body=""),
            "playwright-dom": _fake("playwright-dom", "", ok=False, rc=2,
                                    body=""),
            "github-forge": _fake("github-forge", "", ok=False, rc=2, body=""),
            "gitlab-forge": _fake("gitlab-forge", "", ok=False, rc=2, body=""),
            "groq-api": _fake("groq-api", "", ok=False, rc=2, body=""),
            "cop-chat": _fake("cop-chat", "", ok=False, rc=2, body=""),
        }
        root2 = install(td / "live2", tree_id="boot-attach-2")
        k2 = Kernel(root2, worker="core", live_calls=mixed)
        d2, _ = _disk(root2)
        check("mixed boot stays READY (dead node does not abort)",
              lambda: k2.ready is True and k2.dispatcher is not None)
        check("a node that does not answer is NOT registered",
              lambda: set(k2.rails_compose.get("registered") or [])
              == {"sgh-api", "oa-api"}
              and set(d2.get("nodes") or []) == {"sgh-api", "oa-api"})
        check("failed gem is absent from live_nodes and from state",
              lambda: "gem-api" not in k2.registry.live_nodes()
              and "gem-api" not in k2.registry.state())
        check("failed claude (no model) is absent from the projection",
              lambda: "claude-cli" not in d2.get("nodes")
              and "claude-cli" not in k2.registry.live_nodes())
        check("dead-node warning is a visible refusal on the compose report",
              lambda: "gem-api" in (k2.rails_compose.get("warnings") or {}))

        # --- all dead: still READY, measured-empty ---
        dead = {lid: _fake(lid, "", ok=False, rc=2, body="")
                for lid in WIRED_IDS}
        root3 = install(td / "live3", tree_id="boot-attach-3")
        k3 = Kernel(root3, worker="core", live_calls=dead)
        d3, _ = _disk(root3)
        check("all-dead boot is READY and writes measured-empty projection",
              lambda: k3.ready is True and d3.get("count") == 0
              and d3.get("nodes") == []
              and not (set(WIRED_IDS) & set(k3.registry.live_nodes())))

        src = (Path(__file__).resolve().parent.parent / "cosmos"
               / "cosmos_kernel.py").read_text(encoding="utf-8")
        check("kernel reuses map_wired_nodes (does not re-implement probing)",
              lambda: "map_wired_nodes" in src
              and "file_runtime" in src
              and "LIVE_PROMPT" not in src)
        check("kernel no longer dumps adapters as the registry projection",
              lambda: "sorted(self.adapters)" not in src)
    finally:
        if old_env is not None:
            os.environ["COSMOS_BTS_ROOT"] = old_env

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (boot proves nodes; claim != proof)"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_boot_attach():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
