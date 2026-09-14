#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: openrouter-api has a prove() call path (WIRED_NODES + live_call).

The satellite module already existed (named Gemma 4 pin, farm ling/ds/glm/qwen
seats). The structural half was missing: no WIRED_NODES row, no Kernel compose
row, so nothing asked it for a PROBE_RESULT. Same F-24 class as groq-api.

Hermetic. Injected OpenRouterRail. Never reads, prints, or copies key material.
A missing key is a typed miss — never a green stand-in.

    py -3.14 tests\\test_openrouter_wired.py
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

import cosmos_openrouter_rail as OR                               # noqa: E402
import cosmos_rails_prober as P                                   # noqa: E402
from cosmos_kernel import Kernel, install                         # noqa: E402
from cosmos_paths import CosmosPaths                              # noqa: E402

RESULTS = []


def check(label, fn):
    try:
        RESULTS.append((label, bool(fn()), ""))
    except Exception as e:                                        # noqa: BLE001
        RESULTS.append((label, False, f"{type(e).__name__}: {e}"))


class _Reg:
    def live_nodes(self):
        return {}


def main() -> int:
    old_env = os.environ.pop("COSMOS_BTS_ROOT", None)
    old_or = os.environ.pop("OPENROUTER_API_KEY", None)
    td = Path(tempfile.mkdtemp(prefix="cosmos_or_wired_"))
    try:
        by_id = {s["link_id"]: s for s in P.WIRED_NODES}
        check("openrouter-api is in WIRED_NODES (the prove() call path exists)",
              lambda: "openrouter-api" in by_id)
        row = by_id.get("openrouter-api") or {}
        check("openrouter-api is API core->models, not a coding-rail capture",
              lambda: (row.get("rail_type"), row.get("src"), row.get("dst"),
                       row.get("module"))
              == ("API", "core", "models", None))
        check("openrouter-api is a satellite (does NOT fall through to Anthropic)",
              lambda: row.get("satellite") == "openrouter")
        check("SATELLITES['openrouter'] names cosmos_openrouter_rail and a callable",
              lambda: P.SATELLITES.get("openrouter", (None, None))[0]
              == "cosmos_openrouter_rail"
              and callable(P.SATELLITES.get("openrouter", (None, None))[1]))
        check("probe_module_for(openrouter-api) is cosmos_openrouter_rail",
              lambda: P.probe_module_for(row) == "cosmos_openrouter_rail")
        check("claude-cli remains the only Anthropic-default row",
              lambda: [s["link_id"] for s in P.WIRED_NODES
                       if P.probe_module_for(s) == "cosmos_claude_rail"]
              == ["claude-cli"])

        root = install(td / "live", tree_id="openrouter-wired")
        paths = CosmosPaths(root)
        check("a bare install does not configure the OpenRouter satellite "
              "(existence of openrouter_api_key.txt, never a read)",
              lambda: P._hands_configured(paths, row) is False)
        check("--live cannot force OpenRouter on a root that has never "
              "configured it",
              lambda: P._should_live_probe(
                  paths, _Reg(), row, live=True, ttl_s=P.NODE_PROOF_TTL_S)
              is False)

        live_fn = getattr(P, "_openrouter_live_call", None)
        check("_openrouter_live_call exists on the prober (the prove-shaped path)",
              lambda: callable(live_fn))
        # No key file, no env. The rail returns typed 401 — never a vendor GET.
        rec = live_fn(paths) if callable(live_fn) else {
            "ok": None, "detail": "ABSENT: no _openrouter_live_call"}
        check("missing key is not a green proof (NO_KEY, empty model+body)",
              lambda: rec.get("ok") is False
              and not rec.get("model")
              and not rec.get("body"))

        paths.config(OR.KEY_NAME).write_text(
            "PLACEHOLDER-NOT-A-KEY\n", encoding="utf-8")
        check("openrouter_api_key.txt existing (unread) configures the satellite",
              lambda: P._hands_configured(paths, row) is True)
        check("1-minute clock (live=False) does NOT dispatch OpenRouter "
              "even when the key file exists",
              lambda: P._should_live_probe(
                  paths, _Reg(), row, live=False, ttl_s=P.NODE_PROOF_TTL_S)
              is False)
        check("--live still asks OpenRouter once the key file exists",
              lambda: P._should_live_probe(
                  paths, _Reg(), row, live=True, ttl_s=P.NODE_PROOF_TTL_S)
              is True)

        k = Kernel(root, worker="openrouter-wired")
        composed = list((k.rails_compose or {}).get("composed") or [])
        check("Kernel compose row attaches the adapter without proving",
              lambda: "openrouter-api" in composed
              and "openrouter-api" in k.adapters
              and "openrouter-api" not in k.registry.live_nodes())
        check("boot compose does not invent verified=True",
              lambda: all(r.get("verified") is not True
                          for r in k.registry.matrix()
                          if r.get("link_id") == "openrouter-api"))
        check("_openrouter_live_call never puts key material in the proof record",
              lambda: "PLACEHOLDER-NOT-A-KEY" not in json.dumps(rec))

        real = OR.OpenRouterRail

        class _Fake:
            def __init__(self, *a, **k):
                self._last = {
                    "ok": True, "http": 200, "n_models": 2,
                    "has_gemma4_26b": True,
                    "has_gemma4_31b": True,
                    "model_ids": [OR.DEFAULT_MODEL],
                    "kind": None,
                    "detail": f"http=200 n=2 has {OR.DEFAULT_MODEL}=True",
                }

            def probe(self):
                return True, self._last["detail"]

            def last_identity(self):
                return self._last

        try:
            OR.OpenRouterRail = _Fake
            live = live_fn(paths) if callable(live_fn) else {}
        finally:
            OR.OpenRouterRail = real
        check("injected GET /models is the prove-shaped live_call",
              lambda: live.get("ok") is True and live.get("rc") == 0
              and OR.DEFAULT_MODEL in (live.get("body") or "")
              and live.get("model") == OR.DEFAULT_MODEL
              and live.get("model_source") == "GET /models id list")
        check("injected proof clears the registry runtime-binding gate",
              lambda: __import__("cosmos_registry").proof_ok(live))
        check("default_live_call(openrouter-api) is the OpenRouter path",
              lambda: callable(P.default_live_call(paths, row))
              if row else False)
        src = (Path(__file__).resolve().parent.parent / "cosmos"
               / "cosmos_kernel.py").read_text(encoding="utf-8")
        check("Kernel compose names openrouter-api + boot_compose=True",
              lambda: '"openrouter-api"' in src
              and "cosmos_openrouter_rail" in src)
    finally:
        if old_env is not None:
            os.environ["COSMOS_BTS_ROOT"] = old_env
        if old_or is not None:
            os.environ["OPENROUTER_API_KEY"] = old_or

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (openrouter-api is wired for prove())"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_openrouter_wired():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
