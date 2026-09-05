#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_forge_rail_proposal - the suite for the STAGED cosmos_forge_rail.py proposal.

    py -3.14 builds/probe/test_forge_rail_proposal.py                 # hermetic gate
    py -3.14 builds/probe/test_forge_rail_proposal.py --live --root R # + real forges

The staged module lives in builds/probe/proposed/ and is NOT installed; cosmos/ is
outside this pass's write-fence. This suite proves the proposal against real code so
COW is handed tested work rather than a sketch.

TWO MODES, deliberately.

  Default (no args) is HERMETIC: no network, no live root, no binaries. It builds a
  throwaway sentinel root in a tempdir and injects fake `run`/`which`, so it asserts
  the same thing on any machine at any time. `cosmos_selftest_clock` globs
  builds/*/test_*.py, so this file IS one of the gated suites -- and a suite that
  reaches the network is a suite that goes flaky and reddens the clock for reasons
  that have nothing to do with the code. Flake-by-design is not a gate.

  --live adds the real `gh`/`glab` probes and needs --root. That is EVIDENCE for the
  proposal, not a gate, so it stays opt-in.

The load-bearing check is `rc!=0 with a valid body`: a run returning a perfectly good
payload carrying the bound value must still FAIL when the process exited non-zero.
That is the fabricated-pass class this whole pass was nearly caught by.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
STAGED = REPO / "builds" / "probe" / "proposed" / "cosmos_forge_rail.py"


def load_staged():
    """Import the staged module by location, with cosmos/ on the path (which is where
    it resolves its own imports from once it lands)."""
    sys.path.insert(0, str(REPO / "cosmos"))
    spec = importlib.util.spec_from_file_location("cosmos_forge_rail_staged", STAGED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def hermetic_checks(fr) -> dict:
    """No network, no live root, no binary. Same verdict on any machine."""
    checks: dict[str, str] = {}

    def refuses(label, fn, kind):
        try:
            fn()
            checks[label] = "DID NOT REFUSE"
        except fr.RailSeamError as e:
            checks[label] = "ok" if e.kind == kind else f"wrong kind {e.kind}"
        except Exception as e:                                        # noqa: BLE001
            checks[label] = f"wrong type {type(e).__name__}: {e}"

    refuses("unknown link_id", lambda: fr.merge_spec({"links": ["nope-forge"]}), "BAD_SPEC")
    refuses("empty links", lambda: fr.merge_spec({"links": []}), "BAD_SPEC")
    refuses("overlay not a dict", lambda: fr.merge_spec(["links"]), "BAD_SPEC")
    refuses("bad link in ForgeRail", lambda: fr.ForgeRail("nope", fr.default_spec()), "BAD_SPEC")

    # Authority refusal, against a THROWAWAY root - never the live one.
    from cosmos_paths import CosmosPaths, write_sentinel
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "forge-suite-root"
        write_sentinel(root, tree_id="forge-suite")
        paths = CosmosPaths(root, expected_tree_id="forge-suite")
        duck = type("KernelView", (), {})()
        duck.paths = paths
        duck.ledger = type("Led", (), {"_path": paths.ledger("authority.jsonl")})()
        duck.registry = None
        duck.spend = None
        # ledger_is_authority keys off the ledger path, so this must refuse even
        # though the root is disposable.
        refuses("authority attach", lambda: fr.attach_to_kernel(duck, {}), "REFUSED")
        checks["default spec on a bare root"] = (
            "ok" if fr.load_spec(fr.spec_path_for(paths))["schema"] == fr.SCHEMA
            else "did not fall back to default_spec")

    # An absent binary is UNREACHABLE, never a pass.
    rail = fr.ForgeRail("github-forge", fr.default_spec(), which=lambda _n: None)
    ok, detail = rail.probe()
    checks["absent binary"] = "ok" if (not ok and "ABSENT" in detail) else f"leaked: {ok} {detail}"

    # THE load-bearing one: rc!=0 must not pass even with a perfect body.
    rail = fr.ForgeRail(
        "github-forge", fr.default_spec(), which=lambda _n: "gh",
        run=lambda *_a, **_k: {"rc": 1, "out": '{"resources":{"core":{"limit":5000}}}',
                               "err": "", "timed_out": False})
    ok, detail = rail.probe()
    checks["rc!=0 with a valid body"] = "ok" if not ok else f"FABRICATED PASS: {detail}"

    # A timeout is UNREACHABLE, not a pass.
    rail = fr.ForgeRail("gitlab-forge", fr.default_spec(), which=lambda _n: "glab",
                        run=lambda *_a, **_k: {"rc": None, "out": "", "err": "",
                                               "timed_out": True})
    ok, detail = rail.probe()
    checks["timeout"] = "ok" if (not ok and "TIMEOUT" in detail) else f"leaked: {ok} {detail}"

    # rc==0 with a body missing the bound value must NOT pass: presence of a reply is
    # not proof of an authenticated reply.
    rail = fr.ForgeRail("gitlab-forge", fr.default_spec(), which=lambda _n: "glab",
                        run=lambda *_a, **_k: {"rc": 0, "out": '{"message":"401 Unauthorized"}',
                                               "err": "", "timed_out": False})
    ok, detail = rail.probe()
    checks["rc==0 without the bound value"] = "ok" if not ok else f"FABRICATED PASS: {detail}"

    # And the happy path still passes, or the guards above are just always-false.
    rail = fr.ForgeRail("gitlab-forge", fr.default_spec(), which=lambda _n: "glab",
                        run=lambda *_a, **_k: {"rc": 0, "out": '{"id":7,"username":"u"}',
                                               "err": "", "timed_out": False})
    ok, detail = rail.probe()
    checks["happy path passes"] = "ok" if (ok and "user_id=7" in detail) else f"blocked: {detail}"

    return checks


def main() -> int:
    ap = argparse.ArgumentParser(prog="test_forge_rail_proposal")
    ap.add_argument("--live", action="store_true",
                    help="also probe the REAL gh/glab (needs --root); evidence, not a gate")
    ap.add_argument("--root", default=None)
    a = ap.parse_args()

    if not STAGED.is_file():
        print(json.dumps({"ok": False, "detail": f"staged module missing: {STAGED}"}))
        return 1

    fr = load_staged()
    out: dict = {"staged": str(STAGED), "mode": "live" if a.live else "hermetic"}
    checks = hermetic_checks(fr)
    out["checks"] = checks
    ok = all(v == "ok" for v in checks.values())

    if a.live:
        if not a.root:
            print(json.dumps({"ok": False, "detail": "--live requires --root"}))
            return 2
        out["probe"] = fr._probe_all(a.root)
        ok = ok and out["probe"]["ok"]

    out["ok"] = ok
    print(json.dumps(out, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
