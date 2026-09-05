#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: codex-cli has a prove() call path (WIRED_NODES + live_call).

The credential half closed when Keith placed live/config/openai_api_key.txt.
This suite pins the structural half: the row is wired CLI core->code with
module=None (same shape as claude-cli) AND named as satellite=codex so
probe_module_for / default_live_call cannot fall through to the Anthropic
rail (the F-24 wiring's second escape, measured 2026-08-31).

Hermetic. Injected CodexRail. Never reads, prints, or copies key material.
A missing key is a typed NO_KEY, never worked around.

    py -3.14 tests\\test_codex_wired.py
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

import cosmos_codex_rail                                          # noqa: E402
import cosmos_rails_prober as P                                   # noqa: E402
from cosmos_kernel import install                                 # noqa: E402
from cosmos_paths import CosmosPaths                              # noqa: E402

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                        # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


def main() -> int:
    old_env = os.environ.pop("COSMOS_BTS_ROOT", None)
    td = Path(tempfile.mkdtemp(prefix="cosmos_codex_wired_"))
    try:
        by_id = {s["link_id"]: s for s in P.WIRED_NODES}
        check("codex-cli is in WIRED_NODES (the prove() call path exists)",
              lambda: "codex-cli" in by_id)
        row = by_id.get("codex-cli") or {}
        check("codex-cli shape matches the other CLI coding rail: "
              "rail_type=CLI src=core dst=code module=None",
              lambda: (row.get("rail_type"), row.get("src"), row.get("dst"),
                       row.get("module"))
              == ("CLI", "core", "code", None))
        check("codex-cli is a satellite (does NOT fall through to Anthropic)",
              lambda: row.get("satellite") == "codex")
        check("SATELLITES['codex'] names cosmos_codex_rail and a callable",
              lambda: P.SATELLITES.get("codex", (None, None))[0]
              == "cosmos_codex_rail"
              and callable(P.SATELLITES.get("codex", (None, None))[1]))
        check("probe_module_for(codex-cli) is cosmos_codex_rail, never claude",
              lambda: P.probe_module_for(row) == "cosmos_codex_rail")
        check("claude-cli remains the only Anthropic-default row",
              lambda: [s["link_id"] for s in P.WIRED_NODES
                       if P.probe_module_for(s) == "cosmos_claude_rail"]
              == ["claude-cli"])

        root = install(td / "live", tree_id="codex-wired")
        paths = CosmosPaths(root)
        check("a bare install does not configure the Codex satellite "
              "(existence of openai_api_key.txt, never a read)",
              lambda: P._hands_configured(paths, row) is False)
        check("--live cannot force Codex on a root that has never configured it",
              lambda: P._should_live_probe(
                  paths, _Reg(), row, live=True, ttl_s=P.NODE_PROOF_TTL_S)
              is False)

        # Existence only: write a placeholder whose contents are never read
        # by _hands_configured. Not a real key; not sk- shaped.
        paths.config(cosmos_codex_rail.KEY_NAME).write_text(
            "PLACEHOLDER-NOT-A-KEY\n", encoding="utf-8")
        check("openai_api_key.txt existing (unread) configures the satellite",
              lambda: P._hands_configured(paths, row) is True)
        check("1-minute clock (live=False) does NOT dispatch paid Codex "
              "even when the key file exists — failed prove must not retry",
              lambda: P._should_live_probe(
                  paths, _Reg(), row, live=False, ttl_s=P.NODE_PROOF_TTL_S)
              is False)
        check("unattended skip is requires-live for every rail, not a silent retry",
              lambda: P.SKIP_REQUIRES_LIVE == "requires-live")
        check("1-minute clock cannot dispatch ANY wired rail (not just OpenAI)",
              lambda: all(
                  P._should_live_probe(
                      paths, _Reg(), spec, live=False,
                      ttl_s=P.NODE_PROOF_TTL_S) is False
                  for spec in P.WIRED_NODES))
        check("--live still asks Codex once the key file exists",
              lambda: P._should_live_probe(
                  paths, _Reg(), row, live=True, ttl_s=P.NODE_PROOF_TTL_S)
              is True)

        live_fn = getattr(P, "_codex_live_call", None)
        check("_codex_live_call exists on the prober (the prove-shaped path)",
              lambda: callable(live_fn))
        rec = live_fn(paths) if callable(live_fn) else {
            "ok": None, "detail": "ABSENT: no _codex_live_call"}
        dumped = json.dumps(rec)
        check("missing/invalid key is a typed NO_KEY, not a workaround",
              lambda: rec.get("ok") is False
              and "NO_KEY" in str(rec.get("detail") or rec.get("kind") or ""))
        check("_codex_live_call never puts key material in the proof record",
              lambda: "PLACEHOLDER-NOT-A-KEY" not in dumped)

        real = cosmos_codex_rail.CodexRail

        class _Fake:
            def __init__(self, *a, **k):
                pass

            def dispatch(self, payload):
                return {
                    "ok": True, "rc": 0, "body": "PONG", "text": "PONG",
                    "model": "gpt-5.4-codex", "model_source": "jsonl",
                    "detail": "injected CodexRail.dispatch",
                    "kind": "CLI",
                }

        try:
            cosmos_codex_rail.CodexRail = _Fake
            live = live_fn(paths) if callable(live_fn) else {}
        finally:
            cosmos_codex_rail.CodexRail = real
        check("injected CodexRail.dispatch is the prove-shaped live_call",
              lambda: live.get("ok") is True and live.get("rc") == 0
              and live.get("body") == "PONG"
              and live.get("model") == "gpt-5.4-codex")
        check("injected proof clears the registry runtime-binding gate",
              lambda: __import__("cosmos_registry").proof_ok(live))
        check("default_live_call(codex-cli) is the Codex path, not Claude",
              lambda: callable(P.default_live_call(paths, row))
              if row else False)
    finally:
        if old_env is not None:
            os.environ["COSMOS_BTS_ROOT"] = old_env

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (codex-cli is wired for prove())"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


class _Reg:
    def live_nodes(self):
        return {}


def test_codex_wired():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
