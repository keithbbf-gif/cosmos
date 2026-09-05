#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regression tests for F-33/F-34: Core not served on the REAL root :8770.

The bug had two halves, both measured 2026-08-31:
  1. `COSMOS_Serve_Watchdog` (the only task that starts Core) runs the
     out-of-tree V:\\Ai\\BTS_MESH\\cosmos_watchdog.py, hard-coded to
     ROOT=...\\trylive PORT=8791. It kept the TRIAL Core up and returned rc=0,
     hiding the fact that the real root was unserved.
  2. `cosmos_health_clock._supervise_serve` -- the in-tree fix -- was gated
     behind an opt-in flag the registered SCHTASKS action never passed, so it
     returned DISABLED for all 89,082 polls.

These tests pin half 2 (the part inside this fence). Each asserts something that
is FALSE against the pre-fix module, so they fail if the default is flipped back.

    py -3.14 builds\\health\\test_serve_supervisor.py
    py -3.14 builds\\health\\test_serve_supervisor.py --root V:\\A\\Ai\\COSMOS\\live

The selftest clock invokes discovered suites with no argv. --root is optional:
omitted, the suite installs a scratch root so CosmosPaths can verify. The live
root is still accepted when handed in.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "cosmos"))


def load(mod_path: Path):
    spec = importlib.util.spec_from_file_location("hc_under_test", mod_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_parser(mod):
    """Rebuild main()'s parser to read the shipped default without running it."""
    ap = argparse.ArgumentParser(prog="cosmos_health_clock")
    ap.add_argument("--root", required=True)
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--standup", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--interval", type=float, default=mod.DEFAULT_INTERVAL_S)
    return ap


RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(cond), detail))
    print("%-46s %s %s" % (name, "PASS" if cond else "FAIL", detail))


def test_default_on(mod) -> None:
    """poll_once/loop/standup must default to supervising.

    Pre-fix these defaulted to False -> this test FAILS on the old module.
    """
    import inspect
    for fn_name in ("poll_once", "loop", "standup"):
        sig = inspect.signature(getattr(mod, fn_name))
        got = sig.parameters["supervise"].default
        check("default_on:%s" % fn_name, got is True, "default=%r" % (got,))


def test_cli_flag_pair(mod) -> None:
    """The CLI must expose --supervise AND --no-supervise, defaulting ON.

    Pre-fix --no-supervise did not exist (store_true) -> FAILS on old module.
    """
    src = Path(mod.__file__).read_text(encoding="utf-8")
    check("cli:BooleanOptionalAction",
          "BooleanOptionalAction" in src,
          "argparse pair present")
    check("cli:default_true",
          "action=argparse.BooleanOptionalAction" in src
          and "default=True" in src,
          "flag defaults ON")


def test_standup_registers_explicitly(mod) -> None:
    """standup() must write the flag into the task action EXPLICITLY.

    A registration that omits the flag is precisely how the supervisor stayed
    dormant through 89,082 polls; relying on the default repeats the scar.
    """
    src = Path(mod.__file__).read_text(encoding="utf-8")
    check("standup:explicit_flag",
          '"--supervise" if supervise else "--no-supervise"' in src,
          "task action pins intent")


def test_disabled_path_is_inert(mod, root: str) -> None:
    """--no-supervise must still return DISABLED and touch nothing."""
    from cosmos_paths import CosmosPaths
    paths = CosmosPaths(root)
    r = mod._supervise_serve(paths, up=False, supervise=False,
                             pause_present=False, pause_mode=None)
    check("inert:disabled_kind", r.get("kind") == "DISABLED", json.dumps(r))


def test_already_up_when_port_live(mod, root: str) -> None:
    """With Core actually listening, the supervisor must NOT spawn a second
    writer -- it must report ALREADY_UP. Bound to a live probe, not a guess."""
    from cosmos_paths import CosmosPaths
    paths = CosmosPaths(root)
    sock = mod._probe_port("127.0.0.1", mod.SERVE_PORT)
    if not sock["ok"]:
        check("already_up:core_listening", False,
              "SKIP-as-FAIL: :%d not listening, cannot prove no-double-spawn"
              % mod.SERVE_PORT)
        return
    r = mod._supervise_serve(paths, up=True, supervise=True,
                             pause_present=False, pause_mode=None)
    check("already_up:no_second_writer", r.get("kind") == "ALREADY_UP",
          json.dumps(r))


def test_hold_pause_blocks(mod, root: str) -> None:
    """A HOLD pause must block the spawn; a resume-gate pause must not."""
    from cosmos_paths import CosmosPaths
    paths = CosmosPaths(root)
    r = mod._supervise_serve(paths, up=False, supervise=True,
                             pause_present=True, pause_mode="hold")
    check("pause:hold_blocks", r.get("kind") == "PAUSED_HOLD", json.dumps(r))


def _scratch_root() -> str:
    """Clock-invokable default: a verified scratch install, never the live root."""
    sys.path.insert(0, str(REPO / "cosmos"))
    from cosmos_kernel import install
    td = Path(tempfile.mkdtemp(prefix="cosmos_serve_sup_"))
    return str(install(td / "scratch", tree_id="serve-supervisor-clock"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None,
                    help="verified COSMOS root; omitted -> scratch install so "
                         "the selftest clock can invoke this suite with no argv")
    ap.add_argument("--module", default=str(REPO / "cosmos" / "cosmos_health_clock.py"),
                    help="module under test (point at a _delme copy to prove "
                         "these tests FAIL against the old code)")
    a = ap.parse_args()
    if not a.root:
        a.root = _scratch_root()

    mod = load(Path(a.module))
    print("module under test: %s\n" % mod.__file__)

    test_default_on(mod)
    test_cli_flag_pair(mod)
    test_standup_registers_explicitly(mod)
    test_disabled_path_is_inert(mod, a.root)
    test_already_up_when_port_live(mod, a.root)
    test_hold_pause_blocks(mod, a.root)

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    total = len(RESULTS)
    print("\n%d/%d passed" % (passed, total))
    print(json.dumps({"tests_run": total, "tests_passed": passed,
                      "module": mod.__file__}))
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
