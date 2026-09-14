#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selftest: gdx-drive has a prove() call path (WIRED_NODES + live_call).

Hermetic. Injected GdxDriveRail. Never reads, prints, or copies OAuth tokens.
A missing credential is typed NO_KEY / UNMEASURED, never GREEN.

    py -3.14 tests\\test_gdx_drive_wired.py
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cosmos"))

import cosmos_gdx_drive_rail as R                                 # noqa: E402
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
    td = Path(tempfile.mkdtemp(prefix="cosmos_gdx_wired_"))
    try:
        by_id = {s["link_id"]: s for s in P.WIRED_NODES}
        check("gdx-drive is in WIRED_NODES (the prove() call path exists)",
              lambda: "gdx-drive" in by_id)
        row = by_id.get("gdx-drive") or {}
        check("gdx-drive shape is API core->drive module=None satellite=gdx-drive",
              lambda: (row.get("rail_type"), row.get("src"), row.get("dst"),
                       row.get("module"), row.get("satellite"))
              == ("API", "core", "drive", None, "gdx-drive"))
        check("SATELLITES['gdx-drive'] names cosmos_gdx_drive_rail and a callable",
              lambda: P.SATELLITES.get("gdx-drive", (None, None))[0]
              == "cosmos_gdx_drive_rail"
              and callable(P.SATELLITES.get("gdx-drive", (None, None))[1]))
        check("probe_module_for(gdx-drive) is cosmos_gdx_drive_rail, never claude",
              lambda: P.probe_module_for(row) == "cosmos_gdx_drive_rail")
        check("claude-cli remains the only Anthropic-default row",
              lambda: [s["link_id"] for s in P.WIRED_NODES
                       if P.probe_module_for(s) == "cosmos_claude_rail"]
              == ["claude-cli"])

        root = install(td / "live", tree_id="gdx-drive-wired")
        paths = CosmosPaths(root)
        check("a bare install does not configure the GDX satellite "
              "(existence of gdx_drive_credentials.json, never a read)",
              lambda: P._hands_configured(paths, row) is False)
        check("--live cannot force GDX on a root that has never configured it",
              lambda: P._should_live_probe(
                  paths, _Reg(), row, live=True, ttl_s=P.NODE_PROOF_TTL_S)
              is False)

        paths.config(R.CREDENTIALS_NAME).write_text(
            "PLACEHOLDER-NOT-A-TOKEN\n", encoding="utf-8")
        check("gdx_drive_credentials.json existing (unread) configures the satellite",
              lambda: P._hands_configured(paths, row) is True)
        check("1-minute clock (live=False) does NOT dispatch Drive "
              "even when the token file exists",
              lambda: P._should_live_probe(
                  paths, _Reg(), row, live=False, ttl_s=P.NODE_PROOF_TTL_S)
              is False)
        check("--live still asks GDX once the token file exists",
              lambda: P._should_live_probe(
                  paths, _Reg(), row, live=True, ttl_s=P.NODE_PROOF_TTL_S)
              is True)

        live_fn = getattr(P, "_gdx_drive_live_call", None)
        check("_gdx_drive_live_call exists on the prober (the prove-shaped path)",
              lambda: callable(live_fn))
        rec = live_fn(paths) if callable(live_fn) else {
            "ok": None, "detail": "ABSENT: no _gdx_drive_live_call"}
        dumped = json.dumps(rec)
        check("missing client secrets / invalid token is a typed refusal, not GREEN",
              lambda: rec.get("ok") is False
              and rec.get("kind") in ("NO_KEY", "UNREACHABLE", "AUTH_REQUIRED",
                                      "BROKE"))
        check("_gdx_drive_live_call never puts token material in the proof record",
              lambda: "PLACEHOLDER-NOT-A-TOKEN" not in dumped)

        real = R.GdxDriveRail

        class _Fake:
            def __init__(self, *a, **k):
                pass

            def dispatch(self, payload):
                return {
                    "ok": True, "rc": 0,
                    "body": "gdx-drive about.get email=keith.bbf@gmail.com "
                            "permissionId=106848635693308452650",
                    "text": "gdx-drive about.get email=keith.bbf@gmail.com "
                            "permissionId=106848635693308452650",
                    "model": "keith.bbf@gmail.com",
                    "model_source": R.MODEL_SOURCE,
                    "detail": "injected GdxDriveRail.dispatch",
                    "kind": "API",
                }

        try:
            R.GdxDriveRail = _Fake
            live = live_fn(paths) if callable(live_fn) else {}
        finally:
            R.GdxDriveRail = real
        check("injected GdxDriveRail.dispatch is the prove-shaped live_call",
              lambda: live.get("ok") is True and live.get("rc") == 0
              and live.get("model") == "keith.bbf@gmail.com"
              and "permissionId=106848635693308452650" in live.get("body", ""))
        check("injected proof clears the registry runtime-binding gate",
              lambda: __import__("cosmos_registry").proof_ok(live))
        check("default_live_call(gdx-drive) is the GDX path, not Claude",
              lambda: callable(P.default_live_call(paths, row))
              if row else False)
    finally:
        if old_env is not None:
            os.environ["COSMOS_BTS_ROOT"] = old_env

    bad = [(l, e) for l, ok, e in RESULTS if not ok]
    for label, ok, err in RESULTS:
        print("  %s  %s%s" % ("OK  " if ok else "FAIL", label,
                              ("  [" + err + "]") if err else ""))
    print("SELFTEST %s - %d checks (gdx-drive is wired for prove())"
          % ("PASS" if not bad else "FAIL", len(RESULTS)))
    return 0 if not bad else 1


class _Reg:
    def live_nodes(self):
        return {}


def test_gdx_drive_wired():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
