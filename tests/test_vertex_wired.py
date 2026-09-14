#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: gem-api (GEM-VERTEX / Joanna) has a prove() call path.

WIRED_NODES row is satellite=vertex so probe_module_for / default_live_call
cannot treat bts_gem import-liveness as a proof (F-24). Vendor-emitted
modelVersion is the responder. Missing key is UNMEASURED, never GREEN.

Hermetic. Injected VertexRail. Never reads, prints, or copies key material.

    py -3.14 tests\\test_vertex_wired.py
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

import cosmos_rails_prober as P                                   # noqa: E402
import cosmos_vertex_rail                                         # noqa: E402
from cosmos_kernel import install                                 # noqa: E402
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
    old_vk = os.environ.pop("VERTEX_API_KEY", None)
    td = Path(tempfile.mkdtemp(prefix="cosmos_vertex_wired_"))
    try:
        by_id = {s["link_id"]: s for s in P.WIRED_NODES}
        check("gem-api is in WIRED_NODES (the prove() call path exists)",
              lambda: "gem-api" in by_id)
        row = by_id.get("gem-api") or {}
        check("gem-api shape is API core->models family=gem-vertex",
              lambda: (row.get("rail_type"), row.get("src"), row.get("dst"),
                       row.get("family"))
              == ("API", "core", "models", "gem-vertex"))
        check("gem-api is a vertex satellite (does NOT use bts_gem as prove)",
              lambda: row.get("satellite") == "vertex"
              and row.get("module") is None)
        check("SATELLITES['vertex'] names cosmos_vertex_rail and a callable",
              lambda: P.SATELLITES.get("vertex", (None, None))[0]
              == "cosmos_vertex_rail"
              and callable(P.SATELLITES.get("vertex", (None, None))[1]))
        check("probe_module_for(gem-api) is cosmos_vertex_rail, never claude",
              lambda: P.probe_module_for(row) == "cosmos_vertex_rail")
        check("Kernel compose row already binds cosmos_vertex_rail",
              lambda: ('"gem-api", "cosmos_vertex_rail", "attach_to_kernel"'
                       in (Path(__file__).resolve().parent.parent / "cosmos"
                           / "cosmos_kernel.py").read_text(encoding="utf-8")))

        root = install(td / "live", tree_id="vertex-wired")
        paths = CosmosPaths(root)
        check("a bare install does not configure the Vertex satellite",
              lambda: P._hands_configured(paths, row) is False)
        check("--live cannot force Vertex on a root that has never configured it",
              lambda: P._should_live_probe(
                  paths, _Reg(), row, live=True, ttl_s=P.NODE_PROOF_TTL_S)
              is False)

        paths.config(cosmos_vertex_rail.KEY_NAME).write_text(
            "PLACEHOLDER-NOT-A-VERTEX-KEY\n", encoding="utf-8")
        check("vertex_key.txt existing (unread) configures the satellite",
              lambda: P._hands_configured(paths, row) is True)
        check("1-minute clock (live=False) does NOT dispatch Vertex",
              lambda: P._should_live_probe(
                  paths, _Reg(), row, live=False, ttl_s=P.NODE_PROOF_TTL_S)
              is False)
        check("--live still asks Vertex once the key file exists",
              lambda: P._should_live_probe(
                  paths, _Reg(), row, live=True, ttl_s=P.NODE_PROOF_TTL_S)
              is True)

        live_fn = getattr(P, "_vertex_live_call", None)
        check("_vertex_live_call exists on the prober (the prove-shaped path)",
              lambda: callable(live_fn))

        real = cosmos_vertex_rail.VertexRail

        class _Named:
            def __init__(self, *a, **k):
                self._last = {"modelVersion": "gemini-2.5-flash",
                              "http": 200, "via": "vertex"}

            def last_identity(self):
                return dict(self._last)

            def dispatch(self, payload):
                return {
                    "ok": True, "rc": 0, "body": "PONG", "text": "PONG",
                    "model": "gemini-2.5-flash",
                    "model_source": "modelVersion (generateContent)",
                    "detail": "injected VertexRail.dispatch",
                    "kind": "API", "via": "vertex",
                }

        class _NoName:
            def __init__(self, *a, **k):
                self._last = {"modelVersion": "", "http": 200, "via": "vertex"}

            def last_identity(self):
                return dict(self._last)

            def dispatch(self, payload):
                return {
                    "ok": True, "rc": 0, "body": "PONG", "text": "PONG",
                    "model": "", "detail": "no modelVersion",
                    "kind": "API", "via": "vertex",
                }

        try:
            cosmos_vertex_rail.VertexRail = _Named
            live = live_fn(paths) if callable(live_fn) else {}
        finally:
            cosmos_vertex_rail.VertexRail = real
        dumped = json.dumps(live)
        check("injected VertexRail.dispatch is the prove-shaped live_call",
              lambda: live.get("ok") is True and live.get("rc") == 0
              and live.get("body") == "PONG"
              and live.get("model") == "gemini-2.5-flash"
              and live.get("model_source").startswith("modelVersion"))
        check("injected proof clears the registry runtime-binding gate",
              lambda: __import__("cosmos_registry").proof_ok(live))
        check("_vertex_live_call never puts key material in the proof record",
              lambda: "PLACEHOLDER-NOT-A-VERTEX-KEY" not in dumped)

        try:
            cosmos_vertex_rail.VertexRail = _NoName
            nameless = live_fn(paths) if callable(live_fn) else {}
        finally:
            cosmos_vertex_rail.VertexRail = real
        check("vendor answer with no modelVersion is NOT registered as GREEN",
              lambda: nameless.get("ok") is False
              and nameless.get("model") == ""
              and not __import__("cosmos_registry").proof_ok(nameless))

        paths.config(cosmos_vertex_rail.KEY_NAME).unlink()
        bare = live_fn(paths) if callable(live_fn) else {}
        check("absent credential is UNMEASURED, never fake GREEN",
              lambda: bare.get("ok") is False
              and bare.get("kind") == "UNMEASURED"
              and "UNMEASURED" in str(bare.get("detail") or "")
              and not __import__("cosmos_registry").proof_ok(bare))
        check("default_live_call(gem-api) is the Vertex path",
              lambda: callable(P.default_live_call(paths, row)))
    finally:
        if old_env is not None:
            os.environ["COSMOS_BTS_ROOT"] = old_env
        if old_vk is not None:
            os.environ["VERTEX_API_KEY"] = old_vk

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (gem-api GEM-VERTEX is wired for prove())"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


def test_vertex_wired():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
